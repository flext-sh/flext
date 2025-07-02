package http

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

// ErrorResponse representa uma resposta de erro padronizada
type ErrorResponse struct {
	Error   string            `json:"error"`
	Message string            `json:"message,omitempty"`
	Code    int               `json:"code"`
	Details map[string]string `json:"details,omitempty"`
}

// SuccessResponse representa uma resposta de sucesso padronizada
type SuccessResponse struct {
	Data    interface{} `json:"data,omitempty"`
	Message string      `json:"message,omitempty"`
	Status  string      `json:"status"`
}

// NewErrorResponse cria uma nova resposta de erro
func NewErrorResponse(code int, message string, details map[string]string) *ErrorResponse {
	return &ErrorResponse{
		Error:   http.StatusText(code),
		Message: message,
		Code:    code,
		Details: details,
	}
}

// NewSuccessResponse cria uma nova resposta de sucesso
func NewSuccessResponse(data interface{}, message string) *SuccessResponse {
	return &SuccessResponse{
		Data:    data,
		Message: message,
		Status:  "success",
	}
}

// SendError envia uma resposta de erro
func SendError(c echo.Context, code int, message string, details map[string]string) error {
	return c.JSON(code, NewErrorResponse(code, message, details))
}

// SendSuccess envia uma resposta de sucesso
func SendSuccess(c echo.Context, data interface{}, message string) error {
	return c.JSON(http.StatusOK, NewSuccessResponse(data, message))
}

// SendCreated envia uma resposta de criação
func SendCreated(c echo.Context, data interface{}, message string) error {
	return c.JSON(http.StatusCreated, NewSuccessResponse(data, message))
}

// SendAccepted envia uma resposta de aceito
func SendAccepted(c echo.Context, data interface{}, message string) error {
	return c.JSON(http.StatusAccepted, NewSuccessResponse(data, message))
}

// SendNoContent envia uma resposta sem conteúdo
func SendNoContent(c echo.Context) error {
	return c.NoContent(http.StatusNoContent)
}