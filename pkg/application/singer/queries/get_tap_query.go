package queries

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/singer/application/ports"
	"github.com/flext-sh/flext/pkg/domain/singer/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
	"github.com/google/uuid"
)

// GetTapQuery represents a query to get a tap by ID
type GetTapQuery struct {
	TapID string `json:"tap_id" validate:"required"`
}

// TapDTO represents a tap data transfer object
type TapDTO struct {
	ID                string                 `json:"id"`
	Name              string                 `json:"name"`
	DisplayName       string                 `json:"display_name,omitempty"`
	Description       string                 `json:"description,omitempty"`
	Type              entities.TapType       `json:"type"`
	Status            entities.TapStatus     `json:"status"`
	TapVersion        string                 `json:"tap_version,omitempty"`
	PipName           string                 `json:"pip_name,omitempty"`
	Executable        string                 `json:"executable,omitempty"`
	Repository        string                 `json:"repository,omitempty"`
	HomePage          string                 `json:"home_page,omitempty"`
	Settings          map[string]interface{} `json:"settings,omitempty"`
	ConfigSchema      map[string]interface{} `json:"config_schema,omitempty"`
	StreamMaps        map[string]interface{} `json:"stream_maps,omitempty"`
	Capabilities      []string               `json:"capabilities,omitempty"`
	SupportedFeatures []string               `json:"supported_features,omitempty"`
	Author            string                 `json:"author,omitempty"`
	License           string                 `json:"license,omitempty"`
	Tags              []string               `json:"tags,omitempty"`
	InstallationPath  string                 `json:"installation_path,omitempty"`
	PythonVersion     string                 `json:"python_version,omitempty"`
	Dependencies      []string               `json:"dependencies,omitempty"`
	UsageCount        int                    `json:"usage_count"`
	CreatedAt         string                 `json:"created_at"`
	UpdatedAt         string                 `json:"updated_at"`
	Version           int64                  `json:"version"`
}

// GetTapHandler handles get tap queries
type GetTapHandler struct {
	tapRepo ports.TapRepository
}

// NewGetTapHandler creates a new get tap handler
func NewGetTapHandler(tapRepo ports.TapRepository) *GetTapHandler {
	return &GetTapHandler{
		tapRepo: tapRepo,
	}
}

// Handle executes the get tap query
func (h *GetTapHandler) Handle(ctx context.Context, query GetTapQuery) (*TapDTO, error) {
	// Validate query
	if err := h.validateQuery(query); err != nil {
		return nil, err
	}

	// Parse tap ID
	tapID, err := uuid.Parse(query.TapID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TAP_ID",
			Message:     "Invalid tap ID format",
			Description: err.Error(),
		}
	}

	// Get tap from repository
	tap, err := h.tapRepo.GetByID(ctx, tapID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to retrieve tap",
			Description: err.Error(),
		}
	}

	if tap == nil {
		return nil, &value_objects.DomainError{
			Code:        "TAP_NOT_FOUND",
			Message:     "Tap not found",
			Description: "The specified tap does not exist",
		}
	}

	// Convert to DTO
	return h.mapToDTO(tap), nil
}

// validateQuery validates the query
func (h *GetTapHandler) validateQuery(query GetTapQuery) error {
	if query.TapID == "" {
		return &value_objects.DomainError{
			Code:        "INVALID_QUERY",
			Message:     "Tap ID is required",
			Description: "TapID field cannot be empty",
		}
	}

	return nil
}

// mapToDTO converts tap entity to DTO
func (h *GetTapHandler) mapToDTO(tap *entities.Tap) *TapDTO {
	return &TapDTO{
		ID:                tap.ID.String(),
		Name:              tap.Name,
		DisplayName:       tap.DisplayName,
		Description:       tap.Description,
		Type:              tap.Type,
		Status:            tap.Status,
		TapVersion:        tap.TapVersion,
		PipName:           tap.PipName,
		Executable:        tap.Executable,
		Repository:        tap.Repository,
		HomePage:          tap.HomePage,
		Settings:          tap.Settings,
		ConfigSchema:      tap.ConfigSchema,
		StreamMaps:        tap.StreamMaps,
		Capabilities:      tap.Capabilities,
		SupportedFeatures: tap.SupportedFeatures,
		Author:            tap.Author,
		License:           tap.License,
		Tags:              tap.Tags,
		InstallationPath:  tap.InstallationPath,
		PythonVersion:     tap.PythonVersion,
		Dependencies:      tap.Dependencies,
		UsageCount:        tap.UsageCount,
		CreatedAt:         tap.CreatedAt.Format("2006-01-02T15:04:05Z"),
		UpdatedAt:         tap.UpdatedAt.Format("2006-01-02T15:04:05Z"),
		Version:           tap.Version,
	}
}
