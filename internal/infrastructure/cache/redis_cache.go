package cache

import (
	"context"
	"encoding/json"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
	"github.com/pkg/errors"
	"github.com/samber/lo"
)

// RedisCache implements advanced Redis caching with functional programming
type RedisCache struct {
	client *redis.Client
	logger logging.Logger
	config config.RedisConfig
}

// NewRedisCache creates a new Redis cache instance
func NewRedisCache(cfg config.RedisConfig, logger logging.Logger) (*RedisCache, error) {
	client := redis.NewClient(&redis.Options{
		Addr:         cfg.Address(),
		Password:     cfg.Password,
		DB:           cfg.Database,
		PoolSize:     cfg.PoolSize,
		MinIdleConns: cfg.MinIdleConns,
		MaxRetries:   cfg.MaxRetries,
		DialTimeout:  cfg.DialTimeout,
		ReadTimeout:  cfg.ReadTimeout,
		WriteTimeout: cfg.WriteTimeout,
		IdleTimeout:  cfg.IdleTimeout,
	})
	
	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, errors.Wrap(err, "failed to connect to Redis")
	}
	
	cache := &RedisCache{
		client: client,
		logger: logger,
		config: cfg,
	}
	
	logger.Info("Redis cache initialized successfully",
		logging.F("host", cfg.Host),
		logging.F("port", cfg.Port),
		logging.F("database", cfg.Database),
	)
	
	return cache, nil
}

// CacheManager interface for advanced caching operations
type CacheManager interface {
	Set(ctx context.Context, key string, value interface{}, expiration time.Duration) error
	Get(ctx context.Context, key string, dest interface{}) error
	Delete(ctx context.Context, keys ...string) error
	DeletePattern(ctx context.Context, pattern string) error
	Exists(ctx context.Context, keys ...string) (int64, error)
	TTL(ctx context.Context, key string) (time.Duration, error)
	Expire(ctx context.Context, key string, expiration time.Duration) error
	
	// Advanced operations
	SetNX(ctx context.Context, key string, value interface{}, expiration time.Duration) (bool, error)
	GetSet(ctx context.Context, key string, value interface{}) (string, error)
	Increment(ctx context.Context, key string) (int64, error)
	IncrementBy(ctx context.Context, key string, value int64) (int64, error)
	
	// Hash operations
	HSet(ctx context.Context, key string, values ...interface{}) error
	HGet(ctx context.Context, key, field string) (string, error)
	HGetAll(ctx context.Context, key string) (map[string]string, error)
	HDel(ctx context.Context, key string, fields ...string) error
	
	// List operations
	LPush(ctx context.Context, key string, values ...interface{}) error
	RPush(ctx context.Context, key string, values ...interface{}) error
	LPop(ctx context.Context, key string) (string, error)
	RPop(ctx context.Context, key string) (string, error)
	LLen(ctx context.Context, key string) (int64, error)
	LRange(ctx context.Context, key string, start, stop int64) ([]string, error)
	
	// Set operations
	SAdd(ctx context.Context, key string, members ...interface{}) error
	SMembers(ctx context.Context, key string) ([]string, error)
	SRem(ctx context.Context, key string, members ...interface{}) error
	SCard(ctx context.Context, key string) (int64, error)
	
	// Advanced pipeline operations
	Pipeline(ctx context.Context, fn func(pipe redis.Pipeliner) error) error
	Transaction(ctx context.Context, keys []string, fn func(tx *redis.Tx) error) error
	
	// Cache statistics and monitoring
	GetStatistics(ctx context.Context) (*CacheStatistics, error)
	HealthCheck(ctx context.Context) error
	Close() error
}

// Implement CacheManager interface

// Set stores a value with expiration
func (c *RedisCache) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) error {
	data, err := json.Marshal(value)
	if err != nil {
		return errors.Wrap(err, "failed to marshal value for cache")
	}
	
	if err := c.client.Set(ctx, key, data, expiration).Err(); err != nil {
		return errors.Wrap(err, "failed to set cache value")
	}
	
	c.logger.Debug("Cache value set",
		logging.F("key", key),
		logging.F("expiration", expiration.String()),
	)
	
	return nil
}

// Get retrieves and unmarshals a value
func (c *RedisCache) Get(ctx context.Context, key string, dest interface{}) error {
	data, err := c.client.Get(ctx, key).Result()
	if err != nil {
		if err == redis.Nil {
			return ErrCacheKeyNotFound
		}
		return errors.Wrap(err, "failed to get cache value")
	}
	
	if err := json.Unmarshal([]byte(data), dest); err != nil {
		return errors.Wrap(err, "failed to unmarshal cache value")
	}
	
	c.logger.Debug("Cache value retrieved", logging.F("key", key))
	return nil
}

// Delete removes keys
func (c *RedisCache) Delete(ctx context.Context, keys ...string) error {
	if len(keys) == 0 {
		return nil
	}
	
	deleted, err := c.client.Del(ctx, keys...).Result()
	if err != nil {
		return errors.Wrap(err, "failed to delete cache keys")
	}
	
	c.logger.Debug("Cache keys deleted",
		logging.F("keys", keys),
		logging.F("deleted_count", deleted),
	)
	
	return nil
}

// DeletePattern removes keys matching pattern using functional programming
func (c *RedisCache) DeletePattern(ctx context.Context, pattern string) error {
	keys, err := c.client.Keys(ctx, pattern).Result()
	if err != nil {
		return errors.Wrap(err, "failed to find keys by pattern")
	}
	
	if len(keys) == 0 {
		return nil
	}
	
	// Use functional programming to batch delete
	batches := lo.Chunk(keys, 100) // Process in batches of 100
	
	deletedTotal := 0
	for _, batch := range batches {
		deleted, err := c.client.Del(ctx, batch...).Result()
		if err != nil {
			c.logger.Error("Failed to delete batch",
				logging.F("batch_size", len(batch)),
				logging.F("error", err.Error()),
			)
			continue
		}
		deletedTotal += int(deleted)
	}
	
	c.logger.Info("Pattern-based cache deletion completed",
		logging.F("pattern", pattern),
		logging.F("total_deleted", deletedTotal),
	)
	
	return nil
}

// Advanced operations

// SetNX sets key only if it doesn't exist (atomic operation)
func (c *RedisCache) SetNX(ctx context.Context, key string, value interface{}, expiration time.Duration) (bool, error) {
	data, err := json.Marshal(value)
	if err != nil {
		return false, errors.Wrap(err, "failed to marshal value for SetNX")
	}
	
	result, err := c.client.SetNX(ctx, key, data, expiration).Result()
	if err != nil {
		return false, errors.Wrap(err, "failed to execute SetNX")
	}
	
	return result, nil
}

// Pipeline executes multiple operations in a single round-trip
func (c *RedisCache) Pipeline(ctx context.Context, fn func(pipe redis.Pipeliner) error) error {
	pipe := c.client.Pipeline()
	
	if err := fn(pipe); err != nil {
		return errors.Wrap(err, "failed to execute pipeline function")
	}
	
	results, err := pipe.Exec(ctx)
	if err != nil {
		return errors.Wrap(err, "failed to execute pipeline")
	}
	
	c.logger.Debug("Pipeline executed",
		logging.F("commands_count", len(results)),
	)
	
	return nil
}

// Transaction executes operations in a Redis transaction
func (c *RedisCache) Transaction(ctx context.Context, keys []string, fn func(tx *redis.Tx) error) error {
	return c.client.Watch(ctx, func(tx *redis.Tx) error {
		return fn(tx)
	}, keys...)
}

// Hash operations
func (c *RedisCache) HSet(ctx context.Context, key string, values ...interface{}) error {
	return c.client.HSet(ctx, key, values...).Err()
}

func (c *RedisCache) HGet(ctx context.Context, key, field string) (string, error) {
	return c.client.HGet(ctx, key, field).Result()
}

func (c *RedisCache) HGetAll(ctx context.Context, key string) (map[string]string, error) {
	return c.client.HGetAll(ctx, key).Result()
}

func (c *RedisCache) HDel(ctx context.Context, key string, fields ...string) error {
	return c.client.HDel(ctx, key, fields...).Err()
}

// List operations
func (c *RedisCache) LPush(ctx context.Context, key string, values ...interface{}) error {
	return c.client.LPush(ctx, key, values...).Err()
}

func (c *RedisCache) RPush(ctx context.Context, key string, values ...interface{}) error {
	return c.client.RPush(ctx, key, values...).Err()
}

func (c *RedisCache) LPop(ctx context.Context, key string) (string, error) {
	return c.client.LPop(ctx, key).Result()
}

func (c *RedisCache) RPop(ctx context.Context, key string) (string, error) {
	return c.client.RPop(ctx, key).Result()
}

func (c *RedisCache) LLen(ctx context.Context, key string) (int64, error) {
	return c.client.LLen(ctx, key).Result()
}

func (c *RedisCache) LRange(ctx context.Context, key string, start, stop int64) ([]string, error) {
	return c.client.LRange(ctx, key, start, stop).Result()
}

// Set operations
func (c *RedisCache) SAdd(ctx context.Context, key string, members ...interface{}) error {
	return c.client.SAdd(ctx, key, members...).Err()
}

func (c *RedisCache) SMembers(ctx context.Context, key string) ([]string, error) {
	return c.client.SMembers(ctx, key).Result()
}

func (c *RedisCache) SRem(ctx context.Context, key string, members ...interface{}) error {
	return c.client.SRem(ctx, key, members...).Err()
}

func (c *RedisCache) SCard(ctx context.Context, key string) (int64, error) {
	return c.client.SCard(ctx, key).Result()
}

// Utility methods
func (c *RedisCache) Exists(ctx context.Context, keys ...string) (int64, error) {
	return c.client.Exists(ctx, keys...).Result()
}

func (c *RedisCache) TTL(ctx context.Context, key string) (time.Duration, error) {
	return c.client.TTL(ctx, key).Result()
}

func (c *RedisCache) Expire(ctx context.Context, key string, expiration time.Duration) error {
	return c.client.Expire(ctx, key, expiration).Err()
}

func (c *RedisCache) GetSet(ctx context.Context, key string, value interface{}) (string, error) {
	data, err := json.Marshal(value)
	if err != nil {
		return "", errors.Wrap(err, "failed to marshal value for GetSet")
	}
	return c.client.GetSet(ctx, key, data).Result()
}

func (c *RedisCache) Increment(ctx context.Context, key string) (int64, error) {
	return c.client.Incr(ctx, key).Result()
}

func (c *RedisCache) IncrementBy(ctx context.Context, key string, value int64) (int64, error) {
	return c.client.IncrBy(ctx, key, value).Result()
}

// GetStatistics returns Redis performance statistics
func (c *RedisCache) GetStatistics(ctx context.Context) (*CacheStatistics, error) {
	info, err := c.client.Info(ctx, "memory", "stats", "clients").Result()
	if err != nil {
		return nil, errors.Wrap(err, "failed to get Redis info")
	}
	
	poolStats := c.client.PoolStats()
	
	stats := &CacheStatistics{
		RedisInfo:   info,
		PoolStats:   poolStats,
		Connections: poolStats.TotalConns,
		IdleConns:   poolStats.IdleConns,
		StaleConns:  poolStats.StaleConns,
		Hits:        poolStats.Hits,
		Misses:      poolStats.Misses,
		Timeouts:    poolStats.Timeouts,
	}
	
	return stats, nil
}

// HealthCheck performs Redis health check
func (c *RedisCache) HealthCheck(ctx context.Context) error {
	if err := c.client.Ping(ctx).Err(); err != nil {
		return errors.Wrap(err, "Redis health check failed")
	}
	return nil
}

// Close closes the Redis connection
func (c *RedisCache) Close() error {
	if err := c.client.Close(); err != nil {
		return errors.Wrap(err, "failed to close Redis client")
	}
	c.logger.Info("Redis cache closed successfully")
	return nil
}

// Cache-specific types and errors
var ErrCacheKeyNotFound = errors.New("cache key not found")

// CacheStatistics holds cache performance statistics
type CacheStatistics struct {
	RedisInfo   string              `json:"redis_info"`
	PoolStats   *redis.PoolStats    `json:"pool_stats"`
	Connections uint32              `json:"connections"`
	IdleConns   uint32              `json:"idle_connections"`
	StaleConns  uint32              `json:"stale_connections"`
	Hits        uint32              `json:"hits"`
	Misses      uint32              `json:"misses"`
	Timeouts    uint32              `json:"timeouts"`
}

// CacheKey helper for generating consistent cache keys
type CacheKey struct {
	Prefix    string
	Namespace string
	ID        string
	Version   string
}

// String generates the final cache key
func (ck CacheKey) String() string {
	parts := []string{ck.Prefix}
	
	if ck.Namespace != "" {
		parts = append(parts, ck.Namespace)
	}
	
	if ck.ID != "" {
		parts = append(parts, ck.ID)
	}
	
	if ck.Version != "" {
		parts = append(parts, "v"+ck.Version)
	}
	
	return lo.Reduce(parts, func(acc, part string, _ int) string {
		if acc == "" {
			return part
		}
		return acc + ":" + part
	}, "")
}

// Pipeline helper functions using functional programming
func PipelineSetMultiple(pipe redis.Pipeliner, keyValuePairs map[string]interface{}, expiration time.Duration) error {
	lo.ForEach(lo.Entries(keyValuePairs), func(entry lo.Entry[string, interface{}], _ int) {
		data, _ := json.Marshal(entry.Value)
		pipe.Set(context.Background(), entry.Key, data, expiration)
	})
	return nil
}

func PipelineDeleteMultiple(pipe redis.Pipeliner, keys []string) {
	lo.ForEach(keys, func(key string, _ int) {
		pipe.Del(context.Background(), key)
	})
}