package entities

import (
	"errors"
	"time"
)

// Activate activates the pipeline - UNIFIED BUSINESS LOGIC
func (p *UnifiedPipeline) Activate() error {
	if p.Status == UnifiedPipelineStatusActive {
		return errors.New("pipeline is already active")
	}

	if len(p.Steps) == 0 {
		return errors.New("cannot activate pipeline without steps")
	}

	p.Status = UnifiedPipelineStatusActive
	p.IsActive = true
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.activated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Deactivate deactivates the pipeline
func (p *UnifiedPipeline) Deactivate() error {
	if p.Status == UnifiedPipelineStatusRunning {
		return errors.New("cannot deactivate running pipeline")
	}

	p.Status = UnifiedPipelineStatusDraft
	p.IsActive = false
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.deactivated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Start starts the pipeline execution
func (p *UnifiedPipeline) Start() error {
	if p.Status != UnifiedPipelineStatusActive {
		return errors.New("can only start active pipelines")
	}

	if p.Status == UnifiedPipelineStatusRunning {
		return errors.New("pipeline is already running")
	}

	p.Status = UnifiedPipelineStatusRunning
	now := time.Now()
	p.LastRunAt = &now
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.started", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"timestamp": now,
	}, p.GetVersion()))

	return nil
}

// Complete marks the pipeline as completed
func (p *UnifiedPipeline) Complete() error {
	if p.Status != UnifiedPipelineStatusRunning {
		return errors.New("can only complete running pipelines")
	}

	p.Status = UnifiedPipelineStatusCompleted
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.completed", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"timestamp": time.Now(),
	}, p.GetVersion()))

	return nil
}

// Fail marks the pipeline as failed
func (p *UnifiedPipeline) Fail(reason string) error {
	if p.Status != UnifiedPipelineStatusRunning {
		return errors.New("can only fail running pipelines")
	}

	p.Status = UnifiedPipelineStatusFailed
	p.IncrementVersion()

	p.AddDomainEvent(NewBaseDomainEvent("pipeline.failed", p.GetID(), map[string]interface{}{
		"name":      p.Name,
		"reason":    reason,
		"timestamp": time.Now(),
	}, p.GetVersion()))

	return nil
}

// CanExecute checks if the pipeline can be executed
func (p *UnifiedPipeline) CanExecute() error {
	if p.Status != UnifiedPipelineStatusActive {
		return errors.New("pipeline is not active")
	}
	if len(p.Steps) == 0 {
		return errors.New("pipeline has no steps")
	}
	return nil
}
