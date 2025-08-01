package commands

import (
	"context"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// GetPipelineStatusCommand representa o comando para obter o status de um pipeline
type GetPipelineStatusCommand struct {
	PipelineID uuid.UUID `json:"pipeline_id" validate:"required"`
}

// GetPipelineStatusResult resultado do comando
type GetPipelineStatusResult struct {
	PipelineID     uuid.UUID              `json:"pipeline_id"`
	Name           string                 `json:"name"`
	Status         string                 `json:"status"`
	IsActive       bool                   `json:"is_active"`
	LastExecution  *time.Time             `json:"last_execution,omitempty"`
	NextExecution  *time.Time             `json:"next_execution,omitempty"`
	ExecutionCount int                    `json:"execution_count"`
	SuccessCount   int                    `json:"success_count"`
	FailureCount   int                    `json:"failure_count"`
	HealthStatus   string                 `json:"health_status"`
	HealthChecks   []HealthCheckResult    `json:"health_checks"`
	Metrics        map[string]interface{} `json:"metrics"`
}

// HealthCheckResult representa o resultado de um health check
type HealthCheckResult struct {
	Name         string    `json:"name"`
	Status       string    `json:"status"`
	Message      string    `json:"message,omitempty"`
	CheckedAt    time.Time `json:"checked_at"`
	ResponseTime int64     `json:"response_time_ms"`
}

// PausePipelineCommand representa o comando para pausar um pipeline
type PausePipelineCommand struct {
	PipelineID uuid.UUID `json:"pipeline_id" validate:"required"`
	Reason     string    `json:"reason,omitempty"`
	PausedBy   string    `json:"paused_by" validate:"required"`
}

// PausePipelineResult resultado do comando
type PausePipelineResult struct {
	PipelineID uuid.UUID `json:"pipeline_id"`
	Name       string    `json:"name"`
	Status     string    `json:"status"`
	PausedAt   time.Time `json:"paused_at"`
	PausedBy   string    `json:"paused_by"`
	Reason     string    `json:"reason,omitempty"`
}

// ResumePipelineCommand representa o comando para retomar um pipeline pausado
type ResumePipelineCommand struct {
	PipelineID uuid.UUID `json:"pipeline_id" validate:"required"`
	ResumedBy  string    `json:"resumed_by" validate:"required"`
}

// ResumePipelineResult resultado do comando
type ResumePipelineResult struct {
	PipelineID uuid.UUID `json:"pipeline_id"`
	Name       string    `json:"name"`
	Status     string    `json:"status"`
	ResumedAt  time.Time `json:"resumed_at"`
	ResumedBy  string    `json:"resumed_by"`
}

// GetPipelineStatusHandler manipula comandos de status
type GetPipelineStatusHandler struct {
	pipelineRepo          ports.PipelineRepository
	executionStatsService *services.PipelineExecutionStatsService
}

// NewGetPipelineStatusHandler cria um novo handler
func NewGetPipelineStatusHandler(pipelineRepo ports.PipelineRepository, executionStatsService *services.PipelineExecutionStatsService) *GetPipelineStatusHandler {
	return &GetPipelineStatusHandler{
		pipelineRepo:          pipelineRepo,
		executionStatsService: executionStatsService,
	}
}

// Handle executa o comando de obter status
func (h *GetPipelineStatusHandler) Handle(ctx context.Context, cmd GetPipelineStatusCommand) (*GetPipelineStatusResult, error) {
	// Validar comando
	if cmd.PipelineID == uuid.Nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Pipeline ID is required",
			Description: "PipelineID field cannot be empty",
		}
	}

	// Buscar pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve pipeline",
			Description: err.Error(),
		}
	}

	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: "The specified pipeline does not exist",
		}
	}

	// Realizar health checks
	healthChecks := h.performHealthChecks(ctx, pipeline)
	healthStatus := h.determineHealthStatus(healthChecks)

	// Calcular métricas
	metrics := h.calculateMetrics(ctx, pipeline)

	// Obter estatísticas de execução
	executionCounts, executionMetrics := h.getExecutionData(ctx, pipeline.GetID())

	// Construir resultado
	result := &GetPipelineStatusResult{
		PipelineID:     pipeline.GetID(),
		Name:           pipeline.Name,
		Status:         string(pipeline.Status),
		IsActive:       pipeline.IsActive,
		ExecutionCount: executionCounts.ExecutionCount,
		SuccessCount:   executionCounts.SuccessCount,
		FailureCount:   executionCounts.FailureCount,
		LastExecution:  executionCounts.LastExecution,
		NextExecution:  executionCounts.NextExecution,
		HealthStatus:   healthStatus,
		HealthChecks:   healthChecks,
		Metrics:        h.mergeMetrics(metrics, executionMetrics),
	}

	return result, nil
}

// PausePipelineHandler manipula comandos de pausa
type PausePipelineHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewPausePipelineHandler cria um novo handler
func NewPausePipelineHandler(pipelineRepo ports.PipelineRepository) *PausePipelineHandler {
	return &PausePipelineHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executa o comando de pausar pipeline
func (h *PausePipelineHandler) Handle(ctx context.Context, cmd PausePipelineCommand) (*PausePipelineResult, error) {
	// Validar comando
	if cmd.PipelineID == uuid.Nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Pipeline ID is required",
			Description: "PipelineID field cannot be empty",
		}
	}

	// Buscar pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve pipeline",
			Description: err.Error(),
		}
	}

	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: "The specified pipeline does not exist",
		}
	}

	// Verificar se o pipeline pode ser pausado
	if !pipeline.IsActive {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_ACTIVE",
			Message:     "Pipeline is not active",
			Description: "Only active pipelines can be paused",
		}
	}

	// Pausar o pipeline
	pipeline.Deactivate()
	pipeline.IncrementVersion()

	// Salvar mudanças
	if err := h.pipelineRepo.Save(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "SAVE_FAILED",
			Message:     "Failed to save pipeline changes",
			Description: err.Error(),
		}
	}

	// Construir resultado
	result := &PausePipelineResult{
		PipelineID: pipeline.GetID(),
		Name:       pipeline.Name,
		Status:     string(pipeline.Status),
		PausedAt:   time.Now().UTC(),
		PausedBy:   cmd.PausedBy,
		Reason:     cmd.Reason,
	}

	return result, nil
}

// ResumePipelineHandler manipula comandos de retomada
type ResumePipelineHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewResumePipelineHandler cria um novo handler
func NewResumePipelineHandler(pipelineRepo ports.PipelineRepository) *ResumePipelineHandler {
	return &ResumePipelineHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executa o comando de retomar pipeline
func (h *ResumePipelineHandler) Handle(ctx context.Context, cmd ResumePipelineCommand) (*ResumePipelineResult, error) {
	// Validar comando
	if cmd.PipelineID == uuid.Nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Pipeline ID is required",
			Description: "PipelineID field cannot be empty",
		}
	}

	// Buscar pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve pipeline",
			Description: err.Error(),
		}
	}

	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: "The specified pipeline does not exist",
		}
	}

	// Verificar se o pipeline pode ser retomado
	if pipeline.IsActive {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_ALREADY_ACTIVE",
			Message:     "Pipeline is already active",
			Description: "Pipeline is not paused",
		}
	}

	// Verificar se o pipeline tem steps antes de ativar
	if err := pipeline.Activate(); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "ACTIVATION_FAILED",
			Message:     "Failed to activate pipeline",
			Description: err.Error(),
		}
	}

	// Salvar mudanças
	if err := h.pipelineRepo.Save(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "SAVE_FAILED",
			Message:     "Failed to save pipeline changes",
			Description: err.Error(),
		}
	}

	// Construir resultado
	result := &ResumePipelineResult{
		PipelineID: pipeline.GetID(),
		Name:       pipeline.Name,
		Status:     string(pipeline.Status),
		ResumedAt:  time.Now().UTC(),
		ResumedBy:  cmd.ResumedBy,
	}

	return result, nil
}

// performHealthChecks executa verificações de saúde no pipeline
func (h *GetPipelineStatusHandler) performHealthChecks(ctx context.Context, pipeline *entities.Pipeline) []HealthCheckResult {
	var healthChecks []HealthCheckResult
	startTime := time.Now()

	// Health check 1: Verificar se pipeline tem steps
	stepsCheckStart := time.Now()
	stepsCheckStatus := "healthy"
	stepsCheckMessage := "Pipeline has configured steps"
	if len(pipeline.Steps) == 0 {
		stepsCheckStatus = "unhealthy"
		stepsCheckMessage = "Pipeline has no configured steps"
	}

	healthChecks = append(healthChecks, HealthCheckResult{
		Name:         "steps_configured",
		Status:       stepsCheckStatus,
		Message:      stepsCheckMessage,
		CheckedAt:    time.Now().UTC(),
		ResponseTime: time.Since(stepsCheckStart).Milliseconds(),
	})

	// Health check 2: Verificar configuração
	configCheckStart := time.Now()
	configCheckStatus := "healthy"
	configCheckMessage := "Pipeline configuration is valid"
	if pipeline.Configuration == nil {
		configCheckStatus = "warning"
		configCheckMessage = "Pipeline has no configuration"
	}

	healthChecks = append(healthChecks, HealthCheckResult{
		Name:         "configuration_valid",
		Status:       configCheckStatus,
		Message:      configCheckMessage,
		CheckedAt:    time.Now().UTC(),
		ResponseTime: time.Since(configCheckStart).Milliseconds(),
	})

	// Health check 3: Verificar estado geral
	generalCheckStart := time.Now()
	generalCheckStatus := "healthy"
	generalCheckMessage := "Pipeline is in good state"
	if !pipeline.IsActive && pipeline.Status == entities.PipelineStatusFailed {
		generalCheckStatus = "unhealthy"
		generalCheckMessage = "Pipeline is in failed state"
	}

	healthChecks = append(healthChecks, HealthCheckResult{
		Name:         "general_health",
		Status:       generalCheckStatus,
		Message:      generalCheckMessage,
		CheckedAt:    time.Now().UTC(),
		ResponseTime: time.Since(generalCheckStart).Milliseconds(),
	})

	// Log tempo total
	_ = time.Since(startTime)

	return healthChecks
}

// determineHealthStatus determina o status geral de saúde
func (h *GetPipelineStatusHandler) determineHealthStatus(healthChecks []HealthCheckResult) string {
	hasUnhealthy := false
	hasWarning := false

	for _, check := range healthChecks {
		switch check.Status {
		case "unhealthy":
			hasUnhealthy = true
		case "warning":
			hasWarning = true
		}
	}

	if hasUnhealthy {
		return "unhealthy"
	}
	if hasWarning {
		return "warning"
	}
	return "healthy"
}

// calculateMetrics calcula métricas do pipeline
func (h *GetPipelineStatusHandler) calculateMetrics(ctx context.Context, pipeline *entities.Pipeline) map[string]interface{} {
	metrics := make(map[string]interface{})

	// Métricas básicas
	metrics["steps_count"] = len(pipeline.Steps)
	metrics["is_active"] = pipeline.IsActive
	metrics["version"] = pipeline.GetVersion()
	metrics["created_at"] = pipeline.GetCreatedAt()
	metrics["updated_at"] = pipeline.GetUpdatedAt()

	// Métricas de configuração
	if pipeline.Configuration != nil {
		metrics["has_configuration"] = true
		metrics["configuration_keys"] = len(pipeline.Configuration)
	} else {
		metrics["has_configuration"] = false
		metrics["configuration_keys"] = 0
	}

	// Métricas de tags
	metrics["tags_count"] = len(pipeline.Tags)
	if len(pipeline.Tags) > 0 {
		metrics["tags"] = pipeline.Tags
	}

	// Métricas de schedule
	metrics["has_schedule"] = pipeline.Schedule != ""
	if pipeline.Schedule != "" {
		metrics["schedule"] = pipeline.Schedule
	}

	// Métricas de execução serão adicionadas via mergeMetrics quando disponíveis
	return metrics
}

// ExecutionCounts representa contadores de execução básicos
type ExecutionCounts struct {
	ExecutionCount int
	SuccessCount   int
	FailureCount   int
	LastExecution  *time.Time
	NextExecution  *time.Time
}

// getExecutionData obtém dados de execução e métricas para um pipeline
func (h *GetPipelineStatusHandler) getExecutionData(ctx context.Context, pipelineID uuid.UUID) (*ExecutionCounts, map[string]interface{}) {
	// Inicializar com zeros como fallback
	counts := &ExecutionCounts{
		ExecutionCount: 0,
		SuccessCount:   0,
		FailureCount:   0,
	}
	executionMetrics := make(map[string]interface{})

	// Se o serviço de estatísticas não estiver disponível, retornar zeros
	if h.executionStatsService == nil {
		return counts, executionMetrics
	}

	// Obter contadores básicos de execução
	if executionCount, successCount, failureCount, err := h.executionStatsService.GetPipelineExecutionCounts(ctx, pipelineID); err == nil {
		counts.ExecutionCount = executionCount
		counts.SuccessCount = successCount
		counts.FailureCount = failureCount
	}

	// Obter métricas detalhadas de execução
	if metrics, err := h.executionStatsService.GetPipelineExecutionMetrics(ctx, pipelineID); err == nil {
		counts.LastExecution = metrics.LastExecution
		counts.NextExecution = metrics.NextExecution

		// Adicionar métricas avançadas
		if metrics.LastExecutionDuration != nil {
			executionMetrics["last_execution_duration"] = metrics.LastExecutionDuration.String()
			executionMetrics["last_execution_duration_ms"] = metrics.LastExecutionDuration.Milliseconds()
		}

		if metrics.AverageExecutionTime != nil {
			executionMetrics["average_execution_time"] = metrics.AverageExecutionTime.String()
			executionMetrics["average_execution_time_ms"] = metrics.AverageExecutionTime.Milliseconds()
		}

		executionMetrics["execution_success_rate"] = metrics.ExecutionSuccessRate
		executionMetrics["recent_executions_count"] = len(metrics.RecentExecutions)
		executionMetrics["execution_trend_points"] = len(metrics.ExecutionTrend)

		// Adicionar tendências se disponíveis
		if len(metrics.ExecutionTrend) > 0 {
			executionMetrics["recent_trend"] = metrics.ExecutionTrend
		}

		// Adicionar execuções recentes se disponíveis
		if len(metrics.RecentExecutions) > 0 {
			executionMetrics["recent_executions"] = metrics.RecentExecutions
		}
	}

	return counts, executionMetrics
}

// mergeMetrics combina métricas básicas do pipeline com métricas de execução
func (h *GetPipelineStatusHandler) mergeMetrics(baseMetrics, executionMetrics map[string]interface{}) map[string]interface{} {
	// Começar com métricas base
	merged := make(map[string]interface{})
	for key, value := range baseMetrics {
		merged[key] = value
	}

	// Adicionar métricas de execução
	for key, value := range executionMetrics {
		merged[key] = value
	}

	return merged
}
