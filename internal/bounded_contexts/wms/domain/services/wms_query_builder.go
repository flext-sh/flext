package services

import (
	"fmt"
	"net/url"
	"strconv"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/value_objects"
)

// WMSQueryBuilder provides advanced query building for Oracle WMS APIs
type WMSQueryBuilder struct {
	entity    *entities.WMSEntity
	filters   map[string]interface{}
	ordering  []OrderClause
	pagination PaginationClause
	fields    []string
	joins     []JoinClause
}

// OrderClause represents an ordering specification
type OrderClause struct {
	Field     string `json:"field"`
	Direction string `json:"direction"` // "asc" or "desc"
	NullsLast bool   `json:"nulls_last"`
}

// PaginationClause represents pagination parameters
type PaginationClause struct {
	Mode       string      `json:"mode"`        // "cursor", "offset", "page"
	Limit      int         `json:"limit"`
	Offset     int64       `json:"offset"`
	Cursor     string      `json:"cursor"`
	Page       int         `json:"page"`
	PageSize   int         `json:"page_size"`
}

// JoinClause represents a join with another entity
type JoinClause struct {
	Entity    string `json:"entity"`
	Type      string `json:"type"`      // "inner", "left", "right"
	Condition string `json:"condition"`
	Alias     string `json:"alias"`
}


// FilterCondition represents a single filter condition
type FilterCondition struct {
	Field    string          `json:"field"`
	Operator value_objects.FilterOperator  `json:"operator"`
	Value    interface{}     `json:"value"`
	Values   []interface{}   `json:"values,omitempty"`  // For IN, NOT_IN operators
	
	// Date range specific
	StartDate *time.Time     `json:"start_date,omitempty"`
	EndDate   *time.Time     `json:"end_date,omitempty"`
	
	// Advanced options
	CaseSensitive bool       `json:"case_sensitive"`
	Negate        bool       `json:"negate"`
}

// LogicalOperator defines how conditions are combined
type LogicalOperator string

const (
	LogicalAnd LogicalOperator = "and"
	LogicalOr  LogicalOperator = "or"
	LogicalNot LogicalOperator = "not"
)

// FilterGroup represents a group of conditions with logical operators
type FilterGroup struct {
	Operator   LogicalOperator   `json:"operator"`
	Conditions []FilterCondition `json:"conditions"`
	Groups     []FilterGroup     `json:"groups"`
}

// NewWMSQueryBuilder creates a new query builder for an entity
func NewWMSQueryBuilder(entity *entities.WMSEntity) entities.QueryBuilder {
	return &WMSQueryBuilder{
		entity:  entity,
		filters: make(map[string]interface{}),
		ordering: []OrderClause{},
		fields:  []string{},
		joins:   []JoinClause{},
	}
}

// Where adds a simple filter condition
func (qb *WMSQueryBuilder) Where(field string, operator value_objects.FilterOperator, value interface{}) entities.QueryBuilder {
	switch operator {
	case value_objects.OpEquals:
		qb.filters[field] = value
	case value_objects.OpNotEquals:
		qb.filters[field+"__ne"] = value
	case value_objects.OpGreaterThan:
		qb.filters[field+"__gt"] = value
	case value_objects.OpGreaterThanOrEqual:
		qb.filters[field+"__gte"] = value
	case value_objects.OpLessThan:
		qb.filters[field+"__lt"] = value
	case value_objects.OpLessThanOrEqual:
		qb.filters[field+"__lte"] = value
	case value_objects.OpLike:
		qb.filters[field+"__like"] = value
	case value_objects.OpILike:
		qb.filters[field+"__ilike"] = value
	case value_objects.OpStartsWith:
		qb.filters[field+"__startswith"] = value
	case value_objects.OpEndsWith:
		qb.filters[field+"__endswith"] = value
	case value_objects.OpContains:
		qb.filters[field+"__contains"] = value
	case value_objects.OpIn:
		qb.filters[field+"__in"] = value
	case value_objects.OpNotIn:
		qb.filters[field+"__not_in"] = value
	case value_objects.OpIsNull:
		qb.filters[field+"__isnull"] = "true"
	case value_objects.OpIsNotNull:
		qb.filters[field+"__isnull"] = "false"
	case value_objects.OpBetween:
		// Expect value to be []interface{}{min, max}
		if values, ok := value.([]interface{}); ok && len(values) == 2 {
			qb.filters[field+"__gte"] = values[0]
			qb.filters[field+"__lte"] = values[1]
		}
	}
	
	return qb
}

// WhereAdvanced adds an advanced filter condition
func (qb *WMSQueryBuilder) WhereAdvanced(condition FilterCondition) entities.QueryBuilder {
	return qb.Where(condition.Field, condition.Operator, condition.Value)
}

// WhereGroup adds a group of conditions with logical operators
func (qb *WMSQueryBuilder) WhereGroup(group FilterGroup) entities.QueryBuilder {
	// Convert group to simple filters for Oracle WMS API compatibility
	// This is a simplified implementation - a full version would support complex logical operations
	for _, condition := range group.Conditions {
		qb.WhereAdvanced(condition)
	}
	
	return qb
}

// WhereDate adds date-based filtering
func (qb *WMSQueryBuilder) WhereDate(field string, operator value_objects.FilterOperator, date time.Time) entities.QueryBuilder {
	dateStr := date.Format("2006-01-02T15:04:05Z")
	
	switch operator {
	case value_objects.OpDateBefore:
		return qb.Where(field, value_objects.OpLessThan, dateStr)
	case value_objects.OpDateAfter:
		return qb.Where(field, value_objects.OpGreaterThan, dateStr)
	case value_objects.OpEquals:
		// For date equality, use a range for the whole day
		startOfDay := time.Date(date.Year(), date.Month(), date.Day(), 0, 0, 0, 0, date.Location())
		endOfDay := startOfDay.Add(24 * time.Hour).Add(-time.Nanosecond)
		return qb.WhereDateRange(field, startOfDay, endOfDay)
	default:
		return qb.Where(field, operator, dateStr)
	}
}

// WhereDateRange adds date range filtering
func (qb *WMSQueryBuilder) WhereDateRange(field string, start, end time.Time) entities.QueryBuilder {
	qb.filters[field+"__gte"] = start.Format("2006-01-02T15:04:05Z")
	qb.filters[field+"__lte"] = end.Format("2006-01-02T15:04:05Z")
	return qb
}

// WhereIncremental adds incremental extraction filters
func (qb *WMSQueryBuilder) WhereIncremental(replicationKey string, bookmark interface{}, safetyOverlap time.Duration) entities.QueryBuilder {
	if bookmark == nil {
		return qb
	}
	
	// Handle different bookmark types
	switch v := bookmark.(type) {
	case time.Time:
		// Apply safety overlap for timestamp-based replication
		adjustedTime := v.Add(-safetyOverlap)
		qb.filters[replicationKey+"__gte"] = adjustedTime.Format("2006-01-02T15:04:05Z")
	case string:
		// Try to parse as timestamp first
		if parsedTime, err := time.Parse("2006-01-02T15:04:05Z", v); err == nil {
			adjustedTime := parsedTime.Add(-safetyOverlap)
			qb.filters[replicationKey+"__gte"] = adjustedTime.Format("2006-01-02T15:04:05Z")
		} else {
			// Treat as string/ID
			qb.filters[replicationKey+"__gt"] = v
		}
	default:
		// Numeric or other types
		qb.filters[replicationKey+"__gt"] = v
	}
	
	return qb
}

// OrderBy adds ordering to the query
func (qb *WMSQueryBuilder) OrderBy(field string, direction string) entities.QueryBuilder {
	qb.ordering = append(qb.ordering, OrderClause{
		Field:     field,
		Direction: strings.ToLower(direction),
		NullsLast: true,
	})
	return qb
}

// OrderByAsc adds ascending ordering
func (qb *WMSQueryBuilder) OrderByAsc(field string) entities.QueryBuilder {
	return qb.OrderBy(field, "asc")
}

// OrderByDesc adds descending ordering
func (qb *WMSQueryBuilder) OrderByDesc(field string) entities.QueryBuilder {
	return qb.OrderBy(field, "desc")
}

// Select specifies which fields to include in the result
func (qb *WMSQueryBuilder) Select(fields ...string) entities.QueryBuilder {
	qb.fields = fields
	return qb
}

// Limit sets the maximum number of records to return
func (qb *WMSQueryBuilder) Limit(limit int) entities.QueryBuilder {
	qb.pagination.Limit = limit
	return qb
}

// Offset sets the number of records to skip
func (qb *WMSQueryBuilder) Offset(offset int64) entities.QueryBuilder {
	qb.pagination.Offset = offset
	qb.pagination.Mode = "offset"
	return qb
}

// Page sets page-based pagination
func (qb *WMSQueryBuilder) Page(page, pageSize int) entities.QueryBuilder {
	qb.pagination.Page = page
	qb.pagination.PageSize = pageSize
	qb.pagination.Mode = "page"
	return qb
}

// Cursor sets cursor-based pagination
func (qb *WMSQueryBuilder) Cursor(cursor string) entities.QueryBuilder {
	qb.pagination.Cursor = cursor
	qb.pagination.Mode = "cursor"
	return qb
}

// Join adds a join with another entity (if supported by the API)
func (qb *WMSQueryBuilder) Join(entity, joinType, condition string) entities.QueryBuilder {
	qb.joins = append(qb.joins, JoinClause{
		Entity:    entity,
		Type:      joinType,
		Condition: condition,
	})
	return qb
}

// Build converts the query to URL parameters for Oracle WMS API
func (qb *WMSQueryBuilder) Build() (string, error) {
	params := url.Values{}
	
	// Add filters
	for key, value := range qb.filters {
		params.Set(key, fmt.Sprintf("%v", value))
	}
	
	// Add field selection
	if len(qb.fields) > 0 {
		params.Set("fields", strings.Join(qb.fields, ","))
	}
	
	// Add ordering
	if len(qb.ordering) > 0 {
		var orderFields []string
		for _, order := range qb.ordering {
			if order.Direction == "desc" {
				orderFields = append(orderFields, "-"+order.Field)
			} else {
				orderFields = append(orderFields, order.Field)
			}
		}
		params.Set("ordering", strings.Join(orderFields, ","))
	}
	
	// Add pagination
	switch qb.pagination.Mode {
	case "offset":
		if qb.pagination.Limit > 0 {
			params.Set("limit", strconv.Itoa(qb.pagination.Limit))
		}
		if qb.pagination.Offset > 0 {
			params.Set("offset", strconv.FormatInt(qb.pagination.Offset, 10))
		}
	case "page":
		if qb.pagination.Page > 0 {
			params.Set("page", strconv.Itoa(qb.pagination.Page))
		}
		if qb.pagination.PageSize > 0 {
			params.Set("page_size", strconv.Itoa(qb.pagination.PageSize))
		}
	case "cursor":
		if qb.pagination.Cursor != "" {
			params.Set("cursor", qb.pagination.Cursor)
		}
		if qb.pagination.Limit > 0 {
			params.Set("page_size", strconv.Itoa(qb.pagination.Limit))
		}
	}
	
	return params.Encode(), nil
}

// BuildURL builds a complete URL with the base entity URL and query parameters
func (qb *WMSQueryBuilder) BuildURL(baseURL string) (string, error) {
	queryString, err := qb.Build()
	if err != nil {
		return "", err
	}
	
	if queryString == "" {
		return baseURL, nil
	}
	
	separator := "?"
	if strings.Contains(baseURL, "?") {
		separator = "&"
	}
	
	return baseURL + separator + queryString, nil
}

// GetFilters returns the current filter map
func (qb *WMSQueryBuilder) GetFilters() map[string]interface{} {
	return qb.filters
}

// GetOrdering returns the current ordering clauses
func (qb *WMSQueryBuilder) GetOrdering() []interface{} {
	// Convert OrderClause to []interface{} with proper structure
	result := make([]interface{}, len(qb.ordering))
	for i, order := range qb.ordering {
		result[i] = map[string]interface{}{
			"field":     order.Field,
			"direction": order.Direction,
			"nulls_last": order.NullsLast,
		}
	}
	return result
}

// Clone creates a copy of the query builder
func (qb *WMSQueryBuilder) Clone() entities.QueryBuilder {
	clone := &WMSQueryBuilder{
		entity:     qb.entity,
		filters:    make(map[string]interface{}),
		ordering:   make([]OrderClause, len(qb.ordering)),
		pagination: qb.pagination,
		fields:     make([]string, len(qb.fields)),
		joins:      make([]JoinClause, len(qb.joins)),
	}
	
	// Deep copy filters
	for k, v := range qb.filters {
		clone.filters[k] = v
	}
	
	// Copy slices
	copy(clone.ordering, qb.ordering)
	copy(clone.fields, qb.fields)
	copy(clone.joins, qb.joins)
	
	return clone
}

// Reset clears all conditions and returns to initial state
func (qb *WMSQueryBuilder) Reset() entities.QueryBuilder {
	qb.filters = make(map[string]interface{})
	qb.ordering = []OrderClause{}
	qb.fields = []string{}
	qb.joins = []JoinClause{}
	qb.pagination = PaginationClause{}
	return qb
}

// Validate checks if the query is valid for the entity
func (qb *WMSQueryBuilder) Validate() error {
	// Check if filtered fields exist in entity
	for filterKey := range qb.filters {
		// Extract field name (remove operator suffix)
		fieldName := qb.extractFieldName(filterKey)
		if !qb.fieldExists(fieldName) {
			return fmt.Errorf("field %s does not exist in entity %s", fieldName, qb.entity.Name)
		}
		
		// Check if field supports filtering
		if !qb.fieldSupportsFiltering(fieldName) {
			return fmt.Errorf("field %s does not support filtering", fieldName)
		}
	}
	
	// Check ordering fields
	for _, order := range qb.ordering {
		if !qb.fieldExists(order.Field) {
			return fmt.Errorf("ordering field %s does not exist in entity %s", order.Field, qb.entity.Name)
		}
		
		if !qb.fieldSupportsSorting(order.Field) {
			return fmt.Errorf("field %s does not support sorting", order.Field)
		}
	}
	
	// Check selected fields
	for _, field := range qb.fields {
		if !qb.fieldExists(field) {
			return fmt.Errorf("selected field %s does not exist in entity %s", field, qb.entity.Name)
		}
	}
	
	return nil
}

// Private helper methods

func (qb *WMSQueryBuilder) extractFieldName(filterKey string) string {
	// Remove common filter operators
	suffixes := []string{"__ne", "__gt", "__gte", "__lt", "__lte", "__like", "__ilike", 
		"__startswith", "__endswith", "__contains", "__in", "__not_in", "__isnull"}
	
	for _, suffix := range suffixes {
		if strings.HasSuffix(filterKey, suffix) {
			return strings.TrimSuffix(filterKey, suffix)
		}
	}
	
	return filterKey
}

func (qb *WMSQueryBuilder) fieldExists(fieldName string) bool {
	if qb.entity == nil || len(qb.entity.Fields) == 0 {
		// If no field metadata available, assume field exists
		return true
	}
	
	for _, field := range qb.entity.Fields {
		if field.Name == fieldName {
			return true
		}
	}
	
	return false
}

func (qb *WMSQueryBuilder) fieldSupportsFiltering(fieldName string) bool {
	if qb.entity == nil || len(qb.entity.Fields) == 0 {
		// If no field metadata available, assume filtering is supported
		return true
	}
	
	for _, field := range qb.entity.Fields {
		if field.Name == fieldName {
			return field.IsFilterable
		}
	}
	
	return false
}

func (qb *WMSQueryBuilder) fieldSupportsSorting(fieldName string) bool {
	if qb.entity == nil || len(qb.entity.Fields) == 0 {
		// If no field metadata available, assume sorting is supported
		return true
	}
	
	for _, field := range qb.entity.Fields {
		if field.Name == fieldName {
			return field.IsSortable
		}
	}
	
	return false
}

// Preset query builders for common use cases

// NewIncrementalQuery creates a query builder configured for incremental extraction
func NewIncrementalQuery(entity *entities.WMSEntity, replicationKey string, bookmark interface{}) entities.QueryBuilder {
	qb := NewWMSQueryBuilder(entity)
	
	if bookmark != nil {
		qb.WhereIncremental(replicationKey, bookmark, 5*time.Minute) // 5 minute safety overlap
	}
	
	// Order by replication key for consistent ordering
	qb.OrderByAsc(replicationKey)
	
	return qb
}

// NewFullSyncQuery creates a query builder configured for full synchronization
func NewFullSyncQuery(entity *entities.WMSEntity, resumeContext map[string]interface{}) entities.QueryBuilder {
	qb := NewWMSQueryBuilder(entity)
	
	// Apply resume context if provided
	if minID, exists := resumeContext["min_id_in_target"]; exists {
		qb.Where("id", value_objects.OpLessThan, minID)
		qb.OrderByDesc("id") // Descending order for resume strategy
	} else {
		qb.OrderByAsc("id") // Default ascending order
	}
	
	return qb
}

// NewSampleQuery creates a query builder for sampling data
func NewSampleQuery(entity *entities.WMSEntity, sampleSize int) entities.QueryBuilder {
	qb := NewWMSQueryBuilder(entity)
	qb.Limit(sampleSize)
	qb.OrderByAsc("id") // Consistent ordering for sampling
	return qb
}

// WMSQueryBuilderFactory implements the QueryBuilderFactory interface
type WMSQueryBuilderFactory struct{}

// NewWMSQueryBuilderFactory creates a new query builder factory
func NewWMSQueryBuilderFactory() *WMSQueryBuilderFactory {
	return &WMSQueryBuilderFactory{}
}

// CreateQueryBuilder creates a new query builder for an entity
func (f *WMSQueryBuilderFactory) CreateQueryBuilder(entity *entities.WMSEntity) entities.QueryBuilder {
	return NewWMSQueryBuilder(entity)
}

