package entities

import (
	"time"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/value_objects"
)

// QueryBuilder interface defines query building capabilities
type QueryBuilder interface {
	// Basic filtering
	Where(field string, operator value_objects.FilterOperator, value interface{}) QueryBuilder
	WhereDate(field string, operator value_objects.FilterOperator, date time.Time) QueryBuilder
	WhereDateRange(field string, start, end time.Time) QueryBuilder
	WhereIncremental(replicationKey string, bookmark interface{}, safetyOverlap time.Duration) QueryBuilder
	
	// Ordering
	OrderBy(field string, direction string) QueryBuilder
	OrderByAsc(field string) QueryBuilder
	OrderByDesc(field string) QueryBuilder
	
	// Field selection
	Select(fields ...string) QueryBuilder
	
	// Pagination
	Limit(limit int) QueryBuilder
	Offset(offset int64) QueryBuilder
	Page(page, pageSize int) QueryBuilder
	Cursor(cursor string) QueryBuilder
	
	// Query building
	Build() (string, error)
	BuildURL(baseURL string) (string, error)
	
	// Introspection
	GetFilters() map[string]interface{}
	GetOrdering() []interface{} // Generic interface for ordering clauses
	
	// Utility
	Clone() QueryBuilder
	Reset() QueryBuilder
	Validate() error
}

// QueryBuilderFactory creates query builders for entities
type QueryBuilderFactory interface {
	CreateQueryBuilder(entity *WMSEntity) QueryBuilder
}