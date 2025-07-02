package integration

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pipeline_http "github.com/flext-sh/flext/internal/infrastructure/http"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	shared_kernel_http "github.com/flext-sh/flext/internal/shared_kernel/infrastructure/http"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// InMemoryPipelineRepository é uma implementação em memória para testes
type InMemoryPipelineRepository struct {
	pipelines map[uuid.UUID]*entities.Pipeline
	nextID    int
}

func NewInMemoryPipelineRepository() *InMemoryPipelineRepository {
	return &InMemoryPipelineRepository{
		pipelines: make(map[uuid.UUID]*entities.Pipeline),
		nextID:    1,
	}
}

func (r *InMemoryPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	r.pipelines[pipeline.ID] = pipeline
	return nil
}

func (r *InMemoryPipelineRepository) Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	r.pipelines[pipeline.ID] = pipeline
	return pipeline, nil
}

func (r *InMemoryPipelineRepository) Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	r.pipelines[pipeline.ID] = pipeline
	return pipeline, nil
}

func (r *InMemoryPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	delete(r.pipelines, id)
	return nil
}

func (r *InMemoryPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	pipeline, exists := r.pipelines[id]
	if !exists {
		return nil, nil
	}
	return pipeline, nil
}

func (r *InMemoryPipelineRepository) GetByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	for _, pipeline := range r.pipelines {
		if pipeline.Name == name {
			return pipeline, nil
		}
	}
	return nil, nil
}

func (r *InMemoryPipelineRepository) FindByID(ctx context.Context, id string) (*entities.Pipeline, error) {
	pipelineID, err := uuid.Parse(id)
	if err != nil {
		return nil, err
	}
	return r.GetByID(ctx, pipelineID)
}

func (r *InMemoryPipelineRepository) FindByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	return r.GetByName(ctx, name)
}

func (r *InMemoryPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	pipeline, err := r.GetByName(ctx, name)
	return pipeline != nil, err
}

func (r *InMemoryPipelineRepository) List(ctx context.Context, filter ports.ListPipelinesFilter) ([]*entities.Pipeline, int, error) {
	var result []*entities.Pipeline

	for _, pipeline := range r.pipelines {
		// Apply filters
		if filter.Active != nil && pipeline.IsActive != *filter.Active {
			continue
		}

		// Apply tag filtering
		if len(filter.Tags) > 0 {
			hasTag := false
			for _, filterTag := range filter.Tags {
				for _, pipelineTag := range pipeline.Tags {
					if pipelineTag == filterTag {
						hasTag = true
						break
					}
				}
				if hasTag {
					break
				}
			}
			if !hasTag {
				continue
			}
		}

		result = append(result, pipeline)
	}

	// Apply pagination
	total := len(result)
	start := filter.Offset
	end := start + filter.Limit

	if start > total {
		return []*entities.Pipeline{}, total, nil
	}
	if end > total {
		end = total
	}

	return result[start:end], total, nil
}

func (r *InMemoryPipelineRepository) Count(ctx context.Context) (int, error) {
	return len(r.pipelines), nil
}

// MockLogger para testes
type MockLogger struct{}

func (m *MockLogger) Debug(msg string, fields ...logging.Field)   {}
func (m *MockLogger) Info(msg string, fields ...logging.Field)    {}
func (m *MockLogger) Warn(msg string, fields ...logging.Field)    {}
func (m *MockLogger) Error(msg string, fields ...logging.Field)   {}
func (m *MockLogger) With(fields ...logging.Field) logging.Logger { return m }

func TestPipelineIntegration_CompleteFlow(t *testing.T) {
	// Setup
	repo := NewInMemoryPipelineRepository()
	service := application.NewPipelineService(repo)
	logger := &MockLogger{}

	// Create Echo server
	e := echo.New()
	handler := pipeline_http.NewPipelineHandler(service, logger)
	handler.RegisterRoutes(e)

	t.Run("Create Pipeline Integration", func(t *testing.T) {
		// Prepare request
		createCmd := commands.CreatePipelineCommand{
			Name:        "Integration Test Pipeline",
			Description: "A pipeline created in integration test",
			Type:        "etl",
			Schedule:    "0 0 * * *",
			Configuration: map[string]interface{}{
				"source": "database",
				"target": "warehouse",
			},
		}

		body, _ := json.Marshal(createCmd)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/pipelines", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()

		// Execute
		e.ServeHTTP(rec, req)

		// Assert HTTP response
		assert.Equal(t, http.StatusCreated, rec.Code)

		var response shared_kernel_http.SuccessResponse
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)

		// Assert response data
		resultData, ok := response.Data.(map[string]interface{})
		require.True(t, ok)
		assert.NotEmpty(t, resultData["pipeline_id"])
		assert.Equal(t, "Integration Test Pipeline", resultData["name"])
		assert.Equal(t, "draft", resultData["status"])

		// Verify pipeline was actually created in repository
		pipelines, total, err := repo.List(context.Background(), ports.ListPipelinesFilter{
			Limit:  10,
			Offset: 0,
		})
		require.NoError(t, err)
		assert.Equal(t, 1, total)
		assert.Len(t, pipelines, 1)

		createdPipeline := pipelines[0]
		assert.Equal(t, "Integration Test Pipeline", createdPipeline.Name)
		assert.Equal(t, entities.PipelineTypeETL, createdPipeline.Type)
		assert.Equal(t, entities.PipelineStatusDraft, createdPipeline.Status)
		assert.Equal(t, "0 0 * * *", createdPipeline.Schedule)
	})

	t.Run("Get Pipeline Integration", func(t *testing.T) {
		// First create a pipeline
		pipeline, _ := entities.NewPipeline("Get Test Pipeline", "Test description")
		pipeline.Type = entities.PipelineTypeETL
		repo.Save(context.Background(), pipeline)

		// Prepare request
		req := httptest.NewRequest(http.MethodGet, "/api/v1/pipelines/"+pipeline.ID.String(), nil)
		rec := httptest.NewRecorder()

		// Execute
		e.ServeHTTP(rec, req)

		// Assert
		assert.Equal(t, http.StatusOK, rec.Code)

		var response shared_kernel_http.SuccessResponse
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)

		// Verify response data structure matches DTO
		resultData, ok := response.Data.(map[string]interface{})
		require.True(t, ok)
		assert.Equal(t, pipeline.ID.String(), resultData["id"])
		assert.Equal(t, "Get Test Pipeline", resultData["name"])
		assert.Equal(t, "Test description", resultData["description"])
	})

	t.Run("List Pipelines Integration", func(t *testing.T) {
		// Create multiple pipelines
		for i := 1; i <= 3; i++ {
			pipeline, _ := entities.NewPipeline(fmt.Sprintf("List Test Pipeline %d", i), "Test description")
			pipeline.Type = entities.PipelineTypeETL
			if i%2 == 0 {
				pipeline.Tags = []string{"production"}
			}
			repo.Save(context.Background(), pipeline)
		}

		// Test basic listing
		req := httptest.NewRequest(http.MethodGet, "/api/v1/pipelines?page=1&page_size=10", nil)
		rec := httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)

		var response shared_kernel_http.PaginatedResponse[map[string]interface{}]
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)
		assert.GreaterOrEqual(t, len(response.Data), 3) // At least 3 from this test + possible others

		// Test with tag filtering
		req = httptest.NewRequest(http.MethodGet, "/api/v1/pipelines?tags=production", nil)
		rec = httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusOK, rec.Code)

		err = json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)
		// Should have pipelines with production tag
		assert.GreaterOrEqual(t, len(response.Data), 1)
	})

	t.Run("Add Step Integration", func(t *testing.T) {
		// Create a pipeline first
		pipeline, _ := entities.NewPipeline("Step Test Pipeline", "Test description")
		repo.Save(context.Background(), pipeline)

		// Prepare add step request
		addStepCmd := commands.AddStepCommand{
			PipelineID: pipeline.ID,
			Name:       "Extract Step",
			Type:       "extract",
			Configuration: map[string]interface{}{
				"source_type": "database",
				"connection":  "postgresql://localhost:5432/test",
			},
		}

		body, _ := json.Marshal(addStepCmd)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/pipelines/"+pipeline.ID.String()+"/steps", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()

		// Execute
		e.ServeHTTP(rec, req)

		// Assert
		assert.Equal(t, http.StatusCreated, rec.Code)

		var response shared_kernel_http.SuccessResponse
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)

		// Verify step was added
		updatedPipeline, _ := repo.GetByID(context.Background(), pipeline.ID)
		assert.Len(t, updatedPipeline.Steps, 1)
		assert.Equal(t, "Extract Step", updatedPipeline.Steps[0].Name)
		assert.Equal(t, 1, updatedPipeline.Steps[0].Order)
	})

	t.Run("Execute Pipeline Integration", func(t *testing.T) {
		// Create and activate a pipeline with steps
		pipeline, _ := entities.NewPipeline("Execute Test Pipeline", "Test description")
		pipeline.Activate() // Make it active so it can be executed

		// Add a step so it can be executed
		step := entities.PipelineStep{
			ID:            uuid.New(),
			Name:          "Test Step",
			PluginID:      uuid.New(),
			Configuration: map[string]interface{}{"test": true},
			Order:         1,
		}
		pipeline.AddStep(step)
		repo.Save(context.Background(), pipeline)

		// Prepare execute request
		executeCmd := commands.ExecutePipelineCommand{
			PipelineID: pipeline.ID,
			Context: map[string]interface{}{
				"execution_mode": "test",
			},
		}

		body, _ := json.Marshal(executeCmd)
		req := httptest.NewRequest(http.MethodPost, "/api/v1/pipelines/"+pipeline.ID.String()+"/execute", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()

		// Execute
		e.ServeHTTP(rec, req)

		// Assert
		assert.Equal(t, http.StatusAccepted, rec.Code)

		var response shared_kernel_http.SuccessResponse
		err := json.Unmarshal(rec.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response.Success)

		// Verify response contains execution details
		resultData, ok := response.Data.(map[string]interface{})
		require.True(t, ok)
		assert.NotEmpty(t, resultData["execution_id"])
		assert.Equal(t, "started", resultData["status"])
		assert.NotEmpty(t, resultData["started_at"])
	})

	t.Run("Error Handling Integration", func(t *testing.T) {
		// Test invalid pipeline ID
		req := httptest.NewRequest(http.MethodGet, "/api/v1/pipelines/invalid-uuid", nil)
		rec := httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusInternalServerError, rec.Code) // BaseHandler should catch the invalid UUID

		// Test pipeline not found
		nonExistentID := uuid.New()
		req = httptest.NewRequest(http.MethodGet, "/api/v1/pipelines/"+nonExistentID.String(), nil)
		rec = httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusInternalServerError, rec.Code) // Should handle pipeline not found

		// Test invalid request body
		req = httptest.NewRequest(http.MethodPost, "/api/v1/pipelines", bytes.NewBufferString("invalid json"))
		req.Header.Set("Content-Type", "application/json")
		rec = httptest.NewRecorder()

		e.ServeHTTP(rec, req)

		assert.Equal(t, http.StatusInternalServerError, rec.Code) // Should handle malformed JSON
	})
}

func TestPipelineService_UnitIntegration(t *testing.T) {
	// Test the service layer integration without HTTP
	repo := NewInMemoryPipelineRepository()
	service := application.NewPipelineService(repo)

	t.Run("Service Layer CQRS Integration", func(t *testing.T) {
		ctx := context.Background()

		// Test Command - Create Pipeline
		createCmd := commands.CreatePipelineCommand{
			Name:        "Service Test Pipeline",
			Description: "Testing service layer",
			Type:        "etl",
		}

		result, err := service.CreatePipeline(ctx, createCmd)
		require.NoError(t, err)
		assert.Equal(t, "Service Test Pipeline", result.Name)
		assert.Equal(t, "draft", result.Status)

		// Parse the pipeline ID for queries
		pipelineID, err := uuid.Parse(result.PipelineID)
		require.NoError(t, err)

		// Test Query - Get Pipeline
		getQuery := queries.GetPipelineQuery{PipelineID: pipelineID}
		pipeline, err := service.GetPipeline(ctx, getQuery)
		require.NoError(t, err)
		assert.Equal(t, "Service Test Pipeline", pipeline.Name)
		assert.Equal(t, "Testing service layer", pipeline.Description)

		// Test Query - List Pipelines
		listQuery := queries.ListPipelinesQuery{Limit: 10, Offset: 0}
		listResult, err := service.ListPipelines(ctx, listQuery)
		require.NoError(t, err)
		assert.GreaterOrEqual(t, listResult.Total, 1)
		assert.Len(t, listResult.Pipelines, listResult.Total)

		// Test Command - Add Step
		addStepCmd := commands.AddStepCommand{
			PipelineID: pipelineID,
			Name:       "Service Test Step",
			Configuration: map[string]interface{}{
				"type": "extract",
			},
		}

		stepResult, err := service.AddStep(ctx, addStepCmd)
		require.NoError(t, err)
		assert.NotEmpty(t, stepResult.StepID)

		// Verify step was added via query
		updatedPipeline, err := service.GetPipeline(ctx, getQuery)
		require.NoError(t, err)
		assert.Len(t, updatedPipeline.Steps, 1)
		assert.Equal(t, "Service Test Step", updatedPipeline.Steps[0].Name)
	})
}
