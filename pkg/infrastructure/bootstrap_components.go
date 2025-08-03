package http

import (
	"fmt"
	"math/rand"
	"net/http"

	"github.com/labstack/echo/v4"
)

// StatsCards - Componente de cards de estatísticas
func (h *BootstrapWebHandler) StatsCards(c echo.Context) error {
	// Simular dados dinâmicos
	pipelineCount := rand.Intn(10) + 1
	pluginCount := rand.Intn(20) + 5
	activeJobs := rand.Intn(5)
	systemHealth := "Healthy"

	if rand.Float32() < 0.1 {
		systemHealth = "Warning"
	}

	return c.HTML(http.StatusOK, fmt.Sprintf(`
<div class="row g-3">
    <div class="col-md-3">
        <div class="card text-white bg-primary card-hover h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">Pipelines</h6>
                        <h2 class="mb-0">%d</h2>
                    </div>
                    <div class="fs-1 opacity-75">
                        <i class="bi bi-diagram-3"></i>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="opacity-75">
                        <i class="bi bi-arrow-up"></i> +2 this week
                    </small>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success card-hover h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">Plugins</h6>
                        <h2 class="mb-0">%d</h2>
                    </div>
                    <div class="fs-1 opacity-75">
                        <i class="bi bi-plugin"></i>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="opacity-75">
                        <i class="bi bi-arrow-up"></i> +5 this month
                    </small>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning card-hover h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">Active Jobs</h6>
                        <h2 class="mb-0">%d</h2>
                    </div>
                    <div class="fs-1 opacity-75">
                        <i class="bi bi-gear-fill %s"></i>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="opacity-75">
                        <i class="bi bi-clock"></i> Real-time
                    </small>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white %s card-hover h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-1">System</h6>
                        <h4 class="mb-0">%s</h4>
                    </div>
                    <div class="fs-1 opacity-75">
                        <i class="bi bi-shield-check"></i>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="opacity-75">
                        <i class="bi bi-arrow-clockwise"></i> Auto-check
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
`,
		pipelineCount,
		pluginCount,
		activeJobs,
		map[bool]string{true: "rotate-animation", false: ""}[activeJobs > 0],
		map[string]string{"Healthy": "bg-info", "Warning": "bg-danger"}[systemHealth],
		systemHealth,
	))
}

// PipelinesTable - Tabela de pipelines
func (h *BootstrapWebHandler) PipelinesTable(c echo.Context) error {
	pipelines := []map[string]interface{}{
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
            <td><strong>%d</strong></td>
            <td>%s</td>
            <td>%s</td>
            <td><span class="badge bg-light text-dark">%d</span></td>
            <td><small class="text-muted">%s</small></td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary"
                            hx-get="/pipeline/%d"
                            hx-target="#main-content"
                            data-bs-toggle="tooltip"
                            title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-success"
                            hx-post="/api/pipeline/%d/execute"
                            hx-target="#pipelines-container"
                            data-bs-toggle="tooltip"
                            title="Execute">
                        <i class="bi bi-play"></i>
                    </button>
                    <button class="btn btn-outline-danger"
                            hx-delete="/api/pipeline/%d"
                            hx-target="#pipelines-container"
                            hx-confirm="Are you sure you want to delete this pipeline?"
                            data-bs-toggle="tooltip"
                            title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>`,
			pipeline["id"], pipeline["name"], statusBadge, pipeline["steps"],
			pipeline["created"], pipeline["id"], pipeline["id"], pipeline["id"])
	}

	html += `
    </tbody>
</table>
</div>`

	return c.HTML(http.StatusOK, html)
}

// RecentActivity - Feed de atividade recente
func (h *BootstrapWebHandler) RecentActivity(c echo.Context) error {
	activities := []map[string]interface{}{
		{"time": "2 min ago", "action": "Pipeline 'ETL Data' completed", "type": "success", "icon": "bi-check-circle-fill"},
		{"time": "5 min ago", "action": "Plugin 'Oracle Connector' registered", "type": "info", "icon": "bi-plugin"},
		{"time": "8 min ago", "action": "Pipeline 'Log Processing' started", "type": "primary", "icon": "bi-play-circle-fill"},
		{"time": "12 min ago", "action": "System health check passed", "type": "success", "icon": "bi-shield-check"},
		{"time": "15 min ago", "action": "New user logged in", "type": "info", "icon": "bi-person-check"},
	}

	html := `<div class="activity-feed">`

	for _, activity := range activities {
		html += fmt.Sprintf(`
        <div class="d-flex align-items-start mb-3 p-2 rounded hover-bg-light" style="transition: all 0.3s;">
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
			activity["type"], activity["icon"], activity["action"], activity["time"])
	}

	html += `</div>`
	return c.HTML(http.StatusOK, html)
}

// SystemMetrics - Métricas do sistema
func (h *BootstrapWebHandler) SystemMetrics(c echo.Context) error {
	cpuUsage := rand.Intn(100)
	memoryUsage := rand.Intn(100)
	diskUsage := rand.Intn(100)
	networkIO := rand.Intn(100)

	return c.HTML(http.StatusOK, fmt.Sprintf(`
<div class="row g-3">
    <div class="col-6">
        <div class="d-flex align-items-center">
            <i class="bi bi-cpu text-primary fs-4 me-2"></i>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between mb-1">
                    <small class="fw-medium">CPU Usage</small>
                    <small class="text-muted">%d%%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar %s" role="progressbar" style="width: %d%%"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-6">
        <div class="d-flex align-items-center">
            <i class="bi bi-memory text-success fs-4 me-2"></i>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between mb-1">
                    <small class="fw-medium">Memory</small>
                    <small class="text-muted">%d%%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-success %s" role="progressbar" style="width: %d%%"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-6">
        <div class="d-flex align-items-center">
            <i class="bi bi-hdd text-warning fs-4 me-2"></i>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between mb-1">
                    <small class="fw-medium">Disk</small>
                    <small class="text-muted">%d%%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-warning %s" role="progressbar" style="width: %d%%"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-6">
        <div class="d-flex align-items-center">
            <i class="bi bi-wifi text-info fs-4 me-2"></i>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between mb-1">
                    <small class="fw-medium">Network I/O</small>
                    <small class="text-muted">%d%%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-info" role="progressbar" style="width: %d%%"></div>
                </div>
            </div>
        </div>
    </div>
</div>
<div class="mt-3">
    <div class="alert alert-light border-0 mb-0">
        <div class="row text-center">
            <div class="col-3">
                <div class="fw-bold text-primary">2.4 GHz</div>
                <small class="text-muted">CPU Freq</small>
            </div>
            <div class="col-3">
                <div class="fw-bold text-success">8.0 GB</div>
                <small class="text-muted">Total RAM</small>
            </div>
            <div class="col-3">
                <div class="fw-bold text-warning">256 GB</div>
                <small class="text-muted">Disk Space</small>
            </div>
            <div class="col-3">
                <div class="fw-bold text-info">2d 14h</div>
                <small class="text-muted">Uptime</small>
            </div>
        </div>
    </div>
</div>
`,
		cpuUsage,
		map[bool]string{true: "bg-danger", false: "bg-primary"}[cpuUsage > 80],
		cpuUsage,
		memoryUsage,
		map[bool]string{true: "bg-danger", false: ""}[memoryUsage > 85],
		memoryUsage,
		diskUsage,
		map[bool]string{true: "bg-danger", false: ""}[diskUsage > 90],
		diskUsage,
		networkIO,
		networkIO,
	))
}

// SystemLogs - Logs do sistema
func (h *BootstrapWebHandler) SystemLogs(c echo.Context) error {
	logs := []map[string]string{
		{"time": "15:30:45", "level": "INFO", "message": "Server started successfully", "component": "API"},
		{"time": "15:30:46", "level": "INFO", "message": "Database connection established", "component": "DB"},
		{"time": "15:30:47", "level": "WARN", "message": "High memory usage detected", "component": "SYS"},
		{"time": "15:30:48", "level": "INFO", "message": "Pipeline executor initialized", "component": "EXEC"},
		{"time": "15:30:49", "level": "INFO", "message": "Web interface handler registered", "component": "WEB"},
	}

	html := `<div class="font-monospace small">`

	for _, log := range logs {
		badgeClass := ""
		switch log["level"] {
		case "INFO":
			badgeClass = "bg-primary"
		case "WARN":
			badgeClass = "bg-warning"
		case "ERROR":
			badgeClass = "bg-danger"
		default:
			badgeClass = "bg-secondary"
		}

		html += fmt.Sprintf(`
        <div class="d-flex align-items-center mb-2 p-2 border-start border-3 border-%s bg-light rounded-end">
            <span class="badge %s me-2">%s</span>
            <span class="text-muted me-2">[%s]</span>
            <span class="badge bg-light text-dark me-2">%s</span>
            <span>%s</span>
        </div>`,
			map[string]string{"INFO": "primary", "WARN": "warning", "ERROR": "danger"}[log["level"]],
			badgeClass, log["level"], log["time"], log["component"], log["message"])
	}

	html += `</div>`
	return c.HTML(http.StatusOK, html)
}
