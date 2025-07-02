package plugin_test

import (
	"context"
	"errors"
	"testing"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	pluginUC "github.com/flext-sh/flext/internal/usecases/plugin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// Tests

func TestActivatePluginUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Create a test plugin
	testPlugin, _ := entities.NewPlugin("Test Plugin", "1.0.0", "main.py", entities.PluginTypeSource)

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(testPlugin, nil)
	mockRepo.On("Save", ctx, testPlugin).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("plugin.PluginActivatedEvent")).Return(nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, testPlugin.ID.String(), result.ID)
	assert.Equal(t, "Test Plugin", result.Name)
	assert.Equal(t, "active", result.Status)
	assert.NotEmpty(t, result.ActivatedAt)

	// Verify all expectations were met
	mockRepo.AssertExpectations(t)
	mockValidator.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}

func TestActivatePluginUseCase_Execute_ValidationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.ActivatePluginInput{
		PluginID: uuid.Nil, // Invalid: nil UUID
	}

	validationError := errors.New("plugin ID is required")
	mockValidator.On("ValidateActivatePlugin", input).Return(validationError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, validationError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "FindByID")
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestActivatePluginUseCase_Execute_PluginNotFound(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(nil, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pluginUC.ErrPluginNotFound, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestActivatePluginUseCase_Execute_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	repoError := errors.New("database connection failed")

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(nil, repoError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, repoError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestActivatePluginUseCase_Execute_ActivationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Create a test plugin and activate it first
	testPlugin, _ := entities.NewPlugin("Test Plugin", "1.0.0", "main.py", entities.PluginTypeSource)
	testPlugin.Activate() // Activate it first to make second activation fail

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(testPlugin, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err) // Should fail because plugin is already active
	assert.Nil(t, result)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestActivatePluginUseCase_Execute_SaveError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Create a test plugin
	testPlugin, _ := entities.NewPlugin("Test Plugin", "1.0.0", "main.py", entities.PluginTypeSource)
	saveError := errors.New("database connection failed")

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(testPlugin, nil)
	mockRepo.On("Save", ctx, testPlugin).Return(saveError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, "failed to save plugin", err.Error())

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestActivatePluginUseCase_Execute_EventPublishError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewActivatePluginUseCase(mockRepo, mockValidator, mockEvents)

	pluginID := uuid.New()
	input := pluginUC.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Create a test plugin
	testPlugin, _ := entities.NewPlugin("Test Plugin", "1.0.0", "main.py", entities.PluginTypeSource)
	eventError := errors.New("failed to publish event")

	// Mock expectations
	mockValidator.On("ValidateActivatePlugin", input).Return(nil)
	mockRepo.On("FindByID", ctx, pluginID).Return(testPlugin, nil)
	mockRepo.On("Save", ctx, testPlugin).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("plugin.PluginActivatedEvent")).Return(eventError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	// Event publishing error should not fail the use case
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, testPlugin.ID.String(), result.ID)
	assert.Equal(t, "Test Plugin", result.Name)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}