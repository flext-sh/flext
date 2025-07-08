package services

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// SingerExecutor executa especificações Singer (taps e targets)
type SingerExecutor struct {
	logger  logging.Logger
	workDir string
	timeout time.Duration
}

// SingerMessage representa uma mensagem do protocolo Singer
type SingerMessage struct {
	Type   string                 `json:"type"`
	Record map[string]interface{} `json:"record,omitempty"`
	Schema map[string]interface{} `json:"schema,omitempty"`
	State  map[string]interface{} `json:"state,omitempty"`
	Stream string                 `json:"stream,omitempty"`
}

// ExecutionOptions opções para execução Singer
type ExecutionOptions struct {
	Config      map[string]interface{}
	Catalog     *entities.Catalog
	State       *entities.State
	Properties  []string
	Discover    bool
	Test        bool
	About       bool
	ConfigPath  string
	CatalogPath string
	StatePath   string
}

// ExecutionResult resultado da execução Singer
type ExecutionResult struct {
	ExecutionID      uuid.UUID
	Success          bool
	Error            error
	RecordsProcessed int64
	OutputState      *entities.State
	OutputFiles      []entities.OutputFile
	Metrics          entities.ExecutionMetrics
	Duration         time.Duration
	Messages         []SingerMessage
}

// NewSingerExecutor cria um novo executor Singer
func NewSingerExecutor(logger logging.Logger, workDir string) *SingerExecutor {
	if workDir == "" {
		workDir = "/tmp/flext-singer"
	}

	return &SingerExecutor{
		logger:  logger,
		workDir: workDir,
		timeout: 30 * time.Minute, // timeout padrão
	}
}

// Execute executa uma especificação Singer
func (e *SingerExecutor) Execute(
	ctx context.Context,
	spec *entities.SingerSpec,
	execution *entities.SingerExecution,
	options ExecutionOptions,
) (*ExecutionResult, error) {
	e.logger.Info("Starting Singer execution",
		logging.F("spec_id", spec.GetID().String()),
		logging.F("spec_name", spec.Name),
		logging.F("spec_type", string(spec.Type)),
		logging.F("execution_id", execution.GetID().String()),
	)

	startTime := time.Now()
	result := &ExecutionResult{
		ExecutionID: execution.GetID(),
		Messages:    []SingerMessage{},
	}

	execDir, cmd, err := e.setupExecution(spec, execution, options)
	if err != nil {
		return nil, err
	}
	defer e.cleanup(execDir)

	return e.runExecution(ctx, cmd, execution, result, startTime)
}

// setupExecution prepares the execution environment and command
func (e *SingerExecutor) setupExecution(spec *entities.SingerSpec, execution *entities.SingerExecution, options ExecutionOptions) (string, *exec.Cmd, error) {
	execDir := filepath.Join(e.workDir, execution.GetID().String())
	if err := os.MkdirAll(execDir, 0755); err != nil {
		return "", nil, fmt.Errorf("failed to create execution directory: %w", err)
	}

	if err := e.prepareConfigFiles(execDir, spec, options); err != nil {
		return "", nil, fmt.Errorf("failed to prepare config files: %w", err)
	}

	cmd, err := e.buildCommand(spec, execDir, options)
	if err != nil {
		return "", nil, fmt.Errorf("failed to build command: %w", err)
	}

	if err := execution.Start(); err != nil {
		return "", nil, fmt.Errorf("failed to start execution: %w", err)
	}

	return execDir, cmd, nil
}

// runExecution executes the command and handles the results
func (e *SingerExecutor) runExecution(ctx context.Context, cmd *exec.Cmd, execution *entities.SingerExecution, result *ExecutionResult, startTime time.Time) (*ExecutionResult, error) {
	ctxWithTimeout, cancel := context.WithTimeout(ctx, e.timeout)
	defer cancel()

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to create stdout pipe: %w", err)
	}

	stderr, err := cmd.StderrPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to create stderr pipe: %w", err)
	}

	if err := cmd.Start(); err != nil {
		execution.Fail(err, "Failed to start Singer process")
		return nil, fmt.Errorf("failed to start Singer process: %w", err)
	}

	done := make(chan error, 1)
	go func() {
		done <- e.processOutput(ctxWithTimeout, stdout, stderr, execution, result)
	}()

	select {
	case <-ctxWithTimeout.Done():
		return e.handleTimeout(cmd, execution, result)
	case err := <-done:
		return e.handleCompletion(cmd, execution, result, startTime, err)
	}
}

// handleTimeout handles execution timeout
func (e *SingerExecutor) handleTimeout(cmd *exec.Cmd, execution *entities.SingerExecution, result *ExecutionResult) (*ExecutionResult, error) {
	if cmd.Process != nil {
		cmd.Process.Signal(syscall.SIGTERM)
		time.Sleep(5 * time.Second)
		cmd.Process.Kill()
	}

	err := fmt.Errorf("execution timeout after %v", e.timeout)
	execution.Fail(err, "Execution timed out")
	result.Error = err
	return result, err
}

// handleCompletion handles successful execution completion
func (e *SingerExecutor) handleCompletion(cmd *exec.Cmd, execution *entities.SingerExecution, result *ExecutionResult, startTime time.Time, processErr error) (*ExecutionResult, error) {
	cmdErr := cmd.Wait()
	if cmdErr != nil && processErr == nil {
		processErr = cmdErr
	}

	result.Duration = time.Since(startTime)
	result.RecordsProcessed = execution.RecordsProcessed

	if processErr != nil {
		execution.Fail(processErr, "Singer process failed")
		result.Error = processErr
		result.Success = false
	} else {
		e.handleSuccessfulExecution(execution, result)
	}

	e.finalizeExecution(execution, result)
	return result, processErr
}

// handleSuccessfulExecution processes successful execution results
func (e *SingerExecutor) handleSuccessfulExecution(execution *entities.SingerExecution, result *ExecutionResult) {
	outputState := e.extractFinalState(result.Messages)
	singerState := e.convertToSingerState(outputState)

	execution.Complete(singerState)
	result.OutputState = outputState
	result.Success = true
}

// convertToSingerState converts State to SingerState format
func (e *SingerExecutor) convertToSingerState(outputState *entities.State) *entities.SingerState {
	if outputState == nil || len(outputState.Bookmarks) == 0 {
		return nil
	}

	bookmarks := make(map[string]interface{})
	for streamName, streamState := range outputState.Bookmarks {
		bookmarks[streamName] = map[string]interface{}{
			"replication_key_value": streamState.ReplicationKeyValue,
			"version":               streamState.Version,
			"last_sync_time":        streamState.LastSyncTime,
		}
	}

	return &entities.SingerState{
		Bookmarks: bookmarks,
	}
}

// finalizeExecution calculates metrics and collects output files
func (e *SingerExecutor) finalizeExecution(execution *entities.SingerExecution, result *ExecutionResult) {
	result.Metrics = e.calculateMetrics(result)
	execution.UpdateMetrics(result.Metrics)

	result.OutputFiles = e.collectOutputFiles(filepath.Dir(execution.GetID().String()))
	for _, file := range result.OutputFiles {
		execution.AddOutputFile(file)
	}
}

// prepareConfigFiles prepara os arquivos de configuração necessários
func (e *SingerExecutor) prepareConfigFiles(
	execDir string,
	spec *entities.SingerSpec,
	options ExecutionOptions,
) error {
	if err := e.prepareConfigFile(execDir, &options); err != nil {
		return err
	}

	if err := e.prepareCatalogFile(execDir, spec, &options); err != nil {
		return err
	}

	return e.prepareStateFile(execDir, spec, &options)
}

// prepareConfigFile creates the config.json file if config is provided
func (e *SingerExecutor) prepareConfigFile(execDir string, options *ExecutionOptions) error {
	if len(options.Config) == 0 {
		return nil
	}

	configPath := filepath.Join(execDir, "config.json")
	configData, err := json.MarshalIndent(options.Config, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(configPath, configData, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	options.ConfigPath = configPath
	return nil
}

// prepareCatalogFile creates the catalog.json file for taps if catalog is provided
func (e *SingerExecutor) prepareCatalogFile(execDir string, spec *entities.SingerSpec, options *ExecutionOptions) error {
	if options.Catalog == nil || spec.Type != entities.SingerTypeTap {
		return nil
	}

	catalogPath := filepath.Join(execDir, "catalog.json")
	catalogData, err := json.MarshalIndent(options.Catalog, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal catalog: %w", err)
	}

	if err := os.WriteFile(catalogPath, catalogData, 0644); err != nil {
		return fmt.Errorf("failed to write catalog file: %w", err)
	}

	options.CatalogPath = catalogPath
	return nil
}

// prepareStateFile creates the state.json file for taps if state is provided
func (e *SingerExecutor) prepareStateFile(execDir string, spec *entities.SingerSpec, options *ExecutionOptions) error {
	if options.State == nil || spec.Type != entities.SingerTypeTap {
		return nil
	}

	statePath := filepath.Join(execDir, "state.json")
	stateData, err := json.MarshalIndent(options.State, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal state: %w", err)
	}

	if err := os.WriteFile(statePath, stateData, 0644); err != nil {
		return fmt.Errorf("failed to write state file: %w", err)
	}

	options.StatePath = statePath
	return nil
}

// buildCommand constrói o comando para execução
func (e *SingerExecutor) buildCommand(
	spec *entities.SingerSpec,
	execDir string,
	options ExecutionOptions,
) (*exec.Cmd, error) {
	args := e.buildCommandArgs(spec, options)
	cmd := exec.Command(spec.Executable, args...)
	cmd.Dir = execDir
	cmd.Env = e.buildEnvironment(spec)
	return cmd, nil
}

// buildCommandArgs builds the command line arguments
func (e *SingerExecutor) buildCommandArgs(spec *entities.SingerSpec, options ExecutionOptions) []string {
	var args []string

	args = e.addSpecialOptions(args, options)
	args = e.addConfigArgs(args, options)
	args = e.addTapSpecificArgs(args, spec, options)
	args = e.addPropertyArgs(args, options)

	return args
}

// addSpecialOptions adds special mode options (discover, test, about)
func (e *SingerExecutor) addSpecialOptions(args []string, options ExecutionOptions) []string {
	if options.Discover {
		return append(args, "--discover")
	}
	if options.Test {
		return append(args, "--test")
	}
	if options.About {
		return append(args, "--about")
	}
	return args
}

// addConfigArgs adds configuration file arguments
func (e *SingerExecutor) addConfigArgs(args []string, options ExecutionOptions) []string {
	if options.ConfigPath != "" {
		return append(args, "--config", options.ConfigPath)
	}
	return args
}

// addTapSpecificArgs adds tap-specific arguments (catalog, state)
func (e *SingerExecutor) addTapSpecificArgs(args []string, spec *entities.SingerSpec, options ExecutionOptions) []string {
	if spec.Type != entities.SingerTypeTap {
		return args
	}

	if options.CatalogPath != "" {
		args = append(args, "--catalog", options.CatalogPath)
	}

	if options.StatePath != "" {
		args = append(args, "--state", options.StatePath)
	}

	return args
}

// addPropertyArgs adds property-specific arguments
func (e *SingerExecutor) addPropertyArgs(args []string, options ExecutionOptions) []string {
	if len(options.Properties) > 0 {
		return append(args, "--properties", strings.Join(options.Properties, ","))
	}
	return args
}

// buildEnvironment builds the environment variables for the command
func (e *SingerExecutor) buildEnvironment(spec *entities.SingerSpec) []string {
	env := os.Environ()
	for key, value := range spec.EnvironmentVars {
		env = append(env, fmt.Sprintf("%s=%s", key, value))
	}
	return env
}

// processOutput processa a saída do processo Singer
func (e *SingerExecutor) processOutput(
	ctx context.Context,
	stdout, stderr io.Reader,
	execution *entities.SingerExecution,
	result *ExecutionResult,
) error {
	go e.processStdout(ctx, stdout, execution, result)
	go e.processStderr(ctx, stderr, execution)
	return nil
}

// processStdout processes stdout messages from Singer
func (e *SingerExecutor) processStdout(ctx context.Context, stdout io.Reader, execution *entities.SingerExecution, result *ExecutionResult) {
	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		select {
		case <-ctx.Done():
			return
		default:
			line := scanner.Text()
			if err := e.processSingerMessage(line, execution, result); err != nil {
				e.logger.Warn("Failed to process Singer message",
					logging.F("error", err.Error()),
					logging.F("line", line),
				)
			}
		}
	}
}

// processStderr processes stderr logs from Singer
func (e *SingerExecutor) processStderr(ctx context.Context, stderr io.Reader, execution *entities.SingerExecution) {
	scanner := bufio.NewScanner(stderr)
	for scanner.Scan() {
		select {
		case <-ctx.Done():
			return
		default:
			line := scanner.Text()
			execution.AddLog("error", line, "singer-stderr", nil)
		}
	}
}

// processSingerMessage processa uma mensagem do protocolo Singer
func (e *SingerExecutor) processSingerMessage(
	line string,
	execution *entities.SingerExecution,
	result *ExecutionResult,
) error {
	var message SingerMessage
	if err := json.Unmarshal([]byte(line), &message); err != nil {
		// Não é uma mensagem JSON válida, tratar como log
		execution.AddLog("info", line, "singer-stdout", nil)
		return nil
	}

	result.Messages = append(result.Messages, message)

	switch message.Type {
	case "RECORD":
		execution.AddRecord(message.Stream, "RECORD", line)

	case "SCHEMA":
		execution.AddRecord(message.Stream, "SCHEMA", line)
		// Emitir evento de schema detectado
		execution.AddEvent(&entities.SingerSchemaDetected{
			BaseDomainEvent: domain.NewBaseDomainEvent("singer.schema.detected", execution.GetID()),
			ExecutionID:     execution.GetID(),
			SpecID:          execution.SingerSpecID,
			StreamName:      message.Stream,
			SchemaData:      line,
		})

	case "STATE":
		execution.AddRecord("", "STATE", line)
		// Estado será usado como estado final

	default:
		// Tipo desconhecido, registrar como log
		execution.AddLog("debug", fmt.Sprintf("Unknown message type: %s", message.Type), "singer", map[string]interface{}{
			"message": message,
		})
	}

	return nil
}

// extractFinalState extrai o estado final das mensagens
func (e *SingerExecutor) extractFinalState(messages []SingerMessage) *entities.State {
	stateMessage := e.findLatestStateMessage(messages)
	if stateMessage == nil {
		return nil
	}

	bookmarks := e.extractBookmarksFromState(stateMessage.State)
	return &entities.State{
		Bookmarks: bookmarks,
	}
}

// findLatestStateMessage finds the latest STATE message in the messages
func (e *SingerExecutor) findLatestStateMessage(messages []SingerMessage) *SingerMessage {
	for i := len(messages) - 1; i >= 0; i-- {
		if messages[i].Type == "STATE" && messages[i].State != nil {
			return &messages[i]
		}
	}
	return nil
}

// extractBookmarksFromState extracts bookmarks from a state message
func (e *SingerExecutor) extractBookmarksFromState(state map[string]interface{}) map[string]entities.StreamState {
	bookmarks := make(map[string]entities.StreamState)

	bookmarksData, ok := state["bookmarks"]
	if !ok {
		return bookmarks
	}

	bookmarksMap, ok := bookmarksData.(map[string]interface{})
	if !ok {
		return bookmarks
	}

	for stream, stateData := range bookmarksMap {
		streamState := e.parseStreamState(stateData)
		if streamState != nil {
			bookmarks[stream] = *streamState
		}
	}

	return bookmarks
}

// parseStreamState parses a single stream state from interface data
func (e *SingerExecutor) parseStreamState(stateData interface{}) *entities.StreamState {
	stateMap, ok := stateData.(map[string]interface{})
	if !ok {
		return nil
	}

	streamState := entities.StreamState{}

	if val, exists := stateMap["replication_key_value"]; exists {
		streamState.ReplicationKeyValue = val
	}

	if val, exists := stateMap["version"]; exists {
		if version, ok := val.(float64); ok {
			streamState.Version = int64(version)
		}
	}

	return &streamState
}

// calculateMetrics calcula métricas da execução
func (e *SingerExecutor) calculateMetrics(result *ExecutionResult) entities.ExecutionMetrics {
	metrics := entities.ExecutionMetrics{
		StreamMetrics: make(map[string]int64),
		CustomMetrics: make(map[string]interface{}),
	}

	// Contar registros por stream
	for _, message := range result.Messages {
		if message.Type == "RECORD" && message.Stream != "" {
			metrics.StreamMetrics[message.Stream]++
		}
	}

	// Calcular registros por segundo
	if result.Duration.Seconds() > 0 {
		metrics.RecordsPerSecond = float64(result.RecordsProcessed) / result.Duration.Seconds()
	}

	// Métricas personalizadas
	metrics.CustomMetrics["total_messages"] = len(result.Messages)
	metrics.CustomMetrics["streams_count"] = len(metrics.StreamMetrics)

	return metrics
}

// collectOutputFiles coleta arquivos gerados durante a execução
func (e *SingerExecutor) collectOutputFiles(execDir string) []entities.OutputFile {
	entries, err := os.ReadDir(execDir)
	if err != nil {
		e.logger.Warn("Failed to read execution directory",
			logging.F("error", err.Error()),
			logging.F("dir", execDir),
		)
		return []entities.OutputFile{}
	}

	return e.processDirectoryEntries(entries, execDir)
}

// processDirectoryEntries processes directory entries and creates OutputFile objects
func (e *SingerExecutor) processDirectoryEntries(entries []os.DirEntry, execDir string) []entities.OutputFile {
	var files []entities.OutputFile

	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		file := e.createOutputFile(entry, execDir)
		if file != nil {
			files = append(files, *file)
		}
	}

	return files
}

// createOutputFile creates an OutputFile from a directory entry
func (e *SingerExecutor) createOutputFile(entry os.DirEntry, execDir string) *entities.OutputFile {
	filePath := filepath.Join(execDir, entry.Name())
	info, err := entry.Info()
	if err != nil {
		return nil
	}

	return &entities.OutputFile{
		Name:      entry.Name(),
		Path:      filePath,
		Size:      info.Size(),
		CreatedAt: info.ModTime(),
		MimeType:  e.determineMimeType(entry.Name()),
	}
}

// determineMimeType determines the MIME type based on file extension
func (e *SingerExecutor) determineMimeType(fileName string) string {
	mimeTypes := map[string]string{
		".json": "application/json",
		".csv":  "text/csv",
		".log":  "text/plain",
	}

	ext := filepath.Ext(fileName)
	if mimeType, exists := mimeTypes[ext]; exists {
		return mimeType
	}
	return "application/octet-stream"
}

// cleanup limpa arquivos temporários
func (e *SingerExecutor) cleanup(execDir string) {
	if err := os.RemoveAll(execDir); err != nil {
		e.logger.Warn("Failed to cleanup execution directory",
			logging.F("error", err.Error()),
			logging.F("dir", execDir),
		)
	}
}

// SetTimeout define o timeout para execuções
func (e *SingerExecutor) SetTimeout(timeout time.Duration) {
	e.timeout = timeout
}

// Discover executa o modo discovery de um tap
func (e *SingerExecutor) Discover(
	ctx context.Context,
	spec *entities.SingerSpec,
	config map[string]interface{},
) (*entities.Catalog, error) {
	if spec.Type != entities.SingerTypeTap {
		return nil, fmt.Errorf("discovery is only available for tap specifications")
	}

	// Criar execução temporária para discovery
	execution, err := entities.NewSingerExecution(spec.GetID(), uuid.New(), "tap", "discover", []string{}, config, nil)
	if err != nil {
		return nil, err
	}

	options := ExecutionOptions{
		Config:   config,
		Discover: true,
	}

	result, err := e.Execute(ctx, spec, execution, options)
	if err != nil {
		return nil, err
	}

	// Extrair catálogo das mensagens
	for _, message := range result.Messages {
		if message.Type == "SCHEMA" {
			// Processar esquemas para construir catálogo
			// Esta é uma implementação simplificada
			catalog := &entities.Catalog{
				Streams: []entities.CatalogStream{},
			}

			// TODO: Implementar construção completa do catálogo
			return catalog, nil
		}
	}

	return nil, fmt.Errorf("no schema found in discovery output")
}

// TestConnection testa a conexão de uma especificação
func (e *SingerExecutor) TestConnection(
	ctx context.Context,
	spec *entities.SingerSpec,
	config map[string]interface{},
) error {
	// Criar execução temporária para teste
	execution, err := entities.NewSingerExecution(spec.GetID(), uuid.New(), "tap", "test", []string{}, config, nil)
	if err != nil {
		return err
	}

	options := ExecutionOptions{
		Config: config,
		Test:   true,
	}

	result, err := e.Execute(ctx, spec, execution, options)
	if err != nil {
		return fmt.Errorf("connection test failed: %w", err)
	}

	if !result.Success {
		return fmt.Errorf("connection test failed")
	}

	return nil
}
