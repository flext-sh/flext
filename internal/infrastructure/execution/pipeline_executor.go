package execution

import (
	"context"
	"fmt"
	"path/filepath"
	"sync"
	"time"

	pipelineEntities "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// RealPipelineExecutor executes pipelines with real plugin execution
type RealPipelineExecutor struct {
	pluginRepo     ports.PluginRepository
	pluginExecutor *PluginExecutor
	logger         logging.Logger
	workDir        string
	maxConcurrency int
}

// PipelineExecution represents a complete pipeline execution
type PipelineExecution struct {
	ID           uuid.UUID              `json:"id"`
	PipelineID   uuid.UUID              `json:"pipeline_id"`
	Status       ExecutionStatus        `json:"status"`
	StartedAt    time.Time              `json:"started_at"`
	CompletedAt  *time.Time             `json:"completed_at,omitempty"`
	Steps        []*StepExecution       `json:"steps"`
	Error        *string                `json:"error,omitempty"`
	Context      map[string]interface{} `json:"context,omitempty"`
	TotalRecords int                    `json:"total_records"`
	DataFlow     map[string]interface{} `json:"data_flow,omitempty"`
}

// StepExecution represents a single step execution
type StepExecution struct {
	StepID      uuid.UUID              `json:"step_id"`
	Name        string                 `json:"name"`
	PluginID    uuid.UUID              `json:"plugin_id"`
	Status      ExecutionStatus        `json:"status"`
	StartedAt   *time.Time             `json:"started_at,omitempty"`
	CompletedAt *time.Time             `json:"completed_at,omitempty"`
	Duration    time.Duration          `json:"duration"`
	Result      *ExecutionResult       `json:"result,omitempty"`
	InputData   map[string]interface{} `json:"input_data,omitempty"`
	OutputData  map[string]interface{} `json:"output_data,omitempty"`
	Logs        []string               `json:"logs,omitempty"`
	Error       *string                `json:"error,omitempty"`
}

// ExecutionStatus represents the status of an execution
type ExecutionStatus string

const (
	StatusPending   ExecutionStatus = "pending"
	StatusRunning   ExecutionStatus = "running"
	StatusCompleted ExecutionStatus = "completed"
	StatusFailed    ExecutionStatus = "failed"
	StatusCancelled ExecutionStatus = "cancelled"
)

// NewRealPipelineExecutor creates a new real pipeline executor
func NewRealPipelineExecutor(
	pluginRepo ports.PluginRepository,
	logger logging.Logger,
	workDir string,
	pythonPath string,
) *RealPipelineExecutor {
	return &RealPipelineExecutor{
		pluginRepo:     pluginRepo,
		pluginExecutor: NewPluginExecutor(logger, filepath.Join(workDir, "plugin_executions"), pythonPath),
		logger:         logger,
		workDir:        workDir,
		maxConcurrency: 5, // Default max concurrent steps
	}
}

// SetMaxConcurrency sets the maximum number of concurrent step executions
func (e *RealPipelineExecutor) SetMaxConcurrency(max int) {
	e.maxConcurrency = max
}

// Execute executes a complete pipeline with real plugin execution
func (e *RealPipelineExecutor) Execute(ctx context.Context, pipeline *pipelineEntities.Pipeline) (*PipelineExecution, error) {
	executionID := uuid.New()
	startTime := time.Now()

	e.logger.Info("Starting real pipeline execution",
		logging.F("pipeline_id", pipeline.ID.String()),
		logging.F("pipeline_name", pipeline.Name),
		logging.F("execution_id", executionID.String()),
		logging.F("steps_count", len(pipeline.Steps)),
	)

	execution := &PipelineExecution{
		ID:         executionID,
		PipelineID: pipeline.ID,
		Status:     StatusRunning,
		StartedAt:  startTime,
		Steps:      make([]*StepExecution, 0, len(pipeline.Steps)),
		Context:    make(map[string]interface{}),
		DataFlow:   make(map[string]interface{}),
	}

	// Validate pipeline can be executed
	if err := e.validatePipeline(pipeline); err != nil {
		return e.failExecution(execution, fmt.Sprintf("Pipeline validation failed: %v", err)), nil
	}

	// Create execution plan (order steps by dependencies)
	executionPlan, err := e.createExecutionPlan(pipeline.Steps)
	if err != nil {
		return e.failExecution(execution, fmt.Sprintf("Failed to create execution plan: %v", err)), nil
	}

	e.logger.Info("Pipeline execution plan created",
		logging.F("execution_id", executionID.String()),
		logging.F("planned_steps", len(executionPlan)),
	)

	// Execute steps according to plan
	dataFlow := make(map[string]interface{})

	for i, stepGroup := range executionPlan {
		e.logger.Info("Executing step group",
			logging.F("execution_id", executionID.String()),
			logging.F("group_index", i),
			logging.F("steps_in_group", len(stepGroup)),
		)

		// Execute steps in this group (can be concurrent if no dependencies)
		groupResults, err := e.executeStepGroup(ctx, stepGroup, dataFlow, execution)
		if err != nil {
			return e.failExecution(execution, fmt.Sprintf("Step group %d failed: %v", i, err)), nil
		}

		// Update data flow with results from this group
		for stepID, result := range groupResults {
			if result.OutputData != nil {
				dataFlow[stepID] = result.OutputData
				execution.TotalRecords += result.Result.RecordsCount
			}
		}

		// Check if any step in the group failed
		for _, result := range groupResults {
			if result.Status == StatusFailed {
				return e.failExecution(execution, fmt.Sprintf("Step %s failed: %s",
					result.Name, *result.Error)), nil
			}
		}
	}

	// Complete execution successfully
	completedAt := time.Now()
	execution.CompletedAt = &completedAt
	execution.Status = StatusCompleted
	execution.DataFlow = dataFlow

	e.logger.Info("Pipeline execution completed successfully",
		logging.F("execution_id", executionID.String()),
		logging.F("duration", completedAt.Sub(startTime).String()),
		logging.F("total_records", execution.TotalRecords),
		logging.F("steps_executed", len(execution.Steps)),
	)

	return execution, nil
}

// validatePipeline validates that the pipeline can be executed
func (e *RealPipelineExecutor) validatePipeline(pipeline *pipelineEntities.Pipeline) error {
	if len(pipeline.Steps) == 0 {
		return fmt.Errorf("pipeline has no steps")
	}

	if !pipeline.IsActive {
		return fmt.Errorf("pipeline is not active")
	}

	// Validate that all referenced plugins exist
	for _, step := range pipeline.Steps {
		plugin, err := e.pluginRepo.GetByID(context.Background(), step.PluginID)
		if err != nil {
			return fmt.Errorf("failed to load plugin %s for step %s: %w",
				step.PluginID.String(), step.Name, err)
		}
		if plugin == nil {
			return fmt.Errorf("plugin %s not found for step %s",
				step.PluginID.String(), step.Name)
		}
	}

	return nil
}

// createExecutionPlan creates an execution plan respecting step dependencies
func (e *RealPipelineExecutor) createExecutionPlan(steps []pipelineEntities.PipelineStep) ([][]*pipelineEntities.PipelineStep, error) {
	// Create a map for quick step lookup
	stepMap := make(map[uuid.UUID]*pipelineEntities.PipelineStep)
	for i := range steps {
		stepMap[steps[i].ID] = &steps[i]
	}

	// Track completed steps
	completed := make(map[uuid.UUID]bool)
	executionPlan := make([][]*pipelineEntities.PipelineStep, 0)

	// Keep adding groups until all steps are planned
	for len(completed) < len(steps) {
		// Find steps that can be executed (all dependencies completed)
		var readySteps []*pipelineEntities.PipelineStep

		for i := range steps {
			step := &steps[i]
			if completed[step.ID] {
				continue // Already completed
			}

			// Check if all dependencies are completed
			canExecute := true
			for _, depID := range step.DependsOn {
				if !completed[depID] {
					canExecute = false
					break
				}
			}

			if canExecute {
				readySteps = append(readySteps, step)
			}
		}

		if len(readySteps) == 0 {
			return nil, fmt.Errorf("circular dependency detected or invalid dependencies")
		}

		// Add this group to the execution plan
		executionPlan = append(executionPlan, readySteps)

		// Mark these steps as completed for dependency checking
		for _, step := range readySteps {
			completed[step.ID] = true
		}
	}

	return executionPlan, nil
}

// executeStepGroup executes a group of steps (potentially in parallel)
func (e *RealPipelineExecutor) executeStepGroup(
	ctx context.Context,
	steps []*pipelineEntities.PipelineStep,
	dataFlow map[string]interface{},
	execution *PipelineExecution,
) (map[string]*StepExecution, error) {

	results := make(map[string]*StepExecution)
	var wg sync.WaitGroup
	var mu sync.Mutex
	errorChan := make(chan error, len(steps))

	// Limit concurrency
	semaphore := make(chan struct{}, e.maxConcurrency)

	for _, step := range steps {
		wg.Add(1)
		go func(s *pipelineEntities.PipelineStep) {
			defer wg.Done()

			// Acquire semaphore
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			stepExecution, err := e.executeStep(ctx, s, dataFlow, execution)

			mu.Lock()
			results[s.ID.String()] = stepExecution
			execution.Steps = append(execution.Steps, stepExecution)
			mu.Unlock()

			if err != nil {
				select {
				case errorChan <- err:
				default:
				}
			}
		}(step)
	}

	wg.Wait()
	close(errorChan)

	// Check for errors
	if err := <-errorChan; err != nil {
		return results, err
	}

	return results, nil
}

// executeStep executes a single pipeline step
func (e *RealPipelineExecutor) executeStep(
	ctx context.Context,
	step *pipelineEntities.PipelineStep,
	dataFlow map[string]interface{},
	execution *PipelineExecution,
) (*StepExecution, error) {

	startTime := time.Now()

	stepExecution := &StepExecution{
		StepID:    step.ID,
		Name:      step.Name,
		PluginID:  step.PluginID,
		Status:    StatusRunning,
		StartedAt: &startTime,
		Logs:      make([]string, 0),
		InputData: make(map[string]interface{}),
	}

	e.logger.Info("Executing pipeline step",
		logging.F("execution_id", execution.ID.String()),
		logging.F("step_id", step.ID.String()),
		logging.F("step_name", step.Name),
		logging.F("plugin_id", step.PluginID.String()),
	)

	// Load plugin
	plugin, err := e.pluginRepo.GetByID(ctx, step.PluginID)
	if err != nil {
		return e.failStep(stepExecution, fmt.Sprintf("Failed to load plugin: %v", err)), err
	}

	// Prepare input data from dependencies
	inputData := e.prepareInputData(step, dataFlow)
	stepExecution.InputData = inputData

	// Create plugin execution context
	pluginCtx := &PluginExecutionContext{
		ExecutionID: execution.ID,
		PipelineID:  execution.PipelineID,
		StepID:      step.ID,
		InputData:   inputData,
		Config:      step.Configuration,
		Environment: map[string]string{
			"FLEXT_EXECUTION_ID": execution.ID.String(),
			"FLEXT_PIPELINE_ID":  execution.PipelineID.String(),
			"FLEXT_STEP_ID":      step.ID.String(),
		},
	}

	// Execute plugin
	result, err := e.pluginExecutor.Execute(ctx, plugin, pluginCtx)
	if err != nil {
		return e.failStep(stepExecution, fmt.Sprintf("Plugin execution error: %v", err)), err
	}

	stepExecution.Result = result

	// Complete step execution
	completedAt := time.Now()
	stepExecution.CompletedAt = &completedAt
	stepExecution.Duration = completedAt.Sub(startTime)

	if result.Success {
		stepExecution.Status = StatusCompleted
		stepExecution.OutputData = result.Data

		// Add execution logs
		if result.Stdout != "" {
			stepExecution.Logs = append(stepExecution.Logs,
				fmt.Sprintf("STDOUT: %s", result.Stdout))
		}
		if result.Stderr != "" {
			stepExecution.Logs = append(stepExecution.Logs,
				fmt.Sprintf("STDERR: %s", result.Stderr))
		}

		e.logger.Info("Step execution completed successfully",
			logging.F("step_id", step.ID.String()),
			logging.F("duration", stepExecution.Duration.String()),
			logging.F("records_count", result.RecordsCount),
		)
	} else {
		stepExecution.Status = StatusFailed
		errorMsg := result.Error
		if errorMsg == "" {
			errorMsg = "Plugin execution failed with no specific error"
		}
		stepExecution.Error = &errorMsg

		e.logger.Error("Step execution failed",
			logging.F("step_id", step.ID.String()),
			logging.F("error", errorMsg),
			logging.F("exit_code", result.ExitCode),
		)
	}

	return stepExecution, nil
}

// prepareInputData prepares input data for a step from dataFlow and dependencies
func (e *RealPipelineExecutor) prepareInputData(step *pipelineEntities.PipelineStep, dataFlow map[string]interface{}) map[string]interface{} {
	inputData := make(map[string]interface{})

	// Add data from dependent steps
	for _, depID := range step.DependsOn {
		if data, exists := dataFlow[depID.String()]; exists {
			inputData[fmt.Sprintf("dependency_%s", depID.String())] = data
		}
	}

	// Add step configuration as input
	for key, value := range step.Configuration {
		inputData[key] = value
	}

	// If this is a target step, try to find source data
	if len(step.DependsOn) > 0 {
		// Aggregate records from all dependencies for target steps
		var allRecords []interface{}
		for _, depID := range step.DependsOn {
			if data, exists := dataFlow[depID.String()]; exists {
				if records, ok := data.(map[string]interface{})["records"]; ok {
					if recordList, ok := records.([]interface{}); ok {
						allRecords = append(allRecords, recordList...)
					}
				}
			}
		}
		if len(allRecords) > 0 {
			inputData["records"] = allRecords
		}
	}

	return inputData
}

// failExecution marks an execution as failed
func (e *RealPipelineExecutor) failExecution(execution *PipelineExecution, errorMsg string) *PipelineExecution {
	completedAt := time.Now()
	execution.CompletedAt = &completedAt
	execution.Status = StatusFailed
	execution.Error = &errorMsg

	e.logger.Error("Pipeline execution failed",
		logging.F("execution_id", execution.ID.String()),
		logging.F("error", errorMsg),
	)

	return execution
}

// failStep marks a step execution as failed
func (e *RealPipelineExecutor) failStep(stepExecution *StepExecution, errorMsg string) *StepExecution {
	completedAt := time.Now()
	stepExecution.CompletedAt = &completedAt
	stepExecution.Status = StatusFailed
	stepExecution.Error = &errorMsg
	stepExecution.Duration = completedAt.Sub(*stepExecution.StartedAt)

	return stepExecution
}
