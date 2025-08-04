package entities

import (
	"time"

	"github.com/google/uuid"
)

// Pipeline representa uma entidade de pipeline no domínio do FLEXT Control Panel
type Pipeline struct {
	ID            uuid.UUID `json:"id"`
	Name          string    `json:"name"`
	Description   string    `json:"description"`
	IsActive      bool      `json:"is_active"`
	Tags          []string  `json:"tags"`
	Configuration string    `json:"configuration"`
	Schedule      string    `json:"schedule"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}

// NewPipeline cria uma nova instância de Pipeline
func NewPipeline(name, description string) *Pipeline {
	now := time.Now()
	return &Pipeline{
		ID:          uuid.New(),
		Name:        name,
		Description: description,
		IsActive:    true,
		Tags:        []string{},
		CreatedAt:   now,
		UpdatedAt:   now,
	}
}

// Activate ativa o pipeline
func (p *Pipeline) Activate() {
	p.IsActive = true
	p.UpdatedAt = time.Now()
}

// Deactivate desativa o pipeline
func (p *Pipeline) Deactivate() {
	p.IsActive = false
	p.UpdatedAt = time.Now()
}

// AddTag adiciona uma tag ao pipeline
func (p *Pipeline) AddTag(tag string) {
	for _, existingTag := range p.Tags {
		if existingTag == tag {
			return
		}
	}
	p.Tags = append(p.Tags, tag)
	p.UpdatedAt = time.Now()
}

// RemoveTag remove uma tag do pipeline
func (p *Pipeline) RemoveTag(tag string) {
	for i, existingTag := range p.Tags {
		if existingTag == tag {
			p.Tags = append(p.Tags[:i], p.Tags[i+1:]...)
			p.UpdatedAt = time.Now()
			return
		}
	}
}

// UpdateConfiguration atualiza a configuração do pipeline
func (p *Pipeline) UpdateConfiguration(config string) {
	p.Configuration = config
	p.UpdatedAt = time.Now()
}

// UpdateSchedule atualiza o agendamento do pipeline
func (p *Pipeline) UpdateSchedule(schedule string) {
	p.Schedule = schedule
	p.UpdatedAt = time.Now()
}
