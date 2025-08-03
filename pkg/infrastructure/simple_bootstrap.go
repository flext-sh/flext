package http

import (
	"fmt"
	"net/http"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// SimpleBootstrapHandler - Interface web Bootstrap + HTMX simplificada
type SimpleBootstrapHandler struct {
	logger logging.Logger
}

func NewSimpleBootstrapHandler(logger logging.Logger) *SimpleBootstrapHandler {
	return &SimpleBootstrapHandler{logger: logger}
}

func (h *SimpleBootstrapHandler) RegisterRoutes(e *echo.Echo) {
	e.GET("/", h.Dashboard)
	e.GET("/web", h.Dashboard)
	e.GET("/components/stats", h.StatsCards)
	e.GET("/components/pipelines", h.PipelinesTable)
	e.POST("/api/pipeline/create", h.CreatePipeline)
}

// Dashboard - Página principal limpa
func (h *SimpleBootstrapHandler) Dashboard(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXT Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        .card-hover:hover { transform: translateY(-2px); transition: all 0.3s ease; }
        .htmx-indicator { display: none; }
        .htmx-request .htmx-indicator { display: inline; }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-gear-fill"></i> FLEXT
            </a>
            <div class="navbar-nav">
                <a class="nav-link active" href="/">Dashboard</a>
                <a class="nav-link" href="/pipelines">Pipelines</a>
                <a class="nav-link" href="/monitoring">Monitoring</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <h1 class="display-5 fw-bold text-primary mb-4">
            <i class="bi bi-speedometer2"></i> FLEXT Dashboard
        </h1>

        <!-- Stats Cards -->
        <div hx-get="/components/stats" hx-trigger="load, every 15s" hx-swap="innerHTML">
            <div class="text-center p-4">
                <div class="spinner-border text-primary"></div>
                <p>Loading stats...</p>
            </div>
        </div>

        <!-- Pipelines -->
        <div class="row mt-4">
            <div class="col-lg-8">
                <div class="card card-hover">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="bi bi-diagram-3"></i> Pipelines</h5>
                        <button class="btn btn-primary btn-sm"
                                hx-post="/api/pipeline/create"
                                hx-target="#pipelines-container">
                            <i class="bi bi-plus"></i> Create
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="pipelines-container"
                             hx-get="/components/pipelines"
                             hx-trigger="load, every 30s">
                            <div class="text-center p-3">
                                <div class="spinner-border text-primary"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card card-hover">
                    <div class="card-header">
                        <h5><i class="bi bi-activity"></i> System Status</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <i class="bi bi-check-circle"></i> All systems operational
                        </div>
                        <div class="d-grid">
                            <button class="btn btn-outline-primary">View Details</button>
                        </div>
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

// StatsCards - Componente de estatísticas
func (h *SimpleBootstrapHandler) StatsCards(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary card-hover">
            <div class="card-body text-center">
                <h2>3</h2>
                <p class="mb-0">Pipelines</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success card-hover">
            <div class="card-body text-center">
                <h2>8</h2>
                <p class="mb-0">Plugins</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning card-hover">
            <div class="card-body text-center">
                <h2>2</h2>
                <p class="mb-0">Active Jobs</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info card-hover">
            <div class="card-body text-center">
                <h4>Healthy</h4>
                <p class="mb-0">System</p>
            </div>
        </div>
    </div>
</div>
`)
}

// PipelinesTable - Tabela de pipelines
func (h *SimpleBootstrapHandler) PipelinesTable(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>ETL Pipeline</td>
                <td><span class="badge bg-success">Running</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                    <button class="btn btn-sm btn-outline-danger">Stop</button>
                </td>
            </tr>
            <tr>
                <td>2</td>
                <td>Data Sync</td>
                <td><span class="badge bg-secondary">Stopped</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                    <button class="btn btn-sm btn-outline-success">Start</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
`)
}

// CreatePipeline - Ação para criar pipeline
func (h *SimpleBootstrapHandler) CreatePipeline(c echo.Context) error {
	h.logger.Info("Creating pipeline via HTMX")
	return c.HTML(http.StatusOK, fmt.Sprintf(`
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr class="table-success">
                <td>%d</td>
                <td>New Pipeline</td>
                <td><span class="badge bg-success">Created</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                    <button class="btn btn-sm btn-outline-success">Start</button>
                </td>
            </tr>
            <tr>
                <td>1</td>
                <td>ETL Pipeline</td>
                <td><span class="badge bg-success">Running</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                    <button class="btn btn-sm btn-outline-danger">Stop</button>
                </td>
            </tr>
            <tr>
                <td>2</td>
                <td>Data Sync</td>
                <td><span class="badge bg-secondary">Stopped</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                    <button class="btn btn-sm btn-outline-success">Start</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
`, 100+len("new")))
}
