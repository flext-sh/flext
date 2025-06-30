package services

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pluginEntities "github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// ExecutionStatus define o status de execução
type ExecutionStatus string

const (
	StatusPending    ExecutionStatus = "pending"
	StatusRunning    ExecutionStatus = "running"
	StatusCompleted  ExecutionStatus = "completed"
	StatusFailed     ExecutionStatus = "failed"
	StatusCancelled  ExecutionStatus = "cancelled"
)

// StepExecution representa a execução de um step
type StepExecution struct {
	StepID      uuid.UUID       `json:"step_id"`
	Status      ExecutionStatus `json:"status"`
	StartedAt   *time.Time      `json:"started_at,omitempty"`
	CompletedAt *time.Time      `json:"completed_at,omitempty"`
	Error       *string         `json:"error,omitempty"`
	Output      interface{}     `json:"output,omitempty"`
	Logs        []string        `json:"logs"`
}

// PipelineExecution representa a execução de um pipeline
type PipelineExecution struct {
	ID          uuid.UUID       `json:"id"`
	PipelineID  uuid.UUID       `json:"pipeline_id"`
	Status      ExecutionStatus `json:"status"`
	StartedAt   time.Time       `json:"started_at"`
	CompletedAt *time.Time      `json:"completed_at,omitempty"`
	Steps       []StepExecution `json:"steps"`
	Error       *string         `json:"error,omitempty"`
	Context     map[string]interface{} `json:"context"`
}

// PluginRepository interface para buscar plugins
type PluginRepository interface {
	GetByID(ctx context.Context, id uuid.UUID) (*pluginEntities.Plugin, error)
}

// PipelineExecutor executa pipelines
type PipelineExecutor struct {
	pluginRepo PluginRepository
	logger     logging.Logger
}

// NewPipelineExecutor cria um novo executor de pipeline
func NewPipelineExecutor(pluginRepo PluginRepository, logger logging.Logger) *PipelineExecutor {
	return &PipelineExecutor{
		pluginRepo: pluginRepo,
		logger:     logger,
	}
}

// Execute executa um pipeline
func (e *PipelineExecutor) Execute(ctx context.Context, pipeline *entities.Pipeline) (*PipelineExecution, error) {
	execution := &PipelineExecution{
		ID:         uuid.New(),
		PipelineID: pipeline.ID,
		Status:     StatusRunning,
		StartedAt:  time.Now(),
		Steps:      make([]StepExecution, len(pipeline.Steps)),
		Context:    make(map[string]interface{}),
	}

	logger := e.logger.With(
		logging.F("pipeline_id", pipeline.ID),
		logging.F("execution_id", execution.ID),
	)

	logger.Info("Starting pipeline execution")

	// Verificar se pipeline está ativo
	if !pipeline.IsActive {
		err := "pipeline is not active"
		execution.Status = StatusFailed
		execution.Error = &err
		now := time.Now()
		execution.CompletedAt = &now
		return execution, fmt.Errorf(err)
	}

	// Inicializar execução dos steps
	for i, step := range pipeline.Steps {
		execution.Steps[i] = StepExecution{
			StepID: step.ID,
			Status: StatusPending,
			Logs:   make([]string, 0),
		}
	}

	// Executar steps em ordem (simplificado - sem paralelização por enquanto)
	for i := range pipeline.Steps {
		stepExecution := &execution.Steps[i]
		
		if err := e.executeStep(ctx, &pipeline.Steps[i], stepExecution, execution.Context, logger); err != nil {
			execution.Status = StatusFailed
			errStr := err.Error()
			execution.Error = &errStr
			now := time.Now()
			execution.CompletedAt = &now
			
			logger.Error("Pipeline execution failed", 
				logging.F("step_id", stepExecution.StepID),
				logging.F("error", err.Error()),
			)
			return execution, err
		}
	}

	// Pipeline executado com sucesso
	execution.Status = StatusCompleted
	now := time.Now()
	execution.CompletedAt = &now
	
	logger.Info("Pipeline execution completed successfully")
	return execution, nil
}

// executeStep executa um step individual
func (e *PipelineExecutor) executeStep(
	ctx context.Context, 
	step *entities.PipelineStep, 
	execution *StepExecution, 
	pipelineContext map[string]interface{},
	logger logging.Logger,
) error {
	stepLogger := logger.With(logging.F("step_id", step.ID), logging.F("step_name", step.Name))
	
	stepLogger.Info("Starting step execution")
	
	// Marcar início da execução
	execution.Status = StatusRunning
	now := time.Now()
	execution.StartedAt = &now
	execution.Logs = append(execution.Logs, fmt.Sprintf("Step started at %s", now.Format(time.RFC3339)))

	// Buscar plugin
	plugin, err := e.pluginRepo.GetByID(ctx, step.PluginID)
	if err != nil {
		execution.Status = StatusFailed
		errStr := fmt.Sprintf("Failed to load plugin: %s", err.Error())
		execution.Error = &errStr
		execution.Logs = append(execution.Logs, errStr)
		return fmt.Errorf(errStr)
	}

	// Verificar se plugin está ativo
	if plugin.Status != pluginEntities.PluginStatusActive {
		// Tentar ativar plugin se estiver apenas registrado
		if plugin.Status == pluginEntities.PluginStatusRegistered {
			if err := plugin.Activate(); err != nil {
				execution.Status = StatusFailed
				errStr := fmt.Sprintf("Failed to activate plugin: %s", err.Error())
				execution.Error = &errStr
				execution.Logs = append(execution.Logs, errStr)
				return fmt.Errorf(errStr)
			}
			stepLogger.Info("Plugin activated successfully")
		} else {
			execution.Status = StatusFailed
			errStr := fmt.Sprintf("Plugin is not active (status: %s)", plugin.Status)
			execution.Error = &errStr
			execution.Logs = append(execution.Logs, errStr)
			return fmt.Errorf(errStr)
		}
	}

	// Simular execução do plugin (por enquanto)
	stepLogger.Info("Executing plugin", 
		logging.F("plugin_name", plugin.Name),
		logging.F("plugin_type", plugin.Type),
	)
	
	execution.Logs = append(execution.Logs, fmt.Sprintf("Executing plugin: %s (%s)", plugin.Name, plugin.Type))
	
	// Simular processamento
	time.Sleep(100 * time.Millisecond) // Simulação
	
	// Criar output simulado baseado no tipo de plugin
	output := map[string]interface{}{
		"plugin_name": plugin.Name,
		"plugin_type": string(plugin.Type),
		"processed":   true,
		"timestamp":   time.Now(),
	}
	
	// Adicionar configuração do step ao output
	if step.Configuration != nil {
		output["step_config"] = step.Configuration
	}
	
	execution.Output = output
	execution.Logs = append(execution.Logs, "Plugin execution completed successfully")
	
	// Atualizar contexto do pipeline com output do step
	pipelineContext[step.Name] = output
	
	// Marcar step como completo
	execution.Status = StatusCompleted
	completedAt := time.Now()
	execution.CompletedAt = &completedAt
	execution.Logs = append(execution.Logs, fmt.Sprintf("Step completed at %s", completedAt.Format(time.RFC3339)))
	
	stepLogger.Info("Step execution completed successfully")
	return nil
}

// TODO: Implementar execução real de plugins via:
// 1. Plugin loader dinâmico
// 2. Comunicação via gRPC/HTTP com plugins externos
// 3. Execução de binários com comunicação via stdin/stdout
// 4. Sistema de sandboxing para segurança