package validation

// Helper validation functions

// ValidateStruct validates a struct using reflection and validation tags
// This is a simplified version - in production, consider using a library like go-playground/validator
func ValidateStruct(s interface{}) error {
	// This is a placeholder for struct validation
	// In a real implementation, you would use reflection to validate struct fields
	// based on validation tags
	return nil
}

// Pipeline-specific validation rules
const (
	MaxPipelineNameLength = 100
	MinPipelineNameLength = 3
	MaxDescriptionLength  = 1000
	MaxTagsCount          = 20
	MaxTagLength          = 50
	MinTagLength          = 1
)

// Plugin-specific validation rules
const (
	MaxPluginNameLength  = 80
	MinPluginNameLength  = 2
	MaxAuthorLength      = 100
	MaxEntryPointLength  = 255
	MaxDependenciesCount = 50
)

// ValidateCreatePipelineRequest validates a complete pipeline creation request
func ValidateCreatePipelineRequest(name, description string, tags []string) error {
	validator := NewValidator()

	validator.ValidatePipelineName(name).
		ValidateDescription(description, false).
		ValidateTags(tags)

	validator.ValidateUserInput("name", name).
		ValidateUserInput("description", description)

	return validator.Error()
}

// ValidateRegisterPluginRequest validates a complete plugin registration request
func ValidateRegisterPluginRequest(name, pluginType, version, description, author, entryPoint string, dependencies []string) error {
	validator := NewValidator()

	validator.ValidatePluginName(name).
		Required("type", pluginType).
		ValidateVersion(version).
		ValidateDescription(description, false).
		MaxLength("author", author, MaxAuthorLength).
		Required("entry_point", entryPoint).
		MaxLength("entry_point", entryPoint, MaxEntryPointLength).
		MaxItems("dependencies", dependencies, MaxDependenciesCount)

	validTypes := []string{"source", "transform", "destination", "utility"}
	validType := false
	for _, vt := range validTypes {
		if pluginType == vt {
			validType = true
			break
		}
	}
	if !validType {
		validator.errors.Add("type", "invalid plugin type (must be: source, transform, destination, or utility)", "invalid_type", pluginType)
	}

	validator.ValidateUserInput("name", name).
		ValidateUserInput("description", description).
		ValidateUserInput("author", author).
		ValidateFilePath("entry_point", entryPoint)

	return validator.Error()
}
