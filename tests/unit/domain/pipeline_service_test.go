package domain

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/services"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

// MockPipelineRepository is a mock implementation of PipelineRepository
type MockPipelineRepository struct {
	mock.Mock
}

func (m *MockPipelineRepository) Create(ctx context.Context, pipeline *domain.Pipeline) error {
	args := m.Called(ctx, pipeline)
	return args.Error(0)
}

func (m *MockPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*domain.Pipeline, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) GetByName(ctx context.Context, name string) (*domain.Pipeline, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) List(ctx context.Context, limit, offset int) ([]*domain.Pipeline, int, error) {
	args := m.Called(ctx, limit, offset)
	return args.Get(0).([]*domain.Pipeline), args.Int(1), args.Error(2)
}

func (m *MockPipelineRepository) Update(ctx context.Context, pipeline *domain.Pipeline) error {
	args := m.Called(ctx, pipeline)
	return args.Error(0)
}

func (m *MockPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	args := m.Called(ctx, name)
	return args.Bool(0), args.Error(1)
}

// MockExecutionService is a mock implementation of ExecutionService
type MockExecutionService struct {
	mock.Mock
}

func (m *MockExecutionService) ExecutePipeline(ctx context.Context, pipeline *domain.Pipeline) (*domain.PipelineExecution, error) {
	args := m.Called(ctx, pipeline)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.PipelineExecution), args.Error(1)
}

// PipelineServiceTestSuite defines the test suite for pipeline service
type PipelineServiceTestSuite struct {
	suite.Suite
	service              *services.PipelineService
	mockRepo             *MockPipelineRepository
	mockExecutionService *MockExecutionService
	ctx                  context.Context
}

// SetupTest sets up each test with fresh mocks
func (suite *PipelineServiceTestSuite) SetupTest() {
	suite.mockRepo = new(MockPipelineRepository)
	suite.mockExecutionService = new(MockExecutionService)
	suite.service = services.NewPipelineService(suite.mockRepo, suite.mockExecutionService)
	suite.ctx = context.Background()
}

// TearDownTest cleans up after each test
func (suite *PipelineServiceTestSuite) TearDownTest() {
	suite.mockRepo.AssertExpectations(suite.T())
	suite.mockExecutionService.AssertExpectations(suite.T())
}

// TestCreatePipeline tests pipeline creation with various scenarios
func (suite *PipelineServiceTestSuite) TestCreatePipeline() {
	// Test successful creation
	suite.Run("Successful Creation", func() {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline",
			Description: "Test pipeline",
			Tags:        []string{"test"},
		}

		suite.mockRepo.On("ExistsByName", suite.ctx, "test-pipeline").Return(false, nil)
		suite.mockRepo.On("Create", suite.ctx, mock.AnythingOfType("*domain.Pipeline")).Return(nil)

		result, err := suite.service.CreatePipeline(suite.ctx, pipeline)

		require.NoError(suite.T(), err)
		assert.NotNil(suite.T(), result)
		assert.NotEqual(suite.T(), uuid.Nil, result.ID)
		assert.Equal(suite.T(), "test-pipeline", result.Name)
		assert.Equal(suite.T(), "Test pipeline", result.Description)
		assert.Equal(suite.T(), domain.PipelineStatusActive, result.Status)
		assert.WithinDuration(suite.T(), time.Now(), result.CreatedAt, time.Second)
		assert.WithinDuration(suite.T(), time.Now(), result.UpdatedAt, time.Second)
	})

	// Test duplicate name
	suite.Run("Duplicate Name", func() {
		pipeline := &domain.Pipeline{
			Name:        "duplicate-pipeline",
			Description: "Duplicate pipeline",
		}

		suite.mockRepo.On("ExistsByName", suite.ctx, "duplicate-pipeline").Return(true, nil)

		result, err := suite.service.CreatePipeline(suite.ctx, pipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "already exists")
	})

	// Test invalid pipeline (empty name)
	suite.Run("Invalid Pipeline - Empty Name", func() {
		pipeline := &domain.Pipeline{
			Name:        "",
			Description: "Pipeline without name",
		}

		result, err := suite.service.CreatePipeline(suite.ctx, pipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "name is required")
	})

	// Test repository error during existence check
	suite.Run("Repository Error - Existence Check", func() {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline",
			Description: "Test pipeline",
		}

		suite.mockRepo.On("ExistsByName", suite.ctx, "test-pipeline").Return(false, errors.New("database error"))

		result, err := suite.service.CreatePipeline(suite.ctx, pipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "database error")
	})

	// Test repository error during creation
	suite.Run("Repository Error - Creation", func() {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline",
			Description: "Test pipeline",
		}

		suite.mockRepo.On("ExistsByName", suite.ctx, "test-pipeline").Return(false, nil)
		suite.mockRepo.On("Create", suite.ctx, mock.AnythingOfType("*domain.Pipeline")).Return(errors.New("creation failed"))

		result, err := suite.service.CreatePipeline(suite.ctx, pipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "creation failed")
	})
}

// TestGetPipeline tests pipeline retrieval
func (suite *PipelineServiceTestSuite) TestGetPipeline() {
	pipelineID := uuid.New()

	// Test successful retrieval
	suite.Run("Successful Retrieval", func() {
		expectedPipeline := &domain.Pipeline{
			ID:          pipelineID,
			Name:        "test-pipeline",
			Description: "Test pipeline",
			Status:      domain.PipelineStatusActive,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(expectedPipeline, nil)

		result, err := suite.service.GetPipeline(suite.ctx, pipelineID)

		require.NoError(suite.T(), err)
		assert.Equal(suite.T(), expectedPipeline, result)
	})

	// Test pipeline not found
	suite.Run("Pipeline Not Found", func() {
		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(nil, domain.ErrPipelineNotFound)

		result, err := suite.service.GetPipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Equal(suite.T(), domain.ErrPipelineNotFound, err)
	})

	// Test repository error
	suite.Run("Repository Error", func() {
		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(nil, errors.New("database error"))

		result, err := suite.service.GetPipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "database error")
	})
}

// TestListPipelines tests pipeline listing
func (suite *PipelineServiceTestSuite) TestListPipelines() {
	// Test successful listing
	suite.Run("Successful Listing", func() {
		expectedPipelines := []*domain.Pipeline{
			{
				ID:          uuid.New(),
				Name:        "pipeline-1",
				Description: "First pipeline",
				Status:      domain.PipelineStatusActive,
			},
			{
				ID:          uuid.New(),
				Name:        "pipeline-2",
				Description: "Second pipeline",
				Status:      domain.PipelineStatusActive,
			},
		}

		suite.mockRepo.On("List", suite.ctx, 10, 0).Return(expectedPipelines, 2, nil)

		result, total, err := suite.service.ListPipelines(suite.ctx, 10, 0)

		require.NoError(suite.T(), err)
		assert.Equal(suite.T(), expectedPipelines, result)
		assert.Equal(suite.T(), 2, total)
	})

	// Test empty list
	suite.Run("Empty List", func() {
		suite.mockRepo.On("List", suite.ctx, 10, 0).Return([]*domain.Pipeline{}, 0, nil)

		result, total, err := suite.service.ListPipelines(suite.ctx, 10, 0)

		require.NoError(suite.T(), err)
		assert.Empty(suite.T(), result)
		assert.Equal(suite.T(), 0, total)
	})

	// Test repository error
	suite.Run("Repository Error", func() {
		suite.mockRepo.On("List", suite.ctx, 10, 0).Return([]*domain.Pipeline{}, 0, errors.New("database error"))

		result, total, err := suite.service.ListPipelines(suite.ctx, 10, 0)

		assert.Error(suite.T(), err)
		assert.Empty(suite.T(), result)
		assert.Equal(suite.T(), 0, total)
		assert.Contains(suite.T(), err.Error(), "database error")
	})
}

// TestUpdatePipeline tests pipeline updates
func (suite *PipelineServiceTestSuite) TestUpdatePipeline() {
	pipelineID := uuid.New()

	// Test successful update
	suite.Run("Successful Update", func() {
		existingPipeline := &domain.Pipeline{
			ID:          pipelineID,
			Name:        "original-pipeline",
			Description: "Original description",
			Status:      domain.PipelineStatusActive,
			CreatedAt:   time.Now().Add(-time.Hour),
			UpdatedAt:   time.Now().Add(-time.Hour),
		}

		updatedPipeline := &domain.Pipeline{
			ID:          pipelineID,
			Name:        "updated-pipeline",
			Description: "Updated description",
			Tags:        []string{"updated"},
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(existingPipeline, nil)
		suite.mockRepo.On("ExistsByName", suite.ctx, "updated-pipeline").Return(false, nil)
		suite.mockRepo.On("Update", suite.ctx, mock.AnythingOfType("*domain.Pipeline")).Return(nil)

		result, err := suite.service.UpdatePipeline(suite.ctx, pipelineID, updatedPipeline)

		require.NoError(suite.T(), err)
		assert.NotNil(suite.T(), result)
		assert.Equal(suite.T(), "updated-pipeline", result.Name)
		assert.Equal(suite.T(), "Updated description", result.Description)
		assert.Equal(suite.T(), []string{"updated"}, result.Tags)
		assert.Equal(suite.T(), existingPipeline.CreatedAt, result.CreatedAt)      // CreatedAt should not change
		assert.True(suite.T(), result.UpdatedAt.After(existingPipeline.UpdatedAt)) // UpdatedAt should be updated
	})

	// Test pipeline not found
	suite.Run("Pipeline Not Found", func() {
		updatedPipeline := &domain.Pipeline{
			Name:        "updated-pipeline",
			Description: "Updated description",
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(nil, domain.ErrPipelineNotFound)

		result, err := suite.service.UpdatePipeline(suite.ctx, pipelineID, updatedPipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Equal(suite.T(), domain.ErrPipelineNotFound, err)
	})

	// Test duplicate name (different pipeline)
	suite.Run("Duplicate Name - Different Pipeline", func() {
		existingPipeline := &domain.Pipeline{
			ID:          pipelineID,
			Name:        "original-pipeline",
			Description: "Original description",
		}

		updatedPipeline := &domain.Pipeline{
			Name:        "existing-pipeline",
			Description: "Updated description",
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(existingPipeline, nil)
		suite.mockRepo.On("ExistsByName", suite.ctx, "existing-pipeline").Return(true, nil)

		result, err := suite.service.UpdatePipeline(suite.ctx, pipelineID, updatedPipeline)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "already exists")
	})
}

// TestDeletePipeline tests pipeline deletion
func (suite *PipelineServiceTestSuite) TestDeletePipeline() {
	pipelineID := uuid.New()

	// Test successful deletion
	suite.Run("Successful Deletion", func() {
		existingPipeline := &domain.Pipeline{
			ID:     pipelineID,
			Name:   "test-pipeline",
			Status: domain.PipelineStatusActive,
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(existingPipeline, nil)
		suite.mockRepo.On("Delete", suite.ctx, pipelineID).Return(nil)

		err := suite.service.DeletePipeline(suite.ctx, pipelineID)

		assert.NoError(suite.T(), err)
	})

	// Test pipeline not found
	suite.Run("Pipeline Not Found", func() {
		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(nil, domain.ErrPipelineNotFound)

		err := suite.service.DeletePipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Equal(suite.T(), domain.ErrPipelineNotFound, err)
	})

	// Test cannot delete running pipeline
	suite.Run("Cannot Delete Running Pipeline", func() {
		runningPipeline := &domain.Pipeline{
			ID:     pipelineID,
			Name:   "running-pipeline",
			Status: domain.PipelineStatusRunning,
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(runningPipeline, nil)

		err := suite.service.DeletePipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "cannot delete running pipeline")
	})

	// Test repository error during deletion
	suite.Run("Repository Error - Deletion", func() {
		existingPipeline := &domain.Pipeline{
			ID:     pipelineID,
			Name:   "test-pipeline",
			Status: domain.PipelineStatusActive,
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(existingPipeline, nil)
		suite.mockRepo.On("Delete", suite.ctx, pipelineID).Return(errors.New("deletion failed"))

		err := suite.service.DeletePipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "deletion failed")
	})
}

// TestExecutePipeline tests pipeline execution
func (suite *PipelineServiceTestSuite) TestExecutePipeline() {
	pipelineID := uuid.New()
	executionID := uuid.New()

	// Test successful execution
	suite.Run("Successful Execution", func() {
		pipeline := &domain.Pipeline{
			ID:     pipelineID,
			Name:   "test-pipeline",
			Status: domain.PipelineStatusActive,
		}

		expectedExecution := &domain.PipelineExecution{
			ID:         executionID,
			PipelineID: pipelineID,
			Status:     domain.ExecutionStatusCompleted,
			StartedAt:  time.Now(),
			FinishedAt: time.Now(),
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(pipeline, nil)
		suite.mockExecutionService.On("ExecutePipeline", suite.ctx, pipeline).Return(expectedExecution, nil)

		result, err := suite.service.ExecutePipeline(suite.ctx, pipelineID)

		require.NoError(suite.T(), err)
		assert.Equal(suite.T(), expectedExecution, result)
	})

	// Test pipeline not found
	suite.Run("Pipeline Not Found", func() {
		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(nil, domain.ErrPipelineNotFound)

		result, err := suite.service.ExecutePipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Equal(suite.T(), domain.ErrPipelineNotFound, err)
	})

	// Test execution service error
	suite.Run("Execution Service Error", func() {
		pipeline := &domain.Pipeline{
			ID:     pipelineID,
			Name:   "test-pipeline",
			Status: domain.PipelineStatusActive,
		}

		suite.mockRepo.On("GetByID", suite.ctx, pipelineID).Return(pipeline, nil)
		suite.mockExecutionService.On("ExecutePipeline", suite.ctx, pipeline).Return(nil, errors.New("execution failed"))

		result, err := suite.service.ExecutePipeline(suite.ctx, pipelineID)

		assert.Error(suite.T(), err)
		assert.Nil(suite.T(), result)
		assert.Contains(suite.T(), err.Error(), "execution failed")
	})
}

// TestValidatePipeline tests pipeline validation logic
func (suite *PipelineServiceTestSuite) TestValidatePipeline() {
	// Test valid pipeline
	suite.Run("Valid Pipeline", func() {
		pipeline := &domain.Pipeline{
			Name:        "valid-pipeline",
			Description: "Valid pipeline description",
			Tags:        []string{"valid", "test"},
		}

		err := suite.service.ValidatePipeline(pipeline)
		assert.NoError(suite.T(), err)
	})

	// Test invalid pipeline - empty name
	suite.Run("Invalid Pipeline - Empty Name", func() {
		pipeline := &domain.Pipeline{
			Name:        "",
			Description: "Pipeline without name",
		}

		err := suite.service.ValidatePipeline(pipeline)
		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "name is required")
	})

	// Test invalid pipeline - name too long
	suite.Run("Invalid Pipeline - Name Too Long", func() {
		longName := make([]byte, 256)
		for i := range longName {
			longName[i] = 'a'
		}

		pipeline := &domain.Pipeline{
			Name:        string(longName),
			Description: "Pipeline with very long name",
		}

		err := suite.service.ValidatePipeline(pipeline)
		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "name too long")
	})

	// Test invalid pipeline - description too long
	suite.Run("Invalid Pipeline - Description Too Long", func() {
		longDescription := make([]byte, 1001)
		for i := range longDescription {
			longDescription[i] = 'a'
		}

		pipeline := &domain.Pipeline{
			Name:        "valid-pipeline",
			Description: string(longDescription),
		}

		err := suite.service.ValidatePipeline(pipeline)
		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "description too long")
	})

	// Test invalid pipeline - too many tags
	suite.Run("Invalid Pipeline - Too Many Tags", func() {
		tags := make([]string, 21) // More than 20 tags
		for i := range tags {
			tags[i] = "tag" + string(rune(i))
		}

		pipeline := &domain.Pipeline{
			Name:        "valid-pipeline",
			Description: "Pipeline with too many tags",
			Tags:        tags,
		}

		err := suite.service.ValidatePipeline(pipeline)
		assert.Error(suite.T(), err)
		assert.Contains(suite.T(), err.Error(), "too many tags")
	})
}

// Run the test suite
func TestPipelineService(t *testing.T) {
	suite.Run(t, new(PipelineServiceTestSuite))
}

// TestPipelineValidationEdgeCases tests edge cases in pipeline validation
func TestPipelineValidationEdgeCases(t *testing.T) {
	service := services.NewPipelineService(nil, nil)

	// Test pipeline with special characters in name
	t.Run("Special Characters in Name", func(t *testing.T) {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline_123",
			Description: "Pipeline with special characters",
		}

		err := service.ValidatePipeline(pipeline)
		assert.NoError(t, err)
	})

	// Test pipeline with invalid characters in name
	t.Run("Invalid Characters in Name", func(t *testing.T) {
		pipeline := &domain.Pipeline{
			Name:        "test pipeline with spaces",
			Description: "Pipeline with spaces in name",
		}

		err := service.ValidatePipeline(pipeline)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "invalid characters")
	})

	// Test pipeline with empty tags
	t.Run("Empty Tags", func(t *testing.T) {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline",
			Description: "Pipeline with empty tags",
			Tags:        []string{"", "valid-tag"},
		}

		err := service.ValidatePipeline(pipeline)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "empty tag")
	})

	// Test pipeline with duplicate tags
	t.Run("Duplicate Tags", func(t *testing.T) {
		pipeline := &domain.Pipeline{
			Name:        "test-pipeline",
			Description: "Pipeline with duplicate tags",
			Tags:        []string{"tag1", "tag2", "tag1"},
		}

		err := service.ValidatePipeline(pipeline)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "duplicate tag")
	})
}

// BenchmarkPipelineValidation benchmarks pipeline validation performance
func BenchmarkPipelineValidation(b *testing.B) {
	service := services.NewPipelineService(nil, nil)
	pipeline := &domain.Pipeline{
		Name:        "benchmark-pipeline",
		Description: "Pipeline for benchmarking validation",
		Tags:        []string{"benchmark", "test", "performance"},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = service.ValidatePipeline(pipeline)
	}
}
