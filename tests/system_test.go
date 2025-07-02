package tests

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

type SystemTestSuite struct {
	suite.Suite
	container *container.Container
	ctx       context.Context
	cancel    context.CancelFunc
}

func (suite *SystemTestSuite) SetupSuite() {
	// Initialize logger for tests
	logging.InitLogger(config.LoggingConfig{
		Level:  "info",
		Format: "json",
	})

	// Create test configuration
	cfg := &config.Config{
		Database: config.DatabaseConfig{
			Driver: "memory", // Use in-memory database for tests
		},
		Features: config.FeatureFlags{
			DatabaseEnabled: false, // Force memory mode
		},
		Server: config.ServerConfig{
			Host: "localhost",
			Port: 8080,
		},
	}

	// Initialize container
	var err error
	suite.container, err = container.NewContainer(cfg)
	require.NoError(suite.T(), err)

	// Create test context
	suite.ctx, suite.cancel = context.WithTimeout(context.Background(), 30*time.Second)
}

func (suite *SystemTestSuite) TearDownSuite() {
	if suite.cancel != nil {
		suite.cancel()
	}
	if suite.container != nil {
		suite.container.Shutdown()
	}
}

func (suite *SystemTestSuite) TestSystemInitialization() {
	// Test that container is properly initialized
	assert.NotNil(suite.T(), suite.container)
	
	// Test that services are available
	pipelineService := suite.container.GetPipelineService()
	assert.NotNil(suite.T(), pipelineService)

	pluginService := suite.container.GetPluginService()
	assert.NotNil(suite.T(), pluginService)

	meltanoService := suite.container.GetMeltanoService()
	assert.NotNil(suite.T(), meltanoService)
}

func (suite *SystemTestSuite) TestSystemHealthCheck() {
	// Test system health check
	err := suite.container.HealthCheck(suite.ctx)
	assert.NoError(suite.T(), err)
}

func (suite *SystemTestSuite) TestBasicPipelineOperations() {
	// Test creating and managing pipelines
	pipeline, err := entities.NewPipeline("system-test-pipeline", "System test pipeline")
	require.NoError(suite.T(), err)

	// Verify pipeline properties
	assert.Equal(suite.T(), "system-test-pipeline", pipeline.Name)
	assert.Equal(suite.T(), "System test pipeline", pipeline.Description)
	assert.False(suite.T(), pipeline.IsActive) // New pipelines start inactive
	assert.Equal(suite.T(), entities.PipelineStatusDraft, pipeline.Status) // Should be draft
	assert.Empty(suite.T(), pipeline.Steps)

	// Test adding a step
	step := entities.PipelineStep{
		Name:          "test-step",
		PluginID:      uuid.New(),
		Configuration: make(map[string]interface{}),
		DependsOn:     make([]uuid.UUID, 0),
	}

	err = pipeline.AddStep(step)
	require.NoError(suite.T(), err)
	assert.Len(suite.T(), pipeline.Steps, 1)
}

func (suite *SystemTestSuite) TestConfigurationManagement() {
	// Test configuration handling
	pipeline, err := entities.NewPipeline("config-test", "Configuration test")
	require.NoError(suite.T(), err)

	// Test pipeline configuration
	pipeline.Configuration["env"] = "test"
	pipeline.Configuration["timeout"] = 300
	pipeline.Configuration["retries"] = 3

	assert.Equal(suite.T(), "test", pipeline.Configuration["env"])
	assert.Equal(suite.T(), 300, pipeline.Configuration["timeout"])
	assert.Equal(suite.T(), 3, pipeline.Configuration["retries"])

	// Test step configuration
	stepConfig := map[string]interface{}{
		"source_table": "input_data",
		"target_table": "output_data",
		"batch_size":   1000,
	}

	step := entities.PipelineStep{
		Name:          "configured-step",
		PluginID:      uuid.New(),
		Configuration: stepConfig,
		DependsOn:     make([]uuid.UUID, 0),
	}

	err = pipeline.AddStep(step)
	require.NoError(suite.T(), err)

	addedStep := pipeline.Steps[0]
	assert.Equal(suite.T(), "input_data", addedStep.Configuration["source_table"])
	assert.Equal(suite.T(), "output_data", addedStep.Configuration["target_table"])
	assert.Equal(suite.T(), 1000, addedStep.Configuration["batch_size"])
}

func (suite *SystemTestSuite) TestMeltanoServiceAvailability() {
	// Test Meltano service is available
	meltanoService := suite.container.GetMeltanoService()
	require.NotNil(suite.T(), meltanoService)

	suite.T().Logf("Meltano service initialized successfully")
}

func (suite *SystemTestSuite) TestSingerManagerAvailability() {
	// Test Singer manager is available
	singerManager := suite.container.GetSingerManager()
	require.NotNil(suite.T(), singerManager)

	suite.T().Logf("Singer manager initialized successfully")
}

func (suite *SystemTestSuite) TestDBTManagerAvailability() {
	// Test DBT manager availability
	dbtManager := suite.container.GetDBTManager()
	if dbtManager != nil {
		suite.T().Logf("DBT manager available")
	} else {
		suite.T().Logf("DBT manager not available (expected in test environment)")
	}
}

func (suite *SystemTestSuite) TestHandlersAvailability() {
	// Test HTTP handlers are available
	pipelineHandler := suite.container.GetPipelineHandler()
	assert.NotNil(suite.T(), pipelineHandler)

	pluginHandler := suite.container.GetPluginHandler()
	assert.NotNil(suite.T(), pluginHandler)

	meltanoHandler := suite.container.GetMeltanoHandler()
	assert.NotNil(suite.T(), meltanoHandler)

	connectorsHandler := suite.container.GetConnectorsHandler()
	assert.NotNil(suite.T(), connectorsHandler)

	suite.T().Logf("All HTTP handlers are available")
}

func (suite *SystemTestSuite) TestSystemConcurrency() {
	// Test system can handle concurrent operations
	const numGoroutines = 10

	done := make(chan bool, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			defer func() { done <- true }()

			// Create pipeline concurrently
			pipeline, err := entities.NewPipeline(
				fmt.Sprintf("concurrent-pipeline-%d", id),
				fmt.Sprintf("Concurrent test pipeline %d", id),
			)
			assert.NoError(suite.T(), err)
			assert.NotNil(suite.T(), pipeline)

			// Add step
			step := entities.PipelineStep{
				Name:          fmt.Sprintf("step-%d", id),
				PluginID:      uuid.New(),
				Configuration: map[string]interface{}{"id": id},
				DependsOn:     make([]uuid.UUID, 0),
			}

			err = pipeline.AddStep(step)
			assert.NoError(suite.T(), err)
		}(i)
	}

	// Wait for all goroutines to complete
	for i := 0; i < numGoroutines; i++ {
		select {
		case <-done:
			// OK
		case <-time.After(5 * time.Second):
			suite.T().Fatal("Timeout waiting for concurrent operations")
		}
	}

	suite.T().Logf("Successfully completed %d concurrent operations", numGoroutines)
}

func (suite *SystemTestSuite) TestSystemIntegrity() {
	// Test system maintains integrity under various operations

	// Create multiple pipelines
	pipelines := make([]*entities.Pipeline, 5)
	for i := 0; i < 5; i++ {
		pipeline, err := entities.NewPipeline(
			fmt.Sprintf("integrity-pipeline-%d", i),
			fmt.Sprintf("Integrity test pipeline %d", i),
		)
		require.NoError(suite.T(), err)
		pipelines[i] = pipeline
	}

	// Add steps to each pipeline
	for i, pipeline := range pipelines {
		for j := 0; j < 3; j++ {
			step := entities.PipelineStep{
				Name:          fmt.Sprintf("step-%d-%d", i, j),
				PluginID:      uuid.New(),
				Configuration: map[string]interface{}{"pipeline": i, "step": j},
				DependsOn:     make([]uuid.UUID, 0),
			}

			err := pipeline.AddStep(step)
			require.NoError(suite.T(), err)
		}
		
		// Activate pipeline after adding steps
		err := pipeline.Activate()
		require.NoError(suite.T(), err)
	}

	// Verify all pipelines are valid
	for i, pipeline := range pipelines {
		assert.Equal(suite.T(), fmt.Sprintf("integrity-pipeline-%d", i), pipeline.Name)
		assert.Len(suite.T(), pipeline.Steps, 3)
		assert.True(suite.T(), pipeline.IsActive)
	}

	suite.T().Logf("System integrity test passed with %d pipelines", len(pipelines))
}

func TestSystemTestSuite(t *testing.T) {
	suite.Run(t, new(SystemTestSuite))
}