// Package coordination - FlexCore Instance Coordination for FLEXT Control Panel
package coordination

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/logging"
)

// FlexCoreInstance represents a managed FlexCore instance
type FlexCoreInstance struct {
	ID       string    `json:"id"`
	Address  string    `json:"address"`
	Status   string    `json:"status"`
	LastSeen time.Time `json:"last_seen"`
}

// FlexCoreCoordinator manages multiple FlexCore instances
type FlexCoreCoordinator struct {
	mu        sync.RWMutex
	instances map[string]*FlexCoreInstance
	logger    logging.Logger
}

// NewFlexCoreCoordinator creates a new FlexCore coordinator
func NewFlexCoreCoordinator() *FlexCoreCoordinator {
	return &FlexCoreCoordinator{
		instances: make(map[string]*FlexCoreInstance),
		logger:    logging.GetLogger(),
	}
}

// RegisterInstance registers a new FlexCore instance
func (c *FlexCoreCoordinator) RegisterInstance(ctx context.Context, instanceID, address string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	instance := &FlexCoreInstance{
		ID:       instanceID,
		Address:  address,
		Status:   "registered",
		LastSeen: time.Now(),
	}

	c.instances[instanceID] = instance
	c.logger.Info("FlexCore instance registered: " + instanceID + " at " + address)

	return nil
}

// UnregisterInstance removes a FlexCore instance
func (c *FlexCoreCoordinator) UnregisterInstance(ctx context.Context, instanceID string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.instances[instanceID]; !exists {
		return fmt.Errorf("instance %s not found", instanceID)
	}

	delete(c.instances, instanceID)
	c.logger.Info("FlexCore instance unregistered: " + instanceID)

	return nil
}

// GetInstance retrieves a specific FlexCore instance
func (c *FlexCoreCoordinator) GetInstance(instanceID string) (*FlexCoreInstance, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	instance, exists := c.instances[instanceID]
	if !exists {
		return nil, fmt.Errorf("instance %s not found", instanceID)
	}

	return instance, nil
}

// ListInstances returns all registered FlexCore instances
func (c *FlexCoreCoordinator) ListInstances() []*FlexCoreInstance {
	c.mu.RLock()
	defer c.mu.RUnlock()

	instances := make([]*FlexCoreInstance, 0, len(c.instances))
	for _, instance := range c.instances {
		instances = append(instances, instance)
	}

	return instances
}

// UpdateInstanceStatus updates the status of a FlexCore instance
func (c *FlexCoreCoordinator) UpdateInstanceStatus(instanceID, status string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	instance, exists := c.instances[instanceID]
	if !exists {
		return fmt.Errorf("instance %s not found", instanceID)
	}

	instance.Status = status
	instance.LastSeen = time.Now()

	c.logger.Debug("FlexCore instance status updated: " + instanceID + " -> " + status)

	return nil
}

// HealthCheck performs health check on all instances
func (c *FlexCoreCoordinator) HealthCheck(ctx context.Context) error {
	c.mu.RLock()
	instances := make([]*FlexCoreInstance, 0, len(c.instances))
	for _, instance := range c.instances {
		instances = append(instances, instance)
	}
	c.mu.RUnlock()

	for _, instance := range instances {
		// TODO: Implement actual gRPC health check to FlexCore instance
		c.logger.Debug("Health checking FlexCore instance: " + instance.ID + " at " + instance.Address)

		// For now, just update last seen
		c.UpdateInstanceStatus(instance.ID, "healthy")
	}

	return nil
}
