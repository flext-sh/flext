package plugins

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// PluginInterface define a interface para comunicação com plugins
type PluginInterface interface {
	Initialize(ctx context.Context, config map[string]interface{}) error
	Execute(ctx context.Context, input interface{}) (interface{}, error)
	Validate(ctx context.Context) error
	Cleanup(ctx context.Context) error
	GetSchema() (*PluginSchema, error)
}

// PluginSchema define o schema de um plugin
type PluginSchema struct {
	Name         string                 `json:"name"`
	Version      string                 `json:"version"`
	Type         string                 `json:"type"`
	InputSchema  map[string]interface{} `json:"input_schema"`
	OutputSchema map[string]interface{} `json:"output_schema"`
	ConfigSchema map[string]interface{} `json:"config_schema"`
	Ports        []PortSchema           `json:"ports"`
}

// PortSchema define o schema de uma porta
type PortSchema struct {
	Name        string                 `json:"name"`
	Type        string                 `json:"type"`
	Required    bool                   `json:"required"`
	Description string                 `json:"description"`
	Schema      map[string]interface{} `json:"schema"`
}

// PluginExecution representa uma execução de plugin
type PluginExecution struct {
	PluginID    uuid.UUID              `json:"plugin_id"`
	Input       interface{}            `json:"input"`
	Output      interface{}            `json:"output"`
	Config      map[string]interface{} `json:"config"`
	StartedAt   time.Time              `json:"started_at"`
	CompletedAt *time.Time             `json:"completed_at,omitempty"`
	Error       *string                `json:"error,omitempty"`
	Logs        []string               `json:"logs"`
}

// PluginLoader carrega e executa plugins dinamicamente
type PluginLoader struct {
	pluginDir string
	logger    logging.Logger
	loaded    map[uuid.UUID]*LoadedPlugin
}

// LoadedPlugin representa um plugin carregado
type LoadedPlugin struct {
	Plugin     *entities.Plugin
	Schema     *PluginSchema
	Executable string
	LoadedAt   time.Time
}

// NewPluginLoader cria um novo loader de plugins
func NewPluginLoader(pluginDir string, logger logging.Logger) *PluginLoader {
	return &PluginLoader{
		pluginDir: pluginDir,
		logger:    logger,
		loaded:    make(map[uuid.UUID]*LoadedPlugin),
	}
}

// LoadPlugin carrega um plugin
func (pl *PluginLoader) LoadPlugin(ctx context.Context, plugin *entities.Plugin) error {
	logger := pl.logger.With(
		logging.F("plugin_id", plugin.ID),
		logging.F("plugin_name", plugin.Name),
	)

	logger.Info("Loading plugin")

	// Verificar se plugin já está carregado
	if _, exists := pl.loaded[plugin.ID]; exists {
		logger.Info("Plugin already loaded")
		return nil
	}

	// Verificar se o executável existe
	executable := plugin.EntryPoint
	if !filepath.IsAbs(executable) {
		executable = filepath.Join(pl.pluginDir, executable)
	}

	if _, err := os.Stat(executable); os.IsNotExist(err) {
		return fmt.Errorf("plugin executable not found: %s", executable)
	}

	// Verificar se o arquivo é executável
	if info, err := os.Stat(executable); err != nil {
		return fmt.Errorf("failed to stat plugin executable: %w", err)
	} else if info.Mode()&0111 == 0 {
		return fmt.Errorf("plugin file is not executable: %s", executable)
	}

	// Obter schema do plugin
	schema, err := pl.getPluginSchema(ctx, executable)
	if err != nil {
		logger.Error("Failed to get plugin schema", logging.F("error", err.Error()))
		return fmt.Errorf("failed to get plugin schema: %w", err)
	}

	// Validar compatibilidade do schema
	if err := pl.validatePluginSchema(plugin, schema); err != nil {
		return fmt.Errorf("plugin schema validation failed: %w", err)
	}

	// Marcar plugin como carregado
	pl.loaded[plugin.ID] = &LoadedPlugin{
		Plugin:     plugin,
		Schema:     schema,
		Executable: executable,
		LoadedAt:   time.Now(),
	}

	logger.Info("Plugin loaded successfully")
	return nil
}

// ExecutePlugin executa um plugin
func (pl *PluginLoader) ExecutePlugin(
	ctx context.Context,
	pluginID uuid.UUID,
	input interface{},
	config map[string]interface{},
) (*PluginExecution, error) {
	logger := pl.logger.With(logging.F("plugin_id", pluginID))

	// Verificar se plugin está carregado
	loaded, exists := pl.loaded[pluginID]
	if !exists {
		return nil, fmt.Errorf("plugin not loaded: %s", pluginID)
	}

	execution := &PluginExecution{
		PluginID:  pluginID,
		Input:     input,
		Config:    config,
		StartedAt: time.Now(),
		Logs:      make([]string, 0),
	}

	logger.Info("Executing plugin")

	// Preparar dados de entrada
	inputData := map[string]interface{}{
		"input":  input,
		"config": config,
		"metadata": map[string]interface{}{
			"execution_id": uuid.New(),
			"timestamp":    time.Now(),
		},
	}

	inputJSON, err := json.Marshal(inputData)
	if err != nil {
		execution.Error = &[]string{fmt.Sprintf("Failed to marshal input: %v", err)}[0]
		return execution, err
	}

	// Executar plugin via comando externo
	cmd := exec.CommandContext(ctx, loaded.Executable)
	cmd.Stdin = strings.NewReader(string(inputJSON))

	output, err := cmd.CombinedOutput()
	now := time.Now()
	execution.CompletedAt = &now

	if err != nil {
		errorMsg := fmt.Sprintf("Plugin execution failed: %v\nOutput: %s", err, string(output))
		execution.Error = &errorMsg
		execution.Logs = append(execution.Logs, errorMsg)
		logger.Error("Plugin execution failed",
			logging.F("error", err.Error()),
			logging.F("output", string(output)),
		)
		return execution, fmt.Errorf("%s", errorMsg)
	}

	// Parsear output
	var result map[string]interface{}
	if err := json.Unmarshal(output, &result); err != nil {
		// Se não conseguir parsear como JSON, tratar como string
		result = map[string]interface{}{
			"output": string(output),
			"type":   "text",
		}
	}

	execution.Output = result
	execution.Logs = append(execution.Logs, "Plugin executed successfully")

	logger.Info("Plugin executed successfully")
	return execution, nil
}

// UnloadPlugin descarrega um plugin
func (pl *PluginLoader) UnloadPlugin(pluginID uuid.UUID) {
	if loaded, exists := pl.loaded[pluginID]; exists {
		pl.logger.Info("Unloading plugin",
			logging.F("plugin_id", pluginID),
			logging.F("plugin_name", loaded.Plugin.Name),
		)
		delete(pl.loaded, pluginID)
	}
}

// GetLoadedPlugins retorna lista de plugins carregados
func (pl *PluginLoader) GetLoadedPlugins() map[uuid.UUID]*LoadedPlugin {
	return pl.loaded
}

// getPluginSchema obtém o schema do plugin
func (pl *PluginLoader) getPluginSchema(ctx context.Context, executable string) (*PluginSchema, error) {
	// Executar plugin com flag --schema para obter metadata
	cmd := exec.CommandContext(ctx, executable, "--schema")
	output, err := cmd.Output()
	if err != nil {
		// Se --schema não funcionar, criar schema básico
		return &PluginSchema{
			Name:    filepath.Base(executable),
			Version: "unknown",
			Type:    "generic",
			InputSchema: map[string]interface{}{
				"type": "object",
			},
			OutputSchema: map[string]interface{}{
				"type": "object",
			},
			ConfigSchema: map[string]interface{}{
				"type": "object",
			},
			Ports: []PortSchema{},
		}, nil
	}

	var schema PluginSchema
	if err := json.Unmarshal(output, &schema); err != nil {
		return nil, fmt.Errorf("failed to parse plugin schema: %w", err)
	}

	return &schema, nil
}

// validatePluginSchema valida compatibilidade do schema
func (pl *PluginLoader) validatePluginSchema(plugin *entities.Plugin, schema *PluginSchema) error {
	// Validar tipo do plugin
	if strings.ToLower(schema.Type) != strings.ToLower(string(plugin.Type)) {
		return fmt.Errorf("plugin type mismatch: expected %s, got %s", plugin.Type, schema.Type)
	}

	// Validar nome (opcional, pois pode ser diferente)
	if schema.Name != "" && schema.Name != plugin.Name {
		pl.logger.Warn("Plugin name mismatch",
			logging.F("expected", plugin.Name),
			logging.F("actual", schema.Name),
		)
	}

	return nil
}

// Health check para plugins carregados
func (pl *PluginLoader) HealthCheck(ctx context.Context) map[uuid.UUID]bool {
	health := make(map[uuid.UUID]bool)

	for id, loaded := range pl.loaded {
		// Verificar se o executável ainda existe
		if _, err := os.Stat(loaded.Executable); err != nil {
			health[id] = false
			continue
		}

		// TODO: Implementar ping/health check específico do plugin
		health[id] = true
	}

	return health
}
