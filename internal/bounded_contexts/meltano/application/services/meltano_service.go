package services

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/meltano/infrastructure/config"
	"github.com/flext/flexcore/internal/bounded_contexts/meltano/infrastructure/persistence"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/pkg/errors"
)

// MeltanoResult represents the result of a Meltano operation
type MeltanoResult struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
	Output  string      `json:"output,omitempty"`
}

// ProcessPool manages Python process execution
type ProcessPool struct {
	mu        sync.RWMutex
	active    map[string]*exec.Cmd
	semaphore chan struct{}
	config    *config.MeltanoConfig
	logger    logging.Logger
}

// NewProcessPool creates a new process pool
func NewProcessPool(config *config.MeltanoConfig, logger logging.Logger) *ProcessPool {
	return &ProcessPool{
		active:    make(map[string]*exec.Cmd),
		semaphore: make(chan struct{}, config.MaxConcurrent),
		config:    config,
		logger:    logger,
	}
}

// MeltanoService provides Meltano integration services with robust error handling
type MeltanoService struct {
	config         *config.MeltanoConfig
	logger         logging.Logger
	processPool    *ProcessPool
	stateManager   *persistence.StateManager
	loadedProjects map[string]string // map[project_name]project_path
	mu             sync.RWMutex
}

// NewMeltanoService creates a new Meltano service with robust configuration
func NewMeltanoService(pythonPath, projectRoot string) *MeltanoService {
	// Create logger
	logger := logging.GetLogger().With(logging.F("service", "meltano"))

	// Create default configuration
	cfg := config.DefaultMeltanoConfig()
	cfg.PythonPath = pythonPath
	cfg.ProjectRoot = projectRoot

	// Create process pool
	processPool := NewProcessPool(cfg, logger)

	// Create state manager
	stateManager, err := persistence.NewStateManager(cfg.StateDir, logger)
	if err != nil {
		logger.Warn("Failed to create state manager", logging.F("error", err.Error()))
		stateManager = nil
	}

	service := &MeltanoService{
		config:         cfg,
		logger:         logger,
		processPool:    processPool,
		stateManager:   stateManager,
		loadedProjects: make(map[string]string),
	}

	logger.Info("Meltano service created",
		logging.F("python_path", pythonPath),
		logging.F("project_root", projectRoot))

	return service
}

// NewMeltanoServiceWithConfig creates a new Meltano service with validated configuration
func NewMeltanoServiceWithConfig(logger logging.Logger) (*MeltanoService, error) {
	// Auto-detect configuration
	cfg, err := config.AutoDetectConfiguration(logger)
	if err != nil {
		return nil, errors.Wrap(err, "failed to auto-detect Meltano configuration")
	}

	// Create process pool
	processPool := NewProcessPool(cfg, logger)

	// Create state manager
	stateManager, stateErr := persistence.NewStateManager(cfg.StateDir, logger)
	if stateErr != nil {
		logger.Warn("Failed to create state manager", logging.F("error", stateErr.Error()))
		stateManager = nil
	}

	service := &MeltanoService{
		config:         cfg,
		logger:         logger.With(logging.F("service", "meltano")),
		processPool:    processPool,
		stateManager:   stateManager,
		loadedProjects: make(map[string]string),
	}

	logger.Info("Meltano service created with auto-detected configuration",
		logging.F("python_path", cfg.PythonPath),
		logging.F("meltano_path", cfg.MeltanoPath),
		logging.F("project_root", cfg.ProjectRoot))

	return service, nil
}

// IsAvailable checks if Meltano is available and working with timeout
func (s *MeltanoService) IsAvailable(ctx context.Context) (bool, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Create timeout context
	timeoutCtx, cancel := context.WithTimeout(ctx, s.config.BridgeTimeout)
	defer cancel()

	script := fmt.Sprintf("import %s; print(%s.is_available())",
		s.config.BridgeModule, s.config.BridgeModule)

	result, err := s.executePythonScript(timeoutCtx, script)
	if err != nil {
		s.logger.Error("Failed to check Meltano availability",
			logging.F("error", err.Error()))
		return false, errors.Wrap(err, "failed to check Meltano availability")
	}

	// Check if output contains "True" (handles both "True\n" and "True")
	output := strings.TrimSpace(result.Output)
	available := output == "True"
	s.logger.Debug("Meltano availability check completed",
		logging.F("available", available),
		logging.F("output", result.Output))

	return available, nil
}

// InitProject initializes a new Meltano project
func (s *MeltanoService) InitProject(ctx context.Context, projectName, projectDir string) (*MeltanoResult, error) {
	if projectDir == "" {
		projectDir = projectName
	}

	// Use the meltano_bridge module to initialize project
	script := fmt.Sprintf(`
import meltano_bridge
import json
result = meltano_bridge.init_project('%s', '%s')
print(result)
`, projectName, projectDir)

	result, err := s.executePythonScript(ctx, script)

	// If project creation was successful, register it
	if err == nil && result != nil && result.Success {
		s.mu.Lock()
		fullPath := filepath.Join(s.config.ProjectRoot, projectDir)
		s.loadedProjects[projectName] = fullPath
		s.mu.Unlock()

		s.logger.Info("Project registered in service",
			logging.F("project", projectName),
			logging.F("path", fullPath))
	}

	return result, err
}

// AddPlugin adds a plugin to the Meltano project
func (s *MeltanoService) AddPlugin(ctx context.Context, pluginType, pluginName, pluginVariant string) (*MeltanoResult, error) {
	script := fmt.Sprintf(`
import meltano_bridge
import json
result = meltano_bridge.add_plugin('%s', '%s', '%s')
print(result)
`, pluginType, pluginName, pluginVariant)

	return s.executePythonScript(ctx, script)
}

// InstallPlugins installs all plugins in the project
func (s *MeltanoService) InstallPlugins(ctx context.Context) (*MeltanoResult, error) {
	script := `
import meltano_bridge
import json
result = meltano_bridge.install_plugins()
print(result)
`
	return s.executePythonScript(ctx, script)
}

// RunPipeline runs a Meltano pipeline with state persistence
func (s *MeltanoService) RunPipeline(ctx context.Context, extractor, loader, transformer string) (*MeltanoResult, error) {
	defaultProject, err := s.ensureProjectAvailable(ctx)
	if err != nil {
		return &MeltanoResult{
			Success: false,
			Error:   err.Error(),
		}, nil
	}

	pipelineName := s.buildPipelineName(extractor, loader, transformer)
	executionID := s.startExecutionTracking(ctx, defaultProject, pipelineName)

	script := s.buildPipelineScript(extractor, loader, transformer)
	result, err := s.executeWithRetry(ctx, script, "RunPipeline")

	s.completeExecutionTracking(ctx, executionID, result, err)

	return result, err
}

// ensureProjectAvailable ensures a project is available, creating default if needed
func (s *MeltanoService) ensureProjectAvailable(ctx context.Context) (string, error) {
	s.mu.RLock()
	projectCount := len(s.loadedProjects)
	var defaultProject string
	if projectCount > 0 {
		for name := range s.loadedProjects {
			defaultProject = name
			break
		}
	}
	s.mu.RUnlock()

	if projectCount == 0 {
		s.logger.Warn("No Meltano projects loaded, attempting to create default project")
		_, err := s.InitProject(ctx, "default", ".")
		if err != nil {
			return "", fmt.Errorf("no Meltano project loaded and failed to create default project: %w", err)
		}
		defaultProject = "default"
	}

	return defaultProject, nil
}

// buildPipelineName creates a pipeline name from components
func (s *MeltanoService) buildPipelineName(extractor, loader, transformer string) string {
	if transformer != "" {
		return fmt.Sprintf("%s-%s-%s", extractor, transformer, loader)
	}
	return fmt.Sprintf("%s-%s", extractor, loader)
}

// buildPipelineScript creates the Python script for pipeline execution
func (s *MeltanoService) buildPipelineScript(extractor, loader, transformer string) string {
	return fmt.Sprintf(`
import meltano_bridge
import json
result = meltano_bridge.run_pipeline('%s', '%s', '%s')
print(result)
`, extractor, loader, transformer)
}

// startExecutionTracking begins tracking a pipeline execution
func (s *MeltanoService) startExecutionTracking(ctx context.Context, project, pipelineName string) string {
	if s.stateManager == nil {
		return ""
	}

	executionID, err := s.stateManager.StartExecution(ctx, project, pipelineName)
	if err != nil {
		s.logger.Warn("Failed to start execution tracking", logging.F("error", err.Error()))
		return ""
	}

	return executionID
}

// completeExecutionTracking finishes tracking a pipeline execution
func (s *MeltanoService) completeExecutionTracking(ctx context.Context, executionID string, result *MeltanoResult, err error) {
	if s.stateManager == nil || executionID == "" {
		return
	}

	status, errorMsg := s.determineExecutionStatus(result, err)
	metrics := s.buildExecutionMetrics(result)

	if completeErr := s.stateManager.CompleteExecution(ctx, executionID, status, errorMsg, metrics); completeErr != nil {
		s.logger.Warn("Failed to complete execution tracking", logging.F("error", completeErr.Error()))
	}
}

// determineExecutionStatus determines the execution status and error message
func (s *MeltanoService) determineExecutionStatus(result *MeltanoResult, err error) (string, string) {
	if err != nil {
		return "failed", err.Error()
	}
	if result != nil && !result.Success {
		return "failed", result.Error
	}
	return "completed", ""
}

// buildExecutionMetrics builds metrics for execution tracking
func (s *MeltanoService) buildExecutionMetrics(result *MeltanoResult) map[string]interface{} {
	metrics := make(map[string]interface{})
	if result != nil {
		metrics["success"] = result.Success
		if result.Output != "" {
			metrics["output_length"] = len(result.Output)
		}
	}
	return metrics
}

// GetPlugins gets a list of all plugins in the project
func (s *MeltanoService) GetPlugins(ctx context.Context) (*MeltanoResult, error) {
	script := `
import meltano_bridge
import json
result = meltano_bridge.get_plugins()
print(result)
`
	return s.executePythonScript(ctx, script)
}

// GetProjectInfo gets information about the current project
func (s *MeltanoService) GetProjectInfo(ctx context.Context) (*MeltanoResult, error) {
	script := `
import meltano_bridge
import json
result = meltano_bridge.get_project_info()
print(result)
`
	return s.executePythonScript(ctx, script)
}

// ExecuteCommand executes a raw Meltano command
func (s *MeltanoService) ExecuteCommand(ctx context.Context, command string, args []string) (*MeltanoResult, error) {
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, errors.Wrap(err, "failed to marshal arguments")
	}

	script := fmt.Sprintf(`
import meltano_bridge
import json
result = meltano_bridge.execute_command('%s', '%s')
print(result)
`, command, string(argsJSON))

	return s.executePythonScript(ctx, script)
}

// ExecuteMeltanoDirect executes Meltano commands directly via subprocess
func (s *MeltanoService) ExecuteMeltanoDirect(ctx context.Context, args ...string) (*MeltanoResult, error) {
	cmd := exec.CommandContext(ctx, s.config.MeltanoPath, args...)
	cmd.Dir = s.config.ProjectRoot
	
	// DEBUG: Log exact command being executed
	s.logger.Info("DEBUG: Executing Meltano command",
		logging.F("command", s.config.MeltanoPath),
		logging.F("args", args),
		logging.F("working_dir", s.config.ProjectRoot),
		logging.F("env_vars", len(cmd.Env)))

	output, err := cmd.CombinedOutput()
	
	// DEBUG: Log execution result
	s.logger.Info("DEBUG: Command execution result",
		logging.F("output", string(output)),
		logging.F("error", err),
		logging.F("output_length", len(output)))
	
	if err != nil {
		return &MeltanoResult{
			Success: false,
			Error:   err.Error(),
			Output:  string(output),
		}, nil
	}

	return &MeltanoResult{
		Success: true,
		Output:  string(output),
	}, nil
}

// CreateAdapter creates a Meltano adapter configuration
func (s *MeltanoService) CreateAdapter(ctx context.Context, adapterType string, config map[string]interface{}) (*MeltanoResult, error) {
	configJSON, err := json.Marshal(config)
	if err != nil {
		return nil, errors.Wrap(err, "failed to marshal adapter config")
	}

	script := fmt.Sprintf(`
import meltano_bridge
import json

# Create adapter based on type
adapter_config = json.loads('%s')
if '%s' == 'tap':
    result = meltano_bridge.add_plugin('extractors', adapter_config.get('name', 'tap-generic'), adapter_config.get('variant', ''))
elif '%s' == 'target':
    result = meltano_bridge.add_plugin('loaders', adapter_config.get('name', 'target-generic'), adapter_config.get('variant', ''))
else:
    result = json.dumps({"success": false, "error": "Invalid adapter type"})

print(result)
`, string(configJSON), adapterType, adapterType)

	return s.executePythonScript(ctx, script)
}

// ListProjects lists available Meltano projects
func (s *MeltanoService) ListProjects(ctx context.Context, rootDir string) ([]string, error) {
	projects := []string{}

	// Look for meltano.yml files in subdirectories
	pattern := filepath.Join(rootDir, "*/meltano.yml")
	matches, err := filepath.Glob(pattern)
	if err != nil {
		return nil, errors.Wrap(err, "failed to search for Meltano projects")
	}

	for _, match := range matches {
		projectDir := filepath.Dir(match)
		projectName := filepath.Base(projectDir)
		projects = append(projects, projectName)
	}

	return projects, nil
}

// executePythonScript executes a Python script and returns the parsed result
func (s *MeltanoService) executePythonScript(ctx context.Context, script string) (*MeltanoResult, error) {
	cmd := exec.CommandContext(ctx, s.config.PythonPath, "-c", script)
	cmd.Dir = s.config.ProjectRoot

	output, err := cmd.Output()
	if err != nil {
		return &MeltanoResult{
			Success: false,
			Error:   err.Error(),
		}, nil
	}

	var result MeltanoResult
	if err := json.Unmarshal(output, &result); err != nil {
		// If JSON parsing fails, treat as raw output
		return &MeltanoResult{
			Success: true,
			Output:  string(output),
		}, nil
	}

	return &result, nil
}

// Validate checks if the service configuration is valid
func (s *MeltanoService) Validate() error {
	if s.config.PythonPath == "" {
		return errors.New("Python path is required")
	}

	if s.config.ProjectRoot == "" {
		return errors.New("project root is required")
	}

	return nil
}

// SetPythonPath sets the Python interpreter path
func (s *MeltanoService) SetPythonPath(path string) {
	s.config.PythonPath = path
}

// SetMeltanoPath sets the Meltano executable path
func (s *MeltanoService) SetMeltanoPath(path string) {
	s.config.MeltanoPath = path
}

// SetProjectRoot sets the project root directory
func (s *MeltanoService) SetProjectRoot(path string) {
	s.config.ProjectRoot = path
}

// executeWithTimeout executes a Python script with comprehensive timeout and error handling
func (s *MeltanoService) executeWithTimeout(ctx context.Context, script string) (*MeltanoResult, error) {
	if err := s.acquireProcessSlot(ctx); err != nil {
		return nil, err
	}
	defer s.releaseProcessSlot()

	exec, err := s.prepareExecution(ctx, script)
	if err != nil {
		return nil, err
	}
	defer s.cleanupExecution(exec.ProcessID)

	return s.runExecution(ctx, exec)
}

// ExecutionContext holds context for script execution
type ExecutionContext struct {
	Cmd       *exec.Cmd
	ProcessID string
}

// acquireProcessSlot acquires a semaphore slot for process execution
func (s *MeltanoService) acquireProcessSlot(ctx context.Context) error {
	select {
	case s.processPool.semaphore <- struct{}{}:
		return nil
	case <-ctx.Done():
		return errors.Wrap(ctx.Err(), "context cancelled while waiting for process slot")
	}
}

// releaseProcessSlot releases the semaphore slot
func (s *MeltanoService) releaseProcessSlot() {
	<-s.processPool.semaphore
}

// prepareExecution sets up the command and tracking for execution
func (s *MeltanoService) prepareExecution(ctx context.Context, script string) (*ExecutionContext, error) {
	cmd := exec.CommandContext(ctx, s.config.PythonPath, "-c", script)
	cmd.Dir = s.config.ProjectRoot
	cmd.Env = s.buildEnvironment()

	processID := fmt.Sprintf("meltano_%d", time.Now().UnixNano())
	s.trackActiveProcess(processID, cmd)

	s.logger.Debug("Executing Python script",
		logging.F("process_id", processID),
		logging.F("timeout", s.config.BridgeTimeout))

	return &ExecutionContext{
		Cmd:       cmd,
		ProcessID: processID,
	}, nil
}

// buildEnvironment creates the environment for command execution
func (s *MeltanoService) buildEnvironment() []string {
	if s.config.EnvVars != nil && len(s.config.EnvVars) > 0 {
		envVars := make([]string, 0, len(s.config.EnvVars))
		for key, value := range s.config.EnvVars {
			envVars = append(envVars, fmt.Sprintf("%s=%s", key, value))
		}
		return append(os.Environ(), envVars...)
	}
	return os.Environ()
}

// trackActiveProcess adds the command to the active processes map
func (s *MeltanoService) trackActiveProcess(processID string, cmd *exec.Cmd) {
	s.processPool.mu.Lock()
	s.processPool.active[processID] = cmd
	s.processPool.mu.Unlock()
}

// cleanupExecution removes the process from tracking
func (s *MeltanoService) cleanupExecution(processID string) {
	s.processPool.mu.Lock()
	delete(s.processPool.active, processID)
	s.processPool.mu.Unlock()
}

// runExecution executes the command and processes the result
func (s *MeltanoService) runExecution(ctx context.Context, exec *ExecutionContext) (*MeltanoResult, error) {
	output, err := exec.Cmd.Output()
	if err != nil {
		return s.handleExecutionError(ctx, exec.ProcessID, err)
	}

	return s.parseExecutionResult(exec.ProcessID, output)
}

// handleExecutionError processes command execution errors
func (s *MeltanoService) handleExecutionError(ctx context.Context, processID string, err error) (*MeltanoResult, error) {
	if ctx.Err() == context.DeadlineExceeded {
		s.logger.Error("Python script execution timed out",
			logging.F("process_id", processID),
			logging.F("timeout", s.config.BridgeTimeout))
		return &MeltanoResult{
			Success: false,
			Error:   fmt.Sprintf("execution timed out after %v", s.config.BridgeTimeout),
		}, nil
	}

	s.logger.Error("Python script execution failed",
		logging.F("process_id", processID),
		logging.F("error", err.Error()))

	return &MeltanoResult{
		Success: false,
		Error:   err.Error(),
	}, nil
}

// parseExecutionResult parses the command output into a MeltanoResult
func (s *MeltanoService) parseExecutionResult(processID string, output []byte) (*MeltanoResult, error) {
	var result MeltanoResult
	if err := json.Unmarshal(output, &result); err != nil {
		s.logger.Debug("Failed to parse JSON output, treating as raw output",
			logging.F("process_id", processID),
			logging.F("output", string(output)))

		return &MeltanoResult{
			Success: true,
			Output:  string(output),
		}, nil
	}

	s.logger.Debug("Python script execution completed",
		logging.F("process_id", processID),
		logging.F("success", result.Success))

	return &result, nil
}

// executeWithRetry executes a Python script with retry logic for transient failures
func (s *MeltanoService) executeWithRetry(ctx context.Context, script string, operation string) (*MeltanoResult, error) {
	retryContext := &RetryContext{
		Script:     script,
		Operation:  operation,
		MaxRetries: s.config.MaxRetries,
	}

	for attempt := 1; attempt <= s.config.MaxRetries; attempt++ {
		result, err := s.processRetryAttempt(ctx, retryContext, attempt)
		if result != nil {
			return result, err
		}

		// Continue to next attempt if not final
		if attempt < s.config.MaxRetries {
			if waitErr := s.waitBeforeRetry(ctx, operation, attempt); waitErr != nil {
				return nil, waitErr
			}
		}
	}

	return nil, errors.Errorf("operation %s failed after %d attempts", operation, s.config.MaxRetries)
}

// RetryContext holds context for retry operations
type RetryContext struct {
	Script     string
	Operation  string
	MaxRetries int
	LastErr    error
}

// processRetryAttempt processes a single retry attempt
func (s *MeltanoService) processRetryAttempt(ctx context.Context, retryCtx *RetryContext, attempt int) (*MeltanoResult, error) {
	result, err := s.executeAttempt(ctx, retryCtx.Script, retryCtx.Operation, attempt)

	if err == nil && result != nil && result.Success {
		s.logSuccessfulOperation(retryCtx.Operation, attempt)
		return result, nil
	}

	retryCtx.LastErr = s.handleAttemptFailure(result, err, retryCtx.Operation, attempt)

	if attempt == retryCtx.MaxRetries {
		return s.handleFinalFailure(result, err, retryCtx.Operation, attempt, retryCtx.LastErr)
	}

	return nil, nil // Continue retry
}

// executeAttempt performs a single execution attempt with timeout
func (s *MeltanoService) executeAttempt(ctx context.Context, script string, operation string, attempt int) (*MeltanoResult, error) {
	attemptCtx, cancel := context.WithTimeout(ctx, s.config.BridgeTimeout)
	defer cancel()

	s.logger.Debug("Attempting operation",
		logging.F("operation", operation),
		logging.F("attempt", attempt),
		logging.F("max_retries", s.config.MaxRetries))

	return s.executeWithTimeout(attemptCtx, script)
}

// logSuccessfulOperation logs when an operation completes successfully
func (s *MeltanoService) logSuccessfulOperation(operation string, attempt int) {
	s.logger.Debug("Operation completed successfully",
		logging.F("operation", operation),
		logging.F("attempt", attempt))
}

// handleAttemptFailure processes the failure of a single attempt
func (s *MeltanoService) handleAttemptFailure(result *MeltanoResult, err error, operation string, attempt int) error {
	if err != nil {
		return err
	}
	if result != nil && !result.Success {
		return fmt.Errorf("operation failed: %s", result.Error)
	}
	return fmt.Errorf("operation failed with unknown error")
}

// handleFinalFailure processes the final failure after all retries are exhausted
func (s *MeltanoService) handleFinalFailure(result *MeltanoResult, err error, operation string, attempt int, lastErr error) (*MeltanoResult, error) {
	if err != nil {
		s.logger.Error("Operation failed after all retries",
			logging.F("operation", operation),
			logging.F("attempts", attempt),
			logging.F("error", err.Error()))
		return nil, errors.Wrapf(err, "operation %s failed after %d attempts", operation, attempt)
	}

	if result != nil && !result.Success {
		s.logger.Error("Operation failed after all retries",
			logging.F("operation", operation),
			logging.F("attempts", attempt),
			logging.F("error", result.Error))
		return result, nil
	}

	return nil, lastErr
}

// waitBeforeRetry handles the delay between retry attempts
func (s *MeltanoService) waitBeforeRetry(ctx context.Context, operation string, attempt int) error {
	s.logger.Debug("Retrying operation after delay",
		logging.F("operation", operation),
		logging.F("attempt", attempt),
		logging.F("delay", s.config.RetryDelay))

	select {
	case <-time.After(s.config.RetryDelay):
		return nil
	case <-ctx.Done():
		return errors.Wrap(ctx.Err(), "context cancelled during retry delay")
	}
}

// GetProcessPoolStats returns statistics about the process pool
func (s *MeltanoService) GetProcessPoolStats() map[string]interface{} {
	s.processPool.mu.RLock()
	defer s.processPool.mu.RUnlock()

	return map[string]interface{}{
		"active_processes": len(s.processPool.active),
		"max_concurrent":   s.config.MaxConcurrent,
		"available_slots":  s.config.MaxConcurrent - len(s.processPool.active),
		"bridge_timeout":   s.config.BridgeTimeout.String(),
		"max_retries":      s.config.MaxRetries,
		"retry_delay":      s.config.RetryDelay.String(),
	}
}

// Shutdown gracefully shuts down the service and terminates active processes
func (s *MeltanoService) Shutdown(ctx context.Context) error {
	s.logger.Info("Shutting down Meltano service")

	activeProcesses := s.getActiveProcesses()
	if len(activeProcesses) == 0 {
		s.logger.Info("Meltano service shutdown completed")
		return nil
	}

	s.terminateActiveProcesses(activeProcesses)
	s.waitForProcessTermination(ctx, activeProcesses)

	s.logger.Info("Meltano service shutdown completed")
	return nil
}

// getActiveProcesses retrieves all currently active processes
func (s *MeltanoService) getActiveProcesses() []*exec.Cmd {
	s.processPool.mu.Lock()
	defer s.processPool.mu.Unlock()

	activeProcesses := make([]*exec.Cmd, 0, len(s.processPool.active))
	for _, cmd := range s.processPool.active {
		activeProcesses = append(activeProcesses, cmd)
	}
	return activeProcesses
}

// terminateActiveProcesses sends kill signals to all active processes
func (s *MeltanoService) terminateActiveProcesses(activeProcesses []*exec.Cmd) {
	s.logger.Info("Terminating active processes",
		logging.F("count", len(activeProcesses)))

	for _, cmd := range activeProcesses {
		if cmd.Process != nil {
			if err := cmd.Process.Kill(); err != nil {
				s.logger.Warn("Failed to kill process",
					logging.F("error", err.Error()))
			}
		}
	}
}

// waitForProcessTermination waits for processes to terminate or timeout
func (s *MeltanoService) waitForProcessTermination(ctx context.Context, activeProcesses []*exec.Cmd) {
	done := make(chan struct{})
	go func() {
		for _, cmd := range activeProcesses {
			cmd.Wait()
		}
		close(done)
	}()

	select {
	case <-done:
		s.logger.Info("All processes terminated successfully")
	case <-ctx.Done():
		s.logger.Warn("Shutdown timeout reached, some processes may still be running")
	}
}

// State Management Methods

// SavePluginState saves state for a specific plugin
func (s *MeltanoService) SavePluginState(ctx context.Context, projectName, pluginName string, state map[string]interface{}) error {
	if s.stateManager == nil {
		return errors.New("state manager not available")
	}
	return s.stateManager.SaveState(ctx, projectName, pluginName, state)
}

// LoadPluginState loads state for a specific plugin
func (s *MeltanoService) LoadPluginState(ctx context.Context, projectName, pluginName string) (map[string]interface{}, error) {
	if s.stateManager == nil {
		return make(map[string]interface{}), nil
	}
	return s.stateManager.LoadState(ctx, projectName, pluginName)
}

// DeletePluginState deletes state for a specific plugin
func (s *MeltanoService) DeletePluginState(ctx context.Context, projectName, pluginName string) error {
	if s.stateManager == nil {
		return errors.New("state manager not available")
	}
	return s.stateManager.DeleteState(ctx, projectName, pluginName)
}

// GetExecution retrieves execution details
func (s *MeltanoService) GetExecution(ctx context.Context, executionID string) (*persistence.ExecutionRecord, error) {
	if s.stateManager == nil {
		return nil, errors.New("state manager not available")
	}
	return s.stateManager.GetExecution(ctx, executionID)
}

// ListExecutions lists recent executions
func (s *MeltanoService) ListExecutions(ctx context.Context, projectName string, limit int) ([]*persistence.ExecutionRecord, error) {
	if s.stateManager == nil {
		return []*persistence.ExecutionRecord{}, nil
	}
	return s.stateManager.ListExecutions(ctx, projectName, limit)
}

// GetStateStats returns statistics about state management
func (s *MeltanoService) GetStateStats(ctx context.Context) (map[string]interface{}, error) {
	if s.stateManager == nil {
		return map[string]interface{}{
			"enabled": false,
			"message": "State manager not available",
		}, nil
	}

	stats, err := s.stateManager.GetStats(ctx)
	if err != nil {
		return nil, err
	}

	stats["enabled"] = true
	return stats, nil
}

// ExecutePipelineRequest represents the pipeline execution request exactly as specified in FLEXT_SERVICE_ARCHITECTURE.md
type ExecutePipelineRequest struct {
	ExtractorName string
	LoaderName    string
}

// ExecutionResult represents the pipeline execution result exactly as specified in FLEXT_SERVICE_ARCHITECTURE.md  
type ExecutionResult struct {
	Status   string
	Output   string
	Duration time.Duration
}

// ExecutePipeline executes a Meltano pipeline exactly as specified in FLEXT_SERVICE_ARCHITECTURE.md
func (s *MeltanoService) ExecutePipeline(ctx context.Context, request ExecutePipelineRequest) (*ExecutionResult, error) {
	startTime := time.Now()
	
	// 1. Prepare Meltano command - Executes Python library as subprocess
	cmd := exec.CommandContext(ctx, s.config.PythonPath, "-m", "meltano", 
		"run", request.ExtractorName, request.LoaderName)
	cmd.Dir = s.config.ProjectRoot
	
	// 2. Set environment variables for Python libraries
	cmd.Env = append(os.Environ(),
		fmt.Sprintf("MELTANO_PROJECT_ROOT=%s", s.config.ProjectRoot),
		"PYTHONPATH=/home/marlonsc/flext/flext-core/src:/home/marlonsc/flext/flext-meltano/src",
	)
	
	// 3. Execute Python subprocess
	output, err := cmd.CombinedOutput()
	if err != nil {
		s.logger.Error("Meltano execution failed", 
			logging.F("error", err.Error()),
			logging.F("output", string(output)))
		return nil, fmt.Errorf("meltano execution failed: %w", err)
	}
	
	// 4. Parse Python library output and return to Go service
	result := &ExecutionResult{
		Status:   "completed",
		Output:   string(output),
		Duration: time.Since(startTime),
	}
	
	return result, nil
}
