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

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// MeltanoExecutor executes Singer taps and targets via Meltano
type MeltanoExecutor struct {
	logger         logging.Logger
	meltanoPath    string
	projectPath    string
	workDir        string
	timeout        time.Duration
	env            []string
}

// MeltanoRunResult represents the result of a Meltano run
type MeltanoRunResult struct {
	Success       bool                   `json:"success"`
	ExitCode      int                    `json:"exit_code"`
	Duration      time.Duration          `json:"duration"`
	RecordsCount  int                    `json:"records_count"`
	TapName       string                 `json:"tap_name,omitempty"`
	TargetName    string                 `json:"target_name,omitempty"`
	StateFile     string                 `json:"state_file,omitempty"`
	LogFile       string                 `json:"log_file,omitempty"`
	OutputFile    string                 `json:"output_file,omitempty"`
	Logs          []string               `json:"logs"`
	Error         string                 `json:"error,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// MeltanoConfig represents Meltano pipeline configuration
type MeltanoConfig struct {
	TapName      string                 `json:"tap_name"`
	TargetName   string                 `json:"target_name,omitempty"`
	TapConfig    map[string]interface{} `json:"tap_config"`
	TargetConfig map[string]interface{} `json:"target_config,omitempty"`
	State        map[string]interface{} `json:"state,omitempty"`
	Environment  map[string]string      `json:"environment,omitempty"`
}

// NewMeltanoExecutor creates a new Meltano executor
func NewMeltanoExecutor(logger logging.Logger, meltanoPath, projectPath, workDir string) *MeltanoExecutor {
	return &MeltanoExecutor{
		logger:      logger,
		meltanoPath: meltanoPath,
		projectPath: projectPath,
		workDir:     workDir,
		timeout:     10 * time.Minute, // Default timeout
		env:         os.Environ(),
	}
}

// SetTimeout sets the execution timeout
func (e *MeltanoExecutor) SetTimeout(timeout time.Duration) {
	e.timeout = timeout
}

// SetEnvironment sets additional environment variables
func (e *MeltanoExecutor) SetEnvironment(env map[string]string) {
	e.env = os.Environ()
	for key, value := range env {
		e.env = append(e.env, fmt.Sprintf("%s=%s", key, value))
	}
}

// RunELTJob executes a complete ELT job with tap and target
func (e *MeltanoExecutor) RunELTJob(ctx context.Context, config *MeltanoConfig, executionID uuid.UUID) (*MeltanoRunResult, error) {
	startTime := time.Now()

	e.logger.Info("Starting Meltano ELT job",
		logging.F("execution_id", executionID.String()),
		logging.F("tap_name", config.TapName),
		logging.F("target_name", config.TargetName),
	)

	// Create execution directory
	execDir := filepath.Join(e.workDir, "meltano_executions", executionID.String())
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create execution directory: %w", err)
	}
	defer e.cleanup(execDir)

	// Set up Meltano project environment
	if err := e.setupMeltanoEnvironment(execDir, config); err != nil {
		return nil, fmt.Errorf("failed to setup Meltano environment: %w", err)
	}

	// Execute the ELT job
	result, err := e.executeMeltanoRun(ctx, config, execDir)
	if err != nil {
		e.logger.Error("Meltano ELT job failed",
			logging.F("execution_id", executionID.String()),
			logging.F("error", err.Error()),
		)
		return result, err
	}

	result.Duration = time.Since(startTime)

	e.logger.Info("Meltano ELT job completed",
		logging.F("execution_id", executionID.String()),
		logging.F("success", result.Success),
		logging.F("duration", result.Duration.String()),
		logging.F("records_count", result.RecordsCount),
	)

	return result, nil
}

// RunTapOnly executes only the tap (extractor) part
func (e *MeltanoExecutor) RunTapOnly(ctx context.Context, config *MeltanoConfig, executionID uuid.UUID) (*MeltanoRunResult, error) {
	startTime := time.Now()

	e.logger.Info("Starting Meltano tap execution",
		logging.F("execution_id", executionID.String()),
		logging.F("tap_name", config.TapName),
	)

	// Create execution directory
	execDir := filepath.Join(e.workDir, "meltano_executions", executionID.String())
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create execution directory: %w", err)
	}
	defer e.cleanup(execDir)

	// Set up Meltano environment
	if err := e.setupMeltanoEnvironment(execDir, config); err != nil {
		return nil, fmt.Errorf("failed to setup Meltano environment: %w", err)
	}

	// Execute only the tap
	result, err := e.executeMeltanoInvoke(ctx, config.TapName, config.TapConfig, execDir, "tap")
	if err != nil {
		return result, err
	}

	result.Duration = time.Since(startTime)
	result.TapName = config.TapName

	e.logger.Info("Meltano tap execution completed",
		logging.F("execution_id", executionID.String()),
		logging.F("success", result.Success),
		logging.F("records_count", result.RecordsCount),
	)

	return result, nil
}

// RunTargetOnly executes only the target (loader) part with provided data
func (e *MeltanoExecutor) RunTargetOnly(ctx context.Context, config *MeltanoConfig, inputData []interface{}, executionID uuid.UUID) (*MeltanoRunResult, error) {
	startTime := time.Now()

	e.logger.Info("Starting Meltano target execution",
		logging.F("execution_id", executionID.String()),
		logging.F("target_name", config.TargetName),
		logging.F("input_records", len(inputData)),
	)

	// Create execution directory
	execDir := filepath.Join(e.workDir, "meltano_executions", executionID.String())
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create execution directory: %w", err)
	}
	defer e.cleanup(execDir)

	// Prepare input data file
	inputFile := filepath.Join(execDir, "input.jsonl")
	if err := e.writeJSONLData(inputFile, inputData); err != nil {
		return nil, fmt.Errorf("failed to write input data: %w", err)
	}

	// Set up Meltano environment
	if err := e.setupMeltanoEnvironment(execDir, config); err != nil {
		return nil, fmt.Errorf("failed to setup Meltano environment: %w", err)
	}

	// Execute the target with input data
	result, err := e.executeMeltanoTarget(ctx, config.TargetName, config.TargetConfig, inputFile, execDir)
	if err != nil {
		return result, err
	}

	result.Duration = time.Since(startTime)
	result.TargetName = config.TargetName

	e.logger.Info("Meltano target execution completed",
		logging.F("execution_id", executionID.String()),
		logging.F("success", result.Success),
		logging.F("records_processed", result.RecordsCount),
	)

	return result, nil
}

// setupMeltanoEnvironment sets up the Meltano project environment
func (e *MeltanoExecutor) setupMeltanoEnvironment(execDir string, config *MeltanoConfig) error {
	// Create config files
	if err := e.createTapConfig(execDir, config.TapName, config.TapConfig); err != nil {
		return fmt.Errorf("failed to create tap config: %w", err)
	}

	if config.TargetName != "" && config.TargetConfig != nil {
		if err := e.createTargetConfig(execDir, config.TargetName, config.TargetConfig); err != nil {
			return fmt.Errorf("failed to create target config: %w", err)
		}
	}

	// Create state file if provided
	if config.State != nil {
		stateFile := filepath.Join(execDir, "state.json")
		if err := e.writeConfig(stateFile, config.State); err != nil {
			return fmt.Errorf("failed to create state file: %w", err)
		}
	}

	// Set up environment variables
	if config.Environment != nil {
		for key, value := range config.Environment {
			e.env = append(e.env, fmt.Sprintf("%s=%s", key, value))
		}
	}

	return nil
}

// executeMeltanoRun executes a full Meltano run command
func (e *MeltanoExecutor) executeMeltanoRun(ctx context.Context, config *MeltanoConfig, execDir string) (*MeltanoRunResult, error) {
	// Prepare Meltano run command
	args := []string{"run"}
	
	// Add tap and target
	if config.TargetName != "" {
		args = append(args, fmt.Sprintf("%s:%s", config.TapName, config.TargetName))
	} else {
		args = append(args, config.TapName)
	}

	// Set up output and log files
	outputFile := filepath.Join(execDir, "meltano_output.log")
	logFile := filepath.Join(execDir, "meltano.log")

	// Create command
	cmd := exec.CommandContext(ctx, e.meltanoPath, args...)
	cmd.Dir = e.projectPath
	cmd.Env = e.env

	// Execute command
	result, err := e.executeCommand(cmd, outputFile, logFile)
	if err != nil {
		return result, err
	}

	// Parse Meltano output for metrics
	e.parseMeltanoOutput(result, outputFile, logFile)

	return result, nil
}

// executeMeltanoInvoke executes a Meltano invoke command for a single plugin
func (e *MeltanoExecutor) executeMeltanoInvoke(ctx context.Context, pluginName string, pluginConfig map[string]interface{}, execDir, pluginType string) (*MeltanoRunResult, error) {
	// Create config file
	configFile := filepath.Join(execDir, fmt.Sprintf("%s_config.json", pluginType))
	if err := e.writeConfig(configFile, pluginConfig); err != nil {
		return nil, fmt.Errorf("failed to write plugin config: %w", err)
	}

	// Prepare Meltano invoke command
	args := []string{"invoke", pluginName}
	if pluginType == "tap" {
		args = append(args, "--dump=catalog")
	}

	// Set up output files
	outputFile := filepath.Join(execDir, fmt.Sprintf("%s_output.jsonl", pluginType))
	logFile := filepath.Join(execDir, fmt.Sprintf("%s.log", pluginType))

	// Create command
	cmd := exec.CommandContext(ctx, e.meltanoPath, args...)
	cmd.Dir = e.projectPath
	cmd.Env = e.env

	// Execute command
	result, err := e.executeCommand(cmd, outputFile, logFile)
	if err != nil {
		return result, err
	}

	// Parse output
	if pluginType == "tap" {
		result.RecordsCount = e.countJSONLRecords(outputFile)
		result.OutputFile = outputFile
	}

	return result, nil
}

// executeMeltanoTarget executes a target with input data
func (e *MeltanoExecutor) executeMeltanoTarget(ctx context.Context, targetName string, targetConfig map[string]interface{}, inputFile, execDir string) (*MeltanoRunResult, error) {
	// Create target config file
	configFile := filepath.Join(execDir, "target_config.json")
	if err := e.writeConfig(configFile, targetConfig); err != nil {
		return nil, fmt.Errorf("failed to write target config: %w", err)
	}

	// Prepare Meltano invoke command for target
	args := []string{"invoke", targetName}

	// Set up files
	outputFile := filepath.Join(execDir, "target_output.log")
	logFile := filepath.Join(execDir, "target.log")

	// Create command with input redirection
	cmd := exec.CommandContext(ctx, e.meltanoPath, args...)
	cmd.Dir = e.projectPath
	cmd.Env = e.env

	// Set up input redirection
	inputFileHandle, err := os.Open(inputFile)
	if err != nil {
		return nil, fmt.Errorf("failed to open input file: %w", err)
	}
	defer inputFileHandle.Close()
	cmd.Stdin = inputFileHandle

	// Execute command
	result, err := e.executeCommand(cmd, outputFile, logFile)
	if err != nil {
		return result, err
	}

	// Parse target output for records processed
	result.RecordsCount = e.parseTargetOutput(outputFile)

	return result, nil
}

// executeCommand executes a command and captures output
func (e *MeltanoExecutor) executeCommand(cmd *exec.Cmd, outputFile, logFile string) (*MeltanoRunResult, error) {
	// Create output files
	outFile, err := os.Create(outputFile)
	if err != nil {
		return nil, fmt.Errorf("failed to create output file: %w", err)
	}
	defer outFile.Close()

	errFile, err := os.Create(logFile)
	if err != nil {
		return nil, fmt.Errorf("failed to create log file: %w", err)
	}
	defer errFile.Close()

	cmd.Stdout = outFile
	cmd.Stderr = errFile

	// Set timeout
	timeoutCtx, cancel := context.WithTimeout(context.Background(), e.timeout)
	defer cancel()
	cmd = exec.CommandContext(timeoutCtx, cmd.Path, cmd.Args[1:]...)
	cmd.Dir = cmd.Dir
	cmd.Env = cmd.Env

	// Execute
	err = cmd.Run()

	// Read output files
	stdout, _ := os.ReadFile(outputFile)
	stderr, _ := os.ReadFile(logFile)

	result := &MeltanoRunResult{
		Success:    err == nil,
		LogFile:    logFile,
		OutputFile: outputFile,
		Logs:       e.parseLogLines(string(stderr)),
		Metadata:   make(map[string]interface{}),
	}

	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			result.ExitCode = exitError.ExitCode()
		}
		result.Error = err.Error()
	}

	// Add stdout to logs if not empty
	if len(stdout) > 0 {
		result.Logs = append(result.Logs, fmt.Sprintf("STDOUT: %s", string(stdout)))
	}

	return result, nil
}

// Helper methods

func (e *MeltanoExecutor) createTapConfig(execDir, tapName string, config map[string]interface{}) error {
	configFile := filepath.Join(execDir, fmt.Sprintf("%s_config.json", tapName))
	return e.writeConfig(configFile, config)
}

func (e *MeltanoExecutor) createTargetConfig(execDir, targetName string, config map[string]interface{}) error {
	configFile := filepath.Join(execDir, fmt.Sprintf("%s_config.json", targetName))
	return e.writeConfig(configFile, config)
}

func (e *MeltanoExecutor) writeConfig(filename string, config interface{}) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filename, data, 0644)
}

func (e *MeltanoExecutor) writeJSONLData(filename string, data []interface{}) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	for _, record := range data {
		line, err := json.Marshal(record)
		if err != nil {
			continue
		}
		file.WriteString(string(line) + "\n")
	}
	return nil
}

func (e *MeltanoExecutor) countJSONLRecords(filename string) int {
	content, err := os.ReadFile(filename)
	if err != nil {
		return 0
	}

	lines := strings.Split(strings.TrimSpace(string(content)), "\n")
	count := 0
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line != "" && (strings.HasPrefix(line, "{") || strings.HasPrefix(line, "[")) {
			count++
		}
	}
	return count
}

func (e *MeltanoExecutor) parseTargetOutput(filename string) int {
	content, err := os.ReadFile(filename)
	if err != nil {
		return 0
	}

	// Look for Meltano success messages
	output := string(content)
	if strings.Contains(output, "records") {
		// Simple heuristic - in real implementation would parse properly
		return 1
	}
	return 0
}

func (e *MeltanoExecutor) parseLogLines(logs string) []string {
	if logs == "" {
		return []string{}
	}
	return strings.Split(strings.TrimSpace(logs), "\n")
}

func (e *MeltanoExecutor) parseMeltanoOutput(result *MeltanoRunResult, outputFile, logFile string) {
	// Read and parse output files for Meltano-specific metrics
	if content, err := os.ReadFile(outputFile); err == nil {
		output := string(content)
		
		// Extract records count from Meltano output
		result.RecordsCount = e.countJSONLRecords(outputFile)
		
		// Add metadata
		result.Metadata["output_size"] = len(content)
		result.Metadata["has_catalog"] = strings.Contains(output, "catalog")
		result.Metadata["has_records"] = strings.Contains(output, "RECORD")
	}

	// Parse log file for additional information
	if content, err := os.ReadFile(logFile); err == nil {
		logs := string(content)
		result.Metadata["log_size"] = len(content)
		result.Metadata["has_errors"] = strings.Contains(logs, "ERROR")
		result.Metadata["has_warnings"] = strings.Contains(logs, "WARNING")
	}
}

func (e *MeltanoExecutor) cleanup(execDir string) {
	// Clean up execution directory
	os.RemoveAll(execDir)
}