package http

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/google/uuid"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/application"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
)

// BaseHandler fornece funcionalidades comuns para todos os handlers
type BaseHandler struct {
	logger logging.Logger
	name   string
}

// NewBaseHandler cria um novo handler base
func NewBaseHandler(name string, logger logging.Logger) *BaseHandler {
	return &BaseHandler{
		logger: logger.With(logging.F("handler", name)),
		name:   name,
	}
}

// GetName retorna o nome do handler
func (h *BaseHandler) GetName() string {
	return h.name
}

// GetLogger retorna o logger do handler
func (h *BaseHandler) GetLogger() logging.Logger {
	return h.logger
}

// HandleError trata erros de forma padronizada
func (h *BaseHandler) HandleError(c echo.Context, err error) error {
	h.logger.Error("Handler error",
		logging.F("error", err.Error()),
		logging.F("path", c.Request().URL.Path),
		logging.F("method", c.Request().Method),
	)

	// Determina o status code baseado no tipo do erro
	statusCode := http.StatusInternalServerError
	message := "Internal server error"

	// Personaliza baseado no tipo do erro
	switch e := err.(type) {
	case *application.ValidationErrors:
		statusCode = http.StatusBadRequest
		message = "Validation failed"
		return c.JSON(statusCode, ErrorResponse{
			Error:     message,
			Message:   e.Error(),
			Code:      "VALIDATION_ERROR",
			Details:   e,
			Timestamp: time.Now().UTC(),
			RequestID: getRequestID(c),
		})
	case application.ValidationError:
		statusCode = http.StatusBadRequest
		message = "Validation failed"
		return c.JSON(statusCode, ErrorResponse{
			Error:     message,
			Message:   e.Error(),
			Code:      "VALIDATION_ERROR",
			Details:   []application.ValidationError{e},
			Timestamp: time.Now().UTC(),
			RequestID: getRequestID(c),
		})
	default:
		// Para outros tipos de erro, verifica se é um erro conhecido
		if isNotFoundError(err) {
			statusCode = http.StatusNotFound
			message = "Resource not found"
		} else if isBadRequestError(err) {
			statusCode = http.StatusBadRequest
			message = "Bad request"
		} else if isUnauthorizedError(err) {
			statusCode = http.StatusUnauthorized
			message = "Unauthorized"
		} else if isForbiddenError(err) {
			statusCode = http.StatusForbidden
			message = "Forbidden"
		}
	}

	return c.JSON(statusCode, ErrorResponse{
		Error:     message,
		Message:   err.Error(),
		Code:      getErrorCode(statusCode),
		Timestamp: time.Now().UTC(),
		RequestID: getRequestID(c),
	})
}

// HandleSuccess retorna resposta de sucesso padronizada
func (h *BaseHandler) HandleSuccess(c echo.Context, data interface{}) error {
	return c.JSON(http.StatusOK, SuccessResponse{
		Data:      data,
		Success:   true,
		Timestamp: time.Now().UTC(),
		RequestID: getRequestID(c),
	})
}

// HandleCreated retorna resposta de criação padronizada
func (h *BaseHandler) HandleCreated(c echo.Context, data interface{}) error {
	return c.JSON(http.StatusCreated, SuccessResponse{
		Data:      data,
		Success:   true,
		Timestamp: time.Now().UTC(),
		RequestID: getRequestID(c),
	})
}

// HandleNoContent retorna resposta sem conteúdo
func (h *BaseHandler) HandleNoContent(c echo.Context) error {
	return c.NoContent(http.StatusNoContent)
}

// ValidateRequest valida uma requisição usando validator personalizado
func (h *BaseHandler) ValidateRequest(c echo.Context, req interface{}) error {
	if err := c.Bind(req); err != nil {
		return fmt.Errorf("failed to bind request: %w", err)
	}

	// Se o request implementa Validator, usa ele
	if validator, ok := req.(interface{ Validate() error }); ok {
		if err := validator.Validate(); err != nil {
			return err
		}
	}

	return nil
}

// ParsePagination extrai parâmetros de paginação da query string
func (h *BaseHandler) ParsePagination(c echo.Context) *value_objects.Pagination {
	page, _ := strconv.Atoi(c.QueryParam("page"))
	pageSize, _ := strconv.Atoi(c.QueryParam("page_size"))

	if page <= 0 {
		page = 1
	}
	if pageSize <= 0 {
		pageSize = 10
	}
	if pageSize > 100 {
		pageSize = 100
	}

	return value_objects.NewPagination(page, pageSize)
}

// ParseSort extrai parâmetros de ordenação da query string
func (h *BaseHandler) ParseSort(c echo.Context) *value_objects.Sort {
	sortBy := c.QueryParam("sort_by")
	sortDir := c.QueryParam("sort_dir")

	if sortBy == "" {
		return nil
	}

	return value_objects.NewSort(sortBy, sortDir)
}

// ParseFilters extrai filtros da query string
func (h *BaseHandler) ParseFilters(c echo.Context) []value_objects.Filter {
	filters := make([]value_objects.Filter, 0)

	// Parse filtros simples no formato filter[field]=value
	for key, values := range c.QueryParams() {
		if len(values) > 0 && len(key) > 7 && key[:7] == "filter[" && key[len(key)-1:] == "]" {
			field := key[7 : len(key)-1]
			filters = append(filters, *value_objects.NewFilter(field, "eq", values[0]))
		}
	}

	return filters
}

// ParseQueryOptions extrai todas as opções de consulta
func (h *BaseHandler) ParseQueryOptions(c echo.Context) *value_objects.QueryOptions {
	options := value_objects.NewQueryOptions()

	// Paginação
	options.Pagination = h.ParsePagination(c)

	// Ordenação
	if sort := h.ParseSort(c); sort != nil {
		options.Sort = []value_objects.Sort{*sort}
	}

	// Filtros
	options.Filters = h.ParseFilters(c)

	return options
}

// GetPathParam extrai parâmetro da URL
func (h *BaseHandler) GetPathParam(c echo.Context, param string) string {
	return c.Param(param)
}

// GetQueryParam extrai parâmetro da query string
func (h *BaseHandler) GetQueryParam(c echo.Context, param string) string {
	return c.QueryParam(param)
}

// GetQueryParamAsInt extrai parâmetro da query string como int
func (h *BaseHandler) GetQueryParamAsInt(c echo.Context, param string, defaultValue int) int {
	value, err := strconv.Atoi(c.QueryParam(param))
	if err != nil {
		return defaultValue
	}
	return value
}

// GetQueryParamAsBool extrai parâmetro da query string como bool
func (h *BaseHandler) GetQueryParamAsBool(c echo.Context, param string, defaultValue bool) bool {
	value, err := strconv.ParseBool(c.QueryParam(param))
	if err != nil {
		return defaultValue
	}
	return value
}

// parseUUID parses UUID from path parameter - método compatível com handlers existentes
func (h *BaseHandler) parseUUID(c echo.Context, param string) (uuid.UUID, error) {
	idStr := c.Param(param)
	if idStr == "" {
		return uuid.Nil, fmt.Errorf("missing %s parameter", param)
	}
	
	id, err := uuid.Parse(idStr)
	if err != nil {
		return uuid.Nil, fmt.Errorf("invalid %s: %w", param, err)
	}
	
	return id, nil
}

// ErrorResponse estrutura padrão para respostas de erro
type ErrorResponse struct {
	Error     string      `json:"error"`
	Message   string      `json:"message"`
	Code      string      `json:"code"`
	Details   interface{} `json:"details,omitempty"`
	Timestamp time.Time   `json:"timestamp"`
	RequestID string      `json:"request_id,omitempty"`
}

// SuccessResponse estrutura padrão para respostas de sucesso
type SuccessResponse struct {
	Data      interface{} `json:"data"`
	Success   bool        `json:"success"`
	Timestamp time.Time   `json:"timestamp"`
	RequestID string      `json:"request_id,omitempty"`
}

// PaginatedResponse estrutura para respostas paginadas
type PaginatedResponse[T any] struct {
	Data       []T                       `json:"data"`
	Pagination *value_objects.Pagination `json:"pagination"`
	Success    bool                      `json:"success"`
	Timestamp  time.Time                 `json:"timestamp"`
	RequestID  string                    `json:"request_id,omitempty"`
}

// HandlePaginatedSuccess retorna resposta paginada de sucesso
func (h *BaseHandler) HandlePaginatedSuccess(c echo.Context, data interface{}, pagination *value_objects.Pagination) error {
	response := map[string]interface{}{
		"data":       data,
		"pagination": pagination,
		"success":    true,
		"timestamp":  time.Now().UTC(),
		"request_id": getRequestID(c),
	}

	return c.JSON(http.StatusOK, response)
}

// RESTHandler interface que define operações CRUD padrão
type RESTHandler interface {
	Create(c echo.Context) error
	GetByID(c echo.Context) error
	List(c echo.Context) error
	Update(c echo.Context) error
	Delete(c echo.Context) error
}

// RegisterRESTRoutes registra rotas CRUD para um handler
func RegisterRESTRoutes(e *echo.Group, basePath string, handler RESTHandler) {
	e.POST(basePath, handler.Create)
	e.GET(basePath+"/:id", handler.GetByID)
	e.GET(basePath, handler.List)
	e.PUT(basePath+"/:id", handler.Update)
	e.DELETE(basePath+"/:id", handler.Delete)
}

// HandlerFunc função genérica para endpoints
type HandlerFunc[T any, R any] func(ctx context.Context, req T) (R, error)

// CreateEndpoint cria um endpoint genérico com validação
func CreateEndpoint[T any, R any](
	baseHandler *BaseHandler,
	handlerFunc HandlerFunc[T, R],
	validator func(T) error,
) echo.HandlerFunc {
	return func(c echo.Context) error {
		var req T

		// Bind da requisição
		if err := c.Bind(&req); err != nil {
			return baseHandler.HandleError(c, fmt.Errorf("invalid request format: %w", err))
		}

		// Validação
		if validator != nil {
			if err := validator(req); err != nil {
				return baseHandler.HandleError(c, err)
			}
		}

		// Executa o handler
		result, err := handlerFunc(c.Request().Context(), req)
		if err != nil {
			return baseHandler.HandleError(c, err)
		}

		return baseHandler.HandleSuccess(c, result)
	}
}

// CreateQueryEndpoint cria um endpoint de consulta com paginação
func CreateQueryEndpoint[T any](
	baseHandler *BaseHandler,
	handlerFunc func(ctx context.Context, options *value_objects.QueryOptions) (*value_objects.PaginatedResult[T], error),
) echo.HandlerFunc {
	return func(c echo.Context) error {
		options := baseHandler.ParseQueryOptions(c)

		// Valida as opções
		if err := options.Validate(); err != nil {
			return baseHandler.HandleError(c, err)
		}

		// Executa a consulta
		result, err := handlerFunc(c.Request().Context(), options)
		if err != nil {
			return baseHandler.HandleError(c, err)
		}

		return baseHandler.HandlePaginatedSuccess(c, result.Data, result.Pagination)
	}
}

// SetupCORS configura CORS
func SetupCORS() echo.MiddlewareFunc {
	return middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{"*"},
		AllowMethods: []string{http.MethodGet, http.MethodPost, http.MethodPut, http.MethodDelete, http.MethodOptions},
		AllowHeaders: []string{echo.HeaderOrigin, echo.HeaderContentType, echo.HeaderAccept, echo.HeaderAuthorization},
	})
}

// SetupRequestLogger configura logging de requests
func SetupRequestLogger(logger logging.Logger) echo.MiddlewareFunc {
	return middleware.RequestLoggerWithConfig(middleware.RequestLoggerConfig{
		LogURI:      true,
		LogStatus:   true,
		LogMethod:   true,
		LogLatency:  true,
		LogError:    true,
		LogRemoteIP: true,
		LogValuesFunc: func(c echo.Context, v middleware.RequestLoggerValues) error {
			logger.Info("HTTP Request",
				logging.F("method", v.Method),
				logging.F("uri", v.URI),
				logging.F("status", v.Status),
				logging.F("latency", v.Latency.String()),
				logging.F("remote_ip", v.RemoteIP),
				logging.F("error", v.Error),
			)
			return nil
		},
	})
}

// SetupRequestID adiciona ID único para cada request
func SetupRequestID() echo.MiddlewareFunc {
	return middleware.RequestID()
}

// Funções auxiliares

func getRequestID(c echo.Context) string {
	return c.Response().Header().Get(echo.HeaderXRequestID)
}

func getErrorCode(statusCode int) string {
	switch statusCode {
	case http.StatusBadRequest:
		return "BAD_REQUEST"
	case http.StatusUnauthorized:
		return "UNAUTHORIZED"
	case http.StatusForbidden:
		return "FORBIDDEN"
	case http.StatusNotFound:
		return "NOT_FOUND"
	case http.StatusConflict:
		return "CONFLICT"
	case http.StatusInternalServerError:
		return "INTERNAL_SERVER_ERROR"
	default:
		return "UNKNOWN_ERROR"
	}
}

func isNotFoundError(err error) bool {
	return contains(err.Error(), []string{"not found", "does not exist"})
}

func isBadRequestError(err error) bool {
	return contains(err.Error(), []string{"invalid", "bad request", "malformed"})
}

func isUnauthorizedError(err error) bool {
	return contains(err.Error(), []string{"unauthorized", "authentication"})
}

func isForbiddenError(err error) bool {
	return contains(err.Error(), []string{"forbidden", "access denied"})
}

func contains(text string, patterns []string) bool {
	for _, pattern := range patterns {
		if len(text) >= len(pattern) {
			for i := 0; i <= len(text)-len(pattern); i++ {
				if text[i:i+len(pattern)] == pattern {
					return true
				}
			}
		}
	}
	return false
}
