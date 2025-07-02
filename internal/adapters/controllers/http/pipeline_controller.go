package http

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"

	"github.com/flext-sh/flext/internal/adapters/controllers/http/dto"
	"github.com/flext-sh/flext/internal/usecases/pipeline"
	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// PipelineControllerDeps contains all dependencies for PipelineController
type PipelineControllerDeps struct {
	CreateUseCase  *pipeline.CreatePipelineUseCase
	AddStepUseCase *pipeline.AddStepUseCase
	ExecuteUseCase *pipeline.ExecutePipelineUseCase
	GetUseCase     *pipeline.GetPipelineUseCase
	ListUseCase    *pipeline.ListPipelinesUseCase
	Presenter      PipelinePresenter
}

// PipelineController handles HTTP requests for pipeline operations
type PipelineController struct {
	createUseCase  *pipeline.CreatePipelineUseCase
	addStepUseCase *pipeline.AddStepUseCase
	executeUseCase *pipeline.ExecutePipelineUseCase
	getUseCase     *pipeline.GetPipelineUseCase
	listUseCase    *pipeline.ListPipelinesUseCase
	presenter      PipelinePresenter
}

// NewPipelineController creates a new pipeline controller with dependencies
func NewPipelineController(deps PipelineControllerDeps) *PipelineController {
	return &PipelineController{
		createUseCase:  deps.CreateUseCase,
		addStepUseCase: deps.AddStepUseCase,
		executeUseCase: deps.ExecuteUseCase,
		getUseCase:     deps.GetUseCase,
		listUseCase:    deps.ListUseCase,
		presenter:      deps.Presenter,
	}
}

// CreatePipeline handles POST /pipelines
func (c *PipelineController) CreatePipeline(w http.ResponseWriter, r *http.Request) {
	// Parse request
	var req dto.CreatePipelineRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		c.presenter.PresentBadRequest(w, "Invalid request body")
		return
	}

	// Map to use case input
	input := pipeline.CreatePipelineInput{
		Name:        req.Name,
		Description: req.Description,
		Tags:        req.Tags,
	}

	// Execute use case
	output, err := c.createUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentPipelineCreated(w, output)
}

// GetPipeline handles GET /pipelines/{id}
func (c *PipelineController) GetPipeline(w http.ResponseWriter, r *http.Request) {
	// Extract ID from path
	vars := mux.Vars(r)
	idStr := vars["id"]

	id, err := uuid.Parse(idStr)
	if err != nil {
		c.presenter.PresentBadRequest(w, "Invalid pipeline ID")
		return
	}

	// Execute use case
	input := pipeline.GetPipelineInput{ID: id}
	output, err := c.getUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentPipeline(w, output)
}

// ListPipelines handles GET /pipelines
func (c *PipelineController) ListPipelines(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	query := r.URL.Query()
	
	// Build use case input
	input := pipeline.ListPipelinesInput{
		Limit:  c.parseIntParam(query.Get("limit"), 20),
		Offset: c.parseIntParam(query.Get("offset"), 0),
		Tags:   c.parseTagsParam(query.Get("tags")),
	}

	// Parse active filter
	if activeStr := query.Get("active"); activeStr != "" {
		active, err := strconv.ParseBool(activeStr)
		if err == nil {
			input.Active = &active
		}
	}

	// Execute use case
	output, err := c.listUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentPipelineList(w, output)
}

// AddStep handles POST /pipelines/{id}/steps
func (c *PipelineController) AddStep(w http.ResponseWriter, r *http.Request) {
	// Extract pipeline ID from path
	vars := mux.Vars(r)
	pipelineIDStr := vars["id"]

	pipelineID, err := uuid.Parse(pipelineIDStr)
	if err != nil {
		c.presenter.PresentBadRequest(w, "Invalid pipeline ID")
		return
	}

	// Parse request
	var req dto.AddStepRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		c.presenter.PresentBadRequest(w, "Invalid request body")
		return
	}

	// Parse plugin ID
	pluginID, err := uuid.Parse(req.PluginID)
	if err != nil {
		c.presenter.PresentBadRequest(w, "Invalid plugin ID")
		return
	}

	// Map to use case input
	input := pipeline.AddStepInput{
		PipelineID:    pipelineID,
		Name:          req.Name,
		PluginID:      pluginID,
		Configuration: req.Configuration,
		DependsOn:     c.parseUUIDs(req.DependsOn),
	}

	// Execute use case
	output, err := c.addStepUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentStepAdded(w, output)
}

// ExecutePipeline handles POST /pipelines/{id}/execute
func (c *PipelineController) ExecutePipeline(w http.ResponseWriter, r *http.Request) {
	// Extract pipeline ID from path
	vars := mux.Vars(r)
	pipelineIDStr := vars["id"]

	pipelineID, err := uuid.Parse(pipelineIDStr)
	if err != nil {
		c.presenter.PresentBadRequest(w, "Invalid pipeline ID")
		return
	}

	// Parse request (optional execution parameters)
	var req dto.ExecutePipelineRequest
	if r.ContentLength > 0 {
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			c.presenter.PresentBadRequest(w, "Invalid request body")
			return
		}
	}

	// Map to use case input
	input := pipeline.ExecutePipelineInput{
		PipelineID: pipelineID,
		Context: req.Parameters,
	}

	// Execute use case
	output, err := c.executeUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentExecutionStarted(w, output)
}

// Helper methods

func (c *PipelineController) handleError(w http.ResponseWriter, err error) {
	errorMsg := err.Error()
	switch {
	case strings.Contains(errorMsg, "not found"):
		c.presenter.PresentNotFound(w, "Pipeline not found")
	case strings.Contains(errorMsg, "already exists"):
		c.presenter.PresentConflict(w, "Pipeline with this name already exists")
	case strings.Contains(errorMsg, "validation") || strings.Contains(errorMsg, "invalid"):
		c.presenter.PresentBadRequest(w, err.Error())
	default:
		c.presenter.PresentInternalError(w)
	}
}

func (c *PipelineController) parseIntParam(value string, defaultValue int) int {
	if value == "" {
		return defaultValue
	}
	
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return defaultValue
	}
	
	return parsed
}

func (c *PipelineController) parseTagsParam(value string) []string {
	if value == "" {
		return nil
	}
	
	// Simple comma-separated parsing
	// Could be enhanced with proper CSV parsing
	tags := []string{}
	for _, tag := range splitAndTrim(value, ",") {
		if tag != "" {
			tags = append(tags, tag)
		}
	}
	
	return tags
}

func (c *PipelineController) parseUUIDs(values []string) []uuid.UUID {
	uuids := make([]uuid.UUID, 0, len(values))
	for _, v := range values {
		if id, err := uuid.Parse(v); err == nil {
			uuids = append(uuids, id)
		}
	}
	return uuids
}

// splitAndTrim splits a string and trims each part
func splitAndTrim(s string, sep string) []string {
	parts := []string{}
	for _, part := range strings.Split(s, sep) {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			parts = append(parts, trimmed)
		}
	}
	return parts
}