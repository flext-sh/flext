package database

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// PipelineRepository implements real database operations for pipelines
type PipelineRepository struct {
	db     *Database
	logger logging.Logger
}

// NewPipelineRepository creates a new pipeline repository
func NewPipelineRepository(db *Database, logger logging.Logger) *PipelineRepository {
	return &PipelineRepository{
		db:     db,
		logger: logger,
	}
}

// Save persists a pipeline to the database
func (r *PipelineRepository) Save(ctx context.Context, pipeline *Pipeline) error {
	// Serialize tags and metadata
	tagsJSON, err := json.Marshal(pipeline.Tags)
	if err != nil {
		return fmt.Errorf("failed to marshal tags: %w", err)
	}

	metadataJSON, err := json.Marshal(pipeline.Metadata)
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}

	// Check if pipeline exists
	exists, err := r.exists(ctx, pipeline.ID)
	if err != nil {
		return fmt.Errorf("failed to check pipeline existence: %w", err)
	}

	if exists {
		// Update existing pipeline
		query := `
			UPDATE pipelines 
			SET name = ?, description = ?, status = ?, tags = ?, metadata = ?, 
			    updated_at = CURRENT_TIMESTAMP, version = version + 1
			WHERE id = ?
		`
		_, err = r.db.ExecContext(ctx, query, 
			pipeline.Name, pipeline.Description, pipeline.Status.String(),
			string(tagsJSON), string(metadataJSON), pipeline.ID.String())
	} else {
		// Insert new pipeline
		query := `
			INSERT INTO pipelines (id, name, description, status, tags, metadata, created_by)
			VALUES (?, ?, ?, ?, ?, ?, ?)
		`
		_, err = r.db.ExecContext(ctx, query,
			pipeline.ID.String(), pipeline.Name, pipeline.Description, 
			pipeline.Status.String(), string(tagsJSON), string(metadataJSON), 
			pipeline.CreatedBy)
	}

	if err != nil {
		return fmt.Errorf("failed to save pipeline: %w", err)
	}

	// Save pipeline steps
	if err := r.saveSteps(ctx, pipeline); err != nil {
		return fmt.Errorf("failed to save pipeline steps: %w", err)
	}

	r.logger.Debug("Pipeline saved successfully",
		logging.F("pipeline_id", pipeline.ID.String()),
		logging.F("name", pipeline.Name),
	)

	return nil
}

// FindByID retrieves a pipeline by ID
func (r *PipelineRepository) FindByID(ctx context.Context, id uuid.UUID) (*Pipeline, error) {
	query := `
		SELECT id, name, description, status, tags, metadata, created_at, updated_at, created_by, version
		FROM pipelines WHERE id = ?
	`
	
	row := r.db.QueryRowContext(ctx, query, id.String())
	
	var pipeline Pipeline
	var tagsJSON, metadataJSON string
	var statusStr string
	
	err := row.Scan(
		&pipeline.ID, &pipeline.Name, &pipeline.Description, &statusStr,
		&tagsJSON, &metadataJSON, &pipeline.CreatedAt, &pipeline.UpdatedAt,
		&pipeline.CreatedBy, &pipeline.Version,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, ErrPipelineNotFound
		}
		return nil, fmt.Errorf("failed to scan pipeline: %w", err)
	}

	// Parse status
	if err := pipeline.Status.FromString(statusStr); err != nil {
		return nil, fmt.Errorf("invalid pipeline status: %w", err)
	}

	// Parse tags
	if err := json.Unmarshal([]byte(tagsJSON), &pipeline.Tags); err != nil {
		return nil, fmt.Errorf("failed to unmarshal tags: %w", err)
	}

	// Parse metadata
	if err := json.Unmarshal([]byte(metadataJSON), &pipeline.Metadata); err != nil {
		return nil, fmt.Errorf("failed to unmarshal metadata: %w", err)
	}

	// Load steps
	steps, err := r.loadSteps(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to load pipeline steps: %w", err)
	}
	pipeline.Steps = steps

	return &pipeline, nil
}

// FindByName retrieves a pipeline by name
func (r *PipelineRepository) FindByName(ctx context.Context, name string) (*Pipeline, error) {
	query := `
		SELECT id, name, description, status, tags, metadata, created_at, updated_at, created_by, version
		FROM pipelines WHERE name = ?
	`
	
	row := r.db.QueryRowContext(ctx, query, name)
	
	var pipeline Pipeline
	var tagsJSON, metadataJSON string
	var statusStr string
	
	err := row.Scan(
		&pipeline.ID, &pipeline.Name, &pipeline.Description, &statusStr,
		&tagsJSON, &metadataJSON, &pipeline.CreatedAt, &pipeline.UpdatedAt,
		&pipeline.CreatedBy, &pipeline.Version,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, ErrPipelineNotFound
		}
		return nil, fmt.Errorf("failed to scan pipeline: %w", err)
	}

	// Parse status
	if err := pipeline.Status.FromString(statusStr); err != nil {
		return nil, fmt.Errorf("invalid pipeline status: %w", err)
	}

	// Parse tags and metadata
	json.Unmarshal([]byte(tagsJSON), &pipeline.Tags)
	json.Unmarshal([]byte(metadataJSON), &pipeline.Metadata)

	// Load steps
	steps, err := r.loadSteps(ctx, pipeline.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to load pipeline steps: %w", err)
	}
	pipeline.Steps = steps

	return &pipeline, nil
}

// FindAll retrieves all pipelines with pagination
func (r *PipelineRepository) FindAll(ctx context.Context, limit, offset int) ([]*Pipeline, error) {
	query := `
		SELECT id, name, description, status, tags, metadata, created_at, updated_at, created_by, version
		FROM pipelines 
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`
	
	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query pipelines: %w", err)
	}
	defer rows.Close()

	var pipelines []*Pipeline
	
	for rows.Next() {
		var pipeline Pipeline
		var tagsJSON, metadataJSON string
		var statusStr string
		
		err := rows.Scan(
			&pipeline.ID, &pipeline.Name, &pipeline.Description, &statusStr,
			&tagsJSON, &metadataJSON, &pipeline.CreatedAt, &pipeline.UpdatedAt,
			&pipeline.CreatedBy, &pipeline.Version,
		)
		
		if err != nil {
			return nil, fmt.Errorf("failed to scan pipeline: %w", err)
		}

		// Parse status
		pipeline.Status.FromString(statusStr)
		
		// Parse tags and metadata
		json.Unmarshal([]byte(tagsJSON), &pipeline.Tags)
		json.Unmarshal([]byte(metadataJSON), &pipeline.Metadata)

		// Load steps for each pipeline
		steps, err := r.loadSteps(ctx, pipeline.ID)
		if err != nil {
			r.logger.Error("Failed to load steps for pipeline",
				logging.F("pipeline_id", pipeline.ID.String()),
				logging.F("error", err.Error()),
			)
			continue
		}
		pipeline.Steps = steps

		pipelines = append(pipelines, &pipeline)
	}

	return pipelines, nil
}

// Delete removes a pipeline from the database
func (r *PipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	// Delete steps first (foreign key constraint)
	_, err := r.db.ExecContext(ctx, "DELETE FROM pipeline_steps WHERE pipeline_id = ?", id.String())
	if err != nil {
		return fmt.Errorf("failed to delete pipeline steps: %w", err)
	}

	// Delete pipeline
	result, err := r.db.ExecContext(ctx, "DELETE FROM pipelines WHERE id = ?", id.String())
	if err != nil {
		return fmt.Errorf("failed to delete pipeline: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrPipelineNotFound
	}

	r.logger.Debug("Pipeline deleted successfully", logging.F("pipeline_id", id.String()))
	return nil
}

// Count returns the total number of pipelines
func (r *PipelineRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM pipelines").Scan(&count)
	return count, err
}

// Helper methods

func (r *PipelineRepository) exists(ctx context.Context, id uuid.UUID) (bool, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM pipelines WHERE id = ?", id.String()).Scan(&count)
	return count > 0, err
}

func (r *PipelineRepository) saveSteps(ctx context.Context, pipeline *Pipeline) error {
	// Delete existing steps
	_, err := r.db.ExecContext(ctx, "DELETE FROM pipeline_steps WHERE pipeline_id = ?", pipeline.ID.String())
	if err != nil {
		return fmt.Errorf("failed to delete existing steps: %w", err)
	}

	// Insert new steps
	for i, step := range pipeline.Steps {
		configJSON, err := json.Marshal(step.Config)
		if err != nil {
			return fmt.Errorf("failed to marshal step config: %w", err)
		}

		dependenciesJSON, err := json.Marshal(step.Dependencies)
		if err != nil {
			return fmt.Errorf("failed to marshal step dependencies: %w", err)
		}

		query := `
			INSERT INTO pipeline_steps (id, pipeline_id, name, type, order_index, config, dependencies)
			VALUES (?, ?, ?, ?, ?, ?, ?)
		`
		
		_, err = r.db.ExecContext(ctx, query,
			step.ID.String(), pipeline.ID.String(), step.Name, step.Type.String(),
			i, string(configJSON), string(dependenciesJSON))
		
		if err != nil {
			return fmt.Errorf("failed to insert step: %w", err)
		}
	}

	return nil
}

func (r *PipelineRepository) loadSteps(ctx context.Context, pipelineID uuid.UUID) ([]*Step, error) {
	query := `
		SELECT id, name, type, config, dependencies
		FROM pipeline_steps 
		WHERE pipeline_id = ? 
		ORDER BY order_index
	`
	
	rows, err := r.db.QueryContext(ctx, query, pipelineID.String())
	if err != nil {
		return nil, fmt.Errorf("failed to query steps: %w", err)
	}
	defer rows.Close()

	var steps []*Step
	
	for rows.Next() {
		var step Step
		var configJSON, dependenciesJSON string
		var typeStr string
		
		err := rows.Scan(&step.ID, &step.Name, &typeStr, &configJSON, &dependenciesJSON)
		if err != nil {
			return nil, fmt.Errorf("failed to scan step: %w", err)
		}

		// Parse type
		if err := step.Type.FromString(typeStr); err != nil {
			return nil, fmt.Errorf("invalid step type: %w", err)
		}

		// Parse config and dependencies
		json.Unmarshal([]byte(configJSON), &step.Config)
		json.Unmarshal([]byte(dependenciesJSON), &step.Dependencies)

		steps = append(steps, &step)
	}

	return steps, nil
}