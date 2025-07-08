package middleware

import (
	"net/http"

	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
)

// ErrorResponse representa uma resposta de erro padronizada
type ErrorResponse struct {
	Error   string                 `json:"error"`
	Message string                 `json:"message"`
	Code    int                    `json:"code"`
	Details map[string]interface{} `json:"details,omitempty"`
}

// ValidationError representa um erro de validação
type ValidationError struct {
	Field   string `json:"field"`
	Tag     string `json:"tag"`
	Message string `json:"message"`
}

// ErrorHandler middleware para tratamento de erros
func ErrorHandler() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			err := next(c)
			if err != nil {
				return handleError(c, err)
			}
			return nil
		}
	}
}

// handleError trata diferentes tipos de erro
func handleError(c echo.Context, err error) error {
	switch e := err.(type) {
	case *echo.HTTPError:
		return handleHTTPError(c, e)
	case validator.ValidationErrors:
		return handleValidationErrors(c, e)
	case *ValidationError:
		return handleSingleValidationError(c, e)
	default:
		return handleGenericError(c, e)
	}
}

// handleHTTPError trata erros HTTP do Echo
func handleHTTPError(c echo.Context, err *echo.HTTPError) error {
	code := err.Code
	message := err.Message

	if message == nil {
		message = http.StatusText(code)
	}

	response := ErrorResponse{
		Error:   "http_error",
		Message: message.(string),
		Code:    code,
	}

	return c.JSON(code, response)
}

// handleValidationErrors trata erros de validação do validator
func handleValidationErrors(c echo.Context, errs validator.ValidationErrors) error {
	validationErrors := make([]ValidationError, 0, len(errs))

	for _, err := range errs {
		validationErrors = append(validationErrors, ValidationError{
			Field:   err.Field(),
			Tag:     err.Tag(),
			Message: getValidationMessage(err),
		})
	}

	response := ErrorResponse{
		Error:   "validation_error",
		Message: "Request validation failed",
		Code:    http.StatusBadRequest,
		Details: map[string]interface{}{
			"validation_errors": validationErrors,
		},
	}

	return c.JSON(http.StatusBadRequest, response)
}

// handleSingleValidationError trata um erro de validação único
func handleSingleValidationError(c echo.Context, err *ValidationError) error {
	response := ErrorResponse{
		Error:   "validation_error",
		Message: err.Message,
		Code:    http.StatusBadRequest,
		Details: map[string]interface{}{
			"field": err.Field,
			"tag":   err.Tag,
		},
	}

	return c.JSON(http.StatusBadRequest, response)
}

// handleGenericError trata erros genéricos
func handleGenericError(c echo.Context, err error) error {
	response := ErrorResponse{
		Error:   "internal_error",
		Message: "An internal error occurred",
		Code:    http.StatusInternalServerError,
		Details: map[string]interface{}{
			"error": err.Error(),
		},
	}

	return c.JSON(http.StatusInternalServerError, response)
}

// getValidationMessage retorna mensagem de erro personalizada baseada na tag
func getValidationMessage(fe validator.FieldError) string {
	switch fe.Tag() {
	case "required":
		return fe.Field() + " is required"
	case "email":
		return fe.Field() + " must be a valid email"
	case "min":
		return fe.Field() + " must be at least " + fe.Param() + " characters"
	case "max":
		return fe.Field() + " must be at most " + fe.Param() + " characters"
	case "len":
		return fe.Field() + " must be exactly " + fe.Param() + " characters"
	case "alpha":
		return fe.Field() + " must contain only letters"
	case "alphanum":
		return fe.Field() + " must contain only letters and numbers"
	case "numeric":
		return fe.Field() + " must be numeric"
	case "url":
		return fe.Field() + " must be a valid URL"
	case "uuid":
		return fe.Field() + " must be a valid UUID"
	default:
		return fe.Field() + " is invalid"
	}
}

// ProcessValidationError cria um erro de validação customizado
func ProcessValidationError(err error) error {
	if ve, ok := err.(validator.ValidationErrors); ok {
		return ve
	}
	return err
}

// NewValidationError cria um novo erro de validação
func NewValidationError(field, tag, message string) *ValidationError {
	return &ValidationError{
		Field:   field,
		Tag:     tag,
		Message: message,
	}
}

// Error implementa a interface error
func (ve *ValidationError) Error() string {
	return ve.Message
}
