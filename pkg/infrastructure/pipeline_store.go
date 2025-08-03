package postgres

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/persistence"
	"github.com/lib/pq"
	_ "github.com/lib/pq" // PostgreSQL driver
)

// PipelineStore implements persistence.PipelineStore for PostgreSQL
type PipelineStore struct {
	db *sql.DB
}

// NewPipelineStore creates a new PostgreSQL pipeline store
func NewPipelineStore(db *sql.DB) *PipelineStore {
	return &PipelineStore{db: db}
}

// Create inserts a new pipeline
func (s *PipelineStore) Create(ctx context.Context, model *persistence.PipelineModel) error {
	query := `
		INSERT INTO pipelines (
			id, name, description, is_active, configuration, tags,
			version, created_at, updated_at
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9
		)`

	configJSON, err := json.Marshal(model.Configuration)
	if err != nil {
		return fmt.Errorf("failed to marshal configuration: %w", err)
	}

	now := time.Now().Format(time.RFC3339)
	if model.CreatedAt == "" {
		model.CreatedAt = now
	}
	if model.UpdatedAt == "" {
		model.UpdatedAt = now
	}
	if model.Version == 0 {
		model.Version = 1
	}

	_, err = s.db.ExecContext(ctx, query,
		model.ID,
		model.Name,
		model.Description,
		model.IsActive,
		configJSON,
		pq.Array(model.Tags),
		model.Version,
		model.CreatedAt,
		model.UpdatedAt,
	)

	if err != nil {
		if isUniqueViolation(err) {
			return persistence.ErrAlreadyExists
		}
		return fmt.Errorf("failed to create pipeline: %w", err)
	}

	// Create steps if any
	if len(model.Steps) > 0 {
		return s.createSteps(ctx, model.ID, model.Steps)
	}

	return nil
}

// GetByID retrieves a pipeline by ID
func (s *PipelineStore) GetByID(ctx context.Context, id string) (*persistence.PipelineModel, error) {
	query := `
		SELECT
			id, name, description, is_active, configuration, tags,
			version, created_at, updated_at
		FROM pipelines
		WHERE id = $1`

	model := &persistence.PipelineModel{}
	var configJSON []byte
	var description sql.NullString

	err := s.db.QueryRowContext(ctx, query, id).Scan(
		&model.ID,
		&model.Name,
		&description,
		&model.IsActive,
		&configJSON,
		pq.Array(&model.Tags),
		&model.Version,
		&model.CreatedAt,
		&model.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, persistence.ErrNotFound
		}
		return nil, fmt.Errorf("failed to get pipeline: %w", err)
	}

	if description.Valid {
		model.Description = description.String
	}

	if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
		return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
	}

	// Load steps
	steps, err := s.getStepsByPipelineID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to load steps: %w", err)
	}
	model.Steps = steps

	return model, nil
}

// GetByName retrieves a pipeline by name
func (s *PipelineStore) GetByName(ctx context.Context, name string) (*persistence.PipelineModel, error) {
	query := `
		SELECT
			id, name, description, is_active, configuration, tags,
			version, created_at, updated_at
		FROM pipelines
		WHERE name = $1`

	model := &persistence.PipelineModel{}
	var configJSON []byte
	var description sql.NullString

	err := s.db.QueryRowContext(ctx, query, name).Scan(
		&model.ID,
		&model.Name,
		&description,
		&model.IsActive,
		&configJSON,
		pq.Array(&model.Tags),
		&model.Version,
		&model.CreatedAt,
		&model.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, persistence.ErrNotFound
		}
		return nil, fmt.Errorf("failed to get pipeline by name: %w", err)
	}

	if description.Valid {
		model.Description = description.String
	}

	if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
		return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
	}

	// Load steps
	steps, err := s.getStepsByPipelineID(ctx, model.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to load steps: %w", err)
	}
	model.Steps = steps

	return model, nil
}

// Update updates an existing pipeline
func (s *PipelineStore) Update(ctx context.Context, model *persistence.PipelineModel) error {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	query := `
		UPDATE pipelines SET
			name = $2,
			description = $3,
			is_active = $4,
			configuration = $5,
			tags = $6,
			version = version + 1,
			updated_at = $7
		WHERE id = $1 AND version = $8`

	configJSON, err := json.Marshal(model.Configuration)
	if err != nil {
		return fmt.Errorf("failed to marshal configuration: %w", err)
	}

	model.UpdatedAt = time.Now().Format(time.RFC3339)

	result, err := tx.ExecContext(ctx, query,
		model.ID,
		model.Name,
		model.Description,
		model.IsActive,
		configJSON,
		pq.Array(model.Tags),
		model.UpdatedAt,
		model.Version,
	)

	if err != nil {
		return fmt.Errorf("failed to update pipeline: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return persistence.ErrNotFound
	}

	// Delete and recreate steps
	if err := s.deleteStepsTx(ctx, tx, model.ID); err != nil {
		return fmt.Errorf("failed to delete steps: %w", err)
	}

	if len(model.Steps) > 0 {
		if err := s.createStepsTx(ctx, tx, model.ID, model.Steps); err != nil {
			return fmt.Errorf("failed to create steps: %w", err)
		}
	}

	return tx.Commit()
}

// Delete removes a pipeline
func (s *PipelineStore) Delete(ctx context.Context, id string) error {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Delete steps first
	if err := s.deleteStepsTx(ctx, tx, id); err != nil {
		return fmt.Errorf("failed to delete steps: %w", err)
	}

	// Delete pipeline
	query := `DELETE FROM pipelines WHERE id = $1`
	result, err := tx.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete pipeline: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return persistence.ErrNotFound
	}

	return tx.Commit()
}

// List retrieves pipelines with filtering
func (s *PipelineStore) List(ctx context.Context, filter persistence.PipelineFilter) ([]*persistence.PipelineModel, int, error) {
	// Build query
	whereClause := "WHERE 1=1"
	args := []interface{}{}
	argIndex := 1

	if filter.Active != nil {
		whereClause += fmt.Sprintf(" AND is_active = $%d", argIndex)
		args = append(args, *filter.Active)
		argIndex++
	}

	if len(filter.Tags) > 0 {
		whereClause += fmt.Sprintf(" AND tags && $%d", argIndex)
		args = append(args, pq.Array(filter.Tags))
		argIndex++
	}

	// Count total
	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM pipelines %s", whereClause)
	var total int
	if err := s.db.QueryRowContext(ctx, countQuery, args...).Scan(&total); err != nil {
		return nil, 0, fmt.Errorf("failed to count pipelines: %w", err)
	}

	// Build order clause
	orderClause := "ORDER BY created_at DESC"
	if filter.OrderBy != "" {
		orderDir := "ASC"
		if filter.OrderDir == "desc" {
			orderDir = "DESC"
		}
		orderClause = fmt.Sprintf("ORDER BY %s %s", filter.OrderBy, orderDir)
	}

	// Query with pagination
	query := fmt.Sprintf(`
		SELECT
			id, name, description, is_active, configuration, tags,
			version, created_at, updated_at
		FROM pipelines
		%s
		%s
		LIMIT $%d OFFSET $%d
	`, whereClause, orderClause, argIndex, argIndex+1)

	limit := filter.Limit
	if limit <= 0 {
		limit = 50
	}
	offset := filter.Offset
	if offset < 0 {
		offset = 0
	}

	args = append(args, limit, offset)

	rows, err := s.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query pipelines: %w", err)
	}
	defer rows.Close()

	var pipelines []*persistence.PipelineModel
	for rows.Next() {
		model := &persistence.PipelineModel{}
		var configJSON []byte
		var description sql.NullString

		err := rows.Scan(
			&model.ID,
			&model.Name,
			&description,
			&model.IsActive,
			&configJSON,
			pq.Array(&model.Tags),
			&model.Version,
			&model.CreatedAt,
			&model.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan pipeline: %w", err)
		}

		if description.Valid {
			model.Description = description.String
		}

		if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
			return nil, 0, fmt.Errorf("failed to unmarshal configuration: %w", err)
		}

		pipelines = append(pipelines, model)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("rows error: %w", err)
	}

	return pipelines, total, nil
}

// ExistsByName checks if a pipeline exists with the given name
func (s *PipelineStore) ExistsByName(ctx context.Context, name string) (bool, error) {
	query := `SELECT EXISTS(SELECT 1 FROM pipelines WHERE name = $1)`

	var exists bool
	err := s.db.QueryRowContext(ctx, query, name).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check existence: %w", err)
	}

	return exists, nil
}

// BeginTx starts a new transaction
func (s *PipelineStore) BeginTx(ctx context.Context) (persistence.Transaction, error) {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}

	return &postgresTx{tx: tx}, nil
}

// Helper methods

func (s *PipelineStore) getStepsByPipelineID(ctx context.Context, pipelineID string) ([]persistence.StepModel, error) {
	query := `
		SELECT
			id, pipeline_id, name, plugin_id, configuration, depends_on,
			step_order, created_at, updated_at
		FROM pipeline_steps
		WHERE pipeline_id = $1
		ORDER BY step_order`

	rows, err := s.db.QueryContext(ctx, query, pipelineID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var steps []persistence.StepModel
	for rows.Next() {
		var step persistence.StepModel
		var configJSON []byte

		err := rows.Scan(
			&step.ID,
			&step.PipelineID,
			&step.Name,
			&step.PluginID,
			&configJSON,
			pq.Array(&step.DependsOn),
			&step.Order,
			&step.CreatedAt,
			&step.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}

		if err := json.Unmarshal(configJSON, &step.Configuration); err != nil {
			return nil, err
		}

		steps = append(steps, step)
	}

	return steps, rows.Err()
}

func (s *PipelineStore) createSteps(ctx context.Context, pipelineID string, steps []persistence.StepModel) error {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	if err := s.createStepsTx(ctx, tx, pipelineID, steps); err != nil {
		return err
	}

	return tx.Commit()
}

func (s *PipelineStore) createStepsTx(ctx context.Context, tx *sql.Tx, pipelineID string, steps []persistence.StepModel) error {
	query := `
		INSERT INTO pipeline_steps (
			id, pipeline_id, name, plugin_id, configuration, depends_on,
			step_order, created_at, updated_at
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9
		)`

	stmt, err := tx.PrepareContext(ctx, query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	now := time.Now().Format(time.RFC3339)
	for i, step := range steps {
		configJSON, err := json.Marshal(step.Configuration)
		if err != nil {
			return err
		}

		if step.CreatedAt == "" {
			step.CreatedAt = now
		}
		if step.UpdatedAt == "" {
			step.UpdatedAt = now
		}

		_, err = stmt.ExecContext(ctx,
			step.ID,
			pipelineID,
			step.Name,
			step.PluginID,
			configJSON,
			pq.Array(step.DependsOn),
			i, // order
			step.CreatedAt,
			step.UpdatedAt,
		)
		if err != nil {
			return err
		}
	}

	return nil
}

func (s *PipelineStore) deleteStepsTx(ctx context.Context, tx *sql.Tx, pipelineID string) error {
	query := `DELETE FROM pipeline_steps WHERE pipeline_id = $1`
	_, err := tx.ExecContext(ctx, query, pipelineID)
	return err
}

func isUniqueViolation(err error) bool {
	if pqErr, ok := err.(*pq.Error); ok {
		return pqErr.Code == "23505"
	}
	return false
}

// postgresTx implements persistence.Transaction
type postgresTx struct {
	tx *sql.Tx
}

func (t *postgresTx) Commit() error {
	return t.tx.Commit()
}

func (t *postgresTx) Rollback() error {
	return t.tx.Rollback()
}

func (t *postgresTx) CreatePipeline(ctx context.Context, model *persistence.PipelineModel) error {
	// Implementation similar to Create but using transaction
	// TODO: Implement
	return nil
}

func (t *postgresTx) UpdatePipeline(ctx context.Context, model *persistence.PipelineModel) error {
	// Implementation similar to Update but using transaction
	// TODO: Implement
	return nil
}

func (t *postgresTx) CreateStep(ctx context.Context, model *persistence.StepModel) error {
	// TODO: Implement
	return nil
}

func (t *postgresTx) DeleteStepsByPipelineID(ctx context.Context, pipelineID string) error {
	query := `DELETE FROM pipeline_steps WHERE pipeline_id = $1`
	_, err := t.tx.ExecContext(ctx, query, pipelineID)
	return err
}
