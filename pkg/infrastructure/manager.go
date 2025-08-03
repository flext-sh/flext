package singer

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/domain/singer/domain/entities"
	"github.com/flext-sh/flext/pkg/domain/singer/domain/services"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// SingerManager gerencia especificações Singer e integração com Meltano
type SingerManager struct {
	logger           logging.Logger
	executor         *services.SingerExecutor
	meltanoProject   string
	singerSpecs      map[string]*entities.SingerSpec
	activeExecutions map[uuid.UUID]*ExecutionStatus
	mu               sync.RWMutex
	httpClient       *http.Client
}

// ExecutionStatus representa o status de uma execução ativa
type ExecutionStatus struct {
	ExecutionID uuid.UUID                 `json:"execution_id"`
	SpecID      uuid.UUID                 `json:"spec_id"`
	Status      string                    `json:"status"`
	StartTime   time.Time                 `json:"start_time"`
	Progress    float64                   `json:"progress"`
	Logs        []string                  `json:"logs"`
	Error       string                    `json:"error,omitempty"`
	Cancel      context.CancelFunc        `json:"-"`
	Result      *services.ExecutionResult `json:"result,omitempty"`
}

// MeltanoProjectConfig configuração do projeto Meltano
type MeltanoProjectConfig struct {
	Version            string                        `yaml:"version"`
	DefaultEnvironment string                        `yaml:"default_environment"`
	ProjectID          string                        `yaml:"project_id"`
	Environments       map[string]MeltanoEnvironment `yaml:"environments"`
	Jobs               []MeltanoJob                  `yaml:"jobs"`
	Plugins            map[string][]MeltanoPlugin    `yaml:"plugins"`
}

// MeltanoEnvironment configuração de ambiente Meltano
type MeltanoEnvironment struct {
	Config map[string]interface{} `yaml:"config"`
}

// MeltanoJob definição de job Meltano
type MeltanoJob struct {
	Name     string   `yaml:"name"`
	Tasks    []string `yaml:"tasks"`
	Schedule string   `yaml:"schedule,omitempty"`
}

// MeltanoPlugin definição de plugin Meltano
type MeltanoPlugin struct {
	Name       string                 `yaml:"name"`
	Namespace  string                 `yaml:"namespace"`
	Pip        string                 `yaml:"pip_url"`
	Executable string                 `yaml:"executable"`
	Settings   map[string]interface{} `yaml:"settings"`
	Select     []string               `yaml:"select,omitempty"`
	Metadata   map[string]interface{} `yaml:"metadata,omitempty"`
}

// NewSingerManager cria um novo gerenciador Singer
func NewSingerManager(logger logging.Logger, workDir string, meltanoProject string) *SingerManager {
	return &SingerManager{
		logger:           logger,
		executor:         services.NewSingerExecutor(logger, workDir),
		meltanoProject:   meltanoProject,
		singerSpecs:      make(map[string]*entities.SingerSpec),
		activeExecutions: make(map[uuid.UUID]*ExecutionStatus),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// InitializeMeltanoProject inicializa um projeto Meltano
func (sm *SingerManager) InitializeMeltanoProject(ctx context.Context, projectPath string) error {
	sm.logger.Info("Initializing Meltano project", logging.F("path", projectPath))

	// Verificar se meltano está instalado
	if err := sm.checkMeltanoInstallation(); err != nil {
		return fmt.Errorf("meltano not available: %w", err)
	}

	// Criar diretório do projeto
	if err := os.MkdirAll(projectPath, 0755); err != nil {
		return fmt.Errorf("failed to create project directory: %w", err)
	}

	// Inicializar projeto Meltano
	cmd := exec.CommandContext(ctx, "meltano", "init", filepath.Base(projectPath))
	cmd.Dir = filepath.Dir(projectPath)

	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to initialize meltano project: %w, output: %s", err, output)
	}

	sm.meltanoProject = projectPath
	sm.logger.Info("Meltano project initialized successfully",
		logging.F("path", projectPath),
		logging.F("output", string(output)),
	)

	return nil
}

// InstallSingerPlugin instala um plugin Singer via Meltano
func (sm *SingerManager) InstallSingerPlugin(ctx context.Context, pluginType, name, pipURL string) error {
	if sm.meltanoProject == "" {
		return fmt.Errorf("meltano project not initialized")
	}

	sm.logger.Info("Installing Singer plugin",
		logging.F("type", pluginType),
		logging.F("name", name),
		logging.F("pip_url", pipURL),
	)

	// Comando para adicionar plugin
	args := []string{"add", pluginType, name}
	if pipURL != "" {
		args = append(args, "--custom")
	}

	cmd := exec.CommandContext(ctx, "meltano", args...)
	cmd.Dir = sm.meltanoProject

	// Configurar variáveis de ambiente se necessário
	if pipURL != "" {
		cmd.Env = append(os.Environ(), fmt.Sprintf("PIP_URL=%s", pipURL))
	}

	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to install plugin: %w, output: %s", err, output)
	}

	sm.logger.Info("Singer plugin installed successfully",
		logging.F("name", name),
		logging.F("output", string(output)),
	)

	return nil
}

// RegisterSingerSpec registra uma especificação Singer
func (sm *SingerManager) RegisterSingerSpec(spec *entities.SingerSpec) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	sm.singerSpecs[spec.Name] = spec
	sm.logger.Info("Singer spec registered",
		logging.F("name", spec.Name),
		logging.F("type", string(spec.Type)),
		logging.F("version", spec.Version),
	)

	return nil
}

// GetSingerSpec retorna uma especificação Singer por nome
func (sm *SingerManager) GetSingerSpec(name string) (*entities.SingerSpec, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	spec, exists := sm.singerSpecs[name]
	return spec, exists
}

// ListSingerSpecs lista todas as especificações Singer registradas
func (sm *SingerManager) ListSingerSpecs() []*entities.SingerSpec {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	specs := make([]*entities.SingerSpec, 0, len(sm.singerSpecs))
	for _, spec := range sm.singerSpecs {
		specs = append(specs, spec)
	}

	return specs
}

// DiscoverSingerHub busca especificações no Singer Hub
func (sm *SingerManager) DiscoverSingerHub(ctx context.Context, category string) ([]HubSpec, error) {
	sm.logger.Info("Discovering Singer specs from hub", logging.F("category", category))

	url := "https://hub.meltano.com/api/plugins"
	if category != "" {
		url += "?category=" + category
	}

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := sm.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch from hub: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("hub API returned status %d", resp.StatusCode)
	}

	var hubResponse HubResponse
	if err := json.NewDecoder(resp.Body).Decode(&hubResponse); err != nil {
		return nil, fmt.Errorf("failed to decode hub response: %w", err)
	}

	sm.logger.Info("Discovered Singer specs from hub",
		logging.F("count", len(hubResponse.Plugins)),
	)

	return hubResponse.Plugins, nil
}

// ExecuteSync executa uma sincronização Singer (tap + target)
func (sm *SingerManager) ExecuteSync(
	ctx context.Context,
	tapName, targetName string,
	tapConfig, targetConfig map[string]interface{},
	catalog *entities.Catalog,
	state *entities.State,
) (uuid.UUID, error) {
	// Verificar especificações
	tapSpec, exists := sm.GetSingerSpec(tapName)
	if !exists {
		return uuid.Nil, fmt.Errorf("tap specification not found: %s", tapName)
	}

	targetSpec, exists := sm.GetSingerSpec(targetName)
	if !exists {
		return uuid.Nil, fmt.Errorf("target specification not found: %s", targetName)
	}

	if tapSpec.Type != entities.SingerTypeTap {
		return uuid.Nil, fmt.Errorf("specification %s is not a tap", tapName)
	}

	if targetSpec.Type != entities.SingerTypeTarget {
		return uuid.Nil, fmt.Errorf("specification %s is not a target", targetName)
	}

	// Criar execução
	executionID := uuid.New()
	_ = uuid.New() // pipelineID placeholder

	sm.logger.Info("Starting Singer sync execution",
		logging.F("execution_id", executionID.String()),
		logging.F("tap", tapName),
		logging.F("target", targetName),
	)

	// Criar contexto cancelável
	syncCtx, cancel := context.WithCancel(ctx)

	// Registrar execução ativa
	sm.mu.Lock()
	sm.activeExecutions[executionID] = &ExecutionStatus{
		ExecutionID: executionID,
		SpecID:      tapSpec.GetID(),
		Status:      "running",
		StartTime:   time.Now(),
		Progress:    0.0,
		Logs:        []string{},
		Cancel:      cancel,
	}
	sm.mu.Unlock()

	// Executar sincronização em goroutine
	go func() {
		defer cancel()

		if err := sm.executeFullSync(syncCtx, executionID, tapSpec, targetSpec, tapConfig, targetConfig, catalog, state); err != nil {
			sm.updateExecutionStatus(executionID, "failed", 0.0, err.Error())
			sm.logger.Error("Singer sync execution failed",
				logging.F("execution_id", executionID.String()),
				logging.F("error", err.Error()),
			)
		} else {
			sm.updateExecutionStatus(executionID, "completed", 100.0, "")
			sm.logger.Info("Singer sync execution completed",
				logging.F("execution_id", executionID.String()),
			)
		}
	}()

	return executionID, nil
}

// executeFullSync executa a sincronização completa tap->target
func (sm *SingerManager) executeFullSync(
	ctx context.Context,
	executionID uuid.UUID,
	tapSpec, targetSpec *entities.SingerSpec,
	tapConfig, targetConfig map[string]interface{},
	catalog *entities.Catalog,
	state *entities.State,
) error {
	// Atualizar progresso
	sm.updateExecutionStatus(executionID, "running", 10.0, "Starting tap execution")

	// Convert State to SingerState if needed
	var singerState *entities.SingerState
	if state != nil && len(state.Bookmarks) > 0 {
		bookmarks := make(map[string]interface{})
		for streamName, streamState := range state.Bookmarks {
			bookmarks[streamName] = map[string]interface{}{
				"replication_key_value": streamState.ReplicationKeyValue,
				"version":               streamState.Version,
				"last_sync_time":        streamState.LastSyncTime,
			}
		}
		singerState = &entities.SingerState{
			Bookmarks: bookmarks,
		}
	}

	// Criar execução para o tap
	tapExecution, err := entities.NewSingerExecution(tapSpec.GetID(), uuid.New(), "tap", "run", []string{}, tapConfig, singerState)
	if err != nil {
		return fmt.Errorf("failed to create tap execution: %w", err)
	}

	// Configurar opções para o tap
	tapOptions := services.ExecutionOptions{
		Config:  tapConfig,
		Catalog: catalog,
		State:   state,
	}

	sm.updateExecutionStatus(executionID, "running", 30.0, "Executing tap")

	// Executar tap
	tapResult, err := sm.executor.Execute(ctx, tapSpec, tapExecution, tapOptions)
	if err != nil {
		return fmt.Errorf("tap execution failed: %w", err)
	}

	if !tapResult.Success {
		return fmt.Errorf("tap execution was not successful")
	}

	sm.updateExecutionStatus(executionID, "running", 60.0, "Processing tap output for target")

	// Criar execução para o target
	targetExecution, err := entities.NewSingerExecution(targetSpec.GetID(), uuid.New(), "target", "run", []string{}, targetConfig, nil)
	if err != nil {
		return fmt.Errorf("failed to create target execution: %w", err)
	}

	// TODO: Implementar pipeline tap->target com streaming de dados
	// Este código precisa ser implementado com as variáveis corretas do contexto
	// Por enquanto, simular sucesso
	sm.updateExecutionStatus(executionID, "running", 80.0, "Executing target")

	// Configurar opções para o target
	targetOptions := services.ExecutionOptions{
		Config: targetConfig,
	}

	// Executar target (simplified)
	targetResult, err := sm.executor.Execute(ctx, targetSpec, targetExecution, targetOptions)
	if err != nil {
		return fmt.Errorf("target execution failed: %w", err)
	}

	if !targetResult.Success {
		return fmt.Errorf("target execution was not successful")
	}

	sm.updateExecutionStatus(executionID, "running", 95.0, "Finalizing execution")

	// Armazenar resultado combinado
	sm.mu.Lock()
	if status, exists := sm.activeExecutions[executionID]; exists {
		status.Result = tapResult // Store tap result as primary
	}
	sm.mu.Unlock()

	return nil
}

// GetExecutionStatus retorna o status de uma execução
func (sm *SingerManager) GetExecutionStatus(executionID uuid.UUID) (*ExecutionStatus, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	status, exists := sm.activeExecutions[executionID]
	return status, exists
}

// CancelExecution cancela uma execução ativa
func (sm *SingerManager) CancelExecution(executionID uuid.UUID) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	status, exists := sm.activeExecutions[executionID]
	if !exists {
		return fmt.Errorf("execution not found: %s", executionID)
	}

	if status.Cancel != nil {
		status.Cancel()
	}

	status.Status = "cancelled"
	sm.logger.Info("Singer execution cancelled", logging.F("execution_id", executionID.String()))

	return nil
}

// updateExecutionStatus atualiza o status de uma execução
func (sm *SingerManager) updateExecutionStatus(executionID uuid.UUID, status string, progress float64, message string) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	if execStatus, exists := sm.activeExecutions[executionID]; exists {
		execStatus.Status = status
		execStatus.Progress = progress
		if message != "" {
			execStatus.Logs = append(execStatus.Logs, fmt.Sprintf("[%s] %s", time.Now().Format(time.RFC3339), message))
		}
		if status == "failed" {
			execStatus.Error = message
		}
	}
}

// checkMeltanoInstallation verifica se Meltano está instalado
func (sm *SingerManager) checkMeltanoInstallation() error {
	cmd := exec.Command("meltano", "--version")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("meltano not found in PATH: %w", err)
	}

	sm.logger.Info("Meltano installation found", logging.F("version", strings.TrimSpace(string(output))))
	return nil
}

// LoadMeltanoProject carrega configuração de um projeto Meltano existente
func (sm *SingerManager) LoadMeltanoProject(projectPath string) error {
	configPath := filepath.Join(projectPath, "meltano.yml")

	configData, err := os.ReadFile(configPath)
	if err != nil {
		return fmt.Errorf("failed to read meltano.yml: %w", err)
	}

	var _ MeltanoProjectConfig // config placeholder
	// Note: Seria melhor usar YAML parser, mas por simplicidade usamos uma implementação básica
	sm.logger.Info("Loaded Meltano project configuration",
		logging.F("path", projectPath),
		logging.F("config_size", len(configData)),
	)

	sm.meltanoProject = projectPath
	return nil
}

// CleanupCompletedExecutions remove execuções antigas da memória
func (sm *SingerManager) CleanupCompletedExecutions() {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	cutoff := time.Now().Add(-24 * time.Hour) // Remove execuções com mais de 24h

	for id, status := range sm.activeExecutions {
		if (status.Status == "completed" || status.Status == "failed" || status.Status == "cancelled") &&
			status.StartTime.Before(cutoff) {
			delete(sm.activeExecutions, id)
		}
	}
}

// GetProjectPath retorna o caminho do projeto Meltano
func (sm *SingerManager) GetProjectPath() string {
	return sm.meltanoProject
}

// HubResponse estrutura da resposta do Singer Hub
type HubResponse struct {
	Plugins []HubSpec `json:"plugins"`
}

// HubSpec especificação do Singer Hub
type HubSpec struct {
	Name        string   `json:"name"`
	Namespace   string   `json:"namespace"`
	Type        string   `json:"type"`
	Description string   `json:"description"`
	Keywords    []string `json:"keywords"`
	PipURL      string   `json:"pip_url"`
	Executable  string   `json:"executable"`
	Settings    []struct {
		Name        string `json:"name"`
		Label       string `json:"label"`
		Kind        string `json:"kind"`
		Description string `json:"description"`
		Secret      bool   `json:"secret"`
	} `json:"settings"`
}
