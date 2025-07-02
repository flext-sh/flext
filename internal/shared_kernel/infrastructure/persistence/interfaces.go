package persistence

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// BaseRepositoryInterface defines common repository operations
type BaseRepositoryInterface[T Entity] interface {
	// Create operations
	Create(ctx context.Context, entity T) (T, error)
	CreateBatch(ctx context.Context, entities []T) ([]T, error)

	// Read operations
	GetByID(ctx context.Context, id uuid.UUID) (T, error)
	FindByID(ctx context.Context, id uuid.UUID) (T, error) // Returns nil if not found
	List(ctx context.Context, criteria ListCriteria) ([]T, int, error)
	Exists(ctx context.Context, id uuid.UUID) (bool, error)

	// Update operations
	Update(ctx context.Context, entity T) (T, error)
	UpdatePartial(ctx context.Context, id uuid.UUID, updates map[string]interface{}) (T, error)
	UpdateBatch(ctx context.Context, entities []T) ([]T, error)

	// Delete operations
	Delete(ctx context.Context, id uuid.UUID) error
	DeleteBatch(ctx context.Context, ids []uuid.UUID) error
	SoftDelete(ctx context.Context, id uuid.UUID) error

	// Utility operations
	Count(ctx context.Context, criteria CountCriteria) (int, error)
	Health(ctx context.Context) error
}

// Entity represents a domain entity with common fields
type Entity interface {
	GetID() uuid.UUID
	GetCreatedAt() time.Time
	GetUpdatedAt() time.Time
	IsDeleted() bool
}

// ListCriteria defines criteria for listing entities
type ListCriteria struct {
	// Pagination
	Limit  int `json:"limit"`
	Offset int `json:"offset"`

	// Sorting
	OrderBy   string `json:"order_by"`
	OrderDir  string `json:"order_dir"` // "asc" or "desc"
	SortBy    string `json:"sort_by"`
	SortOrder string `json:"sort_order"`

	// Filtering
	Filters    []Filter               `json:"filters"`
	Search     string                 `json:"search"`
	Tags       []string               `json:"tags"`
	Status     string                 `json:"status"`
	Active     *bool                  `json:"active,omitempty"`
	Metadata   map[string]interface{} `json:"metadata"`

	// Time-based filtering
	CreatedAfter  *time.Time `json:"created_after,omitempty"`
	CreatedBefore *time.Time `json:"created_before,omitempty"`
	UpdatedAfter  *time.Time `json:"updated_after,omitempty"`
	UpdatedBefore *time.Time `json:"updated_before,omitempty"`

	// Soft delete handling
	IncludeDeleted bool `json:"include_deleted"`
	OnlyDeleted    bool `json:"only_deleted"`
}

// CountCriteria defines criteria for counting entities
type CountCriteria struct {
	Filters        []Filter               `json:"filters"`
	Search         string                 `json:"search"`
	Tags           []string               `json:"tags"`
	Status         string                 `json:"status"`
	Active         *bool                  `json:"active,omitempty"`
	Metadata       map[string]interface{} `json:"metadata"`
	IncludeDeleted bool                   `json:"include_deleted"`
}

// Filter represents a single filter criterion
type Filter struct {
	Field    string      `json:"field"`
	Operator string      `json:"operator"` // eq, ne, gt, gte, lt, lte, in, nin, like, ilike
	Value    interface{} `json:"value"`
}

// TransactionalRepository adds transaction support
type TransactionalRepository interface {
	WithTransaction(ctx context.Context, fn func(ctx context.Context) error) error
	BeginTransaction(ctx context.Context) (TransactionContext, error)
	CommitTransaction(ctx TransactionContext) error
	RollbackTransaction(ctx TransactionContext) error
}

// TransactionContext represents a database transaction context
type TransactionContext interface {
	Context() context.Context
	IsCommitted() bool
	IsRollbacked() bool
}

// RepositoryMetrics provides repository performance metrics
type RepositoryMetrics struct {
	TotalOperations    int64         `json:"total_operations"`
	SuccessfulOps      int64         `json:"successful_operations"`
	FailedOps          int64         `json:"failed_operations"`
	AverageLatency     time.Duration `json:"average_latency"`
	LastOperationTime  time.Time     `json:"last_operation_time"`
	ConnectionPoolSize int           `json:"connection_pool_size"`
	ActiveConnections  int           `json:"active_connections"`
}

// MetricsRepository adds metrics collection capabilities
type MetricsRepository interface {
	GetMetrics(ctx context.Context) (*RepositoryMetrics, error)
	ResetMetrics(ctx context.Context) error
}

// CacheableRepository adds caching capabilities
type CacheableRepository interface {
	ClearCache(ctx context.Context) error
	ClearCacheForEntity(ctx context.Context, id uuid.UUID) error
	GetCacheStats(ctx context.Context) (*CacheStats, error)
}

// CacheStats represents cache performance statistics
type CacheStats struct {
	HitCount      int64   `json:"hit_count"`
	MissCount     int64   `json:"miss_count"`
	HitRatio      float64 `json:"hit_ratio"`
	Size          int     `json:"size"`
	MaxSize       int     `json:"max_size"`
	Evictions     int64   `json:"evictions"`
	LastEviction  time.Time `json:"last_eviction"`
}

// ValidatedRepository adds validation capabilities
type ValidatedRepository[T Entity] interface {
	BaseRepository[T]
	ValidateEntity(ctx context.Context, entity T) error
	ValidateID(ctx context.Context, id uuid.UUID) error
}

// AuditableRepository adds audit trail capabilities
type AuditableRepository interface {
	GetAuditTrail(ctx context.Context, entityID uuid.UUID) ([]AuditEntry, error)
	RecordAudit(ctx context.Context, entry AuditEntry) error
}

// AuditEntry represents an audit trail entry
type AuditEntry struct {
	ID        uuid.UUID              `json:"id"`
	EntityID  uuid.UUID              `json:"entity_id"`
	EntityType string                `json:"entity_type"`
	Operation string                 `json:"operation"` // create, update, delete
	UserID    uuid.UUID              `json:"user_id"`
	Username  string                 `json:"username"`
	Changes   map[string]interface{} `json:"changes"`
	Timestamp time.Time              `json:"timestamp"`
	IPAddress string                 `json:"ip_address"`
	UserAgent string                 `json:"user_agent"`
}

// VersionedRepository adds versioning capabilities
type VersionedRepository[T Entity] interface {
	BaseRepository[T]
	GetVersion(ctx context.Context, id uuid.UUID, version int) (T, error)
	GetVersionHistory(ctx context.Context, id uuid.UUID) ([]T, error)
	CreateVersion(ctx context.Context, entity T) (T, error)
}

// SearchableRepository adds full-text search capabilities
type SearchableRepository[T Entity] interface {
	BaseRepository[T]
	Search(ctx context.Context, query SearchQuery) ([]T, int, error)
	IndexEntity(ctx context.Context, entity T) error
	ReindexAll(ctx context.Context) error
}

// SearchQuery represents a search query
type SearchQuery struct {
	Query       string            `json:"query"`
	Fields      []string          `json:"fields"`
	Filters     []Filter          `json:"filters"`
	Facets      []string          `json:"facets"`
	Highlight   bool              `json:"highlight"`
	Limit       int               `json:"limit"`
	Offset      int               `json:"offset"`
	SortBy      string            `json:"sort_by"`
	SortOrder   string            `json:"sort_order"`
	Suggestions bool              `json:"suggestions"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// RepositoryConfig provides common configuration for repositories
type RepositoryConfig struct {
	// Database configuration
	ConnectionString   string        `json:"connection_string"`
	MaxOpenConns      int           `json:"max_open_connections"`
	MaxIdleConns      int           `json:"max_idle_connections"`
	ConnMaxLifetime   time.Duration `json:"connection_max_lifetime"`
	ConnMaxIdleTime   time.Duration `json:"connection_max_idle_time"`

	// Performance configuration
	EnableCache       bool          `json:"enable_cache"`
	CacheSize         int           `json:"cache_size"`
	CacheTTL          time.Duration `json:"cache_ttl"`
	EnableMetrics     bool          `json:"enable_metrics"`
	EnableAudit       bool          `json:"enable_audit"`
	EnableVersioning  bool          `json:"enable_versioning"`

	// Query configuration
	DefaultLimit      int    `json:"default_limit"`
	MaxLimit          int    `json:"max_limit"`
	DefaultOrderBy    string `json:"default_order_by"`
	DefaultOrderDir   string `json:"default_order_direction"`

	// Timeout configuration
	QueryTimeout      time.Duration `json:"query_timeout"`
	TransactionTimeout time.Duration `json:"transaction_timeout"`
}

// RepositoryFactory creates repository instances
type RepositoryFactory interface {
	CreatePipelineRepository(config RepositoryConfig) (interface{}, error)
	CreatePluginRepository(config RepositoryConfig) (interface{}, error)
	CreateUserRepository(config RepositoryConfig) (interface{}, error)
	CreateExecutionRepository(config RepositoryConfig) (interface{}, error)
}

// Common repository interfaces for specific entities

// PipelineRepository interface for pipeline operations
type PipelineRepository interface {
	BaseRepositoryInterface[PipelineEntity]
	TransactionalRepository
	ValidatedRepository[PipelineEntity]
	CacheableRepository

	// Pipeline-specific operations
	FindByName(ctx context.Context, name string) (PipelineEntity, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
	FindByStatus(ctx context.Context, status string) ([]PipelineEntity, error)
	FindByTags(ctx context.Context, tags []string) ([]PipelineEntity, error)
	AddStep(ctx context.Context, pipelineID uuid.UUID, step StepEntity) error
	RemoveStep(ctx context.Context, pipelineID uuid.UUID, stepID uuid.UUID) error
	UpdateStepOrder(ctx context.Context, pipelineID uuid.UUID, stepOrders map[uuid.UUID]int) error
}

// PluginRepository interface for plugin operations
type PluginRepository interface {
	BaseRepositoryInterface[PluginEntity]
	TransactionalRepository
	ValidatedRepository[PluginEntity]
	CacheableRepository

	// Plugin-specific operations
	FindByName(ctx context.Context, name string) (PluginEntity, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
	FindByType(ctx context.Context, pluginType string) ([]PluginEntity, error)
	FindByVersion(ctx context.Context, name, version string) (PluginEntity, error)
	ListVersions(ctx context.Context, name string) ([]string, error)
	FindActive(ctx context.Context) ([]PluginEntity, error)
}

// UserRepository interface for user operations
type UserRepository interface {
	BaseRepositoryInterface[UserEntity]
	TransactionalRepository
	ValidatedRepository[UserEntity]

	// User-specific operations
	FindByUsername(ctx context.Context, username string) (UserEntity, error)
	FindByEmail(ctx context.Context, email string) (UserEntity, error)
	ExistsByUsername(ctx context.Context, username string) (bool, error)
	ExistsByEmail(ctx context.Context, email string) (bool, error)
	FindByRole(ctx context.Context, role string) ([]UserEntity, error)
	UpdateLastLogin(ctx context.Context, userID uuid.UUID) error
}

// ExecutionRepository interface for execution operations
type ExecutionRepository interface {
	BaseRepositoryInterface[ExecutionEntity]
	TransactionalRepository
	MetricsRepository

	// Execution-specific operations
	FindByPipelineID(ctx context.Context, pipelineID uuid.UUID) ([]ExecutionEntity, error)
	FindByStatus(ctx context.Context, status string) ([]ExecutionEntity, error)
	FindRunning(ctx context.Context) ([]ExecutionEntity, error)
	UpdateStatus(ctx context.Context, executionID uuid.UUID, status string) error
	RecordMetric(ctx context.Context, executionID uuid.UUID, metric ExecutionMetric) error
}

// Entity interfaces for type safety

// PipelineEntity represents pipeline entities
type PipelineEntity interface {
	Entity
	GetName() string
	GetDescription() string
	GetType() string
	GetStatus() string
	GetTags() []string
	IsActive() bool
}

// PluginEntity represents plugin entities  
type PluginEntity interface {
	Entity
	GetName() string
	GetType() string
	GetVersion() string
	GetStatus() string
	IsActive() bool
}

// UserEntity represents user entities
type UserEntity interface {
	Entity
	GetUsername() string
	GetEmail() string
	GetRoles() []string
	IsActive() bool
}

// ExecutionEntity represents execution entities
type ExecutionEntity interface {
	Entity
	GetPipelineID() uuid.UUID
	GetStatus() string
	GetStartedAt() time.Time
	GetCompletedAt() *time.Time
}

// StepEntity represents pipeline step entities
type StepEntity interface {
	Entity
	GetPipelineID() uuid.UUID
	GetPluginID() uuid.UUID
	GetName() string
	GetOrder() int
}

// ExecutionMetric represents execution performance metrics
type ExecutionMetric struct {
	MetricType string                 `json:"metric_type"`
	Value      float64                `json:"value"`
	Unit       string                 `json:"unit"`
	Timestamp  time.Time              `json:"timestamp"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// Repository error types
var (
	ErrEntityNotFound    = &value_objects.DomainError{Code: "ENTITY_NOT_FOUND", Message: "Entity not found"}
	ErrEntityExists      = &value_objects.DomainError{Code: "ENTITY_EXISTS", Message: "Entity already exists"}
	ErrInvalidInput      = &value_objects.DomainError{Code: "INVALID_INPUT", Message: "Invalid input provided"}
	ErrTransactionFailed = &value_objects.DomainError{Code: "TRANSACTION_FAILED", Message: "Transaction failed"}
	ErrConnectionFailed  = &value_objects.DomainError{Code: "CONNECTION_FAILED", Message: "Database connection failed"}
	ErrQueryTimeout      = &value_objects.DomainError{Code: "QUERY_TIMEOUT", Message: "Query execution timeout"}
)