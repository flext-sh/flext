package entities

import (
	"encoding/json"
	"fmt"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
)

// SingerSpec representa uma especificação Singer/Meltano
type SingerSpec struct {
	domain.AggregateRoot

	// Metadados básicos
	Name         string             `json:"name" validate:"required,min=1,max=100"`
	Version      string             `json:"version" validate:"required,semver"`
	Type         SingerType         `json:"type" validate:"required,oneof=tap target"`
	Description  string             `json:"description" validate:"max=500"`
	Author       string             `json:"author" validate:"max=100"`
	Settings     SingerSettings     `json:"settings"`
	Capabilities SingerCapabilities `json:"capabilities"`

	// Estado
	IsActive bool     `json:"is_active"`
	Schema   *Schema  `json:"schema,omitempty"`
	Catalog  *Catalog `json:"catalog,omitempty"`
	State    *State   `json:"state,omitempty"`

	// Configuração de execução
	Executable      string                 `json:"executable" validate:"required"`
	ConfigTemplate  map[string]interface{} `json:"config_template"`
	EnvironmentVars map[string]string      `json:"environment_vars"`
}

// SingerType define os tipos de especificação Singer
type SingerType string

const (
	SingerTypeTap    SingerType = "tap"
	SingerTypeTarget SingerType = "target"
)

// SingerSettings define as configurações de uma especificação Singer
type SingerSettings struct {
	Properties map[string]SettingProperty `json:"properties"`
	Required   []string                   `json:"required"`
}

// SettingProperty define uma propriedade de configuração
type SettingProperty struct {
	Type        string      `json:"type" validate:"required,oneof=string integer number boolean array object"`
	Description string      `json:"description" validate:"max=500"`
	Default     interface{} `json:"default,omitempty"`
	Enum        []string    `json:"enum,omitempty"`
	Format      string      `json:"format,omitempty"`
	Minimum     *float64    `json:"minimum,omitempty"`
	Maximum     *float64    `json:"maximum,omitempty"`
	Secret      bool        `json:"secret,omitempty"`
}

// SingerCapabilities define as capacidades de uma especificação Singer
type SingerCapabilities struct {
	Discovery          bool     `json:"discovery"`
	Properties         bool     `json:"properties"`
	Catalog            bool     `json:"catalog"`
	State              bool     `json:"state"`
	TestConnection     bool     `json:"test_connection"`
	AboutInfo          bool     `json:"about_info"`
	StreamMaps         bool     `json:"stream_maps"`
	SchemaFlattening   bool     `json:"schema_flattening"`
	SupportedFormats   []string `json:"supported_formats"`
	SupportedProtocols []string `json:"supported_protocols"`
}

// Schema representa o schema de dados de um tap Singer
type Schema struct {
	Type       string                 `json:"type"`
	Properties map[string]interface{} `json:"properties"`
}

// Catalog representa o catálogo de streams de um tap Singer
type Catalog struct {
	Streams []CatalogStream `json:"streams"`
}

// CatalogStream representa um stream no catálogo
// CatalogStream and StreamMetadata moved to singer_types.go

// Types moved to singer_types.go to avoid duplicates

// NewSingerSpec cria uma nova especificação Singer
func NewSingerSpec(name, version string, singerType SingerType, executable string) (*SingerSpec, error) {
	if name == "" {
		return nil, fmt.Errorf("singer spec name cannot be empty")
	}
	if version == "" {
		return nil, fmt.Errorf("singer spec version cannot be empty")
	}
	if executable == "" {
		return nil, fmt.Errorf("singer spec executable cannot be empty")
	}
	if singerType != SingerTypeTap && singerType != SingerTypeTarget {
		return nil, fmt.Errorf("invalid singer type: %s", singerType)
	}

	spec := &SingerSpec{
		AggregateRoot: domain.NewAggregateRoot(),
		Name:          name,
		Version:       version,
		Type:          singerType,
		Executable:    executable,
		IsActive:      true,
		Settings: SingerSettings{
			Properties: make(map[string]SettingProperty),
			Required:   []string{},
		},
		Capabilities: SingerCapabilities{
			SupportedFormats:   []string{"jsonl"},
			SupportedProtocols: []string{"singer"},
		},
		ConfigTemplate:  make(map[string]interface{}),
		EnvironmentVars: make(map[string]string),
	}

	// Emitir evento de criação
	spec.AddEvent(&SingerSpecCreated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.spec.created", spec.GetID()),
		SpecID:          spec.GetID(),
		Name:            name,
		Type:            string(singerType),
		Version:         version,
	})

	return spec, nil
}

// UpdateSettings atualiza as configurações da especificação
func (s *SingerSpec) UpdateSettings(settings SingerSettings) error {
	s.Settings = settings
	s.MarkAsUpdated()

	// Emitir evento de atualização
	s.AddEvent(&SingerSpecUpdated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.spec.updated", s.GetID()),
		SpecID:          s.GetID(),
		Name:            s.Name,
	})

	return nil
}

// UpdateCapabilities atualiza as capacidades da especificação
func (s *SingerSpec) UpdateCapabilities(capabilities SingerCapabilities) error {
	s.Capabilities = capabilities
	s.MarkAsUpdated()

	// Emitir evento de atualização
	s.AddEvent(&SingerSpecUpdated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.spec.updated", s.GetID()),
		SpecID:          s.GetID(),
		Name:            s.Name,
	})

	return nil
}

// SetSchema define o schema da especificação (para taps)
func (s *SingerSpec) SetSchema(schema *Schema) error {
	if s.Type != SingerTypeTap {
		return fmt.Errorf("schema can only be set for tap specifications")
	}

	s.Schema = schema
	s.MarkAsUpdated()

	return nil
}

// SetCatalog define o catálogo da especificação (para taps)
func (s *SingerSpec) SetCatalog(catalog *Catalog) error {
	if s.Type != SingerTypeTap {
		return fmt.Errorf("catalog can only be set for tap specifications")
	}

	s.Catalog = catalog
	s.MarkAsUpdated()

	return nil
}

// UpdateState atualiza o estado da especificação (para taps)
func (s *SingerSpec) UpdateState(state *State) error {
	if s.Type != SingerTypeTap {
		return fmt.Errorf("state can only be updated for tap specifications")
	}

	s.State = state
	s.MarkAsUpdated()

	// Emitir evento de estado atualizado
	s.AddEvent(&SingerStateUpdated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.state.updated", s.GetID()),
		SpecID:          s.GetID(),
		Name:            s.Name,
	})

	return nil
}

// Activate ativa a especificação
func (s *SingerSpec) Activate() error {
	if s.IsActive {
		return fmt.Errorf("singer spec is already active")
	}

	s.IsActive = true
	s.MarkAsUpdated()

	// Emitir evento de ativação
	s.AddEvent(&SingerSpecActivated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.spec.activated", s.GetID()),
		SpecID:          s.GetID(),
		Name:            s.Name,
	})

	return nil
}

// Deactivate desativa a especificação
func (s *SingerSpec) Deactivate() error {
	if !s.IsActive {
		return fmt.Errorf("singer spec is already inactive")
	}

	s.IsActive = false
	s.MarkAsUpdated()

	// Emitir evento de desativação
	s.AddEvent(&SingerSpecDeactivated{
		BaseDomainEvent: domain.NewBaseDomainEvent("singer.spec.deactivated", s.GetID()),
		SpecID:          s.GetID(),
		Name:            s.Name,
	})

	return nil
}

// ValidateConfig valida uma configuração contra as settings da especificação
func (s *SingerSpec) ValidateConfig(config map[string]interface{}) error {
	// Verificar propriedades obrigatórias
	for _, required := range s.Settings.Required {
		if _, exists := config[required]; !exists {
			return fmt.Errorf("required property '%s' is missing", required)
		}
	}

	// Validar tipos e valores das propriedades
	for key, value := range config {
		property, exists := s.Settings.Properties[key]
		if !exists {
			continue // Propriedade não definida, mas permitida
		}

		if err := s.validatePropertyValue(key, value, property); err != nil {
			return err
		}
	}

	return nil
}

func (s *SingerSpec) validatePropertyValue(key string, value interface{}, property SettingProperty) error {
	// Validação básica de tipo
	switch property.Type {
	case "string":
		if _, ok := value.(string); !ok {
			return fmt.Errorf("property '%s' must be a string", key)
		}
	case "integer":
		if _, ok := value.(int); !ok {
			if _, ok := value.(float64); !ok {
				return fmt.Errorf("property '%s' must be an integer", key)
			}
		}
	case "number":
		if _, ok := value.(float64); !ok {
			if _, ok := value.(int); !ok {
				return fmt.Errorf("property '%s' must be a number", key)
			}
		}
	case "boolean":
		if _, ok := value.(bool); !ok {
			return fmt.Errorf("property '%s' must be a boolean", key)
		}
	}

	// Validação de enum se definido
	if len(property.Enum) > 0 {
		valueStr := fmt.Sprintf("%v", value)
		for _, enumValue := range property.Enum {
			if enumValue == valueStr {
				return nil
			}
		}
		return fmt.Errorf("property '%s' must be one of: %v", key, property.Enum)
	}

	return nil
}

// ToJSON converte a especificação para JSON
func (s *SingerSpec) ToJSON() ([]byte, error) {
	return json.MarshalIndent(s, "", "  ")
}

// FromJSON cria uma especificação a partir de JSON
func FromJSON(data []byte) (*SingerSpec, error) {
	var spec SingerSpec
	if err := json.Unmarshal(data, &spec); err != nil {
		return nil, err
	}
	return &spec, nil
}
