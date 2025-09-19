// Package plugins - FLEXT Distributed Plugin System
//
// This package implements the core plugin architecture for the FLEXT ecosystem,
// enabling deployable plugins (Meltano, Ray, Kubernetes) to be distributed from
// FLEXT Service (Control Panel) to multiple FlexCore instances (Distributed Runtime).
//
// Architecture:
//   - FLEXT Service: Plugin registry, deployment manager, lifecycle management
//   - FlexCore Instances: Plugin runtime engine, loader, execution environment
//   - Plugins: Deployable .so/.dll files with standardized interfaces
//
// Plugin Types:
//   - meltano-plugin.so: Singer taps/targets + DBT + Meltano orchestration
//   - ray-plugin.so: Distributed computing runtime with Ray integration
//   - kubernetes-plugin.so: Container orchestration and management
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package plugins

import (
	"context"
	"time"
)

// PluginID represents a unique plugin identifier
type PluginID string

// PluginType represents the type/category of plugin
type PluginType string

const (
	// PluginTypeMeltano - Data integration plugin (Singer + DBT + Meltano)
	PluginTypeMeltano PluginType = "meltano"
	
	// PluginTypeRay - Distributed computing plugin 
	PluginTypeRay PluginType = "ray"
	
	// PluginTypeKubernetes - Container orchestration plugin
	PluginTypeKubernetes PluginType = "kubernetes"
)

// PluginStatus represents the current status of a plugin
type PluginStatus string

const (
	// PluginStatusRegistered - Plugin is registered but not deployed
	PluginStatusRegistered PluginStatus = "registered"
	
	// PluginStatusDeployed - Plugin is deployed to FlexCore instances
	PluginStatusDeployed PluginStatus = "deployed"
	
	// PluginStatusRunning - Plugin is actively running
	PluginStatusRunning PluginStatus = "running"
	
	// PluginStatusStopped - Plugin is stopped but still deployed
	PluginStatusStopped PluginStatus = "stopped"
	
	// PluginStatusError - Plugin is in error state
	PluginStatusError PluginStatus = "error"
	
	// PluginStatusUndeploying - Plugin is being removed
	PluginStatusUndeploying PluginStatus = "undeploying"
)

// PluginMetadata contains plugin information and capabilities
type PluginMetadata struct {
	ID           PluginID               `json:"id"`
	Name         string                 `json:"name"`
	Type         PluginType             `json:"type"`
	Version      string                 `json:"version"`
	Description  string                 `json:"description"`
	Author       string                 `json:"author"`
	Capabilities []string               `json:"capabilities"`
	Dependencies []string               `json:"dependencies"`
	Config       map[string]interface{} `json:"config"`
	CreatedAt    time.Time              `json:"created_at"`
	UpdatedAt    time.Time              `json:"updated_at"`
}

// PluginDeployment represents a plugin deployment to FlexCore instances
type PluginDeployment struct {
	PluginID        PluginID              `json:"plugin_id"`
	FlexCoreNodes   []string              `json:"flexcore_nodes"`
	Status          PluginStatus          `json:"status"`
	Config          map[string]interface{} `json:"config"`
	DeployedAt      time.Time             `json:"deployed_at"`
	LastHealthCheck time.Time             `json:"last_health_check"`
	HealthStatus    string                `json:"health_status"`
	ErrorMessage    string                `json:"error_message,omitempty"`
}

// PluginExecutionRequest represents a request to execute a plugin
type PluginExecutionRequest struct {
	PluginID     PluginID               `json:"plugin_id"`
	FlexCoreNode string                 `json:"flexcore_node"`
	Operation    string                 `json:"operation"`
	Parameters   map[string]interface{} `json:"parameters"`
	Timeout      time.Duration          `json:"timeout"`
	Async        bool                   `json:"async"`
}

// PluginExecutionResult represents the result of plugin execution
type PluginExecutionResult struct {
	PluginID      PluginID               `json:"plugin_id"`
	FlexCoreNode  string                 `json:"flexcore_node"`
	Operation     string                 `json:"operation"`
	Success       bool                   `json:"success"`
	Result        map[string]interface{} `json:"result"`
	ErrorMessage  string                 `json:"error_message,omitempty"`
	StartedAt     time.Time              `json:"started_at"`
	CompletedAt   time.Time              `json:"completed_at"`
	Duration      time.Duration          `json:"duration"`
}

// Plugin interface - ALL deployable plugins must implement this interface
type Plugin interface {
	// Metadata returns plugin information and capabilities
	Metadata() PluginMetadata

	// Initialize sets up the plugin with configuration
	Initialize(ctx context.Context, config map[string]interface{}) error

	// Execute performs the requested operation with parameters
	Execute(ctx context.Context, operation string, params map[string]interface{}) (map[string]interface{}, error)

	// Health returns the current health status of the plugin
	Health(ctx context.Context) (map[string]interface{}, error)

	// Shutdown gracefully shuts down the plugin
	Shutdown(ctx context.Context) error

	// GetCapabilities returns the list of operations this plugin supports
	GetCapabilities() []string

	// ValidateConfig validates the provided configuration
	ValidateConfig(config map[string]interface{}) error
}

// PluginRegistry interface - Manages plugin registration and discovery
type PluginRegistry interface {
	// RegisterPlugin registers a new plugin
	RegisterPlugin(plugin Plugin) error

	// UnregisterPlugin removes a plugin from registry
	UnregisterPlugin(pluginID PluginID) error

	// GetPlugin retrieves a plugin by ID
	GetPlugin(pluginID PluginID) (Plugin, error)

	// ListPlugins returns all registered plugins
	ListPlugins() ([]PluginMetadata, error)

	// ListPluginsByType returns plugins of specific type
	ListPluginsByType(pluginType PluginType) ([]PluginMetadata, error)

	// FindPluginsByCapability finds plugins with specific capability
	FindPluginsByCapability(capability string) ([]PluginMetadata, error)
}

// PluginDeploymentManager interface - Manages plugin deployment to FlexCore instances
type PluginDeploymentManager interface {
	// DeployPlugin deploys a plugin to specified FlexCore instances
	DeployPlugin(ctx context.Context, pluginID PluginID, nodes []string, config map[string]interface{}) error

	// UndeployPlugin removes a plugin from FlexCore instances
	UndeployPlugin(ctx context.Context, pluginID PluginID, nodes []string) error

	// GetDeploymentStatus returns deployment status for a plugin
	GetDeploymentStatus(pluginID PluginID) ([]PluginDeployment, error)

	// ListDeployments returns all plugin deployments
	ListDeployments() ([]PluginDeployment, error)

	// UpdatePluginConfig updates configuration for deployed plugin
	UpdatePluginConfig(ctx context.Context, pluginID PluginID, nodes []string, config map[string]interface{}) error

	// RestartPlugin restarts a deployed plugin
	RestartPlugin(ctx context.Context, pluginID PluginID, nodes []string) error
}

// PluginExecutor interface - Executes plugins on FlexCore instances
type PluginExecutor interface {
	// ExecutePlugin executes a plugin operation
	ExecutePlugin(ctx context.Context, request PluginExecutionRequest) (*PluginExecutionResult, error)

	// ExecutePluginAsync executes a plugin operation asynchronously
	ExecutePluginAsync(ctx context.Context, request PluginExecutionRequest) (string, error)

	// GetExecutionResult retrieves result of async execution
	GetExecutionResult(executionID string) (*PluginExecutionResult, error)

	// StopExecution stops a running plugin execution
	StopExecution(ctx context.Context, executionID string) error

	// ListExecutions returns all plugin executions
	ListExecutions() ([]*PluginExecutionResult, error)
}

// PluginCommunicator interface - Handles inter-plugin communication
type PluginCommunicator interface {
	// SendMessage sends a message between plugins
	SendMessage(ctx context.Context, fromPlugin PluginID, toPlugin PluginID, message map[string]interface{}) error

	// BroadcastMessage sends a message to all plugins of a type
	BroadcastMessage(ctx context.Context, fromPlugin PluginID, targetType PluginType, message map[string]interface{}) error

	// SubscribeToMessages subscribes to messages for a plugin
	SubscribeToMessages(ctx context.Context, pluginID PluginID, messageHandler func(map[string]interface{}) error) error

	// UnsubscribeFromMessages unsubscribes from messages
	UnsubscribeFromMessages(ctx context.Context, pluginID PluginID) error
}

// FlexCoreClient interface - Communicates with FlexCore instances
type FlexCoreClient interface {
	// LoadPlugin loads a plugin binary on FlexCore instance
	LoadPlugin(ctx context.Context, nodeURL string, pluginPath string, config map[string]interface{}) error

	// UnloadPlugin unloads a plugin from FlexCore instance
	UnloadPlugin(ctx context.Context, nodeURL string, pluginID PluginID) error

	// ExecutePlugin executes a plugin on FlexCore instance
	ExecutePlugin(ctx context.Context, nodeURL string, request PluginExecutionRequest) (*PluginExecutionResult, error)

	// GetPluginHealth checks plugin health on FlexCore instance
	GetPluginHealth(ctx context.Context, nodeURL string, pluginID PluginID) (map[string]interface{}, error)

	// ListPlugins lists plugins on FlexCore instance
	ListPlugins(ctx context.Context, nodeURL string) ([]PluginMetadata, error)

	// UpdatePluginConfig updates plugin configuration on FlexCore instance
	UpdatePluginConfig(ctx context.Context, nodeURL string, pluginID PluginID, config map[string]interface{}) error
}

// PluginLoader interface - Loads plugin binaries (.so/.dll files)
type PluginLoader interface {
	// LoadPluginBinary loads a plugin from binary file
	LoadPluginBinary(pluginPath string) (Plugin, error)

	// UnloadPluginBinary unloads a plugin binary
	UnloadPluginBinary(pluginID PluginID) error

	// ValidatePluginBinary validates a plugin binary before loading
	ValidatePluginBinary(pluginPath string) error

	// GetLoadedPlugins returns all currently loaded plugins
	GetLoadedPlugins() []PluginID
}

// PluginManager interface - Main interface for complete plugin management
type PluginManager interface {
	PluginRegistry
	PluginDeploymentManager
	PluginExecutor
	PluginCommunicator

	// StartManager starts the plugin management system
	StartManager(ctx context.Context) error

	// StopManager stops the plugin management system
	StopManager(ctx context.Context) error

	// HealthCheck performs comprehensive health check of plugin system
	HealthCheck(ctx context.Context) (map[string]interface{}, error)
}