package plugin

// Configuration represents plugin configuration
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

// Remove removes a configuration value
func (c *Configuration) Remove(key string) {
	delete(c.values, key)
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

// Merge merges another configuration into this one
func (c *Configuration) Merge(other Configuration) {
	for k, v := range other.values {
		c.values[k] = v
	}
}

// Keys returns all configuration keys
func (c Configuration) Keys() []string {
	keys := make([]string, 0, len(c.values))
	for k := range c.values {
		keys = append(keys, k)
	}
	return keys
}

// IsEmpty checks if configuration is empty
func (c Configuration) IsEmpty() bool {
	return len(c.values) == 0
}

// PluginMetadata represents metadata about a plugin
type PluginMetadata struct {
	Author      string
	Description string
	Homepage    string
	License     string
	Repository  string
	Tags        []string
}

// PluginEndpoint represents an endpoint exposed by a plugin
type PluginEndpoint struct {
	Name        string
	Method      string
	Path        string
	Description string
	Parameters  []EndpointParameter
}

// EndpointParameter represents a parameter for an endpoint
type EndpointParameter struct {
	Name        string
	Type        string
	Required    bool
	Description string
	Default     interface{}
}

// PluginSchema represents the schema for plugin data
type PluginSchema struct {
	Input  SchemaDefinition
	Output SchemaDefinition
}

// SchemaDefinition represents a schema definition
type SchemaDefinition struct {
	Type       string
	Properties map[string]PropertyDefinition
	Required   []string
}

// PropertyDefinition represents a property in a schema
type PropertyDefinition struct {
	Type        string
	Description string
	Format      string
	Items       *PropertyDefinition // For arrays
	Properties  map[string]PropertyDefinition // For objects
}