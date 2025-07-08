package entities

import (
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// SingerSpecCreated evento emitido quando uma especificação Singer é criada
type SingerSpecCreated struct {
	domain.BaseDomainEvent
	SpecID  uuid.UUID `json:"spec_id"`
	Name    string    `json:"name"`
	Type    string    `json:"type"`
	Version string    `json:"version"`
}

// SingerSpecUpdated evento emitido quando uma especificação Singer é atualizada
type SingerSpecUpdated struct {
	domain.BaseDomainEvent
	SpecID uuid.UUID `json:"spec_id"`
	Name   string    `json:"name"`
}

// SingerSpecActivated evento emitido quando uma especificação Singer é ativada
type SingerSpecActivated struct {
	domain.BaseDomainEvent
	SpecID uuid.UUID `json:"spec_id"`
	Name   string    `json:"name"`
}

// SingerSpecDeactivated evento emitido quando uma especificação Singer é desativada
type SingerSpecDeactivated struct {
	domain.BaseDomainEvent
	SpecID uuid.UUID `json:"spec_id"`
	Name   string    `json:"name"`
}

// SingerStateUpdated evento emitido quando o estado de uma especificação Singer é atualizado
type SingerStateUpdated struct {
	domain.BaseDomainEvent
	SpecID uuid.UUID `json:"spec_id"`
	Name   string    `json:"name"`
}

// SingerExecutionStarted evento emitido quando uma execução Singer inicia
type SingerExecutionStarted struct {
	domain.BaseDomainEvent
	ExecutionID uuid.UUID `json:"execution_id"`
	SpecID      uuid.UUID `json:"spec_id"`
	SpecName    string    `json:"spec_name"`
	SpecType    string    `json:"spec_type"`
}

// SingerExecutionCompleted evento emitido quando uma execução Singer completa
type SingerExecutionCompleted struct {
	domain.BaseDomainEvent
	ExecutionID  uuid.UUID `json:"execution_id"`
	SpecID       uuid.UUID `json:"spec_id"`
	SpecName     string    `json:"spec_name"`
	RecordsCount int64     `json:"records_count"`
	DurationMs   int64     `json:"duration_ms"`
	Success      bool      `json:"success"`
	ErrorMessage string    `json:"error_message,omitempty"`
}

// SingerRecordProcessed evento emitido quando um registro Singer é processado
type SingerRecordProcessed struct {
	domain.BaseDomainEvent
	ExecutionID uuid.UUID `json:"execution_id"`
	SpecID      uuid.UUID `json:"spec_id"`
	StreamName  string    `json:"stream_name"`
	RecordType  string    `json:"record_type"` // RECORD, SCHEMA, STATE
	RecordData  string    `json:"record_data"`
}

// SingerSchemaDetected evento emitido quando um schema Singer é detectado
type SingerSchemaDetected struct {
	domain.BaseDomainEvent
	ExecutionID uuid.UUID `json:"execution_id"`
	SpecID      uuid.UUID `json:"spec_id"`
	StreamName  string    `json:"stream_name"`
	SchemaData  string    `json:"schema_data"`
}
