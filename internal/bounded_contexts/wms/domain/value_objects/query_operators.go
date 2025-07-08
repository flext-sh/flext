package value_objects

// FilterOperator defines supported filter operations
type FilterOperator string

const (
	// Comparison operators
	OpEquals             FilterOperator = "eq"
	OpNotEquals          FilterOperator = "ne"
	OpGreaterThan        FilterOperator = "gt"
	OpGreaterThanOrEqual FilterOperator = "gte"
	OpLessThan           FilterOperator = "lt"
	OpLessThanOrEqual    FilterOperator = "lte"

	// String operators
	OpLike       FilterOperator = "like"
	OpILike      FilterOperator = "ilike"
	OpStartsWith FilterOperator = "starts_with"
	OpEndsWith   FilterOperator = "ends_with"
	OpContains   FilterOperator = "contains"
	OpRegex      FilterOperator = "regex"

	// Array operators
	OpIn    FilterOperator = "in"
	OpNotIn FilterOperator = "not_in"

	// Null operators
	OpIsNull    FilterOperator = "is_null"
	OpIsNotNull FilterOperator = "is_not_null"

	// Date/time operators
	OpDateRange  FilterOperator = "date_range"
	OpDateBefore FilterOperator = "date_before"
	OpDateAfter  FilterOperator = "date_after"
	OpTimeRange  FilterOperator = "time_range"

	// Advanced operators
	OpBetween    FilterOperator = "between"
	OpNotBetween FilterOperator = "not_between"
	OpExists     FilterOperator = "exists"
	OpNotExists  FilterOperator = "not_exists"
)
