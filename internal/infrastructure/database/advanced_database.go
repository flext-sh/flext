package database

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/jmoiron/sqlx"
	"github.com/pkg/errors"
	"gorm.io/driver/postgres"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// AdvancedDatabase combines GORM and SQLX for maximum flexibility
type AdvancedDatabase struct {
	gormDB *gorm.DB
	sqlxDB *sqlx.DB
	config config.DatabaseConfig
	logger logging.Logger
}

// NewAdvancedDatabase creates a database instance with both GORM and SQLX
func NewAdvancedDatabase(cfg config.DatabaseConfig, log logging.Logger) (*AdvancedDatabase, error) {
	db := &AdvancedDatabase{
		config: cfg,
		logger: log,
	}

	// Initialize GORM
	if err := db.initGORM(); err != nil {
		return nil, errors.Wrap(err, "failed to initialize GORM")
	}

	// Initialize SQLX
	if err := db.initSQLX(); err != nil {
		return nil, errors.Wrap(err, "failed to initialize SQLX")
	}

	// Auto-migrate schemas
	if err := db.AutoMigrate(); err != nil {
		return nil, errors.Wrap(err, "failed to auto-migrate schemas")
	}

	db.logger.Info("Advanced database initialized successfully",
		logging.F("driver", cfg.Driver),
		logging.F("host", cfg.Host),
		logging.F("database", cfg.Database),
	)

	return db, nil
}

// initGORM initializes GORM with advanced configuration
func (db *AdvancedDatabase) initGORM() error {
	var dialector gorm.Dialector

	switch db.config.Driver {
	case "postgres":
		dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s TimeZone=UTC",
			db.config.Host, db.config.Port, db.config.Username, db.config.Password, db.config.Database, db.config.SSLMode)
		dialector = postgres.Open(dsn)
	case "sqlite":
		dialector = sqlite.Open("./flext.db")
	default:
		return fmt.Errorf("unsupported database driver: %s", db.config.Driver)
	}

	// GORM configuration with advanced features
	gormConfig := &gorm.Config{
		Logger: logger.New(
			&GormLoggerAdapter{logger: db.logger},
			logger.Config{
				SlowThreshold:             200 * time.Millisecond,
				LogLevel:                  logger.Info,
				IgnoreRecordNotFoundError: true,
				Colorful:                  false,
			},
		),
		PrepareStmt:                              true,  // Prepared statements
		DisableForeignKeyConstraintWhenMigrating: false, // Keep FK constraints
		CreateBatchSize:                          1000,  // Batch size for bulk operations
	}

	var err error
	db.gormDB, err = gorm.Open(dialector, gormConfig)
	if err != nil {
		return errors.Wrap(err, "failed to connect to database with GORM")
	}

	// Configure connection pool for GORM
	sqlDB, err := db.gormDB.DB()
	if err != nil {
		return errors.Wrap(err, "failed to get underlying sql.DB from GORM")
	}

	sqlDB.SetMaxIdleConns(db.config.MaxIdleConns)
	sqlDB.SetMaxOpenConns(db.config.MaxOpenConns)
	sqlDB.SetConnMaxLifetime(db.config.ConnMaxLifetime)

	return nil
}

// initSQLX initializes SQLX for raw SQL operations
func (db *AdvancedDatabase) initSQLX() error {
	var dsn string

	switch db.config.Driver {
	case "postgres":
		dsn = fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
			db.config.Host, db.config.Port, db.config.Username, db.config.Password, db.config.Database, db.config.SSLMode)
	case "sqlite":
		dsn = "./flext.db" // Default SQLite database file
	default:
		return fmt.Errorf("unsupported database driver: %s", db.config.Driver)
	}

	var err error
	db.sqlxDB, err = sqlx.Connect(db.config.Driver, dsn)
	if err != nil {
		return errors.Wrap(err, "failed to connect to database with SQLX")
	}

	// Configure connection pool for SQLX
	db.sqlxDB.SetMaxIdleConns(db.config.MaxIdleConns)
	db.sqlxDB.SetMaxOpenConns(db.config.MaxOpenConns)
	db.sqlxDB.SetConnMaxLifetime(db.config.ConnMaxLifetime)

	return nil
}

// AutoMigrate creates all tables and indexes
func (db *AdvancedDatabase) AutoMigrate() error {
	models := []interface{}{
		&GormPipeline{},
		&GormPipelineStep{},
		&GormExecution{},
		&GormPlugin{},
	}

	for _, model := range models {
		if err := db.gormDB.AutoMigrate(model); err != nil {
			return errors.Wrapf(err, "failed to migrate model: %T", model)
		}
	}

	// Create custom indexes for performance
	if err := db.createCustomIndexes(); err != nil {
		return errors.Wrap(err, "failed to create custom indexes")
	}

	db.logger.Info("Database schema migration completed successfully")
	return nil
}

// createCustomIndexes creates additional performance indexes
func (db *AdvancedDatabase) createCustomIndexes() error {
	indexes := []string{
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pipelines_status_created_at ON pipelines(status, created_at)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pipelines_tags_gin ON pipelines USING GIN(tags)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pipelines_metadata_gin ON pipelines USING GIN(metadata)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pipeline_steps_pipeline_order ON pipeline_steps(pipeline_id, order_index)",
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_executions_pipeline_created ON pipeline_executions(pipeline_id, created_at DESC)",
	}

	for _, indexSQL := range indexes {
		if _, err := db.sqlxDB.Exec(indexSQL); err != nil {
			db.logger.Warn("Failed to create index, continuing",
				logging.F("sql", indexSQL),
				logging.F("error", err.Error()),
			)
		}
	}

	return nil
}

// GetGORM returns the GORM instance
func (db *AdvancedDatabase) GetGORM() *gorm.DB {
	return db.gormDB
}

// GetSQLX returns the SQLX instance
func (db *AdvancedDatabase) GetSQLX() *sqlx.DB {
	return db.sqlxDB
}

// HealthCheck performs comprehensive database health check
func (db *AdvancedDatabase) HealthCheck(ctx context.Context) error {
	// Check GORM connection
	gormSqlDB, err := db.gormDB.DB()
	if err != nil {
		return errors.Wrap(err, "failed to get GORM underlying database")
	}

	if err := gormSqlDB.PingContext(ctx); err != nil {
		return errors.Wrap(err, "GORM database ping failed")
	}

	// Check SQLX connection
	if err := db.sqlxDB.PingContext(ctx); err != nil {
		return errors.Wrap(err, "SQLX database ping failed")
	}

	// Test a simple query
	var count int
	if err := db.sqlxDB.GetContext(ctx, &count, "SELECT 1"); err != nil {
		return errors.Wrap(err, "database test query failed")
	}

	return nil
}

// GetStatistics returns database performance statistics
func (db *AdvancedDatabase) GetStatistics(ctx context.Context) (*DatabaseStatistics, error) {
	gormSqlDB, _ := db.gormDB.DB()
	gormStats := gormSqlDB.Stats()
	sqlxStats := db.sqlxDB.Stats()

	stats := &DatabaseStatistics{
		GORM: ConnectionStats{
			MaxOpenConnections: gormStats.MaxOpenConnections,
			OpenConnections:    gormStats.OpenConnections,
			InUse:              gormStats.InUse,
			Idle:               gormStats.Idle,
			WaitCount:          gormStats.WaitCount,
			WaitDuration:       gormStats.WaitDuration,
		},
		SQLX: ConnectionStats{
			MaxOpenConnections: sqlxStats.MaxOpenConnections,
			OpenConnections:    sqlxStats.OpenConnections,
			InUse:              sqlxStats.InUse,
			Idle:               sqlxStats.Idle,
			WaitCount:          sqlxStats.WaitCount,
			WaitDuration:       sqlxStats.WaitDuration,
		},
	}

	return stats, nil
}

// Close gracefully closes both database connections
func (db *AdvancedDatabase) Close() error {
	var errs []error

	// Close GORM
	if gormSqlDB, err := db.gormDB.DB(); err == nil {
		if err := gormSqlDB.Close(); err != nil {
			errs = append(errs, errors.Wrap(err, "failed to close GORM database"))
		}
	}

	// Close SQLX
	if err := db.sqlxDB.Close(); err != nil {
		errs = append(errs, errors.Wrap(err, "failed to close SQLX database"))
	}

	if len(errs) > 0 {
		return errors.Errorf("database close errors: %v", errs)
	}

	db.logger.Info("Database connections closed successfully")
	return nil
}

// GormLoggerAdapter adapts our logger to GORM's logger interface
type GormLoggerAdapter struct {
	logger logging.Logger
}

func (l *GormLoggerAdapter) Printf(format string, args ...interface{}) {
	l.logger.Info(fmt.Sprintf(format, args...))
}

// DatabaseStatistics holds connection pool statistics
type DatabaseStatistics struct {
	GORM ConnectionStats `json:"gorm"`
	SQLX ConnectionStats `json:"sqlx"`
}

type ConnectionStats struct {
	MaxOpenConnections int           `json:"max_open_connections"`
	OpenConnections    int           `json:"open_connections"`
	InUse              int           `json:"in_use"`
	Idle               int           `json:"idle"`
	WaitCount          int64         `json:"wait_count"`
	WaitDuration       time.Duration `json:"wait_duration"`
}
