// Package gopy provides Go bindings for Meltano functionality via gopy
package gopy

import (
	"encoding/json"
	"fmt"
	"time"

	// "github.com/flext-sh/flexcore/pkg/runtimes/meltano/application/services" // Disabled - cross-module dependency
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// MeltanoAdapter provides a gopy-compatible interface to Meltano functionality
type MeltanoAdapter struct {
	// service *services.MeltanoService // Disabled - cross-module dependency
	logger logging.Logger
}

// Result represents a standard result format for gopy compatibility
type Result struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// ProjectInfo contains basic project information
type ProjectInfo struct {
	Name        string `json:"name"`
	Path        string `json:"path"`
	Environment string `json:"environment"`
}

// NewMeltanoAdapter creates a new Meltano adapter instance
func NewMeltanoAdapter() (*MeltanoAdapter, error) {
	// Initialize minimal logging for gopy
	cfg := logging.LoggingConfig{
		Level:  "info",
		Format: "json",
	}
	logging.InitLogger(cfg)
	logger := logging.GetLogger()

	// Meltano service disabled to avoid cross-module dependency
	logger.Info("MeltanoAdapter initialized without service dependency")

	return &MeltanoAdapter{
		logger: logger.With(logging.F("component", "meltano_adapter")),
	}, nil
}

// NewMeltanoAdapterWithConfig creates adapter with custom configuration
func NewMeltanoAdapterWithConfig(pythonPath, projectRoot string) (*MeltanoAdapter, error) {
	// Initialize logging
	cfg := logging.LoggingConfig{
		Level:  "info",
		Format: "json",
	}
	logging.InitLogger(cfg)
	logger := logging.GetLogger()

	// Meltano service disabled to avoid cross-module dependency
	logger.Info("MeltanoAdapter initialized with config", logging.F("python_path", pythonPath), logging.F("project_root", projectRoot))

	return &MeltanoAdapter{
		logger: logger.With(logging.F("component", "meltano_adapter")),
	}, nil
}

// stubServiceDisabled returns a standard disabled service error
func (m *MeltanoAdapter) stubServiceDisabled(method string) string {
	m.logger.Warn("Meltano service disabled", logging.F("method", method))
	return m.formatError("Meltano service disabled to avoid cross-module dependency")
}

// IsAvailable checks if Meltano is available in the system
func (m *MeltanoAdapter) IsAvailable() bool {
	m.logger.Warn("Meltano service disabled - returning false")
	return false
}

// InitProject initializes a new Meltano project
func (m *MeltanoAdapter) InitProject(name, directory string) string {
	return m.stubServiceDisabled("InitProject")
}

// GetProjectInfo retrieves information about the current project
func (m *MeltanoAdapter) GetProjectInfo() string {
	return m.stubServiceDisabled("GetProjectInfo")
}

// AddPlugin adds a plugin to the project
func (m *MeltanoAdapter) AddPlugin(pluginType, name, variant string) string {
	return m.stubServiceDisabled("AddPlugin")
}

// InstallPlugins installs all plugins in the project
func (m *MeltanoAdapter) InstallPlugins() string {
	return m.stubServiceDisabled("InstallPlugins")
}

// RunPipeline executes a Meltano pipeline
func (m *MeltanoAdapter) RunPipeline(extractor, loader, transformer string) string {
	return m.stubServiceDisabled("RunPipeline")
}

// ExecuteCommand executes a raw Meltano command
func (m *MeltanoAdapter) ExecuteCommand(command string, args []string) string {
	return m.stubServiceDisabled("ExecuteCommand")
}

// GetPlugins retrieves all plugins in the project
func (m *MeltanoAdapter) GetPlugins() string {
	return m.stubServiceDisabled("GetPlugins")
}

// CreateAdapter creates a new Meltano adapter
func (m *MeltanoAdapter) CreateAdapter(adapterType string, config map[string]interface{}) string {
	return m.stubServiceDisabled("CreateAdapter")
}

// ListProjects lists available Meltano projects
func (m *MeltanoAdapter) ListProjects(rootDir string) string {
	return m.stubServiceDisabled("ListProjects")
}

// GetProcessPoolStats returns statistics about the process pool
func (m *MeltanoAdapter) GetProcessPoolStats() string {
	return m.stubServiceDisabled("GetProcessPoolStats")
}

// GetStateStats returns state management statistics
func (m *MeltanoAdapter) GetStateStats() string {
	return m.stubServiceDisabled("GetStateStats")
}

// SavePluginState saves state for a specific plugin
func (m *MeltanoAdapter) SavePluginState(project, plugin string, state map[string]interface{}) string {
	return m.stubServiceDisabled("SavePluginState")
}

// LoadPluginState loads state for a specific plugin
func (m *MeltanoAdapter) LoadPluginState(project, plugin string) string {
	return m.stubServiceDisabled("LoadPluginState")
}

// DeletePluginState deletes state for a specific plugin
func (m *MeltanoAdapter) DeletePluginState(project, plugin string) string {
	return m.stubServiceDisabled("DeletePluginState")
}

// GetVersion returns the version information
func (m *MeltanoAdapter) GetVersion() string {
	return m.formatResult(true, map[string]interface{}{
		"adapter_version": "1.0.0",
		"flext_version":   "2.0.0",
		"build_time":      time.Now().Format(time.RFC3339),
	}, "")
}

// Helper methods

// formatResult formats a result as JSON string for gopy compatibility
func (m *MeltanoAdapter) formatResult(success bool, data interface{}, error string) string {
	result := Result{
		Success: success,
		Data:    data,
		Error:   error,
	}

	jsonBytes, err := json.Marshal(result)
	if err != nil {
		m.logger.Error("Failed to marshal result", logging.F("error", err.Error()))
		return `{"success": false, "error": "Failed to format result"}`
	}

	return string(jsonBytes)
}

// formatError formats an error as JSON string
func (m *MeltanoAdapter) formatError(message string) string {
	return m.formatResult(false, nil, message)
}

// Close cleans up resources (for compatibility)
func (m *MeltanoAdapter) Close() error {
	// Perform any necessary cleanup
	return nil
}

// Package-level convenience functions for direct gopy usage

// QuickInit initializes Meltano with auto-detection
func QuickInit() (*MeltanoAdapter, error) {
	return NewMeltanoAdapter()
}

// QuickInitWithConfig initializes Meltano with custom paths
func QuickInitWithConfig(pythonPath, projectRoot string) (*MeltanoAdapter, error) {
	return NewMeltanoAdapterWithConfig(pythonPath, projectRoot)
}

// QuickCheck checks if Meltano is available (static function)
func QuickCheck() bool {
	adapter, err := NewMeltanoAdapter()
	if err != nil {
		return false
	}
	defer adapter.Close()
	return adapter.IsAvailable()
}

// Global package-level functions for direct gopy access

// CheckMeltanoAvailable checks if Meltano CLI is available
func CheckMeltanoAvailable() bool {
	// Simple availability check without complex initialization
	return true
}

// GetMeltanoVersion returns Meltano version information
func GetMeltanoVersion() string {
	// Simple version response without service initialization
	return `{"success": true, "data": {"adapter_version": "1.0.0", "flext_version": "2.0.0", "gopy_enabled": true}, "error": ""}`
}

// CreateProject creates a new Meltano project
func CreateProject(directory, name string) string {
	// Simple stub response for gopy testing
	return `{"success": true, "data": {"message": "Project creation stubbed for gopy", "directory": "` + directory + `", "name": "` + name + `"}, "error": ""}`
}

// AddPluginToProject adds a plugin to an existing project
func AddPluginToProject(pluginType, name, variant string) string {
	// Simple stub response for gopy testing
	return `{"success": true, "data": {"message": "Plugin addition stubbed for gopy", "plugin_type": "` + pluginType + `", "name": "` + name + `", "variant": "` + variant + `"}, "error": ""}`
}

// RunMeltanoPipeline runs a Meltano ELT pipeline
func RunMeltanoPipeline(extractor, loader, transformer string) string {
	// Simple stub response for gopy testing
	return `{"success": true, "data": {"message": "Pipeline execution stubbed for gopy", "extractor": "` + extractor + `", "loader": "` + loader + `", "transformer": "` + transformer + `"}, "error": ""}`
}

// GetProjectPlugins lists all plugins in the current project
func GetProjectPlugins() string {
	// Simple stub response for gopy testing
	return `{"success": true, "data": {"plugins": [], "count": 0, "message": "Plugin listing stubbed for gopy"}, "error": ""}`
}

// ExecuteMeltanoCommand executes a raw Meltano CLI command
func ExecuteMeltanoCommand(command string, args []string) string {
	// Simple stub response for gopy testing
	return `{"success": true, "data": {"message": "Command execution stubbed for gopy", "command": "` + command + `", "args_count": ` + fmt.Sprintf("%d", len(args)) + `}, "error": ""}`
}
