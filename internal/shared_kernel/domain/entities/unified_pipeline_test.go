// Package entities provides comprehensive tests for unified pipeline entity
// This implements EXTREME TESTING standards as demanded
package entities

import (
	"context"
	"errors"
	"fmt"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockPipelineRepository is a mock implementation for testing
type MockPipelineRepository struct {
	mock.Mock
}

func (m *MockPipelineRepository) Save(ctx context.Context, pipeline *UnifiedPipeline) error {
	args := m.Called(ctx, pipeline)
	return args.Error(0)
}

func (m *MockPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*UnifiedPipeline, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*UnifiedPipeline), args.Error(1)
}

func (m *MockPipelineRepository) GetByName(ctx context.Context, name string) (*UnifiedPipeline, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*UnifiedPipeline), args.Error(1)
}

func (m *MockPipelineRepository) List(ctx context.Context, filter PipelineFilter) ([]*UnifiedPipeline, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*UnifiedPipeline), args.Error(1)
}

func (m *MockPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// MockStepValidator is a mock implementation for testing
type MockStepValidator struct {
	mock.Mock
}

func (m *MockStepValidator) ValidateStep(step UnifiedPipelineStep) error {
	args := m.Called(step)
	return args.Error(0)
}

func (m *MockStepValidator) ValidateStepOrder(steps []UnifiedPipelineStep) error {
	args := m.Called(steps)
	return args.Error(0)
}

func (m *MockStepValidator) ValidateDependencies(steps []UnifiedPipelineStep) error {
	args := m.Called(steps)
	return args.Error(0)
}

// Test fixtures
func createTestUnifiedPipeline() *UnifiedPipeline {
	pipeline, _ := NewUnifiedPipeline("test-pipeline", "Test pipeline for unit testing")
	pipeline.Type = UnifiedPipelineTypeETL
	pipeline.Status = UnifiedPipelineStatusActive
	pipeline.IsActive = true
	return pipeline
}

func createTestPipelineStep(name string, order int) UnifiedPipelineStep {
	return UnifiedPipelineStep{
		ID:       uuid.New(),
		Name:     name,
		PluginID: uuid.New(),
		Order:    order,
		Configuration: map[string]interface{}{
			"source": "database",
			"table":  "users",
		},
		DependsOn:   []uuid.UUID{},
		IsEnabled:   true,
		RetryConfig: createTestRetryConfig(),
		Timeouts:    createTestTimeouts(),
	}
}

func createTestRetryConfig() RetryConfiguration {
	return RetryConfiguration{
		MaxRetries:      3,
		RetryDelay:      1 * time.Second,
		BackoffStrategy: "exponential",
		RetryConditions: []string{"network_error", "timeout"},
	}
}

func createTestTimeouts() StepTimeouts {
	return StepTimeouts{
		ExecutionTimeout: 300 * time.Second,
		StartupTimeout:   30 * time.Second,
		ShutdownTimeout:  10 * time.Second,
	}
}

func createTestScheduleConfig() ScheduleConfiguration {
	return ScheduleConfiguration{
		Enabled:         true,
		CronExpression:  "0 */15 * * * *", // Every 15 minutes
		Timezone:        "UTC",
		MaxConcurrency:  1,
		Enabled:         true,
		StartDate:       time.Now(),
		RetryOnFailure:  true,
		NotifyOnFailure: true,
	}
}

func createTestResourceLimits() ResourceLimits {
	return ResourceLimits{
		MaxMemoryMB:             1024,
		MaxCPUCores:             2.0,
		MaxDiskSpaceMB:          5120,
		MaxNetworkMBps:          100,
		MaxExecutionTimeSeconds: 3600,
	}
}

// EXTREME TESTING: Constructor Tests
func TestNewUnifiedPipeline_Success(t *testing.T) {
	// Arrange
	name := "test-pipeline"
	description := "Test pipeline for unit testing"

	// Act
	pipeline, err := NewUnifiedPipeline(name, description)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, pipeline)
	assert.Equal(t, name, pipeline.Name)
	assert.Equal(t, description, pipeline.Description)
	assert.Equal(t, UnifiedPipelineTypeGeneric, pipeline.Type)
	assert.Equal(t, UnifiedPipelineStatusDraft, pipeline.Status)
	assert.False(t, pipeline.IsActive)
	assert.NotEqual(t, uuid.Nil, pipeline.ID)
	assert.NotNil(t, pipeline.CreatedAt)
	assert.NotNil(t, pipeline.UpdatedAt)
	assert.Empty(t, pipeline.Steps)
	assert.NotNil(t, pipeline.Metadata)
	assert.NotNil(t, pipeline.Tags)
	assert.NotNil(t, pipeline.Variables)
}

func TestNewUnifiedPipeline_EmptyName(t *testing.T) {
	// Act
	pipeline, err := NewUnifiedPipeline("", "Valid description")

	// Assert
	assert.Error(t, err)
	assert.Nil(t, pipeline)
	assert.Contains(t, err.Error(), "pipeline name cannot be empty")
}

func TestNewUnifiedPipeline_InvalidName(t *testing.T) {
	tests := []struct {
		name        string
		invalidName string
		errorMsg    string
	}{
		{"too short", "ab", "pipeline name must be at least 3 characters"},
		{"too long", string(make([]byte, 101)), "pipeline name cannot exceed 100 characters"},
		{"invalid chars", "test@pipeline!", "pipeline name contains invalid characters"},
		{"starts with number", "123pipeline", "pipeline name cannot start with a number"},
		{"only spaces", "   ", "pipeline name cannot be empty"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			pipeline, err := NewUnifiedPipeline(tt.invalidName, "Valid description")

			// Assert
			assert.Error(t, err)
			assert.Nil(t, pipeline)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

// EXTREME TESTING: Step Management Tests
func TestAddStep_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("extract-step", 1)

	// Act
	err := pipeline.AddStep(step)

	// Assert
	assert.NoError(t, err)
	assert.Len(t, pipeline.Steps, 1)
	assert.Equal(t, "extract-step", pipeline.Steps[0].Name)
	assert.Equal(t, 1, pipeline.Steps[0].Order)
	assert.True(t, pipeline.Steps[0].IsEnabled)
}

func TestAddStep_DuplicateID(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	step2 := createTestPipelineStep("step2", 2)
	step2.ID = step1.ID // Duplicate ID

	pipeline.AddStep(step1)

	// Act
	err := pipeline.AddStep(step2)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step with ID already exists")
	assert.Len(t, pipeline.Steps, 1) // Should still have only the first step
}

func TestAddStep_DuplicateName(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("duplicate-name", 1)
	step2 := createTestPipelineStep("duplicate-name", 2)

	pipeline.AddStep(step1)

	// Act
	err := pipeline.AddStep(step2)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step with name 'duplicate-name' already exists")
	assert.Len(t, pipeline.Steps, 1)
}

func TestAddStep_DuplicateOrder(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	step2 := createTestPipelineStep("step2", 1) // Same order

	pipeline.AddStep(step1)

	// Act
	err := pipeline.AddStep(step2)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step with order 1 already exists")
	assert.Len(t, pipeline.Steps, 1)
}

func TestRemoveStep_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("extract-step", 1)
	pipeline.AddStep(step)

	// Act
	err := pipeline.RemoveStep(step.ID)

	// Assert
	assert.NoError(t, err)
	assert.Empty(t, pipeline.Steps)
}

func TestRemoveStep_NotFound(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	nonExistentID := uuid.New()

	// Act
	err := pipeline.RemoveStep(nonExistentID)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step not found")
}

func TestRemoveStep_WithDependents(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	step2 := createTestPipelineStep("step2", 2)
	step2.DependsOn = []uuid.UUID{step1.ID} // step2 depends on step1

	pipeline.AddStep(step1)
	pipeline.AddStep(step2)

	// Act
	err := pipeline.RemoveStep(step1.ID)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step has dependent steps")
	assert.Len(t, pipeline.Steps, 2) // Both steps should still exist
}

func TestUpdateStep_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("original-step", 1)
	pipeline.AddStep(step)

	updatedStep := step
	updatedStep.Name = "updated-step"
	updatedStep.Configuration["new_param"] = "new_value"

	// Act
	err := pipeline.UpdateStep(updatedStep)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "updated-step", pipeline.Steps[0].Name)
	assert.Equal(t, "new_value", pipeline.Steps[0].Configuration["new_param"])
}

func TestUpdateStep_NotFound(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("step", 1)
	step.ID = uuid.New() // Different ID

	// Act
	err := pipeline.UpdateStep(step)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "step not found")
}

// EXTREME TESTING: Pipeline Status Management Tests
func TestActivate_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Status = UnifiedPipelineStatusDraft
	pipeline.IsActive = false
	step := createTestPipelineStep("step1", 1)
	pipeline.AddStep(step)

	// Act
	err := pipeline.Activate()

	// Assert
	assert.NoError(t, err)
	assert.True(t, pipeline.IsActive)
	assert.Equal(t, UnifiedPipelineStatusActive, pipeline.Status)
	assert.NotNil(t, pipeline.ActivatedAt)
}

func TestActivate_NoSteps(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Status = UnifiedPipelineStatusDraft
	pipeline.IsActive = false
	// No steps added

	// Act
	err := pipeline.Activate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "cannot activate pipeline without steps")
	assert.False(t, pipeline.IsActive)
	assert.Equal(t, UnifiedPipelineStatusDraft, pipeline.Status)
}

func TestActivate_AlreadyActive(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Status = UnifiedPipelineStatusActive
	pipeline.IsActive = true
	step := createTestPipelineStep("step1", 1)
	pipeline.AddStep(step)

	// Act
	err := pipeline.Activate()

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.True(t, pipeline.IsActive)
	assert.Equal(t, UnifiedPipelineStatusActive, pipeline.Status)
}

func TestDeactivate_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Status = UnifiedPipelineStatusActive
	pipeline.IsActive = true
	now := time.Now()
	pipeline.ActivatedAt = &now

	// Act
	err := pipeline.Deactivate()

	// Assert
	assert.NoError(t, err)
	assert.False(t, pipeline.IsActive)
	assert.Equal(t, UnifiedPipelineStatusInactive, pipeline.Status)
	assert.NotNil(t, pipeline.DeactivatedAt)
}

func TestDeactivate_AlreadyInactive(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Status = UnifiedPipelineStatusInactive
	pipeline.IsActive = false

	// Act
	err := pipeline.Deactivate()

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.False(t, pipeline.IsActive)
	assert.Equal(t, UnifiedPipelineStatusInactive, pipeline.Status)
}

// EXTREME TESTING: Validation Tests
func TestValidate_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("extract", 1)
	step2 := createTestPipelineStep("transform", 2)
	step3 := createTestPipelineStep("load", 3)
	step2.DependsOn = []uuid.UUID{step1.ID}
	step3.DependsOn = []uuid.UUID{step2.ID}

	pipeline.AddStep(step1)
	pipeline.AddStep(step2)
	pipeline.AddStep(step3)

	// Act
	err := pipeline.Validate()

	// Assert
	assert.NoError(t, err)
}

func TestValidate_EmptyName(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.Name = ""

	// Act
	err := pipeline.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "pipeline name cannot be empty")
}

func TestValidate_CircularDependency(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	step2 := createTestPipelineStep("step2", 2)
	step1.DependsOn = []uuid.UUID{step2.ID} // step1 depends on step2
	step2.DependsOn = []uuid.UUID{step1.ID} // step2 depends on step1 - circular!

	pipeline.AddStep(step1)
	pipeline.AddStep(step2)

	// Act
	err := pipeline.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "circular dependency detected")
}

func TestValidate_InvalidDependency(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	nonExistentID := uuid.New()
	step1.DependsOn = []uuid.UUID{nonExistentID} // Depends on non-existent step

	pipeline.AddStep(step1)

	// Act
	err := pipeline.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid dependency")
}

func TestValidate_DisabledStepWithDependents(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step1 := createTestPipelineStep("step1", 1)
	step2 := createTestPipelineStep("step2", 2)
	step1.IsEnabled = false                 // Disabled step
	step2.DependsOn = []uuid.UUID{step1.ID} // step2 depends on disabled step1

	pipeline.AddStep(step1)
	pipeline.AddStep(step2)

	// Act
	err := pipeline.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "disabled step has dependent enabled steps")
}

// EXTREME TESTING: Configuration Management Tests
func TestSetSchedule_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	scheduleConfig := createTestScheduleConfig()

	// Act
	err := pipeline.SetSchedule(scheduleConfig)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, pipeline.Schedule)
	assert.True(t, pipeline.Schedule.Enabled)
	assert.Equal(t, "0 */15 * * * *", pipeline.Schedule.CronExpression)
	assert.Equal(t, "UTC", pipeline.Schedule.Timezone)
}

func TestSetSchedule_InvalidCron(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	scheduleConfig := createTestScheduleConfig()
	scheduleConfig.CronExpression = "invalid-cron"

	// Act
	err := pipeline.SetSchedule(scheduleConfig)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid cron expression")
}

func TestSetSchedule_InvalidTimezone(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	scheduleConfig := createTestScheduleConfig()
	scheduleConfig.Timezone = "Invalid/Timezone"

	// Act
	err := pipeline.SetSchedule(scheduleConfig)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid timezone")
}

func TestSetResourceLimits_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	resourceLimits := createTestResourceLimits()

	// Act
	err := pipeline.SetResourceLimits(resourceLimits)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, pipeline.ResourceLimits)
	assert.Equal(t, uint64(1024), pipeline.ResourceLimits.MaxMemoryMB)
	assert.Equal(t, 2.0, pipeline.ResourceLimits.MaxCPUCores)
	assert.Equal(t, uint64(5120), pipeline.ResourceLimits.MaxDiskSpaceMB)
}

func TestSetResourceLimits_InvalidLimits(t *testing.T) {
	tests := []struct {
		name      string
		setLimits func(*ResourceLimits)
		errorMsg  string
	}{
		{
			"negative memory",
			func(rl *ResourceLimits) { rl.MaxMemoryMB = 0 },
			"memory limit must be positive",
		},
		{
			"negative CPU",
			func(rl *ResourceLimits) { rl.MaxCPUCores = 0 },
			"CPU limit must be positive",
		},
		{
			"negative execution time",
			func(rl *ResourceLimits) { rl.MaxExecutionTimeSeconds = 0 },
			"execution time limit must be positive",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			pipeline := createTestUnifiedPipeline()
			resourceLimits := createTestResourceLimits()
			tt.setLimits(&resourceLimits)

			// Act
			err := pipeline.SetResourceLimits(resourceLimits)

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

// EXTREME TESTING: Metadata and Variables Tests
func TestSetVariable_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()

	// Act
	err := pipeline.SetVariable("database_url", "postgres://localhost:5432/testdb")

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "postgres://localhost:5432/testdb", pipeline.Variables["database_url"])
}

func TestSetVariable_InvalidKey(t *testing.T) {
	tests := []struct {
		name string
		key  string
	}{
		{"empty key", ""},
		{"key with spaces", "invalid key"},
		{"key with special chars", "invalid@key!"},
		{"key starting with number", "123key"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			pipeline := createTestUnifiedPipeline()

			// Act
			err := pipeline.SetVariable(tt.key, "value")

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "invalid variable key")
		})
	}
}

func TestGetVariable_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.SetVariable("test_var", "test_value")

	// Act
	value, exists := pipeline.GetVariable("test_var")

	// Assert
	assert.True(t, exists)
	assert.Equal(t, "test_value", value)
}

func TestGetVariable_NotFound(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()

	// Act
	value, exists := pipeline.GetVariable("nonexistent_var")

	// Assert
	assert.False(t, exists)
	assert.Nil(t, value)
}

func TestRemoveVariable_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.SetVariable("temp_var", "temp_value")

	// Act
	pipeline.RemoveVariable("temp_var")

	// Assert
	_, exists := pipeline.GetVariable("temp_var")
	assert.False(t, exists)
}

func TestAddTag_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()

	// Act
	err := pipeline.AddTag("environment:production")

	// Assert
	assert.NoError(t, err)
	assert.Contains(t, pipeline.Tags, "environment:production")
}

func TestAddTag_Duplicate(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.AddTag("existing-tag")

	// Act
	err := pipeline.AddTag("existing-tag")

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.Contains(t, pipeline.Tags, "existing-tag")
	// Should only appear once
	count := 0
	for _, tag := range pipeline.Tags {
		if tag == "existing-tag" {
			count++
		}
	}
	assert.Equal(t, 1, count)
}

func TestRemoveTag_Success(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	pipeline.AddTag("temp-tag")

	// Act
	pipeline.RemoveTag("temp-tag")

	// Assert
	assert.NotContains(t, pipeline.Tags, "temp-tag")
}

// EXTREME TESTING: Clone and Copy Tests
func TestClone_Success(t *testing.T) {
	// Arrange
	original := createTestUnifiedPipeline()
	step := createTestPipelineStep("test-step", 1)
	original.AddStep(step)
	original.SetVariable("test_var", "test_value")
	original.AddTag("test-tag")
	original.Activate()

	// Act
	cloned := original.Clone("cloned-pipeline")

	// Assert
	assert.NotNil(t, cloned)
	assert.Equal(t, "cloned-pipeline", cloned.Name)
	assert.NotEqual(t, original.ID, cloned.ID)
	assert.Equal(t, original.Description, cloned.Description)
	assert.Equal(t, original.Type, cloned.Type)
	assert.Equal(t, UnifiedPipelineStatusDraft, cloned.Status) // Should be reset to draft
	assert.False(t, cloned.IsActive)                           // Should be inactive
	assert.Len(t, cloned.Steps, len(original.Steps))
	assert.Equal(t, original.Variables["test_var"], cloned.Variables["test_var"])
	assert.Contains(t, cloned.Tags, "test-tag")

	// Steps should have new IDs but same configuration
	assert.NotEqual(t, original.Steps[0].ID, cloned.Steps[0].ID)
	assert.Equal(t, original.Steps[0].Name, cloned.Steps[0].Name)
	assert.Equal(t, original.Steps[0].Configuration, cloned.Steps[0].Configuration)
}

// EXTREME TESTING: Domain Events Tests
func TestDomainEvents_PipelineCreated(t *testing.T) {
	// Arrange & Act
	pipeline, _ := NewUnifiedPipeline("test-pipeline", "Test description")

	// Assert
	events := pipeline.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPipelineCreated{}, events[0])

	createdEvent := events[0].(*UnifiedPipelineCreated)
	assert.Equal(t, pipeline.ID, createdEvent.PipelineID)
	assert.Equal(t, "test-pipeline", createdEvent.Name)
}

func TestDomainEvents_PipelineActivated(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("test-step", 1)
	pipeline.AddStep(step)
	pipeline.MarkEventsAsCommitted() // Clear creation events

	// Act
	pipeline.Activate()

	// Assert
	events := pipeline.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPipelineActivated{}, events[0])

	activatedEvent := events[0].(*UnifiedPipelineActivated)
	assert.Equal(t, pipeline.ID, activatedEvent.PipelineID)
	assert.NotNil(t, activatedEvent.ActivatedAt)
}

func TestDomainEvents_StepAdded(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	step := createTestPipelineStep("test-step", 1)
	pipeline.MarkEventsAsCommitted() // Clear creation events

	// Act
	pipeline.AddStep(step)

	// Assert
	events := pipeline.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPipelineStepAdded{}, events[0])

	stepAddedEvent := events[0].(*UnifiedPipelineStepAdded)
	assert.Equal(t, pipeline.ID, stepAddedEvent.PipelineID)
	assert.Equal(t, step.ID, stepAddedEvent.StepID)
	assert.Equal(t, "test-step", stepAddedEvent.StepName)
}

// EXTREME TESTING: Performance and Memory Tests
func TestLargeNumberOfSteps(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	const numSteps = 1000

	// Act - Add many steps
	start := time.Now()
	for i := 0; i < numSteps; i++ {
		step := createTestPipelineStep(fmt.Sprintf("step-%d", i), i+1)
		err := pipeline.AddStep(step)
		assert.NoError(t, err)
	}
	duration := time.Since(start)

	// Assert
	assert.Len(t, pipeline.Steps, numSteps)
	assert.Less(t, duration, 1*time.Second) // Should complete within 1 second

	// Test validation performance
	start = time.Now()
	err := pipeline.Validate()
	duration = time.Since(start)

	assert.NoError(t, err)
	assert.Less(t, duration, 500*time.Millisecond) // Validation should be fast
}

// EXTREME TESTING: Concurrency Tests
func TestConcurrentStepOperations(t *testing.T) {
	// Arrange
	pipeline := createTestUnifiedPipeline()
	const numGoroutines = 10
	ch := make(chan error, numGoroutines)

	// Act - Run concurrent step additions
	for i := 0; i < numGoroutines; i++ {
		go func(index int) {
			step := createTestPipelineStep(fmt.Sprintf("concurrent-step-%d", index), index+1)
			err := pipeline.AddStep(step)
			ch <- err
		}(i)
	}

	// Assert - Collect results
	errorCount := 0
	for i := 0; i < numGoroutines; i++ {
		err := <-ch
		if err != nil {
			errorCount++
		}
	}

	// Some operations may fail due to race conditions, but pipeline should remain consistent
	assert.LessOrEqual(t, len(pipeline.Steps), numGoroutines)
	err := pipeline.Validate()
	assert.NoError(t, err) // Pipeline should still be valid
}

// EXTREME TESTING: Benchmark Tests
func BenchmarkNewUnifiedPipeline(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_, _ = NewUnifiedPipeline(fmt.Sprintf("pipeline-%d", i), "Benchmark pipeline")
	}
}

func BenchmarkAddStep(b *testing.B) {
	pipeline := createTestUnifiedPipeline()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		step := createTestPipelineStep(fmt.Sprintf("step-%d", i), i+1)
		_ = pipeline.AddStep(step)
	}
}

func BenchmarkValidate(b *testing.B) {
	pipeline := createTestUnifiedPipeline()
	// Add some steps for more realistic validation
	for i := 0; i < 100; i++ {
		step := createTestPipelineStep(fmt.Sprintf("step-%d", i), i+1)
		if i > 0 {
			step.DependsOn = []uuid.UUID{pipeline.Steps[i-1].ID}
		}
		pipeline.AddStep(step)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = pipeline.Validate()
	}
}

func BenchmarkClone(b *testing.B) {
	original := createTestUnifiedPipeline()
	// Add some complexity
	for i := 0; i < 50; i++ {
		step := createTestPipelineStep(fmt.Sprintf("step-%d", i), i+1)
		original.AddStep(step)
	}
	original.SetVariable("var1", "value1")
	original.AddTag("tag1")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = original.Clone(fmt.Sprintf("cloned-%d", i))
	}
}
