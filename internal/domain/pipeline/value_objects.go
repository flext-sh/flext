package pipeline

import (
	"errors"
	"github.com/google/uuid"
)

// Step represents a pipeline execution step
type Step struct {
	id        uuid.UUID
	name      string
	pluginID  uuid.UUID
	config    map[string]interface{}
	dependsOn []uuid.UUID
}

// NewStep creates a new step with validation
func NewStep(name string, pluginID uuid.UUID) (*Step, error) {
	if name == "" {
		return nil, errors.New("step name cannot be empty")
	}

	if pluginID == uuid.Nil {
		return nil, errors.New("step must have a valid plugin ID")
	}

	return &Step{
		id:        uuid.New(),
		name:      name,
		pluginID:  pluginID,
		config:    make(map[string]interface{}),
		dependsOn: make([]uuid.UUID, 0),
	}, nil
}

// RestoreStep recreates a step from persistence
func RestoreStep(
	id uuid.UUID,
	name string,
	pluginID uuid.UUID,
	config map[string]interface{},
	dependsOn []uuid.UUID,
) Step {
	return Step{
		id:        id,
		name:      name,
		pluginID:  pluginID,
		config:    config,
		dependsOn: dependsOn,
	}
}

// AddDependency adds a dependency to another step
func (s *Step) AddDependency(stepID uuid.UUID) error {
	if stepID == uuid.Nil {
		return errors.New("invalid dependency step ID")
	}

	if stepID == s.id {
		return errors.New("step cannot depend on itself")
	}

	// Check if already exists
	for _, dep := range s.dependsOn {
		if dep == stepID {
			return errors.New("dependency already exists")
		}
	}

	s.dependsOn = append(s.dependsOn, stepID)
	return nil
}

// SetConfiguration sets a configuration value
func (s *Step) SetConfiguration(key string, value interface{}) {
	if s.config == nil {
		s.config = make(map[string]interface{})
	}
	s.config[key] = value
}

// Validate validates the step configuration
func (s Step) Validate() error {
	if s.name == "" {
		return errors.New("step name is required")
	}

	if s.pluginID == uuid.Nil {
		return errors.New("step plugin ID is required")
	}

	// Additional validation can be added here
	return nil
}

// Getters
func (s Step) ID() uuid.UUID          { return s.id }
func (s Step) Name() string           { return s.name }
func (s Step) PluginID() uuid.UUID    { return s.pluginID }
func (s Step) DependsOn() []uuid.UUID { return append([]uuid.UUID{}, s.dependsOn...) }
func (s Step) Configuration() map[string]interface{} {
	// Return a copy to prevent external modification
	config := make(map[string]interface{})
	for k, v := range s.config {
		config[k] = v
	}
	return config
}

// Configuration represents pipeline configuration
type Configuration struct {
	values map[string]interface{}
}

// NewConfiguration creates a new configuration
func NewConfiguration() Configuration {
	return Configuration{
		values: make(map[string]interface{}),
	}
}

// RestoreConfiguration recreates configuration from persistence
func RestoreConfiguration(values map[string]interface{}) Configuration {
	return Configuration{values: values}
}

// Set sets a configuration value
func (c *Configuration) Set(key string, value interface{}) {
	if c.values == nil {
		c.values = make(map[string]interface{})
	}
	c.values[key] = value
}

// Get retrieves a configuration value
func (c Configuration) Get(key string) (interface{}, bool) {
	val, exists := c.values[key]
	return val, exists
}

// GetString retrieves a string configuration value
func (c Configuration) GetString(key string) (string, bool) {
	val, exists := c.values[key]
	if !exists {
		return "", false
	}
	str, ok := val.(string)
	return str, ok
}

// GetInt retrieves an integer configuration value
func (c Configuration) GetInt(key string) (int, bool) {
	val, exists := c.values[key]
	if !exists {
		return 0, false
	}

	switch v := val.(type) {
	case int:
		return v, true
	case int64:
		return int(v), true
	case float64:
		return int(v), true
	default:
		return 0, false
	}
}

// GetBool retrieves a boolean configuration value
func (c Configuration) GetBool(key string) (bool, bool) {
	val, exists := c.values[key]
	if !exists {
		return false, false
	}
	b, ok := val.(bool)
	return b, ok
}

// Clone returns a copy of the configuration
func (c Configuration) Clone() Configuration {
	values := make(map[string]interface{})
	for k, v := range c.values {
		values[k] = v
	}
	return Configuration{values: values}
}

// ToMap returns configuration as a map
func (c Configuration) ToMap() map[string]interface{} {
	result := make(map[string]interface{})
	for k, v := range c.values {
		result[k] = v
	}
	return result
}

// ExecutionContext represents the context for pipeline execution
type ExecutionContext struct {
	pipelineID uuid.UUID
	values     map[string]interface{}
}

// NewExecutionContext creates a new execution context
func NewExecutionContext(pipelineID uuid.UUID) *ExecutionContext {
	return &ExecutionContext{
		pipelineID: pipelineID,
		values:     make(map[string]interface{}),
	}
}

// Set sets a context value
func (ec *ExecutionContext) Set(key string, value interface{}) {
	ec.values[key] = value
}

// Get retrieves a context value
func (ec *ExecutionContext) Get(key string) (interface{}, bool) {
	val, exists := ec.values[key]
	return val, exists
}

// PipelineID returns the pipeline ID
func (ec *ExecutionContext) PipelineID() uuid.UUID {
	return ec.pipelineID
}
