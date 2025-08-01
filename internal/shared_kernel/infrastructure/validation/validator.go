package validation

import (
	"reflect"
	"strings"

	"github.com/flext/flexcore/internal/shared_kernel/application"
	"github.com/go-playground/validator/v10"
)

// ValidatorImpl implementa a interface Validator
type ValidatorImpl struct {
	validator *validator.Validate
}

// NewValidator cria uma nova instância do validador
func NewValidator() application.Validator {
	v := validator.New()

	// Configurar nomes de campos JSON para melhorar mensagens de erro
	v.RegisterTagNameFunc(func(fld reflect.StructField) string {
		name := strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]
		if name == "-" {
			return ""
		}
		return name
	})

	// Registrar validações customizadas
	registerCustomValidations(v)

	return &ValidatorImpl{
		validator: v,
	}
}

// Validate valida um objeto struct
func (v *ValidatorImpl) Validate(obj interface{}) error {
	if err := v.validator.Struct(obj); err != nil {
		return v.translateValidationErrors(err)
	}
	return nil
}

// ValidateStruct valida especificamente um struct
func (v *ValidatorImpl) ValidateStruct(obj interface{}) error {
	return v.Validate(obj)
}

// ValidateField valida um campo específico
func (v *ValidatorImpl) ValidateField(value interface{}, tag string) error {
	if err := v.validator.Var(value, tag); err != nil {
		return v.translateValidationErrors(err)
	}
	return nil
}

// translateValidationErrors converte erros do validator em format amigável
func (v *ValidatorImpl) translateValidationErrors(err error) error {
	validationErrors := application.ValidationErrors{}

	if validationErrs, ok := err.(validator.ValidationErrors); ok {
		for _, fieldErr := range validationErrs {
			validationErrors.Add(
				fieldErr.Field(),
				v.getErrorMessage(fieldErr),
				fieldErr.Value(),
			)
		}
	}

	if len(validationErrors) == 1 {
		return &validationErrors[0]
	}

	return &validationErrors
}

// getErrorMessage retorna mensagem de erro personalizada baseada na tag
func (v *ValidatorImpl) getErrorMessage(fieldErr validator.FieldError) string {
	field := fieldErr.Field()
	tag := fieldErr.Tag()
	param := fieldErr.Param()

	switch tag {
	case "required":
		return field + " is required"
	case "email":
		return field + " must be a valid email address"
	case "min":
		return field + " must be at least " + param + " characters"
	case "max":
		return field + " must be at most " + param + " characters"
	case "len":
		return field + " must be exactly " + param + " characters"
	case "gte":
		return field + " must be greater than or equal to " + param
	case "lte":
		return field + " must be less than or equal to " + param
	case "gt":
		return field + " must be greater than " + param
	case "lt":
		return field + " must be less than " + param
	case "oneof":
		return field + " must be one of: " + param
	case "uuid":
		return field + " must be a valid UUID"
	case "url":
		return field + " must be a valid URL"
	case "alpha":
		return field + " must contain only alphabetic characters"
	case "alphanum":
		return field + " must contain only alphanumeric characters"
	case "numeric":
		return field + " must be numeric"
	case "contains":
		return field + " must contain '" + param + "'"
	case "startswith":
		return field + " must start with '" + param + "'"
	case "endswith":
		return field + " must end with '" + param + "'"
	default:
		return field + " failed validation (" + tag + ")"
	}
}

// registerCustomValidations registra validações customizadas
func registerCustomValidations(v *validator.Validate) {
	// Validação para pipeline type
	v.RegisterValidation("pipeline_type", func(fl validator.FieldLevel) bool {
		value := fl.Field().String()
		validTypes := []string{"etl", "elt", "stream", "batch", "realtime"}
		for _, validType := range validTypes {
			if value == validType {
				return true
			}
		}
		return false
	})

	// Validação para status
	v.RegisterValidation("pipeline_status", func(fl validator.FieldLevel) bool {
		value := fl.Field().String()
		validStatuses := []string{"draft", "active", "paused", "error", "completed"}
		for _, validStatus := range validStatuses {
			if value == validStatus {
				return true
			}
		}
		return false
	})

	// Validação para cron expression (simplificada)
	v.RegisterValidation("cron", func(fl validator.FieldLevel) bool {
		value := fl.Field().String()
		if value == "" {
			return true // Opcional
		}
		// Validação básica de cron (5 ou 6 campos)
		parts := strings.Fields(value)
		return len(parts) == 5 || len(parts) == 6
	})

	// Validação para JSON válido
	v.RegisterValidation("json", func(fl validator.FieldLevel) bool {
		value := fl.Field().String()
		if value == "" {
			return true // Opcional
		}
		// Verificação básica se começa com { ou [
		trimmed := strings.TrimSpace(value)
		return strings.HasPrefix(trimmed, "{") || strings.HasPrefix(trimmed, "[")
	})
}
