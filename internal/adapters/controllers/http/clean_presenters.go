package http

import (
	"encoding/json"
	"net/http"
)

// CleanPipelinePresenter implements all PipelinePresenter methods for Clean Architecture
type CleanPipelinePresenter struct{}

func NewCleanPipelinePresenter() *CleanPipelinePresenter {
	return &CleanPipelinePresenter{}
}

func (p *CleanPipelinePresenter) PresentSuccess(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
	})
}

func (p *CleanPipelinePresenter) PresentCreated(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
	})
}

func (p *CleanPipelinePresenter) PresentBadRequest(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPipelinePresenter) PresentNotFound(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNotFound)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPipelinePresenter) PresentInternalError(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPipelinePresenter) PresentConflict(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusConflict)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPipelinePresenter) PresentPipelineCreated(w http.ResponseWriter, data interface{}) {
	p.PresentCreated(w, data)
}

func (p *CleanPipelinePresenter) PresentPipeline(w http.ResponseWriter, data interface{}) {
	p.PresentSuccess(w, data)
}

func (p *CleanPipelinePresenter) PresentPipelineList(w http.ResponseWriter, data interface{}) {
	p.PresentSuccess(w, data)
}

func (p *CleanPipelinePresenter) PresentStepAdded(w http.ResponseWriter, data interface{}) {
	p.PresentCreated(w, data)
}

func (p *CleanPipelinePresenter) PresentExecutionStarted(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
		"status":  "execution_started",
	})
}

// CleanPluginPresenter implements all PluginPresenter methods for Clean Architecture
type CleanPluginPresenter struct{}

func NewCleanPluginPresenter() *CleanPluginPresenter {
	return &CleanPluginPresenter{}
}

func (p *CleanPluginPresenter) PresentSuccess(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
	})
}

func (p *CleanPluginPresenter) PresentCreated(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"data":    data,
	})
}

func (p *CleanPluginPresenter) PresentBadRequest(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPluginPresenter) PresentNotFound(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusNotFound)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPluginPresenter) PresentInternalError(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPluginPresenter) PresentConflict(w http.ResponseWriter, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusConflict)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": false,
		"error":   message,
	})
}

func (p *CleanPluginPresenter) PresentPluginRegistered(w http.ResponseWriter, data interface{}) {
	p.PresentCreated(w, data)
}

func (p *CleanPluginPresenter) PresentPlugin(w http.ResponseWriter, data interface{}) {
	p.PresentSuccess(w, data)
}

func (p *CleanPluginPresenter) PresentPluginList(w http.ResponseWriter, data interface{}) {
	p.PresentSuccess(w, data)
}

func (p *CleanPluginPresenter) PresentPluginActivated(w http.ResponseWriter, data interface{}) {
	p.PresentSuccess(w, data)
}