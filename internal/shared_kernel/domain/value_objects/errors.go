package value_objects

import (
	"fmt"
)

// DomainError represents a domain-specific error
type DomainError struct {
	Code        string `json:"code"`
	Message     string `json:"message"`
	Description string `json:"description,omitempty"`
}

// Error implements the error interface
func (e *DomainError) Error() string {
	if e.Description != "" {
		return fmt.Sprintf("%s: %s (%s)", e.Code, e.Message, e.Description)
	}
	return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

// NewDomainError creates a new domain error
func NewDomainError(code, message, description string) *DomainError {
	return &DomainError{
		Code:        code,
		Message:     message,
		Description: description,
	}
}

// IsDomainError checks if an error is a domain error
func IsDomainError(err error) bool {
	_, ok := err.(*DomainError)
	return ok
}

// GetDomainError extracts domain error from error, returns nil if not a domain error
func GetDomainError(err error) *DomainError {
	if domainErr, ok := err.(*DomainError); ok {
		return domainErr
	}
	return nil
}
