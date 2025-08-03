package pipeline_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	pipelineUC "github.com/flext-sh/flext/pkg/application/pipeline"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockPipelineExecutor for testing
type MockPipelineExecutor struct {
	mock.Mock
}

// MockPipelineExecutor removed as it's not used in the current implementation

// Tests

func TestExecutePipelineUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	// Create a test pipeline with steps so it can be executed
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")
	step, _ := entities.NewPipelineStep("Test Step", uuid.New())
	testPipeline.AddStep(*step)

	input := pipelineUC.ExecutePipelineInput{
		PipelineID: testPipeline.ID,
		Context: map[string]interface{}{
			"param1": "value1",
			"param2": 42,
		},
	}

	// Mock expectations
	mockValidator.On("ValidateExecutePipeline", input).Return(nil)
	mockRepo.On("FindByID", ctx, testPipeline.ID).Return(testPipeline, nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineExecutionStartedEvent")).Return(nil)
	// Mock events that will be published in the async goroutine - make them optional
	mockEvents.On("Publish", mock.Anything, mock.AnythingOfType("pipeline.PipelineExecutionCompletedEvent")).Return(nil).Maybe()
	mockEvents.On("Publish", mock.Anything, mock.AnythingOfType("pipeline.StepExecutionCompletedEvent")).Return(nil).Maybe()

	// Mock the async executor call (it will be called in a goroutine)
	// Removed mockExecutor.On calls since executor is not used

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, testPipeline.ID.String(), result.PipelineID.String())
	assert.Equal(t, "started", result.Status)
	assert.NotEmpty(t, result.ExecutionID)
	assert.NotEmpty(t, result.StartedAt)

	// Give async goroutine time to complete
	time.Sleep(100 * time.Millisecond)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}

func TestExecutePipelineUseCase_Execute_ValidationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.ExecutePipelineInput{
		PipelineID: uuid.Nil, // Invalid: nil UUID
	}

	validationError := errors.New("pipeline ID is required")
	mockValidator.On("ValidateExecutePipeline", input).Return(validationError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, validationError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "FindByID")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestExecutePipelineUseCase_Execute_PipelineNotFound(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	input := pipelineUC.ExecutePipelineInput{
		PipelineID: pipelineID,
	}

	// Mock expectations
	mockValidator.On("ValidateExecutePipeline", input).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(nil, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pipelineUC.ErrPipelineNotFound, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestExecutePipelineUseCase_Execute_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	input := pipelineUC.ExecutePipelineInput{
		PipelineID: pipelineID,
	}

	repoError := errors.New("database connection failed")

	// Mock expectations
	mockValidator.On("ValidateExecutePipeline", input).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(nil, repoError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, repoError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestExecutePipelineUseCase_Execute_PipelineCannotExecute(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	input := pipelineUC.ExecutePipelineInput{
		PipelineID: pipelineID,
	}

	// Create a test pipeline and deactivate it
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")
	testPipeline.Deactivate() // This should make CanExecute() return an error

	// Mock expectations
	mockValidator.On("ValidateExecutePipeline", input).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(testPipeline, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestExecutePipelineUseCase_Execute_EventPublishError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	// mockExecutor removed as it's not used in current implementation
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewExecutePipelineUseCase(mockRepo, mockValidator, mockEvents)

	// Create a test pipeline with steps so it can be executed
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")
	step, _ := entities.NewPipelineStep("Test Step", uuid.New())
	testPipeline.AddStep(*step)

	input := pipelineUC.ExecutePipelineInput{
		PipelineID: testPipeline.ID,
	}
	eventError := errors.New("failed to publish event")

	// Mock expectations
	mockValidator.On("ValidateExecutePipeline", input).Return(nil)
	mockRepo.On("FindByID", ctx, testPipeline.ID).Return(testPipeline, nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineExecutionStartedEvent")).Return(eventError)
	// Mock async events
	mockEvents.On("Publish", mock.Anything, mock.AnythingOfType("pipeline.PipelineExecutionCompletedEvent")).Return(nil).Maybe()
	mockEvents.On("Publish", mock.Anything, mock.AnythingOfType("pipeline.StepExecutionCompletedEvent")).Return(nil).Maybe()
	// Removed mockExecutor.On calls since executor is not used

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	// Event publishing error should not fail the use case
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, testPipeline.ID.String(), result.PipelineID.String())
	assert.Equal(t, "started", result.Status)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}
