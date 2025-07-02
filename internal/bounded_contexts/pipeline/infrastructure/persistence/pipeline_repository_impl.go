package persistence

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/repositories"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/flext-sh/flext/internal/shared_kernel/infrastructure/persistence"
	"gorm.io/gorm"
)

// PipelineRepositoryImpl implementa PipelineRepository usando GORM
type PipelineRepositoryImpl struct {
	*persistence.BaseRepository[*entities.Pipeline]
	db *gorm.DB
}

// NewPipelineRepository cria uma nova instância do repository de pipeline
func NewPipelineRepository(db *gorm.DB) repositories.PipelineRepository {
	return &PipelineRepositoryImpl{
		BaseRepository: persistence.NewBaseRepository[*entities.Pipeline](db),
		db:             db,
	}
}

// Save salva um pipeline
func (r *PipelineRepositoryImpl) Save(ctx context.Context, pipeline *entities.Pipeline) error {
	return r.Create(ctx, pipeline)
}

// FindByName encontra um pipeline pelo nome
func (r *PipelineRepositoryImpl) FindByName(ctx context.Context, name string) (*entities.Pipeline, error) {
	var pipeline entities.Pipeline
	result := r.db.WithContext(ctx).Where("name = ?", name).First(&pipeline)

	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, &value_objects.DomainError{
				Code:        "PIPELINE_NOT_FOUND",
				Message:     "Pipeline not found",
				Description: fmt.Sprintf("No pipeline found with name: %s", name),
			}
		}
		return nil, result.Error
	}

	return &pipeline, nil
}

// FindByStatus encontra pipelines por status
func (r *PipelineRepositoryImpl) FindByStatus(ctx context.Context, status entities.PipelineStatus, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	return r.findWithFilter(ctx, "status", "eq", string(status), opts)
}

// FindByType encontra pipelines por tipo
func (r *PipelineRepositoryImpl) FindByType(ctx context.Context, pipelineType entities.PipelineType, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	return r.findWithFilter(ctx, "type", "eq", string(pipelineType), opts)
}

// FindActivePipelines encontra todos os pipelines ativos
func (r *PipelineRepositoryImpl) FindActivePipelines(ctx context.Context, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	return r.FindByStatus(ctx, entities.PipelineStatusActive, opts)
}

// FindByOwner encontra pipelines por proprietário
func (r *PipelineRepositoryImpl) FindByOwner(ctx context.Context, ownerID string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	return r.findWithFilter(ctx, "owner_id", "eq", ownerID, opts)
}

// findWithFilter is a generic helper for single field filtering
func (r *PipelineRepositoryImpl) findWithFilter(ctx context.Context, field, operator string, value interface{}, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	filter := value_objects.Filter{
		Field:    field,
		Operator: operator,
		Value:    value,
	}
	opts.Filters = append(opts.Filters, filter)

	return r.Find(ctx, opts)
}

// FindScheduledPipelines encontra pipelines que devem ser executados
func (r *PipelineRepositoryImpl) FindScheduledPipelines(ctx context.Context, scheduledAt time.Time) ([]*entities.Pipeline, error) {
	var pipelines []*entities.Pipeline

	query := r.db.WithContext(ctx).
		Where("status = ?", "active").
		Where("schedule IS NOT NULL").
		Where("schedule != ''").
		Where("next_execution <= ?", scheduledAt)

	if err := query.Find(&pipelines).Error; err != nil {
		return nil, err
	}

	return pipelines, nil
}

// GetExecutionStats obtém estatísticas de execução
func (r *PipelineRepositoryImpl) GetExecutionStats(ctx context.Context, pipelineID string) (*repositories.PipelineExecutionStats, error) {
	// Implementação básica - em produção viria de tabela de execuções
	stats := &repositories.PipelineExecutionStats{
		PipelineID:       pipelineID,
		Name:             "Pipeline",
		TotalExecutions:  0,
		SuccessfulRuns:   0,
		FailedRuns:       0,
		SuccessRate:      0.0,
		AvgRuntime:       0,
		MinRuntime:       0,
		MaxRuntime:       0,
		RecentExecutions: []*repositories.ExecutionRecord{},
		RuntimeTrend:     []*repositories.RuntimeDataPoint{},
		SuccessTrend:     []*repositories.SuccessDataPoint{},
	}

	return stats, nil
}

// GetSuccessRateStats obtém estatísticas de taxa de sucesso
func (r *PipelineRepositoryImpl) GetSuccessRateStats(ctx context.Context) (*repositories.PipelineSuccessStats, error) {
	// Implementação básica - em produção viria de tabela de execuções
	stats := &repositories.PipelineSuccessStats{
		TotalPipelines:     0,
		ActivePipelines:    0,
		TotalExecutions:    0,
		SuccessfulRuns:     0,
		FailedRuns:         0,
		OverallSuccessRate: 0.0,
		AvgSuccessRate:     0.0,
		TopPerformers:      []*repositories.PipelinePerformance{},
		WorstPerformers:    []*repositories.PipelinePerformance{},
	}

	return stats, nil
}

// Additional methods to implement all repository interface requirements

// FindByCreatedBy encontra pipelines por criador
func (r *PipelineRepositoryImpl) FindByCreatedBy(ctx context.Context, createdBy string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Adicionar filtro de criador
	createdByFilter := value_objects.Filter{
		Field:    "created_by",
		Operator: "eq",
		Value:    createdBy,
	}
	opts.Filters = append(opts.Filters, createdByFilter)

	return r.Find(ctx, opts)
}

// FindActiveScheduled encontra pipelines ativos agendados
func (r *PipelineRepositoryImpl) FindActiveScheduled(ctx context.Context, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Adicionar filtros para pipelines ativos e agendados
	activeFilter := value_objects.Filter{
		Field:    "status",
		Operator: "eq",
		Value:    string(entities.PipelineStatusActive),
	}
	scheduledFilter := value_objects.Filter{
		Field:    "schedule",
		Operator: "ne",
		Value:    "",
	}
	opts.Filters = append(opts.Filters, activeFilter, scheduledFilter)

	return r.Find(ctx, opts)
}

// FindByTags encontra pipelines por tags
func (r *PipelineRepositoryImpl) FindByTags(ctx context.Context, tags []string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Para cada tag, adicionar um filtro
	for _, tag := range tags {
		tagFilter := value_objects.Filter{
			Field:    "tags",
			Operator: "like",
			Value:    tag,
		}
		opts.Filters = append(opts.Filters, tagFilter)
	}

	return r.Find(ctx, opts)
}

// FindDueTasks encontra tarefas devidas
func (r *PipelineRepositoryImpl) FindDueTasks(ctx context.Context) ([]*entities.Pipeline, error) {
	var pipelines []*entities.Pipeline

	// Buscar pipelines ativos com schedule definido e próxima execução vencida
	now := time.Now()
	err := r.db.WithContext(ctx).
		Where("status = ?", string(entities.PipelineStatusActive)).
		Where("schedule IS NOT NULL").
		Where("schedule != ''").
		Where("next_execution <= ?", now).
		Find(&pipelines).Error

	if err != nil {
		return nil, err
	}

	return pipelines, nil
}

// FindByExtractorID encontra pipelines por extractor ID
func (r *PipelineRepositoryImpl) FindByExtractorID(ctx context.Context, extractorID string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Adicionar filtro de extractor (assumindo que está na configuração JSON)
	extractorFilter := value_objects.Filter{
		Field:    "configuration",
		Operator: "like",
		Value:    fmt.Sprintf(`"extractor_id":"%s"`, extractorID),
	}
	opts.Filters = append(opts.Filters, extractorFilter)

	return r.Find(ctx, opts)
}

// FindByLoaderID encontra pipelines por loader ID
func (r *PipelineRepositoryImpl) FindByLoaderID(ctx context.Context, loaderID string, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Adicionar filtro de loader (assumindo que está na configuração JSON)
	loaderFilter := value_objects.Filter{
		Field:    "configuration",
		Operator: "like",
		Value:    fmt.Sprintf(`"loader_id":"%s"`, loaderID),
	}
	opts.Filters = append(opts.Filters, loaderFilter)

	return r.Find(ctx, opts)
}

// Search realiza busca com query personalizada
func (r *PipelineRepositoryImpl) Search(ctx context.Context, query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) (*value_objects.Page[*entities.Pipeline], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	if query != nil {
		r.buildSearchFilters(query, opts)
	}

	return r.Find(ctx, opts)
}

// buildSearchFilters builds all filters based on the search query
func (r *PipelineRepositoryImpl) buildSearchFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	r.addTextSearchFilters(query, opts)
	r.addStatusTypeFilters(query, opts)
	r.addMetadataFilters(query, opts)
	r.addConfigurationFilters(query, opts)
	r.addScheduleFilters(query, opts)
}

// addTextSearchFilters adds name and description filters
func (r *PipelineRepositoryImpl) addTextSearchFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	if query.Name != nil && *query.Name != "" {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "name",
			Operator: "like",
			Value:    *query.Name,
		})
	}

	if query.Description != nil && *query.Description != "" {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "description",
			Operator: "like",
			Value:    *query.Description,
		})
	}
}

// addStatusTypeFilters adds status and type filters
func (r *PipelineRepositoryImpl) addStatusTypeFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	if len(query.Status) > 0 {
		statusValues := make([]string, len(query.Status))
		for i, status := range query.Status {
			statusValues[i] = string(status)
		}
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "status",
			Operator: "in",
			Value:    statusValues,
		})
	}

	if len(query.Type) > 0 {
		typeValues := make([]string, len(query.Type))
		for i, pipelineType := range query.Type {
			typeValues[i] = string(pipelineType)
		}
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "type",
			Operator: "in",
			Value:    typeValues,
		})
	}
}

// addMetadataFilters adds creator and tags filters
func (r *PipelineRepositoryImpl) addMetadataFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	if query.CreatedBy != nil && *query.CreatedBy != "" {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "created_by",
			Operator: "eq",
			Value:    *query.CreatedBy,
		})
	}

	for _, tag := range query.Tags {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "tags",
			Operator: "like",
			Value:    tag,
		})
	}
}

// addConfigurationFilters adds extractor and loader filters
func (r *PipelineRepositoryImpl) addConfigurationFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	if query.ExtractorID != nil && *query.ExtractorID != "" {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "configuration",
			Operator: "like",
			Value:    fmt.Sprintf(`"extractor_id":"%s"`, *query.ExtractorID),
		})
	}

	if query.LoaderID != nil && *query.LoaderID != "" {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "configuration",
			Operator: "like",
			Value:    fmt.Sprintf(`"loader_id":"%s"`, *query.LoaderID),
		})
	}
}

// addScheduleFilters adds scheduled pipeline filters
func (r *PipelineRepositoryImpl) addScheduleFilters(query *repositories.PipelineSearchQuery, opts *value_objects.QueryOptions) {
	if query.IsScheduled == nil {
		return
	}

	if *query.IsScheduled {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "schedule",
			Operator: "ne",
			Value:    "",
		})
	} else {
		opts.Filters = append(opts.Filters, value_objects.Filter{
			Field:    "schedule",
			Operator: "eq",
			Value:    "",
		})
	}
}

// fieldCount represents a count result grouped by a field
type fieldCount struct {
	Field string `json:"field"`
	Count int64  `json:"count"`
}

// countByField performs a generic count grouped by the specified field
func (r *PipelineRepositoryImpl) countByField(ctx context.Context, field string) ([]fieldCount, error) {
	var results []fieldCount
	err := r.db.WithContext(ctx).
		Model(&entities.Pipeline{}).
		Select(fmt.Sprintf("%s as field, COUNT(*) as count", field)).
		Group(field).
		Find(&results).Error

	return results, err
}

// CountByStatus conta pipelines por status
func (r *PipelineRepositoryImpl) CountByStatus(ctx context.Context) (map[entities.PipelineStatus]int64, error) {
	results, err := r.countByField(ctx, "status")
	if err != nil {
		return nil, err
	}

	statusMap := make(map[entities.PipelineStatus]int64)
	for _, result := range results {
		statusMap[entities.PipelineStatus(result.Field)] = result.Count
	}

	return statusMap, nil
}

// CountByType conta pipelines por tipo
func (r *PipelineRepositoryImpl) CountByType(ctx context.Context) (map[entities.PipelineType]int64, error) {
	results, err := r.countByField(ctx, "type")
	if err != nil {
		return nil, err
	}

	typeMap := make(map[entities.PipelineType]int64)
	for _, result := range results {
		typeMap[entities.PipelineType(result.Field)] = result.Count
	}

	return typeMap, nil
}

// ExistsByName verifica se existe um pipeline com o nome especificado
func (r *PipelineRepositoryImpl) ExistsByName(ctx context.Context, name string) (bool, error) {
	var count int64
	err := r.db.WithContext(ctx).
		Model(&entities.Pipeline{}).
		Where("name = ?", name).
		Count(&count).Error

	if err != nil {
		return false, err
	}

	return count > 0, nil
}

// UpdateLastExecution atualiza o timestamp da última execução
func (r *PipelineRepositoryImpl) UpdateLastExecution(ctx context.Context, pipelineID string, executionTime time.Time) error {
	result := r.db.WithContext(ctx).
		Model(&entities.Pipeline{}).
		Where("id = ?", pipelineID).
		Update("last_execution", executionTime)

	if result.Error != nil {
		return result.Error
	}

	if result.RowsAffected == 0 {
		return &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found for execution update",
			Description: fmt.Sprintf("No pipeline found with ID: %s", pipelineID),
		}
	}

	return nil
}
