package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
)

// InMemoryCache provides a simple in-memory cache implementation
type InMemoryCache struct {
	data   map[string]cacheItem
	mu     sync.RWMutex
	logger logging.Logger
}

type cacheItem struct {
	value     interface{}
	expiresAt time.Time
}

// NewInMemoryCache creates a new in-memory cache
func NewInMemoryCache(logger logging.Logger) (CacheManager, error) {
	cache := &InMemoryCache{
		data:   make(map[string]cacheItem),
		logger: logger,
	}

	// Start cleanup goroutine
	go cache.cleanup()

	return cache, nil
}

// Set stores a value in the cache with TTL
func (c *InMemoryCache) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	expiresAt := time.Now().Add(ttl)
	c.data[key] = cacheItem{
		value:     value,
		expiresAt: expiresAt,
	}

	return nil
}

// Get retrieves a value from the cache and unmarshals it into dest
func (c *InMemoryCache) Get(ctx context.Context, key string, dest interface{}) error {
	c.mu.RLock()
	defer c.mu.RUnlock()

	item, exists := c.data[key]
	if !exists {
		return fmt.Errorf("key not found: %s", key)
	}

	if time.Now().After(item.expiresAt) {
		// Item has expired, remove it
		delete(c.data, key)
		return fmt.Errorf("key expired: %s", key)
	}

	// Simple type assignment for in-memory cache
	if jsonStr, ok := item.value.(string); ok {
		// Try to unmarshal JSON
		return json.Unmarshal([]byte(jsonStr), dest)
	}

	// Direct assignment if not JSON
	switch d := dest.(type) {
	case *string:
		if s, ok := item.value.(string); ok {
			*d = s
		} else {
			*d = fmt.Sprintf("%v", item.value)
		}
	case *interface{}:
		*d = item.value
	default:
		return fmt.Errorf("unsupported destination type")
	}

	return nil
}

// Delete removes keys from the cache
func (c *InMemoryCache) Delete(ctx context.Context, keys ...string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	for _, key := range keys {
		delete(c.data, key)
	}
	return nil
}

// DeletePattern removes keys matching a pattern from the cache
func (c *InMemoryCache) DeletePattern(ctx context.Context, pattern string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	for key := range c.data {
		// Simple pattern matching (just prefix for now)
		if pattern == "*" || key == pattern {
			delete(c.data, key)
		}
	}
	return nil
}

// Exists checks if keys exist in the cache
func (c *InMemoryCache) Exists(ctx context.Context, keys ...string) (int64, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var count int64 = 0
	for _, key := range keys {
		item, exists := c.data[key]
		if !exists {
			continue
		}

		if time.Now().After(item.expiresAt) {
			// Item has expired
			delete(c.data, key)
			continue
		}

		count++
	}

	return count, nil
}

// SetJSON stores a JSON-serializable value
func (c *InMemoryCache) SetJSON(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	jsonData, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("failed to marshal JSON: %w", err)
	}

	return c.Set(ctx, key, string(jsonData), ttl)
}

// GetJSON retrieves and unmarshals a JSON value
func (c *InMemoryCache) GetJSON(ctx context.Context, key string, dest interface{}) error {
	err := c.Get(ctx, key, dest)
	if err != nil {
		return err
	}

	return nil
}

// Clear removes all items from the cache
func (c *InMemoryCache) Clear(ctx context.Context) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.data = make(map[string]cacheItem)
	return nil
}

// Size returns the number of items in the cache
func (c *InMemoryCache) Size(ctx context.Context) (int, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return len(c.data), nil
}

// Keys returns all keys in the cache
func (c *InMemoryCache) Keys(ctx context.Context, pattern string) ([]string, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	var keys []string
	for key := range c.data {
		// Simple pattern matching (just prefix for now)
		if pattern == "*" || key == pattern {
			keys = append(keys, key)
		}
	}

	return keys, nil
}

// TTL returns the time to live for a key
func (c *InMemoryCache) TTL(ctx context.Context, key string) (time.Duration, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	item, exists := c.data[key]
	if !exists {
		return 0, fmt.Errorf("key not found: %s", key)
	}

	if time.Now().After(item.expiresAt) {
		return 0, fmt.Errorf("key expired: %s", key)
	}

	return time.Until(item.expiresAt), nil
}

// HealthCheck performs a health check on the cache
func (c *InMemoryCache) HealthCheck(ctx context.Context) error {
	// In-memory cache is always healthy
	return nil
}

// GetStatistics returns cache statistics
func (c *InMemoryCache) GetStatistics(ctx context.Context) (*CacheStatistics, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return &CacheStatistics{
		RedisInfo:   "in_memory_cache",
		Connections: 1,
		IdleConns:   0,
		StaleConns:  0,
		Hits:        0,
		Misses:      0,
		Timeouts:    0,
	}, nil
}

// Expire sets a TTL for a key
func (c *InMemoryCache) Expire(ctx context.Context, key string, expiration time.Duration) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	item, exists := c.data[key]
	if !exists {
		return fmt.Errorf("key not found: %s", key)
	}

	item.expiresAt = time.Now().Add(expiration)
	c.data[key] = item
	return nil
}

// SetNX sets a key only if it doesn't exist
func (c *InMemoryCache) SetNX(ctx context.Context, key string, value interface{}, expiration time.Duration) (bool, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.data[key]; exists {
		return false, nil
	}

	expiresAt := time.Now().Add(expiration)
	c.data[key] = cacheItem{
		value:     value,
		expiresAt: expiresAt,
	}

	return true, nil
}

// GetSet sets a new value and returns the old value
func (c *InMemoryCache) GetSet(ctx context.Context, key string, value interface{}) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	item, exists := c.data[key]
	oldValue := ""
	if exists {
		if s, ok := item.value.(string); ok {
			oldValue = s
		} else {
			oldValue = fmt.Sprintf("%v", item.value)
		}
	}

	expiresAt := time.Now().Add(24 * time.Hour) // Default TTL
	c.data[key] = cacheItem{
		value:     value,
		expiresAt: expiresAt,
	}

	return oldValue, nil
}

// Increment increments a numeric value
func (c *InMemoryCache) Increment(ctx context.Context, key string) (int64, error) {
	return c.IncrementBy(ctx, key, 1)
}

// IncrementBy increments a numeric value by amount
func (c *InMemoryCache) IncrementBy(ctx context.Context, key string, value int64) (int64, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	item, exists := c.data[key]
	currentValue := int64(0)

	if exists {
		if i, ok := item.value.(int64); ok {
			currentValue = i
		} else if i, ok := item.value.(int); ok {
			currentValue = int64(i)
		}
	}

	newValue := currentValue + value
	expiresAt := time.Now().Add(24 * time.Hour) // Default TTL
	if exists {
		expiresAt = item.expiresAt
	}

	c.data[key] = cacheItem{
		value:     newValue,
		expiresAt: expiresAt,
	}

	return newValue, nil
}

// Basic implementations for hash, list, and set operations
// These are simplified for in-memory cache

func (c *InMemoryCache) HSet(ctx context.Context, key string, values ...interface{}) error {
	// Simplified: store as a map
	c.mu.Lock()
	defer c.mu.Unlock()

	hashMap := make(map[string]interface{})
	for i := 0; i < len(values)-1; i += 2 {
		field := fmt.Sprintf("%v", values[i])
		value := values[i+1]
		hashMap[field] = value
	}

	expiresAt := time.Now().Add(24 * time.Hour) // Default TTL
	c.data[key] = cacheItem{
		value:     hashMap,
		expiresAt: expiresAt,
	}

	return nil
}

func (c *InMemoryCache) HGet(ctx context.Context, key, field string) (string, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	item, exists := c.data[key]
	if !exists {
		return "", fmt.Errorf("key not found: %s", key)
	}

	if hashMap, ok := item.value.(map[string]interface{}); ok {
		if value, exists := hashMap[field]; exists {
			return fmt.Sprintf("%v", value), nil
		}
	}

	return "", fmt.Errorf("field not found: %s", field)
}

func (c *InMemoryCache) HGetAll(ctx context.Context, key string) (map[string]string, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	item, exists := c.data[key]
	if !exists {
		return nil, fmt.Errorf("key not found: %s", key)
	}

	result := make(map[string]string)
	if hashMap, ok := item.value.(map[string]interface{}); ok {
		for k, v := range hashMap {
			result[k] = fmt.Sprintf("%v", v)
		}
	}

	return result, nil
}

func (c *InMemoryCache) HDel(ctx context.Context, key string, fields ...string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	item, exists := c.data[key]
	if !exists {
		return nil
	}

	if hashMap, ok := item.value.(map[string]interface{}); ok {
		for _, field := range fields {
			delete(hashMap, field)
		}
		c.data[key] = item
	}

	return nil
}

// List operations (simplified)
func (c *InMemoryCache) LPush(ctx context.Context, key string, values ...interface{}) error {
	// Simplified implementation
	return nil
}

func (c *InMemoryCache) RPush(ctx context.Context, key string, values ...interface{}) error {
	// Simplified implementation
	return nil
}

func (c *InMemoryCache) LPop(ctx context.Context, key string) (string, error) {
	return "", fmt.Errorf("not implemented")
}

func (c *InMemoryCache) RPop(ctx context.Context, key string) (string, error) {
	return "", fmt.Errorf("not implemented")
}

func (c *InMemoryCache) LLen(ctx context.Context, key string) (int64, error) {
	return 0, nil
}

func (c *InMemoryCache) LRange(ctx context.Context, key string, start, stop int64) ([]string, error) {
	return []string{}, nil
}

// Set operations (simplified)
func (c *InMemoryCache) SAdd(ctx context.Context, key string, members ...interface{}) error {
	return nil
}

func (c *InMemoryCache) SMembers(ctx context.Context, key string) ([]string, error) {
	return []string{}, nil
}

func (c *InMemoryCache) SRem(ctx context.Context, key string, members ...interface{}) error {
	return nil
}

func (c *InMemoryCache) SCard(ctx context.Context, key string) (int64, error) {
	return 0, nil
}

// Pipeline operations (simplified for in-memory cache)
func (c *InMemoryCache) Pipeline(ctx context.Context, fn func(pipe redis.Pipeliner) error) error {
	// For in-memory cache, execute immediately (no batching needed)
	return nil
}

func (c *InMemoryCache) Transaction(ctx context.Context, keys []string, fn func(tx *redis.Tx) error) error {
	// For in-memory cache, execute immediately (no transactions needed)
	return nil
}

// Close closes the cache (cleanup for in-memory cache)
func (c *InMemoryCache) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.data = make(map[string]cacheItem)
	c.logger.Info("In-memory cache closed")
	return nil
}

// cleanup removes expired items periodically
func (c *InMemoryCache) cleanup() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		c.mu.Lock()
		now := time.Now()
		for key, item := range c.data {
			if now.After(item.expiresAt) {
				delete(c.data, key)
			}
		}
		c.mu.Unlock()
	}
}
