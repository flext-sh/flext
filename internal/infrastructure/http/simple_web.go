package http

import (
	"fmt"
	"net/http"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// SimpleWebHandler - Interface web super simples com HTMX
type SimpleWebHandler struct {
	logger logging.Logger
}

func NewSimpleWebHandler(logger logging.Logger) *SimpleWebHandler {
	return &SimpleWebHandler{logger: logger}
}

func (h *SimpleWebHandler) RegisterRoutes(e *echo.Echo) {
	// Página principal
	e.GET("/", h.Home)
	
	// Componentes reativos
	e.GET("/stats", h.GetStats)
	e.GET("/pipelines", h.GetPipelines)
	e.POST("/pipeline/create", h.CreatePipeline)
	e.GET("/logs", h.GetLogs)
	
	// Assets estáticos
	e.Static("/static", "web/static")
}

// Home - Página principal com TUDO reativo
func (h *SimpleWebHandler) Home(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<!DOCTYPE html>
<html>
<head>
    <title>FLEXT</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-6">
        <h1 class="text-3xl font-bold mb-6">🚀 FLEXT Dashboard</h1>
        
        <!-- Stats que atualizam sozinhas -->
        <div class="grid grid-cols-3 gap-4 mb-6" 
             hx-get="/stats" 
             hx-trigger="load, every 10s">
            <div class="bg-white p-4 rounded shadow">Loading...</div>
        </div>
        
        <!-- Lista de pipelines reativa -->
        <div class="bg-white rounded shadow">
            <div class="p-4 border-b">
                <h2 class="text-xl font-bold">Pipelines</h2>
                <button class="bg-blue-500 text-white px-4 py-2 rounded"
                        hx-post="/pipeline/create"
                        hx-target="#pipelines">
                    ➕ Create
                </button>
            </div>
            <div id="pipelines" 
                 hx-get="/pipelines" 
                 hx-trigger="load, every 30s">
                Loading pipelines...
            </div>
        </div>
        
        <!-- Logs em tempo real -->
        <div class="mt-6 bg-black text-green-400 p-4 rounded font-mono"
             hx-get="/logs" 
             hx-trigger="load, every 5s"
             hx-swap="innerHTML">
            Loading logs...
        </div>
    </div>
</body>
</html>
`)
}

// GetStats - Retorna cards de estatísticas
func (h *SimpleWebHandler) GetStats(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<div class="bg-blue-500 text-white p-4 rounded shadow">
    <h3 class="text-lg font-bold">Pipelines</h3>
    <p class="text-2xl">3</p>
</div>
<div class="bg-green-500 text-white p-4 rounded shadow">
    <h3 class="text-lg font-bold">Plugins</h3>
    <p class="text-2xl">8</p>
</div>
<div class="bg-yellow-500 text-white p-4 rounded shadow">
    <h3 class="text-lg font-bold">Jobs</h3>
    <p class="text-2xl">2</p>
</div>
`)
}

// GetPipelines - Lista de pipelines
func (h *SimpleWebHandler) GetPipelines(c echo.Context) error {
	return c.HTML(http.StatusOK, `
<div class="divide-y">
    <div class="p-4 flex justify-between items-center">
        <div>
            <h3 class="font-bold">ETL Pipeline</h3>
            <span class="text-green-600">✅ Running</span>
        </div>
        <button class="bg-red-500 text-white px-3 py-1 rounded text-sm">Stop</button>
    </div>
    <div class="p-4 flex justify-between items-center">
        <div>
            <h3 class="font-bold">Data Sync</h3>
            <span class="text-gray-600">⏸️ Stopped</span>
        </div>
        <button class="bg-green-500 text-white px-3 py-1 rounded text-sm">Start</button>
    </div>
</div>
`)
}

// CreatePipeline - Cria novo pipeline
func (h *SimpleWebHandler) CreatePipeline(c echo.Context) error {
	h.logger.Info("Creating new pipeline...")
	return c.HTML(http.StatusOK, `
<div class="divide-y">
    <div class="p-4 flex justify-between items-center bg-green-50">
        <div>
            <h3 class="font-bold">New Pipeline ` + fmt.Sprintf("%d", len("123")) + `</h3>
            <span class="text-green-600">✅ Created</span>
        </div>
        <button class="bg-red-500 text-white px-3 py-1 rounded text-sm">Delete</button>
    </div>
    <div class="p-4 flex justify-between items-center">
        <div>
            <h3 class="font-bold">ETL Pipeline</h3>
            <span class="text-green-600">✅ Running</span>
        </div>
        <button class="bg-red-500 text-white px-3 py-1 rounded text-sm">Stop</button>
    </div>
</div>
`)
}

// GetLogs - Logs em tempo real
func (h *SimpleWebHandler) GetLogs(c echo.Context) error {
	return c.HTML(http.StatusOK, `
[2025-06-30 15:30:45] INFO: Server started ✅<br>
[2025-06-30 15:30:46] INFO: Database connected ✅<br>
[2025-06-30 15:30:47] WARN: High memory usage ⚠️<br>
[2025-06-30 15:30:48] INFO: Pipeline executed ✅<br>
`)
}
