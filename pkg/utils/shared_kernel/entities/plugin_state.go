package entities

import "errors"

// Activate activates the plugin - UNIFIED BUSINESS LOGIC
func (p *UnifiedPlugin) Activate() error {
	if p.Status == UnifiedPluginStatusActive {
		return errors.New("plugin is already active")
	}
	if p.Status == UnifiedPluginStatusFailed {
		return errors.New("cannot activate failed plugin")
	}

	p.Status = UnifiedPluginStatusActive
	p.IsActive = true
	p.Metadata.Health = "healthy"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.activated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Deactivate deactivates the plugin
func (p *UnifiedPlugin) Deactivate() {
	if p.Status == UnifiedPluginStatusInactive {
		return
	}

	p.Status = UnifiedPluginStatusInactive
	p.IsActive = false
	p.Metadata.Health = "inactive"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.deactivated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))
}

// MarkAsFailed marks the plugin as failed
func (p *UnifiedPlugin) MarkAsFailed(reason string) {
	p.Status = UnifiedPluginStatusFailed
	p.IsActive = false
	p.Metadata.FailureReason = reason
	p.Metadata.Health = "failed"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.failed", p.GetID(), map[string]interface{}{
		"name":   p.Name,
		"reason": reason,
	}, p.GetVersion()))
}

// CanExecute checks if plugin can execute
func (p *UnifiedPlugin) CanExecute() error {
	if p.Status != UnifiedPluginStatusActive {
		return errors.New("plugin is not active")
	}
	if p.Metadata.Health == "failed" {
		return errors.New("plugin health check failed")
	}
	return nil
}

// IsCompatibleWith checks if this plugin is compatible with another plugin
func (p *UnifiedPlugin) IsCompatibleWith(other *UnifiedPlugin) bool {
	return p.Type != other.Type
}
