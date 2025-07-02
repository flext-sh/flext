package errors

import (
	"context"
	"fmt"
	"math"
	"math/rand"
	"net"
	"strings"
	"syscall"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
)

// WMSErrorHandler provides comprehensive error handling and retry logic for WMS operations
type WMSErrorHandler struct {
	config ErrorHandlingConfig
}

// Ensure WMSErrorHandler implements the ErrorHandler interface
var _ entities.ErrorHandler = (*WMSErrorHandler)(nil)

// ErrorHandlingConfig configures error handling behavior
type ErrorHandlingConfig struct {
	// Retry configuration
	MaxRetries          int           `json:"max_retries"`
	InitialDelay        time.Duration `json:"initial_delay"`
	MaxDelay            time.Duration `json:"max_delay"`
	BackoffMultiplier   float64       `json:"backoff_multiplier"`
	RandomizationFactor float64       `json:"randomization_factor"`

	// Circuit breaker
	UseCircuitBreaker bool          `json:"use_circuit_breaker"`
	FailureThreshold  int           `json:"failure_threshold"`
	RecoveryTimeout   time.Duration `json:"recovery_timeout"`

	// Error categorization
	RetryableHTTPCodes []int    `json:"retryable_http_codes"`
	RetryableErrors    []string `json:"retryable_errors"`
	NonRetryableErrors []string `json:"non_retryable_errors"`

	// Timeout configuration
	OperationTimeout  time.Duration `json:"operation_timeout"`
	ConnectionTimeout time.Duration `json:"connection_timeout"`

	// Error reporting
	LogErrors           bool   `json:"log_errors"`
	ErrorReportingLevel string `json:"error_reporting_level"`
}

// RetryDecision represents the decision on whether to retry an operation
type RetryDecision struct {
	ShouldRetry bool               `json:"should_retry"`
	Delay       time.Duration      `json:"delay"`
	Reason      string             `json:"reason"`
	ErrorType   entities.ErrorType `json:"error_type"`
	Attempt     int                `json:"attempt"`
}

// NewWMSErrorHandler creates a new error handler with default configuration
func NewWMSErrorHandler() *WMSErrorHandler {
	return &WMSErrorHandler{
		config: ErrorHandlingConfig{
			MaxRetries:          3,
			InitialDelay:        1 * time.Second,
			MaxDelay:            30 * time.Second,
			BackoffMultiplier:   2.0,
			RandomizationFactor: 0.1,
			UseCircuitBreaker:   true,
			FailureThreshold:    5,
			RecoveryTimeout:     60 * time.Second,
			RetryableHTTPCodes:  []int{429, 500, 502, 503, 504},
			RetryableErrors:     []string{"timeout", "connection", "temporary", "network"},
			NonRetryableErrors:  []string{"authentication", "authorization", "invalid", "not_found"},
			OperationTimeout:    5 * time.Minute,
			ConnectionTimeout:   30 * time.Second,
			LogErrors:           true,
			ErrorReportingLevel: "detailed",
		},
	}
}

// AnalyzeError provides comprehensive analysis of an error - implements ErrorHandler interface
func (h *WMSErrorHandler) AnalyzeError(err error) entities.ErrorAnalysis {
	if err == nil {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeUnknown,
			IsRetryable: false,
			Category:    "none",
			Severity:    "low",
			Description: "No error",
		}
	}

	errorMsg := strings.ToLower(err.Error())

	// Network errors
	if h.isNetworkError(err) {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeNetwork,
			IsRetryable: true,
			Severity:    "medium",
			Category:    "network",
			Description: "Network connectivity issue",
		}
	}

	// Timeout errors
	if h.isTimeoutError(err) {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeTimeout,
			IsRetryable: true,
			Severity:    "medium",
			Category:    "timeout",
			Description: "Operation timed out",
		}
	}

	// Authentication errors
	if strings.Contains(errorMsg, "authentication") || strings.Contains(errorMsg, "auth") ||
		strings.Contains(errorMsg, "unauthorized") || strings.Contains(errorMsg, "401") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeAuthentication,
			IsRetryable: false,
			Severity:    "high",
			Category:    "authentication",
			Description: "Authentication failed",
		}
	}

	// Authorization errors
	if strings.Contains(errorMsg, "authorization") || strings.Contains(errorMsg, "forbidden") ||
		strings.Contains(errorMsg, "access denied") || strings.Contains(errorMsg, "403") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeAuthorization,
			IsRetryable: false,
			Severity:    "high",
			Category:    "authorization",
			Description: "Access denied",
		}
	}

	// Rate limit errors
	if strings.Contains(errorMsg, "rate limit") || strings.Contains(errorMsg, "429") ||
		strings.Contains(errorMsg, "too many requests") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeRateLimit,
			IsRetryable: true,
			Severity:    "medium",
			Category:    "rate_limit",
			Description: "Rate limit exceeded",
		}
	}

	// Server errors
	if strings.Contains(errorMsg, "500") || strings.Contains(errorMsg, "502") ||
		strings.Contains(errorMsg, "503") || strings.Contains(errorMsg, "504") ||
		strings.Contains(errorMsg, "internal server error") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeServerError,
			IsRetryable: true,
			Severity:    "high",
			Category:    "server_error",
			Description: "Server-side error",
		}
	}

	// Client errors
	if strings.Contains(errorMsg, "400") || strings.Contains(errorMsg, "404") ||
		strings.Contains(errorMsg, "bad request") || strings.Contains(errorMsg, "not found") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeClientError,
			IsRetryable: false,
			Severity:    "medium",
			Category:    "client_error",
			Description: "Client request error",
		}
	}

	// Data errors
	if strings.Contains(errorMsg, "validation") || strings.Contains(errorMsg, "parse") ||
		strings.Contains(errorMsg, "decode") || strings.Contains(errorMsg, "marshal") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeData,
			IsRetryable: false,
			Severity:    "medium",
			Category:    "data",
			Description: "Data processing error",
		}
	}

	// Configuration errors
	if strings.Contains(errorMsg, "configuration") || strings.Contains(errorMsg, "config") ||
		strings.Contains(errorMsg, "invalid url") || strings.Contains(errorMsg, "missing") {
		return entities.ErrorAnalysis{
			ErrorType:   entities.ErrorTypeConfiguration,
			IsRetryable: false,
			Severity:    "critical",
			Category:    "configuration",
			Description: "Configuration error",
		}
	}

	// Default to unknown error
	return entities.ErrorAnalysis{
		ErrorType:   entities.ErrorTypeUnknown,
		IsRetryable: true, // Conservative approach - try once more
		Severity:    "medium",
		Category:    "unknown",
		Description: fmt.Sprintf("Unknown error: %s", err.Error()),
	}
}

// ShouldRetry determines if an operation should be retried - implements ErrorHandler interface
func (h *WMSErrorHandler) ShouldRetry(err error, attempt int) bool {
	if err == nil {
		return false
	}

	if attempt >= h.config.MaxRetries {
		return false
	}

	analysis := h.AnalyzeError(err)
	return analysis.IsRetryable
}

// ExecuteWithRetry executes a function with retry logic
func (h *WMSErrorHandler) ExecuteWithRetry(ctx context.Context, operation func() error) error {
	var lastErr error

	for attempt := 0; attempt <= h.config.MaxRetries; attempt++ {
		// Create timeout context for this attempt
		_, cancel := context.WithTimeout(ctx, h.config.OperationTimeout)

		// Execute operation
		err := operation()
		cancel() // Clean up timeout context

		if err == nil {
			return nil // Success
		}

		lastErr = err

		// Check if we should retry
		shouldRetry := h.ShouldRetry(err, attempt)
		if !shouldRetry {
			break
		}

		// Calculate delay for retry
		delay := h.calculateBackoffDelay(attempt)
		if delay > 0 {
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(delay):
				// Continue to next attempt
			}
		}
	}

	return fmt.Errorf("operation failed after %d attempts: %w", h.config.MaxRetries+1, lastErr)
}

// categorizeError determines the error type based on error characteristics
func (h *WMSErrorHandler) categorizeError(err error) entities.ErrorType {
	if err == nil {
		return entities.ErrorTypeUnknown
	}

	errStr := strings.ToLower(err.Error())

	// Network errors
	if strings.Contains(errStr, "connection") || strings.Contains(errStr, "network") ||
		strings.Contains(errStr, "timeout") || strings.Contains(errStr, "dns") {
		if strings.Contains(errStr, "timeout") {
			return entities.ErrorTypeTimeout
		}
		return entities.ErrorTypeNetwork
	}

	// Authentication errors
	if strings.Contains(errStr, "unauthorized") || strings.Contains(errStr, "401") ||
		strings.Contains(errStr, "authentication") || strings.Contains(errStr, "invalid credentials") {
		return entities.ErrorTypeAuthentication
	}

	// Authorization errors
	if strings.Contains(errStr, "forbidden") || strings.Contains(errStr, "403") ||
		strings.Contains(errStr, "access denied") {
		return entities.ErrorTypeAuthorization
	}

	// Rate limit errors
	if strings.Contains(errStr, "rate limit") || strings.Contains(errStr, "429") ||
		strings.Contains(errStr, "too many requests") {
		return entities.ErrorTypeRateLimit
	}

	// Validation errors
	if strings.Contains(errStr, "validation") || strings.Contains(errStr, "invalid") ||
		strings.Contains(errStr, "bad request") || strings.Contains(errStr, "400") {
		return entities.ErrorTypeValidation
	}

	// Data errors
	if strings.Contains(errStr, "parse") || strings.Contains(errStr, "unmarshal") ||
		strings.Contains(errStr, "decode") || strings.Contains(errStr, "format") {
		return entities.ErrorTypeData
	}

	return entities.ErrorTypeUnknown
}

// CreateExtractionError implements the ErrorHandler interface
func (h *WMSErrorHandler) CreateExtractionError(err error, context map[string]interface{}) *entities.ExtractionError {
	analysis := h.AnalyzeError(err)

	return &entities.ExtractionError{
		Message:     err.Error(),
		Type:        analysis.ErrorType,
		Context:     context,
		Timestamp:   time.Now(),
		Retryable:   analysis.IsRetryable,
		Recoverable: true, // Default to recoverable unless proven otherwise
	}
}

// UpdateClientMetrics implements the ErrorHandler interface
func (h *WMSErrorHandler) UpdateClientMetrics(client *entities.WMSClient, err error) {
	if client == nil {
		return
	}

	analysis := h.AnalyzeError(err)

	// Update error metrics
	if client.Metrics.ErrorsByType == nil {
		client.Metrics.ErrorsByType = make(map[string]int)
	}
	client.Metrics.ErrorsByType[string(analysis.ErrorType)]++
	client.Metrics.FailedRequests++

	now := time.Now()
	client.Metrics.LastError = &now
}

// WMSErrorHandlerFactory implements ErrorHandlerFactory
type WMSErrorHandlerFactory struct{}

// NewWMSErrorHandlerFactory creates a new error handler factory
func NewWMSErrorHandlerFactory() *WMSErrorHandlerFactory {
	return &WMSErrorHandlerFactory{}
}

// CreateErrorHandler creates a new error handler
func (f *WMSErrorHandlerFactory) CreateErrorHandler() entities.ErrorHandler {
	return NewWMSErrorHandler()
}

// ExecuteWithRetryAndResult executes a function with retry logic and returns a result
// Note: Using interface{} instead of generics for Go compatibility
func (h *WMSErrorHandler) ExecuteWithRetryAndResult(ctx context.Context, operation func() (interface{}, error)) (interface{}, error) {
	var lastErr error
	var result interface{}

	for attempt := 0; attempt <= h.config.MaxRetries; attempt++ {
		// Create timeout context for this attempt
		_, cancel := context.WithTimeout(ctx, h.config.OperationTimeout)

		// Execute operation
		res, err := operation()
		cancel() // Clean up timeout context

		if err == nil {
			return res, nil // Success
		}

		lastErr = err

		// Check if we should retry
		shouldRetry := h.ShouldRetry(err, attempt)
		if !shouldRetry {
			break
		}

		// Calculate delay for retry
		delay := h.calculateBackoffDelay(attempt)
		if delay > 0 {
			select {
			case <-ctx.Done():
				return result, ctx.Err()
			case <-time.After(delay):
				// Continue to next attempt
			}
		}
	}

	return result, fmt.Errorf("operation failed after %d attempts: %w", h.config.MaxRetries+1, lastErr)
}

// Private helper methods

func (h *WMSErrorHandler) isNetworkError(err error) bool {
	// Check for network-related errors
	if netErr, ok := err.(net.Error); ok {
		return netErr.Temporary() || netErr.Timeout()
	}

	// Check for specific network error types
	if _, ok := err.(*net.OpError); ok {
		return true
	}

	// Check for DNS errors
	if _, ok := err.(*net.DNSError); ok {
		return true
	}

	// Check for syscall errors
	if syscallErr, ok := err.(*net.OpError); ok {
		if errno, ok := syscallErr.Err.(syscall.Errno); ok {
			switch errno {
			case syscall.ECONNREFUSED, syscall.ECONNRESET, syscall.ENETUNREACH, syscall.EHOSTUNREACH:
				return true
			}
		}
	}

	errorMsg := strings.ToLower(err.Error())
	networkKeywords := []string{
		"connection refused", "connection reset", "connection timeout",
		"network unreachable", "host unreachable", "dns", "resolve",
		"no route to host", "network is down",
	}

	for _, keyword := range networkKeywords {
		if strings.Contains(errorMsg, keyword) {
			return true
		}
	}

	return false
}

func (h *WMSErrorHandler) isTimeoutError(err error) bool {
	// Check for timeout interface
	if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
		return true
	}

	// Check for context timeout
	if err == context.DeadlineExceeded {
		return true
	}

	// Check for timeout in error message
	errorMsg := strings.ToLower(err.Error())
	timeoutKeywords := []string{
		"timeout", "timed out", "deadline exceeded", "context canceled",
	}

	for _, keyword := range timeoutKeywords {
		if strings.Contains(errorMsg, keyword) {
			return true
		}
	}

	return false
}

func (h *WMSErrorHandler) calculateBackoffDelay(attempt int) time.Duration {
	// Exponential backoff: delay = initial_delay * (backoff_multiplier ^ attempt)
	delay := float64(h.config.InitialDelay) * math.Pow(h.config.BackoffMultiplier, float64(attempt))

	// Apply maximum delay limit
	if delay > float64(h.config.MaxDelay) {
		delay = float64(h.config.MaxDelay)
	}

	// Add jitter to avoid thundering herd
	if h.config.RandomizationFactor > 0 {
		jitter := delay * h.config.RandomizationFactor * (rand.Float64()*2 - 1) // +/- randomization_factor
		delay += jitter
	}

	// Ensure minimum delay
	if delay < float64(h.config.InitialDelay) {
		delay = float64(h.config.InitialDelay)
	}

	return time.Duration(delay)
}

// HttpError represents an HTTP error with status code
type HttpError struct {
	StatusCode int
	Message    string
}

func (e *HttpError) Error() string {
	return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Message)
}

// NewHttpError creates a new HTTP error
func NewHttpError(statusCode int, message string) *HttpError {
	return &HttpError{
		StatusCode: statusCode,
		Message:    message,
	}
}
