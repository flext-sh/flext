package middleware

import (
	"net/http"

	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
)

// RequestValidator representa um validador personalizado para requests
type RequestValidator struct {
	validator *validator.Validate
}

// NewRequestValidator cria um novo validador de request
func NewRequestValidator() *RequestValidator {
	v := validator.New()

	// Registrar validações customizadas
	v.RegisterValidation("pipeline_name", validatePipelineName)
	v.RegisterValidation("plugin_type", validatePluginType)

	return &RequestValidator{validator: v}
}

// Validate implementa a interface echo.Validator
func (rv *RequestValidator) Validate(i interface{}) error {
	if err := rv.validator.Struct(i); err != nil {
		return ProcessValidationError(err)
	}
	return nil
}

// validatePipelineName valida nomes de pipeline
func validatePipelineName(fl validator.FieldLevel) bool {
	name := fl.Field().String()
	// Nome deve ter entre 3-100 caracteres e apenas letras, números, _ e -
	if len(name) < 3 || len(name) > 100 {
		return false
	}

	for _, char := range name {
		if !((char >= 'a' && char <= 'z') ||
			(char >= 'A' && char <= 'Z') ||
			(char >= '0' && char <= '9') ||
			char == '_' || char == '-') {
			return false
		}
	}
	return true
}

// validatePluginType valida tipos de plugin
func validatePluginType(fl validator.FieldLevel) bool {
	pluginType := fl.Field().String()
	validTypes := []string{"source", "target", "transformer", "utility"}

	for _, validType := range validTypes {
		if pluginType == validType {
			return true
		}
	}
	return false
}

// ValidateRequestBody middleware para validar o corpo da requisição
func ValidateRequestBody(target interface{}) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if err := c.Bind(target); err != nil {
				return c.JSON(http.StatusBadRequest, ErrorResponse{
					Error:   "invalid_request_body",
					Message: "Request body is invalid",
					Code:    http.StatusBadRequest,
				})
			}

			if err := c.Validate(target); err != nil {
				return err
			}

			// Adicionar objeto validado ao contexto
			c.Set("validated_body", target)
			return next(c)
		}
	}
}

// GetValidatedBody recupera o corpo validado do contexto
func GetValidatedBody(c echo.Context) interface{} {
	return c.Get("validated_body")
}
