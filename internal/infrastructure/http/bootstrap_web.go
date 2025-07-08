package http

import (
	"net/http"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// BootstrapWebHandler - Interface web com Bootstrap + HTMX
type BootstrapWebHandler struct {
	logger logging.Logger
}

func NewBootstrapWebHandler(logger logging.Logger) *BootstrapWebHandler {
	return &BootstrapWebHandler{logger: logger}
}

func (h *BootstrapWebHandler) RegisterRoutes(e *echo.Echo) {
	// Página principal
	e.GET("/", h.Dashboard)
	e.GET("/web", h.Dashboard)

	// Componentes HTMX
	e.GET("/components/stats", h.StatsCards)
	e.GET("/components/pipelines", h.PipelinesTable)
	e.GET("/components/activity", h.RecentActivity)
	e.GET("/components/logs", h.SystemLogs)
	e.GET("/components/metrics", h.SystemMetrics)

	// Ações
	e.POST("/api/pipeline/create", h.CreatePipeline)
	e.POST("/api/pipeline/:id/execute", h.ExecutePipeline)
	e.DELETE("/api/pipeline/:id", h.DeletePipeline)
	e.POST("/api/plugin/register", h.RegisterPlugin)
	e.GET("/api/diagnostics", h.RunDiagnostics)

	// Páginas específicas
	e.GET("/pipelines", h.PipelinesPage)
	e.GET("/plugins", h.PluginsPage)
	e.GET("/monitoring", h.MonitoringPage)
}

// Dashboard - Página principal com Bootstrap + HTMX
func (h *BootstrapWebHandler) Dashboard(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXT - Framework Dashboard</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">

    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    <!-- Custom HTMX + Bootstrap styles -->
    <style>
        .htmx-indicator { display: none; }
        .htmx-request .htmx-indicator { display: inline; }
        .htmx-request.htmx-indicator { display: inline; }
        .fade-me-in {
            opacity: 0;
            transition: opacity 1s ease-in;
        }
        .fade-me-out {
            opacity: 1;
            transition: opacity 1s ease-out;
        }
        .card-hover:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-gear-fill"></i> FLEXT
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/"><i class="bi bi-speedometer2"></i> Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pipelines"><i class="bi bi-diagram-3"></i> Pipelines</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/plugins"><i class="bi bi-plugin"></i> Plugins</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/monitoring"><i class="bi bi-graph-up"></i> Monitoring</a>
                    </li>
                </ul>
                <span class="navbar-text">
                    <span class="badge bg-success pulse"
                          hx-get="/health"
                          hx-trigger="every 30s"
                          hx-swap="innerHTML">Healthy</span>
                </span>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col">
                <h1 class="display-5 fw-bold text-primary">
                    <i class="bi bi-speedometer2"></i> FLEXT Dashboard
                </h1>
                <p class="lead text-muted">Real-time framework management and monitoring</p>
            </div>
        </div>

        <!-- Stats Cards -->
        <div id="stats-container"
             hx-get="/components/stats"
             hx-trigger="load, every 15s"
             hx-swap="innerHTML"
             hx-indicator="#stats-loading">
            <div id="stats-loading" class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading stats...</span>
                </div>
            </div>
        </div>

        <!-- Main Content Grid -->
        <div class="row mt-4">
            <!-- Pipelines -->
            <div class="col-lg-8">
                <div class="card card-hover h-100">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-diagram-3 text-primary"></i> Pipelines
                            </h5>
                            <button class="btn btn-primary btn-sm"
                                    hx-post="/api/pipeline/create"
                                    hx-target="#pipelines-container"
                                    hx-indicator="#create-pipeline-spinner">
                                <span id="create-pipeline-spinner" class="spinner-border spinner-border-sm htmx-indicator" role="status"></span>
                                <i class="bi bi-plus-lg"></i> Create
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="pipelines-container"
                             hx-get="/components/pipelines"
                             hx-trigger="load, every 30s"
                             hx-swap="innerHTML">
                            <div class="text-center p-3">
                                <div class="spinner-border text-primary" role="status"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Activity Feed -->
            <div class="col-lg-4">
                <div class="card card-hover h-100">
                    <div class="card-header bg-white">
                        <h5 class="card-title mb-0">
                            <i class="bi bi-activity text-success"></i> Recent Activity
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="activity-container"
                             hx-get="/components/activity"
                             hx-trigger="load, every 10s"
                             hx-swap="innerHTML"
                             style="max-height: 300px; overflow-y: auto;">
                            <div class="text-center p-3">
                                <div class="spinner-border text-success" role="status"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- System Monitoring -->
        <div class="row mt-4">
            <!-- System Metrics -->
            <div class="col-lg-6">
                <div class="card card-hover">
                    <div class="card-header bg-white">
                        <h5 class="card-title mb-0">
                            <i class="bi bi-cpu text-warning"></i> System Metrics
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="metrics-container"
                             hx-get="/components/metrics"
                             hx-trigger="load, every 5s"
                             hx-swap="innerHTML">
                            <div class="text-center p-3">
                                <div class="spinner-border text-warning" role="status"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Logs -->
            <div class="col-lg-6">
                <div class="card card-hover">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-journal-text text-info"></i> System Logs
                            </h5>
                            <button class="btn btn-outline-secondary btn-sm"
                                    hx-get="/components/logs"
                                    hx-target="#logs-container">
                                <i class="bi bi-arrow-clockwise"></i> Refresh
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="logs-container"
                             hx-get="/components/logs"
                             hx-trigger="load, every 10s"
                             hx-swap="innerHTML"
                             style="max-height: 250px; overflow-y: auto;">
                            <div class="text-center p-3">
                                <div class="spinner-border text-info" role="status"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="row mt-4">
            <div class="col">
                <div class="card card-hover">
                    <div class="card-header bg-white">
                        <h5 class="card-title mb-0">
                            <i class="bi bi-lightning text-warning"></i> Quick Actions
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-2">
                            <div class="col-md-3">
                                <button class="btn btn-primary w-100"
                                        hx-post="/api/pipeline/create"
                                        hx-target="#pipelines-container">
                                    <i class="bi bi-plus-circle"></i> Create Pipeline
                                </button>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-success w-100"
                                        hx-post="/api/plugin/register"
                                        hx-target="#activity-container">
                                    <i class="bi bi-plugin"></i> Register Plugin
                                </button>
                            </div>
                            <div class="col-md-3">
                                <a href="/monitoring" class="btn btn-info w-100">
                                    <i class="bi bi-graph-up"></i> View Monitoring
                                </a>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-warning w-100"
                                        hx-get="/api/diagnostics"
                                        hx-target="#activity-container"
                                        hx-indicator="#diagnostics-spinner">
                                    <span id="diagnostics-spinner" class="spinner-border spinner-border-sm htmx-indicator" role="status"></span>
                                    <i class="bi bi-shield-check"></i> Diagnostics
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- HTMX Extensions and Config -->
    <script>
        // HTMX configuration
        htmx.config.globalViewTransitions = true;

        // Add fade transitions
        document.body.addEventListener('htmx:beforeSwap', function(evt) {
            if (evt.target.id === 'stats-container' ||
                evt.target.id === 'pipelines-container' ||
                evt.target.id === 'activity-container') {
                evt.target.classList.add('fade-me-out');
            }
        });

        document.body.addEventListener('htmx:afterSwap', function(evt) {
            if (evt.target.id === 'stats-container' ||
                evt.target.id === 'pipelines-container' ||
                evt.target.id === 'activity-container') {
                evt.target.classList.remove('fade-me-out');
                evt.target.classList.add('fade-me-in');
            }
        });

        // Toast notifications for actions
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            if (evt.detail.xhr.status >= 200 && evt.detail.xhr.status < 300) {
                if (evt.detail.requestConfig.verb === 'post') {
                    showToast('Action completed successfully!', 'success');
                }
            } else {
                showToast('Action failed. Please try again.', 'danger');
            }
        });

        function showToast(message, type) {
            const toastHtml = '<div class="toast align-items-center text-bg-' + type + ' border-0" role="alert">' +
                '<div class="d-flex">' +
                '<div class="toast-body">' + message + '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
                '</div></div>';

            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                toastContainer.style.zIndex = '1055';
                document.body.appendChild(toastContainer);
            }

            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const newToast = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(newToast);
            toast.show();

            newToast.addEventListener('hidden.bs.toast', function() {
                newToast.remove();
            });
        }
    </script>
</body>
</html>
`)
}
