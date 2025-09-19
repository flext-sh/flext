// Package loader - Plugin Factory Registry for Dynamic Plugin Registration
//
// This file contains the plugin factory registry that registers specific plugin
// implementations without requiring the main service to import them directly.
// This follows dependency inversion principle and allows for pluggable architecture.
//
// The factories are registered once and used to create plugin instances dynamically.
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package loader

import (
	"github.com/flext-sh/flext/pkg/plugins"
	"github.com/flext-sh/flext/pkg/plugins/meltano"
	"github.com/flext-sh/flext/pkg/plugins/ray"
	"github.com/flext-sh/flext/pkg/plugins/kubernetes"
	"github.com/flext-sh/flext/pkg/logging"
)

// RegisterCorePluginFactories registers the core plugin factories with the loader
// This is the ONLY place where specific plugin implementations are imported
func RegisterCorePluginFactories(loader *PluginLoader, logger logging.Logger) {
	logger.Info("📦 Registering core plugin factories via DI...")

	// Register Meltano Plugin Factory
	loader.RegisterPluginFactory(plugins.PluginTypeMeltano, func() plugins.Plugin {
		return meltano.NewMeltanoPlugin()
	})
	logger.Info("✅ Meltano plugin factory registered")

	// Register Ray Plugin Factory
	loader.RegisterPluginFactory(plugins.PluginTypeRay, func() plugins.Plugin {
		return ray.NewRayPlugin()
	})
	logger.Info("✅ Ray plugin factory registered")

	// Register Kubernetes Plugin Factory
	loader.RegisterPluginFactory(plugins.PluginTypeKubernetes, func() plugins.Plugin {
		return kubernetes.NewKubernetesPlugin()
	})
	logger.Info("✅ Kubernetes plugin factory registered")

	logger.Info("✅ All core plugin factories registered successfully")
}

// GetDefaultPluginConfigurations returns default configurations for core plugins
func GetDefaultPluginConfigurations() []PluginConfiguration {
	return []PluginConfiguration{
		{
			PluginType:   plugins.PluginTypeMeltano,
			BinaryPath:   "./plugins/meltano-plugin.so",
			Enabled:      true,
			AutoRegister: true,
			Config: map[string]interface{}{
				"flexcore_node_url": "http://localhost:8081",
				"python_venv":       "./venv",
				"meltano_project":   "./meltano_project",
			},
		},
		{
			PluginType:   plugins.PluginTypeRay,
			BinaryPath:   "./plugins/ray-plugin.so",
			Enabled:      true,
			AutoRegister: true,
			Config: map[string]interface{}{
				"flexcore_node_url": "http://localhost:8081",
				"python_venv":       "./venv",
				"ray_cluster_url":   "ray://localhost:10001",
			},
		},
		{
			PluginType:   plugins.PluginTypeKubernetes,
			BinaryPath:   "./plugins/kubernetes-plugin.so",
			Enabled:      true,
			AutoRegister: true,
			Config: map[string]interface{}{
				"flexcore_node_url": "http://localhost:8081",
				"kubeconfig_path":   "",
				"namespace":         "default",
				"cluster_name":      "default",
			},
		},
	}
}