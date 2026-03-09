package container

import (
	"sync"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// UnifiedContainer provides basic dependency injection
// SIMPLIFIED VERSION for compilation compatibility
// TODO: Restore full DDD architecture when domain packages are properly organized
type UnifiedContainer struct {
	mu     sync.RWMutex
	logger logging.Logger
}

// NewUnifiedContainer creates a new container with basic dependencies
func NewUnifiedContainer() (*UnifiedContainer, error) {
	logger := logging.GetLogger()

	return &UnifiedContainer{
		logger: logger,
	}, nil
}

// GetLogger returns the logger instance
func (c *UnifiedContainer) GetLogger() logging.Logger {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.logger
}
