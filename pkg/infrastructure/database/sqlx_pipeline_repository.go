package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	"github.com/samber/lo"
)

// SqlxPipelineRepository high-performance SQLX repository with functional programming
type SqlxPipelineRepository struct {
	db     *sqlx.DB
	logger logging.Logger
}

// NewSqlxPipelineRepository creates a new SQLX repository
func NewSqlxPipelineRepository(db *sqlx.DB, logger logging.Logger) *SqlxPipelineRepository {
	return &SqlxPipelineRepository{
		db:     db,
		logger: logger.With(logging.F("component", "sqlx_pipeline_repo")),
	}
}

// PipelineRow represents database row structure
type PipelineRow struct {
	ID            string         `db:"id"`
	Name          string         `db:"name"`
	Description   sql.NullString `db:"description"`
	IsActive      bool           `db:"is_active"`
	Tags          pq.StringArray `db:"tags"`
	Configuration []byte         `db:"configuration"`
	Schedule      sql.NullString `db:"schedule"`
	CreatedAt     time.Time      `db:"created_at"`
	UpdatedAt     time.Time      `db:"updated_at"`
}

// Save saves a pipeline using high-performance SQLX with batch operations
func (r *SqlxPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	tx, err := r.db.BeginTxx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Upsert pipeline using functional programming approach
	query := `
		INSERT INTO pipelines (id, name, description, is_active, tags, configuration, schedule, created_at, updated_at)
		VALUES (:id, :name, :description, :is_active, :tags, :configuration, :schedule, :created_at, :updated_at)
		ON CONFLICT (id) DO UPDATE SET
			name = EXCLUDED.name,
			description = EXCLUDED.description,
			is_active = EXCLUDED.is_active,
			tags = EXCLUDED.tags,
			configuration = EXCLUDED.configuration,
			schedule = EXCLUDED.schedule,
			updated_at = EXCLUDED.updated_at
	`

	row := PipelineRow{
		ID:            pipeline.ID.String(),
		Name:          pipeline.Name,
		IsActive:      pipeline.IsActive,
		Tags:          pq.StringArray(pipeline.Tags),
		Configuration: []byte("{}"), // Simplified for now
		CreatedAt:     pipeline.CreatedAt,
		UpdatedAt:     pipeline.UpdatedAt,
	}

	if pipeline.Description != "" {
		row.Description = sql.NullString{String: pipeline.Description, Valid: true}
	}

	if pipeline.Schedule != "" {
		row.Schedule = sql.NullString{String: pipeline.Schedule, Valid: true}
	}

	_, err = tx.NamedExecContext(ctx, query, row)
	if err != nil {
		return fmt.Errorf("failed to save pipeline: %w", err)
	}

	return tx.Commit()
}

// GetByID finds pipeline by ID using high-performance SQLX
func (r *SqlxPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	query := `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM pipelines
		WHERE id = $1
	`

	var row PipelineRow
	err := r.db.GetContext(ctx, &row, query, id.String())
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to get pipeline: %w", err)
	}

	return r.rowToPipeline(row)
}

// FindByID finds pipeline by string ID (for interface compatibility)
func (r *SqlxPipelineRepository) FindByID(ctx context.Context, id string) (*entities.Pipeline, error) {
	uuid, err := uuid.Parse(id)
	if err != nil {
		return nil, fmt.Errorf("invalid UUID format: %w", err)
	}
	return r.GetByID(ctx, uuid)
}

// GetByName finds pipeline by name
func (r *SqlxPipelineRepository) GetByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	query := `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM pipelines
		WHERE name = $1
	`

	var row PipelineRow
	err := r.db.GetContext(ctx, &row, query, name)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to get pipeline by name: %w", err)
	}

	return r.rowToPipeline(row)
}

// List lists pipelines with functional programming transformations
func (r *SqlxPipelineRepository) List(ctx context.Context, filter interface{}) ([]*entities.Pipeline, error) {
	query := `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM pipelines
		ORDER BY created_at DESC
	`

	var rows []PipelineRow
	err := r.db.SelectContext(ctx, &rows, query)
	if err != nil {
		return nil, fmt.Errorf("failed to list pipelines: %w", err)
	}

	// Use functional programming to transform rows to entities
	pipelines := lo.FilterMap(rows, func(row PipelineRow, _ int) (*entities.Pipeline, bool) {
		pipeline, err := r.rowToPipeline(row)
		if err != nil {
			r.logger.Error("Failed to convert row to pipeline", logging.F("error", err))
			return nil, false
		}
		return pipeline, true
	})

	return pipelines, nil
}

// Count returns total number of pipelines
func (r *SqlxPipelineRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM pipelines`

	var count int
	err := r.db.GetContext(ctx, &count, query)
	if err != nil {
		return 0, fmt.Errorf("failed to count pipelines: %w", err)
	}

	return count, nil
}

// GetPipelineMetrics gets metrics using functional programming
func (r *SqlxPipelineRepository) GetPipelineMetrics(ctx context.Context) (map[string]interface{}, error) {
	query := `
		SELECT
			COUNT(*) as total_pipelines,
			COUNT(CASE WHEN is_active = true THEN 1 END) as active_pipelines,
			COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_pipelines
		FROM pipelines
	`

	type MetricsRow struct {
		TotalPipelines    int `db:"total_pipelines"`
		ActivePipelines   int `db:"active_pipelines"`
		InactivePipelines int `db:"inactive_pipelines"`
	}

	var result MetricsRow
	err := r.db.GetContext(ctx, &result, query)
	if err != nil {
		return nil, fmt.Errorf("failed to get pipeline metrics: %w", err)
	}

	// Use functional programming to build metrics map
	metrics := lo.Assign(map[string]interface{}{
		"total_pipelines":    result.TotalPipelines,
		"active_pipelines":   result.ActivePipelines,
		"inactive_pipelines": result.InactivePipelines,
	})

	return metrics, nil
}

// rowToPipeline converts database row to domain entity using proper constructor
func (r *SqlxPipelineRepository) rowToPipeline(row PipelineRow) (*entities.Pipeline, error) {
	id, err := uuid.Parse(row.ID)
	if err != nil {
		return nil, fmt.Errorf("invalid UUID: %w", err)
	}

	description := ""
	if row.Description.Valid {
		description = row.Description.String
	}

	// Create pipeline using proper domain constructor
	pipeline, err := entities.NewPipeline(row.Name, description)
	if err != nil {
		return nil, fmt.Errorf("failed to create pipeline entity: %w", err)
	}

	// Set ID manually since NewPipeline generates a new one
	pipeline.ID = id
	pipeline.IsActive = row.IsActive
	pipeline.Tags = []string(row.Tags)
	pipeline.CreatedAt = row.CreatedAt
	pipeline.UpdatedAt = row.UpdatedAt

	if row.Schedule.Valid {
		pipeline.Schedule = row.Schedule.String
	}

	return pipeline, nil
}

// HealthCheck performs repository health check
func (r *SqlxPipelineRepository) HealthCheck(ctx context.Context) error {
	err := r.db.PingContext(ctx)
	if err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	// Test a simple query
	var count int
	err = r.db.GetContext(ctx, &count, "SELECT COUNT(*) FROM pipelines")
	if err != nil {
		return fmt.Errorf("failed to query pipelines table: %w", err)
	}

	r.logger.Info("SQLX Repository health check passed",
		logging.F("pipeline_count", count))

	return nil
}
