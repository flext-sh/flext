package database

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// PluginRepository implements real database operations for plugins
type PluginRepository struct {
	db     *Database
	logger logging.Logger
}

// NewPluginRepository creates a new plugin repository
func NewPluginRepository(db *Database, logger logging.Logger) *PluginRepository {
	return &PluginRepository{
		db:     db,
		logger: logger,
	}
}

// Save persists a plugin to the database
func (r *PluginRepository) Save(ctx context.Context, plugin *Plugin) error {
	// Serialize dependencies
	dependenciesJSON, err := json.Marshal(plugin.Dependencies)
	if err != nil {
		return fmt.Errorf("failed to marshal dependencies: %w", err)
	}

	// Check if plugin exists
	exists, err := r.exists(ctx, plugin.ID)
	if err != nil {
		return fmt.Errorf("failed to check plugin existence: %w", err)
	}

	if exists {
		// Update existing plugin
		query := `
			UPDATE plugins 
			SET name = ?, type = ?, version = ?, description = ?, author = ?, 
			    entry_point = ?, dependencies = ?, config_schema = ?, status = ?,
			    updated_at = CURRENT_TIMESTAMP
			WHERE id = ?
		`
		_, err = r.db.ExecContext(ctx, query,
			plugin.Name, plugin.Type, plugin.Version, plugin.Description,
			plugin.Author, plugin.EntryPoint, string(dependenciesJSON),
			plugin.ConfigSchema, plugin.Status, plugin.ID.String())
	} else {
		// Insert new plugin
		query := `
			INSERT INTO plugins (id, name, type, version, description, author, 
			                   entry_point, dependencies, config_schema, status)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		`
		_, err = r.db.ExecContext(ctx, query,
			plugin.ID.String(), plugin.Name, plugin.Type, plugin.Version,
			plugin.Description, plugin.Author, plugin.EntryPoint,
			string(dependenciesJSON), plugin.ConfigSchema, plugin.Status)
	}

	if err != nil {
		return fmt.Errorf("failed to save plugin: %w", err)
	}

	r.logger.Debug("Plugin saved successfully",
		logging.F("plugin_id", plugin.ID.String()),
		logging.F("name", plugin.Name),
	)

	return nil
}

// FindByID retrieves a plugin by ID
func (r *PluginRepository) FindByID(ctx context.Context, id uuid.UUID) (*Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, entry_point, 
		       dependencies, config_schema, status, created_at, updated_at
		FROM plugins WHERE id = ?
	`

	row := r.db.QueryRowContext(ctx, query, id.String())

	var plugin Plugin
	var dependenciesJSON string

	err := row.Scan(
		&plugin.ID, &plugin.Name, &plugin.Type, &plugin.Version,
		&plugin.Description, &plugin.Author, &plugin.EntryPoint,
		&dependenciesJSON, &plugin.ConfigSchema, &plugin.Status,
		&plugin.CreatedAt, &plugin.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, ErrPluginNotFound
		}
		return nil, fmt.Errorf("failed to scan plugin: %w", err)
	}

	// Parse dependencies
	if err := json.Unmarshal([]byte(dependenciesJSON), &plugin.Dependencies); err != nil {
		return nil, fmt.Errorf("failed to unmarshal dependencies: %w", err)
	}

	return &plugin, nil
}

// FindByName retrieves a plugin by name
func (r *PluginRepository) FindByName(ctx context.Context, name string) (*Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, entry_point, 
		       dependencies, config_schema, status, created_at, updated_at
		FROM plugins WHERE name = ?
	`

	row := r.db.QueryRowContext(ctx, query, name)

	var plugin Plugin
	var dependenciesJSON string

	err := row.Scan(
		&plugin.ID, &plugin.Name, &plugin.Type, &plugin.Version,
		&plugin.Description, &plugin.Author, &plugin.EntryPoint,
		&dependenciesJSON, &plugin.ConfigSchema, &plugin.Status,
		&plugin.CreatedAt, &plugin.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, ErrPluginNotFound
		}
		return nil, fmt.Errorf("failed to scan plugin: %w", err)
	}

	// Parse dependencies
	json.Unmarshal([]byte(dependenciesJSON), &plugin.Dependencies)

	return &plugin, nil
}

// FindAll retrieves all plugins with pagination
func (r *PluginRepository) FindAll(ctx context.Context, limit, offset int) ([]*Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, entry_point, 
		       dependencies, config_schema, status, created_at, updated_at
		FROM plugins 
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*Plugin

	for rows.Next() {
		var plugin Plugin
		var dependenciesJSON string

		err := rows.Scan(
			&plugin.ID, &plugin.Name, &plugin.Type, &plugin.Version,
			&plugin.Description, &plugin.Author, &plugin.EntryPoint,
			&dependenciesJSON, &plugin.ConfigSchema, &plugin.Status,
			&plugin.CreatedAt, &plugin.UpdatedAt,
		)

		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		// Parse dependencies
		json.Unmarshal([]byte(dependenciesJSON), &plugin.Dependencies)

		plugins = append(plugins, &plugin)
	}

	return plugins, nil
}

// FindByType retrieves plugins by type
func (r *PluginRepository) FindByType(ctx context.Context, pluginType string) ([]*Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, entry_point, 
		       dependencies, config_schema, status, created_at, updated_at
		FROM plugins WHERE type = ?
		ORDER BY name
	`

	rows, err := r.db.QueryContext(ctx, query, pluginType)
	if err != nil {
		return nil, fmt.Errorf("failed to query plugins by type: %w", err)
	}
	defer rows.Close()

	var plugins []*Plugin

	for rows.Next() {
		var plugin Plugin
		var dependenciesJSON string

		err := rows.Scan(
			&plugin.ID, &plugin.Name, &plugin.Type, &plugin.Version,
			&plugin.Description, &plugin.Author, &plugin.EntryPoint,
			&dependenciesJSON, &plugin.ConfigSchema, &plugin.Status,
			&plugin.CreatedAt, &plugin.UpdatedAt,
		)

		if err != nil {
			return nil, fmt.Errorf("failed to scan plugin: %w", err)
		}

		// Parse dependencies
		json.Unmarshal([]byte(dependenciesJSON), &plugin.Dependencies)

		plugins = append(plugins, &plugin)
	}

	return plugins, nil
}

// Delete removes a plugin from the database
func (r *PluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM plugins WHERE id = ?", id.String())
	if err != nil {
		return fmt.Errorf("failed to delete plugin: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrPluginNotFound
	}

	r.logger.Debug("Plugin deleted successfully", logging.F("plugin_id", id.String()))
	return nil
}

// Count returns the total number of plugins
func (r *PluginRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM plugins").Scan(&count)
	return count, err
}

// Helper methods

func (r *PluginRepository) exists(ctx context.Context, id uuid.UUID) (bool, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM plugins WHERE id = ?", id.String()).Scan(&count)
	return count > 0, err
}