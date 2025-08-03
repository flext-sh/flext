package services

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/flext-sh/flext/pkg/domain/dbt/domain/entities"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// DbtExecutor executa comandos dbt
type DbtExecutor struct {
	logger      logging.Logger
	dbtPath     string
	pythonPath  string
	workingDir  string
	defaultVenv string
}

// DbtRunOptions opções para execução dbt
type DbtRunOptions struct {
	Models        []string          `json:"models,omitempty"`
	Exclude       []string          `json:"exclude,omitempty"`
	Select        []string          `json:"select,omitempty"`
	FullRefresh   bool              `json:"full_refresh,omitempty"`
	Vars          map[string]string `json:"vars,omitempty"`
	Threads       int               `json:"threads,omitempty"`
	Profiles      string            `json:"profiles,omitempty"`
	Target        string            `json:"target,omitempty"`
	FailFast      bool              `json:"fail_fast,omitempty"`
	StoreFailures bool              `json:"store_failures,omitempty"`
	WarnError     bool              `json:"warn_error,omitempty"`
}

// DbtTestOptions opções para testes dbt
type DbtTestOptions struct {
	Models        []string          `json:"models,omitempty"`
	Select        []string          `json:"select,omitempty"`
	Exclude       []string          `json:"exclude,omitempty"`
	Vars          map[string]string `json:"vars,omitempty"`
	Threads       int               `json:"threads,omitempty"`
	Profiles      string            `json:"profiles,omitempty"`
	Target        string            `json:"target,omitempty"`
	FailFast      bool              `json:"fail_fast,omitempty"`
	StoreFailures bool              `json:"store_failures,omitempty"`
	WarnError     bool              `json:"warn_error,omitempty"`
}

// DbtRunResult resultado da execução dbt
type DbtRunResult struct {
	RunID      uuid.UUID           `json:"run_id"`
	ProjectID  uuid.UUID           `json:"project_id"`
	Command    string              `json:"command"`
	Args       []string            `json:"args"`
	ExitCode   int                 `json:"exit_code"`
	Success    bool                `json:"success"`
	StartTime  time.Time           `json:"start_time"`
	EndTime    time.Time           `json:"end_time"`
	Duration   time.Duration       `json:"duration"`
	Stdout     string              `json:"stdout"`
	Stderr     string              `json:"stderr"`
	Results    []DbtNodeResult     `json:"results"`
	Metrics    DbtExecutionMetrics `json:"metrics"`
	Manifest   *DbtManifest        `json:"manifest,omitempty"`
	RunResults *DbtRunResultsJson  `json:"run_results,omitempty"`
}

// DbtNodeResult resultado de um nó (model, test, etc.)
type DbtNodeResult struct {
	UniqueID      string      `json:"unique_id"`
	Name          string      `json:"name"`
	Status        string      `json:"status"`
	ExecutionTime float64     `json:"execution_time"`
	RowsAffected  *int64      `json:"rows_affected,omitempty"`
	Message       string      `json:"message,omitempty"`
	Failures      int         `json:"failures,omitempty"`
	Thread        string      `json:"thread,omitempty"`
	Timing        []DbtTiming `json:"timing"`
}

// DbtTiming informações de timing
type DbtTiming struct {
	Name        string    `json:"name"`
	StartedAt   time.Time `json:"started_at"`
	CompletedAt time.Time `json:"completed_at"`
}

// DbtExecutionMetrics métricas de execução
type DbtExecutionMetrics struct {
	ModelsRun    int     `json:"models_run"`
	TestsRun     int     `json:"tests_run"`
	SeedsRun     int     `json:"seeds_run"`
	SnapshotsRun int     `json:"snapshots_run"`
	Errors       int     `json:"errors"`
	Warnings     int     `json:"warnings"`
	Skipped      int     `json:"skipped"`
	TotalNodes   int     `json:"total_nodes"`
	SuccessRate  float64 `json:"success_rate"`
}

// DbtManifest representa o manifest.json do dbt
type DbtManifest struct {
	Metadata  DbtMetadata          `json:"metadata"`
	Nodes     map[string]DbtNode   `json:"nodes"`
	Sources   map[string]DbtSource `json:"sources"`
	Macros    map[string]DbtMacro  `json:"macros"`
	ParentMap map[string][]string  `json:"parent_map"`
	ChildMap  map[string][]string  `json:"child_map"`
}

// DbtMetadata metadados do manifest
type DbtMetadata struct {
	DbtVersion   string            `json:"dbt_version"`
	GeneratedAt  time.Time         `json:"generated_at"`
	InvocationID string            `json:"invocation_id"`
	EnvVars      map[string]string `json:"env_vars"`
}

// DbtNode representa um nó no manifest
type DbtNode struct {
	UniqueID     string                 `json:"unique_id"`
	Name         string                 `json:"name"`
	ResourceType string                 `json:"resource_type"`
	PackageName  string                 `json:"package_name"`
	Path         string                 `json:"path"`
	OriginalPath string                 `json:"original_file_path"`
	Database     string                 `json:"database"`
	Schema       string                 `json:"schema"`
	Alias        string                 `json:"alias"`
	Description  string                 `json:"description"`
	Config       map[string]interface{} `json:"config"`
	Tags         []string               `json:"tags"`
	Refs         [][]string             `json:"refs"`
	Sources      [][]string             `json:"sources"`
	DependsOn    DbtDependsOn           `json:"depends_on"`
}

// DbtSource representa uma source no manifest
type DbtSource struct {
	UniqueID    string                 `json:"unique_id"`
	Name        string                 `json:"name"`
	SourceName  string                 `json:"source_name"`
	Database    string                 `json:"database"`
	Schema      string                 `json:"schema"`
	Identifier  string                 `json:"identifier"`
	Description string                 `json:"description"`
	Columns     map[string]interface{} `json:"columns"`
	Meta        map[string]interface{} `json:"meta"`
	Tags        []string               `json:"tags"`
}

// DbtMacro representa um macro no manifest
type DbtMacro struct {
	UniqueID    string                 `json:"unique_id"`
	Name        string                 `json:"name"`
	PackageName string                 `json:"package_name"`
	Path        string                 `json:"path"`
	Description string                 `json:"description"`
	Arguments   []DbtMacroArg          `json:"arguments"`
	Meta        map[string]interface{} `json:"meta"`
	Tags        []string               `json:"tags"`
}

// DbtMacroArg argumento de macro
type DbtMacroArg struct {
	Name        string      `json:"name"`
	Type        string      `json:"type"`
	Description string      `json:"description"`
	Default     interface{} `json:"default"`
}

// DbtDependsOn dependências de um nó
type DbtDependsOn struct {
	Macros []string `json:"macros"`
	Nodes  []string `json:"nodes"`
}

// DbtRunResultsJson resultado completo da execução
type DbtRunResultsJson struct {
	Metadata    DbtMetadata            `json:"metadata"`
	Results     []DbtNodeResult        `json:"results"`
	ElapsedTime float64                `json:"elapsed_time"`
	Args        map[string]interface{} `json:"args"`
}

// NewDbtExecutor cria um novo executor dbt
func NewDbtExecutor(logger logging.Logger, dbtPath, pythonPath, workingDir string) *DbtExecutor {
	if dbtPath == "" {
		dbtPath = "dbt" // Usar dbt do PATH
	}
	if pythonPath == "" {
		pythonPath = "python3" // Usar python3 do PATH
	}
	if workingDir == "" {
		workingDir = "/tmp/dbt-workspace"
	}

	return &DbtExecutor{
		logger:     logger,
		dbtPath:    dbtPath,
		pythonPath: pythonPath,
		workingDir: workingDir,
	}
}

// Run executa dbt run
func (e *DbtExecutor) Run(
	ctx context.Context,
	project *entities.DbtProject,
	options DbtRunOptions,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt run",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	// Construir argumentos do comando
	args := []string{"run"}
	args = append(args, e.buildCommonArgs(options.Models, options.Exclude, options.Select, options.Vars, options.Threads, options.Profiles, options.Target)...)

	if options.FullRefresh {
		args = append(args, "--full-refresh")
	}
	if options.FailFast {
		args = append(args, "--fail-fast")
	}
	if options.StoreFailures {
		args = append(args, "--store-failures")
	}
	if options.WarnError {
		args = append(args, "--warn-error")
	}

	return e.executeCommand(ctx, project, "run", args)
}

// Test executa dbt test
func (e *DbtExecutor) Test(
	ctx context.Context,
	project *entities.DbtProject,
	options DbtTestOptions,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt test",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	// Construir argumentos do comando
	args := []string{"test"}
	args = append(args, e.buildCommonArgs(options.Models, options.Exclude, options.Select, options.Vars, options.Threads, options.Profiles, options.Target)...)

	if options.FailFast {
		args = append(args, "--fail-fast")
	}
	if options.StoreFailures {
		args = append(args, "--store-failures")
	}
	if options.WarnError {
		args = append(args, "--warn-error")
	}

	return e.executeCommand(ctx, project, "test", args)
}

// Compile executa dbt compile
func (e *DbtExecutor) Compile(
	ctx context.Context,
	project *entities.DbtProject,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt compile",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"compile"}
	return e.executeCommand(ctx, project, "compile", args)
}

// Parse executa dbt parse
func (e *DbtExecutor) Parse(
	ctx context.Context,
	project *entities.DbtProject,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt parse",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"parse"}
	return e.executeCommand(ctx, project, "parse", args)
}

// Seed executa dbt seed
func (e *DbtExecutor) Seed(
	ctx context.Context,
	project *entities.DbtProject,
	models []string,
	fullRefresh bool,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt seed",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"seed"}
	if len(models) > 0 {
		args = append(args, "--select", strings.Join(models, " "))
	}
	if fullRefresh {
		args = append(args, "--full-refresh")
	}

	return e.executeCommand(ctx, project, "seed", args)
}

// Snapshot executa dbt snapshot
func (e *DbtExecutor) Snapshot(
	ctx context.Context,
	project *entities.DbtProject,
	selectModels []string,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt snapshot",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"snapshot"}
	if len(selectModels) > 0 {
		args = append(args, "--select", strings.Join(selectModels, " "))
	}

	return e.executeCommand(ctx, project, "snapshot", args)
}

// Debug executa dbt debug
func (e *DbtExecutor) Debug(
	ctx context.Context,
	project *entities.DbtProject,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt debug",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"debug"}
	return e.executeCommand(ctx, project, "debug", args)
}

// Deps executa dbt deps
func (e *DbtExecutor) Deps(
	ctx context.Context,
	project *entities.DbtProject,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt deps",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"deps"}
	return e.executeCommand(ctx, project, "deps", args)
}

// Clean executa dbt clean
func (e *DbtExecutor) Clean(
	ctx context.Context,
	project *entities.DbtProject,
) (*DbtRunResult, error) {
	e.logger.Info("Starting dbt clean",
		logging.F("project_id", project.GetID().String()),
		logging.F("project_name", project.Name),
	)

	args := []string{"clean"}
	return e.executeCommand(ctx, project, "clean", args)
}

// buildCommonArgs constrói argumentos comuns para comandos dbt
func (e *DbtExecutor) buildCommonArgs(
	models, exclude, selectArgs []string,
	vars map[string]string,
	threads int,
	profiles, target string,
) []string {
	var args []string

	// Models
	if len(models) > 0 {
		args = append(args, "--models", strings.Join(models, " "))
	}

	// Exclude
	if len(exclude) > 0 {
		args = append(args, "--exclude", strings.Join(exclude, " "))
	}

	// Select
	if len(selectArgs) > 0 {
		args = append(args, "--select", strings.Join(selectArgs, " "))
	}

	// Variables
	if len(vars) > 0 {
		varPairs := make([]string, 0, len(vars))
		for key, value := range vars {
			varPairs = append(varPairs, fmt.Sprintf("%s:%s", key, value))
		}
		args = append(args, "--vars", "{"+strings.Join(varPairs, ",")+"}")
	}

	// Threads
	if threads > 0 {
		args = append(args, "--threads", strconv.Itoa(threads))
	}

	// Profiles directory
	if profiles != "" {
		args = append(args, "--profiles-dir", profiles)
	}

	// Target
	if target != "" {
		args = append(args, "--target", target)
	}

	return args
}

// executeCommand executa um comando dbt
func (e *DbtExecutor) executeCommand(
	ctx context.Context,
	project *entities.DbtProject,
	command string,
	args []string,
) (*DbtRunResult, error) {
	execution, err := e.prepareExecution(ctx, project, command, args)
	if err != nil {
		return nil, err
	}

	result, err := e.runCommandExecution(execution)
	if err != nil {
		return nil, err
	}

	e.finalizeExecution(project, result, execution.RunID)
	return result, nil
}

// prepareExecution sets up the execution context and validates prerequisites
func (e *DbtExecutor) prepareExecution(
	ctx context.Context,
	project *entities.DbtProject,
	command string,
	args []string,
) (*DbtExecution, error) {
	runID := uuid.New()
	e.logCommandStart(runID, command, args)

	if err := e.ensureWorkingDirectory(project.ProjectDir); err != nil {
		return nil, fmt.Errorf("failed to prepare working directory: %w", err)
	}

	cmd := e.buildCommand(ctx, project, args)
	stdoutBuf, stderrBuf := e.setupCommandOutput(cmd)

	return &DbtExecution{
		RunID:     runID,
		Project:   project,
		Command:   command,
		Args:      args,
		StartTime: time.Now(),
		Cmd:       cmd,
		StdoutBuf: stdoutBuf,
		StderrBuf: stderrBuf,
	}, nil
}

// runCommandExecution executes the prepared command and returns the result
func (e *DbtExecutor) runCommandExecution(execution *DbtExecution) (*DbtRunResult, error) {
	err := execution.Cmd.Run()
	endTime := time.Now()
	duration := endTime.Sub(execution.StartTime)

	exitCode := e.determineExitCode(err)
	result := e.buildRunResult(DbtRunResultConfig{
		RunID:     execution.RunID,
		Project:   execution.Project,
		Command:   execution.Command,
		Args:      execution.Args,
		ExitCode:  exitCode,
		StartTime: execution.StartTime,
		EndTime:   endTime,
		Duration:  duration,
		StdoutBuf: execution.StdoutBuf,
		StderrBuf: execution.StderrBuf,
	})

	return result, nil
}

// finalizeExecution handles post-processing and logging
func (e *DbtExecutor) finalizeExecution(project *entities.DbtProject, result *DbtRunResult, runID uuid.UUID) {
	e.postProcessResult(project, result, runID)
	e.logCommandCompletion(runID, result, result.Duration, result.ExitCode)
}

// logCommandStart logs the start of a dbt command execution
func (e *DbtExecutor) logCommandStart(runID uuid.UUID, command string, args []string) {
	e.logger.Info("Executing dbt command",
		logging.F("run_id", runID.String()),
		logging.F("command", command),
		logging.F("args", strings.Join(args, " ")),
	)
}

// buildCommand creates and configures the exec.Cmd
func (e *DbtExecutor) buildCommand(ctx context.Context, project *entities.DbtProject, args []string) *exec.Cmd {
	cmd := exec.CommandContext(ctx, e.dbtPath, args...)
	cmd.Dir = project.ProjectDir
	cmd.Env = e.buildEnvironment(project)
	return cmd
}

// setupCommandOutput configures stdout and stderr capture
func (e *DbtExecutor) setupCommandOutput(cmd *exec.Cmd) (*strings.Builder, *strings.Builder) {
	stdoutBuf := &strings.Builder{}
	stderrBuf := &strings.Builder{}
	cmd.Stdout = stdoutBuf
	cmd.Stderr = stderrBuf
	return stdoutBuf, stderrBuf
}

// determineExitCode extracts the exit code from command execution error
func (e *DbtExecutor) determineExitCode(err error) int {
	if err == nil {
		return 0
	}
	if exitError, ok := err.(*exec.ExitError); ok {
		return exitError.ExitCode()
	}
	return 1
}

// DbtRunResultConfig holds parameters for building a DbtRunResult
type DbtRunResultConfig struct {
	RunID     uuid.UUID
	Project   *entities.DbtProject
	Command   string
	Args      []string
	ExitCode  int
	StartTime time.Time
	EndTime   time.Time
	Duration  time.Duration
	StdoutBuf *strings.Builder
	StderrBuf *strings.Builder
}

// DbtExecution holds execution context and data
type DbtExecution struct {
	RunID     uuid.UUID
	Project   *entities.DbtProject
	Command   string
	Args      []string
	StartTime time.Time
	Cmd       *exec.Cmd
	StdoutBuf *strings.Builder
	StderrBuf *strings.Builder
}

// buildRunResult creates the DbtRunResult from execution data
func (e *DbtExecutor) buildRunResult(config DbtRunResultConfig) *DbtRunResult {
	return &DbtRunResult{
		RunID:     config.RunID,
		ProjectID: config.Project.GetID(),
		Command:   config.Command,
		Args:      config.Args,
		ExitCode:  config.ExitCode,
		Success:   config.ExitCode == 0,
		StartTime: config.StartTime,
		EndTime:   config.EndTime,
		Duration:  config.Duration,
		Stdout:    config.StdoutBuf.String(),
		Stderr:    config.StderrBuf.String(),
	}
}

// postProcessResult handles result file loading and metrics calculation
func (e *DbtExecutor) postProcessResult(project *entities.DbtProject, result *DbtRunResult, runID uuid.UUID) {
	if result.Success {
		if err := e.loadResultFiles(project, result); err != nil {
			e.logger.Warn("Failed to load result files",
				logging.F("error", err.Error()),
				logging.F("run_id", runID.String()),
			)
		}
	}
	result.Metrics = e.calculateMetrics(result)
}

// logCommandCompletion logs the completion of a dbt command execution
func (e *DbtExecutor) logCommandCompletion(runID uuid.UUID, result *DbtRunResult, duration time.Duration, exitCode int) {
	e.logger.Info("dbt command completed",
		logging.F("run_id", runID.String()),
		logging.F("success", result.Success),
		logging.F("duration_ms", duration.Milliseconds()),
		logging.F("exit_code", exitCode),
	)
}

// ensureWorkingDirectory garante que o diretório de trabalho existe
func (e *DbtExecutor) ensureWorkingDirectory(workDir string) error {
	if _, err := os.Stat(workDir); os.IsNotExist(err) {
		if err := os.MkdirAll(workDir, 0755); err != nil {
			return fmt.Errorf("failed to create working directory: %w", err)
		}
	}
	return nil
}

// buildEnvironment constrói o ambiente para execução
func (e *DbtExecutor) buildEnvironment(project *entities.DbtProject) []string {
	env := os.Environ()

	// Adicionar variáveis do projeto
	for key, value := range project.Vars {
		if strValue, ok := value.(string); ok {
			env = append(env, fmt.Sprintf("DBT_VAR_%s=%s", strings.ToUpper(key), strValue))
		}
	}

	// Adicionar variáveis do DBT
	env = append(env, "DBT_PROFILES_DIR="+filepath.Dir(project.ProjectDir))
	env = append(env, "DBT_PROJECT_DIR="+project.ProjectDir)

	return env
}

// loadResultFiles carrega arquivos de resultado do dbt
func (e *DbtExecutor) loadResultFiles(project *entities.DbtProject, result *DbtRunResult) error {
	targetDir := project.GetTargetPath()

	// Carregar manifest.json
	manifestPath := filepath.Join(targetDir, "manifest.json")
	if manifest, err := e.loadManifest(manifestPath); err == nil {
		result.Manifest = manifest
	}

	// Carregar run_results.json
	runResultsPath := filepath.Join(targetDir, "run_results.json")
	if runResults, err := e.loadRunResults(runResultsPath); err == nil {
		result.RunResults = runResults
		result.Results = runResults.Results
	}

	return nil
}

// loadManifest carrega o arquivo manifest.json
func (e *DbtExecutor) loadManifest(path string) (*DbtManifest, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var manifest DbtManifest
	if err := json.Unmarshal(data, &manifest); err != nil {
		return nil, err
	}

	return &manifest, nil
}

// loadRunResults carrega o arquivo run_results.json
func (e *DbtExecutor) loadRunResults(path string) (*DbtRunResultsJson, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var runResults DbtRunResultsJson
	if err := json.Unmarshal(data, &runResults); err != nil {
		return nil, err
	}

	return &runResults, nil
}

// calculateMetrics calcula métricas da execução
func (e *DbtExecutor) calculateMetrics(result *DbtRunResult) DbtExecutionMetrics {
	metrics := DbtExecutionMetrics{}

	for _, nodeResult := range result.Results {
		e.updateResourceCounts(&metrics, nodeResult)
		e.updateStatusCounts(&metrics, nodeResult)
		metrics.TotalNodes++
	}

	e.calculateSuccessRate(&metrics)
	return metrics
}

// updateResourceCounts updates resource type counters based on node type
func (e *DbtExecutor) updateResourceCounts(metrics *DbtExecutionMetrics, nodeResult DbtNodeResult) {
	switch {
	case strings.Contains(nodeResult.UniqueID, "model."):
		metrics.ModelsRun++
	case strings.Contains(nodeResult.UniqueID, "test."):
		metrics.TestsRun++
	case strings.Contains(nodeResult.UniqueID, "seed."):
		metrics.SeedsRun++
	case strings.Contains(nodeResult.UniqueID, "snapshot."):
		metrics.SnapshotsRun++
	}
}

// updateStatusCounts updates status counters based on node status
func (e *DbtExecutor) updateStatusCounts(metrics *DbtExecutionMetrics, nodeResult DbtNodeResult) {
	switch nodeResult.Status {
	case "error":
		metrics.Errors++
	case "warn":
		metrics.Warnings++
	case "skipped":
		metrics.Skipped++
	}
}

// calculateSuccessRate calculates the success rate for the execution
func (e *DbtExecutor) calculateSuccessRate(metrics *DbtExecutionMetrics) {
	if metrics.TotalNodes > 0 {
		successful := metrics.TotalNodes - metrics.Errors
		metrics.SuccessRate = float64(successful) / float64(metrics.TotalNodes) * 100
	}
}

// ParseLogOutput faz parsing da saída de logs do dbt
func (e *DbtExecutor) ParseLogOutput(output string) []DbtNodeResult {
	patterns := e.buildLogPatterns()
	lines := strings.Split(output, "\n")

	var results []DbtNodeResult
	for _, line := range lines {
		if result := e.parseLogLine(line, patterns); result != nil {
			results = append(results, *result)
		}
	}

	return results
}

// buildLogPatterns creates regex patterns for different log types
func (e *DbtExecutor) buildLogPatterns() map[string]*regexp.Regexp {
	return map[string]*regexp.Regexp{
		"model": regexp.MustCompile(`(?i)(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\s+\d+\s+of\s+\d+\]\s+([A-Z]+)\s+(model\.[^\s]+)\s+\[([A-Z]+)\s+in\s+([\d\.]+)s\]`),
		"test":  regexp.MustCompile(`(?i)(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\s+\d+\s+of\s+\d+\]\s+([A-Z]+)\s+(test\.[^\s]+)\s+\[([A-Z]+)\s+in\s+([\d\.]+)s\]`),
		"seed":  regexp.MustCompile(`(?i)(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\s+\d+\s+of\s+\d+\]\s+([A-Z]+)\s+(seed\.[^\s]+)\s+\[([A-Z]+)\s+in\s+([\d\.]+)s\]`),
	}
}

// parseLogLine attempts to parse a single log line into a DbtNodeResult
func (e *DbtExecutor) parseLogLine(line string, patterns map[string]*regexp.Regexp) *DbtNodeResult {
	for _, pattern := range patterns {
		matches := pattern.FindStringSubmatch(line)
		if len(matches) >= 7 {
			return e.createNodeResultFromMatches(matches)
		}
	}
	return nil
}

// createNodeResultFromMatches creates a DbtNodeResult from regex matches
func (e *DbtExecutor) createNodeResultFromMatches(matches []string) *DbtNodeResult {
	execTime, _ := strconv.ParseFloat(matches[6], 64)

	return &DbtNodeResult{
		UniqueID:      matches[4],
		Name:          extractNodeName(matches[4]),
		Status:        strings.ToLower(matches[5]),
		ExecutionTime: execTime,
		Thread:        matches[2],
	}
}

// extractNodeName extrai o nome do nó do unique_id
func extractNodeName(uniqueID string) string {
	parts := strings.Split(uniqueID, ".")
	if len(parts) >= 3 {
		return parts[len(parts)-1]
	}
	return uniqueID
}

// ValidateProject valida se um projeto dbt é válido
func (e *DbtExecutor) ValidateProject(project *entities.DbtProject) error {
	if err := e.validateProjectDirectory(project.ProjectDir); err != nil {
		return err
	}

	if err := e.validateDbtProjectFile(project.ProjectDir); err != nil {
		return err
	}

	e.validateModelPaths(project)
	return nil
}

// validateProjectDirectory checks if the project directory exists
func (e *DbtExecutor) validateProjectDirectory(projectDir string) error {
	if _, err := os.Stat(projectDir); os.IsNotExist(err) {
		return fmt.Errorf("project directory does not exist: %s", projectDir)
	}
	return nil
}

// validateDbtProjectFile checks if dbt_project.yml exists
func (e *DbtExecutor) validateDbtProjectFile(projectDir string) error {
	dbtProjectFile := filepath.Join(projectDir, "dbt_project.yml")
	if _, err := os.Stat(dbtProjectFile); os.IsNotExist(err) {
		return fmt.Errorf("dbt_project.yml not found in: %s", projectDir)
	}
	return nil
}

// validateModelPaths checks if model directories exist and logs warnings for missing ones
func (e *DbtExecutor) validateModelPaths(project *entities.DbtProject) {
	for _, modelPath := range project.ModelPaths {
		fullPath := filepath.Join(project.ProjectDir, modelPath)
		if _, err := os.Stat(fullPath); os.IsNotExist(err) {
			e.logger.Warn("Model path does not exist",
				logging.F("path", fullPath),
				logging.F("project", project.Name),
			)
		}
	}
}

// GetDbtVersion retorna a versão do dbt instalado
func (e *DbtExecutor) GetDbtVersion(ctx context.Context) (string, error) {
	cmd := exec.CommandContext(ctx, e.dbtPath, "--version")
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to get dbt version: %w", err)
	}

	// Parse version from output
	versionRegex := regexp.MustCompile(`dbt version:\s+([\d\.]+)`)
	matches := versionRegex.FindStringSubmatch(string(output))
	if len(matches) >= 2 {
		return matches[1], nil
	}

	return string(output), nil
}
