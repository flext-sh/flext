package entities

import (
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain/entities"
)

// TapStatus representa o status de um tap
type TapStatus string

const (
	TapStatusInstalled    TapStatus = "installed"
	TapStatusNotInstalled TapStatus = "not_installed"
	TapStatusUpdating     TapStatus = "updating"
	TapStatusFailed       TapStatus = "failed"
	TapStatusDeprecated   TapStatus = "deprecated"
)

// TapType representa o tipo de tap
type TapType string

const (
	TapTypeExtractor TapType = "extractor"
	TapTypeLoader    TapType = "loader"
	TapTypeUtility   TapType = "utility"
)

// Tap representa um Singer tap (extractor ou loader)
type Tap struct {
	entities.BaseEntity

	// Core attributes
	Name        string    `json:"name" validate:"required,min=3,max=100"`
	DisplayName string    `json:"display_name,omitempty"`
	Description string    `json:"description,omitempty" validate:"max=500"`
	Type        TapType   `json:"type" validate:"required"`
	Status      TapStatus `json:"status"`
	TapVersion  string    `json:"tap_version,omitempty"`

	// Technical details
	PipName    string `json:"pip_name,omitempty"`
	Executable string `json:"executable,omitempty"`
	Repository string `json:"repository,omitempty"`
	HomePage   string `json:"home_page,omitempty"`

	// Configuration
	Settings     map[string]interface{} `json:"settings,omitempty"`
	ConfigSchema map[string]interface{} `json:"config_schema,omitempty"`
	StreamMaps   map[string]interface{} `json:"stream_maps,omitempty"`

	// Capabilities
	Capabilities      []string `json:"capabilities,omitempty"`
	SupportedFeatures []string `json:"supported_features,omitempty"`

	// Metadata
	Author  string   `json:"author,omitempty"`
	License string   `json:"license,omitempty"`
	Tags    []string `json:"tags,omitempty"`

	// Installation info
	InstallationPath string   `json:"installation_path,omitempty"`
	PythonVersion    string   `json:"python_version,omitempty"`
	Dependencies     []string `json:"dependencies,omitempty"`

	// Usage tracking
	LastUsed          *time.Time `json:"last_used,omitempty"`
	UsageCount        int        `json:"usage_count"`
	LastSuccessfulRun *time.Time `json:"last_successful_run,omitempty"`
	LastFailedRun     *time.Time `json:"last_failed_run,omitempty"`
}

// NewTap cria um novo tap
func NewTap(name, displayName, description string, tapType TapType) *Tap {
	return &Tap{
		BaseEntity: *entities.NewBaseEntity(),
		Name:              name,
		DisplayName:       displayName,
		Description:       description,
		Type:              tapType,
		Status:            TapStatusNotInstalled,
		Settings:          make(map[string]interface{}),
		ConfigSchema:      make(map[string]interface{}),
		StreamMaps:        make(map[string]interface{}),
		Capabilities:      []string{},
		SupportedFeatures: []string{},
		Tags:              []string{},
		Dependencies:      []string{},
		UsageCount:        0,
	}
}

// Install marca o tap como instalado
func (t *Tap) Install(version, installationPath string) error {
	if t.Status == TapStatusInstalled {
		return &TapError{
			Code:    "TAP_ALREADY_INSTALLED",
			Message: "Tap is already installed",
			TapName: t.Name,
		}
	}

	t.Status = TapStatusInstalled
	t.TapVersion = version
	t.InstallationPath = installationPath
	t.UpdateTimestamp()

	return nil
}

// Uninstall remove o tap
func (t *Tap) Uninstall() error {
	if t.Status == TapStatusNotInstalled {
		return &TapError{
			Code:    "TAP_NOT_INSTALLED",
			Message: "Tap is not installed",
			TapName: t.Name,
		}
	}

	t.Status = TapStatusNotInstalled
	t.TapVersion = ""
	t.InstallationPath = ""
	t.UpdateTimestamp()

	return nil
}

// UpdateConfiguration atualiza a configuracao do tap
func (t *Tap) UpdateConfiguration(settings map[string]interface{}) error {
	if settings == nil {
		return &TapError{
			Code:    "INVALID_CONFIGURATION",
			Message: "Configuration cannot be nil",
			TapName: t.Name,
		}
	}

	t.Settings = settings
	t.UpdateTimestamp()

	return nil
}

// RecordUsage registra uso do tap
func (t *Tap) RecordUsage(successful bool) {
	now := time.Now().UTC()
	t.LastUsed = &now
	t.UsageCount++

	if successful {
		t.LastSuccessfulRun = &now
	} else {
		t.LastFailedRun = &now
	}

	t.UpdateTimestamp()
}

// IsInstalled verifica se o tap esta instalado
func (t *Tap) IsInstalled() bool {
	return t.Status == TapStatusInstalled
}

// CanExecute verifica se o tap pode ser executado
func (t *Tap) CanExecute() error {
	if !t.IsInstalled() {
		return &TapError{
			Code:    "TAP_NOT_INSTALLED",
			Message: "Tap must be installed before execution",
			TapName: t.Name,
		}
	}

	if t.Status == TapStatusFailed {
		return &TapError{
			Code:    "TAP_IN_FAILED_STATE",
			Message: "Tap is in failed state and cannot be executed",
			TapName: t.Name,
		}
	}

	if t.Status == TapStatusUpdating {
		return &TapError{
			Code:    "TAP_UPDATING",
			Message: "Tap is currently updating and cannot be executed",
			TapName: t.Name,
		}
	}

	return nil
}

// Validate valida o tap
func (t *Tap) Validate() error {
	if t.Name == "" {
		return &TapError{
			Code:    "INVALID_TAP",
			Message: "Tap name is required",
			TapName: t.Name,
		}
	}

	if len(t.Name) < 3 || len(t.Name) > 100 {
		return &TapError{
			Code:    "INVALID_TAP",
			Message: "Tap name must be between 3 and 100 characters",
			TapName: t.Name,
		}
	}

	if t.Type == "" {
		return &TapError{
			Code:    "INVALID_TAP",
			Message: "Tap type is required",
			TapName: t.Name,
		}
	}

	validTypes := []TapType{TapTypeExtractor, TapTypeLoader, TapTypeUtility}
	isValidType := false
	for _, validType := range validTypes {
		if t.Type == validType {
			isValidType = true
			break
		}
	}

	if !isValidType {
		return &TapError{
			Code:    "INVALID_TAP",
			Message: "Invalid tap type",
			TapName: t.Name,
		}
	}

	return nil
}

// UpdateTimestamp atualiza o timestamp
func (t *Tap) UpdateTimestamp() {
	t.SetUpdatedAt(time.Now().UTC())
	t.IncrementVersion()
}

// TapError representa um erro especifico de tap
type TapError struct {
	Code    string
	Message string
	TapName string
}

func (e *TapError) Error() string {
	if e.TapName != "" {
		return e.Message + " (tap: " + e.TapName + ")"
	}
	return e.Message
}
