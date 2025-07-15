// Package entities provides comprehensive tests for unified plugin entity
// This implements EXTREME TESTING standards as demanded
package entities

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockPluginRepository is a mock implementation for testing
type MockUnifiedPluginRepository struct {
	mock.Mock
}

func (m *MockUnifiedPluginRepository) Save(ctx context.Context, plugin *UnifiedPlugin) error {
	args := m.Called(ctx, plugin)
	return args.Error(0)
}

func (m *MockUnifiedPluginRepository) GetByID(ctx context.Context, id uuid.UUID) (*UnifiedPlugin, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*UnifiedPlugin), args.Error(1)
}

func (m *MockUnifiedPluginRepository) GetByName(ctx context.Context, name string) (*UnifiedPlugin, error) {
	args := m.Called(ctx, name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*UnifiedPlugin), args.Error(1)
}

func (m *MockUnifiedPluginRepository) List(ctx context.Context, filter PluginFilter) ([]*UnifiedPlugin, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]*UnifiedPlugin), args.Error(1)
}

func (m *MockUnifiedPluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// MockPluginValidator is a mock implementation for testing
type MockUnifiedPluginValidator struct {
	mock.Mock
}

func (m *MockUnifiedPluginValidator) ValidatePlugin(plugin *UnifiedPlugin) error {
	args := m.Called(plugin)
	return args.Error(0)
}

func (m *MockUnifiedPluginValidator) ValidateConfiguration(config map[string]interface{}) error {
	args := m.Called(config)
	return args.Error(0)
}

func (m *MockUnifiedPluginValidator) ValidateSchema(schema PluginSchema) error {
	args := m.Called(schema)
	return args.Error(0)
}

// MockHealthChecker is a mock implementation for testing
type MockUnifiedPluginHealthChecker struct {
	mock.Mock
}

func (m *MockUnifiedPluginHealthChecker) CheckHealth(ctx context.Context, plugin *UnifiedPlugin) (*PluginHealthStatus, error) {
	args := m.Called(ctx, plugin)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*PluginHealthStatus), args.Error(1)
}

// Test fixtures
func createTestUnifiedPlugin() *UnifiedPlugin {
	plugin, _ := NewUnifiedPlugin("test-plugin", "1.0.0", "./test-plugin", UnifiedPluginTypeSource)
	return plugin
}

func createTestPluginSchema() PluginSchema {
	return PluginSchema{
		InputSchema: map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"source_url": map[string]interface{}{
					"type":        "string",
					"description": "Source URL for data extraction",
				},
				"batch_size": map[string]interface{}{
					"type":    "integer",
					"minimum": 1,
					"maximum": 10000,
				},
			},
			"required": []string{"source_url"},
		},
		OutputSchema: map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"records": map[string]interface{}{
					"type": "array",
					"items": map[string]interface{}{
						"type": "object",
					},
				},
				"record_count": map[string]interface{}{
					"type": "integer",
				},
			},
		},
		ConfigSchema: map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"timeout": map[string]interface{}{
					"type":    "integer",
					"default": 30,
				},
				"retries": map[string]interface{}{
					"type":    "integer",
					"default": 3,
				},
			},
		},
	}
}

func createTestPluginCapabilities() PluginCapabilities {
	return PluginCapabilities{
		SupportsStreaming:    true,
		SupportsBatching:     true,
		SupportsIncremental:  true,
		SupportsParallelism:  true,
		SupportsTransactions: false,
		SupportsRollback:     false,
		MaxConcurrency:       10,
		MaxMemoryMB:          512,
		EstimatedCPUUsage:    0.5,
		SupportedFormats:     []string{"json", "csv", "parquet"},
		RequiredPermissions:  []string{"read:data", "network:outbound"},
	}
}

func createTestPluginDependencies() []PluginDependency {
	return []PluginDependency{
		{
			Name:           "requests",
			Version:        ">=2.25.0",
			Type:           "python",
			Required:       true,
			Description:    "HTTP library for API requests",
			InstallCommand: "pip install requests>=2.25.0",
		},
		{
			Name:           "pandas",
			Version:        ">=1.3.0",
			Type:           "python",
			Required:       false,
			Description:    "Data manipulation library",
			InstallCommand: "pip install pandas>=1.3.0",
		},
	}
}

func createTestSecurityConfig() SecurityConfiguration {
	return SecurityConfiguration{
		AllowedDomains:      []string{"api.example.com", "data.example.org"},
		BlockedDomains:      []string{"malicious.com"},
		AllowedPorts:        []int{80, 443, 8080},
		RequiredPermissions: []string{"network:outbound", "file:read"},
		TrustedCertificates: []string{"cert1.pem", "cert2.pem"},
		AllowInsecureHTTPS:  false,
		Sandboxed:           true,
		ResourceLimits: SecurityResourceLimits{
			MaxMemoryMB:             256,
			MaxCPUPercent:           50,
			MaxFileDescriptors:      100,
			MaxNetworkConnections:   10,
			MaxExecutionTimeSeconds: 300,
		},
	}
}

func createTestMonitoringConfig() MonitoringConfiguration {
	return MonitoringConfiguration{
		Enabled:             true,
		MetricsEnabled:      true,
		TracingEnabled:      true,
		LoggingEnabled:      true,
		HealthCheckEnabled:  true,
		HealthCheckInterval: 30 * time.Second,
		MetricsInterval:     10 * time.Second,
		LogLevel:            "INFO",
		CustomMetrics:       []string{"records_processed", "errors_count"},
		Alerts: []AlertConfiguration{
			{
				Name:      "high_error_rate",
				Condition: "error_rate > 0.1",
				Severity:  "warning",
				Enabled:   true,
			},
		},
	}
}

// EXTREME TESTING: Constructor Tests
func TestNewUnifiedPlugin_Success(t *testing.T) {
	// Arrange
	name := "test-plugin"
	version := "1.0.0"
	path := "./test-plugin"
	pluginType := UnifiedPluginTypeSource

	// Act
	plugin, err := NewUnifiedPlugin(name, version, path, pluginType)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, plugin)
	assert.Equal(t, name, plugin.Name)
	assert.Equal(t, version, plugin.Version)
	assert.Equal(t, path, plugin.Path)
	assert.Equal(t, pluginType, plugin.Type)
	assert.Equal(t, UnifiedPluginStatusRegistered, plugin.Status)
	assert.False(t, plugin.IsActive)
	assert.NotEqual(t, uuid.Nil, plugin.ID)
	assert.NotNil(t, plugin.CreatedAt)
	assert.NotNil(t, plugin.UpdatedAt)
	assert.NotNil(t, plugin.Metadata)
	assert.NotNil(t, plugin.Tags)
	assert.NotNil(t, plugin.Configuration)
}

func TestNewUnifiedPlugin_EmptyName(t *testing.T) {
	// Act
	plugin, err := NewUnifiedPlugin("", "1.0.0", "./test", UnifiedPluginTypeSource)

	// Assert
	assert.Error(t, err)
	assert.Nil(t, plugin)
	assert.Contains(t, err.Error(), "plugin name cannot be empty")
}

func TestNewUnifiedPlugin_InvalidName(t *testing.T) {
	tests := []struct {
		name        string
		invalidName string
		errorMsg    string
	}{
		{"too short", "ab", "plugin name must be at least 3 characters"},
		{"too long", string(make([]byte, 101)), "plugin name cannot exceed 100 characters"},
		{"invalid chars", "test@plugin!", "plugin name contains invalid characters"},
		{"starts with number", "123plugin", "plugin name cannot start with a number"},
		{"only spaces", "   ", "plugin name cannot be empty"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			plugin, err := NewUnifiedPlugin(tt.invalidName, "1.0.0", "./test", UnifiedPluginTypeSource)

			// Assert
			assert.Error(t, err)
			assert.Nil(t, plugin)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

func TestNewUnifiedPlugin_InvalidVersion(t *testing.T) {
	tests := []struct {
		name           string
		invalidVersion string
		errorMsg       string
	}{
		{"empty version", "", "plugin version cannot be empty"},
		{"invalid semver", "1.0", "invalid semantic version"},
		{"invalid format", "v1.0.0", "invalid semantic version"},
		{"non-numeric", "abc.def.ghi", "invalid semantic version"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			plugin, err := NewUnifiedPlugin("test-plugin", tt.invalidVersion, "./test", UnifiedPluginTypeSource)

			// Assert
			assert.Error(t, err)
			assert.Nil(t, plugin)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

func TestNewUnifiedPlugin_InvalidPath(t *testing.T) {
	tests := []struct {
		name        string
		invalidPath string
		errorMsg    string
	}{
		{"empty path", "", "plugin path cannot be empty"},
		{"absolute path required", "relative/path", "plugin path must be absolute or relative with ./"},
		{"invalid chars", "./test\\invalid", "plugin path contains invalid characters"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Act
			plugin, err := NewUnifiedPlugin("test-plugin", "1.0.0", tt.invalidPath, UnifiedPluginTypeSource)

			// Assert
			assert.Error(t, err)
			assert.Nil(t, plugin)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

// EXTREME TESTING: Status Management Tests
func TestUnifiedPlugin_Activate_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Status = UnifiedPluginStatusRegistered

	// Act
	err := plugin.Activate()

	// Assert
	assert.NoError(t, err)
	assert.True(t, plugin.IsActive)
	assert.Equal(t, UnifiedPluginStatusActive, plugin.Status)
	assert.NotNil(t, plugin.ActivatedAt)
}

func TestActivate_InvalidStatus(t *testing.T) {
	tests := []struct {
		name   string
		status UnifiedPluginStatus
	}{
		{"failed status", UnifiedPluginStatusFailed},
		{"uninstalled status", UnifiedPluginStatusUninstalled},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			plugin := createTestUnifiedPlugin()
			plugin.Status = tt.status

			// Act
			err := plugin.Activate()

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "cannot activate plugin")
			assert.False(t, plugin.IsActive)
		})
	}
}

func TestUnifiedPlugin_Activate_AlreadyActive(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Status = UnifiedPluginStatusActive
	plugin.IsActive = true
	now := time.Now()
	plugin.ActivatedAt = &now

	// Act
	err := plugin.Activate()

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.True(t, plugin.IsActive)
	assert.Equal(t, UnifiedPluginStatusActive, plugin.Status)
}

func TestUnifiedPlugin_Deactivate_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Status = UnifiedPluginStatusActive
	plugin.IsActive = true
	now := time.Now()
	plugin.ActivatedAt = &now

	// Act
	err := plugin.Deactivate()

	// Assert
	assert.NoError(t, err)
	assert.False(t, plugin.IsActive)
	assert.Equal(t, UnifiedPluginStatusInactive, plugin.Status)
	assert.NotNil(t, plugin.DeactivatedAt)
}

func TestUnifiedPlugin_Deactivate_AlreadyInactive(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Status = UnifiedPluginStatusInactive
	plugin.IsActive = false

	// Act
	err := plugin.Deactivate()

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.False(t, plugin.IsActive)
	assert.Equal(t, UnifiedPluginStatusInactive, plugin.Status)
}

func TestMarkAsFailed_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Status = UnifiedPluginStatusActive
	errorMsg := "Plugin execution failed"

	// Act
	plugin.MarkAsFailed(errorMsg)

	// Assert
	assert.False(t, plugin.IsActive)
	assert.Equal(t, UnifiedPluginStatusFailed, plugin.Status)
	assert.Equal(t, errorMsg, plugin.LastError)
	assert.NotNil(t, plugin.LastErrorAt)
}

// EXTREME TESTING: Configuration Management Tests
func TestSetConfiguration_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	config := map[string]interface{}{
		"timeout":    30,
		"retries":    3,
		"batch_size": 1000,
	}

	// Act
	err := plugin.SetConfiguration(config)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, 30, plugin.Configuration["timeout"])
	assert.Equal(t, 3, plugin.Configuration["retries"])
	assert.Equal(t, 1000, plugin.Configuration["batch_size"])
}

func TestSetConfiguration_NilConfig(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()

	// Act
	err := plugin.SetConfiguration(nil)

	// Assert
	assert.NoError(t, err)
	assert.Empty(t, plugin.Configuration)
}

func TestSetConfiguration_OverwriteExisting(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Configuration["existing_key"] = "existing_value"
	newConfig := map[string]interface{}{
		"new_key": "new_value",
	}

	// Act
	err := plugin.SetConfiguration(newConfig)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "new_value", plugin.Configuration["new_key"])
	_, exists := plugin.Configuration["existing_key"]
	assert.False(t, exists) // Should be overwritten, not merged
}

func TestUpdateConfiguration_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Configuration["existing_key"] = "existing_value"
	updates := map[string]interface{}{
		"new_key":      "new_value",
		"existing_key": "updated_value",
	}

	// Act
	err := plugin.UpdateConfiguration(updates)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "updated_value", plugin.Configuration["existing_key"])
	assert.Equal(t, "new_value", plugin.Configuration["new_key"])
}

func TestGetConfigurationValue_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Configuration["test_key"] = "test_value"

	// Act
	value, exists := plugin.GetConfigurationValue("test_key")

	// Assert
	assert.True(t, exists)
	assert.Equal(t, "test_value", value)
}

func TestGetConfigurationValue_NotFound(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()

	// Act
	value, exists := plugin.GetConfigurationValue("nonexistent_key")

	// Assert
	assert.False(t, exists)
	assert.Nil(t, value)
}

// EXTREME TESTING: Schema Management Tests
func TestSetSchema_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()

	// Act
	err := plugin.SetSchema(schema)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, plugin.Schema)
	assert.Equal(t, schema.InputSchema, plugin.Schema.InputSchema)
	assert.Equal(t, schema.OutputSchema, plugin.Schema.OutputSchema)
	assert.Equal(t, schema.ConfigSchema, plugin.Schema.ConfigSchema)
}

func TestSetSchema_InvalidInputSchema(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	schema.InputSchema = map[string]interface{}{
		"type": "invalid_type", // Invalid JSON schema type
	}

	// Act
	err := plugin.SetSchema(schema)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid input schema")
}

func TestValidateInputData_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	plugin.SetSchema(schema)

	inputData := map[string]interface{}{
		"source_url": "https://api.example.com/data",
		"batch_size": 1000,
	}

	// Act
	err := plugin.ValidateInputData(inputData)

	// Assert
	assert.NoError(t, err)
}

func TestValidateInputData_MissingRequiredField(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	plugin.SetSchema(schema)

	inputData := map[string]interface{}{
		"batch_size": 1000,
		// Missing required "source_url"
	}

	// Act
	err := plugin.ValidateInputData(inputData)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "missing required field")
}

func TestValidateInputData_NoSchema(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	// No schema set

	inputData := map[string]interface{}{
		"any_key": "any_value",
	}

	// Act
	err := plugin.ValidateInputData(inputData)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "no input schema defined")
}

// EXTREME TESTING: Capabilities Management Tests
func TestSetCapabilities_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	capabilities := createTestPluginCapabilities()

	// Act
	err := plugin.SetCapabilities(capabilities)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, plugin.Capabilities)
	assert.True(t, plugin.Capabilities.SupportsStreaming)
	assert.True(t, plugin.Capabilities.SupportsBatching)
	assert.Equal(t, 10, plugin.Capabilities.MaxConcurrency)
	assert.Equal(t, uint64(512), plugin.Capabilities.MaxMemoryMB)
}

func TestSetCapabilities_InvalidLimits(t *testing.T) {
	tests := []struct {
		name          string
		setCapability func(*PluginCapabilities)
		errorMsg      string
	}{
		{
			"negative max concurrency",
			func(cap *PluginCapabilities) { cap.MaxConcurrency = -1 },
			"max concurrency must be positive",
		},
		{
			"zero max memory",
			func(cap *PluginCapabilities) { cap.MaxMemoryMB = 0 },
			"max memory must be positive",
		},
		{
			"invalid CPU usage",
			func(cap *PluginCapabilities) { cap.EstimatedCPUUsage = -0.5 },
			"CPU usage must be between 0 and 1",
		},
		{
			"CPU usage over 100%",
			func(cap *PluginCapabilities) { cap.EstimatedCPUUsage = 1.5 },
			"CPU usage must be between 0 and 1",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			plugin := createTestUnifiedPlugin()
			capabilities := createTestPluginCapabilities()
			tt.setCapability(&capabilities)

			// Act
			err := plugin.SetCapabilities(capabilities)

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

func TestSupportsFormat_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	capabilities := createTestPluginCapabilities()
	plugin.SetCapabilities(capabilities)

	// Act & Assert
	assert.True(t, plugin.SupportsFormat("json"))
	assert.True(t, plugin.SupportsFormat("csv"))
	assert.True(t, plugin.SupportsFormat("parquet"))
	assert.False(t, plugin.SupportsFormat("xml"))
}

func TestSupportsFormat_NoCapabilities(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	// No capabilities set

	// Act & Assert
	assert.False(t, plugin.SupportsFormat("json"))
}

func TestHasPermission_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	capabilities := createTestPluginCapabilities()
	plugin.SetCapabilities(capabilities)

	// Act & Assert
	assert.True(t, plugin.HasPermission("read:data"))
	assert.True(t, plugin.HasPermission("network:outbound"))
	assert.False(t, plugin.HasPermission("write:system"))
}

// EXTREME TESTING: Dependencies Management Tests
func TestSetDependencies_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	dependencies := createTestPluginDependencies()

	// Act
	err := plugin.SetDependencies(dependencies)

	// Assert
	assert.NoError(t, err)
	assert.Len(t, plugin.Dependencies, 2)
	assert.Equal(t, "requests", plugin.Dependencies[0].Name)
	assert.Equal(t, ">=2.25.0", plugin.Dependencies[0].Version)
	assert.True(t, plugin.Dependencies[0].Required)
}

func TestSetDependencies_InvalidDependency(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	dependencies := []PluginDependency{
		{
			Name:    "", // Empty name
			Version: "1.0.0",
			Type:    "python",
		},
	}

	// Act
	err := plugin.SetDependencies(dependencies)

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "dependency name cannot be empty")
}

func TestGetRequiredDependencies_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	dependencies := createTestPluginDependencies()
	plugin.SetDependencies(dependencies)

	// Act
	requiredDeps := plugin.GetRequiredDependencies()

	// Assert
	assert.Len(t, requiredDeps, 1) // Only "requests" is required
	assert.Equal(t, "requests", requiredDeps[0].Name)
}

func TestGetOptionalDependencies_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	dependencies := createTestPluginDependencies()
	plugin.SetDependencies(dependencies)

	// Act
	optionalDeps := plugin.GetOptionalDependencies()

	// Assert
	assert.Len(t, optionalDeps, 1) // Only "pandas" is optional
	assert.Equal(t, "pandas", optionalDeps[0].Name)
}

// EXTREME TESTING: Security Configuration Tests
func TestSetSecurityConfiguration_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	securityConfig := createTestSecurityConfig()

	// Act
	err := plugin.SetSecurityConfiguration(securityConfig)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, plugin.Security)
	assert.Contains(t, plugin.Security.AllowedDomains, "api.example.com")
	assert.Contains(t, plugin.Security.BlockedDomains, "malicious.com")
	assert.True(t, plugin.Security.Sandboxed)
	assert.False(t, plugin.Security.AllowInsecureHTTPS)
}

func TestSetSecurityConfiguration_InvalidConfig(t *testing.T) {
	tests := []struct {
		name      string
		setConfig func(*SecurityConfiguration)
		errorMsg  string
	}{
		{
			"empty allowed domains with blocked domains",
			func(sc *SecurityConfiguration) {
				sc.AllowedDomains = []string{}
				sc.BlockedDomains = []string{"malicious.com"}
			},
			"cannot have blocked domains without allowed domains",
		},
		{
			"invalid port range",
			func(sc *SecurityConfiguration) {
				sc.AllowedPorts = []int{-1, 65536}
			},
			"invalid port number",
		},
		{
			"zero memory limit",
			func(sc *SecurityConfiguration) {
				sc.ResourceLimits.MaxMemoryMB = 0
			},
			"memory limit must be positive",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			plugin := createTestUnifiedPlugin()
			securityConfig := createTestSecurityConfig()
			tt.setConfig(&securityConfig)

			// Act
			err := plugin.SetSecurityConfiguration(securityConfig)

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

func TestIsDomainAllowed_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	securityConfig := createTestSecurityConfig()
	plugin.SetSecurityConfiguration(securityConfig)

	// Act & Assert
	assert.True(t, plugin.IsDomainAllowed("api.example.com"))
	assert.True(t, plugin.IsDomainAllowed("data.example.org"))
	assert.False(t, plugin.IsDomainAllowed("malicious.com"))
	assert.False(t, plugin.IsDomainAllowed("unknown.com"))
}

func TestIsPortAllowed_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	securityConfig := createTestSecurityConfig()
	plugin.SetSecurityConfiguration(securityConfig)

	// Act & Assert
	assert.True(t, plugin.IsPortAllowed(80))
	assert.True(t, plugin.IsPortAllowed(443))
	assert.True(t, plugin.IsPortAllowed(8080))
	assert.False(t, plugin.IsPortAllowed(22))
	assert.False(t, plugin.IsPortAllowed(3306))
}

// EXTREME TESTING: Monitoring Configuration Tests
func TestSetMonitoringConfiguration_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	monitoringConfig := createTestMonitoringConfig()

	// Act
	err := plugin.SetMonitoringConfiguration(monitoringConfig)

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, plugin.Monitoring)
	assert.True(t, plugin.Monitoring.Enabled)
	assert.True(t, plugin.Monitoring.MetricsEnabled)
	assert.Equal(t, 30*time.Second, plugin.Monitoring.HealthCheckInterval)
	assert.Equal(t, "INFO", plugin.Monitoring.LogLevel)
	assert.Len(t, plugin.Monitoring.Alerts, 1)
}

func TestSetMonitoringConfiguration_InvalidConfig(t *testing.T) {
	tests := []struct {
		name      string
		setConfig func(*MonitoringConfiguration)
		errorMsg  string
	}{
		{
			"invalid log level",
			func(mc *MonitoringConfiguration) {
				mc.LogLevel = "INVALID"
			},
			"invalid log level",
		},
		{
			"invalid health check interval",
			func(mc *MonitoringConfiguration) {
				mc.HealthCheckInterval = -1 * time.Second
			},
			"health check interval must be positive",
		},
		{
			"invalid metrics interval",
			func(mc *MonitoringConfiguration) {
				mc.MetricsInterval = 0
			},
			"metrics interval must be positive",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Arrange
			plugin := createTestUnifiedPlugin()
			monitoringConfig := createTestMonitoringConfig()
			tt.setConfig(&monitoringConfig)

			// Act
			err := plugin.SetMonitoringConfiguration(monitoringConfig)

			// Assert
			assert.Error(t, err)
			assert.Contains(t, err.Error(), tt.errorMsg)
		})
	}
}

// EXTREME TESTING: Metadata and Tags Tests
func TestSetMetadata_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	metadata := map[string]interface{}{
		"author":      "Test Author",
		"description": "Test plugin for unit testing",
		"category":    "data-extraction",
		"license":     "MIT",
	}

	// Act
	err := plugin.SetMetadata(metadata)

	// Assert
	assert.NoError(t, err)
	assert.Equal(t, "Test Author", plugin.Metadata["author"])
	assert.Equal(t, "Test plugin for unit testing", plugin.Metadata["description"])
	assert.Equal(t, "data-extraction", plugin.Metadata["category"])
	assert.Equal(t, "MIT", plugin.Metadata["license"])
}

func TestSetMetadata_NilMetadata(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Metadata["existing"] = "value"

	// Act
	err := plugin.SetMetadata(nil)

	// Assert
	assert.NoError(t, err)
	assert.Empty(t, plugin.Metadata)
}

func TestGetMetadataValue_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Metadata["test_key"] = "test_value"

	// Act
	value, exists := plugin.GetMetadataValue("test_key")

	// Assert
	assert.True(t, exists)
	assert.Equal(t, "test_value", value)
}

func TestGetMetadataValue_NotFound(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()

	// Act
	value, exists := plugin.GetMetadataValue("nonexistent_key")

	// Assert
	assert.False(t, exists)
	assert.Nil(t, value)
}

func TestUnifiedPlugin_AddTag_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()

	// Act
	err := plugin.AddTag("data-source")

	// Assert
	assert.NoError(t, err)
	assert.Contains(t, plugin.Tags, "data-source")
}

func TestUnifiedPlugin_AddTag_Duplicate(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.AddTag("existing-tag")

	// Act
	err := plugin.AddTag("existing-tag")

	// Assert
	assert.NoError(t, err) // Should be idempotent
	assert.Contains(t, plugin.Tags, "existing-tag")
	// Should only appear once
	count := 0
	for _, tag := range plugin.Tags {
		if tag == "existing-tag" {
			count++
		}
	}
	assert.Equal(t, 1, count)
}

func TestUnifiedPlugin_RemoveTag_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.AddTag("temp-tag")

	// Act
	plugin.RemoveTag("temp-tag")

	// Assert
	assert.NotContains(t, plugin.Tags, "temp-tag")
}

func TestHasTag_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.AddTag("test-tag")

	// Act & Assert
	assert.True(t, plugin.HasTag("test-tag"))
	assert.False(t, plugin.HasTag("nonexistent-tag"))
}

// EXTREME TESTING: Validation Tests
func TestUnifiedPlugin_Validate_Success(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	capabilities := createTestPluginCapabilities()
	dependencies := createTestPluginDependencies()

	plugin.SetSchema(schema)
	plugin.SetCapabilities(capabilities)
	plugin.SetDependencies(dependencies)

	// Act
	err := plugin.Validate()

	// Assert
	assert.NoError(t, err)
}

func TestUnifiedPlugin_Validate_EmptyName(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Name = ""

	// Act
	err := plugin.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "plugin name cannot be empty")
}

func TestValidate_InvalidVersion(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Version = "invalid-version"

	// Act
	err := plugin.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "invalid plugin version")
}

func TestValidate_EmptyPath(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Path = ""

	// Act
	err := plugin.Validate()

	// Assert
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "plugin path cannot be empty")
}

// EXTREME TESTING: Clone and Copy Tests
func TestUnifiedPlugin_Clone_Success(t *testing.T) {
	// Arrange
	original := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	capabilities := createTestPluginCapabilities()
	dependencies := createTestPluginDependencies()

	original.SetSchema(schema)
	original.SetCapabilities(capabilities)
	original.SetDependencies(dependencies)
	original.SetConfiguration(map[string]interface{}{"key": "value"})
	original.AddTag("test-tag")
	original.Activate()

	// Act
	cloned := original.Clone("cloned-plugin", "2.0.0")

	// Assert
	assert.NotNil(t, cloned)
	assert.Equal(t, "cloned-plugin", cloned.Name)
	assert.Equal(t, "2.0.0", cloned.Version)
	assert.NotEqual(t, original.ID, cloned.ID)
	assert.Equal(t, original.Path, cloned.Path)
	assert.Equal(t, original.Type, cloned.Type)
	assert.Equal(t, UnifiedPluginStatusRegistered, cloned.Status) // Should be reset
	assert.False(t, cloned.IsActive)                              // Should be inactive

	// Configuration should be copied
	assert.Equal(t, original.Configuration["key"], cloned.Configuration["key"])

	// Tags should be copied
	assert.Contains(t, cloned.Tags, "test-tag")

	// Schema should be copied
	assert.Equal(t, original.Schema.InputSchema, cloned.Schema.InputSchema)

	// Capabilities should be copied
	assert.Equal(t, original.Capabilities.SupportsStreaming, cloned.Capabilities.SupportsStreaming)

	// Dependencies should be copied
	assert.Len(t, cloned.Dependencies, len(original.Dependencies))
}

// EXTREME TESTING: Domain Events Tests
func TestDomainEvents_PluginCreated(t *testing.T) {
	// Arrange & Act
	plugin, _ := NewUnifiedPlugin("test-plugin", "1.0.0", "./test", UnifiedPluginTypeSource)

	// Assert
	events := plugin.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPluginCreated{}, events[0])

	createdEvent := events[0].(*UnifiedPluginCreated)
	assert.Equal(t, plugin.ID, createdEvent.PluginID)
	assert.Equal(t, "test-plugin", createdEvent.Name)
	assert.Equal(t, "1.0.0", createdEvent.Version)
}

func TestDomainEvents_PluginActivated(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.MarkEventsAsCommitted() // Clear creation events

	// Act
	plugin.Activate()

	// Assert
	events := plugin.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPluginActivated{}, events[0])

	activatedEvent := events[0].(*UnifiedPluginActivated)
	assert.Equal(t, plugin.ID, activatedEvent.PluginID)
	assert.NotNil(t, activatedEvent.ActivatedAt)
}

func TestDomainEvents_PluginDeactivated(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Activate()
	plugin.MarkEventsAsCommitted() // Clear previous events

	// Act
	plugin.Deactivate()

	// Assert
	events := plugin.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPluginDeactivated{}, events[0])

	deactivatedEvent := events[0].(*UnifiedPluginDeactivated)
	assert.Equal(t, plugin.ID, deactivatedEvent.PluginID)
	assert.NotNil(t, deactivatedEvent.DeactivatedAt)
}

func TestDomainEvents_PluginFailed(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	plugin.Activate()
	plugin.MarkEventsAsCommitted() // Clear previous events
	errorMsg := "Plugin execution failed"

	// Act
	plugin.MarkAsFailed(errorMsg)

	// Assert
	events := plugin.GetUncommittedEvents()
	assert.Len(t, events, 1)
	assert.IsType(t, &UnifiedPluginFailed{}, events[0])

	failedEvent := events[0].(*UnifiedPluginFailed)
	assert.Equal(t, plugin.ID, failedEvent.PluginID)
	assert.Equal(t, errorMsg, failedEvent.Error)
	assert.NotNil(t, failedEvent.FailedAt)
}

// EXTREME TESTING: Performance and Memory Tests
func TestLargeConfiguration(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	largeConfig := make(map[string]interface{})

	// Create a large configuration with 10,000 entries
	for i := 0; i < 10000; i++ {
		largeConfig[fmt.Sprintf("key_%d", i)] = fmt.Sprintf("value_%d", i)
	}

	// Act
	start := time.Now()
	err := plugin.SetConfiguration(largeConfig)
	duration := time.Since(start)

	// Assert
	assert.NoError(t, err)
	assert.Len(t, plugin.Configuration, 10000)
	assert.Less(t, duration, 100*time.Millisecond) // Should be fast

	// Test access performance
	start = time.Now()
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key_%d", i)
		_, exists := plugin.GetConfigurationValue(key)
		assert.True(t, exists)
	}
	duration = time.Since(start)
	assert.Less(t, duration, 10*time.Millisecond) // Access should be very fast
}

func TestManyTags(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	const numTags = 1000

	// Act - Add many tags
	start := time.Now()
	for i := 0; i < numTags; i++ {
		err := plugin.AddTag(fmt.Sprintf("tag-%d", i))
		assert.NoError(t, err)
	}
	duration := time.Since(start)

	// Assert
	assert.Len(t, plugin.Tags, numTags)
	assert.Less(t, duration, 100*time.Millisecond) // Should complete quickly

	// Test tag lookup performance
	start = time.Now()
	for i := 0; i < 100; i++ {
		tagName := fmt.Sprintf("tag-%d", i)
		assert.True(t, plugin.HasTag(tagName))
	}
	duration = time.Since(start)
	assert.Less(t, duration, 10*time.Millisecond) // Lookup should be fast
}

// EXTREME TESTING: Concurrency Tests
func TestConcurrentConfigurationOperations(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	const numGoroutines = 10
	ch := make(chan error, numGoroutines)

	// Act - Run concurrent configuration updates
	for i := 0; i < numGoroutines; i++ {
		go func(index int) {
			config := map[string]interface{}{
				fmt.Sprintf("key_%d", index): fmt.Sprintf("value_%d", index),
			}
			err := plugin.UpdateConfiguration(config)
			ch <- err
		}(i)
	}

	// Assert - Collect results
	for i := 0; i < numGoroutines; i++ {
		err := <-ch
		assert.NoError(t, err)
	}

	// All updates should be present
	assert.GreaterOrEqual(t, len(plugin.Configuration), numGoroutines)
}

func TestConcurrentTagOperations(t *testing.T) {
	// Arrange
	plugin := createTestUnifiedPlugin()
	const numGoroutines = 20
	ch := make(chan error, numGoroutines)

	// Act - Run concurrent tag operations
	for i := 0; i < numGoroutines; i++ {
		go func(index int) {
			tagName := fmt.Sprintf("concurrent-tag-%d", index)
			err := plugin.AddTag(tagName)
			ch <- err
		}(i)
	}

	// Assert - Collect results
	for i := 0; i < numGoroutines; i++ {
		err := <-ch
		assert.NoError(t, err)
	}

	// All tags should be present
	assert.GreaterOrEqual(t, len(plugin.Tags), numGoroutines)
}

// EXTREME TESTING: Benchmark Tests
func BenchmarkNewUnifiedPlugin(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_, _ = NewUnifiedPlugin(
			fmt.Sprintf("plugin-%d", i),
			"1.0.0",
			"./test",
			UnifiedPluginTypeSource,
		)
	}
}

func BenchmarkSetConfiguration(b *testing.B) {
	plugin := createTestUnifiedPlugin()
	config := map[string]interface{}{
		"timeout":    30,
		"retries":    3,
		"batch_size": 1000,
		"workers":    5,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = plugin.SetConfiguration(config)
	}
}

func BenchmarkGetConfigurationValue(b *testing.B) {
	plugin := createTestUnifiedPlugin()
	plugin.SetConfiguration(map[string]interface{}{
		"test_key": "test_value",
	})

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = plugin.GetConfigurationValue("test_key")
	}
}

func BenchmarkAddTag(b *testing.B) {
	plugin := createTestUnifiedPlugin()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = plugin.AddTag(fmt.Sprintf("tag-%d", i))
	}
}

func BenchmarkHasTag(b *testing.B) {
	plugin := createTestUnifiedPlugin()
	// Pre-populate with tags
	for i := 0; i < 100; i++ {
		plugin.AddTag(fmt.Sprintf("tag-%d", i))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = plugin.HasTag(fmt.Sprintf("tag-%d", i%100))
	}
}

func BenchmarkUnifiedPlugin_Validate(b *testing.B) {
	plugin := createTestUnifiedPlugin()
	schema := createTestPluginSchema()
	capabilities := createTestPluginCapabilities()
	dependencies := createTestPluginDependencies()

	plugin.SetSchema(schema)
	plugin.SetCapabilities(capabilities)
	plugin.SetDependencies(dependencies)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = plugin.Validate()
	}
}

func BenchmarkUnifiedPlugin_Clone(b *testing.B) {
	original := createTestUnifiedPlugin()
	// Add complexity
	schema := createTestPluginSchema()
	capabilities := createTestPluginCapabilities()
	dependencies := createTestPluginDependencies()

	original.SetSchema(schema)
	original.SetCapabilities(capabilities)
	original.SetDependencies(dependencies)
	original.SetConfiguration(map[string]interface{}{
		"key1": "value1",
		"key2": "value2",
	})
	original.AddTag("tag1")
	original.AddTag("tag2")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = original.Clone(fmt.Sprintf("cloned-%d", i), "2.0.0")
	}
}
