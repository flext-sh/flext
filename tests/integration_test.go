package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/flext-sh/flext/internal/infrastructure/container"
	pipelineCommands "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	pluginCommands "github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/commands"
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

func setupTestServer() *echo.Echo {
	// Inicializar container de dependências
	container := container.NewContainer()

	// Criar instância do Echo
	e := echo.New()

	// Configurar validator
	e.Validator = &CustomValidator{validator: validator.New()}

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Registrar rotas dos handlers
	pipelineHandler := container.GetPipelineHandler()
	pipelineHandler.RegisterRoutes(e)

	pluginHandler := container.GetPluginHandler()
	pluginHandler.RegisterRoutes(e)

	return e
}

func TestCreatePipeline(t *testing.T) {
	e := setupTestServer()

	// Criar comando de pipeline
	cmd := pipelineCommands.CreatePipelineCommand{
		Name:        "Test Pipeline",
		Description: "Pipeline de teste",
		Tags:        []string{"test", "integration"},
	}

	// Converter para JSON
	jsonData, err := json.Marshal(cmd)
	if err != nil {
		t.Fatalf("Failed to marshal command: %v", err)
	}

	// Criar requisição
	req := httptest.NewRequest(http.MethodPost, "/api/v1/pipelines", bytes.NewBuffer(jsonData))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()

	// Executar
	e.ServeHTTP(rec, req)

	// Verificar resultado
	if rec.Code != http.StatusCreated {
		t.Errorf("Expected status 201, got %d. Body: %s", rec.Code, rec.Body.String())
	}

	// Verificar estrutura da resposta
	var result pipelineCommands.CreatePipelineResult
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if result.ID.String() == "" {
		t.Error("Expected non-empty pipeline ID")
	}
}

func TestRegisterPlugin(t *testing.T) {
	e := setupTestServer()

	// Criar comando de plugin
	cmd := pluginCommands.RegisterPluginCommand{
		Name:        "Test Plugin",
		Type:        "source",
		Version:     "1.0.0",
		Description: "Plugin de teste",
		Author:      "Test Author",
		EntryPoint:  "/usr/bin/test-plugin",
		Ports: []pluginCommands.PortDefinition{
			{
				Name:        "input",
				Type:        "source",
				Required:    true,
				Description: "Input port",
			},
		},
	}

	// Converter para JSON
	jsonData, err := json.Marshal(cmd)
	if err != nil {
		t.Fatalf("Failed to marshal command: %v", err)
	}

	// Criar requisição
	req := httptest.NewRequest(http.MethodPost, "/api/v1/plugins", bytes.NewBuffer(jsonData))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	rec := httptest.NewRecorder()

	// Executar
	e.ServeHTTP(rec, req)

	// Verificar resultado
	if rec.Code != http.StatusCreated {
		t.Errorf("Expected status 201, got %d. Body: %s", rec.Code, rec.Body.String())
	}

	// Verificar estrutura da resposta
	var result pluginCommands.RegisterPluginResult
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if result.ID.String() == "" {
		t.Error("Expected non-empty plugin ID")
	}
}

func TestListPipelines(t *testing.T) {
	e := setupTestServer()

	// Criar requisição
	req := httptest.NewRequest(http.MethodGet, "/api/v1/pipelines", nil)
	rec := httptest.NewRecorder()

	// Executar
	e.ServeHTTP(rec, req)

	// Verificar resultado
	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d. Body: %s", rec.Code, rec.Body.String())
	}

	// Verificar estrutura da resposta
	var result map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if _, exists := result["pipelines"]; !exists {
		t.Error("Expected 'pipelines' field in response")
	}
	if _, exists := result["total"]; !exists {
		t.Error("Expected 'total' field in response")
	}
}

func TestListPlugins(t *testing.T) {
	e := setupTestServer()

	// Criar requisição
	req := httptest.NewRequest(http.MethodGet, "/api/v1/plugins", nil)
	rec := httptest.NewRecorder()

	// Executar
	e.ServeHTTP(rec, req)

	// Verificar resultado
	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d. Body: %s", rec.Code, rec.Body.String())
	}

	// Verificar estrutura da resposta
	var result map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if _, exists := result["plugins"]; !exists {
		t.Error("Expected 'plugins' field in response")
	}
	if _, exists := result["total"]; !exists {
		t.Error("Expected 'total' field in response")
	}
}

func TestHealthEndpoint(t *testing.T) {
	e := setupTestServer()

	// Health check
	e.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"status":  "ok",
			"version": "1.0.0",
		})
	})

	// Criar requisição
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	// Executar
	e.ServeHTTP(rec, req)

	// Verificar resultado
	if rec.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", rec.Code)
	}

	// Verificar estrutura da resposta
	var result map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	if result["status"] != "ok" {
		t.Error("Expected status 'ok'")
	}
}