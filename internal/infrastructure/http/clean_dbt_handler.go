package http

import (
	"net/http"
	"strconv"

	dbtUC "github.com/flext-sh/flext/internal/usecases/dbt"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

// CleanDbtHandler handles HTTP requests for DBT using Clean Architecture
type CleanDbtHandler struct {
	createProjectUC  *dbtUC.CreateProjectUseCase
	executeProjectUC *dbtUC.ExecuteProjectUseCase
	getProjectUC     *dbtUC.GetProjectUseCase
	listProjectsUC   *dbtUC.ListProjectsUseCase
	deleteProjectUC  *dbtUC.DeleteProjectUseCase
}

// NewCleanDbtHandler creates a new Clean Architecture DBT handler
func NewCleanDbtHandler(
	createProjectUC *dbtUC.CreateProjectUseCase,
	executeProjectUC *dbtUC.ExecuteProjectUseCase,
	getProjectUC *dbtUC.GetProjectUseCase,
	listProjectsUC *dbtUC.ListProjectsUseCase,
	deleteProjectUC *dbtUC.DeleteProjectUseCase,
) *CleanDbtHandler {
	return &CleanDbtHandler{
		createProjectUC:  createProjectUC,
		executeProjectUC: executeProjectUC,
		getProjectUC:     getProjectUC,
		listProjectsUC:   listProjectsUC,
		deleteProjectUC:  deleteProjectUC,
	}
}

// CreateProject handles DBT project creation
func (h *CleanDbtHandler) CreateProject(c echo.Context) error {
	var input dbtUC.CreateProjectInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	result, err := h.createProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, dbtUC.ErrProjectNameAlreadyExists) {
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

// ExecuteProject handles DBT project execution
func (h *CleanDbtHandler) ExecuteProject(c echo.Context) error {
	var input dbtUC.ExecuteProjectInput
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

	result, err := h.executeProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, dbtUC.ErrProjectNotFound) {
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

// GetProject handles getting a specific DBT project
func (h *CleanDbtHandler) GetProject(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}

	input := dbtUC.GetProjectInput{ID: id}
	result, err := h.getProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, dbtUC.ErrProjectNotFound) {
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

// ListProjects handles listing DBT projects with pagination
func (h *CleanDbtHandler) ListProjects(c echo.Context) error {
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

	input := dbtUC.ListProjectsInput{
		Limit:  limit,
		Offset: (page - 1) * limit, // Convert page to offset
	}

	result, err := h.listProjectsUC.Execute(c.Request().Context(), input)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// DeleteProject handles DBT project deletion
func (h *CleanDbtHandler) DeleteProject(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid project ID format",
		})
	}

	input := dbtUC.DeleteProjectInput{ID: id}
	err = h.deleteProjectUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, dbtUC.ErrProjectNotFound) {
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
