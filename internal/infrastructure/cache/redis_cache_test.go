package cache

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
	"github.com/samber/lo"
	"github.com/stretchr/testify/assert"
)

// TestRedisCache tests Redis cache functionality
// Note: This test requires a Redis server running locally
func TestRedisCache_FunctionalProgramming(t *testing.T) {
	// Skip if CI environment or no Redis available
	if testing.Short() {
		t.Skip("Skipping Redis integration test in short mode")
	}

	// Initialize basic logger for testing
	logging.InitLogger(config.LoggingConfig{
		Level:  "info",
		Format: "json",
	})
	logger := logging.GetLogger()
	cfg := config.RedisConfig{
		Host:         "localhost",
		Port:         6379,
		Password:     "",
		Database:     0,
		PoolSize:     5,
		MinIdleConns: 2,
		MaxRetries:   3,
		DialTimeout:  5 * time.Second,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
		IdleTimeout:  5 * time.Minute,
	}

	// Test cache creation with fallback
	cache, err := NewRedisCache(cfg, logger)
	if err != nil {
		t.Logf("Redis not available, testing cache logic only: %v", err)

		// Test functional programming components without Redis
		testCacheKeyGeneration(t)
		testPipelineHelpers(t)
		return
	}
	defer cache.Close()

	ctx := context.Background()

	t.Run("Basic Operations", func(t *testing.T) {
		// Test Set and Get
		testData := map[string]interface{}{
			"name":    "FLEXT Test",
			"version": "2.0.0",
			"active":  true,
		}

		err := cache.Set(ctx, "test:basic", testData, time.Minute)
		assert.NoError(t, err)

		var retrieved map[string]interface{}
		err = cache.Get(ctx, "test:basic", &retrieved)
		assert.NoError(t, err)
		assert.Equal(t, testData["name"], retrieved["name"])
		assert.Equal(t, testData["version"], retrieved["version"])
		assert.Equal(t, testData["active"], retrieved["active"])

		// Test Exists
		count, err := cache.Exists(ctx, "test:basic")
		assert.NoError(t, err)
		assert.Equal(t, int64(1), count)

		// Test Delete
		err = cache.Delete(ctx, "test:basic")
		assert.NoError(t, err)

		// Verify deletion
		count, err = cache.Exists(ctx, "test:basic")
		assert.NoError(t, err)
		assert.Equal(t, int64(0), count)
	})

	t.Run("Advanced Operations", func(t *testing.T) {
		// Test SetNX (atomic operation)
		success, err := cache.SetNX(ctx, "test:setnx", "first", time.Minute)
		assert.NoError(t, err)
		assert.True(t, success)

		// Try to set again (should fail)
		success, err = cache.SetNX(ctx, "test:setnx", "second", time.Minute)
		assert.NoError(t, err)
		assert.False(t, success)

		// Test Increment operations
		count, err := cache.Increment(ctx, "test:counter")
		assert.NoError(t, err)
		assert.Equal(t, int64(1), count)

		count, err = cache.IncrementBy(ctx, "test:counter", 5)
		assert.NoError(t, err)
		assert.Equal(t, int64(6), count)

		// Cleanup
		cache.Delete(ctx, "test:setnx", "test:counter")
	})

	t.Run("Hash Operations", func(t *testing.T) {
		hashKey := "test:hash"

		// Test HSet
		err := cache.HSet(ctx, hashKey, "field1", "value1", "field2", "value2")
		assert.NoError(t, err)

		// Test HGet
		value, err := cache.HGet(ctx, hashKey, "field1")
		assert.NoError(t, err)
		assert.Equal(t, "value1", value)

		// Test HGetAll
		allFields, err := cache.HGetAll(ctx, hashKey)
		assert.NoError(t, err)
		assert.Equal(t, "value1", allFields["field1"])
		assert.Equal(t, "value2", allFields["field2"])

		// Test HDel
		err = cache.HDel(ctx, hashKey, "field1")
		assert.NoError(t, err)

		// Verify deletion
		_, err = cache.HGet(ctx, hashKey, "field1")
		assert.Error(t, err) // Should not exist

		// Cleanup
		cache.Delete(ctx, hashKey)
	})

	t.Run("List Operations", func(t *testing.T) {
		listKey := "test:list"

		// Test LPush and RPush
		err := cache.LPush(ctx, listKey, "item1", "item2")
		assert.NoError(t, err)

		err = cache.RPush(ctx, listKey, "item3", "item4")
		assert.NoError(t, err)

		// Test LLen
		length, err := cache.LLen(ctx, listKey)
		assert.NoError(t, err)
		assert.Equal(t, int64(4), length)

		// Test LRange
		items, err := cache.LRange(ctx, listKey, 0, -1)
		assert.NoError(t, err)
		assert.Len(t, items, 4)

		// Test LPop and RPop
		leftItem, err := cache.LPop(ctx, listKey)
		assert.NoError(t, err)
		assert.Equal(t, "item2", leftItem)

		rightItem, err := cache.RPop(ctx, listKey)
		assert.NoError(t, err)
		assert.Equal(t, "item4", rightItem)

		// Cleanup
		cache.Delete(ctx, listKey)
	})

	t.Run("Set Operations", func(t *testing.T) {
		setKey := "test:set"

		// Test SAdd
		err := cache.SAdd(ctx, setKey, "member1", "member2", "member3")
		assert.NoError(t, err)

		// Test SCard
		count, err := cache.SCard(ctx, setKey)
		assert.NoError(t, err)
		assert.Equal(t, int64(3), count)

		// Test SMembers
		members, err := cache.SMembers(ctx, setKey)
		assert.NoError(t, err)
		assert.Len(t, members, 3)
		assert.Contains(t, members, "member1")
		assert.Contains(t, members, "member2")
		assert.Contains(t, members, "member3")

		// Test SRem
		err = cache.SRem(ctx, setKey, "member1")
		assert.NoError(t, err)

		count, err = cache.SCard(ctx, setKey)
		assert.NoError(t, err)
		assert.Equal(t, int64(2), count)

		// Cleanup
		cache.Delete(ctx, setKey)
	})

	t.Run("Pipeline Operations", func(t *testing.T) {
		// Test pipeline with functional programming
		err := cache.Pipeline(ctx, func(pipe redis.Pipeliner) error {
			data := map[string]interface{}{
				"test:pipe1": "value1",
				"test:pipe2": "value2",
				"test:pipe3": "value3",
			}
			return PipelineSetMultiple(pipe, data, time.Minute)
		})
		assert.NoError(t, err)

		// Verify pipeline operations
		var value1, value2, value3 string
		cache.Get(ctx, "test:pipe1", &value1)
		cache.Get(ctx, "test:pipe2", &value2)
		cache.Get(ctx, "test:pipe3", &value3)

		assert.Equal(t, "value1", value1)
		assert.Equal(t, "value2", value2)
		assert.Equal(t, "value3", value3)

		// Cleanup using pipeline
		err = cache.Pipeline(ctx, func(pipe redis.Pipeliner) error {
			keys := []string{"test:pipe1", "test:pipe2", "test:pipe3"}
			PipelineDeleteMultiple(pipe, keys)
			return nil
		})
		assert.NoError(t, err)
	})

	t.Run("Pattern Delete with Functional Programming", func(t *testing.T) {
		// Create test keys with pattern
		testKeys := map[string]interface{}{
			"pattern:test:1": "value1",
			"pattern:test:2": "value2",
			"pattern:test:3": "value3",
			"other:key":      "other",
		}

		// Set all keys
		for key, value := range testKeys {
			cache.Set(ctx, key, value, time.Minute)
		}

		// Delete by pattern
		err := cache.DeletePattern(ctx, "pattern:test:*")
		assert.NoError(t, err)

		// Verify pattern keys are deleted
		count, err := cache.Exists(ctx, "pattern:test:1", "pattern:test:2", "pattern:test:3")
		assert.NoError(t, err)
		assert.Equal(t, int64(0), count)

		// Verify other key still exists
		count, err = cache.Exists(ctx, "other:key")
		assert.NoError(t, err)
		assert.Equal(t, int64(1), count)

		// Cleanup
		cache.Delete(ctx, "other:key")
	})

	t.Run("Health Check", func(t *testing.T) {
		err := cache.HealthCheck(ctx)
		assert.NoError(t, err)
	})

	t.Run("Statistics", func(t *testing.T) {
		stats, err := cache.GetStatistics(ctx)
		assert.NoError(t, err)
		assert.NotNil(t, stats)
		assert.NotEmpty(t, stats.RedisInfo)
		assert.NotNil(t, stats.PoolStats)
	})
}

// Test functional programming components independently
func testCacheKeyGeneration(t *testing.T) {
	t.Run("CacheKey Generation", func(t *testing.T) {
		// Test cache key generation with functional programming
		key := CacheKey{
			Prefix:    "flext",
			Namespace: "pipeline",
			ID:        "123",
			Version:   "1.0",
		}

		expected := "flext:pipeline:123:v1.0"
		assert.Equal(t, expected, key.String())

		// Test partial key
		partialKey := CacheKey{
			Prefix: "flext",
			ID:     "456",
		}
		assert.Equal(t, "flext:456", partialKey.String())

		// Test empty key
		emptyKey := CacheKey{}
		assert.Equal(t, "", emptyKey.String())
	})
}

func testPipelineHelpers(t *testing.T) {
	t.Run("Pipeline Helpers", func(t *testing.T) {
		// Test that pipeline helper functions use functional programming correctly
		data := map[string]interface{}{
			"key1": "value1",
			"key2": map[string]string{"nested": "value"},
			"key3": []string{"array", "value"},
		}

		// Test that lo.Entries works correctly (used in PipelineSetMultiple)
		entries := lo.Entries(data)
		assert.Len(t, entries, 3)

		// Test that lo.ForEach works correctly (used in pipeline functions)
		keys := []string{"key1", "key2", "key3"}
		processed := make([]string, 0)
		lo.ForEach(keys, func(key string, _ int) {
			processed = append(processed, "processed:"+key)
		})

		assert.Len(t, processed, 3)
		assert.Contains(t, processed, "processed:key1")
		assert.Contains(t, processed, "processed:key2")
		assert.Contains(t, processed, "processed:key3")

		// Test lo.Chunk used in DeletePattern
		longList := make([]string, 250)
		for i := range longList {
			longList[i] = fmt.Sprintf("item_%d", i)
		}

		batches := lo.Chunk(longList, 100)
		assert.Len(t, batches, 3) // 250 items in chunks of 100 = 3 batches
		assert.Len(t, batches[0], 100)
		assert.Len(t, batches[1], 100)
		assert.Len(t, batches[2], 50) // Last batch has remainder
	})
}
