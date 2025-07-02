package http

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/application"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// MockLogger é um mock do logger para testes
type MockLogger struct {
	entries []LogEntry
}

type LogEntry struct {
	Level   string
	Message string
	Fields  map[string]interface{}
}

func (m *MockLogger) Debug(msg string, fields ...logging.Field) {
	m.addEntry("DEBUG", msg, fields)
}

func (m *MockLogger) Info(msg string, fields ...logging.Field) {
	m.addEntry("INFO", msg, fields)
}

func (m *MockLogger) Warn(msg string, fields ...logging.Field) {
	m.addEntry("WARN", msg, fields)
}

func (m *MockLogger) Error(msg string, fields ...logging.Field) {
	m.addEntry("ERROR", msg, fields)
}

func (m *MockLogger) With(fields ...logging.Field) logging.Logger {
	return m // Simplified for testing
}

func (m *MockLogger) addEntry(level, msg string, fields []logging.Field) {
	fieldMap := make(map[string]interface{})
	for _, field := range fields {
		fieldMap[field.Key] = field.Value
	}
	m.entries = append(m.entries, LogEntry{
		Level:   level,
		Message: msg,
		Fields:  fieldMap,
	})
}

func TestBaseHandler_HandleError_ValidationErrors(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	validationErrors := application.ValidationErrors{
		{
			Field:   "name",
			Message: "Name is required",
			Value:   "",
		},
		{
			Field:   "email",
			Message: "Invalid email format",
			Value:   "invalid-email",
		},
	}

	// Act
	err := handler.HandleError(c, &validationErrors)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	var response ErrorResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.Equal(t, "Validation failed", response.Error)
	assert.Equal(t, "VALIDATION_ERROR", response.Code)
	assert.NotNil(t, response.Details)
	assert.NotZero(t, response.Timestamp)

	// Verificar se o erro foi logado
	assert.Len(t, mockLogger.entries, 1)
	assert.Equal(t, "ERROR", mockLogger.entries[0].Level)
	assert.Contains(t, mockLogger.entries[0].Message, "Handler error")
}

func TestBaseHandler_HandleError_SingleValidationError(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	validationError := application.ValidationError{
		Field:   "name",
		Message: "Name is required",
		Value:   "",
	}

	// Act
	err := handler.HandleError(c, validationError)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusBadRequest, rec.Code)

	var response ErrorResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.Equal(t, "Validation failed", response.Error)
	assert.Equal(t, "VALIDATION_ERROR", response.Code)

	// Deve ter o erro único em um array
	details, ok := response.Details.([]interface{})
	require.True(t, ok)
	assert.Len(t, details, 1)
}

func TestBaseHandler_HandleError_GenericError(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	genericError := fmt.Errorf("something went wrong")

	// Act
	err := handler.HandleError(c, genericError)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusInternalServerError, rec.Code)

	var response ErrorResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.Equal(t, "Internal server error", response.Error)
	assert.Equal(t, "INTERNAL_SERVER_ERROR", response.Code)
	assert.Equal(t, "something went wrong", response.Message)
}

func TestBaseHandler_HandleSuccess(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	data := map[string]string{
		"message": "Success",
		"status":  "ok",
	}

	// Act
	err := handler.HandleSuccess(c, data)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response SuccessResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.True(t, response.Success)
	assert.NotNil(t, response.Data)
	assert.NotZero(t, response.Timestamp)
}

func TestBaseHandler_HandleCreated(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodPost, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	data := map[string]string{
		"id":   "123",
		"name": "Created Resource",
	}

	// Act
	err := handler.HandleCreated(c, data)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusCreated, rec.Code)

	var response SuccessResponse
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.True(t, response.Success)
	assert.NotNil(t, response.Data)
	assert.NotZero(t, response.Timestamp)
}

func TestBaseHandler_ParsePagination(t *testing.T) {
	tests := []struct {
		name         string
		queryParams  map[string]string
		expectedPage int
		expectedSize int
	}{
		{
			name:         "default values",
			queryParams:  map[string]string{},
			expectedPage: 1,
			expectedSize: 10,
		},
		{
			name: "valid parameters",
			queryParams: map[string]string{
				"page":      "2",
				"page_size": "25",
			},
			expectedPage: 2,
			expectedSize: 25,
		},
		{
			name: "invalid page defaults to 1",
			queryParams: map[string]string{
				"page":      "0",
				"page_size": "20",
			},
			expectedPage: 1,
			expectedSize: 20,
		},
		{
			name: "invalid page_size defaults to 10",
			queryParams: map[string]string{
				"page":      "2",
				"page_size": "0",
			},
			expectedPage: 2,
			expectedSize: 10,
		},
		{
			name: "page_size over limit capped at 100",
			queryParams: map[string]string{
				"page":      "1",
				"page_size": "150",
			},
			expectedPage: 1,
			expectedSize: 100,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			q := req.URL.Query()
			for k, v := range tt.queryParams {
				q.Add(k, v)
			}
			req.URL.RawQuery = q.Encode()

			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mockLogger := &MockLogger{}
			handler := NewBaseHandler("TestHandler", mockLogger)

			// Act
			pagination := handler.ParsePagination(c)

			// Assert
			assert.Equal(t, tt.expectedPage, pagination.Page)
			assert.Equal(t, tt.expectedSize, pagination.PageSize)
		})
	}
}

func TestBaseHandler_ParseSort(t *testing.T) {
	tests := []struct {
		name          string
		queryParams   map[string]string
		expectNil     bool
		expectedBy    string
		expectedOrder string
	}{
		{
			name:        "no sort parameters",
			queryParams: map[string]string{},
			expectNil:   true,
		},
		{
			name: "valid sort parameters",
			queryParams: map[string]string{
				"sort_by":  "name",
				"sort_dir": "desc",
			},
			expectNil:     false,
			expectedBy:    "name",
			expectedOrder: "desc",
		},
		{
			name: "only sort_by parameter",
			queryParams: map[string]string{
				"sort_by": "created_at",
			},
			expectNil:     false,
			expectedBy:    "created_at",
			expectedOrder: "asc", // Should default to asc
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			e := echo.New()
			req := httptest.NewRequest(http.MethodGet, "/test", nil)
			q := req.URL.Query()
			for k, v := range tt.queryParams {
				q.Add(k, v)
			}
			req.URL.RawQuery = q.Encode()

			rec := httptest.NewRecorder()
			c := e.NewContext(req, rec)

			mockLogger := &MockLogger{}
			handler := NewBaseHandler("TestHandler", mockLogger)

			// Act
			sort := handler.ParseSort(c)

			// Assert
			if tt.expectNil {
				assert.Nil(t, sort)
			} else {
				require.NotNil(t, sort)
				assert.Equal(t, tt.expectedBy, sort.Field)
				assert.Equal(t, tt.expectedOrder, sort.Order)
			}
		})
	}
}

func TestBaseHandler_HandlePaginatedSuccess(t *testing.T) {
	// Arrange
	e := echo.New()
	req := httptest.NewRequest(http.MethodGet, "/test", nil)
	rec := httptest.NewRecorder()
	c := e.NewContext(req, rec)

	mockLogger := &MockLogger{}
	handler := NewBaseHandler("TestHandler", mockLogger)

	data := []map[string]string{
		{"id": "1", "name": "Item 1"},
		{"id": "2", "name": "Item 2"},
	}

	pagination := value_objects.NewPagination(1, 10)

	// Act
	err := handler.HandlePaginatedSuccess(c, data, pagination)

	// Assert
	require.NoError(t, err)
	assert.Equal(t, http.StatusOK, rec.Code)

	var response PaginatedResponse[map[string]string]
	err = json.Unmarshal(rec.Body.Bytes(), &response)
	require.NoError(t, err)

	assert.True(t, response.Success)
	assert.Len(t, response.Data, 2)
	assert.Equal(t, pagination, response.Pagination)
	assert.NotZero(t, response.Timestamp)
}
