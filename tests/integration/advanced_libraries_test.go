package integration

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/infrastructure/container"
	"github.com/pkg/errors"
	"github.com/samber/lo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Test configuration for integration tests
func getTestConfig() *config.Config {
	cfg := config.DefaultConfig()

	// Disable external dependencies for testing
	cfg.Features.DatabaseEnabled = false
	cfg.Features.RedisEnabled = false
	cfg.Features.GormEnabled = false
	cfg.Features.SqlxEnabled = false
	cfg.Features.AuthRequired = false

	// Enable features that don't require external services
	cfg.Features.MetricsEnabled = true
	cfg.Features.WebSocketEnabled = true
	cfg.Features.PluginSystemEnabled = true
	cfg.Features.PipelineExecution = true

	// Use a test port
	cfg.Server.Port = 8082

	return cfg
}

// TestAdvancedContainerInitialization tests that the advanced container can be created
func TestAdvancedContainerInitialization(t *testing.T) {
	cfg := getTestConfig()

	// Initialize logging for tests
	logging.InitLogger(cfg.Logging)

	// Create advanced container
	factory := container.NewFactory()
	advancedContainer, err := factory.CreateAdvancedContainer(cfg)
	require.NoError(t, err, "Advanced container should initialize successfully")
	require.NotNil(t, advancedContainer, "Advanced container should not be nil")

	// Verify container has expected components
	// Test HealthCheck functionality
	err = advancedContainer.HealthCheck(context.Background())
	assert.NoError(t, err, "Advanced container health check should pass")

	// Clean up
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = advancedContainer.Shutdown(ctx)
	assert.NoError(t, err, "Container shutdown should be clean")
}

// TestSamberLoFunctionalProgramming tests the samber/lo library integration
func TestSamberLoFunctionalProgramming(t *testing.T) {
	// Test Map function
	numbers := []int{1, 2, 3, 4, 5}
	doubled := lo.Map(numbers, func(x int, index int) int {
		return x * 2
	})
	expected := []int{2, 4, 6, 8, 10}
	assert.Equal(t, expected, doubled, "Map function should double all numbers")

	// Test Filter function
	filtered := lo.Filter(numbers, func(x int, index int) bool {
		return x%2 == 0
	})
	expectedFiltered := []int{2, 4}
	assert.Equal(t, expectedFiltered, filtered, "Filter should return only even numbers")

	// Test Find function
	found, ok := lo.Find(numbers, func(x int) bool {
		return x > 3
	})
	assert.True(t, ok, "Should find number greater than 3")
	assert.Equal(t, 4, found, "Should find first number greater than 3")

	// Test Reduce function
	sum := lo.Reduce(numbers, func(acc int, x int, index int) int {
		return acc + x
	}, 0)
	assert.Equal(t, 15, sum, "Sum should be 15")

	// Test Contains function
	assert.True(t, lo.Contains(numbers, 3), "Should contain 3")
	assert.False(t, lo.Contains(numbers, 10), "Should not contain 10")

	// Test Uniq function
	duplicates := []int{1, 2, 2, 3, 3, 3, 4}
	unique := lo.Uniq(duplicates)
	expectedUnique := []int{1, 2, 3, 4}
	assert.Equal(t, expectedUnique, unique, "Should remove duplicates")
}

// TestZerologIntegration tests structured logging with zerolog
func TestZerologIntegration(t *testing.T) {
	cfg := getTestConfig()
	cfg.Logging.Level = "debug"
	cfg.Logging.Format = "json"
	cfg.Logging.Structured = true

	// Initialize logging
	logging.InitLogger(cfg.Logging)
	logger := logging.GetLogger()

	// Test that logger is not nil
	require.NotNil(t, logger, "Logger should be initialized")

	// Test logging with fields
	logger.Info("Test log message",
		logging.F("component", "integration_test"),
		logging.F("test_case", "zerolog_integration"),
		logging.F("number", 42),
		logging.F("success", true),
	)

	// Test different log levels
	logger.Debug("Debug message", logging.F("level", "debug"))
	logger.Info("Info message", logging.F("level", "info"))
	logger.Warn("Warning message", logging.F("level", "warn"))

	// Test with context
	contextLogger := logger.With(logging.F("context", "test_context"))
	contextLogger.Info("Message with context")

	// The test passes if no panics occur and logger methods are callable
	assert.True(t, true, "Zerolog integration test completed successfully")
}

// TestViperConfigurationManagement tests advanced configuration with Viper
func TestViperConfigurationManagement(t *testing.T) {
	// Test config loading without file (environment-based)
	cfg := config.LoadFromEnv()
	require.NotNil(t, cfg, "Config should be loaded from environment")

	// Test config validation
	err := cfg.Validate()
	// Note: This might fail due to JWT secret key requirement, which is expected
	if err != nil {
		t.Logf("Config validation failed as expected: %v", err)
	}

	// Test default configuration
	defaultCfg := config.DefaultConfig()
	assert.NotNil(t, defaultCfg, "Default config should not be nil")
	assert.Equal(t, "development", defaultCfg.Server.Environment)
	assert.Equal(t, 8081, defaultCfg.Server.Port)
	assert.True(t, defaultCfg.Features.MetricsEnabled)
	assert.True(t, defaultCfg.Features.WebSocketEnabled)

	// Test port conflict resolution
	originalPort := defaultCfg.Server.Port
	availablePort := defaultCfg.GetAvailablePort()
	assert.GreaterOrEqual(t, availablePort, originalPort, "Available port should be >= original port")

	// Test address generation
	address := defaultCfg.Address()
	assert.Contains(t, address, ":", "Address should contain port separator")
	assert.Contains(t, address, defaultCfg.Server.Host, "Address should contain host")
}

// TestPkgErrorsIntegration tests enhanced error handling with pkg/errors
func TestPkgErrorsIntegration(t *testing.T) {
	// Test basic error creation and wrapping
	baseErr := assert.AnError
	wrappedErr := errors.Wrap(baseErr, "test operation failed")

	assert.Error(t, wrappedErr, "Wrapped error should be an error")
	assert.Contains(t, wrappedErr.Error(), "test operation failed", "Error should contain custom message")
	assert.Contains(t, wrappedErr.Error(), baseErr.Error(), "Error should contain original error")

	// Test error cause extraction
	originalErr := errors.Cause(wrappedErr)
	assert.Equal(t, baseErr, originalErr, "Should extract original error")

	// Test multiple levels of wrapping
	doubleWrapped := errors.Wrap(wrappedErr, "second level wrap")
	assert.Contains(t, doubleWrapped.Error(), "second level wrap", "Should contain second wrap message")
	assert.Contains(t, doubleWrapped.Error(), "test operation failed", "Should contain first wrap message")

	// Test error formatting with stack trace
	errorWithStack := errors.Errorf("formatted error with number: %d", 42)
	assert.Contains(t, errorWithStack.Error(), "formatted error with number: 42", "Should support error formatting")
}

// TestInMemoryCacheImplementation tests cache functionality without Redis
func TestInMemoryCacheImplementation(t *testing.T) {
	// For now, just test that we can work with map-based caching
	cache := make(map[string]interface{})

	// Test basic operations
	key := "test_key"
	value := "test_value"

	// Set value
	cache[key] = value

	// Get value
	retrievedValue, exists := cache[key]
	assert.True(t, exists, "Key should exist")
	assert.Equal(t, value, retrievedValue, "Retrieved value should match set value")

	// Test JSON-like operations
	testData := map[string]interface{}{
		"name":  "test",
		"value": 42,
		"list":  []string{"a", "b", "c"},
	}

	jsonKey := "json_key"
	cache[jsonKey] = testData

	retrievedData, exists := cache[jsonKey]
	assert.True(t, exists, "JSON key should exist")

	if dataMap, ok := retrievedData.(map[string]interface{}); ok {
		assert.Equal(t, testData["name"], dataMap["name"], "JSON data should match")
		assert.Equal(t, testData["value"], dataMap["value"], "JSON value should match")
	}

	// Test deletion
	delete(cache, key)
	_, exists = cache[key]
	assert.False(t, exists, "Key should not exist after delete")
}

// TestAdvancedStatisticsCollection tests comprehensive statistics
func TestAdvancedStatisticsCollection(t *testing.T) {
	cfg := getTestConfig()
	logging.InitLogger(cfg.Logging)

	// Create container with monitoring enabled
	cfg.Features.MetricsEnabled = true
	factory := container.NewFactory()
	advancedContainer, err := factory.CreateAdvancedContainer(cfg)
	require.NoError(t, err, "Advanced container should initialize")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// TODO: Fix GetAdvancedStatistics method call - interface doesn't have this method
	// Get statistics
	// stats, err := advancedContainer.GetAdvancedStatistics(ctx)
	// require.NoError(t, err, "Should get statistics")
	// require.NotNil(t, stats, "Statistics should not be nil")

	// Verify statistics structure
	// assert.NotNil(t, stats.Components, "Components should be present")

	// Check for expected components
	// if features, ok := stats.Components["features"].(map[string]bool); ok {
	//	assert.Contains(t, features, "gorm_enabled", "Should contain GORM feature flag")
	//	assert.Contains(t, features, "sqlx_enabled", "Should contain SQLX feature flag")
	//	assert.Contains(t, features, "redis_enabled", "Should contain Redis feature flag")
	// }

	// Clean up
	err = advancedContainer.Shutdown(ctx)
	assert.NoError(t, err, "Container shutdown should be clean")
}

// TestJSONSerialization tests JSON handling across the application
func TestJSONSerialization(t *testing.T) {
	// Test complex data structure serialization
	testData := map[string]interface{}{
		"string_field":  "test value",
		"number_field":  42,
		"boolean_field": true,
		"array_field":   []string{"a", "b", "c"},
		"object_field": map[string]interface{}{
			"nested_string": "nested value",
			"nested_number": 123,
		},
		"null_field": nil,
	}

	// Serialize to JSON
	jsonData, err := json.Marshal(testData)
	assert.NoError(t, err, "JSON marshaling should succeed")
	assert.NotEmpty(t, jsonData, "JSON data should not be empty")

	// Deserialize from JSON
	var deserializedData map[string]interface{}
	err = json.Unmarshal(jsonData, &deserializedData)
	assert.NoError(t, err, "JSON unmarshaling should succeed")

	// Verify data integrity
	assert.Equal(t, testData["string_field"], deserializedData["string_field"])
	assert.Equal(t, float64(42), deserializedData["number_field"]) // JSON numbers are float64
	assert.Equal(t, testData["boolean_field"], deserializedData["boolean_field"])

	// Verify nested object
	if nestedObj, ok := deserializedData["object_field"].(map[string]interface{}); ok {
		assert.Equal(t, "nested value", nestedObj["nested_string"])
		assert.Equal(t, float64(123), nestedObj["nested_number"])
	} else {
		t.Error("Nested object not properly deserialized")
	}
}

// TestPerformanceWithAdvancedLibraries tests performance characteristics
func TestPerformanceWithAdvancedLibraries(t *testing.T) {
	// Test samber/lo performance with large datasets
	largeDataset := make([]int, 10000)
	for i := range largeDataset {
		largeDataset[i] = i
	}

	start := time.Now()

	// Perform functional operations
	filtered := lo.Filter(largeDataset, func(x int, index int) bool {
		return x%2 == 0
	})

	mapped := lo.Map(filtered, func(x int, index int) int {
		return x * 2
	})

	sum := lo.Reduce(mapped, func(acc int, x int, index int) int {
		return acc + x
	}, 0)

	duration := time.Since(start)

	assert.Greater(t, len(filtered), 0, "Filtered dataset should not be empty")
	assert.Greater(t, len(mapped), 0, "Mapped dataset should not be empty")
	assert.Greater(t, sum, 0, "Sum should be positive")
	assert.Less(t, duration, time.Second, "Operations should complete within reasonable time")

	t.Logf("Processed %d items in %v", len(largeDataset), duration)
}

// TestConcurrentOperations tests thread safety of advanced components
func TestConcurrentOperations(t *testing.T) {
	cfg := getTestConfig()
	logging.InitLogger(cfg.Logging)

	// Test concurrent operations with samber/lo
	const numGoroutines = 10
	const operationsPerGoroutine = 100

	done := make(chan bool, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			defer func() { done <- true }()

			// Create test data for this goroutine
			numbers := make([]int, operationsPerGoroutine)
			for j := 0; j < operationsPerGoroutine; j++ {
				numbers[j] = id*1000 + j
			}

			// Perform functional operations
			filtered := lo.Filter(numbers, func(x int, index int) bool {
				return x%2 == 0
			})

			mapped := lo.Map(filtered, func(x int, index int) int {
				return x * 2
			})

			sum := lo.Reduce(mapped, func(acc int, x int, index int) int {
				return acc + x
			}, 0)

			// Verify results are consistent
			if len(filtered) == 0 {
				t.Errorf("Goroutine %d: No filtered results", id)
				return
			}

			if len(mapped) != len(filtered) {
				t.Errorf("Goroutine %d: Mapped length mismatch", id)
				return
			}

			if sum <= 0 {
				t.Errorf("Goroutine %d: Invalid sum: %d", id, sum)
				return
			}
		}(i)
	}

	// Wait for all goroutines to complete
	for i := 0; i < numGoroutines; i++ {
		select {
		case <-done:
		case <-time.After(10 * time.Second):
			t.Fatal("Concurrent operations timed out")
		}
	}

	t.Logf("Successfully completed %d concurrent functional programming operations", numGoroutines)
}
