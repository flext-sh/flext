package persistence

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"

	pipelinePorts "github.com/flext-sh/flext/pkg/domain/pipeline/application/ports"
	pipelineEntities "github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	pluginPorts "github.com/flext-sh/flext/pkg/domain/plugin/application/ports"
	pluginEntities "github.com/flext-sh/flext/pkg/domain/plugin/domain/entities"
	"github.com/flext-sh/flext/pkg/infrastructure/database"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// SimplePipelineRepository implementa PipelineRepository usando PostgreSQL de forma simplificada
type SimplePipelineRepository struct {
	db     *database.Connection
	logger logging.Logger
}

// NewPostgreSQLPipelineRepository cria um novo repository PostgreSQL para pipelines
func NewPostgreSQLPipelineRepository(db *database.Connection, logger logging.Logger) pipelinePorts.PipelineRepository {
	return &SimplePipelineRepository{
		db:     db,
		logger: logger,
	}
}

// Save salva um pipeline no banco de dados
func (r *SimplePipelineRepository) Save(ctx context.Context, pipeline *pipelineEntities.Pipeline) error {
	// Verificação defensiva para evitar nil pointer
	if r == nil {
		return fmt.Errorf("repository is nil")
	}
	if r.db == nil {
		return fmt.Errorf("database connection is nil")
	}

	db := r.db.GetDB()
	if db == nil {
		return fmt.Errorf("database instance is nil")
	}

	configJSON, _ := json.Marshal(pipeline.Configuration)

	query := `
		INSERT INTO pipelines (id, name, description, is_active, configuration, tags, version, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		ON CONFLICT (id) DO UPDATE SET
			name = EXCLUDED.name,
			description = EXCLUDED.description,
			is_active = EXCLUDED.is_active,
			configuration = EXCLUDED.configuration,
			tags = EXCLUDED.tags,
			version = EXCLUDED.version,
			updated_at = EXCLUDED.updated_at
	`

	_, err := db.ExecContext(ctx, query,
		pipeline.ID.String(),
		pipeline.Name,
		pipeline.Description,
		pipeline.IsActive,
		configJSON,
		pq.Array(pipeline.Tags), // Use pq.Array for PostgreSQL text arrays
		pipeline.Version,
		pipeline.CreatedAt,
		pipeline.UpdatedAt,
	)

	if err != nil {
		r.logger.Error("Failed to save pipeline", logging.F("error", err), logging.F("pipeline_id", pipeline.ID))
		return fmt.Errorf("failed to save pipeline: %w", err)
	}

	r.logger.Info("Pipeline saved successfully", logging.F("pipeline_id", pipeline.ID), logging.F("name", pipeline.Name))
	return nil
}

// GetByID encontra um pipeline pelo ID
func (r *SimplePipelineRepository) GetByID(ctx context.Context, id uuid.UUID) (*pipelineEntities.Pipeline, error) {
	query := `
		SELECT id, name, description, is_active, configuration, tags, version, created_at, updated_at
		FROM pipelines
		WHERE id = $1
	`

	var configJSON []byte
	var idStr string
	var version int // PostgreSQL INTEGER scans into int, not int64
	var createdAt, updatedAt time.Time
	var pipelineName, pipelineDescription string
	var isActive bool
	var tags pq.StringArray

	err := r.db.GetDB().QueryRowContext(ctx, query, id.String()).Scan(
		&idStr,
		&pipelineName,
		&pipelineDescription,
		&isActive,
		&configJSON,
		&tags,
		&version,
		&createdAt,
		&updatedAt,
	)

	if err != nil {
		if err.Error() == "sql: no rows in result set" {
			return nil, fmt.Errorf("pipeline not found")
		}
		return nil, fmt.Errorf("failed to get pipeline: %w", err)
	}

	// Parse UUID from string
	pipelineID, err := uuid.Parse(idStr)
	if err != nil {
		return nil, fmt.Errorf("failed to parse pipeline ID: %w", err)
	}

	// Create new pipeline with proper initialization
	pipeline, err := pipelineEntities.NewPipeline(pipelineName, pipelineDescription)
	if err != nil {
		return nil, fmt.Errorf("failed to create pipeline: %w", err)
	}

	// Set database fields
	pipeline.SetID(pipelineID)
	pipeline.IsActive = isActive
	pipeline.CreatedAt = createdAt
	pipeline.UpdatedAt = updatedAt
	pipeline.Version = int64(version)

	// Parse JSON fields
	if len(configJSON) > 0 {
		if err := json.Unmarshal(configJSON, &pipeline.Configuration); err != nil {
			// Log error but don't fail - use empty configuration
			pipeline.Configuration = make(map[string]interface{})
		}
	}

	// Set tags from array
	pipeline.Tags = []string(tags)

	return pipeline, nil
}

// Create cria um novo pipeline
func (r *SimplePipelineRepository) Create(ctx context.Context, pipeline *pipelineEntities.Pipeline) (*pipelineEntities.Pipeline, error) {
	err := r.Save(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	return pipeline, nil
}

// Update atualiza um pipeline existente
func (r *SimplePipelineRepository) Update(ctx context.Context, pipeline *pipelineEntities.Pipeline) (*pipelineEntities.Pipeline, error) {
	err := r.Save(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	return pipeline, nil
}

// GetByName encontra um pipeline pelo nome
func (r *SimplePipelineRepository) GetByName(ctx context.Context, name string) (*pipelineEntities.Pipeline, error) {
	// Verificação defensiva para evitar nil pointer
	if r == nil {
		return nil, fmt.Errorf("repository is nil")
	}
	if r.db == nil {
		return nil, fmt.Errorf("database connection is nil")
	}

	db := r.db.GetDB()
	if db == nil {
		return nil, fmt.Errorf("database instance is nil")
	}

	query := `
		SELECT id, name, description, is_active, configuration, tags, version, created_at, updated_at
		FROM pipelines
		WHERE name = $1
	`

	var configJSON []byte
	var idStr string
	var version int // PostgreSQL INTEGER scans into int, not int64
	var createdAt, updatedAt time.Time
	var pipelineName, pipelineDescription string
	var isActive bool
	var tags pq.StringArray

	err := db.QueryRowContext(ctx, query, name).Scan(
		&idStr,
		&pipelineName,
		&pipelineDescription,
		&isActive,
		&configJSON,
		&tags,
		&version,
		&createdAt,
		&updatedAt,
	)

	if err != nil {
		if err.Error() == "sql: no rows in result set" {
			return nil, nil // Não encontrado
		}
		return nil, fmt.Errorf("failed to scan pipeline: %w", err)
	}

	// Parse ID
	id, err := uuid.Parse(idStr)
	if err != nil {
		return nil, fmt.Errorf("failed to parse pipeline ID: %w", err)
	}

	// Create new pipeline with proper initialization
	pipeline, err := pipelineEntities.NewPipeline(pipelineName, pipelineDescription)
	if err != nil {
		return nil, fmt.Errorf("failed to create pipeline: %w", err)
	}

	// Set database fields
	pipeline.SetID(id)
	pipeline.IsActive = isActive
	pipeline.CreatedAt = createdAt
	pipeline.UpdatedAt = updatedAt
	pipeline.Version = int64(version)

	// Parse JSON fields
	if len(configJSON) > 0 {
		if err := json.Unmarshal(configJSON, &pipeline.Configuration); err != nil {
			// Log error but don't fail - use empty configuration
			pipeline.Configuration = make(map[string]interface{})
		}
	}

	// Set tags from array
	pipeline.Tags = []string(tags)

	return pipeline, nil
}

// FindByID encontra um pipeline pelo ID como string
func (r *SimplePipelineRepository) FindByID(ctx context.Context, id string) (*pipelineEntities.Pipeline, error) {
	pipelineID, err := uuid.Parse(id)
	if err != nil {
		return nil, fmt.Errorf("invalid UUID format: %w", err)
	}
	return r.GetByID(ctx, pipelineID)
}

// FindByName é um alias para GetByName
func (r *SimplePipelineRepository) FindByName(ctx context.Context, name string) (*pipelineEntities.Pipeline, error) {
	return r.GetByName(ctx, name)
}

// ExistsByName verifica se existe um pipeline com o nome
func (r *SimplePipelineRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	query := `SELECT EXISTS(SELECT 1 FROM pipelines WHERE name = $1)`

	var exists bool
	err := r.db.GetDB().QueryRowContext(ctx, query, name).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check pipeline existence: %w", err)
	}

	return exists, nil
}

// List lista pipelines com filtros
func (r *SimplePipelineRepository) List(ctx context.Context, filter pipelinePorts.ListPipelinesFilter) ([]*pipelineEntities.Pipeline, int, error) {
	query := `
		SELECT id, name, description, is_active, configuration, tags, version, created_at, updated_at
		FROM pipelines
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, filter.Limit, filter.Offset)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to list pipelines: %w", err)
	}
	defer rows.Close()

	var pipelines []*pipelineEntities.Pipeline
	for rows.Next() {
		var configJSON []byte
		var idStr string
		var version int // PostgreSQL INTEGER scans into int, not int64
		var createdAt, updatedAt time.Time
		var pipelineName, pipelineDescription string
		var isActive bool
		var tags pq.StringArray

		err := rows.Scan(
			&idStr,
			&pipelineName,
			&pipelineDescription,
			&isActive,
			&configJSON,
			&tags,
			&version,
			&createdAt,
			&updatedAt,
		)
		if err != nil {
			r.logger.Error("Failed to scan pipeline row", logging.F("error", err))
			continue
		}

		// Parse UUID from string
		pipelineID, err := uuid.Parse(idStr)
		if err != nil {
			r.logger.Error("Failed to parse pipeline ID", logging.F("error", err), logging.F("id_str", idStr))
			continue
		}

		// Create new pipeline with proper initialization
		pipeline, err := pipelineEntities.NewPipeline(pipelineName, pipelineDescription)
		if err != nil {
			r.logger.Error("Failed to create pipeline", logging.F("error", err))
			continue
		}

		// Set database fields
		pipeline.SetID(pipelineID)
		pipeline.IsActive = isActive
		pipeline.CreatedAt = createdAt
		pipeline.UpdatedAt = updatedAt
		pipeline.Version = int64(version)

		// Parse JSON fields
		if len(configJSON) > 0 {
			if err := json.Unmarshal(configJSON, &pipeline.Configuration); err != nil {
				// Log error but don't fail - use empty configuration
				pipeline.Configuration = make(map[string]interface{})
			}
		}

		// Convert pq.StringArray to []string
		pipeline.Tags = make([]string, len(tags))
		copy(pipeline.Tags, tags)

		pipelines = append(pipelines, pipeline)
	}

	// Get total count
	total, err := r.Count(ctx)
	if err != nil {
		return pipelines, 0, fmt.Errorf("failed to get total count: %w", err)
	}

	return pipelines, total, nil
}

// Count conta o total de pipelines
func (r *SimplePipelineRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM pipelines`

	var count int
	err := r.db.GetDB().QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count pipelines: %w", err)
	}

	return count, nil
}

// Delete remove um pipeline
func (r *SimplePipelineRepository) Delete(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM pipelines WHERE id = $1`

	_, err := r.db.GetDB().ExecContext(ctx, query, id.String())
	if err != nil {
		return fmt.Errorf("failed to delete pipeline: %w", err)
	}

	return nil
}

// SimplePluginRepository implementa PluginRepository usando PostgreSQL de forma simplificada
type SimplePluginRepository struct {
	db     *database.Connection
	logger logging.Logger
}

// NewPostgreSQLPluginRepository cria um novo repository PostgreSQL para plugins
func NewPostgreSQLPluginRepository(db *database.Connection, logger logging.Logger) pluginPorts.PluginRepository {
	return &SimplePluginRepository{
		db:     db,
		logger: logger,
	}
}

// Save salva um plugin no banco de dados
func (r *SimplePluginRepository) Save(ctx context.Context, plugin *pluginEntities.Plugin) error {
	configJSON, _ := json.Marshal(plugin.Configuration)
	metadataJSON, _ := json.Marshal(plugin.Metadata)

	query := `
		INSERT INTO plugins (id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		ON CONFLICT (id) DO UPDATE SET
			name = EXCLUDED.name,
			type = EXCLUDED.type,
			version = EXCLUDED.version,
			description = EXCLUDED.description,
			author = EXCLUDED.author,
			status = EXCLUDED.status,
			entry_point = EXCLUDED.entry_point,
			dependencies = EXCLUDED.dependencies,
			configuration = EXCLUDED.configuration,
			metadata = EXCLUDED.metadata,
			updated_at = EXCLUDED.updated_at
	`

	_, err := r.db.GetDB().ExecContext(ctx, query,
		plugin.ID.String(),
		plugin.Name,
		string(plugin.Type),
		plugin.Version,
		plugin.Description,
		plugin.Author,
		string(plugin.Status),
		plugin.EntryPoint,
		pq.Array(plugin.Dependencies),
		configJSON,
		metadataJSON,
		plugin.CreatedAt,
		plugin.UpdatedAt,
	)

	if err != nil {
		r.logger.Error("Failed to save plugin", logging.F("error", err), logging.F("plugin_id", plugin.ID))
		return fmt.Errorf("failed to save plugin: %w", err)
	}

	r.logger.Info("Plugin saved successfully", logging.F("plugin_id", plugin.ID), logging.F("name", plugin.Name))
	return nil
}

// GetByID encontra um plugin pelo ID
func (r *SimplePluginRepository) GetByID(ctx context.Context, id uuid.UUID) (*pluginEntities.Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at
		FROM plugins
		WHERE id = $1
	`

	var plugin pluginEntities.Plugin
	var configJSON, metadataJSON []byte
	var pluginType, status, idStr string

	err := r.db.GetDB().QueryRowContext(ctx, query, id.String()).Scan(
		&idStr,
		&plugin.Name,
		&pluginType,
		&plugin.Version,
		&plugin.Description,
		&plugin.Author,
		&status,
		&plugin.EntryPoint,
		pq.Array(&plugin.Dependencies),
		&configJSON,
		&metadataJSON,
		&plugin.CreatedAt,
		&plugin.UpdatedAt,
	)

	if err != nil {
		if err.Error() == "sql: no rows in result set" {
			return nil, fmt.Errorf("plugin not found")
		}
		return nil, fmt.Errorf("failed to get plugin: %w", err)
	}

	// Parse UUID from string
	pluginID, err := uuid.Parse(idStr)
	if err != nil {
		return nil, fmt.Errorf("failed to parse plugin ID: %w", err)
	}
	plugin.ID = pluginID

	plugin.Type = pluginEntities.PluginType(pluginType)
	plugin.Status = pluginEntities.PluginStatus(status)
	json.Unmarshal(configJSON, &plugin.Configuration)
	json.Unmarshal(metadataJSON, &plugin.Metadata)

	return &plugin, nil
}

// ExistsByName verifica se existe um plugin com o nome
func (r *SimplePluginRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	query := `SELECT EXISTS(SELECT 1 FROM plugins WHERE name = $1)`

	var exists bool
	err := r.db.GetDB().QueryRowContext(ctx, query, name).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check plugin existence: %w", err)
	}

	return exists, nil
}

// GetActivePlugins busca todos os plugins ativos
func (r *SimplePluginRepository) GetActivePlugins(ctx context.Context) ([]*pluginEntities.Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at
		FROM plugins
		WHERE status = 'active' OR is_active = true
		ORDER BY created_at DESC
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to list active plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*pluginEntities.Plugin
	for rows.Next() {
		var plugin pluginEntities.Plugin
		var configJSON, metadataJSON []byte
		var pluginType, status string

		var idStr string
		err := rows.Scan(
			&idStr,
			&plugin.Name,
			&pluginType,
			&plugin.Version,
			&plugin.Description,
			&plugin.Author,
			&status,
			&plugin.EntryPoint,
			pq.Array(&plugin.Dependencies),
			&configJSON,
			&metadataJSON,
			&plugin.CreatedAt,
			&plugin.UpdatedAt,
		)
		if err != nil {
			continue
		}

		// Parse UUID from string
		pluginID, err := uuid.Parse(idStr)
		if err != nil {
			continue
		}
		plugin.ID = pluginID

		plugin.Type = pluginEntities.PluginType(pluginType)
		plugin.Status = pluginEntities.PluginStatus(status)
		json.Unmarshal(configJSON, &plugin.Configuration)
		json.Unmarshal(metadataJSON, &plugin.Metadata)

		plugins = append(plugins, &plugin)
	}

	return plugins, nil
}

// GetByType busca plugins por tipo
func (r *SimplePluginRepository) GetByType(ctx context.Context, pluginType pluginEntities.PluginType) ([]*pluginEntities.Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at
		FROM plugins
		WHERE type = $1
		ORDER BY created_at DESC
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, string(pluginType))
	if err != nil {
		return nil, fmt.Errorf("failed to list plugins by type: %w", err)
	}
	defer rows.Close()

	var plugins []*pluginEntities.Plugin
	for rows.Next() {
		var plugin pluginEntities.Plugin
		var configJSON, metadataJSON []byte
		var pType, status string

		err := rows.Scan(
			&plugin.ID,
			&plugin.Name,
			&pType,
			&plugin.Version,
			&plugin.Description,
			&plugin.Author,
			&status,
			&plugin.EntryPoint,
			pq.Array(&plugin.Dependencies),
			&configJSON,
			&metadataJSON,
			&plugin.CreatedAt,
			&plugin.UpdatedAt,
		)
		if err != nil {
			continue
		}

		plugin.Type = pluginEntities.PluginType(pType)
		plugin.Status = pluginEntities.PluginStatus(status)
		json.Unmarshal(configJSON, &plugin.Configuration)
		json.Unmarshal(metadataJSON, &plugin.Metadata)

		plugins = append(plugins, &plugin)
	}

	return plugins, nil
}

// List lista plugins com filtros
func (r *SimplePluginRepository) List(ctx context.Context, filter pluginPorts.ListPluginsFilter) ([]*pluginEntities.Plugin, int, error) {
	query := `
		SELECT id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at
		FROM plugins
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.GetDB().QueryContext(ctx, query, filter.Limit, filter.Offset)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to list plugins: %w", err)
	}
	defer rows.Close()

	var plugins []*pluginEntities.Plugin
	for rows.Next() {
		var plugin pluginEntities.Plugin
		var configJSON, metadataJSON []byte
		var pluginType, status string

		var idStr string
		err := rows.Scan(
			&idStr,
			&plugin.Name,
			&pluginType,
			&plugin.Version,
			&plugin.Description,
			&plugin.Author,
			&status,
			&plugin.EntryPoint,
			pq.Array(&plugin.Dependencies),
			&configJSON,
			&metadataJSON,
			&plugin.CreatedAt,
			&plugin.UpdatedAt,
		)
		if err != nil {
			continue
		}

		// Parse UUID from string
		pluginID, err := uuid.Parse(idStr)
		if err != nil {
			continue
		}
		plugin.ID = pluginID

		plugin.Type = pluginEntities.PluginType(pluginType)
		plugin.Status = pluginEntities.PluginStatus(status)
		json.Unmarshal(configJSON, &plugin.Configuration)
		json.Unmarshal(metadataJSON, &plugin.Metadata)

		plugins = append(plugins, &plugin)
	}

	// Get total count
	total, err := r.Count(ctx)
	if err != nil {
		return plugins, 0, fmt.Errorf("failed to get total count: %w", err)
	}

	return plugins, total, nil
}

// Count conta o total de plugins
func (r *SimplePluginRepository) Count(ctx context.Context) (int, error) {
	query := `SELECT COUNT(*) FROM plugins`

	var count int
	err := r.db.GetDB().QueryRowContext(ctx, query).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count plugins: %w", err)
	}

	return count, nil
}

// Delete remove um plugin
func (r *SimplePluginRepository) Delete(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM plugins WHERE id = $1`

	_, err := r.db.GetDB().ExecContext(ctx, query, id.String())
	if err != nil {
		return fmt.Errorf("failed to delete plugin: %w", err)
	}

	return nil
}

// GetByName encontra um plugin pelo nome
func (r *SimplePluginRepository) GetByName(ctx context.Context, name string) (*pluginEntities.Plugin, error) {
	query := `
		SELECT id, name, type, version, description, author, status, entry_point, dependencies, configuration, metadata, created_at, updated_at
		FROM plugins
		WHERE name = $1
	`

	var plugin pluginEntities.Plugin
	var configJSON, metadataJSON []byte
	var pluginType, status, idStr string

	err := r.db.GetDB().QueryRowContext(ctx, query, name).Scan(
		&idStr,
		&plugin.Name,
		&pluginType,
		&plugin.Version,
		&plugin.Description,
		&plugin.Author,
		&status,
		&plugin.EntryPoint,
		pq.Array(&plugin.Dependencies),
		&configJSON,
		&metadataJSON,
		&plugin.CreatedAt,
		&plugin.UpdatedAt,
	)

	if err != nil {
		if err.Error() == "sql: no rows in result set" {
			return nil, fmt.Errorf("plugin not found")
		}
		return nil, fmt.Errorf("failed to get plugin by name: %w", err)
	}

	// Parse UUID from string
	pluginID, err := uuid.Parse(idStr)
	if err != nil {
		return nil, fmt.Errorf("failed to parse plugin ID: %w", err)
	}
	plugin.ID = pluginID

	plugin.Type = pluginEntities.PluginType(pluginType)
	plugin.Status = pluginEntities.PluginStatus(status)
	json.Unmarshal(configJSON, &plugin.Configuration)
	json.Unmarshal(metadataJSON, &plugin.Metadata)

	return &plugin, nil
}

// UpdateStatus atualiza o status de um plugin
func (r *SimplePluginRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status pluginEntities.PluginStatus) error {
	query := `UPDATE plugins SET status = $1, updated_at = $2 WHERE id = $3`

	_, err := r.db.GetDB().ExecContext(ctx, query, string(status), time.Now(), id.String())
	if err != nil {
		return fmt.Errorf("failed to update plugin status: %w", err)
	}

	return nil
}
