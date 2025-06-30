package main

import (
	"log"
	"net/http"

	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// CustomValidator implementa a interface echo.Validator
type CustomValidator struct {
	validator *validator.Validate
}

func (cv *CustomValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}

func main() {
	// Inicializar container de dependências
	container := container.NewContainer()

	// Criar instância do Echo
	e := echo.New()

	// Configurar validator
	e.Validator = &CustomValidator{validator: validator.New()}

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORS())

	// Health check
	e.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"status":  "ok",
			"version": "1.0.0",
		})
	})

	// Registrar rotas dos handlers
	pipelineHandler := container.GetPipelineHandler()
	pipelineHandler.RegisterRoutes(e)

	pluginHandler := container.GetPluginHandler()
	pluginHandler.RegisterRoutes(e)

	// Documentação da API
	e.GET("/", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"name":        "FLEXT API",
			"description": "Unified Hexagonal Architecture + DDD Implementation",
			"version":     "1.0.0",
			"endpoints": map[string]interface{}{
				"health":    "GET /health",
				"pipelines": map[string]string{
					"create":    "POST /api/v1/pipelines",
					"get":       "GET /api/v1/pipelines/:id",
					"list":      "GET /api/v1/pipelines",
					"add_step":  "POST /api/v1/pipelines/:id/steps",
				},
				"plugins": map[string]string{
					"register": "POST /api/v1/plugins",
					"get":      "GET /api/v1/plugins/:id",
					"list":     "GET /api/v1/plugins",
				},
			},
		})
	})

	// Iniciar servidor
	log.Println("Starting FLEXT server on :8080")
	log.Fatal(e.Start(":8080"))
}