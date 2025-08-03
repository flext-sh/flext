package entities

import (
	"time"
)

// SingerState represents Singer protocol state for incremental replication
type SingerState struct {
	Bookmarks map[string]interface{} `json:"bookmarks"`
	Currently string                 `json:"currently_syncing,omitempty"`
}

// State represents Singer spec state (legacy compatibility)
type State struct {
	Bookmarks map[string]StreamState `json:"bookmarks"`
}

// StreamState represents the state of a specific stream
type StreamState struct {
	ReplicationKeyValue interface{} `json:"replication_key_value,omitempty"`
	Version             int64       `json:"version,omitempty"`
	LastSyncTime        *time.Time  `json:"last_sync_time,omitempty"`
}

// ExecutionStatus defines the status of a Singer execution
type ExecutionStatus string

const (
	ExecutionStatusPending   ExecutionStatus = "pending"
	ExecutionStatusRunning   ExecutionStatus = "running"
	ExecutionStatusCompleted ExecutionStatus = "completed"
	ExecutionStatusFailed    ExecutionStatus = "failed"
	ExecutionStatusCanceled  ExecutionStatus = "canceled"
)

// SingerCatalog represents Singer protocol catalog
type SingerCatalog struct {
	Streams []CatalogStream `json:"streams"`
}

// CatalogStream represents a stream in Singer catalog
type CatalogStream struct {
	TapStreamID       string                 `json:"tap_stream_id"`
	Schema            map[string]interface{} `json:"schema"`
	Metadata          []StreamMetadata       `json:"metadata"`
	TableName         string                 `json:"table_name,omitempty"`
	StreamAlias       string                 `json:"stream_alias,omitempty"`
	KeyProperties     []string               `json:"key_properties,omitempty"`
	ReplicationKey    string                 `json:"replication_key,omitempty"`
	ReplicationMethod string                 `json:"replication_method,omitempty"`
}

// StreamMetadata represents metadata for a catalog stream
type StreamMetadata struct {
	BreadcrumbPath []string               `json:"breadcrumb"`
	Metadata       map[string]interface{} `json:"metadata"`
}

// SingerRecord represents a Singer protocol record
type SingerRecord struct {
	Type   string                 `json:"type"`
	Stream string                 `json:"stream"`
	Record map[string]interface{} `json:"record"`
	Time   *time.Time             `json:"time_extracted,omitempty"`
}

// SingerSchema represents a Singer protocol schema message
type SingerSchema struct {
	Type          string                 `json:"type"`
	Stream        string                 `json:"stream"`
	Schema        map[string]interface{} `json:"schema"`
	KeyProperties []string               `json:"key_properties"`
}

// SingerMessage represents a Singer protocol message
type SingerMessage struct {
	Type    string        `json:"type"`
	Record  *SingerRecord `json:"record,omitempty"`
	Schema  *SingerSchema `json:"schema,omitempty"`
	State   *SingerState  `json:"state,omitempty"`
	Version *int          `json:"version,omitempty"`
}
