package database

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// ExecutionRepository implements real database operations for executions
type ExecutionRepository struct {
	db     *Database
	logger logging.Logger
}

// NewExecutionRepository creates a new execution repository
func NewExecutionRepository(db *Database, logger logging.Logger) *ExecutionRepository {
	return &ExecutionRepository{
		db:     db,
		logger: logger,
	}
}

// Save persists an execution to the database
func (r *ExecutionRepository) Save(ctx context.Context, execution *Execution) error {
	// Serialize logs and metrics
	logsJSON, err := json.Marshal(execution.Logs)
	if err != nil {
		return fmt.Errorf("failed to marshal logs: %w", err)
	}

	metricsJSON, err := json.Marshal(execution.Metrics)
	if err != nil {
		return fmt.Errorf("failed to marshal metrics: %w", err)
	}

	// Convert duration to milliseconds
	var durationMs *int64
	if execution.Duration > 0 {
		ms := execution.Duration.Milliseconds()
		durationMs = &ms
	}

	// Check if execution exists
	exists, err := r.exists(ctx, execution.ID)
	if err != nil {
		return fmt.Errorf("failed to check execution existence: %w", err)
	}

	if exists {
		// Update existing execution
		query := `
			UPDATE executions 
			SET status = ?, started_at = ?, completed_at = ?, duration_ms = ?, 
			    success = ?, error_message = ?, logs = ?, metrics = ?
			WHERE id = ?
		`
		_, err = r.db.ExecContext(ctx, query,
			execution.Status, execution.StartedAt, execution.CompletedAt,
			durationMs, execution.Success, execution.ErrorMessage,
			string(logsJSON), string(metricsJSON), execution.ID.String())
	} else {
		// Insert new execution
		query := `
			INSERT INTO executions (id, pipeline_id, status, started_at, completed_at, 
			                       duration_ms, success, error_message, logs, metrics)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		`
		_, err = r.db.ExecContext(ctx, query,
			execution.ID.String(), execution.PipelineID.String(), execution.Status,
			execution.StartedAt, execution.CompletedAt, durationMs,
			execution.Success, execution.ErrorMessage,
			string(logsJSON), string(metricsJSON))
	}

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
func (r *ExecutionRepository) FindByID(ctx context.Context, id uuid.UUID) (*Execution, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions WHERE id = ?
	`

	row := r.db.QueryRowContext(ctx, query, id.String())

	var execution Execution
	var logsJSON, metricsJSON string
	var durationMs *int64

	err := row.Scan(
		&execution.ID, &execution.PipelineID, &execution.Status,
		&execution.StartedAt, &execution.CompletedAt, &durationMs,
		&execution.Success, &execution.ErrorMessage,
		&logsJSON, &metricsJSON, &execution.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, ErrExecutionNotFound
		}
		return nil, fmt.Errorf("failed to scan execution: %w", err)
	}

	// Convert duration from milliseconds
	if durationMs != nil {
		execution.Duration = time.Duration(*durationMs) * time.Millisecond
	}

	// Parse logs
	if err := json.Unmarshal([]byte(logsJSON), &execution.Logs); err != nil {
		return nil, fmt.Errorf("failed to unmarshal logs: %w", err)
	}

	// Parse metrics
	if err := json.Unmarshal([]byte(metricsJSON), &execution.Metrics); err != nil {
		return nil, fmt.Errorf("failed to unmarshal metrics: %w", err)
	}

	return &execution, nil
}

// FindByPipelineID retrieves executions by pipeline ID
func (r *ExecutionRepository) FindByPipelineID(ctx context.Context, pipelineID uuid.UUID, limit, offset int) ([]*Execution, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		WHERE pipeline_id = ?
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, pipelineID.String(), limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query executions: %w", err)
	}
	defer rows.Close()

	var executions []*Execution

	for rows.Next() {
		var execution Execution
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

		// Parse logs and metrics
		json.Unmarshal([]byte(logsJSON), &execution.Logs)
		json.Unmarshal([]byte(metricsJSON), &execution.Metrics)

		executions = append(executions, &execution)
	}

	return executions, nil
}

// FindAll retrieves all executions with pagination
func (r *ExecutionRepository) FindAll(ctx context.Context, limit, offset int) ([]*Execution, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query executions: %w", err)
	}
	defer rows.Close()

	var executions []*Execution

	for rows.Next() {
		var execution Execution
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

		// Parse logs and metrics
		json.Unmarshal([]byte(logsJSON), &execution.Logs)
		json.Unmarshal([]byte(metricsJSON), &execution.Metrics)

		executions = append(executions, &execution)
	}

	return executions, nil
}

// FindByStatus retrieves executions by status
func (r *ExecutionRepository) FindByStatus(ctx context.Context, status string, limit, offset int) ([]*Execution, error) {
	query := `
		SELECT id, pipeline_id, status, started_at, completed_at, duration_ms, 
		       success, error_message, logs, metrics, created_at
		FROM executions 
		WHERE status = ?
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, status, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query executions by status: %w", err)
	}
	defer rows.Close()

	var executions []*Execution

	for rows.Next() {
		var execution Execution
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

		// Parse logs and metrics
		json.Unmarshal([]byte(logsJSON), &execution.Logs)
		json.Unmarshal([]byte(metricsJSON), &execution.Metrics)

		executions = append(executions, &execution)
	}

	return executions, nil
}

// Delete removes an execution from the database
func (r *ExecutionRepository) Delete(ctx context.Context, id uuid.UUID) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM executions WHERE id = ?", id.String())
	if err != nil {
		return fmt.Errorf("failed to delete execution: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrExecutionNotFound
	}

	r.logger.Debug("Execution deleted successfully", logging.F("execution_id", id.String()))
	return nil
}

// Count returns the total number of executions
func (r *ExecutionRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM executions").Scan(&count)
	return count, err
}

// CountByPipelineID returns the number of executions for a pipeline
func (r *ExecutionRepository) CountByPipelineID(ctx context.Context, pipelineID uuid.UUID) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, 
		"SELECT COUNT(*) FROM executions WHERE pipeline_id = ?", 
		pipelineID.String()).Scan(&count)
	return count, err
}

// GetExecutionStats returns execution statistics
func (r *ExecutionRepository) GetExecutionStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// Total executions
	var total int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM executions").Scan(&total)
	if err != nil {
		return nil, fmt.Errorf("failed to get total executions: %w", err)
	}
	stats["total"] = total

	// Success rate
	var successful int
	err = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM executions WHERE success = true").Scan(&successful)
	if err != nil {
		return nil, fmt.Errorf("failed to get successful executions: %w", err)
	}
	stats["successful"] = successful

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
	rows, err := r.db.QueryContext(ctx, statusQuery)
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
	var avgDuration *float64
	err = r.db.QueryRowContext(ctx, 
		"SELECT AVG(duration_ms) FROM executions WHERE duration_ms IS NOT NULL").Scan(&avgDuration)
	if err != nil {
		return nil, fmt.Errorf("failed to get average duration: %w", err)
	}
	if avgDuration != nil {
		stats["average_duration_ms"] = *avgDuration
	} else {
		stats["average_duration_ms"] = 0.0
	}

	return stats, nil
}

// Helper methods

func (r *ExecutionRepository) exists(ctx context.Context, id uuid.UUID) (bool, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM executions WHERE id = ?", id.String()).Scan(&count)
	return count > 0, err
}