package queries

import (
	"time"

	"github.com/google/uuid"
)

// PipelineDTO representa um pipeline para transferência de dados
type PipelineDTO struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	IsActive      bool                   `json:"is_active"`
	Steps         []PipelineStepDTO      `json:"steps"`
	Tags          []string               `json:"tags"`
	Configuration map[string]interface{} `json:"configuration"`
	Schedule      *PipelineScheduleDTO   `json:"schedule,omitempty"`
	CreatedAt     time.Time              `json:"created_at"`
	UpdatedAt     time.Time              `json:"updated_at"`
	Version       int                    `json:"version"`
}

// PipelineStepDTO representa um step de pipeline para transferência de dados
type PipelineStepDTO struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	PluginID      uuid.UUID              `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
}

// PipelineScheduleDTO representa um schedule de pipeline para transferência de dados
type PipelineScheduleDTO struct {
	CronExpression string                 `json:"cron_expression"`
	Timezone       string                 `json:"timezone"`
	IsActive       bool                   `json:"is_active"`
	NextRun        *time.Time             `json:"next_run,omitempty"`
	LastRun        *time.Time             `json:"last_run,omitempty"`
	Configuration  map[string]interface{} `json:"configuration"`
}
