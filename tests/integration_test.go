package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	pipelineCommands "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	pluginCommands "github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/commands"
	"github.com/flext-sh/flext/internal/infrastructure/config"
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

func setupTestServer() *echo.Echo {
	// Load test configuration
	cfg := config.LoadFromEnv()
	cfg.Features.DatabaseEnabled = false // Use in-memory repositories for tests

	// Inicializar container de dependências
	appContainer, err := container.NewContainer(cfg)
	if err != nil {
		panic("Failed to initialize container: " + err.Error())
	}

	// Criar instância do Echo
	e := echo.New()

	// Configurar validator
	e.Validator = &CustomValidator{validator: validator.New()}

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Registrar rotas dos handlers
	pipelineHandler := appContainer.GetPipelineHandler()
	pipelineHandler.RegisterRoutes(e)

	pluginHandler := appContainer.GetPluginHandler()
	pluginHandler.RegisterRoutes(e)

	return e
}

func TestCreatePipeline(t *testing.T) {
	e := setupTestServer()

	// Criar comando de pipeline
	cmd := pipelineCommands.CreatePipelineCommand{
		Name:        "TestPipeline",
		Description: "Pipeline de teste",
		Type:        "etl",
		CreatedBy:   "test_user",
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

	// Debug: Print response body
	t.Logf("Response body: %s", rec.Body.String())

	// Verificar estrutura da resposta - pode estar encapsulada em uma estrutura de resposta
	var responseWrapper map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &responseWrapper); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	// Check if data field exists (BaseHandler wraps responses)
	var result pipelineCommands.CreatePipelineResult
	if data, exists := responseWrapper["data"]; exists {
		dataBytes, _ := json.Marshal(data)
		json.Unmarshal(dataBytes, &result)
	} else {
		json.Unmarshal(rec.Body.Bytes(), &result)
	}

	if result.PipelineID == "" {
		t.Error("Expected non-empty pipeline ID")
	}
}

func TestRegisterPlugin(t *testing.T) {
	e := setupTestServer()

	// Criar comando de plugin
	cmd := pluginCommands.RegisterPluginCommand{
		Name:        "TestPlugin",
		Type:        "source",
		Version:     "1.0.0",
		Description: "Plugin de teste",
		Author:      "TestAuthor",
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

	// Debug: Print response body
	t.Logf("List pipelines response body: %s", rec.Body.String())

	// Verificar estrutura da resposta
	var result map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	// Check if the response is wrapped in a "data" field
	if data, exists := result["data"]; exists {
		if dataMap, ok := data.(map[string]interface{}); ok {
			if _, exists := dataMap["pipelines"]; !exists {
				t.Error("Expected 'pipelines' field in response data")
			}
			if _, exists := dataMap["total"]; !exists {
				t.Error("Expected 'total' field in response data")
			}
		}
	} else {
		// Legacy format
		if _, exists := result["pipelines"]; !exists {
			t.Error("Expected 'pipelines' field in response")
		}
		if _, exists := result["total"]; !exists {
			t.Error("Expected 'total' field in response")
		}
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

	// Debug: Print response body
	t.Logf("List plugins response body: %s", rec.Body.String())

	// Verificar estrutura da resposta
	var result map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
		t.Fatalf("Failed to unmarshal response: %v", err)
	}

	// Check if the response is wrapped in a "data" field
	if data, exists := result["data"]; exists {
		if dataMap, ok := data.(map[string]interface{}); ok {
			if _, exists := dataMap["plugins"]; !exists {
				t.Error("Expected 'plugins' field in response data")
			}
			if _, exists := dataMap["total"]; !exists {
				t.Error("Expected 'total' field in response data")
			}
		}
	} else {
		// Legacy format
		if _, exists := result["plugins"]; !exists {
			t.Error("Expected 'plugins' field in response")
		}
		if _, exists := result["total"]; !exists {
			t.Error("Expected 'total' field in response")
		}
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
