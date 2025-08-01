package plugin_test

import (
	"context"
	"errors"
	"testing"

	"github.com/flext/flexcore/internal/bounded_contexts/plugin/domain/entities"
	pluginUC "github.com/flext/flexcore/internal/usecases/plugin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// Mocks

type MockPluginRepository struct {
	mock.Mock
}

func (m *MockPluginRepository) Save(ctx context.Context, p *entities.Plugin) error {
	args := m.Called(ctx, p)
	return args.Error(0)
}

func (m *MockPluginRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Plugin), args.Error(1)
}

func (m *MockPluginRepository) FindByName(ctx context.Context, name string) (*entities.Plugin, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Plugin), args.Error(1)
}

func (m *MockPluginRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	args := m.Called(ctx, name)
	return args.Bool(0), args.Error(1)
}

func (m *MockPluginRepository) List(ctx context.Context, criteria pluginUC.ListCriteria) ([]*entities.Plugin, int, error) {
	args := m.Called(ctx, criteria)
	return args.Get(0).([]*entities.Plugin), args.Int(1), args.Error(2)
}

func (m *MockPluginRepository) ListByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error) {
	args := m.Called(ctx, pluginType)
	return args.Get(0).([]*entities.Plugin), args.Error(1)
}

func (m *MockPluginRepository) ListActive(ctx context.Context) ([]*entities.Plugin, error) {
	args := m.Called(ctx)
	return args.Get(0).([]*entities.Plugin), args.Error(1)
}

func (m *MockPluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type MockPluginInputValidator struct {
	mock.Mock
}

func (m *MockPluginInputValidator) ValidateRegisterPlugin(input pluginUC.RegisterPluginInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateActivatePlugin(input pluginUC.ActivatePluginInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateUpdatePlugin(input pluginUC.UpdatePluginInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateGetPlugin(input pluginUC.GetPluginInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateGetPluginByName(input pluginUC.GetPluginByNameInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateListPlugins(input pluginUC.ListPluginsInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateListPluginsByType(input pluginUC.ListPluginsByTypeInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidateDeletePlugin(input pluginUC.DeletePluginInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockPluginInputValidator) ValidatePluginHealthCheck(input pluginUC.PluginHealthCheckInput) error {
	args := m.Called(input)
	return args.Error(0)
}

type MockPluginEventPublisher struct {
	mock.Mock
}

func (m *MockPluginEventPublisher) Publish(ctx context.Context, event interface{}) error {
	args := m.Called(ctx, event)
	return args.Error(0)
}

// Tests

func TestRegisterPluginUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:         "Test Plugin",
		Type:         "source",
		Version:      "1.0.0",
		Capabilities: []string{"read", "write"},
		Configuration: map[string]interface{}{
			"host": "localhost",
			"port": 5432,
		},
	}

	// Mock expectations
	mockValidator.On("ValidateRegisterPlugin", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Plugin").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*entities.Plugin")).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("plugin.PluginRegisteredEvent")).Return(nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Plugin", result.Name)
	assert.Equal(t, "source", result.Type)
	assert.Equal(t, "1.0.0", result.Version)
	assert.Equal(t, "registered", result.Status)
	assert.Equal(t, []string{"read", "write"}, result.Capabilities)
	assert.NotEmpty(t, result.ID)
	assert.NotEmpty(t, result.RegisteredAt)

	// Verify all expectations were met
	mockRepo.AssertExpectations(t)
	mockValidator.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}

func TestRegisterPluginUseCase_Execute_ValidationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:    "", // Invalid: empty name
		Type:    "source",
		Version: "1.0.0",
	}

	validationError := errors.New("name is required")
	mockValidator.On("ValidateRegisterPlugin", input).Return(validationError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, validationError, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "ExistsByName")
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestRegisterPluginUseCase_Execute_PluginAlreadyExists(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:    "Existing Plugin",
		Type:    "source",
		Version: "1.0.0",
	}

	// Mock expectations
	mockValidator.On("ValidateRegisterPlugin", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Existing Plugin").Return(true, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pluginUC.ErrPluginAlreadyExists, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestRegisterPluginUseCase_Execute_InvalidPluginType(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:    "Test Plugin",
		Type:    "invalid_type", // Invalid type
		Version: "1.0.0",
	}

	// Mock expectations
	mockValidator.On("ValidateRegisterPlugin", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Plugin").Return(false, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "invalid plugin type")

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestRegisterPluginUseCase_Execute_SaveError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:    "Test Plugin",
		Type:    "source",
		Version: "1.0.0",
	}

	saveError := errors.New("failed to save to database")

	// Mock expectations
	mockValidator.On("ValidateRegisterPlugin", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Plugin").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*entities.Plugin")).Return(saveError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "failed to save plugin")

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestRegisterPluginUseCase_Execute_EventPublishError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPluginRepository)
	mockValidator := new(MockPluginInputValidator)
	mockEvents := new(MockPluginEventPublisher)

	useCase := pluginUC.NewRegisterPluginUseCase(mockRepo, mockValidator, mockEvents)

	input := pluginUC.RegisterPluginInput{
		Name:    "Test Plugin",
		Type:    "source",
		Version: "1.0.0",
	}

	eventError := errors.New("failed to publish event")

	// Mock expectations
	mockValidator.On("ValidateRegisterPlugin", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Plugin").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*entities.Plugin")).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("plugin.PluginRegisteredEvent")).Return(eventError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	// Event publishing error should not fail the use case
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Plugin", result.Name)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}
