package gateways

import (
	"context"
	"errors"

	domainPipeline "github.com/flext-sh/flext/internal/domain/pipeline"
	"github.com/flext-sh/flext/internal/infrastructure/persistence"
	"github.com/flext-sh/flext/internal/usecases/pipeline"
	"github.com/google/uuid"
)

// PipelineRepositoryGateway adapts the infrastructure persistence to the use case interface
type PipelineRepositoryGateway struct {
	store persistence.PipelineStore
}

// NewPipelineRepositoryGateway creates a new repository gateway
func NewPipelineRepositoryGateway(store persistence.PipelineStore) *PipelineRepositoryGateway {
	return &PipelineRepositoryGateway{
		store: store,
	}
}

// Save persists a pipeline
func (g *PipelineRepositoryGateway) Save(ctx context.Context, p *domainPipeline.Pipeline) error {
	// Convert domain entity to persistence model
	model := g.domainToPersistence(p)

	// Save using the store
	return g.store.Create(ctx, model)
}

// FindByID retrieves a pipeline by ID
func (g *PipelineRepositoryGateway) FindByID(ctx context.Context, id uuid.UUID) (*domainPipeline.Pipeline, error) {
	// Fetch from store
	model, err := g.store.GetByID(ctx, id.String())
	if err != nil {
		if errors.Is(err, persistence.ErrNotFound) {
			return nil, nil
		}
		return nil, err
	}

	// Convert to domain entity
	return g.persistenceToDomain(model)
}

// FindByName retrieves a pipeline by name
func (g *PipelineRepositoryGateway) FindByName(ctx context.Context, name string) (*domainPipeline.Pipeline, error) {
	// Fetch from store
	model, err := g.store.GetByName(ctx, name)
	if err != nil {
		if errors.Is(err, persistence.ErrNotFound) {
			return nil, nil
		}
		return nil, err
	}

	// Convert to domain entity
	return g.persistenceToDomain(model)
}

// ExistsByName checks if a pipeline exists with the given name
func (g *PipelineRepositoryGateway) ExistsByName(ctx context.Context, name string) (bool, error) {
	return g.store.ExistsByName(ctx, name)
}

// List retrieves pipelines based on criteria
func (g *PipelineRepositoryGateway) List(ctx context.Context, criteria pipeline.ListCriteria) ([]*domainPipeline.Pipeline, int, error) {
	// Convert criteria to store filter
	filter := persistence.PipelineFilter{
		Limit:    criteria.Limit,
		Offset:   criteria.Offset,
		Active:   criteria.Active,
		Tags:     criteria.Tags,
		OrderBy:  criteria.OrderBy,
		OrderDir: criteria.OrderDir,
	}

	// Fetch from store
	models, total, err := g.store.List(ctx, filter)
	if err != nil {
		return nil, 0, err
	}

	// Convert to domain entities
	pipelines := make([]*domainPipeline.Pipeline, len(models))
	for i, model := range models {
		p, err := g.persistenceToDomain(model)
		if err != nil {
			return nil, 0, err
		}
		pipelines[i] = p
	}

	return pipelines, total, nil
}

// Delete removes a pipeline
func (g *PipelineRepositoryGateway) Delete(ctx context.Context, id uuid.UUID) error {
	return g.store.Delete(ctx, id.String())
}

// Conversion methods

func (g *PipelineRepositoryGateway) domainToPersistence(p *domainPipeline.Pipeline) *persistence.PipelineModel {
	// Convert steps
	steps := make([]persistence.StepModel, len(p.Steps()))
	for i, step := range p.Steps() {
		steps[i] = persistence.StepModel{
			ID:            step.ID().String(),
			Name:          step.Name(),
			PluginID:      step.PluginID().String(),
			Configuration: step.Configuration(),
			DependsOn:     g.uuidsToStrings(step.DependsOn()),
		}
	}

	return &persistence.PipelineModel{
		ID:            p.ID().String(),
		Name:          p.Name(),
		Description:   p.Description(),
		IsActive:      p.IsActive(),
		Tags:          p.Tags(),
		Configuration: p.Configuration().ToMap(),
		Steps:         steps,
	}
}

func (g *PipelineRepositoryGateway) persistenceToDomain(model *persistence.PipelineModel) (*domainPipeline.Pipeline, error) {
	// Parse ID
	id, err := uuid.Parse(model.ID)
	if err != nil {
		return nil, err
	}

	// Convert steps
	steps := make([]domainPipeline.Step, len(model.Steps))
	for i, stepModel := range model.Steps {
		stepID, err := uuid.Parse(stepModel.ID)
		if err != nil {
			return nil, err
		}

		pluginID, err := uuid.Parse(stepModel.PluginID)
		if err != nil {
			return nil, err
		}

		dependsOn, err := g.stringsToUUIDs(stepModel.DependsOn)
		if err != nil {
			return nil, err
		}

		steps[i] = domainPipeline.RestoreStep(
			stepID,
			stepModel.Name,
			pluginID,
			stepModel.Configuration,
			dependsOn,
		)
	}

	// Restore configuration
	config := domainPipeline.RestoreConfiguration(model.Configuration)

	// Restore pipeline
	return domainPipeline.RestorePipeline(
		id,
		model.Name,
		model.Description,
		model.IsActive,
		steps,
		model.Tags,
		config,
	), nil
}

func (g *PipelineRepositoryGateway) uuidsToStrings(uuids []uuid.UUID) []string {
	strings := make([]string, len(uuids))
	for i, id := range uuids {
		strings[i] = id.String()
	}
	return strings
}

func (g *PipelineRepositoryGateway) stringsToUUIDs(strings []string) ([]uuid.UUID, error) {
	uuids := make([]uuid.UUID, len(strings))
	for i, s := range strings {
		id, err := uuid.Parse(s)
		if err != nil {
			return nil, err
		}
		uuids[i] = id
	}
	return uuids, nil
}
