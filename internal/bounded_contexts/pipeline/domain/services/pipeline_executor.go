package services

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pluginEntities "github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
)

// ExecutionStatus define o status de execução
type ExecutionStatus string

const (
	StatusPending   ExecutionStatus = "pending"
	StatusRunning   ExecutionStatus = "running"
	StatusCompleted ExecutionStatus = "completed"
	StatusFailed    ExecutionStatus = "failed"
	StatusCancelled ExecutionStatus = "cancelled"
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
	ID          uuid.UUID              `json:"id"`
	PipelineID  uuid.UUID              `json:"pipeline_id"`
	Status      ExecutionStatus        `json:"status"`
	StartedAt   time.Time              `json:"started_at"`
	CompletedAt *time.Time             `json:"completed_at,omitempty"`
	Steps       []StepExecution        `json:"steps"`
	Error       *string                `json:"error,omitempty"`
	Context     map[string]interface{} `json:"context"`
}

// PluginRepository interface para buscar plugins (alias para o repositório do plugin)
type PluginRepository interface {
	GetByID(ctx context.Context, id uuid.UUID) (*pluginEntities.Plugin, error)
	GetActivePlugins(ctx context.Context) ([]*pluginEntities.Plugin, error)
}

// RealPluginExecutionContext contexto para execução real de plugins
type RealPluginExecutionContext struct {
	ExecutionID uuid.UUID              `json:"execution_id"`
	PipelineID  uuid.UUID              `json:"pipeline_id"`
	StepID      uuid.UUID              `json:"step_id"`
	InputData   map[string]interface{} `json:"input_data,omitempty"`
	Config      map[string]interface{} `json:"config"`
	Environment map[string]string      `json:"environment,omitempty"`
}

// RealPluginExecutionResult resultado da execução real
type RealPluginExecutionResult struct {
	Success      bool                   `json:"success"`
	ExitCode     int                    `json:"exit_code"`
	Duration     time.Duration          `json:"duration"`
	Data         map[string]interface{} `json:"data,omitempty"`
	RecordsCount int                    `json:"records_count"`
	Error        string                 `json:"error,omitempty"`
}

// RealPluginExecutor interface para execução real de plugins
type RealPluginExecutor interface {
	ExecuteSource(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error)
	ExecuteTarget(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error)
	ExecuteTransformer(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error)
	ExecuteUtility(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error)
}

// PipelineExecutor executa pipelines
type PipelineExecutor struct {
	pluginRepo   PluginRepository
	realExecutor RealPluginExecutor // Interface para execução real
}

// NewPipelineExecutor cria um novo executor de pipeline
func NewPipelineExecutor(pluginRepo PluginRepository, realExecutor RealPluginExecutor) *PipelineExecutor {
	return &PipelineExecutor{
		pluginRepo:   pluginRepo,
		realExecutor: realExecutor, // Executor real injetado
	}
}

// NewPipelineExecutorWithSimulation cria um executor apenas com simulação
func NewPipelineExecutorWithSimulation(pluginRepo PluginRepository) *PipelineExecutor {
	return &PipelineExecutor{
		pluginRepo:   pluginRepo,
		realExecutor: nil, // Usar apenas simulação
	}
}

// createRealPluginExecutor retorna o executor real de plugins
func (e *PipelineExecutor) createRealPluginExecutor() RealPluginExecutor {
	if e.realExecutor != nil {
		return e.realExecutor
	}
	
	// Se não há executor configurado, retornar nil para usar fallback
	return nil
}

// Execute executa um pipeline com execução real dos steps
func (e *PipelineExecutor) Execute(ctx context.Context, pipeline *entities.Pipeline) (*PipelineExecution, error) {
	execution := &PipelineExecution{
		ID:         uuid.New(),
		PipelineID: pipeline.ID,
		Status:     StatusRunning,
		StartedAt:  time.Now(),
		Steps:      make([]StepExecution, 0),
		Context:    make(map[string]interface{}),
	}

	// Verificar se pipeline está ativo
	if !pipeline.IsActive {
		err := "pipeline is not active"
		execution.Status = StatusFailed
		execution.Error = &err
		now := time.Now()
		execution.CompletedAt = &now
		return execution, fmt.Errorf("%s", err)
	}

	// Verificar se pipeline tem steps
	if len(pipeline.Steps) == 0 {
		err := "pipeline has no steps to execute"
		execution.Status = StatusFailed
		execution.Error = &err
		now := time.Now()
		execution.CompletedAt = &now
		return execution, fmt.Errorf("%s", err)
	}

	// Executar steps do pipeline
	dataFlow := make(map[string]interface{})
	
	for _, step := range pipeline.Steps {
		stepExecution := &StepExecution{
			StepID:    step.ID,
			Status:    StatusRunning,
			StartedAt: func() *time.Time { t := time.Now(); return &t }(),
			Logs:      make([]string, 0),
		}

		// Executar step
		if err := e.executeStep(ctx, &step, stepExecution, dataFlow); err != nil {
			// Se step falhou, falhar toda a execução
			execution.Status = StatusFailed
			errStr := fmt.Sprintf("Step %s failed: %v", step.Name, err)
			execution.Error = &errStr
			now := time.Now()
			execution.CompletedAt = &now
			execution.Steps = append(execution.Steps, *stepExecution)
			return execution, fmt.Errorf("%s", errStr)
		}

		execution.Steps = append(execution.Steps, *stepExecution)
	}

	// Pipeline executado com sucesso
	execution.Status = StatusCompleted
	now := time.Now()
	execution.CompletedAt = &now
	execution.Context["data_flow"] = dataFlow

	return execution, nil
}

// executeStep executa um step individual com execução real do plugin
func (e *PipelineExecutor) executeStep(
	ctx context.Context,
	step *entities.PipelineStep,
	execution *StepExecution,
	dataFlow map[string]interface{},
) error {
	// Marcar início da execução
	execution.Status = StatusRunning
	execution.Logs = append(execution.Logs, fmt.Sprintf("Step '%s' started", step.Name))

	// Buscar plugin
	plugin, err := e.pluginRepo.GetByID(ctx, step.PluginID)
	if err != nil {
		execution.Status = StatusFailed
		errStr := fmt.Sprintf("Failed to load plugin: %s", err.Error())
		execution.Error = &errStr
		execution.Logs = append(execution.Logs, errStr)
		return fmt.Errorf("%s", errStr)
	}

	if plugin == nil {
		execution.Status = StatusFailed
		errStr := "Plugin not found"
		execution.Error = &errStr
		execution.Logs = append(execution.Logs, errStr)
		return fmt.Errorf("%s", errStr)
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
				return fmt.Errorf("%s", errStr)
			}
			execution.Logs = append(execution.Logs, "Plugin activated successfully")
		} else {
			execution.Status = StatusFailed
			errStr := fmt.Sprintf("Plugin is not active (status: %s)", plugin.Status)
			execution.Error = &errStr
			execution.Logs = append(execution.Logs, errStr)
			return fmt.Errorf("%s", errStr)
		}
	}

	execution.Logs = append(execution.Logs, fmt.Sprintf("Executing plugin: %s (%s)", plugin.Name, plugin.Type))

	// Preparar dados de entrada do step
	inputData := e.prepareStepInputData(step, dataFlow)

	// Executar plugin baseado no tipo
	var output map[string]interface{}
	var recordsProcessed int

	switch plugin.Type {
	case pluginEntities.PluginTypeSource:
		output, recordsProcessed, err = e.executeSourcePlugin(ctx, plugin, step, inputData)
	case pluginEntities.PluginTypeTarget:
		output, recordsProcessed, err = e.executeTargetPlugin(ctx, plugin, step, inputData)
	case pluginEntities.PluginTypeTransformer:
		output, recordsProcessed, err = e.executeTransformerPlugin(ctx, plugin, step, inputData)
	case pluginEntities.PluginTypeUtility:
		output, recordsProcessed, err = e.executeUtilityPlugin(ctx, plugin, step, inputData)
	default:
		err = fmt.Errorf("unsupported plugin type: %s", plugin.Type)
	}

	if err != nil {
		execution.Status = StatusFailed
		errStr := fmt.Sprintf("Plugin execution failed: %v", err)
		execution.Error = &errStr
		execution.Logs = append(execution.Logs, errStr)
		return fmt.Errorf("%s", errStr)
	}

	// Sucesso
	execution.Status = StatusCompleted
	execution.Output = output
	completedAt := time.Now()
	execution.CompletedAt = &completedAt
	execution.Logs = append(execution.Logs, fmt.Sprintf("Step completed successfully (%d records processed)", recordsProcessed))

	// Adicionar output ao data flow
	dataFlow[step.ID.String()] = output

	return nil
}

// prepareStepInputData prepara dados de entrada para um step
func (e *PipelineExecutor) prepareStepInputData(step *entities.PipelineStep, dataFlow map[string]interface{}) map[string]interface{} {
	inputData := make(map[string]interface{})

	// Adicionar configuração do step
	for key, value := range step.Configuration {
		inputData[key] = value
	}

	// Adicionar dados de steps dependentes
	for _, depID := range step.DependsOn {
		if data, exists := dataFlow[depID.String()]; exists {
			inputData[fmt.Sprintf("dependency_%s", depID.String())] = data
		}
	}

	return inputData
}

// executeSourcePlugin executa um plugin de fonte (extração) - IMPLEMENTAÇÃO REAL
func (e *PipelineExecutor) executeSourcePlugin(
	ctx context.Context,
	plugin *pluginEntities.Plugin,
	step *entities.PipelineStep,
	inputData map[string]interface{},
) (map[string]interface{}, int, error) {
	
	// IMPLEMENTAÇÃO REAL: execução via infrastructure layer
	// Delegar para o executor real de plugins
	
	// Criar executor de plugin real (infrastructure layer)
	realExecutor := e.createRealPluginExecutor()
	
	// Se não há executor real configurado, usar implementação simulada temporariamente
	if realExecutor == nil {
		// Fallback para simulação se não há executor real
		time.Sleep(100 * time.Millisecond)
		output := map[string]interface{}{
			"plugin_name":       plugin.Name,
			"plugin_type":       string(plugin.Type),
			"extraction_time":   time.Now(),
			"records_extracted": 100, // Simulado
			"execution_success": true,
			"execution_mode":    "simulation", // Indica que é simulação
			"records": []map[string]interface{}{
				{"id": 1, "name": "simulated_user_1", "email": "user1@example.com"},
				{"id": 2, "name": "simulated_user_2", "email": "user2@example.com"},
			},
		}
		return output, 100, nil
	}
	
	// Preparar contexto de execução
	execCtx := &RealPluginExecutionContext{
		ExecutionID: uuid.New(),
		PipelineID:  uuid.Nil, // Will be set by caller context
		StepID:      step.ID,
		InputData:   inputData,
		Config:      step.Configuration,
		Environment: map[string]string{
			"FLEXT_PLUGIN_TYPE": string(plugin.Type),
			"FLEXT_STEP_NAME":   step.Name,
		},
	}
	
	// Executar plugin real
	result, err := realExecutor.ExecuteSource(ctx, plugin, execCtx)
	if err != nil {
		return nil, 0, fmt.Errorf("real source plugin execution failed: %w", err)
	}
	
	// Retornar dados reais extraídos
	output := map[string]interface{}{
		"plugin_name":       plugin.Name,
		"plugin_type":       string(plugin.Type),
		"extraction_time":   time.Now(),
		"records_extracted": result.RecordsCount,
		"execution_success": result.Success,
		"execution_duration": result.Duration,
		"real_data":         result.Data,
		"records":           result.Data["records"], // Dados reais para próximos steps
	}

	return output, result.RecordsCount, nil
}

// executeTargetPlugin executa um plugin de destino (carregamento) - IMPLEMENTAÇÃO REAL
func (e *PipelineExecutor) executeTargetPlugin(
	ctx context.Context,
	plugin *pluginEntities.Plugin,
	step *entities.PipelineStep,
	inputData map[string]interface{},
) (map[string]interface{}, int, error) {
	
	// IMPLEMENTAÇÃO REAL: execução via infrastructure layer
	// Delegar para o executor real de plugins
	
	// Criar executor de plugin real (infrastructure layer)
	realExecutor := e.createRealPluginExecutor()
	
	// Se não há executor real configurado, usar implementação simulada temporariamente
	if realExecutor == nil {
		// Fallback para simulação se não há executor real
		recordsToLoad := 0
		for key, value := range inputData {
			if strings.Contains(key, "dependency_") || key == "records" {
				if records, ok := value.([]interface{}); ok {
					recordsToLoad += len(records)
				}
			}
		}
		
		time.Sleep(80 * time.Millisecond)
		output := map[string]interface{}{
			"plugin_name":       plugin.Name,
			"plugin_type":       string(plugin.Type),
			"load_time":         time.Now(),
			"records_loaded":    recordsToLoad,
			"execution_success": true,
			"execution_mode":    "simulation", // Indica que é simulação
			"load_status":       "simulated_success",
		}
		return output, recordsToLoad, nil
	}
	
	// Preparar contexto de execução com dados de entrada
	execCtx := &RealPluginExecutionContext{
		ExecutionID: uuid.New(),
		PipelineID:  uuid.Nil, // Will be set by caller context
		StepID:      step.ID,
		InputData:   inputData, // Inclui records dos steps anteriores
		Config:      step.Configuration,
		Environment: map[string]string{
			"FLEXT_PLUGIN_TYPE": string(plugin.Type),
			"FLEXT_STEP_NAME":   step.Name,
		},
	}
	
	// Executar plugin real
	result, err := realExecutor.ExecuteTarget(ctx, plugin, execCtx)
	if err != nil {
		return nil, 0, fmt.Errorf("real target plugin execution failed: %w", err)
	}
	
	// Retornar resultado real do carregamento
	output := map[string]interface{}{
		"plugin_name":       plugin.Name,
		"plugin_type":       string(plugin.Type),
		"load_time":         time.Now(),
		"records_loaded":    result.RecordsCount,
		"execution_success": result.Success,
		"execution_duration": result.Duration,
		"target_result":     result.Data,
		"load_status":       "completed",
	}

	return output, result.RecordsCount, nil
}

// executeTransformerPlugin executa um plugin de transformação - IMPLEMENTAÇÃO REAL
func (e *PipelineExecutor) executeTransformerPlugin(
	ctx context.Context,
	plugin *pluginEntities.Plugin,
	step *entities.PipelineStep,
	inputData map[string]interface{},
) (map[string]interface{}, int, error) {
	
	// IMPLEMENTAÇÃO REAL: execução via infrastructure layer
	realExecutor := e.createRealPluginExecutor()
	
	// Se não há executor real configurado, usar implementação simulada temporariamente
	if realExecutor == nil {
		// Fallback para simulação se não há executor real
		time.Sleep(60 * time.Millisecond)
		output := map[string]interface{}{
			"plugin_name":           plugin.Name,
			"plugin_type":           string(plugin.Type),
			"transformation_time":   time.Now(),
			"records_transformed":   50, // Simulado
			"execution_success":     true,
			"execution_mode":        "simulation", // Indica que é simulação
			"transformation_rules":  inputData["rules"],
			"records": []map[string]interface{}{
				{"id": 1, "name": "transformed_user_1", "email": "t_user1@example.com", "status": "active"},
				{"id": 2, "name": "transformed_user_2", "email": "t_user2@example.com", "status": "active"},
			},
		}
		return output, 50, nil
	}
	
	// Preparar contexto de execução
	execCtx := &RealPluginExecutionContext{
		ExecutionID: uuid.New(),
		PipelineID:  uuid.Nil, // Will be set by caller context
		StepID:      step.ID,
		InputData:   inputData,
		Config:      step.Configuration,
		Environment: map[string]string{
			"FLEXT_PLUGIN_TYPE": string(plugin.Type),
			"FLEXT_STEP_NAME":   step.Name,
		},
	}
	
	// Executar plugin real
	result, err := realExecutor.ExecuteTransformer(ctx, plugin, execCtx)
	if err != nil {
		return nil, 0, fmt.Errorf("real transformer plugin execution failed: %w", err)
	}
	
	// Retornar resultado real da transformação
	output := map[string]interface{}{
		"plugin_name":           plugin.Name,
		"plugin_type":           string(plugin.Type),
		"transformation_time":   time.Now(),
		"records_transformed":   result.RecordsCount,
		"execution_success":     result.Success,
		"execution_duration":    result.Duration,
		"transformed_data":      result.Data,
		"records":               result.Data["records"], // Dados transformados
	}

	return output, result.RecordsCount, nil
}

// executeUtilityPlugin executa um plugin utilitário - IMPLEMENTAÇÃO REAL
func (e *PipelineExecutor) executeUtilityPlugin(
	ctx context.Context,
	plugin *pluginEntities.Plugin,
	step *entities.PipelineStep,
	inputData map[string]interface{},
) (map[string]interface{}, int, error) {
	
	// IMPLEMENTAÇÃO REAL: execução via infrastructure layer
	realExecutor := e.createRealPluginExecutor()
	
	// Se não há executor real configurado, usar implementação simulada temporariamente
	if realExecutor == nil {
		// Fallback para simulação se não há executor real
		time.Sleep(30 * time.Millisecond)
		output := map[string]interface{}{
			"plugin_name":      plugin.Name,
			"plugin_type":      string(plugin.Type),
			"execution_time":   time.Now(),
			"utility_result":   "simulated_success",
			"operations":       []string{"validate", "clean", "notify"},
			"execution_success": true,
			"execution_mode":   "simulation", // Indica que é simulação
		}
		return output, 1, nil
	}
	
	// Preparar contexto de execução
	execCtx := &RealPluginExecutionContext{
		ExecutionID: uuid.New(),
		PipelineID:  uuid.Nil, // Will be set by caller context
		StepID:      step.ID,
		InputData:   inputData,
		Config:      step.Configuration,
		Environment: map[string]string{
			"FLEXT_PLUGIN_TYPE": string(plugin.Type),
			"FLEXT_STEP_NAME":   step.Name,
		},
	}
	
	// Executar plugin real
	result, err := realExecutor.ExecuteUtility(ctx, plugin, execCtx)
	if err != nil {
		return nil, 0, fmt.Errorf("real utility plugin execution failed: %w", err)
	}
	
	// Retornar resultado real da operação utilitária
	output := map[string]interface{}{
		"plugin_name":       plugin.Name,
		"plugin_type":       string(plugin.Type),
		"execution_time":    time.Now(),
		"execution_success": result.Success,
		"execution_duration": result.Duration,
		"utility_result":    result.Data,
		"operations_count":  result.RecordsCount,
		"execution_mode":    "real", // Indica que é execução real
	}

	return output, result.RecordsCount, nil
}

/*
func (e *PipelineExecutor) executeStep(
	ctx context.Context,
	step *entities.PipelineStep,
	execution *StepExecution,
	pipelineContext map[string]interface{},
) error {
	// Logging removido - domain layer não deve ter logging

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
		return fmt.Errorf("%s", errStr)
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
				return fmt.Errorf("%s", errStr)
			}
			// Log removido
		} else {
			execution.Status = StatusFailed
			errStr := fmt.Sprintf("Plugin is not active (status: %s)", plugin.Status)
			execution.Error = &errStr
			execution.Logs = append(execution.Logs, errStr)
			return fmt.Errorf("%s", errStr)
		}
	}

	// Simular execução do plugin (por enquanto)
	// Logs removidos - devem ser feitos na camada superior

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

	// Log removido - domain não deve ter logging
	return nil
}

// TODO: Implementar execução real de plugins via:
// 1. Plugin loader dinâmico
// 2. Comunicação via gRPC/HTTP com plugins externos
// 3. Execução de binários com comunicação via stdin/stdout
// 4. Sistema de sandboxing para segurança
*/
