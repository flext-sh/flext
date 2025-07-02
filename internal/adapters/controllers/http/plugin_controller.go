package http

import (
	"encoding/json"
	"net/http"

	"github.com/flext-sh/flext/internal/adapters/controllers/http/dto"
	"github.com/flext-sh/flext/internal/usecases/plugin"
	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

// PluginController handles HTTP requests for plugin operations
type PluginController struct {
	registerUseCase  *plugin.RegisterPluginUseCase
	activateUseCase  *plugin.ActivatePluginUseCase
	presenter        PluginPresenter
}

// NewPluginController creates a new plugin controller
func NewPluginController(
	registerUseCase *plugin.RegisterPluginUseCase,
	activateUseCase *plugin.ActivatePluginUseCase,
	presenter PluginPresenter,
) *PluginController {
	return &PluginController{
		registerUseCase: registerUseCase,
		activateUseCase: activateUseCase,
		presenter:       presenter,
	}
}

// RegisterPlugin handles POST /plugins
func (c *PluginController) RegisterPlugin(w http.ResponseWriter, r *http.Request) {
	// Parse request
	var req dto.RegisterPluginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		c.presenter.PresentBadRequest(w, "Invalid request body")
		return
	}

	// Map to use case input
	input := plugin.RegisterPluginInput{
		Name:          req.Name,
		Type:          req.Type,
		Version:       req.Version,
		Capabilities:  req.Capabilities,
		Configuration: req.Configuration,
	}

	// Execute use case
	output, err := c.registerUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentPluginRegistered(w, output)
}

// ActivatePlugin handles PUT /plugins/{id}/activate
func (c *PluginController) ActivatePlugin(w http.ResponseWriter, r *http.Request) {
	// Extract plugin ID from path
	vars := mux.Vars(r)
	pluginIDStr := vars["id"]

	pluginID, err := uuid.Parse(pluginIDStr)
	if err != nil {
		c.presenter.PresentBadRequest(w, "Invalid plugin ID")
		return
	}

	// Map to use case input
	input := plugin.ActivatePluginInput{
		PluginID: pluginID,
	}

	// Execute use case
	output, err := c.activateUseCase.Execute(r.Context(), input)
	if err != nil {
		c.handleError(w, err)
		return
	}

	// Present response
	c.presenter.PresentPluginActivated(w, output)
}

// Helper methods

func (c *PluginController) handleError(w http.ResponseWriter, err error) {
	switch err {
	case plugin.ErrPluginNotFound:
		c.presenter.PresentNotFound(w, "Plugin not found")
	case plugin.ErrPluginAlreadyExists:
		c.presenter.PresentConflict(w, "Plugin with this name already exists")
	default:
		c.presenter.PresentInternalError(w)
	}
}

// PluginPresenter defines the interface for presenting plugin responses
type PluginPresenter interface {
	PresentPluginRegistered(w http.ResponseWriter, output *plugin.RegisterPluginOutput)
	PresentPluginActivated(w http.ResponseWriter, output *plugin.ActivatePluginOutput)
	PresentBadRequest(w http.ResponseWriter, message string)
	PresentNotFound(w http.ResponseWriter, message string)
	PresentConflict(w http.ResponseWriter, message string)
	PresentInternalError(w http.ResponseWriter)
}