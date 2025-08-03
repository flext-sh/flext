package database

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// GormPipeline GORM model for pipelines with advanced features
type GormPipeline struct {
	ID          uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	Name        string         `gorm:"uniqueIndex;not null" json:"name"`
	Description string         `gorm:"type:text" json:"description"`
	Status      string         `gorm:"not null;default:'draft'" json:"status"`
	Tags        []string       `gorm:"type:text[]" json:"tags"`
	Metadata    string         `gorm:"type:jsonb" json:"metadata"`
	CreatedAt   time.Time      `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt   time.Time      `gorm:"autoUpdateTime" json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
	CreatedBy   string         `gorm:"not null" json:"created_by"`
	Version     int            `gorm:"default:1" json:"version"`

	// Relationships
	Steps      []GormPipelineStep `gorm:"foreignKey:PipelineID;constraint:OnDelete:CASCADE" json:"steps,omitempty"`
	Executions []GormExecution    `gorm:"foreignKey:PipelineID;constraint:OnDelete:CASCADE" json:"executions,omitempty"`
}

// GormPipelineStep GORM model for pipeline steps
type GormPipelineStep struct {
	ID           uuid.UUID `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	PipelineID   uuid.UUID `gorm:"type:uuid;not null;index" json:"pipeline_id"`
	Name         string    `gorm:"not null" json:"name"`
	Type         string    `gorm:"not null" json:"type"`
	OrderIndex   int       `gorm:"not null" json:"order_index"`
	Config       string    `gorm:"type:jsonb" json:"config"`
	Dependencies []string  `gorm:"type:text[]" json:"dependencies"`
	CreatedAt    time.Time `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt    time.Time `gorm:"autoUpdateTime" json:"updated_at"`

	// Relationship
	Pipeline GormPipeline `gorm:"constraint:OnDelete:CASCADE" json:"-"`
}

// GormExecution GORM model for pipeline executions
type GormExecution struct {
	ID         uuid.UUID  `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	PipelineID uuid.UUID  `gorm:"type:uuid;not null;index" json:"pipeline_id"`
	Status     string     `gorm:"not null;default:'pending'" json:"status"`
	StartedAt  *time.Time `json:"started_at,omitempty"`
	FinishedAt *time.Time `json:"finished_at,omitempty"`
	Error      string     `gorm:"type:text" json:"error,omitempty"`
	Metadata   string     `gorm:"type:jsonb" json:"metadata"`
	CreatedAt  time.Time  `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt  time.Time  `gorm:"autoUpdateTime" json:"updated_at"`

	// Relationship
	Pipeline GormPipeline `gorm:"constraint:OnDelete:CASCADE" json:"-"`
}

// GormPlugin GORM model for plugins
type GormPlugin struct {
	ID          uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	Name        string         `gorm:"uniqueIndex;not null" json:"name"`
	Version     string         `gorm:"not null" json:"version"`
	Type        string         `gorm:"not null" json:"type"`
	Description string         `gorm:"type:text" json:"description"`
	Config      string         `gorm:"type:jsonb" json:"config"`
	Enabled     bool           `gorm:"default:true" json:"enabled"`
	CreatedAt   time.Time      `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt   time.Time      `gorm:"autoUpdateTime" json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
}

// TableName methods for custom table names
func (GormPipeline) TableName() string {
	return "pipelines"
}

func (GormPipelineStep) TableName() string {
	return "pipeline_steps"
}

func (GormExecution) TableName() string {
	return "pipeline_executions"
}

func (GormPlugin) TableName() string {
	return "plugins"
}

// BeforeCreate hooks
func (p *GormPipeline) BeforeCreate(tx *gorm.DB) error {
	if p.ID == uuid.Nil {
		p.ID = uuid.New()
	}
	return nil
}

func (s *GormPipelineStep) BeforeCreate(tx *gorm.DB) error {
	if s.ID == uuid.Nil {
		s.ID = uuid.New()
	}
	return nil
}

func (e *GormExecution) BeforeCreate(tx *gorm.DB) error {
	if e.ID == uuid.Nil {
		e.ID = uuid.New()
	}
	return nil
}

func (p *GormPlugin) BeforeCreate(tx *gorm.DB) error {
	if p.ID == uuid.Nil {
		p.ID = uuid.New()
	}
	return nil
}
