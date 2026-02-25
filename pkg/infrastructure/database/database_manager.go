package database

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// DatabaseManager manages all database repositories and operations
type DatabaseManager struct {
	db                 *Database
	logger             logging.Logger
	PipelineRepository *PipelineRepository
	PluginRepository   *PluginRepository
	// ExecutionRepository *ExecutionRepository // Disabled - implementation not found
}

// NewDatabaseManager creates a new database manager with all repositories
func NewDatabaseManager(config *DatabaseConfig, logger logging.Logger) (*DatabaseManager, error) {
	// Create database connection
	db, err := NewDatabase(config, logger)
	if err != nil {
		return nil, fmt.Errorf("failed to create database: %w", err)
	}

	// Create repositories
	pipelineRepo := NewPipelineRepository(db, logger)
	pluginRepo := NewPluginRepository(db, logger)
	// executionRepo := NewExecutionRepository(db, logger) // Disabled - implementation not found

	manager := &DatabaseManager{
		db:                 db,
		logger:             logger,
		PipelineRepository: pipelineRepo,
		PluginRepository:   pluginRepo,
		// ExecutionRepository: executionRepo, // Disabled - implementation not found
	}

	// Test connectivity
	if err := manager.HealthCheck(); err != nil {
		return nil, fmt.Errorf("database health check failed: %w", err)
	}

	logger.Info("Database manager initialized successfully",
		logging.F("driver", config.Driver),
		logging.F("database", config.Database),
	)

	return manager, nil
}

// HealthCheck performs a comprehensive health check on all database components
func (dm *DatabaseManager) HealthCheck() error {
	// Test basic connectivity
	if err := dm.db.Ping(); err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	// Test each table with a simple count query
	ctx := context.Background()

	tables := []string{"pipelines", "pipeline_steps", "plugins", "executions"}
	for _, table := range tables {
		var count int
		query := fmt.Sprintf("SELECT COUNT(*) FROM %s", table)
		if err := dm.db.QueryRowContext(ctx, query).Scan(&count); err != nil {
			return fmt.Errorf("failed to query table %s: %w", table, err)
		}
	}

	dm.logger.Debug("Database health check passed")
	return nil
}

// GetDatabaseStats returns comprehensive database statistics
func (dm *DatabaseManager) GetDatabaseStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// Basic database info
	dbStats := dm.db.Stats()
	stats["connection_pool"] = map[string]interface{}{
		"max_open_connections": dbStats.MaxOpenConnections,
		"open_connections":     dbStats.OpenConnections,
		"in_use":               dbStats.InUse,
		"idle":                 dbStats.Idle,
		"wait_count":           dbStats.WaitCount,
		"wait_duration":        dbStats.WaitDuration.String(),
		"max_idle_closed":      dbStats.MaxIdleClosed,
		"max_idle_time_closed": dbStats.MaxIdleTimeClosed,
		"max_lifetime_closed":  dbStats.MaxLifetimeClosed,
	}

	// Table counts
	tableCounts := make(map[string]int)
	tables := []string{"pipelines", "pipeline_steps", "plugins", "executions",
		"quality_reports", "metrics", "alerts", "health_checks"}

	for _, table := range tables {
		var count int
		query := fmt.Sprintf("SELECT COUNT(*) FROM %s", table)
		if err := dm.db.QueryRowContext(ctx, query).Scan(&count); err != nil {
			dm.logger.Error("Failed to get count for table",
				logging.F("table", table),
				logging.F("error", err.Error()),
			)
			tableCounts[table] = -1 // indicate error
		} else {
			tableCounts[table] = count
		}
	}
	stats["table_counts"] = tableCounts

	// Execution statistics
	// ExecutionRepository disabled - not implemented
	// if execStats, err := dm.ExecutionRepository.GetExecutionStats(ctx); err != nil {
	//	dm.logger.Error("Failed to get execution stats", logging.F("error", err.Error()))
	// } else {
	//	stats["execution_stats"] = execStats
	// }

	// Recent activity (last 24 hours)
	recentActivity := make(map[string]int)

	// Recent pipelines
	var recentPipelines int
	err := dm.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM pipelines WHERE created_at > datetime('now', '-1 day')").Scan(&recentPipelines)
	if err != nil {
		dm.logger.Error("Failed to get recent pipelines", logging.F("error", err.Error()))
	}
	recentActivity["pipelines_24h"] = recentPipelines

	// Recent executions
	var recentExecutions int
	err = dm.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM executions WHERE created_at > datetime('now', '-1 day')").Scan(&recentExecutions)
	if err != nil {
		dm.logger.Error("Failed to get recent executions", logging.F("error", err.Error()))
	}
	recentActivity["executions_24h"] = recentExecutions

	stats["recent_activity"] = recentActivity

	return stats, nil
}

// RunMaintenance performs database maintenance tasks
func (dm *DatabaseManager) RunMaintenance(ctx context.Context) error {
	dm.logger.Info("Starting database maintenance")

	// Clean up old executions (older than 30 days)
	result, err := dm.db.ExecContext(ctx,
		"DELETE FROM executions WHERE created_at < datetime('now', '-30 days')")
	if err != nil {
		return fmt.Errorf("failed to clean up old executions: %w", err)
	}

	if deletedRows, err := result.RowsAffected(); err == nil {
		dm.logger.Info("Cleaned up old executions",
			logging.F("deleted_rows", deletedRows),
		)
	}

	// Clean up old metrics (older than 7 days)
	result, err = dm.db.ExecContext(ctx,
		"DELETE FROM metrics WHERE timestamp < datetime('now', '-7 days')")
	if err != nil {
		return fmt.Errorf("failed to clean up old metrics: %w", err)
	}

	if deletedRows, err := result.RowsAffected(); err == nil {
		dm.logger.Info("Cleaned up old metrics",
			logging.F("deleted_rows", deletedRows),
		)
	}

	// Clean up resolved alerts (older than 14 days)
	result, err = dm.db.ExecContext(ctx,
		"DELETE FROM alerts WHERE status = 'resolved' AND resolved_at < datetime('now', '-14 days')")
	if err != nil {
		return fmt.Errorf("failed to clean up old alerts: %w", err)
	}

	if deletedRows, err := result.RowsAffected(); err == nil {
		dm.logger.Info("Cleaned up old alerts",
			logging.F("deleted_rows", deletedRows),
		)
	}

	// Clean up old health checks (older than 3 days)
	result, err = dm.db.ExecContext(ctx,
		"DELETE FROM health_checks WHERE timestamp < datetime('now', '-3 days')")
	if err != nil {
		return fmt.Errorf("failed to clean up old health checks: %w", err)
	}

	if deletedRows, err := result.RowsAffected(); err == nil {
		dm.logger.Info("Cleaned up old health checks",
			logging.F("deleted_rows", deletedRows),
		)
	}

	// Vacuum database (SQLite specific optimization)
	if dm.db.config.Driver == "sqlite3" {
		if _, err := dm.db.Exec("VACUUM"); err != nil {
			dm.logger.Error("Failed to vacuum database", logging.F("error", err.Error()))
		} else {
			dm.logger.Info("Database vacuum completed")
		}
	}

	dm.logger.Info("Database maintenance completed")
	return nil
}

// Transaction support for complex operations
func (dm *DatabaseManager) WithTransaction(ctx context.Context, fn func(ctx context.Context) error) error {
	tx, err := dm.db.BeginTx(ctx)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
			panic(r)
		}
	}()

	if err := fn(ctx); err != nil {
		if rollbackErr := tx.Rollback(); rollbackErr != nil {
			dm.logger.Error("Failed to rollback transaction",
				logging.F("original_error", err.Error()),
				logging.F("rollback_error", rollbackErr.Error()),
			)
		}
		return err
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %w", err)
	}

	return nil
}

// Close shuts down the database manager and all connections
func (dm *DatabaseManager) Close() error {
	dm.logger.Info("Shutting down database manager")
	return dm.db.Close()
}

// GetDatabase returns the underlying database for advanced operations
func (dm *DatabaseManager) GetDatabase() *Database {
	return dm.db
}

// Backup creates a database backup (SQLite specific)
func (dm *DatabaseManager) Backup(ctx context.Context, backupPath string) error {
	if dm.db.config.Driver != "sqlite3" {
		return fmt.Errorf("backup only supported for SQLite databases")
	}

	// For SQLite, we can use the backup API or simple file copy
	// This is a simplified implementation
	query := fmt.Sprintf("VACUUM INTO '%s'", backupPath)
	if _, err := dm.db.ExecContext(ctx, query); err != nil {
		return fmt.Errorf("failed to create backup: %w", err)
	}

	dm.logger.Info("Database backup created",
		logging.F("backup_path", backupPath),
	)

	return nil
}

// GetRepository returns a specific repository by name
func (dm *DatabaseManager) GetRepository(name string) interface{} {
	switch name {
	case "pipeline":
		return dm.PipelineRepository
	case "plugin":
		return dm.PluginRepository
	case "execution":
		// return dm.ExecutionRepository // Disabled - ExecutionRepository not implemented
		return nil
	default:
		return nil
	}
}
