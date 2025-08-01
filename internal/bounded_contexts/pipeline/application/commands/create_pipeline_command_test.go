package commands

import (
	"context"
	"testing"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// MockPipelineRepository é um mock do repositório de pipelines
type MockPipelineRepository struct {
	mock.Mock
}

func (m *MockPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	args := m.Called(ctx, pipeline)
	return args.Error(0)
}

func (m *MockPipelineRepository) Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, pipeline)
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	args := m.Called(ctx, pipeline)
	return args.Get(0).(*entities.Pipeline), args.Error(1)
}

func (m *MockPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
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

func (m *MockPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	args := m.Called(ctx, name)
	return args.Bool(0), args.Error(1)
}

func (m *MockPipelineRepository) List(ctx context.Context, filter ports.ListPipelinesFilter) ([]*entities.Pipeline, int, error) {
	args := m.Called(ctx, filter)
	return args.Get(0).([]*entities.Pipeline), args.Int(1), args.Error(2)
}

func (m *MockPipelineRepository) Count(ctx context.Context) (int, error) {
	args := m.Called(ctx)
	return args.Int(0), args.Error(1)
}

// NewMockPipelineRepository creates a new mock repository for testing
func NewMockPipelineRepository() *MockPipelineRepository {
	return &MockPipelineRepository{}
}

func TestCreatePipelineCommandHandler_Handle_Success(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	cmd := &CreatePipelineCommand{
		Name:        "Test Pipeline",
		Description: "A test pipeline",
		Type:        "etl",
	}

	// Mock repository calls
	mockRepo.On("GetByName", ctx, "Test Pipeline").Return(nil, &value_objects.DomainError{
		Code: "PIPELINE_NOT_FOUND",
	})
	mockRepo.On("Save", ctx, mock.MatchedBy(func(p *entities.Pipeline) bool {
		return p.Name == "Test Pipeline" && p.Type == entities.PipelineTypeETL
	})).Return(nil)

	// Act
	result, err := handler.Handle(ctx, cmd)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.NotEmpty(t, result.PipelineID)
	assert.Equal(t, "Test Pipeline", result.Name)
	assert.Equal(t, "draft", result.Status) // Pipeline starts as draft
	assert.WithinDuration(t, time.Now(), result.CreatedAt, time.Minute)

	mockRepo.AssertExpectations(t)
}

func TestCreatePipelineCommandHandler_Handle_PipelineNameExists(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	cmd := &CreatePipelineCommand{
		Name:        "Existing Pipeline",
		Description: "A test pipeline",
		Type:        "etl",
	}

	existingPipeline := &entities.Pipeline{
		Name: "Existing Pipeline",
	}

	// Mock repository calls
	mockRepo.On("GetByName", ctx, "Existing Pipeline").Return(existingPipeline, nil)

	// Act
	result, err := handler.Handle(ctx, cmd)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)

	domainErr, ok := err.(*value_objects.DomainError)
	require.True(t, ok)
	assert.Equal(t, "PIPELINE_NAME_EXISTS", domainErr.Code)
	assert.Contains(t, domainErr.Message, "already exists")

	mockRepo.AssertExpectations(t)
}

func TestCreatePipelineCommandHandler_Handle_InvalidCommand(t *testing.T) {
	// Arrange
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	tests := []struct {
		name          string
		cmd           *CreatePipelineCommand
		expectedError string
	}{
		{
			name: "empty name",
			cmd: &CreatePipelineCommand{
				Name: "",
				Type: "etl",
			},
			expectedError: "Pipeline name is required",
		},
		{
			name: "name too short",
			cmd: &CreatePipelineCommand{
				Name: "ab",
				Type: "etl",
			},
			expectedError: "Name must be between 3 and 100 characters",
		},
		{
			name: "name too long",
			cmd: &CreatePipelineCommand{
				Name: string(make([]byte, 101)), // 101 characters
				Type: "etl",
			},
			expectedError: "Name must be between 3 and 100 characters",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			result, err := handler.Handle(context.Background(), tt.cmd)

			// Assert
			assert.Error(t, err)
			assert.Nil(t, result)
			assert.Contains(t, err.Error(), tt.expectedError)
		})
	}
}

func TestCreatePipelineCommandHandler_Handle_RepositoryError(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	cmd := &CreatePipelineCommand{
		Name:        "Test Pipeline",
		Description: "A test pipeline",
		Type:        "etl",
	}

	// Mock repository error
	mockRepo.On("GetByName", ctx, "Test Pipeline").Return(nil, &value_objects.DomainError{
		Code: "PIPELINE_NOT_FOUND",
	})
	mockRepo.On("Save", ctx, mock.AnythingOfType("*entities.Pipeline")).Return(
		&value_objects.DomainError{
			Code:    "DATABASE_ERROR",
			Message: "Failed to save pipeline",
		})

	// Act
	result, err := handler.Handle(ctx, cmd)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, result)

	domainErr, ok := err.(*value_objects.DomainError)
	require.True(t, ok)
	assert.Equal(t, "DATABASE_ERROR", domainErr.Code)

	mockRepo.AssertExpectations(t)
}

func TestCreatePipelineCommandHandler_Handle_WithSchedule(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	cmd := &CreatePipelineCommand{
		Name:        "Scheduled Pipeline",
		Description: "A scheduled pipeline",
		Type:        "etl",
		Schedule:    "0 0 * * *", // Daily at midnight
	}

	// Mock repository calls
	mockRepo.On("GetByName", ctx, "Scheduled Pipeline").Return(nil, &value_objects.DomainError{
		Code: "PIPELINE_NOT_FOUND",
	})
	mockRepo.On("Save", ctx, mock.MatchedBy(func(p *entities.Pipeline) bool {
		return p.Name == "Scheduled Pipeline" && p.Schedule == "0 0 * * *"
	})).Return(nil)

	// Act
	result, err := handler.Handle(ctx, cmd)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Scheduled Pipeline", result.Name)

	mockRepo.AssertExpectations(t)
}

func TestCreatePipelineCommandHandler_Handle_WithConfiguration(t *testing.T) {
	// Arrange
	ctx := context.Background()
	mockRepo := &MockPipelineRepository{}
	handler := NewCreatePipelineCommandHandler(mockRepo)

	config := map[string]interface{}{
		"source":     "database",
		"target":     "warehouse",
		"batch_size": 1000,
	}

	cmd := &CreatePipelineCommand{
		Name:          "Configured Pipeline",
		Description:   "A pipeline with configuration",
		Type:          "etl",
		Configuration: config,
	}

	// Mock repository calls
	mockRepo.On("GetByName", ctx, "Configured Pipeline").Return(nil, &value_objects.DomainError{
		Code: "PIPELINE_NOT_FOUND",
	})
	mockRepo.On("Save", ctx, mock.MatchedBy(func(p *entities.Pipeline) bool {
		return p.Name == "Configured Pipeline" && p.Configuration != nil
	})).Return(nil)

	// Act
	result, err := handler.Handle(ctx, cmd)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "Configured Pipeline", result.Name)

	mockRepo.AssertExpectations(t)
}

// TestCreatePipelineCommandIntegration testa o fluxo completo end-to-end
func TestCreatePipelineCommandIntegration(t *testing.T) {
	tests := []struct {
		name           string
		setupData      func(*MockPipelineRepository)
		command        CreatePipelineCommand
		expectedResult func(*CreatePipelineResult) bool
		expectError    bool
		errorContains  string
	}{
		{
			name: "complete_pipeline_creation_flow",
			setupData: func(repo *MockPipelineRepository) {
				// Repository starts empty - mock GetByName to return not found
				repo.On("GetByName", mock.Anything, "E2E Test Pipeline").Return(nil, &value_objects.DomainError{Code: "PIPELINE_NOT_FOUND"})
				repo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(nil)
			},
			command: CreatePipelineCommand{
				Name:        "E2E Test Pipeline",
				Description: "Integration test pipeline",
				Type:        "etl",
				Tags:        []string{"integration", "test", "e2e"},
				CreatedBy:   "test_user",
				Configuration: map[string]interface{}{
					"timeout":     3600,
					"retries":     3,
					"environment": "test",
					"features": map[string]bool{
						"monitoring": true,
						"logging":    true,
					},
				},
			},
			expectedResult: func(result *CreatePipelineResult) bool {
				return result.Name == "E2E Test Pipeline" &&
					result.Status == "draft"
			},
			expectError: false,
		},
		{
			name: "pipeline_with_complex_configuration",
			setupData: func(repo *MockPipelineRepository) {
				// Repository starts empty - mock GetByName to return not found
				repo.On("GetByName", mock.Anything, "Complex Config Pipeline").Return(nil, &value_objects.DomainError{Code: "PIPELINE_NOT_FOUND"})
				repo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(nil)
			},
			command: CreatePipelineCommand{
				Name:        "Complex Config Pipeline",
				Description: "Pipeline with complex nested configuration",
				Type:        "etl",
				CreatedBy:   "test_user",
				Configuration: map[string]interface{}{
					"data_sources": []map[string]interface{}{
						{
							"name":     "source1",
							"type":     "postgresql",
							"host":     "localhost",
							"port":     5432,
							"database": "test_db",
							"schema":   "public",
							"tables":   []string{"users", "orders", "products"},
							"filters": map[string]interface{}{
								"date_range": map[string]string{
									"start": "2024-01-01",
									"end":   "2024-12-31",
								},
							},
						},
						{
							"name": "source2",
							"type": "rest_api",
							"url":  "https://api.example.com/v1",
							"auth": map[string]string{
								"type":  "bearer",
								"token": "test_token",
							},
							"endpoints": []string{"/users", "/orders"},
						},
					},
					"transformations": []map[string]interface{}{
						{
							"name":   "clean_data",
							"type":   "python",
							"script": "data_cleaning.py",
							"params": map[string]interface{}{
								"remove_nulls":     true,
								"standardize_case": true,
							},
						},
					},
					"destinations": []map[string]interface{}{
						{
							"name":   "warehouse",
							"type":   "postgresql",
							"schema": "analytics",
							"tables": map[string]string{
								"users":    "dim_users",
								"orders":   "fact_orders",
								"products": "dim_products",
							},
						},
					},
				},
			},
			expectedResult: func(result *CreatePipelineResult) bool {
				return result.Name == "Complex Config Pipeline" &&
					result.Status == "draft"
			},
			expectError: false,
		},
		{
			name: "error_handling_repository_failure",
			setupData: func(repo *MockPipelineRepository) {
				// Setup repository to fail on save
				repo.On("GetByName", mock.Anything, "Should Fail Pipeline").Return(nil, &value_objects.DomainError{Code: "PIPELINE_NOT_FOUND"})
				repo.On("Save", mock.Anything, mock.AnythingOfType("*entities.Pipeline")).Return(&value_objects.DomainError{Code: "SAVE_FAILED", Message: "failed to save pipeline"})
			},
			command: CreatePipelineCommand{
				Name:        "Should Fail Pipeline",
				Description: "This pipeline creation should fail",
				Type:        "etl",
				CreatedBy:   "test_user",
			},
			expectedResult: nil,
			expectError:    true,
			errorContains:  "failed to save pipeline",
		},
		{
			name: "pipeline_name_uniqueness_validation",
			setupData: func(repo *MockPipelineRepository) {
				// Setup repository to simulate existing pipeline
				existingPipeline := &entities.Pipeline{
					Name:        "Existing Pipeline",
					Description: "Already exists",
					Status:      entities.PipelineStatusDraft,
				}
				repo.On("GetByName", mock.Anything, "Existing Pipeline").Return(existingPipeline, nil)
			},
			command: CreatePipelineCommand{
				Name:        "Existing Pipeline",
				Description: "Should fail due to name conflict",
				Type:        "etl",
				CreatedBy:   "test_user",
			},
			expectedResult: nil,
			expectError:    true,
			errorContains:  "already exists",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			mockRepo := NewMockPipelineRepository()
			tt.setupData(mockRepo)

			handler := NewCreatePipelineCommandHandler(mockRepo)
			ctx := context.Background()

			// Execute
			result, err := handler.Handle(ctx, &tt.command)

			// Validate
			if tt.expectError {
				assert.Error(t, err)
				if tt.errorContains != "" {
					assert.Contains(t, err.Error(), tt.errorContains)
				}
				assert.Nil(t, result)
				return
			}

			// Success case validation
			assert.NoError(t, err)
			assert.NotNil(t, result)

			if tt.expectedResult != nil && result != nil {
				assert.True(t, tt.expectedResult(result), "Result validation failed")
			}

			// Validate that basic result fields are correct
			assert.Equal(t, tt.command.Name, result.Name)
			assert.Equal(t, "draft", result.Status)
		})
	}
}

// TestPipelineServiceIntegration testa o servico completo
func TestPipelineServiceIntegration(t *testing.T) {
	t.Skip("Temporarily disabled due to service layer dependency issues")
}

// TestErrorHandlingFlow testa fluxos de erro completos
func TestErrorHandlingFlow(t *testing.T) {
	t.Skip("Temporarily disabled due to service layer dependency issues")
}
