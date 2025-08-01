package pipeline_test

import (
	"context"
	"errors"
	"testing"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/entities"
	pipelineUC "github.com/flext/flexcore/internal/usecases/pipeline"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// Mocks

type MockPipelineRepository struct {
	mock.Mock
}

func (m *MockPipelineRepository) Save(ctx context.Context, p *entities.Pipeline) error {
	args := m.Called(ctx, p)
	return args.Error(0)
}

func (m *MockPipelineRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) FindByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	args := m.Called(ctx, name)
	return args.Bool(0), args.Error(1)
}

func (m *MockPipelineRepository) List(ctx context.Context, criteria pipelineUC.ListCriteria) ([]*entities.Pipeline, int, error) {
	args := m.Called(ctx, criteria)
	return args.Get(0).([]*entities.Pipeline), args.Int(1), args.Error(2)
}

func (m *MockPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockPipelineRepository) Create(ctx context.Context, p *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, p)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) GetByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Update(ctx context.Context, p *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, p)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Count(ctx context.Context) (int, error) {
	args := m.Called(ctx)
	return args.Int(0), args.Error(1)
}

type MockInputValidator struct {
	mock.Mock
}

func (m *MockInputValidator) ValidateCreatePipeline(input pipelineUC.CreatePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateAddStep(input pipelineUC.AddStepInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateExecutePipeline(input pipelineUC.ExecutePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateCreatePipelineInput(input pipelineUC.CreatePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateUpdatePipelineInput(input pipelineUC.UpdatePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateDeletePipelineInput(input pipelineUC.DeletePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateGetPipelineInput(input pipelineUC.GetPipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateGetPipeline(input pipelineUC.GetPipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateListPipelinesInput(input pipelineUC.ListPipelinesInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateListPipelines(input pipelineUC.ListPipelinesInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateGetPipelineByNameInput(input pipelineUC.GetPipelineByNameInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateGetPipelineByName(input pipelineUC.GetPipelineByNameInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateAddStepInput(input pipelineUC.AddStepInput) error {
	args := m.Called(input)
	return args.Error(0)
}

// Removed duplicate ValidateAddStep method

func (m *MockInputValidator) ValidateExecutePipelineInput(input pipelineUC.ExecutePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

func (m *MockInputValidator) ValidateDeletePipeline(input pipelineUC.DeletePipelineInput) error {
	args := m.Called(input)
	return args.Error(0)
}

type MockEventPublisher struct {
	mock.Mock
}

func (m *MockEventPublisher) Publish(ctx context.Context, event interface{}) error {
	args := m.Called(ctx, event)
	return args.Error(0)
}

// Tests

func TestCreatePipelineUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "Test Pipeline",
		Description: "Test Description",
		Tags:        []string{"tag1", "tag2"},
	}

	// Mock expectations
	mockValidator.On("ValidateCreatePipeline", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Pipeline").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*pipeline.Pipeline")).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineCreatedEvent")).Return(nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Pipeline", result.Name)
	assert.Equal(t, "Test Description", result.Description)
	assert.Equal(t, []string{"tag1", "tag2"}, result.Tags)
	assert.True(t, result.IsActive)
	assert.NotEmpty(t, result.ID)
	assert.NotEmpty(t, result.CreatedAt)

	// Verify all expectations were met
	mockRepo.AssertExpectations(t)
	mockValidator.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}

func TestCreatePipelineUseCase_Execute_ValidationError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "", // Invalid: empty name
		Description: "Test Description",
		Tags:        []string{"tag1"},
	}

	validationError := errors.New("name is required")
	mockValidator.On("ValidateCreatePipeline", input).Return(validationError)

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

func TestCreatePipelineUseCase_Execute_NameAlreadyExists(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "Existing Pipeline",
		Description: "Test Description",
		Tags:        []string{"tag1"},
	}

	// Mock expectations
	mockValidator.On("ValidateCreatePipeline", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Existing Pipeline").Return(true, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pipelineUC.ErrPipelineNameAlreadyExists, err)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestCreatePipelineUseCase_Execute_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "Test Pipeline",
		Description: "Test Description",
		Tags:        []string{"tag1"},
	}

	repoError := errors.New("database connection failed")

	// Mock expectations
	mockValidator.On("ValidateCreatePipeline", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Pipeline").Return(false, repoError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "failed to check pipeline existence")

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockRepo.AssertNotCalled(t, "Save")
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestCreatePipelineUseCase_Execute_SaveError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "Test Pipeline",
		Description: "Test Description",
		Tags:        []string{"tag1"},
	}

	saveError := errors.New("failed to save to database")

	// Mock expectations
	mockValidator.On("ValidateCreatePipeline", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Pipeline").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*pipeline.Pipeline")).Return(saveError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Contains(t, err.Error(), "failed to save pipeline")

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertNotCalled(t, "Publish")
}

func TestCreatePipelineUseCase_Execute_EventPublishError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)
	mockValidator := new(MockInputValidator)
	mockEvents := new(MockEventPublisher)

	useCase := pipelineUC.NewCreatePipelineUseCase(mockRepo, mockValidator, mockEvents)

	input := pipelineUC.CreatePipelineInput{
		Name:        "Test Pipeline",
		Description: "Test Description",
		Tags:        []string{"tag1"},
	}

	eventError := errors.New("failed to publish event")

	// Mock expectations
	mockValidator.On("ValidateCreatePipeline", input).Return(nil)
	mockRepo.On("ExistsByName", ctx, "Test Pipeline").Return(false, nil)
	mockRepo.On("Save", ctx, mock.AnythingOfType("*pipeline.Pipeline")).Return(nil)
	mockEvents.On("Publish", ctx, mock.AnythingOfType("pipeline.PipelineCreatedEvent")).Return(eventError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	// Event publishing error should not fail the use case
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Test Pipeline", result.Name)

	// Verify expectations
	mockValidator.AssertExpectations(t)
	mockRepo.AssertExpectations(t)
	mockEvents.AssertExpectations(t)
}
