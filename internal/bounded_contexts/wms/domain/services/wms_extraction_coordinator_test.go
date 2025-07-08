// Package services provides comprehensive tests for WMS extraction coordinator
// This implements EXTREME TESTING standards as demanded
package services

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"
)

// MockWMSClient is a mock implementation of WMSClientInterface
type MockWMSClient struct {
	mock.Mock
}

func (m *MockWMSClient) ExecuteQuery(ctx context.Context, query string, params map[string]interface{}) (*QueryResult, error) {
	args := m.Called(ctx, query, params)
	return args.Get(0).(*QueryResult), args.Error(1)
}

func (m *MockWMSClient) GetEntitySchema(entityName string) (*EntitySchema, error) {
	args := m.Called(entityName)
	return args.Get(0).(*EntitySchema), args.Error(1)
}

func (m *MockWMSClient) ValidateConnection() error {
	args := m.Called()
	return args.Error(0)
}

// MockExtractionStateManager is a mock implementation of ExtractionStateManagerInterface
type MockExtractionStateManager struct {
	mock.Mock
}

func (m *MockExtractionStateManager) SaveState(extractionID uuid.UUID, state *ExtractionState) error {
	args := m.Called(extractionID, state)
	return args.Error(0)
}

func (m *MockExtractionStateManager) LoadState(extractionID uuid.UUID) (*ExtractionState, error) {
	args := m.Called(extractionID)
	return args.Get(0).(*ExtractionState), args.Error(1)
}

func (m *MockExtractionStateManager) UpdateBookmark(extractionID uuid.UUID, bookmark map[string]interface{}) error {
	args := m.Called(extractionID, bookmark)
	return args.Error(0)
}

// MockMetricService is a mock implementation of MetricServiceInterface
type MockMetricService struct {
	mock.Mock
}

func (m *MockMetricService) StartExtraction(extractionID uuid.UUID) error {
	args := m.Called(extractionID)
	return args.Error(0)
}

func (m *MockMetricService) UpdateProgress(extractionID uuid.UUID, metrics ExtractionMetrics) error {
	args := m.Called(extractionID, metrics)
	return args.Error(0)
}

func (m *MockMetricService) FinishExtraction(extractionID uuid.UUID, success bool) error {
	args := m.Called(extractionID, success)
	return args.Error(0)
}

// MockErrorHandler is a mock implementation of ErrorHandlerInterface
type MockErrorHandler struct {
	mock.Mock
}

func (m *MockErrorHandler) HandleError(extractionID uuid.UUID, err error) (*ErrorResponse, error) {
	args := m.Called(extractionID, err)
	return args.Get(0).(*ErrorResponse), args.Error(1)
}

func (m *MockErrorHandler) ShouldRetry(err error, attemptCount int) bool {
	args := m.Called(err, attemptCount)
	return args.Bool(0)
}

func (m *MockErrorHandler) GetBackoffDelay(attemptCount int) time.Duration {
	args := m.Called(attemptCount)
	return args.Get(0).(time.Duration)
}

// Test fixtures
func createTestConfig() *ExtractionConfiguration {
	return &ExtractionConfiguration{
		BatchSize:      1000,
		MaxConcurrency: 5,
		Timeout:        30 * time.Second,
		RetryPolicy: RetryPolicy{
			MaxAttempts:   3,
			InitialDelay:  100 * time.Millisecond,
			MaxDelay:      5 * time.Second,
			BackoffFactor: 2.0,
		},
		Filters: map[string]interface{}{
			"status": "active",
		},
		PaginationConfig: &PaginationConfig{
			PageSize:   1000,
			Strategy:   "offset",
			SortColumn: "id",
			SortOrder:  "ASC",
		},
	}
}

func createTestCoordinator(
	client WMSClientInterface,
	stateManager ExtractionStateManagerInterface,
	metricService MetricServiceInterface,
	errorHandler ErrorHandlerInterface,
) (*WMSExtractionCoordinator, error) {
	extractionID := uuid.New()
	entityName := "test_entity"
	extractionType := entities.ExtractionType("full")
	config := createTestConfig()

	return NewWMSExtractionCoordinator(
		extractionID,
		entityName,
		extractionType,
		client,
		stateManager,
		metricService,
		errorHandler,
		config,
	)
}

// EXTREME TESTING: Constructor Tests
func TestNewWMSExtractionCoordinator_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	// Act
	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)

	// Assert
	require.NoError(t, err)
	assert.NotNil(t, coordinator)
	assert.NotEqual(t, uuid.Nil, coordinator.ExtractionID)
	assert.Equal(t, "test_entity", coordinator.EntityName)
	assert.NotNil(t, coordinator.config)
}

func TestNewWMSExtractionCoordinator_NilExtractionID(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}
	config := createTestConfig()

	// Act
	coordinator, err := NewWMSExtractionCoordinator(
		uuid.Nil, // Invalid ID
		"test_entity",
		entities.ExtractionType("full"),
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
		config,
	)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, coordinator)
	assert.Contains(t, err.Error(), "extraction ID cannot be nil")
}

func TestNewWMSExtractionCoordinator_EmptyEntityName(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}
	config := createTestConfig()

	// Act
	coordinator, err := NewWMSExtractionCoordinator(
		uuid.New(),
		"", // Empty entity name
		entities.ExtractionType("full"),
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
		config,
	)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, coordinator)
	assert.Contains(t, err.Error(), "entity name cannot be empty")
}

func TestNewWMSExtractionCoordinator_NilDependencies(t *testing.T) {
	testCases := []struct {
		name          string
		client        WMSClientInterface
		stateManager  ExtractionStateManagerInterface
		metricService MetricServiceInterface
		errorHandler  ErrorHandlerInterface
		config        *ExtractionConfiguration
		expectedError string
	}{
		{
			name:          "nil client",
			client:        nil,
			stateManager:  &MockExtractionStateManager{},
			metricService: &MockMetricService{},
			errorHandler:  &MockErrorHandler{},
			config:        createTestConfig(),
			expectedError: "client cannot be nil",
		},
		{
			name:          "nil state manager",
			client:        &MockWMSClient{},
			stateManager:  nil,
			metricService: &MockMetricService{},
			errorHandler:  &MockErrorHandler{},
			config:        createTestConfig(),
			expectedError: "state manager cannot be nil",
		},
		{
			name:          "nil metric service",
			client:        &MockWMSClient{},
			stateManager:  &MockExtractionStateManager{},
			metricService: nil,
			errorHandler:  &MockErrorHandler{},
			config:        createTestConfig(),
			expectedError: "metric service cannot be nil",
		},
		{
			name:          "nil error handler",
			client:        &MockWMSClient{},
			stateManager:  &MockExtractionStateManager{},
			metricService: &MockMetricService{},
			errorHandler:  nil,
			config:        createTestConfig(),
			expectedError: "error handler cannot be nil",
		},
		{
			name:          "nil configuration",
			client:        &MockWMSClient{},
			stateManager:  &MockExtractionStateManager{},
			metricService: &MockMetricService{},
			errorHandler:  &MockErrorHandler{},
			config:        nil,
			expectedError: "configuration cannot be nil",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Act
			coordinator, err := NewWMSExtractionCoordinator(
				uuid.New(),
				"test_entity",
				entities.ExtractionType("full"),
				tc.client,
				tc.stateManager,
				tc.metricService,
				tc.errorHandler,
				tc.config,
			)

			// Assert
			assert.Error(t, err)
			assert.Nil(t, coordinator)
			assert.Contains(t, err.Error(), tc.expectedError)
		})
	}
}

// EXTREME TESTING: StartExtraction Tests
func TestStartExtraction_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	ctx := context.Background()

	// Setup mocks
	mockClient.On("ValidateConnection").Return(nil)
	mockMetricService.On("StartExtraction", coordinator.ExtractionID).Return(nil)
	mockStateManager.On("SaveState", coordinator.ExtractionID, mock.AnythingOfType("*services.ExtractionState")).Return(nil)

	// Act
	err = coordinator.StartExtraction(ctx)

	// Assert
	assert.NoError(t, err)
	mockClient.AssertExpectations(t)
	mockMetricService.AssertExpectations(t)
	mockStateManager.AssertExpectations(t)
}

func TestStartExtraction_ClientValidationFails(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	ctx := context.Background()
	expectedError := errors.New("connection failed")

	// Setup mocks
	mockClient.On("ValidateConnection").Return(expectedError)

	// Act
	err = coordinator.StartExtraction(ctx)

	// Assert
	assert.Error(t, err)
	assert.Equal(t, expectedError, err)
	mockClient.AssertExpectations(t)
}

func TestStartExtraction_MetricServiceFails(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	ctx := context.Background()
	expectedError := errors.New("metric service failed")

	// Setup mocks
	mockClient.On("ValidateConnection").Return(nil)
	mockMetricService.On("StartExtraction", coordinator.ExtractionID).Return(expectedError)

	// Act
	err = coordinator.StartExtraction(ctx)

	// Assert
	assert.Error(t, err)
	assert.Equal(t, expectedError, err)
	mockClient.AssertExpectations(t)
	mockMetricService.AssertExpectations(t)
}

func TestStartExtraction_StateManagerFails(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	ctx := context.Background()
	expectedError := errors.New("state save failed")

	// Setup mocks
	mockClient.On("ValidateConnection").Return(nil)
	mockMetricService.On("StartExtraction", coordinator.ExtractionID).Return(nil)
	mockStateManager.On("SaveState", coordinator.ExtractionID, mock.AnythingOfType("*services.ExtractionState")).Return(expectedError)

	// Act
	err = coordinator.StartExtraction(ctx)

	// Assert
	assert.Error(t, err)
	assert.Equal(t, expectedError, err)
	mockClient.AssertExpectations(t)
	mockMetricService.AssertExpectations(t)
	mockStateManager.AssertExpectations(t)
}

// EXTREME TESTING: GetExtractionStatus Tests
func TestGetExtractionStatus_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	expectedState := &ExtractionState{
		Status:           ExtractionStatusRunning,
		Progress:         50.0,
		ProcessedRecords: 500,
		TotalRecords:     1000,
		StartedAt:        time.Now(),
		UpdatedAt:        time.Now(),
	}

	// Setup mocks
	mockStateManager.On("LoadState", coordinator.ExtractionID).Return(expectedState, nil)

	// Act
	state, err := coordinator.GetExtractionStatus()

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, expectedState, state)
	mockStateManager.AssertExpectations(t)
}

// EXTREME TESTING: UpdateProgress Tests
func TestUpdateProgress_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	processedRecords := int64(750)
	totalRecords := int64(1000)

	// Setup mocks
	mockMetricService.On("UpdateProgress", coordinator.ExtractionID, mock.AnythingOfType("services.ExtractionMetrics")).Return(nil)

	// Act
	err = coordinator.UpdateProgress(processedRecords, totalRecords)

	// Assert
	assert.NoError(t, err)
	mockMetricService.AssertExpectations(t)
}

// EXTREME TESTING: CompleteExtraction Tests
func TestCompleteExtraction_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	// Setup mocks
	mockMetricService.On("FinishExtraction", coordinator.ExtractionID, true).Return(nil)

	// Act
	err = coordinator.CompleteExtraction()

	// Assert
	assert.NoError(t, err)
	mockMetricService.AssertExpectations(t)
}

// EXTREME TESTING: FailExtraction Tests
func TestFailExtraction_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	reasonError := errors.New("extraction failed due to network error")
	errorResponse := &ErrorResponse{
		ShouldRetry:  false,
		ErrorCode:    "NETWORK_ERROR",
		ErrorMessage: "network connection failed",
		CanContinue:  false,
	}

	// Setup mocks
	mockMetricService.On("FinishExtraction", coordinator.ExtractionID, false).Return(nil)
	mockErrorHandler.On("HandleError", coordinator.ExtractionID, reasonError).Return(errorResponse, nil)

	// Act
	err = coordinator.FailExtraction(reasonError)

	// Assert
	assert.NoError(t, err)
	mockMetricService.AssertExpectations(t)
	mockErrorHandler.AssertExpectations(t)
}

// EXTREME TESTING: Configuration Tests
func TestGetConfiguration(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	// Act
	config := coordinator.GetConfiguration()

	// Assert
	assert.NotNil(t, config)
	assert.Equal(t, 1000, config.BatchSize)
	assert.Equal(t, 5, config.MaxConcurrency)
	assert.Equal(t, 30*time.Second, config.Timeout)
}

func TestUpdateConfiguration_Success(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	newConfig := &ExtractionConfiguration{
		BatchSize:      2000,
		MaxConcurrency: 10,
		Timeout:        60 * time.Second,
		RetryPolicy: RetryPolicy{
			MaxAttempts:   5,
			InitialDelay:  200 * time.Millisecond,
			MaxDelay:      10 * time.Second,
			BackoffFactor: 1.5,
		},
	}

	// Act
	err = coordinator.UpdateConfiguration(newConfig)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, newConfig, coordinator.GetConfiguration())
}

func TestUpdateConfiguration_NilConfig(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	// Act
	err = coordinator.UpdateConfiguration(nil)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "configuration cannot be nil")
}

// EXTREME TESTING: Concurrency Tests
func TestConcurrentOperations(t *testing.T) {
	// Arrange
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, err := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)
	require.NoError(t, err)

	// Setup mocks for concurrent access
	expectedState := &ExtractionState{
		Status:           ExtractionStatusRunning,
		Progress:         50.0,
		ProcessedRecords: 500,
		TotalRecords:     1000,
		StartedAt:        time.Now(),
		UpdatedAt:        time.Now(),
	}
	mockStateManager.On("LoadState", coordinator.ExtractionID).Return(expectedState, nil)
	mockMetricService.On("UpdateProgress", coordinator.ExtractionID, mock.AnythingOfType("services.ExtractionMetrics")).Return(nil)

	// Act - Run concurrent operations
	const numGoroutines = 10
	ch := make(chan error, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(i int) {
			if i%2 == 0 {
				_, err := coordinator.GetExtractionStatus()
				ch <- err
			} else {
				err := coordinator.UpdateProgress(int64(i*100), 1000)
				ch <- err
			}
		}(i)
	}

	// Assert - Collect results
	for i := 0; i < numGoroutines; i++ {
		err := <-ch
		assert.NoError(t, err)
	}
}

// EXTREME TESTING: Benchmark Tests
func BenchmarkGetExtractionStatus(b *testing.B) {
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, _ := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)

	expectedState := &ExtractionState{
		Status:           ExtractionStatusRunning,
		Progress:         50.0,
		ProcessedRecords: 500,
		TotalRecords:     1000,
		StartedAt:        time.Now(),
		UpdatedAt:        time.Now(),
	}
	mockStateManager.On("LoadState", coordinator.ExtractionID).Return(expectedState, nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = coordinator.GetExtractionStatus()
	}
}

func BenchmarkUpdateProgress(b *testing.B) {
	mockClient := &MockWMSClient{}
	mockStateManager := &MockExtractionStateManager{}
	mockMetricService := &MockMetricService{}
	mockErrorHandler := &MockErrorHandler{}

	coordinator, _ := createTestCoordinator(
		mockClient,
		mockStateManager,
		mockMetricService,
		mockErrorHandler,
	)

	mockMetricService.On("UpdateProgress", coordinator.ExtractionID, mock.AnythingOfType("services.ExtractionMetrics")).Return(nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = coordinator.UpdateProgress(int64(i), 10000)
	}
}
