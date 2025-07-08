package entities

import (
	"context"
	"time"
)

// ErrorHandler interface for handling errors without import cycles
type ErrorHandler interface {
	ExecuteWithRetry(ctx context.Context, operation func() error) error
	ShouldRetry(err error, attempt int) bool
	AnalyzeError(err error) ErrorAnalysis
	CreateExtractionError(err error, context map[string]interface{}) *ExtractionError
	UpdateClientMetrics(client *WMSClient, err error)
}

// ErrorAnalysis represents the result of error analysis
type ErrorAnalysis struct {
	ErrorType   ErrorType     `json:"error_type"`
	IsRetryable bool          `json:"is_retryable"`
	Category    string        `json:"category"`
	Severity    string        `json:"severity"`
	Delay       time.Duration `json:"delay"`
	Description string        `json:"description"`
}

// ErrorType categorizes different types of errors
type ErrorType string

const (
	ErrorTypeNetwork        ErrorType = "network"
	ErrorTypeAuthentication ErrorType = "authentication"
	ErrorTypeAuthorization  ErrorType = "authorization"
	ErrorTypeRateLimit      ErrorType = "rate_limit"
	ErrorTypeTimeout        ErrorType = "timeout"
	ErrorTypeValidation     ErrorType = "validation"
	ErrorTypeData           ErrorType = "data"
	ErrorTypeSystem         ErrorType = "system"
	ErrorTypeServerError    ErrorType = "server_error"
	ErrorTypeClientError    ErrorType = "client_error"
	ErrorTypeConfiguration  ErrorType = "configuration"
	ErrorTypeUnknown        ErrorType = "unknown"
)

// ExtractionError represents an error that occurred during extraction
type ExtractionError struct {
	Message       string                 `json:"message"`
	Type          ErrorType              `json:"type"`
	Code          string                 `json:"code,omitempty"`
	Context       map[string]interface{} `json:"context,omitempty"`
	RecordContext map[string]interface{} `json:"record_context,omitempty"`
	Timestamp     time.Time              `json:"timestamp"`
	Retryable     bool                   `json:"retryable"`
	Recoverable   bool                   `json:"recoverable"`
	Details       string                 `json:"details,omitempty"`
	HTTPStatus    *int                   `json:"http_status,omitempty"`
	RetryAttempt  int                    `json:"retry_attempt"`
}

// ErrorHandlerFactory creates error handlers
type ErrorHandlerFactory interface {
	CreateErrorHandler() ErrorHandler
}
