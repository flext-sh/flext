package services

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"reflect"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
)

// WMSSchemaService provides dynamic schema discovery and generation for WMS entities
type WMSSchemaService struct {
	httpClient *http.Client

	// Schema generation configuration
	config SchemaGenerationConfig

	// Cache for generated schemas
	schemaCache map[string]*CachedSchema

	// Supported data type mappings
	typeMapping map[string][]string
}

// SchemaGenerationConfig configures schema generation behavior
type SchemaGenerationConfig struct {
	// Discovery methods
	PreferMetadataDiscovery bool `json:"prefer_metadata_discovery"`
	SampleSizeForInference  int  `json:"sample_size_for_inference"`
	MaxSamplePages          int  `json:"max_sample_pages"`

	// Schema generation options
	IncludeExamples         bool `json:"include_examples"`
	IncludeDescriptions     bool `json:"include_descriptions"`
	InferFieldConstraints   bool `json:"infer_field_constraints"`
	GenerateValidationRules bool `json:"generate_validation_rules"`

	// Type inference settings
	TypeConfidenceThreshold float64 `json:"type_confidence_threshold"`
	NumericPrecisionCheck   bool    `json:"numeric_precision_check"`
	DateFormatDetection     bool    `json:"date_format_detection"`

	// Advanced features
	DetectEnumValues  bool `json:"detect_enum_values"`
	MaxEnumValues     int  `json:"max_enum_values"`
	DetectForeignKeys bool `json:"detect_foreign_keys"`
	DetectPrimaryKeys bool `json:"detect_primary_keys"`

	// Performance settings
	ParallelFieldAnalysis bool          `json:"parallel_field_analysis"`
	CacheSchemas          bool          `json:"cache_schemas"`
	SchemaCacheTTL        time.Duration `json:"schema_cache_ttl"`

	// Output format options
	JSONSchemaVersion string `json:"json_schema_version"` // "draft-07", "draft-2019-09"
	IncludeTitle      bool   `json:"include_title"`
	IncludeMetadata   bool   `json:"include_metadata"`
}

// CachedSchema represents a cached schema with metadata
type CachedSchema struct {
	Schema           *entities.WMSEntitySchema `json:"schema"`
	CachedAt         time.Time                 `json:"cached_at"`
	ExpiresAt        time.Time                 `json:"expires_at"`
	GenerationMethod string                    `json:"generation_method"`
	SampleSize       int                       `json:"sample_size"`
	Confidence       float64                   `json:"confidence"`
}

// FieldAnalysis contains detailed analysis of a field
type FieldAnalysis struct {
	Name           string  `json:"name"`
	Type           string  `json:"type"`
	TypeConfidence float64 `json:"type_confidence"`
	Format         string  `json:"format,omitempty"`

	// Statistical analysis
	NonNullCount int64 `json:"non_null_count"`
	NullCount    int64 `json:"null_count"`
	UniqueCount  int64 `json:"unique_count"`

	// Type-specific analysis
	MinLength *int     `json:"min_length,omitempty"`
	MaxLength *int     `json:"max_length,omitempty"`
	AvgLength *float64 `json:"avg_length,omitempty"`
	MinValue  *float64 `json:"min_value,omitempty"`
	MaxValue  *float64 `json:"max_value,omitempty"`

	// Pattern analysis
	CommonPatterns []PatternInfo `json:"common_patterns,omitempty"`
	DateFormats    []string      `json:"date_formats,omitempty"`

	// Enum detection
	PossibleEnum bool          `json:"possible_enum"`
	EnumValues   []interface{} `json:"enum_values,omitempty"`

	// Key detection
	IsPrimaryKey    bool   `json:"is_primary_key"`
	IsForeignKey    bool   `json:"is_foreign_key"`
	ReferencedTable string `json:"referenced_table,omitempty"`

	// Sample values
	SampleValues []interface{} `json:"sample_values,omitempty"`

	// Business metadata
	Description  string `json:"description,omitempty"`
	BusinessName string `json:"business_name,omitempty"`
	Category     string `json:"category,omitempty"`
}

// PatternInfo represents a detected pattern in field values
type PatternInfo struct {
	Pattern     string  `json:"pattern"`
	Frequency   int     `json:"frequency"`
	Confidence  float64 `json:"confidence"`
	Description string  `json:"description,omitempty"`
}

// MetadataSource represents metadata obtained from API describe endpoints
type MetadataSource struct {
	Fields       []FieldMetadata  `json:"fields"`
	EntityName   string           `json:"entity_name"`
	TableName    string           `json:"table_name,omitempty"`
	Description  string           `json:"description,omitempty"`
	PrimaryKeys  []string         `json:"primary_keys,omitempty"`
	ForeignKeys  []ForeignKeyInfo `json:"foreign_keys,omitempty"`
	Indexes      []IndexInfo      `json:"indexes,omitempty"`
	Constraints  []ConstraintInfo `json:"constraints,omitempty"`
	LastModified *time.Time       `json:"last_modified,omitempty"`
	Version      string           `json:"version,omitempty"`
}

// FieldMetadata represents field metadata from API
type FieldMetadata struct {
	Name         string      `json:"name"`
	Type         string      `json:"type"`
	Length       *int        `json:"length,omitempty"`
	Precision    *int        `json:"precision,omitempty"`
	Scale        *int        `json:"scale,omitempty"`
	Nullable     bool        `json:"nullable"`
	DefaultValue interface{} `json:"default_value,omitempty"`
	Description  string      `json:"description,omitempty"`
	Format       string      `json:"format,omitempty"`

	// Constraints
	Required bool `json:"required"`
	Unique   bool `json:"unique"`
	Indexed  bool `json:"indexed"`

	// Business metadata
	DisplayName  string `json:"display_name,omitempty"`
	Category     string `json:"category,omitempty"`
	BusinessRule string `json:"business_rule,omitempty"`
}

// ForeignKeyInfo represents foreign key relationships
type ForeignKeyInfo struct {
	ColumnName       string `json:"column_name"`
	ReferencedTable  string `json:"referenced_table"`
	ReferencedColumn string `json:"referenced_column"`
	OnDelete         string `json:"on_delete,omitempty"`
	OnUpdate         string `json:"on_update,omitempty"`
}

// IndexInfo represents database indexes
type IndexInfo struct {
	Name        string   `json:"name"`
	Columns     []string `json:"columns"`
	Unique      bool     `json:"unique"`
	Type        string   `json:"type,omitempty"`
	Description string   `json:"description,omitempty"`
}

// ConstraintInfo represents database constraints
type ConstraintInfo struct {
	Name        string   `json:"name"`
	Type        string   `json:"type"` // "CHECK", "NOT NULL", "UNIQUE", etc.
	Columns     []string `json:"columns"`
	Expression  string   `json:"expression,omitempty"`
	Description string   `json:"description,omitempty"`
}

// NewWMSSchemaService creates a new schema service with default configuration
func NewWMSSchemaService() *WMSSchemaService {
	return &WMSSchemaService{
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		config: SchemaGenerationConfig{
			PreferMetadataDiscovery: true,
			SampleSizeForInference:  100,
			MaxSamplePages:          5,
			IncludeExamples:         true,
			IncludeDescriptions:     true,
			InferFieldConstraints:   true,
			GenerateValidationRules: true,
			TypeConfidenceThreshold: 0.8,
			NumericPrecisionCheck:   true,
			DateFormatDetection:     true,
			DetectEnumValues:        true,
			MaxEnumValues:           50,
			DetectForeignKeys:       true,
			DetectPrimaryKeys:       true,
			ParallelFieldAnalysis:   true,
			CacheSchemas:            true,
			SchemaCacheTTL:          1 * time.Hour,
			JSONSchemaVersion:       "draft-07",
			IncludeTitle:            true,
			IncludeMetadata:         true,
		},
		schemaCache: make(map[string]*CachedSchema),
		typeMapping: getDefaultTypeMapping(),
	}
}

// GenerateSchema generates a JSON schema for a WMS entity using the best available method
func (s *WMSSchemaService) GenerateSchema(ctx context.Context, client *entities.WMSClient, entityName string) (*entities.WMSEntitySchema, error) {
	if cached := s.checkSchemaCache(entityName); cached != nil {
		return cached, nil
	}

	schema, method := s.attemptSchemaGeneration(ctx, client, entityName)
	if schema == nil {
		return nil, fmt.Errorf("failed to generate schema for entity %s", entityName)
	}

	s.finalizeSchema(schema, method)
	s.cacheSchemaIfEnabled(entityName, schema, method)

	return schema, nil
}

// GenerateFromMetadata generates schema from API metadata endpoints
func (s *WMSSchemaService) generateFromMetadata(ctx context.Context, client *entities.WMSClient, entityName string) (*entities.WMSEntitySchema, error) {
	// Construct metadata endpoint URL
	metadataURL := fmt.Sprintf("%s/wms/lgfapi/%s/entity/%s/describe",
		client.BaseURL, client.APIVersion, entityName)

	// Make request to metadata endpoint
	req, err := http.NewRequestWithContext(ctx, "GET", metadataURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create metadata request: %w", err)
	}

	// Add authentication headers
	for key, value := range client.Headers {
		req.Header.Set(key, value)
	}

	resp, err := s.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch metadata: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("metadata endpoint returned status %d", resp.StatusCode)
	}

	// Parse metadata response
	var metadata MetadataSource
	if err := json.NewDecoder(resp.Body).Decode(&metadata); err != nil {
		return nil, fmt.Errorf("failed to parse metadata response: %w", err)
	}

	// Convert metadata to JSON schema
	return s.convertMetadataToSchema(entityName, &metadata), nil
}

// GenerateFromSamples generates schema by analyzing sample data
func (s *WMSSchemaService) generateFromSamples(ctx context.Context, client *entities.WMSClient, entityName string) (*entities.WMSEntitySchema, error) {
	// Get sample data from the entity
	samples, err := s.fetchSampleData(ctx, client, entityName)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch sample data: %w", err)
	}

	if len(samples) == 0 {
		return nil, fmt.Errorf("no sample data available for entity %s", entityName)
	}

	// Analyze sample data to infer schema
	fieldAnalyses := s.analyzeSampleData(samples)

	// Convert field analyses to JSON schema
	return s.convertAnalysisToSchema(entityName, fieldAnalyses), nil
}

// GenerateMinimalSchema creates a basic schema when other methods fail
func (s *WMSSchemaService) generateMinimalSchema(entityName string) *entities.WMSEntitySchema {
	return &entities.WMSEntitySchema{
		Type: "object",
		Properties: map[string]*entities.SchemaProperty{
			"id": {
				Type:        "integer",
				Description: "Primary key identifier",
				PrimaryKey:  true,
			},
		},
		Required:             []string{},
		AdditionalProperties: true,
		Title:                entityName,
		Description:          fmt.Sprintf("Minimal schema for %s entity", entityName),
		GeneratedAt:          time.Now(),
		GenerationMethod:     "minimal",
	}
}

// fetchSampleData retrieves sample records from the WMS entity
func (s *WMSSchemaService) fetchSampleData(ctx context.Context, client *entities.WMSClient, entityName string) ([]map[string]interface{}, error) {
	var allSamples []map[string]interface{}
	pageSize := 50 // Small page size for sampling
	maxPages := s.config.MaxSamplePages

	for page := 1; page <= maxPages; page++ {
		// Construct sample data URL
		sampleURL := fmt.Sprintf("%s/wms/lgfapi/%s/entity/%s?page=%d&page_size=%d",
			client.BaseURL, client.APIVersion, entityName, page, pageSize)

		// Make request
		req, err := http.NewRequestWithContext(ctx, "GET", sampleURL, nil)
		if err != nil {
			return nil, fmt.Errorf("failed to create sample request: %w", err)
		}

		// Add authentication headers
		for key, value := range client.Headers {
			req.Header.Set(key, value)
		}

		resp, err := s.httpClient.Do(req)
		if err != nil {
			return nil, fmt.Errorf("failed to fetch sample data: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			if page == 1 {
				return nil, fmt.Errorf("sample endpoint returned status %d", resp.StatusCode)
			}
			break // No more pages
		}

		// Parse response
		var response struct {
			Results []map[string]interface{} `json:"results"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
			return nil, fmt.Errorf("failed to parse sample response: %w", err)
		}

		allSamples = append(allSamples, response.Results...)

		// Stop if we have enough samples
		if len(allSamples) >= s.config.SampleSizeForInference {
			break
		}

		// Stop if this page had no results
		if len(response.Results) == 0 {
			break
		}
	}

	return allSamples, nil
}

// analyzeSampleData performs statistical analysis on sample data to infer field types and constraints
func (s *WMSSchemaService) analyzeSampleData(samples []map[string]interface{}) map[string]*FieldAnalysis {
	fieldAnalyses := make(map[string]*FieldAnalysis)

	// Collect all field names
	allFields := make(map[string]bool)
	for _, sample := range samples {
		for fieldName := range sample {
			allFields[fieldName] = true
		}
	}

	// Analyze each field
	for fieldName := range allFields {
		analysis := s.analyzeField(fieldName, samples)
		fieldAnalyses[fieldName] = analysis
	}

	return fieldAnalyses
}

// analyzeField performs detailed analysis of a single field across all samples
func (s *WMSSchemaService) analyzeField(fieldName string, samples []map[string]interface{}) *FieldAnalysis {
	analysis := s.initializeFieldAnalysis(fieldName)
	values, nonNullValues := s.collectFieldValues(fieldName, samples)

	analysis.NonNullCount = int64(len(nonNullValues))
	analysis.NullCount = int64(len(values)) - analysis.NonNullCount

	if len(nonNullValues) == 0 {
		return s.handleNullOnlyField(analysis)
	}

	bestType := s.inferBestType(nonNullValues)
	analysis.Type = bestType
	analysis.TypeConfidence = s.calculateTypeConfidence(nonNullValues, bestType)

	s.performTypeSpecificAnalysis(analysis, bestType, nonNullValues)
	s.performAdvancedAnalysis(analysis, nonNullValues)
	s.storeSampleValues(analysis, nonNullValues)

	return analysis
}

// detectValueType determines the JSON Schema type for a value
func (s *WMSSchemaService) detectValueType(value interface{}) string {
	if value == nil {
		return "null"
	}

	switch v := value.(type) {
	case bool:
		return "boolean"
	case int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
		return "integer"
	case float32, float64:
		return "number"
	case string:
		// Try to detect if string represents other types
		if s.config.DateFormatDetection && s.isDateString(v) {
			return "string" // with format: date-time
		}
		return "string"
	case []interface{}:
		return "array"
	case map[string]interface{}:
		return "object"
	default:
		// Use reflection for complex types
		rv := reflect.ValueOf(value)
		switch rv.Kind() {
		case reflect.Slice, reflect.Array:
			return "array"
		case reflect.Map, reflect.Struct:
			return "object"
		default:
			return "string"
		}
	}
}

// analyzeStringField performs string-specific analysis
func (s *WMSSchemaService) analyzeStringField(analysis *FieldAnalysis, values []interface{}) {
	var lengths []int
	var stringValues []string

	for _, value := range values {
		if str, ok := value.(string); ok {
			lengths = append(lengths, len(str))
			stringValues = append(stringValues, str)
		}
	}

	if len(lengths) > 0 {
		minLen, maxLen := lengths[0], lengths[0]
		totalLen := 0
		for _, length := range lengths {
			if length < minLen {
				minLen = length
			}
			if length > maxLen {
				maxLen = length
			}
			totalLen += length
		}

		analysis.MinLength = &minLen
		analysis.MaxLength = &maxLen
		avgLen := float64(totalLen) / float64(len(lengths))
		analysis.AvgLength = &avgLen
	}

	// Detect common patterns
	if s.config.InferFieldConstraints {
		s.detectStringPatterns(analysis, stringValues)
	}

	// Detect date formats
	if s.config.DateFormatDetection {
		s.detectDateFormats(analysis, stringValues)
	}
}

// analyzeNumericField performs numeric-specific analysis
func (s *WMSSchemaService) analyzeNumericField(analysis *FieldAnalysis, values []interface{}) {
	var numericValues []float64

	for _, value := range values {
		if num, ok := s.convertToFloat64(value); ok {
			numericValues = append(numericValues, num)
		}
	}

	if len(numericValues) > 0 {
		min, max := numericValues[0], numericValues[0]
		for _, num := range numericValues {
			if num < min {
				min = num
			}
			if num > max {
				max = num
			}
		}

		analysis.MinValue = &min
		analysis.MaxValue = &max
	}
}

// analyzeBooleanField performs boolean-specific analysis
func (s *WMSSchemaService) analyzeBooleanField(analysis *FieldAnalysis, values []interface{}) {
	// Boolean fields don't need much additional analysis
	// Could track true/false distribution if needed
}

// detectEnumValues determines if a field has enum-like characteristics
func (s *WMSSchemaService) detectEnumValues(analysis *FieldAnalysis, values []interface{}) {
	uniqueValues := make(map[interface{}]int)
	for _, value := range values {
		uniqueValues[value]++
	}

	analysis.UniqueCount = int64(len(uniqueValues))

	// Consider as enum if:
	// 1. Number of unique values is small relative to total values
	// 2. Number of unique values is below threshold
	totalValues := len(values)
	uniqueRatio := float64(len(uniqueValues)) / float64(totalValues)

	if len(uniqueValues) <= s.config.MaxEnumValues && uniqueRatio < 0.1 {
		analysis.PossibleEnum = true
		for value := range uniqueValues {
			analysis.EnumValues = append(analysis.EnumValues, value)
		}
	}
}

// detectPrimaryKey attempts to detect if a field is a primary key
func (s *WMSSchemaService) detectPrimaryKey(analysis *FieldAnalysis, values []interface{}) {
	// Simple heuristics for primary key detection:
	// 1. Field name suggests it's an ID
	// 2. All values are unique
	// 3. No null values
	// 4. Numeric or string type

	fieldName := strings.ToLower(analysis.Name)
	isIDName := strings.Contains(fieldName, "id") || fieldName == "pk" || strings.HasSuffix(fieldName, "_id")

	if isIDName && analysis.NullCount == 0 && analysis.UniqueCount == int64(len(values)) {
		if analysis.Type == "integer" || analysis.Type == "string" {
			analysis.IsPrimaryKey = true
		}
	}
}

// Helper methods

func (s *WMSSchemaService) isDateString(str string) bool {
	// Common date formats to check
	dateFormats := []string{
		time.RFC3339,
		time.RFC3339Nano,
		"2006-01-02",
		"2006-01-02 15:04:05",
		"01/02/2006",
		"01-02-2006",
	}

	for _, format := range dateFormats {
		if _, err := time.Parse(format, str); err == nil {
			return true
		}
	}

	return false
}

func (s *WMSSchemaService) convertToFloat64(value interface{}) (float64, bool) {
	switch v := value.(type) {
	case int:
		return float64(v), true
	case int8:
		return float64(v), true
	case int16:
		return float64(v), true
	case int32:
		return float64(v), true
	case int64:
		return float64(v), true
	case uint:
		return float64(v), true
	case uint8:
		return float64(v), true
	case uint16:
		return float64(v), true
	case uint32:
		return float64(v), true
	case uint64:
		return float64(v), true
	case float32:
		return float64(v), true
	case float64:
		return v, true
	default:
		return 0, false
	}
}

func (s *WMSSchemaService) detectStringPatterns(analysis *FieldAnalysis, values []string) {
	// Implementation of pattern detection would go here
	// This could include regex pattern detection, common formats, etc.
}

func (s *WMSSchemaService) detectDateFormats(analysis *FieldAnalysis, values []string) {
	// Implementation of date format detection would go here
}

func (s *WMSSchemaService) convertMetadataToSchema(entityName string, metadata *MetadataSource) *entities.WMSEntitySchema {
	properties := make(map[string]*entities.SchemaProperty)
	var required []string

	for _, field := range metadata.Fields {
		prop := &entities.SchemaProperty{
			Type:        s.mapDatabaseTypeToJSONType(field.Type),
			Description: field.Description,
			Nullable:    field.Nullable,
			PrimaryKey:  contains(metadata.PrimaryKeys, field.Name),
		}

		if field.Length != nil {
			prop.MaxLength = field.Length
		}

		if field.DefaultValue != nil {
			prop.Default = field.DefaultValue
		}

		if field.Required {
			required = append(required, field.Name)
		}

		properties[field.Name] = prop
	}

	return &entities.WMSEntitySchema{
		Type:                 "object",
		Properties:           properties,
		Required:             required,
		AdditionalProperties: false,
		Title:                entityName,
		Description:          metadata.Description,
		GeneratedAt:          time.Now(),
		GenerationMethod:     "metadata",
	}
}

func (s *WMSSchemaService) convertAnalysisToSchema(entityName string, analyses map[string]*FieldAnalysis) *entities.WMSEntitySchema {
	properties := make(map[string]*entities.SchemaProperty)
	var required []string

	for fieldName, analysis := range analyses {
		prop := &entities.SchemaProperty{
			Type:       analysis.Type,
			Nullable:   analysis.NullCount > 0,
			PrimaryKey: analysis.IsPrimaryKey,
		}

		// Add constraints based on analysis
		if analysis.MinLength != nil {
			prop.MinLength = analysis.MinLength
		}
		if analysis.MaxLength != nil {
			prop.MaxLength = analysis.MaxLength
		}
		if analysis.MinValue != nil {
			prop.Minimum = analysis.MinValue
		}
		if analysis.MaxValue != nil {
			prop.Maximum = analysis.MaxValue
		}

		// Add enum values if detected
		if analysis.PossibleEnum && len(analysis.EnumValues) > 0 {
			prop.Enum = analysis.EnumValues
		}

		// Add examples
		if s.config.IncludeExamples && len(analysis.SampleValues) > 0 {
			prop.Examples = analysis.SampleValues[:min(3, len(analysis.SampleValues))]
		}

		// Add description
		if s.config.IncludeDescriptions && analysis.Description != "" {
			prop.Description = analysis.Description
		}

		// Determine if field should be required
		nullRatio := float64(analysis.NullCount) / float64(analysis.NullCount+analysis.NonNullCount)
		if nullRatio < 0.1 { // Less than 10% null values
			required = append(required, fieldName)
		}

		properties[fieldName] = prop
	}

	return &entities.WMSEntitySchema{
		Type:                 "object",
		Properties:           properties,
		Required:             required,
		AdditionalProperties: true,
		Title:                entityName,
		Description:          fmt.Sprintf("Generated schema for %s entity", entityName),
		GeneratedAt:          time.Now(),
		GenerationMethod:     "sample",
	}
}

func (s *WMSSchemaService) mapDatabaseTypeToJSONType(dbType string) interface{} {
	dbType = strings.ToUpper(dbType)

	if types, exists := s.typeMapping[dbType]; exists {
		if len(types) == 1 {
			return types[0]
		}
		return types // Multiple types
	}

	// Default fallback based on common patterns
	if strings.Contains(dbType, "INT") {
		return "integer"
	}
	if strings.Contains(dbType, "FLOAT") || strings.Contains(dbType, "DOUBLE") || strings.Contains(dbType, "DECIMAL") {
		return "number"
	}
	if strings.Contains(dbType, "BOOL") {
		return "boolean"
	}

	return "string" // Default fallback
}

func (s *WMSSchemaService) getCachedSchema(entityName string) *CachedSchema {
	if cached, exists := s.schemaCache[entityName]; exists {
		if time.Now().Before(cached.ExpiresAt) {
			return cached
		}
		// Remove expired cache
		delete(s.schemaCache, entityName)
	}
	return nil
}

func (s *WMSSchemaService) cacheSchema(entityName string, schema *entities.WMSEntitySchema, method string, sampleSize int, confidence float64) {
	now := time.Now()
	s.schemaCache[entityName] = &CachedSchema{
		Schema:           schema,
		CachedAt:         now,
		ExpiresAt:        now.Add(s.config.SchemaCacheTTL),
		GenerationMethod: method,
		SampleSize:       sampleSize,
		Confidence:       confidence,
	}
}

func getDefaultTypeMapping() map[string][]string {
	return map[string][]string{
		"VARCHAR":   {"string"},
		"VARCHAR2":  {"string"},
		"CHAR":      {"string"},
		"TEXT":      {"string"},
		"CLOB":      {"string"},
		"NUMBER":    {"number"},
		"INTEGER":   {"integer"},
		"INT":       {"integer"},
		"BIGINT":    {"integer"},
		"SMALLINT":  {"integer"},
		"FLOAT":     {"number"},
		"DOUBLE":    {"number"},
		"DECIMAL":   {"number"},
		"NUMERIC":   {"number"},
		"DATE":      {"string"},
		"TIMESTAMP": {"string"},
		"DATETIME":  {"string"},
		"TIME":      {"string"},
		"BOOLEAN":   {"boolean"},
		"BOOL":      {"boolean"},
		"BLOB":      {"string"},
		"BINARY":    {"string"},
	}
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Helper methods for GenerateSchema

func (s *WMSSchemaService) checkSchemaCache(entityName string) *entities.WMSEntitySchema {
	if s.config.CacheSchemas {
		if cached := s.getCachedSchema(entityName); cached != nil {
			return cached.Schema
		}
	}
	return nil
}

func (s *WMSSchemaService) attemptSchemaGeneration(ctx context.Context, client *entities.WMSClient, entityName string) (*entities.WMSEntitySchema, string) {
	// Try metadata-based generation first if preferred
	if s.config.PreferMetadataDiscovery {
		if schema, err := s.generateFromMetadata(ctx, client, entityName); err == nil && schema != nil {
			return schema, "metadata"
		}
	}

	// Fall back to sample-based generation
	if schema, err := s.generateFromSamples(ctx, client, entityName); err == nil && schema != nil {
		return schema, "sample"
	}

	// Last resort: create minimal schema
	return s.generateMinimalSchema(entityName), "minimal"
}

func (s *WMSSchemaService) finalizeSchema(schema *entities.WMSEntitySchema, method string) {
	schema.GeneratedAt = time.Now()
	schema.GenerationMethod = method
	schema.Version = "1.0"
}

func (s *WMSSchemaService) cacheSchemaIfEnabled(entityName string, schema *entities.WMSEntitySchema, method string) {
	if s.config.CacheSchemas {
		s.cacheSchema(entityName, schema, method, 0, 1.0)
	}
}

// Helper methods for analyzeField

func (s *WMSSchemaService) initializeFieldAnalysis(fieldName string) *FieldAnalysis {
	return &FieldAnalysis{
		Name:           fieldName,
		CommonPatterns: []PatternInfo{},
		DateFormats:    []string{},
		SampleValues:   []interface{}{},
	}
}

func (s *WMSSchemaService) collectFieldValues(fieldName string, samples []map[string]interface{}) ([]interface{}, []interface{}) {
	var values []interface{}
	var nonNullValues []interface{}

	for _, sample := range samples {
		if value, exists := sample[fieldName]; exists {
			values = append(values, value)
			if value != nil {
				nonNullValues = append(nonNullValues, value)
			}
		}
	}

	return values, nonNullValues
}

func (s *WMSSchemaService) handleNullOnlyField(analysis *FieldAnalysis) *FieldAnalysis {
	analysis.Type = "null"
	analysis.TypeConfidence = 1.0
	return analysis
}

func (s *WMSSchemaService) inferBestType(nonNullValues []interface{}) string {
	typeCounter := make(map[string]int)
	for _, value := range nonNullValues {
		detectedType := s.detectValueType(value)
		typeCounter[detectedType]++
	}

	var bestType string
	var maxCount int
	for valueType, count := range typeCounter {
		if count > maxCount {
			maxCount = count
			bestType = valueType
		}
	}

	return bestType
}

func (s *WMSSchemaService) calculateTypeConfidence(nonNullValues []interface{}, bestType string) float64 {
	typeCounter := make(map[string]int)
	for _, value := range nonNullValues {
		detectedType := s.detectValueType(value)
		typeCounter[detectedType]++
	}

	maxCount := typeCounter[bestType]
	return float64(maxCount) / float64(len(nonNullValues))
}

func (s *WMSSchemaService) performTypeSpecificAnalysis(analysis *FieldAnalysis, bestType string, nonNullValues []interface{}) {
	switch bestType {
	case "string":
		s.analyzeStringField(analysis, nonNullValues)
	case "integer", "number":
		s.analyzeNumericField(analysis, nonNullValues)
	case "boolean":
		s.analyzeBooleanField(analysis, nonNullValues)
	}
}

func (s *WMSSchemaService) performAdvancedAnalysis(analysis *FieldAnalysis, nonNullValues []interface{}) {
	if s.config.DetectEnumValues {
		s.detectEnumValues(analysis, nonNullValues)
	}

	if s.config.DetectPrimaryKeys {
		s.detectPrimaryKey(analysis, nonNullValues)
	}
}

func (s *WMSSchemaService) storeSampleValues(analysis *FieldAnalysis, nonNullValues []interface{}) {
	sampleCount := 5
	if len(nonNullValues) < sampleCount {
		sampleCount = len(nonNullValues)
	}
	analysis.SampleValues = nonNullValues[:sampleCount]
}
