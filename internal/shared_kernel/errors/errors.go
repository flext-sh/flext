package errors

import (
	"fmt"
	"net/http"
)

// DomainError representa um erro de domínio
type DomainError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Details string `json:"details,omitempty"`
}

func (e DomainError) Error() string {
	return e.Message
}

// ErrorType define tipos de erro
type ErrorType string

const (
	ValidationError   ErrorType = "VALIDATION_ERROR"
	NotFoundError     ErrorType = "NOT_FOUND"
	ConflictError     ErrorType = "CONFLICT"
	InternalError     ErrorType = "INTERNAL_ERROR"
	UnauthorizedError ErrorType = "UNAUTHORIZED"
)

// APIError representa um erro da API com código HTTP
type APIError struct {
	Type       ErrorType `json:"type"`
	Message    string    `json:"message"`
	Details    string    `json:"details,omitempty"`
	StatusCode int       `json:"-"`
}

func (e APIError) Error() string {
	return e.Message
}

// Constructors para diferentes tipos de erro

func NewValidationError(message, details string) APIError {
	return APIError{
		Type:       ValidationError,
		Message:    message,
		Details:    details,
		StatusCode: http.StatusBadRequest,
	}
}

func NewNotFoundError(resource, id string) APIError {
	return APIError{
		Type:       NotFoundError,
		Message:    fmt.Sprintf("%s not found", resource),
		Details:    fmt.Sprintf("Resource with ID %s was not found", id),
		StatusCode: http.StatusNotFound,
	}
}

func NewConflictError(message, details string) APIError {
	return APIError{
		Type:       ConflictError,
		Message:    message,
		Details:    details,
		StatusCode: http.StatusConflict,
	}
}

func NewInternalError(message, details string) APIError {
	return APIError{
		Type:       InternalError,
		Message:    message,
		Details:    details,
		StatusCode: http.StatusInternalServerError,
	}
}

func NewUnauthorizedError(message string) APIError {
	return APIError{
		Type:       UnauthorizedError,
		Message:    message,
		StatusCode: http.StatusUnauthorized,
	}
}

// ErrorResponse padroniza respostas de erro da API
type ErrorResponse struct {
	Error APIError `json:"error"`
}

// NewErrorResponse cria uma resposta de erro padronizada
func NewErrorResponse(err APIError) ErrorResponse {
	return ErrorResponse{Error: err}
}