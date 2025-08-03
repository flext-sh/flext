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

// PluginStore implements persistence.PluginStore for PostgreSQL
type PluginStore struct {
	db *sql.DB
}

// NewPluginStore creates a new PostgreSQL plugin store
func NewPluginStore(db *sql.DB) *PluginStore {
	return &PluginStore{db: db}
}

// Create inserts a new plugin
func (s *PluginStore) Create(ctx context.Context, model *persistence.PluginModel) error {
	query := `
		INSERT INTO plugins (
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
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

	_, err = s.db.ExecContext(ctx, query,
		model.ID,
		model.Name,
		model.Type,
		model.Version,
		model.Status,
		configJSON,
		pq.Array(model.Capabilities),
		model.CreatedAt,
		model.UpdatedAt,
	)

	if err != nil {
		if isUniqueViolation(err) {
			return persistence.ErrAlreadyExists
		}
		return fmt.Errorf("failed to create plugin: %w", err)
	}

	return nil
}

// GetByID retrieves a plugin by ID
func (s *PluginStore) GetByID(ctx context.Context, id string) (*persistence.PluginModel, error) {
	query := `
		SELECT
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
		FROM plugins
		WHERE id = $1`

	model := &persistence.PluginModel{}
	var configJSON []byte

	err := s.db.QueryRowContext(ctx, query, id).Scan(
		&model.ID,
		&model.Name,
		&model.Type,
		&model.Version,
		&model.Status,
		&configJSON,
		pq.Array(&model.Capabilities),
		&model.CreatedAt,
		&model.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, persistence.ErrNotFound
		}
		return nil, fmt.Errorf("failed to get plugin: %w", err)
	}

	if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
		return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
	}

	return model, nil
}

// GetByName retrieves a plugin by name
func (s *PluginStore) GetByName(ctx context.Context, name string) (*persistence.PluginModel, error) {
	query := `
		SELECT
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
		FROM plugins
		WHERE name = $1`

	model := &persistence.PluginModel{}
	var configJSON []byte

	err := s.db.QueryRowContext(ctx, query, name).Scan(
		&model.ID,
		&model.Name,
		&model.Type,
		&model.Version,
		&model.Status,
		&configJSON,
		pq.Array(&model.Capabilities),
		&model.CreatedAt,
		&model.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, persistence.ErrNotFound
		}
		return nil, fmt.Errorf("failed to get plugin by name: %w", err)
	}

	if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
		return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
	}

	return model, nil
}

// Update updates an existing plugin
func (s *PluginStore) Update(ctx context.Context, model *persistence.PluginModel) error {
	query := `
		UPDATE plugins SET
			name = $2,
			type = $3,
			version = $4,
			status = $5,
			configuration = $6,
			capabilities = $7,
			updated_at = $8
		WHERE id = $1`

	configJSON, err := json.Marshal(model.Configuration)
	if err != nil {
		return fmt.Errorf("failed to marshal configuration: %w", err)
	}

	model.UpdatedAt = time.Now().Format(time.RFC3339)

	result, err := s.db.ExecContext(ctx, query,
		model.ID,
		model.Name,
		model.Type,
		model.Version,
		model.Status,
		configJSON,
		pq.Array(model.Capabilities),
		model.UpdatedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to update plugin: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return persistence.ErrNotFound
	}

	return nil
}

// Delete removes a plugin
func (s *PluginStore) Delete(ctx context.Context, id string) error {
	query := `DELETE FROM plugins WHERE id = $1`

	result, err := s.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete plugin: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return persistence.ErrNotFound
	}

	return nil
}

// List retrieves plugins with pagination
func (s *PluginStore) List(ctx context.Context, limit, offset int) ([]*persistence.PluginModel, int, error) {
	// Count total
	countQuery := "SELECT COUNT(*) FROM plugins"
	var total int
	if err := s.db.QueryRowContext(ctx, countQuery).Scan(&total); err != nil {
		return nil, 0, fmt.Errorf("failed to count plugins: %w", err)
	}

	// Query with pagination
	query := `
		SELECT
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
		FROM plugins
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2`

	if limit <= 0 {
		limit = 50
	}
	if offset < 0 {
		offset = 0
	}

	rows, err := s.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*persistence.PluginModel
	for rows.Next() {
		model := &persistence.PluginModel{}
		var configJSON []byte

		err := rows.Scan(
			&model.ID,
			&model.Name,
			&model.Type,
			&model.Version,
			&model.Status,
			&configJSON,
			pq.Array(&model.Capabilities),
			&model.CreatedAt,
			&model.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan plugin: %w", err)
		}

		if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
			return nil, 0, fmt.Errorf("failed to unmarshal configuration: %w", err)
		}

		plugins = append(plugins, model)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("rows error: %w", err)
	}

	return plugins, total, nil
}

// ListByType retrieves plugins by type
func (s *PluginStore) ListByType(ctx context.Context, pluginType string) ([]*persistence.PluginModel, error) {
	query := `
		SELECT
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
		FROM plugins
		WHERE type = $1
		ORDER BY created_at DESC`

	rows, err := s.db.QueryContext(ctx, query, pluginType)
	if err != nil {
		return nil, fmt.Errorf("failed to query plugins by type: %w", err)
	}
	defer rows.Close()

	var plugins []*persistence.PluginModel
	for rows.Next() {
		model := &persistence.PluginModel{}
		var configJSON []byte

		err := rows.Scan(
			&model.ID,
			&model.Name,
			&model.Type,
			&model.Version,
			&model.Status,
			&configJSON,
			pq.Array(&model.Capabilities),
			&model.CreatedAt,
			&model.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
			return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
		}

		plugins = append(plugins, model)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return plugins, nil
}

// ListActive retrieves active plugins
func (s *PluginStore) ListActive(ctx context.Context) ([]*persistence.PluginModel, error) {
	query := `
		SELECT
			id, name, type, version, status, configuration, capabilities,
			created_at, updated_at
		FROM plugins
		WHERE status = 'active'
		ORDER BY created_at DESC`

	rows, err := s.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to query active plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*persistence.PluginModel
	for rows.Next() {
		model := &persistence.PluginModel{}
		var configJSON []byte

		err := rows.Scan(
			&model.ID,
			&model.Name,
			&model.Type,
			&model.Version,
			&model.Status,
			&configJSON,
			pq.Array(&model.Capabilities),
			&model.CreatedAt,
			&model.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		if err := json.Unmarshal(configJSON, &model.Configuration); err != nil {
			return nil, fmt.Errorf("failed to unmarshal configuration: %w", err)
		}

		plugins = append(plugins, model)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("rows error: %w", err)
	}

	return plugins, nil
}
