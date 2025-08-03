package commands

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/pipeline/application/ports"
	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
	"github.com/google/uuid"
)

// AddStepCommand representa o comando para adicionar um passo ao pipeline
type AddStepCommand struct {
	PipelineID    uuid.UUID              `json:"pipeline_id" validate:"required"`
	Name          string                 `json:"name" validate:"required,max=100"`
	Type          string                 `json:"type,omitempty"`          // Tipo do passo (transform, validate, etc.)
	PluginID      uuid.UUID              `json:"plugin_id,omitempty"`     // ID do plugin a ser usado
	Configuration map[string]interface{} `json:"configuration,omitempty"` // Configuração específica do passo
	Order         int                    `json:"order,omitempty"`         // Ordem de execução (opcional, auto-calculado se não fornecido)
	DependsOn     []uuid.UUID            `json:"depends_on,omitempty"`    // Passos dos quais este depende
}

// AddStepResult resultado do comando
type AddStepResult struct {
	StepID     uuid.UUID `json:"step_id"`
	PipelineID uuid.UUID `json:"pipeline_id"`
	Name       string    `json:"name"`
	Order      int       `json:"order"`
	Message    string    `json:"message,omitempty"`
}

// AddStepHandler manipula o comando de adição de passo
type AddStepHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewAddStepHandler cria um novo handler
func NewAddStepHandler(pipelineRepo ports.PipelineRepository) *AddStepHandler {
	return &AddStepHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executa o comando
func (h *AddStepHandler) Handle(ctx context.Context, cmd AddStepCommand) (*AddStepResult, error) {
	// Validate command
	if err := h.validateCommand(cmd); err != nil {
		return nil, err
	}

	// Buscar o pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve pipeline",
			Description: err.Error(),
		}
	}

	if pipeline == nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: "The specified pipeline does not exist",
		}
	}

	// Verificar se é possível adicionar steps (pipeline não pode estar em execução)
	if err := h.validateCanAddStep(pipeline); err != nil {
		return nil, err
	}

	// Validar dependências
	if err := h.validateDependencies(pipeline, cmd.DependsOn); err != nil {
		return nil, err
	}

	// Criar o step
	step, err := h.createStep(cmd, pipeline)
	if err != nil {
		return nil, err
	}

	// Adicionar o step ao pipeline
	if err := pipeline.AddStep(*step); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "BUSINESS_RULE_VIOLATION",
			Message:     "Failed to add step to pipeline",
			Description: err.Error(),
		}
	}

	// Salvar o pipeline atualizado
	if err := h.pipelineRepo.Save(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to save pipeline with new step",
			Description: err.Error(),
		}
	}

	// Preparar resultado
	result := &AddStepResult{
		StepID:     step.ID,
		PipelineID: cmd.PipelineID,
		Name:       step.Name,
		Order:      step.Order,
		Message:    "Step added successfully",
	}

	return result, nil
}

// validateCommand performs comprehensive command validation
func (h *AddStepHandler) validateCommand(cmd AddStepCommand) error {
	if cmd.PipelineID == uuid.Nil {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Pipeline ID is required",
			Description: "PipelineID field cannot be empty",
		}
	}

	if cmd.Name == "" {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Step name is required",
			Description: "Name field cannot be empty",
		}
	}

	if len(cmd.Name) < 3 || len(cmd.Name) > 100 {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Step name must be between 3 and 100 characters",
			Description: "Name length validation failed",
		}
	}

	// Validate step type if provided
	if cmd.Type != "" {
		validTypes := []string{"extract", "transform", "load", "validate", "filter", "aggregate", "custom"}
		isValid := false
		for _, validType := range validTypes {
			if cmd.Type == validType {
				isValid = true
				break
			}
		}
		if !isValid {
			return &value_objects.DomainError{
				Code:        "INVALID_COMMAND",
				Message:     "Invalid step type",
				Description: "Step type must be one of: extract, transform, load, validate, filter, aggregate, custom",
			}
		}
	}

	// Validate order if provided
	if cmd.Order < 0 {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Step order cannot be negative",
			Description: "Order must be 0 or positive integer",
		}
	}

	// Validate configuration if provided
	if cmd.Configuration != nil {
		if len(cmd.Configuration) > 50 {
			return &value_objects.DomainError{
				Code:        "INVALID_COMMAND",
				Message:     "Configuration too large",
				Description: "Configuration cannot contain more than 50 keys",
			}
		}

		// Validate configuration values
		for key, value := range cmd.Configuration {
			if key == "" {
				return &value_objects.DomainError{
					Code:        "INVALID_COMMAND",
					Message:     "Invalid configuration key",
					Description: "Configuration keys cannot be empty",
				}
			}

			// Ensure value is JSON-serializable
			switch value.(type) {
			case string, int, int64, float64, bool, map[string]interface{}, []interface{}, nil:
				// Valid types
			default:
				return &value_objects.DomainError{
					Code:        "INVALID_COMMAND",
					Message:     "Invalid configuration value type",
					Description: "Configuration values must be JSON-serializable",
				}
			}
		}
	}

	return nil
}

// validateCanAddStep checks if step can be added to pipeline
func (h *AddStepHandler) validateCanAddStep(pipeline *entities.Pipeline) error {
	// Check if pipeline allows modifications
	if pipeline.Status == entities.PipelineStatusCompleted || pipeline.Status == entities.PipelineStatusFailed {
		return &value_objects.DomainError{
			Code:        "BUSINESS_RULE_VIOLATION",
			Message:     "Cannot add steps to completed or failed pipeline",
			Description: "Pipeline must be in draft, active, or paused status to add steps",
		}
	}

	// Check step limit (business rule)
	maxSteps := 50 // Business rule: maximum 50 steps per pipeline
	if len(pipeline.Steps) >= maxSteps {
		return &value_objects.DomainError{
			Code:        "BUSINESS_RULE_VIOLATION",
			Message:     "Pipeline has reached maximum number of steps",
			Description: "Maximum 50 steps allowed per pipeline",
		}
	}

	return nil
}

// validateDependencies validates step dependencies
func (h *AddStepHandler) validateDependencies(pipeline *entities.Pipeline, dependsOn []uuid.UUID) error {
	if len(dependsOn) == 0 {
		return nil // No dependencies to validate
	}

	// Check if all dependencies exist in the pipeline
	stepMap := make(map[uuid.UUID]bool)
	for _, step := range pipeline.Steps {
		stepMap[step.ID] = true
	}

	for _, depID := range dependsOn {
		if !stepMap[depID] {
			return &value_objects.DomainError{
				Code:        "DEPENDENCY_NOT_FOUND",
				Message:     "Step dependency not found",
				Description: "All dependencies must exist in the same pipeline",
			}
		}
	}

	// Check for circular dependencies (basic check)
	if len(dependsOn) > 10 {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Too many dependencies",
			Description: "Maximum 10 dependencies allowed per step",
		}
	}

	return nil
}

// createStep creates a new pipeline step from command
func (h *AddStepHandler) createStep(cmd AddStepCommand, pipeline *entities.Pipeline) (*entities.PipelineStep, error) {
	stepID := uuid.New()

	// Calculate order if not provided
	order := cmd.Order
	if order == 0 {
		// Auto-calculate next order
		maxOrder := 0
		for _, step := range pipeline.Steps {
			if step.Order > maxOrder {
				maxOrder = step.Order
			}
		}
		order = maxOrder + 1
	}

	// Use provided PluginID or generate a default one
	pluginID := cmd.PluginID
	if pluginID == uuid.Nil {
		// For now, generate a default plugin ID
		// In real implementation, this would be based on step type or user selection
		pluginID = uuid.New()
	}

	// Prepare configuration
	configuration := cmd.Configuration
	if configuration == nil {
		configuration = make(map[string]interface{})
	}

	// Add step metadata to configuration
	configuration["step_type"] = cmd.Type
	configuration["created_at"] = "system_generated"

	step := &entities.PipelineStep{
		ID:            stepID,
		Name:          cmd.Name,
		PluginID:      pluginID,
		Configuration: configuration,
		Order:         order,
		DependsOn:     cmd.DependsOn,
	}

	return step, nil
}

// validateStepName checks if step name is unique within pipeline
func (h *AddStepHandler) validateStepName(pipeline *entities.Pipeline, stepName string) error {
	for _, step := range pipeline.Steps {
		if step.Name == stepName {
			return &value_objects.DomainError{
				Code:        "STEP_NAME_EXISTS",
				Message:     "Step name already exists",
				Description: "Step names must be unique within a pipeline",
			}
		}
	}
	return nil
}
