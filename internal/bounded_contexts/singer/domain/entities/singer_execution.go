package entities

import (
	"fmt"
	"time"

	"github.com/flext/flexcore/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// SingerExecution represents a Singer protocol execution following Clean Architecture
type SingerExecution struct {
	domain.AggregateRoot

	// Singer execution metadata
	SingerSpecID uuid.UUID         `json:"singer_spec_id" validate:"required"`
	PipelineID   uuid.UUID         `json:"pipeline_id" validate:"required"`
	Type         string            `json:"type"` // "tap" or "target"
	Command      string            `json:"command"`
	Args         []string          `json:"args"`
	Environment  map[string]string `json:"environment"`

	// Execution state
	Status      ExecutionStatus `json:"status"`
	StartedAt   time.Time       `json:"started_at"`
	CompletedAt *time.Time      `json:"completed_at,omitempty"`
	Duration    *time.Duration  `json:"duration,omitempty"`

	// Singer protocol data
	Config      map[string]interface{} `json:"config"`
	Catalog     *SingerCatalog         `json:"catalog,omitempty"`
	InputState  *SingerState           `json:"input_state,omitempty"`
	OutputState *SingerState           `json:"output_state,omitempty"`

	// Execution results
	RecordsProcessed int64    `json:"records_processed"`
	RecordsExtracted int64    `json:"records_extracted"`
	RecordsLoaded    int64    `json:"records_loaded"`
	BytesProcessed   int64    `json:"bytes_processed"`
	StreamsProcessed []string `json:"streams_processed"`

	// Performance and monitoring
	Metrics     ExecutionMetrics `json:"metrics"`
	Logs        []ExecutionLog   `json:"logs"`
	Error       *ExecutionError  `json:"error,omitempty"`
	OutputFiles []OutputFile     `json:"output_files"`

	// Output information
	OutputPath string `json:"output_path,omitempty"`
	LogPath    string `json:"log_path,omitempty"`
}

// ExecutionStatus and related types moved to singer_types.go

// ExecutionMetrics contains comprehensive execution metrics
type ExecutionMetrics struct {
	// Performance metrics
	RecordsPerSecond      float64 `json:"records_per_second"`
	BytesPerSecond        float64 `json:"bytes_per_second"`
	ThroughputMBPerSecond float64 `json:"throughput_mb_per_second"`

	// Resource usage
	MemoryUsageMB   float64 `json:"memory_usage_mb"`
	CPUUsagePercent float64 `json:"cpu_usage_percent"`
	DiskUsageMB     float64 `json:"disk_usage_mb"`

	// Network metrics
	NetworkBytesIn  int64 `json:"network_bytes_in"`
	NetworkBytesOut int64 `json:"network_bytes_out"`

	// Stream-specific metrics
	StreamMetrics map[string]int64 `json:"stream_metrics"`

	// Custom metrics
	CustomMetrics map[string]interface{} `json:"custom_metrics"`
}

// ExecutionLog representa um log de execução
type ExecutionLog struct {
	Timestamp time.Time              `json:"timestamp"`
	Level     string                 `json:"level"`
	Message   string                 `json:"message"`
	Source    string                 `json:"source"`
	Data      map[string]interface{} `json:"data,omitempty"`
}

// ExecutionError representa um erro de execução
type ExecutionError struct {
	Code       string    `json:"code"`
	Message    string    `json:"message"`
	Details    string    `json:"details,omitempty"`
	StackTrace string    `json:"stack_trace,omitempty"`
	Timestamp  time.Time `json:"timestamp"`
}

// OutputFile representa um arquivo gerado durante a execução
type OutputFile struct {
	Name        string    `json:"name"`
	Path        string    `json:"path"`
	Size        int64     `json:"size"`
	MimeType    string    `json:"mime_type"`
	Checksum    string    `json:"checksum"`
	CreatedAt   time.Time `json:"created_at"`
	Description string    `json:"description,omitempty"`
}

// NewSingerExecution creates a new Singer execution following Clean Architecture
func NewSingerExecution(
	singerSpecID, pipelineID uuid.UUID,
	executionType, command string,
	args []string,
	config map[string]interface{},
	inputState *SingerState,
) (*SingerExecution, error) {
	if singerSpecID == uuid.Nil {
		return nil, fmt.Errorf("singer spec ID cannot be empty")
	}
	if pipelineID == uuid.Nil {
		return nil, fmt.Errorf("pipeline ID cannot be empty")
	}
	if executionType == "" {
		return nil, fmt.Errorf("execution type cannot be empty")
	}
	if command == "" {
		return nil, fmt.Errorf("command cannot be empty")
	}
	if config == nil {
		config = make(map[string]interface{})
	}
	if args == nil {
		args = []string{}
	}

	execution := &SingerExecution{
		AggregateRoot:    domain.NewAggregateRoot(),
		SingerSpecID:     singerSpecID,
		PipelineID:       pipelineID,
		Type:             executionType,
		Command:          command,
		Args:             args,
		Environment:      make(map[string]string),
		Status:           ExecutionStatusPending,
		StartedAt:        time.Now(),
		Config:           config,
		InputState:       inputState,
		RecordsProcessed: 0,
		RecordsExtracted: 0,
		RecordsLoaded:    0,
		BytesProcessed:   0,
		StreamsProcessed: []string{},
		Metrics: ExecutionMetrics{
			StreamMetrics: make(map[string]int64),
			CustomMetrics: make(map[string]interface{}),
		},
		Logs:        []ExecutionLog{},
		OutputFiles: []OutputFile{},
	}

	// Emit domain event
	execution.AddEvent(&SingerExecutionStarted{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.execution.started", execution.AggregateRoot.GetID()),
		ExecutionID:     execution.AggregateRoot.GetID(),
		SpecID:          singerSpecID,
		SpecName:        "", // Will be set by the calling service
		SpecType:        executionType,
	})

	return execution, nil
}

// Start inicia a execução
func (e *SingerExecution) Start() error {
	if e.Status != ExecutionStatusPending {
		return fmt.Errorf("execution can only be started from pending status, current: %s", e.Status)
	}

	e.Status = ExecutionStatusRunning
	e.StartedAt = time.Now()
	e.AggregateRoot.MarkAsUpdated()

	e.AddLog("info", "Execution started", "system", nil)

	return nil
}

// Complete marca a execução como completa
func (e *SingerExecution) Complete(outputState *SingerState) error {
	if e.Status != ExecutionStatusRunning {
		return fmt.Errorf("execution can only be completed from running status, current: %s", e.Status)
	}

	now := time.Now()
	e.Status = ExecutionStatusCompleted
	e.CompletedAt = &now
	duration := now.Sub(e.StartedAt)
	e.Duration = &duration
	e.OutputState = outputState
	e.AggregateRoot.MarkAsUpdated()

	// Calcular métricas finais
	e.calculateFinalMetrics()

	e.AddLog("info", "Execution completed successfully", "system", map[string]interface{}{
		"duration_ms":       duration.Milliseconds(),
		"records_processed": e.RecordsProcessed,
	})

	// Emitir evento de conclusão
	e.AddEvent(&SingerExecutionCompleted{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.execution.completed", e.AggregateRoot.GetID()),
		ExecutionID:     e.AggregateRoot.GetID(),
		SpecID:          e.SingerSpecID,
		RecordsCount:    e.RecordsProcessed,
		DurationMs:      duration.Milliseconds(),
		Success:         true,
	})

	return nil
}

// Fail marca a execução como falhada
func (e *SingerExecution) Fail(err error, details string) error {
	if e.Status == ExecutionStatusCompleted {
		return fmt.Errorf("cannot fail a completed execution")
	}

	now := time.Now()
	e.Status = ExecutionStatusFailed
	e.CompletedAt = &now
	if e.StartedAt.IsZero() {
		e.StartedAt = now
	}
	duration := now.Sub(e.StartedAt)
	e.Duration = &duration

	e.Error = &ExecutionError{
		Code:      "EXECUTION_FAILED",
		Message:   err.Error(),
		Details:   details,
		Timestamp: now,
	}
	e.AggregateRoot.MarkAsUpdated()

	e.AddLog("error", fmt.Sprintf("Execution failed: %s", err.Error()), "system", map[string]interface{}{
		"error_details": details,
	})

	// Emitir evento de falha
	e.AddEvent(&SingerExecutionCompleted{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.execution.completed", e.AggregateRoot.GetID()),
		ExecutionID:     e.AggregateRoot.GetID(),
		SpecID:          e.SingerSpecID,
		RecordsCount:    e.RecordsProcessed,
		DurationMs:      duration.Milliseconds(),
		Success:         false,
		ErrorMessage:    err.Error(),
	})

	return nil
}

// Cancel cancela a execução
func (e *SingerExecution) Cancel() error {
	if e.Status == ExecutionStatusCompleted || e.Status == ExecutionStatusFailed {
		return fmt.Errorf("cannot cancel a completed or failed execution")
	}

	now := time.Now()
	e.Status = ExecutionStatusCanceled
	e.CompletedAt = &now
	if e.StartedAt.IsZero() {
		e.StartedAt = now
	}
	duration := now.Sub(e.StartedAt)
	e.Duration = &duration
	e.AggregateRoot.MarkAsUpdated()

	e.AddLog("warn", "Execution cancelled", "system", nil)

	return nil
}

// AddRecord registra um novo registro processado
func (e *SingerExecution) AddRecord(streamName, recordType, recordData string) {
	e.RecordsProcessed++

	// Atualizar métricas do stream
	if e.Metrics.StreamMetrics == nil {
		e.Metrics.StreamMetrics = make(map[string]int64)
	}
	e.Metrics.StreamMetrics[streamName]++

	// Adicionar stream à lista se não existir
	for _, stream := range e.StreamsProcessed {
		if stream == streamName {
			goto found
		}
	}
	e.StreamsProcessed = append(e.StreamsProcessed, streamName)
found:

	e.AggregateRoot.MarkAsUpdated()

	// Emitir evento de registro processado
	e.AddEvent(&SingerRecordProcessed{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.record.processed", e.AggregateRoot.GetID()),
		ExecutionID:     e.AggregateRoot.GetID(),
		SpecID:          e.SingerSpecID,
		StreamName:      streamName,
		RecordType:      recordType,
		RecordData:      recordData,
	})
}

// AddLog adiciona um log à execução
func (e *SingerExecution) AddLog(level, message, source string, data map[string]interface{}) {
	log := ExecutionLog{
		Timestamp: time.Now(),
		Level:     level,
		Message:   message,
		Source:    source,
		Data:      data,
	}

	e.Logs = append(e.Logs, log)
	e.AggregateRoot.MarkAsUpdated()
}

// AddOutputFile adiciona um arquivo de saída
func (e *SingerExecution) AddOutputFile(file OutputFile) {
	e.OutputFiles = append(e.OutputFiles, file)
	e.AggregateRoot.MarkAsUpdated()
}

// UpdateMetrics atualiza as métricas da execução
func (e *SingerExecution) UpdateMetrics(metrics ExecutionMetrics) {
	e.Metrics = metrics
	e.AggregateRoot.MarkAsUpdated()
}

// calculateFinalMetrics calcula as métricas finais da execução
func (e *SingerExecution) calculateFinalMetrics() {
	if e.Duration != nil && e.Duration.Seconds() > 0 {
		e.Metrics.RecordsPerSecond = float64(e.RecordsProcessed) / e.Duration.Seconds()
	}
}

// GetDurationMs retorna a duração em milissegundos
func (e *SingerExecution) GetDurationMs() int64 {
	if e.Duration == nil {
		return 0
	}
	return e.Duration.Milliseconds()
}

// IsRunning verifica se a execução está em andamento
func (e *SingerExecution) IsRunning() bool {
	return e.Status == ExecutionStatusRunning
}

// IsCompleted verifica se a execução foi completada (com sucesso ou falha)
func (e *SingerExecution) IsCompleted() bool {
	return e.Status == ExecutionStatusCompleted || e.Status == ExecutionStatusFailed || e.Status == ExecutionStatusCanceled
}

// IsSuccess verifica se a execução foi bem-sucedida
func (e *SingerExecution) IsSuccess() bool {
	return e.Status == ExecutionStatusCompleted
}
