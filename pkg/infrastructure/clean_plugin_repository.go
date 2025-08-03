package postgresql

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
	pluginUC "github.com/flext-sh/flext/pkg/application/plugin"
	"github.com/google/uuid"
	"github.com/lib/pq"
)

// CleanPluginRepository implements PluginRepository using PostgreSQL for Clean Architecture
type CleanPluginRepository struct {
	db *sql.DB
}

// NewCleanPluginRepository creates a new PostgreSQL plugin repository for Clean Architecture
func NewCleanPluginRepository(db *sql.DB) *CleanPluginRepository {
	return &CleanPluginRepository{
		db: db,
	}
}

// Save saves a plugin to PostgreSQL
func (r *CleanPluginRepository) Save(ctx context.Context, plugin *entities.Plugin) error {
	// Check if plugin exists
	var exists bool
	err := r.db.QueryRowContext(ctx, "SELECT EXISTS(SELECT 1 FROM clean_plugins WHERE id = $1)", plugin.ID).Scan(&exists)
	if err != nil {
		return fmt.Errorf("failed to check plugin existence: %w", err)
	}

	if exists {
		// Update existing plugin
		_, err = r.db.ExecContext(ctx, `
			UPDATE clean_plugins
			SET name = $2, type = $3, version = $4, status = $5, capabilities = $6,
			    configuration = $7, metadata = $8, is_active = $9, updated_at = $10
			WHERE id = $1`,
			plugin.ID, plugin.Name, string(plugin.Type), plugin.Version, string(plugin.Status),
			pq.Array(plugin.Capabilities), plugin.Configuration, plugin.Metadata,
			plugin.IsActive, time.Now(),
		)
		if err != nil {
			return fmt.Errorf("failed to update plugin: %w", err)
		}
	} else {
		// Insert new plugin
		_, err = r.db.ExecContext(ctx, `
			INSERT INTO clean_plugins (id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
			plugin.ID, plugin.Name, string(plugin.Type), plugin.Version, string(plugin.Status),
			pq.Array(plugin.Capabilities), plugin.Configuration, plugin.Metadata,
			plugin.IsActive, plugin.CreatedAt, plugin.UpdatedAt,
		)
		if err != nil {
			return fmt.Errorf("failed to insert plugin: %w", err)
		}
	}

	return nil
}

// FindByID finds a plugin by ID
func (r *CleanPluginRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.Plugin, error) {
	var plugin entities.Plugin
	var capabilities pq.StringArray
	var pluginType, status string

	err := r.db.QueryRowContext(ctx, `
		SELECT id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at
		FROM clean_plugins WHERE id = $1`, id).Scan(
		&plugin.ID, &plugin.Name, &pluginType, &plugin.Version, &status,
		&capabilities, &plugin.Configuration, &plugin.Metadata, &plugin.IsActive,
		&plugin.CreatedAt, &plugin.UpdatedAt,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to find plugin: %w", err)
	}

	// Convert string types back to enums
	plugin.Type = entities.PluginType(pluginType)
	plugin.Status = entities.PluginStatus(status)
	plugin.Capabilities = []string(capabilities)

	// Set aggregate root
	plugin.AggregateRoot = domain.NewAggregateRootWithID(id, plugin.CreatedAt, plugin.UpdatedAt)

	return &plugin, nil
}

// FindByName finds a plugin by name
func (r *CleanPluginRepository) FindByName(ctx context.Context, name string) (*entities.Plugin, error) {
	var plugin entities.Plugin
	var capabilities pq.StringArray
	var pluginType, status string

	err := r.db.QueryRowContext(ctx, `
		SELECT id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at
		FROM clean_plugins WHERE name = $1`, name).Scan(
		&plugin.ID, &plugin.Name, &pluginType, &plugin.Version, &status,
		&capabilities, &plugin.Configuration, &plugin.Metadata, &plugin.IsActive,
		&plugin.CreatedAt, &plugin.UpdatedAt,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("failed to find plugin by name: %w", err)
	}

	// Convert string types back to enums
	plugin.Type = entities.PluginType(pluginType)
	plugin.Status = entities.PluginStatus(status)
	plugin.Capabilities = []string(capabilities)

	// Set aggregate root
	plugin.AggregateRoot = domain.NewAggregateRootWithID(plugin.ID, plugin.CreatedAt, plugin.UpdatedAt)

	return &plugin, nil
}

// ExistsByName checks if a plugin exists by name
func (r *CleanPluginRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	var exists bool
	err := r.db.QueryRowContext(ctx, "SELECT EXISTS(SELECT 1 FROM clean_plugins WHERE name = $1)", name).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check plugin existence: %w", err)
	}
	return exists, nil
}

// List lists plugins with criteria
func (r *CleanPluginRepository) List(ctx context.Context, criteria pluginUC.ListCriteria) ([]*entities.Plugin, int, error) {
	// Build WHERE clause
	whereClause := "WHERE 1=1"
	args := []interface{}{}
	argIndex := 1

	if criteria.Type != nil {
		whereClause += fmt.Sprintf(" AND type = $%d", argIndex)
		args = append(args, string(*criteria.Type))
		argIndex++
	}

	if criteria.Status != nil {
		whereClause += fmt.Sprintf(" AND status = $%d", argIndex)
		args = append(args, string(*criteria.Status))
		argIndex++
	}

	// Count total
	var total int
	countQuery := "SELECT COUNT(*) FROM clean_plugins " + whereClause
	err := r.db.QueryRowContext(ctx, countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count plugins: %w", err)
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

	// Query plugins
	query := `
		SELECT id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at
		FROM clean_plugins ` + whereClause

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*entities.Plugin
	for rows.Next() {
		var plugin entities.Plugin
		var capabilities pq.StringArray
		var pluginType, status string

		err := rows.Scan(
			&plugin.ID, &plugin.Name, &pluginType, &plugin.Version, &status,
			&capabilities, &plugin.Configuration, &plugin.Metadata, &plugin.IsActive,
			&plugin.CreatedAt, &plugin.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan plugin: %w", err)
		}

		// Convert string types back to enums
		plugin.Type = entities.PluginType(pluginType)
		plugin.Status = entities.PluginStatus(status)
		plugin.Capabilities = []string(capabilities)

		// Set aggregate root
		plugin.AggregateRoot = domain.NewAggregateRootWithID(plugin.ID, plugin.CreatedAt, plugin.UpdatedAt)

		plugins = append(plugins, &plugin)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("failed to iterate plugins: %w", err)
	}

	return plugins, total, nil
}

// ListByType lists plugins by type
func (r *CleanPluginRepository) ListByType(ctx context.Context, pluginType entities.PluginType) ([]*entities.Plugin, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at
		FROM clean_plugins WHERE type = $1 ORDER BY name`, string(pluginType))
	if err != nil {
		return nil, fmt.Errorf("failed to query plugins by type: %w", err)
	}
	defer rows.Close()

	var plugins []*entities.Plugin
	for rows.Next() {
		var plugin entities.Plugin
		var capabilities pq.StringArray
		var typeStr, status string

		err := rows.Scan(
			&plugin.ID, &plugin.Name, &typeStr, &plugin.Version, &status,
			&capabilities, &plugin.Configuration, &plugin.Metadata, &plugin.IsActive,
			&plugin.CreatedAt, &plugin.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		// Convert string types back to enums
		plugin.Type = entities.PluginType(typeStr)
		plugin.Status = entities.PluginStatus(status)
		plugin.Capabilities = []string(capabilities)

		// Set aggregate root
		plugin.AggregateRoot = domain.NewAggregateRootWithID(plugin.ID, plugin.CreatedAt, plugin.UpdatedAt)

		plugins = append(plugins, &plugin)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("failed to iterate plugins: %w", err)
	}

	return plugins, nil
}

// ListActive lists all active plugins
func (r *CleanPluginRepository) ListActive(ctx context.Context) ([]*entities.Plugin, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, name, type, version, status, capabilities, configuration, metadata, is_active, created_at, updated_at
		FROM clean_plugins WHERE is_active = true ORDER BY name`)
	if err != nil {
		return nil, fmt.Errorf("failed to query active plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*entities.Plugin
	for rows.Next() {
		var plugin entities.Plugin
		var capabilities pq.StringArray
		var pluginType, status string

		err := rows.Scan(
			&plugin.ID, &plugin.Name, &pluginType, &plugin.Version, &status,
			&capabilities, &plugin.Configuration, &plugin.Metadata, &plugin.IsActive,
			&plugin.CreatedAt, &plugin.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		// Convert string types back to enums
		plugin.Type = entities.PluginType(pluginType)
		plugin.Status = entities.PluginStatus(status)
		plugin.Capabilities = []string(capabilities)

		// Set aggregate root
		plugin.AggregateRoot = domain.NewAggregateRootWithID(plugin.ID, plugin.CreatedAt, plugin.UpdatedAt)

		plugins = append(plugins, &plugin)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("failed to iterate plugins: %w", err)
	}

	return plugins, nil
}

// Delete deletes a plugin
func (r *CleanPluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM clean_plugins WHERE id = $1", id)
	if err != nil {
		return fmt.Errorf("failed to delete plugin: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("plugin not found")
	}

	return nil
}

// Health check for the repository
func (r *CleanPluginRepository) HealthCheck(ctx context.Context) error {
	err := r.db.PingContext(ctx)
	if err != nil {
		return fmt.Errorf("database ping failed: %w", err)
	}

	// Test a simple query
	var count int
	err = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM clean_plugins").Scan(&count)
	if err != nil {
		return fmt.Errorf("failed to query plugins table: %w", err)
	}

	return nil
}
