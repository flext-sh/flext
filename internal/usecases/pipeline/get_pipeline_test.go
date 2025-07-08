package pipeline_test

import (
	"context"
	"errors"
	"testing"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pipelineUC "github.com/flext-sh/flext/internal/usecases/pipeline"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// Tests

func TestGetPipelineUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewGetPipelineUseCase(mockRepo, new(MockInputValidator))

	pipelineID := uuid.New()
	input := pipelineUC.GetPipelineInput{
		ID: pipelineID,
	}

	// Create a test pipeline with steps
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Test Description")
	step, _ := entities.NewPipelineStep("Test Step", uuid.New())
	testPipeline.AddStep(*step)

	// Mock expectations
	mockRepo.On("FindByID", ctx, pipelineID).Return(testPipeline, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, testPipeline.ID.String(), result.ID)
	assert.Equal(t, "Test Pipeline", result.Name)
	assert.Equal(t, "Test Description", result.Description)
	assert.True(t, result.IsActive)
	assert.Len(t, result.Steps, 1)
	assert.Equal(t, "Test Step", result.Steps[0].Name)
	assert.NotEmpty(t, result.CreatedAt)
	assert.NotEmpty(t, result.UpdatedAt)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestGetPipelineUseCase_Execute_InvalidInput(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewGetPipelineUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.GetPipelineInput{
		ID: uuid.Nil, // Invalid: nil UUID
	}

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pipelineUC.ErrInvalidInput, err)

	// Verify expectations
	mockRepo.AssertNotCalled(t, "FindByID")
}

func TestGetPipelineUseCase_Execute_PipelineNotFound(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewGetPipelineUseCase(mockRepo, new(MockInputValidator))

	pipelineID := uuid.New()
	input := pipelineUC.GetPipelineInput{
		ID: pipelineID,
	}

	// Mock expectations
	mockRepo.On("FindByID", ctx, pipelineID).Return(nil, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, pipelineUC.ErrPipelineNotFound, err)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestGetPipelineUseCase_Execute_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewGetPipelineUseCase(mockRepo, new(MockInputValidator))

	pipelineID := uuid.New()
	input := pipelineUC.GetPipelineInput{
		ID: pipelineID,
	}

	repoError := errors.New("database connection failed")

	// Mock expectations
	mockRepo.On("FindByID", ctx, pipelineID).Return(nil, repoError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, repoError, err)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestGetPipelineUseCase_Execute_WithMultipleSteps(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewGetPipelineUseCase(mockRepo, new(MockInputValidator))

	pipelineID := uuid.New()
	input := pipelineUC.GetPipelineInput{
		ID: pipelineID,
	}

	// Create a test pipeline with multiple steps
	testPipeline, _ := entities.NewPipeline("Test Pipeline", "Test Description")

	// Add multiple steps
	step1, _ := entities.NewPipelineStep("Step 1", uuid.New())
	step2, _ := entities.NewPipelineStep("Step 2", uuid.New())
	step3, _ := entities.NewPipelineStep("Step 3", uuid.New())

	// Add dependency (step3 depends on step1)
	step3.DependsOn = []uuid.UUID{step1.ID}

	testPipeline.AddStep(*step1)
	testPipeline.AddStep(*step2)
	testPipeline.AddStep(*step3)

	// Mock expectations
	mockRepo.On("FindByID", ctx, pipelineID).Return(testPipeline, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Steps, 3)

	// Check that step dependencies are properly mapped
	var step3Output *pipelineUC.StepOutput
	for i := range result.Steps {
		if result.Steps[i].Name == "Step 3" {
			step3Output = &result.Steps[i]
			break
		}
	}
	assert.NotNil(t, step3Output)
	assert.Len(t, step3Output.DependsOn, 1)
	assert.Equal(t, step1.ID.String(), step3Output.DependsOn[0])

	// Verify expectations
	mockRepo.AssertExpectations(t)
}
