package commands

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/domain/singer/application/ports"
	"github.com/flext-sh/flext/pkg/domain/singer/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
)

// InstallTapCommand representa o comando para instalar um tap
type InstallTapCommand struct {
	Name          string                 `json:"name" validate:"required,min=3,max=100"`
	DisplayName   string                 `json:"display_name,omitempty"`
	Description   string                 `json:"description,omitempty" validate:"max=500"`
	Type          entities.TapType       `json:"type" validate:"required"`
	PipName       string                 `json:"pip_name,omitempty"`
	Version       string                 `json:"version,omitempty"`
	Repository    string                 `json:"repository,omitempty"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
	Force         bool                   `json:"force,omitempty"`
}

// InstallTapResult resultado do comando
type InstallTapResult struct {
	TapID            string             `json:"tap_id"`
	Name             string             `json:"name"`
	Version          string             `json:"version"`
	Status           entities.TapStatus `json:"status"`
	InstallationPath string             `json:"installation_path"`
	InstalledAt      time.Time          `json:"installed_at"`
	Message          string             `json:"message,omitempty"`
}

// InstallTapHandler manipula o comando de instalacao de tap
type InstallTapHandler struct {
	tapRepo ports.TapRepository
}

// NewInstallTapHandler cria um novo handler
func NewInstallTapHandler(tapRepo ports.TapRepository) *InstallTapHandler {
	return &InstallTapHandler{
		tapRepo: tapRepo,
	}
}

// Handle executa o comando
func (h *InstallTapHandler) Handle(ctx context.Context, cmd InstallTapCommand) (*InstallTapResult, error) {
	// Validate command
	if err := h.validateCommand(cmd); err != nil {
		return nil, err
	}

	// Check if tap already exists
	existingTap, err := h.tapRepo.GetByName(ctx, cmd.Name)
	if err != nil && !isNotFoundError(err) {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to check existing tap",
			Description: err.Error(),
		}
	}

	// Handle existing tap
	if existingTap != nil {
		if existingTap.IsInstalled() && !cmd.Force {
			return nil, &value_objects.DomainError{
				Code:        "TAP_ALREADY_INSTALLED",
				Message:     "Tap is already installed",
				Description: "Use force=true to reinstall",
			}
		}

		// Reinstall existing tap
		return h.reinstallTap(ctx, existingTap, cmd)
	}

	// Create new tap
	tap := entities.NewTap(cmd.Name, cmd.DisplayName, cmd.Description, cmd.Type)

	// Set additional properties
	if cmd.PipName != "" {
		tap.PipName = cmd.PipName
	}
	if cmd.Repository != "" {
		tap.Repository = cmd.Repository
	}
	if cmd.Configuration != nil {
		if err := tap.UpdateConfiguration(cmd.Configuration); err != nil {
			return nil, &value_objects.DomainError{
				Code:        "INVALID_CONFIGURATION",
				Message:     "Invalid tap configuration",
				Description: err.Error(),
			}
		}
	}

	// Validate tap before installation
	if err := tap.Validate(); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TAP",
			Message:     "Tap validation failed",
			Description: err.Error(),
		}
	}

	// Simulate installation (in real implementation, this would call external installer)
	installationPath, version, err := h.performInstallation(tap, cmd.Version)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INSTALLATION_FAILED",
			Message:     "Failed to install tap",
			Description: err.Error(),
		}
	}

	// Mark tap as installed
	if err := tap.Install(version, installationPath); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "TAP_STATE_ERROR",
			Message:     "Failed to update tap state",
			Description: err.Error(),
		}
	}

	// Save tap
	if err := h.tapRepo.Save(ctx, tap); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to save tap",
			Description: err.Error(),
		}
	}

	// Prepare result
	result := &InstallTapResult{
		TapID:            tap.ID.String(),
		Name:             tap.Name,
		Version:          tap.TapVersion,
		Status:           tap.Status,
		InstallationPath: tap.InstallationPath,
		InstalledAt:      tap.UpdatedAt,
		Message:          "Tap installed successfully",
	}

	return result, nil
}

// validateCommand performs comprehensive command validation
func (h *InstallTapHandler) validateCommand(cmd InstallTapCommand) error {
	if cmd.Name == "" {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Tap name is required",
			Description: "Name field cannot be empty",
		}
	}

	if len(cmd.Name) < 3 || len(cmd.Name) > 100 {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Tap name must be between 3 and 100 characters",
			Description: "Name length validation failed",
		}
	}

	// Validate tap type
	validTypes := []entities.TapType{
		entities.TapTypeExtractor,
		entities.TapTypeLoader,
		entities.TapTypeUtility,
	}
	isValidType := false
	for _, validType := range validTypes {
		if cmd.Type == validType {
			isValidType = true
			break
		}
	}
	if !isValidType {
		return &value_objects.DomainError{
			Code:        "INVALID_COMMAND",
			Message:     "Invalid tap type",
			Description: "Type must be extractor, loader, or utility",
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
	}

	return nil
}

// reinstallTap handles reinstallation of existing tap
func (h *InstallTapHandler) reinstallTap(ctx context.Context, tap *entities.Tap, cmd InstallTapCommand) (*InstallTapResult, error) {
	// Uninstall first if installed
	if tap.IsInstalled() {
		if err := tap.Uninstall(); err != nil {
			return nil, &value_objects.DomainError{
				Code:        "UNINSTALL_FAILED",
				Message:     "Failed to uninstall existing tap",
				Description: err.Error(),
			}
		}
	}

	// Update configuration if provided
	if cmd.Configuration != nil {
		if err := tap.UpdateConfiguration(cmd.Configuration); err != nil {
			return nil, &value_objects.DomainError{
				Code:        "INVALID_CONFIGURATION",
				Message:     "Invalid tap configuration",
				Description: err.Error(),
			}
		}
	}

	// Perform installation
	installationPath, version, err := h.performInstallation(tap, cmd.Version)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INSTALLATION_FAILED",
			Message:     "Failed to reinstall tap",
			Description: err.Error(),
		}
	}

	// Mark as installed
	if err := tap.Install(version, installationPath); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "TAP_STATE_ERROR",
			Message:     "Failed to update tap state",
			Description: err.Error(),
		}
	}

	// Update in repository
	updatedTap, err := h.tapRepo.Update(ctx, tap)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to update tap",
			Description: err.Error(),
		}
	}

	return &InstallTapResult{
		TapID:            updatedTap.ID.String(),
		Name:             updatedTap.Name,
		Version:          updatedTap.TapVersion,
		Status:           updatedTap.Status,
		InstallationPath: updatedTap.InstallationPath,
		InstalledAt:      updatedTap.UpdatedAt,
		Message:          "Tap reinstalled successfully",
	}, nil
}

// performInstallation simulates tap installation
func (h *InstallTapHandler) performInstallation(tap *entities.Tap, requestedVersion string) (string, string, error) {
	// In real implementation, this would:
	// 1. Check if pip package exists
	// 2. Install using pip or other package manager
	// 3. Verify installation
	// 4. Return actual installation path and version

	// For now, simulate successful installation
	version := requestedVersion
	if version == "" {
		version = "1.0.0" // Default version
	}

	installationPath := "/usr/local/bin/" + tap.Name

	// Simulate some validation
	if tap.PipName == "failing-tap" {
		return "", "", &value_objects.DomainError{
			Code:        "INSTALLATION_ERROR",
			Message:     "Package not found",
			Description: "The specified pip package could not be found",
		}
	}

	return installationPath, version, nil
}

// isNotFoundError checks if error is a not found error
func isNotFoundError(err error) bool {
	if domainErr, ok := err.(*value_objects.DomainError); ok {
		return domainErr.Code == "TAP_NOT_FOUND" || domainErr.Code == "NOT_FOUND"
	}
	return false
}
