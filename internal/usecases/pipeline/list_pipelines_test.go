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

func TestListPipelinesUseCase_Execute_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.ListPipelinesInput{
		Limit:    10,
		Offset:   0,
		OrderBy:  "name",
		OrderDir: "asc",
	}

	// Create test pipelines
	pipeline1, _ := entities.NewPipeline("Pipeline 1", "Description 1")
	pipeline2, _ := entities.NewPipeline("Pipeline 2", "Description 2")
	
	// Add steps to pipeline1
	step1, _ := entities.NewPipelineStep("Step 1", uuid.New())
	pipeline1.AddStep(*step1)

	testPipelines := []*entities.Pipeline{pipeline1, pipeline2}
	totalCount := 2

	// Expected criteria
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:    10,
		Offset:   0,
		OrderBy:  "name",
		OrderDir: "asc",
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return(testPipelines, totalCount, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Pipelines, 2)
	assert.Equal(t, 2, result.Total)
	assert.Equal(t, 10, result.Limit)
	assert.Equal(t, 0, result.Offset)

	// Check first pipeline
	assert.Equal(t, pipeline1.ID.String(), result.Pipelines[0].ID)
	assert.Equal(t, "Pipeline 1", result.Pipelines[0].Name)
	assert.Equal(t, "Description 1", result.Pipelines[0].Description)
	assert.True(t, result.Pipelines[0].IsActive)
	assert.Equal(t, 1, result.Pipelines[0].StepCount)

	// Check second pipeline
	assert.Equal(t, pipeline2.ID.String(), result.Pipelines[1].ID)
	assert.Equal(t, "Pipeline 2", result.Pipelines[1].Name)
	assert.Equal(t, "Description 2", result.Pipelines[1].Description)
	assert.True(t, result.Pipelines[1].IsActive)
	assert.Equal(t, 0, result.Pipelines[1].StepCount)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestListPipelinesUseCase_Execute_WithDefaults(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.ListPipelinesInput{
		// No limit/offset specified, should use defaults
	}

	testPipelines := []*entities.Pipeline{}
	totalCount := 0

	// Expected criteria with defaults
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:  20, // Default limit
		Offset: 0,  // Default offset
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return(testPipelines, totalCount, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Pipelines, 0)
	assert.Equal(t, 0, result.Total)
	assert.Equal(t, 20, result.Limit) // Should use default
	assert.Equal(t, 0, result.Offset)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestListPipelinesUseCase_Execute_LimitValidation(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.ListPipelinesInput{
		Limit:  200, // Exceeds maximum
		Offset: -5,  // Negative offset
	}

	testPipelines := []*entities.Pipeline{}
	totalCount := 0

	// Expected criteria with corrected values
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:  100, // Should be capped at 100
		Offset: 0,   // Should be corrected to 0
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return(testPipelines, totalCount, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, 100, result.Limit) // Should be capped
	assert.Equal(t, 0, result.Offset)  // Should be corrected

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestListPipelinesUseCase_Execute_WithFilters(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	activeFilter := true
	input := pipelineUC.ListPipelinesInput{
		Limit:    10,
		Offset:   0,
		Active:   &activeFilter,
		Tags:     []string{"tag1", "tag2"},
		OrderBy:  "created_at",
		OrderDir: "desc",
	}

	testPipelines := []*entities.Pipeline{}
	totalCount := 0

	// Expected criteria with filters
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:    10,
		Offset:   0,
		Active:   &activeFilter,
		Tags:     []string{"tag1", "tag2"},
		OrderBy:  "created_at",
		OrderDir: "desc",
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return(testPipelines, totalCount, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestListPipelinesUseCase_Execute_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.ListPipelinesInput{
		Limit:  10,
		Offset: 0,
	}

	repoError := errors.New("database connection failed")

	// Expected criteria
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:  10,
		Offset: 0,
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return([]*entities.Pipeline{}, 0, repoError)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)
	assert.Equal(t, repoError, err)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}

func TestListPipelinesUseCase_Execute_WithPagination(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := new(MockPipelineRepository)

	useCase := pipelineUC.NewListPipelinesUseCase(mockRepo, new(MockInputValidator))

	input := pipelineUC.ListPipelinesInput{
		Limit:  5,
		Offset: 10,
	}

	// Create test pipelines
	pipelines := make([]*entities.Pipeline, 5)
	for i := 0; i < 5; i++ {
		pipeline, _ := entities.NewPipeline("Pipeline", "Description")
		pipelines[i] = pipeline
	}
	totalCount := 25

	// Expected criteria
	expectedCriteria := pipelineUC.ListCriteria{
		Limit:  5,
		Offset: 10,
	}

	// Mock expectations
	mockRepo.On("List", ctx, expectedCriteria).Return(pipelines, totalCount, nil)

	// Act
	result, err := useCase.Execute(ctx, input)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.Pipelines, 5)
	assert.Equal(t, 25, result.Total)
	assert.Equal(t, 5, result.Limit)
	assert.Equal(t, 10, result.Offset)

	// Verify expectations
	mockRepo.AssertExpectations(t)
}