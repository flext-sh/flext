package execution

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// PluginExecutor executes plugins with real implementations
type PluginExecutor struct {
	logger      logging.Logger
	workDir     string
	pythonPath  string
	timeout     time.Duration
	env         []string
}

// ExecutionResult represents the result of plugin execution
type ExecutionResult struct {
	Success      bool                   `json:"success"`
	ExitCode     int                    `json:"exit_code"`
	Stdout       string                 `json:"stdout"`
	Stderr       string                 `json:"stderr"`
	Duration     time.Duration          `json:"duration"`
	Data         map[string]interface{} `json:"data,omitempty"`
	RecordsCount int                    `json:"records_count"`
	Error        string                 `json:"error,omitempty"`
}

// PluginExecutionContext contains context for plugin execution
type PluginExecutionContext struct {
	ExecutionID uuid.UUID              `json:"execution_id"`
	PipelineID  uuid.UUID              `json:"pipeline_id"`
	StepID      uuid.UUID              `json:"step_id"`
	InputData   map[string]interface{} `json:"input_data,omitempty"`
	Config      map[string]interface{} `json:"config"`
	Environment map[string]string      `json:"environment,omitempty"`
}

// NewPluginExecutor creates a new plugin executor
func NewPluginExecutor(logger logging.Logger, workDir, pythonPath string) *PluginExecutor {
	return &PluginExecutor{
		logger:     logger,
		workDir:    workDir,
		pythonPath: pythonPath,
		timeout:    5 * time.Minute, // Default timeout
		env:        os.Environ(),
	}
}

// SetTimeout sets the execution timeout
func (e *PluginExecutor) SetTimeout(timeout time.Duration) {
	e.timeout = timeout
}

// SetEnvironment sets additional environment variables
func (e *PluginExecutor) SetEnvironment(env map[string]string) {
	e.env = os.Environ()
	for key, value := range env {
		e.env = append(e.env, fmt.Sprintf("%s=%s", key, value))
	}
}

// Execute executes a plugin with real implementation
func (e *PluginExecutor) Execute(ctx context.Context, plugin *entities.Plugin, execCtx *PluginExecutionContext) (*ExecutionResult, error) {
	startTime := time.Now()

	e.logger.Info("Starting real plugin execution",
		logging.F("plugin_id", plugin.ID.String()),
		logging.F("plugin_name", plugin.Name),
		logging.F("plugin_type", plugin.Type),
		logging.F("execution_id", execCtx.ExecutionID.String()),
	)

	// Create execution directory
	execDir := filepath.Join(e.workDir, "executions", execCtx.ExecutionID.String())
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create execution directory: %w", err)
	}
	defer e.cleanup(execDir)

	// Determine execution strategy based on plugin type
	var result *ExecutionResult
	var err error

	switch plugin.Type {
	case "source":
		result, err = e.executeTap(ctx, plugin, execCtx, execDir)
	case "target":
		result, err = e.executeTarget(ctx, plugin, execCtx, execDir)
	case "transformer":
		result, err = e.executeTransformer(ctx, plugin, execCtx, execDir)
	case "utility":
		result, err = e.executeUtility(ctx, plugin, execCtx, execDir)
	default:
		return nil, fmt.Errorf("unsupported plugin type: %s", plugin.Type)
	}

	if err != nil {
		e.logger.Error("Plugin execution failed",
			logging.F("plugin_id", plugin.ID.String()),
			logging.F("error", err.Error()),
		)
		return &ExecutionResult{
			Success:  false,
			Duration: time.Since(startTime),
			Error:    err.Error(),
		}, nil
	}

	result.Duration = time.Since(startTime)
	
	e.logger.Info("Plugin execution completed",
		logging.F("plugin_id", plugin.ID.String()),
		logging.F("success", result.Success),
		logging.F("duration", result.Duration.String()),
		logging.F("records_count", result.RecordsCount),
	)

	return result, nil
}

// executeTap executes a Singer tap (source plugin)
func (e *PluginExecutor) executeTap(ctx context.Context, plugin *entities.Plugin, execCtx *PluginExecutionContext, execDir string) (*ExecutionResult, error) {
	// Create tap configuration file
	configFile := filepath.Join(execDir, "tap_config.json")
	if err := e.writeConfig(configFile, execCtx.Config); err != nil {
		return nil, fmt.Errorf("failed to write tap config: %w", err)
	}

	// Create state file if needed
	stateFile := filepath.Join(execDir, "tap_state.json")
	if execCtx.InputData != nil && execCtx.InputData["state"] != nil {
		if err := e.writeConfig(stateFile, execCtx.InputData["state"]); err != nil {
			return nil, fmt.Errorf("failed to write tap state: %w", err)
		}
	}

	// Prepare tap command
	var cmd *exec.Cmd
	outputFile := filepath.Join(execDir, "tap_output.jsonl")

	if strings.HasPrefix(plugin.EntryPoint, "tap_") {
		// Singer tap via Python
		args := []string{"-m", plugin.EntryPoint, "--config", configFile}
		if _, err := os.Stat(stateFile); err == nil {
			args = append(args, "--state", stateFile)
		}
		
		cmd = exec.CommandContext(ctx, e.pythonPath, args...)
	} else {
		// Custom binary or script
		cmd = exec.CommandContext(ctx, plugin.EntryPoint, "--config", configFile)
	}

	// Set up environment
	cmd.Env = e.env
	cmd.Dir = execDir

	// Execute and capture output
	return e.executeCommand(cmd, outputFile, "tap")
}

// executeTarget executes a Singer target (destination plugin)
func (e *PluginExecutor) executeTarget(ctx context.Context, plugin *entities.Plugin, execCtx *PluginExecutionContext, execDir string) (*ExecutionResult, error) {
	// Create target configuration file
	configFile := filepath.Join(execDir, "target_config.json")
	if err := e.writeConfig(configFile, execCtx.Config); err != nil {
		return nil, fmt.Errorf("failed to write target config: %w", err)
	}

	// Prepare input data file
	inputFile := filepath.Join(execDir, "input.jsonl")
	if execCtx.InputData != nil && execCtx.InputData["records"] != nil {
		if err := e.writeJSONLData(inputFile, execCtx.InputData["records"]); err != nil {
			return nil, fmt.Errorf("failed to write input data: %w", err)
		}
	}

	// Prepare target command
	var cmd *exec.Cmd
	outputFile := filepath.Join(execDir, "target_output.log")

	if strings.HasPrefix(plugin.EntryPoint, "target_") {
		// Singer target via Python
		cmd = exec.CommandContext(ctx, e.pythonPath, "-m", plugin.EntryPoint, "--config", configFile)
	} else {
		// Custom binary or script
		cmd = exec.CommandContext(ctx, plugin.EntryPoint, "--config", configFile)
	}

	// Set up input redirection if we have input data
	if _, err := os.Stat(inputFile); err == nil {
		inputFileHandle, err := os.Open(inputFile)
		if err != nil {
			return nil, fmt.Errorf("failed to open input file: %w", err)
		}
		defer inputFileHandle.Close()
		cmd.Stdin = inputFileHandle
	}

	// Set up environment
	cmd.Env = e.env
	cmd.Dir = execDir

	return e.executeCommand(cmd, outputFile, "target")
}

// executeTransformer executes a data transformer plugin
func (e *PluginExecutor) executeTransformer(ctx context.Context, plugin *entities.Plugin, execCtx *PluginExecutionContext, execDir string) (*ExecutionResult, error) {
	// Create transformer configuration
	configFile := filepath.Join(execDir, "transform_config.json")
	if err := e.writeConfig(configFile, execCtx.Config); err != nil {
		return nil, fmt.Errorf("failed to write transformer config: %w", err)
	}

	// Prepare input data
	inputFile := filepath.Join(execDir, "transform_input.json")
	if execCtx.InputData != nil {
		if err := e.writeConfig(inputFile, execCtx.InputData); err != nil {
			return nil, fmt.Errorf("failed to write input data: %w", err)
		}
	}

	// Prepare transformer command
	outputFile := filepath.Join(execDir, "transform_output.json")
	cmd := exec.CommandContext(ctx, e.pythonPath, plugin.EntryPoint, 
		"--config", configFile, "--input", inputFile, "--output", outputFile)

	// Set up environment
	cmd.Env = e.env
	cmd.Dir = execDir

	return e.executeCommand(cmd, outputFile, "transformer")
}

// executeUtility executes a utility plugin
func (e *PluginExecutor) executeUtility(ctx context.Context, plugin *entities.Plugin, execCtx *PluginExecutionContext, execDir string) (*ExecutionResult, error) {
	// Create utility configuration
	configFile := filepath.Join(execDir, "utility_config.json")
	if err := e.writeConfig(configFile, execCtx.Config); err != nil {
		return nil, fmt.Errorf("failed to write utility config: %w", err)
	}

	// Prepare utility command
	outputFile := filepath.Join(execDir, "utility_output.log")
	cmd := exec.CommandContext(ctx, e.pythonPath, plugin.EntryPoint, "--config", configFile)

	// Set up environment
	cmd.Env = e.env
	cmd.Dir = execDir

	return e.executeCommand(cmd, outputFile, "utility")
}

// executeCommand executes a command and captures its output
func (e *PluginExecutor) executeCommand(cmd *exec.Cmd, outputFile, pluginType string) (*ExecutionResult, error) {
	// Set up output capture
	stdoutFile, err := os.Create(outputFile)
	if err != nil {
		return nil, fmt.Errorf("failed to create output file: %w", err)
	}
	defer stdoutFile.Close()

	stderrFile, err := os.Create(outputFile + ".err")
	if err != nil {
		return nil, fmt.Errorf("failed to create stderr file: %w", err)
	}
	defer stderrFile.Close()

	cmd.Stdout = stdoutFile
	cmd.Stderr = stderrFile

	// Execute command with timeout
	timeoutCtx, cancel := context.WithTimeout(context.Background(), e.timeout)
	defer cancel()
	
	// Store original values before recreating command
	originalDir := cmd.Dir
	originalEnv := cmd.Env
	cmd = exec.CommandContext(timeoutCtx, cmd.Path, cmd.Args[1:]...)
	cmd.Env = originalEnv
	cmd.Dir = originalDir

	startTime := time.Now()
	err = cmd.Run()
	duration := time.Since(startTime)

	// Read output files
	stdout, _ := os.ReadFile(outputFile)
	stderr, _ := os.ReadFile(outputFile + ".err")

	result := &ExecutionResult{
		Success:  err == nil,
		Stdout:   string(stdout),
		Stderr:   string(stderr),
		Duration: duration,
	}

	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			result.ExitCode = exitError.ExitCode()
		}
		result.Error = err.Error()
	}

	// Parse output data based on plugin type
	if result.Success {
		switch pluginType {
		case "tap":
			result.RecordsCount = e.countJSONLRecords(string(stdout))
			result.Data = map[string]interface{}{
				"records_extracted": result.RecordsCount,
				"output_format":     "singer_jsonl",
			}
		case "target":
			result.RecordsCount = e.parseTargetStats(string(stdout))
			result.Data = map[string]interface{}{
				"records_loaded": result.RecordsCount,
				"target_type":    "singer_target",
			}
		case "transformer":
			data, records := e.parseTransformerOutput(outputFile)
			result.Data = data
			result.RecordsCount = records
		case "utility":
			result.Data = map[string]interface{}{
				"utility_executed": true,
				"output_lines":     len(strings.Split(string(stdout), "\n")),
			}
		}
	}

	return result, nil
}

// Helper methods

func (e *PluginExecutor) writeConfig(filename string, config interface{}) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filename, data, 0644)
}

func (e *PluginExecutor) writeJSONLData(filename string, data interface{}) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	if records, ok := data.([]interface{}); ok {
		for _, record := range records {
			line, err := json.Marshal(record)
			if err != nil {
				continue
			}
			file.WriteString(string(line) + "\n")
		}
	}
	return nil
}

func (e *PluginExecutor) countJSONLRecords(output string) int {
	if output == "" {
		return 0
	}
	lines := strings.Split(strings.TrimSpace(output), "\n")
	count := 0
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line != "" && strings.HasPrefix(line, "{") {
			count++
		}
	}
	return count
}

func (e *PluginExecutor) parseTargetStats(output string) int {
	// Simple heuristic: count lines that mention "records" 
	lines := strings.Split(output, "\n")
	for _, line := range lines {
		if strings.Contains(line, "loaded") && strings.Contains(line, "records") {
			// Extract number if possible (basic implementation)
			return 1 // Placeholder - would need proper parsing
		}
	}
	return 0
}

func (e *PluginExecutor) parseTransformerOutput(outputFile string) (map[string]interface{}, int) {
	data := make(map[string]interface{})
	
	if content, err := os.ReadFile(outputFile); err == nil {
		var output map[string]interface{}
		if json.Unmarshal(content, &output) == nil {
			data = output
			if records, ok := output["records_processed"].(float64); ok {
				return data, int(records)
			}
		}
	}
	
	return data, 0
}

func (e *PluginExecutor) cleanup(execDir string) {
	// Clean up execution directory
	os.RemoveAll(execDir)
}