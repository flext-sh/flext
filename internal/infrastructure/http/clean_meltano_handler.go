package http

import (
	"net/http"
	"strconv"
	"strings"

	meltanoUC "github.com/flext-sh/flext/internal/usecases/meltano"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

// CleanMeltanoHandler handles HTTP requests for Meltano using Clean Architecture
type CleanMeltanoHandler struct {
	createProjectUC *meltanoUC.CreateProjectUseCase
	addPluginUC     *meltanoUC.AddPluginUseCase
	runPipelineUC   *meltanoUC.RunPipelineUseCase
	addScheduleUC   *meltanoUC.AddScheduleUseCase
	getProjectUC    *meltanoUC.GetProjectUseCase
	listProjectsUC  *meltanoUC.ListProjectsUseCase
	deleteProjectUC *meltanoUC.DeleteProjectUseCase
}

// NewCleanMeltanoHandler creates a new Clean Architecture Meltano handler
func NewCleanMeltanoHandler(
	createProjectUC *meltanoUC.CreateProjectUseCase,
	addPluginUC *meltanoUC.AddPluginUseCase,
	runPipelineUC *meltanoUC.RunPipelineUseCase,
	addScheduleUC *meltanoUC.AddScheduleUseCase,
	getProjectUC *meltanoUC.GetProjectUseCase,
	listProjectsUC *meltanoUC.ListProjectsUseCase,
	deleteProjectUC *meltanoUC.DeleteProjectUseCase,
) *CleanMeltanoHandler {
	return &CleanMeltanoHandler{
		createProjectUC: createProjectUC,
		addPluginUC:     addPluginUC,
		runPipelineUC:   runPipelineUC,
		addScheduleUC:   addScheduleUC,
		getProjectUC:    getProjectUC,
		listProjectsUC:  listProjectsUC,
		deleteProjectUC: deleteProjectUC,
	}
}

// CreateProject handles Meltano project creation
func (h *CleanMeltanoHandler) CreateProject(c echo.Context) error {
	var input meltanoUC.CreateProjectInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	result, err := h.createProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		// Check if error contains "already exists" message
	if strings.Contains(strings.ToLower(err.Error()), "already exists") {
			return c.JSON(http.StatusConflict, map[string]string{
				"error": err.Error(),
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, result)
}

// AddPlugin handles adding plugins to a Meltano project
func (h *CleanMeltanoHandler) AddPlugin(c echo.Context) error {
	var input meltanoUC.AddPluginInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	// Get project ID from URL parameter
	projectIDStr := c.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}
	input.ProjectID = projectID

	result, err := h.addPluginUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, meltanoUC.ErrProjectNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Project not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// RunPipeline handles running Meltano pipelines
func (h *CleanMeltanoHandler) RunPipeline(c echo.Context) error {
	var input meltanoUC.RunPipelineInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	// Get project ID from URL parameter
	projectIDStr := c.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}
	input.ProjectID = projectID

	result, err := h.runPipelineUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, meltanoUC.ErrProjectNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Project not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// AddSchedule handles adding schedules to a Meltano project
func (h *CleanMeltanoHandler) AddSchedule(c echo.Context) error {
	var input meltanoUC.AddScheduleInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	// Get project ID from URL parameter
	projectIDStr := c.Param("projectId")
	projectID, err := uuid.Parse(projectIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}
	input.ProjectID = projectID

	result, err := h.addScheduleUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, meltanoUC.ErrProjectNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Project not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, result)
}

// GetProject handles getting a specific Meltano project
func (h *CleanMeltanoHandler) GetProject(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}

	input := meltanoUC.GetProjectInput{ID: id}
	result, err := h.getProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, meltanoUC.ErrProjectNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Project not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// ListProjects handles listing Meltano projects with pagination
func (h *CleanMeltanoHandler) ListProjects(c echo.Context) error {
	page := 1
	limit := 10

	if pageStr := c.QueryParam("page"); pageStr != "" {
		if p, err := strconv.Atoi(pageStr); err == nil && p > 0 {
			page = p
		}
	}

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	input := meltanoUC.ListProjectsInput{
		Limit:    limit,
		Offset:   (page - 1) * limit, // Convert page to offset
		OrderBy:  c.QueryParam("order_by"),
		OrderDir: c.QueryParam("order_dir"),
	}

	result, err := h.listProjectsUC.Execute(c.Request().Context(), input)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// DeleteProject handles Meltano project deletion
func (h *CleanMeltanoHandler) DeleteProject(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}

	input := meltanoUC.DeleteProjectInput{ID: id}
	err = h.deleteProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, meltanoUC.ErrProjectNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Project not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.NoContent(http.StatusNoContent)
}