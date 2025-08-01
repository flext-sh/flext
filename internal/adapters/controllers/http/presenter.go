package http

import (
	"encoding/json"
	"net/http"

	"github.com/flext/flexcore/internal/usecases/pipeline"
)

// PipelinePresenter defines the interface for presenting pipeline responses
type PipelinePresenter interface {
	PresentPipelineCreated(w http.ResponseWriter, output *pipeline.CreatePipelineOutput)
	PresentPipeline(w http.ResponseWriter, output *pipeline.GetPipelineOutput)
	PresentPipelineList(w http.ResponseWriter, output *pipeline.ListPipelinesOutput)
	PresentStepAdded(w http.ResponseWriter, output *pipeline.AddStepOutput)
	PresentExecutionStarted(w http.ResponseWriter, output *pipeline.ExecutePipelineOutput)
	PresentBadRequest(w http.ResponseWriter, message string)
	PresentNotFound(w http.ResponseWriter, message string)
	PresentConflict(w http.ResponseWriter, message string)
	PresentInternalError(w http.ResponseWriter)
}

// JSONPresenter implements PipelinePresenter for JSON responses
type JSONPresenter struct{}

// NewJSONPresenter creates a new JSON presenter
func NewJSONPresenter() *JSONPresenter {
	return &JSONPresenter{}
}

// PresentPipelineCreated presents a created pipeline
func (p *JSONPresenter) PresentPipelineCreated(w http.ResponseWriter, output *pipeline.CreatePipelineOutput) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)

	response := map[string]interface{}{
		"id":          output.ID,
		"name":        output.Name,
		"description": output.Description,
		"tags":        output.Tags,
		"is_active":   output.IsActive,
		"created_at":  output.CreatedAt,
	}

	json.NewEncoder(w).Encode(response)
}

// PresentPipeline presents a single pipeline
func (p *JSONPresenter) PresentPipeline(w http.ResponseWriter, output *pipeline.GetPipelineOutput) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	response := map[string]interface{}{
		"id":          output.ID,
		"name":        output.Name,
		"description": output.Description,
		"tags":        output.Tags,
		"is_active":   output.IsActive,
		"steps":       p.presentSteps(output.Steps),
		"created_at":  output.CreatedAt,
		"updated_at":  output.UpdatedAt,
	}

	json.NewEncoder(w).Encode(response)
}

// PresentPipelineList presents a list of pipelines
func (p *JSONPresenter) PresentPipelineList(w http.ResponseWriter, output *pipeline.ListPipelinesOutput) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	pipelines := make([]map[string]interface{}, len(output.Pipelines))
	for i, p := range output.Pipelines {
		pipelines[i] = map[string]interface{}{
			"id":          p.ID,
			"name":        p.Name,
			"description": p.Description,
			"tags":        p.Tags,
			"is_active":   p.IsActive,
			"step_count":  p.StepCount,
			"created_at":  p.CreatedAt,
			"updated_at":  p.UpdatedAt,
		}
	}

	response := map[string]interface{}{
		"pipelines": pipelines,
		"total":     output.Total,
		"limit":     output.Limit,
		"offset":    output.Offset,
	}

	json.NewEncoder(w).Encode(response)
}

// PresentStepAdded presents a step addition response
func (p *JSONPresenter) PresentStepAdded(w http.ResponseWriter, output *pipeline.AddStepOutput) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)

	response := map[string]interface{}{
		"step_id":     output.StepID,
		"pipeline_id": output.PipelineID,
		"name":        output.StepName,
		"order":       output.Order,
	}

	json.NewEncoder(w).Encode(response)
}

// PresentExecutionStarted presents a pipeline execution start response
func (p *JSONPresenter) PresentExecutionStarted(w http.ResponseWriter, output *pipeline.ExecutePipelineOutput) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)

	response := map[string]interface{}{
		"execution_id": output.ExecutionID,
		"pipeline_id":  output.PipelineID,
		"status":       output.Status,
		"started_at":   output.StartedAt,
	}

	json.NewEncoder(w).Encode(response)
}

// PresentBadRequest presents a bad request error
func (p *JSONPresenter) PresentBadRequest(w http.ResponseWriter, message string) {
	p.presentError(w, http.StatusBadRequest, "Bad Request", message)
}

// PresentNotFound presents a not found error
func (p *JSONPresenter) PresentNotFound(w http.ResponseWriter, message string) {
	p.presentError(w, http.StatusNotFound, "Not Found", message)
}

// PresentConflict presents a conflict error
func (p *JSONPresenter) PresentConflict(w http.ResponseWriter, message string) {
	p.presentError(w, http.StatusConflict, "Conflict", message)
}

// PresentInternalError presents an internal server error
func (p *JSONPresenter) PresentInternalError(w http.ResponseWriter) {
	p.presentError(w, http.StatusInternalServerError, "Internal Server Error", "An unexpected error occurred")
}

// Helper methods

func (p *JSONPresenter) presentError(w http.ResponseWriter, statusCode int, error string, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	response := map[string]interface{}{
		"error":   error,
		"message": message,
		"code":    statusCode,
	}

	json.NewEncoder(w).Encode(response)
}

func (p *JSONPresenter) presentSteps(steps []pipeline.StepOutput) []map[string]interface{} {
	result := make([]map[string]interface{}, len(steps))
	for i, step := range steps {
		result[i] = map[string]interface{}{
			"id":            step.ID,
			"name":          step.Name,
			"plugin_id":     step.PluginID,
			"configuration": step.Configuration,
			"depends_on":    step.DependsOn,
		}
	}
	return result
}
