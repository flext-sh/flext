package http

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
)

// CreatePipeline - Ação para criar pipeline
func (h *BootstrapWebHandler) CreatePipeline(c echo.Context) error {
	h.logger.Info("Creating new pipeline via HTMX")
	
	// Simular criação de pipeline
	newPipelineID := time.Now().Unix()
	newPipelineName := fmt.Sprintf("Pipeline-%d", newPipelineID)
	
	// Retornar tabela atualizada com novo pipeline
	pipelines := []map[string]interface{}{
		{"id": newPipelineID, "name": newPipelineName, "status": "created", "steps": 1, "created": time.Now().Format("2006-01-02")},
		{"id": 1, "name": "ETL Data Pipeline", "status": "running", "steps": 4, "created": "2025-06-30"},
		{"id": 2, "name": "Log Processing", "status": "stopped", "steps": 3, "created": "2025-06-29"},
		{"id": 3, "name": "Analytics Pipeline", "status": "completed", "steps": 5, "created": "2025-06-28"},
	}

	html := `<div class="table-responsive">
<table class="table table-hover align-middle">
    <thead class="table-light">
        <tr>
            <th><i class="bi bi-hash"></i> ID</th>
            <th><i class="bi bi-diagram-3"></i> Name</th>
            <th><i class="bi bi-circle-fill"></i> Status</th>
            <th><i class="bi bi-list-ol"></i> Steps</th>
            <th><i class="bi bi-calendar"></i> Created</th>
            <th><i class="bi bi-gear"></i> Actions</th>
        </tr>
    </thead>
    <tbody>`

	for _, pipeline := range pipelines {
		statusBadge := ""
		rowClass := ""
		switch pipeline["status"] {
		case "running":
			statusBadge = `<span class="badge bg-success"><i class="bi bi-play-fill"></i> Running</span>`
		case "stopped":
			statusBadge = `<span class="badge bg-secondary"><i class="bi bi-stop-fill"></i> Stopped</span>`
		case "completed":
			statusBadge = `<span class="badge bg-primary"><i class="bi bi-check-circle-fill"></i> Completed</span>`
		case "created":
			statusBadge = `<span class="badge bg-success"><i class="bi bi-plus-circle-fill"></i> Created</span>`
			rowClass = `class="table-success"`
		}

		html += fmt.Sprintf(`
        <tr %s>
            <td><strong>%v</strong></td>
            <td>%s</td>
            <td>%s</td>
            <td><span class="badge bg-light text-dark">%v</span></td>
            <td><small class="text-muted">%s</small></td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" data-bs-toggle="tooltip" title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-success"
                            hx-post="/api/pipeline/%v/execute"
                            hx-target="#pipelines-container"
                            data-bs-toggle="tooltip" title="Execute">
                        <i class="bi bi-play"></i>
                    </button>
                    <button class="btn btn-outline-danger"
                            hx-delete="/api/pipeline/%v"
                            hx-target="#pipelines-container"
                            hx-confirm="Are you sure?"
                            data-bs-toggle="tooltip" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>`,
			rowClass, pipeline["id"], pipeline["name"], statusBadge, pipeline["steps"], 
			pipeline["created"], pipeline["id"], pipeline["id"])
	}

	html += `
    </tbody>
</table>
</div>`

	return c.HTML(http.StatusOK, html)
}

// ExecutePipeline - Ação para executar pipeline
func (h *BootstrapWebHandler) ExecutePipeline(c echo.Context) error {
	pipelineID := c.Param("id")
	h.logger.Info(fmt.Sprintf("Executing pipeline %s via HTMX", pipelineID))
	
	// Simular execução
	pipelines := []map[string]interface{}{
		{"id": 1, "name": "ETL Data Pipeline", "status": "running", "steps": 4, "created": "2025-06-30"},
		{"id": 2, "name": "Log Processing", "status": "running", "steps": 3, "created": "2025-06-29"},
		{"id": 3, "name": "Analytics Pipeline", "status": "completed", "steps": 5, "created": "2025-06-28"},
	}

	// Atualizar status do pipeline executado
	executedID, _ := strconv.Atoi(pipelineID)
	for i, pipeline := range pipelines {
		if pipeline["id"] == executedID {
			pipelines[i]["status"] = "running"
			break
		}
	}

	html := `<div class="table-responsive">
<table class="table table-hover align-middle">
    <thead class="table-light">
        <tr>
            <th><i class="bi bi-hash"></i> ID</th>
            <th><i class="bi bi-diagram-3"></i> Name</th>
            <th><i class="bi bi-circle-fill"></i> Status</th>
            <th><i class="bi bi-list-ol"></i> Steps</th>
            <th><i class="bi bi-calendar"></i> Created</th>
            <th><i class="bi bi-gear"></i> Actions</th>
        </tr>
    </thead>
    <tbody>`

	for _, pipeline := range pipelines {
		statusBadge := ""
		rowClass := ""
		switch pipeline["status"] {
		case "running":
			statusBadge = `<span class="badge bg-success"><i class="bi bi-play-fill"></i> Running</span>`
			if pipeline["id"] == executedID {
				rowClass = `class="table-warning"`
			}
		case "stopped":
			statusBadge = `<span class="badge bg-secondary"><i class="bi bi-stop-fill"></i> Stopped</span>`
		case "completed":
			statusBadge = `<span class="badge bg-primary"><i class="bi bi-check-circle-fill"></i> Completed</span>`
		}

		html += fmt.Sprintf(`
        <tr %s>
            <td><strong>%v</strong></td>
            <td>%s</td>
            <td>%s</td>
            <td><span class="badge bg-light text-dark">%v</span></td>
            <td><small class="text-muted">%s</small></td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" data-bs-toggle="tooltip" title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-success"
                            hx-post="/api/pipeline/%v/execute"
                            hx-target="#pipelines-container"
                            data-bs-toggle="tooltip" title="Execute">
                        <i class="bi bi-play"></i>
                    </button>
                    <button class="btn btn-outline-danger"
                            hx-delete="/api/pipeline/%v"
                            hx-target="#pipelines-container"
                            hx-confirm="Are you sure?"
                            data-bs-toggle="tooltip" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>`,
			rowClass, pipeline["id"], pipeline["name"], statusBadge, pipeline["steps"], 
			pipeline["created"], pipeline["id"], pipeline["id"])
	}

	html += `
    </tbody>
</table>
</div>`

	return c.HTML(http.StatusOK, html)
}

// DeletePipeline - Ação para deletar pipeline
func (h *BootstrapWebHandler) DeletePipeline(c echo.Context) error {
	pipelineID := c.Param("id")
	h.logger.Info(fmt.Sprintf("Deleting pipeline %s via HTMX", pipelineID))
	
	// Simular exclusão
	pipelines := []map[string]interface{}{
		{"id": 1, "name": "ETL Data Pipeline", "status": "running", "steps": 4, "created": "2025-06-30"},
		{"id": 2, "name": "Log Processing", "status": "stopped", "steps": 3, "created": "2025-06-29"},
		{"id": 3, "name": "Analytics Pipeline", "status": "completed", "steps": 5, "created": "2025-06-28"},
	}

	// Remover pipeline deletado
	deletedID, _ := strconv.Atoi(pipelineID)
	filteredPipelines := []map[string]interface{}{}
	for _, pipeline := range pipelines {
		if pipeline["id"] != deletedID {
			filteredPipelines = append(filteredPipelines, pipeline)
		}
	}

	html := `<div class="table-responsive">
<table class="table table-hover align-middle">
    <thead class="table-light">
        <tr>
            <th><i class="bi bi-hash"></i> ID</th>
            <th><i class="bi bi-diagram-3"></i> Name</th>
            <th><i class="bi bi-circle-fill"></i> Status</th>
            <th><i class="bi bi-list-ol"></i> Steps</th>
            <th><i class="bi bi-calendar"></i> Created</th>
            <th><i class="bi bi-gear"></i> Actions</th>
        </tr>
    </thead>
    <tbody>`

	for _, pipeline := range filteredPipelines {
		statusBadge := ""
		switch pipeline["status"] {
		case "running":
			statusBadge = `<span class="badge bg-success"><i class="bi bi-play-fill"></i> Running</span>`
		case "stopped":
			statusBadge = `<span class="badge bg-secondary"><i class="bi bi-stop-fill"></i> Stopped</span>`
		case "completed":
			statusBadge = `<span class="badge bg-primary"><i class="bi bi-check-circle-fill"></i> Completed</span>`
		}

		html += fmt.Sprintf(`
        <tr>
            <td><strong>%v</strong></td>
            <td>%s</td>
            <td>%s</td>
            <td><span class="badge bg-light text-dark">%v</span></td>
            <td><small class="text-muted">%s</small></td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" data-bs-toggle="tooltip" title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-success"
                            hx-post="/api/pipeline/%v/execute"
                            hx-target="#pipelines-container"
                            data-bs-toggle="tooltip" title="Execute">
                        <i class="bi bi-play"></i>
                    </button>
                    <button class="btn btn-outline-danger"
                            hx-delete="/api/pipeline/%v"
                            hx-target="#pipelines-container"
                            hx-confirm="Are you sure?"
                            data-bs-toggle="tooltip" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>`,
			pipeline["id"], pipeline["name"], statusBadge, pipeline["steps"], 
			pipeline["created"], pipeline["id"], pipeline["id"])
	}

	if len(filteredPipelines) == 0 {
		html += `
        <tr>
            <td colspan="6" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                No pipelines found. Create one to get started!
            </td>
        </tr>`
	}

	html += `
    </tbody>
</table>
</div>`

	return c.HTML(http.StatusOK, html)
}

// RegisterPlugin - Ação para registrar plugin
func (h *BootstrapWebHandler) RegisterPlugin(c echo.Context) error {
	h.logger.Info("Registering new plugin via HTMX")
	
	// Simular registro de plugin - retorna nova atividade
	newActivity := fmt.Sprintf("Plugin 'New-Plugin-%d' registered", time.Now().Unix())
	
	activities := []map[string]interface{}{
		{"time": "Just now", "action": newActivity, "type": "success", "icon": "bi-plugin"},
		{"time": "2 min ago", "action": "Pipeline 'ETL Data' completed", "type": "success", "icon": "bi-check-circle-fill"},
		{"time": "5 min ago", "action": "Plugin 'Oracle Connector' registered", "type": "info", "icon": "bi-plugin"},
		{"time": "8 min ago", "action": "Pipeline 'Log Processing' started", "type": "primary", "icon": "bi-play-circle-fill"},
		{"time": "12 min ago", "action": "System health check passed", "type": "success", "icon": "bi-shield-check"},
	}

	html := `<div class="activity-feed">`

	for i, activity := range activities {
		rowClass := ""
		if i == 0 {
			rowClass = `style="background-color: #d1edff; border-left: 4px solid #0d6efd;"`
		}

		html += fmt.Sprintf(`
        <div class="d-flex align-items-start mb-3 p-2 rounded hover-bg-light" %s>
            <div class="flex-shrink-0 me-3">
                <span class="badge bg-%s rounded-pill p-2">
                    <i class="%s"></i>
                </span>
            </div>
            <div class="flex-grow-1">
                <p class="mb-1 fw-medium">%s</p>
                <small class="text-muted">
                    <i class="bi bi-clock"></i> %s
                </small>
            </div>
        </div>`,
			rowClass, activity["type"], activity["icon"], activity["action"], activity["time"])
	}

	html += `</div>`
	return c.HTML(http.StatusOK, html)
}

// RunDiagnostics - Ação para executar diagnósticos
func (h *BootstrapWebHandler) RunDiagnostics(c echo.Context) error {
	h.logger.Info("Running system diagnostics via HTMX")
	
	// Simular diagnósticos - retorna nova atividade
	diagnosticsResult := "System diagnostics completed - All systems operational"
	
	activities := []map[string]interface{}{
		{"time": "Just now", "action": diagnosticsResult, "type": "success", "icon": "bi-shield-check"},
		{"time": "2 min ago", "action": "Pipeline 'ETL Data' completed", "type": "success", "icon": "bi-check-circle-fill"},
		{"time": "5 min ago", "action": "Plugin 'Oracle Connector' registered", "type": "info", "icon": "bi-plugin"},
		{"time": "8 min ago", "action": "Pipeline 'Log Processing' started", "type": "primary", "icon": "bi-play-circle-fill"},
		{"time": "12 min ago", "action": "System health check passed", "type": "success", "icon": "bi-shield-check"},
	}

	html := `<div class="activity-feed">`

	for i, activity := range activities {
		rowClass := ""
		if i == 0 {
			rowClass = `style="background-color: #d1f2eb; border-left: 4px solid #198754;"`
		}

		html += fmt.Sprintf(`
        <div class="d-flex align-items-start mb-3 p-2 rounded hover-bg-light" %s>
            <div class="flex-shrink-0 me-3">
                <span class="badge bg-%s rounded-pill p-2">
                    <i class="%s"></i>
                </span>
            </div>
            <div class="flex-grow-1">
                <p class="mb-1 fw-medium">%s</p>
                <small class="text-muted">
                    <i class="bi bi-clock"></i> %s
                </small>
            </div>
        </div>`,
			rowClass, activity["type"], activity["icon"], activity["action"], activity["time"])
	}

	html += `</div>`
	return c.HTML(http.StatusOK, html)
}

// PipelinesPage - Página dedicada de pipelines
func (h *BootstrapWebHandler) PipelinesPage(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipelines - FLEXT</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body class="bg-light">
    <div class="container mt-4">
        <h1><i class="bi bi-diagram-3"></i> Pipelines Management</h1>
        <p class="text-muted">Manage and monitor your data pipelines</p>
        
        <div class="card" hx-get="/components/pipelines" hx-trigger="load">
            <div class="card-body text-center">
                <div class="spinner-border" role="status"></div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
`)
}

// PluginsPage - Página dedicada de plugins
func (h *BootstrapWebHandler) PluginsPage(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plugins - FLEXT</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body class="bg-light">
    <div class="container mt-4">
        <h1><i class="bi bi-plugin"></i> Plugins Registry</h1>
        <p class="text-muted">Manage your framework plugins and extensions</p>
        
        <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> Plugins page coming soon!
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
`)
}

// MonitoringPage - Página dedicada de monitoramento
func (h *BootstrapWebHandler) MonitoringPage(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoring - FLEXT</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body class="bg-light">
    <div class="container mt-4">
        <h1><i class="bi bi-graph-up"></i> System Monitoring</h1>
        <p class="text-muted">Real-time system performance and health monitoring</p>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">System Metrics</div>
                    <div class="card-body" hx-get="/components/metrics" hx-trigger="load, every 5s">
                        <div class="text-center"><div class="spinner-border" role="status"></div></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">System Logs</div>
                    <div class="card-body" hx-get="/components/logs" hx-trigger="load, every 10s">
                        <div class="text-center"><div class="spinner-border" role="status"></div></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
`)
}
