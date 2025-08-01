package dbt

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// DBTManager manages dbt project operations
type DBTManager struct {
	projectPath   string
	profilesDir   string
	logger        logging.Logger
	pythonPath    string
	dbtPath       string
	venvPath      string
	defaultTarget string
}

// DBTConfig represents dbt configuration
type DBTConfig struct {
	ProjectPath   string `json:"project_path"`
	ProfilesDir   string `json:"profiles_dir"`
	PythonPath    string `json:"python_path"`
	DBTPath       string `json:"dbt_path"`
	VenvPath      string `json:"venv_path"`
	DefaultTarget string `json:"default_target"`
}

// DBTRunResult represents the result of a dbt command execution
type DBTRunResult struct {
	ID          uuid.UUID              `json:"id"`
	Command     string                 `json:"command"`
	Args        []string               `json:"args"`
	ExitCode    int                    `json:"exit_code"`
	Success     bool                   `json:"success"`
	Duration    time.Duration          `json:"duration"`
	Output      string                 `json:"output"`
	ErrorOutput string                 `json:"error_output"`
	Models      []DBTModelResult       `json:"models,omitempty"`
	Tests       []DBTTestResult        `json:"tests,omitempty"`
	Metadata    map[string]interface{} `json:"metadata"`
	StartedAt   time.Time              `json:"started_at"`
	CompletedAt time.Time              `json:"completed_at"`
}

// DBTModelResult represents the result of a dbt model execution
type DBTModelResult struct {
	Name          string                 `json:"name"`
	Status        string                 `json:"status"`
	ExecutionTime float64                `json:"execution_time"`
	RowsAffected  int64                  `json:"rows_affected"`
	ErrorMessage  string                 `json:"error_message,omitempty"`
	Metadata      map[string]interface{} `json:"metadata"`
}

// DBTTestResult represents the result of a dbt test execution
type DBTTestResult struct {
	Name         string                 `json:"name"`
	Status       string                 `json:"status"`
	ErrorMessage string                 `json:"error_message,omitempty"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// DBTProjectInfo represents dbt project information
type DBTProjectInfo struct {
	Name        string            `json:"name"`
	Version     string            `json:"version"`
	ProfileName string            `json:"profile_name"`
	ModelPaths  []string          `json:"model_paths"`
	TestPaths   []string          `json:"test_paths"`
	MacroPaths  []string          `json:"macro_paths"`
	Vars        map[string]string `json:"vars"`
}

// NewDBTManager creates a new dbt manager
func NewDBTManager(config *DBTConfig, logger logging.Logger) (*DBTManager, error) {
	if config == nil {
		config = &DBTConfig{
			ProjectPath:   "./dbt_project",
			ProfilesDir:   "~/.dbt",
			PythonPath:    "python3",
			DBTPath:       "dbt",
			DefaultTarget: "dev",
		}
	}

	manager := &DBTManager{
		projectPath:   config.ProjectPath,
		profilesDir:   config.ProfilesDir,
		logger:        logger,
		pythonPath:    config.PythonPath,
		dbtPath:       config.DBTPath,
		venvPath:      config.VenvPath,
		defaultTarget: config.DefaultTarget,
	}

	// Validate dbt installation
	if err := manager.validateInstallation(); err != nil {
		return nil, fmt.Errorf("dbt validation failed: %w", err)
	}

	return manager, nil
}

// validateInstallation checks if dbt is properly installed and accessible
func (dm *DBTManager) validateInstallation() error {
	// Check if dbt command is available
	cmd := exec.Command(dm.dbtPath, "--version")
	if dm.venvPath != "" {
		cmd.Env = append(os.Environ(), fmt.Sprintf("PATH=%s/bin:%s", dm.venvPath, os.Getenv("PATH")))
	}

	output, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("dbt not found or not executable: %w", err)
	}

	dm.logger.Info("DBT installation validated",
		logging.F("version_output", strings.TrimSpace(string(output))),
	)

	return nil
}

// InitProject initializes a new dbt project
func (dm *DBTManager) InitProject(ctx context.Context, projectName string) (*DBTRunResult, error) {
	result := &DBTRunResult{
		ID:        uuid.New(),
		Command:   "init",
		Args:      []string{projectName},
		StartedAt: time.Now(),
		Metadata:  make(map[string]interface{}),
	}

	// Create project directory if it doesn't exist
	if err := os.MkdirAll(dm.projectPath, 0755); err != nil {
		return nil, fmt.Errorf("failed to create project directory: %w", err)
	}

	// Run dbt init command
	cmd := exec.CommandContext(ctx, dm.dbtPath, "init", projectName)
	cmd.Dir = dm.projectPath
	if dm.profilesDir != "" {
		cmd.Env = append(os.Environ(), fmt.Sprintf("DBT_PROFILES_DIR=%s", dm.profilesDir))
	}

	output, err := cmd.CombinedOutput()
	result.CompletedAt = time.Now()
	result.Duration = result.CompletedAt.Sub(result.StartedAt)
	result.Output = string(output)

	if err != nil {
		result.Success = false
		result.ErrorOutput = err.Error()
		result.ExitCode = 1
		return result, fmt.Errorf("dbt init failed: %w", err)
	}

	result.Success = true
	result.ExitCode = 0

	dm.logger.Info("DBT project initialized",
		logging.F("project_name", projectName),
		logging.F("duration", result.Duration.String()),
	)

	return result, nil
}

// Run executes dbt run command
func (dm *DBTManager) Run(ctx context.Context, models []string, target string) (*DBTRunResult, error) {
	args := []string{"run"}

	if target == "" {
		target = dm.defaultTarget
	}
	args = append(args, "--target", target)

	if len(models) > 0 {
		args = append(args, "--models", strings.Join(models, ","))
	}

	return dm.executeCommand(ctx, args)
}

// Test executes dbt test command
func (dm *DBTManager) Test(ctx context.Context, models []string, target string) (*DBTRunResult, error) {
	args := []string{"test"}

	if target == "" {
		target = dm.defaultTarget
	}
	args = append(args, "--target", target)

	if len(models) > 0 {
		args = append(args, "--models", strings.Join(models, ","))
	}

	return dm.executeCommand(ctx, args)
}

// Compile executes dbt compile command
func (dm *DBTManager) Compile(ctx context.Context, models []string, target string) (*DBTRunResult, error) {
	args := []string{"compile"}

	if target == "" {
		target = dm.defaultTarget
	}
	args = append(args, "--target", target)

	if len(models) > 0 {
		args = append(args, "--models", strings.Join(models, ","))
	}

	return dm.executeCommand(ctx, args)
}

// Docs generates dbt documentation
func (dm *DBTManager) Docs(ctx context.Context, serve bool, port int) (*DBTRunResult, error) {
	args := []string{"docs", "generate"}

	result, err := dm.executeCommand(ctx, args)
	if err != nil {
		return result, err
	}

	if serve {
		serveArgs := []string{"docs", "serve"}
		if port > 0 {
			serveArgs = append(serveArgs, "--port", fmt.Sprintf("%d", port))
		}

		// Start docs server in background
		go func() {
			serveResult, err := dm.executeCommand(context.Background(), serveArgs)
			if err != nil {
				dm.logger.Error("Failed to serve dbt docs",
					logging.F("error", err.Error()),
				)
			} else {
				dm.logger.Info("DBT docs server started",
					logging.F("port", port),
					logging.F("result", serveResult.Output),
				)
			}
		}()
	}

	return result, nil
}

// Seed executes dbt seed command
func (dm *DBTManager) Seed(ctx context.Context, seeds []string, target string) (*DBTRunResult, error) {
	args := []string{"seed"}

	if target == "" {
		target = dm.defaultTarget
	}
	args = append(args, "--target", target)

	if len(seeds) > 0 {
		args = append(args, "--select", strings.Join(seeds, ","))
	}

	return dm.executeCommand(ctx, args)
}

// Snapshot executes dbt snapshot command
func (dm *DBTManager) Snapshot(ctx context.Context, snapshots []string, target string) (*DBTRunResult, error) {
	args := []string{"snapshot"}

	if target == "" {
		target = dm.defaultTarget
	}
	args = append(args, "--target", target)

	if len(snapshots) > 0 {
		args = append(args, "--select", strings.Join(snapshots, ","))
	}

	return dm.executeCommand(ctx, args)
}

// GetProjectInfo retrieves dbt project information
func (dm *DBTManager) GetProjectInfo(ctx context.Context) (*DBTProjectInfo, error) {
	projectFilePath := filepath.Join(dm.projectPath, "dbt_project.yml")

	// Check if project file exists
	if _, err := os.Stat(projectFilePath); os.IsNotExist(err) {
		return nil, fmt.Errorf("dbt_project.yml not found at %s", projectFilePath)
	}

	// Parse project file (simplified - in real implementation would use YAML parser)
	info := &DBTProjectInfo{
		Name:        "flext_dbt_project",
		Version:     "1.0.0",
		ProfileName: "flext",
		ModelPaths:  []string{"models"},
		TestPaths:   []string{"tests"},
		MacroPaths:  []string{"macros"},
		Vars:        make(map[string]string),
	}

	return info, nil
}

// ListModels lists all available dbt models
func (dm *DBTManager) ListModels(ctx context.Context) ([]string, error) {
	result, err := dm.executeCommand(ctx, []string{"list", "--resource-type", "model"})
	if err != nil {
		return nil, err
	}

	models := strings.Split(strings.TrimSpace(result.Output), "\n")
	var filteredModels []string
	for _, model := range models {
		model = strings.TrimSpace(model)
		if model != "" && !strings.HasPrefix(model, "WARNING") {
			filteredModels = append(filteredModels, model)
		}
	}

	return filteredModels, nil
}

// ListTests lists all available dbt tests
func (dm *DBTManager) ListTests(ctx context.Context) ([]string, error) {
	result, err := dm.executeCommand(ctx, []string{"list", "--resource-type", "test"})
	if err != nil {
		return nil, err
	}

	tests := strings.Split(strings.TrimSpace(result.Output), "\n")
	var filteredTests []string
	for _, test := range tests {
		test = strings.TrimSpace(test)
		if test != "" && !strings.HasPrefix(test, "WARNING") {
			filteredTests = append(filteredTests, test)
		}
	}

	return filteredTests, nil
}

// GetRunHistory retrieves dbt run history
func (dm *DBTManager) GetRunHistory(ctx context.Context, limit int) ([]*DBTRunResult, error) {
	// In a real implementation, this would query a database or log files
	// For now, returning empty slice
	return []*DBTRunResult{}, nil
}

// executeCommand executes a dbt command and returns the result
func (dm *DBTManager) executeCommand(ctx context.Context, args []string) (*DBTRunResult, error) {
	result := &DBTRunResult{
		ID:        uuid.New(),
		Command:   dm.dbtPath,
		Args:      args,
		StartedAt: time.Now(),
		Metadata:  make(map[string]interface{}),
	}

	cmd := exec.CommandContext(ctx, dm.dbtPath, args...)
	cmd.Dir = dm.projectPath

	// Set environment variables
	env := os.Environ()
	if dm.profilesDir != "" {
		env = append(env, fmt.Sprintf("DBT_PROFILES_DIR=%s", dm.profilesDir))
	}
	if dm.venvPath != "" {
		env = append(env, fmt.Sprintf("PATH=%s/bin:%s", dm.venvPath, os.Getenv("PATH")))
	}
	cmd.Env = env

	output, err := cmd.CombinedOutput()
	result.CompletedAt = time.Now()
	result.Duration = result.CompletedAt.Sub(result.StartedAt)
	result.Output = string(output)

	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			result.ExitCode = exitError.ExitCode()
		} else {
			result.ExitCode = 1
		}
		result.Success = false
		result.ErrorOutput = err.Error()

		dm.logger.Error("DBT command failed",
			logging.F("command", strings.Join(args, " ")),
			logging.F("exit_code", result.ExitCode),
			logging.F("error", err.Error()),
		)

		return result, fmt.Errorf("dbt command failed: %w", err)
	}

	result.Success = true
	result.ExitCode = 0

	// Parse output for model and test results
	dm.parseResults(result)

	dm.logger.Info("DBT command completed successfully",
		logging.F("command", strings.Join(args, " ")),
		logging.F("duration", result.Duration.String()),
	)

	return result, nil
}

// parseResults parses dbt command output for structured results
func (dm *DBTManager) parseResults(result *DBTRunResult) {
	// Parse JSON output if available (dbt --output json)
	lines := strings.Split(result.Output, "\n")

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "{") && strings.HasSuffix(line, "}") {
			// Try to parse as JSON
			var jsonResult map[string]interface{}
			if err := json.Unmarshal([]byte(line), &jsonResult); err == nil {
				if resourceType, ok := jsonResult["resource_type"].(string); ok {
					switch resourceType {
					case "model":
						model := dm.parseModelResult(jsonResult)
						result.Models = append(result.Models, model)
					case "test":
						test := dm.parseTestResult(jsonResult)
						result.Tests = append(result.Tests, test)
					}
				}
			}
		}
	}
}

// parseModelResult parses a model result from JSON
func (dm *DBTManager) parseModelResult(data map[string]interface{}) DBTModelResult {
	model := DBTModelResult{
		Metadata: make(map[string]interface{}),
	}

	if name, ok := data["unique_id"].(string); ok {
		model.Name = name
	}
	if status, ok := data["status"].(string); ok {
		model.Status = status
	}
	if execTime, ok := data["execution_time"].(float64); ok {
		model.ExecutionTime = execTime
	}

	return model
}

// parseTestResult parses a test result from JSON
func (dm *DBTManager) parseTestResult(data map[string]interface{}) DBTTestResult {
	test := DBTTestResult{
		Metadata: make(map[string]interface{}),
	}

	if name, ok := data["unique_id"].(string); ok {
		test.Name = name
	}
	if status, ok := data["status"].(string); ok {
		test.Status = status
	}

	return test
}

// CreateProfile creates a dbt profile configuration
func (dm *DBTManager) CreateProfile(profileName string, config map[string]interface{}) error {
	profilesDir := dm.profilesDir
	if profilesDir == "" {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return fmt.Errorf("failed to get home directory: %w", err)
		}
		profilesDir = filepath.Join(homeDir, ".dbt")
	}

	// Ensure profiles directory exists
	if err := os.MkdirAll(profilesDir, 0755); err != nil {
		return fmt.Errorf("failed to create profiles directory: %w", err)
	}

	profilesFile := filepath.Join(profilesDir, "profiles.yml")

	// Create a basic profile (in real implementation would use YAML library)
	profileContent := fmt.Sprintf(`
%s:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: postgres
      password: password
      port: 5432
      dbname: postgres
      schema: public
      threads: 1
      keepalives_idle: 0
`, profileName)

	if err := os.WriteFile(profilesFile, []byte(profileContent), 0644); err != nil {
		return fmt.Errorf("failed to write profiles.yml: %w", err)
	}

	dm.logger.Info("DBT profile created",
		logging.F("profile_name", profileName),
		logging.F("profiles_file", profilesFile),
	)

	return nil
}

// CheckConnection tests dbt database connection
func (dm *DBTManager) CheckConnection(ctx context.Context, target string) (*DBTRunResult, error) {
	args := []string{"debug"}

	if target != "" {
		args = append(args, "--target", target)
	}

	return dm.executeCommand(ctx, args)
}
