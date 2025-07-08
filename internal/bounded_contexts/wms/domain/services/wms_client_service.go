// Package services provides WMS client service following SOLID principles
// This file implements the WMSClientInterface with Single Responsibility
package services

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"
)

// WMSClientService implements WMSClientInterface following SOLID principles
// SOLID: S - Single responsibility (only handles WMS client operations)
// SOLID: O - Open/Closed (can be extended without modification)
type WMSClientService struct {
	// Dependencies injected for SOLID compliance
	dbConnection  DatabaseConnectionInterface
	cacheService  CacheServiceInterface
	logger        LoggerInterface
	healthChecker HealthCheckerInterface

	// Configuration
	config     *WMSClientConfiguration
	timeout    time.Duration
	maxRetries int

	// Connection state
	isConnected     bool
	lastHealthCheck time.Time
}

// DatabaseConnectionInterface defines database contract - SOLID: I - Interface Segregation
type DatabaseConnectionInterface interface {
	Query(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error)
	QueryRow(ctx context.Context, query string, args ...interface{}) *sql.Row
	Exec(ctx context.Context, query string, args ...interface{}) (sql.Result, error)
	Begin(ctx context.Context) (*sql.Tx, error)
	Close() error
	Ping(ctx context.Context) error
}

// CacheServiceInterface defines caching contract - SOLID: I - Interface Segregation
type CacheServiceInterface interface {
	Get(key string) (interface{}, bool)
	Set(key string, value interface{}, ttl time.Duration) error
	Delete(key string) error
	Clear() error
}

// LoggerInterface defines logging contract - SOLID: I - Interface Segregation
type LoggerInterface interface {
	Debug(msg string, fields ...interface{})
	Info(msg string, fields ...interface{})
	Warn(msg string, fields ...interface{})
	Error(msg string, err error, fields ...interface{})
}

// HealthCheckerInterface defines health checking contract - SOLID: I - Interface Segregation
type HealthCheckerInterface interface {
	CheckHealth(ctx context.Context) (*HealthStatus, error)
	RegisterHealthCheck(name string, checker func(ctx context.Context) error)
}

// WMSClientConfiguration holds client configuration
type WMSClientConfiguration struct {
	// Connection settings
	Host        string `json:"host"`
	Port        int    `json:"port"`
	ServiceName string `json:"service_name"`
	Username    string `json:"username"`
	Password    string `json:"password"`

	// Performance settings
	MaxOpenConns    int           `json:"max_open_conns"`
	MaxIdleConns    int           `json:"max_idle_conns"`
	ConnMaxLifetime time.Duration `json:"conn_max_lifetime"`
	ConnMaxIdleTime time.Duration `json:"conn_max_idle_time"`

	// Security settings
	TLSEnabled    bool `json:"tls_enabled"`
	TLSSkipVerify bool `json:"tls_skip_verify"`

	// Query settings
	QueryTimeout time.Duration `json:"query_timeout"`
	FetchSize    int           `json:"fetch_size"`

	// Cache settings
	CacheEnabled bool          `json:"cache_enabled"`
	CacheTTL     time.Duration `json:"cache_ttl"`
}

// HealthStatus represents connection health status
type HealthStatus struct {
	IsHealthy       bool              `json:"is_healthy"`
	LastCheck       time.Time         `json:"last_check"`
	ResponseTime    time.Duration     `json:"response_time"`
	ErrorMessage    string            `json:"error_message,omitempty"`
	ConnectionCount int               `json:"connection_count"`
	Details         map[string]string `json:"details"`
}

// NewWMSClientService creates a new WMS client service
// SOLID: D - Dependency Inversion (depends on interfaces)
func NewWMSClientService(
	dbConnection DatabaseConnectionInterface,
	cacheService CacheServiceInterface,
	logger LoggerInterface,
	healthChecker HealthCheckerInterface,
	config *WMSClientConfiguration,
) (*WMSClientService, error) {

	if dbConnection == nil {
		return nil, errors.New("database connection cannot be nil")
	}
	if logger == nil {
		return nil, errors.New("logger cannot be nil")
	}
	if config == nil {
		return nil, errors.New("configuration cannot be nil")
	}

	service := &WMSClientService{
		dbConnection:  dbConnection,
		cacheService:  cacheService,
		logger:        logger,
		healthChecker: healthChecker,
		config:        config,
		timeout:       config.QueryTimeout,
		maxRetries:    3, // Default retry count
		isConnected:   false,
	}

	// Register health check
	if healthChecker != nil {
		healthChecker.RegisterHealthCheck("wms_database", service.pingDatabase)
	}

	return service, nil
}

// ExecuteQuery executes a SQL query and returns results
// SOLID: S - Single responsibility (only executes queries)
func (s *WMSClientService) ExecuteQuery(ctx context.Context, query string, params map[string]interface{}) (*QueryResult, error) {
	if query == "" {
		return nil, errors.New("query cannot be empty")
	}

	s.logger.Debug("Executing WMS query", "query", query, "params", params)

	// Check cache first (if enabled)
	if s.config.CacheEnabled && s.cacheService != nil {
		cacheKey := s.generateCacheKey(query, params)
		if cached, found := s.cacheService.Get(cacheKey); found {
			s.logger.Debug("Query result found in cache", "cache_key", cacheKey)
			if result, ok := cached.(*QueryResult); ok {
				return result, nil
			}
		}
	}

	// Create context with timeout
	queryCtx, cancel := context.WithTimeout(ctx, s.timeout)
	defer cancel()

	// Convert params to slice for database query
	args := s.convertParamsToArgs(params)

	// Execute query with retry logic
	result, err := s.executeQueryWithRetry(queryCtx, query, args)
	if err != nil {
		s.logger.Error("Failed to execute WMS query", err, "query", query)
		return nil, err
	}

	// Cache result (if enabled)
	if s.config.CacheEnabled && s.cacheService != nil {
		cacheKey := s.generateCacheKey(query, params)
		if err := s.cacheService.Set(cacheKey, result, s.config.CacheTTL); err != nil {
			s.logger.Warn("Failed to cache query result", "error", err.Error())
		}
	}

	s.logger.Info("WMS query executed successfully",
		"records_count", len(result.Data),
		"execution_time", result.ExecutionTime)

	return result, nil
}

// GetEntitySchema retrieves schema information for an entity
func (s *WMSClientService) GetEntitySchema(entityName string) (*EntitySchema, error) {
	if entityName == "" {
		return nil, errors.New("entity name cannot be empty")
	}

	// Check cache first
	if s.config.CacheEnabled && s.cacheService != nil {
		cacheKey := fmt.Sprintf("schema:%s", entityName)
		if cached, found := s.cacheService.Get(cacheKey); found {
			if schema, ok := cached.(*EntitySchema); ok {
				return schema, nil
			}
		}
	}

	// Query to get table schema from Oracle data dictionary
	query := `
		SELECT
			column_name,
			data_type,
			nullable,
			data_default,
			data_length
		FROM user_tab_columns
		WHERE table_name = UPPER(?)
		ORDER BY column_id
	`

	ctx, cancel := context.WithTimeout(context.Background(), s.timeout)
	defer cancel()

	rows, err := s.dbConnection.Query(ctx, query, entityName)
	if err != nil {
		return nil, fmt.Errorf("failed to query schema for entity %s: %w", entityName, err)
	}
	defer rows.Close()

	var columns []ColumnDefinition
	for rows.Next() {
		var col ColumnDefinition
		var nullable, defaultValue string

		err := rows.Scan(
			&col.Name,
			&col.DataType,
			&nullable,
			&defaultValue,
			&col.MaxLength,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan column definition: %w", err)
		}

		col.IsNullable = nullable == "Y"
		col.DefaultValue = defaultValue

		columns = append(columns, col)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error reading schema rows: %w", err)
	}

	// Get primary key information
	primaryKeys, err := s.getPrimaryKeys(ctx, entityName)
	if err != nil {
		s.logger.Warn("Failed to get primary keys", "entity", entityName, "error", err.Error())
	}

	// Get index information
	indexes, err := s.getIndexes(ctx, entityName)
	if err != nil {
		s.logger.Warn("Failed to get indexes", "entity", entityName, "error", err.Error())
	}

	schema := &EntitySchema{
		TableName:   entityName,
		Columns:     columns,
		PrimaryKeys: primaryKeys,
		Indexes:     indexes,
	}

	// Cache schema
	if s.config.CacheEnabled && s.cacheService != nil {
		cacheKey := fmt.Sprintf("schema:%s", entityName)
		if err := s.cacheService.Set(cacheKey, schema, s.config.CacheTTL); err != nil {
			s.logger.Warn("Failed to cache schema", "error", err.Error())
		}
	}

	return schema, nil
}

// ValidateConnection validates the database connection
func (s *WMSClientService) ValidateConnection() error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := s.dbConnection.Ping(ctx); err != nil {
		s.isConnected = false
		return fmt.Errorf("connection validation failed: %w", err)
	}

	s.isConnected = true
	s.lastHealthCheck = time.Now()
	return nil
}

// Helper methods

func (s *WMSClientService) executeQueryWithRetry(ctx context.Context, query string, args []interface{}) (*QueryResult, error) {
	var lastErr error
	startTime := time.Now()

	for attempt := 0; attempt < s.maxRetries; attempt++ {
		if attempt > 0 {
			// Exponential backoff
			backoff := time.Duration(attempt*attempt) * time.Second
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(backoff):
			}
		}

		rows, err := s.dbConnection.Query(ctx, query, args...)
		if err != nil {
			lastErr = err
			s.logger.Warn("Query attempt failed", "attempt", attempt+1, "error", err.Error())
			continue
		}

		// Process rows
		data, err := s.processRows(rows)
		rows.Close()

		if err != nil {
			lastErr = err
			continue
		}

		return &QueryResult{
			Data:          data,
			TotalCount:    int64(len(data)),
			HasMore:       false, // This would be determined by pagination logic
			ExecutionTime: time.Since(startTime),
		}, nil
	}

	return nil, fmt.Errorf("query failed after %d attempts: %w", s.maxRetries, lastErr)
}

func (s *WMSClientService) processRows(rows *sql.Rows) ([]map[string]interface{}, error) {
	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var data []map[string]interface{}
	for rows.Next() {
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))
		for i := range values {
			valuePtrs[i] = &values[i]
		}

		if err := rows.Scan(valuePtrs...); err != nil {
			return nil, err
		}

		row := make(map[string]interface{})
		for i, col := range columns {
			row[col] = values[i]
		}
		data = append(data, row)
	}

	return data, rows.Err()
}

func (s *WMSClientService) convertParamsToArgs(params map[string]interface{}) []interface{} {
	args := make([]interface{}, 0, len(params))
	for _, v := range params {
		args = append(args, v)
	}
	return args
}

func (s *WMSClientService) generateCacheKey(query string, params map[string]interface{}) string {
	// Simple cache key generation - could be improved with hashing
	return fmt.Sprintf("query:%s:%v", query, params)
}

func (s *WMSClientService) getPrimaryKeys(ctx context.Context, tableName string) ([]string, error) {
	query := `
		SELECT column_name
		FROM user_cons_columns
		WHERE constraint_name = (
			SELECT constraint_name
			FROM user_constraints
			WHERE table_name = UPPER(?)
			AND constraint_type = 'P'
		)
		ORDER BY position
	`

	rows, err := s.dbConnection.Query(ctx, query, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var primaryKeys []string
	for rows.Next() {
		var columnName string
		if err := rows.Scan(&columnName); err != nil {
			return nil, err
		}
		primaryKeys = append(primaryKeys, columnName)
	}

	return primaryKeys, rows.Err()
}

func (s *WMSClientService) getIndexes(ctx context.Context, tableName string) ([]IndexDefinition, error) {
	query := `
		SELECT
			i.index_name,
			ic.column_name,
			i.uniqueness
		FROM user_indexes i
		JOIN user_ind_columns ic ON i.index_name = ic.index_name
		WHERE i.table_name = UPPER(?)
		ORDER BY i.index_name, ic.column_position
	`

	rows, err := s.dbConnection.Query(ctx, query, tableName)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	indexMap := make(map[string]*IndexDefinition)
	for rows.Next() {
		var indexName, columnName, uniqueness string
		if err := rows.Scan(&indexName, &columnName, &uniqueness); err != nil {
			return nil, err
		}

		if index, exists := indexMap[indexName]; exists {
			index.Columns = append(index.Columns, columnName)
		} else {
			indexMap[indexName] = &IndexDefinition{
				Name:     indexName,
				Columns:  []string{columnName},
				IsUnique: uniqueness == "UNIQUE",
			}
		}
	}

	var indexes []IndexDefinition
	for _, index := range indexMap {
		indexes = append(indexes, *index)
	}

	return indexes, rows.Err()
}

func (s *WMSClientService) pingDatabase(ctx context.Context) error {
	return s.dbConnection.Ping(ctx)
}
