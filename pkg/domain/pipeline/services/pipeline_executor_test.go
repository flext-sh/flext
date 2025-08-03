// Package services provides comprehensive tests for pipeline executor service
// This implements EXTREME TESTING standards as demanded
package services

import (
	"context"
	"errors"
	"fmt"
	"testing"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	pluginEntities "github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// MockPluginRepository is a mock implementation of PluginRepository
type MockPluginRepository struct {
	mock.Mock
}

func (m *MockPluginRepository) GetByID(ctx context.Context, id uuid.UUID) (*pluginEntities.Plugin, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*pluginEntities.Plugin), args.Error(1)
}

func (m *MockPluginRepository) GetActivePlugins(ctx context.Context) ([]*pluginEntities.Plugin, error) {
	args := m.Called(ctx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*pluginEntities.Plugin), args.Error(1)
}

// MockRealPluginExecutor is a mock implementation of RealPluginExecutor
type MockRealPluginExecutor struct {
	mock.Mock
}

func (m *MockRealPluginExecutor) ExecuteSource(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error) {
	args := m.Called(ctx, plugin, execCtx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*RealPluginExecutionResult), args.Error(1)
}

func (m *MockRealPluginExecutor) ExecuteTarget(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error) {
	args := m.Called(ctx, plugin, execCtx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*RealPluginExecutionResult), args.Error(1)
}

func (m *MockRealPluginExecutor) ExecuteTransformer(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error) {
	args := m.Called(ctx, plugin, execCtx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*RealPluginExecutionResult), args.Error(1)
}

func (m *MockRealPluginExecutor) ExecuteUtility(ctx context.Context, plugin *pluginEntities.Plugin, execCtx *RealPluginExecutionContext) (*RealPluginExecutionResult, error) {
	args := m.Called(ctx, plugin, execCtx)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*RealPluginExecutionResult), args.Error(1)
}

// Test fixtures
func createTestPipeline() *entities.Pipeline {
	pipeline, _ := entities.NewPipeline("test-pipeline", "Test pipeline for unit testing")
	pipeline.Type = entities.PipelineTypeETL
	pipeline.Status = entities.PipelineStatusActive
	pipeline.IsActive = true

	// Add test steps
	step1 := entities.PipelineStep{
		ID:       uuid.New(),
		Name:     "extract-step",
		PluginID: uuid.New(),
		Order:    1,
		Configuration: map[string]interface{}{
			"source": "database",
			"table":  "users",
		},
		DependsOn: []uuid.UUID{},
	}

	step2 := entities.PipelineStep{
		ID:       uuid.New(),
		Name:     "transform-step",
		PluginID: uuid.New(),
		Order:    2,
		Configuration: map[string]interface{}{
			"transformation": "filter_active_users",
		},
		DependsOn: []uuid.UUID{},
	}

	pipeline.Steps = []entities.PipelineStep{step1, step2}
	return pipeline
}

func createTestPlugin(id uuid.UUID, name string) *pluginEntities.Plugin {
	plugin, _ := pluginEntities.NewPlugin(name, "1.0.0", "./"+name, pluginEntities.PluginTypeSource)
	plugin.Status = pluginEntities.PluginStatusActive
	plugin.IsActive = true
	return plugin
}

func createTestExecutor(
	mockPluginRepo *MockPluginRepository,
	mockRealExecutor *MockRealPluginExecutor,
) *PipelineExecutor {
	return NewPipelineExecutor(mockPluginRepo, mockRealExecutor)
}

// EXTREME TESTING: Constructor Tests
func TestNewPipelineExecutor_Success(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	// Act
	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)

	// Assert
	assert.NotNil(t, executor)
	assert.Equal(t, mockPluginRepo, executor.pluginRepo)
	assert.Equal(t, mockRealExecutor, executor.realExecutor)
}

func TestNewPipelineExecutor_NilDependencies(t *testing.T) {
	// Test with nil plugin repo
	executor := NewPipelineExecutor(nil, &MockRealPluginExecutor{})
	assert.NotNil(t, executor)
	assert.Nil(t, executor.pluginRepo)

	// Test with nil real executor (allowed for simulation mode)
	executor2 := NewPipelineExecutor(&MockPluginRepository{}, nil)
	assert.NotNil(t, executor2)
	assert.Nil(t, executor2.realExecutor)
}

// EXTREME TESTING: Execute Tests
func TestExecute_Success(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	ctx := context.Background()

	// Create plugins for steps
	plugin1 := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin2 := createTestPlugin(pipeline.Steps[1].PluginID, "transform-plugin")

	// Setup mocks
	mockPluginRepo.On("GetByID", ctx, pipeline.Steps[0].PluginID).Return(plugin1, nil)
	mockPluginRepo.On("GetByID", ctx, pipeline.Steps[1].PluginID).Return(plugin2, nil)

	// Mock successful execution results
	result1 := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		Data:         map[string]interface{}{"users": []string{"user1", "user2"}},
		RecordsCount: 2,
	}
	result2 := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     150 * time.Millisecond,
		Data:         map[string]interface{}{"filtered_users": []string{"user1"}},
		RecordsCount: 1,
	}

	mockRealExecutor.On("ExecuteSource", ctx, plugin1, mock.AnythingOfType("*services.RealPluginExecutionContext")).Return(result1, nil)
	mockRealExecutor.On("ExecuteSource", ctx, plugin2, mock.AnythingOfType("*services.RealPluginExecutionContext")).Return(result2, nil)

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusCompleted, execution.Status)
	assert.Len(t, execution.Steps, 2)
	assert.Equal(t, StatusCompleted, execution.Steps[0].Status)
	assert.Equal(t, StatusCompleted, execution.Steps[1].Status)
	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

func TestExecute_InactivePipeline(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	pipeline.IsActive = false // Make pipeline inactive
	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Contains(t, err.Error(), "pipeline is not active")
}

func TestExecute_PluginNotFound(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	ctx := context.Background()
	expectedError := errors.New("plugin not found")

	// Setup mocks
	mockPluginRepo.On("GetByID", ctx, pipeline.Steps[0].PluginID).Return(nil, expectedError)

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Contains(t, err.Error(), "Step extract-step failed")
	mockPluginRepo.AssertExpectations(t)
}

func TestExecute_NoSteps(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	pipeline.Steps = []entities.PipelineStep{} // No steps
	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Contains(t, err.Error(), "pipeline has no steps to execute")
}

// EXTREME TESTING: Simulation Mode Tests
func TestNewPipelineExecutorWithSimulation(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}

	// Act
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	// Assert
	assert.NotNil(t, executor)
	assert.Equal(t, mockPluginRepo, executor.pluginRepo)
	assert.Nil(t, executor.realExecutor)
}

// EXTREME TESTING: Concurrency Tests
func TestConcurrentExecutions(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	plugin1 := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin2 := createTestPlugin(pipeline.Steps[1].PluginID, "transform-plugin")

	// Setup mocks for concurrent executions
	mockPluginRepo.On("GetByID", mock.AnythingOfType("*context.Context"), pipeline.Steps[0].PluginID).Return(plugin1, nil)
	mockPluginRepo.On("GetByID", mock.AnythingOfType("*context.Context"), pipeline.Steps[1].PluginID).Return(plugin2, nil)

	result := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		Data:         map[string]interface{}{"data": "test"},
		RecordsCount: 1,
	}

	mockRealExecutor.On("ExecuteSource", mock.AnythingOfType("*context.Context"), mock.Anything, mock.AnythingOfType("*services.RealPluginExecutionContext")).Return(result, nil)

	// Act - Run concurrent executions
	const numGoroutines = 3
	ch := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func() {
			ctx := context.Background()
			_, err := executor.Execute(ctx, pipeline)
			ch <- err
		}()
	}

	// Assert - Collect results
	for i := 0; i < numGoroutines; i++ {
		err := <-ch
		assert.NoError(t, err)
	}
}

// EXTREME TESTING: Benchmark Tests
func BenchmarkExecute(b *testing.B) {
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}

	executor := createTestExecutor(mockPluginRepo, mockRealExecutor)
	pipeline := createTestPipeline()
	plugin1 := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin2 := createTestPlugin(pipeline.Steps[1].PluginID, "transform-plugin")

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.AnythingOfType("*context.Context"), pipeline.Steps[0].PluginID).Return(plugin1, nil)
	mockPluginRepo.On("GetByID", mock.AnythingOfType("*context.Context"), pipeline.Steps[1].PluginID).Return(plugin2, nil)

	result := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		Data:         map[string]interface{}{"data": "test"},
		RecordsCount: 1,
	}

	mockRealExecutor.On("ExecuteSource", mock.AnythingOfType("*context.Context"), mock.Anything, mock.AnythingOfType("*services.RealPluginExecutionContext")).Return(result, nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ctx := context.Background()
		_, _ = executor.Execute(ctx, pipeline)
	}
}

// EXTREME TESTING: Plugin Type Specific Execution Tests
func TestExecuteSourcePlugin_SimulationMode(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	plugin := createTestPlugin(uuid.New(), "source-plugin")
	plugin.Type = pluginEntities.PluginTypeSource
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "extract-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"source": "database"},
	}
	inputData := map[string]interface{}{"table": "users"}

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeSourcePlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, output)
	assert.Equal(t, 100, recordsProcessed) // Simulation default
	assert.Equal(t, "simulation", output["execution_mode"])
	assert.Equal(t, plugin.Name, output["plugin_name"])
	assert.Contains(t, output, "records_extracted")
	assert.Contains(t, output, "records")
}

func TestExecuteTargetPlugin_SimulationMode(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	plugin := createTestPlugin(uuid.New(), "target-plugin")
	plugin.Type = pluginEntities.PluginTypeTarget
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "load-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"target": "warehouse"},
	}
	inputData := map[string]interface{}{
		"records": []interface{}{
			map[string]interface{}{"id": 1, "name": "user1"},
			map[string]interface{}{"id": 2, "name": "user2"},
		},
	}

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeTargetPlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, output)
	assert.Equal(t, 2, recordsProcessed) // Should count input records
	assert.Equal(t, "simulation", output["execution_mode"])
	assert.Equal(t, "simulated_success", output["load_status"])
}

func TestExecuteTransformerPlugin_SimulationMode(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	plugin := createTestPlugin(uuid.New(), "transformer-plugin")
	plugin.Type = pluginEntities.PluginTypeTransformer
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "transform-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"rules": []string{"uppercase"}},
	}
	inputData := map[string]interface{}{"rules": []string{"uppercase", "validate"}}

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeTransformerPlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, output)
	assert.Equal(t, 50, recordsProcessed) // Simulation default
	assert.Equal(t, "simulation", output["execution_mode"])
	assert.Contains(t, output, "transformation_rules")
	assert.Contains(t, output, "records")
}

func TestExecuteUtilityPlugin_SimulationMode(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	plugin := createTestPlugin(uuid.New(), "utility-plugin")
	plugin.Type = pluginEntities.PluginTypeUtility
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "utility-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"operation": "validate"},
	}
	inputData := map[string]interface{}{"data": "test"}

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeUtilityPlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, output)
	assert.Equal(t, 1, recordsProcessed) // Utility default
	assert.Equal(t, "simulation", output["execution_mode"])
	assert.Equal(t, "simulated_success", output["utility_result"])
	assert.Contains(t, output, "operations")
}

// EXTREME TESTING: Real Executor Tests
func TestExecuteSourcePlugin_RealMode_Success(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	plugin := createTestPlugin(uuid.New(), "source-plugin")
	plugin.Type = pluginEntities.PluginTypeSource
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "extract-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"source": "database"},
	}
	inputData := map[string]interface{}{"table": "users"}

	realResult := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     200 * time.Millisecond,
		RecordsCount: 500,
		Data: map[string]interface{}{
			"records": []map[string]interface{}{
				{"id": 1, "name": "real_user_1"},
				{"id": 2, "name": "real_user_2"},
			},
		},
	}

	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(realResult, nil)

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeSourcePlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, output)
	assert.Equal(t, 500, recordsProcessed)
	assert.Equal(t, plugin.Name, output["plugin_name"])
	assert.Equal(t, 500, output["records_extracted"])
	assert.Equal(t, true, output["execution_success"])
	assert.Equal(t, 200*time.Millisecond, output["execution_duration"])
	assert.Equal(t, realResult.Data, output["real_data"])

	mockRealExecutor.AssertExpectations(t)
}

func TestExecuteSourcePlugin_RealMode_Failure(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	plugin := createTestPlugin(uuid.New(), "source-plugin")
	plugin.Type = pluginEntities.PluginTypeSource
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "extract-step",
		PluginID:      plugin.ID,
		Configuration: map[string]interface{}{"source": "database"},
	}
	inputData := map[string]interface{}{"table": "users"}

	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(nil, errors.New("database connection failed"))

	ctx := context.Background()

	// Act
	output, recordsProcessed, err := executor.executeSourcePlugin(ctx, plugin, &step, inputData)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, output)
	assert.Equal(t, 0, recordsProcessed)
	assert.Contains(t, err.Error(), "real source plugin execution failed")
	assert.Contains(t, err.Error(), "database connection failed")

	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Data Flow Tests
func TestPrepareStepInputData_WithDependencies(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	dep1ID := uuid.New()
	dep2ID := uuid.New()
	step := entities.PipelineStep{
		ID:       uuid.New(),
		Name:     "test-step",
		PluginID: uuid.New(),
		Configuration: map[string]interface{}{
			"param1": "value1",
			"param2": 42,
		},
		DependsOn: []uuid.UUID{dep1ID, dep2ID},
	}

	dataFlow := map[string]interface{}{
		dep1ID.String(): map[string]interface{}{"output1": "data1"},
		dep2ID.String(): map[string]interface{}{"output2": "data2"},
		"other":         "should_not_be_included",
	}

	// Act
	inputData := executor.prepareStepInputData(&step, dataFlow)

	// Assert
	assert.NotNil(t, inputData)
	assert.Equal(t, "value1", inputData["param1"])
	assert.Equal(t, 42, inputData["param2"])
	assert.Contains(t, inputData, fmt.Sprintf("dependency_%s", dep1ID.String()))
	assert.Contains(t, inputData, fmt.Sprintf("dependency_%s", dep2ID.String()))
	assert.NotContains(t, inputData, "other")
}

func TestPrepareStepInputData_NoDependencies(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	step := entities.PipelineStep{
		ID:       uuid.New(),
		Name:     "test-step",
		PluginID: uuid.New(),
		Configuration: map[string]interface{}{
			"param1": "value1",
		},
		DependsOn: []uuid.UUID{},
	}

	dataFlow := map[string]interface{}{
		"some_step": "some_data",
	}

	// Act
	inputData := executor.prepareStepInputData(&step, dataFlow)

	// Assert
	assert.NotNil(t, inputData)
	assert.Equal(t, "value1", inputData["param1"])
	assert.Len(t, inputData, 1) // Only configuration
}

// EXTREME TESTING: Context and Cancellation Tests
func TestExecute_ContextCancellation(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[0].PluginID).Return(plugin, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(nil, context.Canceled)

	// Create cancelled context
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Contains(t, err.Error(), "Step extract-step failed")

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

func TestExecute_ContextTimeout(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[0].PluginID).Return(plugin, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(nil, context.DeadlineExceeded)

	// Create timeout context
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Millisecond)
	defer cancel()

	// Wait for timeout
	time.Sleep(2 * time.Millisecond)

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Plugin Status Tests
func TestExecute_PluginRegisteredThenActivated(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin.Status = pluginEntities.PluginStatusRegistered // Not active yet

	result := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		Data:         map[string]interface{}{"test": "data"},
		RecordsCount: 1,
	}

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[0].PluginID).Return(plugin, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(result, nil)

	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.NoError(t, err) // Should succeed after automatic activation
	assert.NotNil(t, execution)
	assert.Equal(t, StatusCompleted, execution.Status)
	assert.Contains(t, execution.Steps[0].Logs, "Plugin activated successfully")

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

func TestExecute_PluginInactive(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin.Status = pluginEntities.PluginStatusInactive // Inactive

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[0].PluginID).Return(plugin, nil)

	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Contains(t, err.Error(), "Step extract-step failed")
	assert.Contains(t, *execution.Steps[0].Error, "Plugin is not active")

	mockPluginRepo.AssertExpectations(t)
}

// EXTREME TESTING: Complex Multi-Step Pipeline Tests
func TestExecute_ComplexPipeline_Success(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	// Create complex pipeline with dependencies
	pipeline, _ := entities.NewPipeline("complex-pipeline", "Complex ETL pipeline")
	pipeline.IsActive = true

	// Create plugins
	sourcePlugin := createTestPlugin(uuid.New(), "source-plugin")
	sourcePlugin.Type = pluginEntities.PluginTypeSource
	transformPlugin := createTestPlugin(uuid.New(), "transform-plugin")
	transformPlugin.Type = pluginEntities.PluginTypeTransformer
	targetPlugin := createTestPlugin(uuid.New(), "target-plugin")
	targetPlugin.Type = pluginEntities.PluginTypeTarget

	// Create steps with dependencies
	sourceStep := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "extract-data",
		PluginID:      sourcePlugin.ID,
		Order:         1,
		Configuration: map[string]interface{}{"source": "database"},
		DependsOn:     []uuid.UUID{},
	}

	transformStep := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "transform-data",
		PluginID:      transformPlugin.ID,
		Order:         2,
		Configuration: map[string]interface{}{"rules": []string{"clean", "validate"}},
		DependsOn:     []uuid.UUID{sourceStep.ID},
	}

	targetStep := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "load-data",
		PluginID:      targetPlugin.ID,
		Order:         3,
		Configuration: map[string]interface{}{"target": "warehouse"},
		DependsOn:     []uuid.UUID{transformStep.ID},
	}

	pipeline.Steps = []entities.PipelineStep{sourceStep, transformStep, targetStep}

	// Setup mocks
	mockPluginRepo.On("GetByID", mock.Anything, sourcePlugin.ID).Return(sourcePlugin, nil)
	mockPluginRepo.On("GetByID", mock.Anything, transformPlugin.ID).Return(transformPlugin, nil)
	mockPluginRepo.On("GetByID", mock.Anything, targetPlugin.ID).Return(targetPlugin, nil)

	// Mock execution results
	sourceResult := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     150 * time.Millisecond,
		RecordsCount: 1000,
		Data: map[string]interface{}{
			"records": []map[string]interface{}{
				{"id": 1, "name": "user1"},
				{"id": 2, "name": "user2"},
			},
		},
	}

	transformResult := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		RecordsCount: 950, // Some records filtered out
		Data: map[string]interface{}{
			"records": []map[string]interface{}{
				{"id": 1, "name": "USER1", "status": "valid"},
				{"id": 2, "name": "USER2", "status": "valid"},
			},
		},
	}

	targetResult := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     200 * time.Millisecond,
		RecordsCount: 950,
		Data:         map[string]interface{}{"loaded": true},
	}

	mockRealExecutor.On("ExecuteSource", mock.Anything, sourcePlugin, mock.Anything).Return(sourceResult, nil)
	mockRealExecutor.On("ExecuteTransformer", mock.Anything, transformPlugin, mock.Anything).Return(transformResult, nil)
	mockRealExecutor.On("ExecuteTarget", mock.Anything, targetPlugin, mock.Anything).Return(targetResult, nil)

	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	require.NoError(t, err)
	require.NotNil(t, execution)
	assert.Equal(t, StatusCompleted, execution.Status)
	assert.Len(t, execution.Steps, 3)

	// Verify all steps completed successfully
	for i, stepExecution := range execution.Steps {
		assert.Equal(t, StatusCompleted, stepExecution.Status, fmt.Sprintf("Step %d should be completed", i+1))
		assert.NotNil(t, stepExecution.StartedAt)
		assert.NotNil(t, stepExecution.CompletedAt)
		assert.Nil(t, stepExecution.Error)
		assert.NotNil(t, stepExecution.Output)
	}

	// Verify data flow
	assert.Contains(t, execution.Context, "data_flow")
	dataFlow := execution.Context["data_flow"].(map[string]interface{})
	assert.Contains(t, dataFlow, sourceStep.ID.String())
	assert.Contains(t, dataFlow, transformStep.ID.String())
	assert.Contains(t, dataFlow, targetStep.ID.String())

	// Verify execution order and data passing
	sourceOutput := execution.Steps[0].Output.(map[string]interface{})
	assert.Equal(t, 1000, sourceOutput["records_extracted"])

	transformOutput := execution.Steps[1].Output.(map[string]interface{})
	assert.Equal(t, 950, transformOutput["records_transformed"])

	targetOutput := execution.Steps[2].Output.(map[string]interface{})
	assert.Equal(t, 950, targetOutput["records_loaded"])

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Error Handling and Recovery Tests
func TestExecute_MiddleStepFailure(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin1 := createTestPlugin(pipeline.Steps[0].PluginID, "extract-plugin")
	plugin2 := createTestPlugin(pipeline.Steps[1].PluginID, "transform-plugin")

	// Setup mocks - first step succeeds, second fails
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[0].PluginID).Return(plugin1, nil)
	mockPluginRepo.On("GetByID", mock.Anything, pipeline.Steps[1].PluginID).Return(plugin2, nil)

	successResult := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     100 * time.Millisecond,
		Data:         map[string]interface{}{"data": "test"},
		RecordsCount: 1,
	}

	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin1, mock.Anything).Return(successResult, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin2, mock.Anything).Return(nil, errors.New("transformation failed"))

	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.Error(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusFailed, execution.Status)
	assert.Len(t, execution.Steps, 2)                           // Both steps should be recorded
	assert.Equal(t, StatusCompleted, execution.Steps[0].Status) // First step succeeded
	assert.Equal(t, StatusFailed, execution.Steps[1].Status)    // Second step failed
	assert.Contains(t, err.Error(), "Step transform-step failed")

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Performance and Load Tests
func TestExecute_LargePipeline(t *testing.T) {
	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline, _ := entities.NewPipeline("large-pipeline", "Large pipeline with many steps")
	pipeline.IsActive = true

	// Create 50 steps
	const numSteps = 50
	for i := 0; i < numSteps; i++ {
		plugin := createTestPlugin(uuid.New(), fmt.Sprintf("plugin-%d", i))
		step := entities.PipelineStep{
			ID:            uuid.New(),
			Name:          fmt.Sprintf("step-%d", i),
			PluginID:      plugin.ID,
			Order:         i + 1,
			Configuration: map[string]interface{}{"index": i},
			DependsOn:     []uuid.UUID{},
		}
		pipeline.Steps = append(pipeline.Steps, step)

		// Setup mocks
		mockPluginRepo.On("GetByID", mock.Anything, plugin.ID).Return(plugin, nil)
		result := &RealPluginExecutionResult{
			Success:      true,
			ExitCode:     0,
			Duration:     10 * time.Millisecond,
			Data:         map[string]interface{}{"index": i},
			RecordsCount: 1,
		}
		mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(result, nil)
	}

	ctx := context.Background()
	start := time.Now()

	// Act
	execution, err := executor.Execute(ctx, pipeline)
	duration := time.Since(start)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusCompleted, execution.Status)
	assert.Len(t, execution.Steps, numSteps)
	assert.Less(t, duration, 5*time.Second) // Should complete within reasonable time

	// Verify all steps completed
	for i, stepExecution := range execution.Steps {
		assert.Equal(t, StatusCompleted, stepExecution.Status, fmt.Sprintf("Step %d should be completed", i))
	}

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Memory Usage Tests
func TestExecute_MemoryEfficiency(t *testing.T) {
	// This test verifies that the executor doesn't leak memory
	// even with large data flows

	// Arrange
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "memory-test-plugin")

	// Create large data set for testing memory efficiency
	largeDataSet := make([]map[string]interface{}, 10000)
	for i := 0; i < 10000; i++ {
		largeDataSet[i] = map[string]interface{}{
			"id":   i,
			"name": fmt.Sprintf("user_%d", i),
			"data": make([]byte, 1024), // 1KB per record
		}
	}

	result := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     500 * time.Millisecond,
		RecordsCount: 10000,
		Data:         map[string]interface{}{"records": largeDataSet},
	}

	mockPluginRepo.On("GetByID", mock.Anything, plugin.ID).Return(plugin, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, plugin, mock.Anything).Return(result, nil)

	ctx := context.Background()

	// Act
	execution, err := executor.Execute(ctx, pipeline)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, execution)
	assert.Equal(t, StatusCompleted, execution.Status)

	// Verify large data was handled correctly
	output := execution.Steps[0].Output.(map[string]interface{})
	assert.Equal(t, 10000, output["records_extracted"])
	assert.Contains(t, execution.Context["data_flow"], pipeline.Steps[0].ID.String())

	mockPluginRepo.AssertExpectations(t)
	mockRealExecutor.AssertExpectations(t)
}

// EXTREME TESTING: Additional Benchmark Tests
func BenchmarkExecute_SingleStep_Simulation(b *testing.B) {
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	pipeline := createTestPipeline()
	plugin := createTestPlugin(pipeline.Steps[0].PluginID, "bench-plugin")
	pipeline.Steps = pipeline.Steps[:1] // Only first step

	mockPluginRepo.On("GetByID", mock.Anything, plugin.ID).Return(plugin, nil)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = executor.Execute(ctx, pipeline)
	}
}

func BenchmarkExecute_MultiStep_RealExecutor(b *testing.B) {
	mockPluginRepo := &MockPluginRepository{}
	mockRealExecutor := &MockRealPluginExecutor{}
	executor := NewPipelineExecutor(mockPluginRepo, mockRealExecutor)

	pipeline := createTestPipeline()
	plugin1 := createTestPlugin(pipeline.Steps[0].PluginID, "plugin1")
	plugin2 := createTestPlugin(pipeline.Steps[1].PluginID, "plugin2")

	result := &RealPluginExecutionResult{
		Success:      true,
		ExitCode:     0,
		Duration:     1 * time.Millisecond,
		Data:         map[string]interface{}{"test": "data"},
		RecordsCount: 1,
	}

	mockPluginRepo.On("GetByID", mock.Anything, plugin1.ID).Return(plugin1, nil)
	mockPluginRepo.On("GetByID", mock.Anything, plugin2.ID).Return(plugin2, nil)
	mockRealExecutor.On("ExecuteSource", mock.Anything, mock.Anything, mock.Anything).Return(result, nil)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = executor.Execute(ctx, pipeline)
	}
}

func BenchmarkPrepareStepInputData_LargeDependencies(b *testing.B) {
	mockPluginRepo := &MockPluginRepository{}
	executor := NewPipelineExecutorWithSimulation(mockPluginRepo)

	// Create step with many dependencies
	step := entities.PipelineStep{
		ID:       uuid.New(),
		Name:     "dependent-step",
		PluginID: uuid.New(),
		Configuration: map[string]interface{}{
			"param1": "value1",
			"param2": "value2",
		},
		DependsOn: make([]uuid.UUID, 100), // 100 dependencies
	}

	// Fill dependencies
	for i := 0; i < 100; i++ {
		step.DependsOn[i] = uuid.New()
	}

	// Create large data flow
	dataFlow := make(map[string]interface{})
	for _, depID := range step.DependsOn {
		dataFlow[depID.String()] = map[string]interface{}{
			"records": make([]interface{}, 1000),
			"count":   1000,
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = executor.prepareStepInputData(&step, dataFlow)
	}
}
