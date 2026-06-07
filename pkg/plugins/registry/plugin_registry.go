// Package registry - Plugin Registry Implementation for FLEXT Service
//
// This package implements the plugin registry that manages all deployable plugins
// in the FLEXT ecosystem. The registry runs in FLEXT Service (Control Panel) and
// coordinates plugin deployment to multiple FlexCore instances.
//
// Architecture:
//   - FLEXT Service: Central plugin registry and deployment coordination
//   - FlexCore Instances: Distributed runtime that receives and executes plugins
//   - Plugin Binaries: .so/.dll files that implement the Plugin interface
//
// Plugin Registry Functions:
//   - Plugin registration and discovery
//   - Plugin metadata management
//   - Plugin deployment coordination
//   - Inter-plugin communication coordination
//   - Plugin lifecycle management
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package registry

import (
	"context"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

// PluginRegistry implements the central plugin registry for FLEXT Service
type PluginRegistry struct {
	plugins           map[plugins.PluginID]plugins.PluginMetadata
	deployments       map[plugins.PluginID][]plugins.PluginDeployment
	flexcoreNodes     map[string]FlexCoreNode
	pluginBinaries    map[plugins.PluginID]string
	communicator      plugins.PluginCommunicator
	deploymentManager plugins.PluginDeploymentManager
	mu                sync.RWMutex
	ctx               context.Context
	cancel            context.CancelFunc
}

// FlexCoreNode represents a FlexCore instance that can run plugins
type FlexCoreNode struct {
	URL           string                 `json:"url"`
	Name          string                 `json:"name"`
	Status        string                 `json:"status"`
	LastSeen      time.Time              `json:"last_seen"`
	LoadedPlugins []plugins.PluginID     `json:"loaded_plugins"`
	Capabilities  []string               `json:"capabilities"`
	Resources     map[string]interface{} `json:"resources"`
	Configuration map[string]interface{} `json:"configuration"`
}

// NewPluginRegistry creates a new plugin registry instance
func NewPluginRegistry() *PluginRegistry {
	ctx, cancel := context.WithCancel(context.Background())

	return &PluginRegistry{
		plugins:        make(map[plugins.PluginID]plugins.PluginMetadata),
		deployments:    make(map[plugins.PluginID][]plugins.PluginDeployment),
		flexcoreNodes:  make(map[string]FlexCoreNode),
		pluginBinaries: make(map[plugins.PluginID]string),
		ctx:            ctx,
		cancel:         cancel,
	}
}
