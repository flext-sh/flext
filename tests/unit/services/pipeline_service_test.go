package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pluginEntities "github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	domainServices "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/services"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// MockPipelineRepository provides mock implementation for testing
type MockPipelineRepository struct {
	mock.Mock
}

func (m *MockPipelineRepository) Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, pipeline)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	args := m.Called(ctx, pipeline)
	return args.Error(0)
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

func (m *MockPipelineRepository) List(ctx context.Context, filter ports.ListPipelinesFilter) ([]*entities.Pipeline, int, error) {
	args := m.Called(ctx, filter)
	return args.Get(0).([]*entities.Pipeline), args.Int(1), args.Error(2)
}

func (m *MockPipelineRepository) FindByID(ctx context.Context, id string) (*entities.Pipeline, error) {
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

func (m *MockPipelineRepository) Count(ctx context.Context) (int, error) {
	args := m.Called(ctx)
	return args.Int(0), args.Error(1)
}

func (m *MockPipelineRepository) Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, pipeline)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	args := m.Called(ctx, name)
	return args.Bool(0), args.Error(1)
}

// MockExecutionService provides mock implementation for testing
type MockExecutionService struct {
	mock.Mock
}

func (m *MockExecutionService) ExecutePipeline(ctx context.Context, pipeline *entities.Pipeline) (*ports.ExecutionRecord, error) {
	args := m.Called(ctx, pipeline)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*ports.ExecutionRecord), args.Error(1)
}

func (m *MockExecutionService) Count(ctx context.Context) (int, error) {
	args := m.Called(ctx)
	return args.Get(0).(int), args.Error(1)
}

// MockPipelineExecutor provides mock implementation for domain services
type MockPipelineExecutor struct {
	mock.Mock
}

func (m *MockPipelineExecutor) Execute(ctx context.Context, pipeline *entities.Pipeline) (*domainServices.PipelineExecution, error) {
	args := m.Called(ctx, pipeline)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domainServices.PipelineExecution), args.Error(1)
}

// MockExecutionStatsService provides mock implementation for execution stats
type MockExecutionStatsService struct {
	mock.Mock
}

func (m *MockExecutionStatsService) GetPipelineExecutionMetrics(ctx context.Context, pipelineID uuid.UUID) (*services.PipelineExecutionMetrics, error) {
	args := m.Called(ctx, pipelineID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*services.PipelineExecutionMetrics), args.Error(1)
}

func (m *MockExecutionStatsService) GetGlobalExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	args := m.Called(ctx)
	return args.Get(0).(map[string]interface{}), args.Error(1)
}

func (m *MockExecutionStatsService) RecordExecution(ctx context.Context, execution *ports.ExecutionRecord) error {
	args := m.Called(ctx, execution)
	return args.Error(0)
}

func (m *MockExecutionStatsService) GetPipelineLastExecution(ctx context.Context, pipelineID uuid.UUID) (*ports.ExecutionRecord, error) {
	args := m.Called(ctx, pipelineID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*ports.ExecutionRecord), args.Error(1)
}

func (m *MockExecutionStatsService) GetPipelineExecutionCounts(ctx context.Context, pipelineID uuid.UUID) (int, int, int, error) {
	args := m.Called(ctx, pipelineID)
	return args.Int(0), args.Int(1), args.Int(2), args.Error(3)
}

// MockPluginRepository provides mock implementation for testing the domain executor
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

// Test helper to create a valid pipeline
func createValidPipeline(name string) *entities.Pipeline {
	pipeline, _ := entities.NewPipeline(name, "Test pipeline description")
	pipeline.Tags = []string{"test"}
	
	// Add at least one step first so it can be activated
	step := entities.PipelineStep{
		ID:            uuid.New(),
		Name:          "Test Step",
		PluginID:      uuid.New(),
		Configuration: map[string]interface{}{"test": true},
		Order:         1,
		DependsOn:     []uuid.UUID{},
	}
	pipeline.Steps = []entities.PipelineStep{step}
	
	// Now activate the pipeline to ensure it can be executed
	err := pipeline.Activate()
	if err != nil {
		// Handle activation error, but for tests we can ignore
	}
	return pipeline
}

// Helper function to create string pointers
func stringPtr(s string) *string {
	return &s
}

// Test helper to create pipeline service with mocks
func createPipelineService(repo *MockPipelineRepository, execService *MockExecutionService) *application.PipelineService {
	// Create a mock plugin repository for the executor
	mockPluginRepo := &MockPluginRepository{}
	// Set up default expectations for any plugin lookup
	mockPlugin, _ := pluginEntities.NewPlugin("test-plugin", "1.0.0", "test-entry", pluginEntities.PluginTypeSource)
	mockPluginRepo.On("GetByID", mock.Anything, mock.AnythingOfType("uuid.UUID")).Return(mockPlugin, nil)
	// Create an executor with simulation mode (no real plugin execution)
	mockExecutor := domainServices.NewPipelineExecutorWithSimulation(mockPluginRepo)
	// Pass nil for stats service - it will be handled gracefully
	return application.NewPipelineService(repo, mockExecutor, nil)
}

// TestPipelineService_CreatePipeline tests pipeline creation scenarios
func TestPipelineService_CreatePipeline(t *testing.T) {
	tests := []struct {
		name          string
		command       commands.CreatePipelineCommand
		setupMocks    func(*MockPipelineRepository)
		expectedError string
		expectSuccess bool
	}{
		{
			name: "successful creation",
			command: commands.CreatePipelineCommand{
				Name:        "test-pipeline",
				Description: "Test pipeline description",
				Type:        "etl",
				Tags:        []string{"test"},
				CreatedBy:   "test-user",
			},
			setupMocks: func(repo *MockPipelineRepository) {
				repo.On("GetByName", mock.Anything, "test-pipeline").Return(nil, errors.New("not found"))
				repo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(nil)
			},
			expectSuccess: true,
		},
		{
			name: "duplicate name error",
			command: commands.CreatePipelineCommand{
				Name:        "existing-pipeline",
				Description: "Test pipeline description",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			setupMocks: func(repo *MockPipelineRepository) {
				existing := createValidPipeline("existing-pipeline")
				repo.On("GetByName", mock.Anything, "existing-pipeline").Return(existing, nil)
			},
			expectedError: "already exists",
		},
		{
			name: "invalid pipeline - empty name",
			command: commands.CreatePipelineCommand{
				Name:        "",
				Description: "Pipeline without name",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			setupMocks:    func(repo *MockPipelineRepository) {},
			expectedError: "name is required",
		},
		{
			name: "repository error during creation",
			command: commands.CreatePipelineCommand{
				Name:        "test-pipeline",
				Description: "Test pipeline description",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			setupMocks: func(repo *MockPipelineRepository) {
				repo.On("GetByName", mock.Anything, "test-pipeline").Return(nil, errors.New("not found"))
				repo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(errors.New("insert failed"))
			},
			expectedError: "insert failed",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := new(MockPipelineRepository)
			mockExecution := new(MockExecutionService)
			service := createPipelineService(mockRepo, mockExecution)

			tt.setupMocks(mockRepo)

			// Execute
			result, err := service.CreatePipeline(context.Background(), tt.command)

			// Assert
			if tt.expectSuccess {
				require.NoError(t, err)
				assert.NotNil(t, result)
				assert.NotEmpty(t, result.PipelineID)
				assert.Equal(t, tt.command.Name, result.Name)
				assert.Equal(t, tt.command.Type, result.Type)
				assert.WithinDuration(t, time.Now(), result.CreatedAt, time.Second)
			} else {
				assert.Error(t, err)
				assert.Nil(t, result)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
			mockExecution.AssertExpectations(t)
		})
	}
}

// TestPipelineService_GetPipeline tests pipeline retrieval
func TestPipelineService_GetPipeline(t *testing.T) {
	pipelineID := uuid.New()

	tests := []struct {
		name          string
		query         queries.GetPipelineQuery
		setupMocks    func(*MockPipelineRepository)
		expectedError string
		expectSuccess bool
	}{
		{
			name:  "successful retrieval",
			query: queries.GetPipelineQuery{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository) {
				pipeline := createValidPipeline("test-pipeline")
				pipeline.ID = pipelineID
				repo.On("GetByID", mock.Anything, pipelineID).Return(pipeline, nil)
			},
			expectSuccess: true,
		},
		{
			name:  "pipeline not found",
			query: queries.GetPipelineQuery{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository) {
				repo.On("GetByID", mock.Anything, pipelineID).Return(nil, errors.New("pipeline not found"))
			},
			expectedError: "pipeline not found",
		},
		{
			name:  "repository error",
			query: queries.GetPipelineQuery{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository) {
				repo.On("GetByID", mock.Anything, pipelineID).Return(nil, errors.New("connection timeout"))
			},
			expectedError: "connection timeout",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := new(MockPipelineRepository)
			mockExecution := new(MockExecutionService)
			service := createPipelineService(mockRepo, mockExecution)

			tt.setupMocks(mockRepo)

			// Execute
			result, err := service.GetPipeline(context.Background(), tt.query)

			// Assert
			if tt.expectSuccess {
				require.NoError(t, err)
				assert.NotNil(t, result)
				assert.Equal(t, tt.query.PipelineID, result.ID)
			} else {
				assert.Error(t, err)
				assert.Nil(t, result)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
			mockExecution.AssertExpectations(t)
		})
	}
}

// TestPipelineService_ListPipelines tests pipeline listing
func TestPipelineService_ListPipelines(t *testing.T) {
	tests := []struct {
		name          string
		query         queries.ListPipelinesQuery
		setupMocks    func(*MockPipelineRepository)
		expectedCount int
		expectedTotal int
		expectedError string
		expectSuccess bool
	}{
		{
			name:  "successful listing with results",
			query: queries.ListPipelinesQuery{Limit: 10, Offset: 0},
			setupMocks: func(repo *MockPipelineRepository) {
				pipelines := []*entities.Pipeline{
					createValidPipeline("pipeline-1"),
					createValidPipeline("pipeline-2"),
				}
				filter := ports.ListPipelinesFilter{Limit: 10, Offset: 0}
				repo.On("List", mock.Anything, filter).Return(pipelines, 2, nil)
			},
			expectedCount: 2,
			expectedTotal: 2,
			expectSuccess: true,
		},
		{
			name:  "successful listing with no results",
			query: queries.ListPipelinesQuery{Limit: 10, Offset: 0},
			setupMocks: func(repo *MockPipelineRepository) {
				filter := ports.ListPipelinesFilter{Limit: 10, Offset: 0}
				repo.On("List", mock.Anything, filter).Return([]*entities.Pipeline{}, 0, nil)
			},
			expectedCount: 0,
			expectedTotal: 0,
			expectSuccess: true,
		},
		{
			name:  "repository error",
			query: queries.ListPipelinesQuery{Limit: 10, Offset: 0},
			setupMocks: func(repo *MockPipelineRepository) {
				filter := ports.ListPipelinesFilter{Limit: 10, Offset: 0}
				repo.On("List", mock.Anything, filter).Return([]*entities.Pipeline{}, 0, errors.New("query failed"))
			},
			expectedError: "query failed",
		},
		{
			name:  "pagination test",
			query: queries.ListPipelinesQuery{Limit: 5, Offset: 10},
			setupMocks: func(repo *MockPipelineRepository) {
				pipelines := []*entities.Pipeline{
					createValidPipeline("pipeline-11"),
					createValidPipeline("pipeline-12"),
				}
				filter := ports.ListPipelinesFilter{Limit: 5, Offset: 10}
				repo.On("List", mock.Anything, filter).Return(pipelines, 15, nil)
			},
			expectedCount: 2,
			expectedTotal: 15,
			expectSuccess: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := new(MockPipelineRepository)
			mockExecution := new(MockExecutionService)
			service := createPipelineService(mockRepo, mockExecution)

			tt.setupMocks(mockRepo)

			// Execute
			result, err := service.ListPipelines(context.Background(), tt.query)

			// Assert
			if tt.expectSuccess {
				require.NoError(t, err)
				assert.NotNil(t, result)
				assert.Len(t, result.Pipelines, tt.expectedCount)
				assert.Equal(t, tt.expectedTotal, result.Total)
			} else {
				assert.Error(t, err)
				assert.Nil(t, result)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
			mockExecution.AssertExpectations(t)
		})
	}
}

// TestPipelineService_ExecutePipeline tests pipeline execution
func TestPipelineService_ExecutePipeline(t *testing.T) {
	pipelineID := uuid.New()

	tests := []struct {
		name          string
		command       commands.ExecutePipelineCommand
		setupMocks    func(*MockPipelineRepository, *MockExecutionService)
		expectedError string
		expectSuccess bool
	}{
		{
			name:    "successful execution",
			command: commands.ExecutePipelineCommand{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository, exec *MockExecutionService) {
				pipeline := createValidPipeline("test-pipeline")
				pipeline.ID = pipelineID

				repo.On("GetByID", mock.Anything, pipelineID).Return(pipeline, nil)
				// Note: exec mock not needed since we're using the domain executor directly
			},
			expectSuccess: true,
		},
		{
			name:    "pipeline not found",
			command: commands.ExecutePipelineCommand{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository, exec *MockExecutionService) {
				repo.On("GetByID", mock.Anything, pipelineID).Return(nil, errors.New("pipeline not found"))
			},
			expectedError: "pipeline not found",
		},
		{
			name:    "execution service error",
			command: commands.ExecutePipelineCommand{PipelineID: pipelineID},
			setupMocks: func(repo *MockPipelineRepository, exec *MockExecutionService) {
				pipeline := createValidPipeline("test-pipeline")
				pipeline.ID = pipelineID

				// Create a pipeline without steps to cause execution failure
				emptyPipeline := createValidPipeline("test-pipeline")
				emptyPipeline.ID = pipelineID
				emptyPipeline.Steps = []entities.PipelineStep{} // Remove steps to cause failure
				repo.On("GetByID", mock.Anything, pipelineID).Return(emptyPipeline, nil)
			},
			expectedError: "has no steps",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := new(MockPipelineRepository)
			mockExecution := new(MockExecutionService)
			service := createPipelineService(mockRepo, mockExecution)

			tt.setupMocks(mockRepo, mockExecution)

			// Execute
			result, err := service.ExecutePipeline(context.Background(), tt.command)

			// Assert
			if tt.expectSuccess {
				require.NoError(t, err)
				assert.NotNil(t, result)
				assert.Equal(t, tt.command.PipelineID, result.PipelineID)
			} else {
				assert.Error(t, err)
				assert.Nil(t, result)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
			mockExecution.AssertExpectations(t)
		})
	}
}

// TestCommandValidation tests command validation logic
func TestCommandValidation(t *testing.T) {
	tests := []struct {
		name          string
		command       commands.CreatePipelineCommand
		expectedError string
		expectValid   bool
	}{
		{
			name: "valid command",
			command: commands.CreatePipelineCommand{
				Name:        "valid-pipeline",
				Description: "Valid pipeline description",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			expectValid: true,
		},
		{
			name: "empty name",
			command: commands.CreatePipelineCommand{
				Name:        "",
				Description: "Pipeline without name",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			expectedError: "name is required",
		},
		{
			name: "name too short",
			command: commands.CreatePipelineCommand{
				Name:        "ab", // Only 2 characters
				Description: "Pipeline with short name",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			expectedError: "between 3 and 100 characters",
		},
		{
			name: "name too long",
			command: commands.CreatePipelineCommand{
				Name:        string(make([]byte, 101)), // 101 characters
				Description: "Pipeline with very long name",
				Type:        "etl",
				CreatedBy:   "test-user",
			},
			expectedError: "between 3 and 100 characters",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.command.Validate()

			if tt.expectValid {
				assert.NoError(t, err)
			} else {
				assert.Error(t, err)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}
		})
	}
}

// TestPipelineService_UpdatePipeline tests pipeline updates
func TestPipelineService_UpdatePipeline(t *testing.T) {
	pipelineID := uuid.New()

	tests := []struct {
		name          string
		command       commands.UpdatePipelineCommand
		setupMocks    func(*MockPipelineRepository)
		expectedError string
		expectSuccess bool
	}{
		{
			name: "successful update",
			command: commands.UpdatePipelineCommand{
				PipelineID:  pipelineID,
				Name:        stringPtr("updated-pipeline"),
				Description: stringPtr("Updated description"),
				Tags:        []string{"updated"},
			},
			setupMocks: func(repo *MockPipelineRepository) {
				existing := createValidPipeline("original-pipeline")
				existing.ID = pipelineID
				
				// Create updated pipeline with expected changes
				updated := createValidPipeline("updated-pipeline")
				updated.ID = pipelineID
				updated.Description = "Updated description"

				repo.On("GetByID", mock.Anything, pipelineID).Return(existing, nil)
				repo.On("Update", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(updated, nil)
			},
			expectSuccess: true,
		},
		{
			name: "pipeline not found",
			command: commands.UpdatePipelineCommand{
				PipelineID:  pipelineID,
				Name:        stringPtr("updated-pipeline"),
				Description: stringPtr("Updated description"),
			},
			setupMocks: func(repo *MockPipelineRepository) {
				repo.On("GetByID", mock.Anything, pipelineID).Return(nil, errors.New("pipeline not found"))
			},
			expectedError: "pipeline not found",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := new(MockPipelineRepository)
			mockExecution := new(MockExecutionService)
			service := createPipelineService(mockRepo, mockExecution)

			tt.setupMocks(mockRepo)

			// Execute
			result, err := service.UpdatePipeline(context.Background(), tt.command)

			// Assert
			if tt.expectSuccess {
				require.NoError(t, err)
				assert.NotNil(t, result)
				assert.Equal(t, *tt.command.Name, result.Name)
				assert.Equal(t, *tt.command.Description, result.Description)
			} else {
				assert.Error(t, err)
				assert.Nil(t, result)
				if tt.expectedError != "" {
					assert.Contains(t, err.Error(), tt.expectedError)
				}
			}

			// Verify mock expectations
			mockRepo.AssertExpectations(t)
			mockExecution.AssertExpectations(t)
		})
	}
}

// BenchmarkCommandValidation benchmarks the validation performance
func BenchmarkCommandValidation(b *testing.B) {
	command := commands.CreatePipelineCommand{
		Name:        "benchmark-pipeline",
		Description: "Benchmark test pipeline",
		Type:        "etl",
		CreatedBy:   "test-user",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = command.Validate()
	}
}

// BenchmarkPipelineCreation benchmarks pipeline creation (mock scenario)
func BenchmarkPipelineCreation(b *testing.B) {
	mockRepo := new(MockPipelineRepository)
	mockExecution := new(MockExecutionService)
	service := createPipelineService(mockRepo, mockExecution)

	// Setup mocks for successful creation
	mockRepo.On("GetByName", mock.Anything, mock.AnythingOfType("string")).Return(nil, errors.New("not found"))
	mockRepo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		command := commands.CreatePipelineCommand{
			Name:        "benchmark-pipeline-" + string(rune(i)),
			Description: "Benchmark test pipeline",
			Type:        "etl",
			CreatedBy:   "test-user",
		}
		_, _ = service.CreatePipeline(context.Background(), command)
	}
}
