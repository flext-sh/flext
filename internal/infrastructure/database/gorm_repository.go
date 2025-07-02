package database

import (
	"context"
	"encoding/json"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
	"github.com/pkg/errors"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// GormPipelineRepository implements advanced pipeline operations using GORM
type GormPipelineRepository struct {
	db     *gorm.DB
	logger logging.Logger
}

// NewGormPipelineRepository creates a new GORM-based pipeline repository
func NewGormPipelineRepository(db *gorm.DB, logger logging.Logger) *GormPipelineRepository {
	return &GormPipelineRepository{
		db:     db,
		logger: logger,
	}
}

// Save pipeline with advanced GORM features
func (r *GormPipelineRepository) Save(ctx context.Context, pipeline *Pipeline) error {
	gormPipeline := r.domainToGorm(pipeline)
	
	// Use GORM's upsert functionality
	result := r.db.WithContext(ctx).Clauses(clause.OnConflict{
		Columns:   []clause.Column{{Name: "id"}},
		DoUpdates: clause.AssignmentColumns([]string{"name", "description", "status", "tags", "metadata", "updated_at", "version"}),
	}).Create(&gormPipeline)
	
	if result.Error != nil {
		return errors.Wrap(result.Error, "failed to save pipeline with GORM")
	}
	
	r.logger.Debug("Pipeline saved with GORM",
		logging.F("pipeline_id", pipeline.ID.String()),
		logging.F("rows_affected", result.RowsAffected),
	)
	
	return nil
}

// FindByID with preloading
func (r *GormPipelineRepository) FindByID(ctx context.Context, id uuid.UUID) (*Pipeline, error) {
	var gormPipeline GormPipeline
	
	result := r.db.WithContext(ctx).
		Preload("Steps", func(db *gorm.DB) *gorm.DB {
			return db.Order("order_index")
		}).
		Preload("Executions", func(db *gorm.DB) *gorm.DB {
			return db.Order("created_at DESC").Limit(10)
		}).
		First(&gormPipeline, "id = ?", id)
	
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, ErrPipelineNotFound
		}
		return nil, errors.Wrap(result.Error, "failed to find pipeline by ID")
	}
	
	return r.gormToDomain(&gormPipeline), nil
}

// FindByNameWithSteps advanced query with custom preloading
func (r *GormPipelineRepository) FindByNameWithSteps(ctx context.Context, name string) (*Pipeline, error) {
	var gormPipeline GormPipeline
	
	result := r.db.WithContext(ctx).
		Preload("Steps", func(db *gorm.DB) *gorm.DB {
			return db.Order("order_index").Where("deleted_at IS NULL")
		}).
		Where("name = ? AND deleted_at IS NULL", name).
		First(&gormPipeline)
	
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, ErrPipelineNotFound
		}
		return nil, errors.Wrap(result.Error, "failed to find pipeline by name")
	}
	
	return r.gormToDomain(&gormPipeline), nil
}

// FindAllWithFilters advanced filtering and pagination
func (r *GormPipelineRepository) FindAllWithFilters(ctx context.Context, filters PipelineFilters) ([]*Pipeline, int64, error) {
	query := r.db.WithContext(ctx).Model(&GormPipeline{})
	
	// Apply filters
	if filters.Status != "" {
		query = query.Where("status = ?", filters.Status)
	}
	
	if len(filters.Tags) > 0 {
		query = query.Where("tags && ?", filters.Tags)
	}
	
	if filters.CreatedBy != "" {
		query = query.Where("created_by = ?", filters.CreatedBy)
	}
	
	if !filters.CreatedAfter.IsZero() {
		query = query.Where("created_at >= ?", filters.CreatedAfter)
	}
	
	// Count total
	var total int64
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, errors.Wrap(err, "failed to count pipelines")
	}
	
	// Apply pagination and preloading
	var gormPipelines []GormPipeline
	result := query.
		Preload("Steps", func(db *gorm.DB) *gorm.DB {
			return db.Order("order_index")
		}).
		Order("created_at DESC").
		Limit(filters.Limit).
		Offset(filters.Offset).
		Find(&gormPipelines)
	
	if result.Error != nil {
		return nil, 0, errors.Wrap(result.Error, "failed to find pipelines with filters")
	}
	
	// Convert to domain
	pipelines := make([]*Pipeline, len(gormPipelines))
	for i, gp := range gormPipelines {
		pipelines[i] = r.gormToDomain(&gp)
	}
	
	return pipelines, total, nil
}

// BulkUpdateStatus advanced bulk operations
func (r *GormPipelineRepository) BulkUpdateStatus(ctx context.Context, ids []uuid.UUID, status string) error {
	result := r.db.WithContext(ctx).
		Model(&GormPipeline{}).
		Where("id IN ?", ids).
		Updates(map[string]interface{}{
			"status":     status,
			"updated_at": "NOW()",
			"version":    gorm.Expr("version + 1"),
		})
	
	if result.Error != nil {
		return errors.Wrap(result.Error, "failed to bulk update pipeline status")
	}
	
	r.logger.Info("Bulk updated pipeline status",
		logging.F("count", result.RowsAffected),
		logging.F("status", status),
	)
	
	return nil
}

// DeleteWithCascade soft delete with cascade
func (r *GormPipelineRepository) DeleteWithCascade(ctx context.Context, id uuid.UUID) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Soft delete steps first
		if err := tx.Where("pipeline_id = ?", id).Delete(&GormPipelineStep{}).Error; err != nil {
			return errors.Wrap(err, "failed to delete pipeline steps")
		}
		
		// Soft delete executions
		if err := tx.Where("pipeline_id = ?", id).Delete(&GormExecution{}).Error; err != nil {
			return errors.Wrap(err, "failed to delete pipeline executions")
		}
		
		// Soft delete pipeline
		if err := tx.Delete(&GormPipeline{}, "id = ?", id).Error; err != nil {
			return errors.Wrap(err, "failed to delete pipeline")
		}
		
		return nil
	})
}

// Conversion methods
func (r *GormPipelineRepository) domainToGorm(p *Pipeline) *GormPipeline {
	metadataJSON, _ := json.Marshal(p.Metadata)
	
	gp := &GormPipeline{
		ID:          p.ID,
		Name:        p.Name,
		Description: p.Description,
		Status:      p.Status.String(),
		Tags:        p.Tags,
		Metadata:    string(metadataJSON),
		CreatedBy:   p.CreatedBy,
		Version:     p.Version,
	}
	
	// Convert steps
	for i, step := range p.Steps {
		configJSON, _ := json.Marshal(step.Config)
		
		// Convert UUID dependencies to strings
		var deps []string
		for _, dep := range step.Dependencies {
			deps = append(deps, dep.String())
		}
		
		gp.Steps = append(gp.Steps, GormPipelineStep{
			ID:           step.ID,
			PipelineID:   p.ID,
			Name:         step.Name,
			Type:         step.Type.String(),
			OrderIndex:   i,
			Config:       string(configJSON),
			Dependencies: deps,
		})
	}
	
	return gp
}

func (r *GormPipelineRepository) gormToDomain(gp *GormPipeline) *Pipeline {
	var metadata map[string]interface{}
	json.Unmarshal([]byte(gp.Metadata), &metadata)
	
	p := &Pipeline{
		ID:          gp.ID,
		Name:        gp.Name,
		Description: gp.Description,
		Tags:        gp.Tags,
		Metadata:    metadata,
		CreatedAt:   gp.CreatedAt,
		UpdatedAt:   gp.UpdatedAt,
		CreatedBy:   gp.CreatedBy,
		Version:     gp.Version,
		Steps:       make([]*Step, len(gp.Steps)),
	}
	
	// Parse status
	p.Status.FromString(gp.Status)
	
	// Convert steps
	for i, gs := range gp.Steps {
		var config map[string]interface{}
		json.Unmarshal([]byte(gs.Config), &config)
		
		// Convert string dependencies to UUIDs
		var deps []uuid.UUID
		for _, depStr := range gs.Dependencies {
			if depUUID, err := uuid.Parse(depStr); err == nil {
				deps = append(deps, depUUID)
			}
		}
		
		step := &Step{
			ID:           gs.ID,
			Name:         gs.Name,
			Config:       config,
			Dependencies: deps,
		}
		step.Type.FromString(gs.Type)
		p.Steps[i] = step
	}
	
	return p
}

// PipelineFilters for advanced querying
type PipelineFilters struct {
	Status       string
	Tags         []string
	CreatedBy    string
	CreatedAfter time.Time
	Limit        int
	Offset       int
}