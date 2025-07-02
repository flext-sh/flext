package pipeline_test

import (
	"context"
	"errors"
	"testing"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pipelineUC "github.com/flext-sh/flext/internal/usecases/pipeline"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockPluginRegistry for testing
type MockPluginRegistry struct {
	mock.Mock
}

func (m *MockPluginRegistry) GetPlugin(ctx context.Context, id uuid.UUID) (*pipelineUC.PluginInfo, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*pipelineUC.PluginInfo), args.Error(1)
}

func (m *MockPluginRegistry) ValidatePlugin(ctx context.Context, pluginID uuid.UUID) error {
	args := m.Called(ctx, pluginID)
	return args.Error(0)
}

// Tests

func TestAddStepUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()

	// Create a test pipeline first
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")

	input := pipelineUC.AddStepInput{
		PipelineID: testPipeline.ID,
		Name:       "Test Step",
		PluginID:   pluginID,
		Configuration: map[string]interface{}{
			"key": "value",
		},
		DependsOn: []uuid.UUID{},
	}

	// Mock expectations
	mockValidator.On("ValidateAddStepInput", input).Return(nil)
	mockPluginRepo.On("ValidatePlugin", ctx, pluginID).Return(nil)
	mockRepo.On("FindByID", ctx, testPipeline.ID).Return(testPipeline, nil)
	mockRepo.On("Save", ctx, testPipeline).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineStepAddedEvent")).Return(nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Step", result.StepName)
	assert.Equal(t, testPipeline.ID.String(), result.PipelineID)
	// PluginID field removed from AddStepOutput
	assert.NotEmpty(t, result.StepID)
	// CreatedAt field removed from AddStepOutput

	// Verify all expectations were met
	mockRepo.AssertExpectations(t)
	mockPluginRepo.AssertExpectations(t)
	mockValidator.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}

func TestAddStepUseCase_Execute_ValidationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.AddStepInput{
		PipelineID: uuid.New(),
		Name:       "", // Invalid: empty name
		PluginID:   uuid.New(),
	}

	validationError := errors.New("step name is required")
	mockValidator.On("ValidateAddStep", input).Return(validationError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, validationError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockPluginRepo.AssertNotCalled(t, "ValidatePlugin")
	mockRepo.AssertNotCalled(t, "FindByID")
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestAddStepUseCase_Execute_InvalidPlugin(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pipelineUC.AddStepInput{
		PipelineID: uuid.New(),
		Name:       "Test Step",
		PluginID:   pluginID,
	}

	pluginError := errors.New("plugin not found")

	// Mock expectations
	mockValidator.On("ValidateAddStepInput", input).Return(nil)
	mockPluginRepo.On("ValidatePlugin", ctx, pluginID).Return(pluginError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, "invalid plugin", err.Error())

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockPluginRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "FindByID")
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestAddStepUseCase_Execute_PipelineNotFound(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	pluginID := uuid.New()

	input := pipelineUC.AddStepInput{
		PipelineID: pipelineID,
		Name:       "Test Step",
		PluginID:   pluginID,
	}

	// Mock expectations
	mockValidator.On("ValidateAddStepInput", input).Return(nil)
	mockPluginRepo.On("ValidatePlugin", ctx, pluginID).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(nil, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pipelineUC.ErrPipelineNotFound, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockPluginRepo.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestAddStepUseCase_Execute_SaveError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	pluginID := uuid.New()

	input := pipelineUC.AddStepInput{
		PipelineID: pipelineID,
		Name:       "Test Step",
		PluginID:   pluginID,
	}

	// Create a test pipeline
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")
	saveError := errors.New("database connection failed")

	// Mock expectations
	mockValidator.On("ValidateAddStepInput", input).Return(nil)
	mockPluginRepo.On("ValidatePlugin", ctx, pluginID).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(testPipeline, nil)
	mockRepo.On("Save", ctx, testPipeline).Return(saveError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, "failed to save pipeline", err.Error())

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockPluginRepo.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestAddStepUseCase_Execute_EventPublishError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockPluginRepo := new(MockPluginRegistry)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewAddStepUseCase(mockRepo, mockValidator, mockEvents)

	pipelineID := uuid.New()
	pluginID := uuid.New()

	input := pipelineUC.AddStepInput{
		PipelineID: pipelineID,
		Name:       "Test Step",
		PluginID:   pluginID,
	}

	// Create a test pipeline
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Description")
	eventError := errors.New("failed to publish event")

	// Mock expectations
	mockValidator.On("ValidateAddStepInput", input).Return(nil)
	mockPluginRepo.On("ValidatePlugin", ctx, pluginID).Return(nil)
	mockRepo.On("FindByID", ctx, pipelineID).Return(testPipeline, nil)
	mockRepo.On("Save", ctx, testPipeline).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineStepAddedEvent")).Return(eventError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	// Event publishing error should not fail the use case
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Step", result.StepName)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockPluginRepo.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}