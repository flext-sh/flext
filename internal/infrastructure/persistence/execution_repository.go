package persistence

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/infrastructure/database"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// PostgreSQLExecutionRepository implements ExecutionRepository for PostgreSQL
type PostgreSQLExecutionRepository struct {
	db     *database.Connection
	logger logging.Logger
}

// NewPostgreSQLExecutionRepository creates a new PostgreSQL execution repository
func NewPostgreSQLExecutionRepository(db *database.Connection, logger logging.Logger) *PostgreSQLExecutionRepository {
	return &PostgreSQLExecutionRepository{
		db:     db,
		logger: logger,
	}
}

// Save persists an execution record to the database
func (r *PostgreSQLExecutionRepository) Save(ctx context.Context, execution *ports.ExecutionRecord) error {
	// Serialize logs and metrics to JSON
	logsJSON, err := json.Marshal(execution.Logs)
	if err != nil {
		return fmt.Errorf("failed to marshal logs: %w", err)
	}

	metricsJSON, err := json.Marshal(execution.Metrics)
	if err != nil {
		return fmt.Errorf("failed to marshal metrics: %w", err)
	}

	// Convert duration to milliseconds for storage
	var durationMs *int64
	if execution.Duration > 0 {
		ms := execution.Duration.Milliseconds()
		durationMs = &ms
	}

	// Set created_at if not set
	if execution.CreatedAt.IsZero() {
		execution.CreatedAt = time.Now().UTC()
	}

	// Use upsert (INSERT ... ON CONFLICT DO UPDATE) for PostgreSQL
	query := `
		INSERT INTO executions (id, pipeline_id, status, started_at, completed_at, 
		                       duration_ms, success, error_message, logs, metrics, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		ON CONFLICT (id) DO UPDATE SET
			status = EXCLUDED.status,
			started_at = EXCLUDED.started_at,
			completed_at = EXCLUDED.completed_at,
			duration_ms = EXCLUDED.duration_ms,
			success = EXCLUDED.success,
			error_message = EXCLUDED.error_message,
			logs = EXCLUDED.logs,
			metrics = EXCLUDED.metrics
	`

	_, err = r.db.GetDB().ExecContext(ctx, query,
		execution.ID.String(),
		execution.PipelineID.String(),
		execution.Status,
		execution.StartedAt,
		execution.CompletedAt,
		durationMs,
		execution.Success,
		execution.ErrorMessage,
		string(logsJSON),
		string(metricsJSON),
		execution.CreatedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to save execution: %w", err)
	}

	r.logger.Debug("Execution saved successfully",
		logging.F("execution_id", execution.ID.String()),
		logging.F("pipeline_id", execution.PipelineID.String()),
		logging.F("status", execution.Status),
	)

	return nil
}

// FindByID retrieves an execution by ID
func (r *PostgreSQLExecutionRepository) FindByID(ctx context.Context, id uuid.UUID) (*ports.ExecutionRecord, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions WHERE id = $1
	`

	row := r.db.GetDB().QueryRowContext(ctx, query, id.String())

	execution, err := r.scanExecution(row)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // Not found
		}
		return nil, fmt.Errorf("failed to find execution by ID: %w", err)
	}

	return execution, nil
}

// Delete removes an execution from the database
func (r *PostgreSQLExecutionRepository) Delete(ctx context.Context, id uuid.UUID) error {
	result, err := r.db.GetDB().ExecContext(ctx, "DELETE FROM executions WHERE id = $1", id.String())
	if err != nil {
		return fmt.Errorf("failed to delete execution: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("execution not found")
	}

	r.logger.Debug("Execution deleted successfully", logging.F("execution_id", id.String()))
	return nil
}

// FindByPipelineID retrieves executions by pipeline ID with pagination
func (r *PostgreSQLExecutionRepository) FindByPipelineID(ctx context.Context, pipelineID uuid.UUID, limit, offset int) ([]*ports.ExecutionRecord, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		WHERE pipeline_id = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, pipelineID.String(), limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query executions by pipeline ID: %w", err)
	}
	defer rows.Close()

	return r.scanExecutions(rows)
}

// FindByStatus retrieves executions by status with pagination
func (r *PostgreSQLExecutionRepository) FindByStatus(ctx context.Context, status string, limit, offset int) ([]*ports.ExecutionRecord, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		WHERE status = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, status, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query executions by status: %w", err)
	}
	defer rows.Close()

	return r.scanExecutions(rows)
}

// FindAll retrieves all executions with pagination
func (r *PostgreSQLExecutionRepository) FindAll(ctx context.Context, limit, offset int) ([]*ports.ExecutionRecord, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query all executions: %w", err)
	}
	defer rows.Close()

	return r.scanExecutions(rows)
}

// Count returns the total number of executions
func (r *PostgreSQLExecutionRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.GetDB().QueryRowContext(ctx, "SELECT COUNT(*) FROM executions").Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count executions: %w", err)
	}
	return count, nil
}

// CountByPipelineID returns the number of executions for a specific pipeline
func (r *PostgreSQLExecutionRepository) CountByPipelineID(ctx context.Context, pipelineID uuid.UUID) (int, error) {
	var count int
	err := r.db.GetDB().QueryRowContext(ctx, 
		"SELECT COUNT(*) FROM executions WHERE pipeline_id = $1", 
		pipelineID.String()).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count executions by pipeline ID: %w", err)
	}
	return count, nil
}

// GetExecutionStats returns aggregated execution statistics
func (r *PostgreSQLExecutionRepository) GetExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// Total executions
	total, err := r.Count(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get total executions: %w", err)
	}
	stats["total_executions"] = total

	// Successful executions
	var successful int
	err = r.db.GetDB().QueryRowContext(ctx, "SELECT COUNT(*) FROM executions WHERE success = true").Scan(&successful)
	if err != nil {
		return nil, fmt.Errorf("failed to get successful executions: %w", err)
	}
	stats["successful_executions"] = successful
	stats["failed_executions"] = total - successful

	// Success rate
	if total > 0 {
		stats["success_rate"] = float64(successful) / float64(total) * 100
	} else {
		stats["success_rate"] = 0.0
	}

	// Status distribution
	statusQuery := `
		SELECT status, COUNT(*) 
		FROM executions 
		GROUP BY status
	`
	rows, err := r.db.GetDB().QueryContext(ctx, statusQuery)
	if err != nil {
		return nil, fmt.Errorf("failed to get status distribution: %w", err)
	}
	defer rows.Close()

	statusDistribution := make(map[string]int)
	for rows.Next() {
		var status string
		var count int
		if err := rows.Scan(&status, &count); err != nil {
			continue
		}
		statusDistribution[status] = count
	}
	stats["status_distribution"] = statusDistribution

	// Average duration
	var avgDurationMs *float64
	err = r.db.GetDB().QueryRowContext(ctx, 
		"SELECT AVG(duration_ms) FROM executions WHERE duration_ms IS NOT NULL").Scan(&avgDurationMs)
	if err != nil {
		return nil, fmt.Errorf("failed to get average duration: %w", err)
	}
	
	if avgDurationMs != nil {
		stats["average_duration_ms"] = *avgDurationMs
		avgDuration := time.Duration(*avgDurationMs) * time.Millisecond
		stats["average_duration"] = avgDuration.String()
	} else {
		stats["average_duration_ms"] = 0.0
		stats["average_duration"] = "0s"
	}

	// Recent activity (last 24 hours)
	var recent24h int
	err = r.db.GetDB().QueryRowContext(ctx, 
		"SELECT COUNT(*) FROM executions WHERE created_at > $1", 
		time.Now().Add(-24*time.Hour)).Scan(&recent24h)
	if err == nil {
		stats["executions_last_24h"] = recent24h
	}

	return stats, nil
}

// GetPipelineStats returns execution statistics for a specific pipeline
func (r *PostgreSQLExecutionRepository) GetPipelineStats(ctx context.Context, pipelineID uuid.UUID) (*ports.ExecutionStats, error) {
	stats := &ports.ExecutionStats{}

	// Total executions for this pipeline
	total, err := r.CountByPipelineID(ctx, pipelineID)
	if err != nil {
		return nil, fmt.Errorf("failed to get pipeline execution count: %w", err)
	}
	stats.TotalExecutions = total

	if total == 0 {
		return stats, nil // No executions, return empty stats
	}

	// Successful executions for this pipeline
	var successful int
	err = r.db.GetDB().QueryRowContext(ctx, 
		"SELECT COUNT(*) FROM executions WHERE pipeline_id = $1 AND success = true", 
		pipelineID.String()).Scan(&successful)
	if err != nil {
		return nil, fmt.Errorf("failed to get successful executions for pipeline: %w", err)
	}
	stats.SuccessfulExecutions = successful
	stats.FailedExecutions = total - successful

	// Success rate
	if total > 0 {
		stats.SuccessRate = float64(successful) / float64(total) * 100
	}

	// Last execution time
	var lastExecution *time.Time
	err = r.db.GetDB().QueryRowContext(ctx, 
		"SELECT MAX(started_at) FROM executions WHERE pipeline_id = $1 AND started_at IS NOT NULL", 
		pipelineID.String()).Scan(&lastExecution)
	if err != nil && err != sql.ErrNoRows {
		return nil, fmt.Errorf("failed to get last execution time: %w", err)
	}
	stats.LastExecution = lastExecution

	// Average execution time for this pipeline
	var avgDurationMs *float64
	err = r.db.GetDB().QueryRowContext(ctx, 
		"SELECT AVG(duration_ms) FROM executions WHERE pipeline_id = $1 AND duration_ms IS NOT NULL", 
		pipelineID.String()).Scan(&avgDurationMs)
	if err != nil && err != sql.ErrNoRows {
		return nil, fmt.Errorf("failed to get average execution time: %w", err)
	}
	
	if avgDurationMs != nil {
		avgDuration := time.Duration(*avgDurationMs) * time.Millisecond
		stats.AverageExecutionTime = &avgDuration
	}

	return stats, nil
}

// Helper methods

// scanExecution scans a single execution from a database row
func (r *PostgreSQLExecutionRepository) scanExecution(row *sql.Row) (*ports.ExecutionRecord, error) {
	var execution ports.ExecutionRecord
	var logsJSON, metricsJSON string
	var durationMs *int64

	err := row.Scan(
		&execution.ID, &execution.PipelineID, &execution.Status,
		&execution.StartedAt, &execution.CompletedAt, &durationMs,
		&execution.Success, &execution.ErrorMessage,
		&logsJSON, &metricsJSON, &execution.CreatedAt,
	)

	if err != nil {
		return nil, err
	}

	// Convert duration from milliseconds
	if durationMs != nil {
		execution.Duration = time.Duration(*durationMs) * time.Millisecond
	}

	// Parse logs (ignore errors for empty/invalid JSON)
	if logsJSON != "" && logsJSON != "null" {
		json.Unmarshal([]byte(logsJSON), &execution.Logs)
	}
	if execution.Logs == nil {
		execution.Logs = []ports.ExecutionLog{}
	}

	// Parse metrics (ignore errors for empty/invalid JSON)
	if metricsJSON != "" && metricsJSON != "null" {
		json.Unmarshal([]byte(metricsJSON), &execution.Metrics)
	}
	if execution.Metrics == nil {
		execution.Metrics = make(map[string]interface{})
	}

	return &execution, nil
}

// scanExecutions scans multiple executions from database rows
func (r *PostgreSQLExecutionRepository) scanExecutions(rows *sql.Rows) ([]*ports.ExecutionRecord, error) {
	var executions []*ports.ExecutionRecord

	for rows.Next() {
		var execution ports.ExecutionRecord
		var logsJSON, metricsJSON string
		var durationMs *int64

		err := rows.Scan(
			&execution.ID, &execution.PipelineID, &execution.Status,
			&execution.StartedAt, &execution.CompletedAt, &durationMs,
			&execution.Success, &execution.ErrorMessage,
			&logsJSON, &metricsJSON, &execution.CreatedAt,
		)

		if err != nil {
			return nil, fmt.Errorf("failed to scan execution: %w", err)
		}

		// Convert duration from milliseconds
		if durationMs != nil {
			execution.Duration = time.Duration(*durationMs) * time.Millisecond
		}

		// Parse logs and metrics (ignore errors for empty/invalid JSON)
		if logsJSON != "" && logsJSON != "null" {
			json.Unmarshal([]byte(logsJSON), &execution.Logs)
		}
		if execution.Logs == nil {
			execution.Logs = []ports.ExecutionLog{}
		}

		if metricsJSON != "" && metricsJSON != "null" {
			json.Unmarshal([]byte(metricsJSON), &execution.Metrics)
		}
		if execution.Metrics == nil {
			execution.Metrics = make(map[string]interface{})
		}

		executions = append(executions, &execution)
	}

	return executions, nil
}

// InMemoryExecutionRepository provides an in-memory implementation for testing
type InMemoryExecutionRepository struct {
	executions map[string]*ports.ExecutionRecord
	logger     logging.Logger
}

// NewInMemoryExecutionRepository creates a new in-memory execution repository
func NewInMemoryExecutionRepository() *InMemoryExecutionRepository {
	return &InMemoryExecutionRepository{
		executions: make(map[string]*ports.ExecutionRecord),
		logger:     logging.GetLogger(),
	}
}

// Save persists an execution record to memory
func (r *InMemoryExecutionRepository) Save(ctx context.Context, execution *ports.ExecutionRecord) error {
	if execution.ID == uuid.Nil {
		execution.ID = uuid.New()
	}
	if execution.CreatedAt.IsZero() {
		execution.CreatedAt = time.Now().UTC()
	}

	// Set success flag based on status and error
	execution.Success = (execution.Status == "completed" || execution.Status == "success") && execution.ErrorMessage == ""

	// Calculate duration if not set
	if execution.Duration == 0 && execution.StartedAt != nil && execution.CompletedAt != nil {
		execution.Duration = execution.CompletedAt.Sub(*execution.StartedAt)
	}

	// Deep copy to avoid mutations
	copy := *execution
	if copy.Logs == nil {
		copy.Logs = []ports.ExecutionLog{}
	}
	if copy.Metrics == nil {
		copy.Metrics = make(map[string]interface{})
	}

	r.executions[execution.ID.String()] = &copy

	r.logger.Debug("Execution saved to memory",
		logging.F("execution_id", execution.ID.String()),
		logging.F("pipeline_id", execution.PipelineID.String()),
		logging.F("status", execution.Status),
	)

	return nil
}

// FindByID retrieves an execution by ID from memory
func (r *InMemoryExecutionRepository) FindByID(ctx context.Context, id uuid.UUID) (*ports.ExecutionRecord, error) {
	execution, exists := r.executions[id.String()]
	if !exists {
		return nil, nil
	}

	// Return a copy to avoid mutations
	copy := *execution
	return &copy, nil
}

// Delete removes an execution from memory
func (r *InMemoryExecutionRepository) Delete(ctx context.Context, id uuid.UUID) error {
	if _, exists := r.executions[id.String()]; !exists {
		return fmt.Errorf("execution not found")
	}

	delete(r.executions, id.String())
	r.logger.Debug("Execution deleted from memory", logging.F("execution_id", id.String()))
	return nil
}

// FindByPipelineID retrieves executions by pipeline ID from memory
func (r *InMemoryExecutionRepository) FindByPipelineID(ctx context.Context, pipelineID uuid.UUID, limit, offset int) ([]*ports.ExecutionRecord, error) {
	var results []*ports.ExecutionRecord

	for _, execution := range r.executions {
		if execution.PipelineID == pipelineID {
			copy := *execution
			results = append(results, &copy)
		}
	}

	// Sort by creation time (newest first)
	for i := 0; i < len(results)-1; i++ {
		for j := i + 1; j < len(results); j++ {
			if results[i].CreatedAt.Before(results[j].CreatedAt) {
				results[i], results[j] = results[j], results[i]
			}
		}
	}

	// Apply pagination
	if offset >= len(results) {
		return []*ports.ExecutionRecord{}, nil
	}

	end := offset + limit
	if end > len(results) {
		end = len(results)
	}

	return results[offset:end], nil
}

// FindByStatus retrieves executions by status from memory
func (r *InMemoryExecutionRepository) FindByStatus(ctx context.Context, status string, limit, offset int) ([]*ports.ExecutionRecord, error) {
	var results []*ports.ExecutionRecord

	for _, execution := range r.executions {
		if execution.Status == status {
			copy := *execution
			results = append(results, &copy)
		}
	}

	// Apply pagination
	if offset >= len(results) {
		return []*ports.ExecutionRecord{}, nil
	}

	end := offset + limit
	if end > len(results) {
		end = len(results)
	}

	return results[offset:end], nil
}

// FindAll retrieves all executions from memory
func (r *InMemoryExecutionRepository) FindAll(ctx context.Context, limit, offset int) ([]*ports.ExecutionRecord, error) {
	var results []*ports.ExecutionRecord

	for _, execution := range r.executions {
		copy := *execution
		results = append(results, &copy)
	}

	// Apply pagination
	if offset >= len(results) {
		return []*ports.ExecutionRecord{}, nil
	}

	end := offset + limit
	if end > len(results) {
		end = len(results)
	}

	return results[offset:end], nil
}

// Count returns the total number of executions in memory
func (r *InMemoryExecutionRepository) Count(ctx context.Context) (int, error) {
	return len(r.executions), nil
}

// CountByPipelineID returns the number of executions for a specific pipeline in memory
func (r *InMemoryExecutionRepository) CountByPipelineID(ctx context.Context, pipelineID uuid.UUID) (int, error) {
	count := 0
	for _, execution := range r.executions {
		if execution.PipelineID == pipelineID {
			count++
		}
	}
	return count, nil
}

// GetExecutionStats returns aggregated execution statistics from memory
func (r *InMemoryExecutionRepository) GetExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	total := len(r.executions)
	successful := 0
	statusDistribution := make(map[string]int)

	for _, execution := range r.executions {
		if execution.Success {
			successful++
		}
		statusDistribution[execution.Status]++
	}

	stats["total_executions"] = total
	stats["successful_executions"] = successful
	stats["failed_executions"] = total - successful

	if total > 0 {
		stats["success_rate"] = float64(successful) / float64(total) * 100
	} else {
		stats["success_rate"] = 0.0
	}

	stats["status_distribution"] = statusDistribution

	return stats, nil
}

// GetPipelineStats returns execution statistics for a specific pipeline from memory
func (r *InMemoryExecutionRepository) GetPipelineStats(ctx context.Context, pipelineID uuid.UUID) (*ports.ExecutionStats, error) {
	stats := &ports.ExecutionStats{}

	var pipelineExecutions []*ports.ExecutionRecord
	for _, execution := range r.executions {
		if execution.PipelineID == pipelineID {
			pipelineExecutions = append(pipelineExecutions, execution)
		}
	}

	stats.TotalExecutions = len(pipelineExecutions)

	if stats.TotalExecutions == 0 {
		return stats, nil
	}

	successful := 0
	var totalDuration time.Duration
	durationCount := 0

	for _, execution := range pipelineExecutions {
		if execution.Success {
			successful++
		}
		if execution.Duration > 0 {
			totalDuration += execution.Duration
			durationCount++
		}
		if stats.LastExecution == nil || (execution.StartedAt != nil && 
			(stats.LastExecution == nil || execution.StartedAt.After(*stats.LastExecution))) {
			stats.LastExecution = execution.StartedAt
		}
	}

	stats.SuccessfulExecutions = successful
	stats.FailedExecutions = stats.TotalExecutions - successful

	if stats.TotalExecutions > 0 {
		stats.SuccessRate = float64(successful) / float64(stats.TotalExecutions) * 100
	}

	if durationCount > 0 {
		avgDuration := totalDuration / time.Duration(durationCount)
		stats.AverageExecutionTime = &avgDuration
	}

	return stats, nil
}