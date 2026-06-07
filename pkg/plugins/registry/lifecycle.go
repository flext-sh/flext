package registry

import (
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

// SetCommunicator sets the plugin communicator for inter-plugin messaging
func (pr *PluginRegistry) SetCommunicator(communicator plugins.PluginCommunicator) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	pr.communicator = communicator
}

// Start starts the plugin registry background services
func (pr *PluginRegistry) Start() error {
	go pr.nodeHealthChecker()
	go pr.deploymentMonitor()

	return nil
}

// Stop stops the plugin registry
func (pr *PluginRegistry) Stop() error {
	pr.cancel()
	return nil
}

func (pr *PluginRegistry) nodeHealthChecker() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-pr.ctx.Done():
			return
		case <-ticker.C:
			pr.checkNodeHealth()
		}
	}
}

func (pr *PluginRegistry) deploymentMonitor() {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-pr.ctx.Done():
			return
		case <-ticker.C:
			pr.monitorDeployments()
		}
	}
}
