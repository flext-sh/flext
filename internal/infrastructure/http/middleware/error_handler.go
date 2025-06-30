package middleware

import (
	"log"
	"net/http"

	sharedErrors "github.com/flext-sh/flext/internal/shared_kernel/errors"
	"github.com/labstack/echo/v4"
)

// ErrorHandler middleware para tratamento centralizado de erros
func ErrorHandler() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			err := next(c)
			if err == nil {
				return nil
			}

			// Log do erro original
			log.Printf("Error in %s %s: %v", c.Request().Method, c.Request().URL.Path, err)

			// Tratar diferentes tipos de erro
			switch e := err.(type) {
			case sharedErrors.APIError:
				// Erro já tipado
				response := sharedErrors.NewErrorResponse(e)
				return c.JSON(e.StatusCode, response)
			
			case *echo.HTTPError:
				// Erro do Echo
				apiErr := sharedErrors.APIError{
					Type:       sharedErrors.InternalError,
					Message:    "Internal server error",
					StatusCode: e.Code,
				}
				if e.Code == http.StatusNotFound {
					apiErr.Type = sharedErrors.NotFoundError
					apiErr.Message = "Endpoint not found"
				}
				response := sharedErrors.NewErrorResponse(apiErr)
				return c.JSON(e.Code, response)
			
			default:
				// Erro genérico
				apiErr := sharedErrors.NewInternalError(
					"Internal server error",
					"An unexpected error occurred",
				)
				response := sharedErrors.NewErrorResponse(apiErr)
				return c.JSON(http.StatusInternalServerError, response)
			}
		}
	}
}

// ValidationErrorHandler trata erros de validação do validator
func ValidationErrorHandler(err error) sharedErrors.APIError {
	return sharedErrors.NewValidationError(
		"Validation failed",
		err.Error(),
	)
}