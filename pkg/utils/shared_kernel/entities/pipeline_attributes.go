package entities

// UpdateConfiguration updates the pipeline configuration
func (p *UnifiedPipeline) UpdateConfiguration(settings map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range settings {
		p.Configuration[k] = v
	}

	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.configuration.updated", p.GetID(), map[string]interface{}{
		"configuration": settings,
	}, p.GetVersion()))
}

// SetSchedule sets the pipeline schedule
func (p *UnifiedPipeline) SetSchedule(schedule string) {
	p.Schedule = schedule
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("pipeline.schedule.updated", p.GetID(), map[string]interface{}{
		"schedule": schedule,
	}, p.GetVersion()))
}

// AddTag adds a tag to the pipeline
func (p *UnifiedPipeline) AddTag(tag string) {
	for _, existingTag := range p.Tags {
		if existingTag == tag {
			return
		}
	}
	p.Tags = append(p.Tags, tag)
	p.IncrementVersion()
}

// RemoveTag removes a tag from the pipeline
func (p *UnifiedPipeline) RemoveTag(tag string) {
	for i, existingTag := range p.Tags {
		if existingTag == tag {
			p.Tags = append(p.Tags[:i], p.Tags[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
}

// IsScheduled returns true if the pipeline has a schedule
func (p *UnifiedPipeline) IsScheduled() bool {
	return p.Schedule != ""
}

// HasTag checks if the pipeline has a specific tag
func (p *UnifiedPipeline) HasTag(tag string) bool {
	for _, t := range p.Tags {
		if t == tag {
			return true
		}
	}
	return false
}
