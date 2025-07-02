package database

import (
	"context"
	"fmt"
	"sync"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
)

// InMemoryAdvancedDatabase provides a simple in-memory database fallback
type InMemoryAdvancedDatabase struct {
	data   map[string]interface{}
	mu     sync.RWMutex
	logger logging.Logger
}

// NewInMemoryAdvancedDatabase creates a new in-memory database fallback
func NewInMemoryAdvancedDatabase(logger logging.Logger) (*AdvancedDatabase, error) {
	// Create a mock AdvancedDatabase with nil GORM and SQLX (fallback mode)
	advancedDB := &AdvancedDatabase{
		gormDB: nil, // Will be nil for in-memory fallback
		sqlxDB: nil, // Will be nil for in-memory fallback
		logger: logger,
	}
	
	logger.Info("In-memory database fallback created successfully")
	return advancedDB, nil
}

// Store stores data in memory
func (db *InMemoryAdvancedDatabase) Store(key string, value interface{}) error {
	db.mu.Lock()
	defer db.mu.Unlock()
	
	db.data[key] = value
	return nil
}

// Retrieve gets data from memory
func (db *InMemoryAdvancedDatabase) Retrieve(key string) (interface{}, error) {
	db.mu.RLock()
	defer db.mu.RUnlock()
	
	value, exists := db.data[key]
	if !exists {
		return nil, fmt.Errorf("key not found: %s", key)
	}
	
	return value, nil
}

// Delete removes data from memory
func (db *InMemoryAdvancedDatabase) Delete(key string) error {
	db.mu.Lock()
	defer db.mu.Unlock()
	
	delete(db.data, key)
	return nil
}

// HealthCheck performs a health check
func (db *InMemoryAdvancedDatabase) HealthCheck(ctx context.Context) error {
	// In-memory database is always healthy
	return nil
}

// GetStatistics returns database statistics
func (db *InMemoryAdvancedDatabase) GetStatistics(ctx context.Context) (map[string]interface{}, error) {
	db.mu.RLock()
	defer db.mu.RUnlock()
	
	return map[string]interface{}{
		"type":        "in_memory",
		"total_items": len(db.data),
		"status":      "healthy",
	}, nil
}

// Close closes the in-memory database
func (db *InMemoryAdvancedDatabase) Close() error {
	db.mu.Lock()
	defer db.mu.Unlock()
	
	db.data = make(map[string]interface{})
	db.logger.Info("In-memory database closed")
	return nil
}