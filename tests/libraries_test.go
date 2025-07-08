package tests

import (
	"context"
	"testing"
	"time"

	"github.com/pkg/errors"
	"github.com/samber/lo"
	"github.com/stretchr/testify/assert"
)

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

	// Test Chunk function
	chunk := lo.Chunk(numbers, 2)
	expectedChunk := [][]int{{1, 2}, {3, 4}, {5}}
	assert.Equal(t, expectedChunk, chunk, "Should chunk array correctly")

	// Test Reverse function
	reversed := lo.Reverse(numbers)
	expectedReversed := []int{5, 4, 3, 2, 1}
	assert.Equal(t, expectedReversed, reversed, "Should reverse array")
}

// TestPkgErrorsIntegration tests enhanced error handling with pkg/errors
func TestPkgErrorsIntegration(t *testing.T) {
	// Test basic error creation and wrapping
	baseErr := errors.New("base error")
	wrappedErr := errors.Wrap(baseErr, "operation failed")

	assert.Error(t, wrappedErr, "Wrapped error should be an error")
	assert.Contains(t, wrappedErr.Error(), "operation failed", "Error should contain custom message")
	assert.Contains(t, wrappedErr.Error(), "base error", "Error should contain original error")

	// Test error cause extraction
	originalErr := errors.Cause(wrappedErr)
	assert.Equal(t, baseErr, originalErr, "Should extract original error")

	// Test multiple levels of wrapping
	doubleWrapped := errors.Wrap(wrappedErr, "second level wrap")
	assert.Contains(t, doubleWrapped.Error(), "second level wrap", "Should contain second wrap message")
	assert.Contains(t, doubleWrapped.Error(), "operation failed", "Should contain first wrap message")

	// Test error formatting
	errorWithStack := errors.Errorf("formatted error with number: %d", 42)
	assert.Contains(t, errorWithStack.Error(), "formatted error with number: 42", "Should support error formatting")

	// Test WithStack
	stackErr := errors.WithStack(baseErr)
	assert.NotNil(t, stackErr, "WithStack should add stack trace")

	// Test WithMessage
	msgErr := errors.WithMessage(baseErr, "additional context")
	assert.Contains(t, msgErr.Error(), "additional context", "Should contain additional message")
	assert.Contains(t, msgErr.Error(), "base error", "Should contain original error")
}

// TestAdvancedFunctionalOperations tests more complex samber/lo operations
func TestAdvancedFunctionalOperations(t *testing.T) {
	numbers := []int{1, 2, 3, 4, 5, 6}

	// Test GroupBy function
	grouped := lo.GroupBy(numbers, func(x int) string {
		if x%2 == 0 {
			return "even"
		}
		return "odd"
	})

	assert.Contains(t, grouped, "even", "Should have even group")
	assert.Contains(t, grouped, "odd", "Should have odd group")
	assert.Len(t, grouped["even"], 3, "Even group should have 3 items")
	assert.Len(t, grouped["odd"], 3, "Odd group should have 3 items")

	// Test Flatten function
	nested := [][]int{{1, 2}, {3, 4}, {5, 6}}
	flattened := lo.Flatten(nested)
	expected := []int{1, 2, 3, 4, 5, 6}
	assert.Equal(t, expected, flattened, "Should flatten nested arrays")

	// Test Union function
	set1 := []int{1, 2, 3}
	set2 := []int{3, 4, 5}
	union := lo.Union(set1, set2)
	expectedUnion := []int{1, 2, 3, 4, 5}
	assert.Equal(t, expectedUnion, union, "Should create union of arrays")

	// Test Difference function
	diff, _ := lo.Difference(set1, set2)
	expectedDiff := []int{1, 2}
	assert.Equal(t, expectedDiff, diff, "Should find difference between arrays")
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
	t.Logf("Filtered %d items, mapped to %d items, sum: %d", len(filtered), len(mapped), sum)
}

// TestConcurrentOperations tests thread safety of functional operations
func TestConcurrentOperations(t *testing.T) {
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

// TestContextOperations tests context handling
func TestContextOperations(t *testing.T) {
	// Test basic context operations
	ctx := context.Background()
	assert.NotNil(t, ctx, "Background context should not be nil")

	// Test context with timeout
	timeoutCtx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
	defer cancel()

	select {
	case <-time.After(150 * time.Millisecond):
		t.Error("Context should have timed out")
	case <-timeoutCtx.Done():
		assert.Equal(t, context.DeadlineExceeded, timeoutCtx.Err(), "Should be deadline exceeded")
	}

	// Test context with cancellation
	cancelCtx, cancelFunc := context.WithCancel(ctx)

	go func() {
		time.Sleep(50 * time.Millisecond)
		cancelFunc()
	}()

	select {
	case <-time.After(100 * time.Millisecond):
		t.Error("Context should have been cancelled")
	case <-cancelCtx.Done():
		assert.Equal(t, context.Canceled, cancelCtx.Err(), "Should be canceled")
	}

	// Test context with value
	valueCtx := context.WithValue(ctx, "key", "value")
	retrievedValue := valueCtx.Value("key")
	assert.Equal(t, "value", retrievedValue, "Should retrieve context value")
}
