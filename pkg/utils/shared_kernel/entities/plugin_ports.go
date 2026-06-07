package entities

import (
	"errors"
	"fmt"
)

// AddPort adds a port to the plugin - UNIFIED IMPLEMENTATION
func (p *UnifiedPlugin) AddPort(port UnifiedPort) error {
	if port.Name == "" {
		return errors.New("port name cannot be empty")
	}
	if port.Type == "" {
		return errors.New("port type cannot be empty")
	}

	for _, existingPort := range p.Ports {
		if existingPort.Name == port.Name {
			return fmt.Errorf("port %s already exists", port.Name)
		}
	}

	p.Ports = append(p.Ports, port)
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("port.added", p.GetID(), map[string]interface{}{
		"port_name": port.Name,
		"port_type": port.Type,
	}, p.GetVersion()))

	return nil
}

// RemovePort removes a port from the plugin
func (p *UnifiedPlugin) RemovePort(portName string) error {
	for i, port := range p.Ports {
		if port.Name == portName {
			p.Ports = append(p.Ports[:i], p.Ports[i+1:]...)
			p.IncrementVersion()
			p.AddDomainEvent(NewBaseDomainEvent("port.removed", p.GetID(), map[string]interface{}{
				"port_name": portName,
			}, p.GetVersion()))
			return nil
		}
	}
	return fmt.Errorf("port %s not found", portName)
}

// GetPortByName returns a port by name
func (p *UnifiedPlugin) GetPortByName(name string) (*UnifiedPort, error) {
	for _, port := range p.Ports {
		if port.Name == name {
			return &port, nil
		}
	}
	return nil, fmt.Errorf("port %s not found", name)
}

// GetInputPorts returns all input ports
func (p *UnifiedPlugin) GetInputPorts() []UnifiedPort {
	var inputPorts []UnifiedPort
	for _, port := range p.Ports {
		if port.Direction == "input" || port.Direction == "bidirectional" {
			inputPorts = append(inputPorts, port)
		}
	}
	return inputPorts
}

// GetOutputPorts returns all output ports
func (p *UnifiedPlugin) GetOutputPorts() []UnifiedPort {
	var outputPorts []UnifiedPort
	for _, port := range p.Ports {
		if port.Direction == "output" || port.Direction == "bidirectional" {
			outputPorts = append(outputPorts, port)
		}
	}
	return outputPorts
}
