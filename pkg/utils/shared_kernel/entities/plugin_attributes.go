package entities

// UpdateConfiguration updates the plugin configuration
func (p *UnifiedPlugin) UpdateConfiguration(settings map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range settings {
		p.Configuration[k] = v
	}

	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.configuration.updated", p.GetID(), map[string]interface{}{
		"configuration": settings,
	}, p.GetVersion()))
}

// AddDependency adds a dependency to the plugin
func (p *UnifiedPlugin) AddDependency(dependency string) {
	if dependency == "" {
		return
	}

	for _, dep := range p.Dependencies {
		if dep == dependency {
			return
		}
	}

	p.Dependencies = append(p.Dependencies, dependency)
	p.IncrementVersion()
}

// RemoveDependency removes a dependency from the plugin
func (p *UnifiedPlugin) RemoveDependency(dependency string) {
	for i, dep := range p.Dependencies {
		if dep == dependency {
			p.Dependencies = append(p.Dependencies[:i], p.Dependencies[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
}

// AddCapability adds a capability to the plugin
func (p *UnifiedPlugin) AddCapability(capability string) {
	if capability == "" {
		return
	}

	for _, cap := range p.Capabilities {
		if cap == capability {
			return
		}
	}

	p.Capabilities = append(p.Capabilities, capability)
	p.IncrementVersion()
}

// AddTag adds a tag to the plugin
func (p *UnifiedPlugin) AddTag(tag string) {
	if tag == "" {
		return
	}

	for _, existingTag := range p.Tags {
		if existingTag == tag {
			return
		}
	}

	p.Tags = append(p.Tags, tag)
	p.IncrementVersion()
}

// RemoveTag removes a tag from the plugin
func (p *UnifiedPlugin) RemoveTag(tag string) {
	for i, existingTag := range p.Tags {
		if existingTag == tag {
			p.Tags = append(p.Tags[:i], p.Tags[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
}

// HasCapability checks if the plugin has a specific capability
func (p *UnifiedPlugin) HasCapability(capability string) bool {
	for _, cap := range p.Capabilities {
		if cap == capability {
			return true
		}
	}
	return false
}

// HasTag checks if the plugin has a specific tag
func (p *UnifiedPlugin) HasTag(tag string) bool {
	for _, t := range p.Tags {
		if t == tag {
			return true
		}
	}
	return false
}

// HasDependency checks if the plugin has a specific dependency
func (p *UnifiedPlugin) HasDependency(dependency string) bool {
	for _, dep := range p.Dependencies {
		if dep == dependency {
			return true
		}
	}
	return false
}
