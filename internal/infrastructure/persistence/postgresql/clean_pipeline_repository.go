package postgresql

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/entities"
	pipelineUC "github.com/flext/flexcore/internal/usecases/pipeline"
	"github.com/google/uuid"
	"github.com/lib/pq"
)

// CleanPipelineRepository implements PipelineRepository using PostgreSQL for Clean Architecture
type CleanPipelineRepository struct {
	db *sql.DB
}

// NewCleanPipelineRepository creates a new PostgreSQL pipeline repository for Clean Architecture
func NewCleanPipelineRepository(db *sql.DB) *CleanPipelineRepository {
	return &CleanPipelineRepository{
		db: db,
	}
}

// Save saves a pipeline to PostgreSQL
func (r *CleanPipelineRepository) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Check if pipeline exists
	var exists bool
	err = tx.QueryRowContext(ctx, "SELECT EXISTS(SELECT 1 FROM clean_pipelines WHERE id = $1)", pipeline.ID).Scan(&exists)
	if err != nil {
		return fmt.Errorf("failed to check pipeline existence: %w", err)
	}

	if exists {
		// Update existing pipeline
		_, err = tx.ExecContext(ctx, `
			UPDATE clean_pipelines
			SET name = $2, description = $3, is_active = $4, tags = $5,
			    configuration = $6, schedule = $7, updated_at = $8
			WHERE id = $1`,
			pipeline.ID, pipeline.Name, pipeline.Description, pipeline.IsActive,
			pq.Array(pipeline.Tags), pipeline.Configuration, pipeline.Schedule, time.Now(),
		)
		if err != nil {
			return fmt.Errorf("failed to update pipeline: %w", err)
		}

		// Delete existing steps
		_, err = tx.ExecContext(ctx, "DELETE FROM clean_pipeline_steps WHERE pipeline_id = $1", pipeline.ID)
		if err != nil {
			return fmt.Errorf("failed to delete existing steps: %w", err)
		}
	} else {
		// Insert new pipeline
		_, err = tx.ExecContext(ctx, `
			INSERT INTO clean_pipelines (id, name, description, is_active, tags, configuration, schedule, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
			pipeline.ID, pipeline.Name, pipeline.Description, pipeline.IsActive,
			pq.Array(pipeline.Tags), pipeline.Configuration, pipeline.Schedule,
			pipeline.CreatedAt, pipeline.UpdatedAt,
		)
		if err != nil {
			return fmt.Errorf("failed to insert pipeline: %w", err)
		}
	}

	// Insert steps
	for _, step := range pipeline.Steps {
		_, err = tx.ExecContext(ctx, `
			INSERT INTO clean_pipeline_steps (id, pipeline_id, name, plugin_id, configuration, order_index, depends_on, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
			step.ID, pipeline.ID, step.Name, step.PluginID,
			step.Configuration, step.Order, pq.Array(step.DependsOn),
			time.Now(), time.Now(),
		)
		if err != nil {
			return fmt.Errorf("failed to insert pipeline step: %w", err)
		}
	}

	return tx.Commit()
}

// FindByID finds a pipeline by ID
func (r *CleanPipelineRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	var pipeline entities.Pipeline
	var tags pq.StringArray
	var schedule sql.NullString

	err := r.db.QueryRowContext(ctx, `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM clean_pipelines WHERE id = $1`, id).Scan(
		&pipeline.ID, &pipeline.Name, &pipeline.Description, &pipeline.IsActive,
		&tags, &pipeline.Configuration, &schedule, &pipeline.CreatedAt, &pipeline.UpdatedAt,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to find pipeline: %w", err)
	}

	pipeline.Tags = []string(tags)
	if schedule.Valid {
		pipeline.Schedule = schedule.String
	}

	// Load steps
	steps, err := r.findStepsByPipelineID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to load pipeline steps: %w", err)
	}
	pipeline.Steps = steps

	// The BaseAggregateRoot is already embedded in Pipeline entity

	return &pipeline, nil
}

// FindByName finds a pipeline by name
func (r *CleanPipelineRepository) FindByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	var pipeline entities.Pipeline
	var tags pq.StringArray
	var schedule sql.NullString

	err := r.db.QueryRowContext(ctx, `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM clean_pipelines WHERE name = $1`, name).Scan(
		&pipeline.ID, &pipeline.Name, &pipeline.Description, &pipeline.IsActive,
		&tags, &pipeline.Configuration, &schedule, &pipeline.CreatedAt, &pipeline.UpdatedAt,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to find pipeline by name: %w", err)
	}

	pipeline.Tags = []string(tags)
	if schedule.Valid {
		pipeline.Schedule = schedule.String
	}

	// Load steps
	steps, err := r.findStepsByPipelineID(ctx, pipeline.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to load pipeline steps: %w", err)
	}
	pipeline.Steps = steps

	// Set aggregate root
	// The BaseAggregateRoot is already embedded in Pipeline entity

	return &pipeline, nil
}

// ExistsByName checks if a pipeline exists by name
func (r *CleanPipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	var exists bool
	err := r.db.QueryRowContext(ctx, "SELECT EXISTS(SELECT 1 FROM clean_pipelines WHERE name = $1)", name).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check pipeline existence: %w", err)
	}
	return exists, nil
}

// List lists pipelines with criteria
func (r *CleanPipelineRepository) List(ctx context.Context, criteria pipelineUC.ListCriteria) ([]*entities.Pipeline, int, error) {
	// Build WHERE clause
	whereClause := "WHERE 1=1"
	args := []interface{}{}
	argIndex := 1

	if criteria.Active != nil {
		whereClause += fmt.Sprintf(" AND is_active = $%d", argIndex)
		args = append(args, *criteria.Active)
		argIndex++
	}

	if len(criteria.Tags) > 0 {
		whereClause += fmt.Sprintf(" AND tags && $%d", argIndex)
		args = append(args, pq.Array(criteria.Tags))
		argIndex++
	}

	// Count total
	var total int
	countQuery := "SELECT COUNT(*) FROM clean_pipelines " + whereClause
	err := r.db.QueryRowContext(ctx, countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count pipelines: %w", err)
	}

	// Build ORDER BY clause
	orderBy := "created_at"
	if criteria.OrderBy != "" {
		orderBy = criteria.OrderBy
	}
	orderDir := "DESC"
	if criteria.OrderDir != "" {
		orderDir = criteria.OrderDir
	}

	// Add LIMIT and OFFSET
	whereClause += fmt.Sprintf(" ORDER BY %s %s LIMIT $%d OFFSET $%d", orderBy, orderDir, argIndex, argIndex+1)
	args = append(args, criteria.Limit, criteria.Offset)

	// Query pipelines
	query := `
		SELECT id, name, description, is_active, tags, configuration, schedule, created_at, updated_at
		FROM clean_pipelines ` + whereClause

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query pipelines: %w", err)
	}
	defer rows.Close()

	var pipelines []*entities.Pipeline
	for rows.Next() {
		var pipeline entities.Pipeline
		var tags pq.StringArray
		var schedule sql.NullString

		err := rows.Scan(
			&pipeline.ID, &pipeline.Name, &pipeline.Description, &pipeline.IsActive,
			&tags, &pipeline.Configuration, &schedule, &pipeline.CreatedAt, &pipeline.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan pipeline: %w", err)
		}

		pipeline.Tags = []string(tags)
		if schedule.Valid {
			pipeline.Schedule = schedule.String
		}

		// Load steps
		steps, err := r.findStepsByPipelineID(ctx, pipeline.ID)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to load pipeline steps: %w", err)
		}
		pipeline.Steps = steps

		// Set aggregate root
		// The BaseAggregateRoot is already embedded in Pipeline entity

		pipelines = append(pipelines, &pipeline)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("failed to iterate pipelines: %w", err)
	}

	return pipelines, total, nil
}

// Delete deletes a pipeline
func (r *CleanPipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Delete steps first (foreign key constraint)
	_, err = tx.ExecContext(ctx, "DELETE FROM clean_pipeline_steps WHERE pipeline_id = $1", id)
	if err != nil {
		return fmt.Errorf("failed to delete pipeline steps: %w", err)
	}

	// Delete pipeline
	result, err := tx.ExecContext(ctx, "DELETE FROM clean_pipelines WHERE id = $1", id)
	if err != nil {
		return fmt.Errorf("failed to delete pipeline: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("pipeline not found")
	}

	return tx.Commit()
}

// findStepsByPipelineID finds all steps for a pipeline
func (r *CleanPipelineRepository) findStepsByPipelineID(ctx context.Context, pipelineID uuid.UUID) ([]entities.PipelineStep, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, name, plugin_id, configuration, order_index, depends_on, created_at, updated_at
		FROM clean_pipeline_steps WHERE pipeline_id = $1 ORDER BY order_index`, pipelineID)
	if err != nil {
		return nil, fmt.Errorf("failed to query pipeline steps: %w", err)
	}
	defer rows.Close()

	var steps []entities.PipelineStep
	for rows.Next() {
		var step entities.PipelineStep
		var dependsOn pq.StringArray
		var createdAt, updatedAt time.Time

		err := rows.Scan(
			&step.ID, &step.Name, &step.PluginID, &step.Configuration,
			&step.Order, &dependsOn, &createdAt, &updatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan pipeline step: %w", err)
		}

		// Convert string array to UUID array
		step.DependsOn = make([]uuid.UUID, len(dependsOn))
		for i, dep := range dependsOn {
			step.DependsOn[i], err = uuid.Parse(dep)
			if err != nil {
				return nil, fmt.Errorf("failed to parse dependency UUID: %w", err)
			}
		}

		steps = append(steps, step)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("failed to iterate pipeline steps: %w", err)
	}

	return steps, nil
}

// Health check for the repository
func (r *CleanPipelineRepository) HealthCheck(ctx context.Context) error {
	err := r.db.PingContext(ctx)
	if err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	// Test a simple query
	var count int
	err = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM clean_pipelines").Scan(&count)
	if err != nil {
		return fmt.Errorf("failed to query pipelines table: %w", err)
	}

	return nil
}

// Count retorna o número total de pipelines
func (r *CleanPipelineRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM clean_pipelines").Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count pipelines: %w", err)
	}
	return count, nil
}

// Create cria um novo pipeline
func (r *CleanPipelineRepository) Create(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Insert new pipeline
	_, err = tx.ExecContext(ctx, `
		INSERT INTO clean_pipelines (id, name, description, is_active, tags, configuration, schedule, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
		pipeline.ID, pipeline.Name, pipeline.Description, pipeline.IsActive,
		pq.Array(pipeline.Tags), pipeline.Configuration, pipeline.Schedule,
		pipeline.CreatedAt, pipeline.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to insert pipeline: %w", err)
	}

	// Insert steps
	for _, step := range pipeline.Steps {
		_, err = tx.ExecContext(ctx, `
			INSERT INTO clean_pipeline_steps (id, pipeline_id, name, plugin_id, configuration, order_index, depends_on, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
			step.ID, pipeline.ID, step.Name, step.PluginID,
			step.Configuration, step.Order, pq.Array(step.DependsOn),
			time.Now(), time.Now(),
		)
		if err != nil {
			return nil, fmt.Errorf("failed to insert pipeline step: %w", err)
		}
	}

	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return pipeline, nil
}

// Update atualiza um pipeline existente
func (r *CleanPipelineRepository) Update(ctx context.Context, pipeline *entities.Pipeline) (*entities.Pipeline, error) {
	err := r.Save(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	return pipeline, nil
}

// GetByID alias para FindByID para compatibilidade
func (r *CleanPipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Pipeline, error) {
	return r.FindByID(ctx, id)
}

// GetByName alias para FindByName para compatibilidade
func (r *CleanPipelineRepository) GetByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	return r.FindByName(ctx, name)
}
