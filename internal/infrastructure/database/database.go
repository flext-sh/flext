package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	_ "github.com/lib/pq"           // PostgreSQL driver
	_ "github.com/mattn/go-sqlite3" // SQLite driver
)

// DatabaseConfig holds database configuration
type DatabaseConfig struct {
	Driver          string `json:"driver"`          // postgres, sqlite3, mysql
	Host            string `json:"host"`
	Port            int    `json:"port"`
	Database        string `json:"database"`
	Username        string `json:"username"`
	Password        string `json:"password"`
	SSLMode         string `json:"ssl_mode"`
	MaxOpenConns    int    `json:"max_open_conns"`
	MaxIdleConns    int    `json:"max_idle_conns"`
	ConnMaxLifetime time.Duration `json:"conn_max_lifetime"`
}

// Database represents the database connection and operations
type Database struct {
	db     *sql.DB
	config *DatabaseConfig
	logger logging.Logger
}

// NewDatabase creates a new database connection
func NewDatabase(config *DatabaseConfig, logger logging.Logger) (*Database, error) {
	if config == nil {
		config = DefaultDatabaseConfig()
	}

	db := &Database{
		config: config,
		logger: logger,
	}

	if err := db.connect(); err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	if err := db.migrate(); err != nil {
		return nil, fmt.Errorf("failed to migrate database: %w", err)
	}

	return db, nil
}

// DefaultDatabaseConfig returns default database configuration
func DefaultDatabaseConfig() *DatabaseConfig {
	return &DatabaseConfig{
		Driver:          "sqlite3",
		Database:        "./flext.db",
		MaxOpenConns:    25,
		MaxIdleConns:    5,
		ConnMaxLifetime: 5 * time.Minute,
	}
}

// connect establishes database connection
func (d *Database) connect() error {
	dsn := d.buildDSN()
	
	db, err := sql.Open(d.config.Driver, dsn)
	if err != nil {
		return fmt.Errorf("failed to open database: %w", err)
	}

	// Configure connection pool
	db.SetMaxOpenConns(d.config.MaxOpenConns)
	db.SetMaxIdleConns(d.config.MaxIdleConns)
	db.SetConnMaxLifetime(d.config.ConnMaxLifetime)

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	d.db = db
	d.logger.Info("Database connected successfully",
		logging.F("driver", d.config.Driver),
		logging.F("database", d.config.Database),
	)

	return nil
}

// buildDSN builds the database connection string
func (d *Database) buildDSN() string {
	switch d.config.Driver {
	case "postgres":
		return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
			d.config.Host, d.config.Port, d.config.Username, 
			d.config.Password, d.config.Database, d.config.SSLMode)
	case "sqlite3":
		return d.config.Database
	case "mysql":
		return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?parseTime=true",
			d.config.Username, d.config.Password, d.config.Host, 
			d.config.Port, d.config.Database)
	default:
		return d.config.Database
	}
}

// migrate runs database migrations
func (d *Database) migrate() error {
	migrations := []string{
		d.createPipelinesTable(),
		d.createPipelineStepsTable(),
		d.createPluginsTable(),
		d.createExecutionsTable(),
		d.createQualityReportsTable(),
		d.createMetricsTable(),
		d.createAlertsTable(),
		d.createHealthChecksTable(),
	}

	for _, migration := range migrations {
		if _, err := d.db.Exec(migration); err != nil {
			return fmt.Errorf("migration failed: %w", err)
		}
	}

	d.logger.Info("Database migrations completed successfully")
	return nil
}

// Schema definitions
func (d *Database) createPipelinesTable() string {
	return `
		CREATE TABLE IF NOT EXISTS pipelines (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL UNIQUE,
			description TEXT,
			status TEXT NOT NULL DEFAULT 'created',
			tags TEXT, -- JSON array
			metadata TEXT, -- JSON object
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			created_by TEXT,
			version INTEGER DEFAULT 1
		);
		CREATE INDEX IF NOT EXISTS idx_pipelines_name ON pipelines(name);
		CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);
		CREATE INDEX IF NOT EXISTS idx_pipelines_created_at ON pipelines(created_at);
	`
}

func (d *Database) createPipelineStepsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS pipeline_steps (
			id TEXT PRIMARY KEY,
			pipeline_id TEXT NOT NULL,
			name TEXT NOT NULL,
			type TEXT NOT NULL,
			order_index INTEGER NOT NULL,
			config TEXT, -- JSON object
			dependencies TEXT, -- JSON array
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON DELETE CASCADE
		);
		CREATE INDEX IF NOT EXISTS idx_pipeline_steps_pipeline_id ON pipeline_steps(pipeline_id);
		CREATE INDEX IF NOT EXISTS idx_pipeline_steps_order ON pipeline_steps(pipeline_id, order_index);
	`
}

func (d *Database) createPluginsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS plugins (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL UNIQUE,
			type TEXT NOT NULL,
			version TEXT NOT NULL,
			description TEXT,
			author TEXT,
			entry_point TEXT NOT NULL,
			dependencies TEXT, -- JSON array
			config_schema TEXT, -- JSON schema
			status TEXT NOT NULL DEFAULT 'inactive',
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_plugins_name ON plugins(name);
		CREATE INDEX IF NOT EXISTS idx_plugins_type ON plugins(type);
		CREATE INDEX IF NOT EXISTS idx_plugins_status ON plugins(status);
	`
}

func (d *Database) createExecutionsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS executions (
			id TEXT PRIMARY KEY,
			pipeline_id TEXT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			started_at DATETIME,
			completed_at DATETIME,
			duration_ms INTEGER,
			success BOOLEAN,
			error_message TEXT,
			logs TEXT, -- JSON array
			metrics TEXT, -- JSON object
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
		);
		CREATE INDEX IF NOT EXISTS idx_executions_pipeline_id ON executions(pipeline_id);
		CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
		CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at);
	`
}

func (d *Database) createQualityReportsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS quality_reports (
			id TEXT PRIMARY KEY,
			resource_id TEXT NOT NULL,
			resource_type TEXT NOT NULL,
			overall_score REAL NOT NULL,
			max_score REAL NOT NULL,
			status TEXT NOT NULL,
			checks TEXT, -- JSON array
			summary TEXT, -- JSON object
			recommendations TEXT, -- JSON array
			duration_ms INTEGER,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_quality_reports_resource ON quality_reports(resource_id, resource_type);
		CREATE INDEX IF NOT EXISTS idx_quality_reports_created_at ON quality_reports(created_at);
	`
}

func (d *Database) createMetricsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS metrics (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			type TEXT NOT NULL,
			value REAL NOT NULL,
			tags TEXT, -- JSON object
			unit TEXT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name);
		CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
	`
}

func (d *Database) createAlertsTable() string {
	return `
		CREATE TABLE IF NOT EXISTS alerts (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			level TEXT NOT NULL,
			message TEXT NOT NULL,
			component TEXT,
			status TEXT NOT NULL DEFAULT 'firing',
			labels TEXT, -- JSON object
			annotations TEXT, -- JSON object
			value REAL,
			threshold REAL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			resolved_at DATETIME
		);
		CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
		CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level);
		CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
	`
}

func (d *Database) createHealthChecksTable() string {
	return `
		CREATE TABLE IF NOT EXISTS health_checks (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			status TEXT NOT NULL,
			message TEXT,
			duration_ms INTEGER,
			details TEXT, -- JSON object
			error TEXT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
		);
		CREATE INDEX IF NOT EXISTS idx_health_checks_name ON health_checks(name);
		CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_checks(timestamp);
	`
}

// Query methods
func (d *Database) Query(query string, args ...interface{}) (*sql.Rows, error) {
	return d.db.Query(query, args...)
}

func (d *Database) QueryRow(query string, args ...interface{}) *sql.Row {
	return d.db.QueryRow(query, args...)
}

func (d *Database) Exec(query string, args ...interface{}) (sql.Result, error) {
	return d.db.Exec(query, args...)
}

func (d *Database) ExecContext(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
	return d.db.ExecContext(ctx, query, args...)
}

func (d *Database) QueryContext(ctx context.Context, query string, args ...interface{}) (*sql.Rows, error) {
	return d.db.QueryContext(ctx, query, args...)
}

func (d *Database) QueryRowContext(ctx context.Context, query string, args ...interface{}) *sql.Row {
	return d.db.QueryRowContext(ctx, query, args...)
}

// Transaction support
func (d *Database) BeginTx(ctx context.Context) (*sql.Tx, error) {
	return d.db.BeginTx(ctx, nil)
}

// Health check
func (d *Database) Ping() error {
	return d.db.Ping()
}

// Close connection
func (d *Database) Close() error {
	if d.db != nil {
		return d.db.Close()
	}
	return nil
}

// GetDB returns the underlying sql.DB for advanced operations
func (d *Database) GetDB() *sql.DB {
	return d.db
}

// Stats returns database statistics
func (d *Database) Stats() sql.DBStats {
	return d.db.Stats()
}