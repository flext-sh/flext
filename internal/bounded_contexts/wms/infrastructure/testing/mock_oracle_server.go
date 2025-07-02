package testing

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"time"
)

// MockOracleWMSServer simulates an Oracle WMS API server for testing
type MockOracleWMSServer struct {
	server  *httptest.Server
	baseURL string
	
	// Simulated data
	entities map[string]*MockEntity
	records  map[string][]map[string]interface{}
	
	// Authentication
	validCredentials map[string]string
	
	// Response configurations
	simulateDelay    time.Duration
	simulateErrors   bool
	errorRate        float64
}

// MockEntity represents a WMS entity in the mock server
type MockEntity struct {
	Name        string                 `json:"name"`
	DisplayName string                 `json:"display_name"`
	Fields      []MockField            `json:"fields"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// MockField represents a field in a WMS entity
type MockField struct {
	Name         string `json:"name"`
	Type         string `json:"type"`
	Required     bool   `json:"required"`
	IsPrimaryKey bool   `json:"is_primary_key"`
	MaxLength    *int   `json:"max_length,omitempty"`
}

// NewMockOracleWMSServer creates a new mock Oracle WMS server
func NewMockOracleWMSServer() *MockOracleWMSServer {
	mock := &MockOracleWMSServer{
		entities: make(map[string]*MockEntity),
		records:  make(map[string][]map[string]interface{}),
		validCredentials: map[string]string{
			"testuser": "testpass",
			"admin":    "admin123",
		},
		simulateDelay: 100 * time.Millisecond,
		simulateErrors: false,
		errorRate:     0.0,
	}
	
	// Setup default entities
	mock.setupDefaultEntities()
	
	// Setup HTTP server
	mux := http.NewServeMux()
	mock.setupRoutes(mux)
	
	mock.server = httptest.NewServer(mux)
	mock.baseURL = mock.server.URL
	
	return mock
}

// GetBaseURL returns the base URL of the mock server
func (m *MockOracleWMSServer) GetBaseURL() string {
	return m.baseURL
}

// Close shuts down the mock server
func (m *MockOracleWMSServer) Close() {
	if m.server != nil {
		m.server.Close()
	}
}

// SetSimulateDelay configures response delay
func (m *MockOracleWMSServer) SetSimulateDelay(delay time.Duration) {
	m.simulateDelay = delay
}

// SetSimulateErrors configures error simulation
func (m *MockOracleWMSServer) SetSimulateErrors(enable bool, rate float64) {
	m.simulateErrors = enable
	m.errorRate = rate
}

// setupDefaultEntities creates sample WMS entities
func (m *MockOracleWMSServer) setupDefaultEntities() {
	// Item Master entity
	itemMaster := &MockEntity{
		Name:        "item_master",
		DisplayName: "Item Master",
		Fields: []MockField{
			{Name: "item_id", Type: "string", Required: true, IsPrimaryKey: true, MaxLength: intPtr(50)},
			{Name: "item_name", Type: "string", Required: true, MaxLength: intPtr(200)},
			{Name: "item_description", Type: "string", Required: false, MaxLength: intPtr(500)},
			{Name: "item_type", Type: "string", Required: true, MaxLength: intPtr(50)},
			{Name: "unit_of_measure", Type: "string", Required: true, MaxLength: intPtr(10)},
			{Name: "created_date", Type: "datetime", Required: true},
			{Name: "modified_date", Type: "datetime", Required: true},
			{Name: "created_by", Type: "string", Required: true, MaxLength: intPtr(100)},
			{Name: "modified_by", Type: "string", Required: true, MaxLength: intPtr(100)},
		},
		Metadata: map[string]interface{}{
			"table_name": "WMS_ITEM_MASTER",
			"schema":     "WMS",
		},
	}
	
	// Inventory entity
	inventory := &MockEntity{
		Name:        "inventory",
		DisplayName: "Inventory",
		Fields: []MockField{
			{Name: "inventory_id", Type: "string", Required: true, IsPrimaryKey: true, MaxLength: intPtr(50)},
			{Name: "item_id", Type: "string", Required: true, MaxLength: intPtr(50)},
			{Name: "location_id", Type: "string", Required: true, MaxLength: intPtr(50)},
			{Name: "quantity_on_hand", Type: "decimal", Required: true},
			{Name: "quantity_available", Type: "decimal", Required: true},
			{Name: "quantity_reserved", Type: "decimal", Required: false},
			{Name: "last_count_date", Type: "datetime", Required: false},
			{Name: "modified_date", Type: "datetime", Required: true},
		},
		Metadata: map[string]interface{}{
			"table_name": "WMS_INVENTORY",
			"schema":     "WMS",
		},
	}
	
	// Shipment entity
	shipment := &MockEntity{
		Name:        "shipment",
		DisplayName: "Shipment",
		Fields: []MockField{
			{Name: "shipment_id", Type: "string", Required: true, IsPrimaryKey: true, MaxLength: intPtr(50)},
			{Name: "shipment_number", Type: "string", Required: true, MaxLength: intPtr(100)},
			{Name: "customer_id", Type: "string", Required: true, MaxLength: intPtr(50)},
			{Name: "ship_date", Type: "datetime", Required: false},
			{Name: "delivery_date", Type: "datetime", Required: false},
			{Name: "status", Type: "string", Required: true, MaxLength: intPtr(20)},
			{Name: "tracking_number", Type: "string", Required: false, MaxLength: intPtr(100)},
			{Name: "created_date", Type: "datetime", Required: true},
			{Name: "modified_date", Type: "datetime", Required: true},
		},
		Metadata: map[string]interface{}{
			"table_name": "WMS_SHIPMENT",
			"schema":     "WMS",
		},
	}
	
	m.entities["item_master"] = itemMaster
	m.entities["inventory"] = inventory
	m.entities["shipment"] = shipment
	
	// Generate sample data
	m.generateSampleData()
}

// generateSampleData creates sample records for testing
func (m *MockOracleWMSServer) generateSampleData() {
	now := time.Now()
	
	// Sample Item Master data
	m.records["item_master"] = []map[string]interface{}{
		{
			"item_id":          "ITEM001",
			"item_name":        "Product A",
			"item_description": "High-quality product A for testing",
			"item_type":        "FINISHED_GOOD",
			"unit_of_measure":  "EA",
			"created_date":     now.Add(-30 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":    now.Add(-2 * time.Hour).Format(time.RFC3339),
			"created_by":       "system",
			"modified_by":      "admin",
		},
		{
			"item_id":          "ITEM002",
			"item_name":        "Product B",
			"item_description": "Standard product B for testing",
			"item_type":        "FINISHED_GOOD",
			"unit_of_measure":  "PCS",
			"created_date":     now.Add(-25 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":    now.Add(-1 * time.Hour).Format(time.RFC3339),
			"created_by":       "system",
			"modified_by":      "admin",
		},
		{
			"item_id":          "ITEM003",
			"item_name":        "Product C",
			"item_description": "Premium product C for testing",
			"item_type":        "RAW_MATERIAL",
			"unit_of_measure":  "KG",
			"created_date":     now.Add(-20 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":    now.Add(-30 * time.Minute).Format(time.RFC3339),
			"created_by":       "system",
			"modified_by":      "user1",
		},
	}
	
	// Sample Inventory data
	m.records["inventory"] = []map[string]interface{}{
		{
			"inventory_id":       "INV001",
			"item_id":           "ITEM001",
			"location_id":       "LOC001",
			"quantity_on_hand":  100.0,
			"quantity_available": 85.0,
			"quantity_reserved":  15.0,
			"last_count_date":   now.Add(-7 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":     now.Add(-1 * time.Hour).Format(time.RFC3339),
		},
		{
			"inventory_id":       "INV002",
			"item_id":           "ITEM002",
			"location_id":       "LOC001",
			"quantity_on_hand":  250.0,
			"quantity_available": 200.0,
			"quantity_reserved":  50.0,
			"last_count_date":   now.Add(-5 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":     now.Add(-2 * time.Hour).Format(time.RFC3339),
		},
	}
	
	// Sample Shipment data
	m.records["shipment"] = []map[string]interface{}{
		{
			"shipment_id":     "SHIP001",
			"shipment_number": "SN-2024-001",
			"customer_id":     "CUST001",
			"ship_date":       now.Add(-2 * 24 * time.Hour).Format(time.RFC3339),
			"delivery_date":   nil,
			"status":          "SHIPPED",
			"tracking_number": "TRK123456789",
			"created_date":    now.Add(-3 * 24 * time.Hour).Format(time.RFC3339),
			"modified_date":   now.Add(-2 * 24 * time.Hour).Format(time.RFC3339),
		},
	}
}

// setupRoutes configures HTTP routes for the mock server
func (m *MockOracleWMSServer) setupRoutes(mux *http.ServeMux) {
	// Authentication endpoint
	mux.HandleFunc("/auth/login", m.handleLogin)
	
	// Entity discovery endpoints
	mux.HandleFunc("/api/v1/entities", m.handleListEntities)
	mux.HandleFunc("/api/v1/entities/", m.handleGetEntity)
	
	// Data extraction endpoints
	mux.HandleFunc("/api/v1/data/", m.handleExtractData)
	
	// Schema endpoints
	mux.HandleFunc("/api/v1/schema/", m.handleGetSchema)
	
	// WMS API Info endpoint (Oracle WMS specific)
	mux.HandleFunc("/wms/lgfapi/", m.handleWMSRequests)
	
	// Add specific handlers for entity operations after the general handler
	// These will be checked by the general handler
	
	// Health check
	mux.HandleFunc("/health", m.handleHealth)
}

// Common middleware for authentication and delay simulation
func (m *MockOracleWMSServer) middleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Simulate processing delay
		if m.simulateDelay > 0 {
			time.Sleep(m.simulateDelay)
		}
		
		// Simulate random errors
		if m.simulateErrors && m.shouldSimulateError() {
			http.Error(w, "Simulated server error", http.StatusInternalServerError)
			return
		}
		
		// Check authentication for protected endpoints
		if r.URL.Path != "/health" && r.URL.Path != "/auth/login" {
			if !m.isAuthenticated(r) {
				http.Error(w, "Authentication required", http.StatusUnauthorized)
				return
			}
		}
		
		w.Header().Set("Content-Type", "application/json")
		next(w, r)
	}
}

// Authentication handlers
func (m *MockOracleWMSServer) handleLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	
	var loginReq struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&loginReq); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	if expectedPass, ok := m.validCredentials[loginReq.Username]; ok && expectedPass == loginReq.Password {
		response := map[string]interface{}{
			"access_token": fmt.Sprintf("mock_token_%s_%d", loginReq.Username, time.Now().Unix()),
			"token_type":   "Bearer",
			"expires_in":   3600,
			"scope":        "wms:read wms:write",
		}
		json.NewEncoder(w).Encode(response)
	} else {
		http.Error(w, "Invalid credentials", http.StatusUnauthorized)
	}
}

// Entity discovery handlers
func (m *MockOracleWMSServer) handleListEntities(w http.ResponseWriter, r *http.Request) {
	m.middleware(func(w http.ResponseWriter, r *http.Request) {
		entities := make([]map[string]interface{}, 0, len(m.entities))
		for _, entity := range m.entities {
			entities = append(entities, map[string]interface{}{
				"name":         entity.Name,
				"display_name": entity.DisplayName,
				"field_count":  len(entity.Fields),
				"metadata":     entity.Metadata,
			})
		}
		
		response := map[string]interface{}{
			"entities": entities,
			"total":    len(entities),
		}
		json.NewEncoder(w).Encode(response)
	})(w, r)
}

func (m *MockOracleWMSServer) handleGetEntity(w http.ResponseWriter, r *http.Request) {
	m.middleware(func(w http.ResponseWriter, r *http.Request) {
		entityName := strings.TrimPrefix(r.URL.Path, "/api/v1/entities/")
		
		entity, ok := m.entities[entityName]
		if !ok {
			http.Error(w, "Entity not found", http.StatusNotFound)
			return
		}
		
		json.NewEncoder(w).Encode(entity)
	})(w, r)
}

// Data extraction handlers
func (m *MockOracleWMSServer) handleExtractData(w http.ResponseWriter, r *http.Request) {
	m.middleware(func(w http.ResponseWriter, r *http.Request) {
		entityName := strings.TrimPrefix(r.URL.Path, "/api/v1/data/")
		
		records, ok := m.records[entityName]
		if !ok {
			http.Error(w, "Entity not found", http.StatusNotFound)
			return
		}
		
		// Handle pagination
		limit := 100 // default
		offset := 0
		if limitStr := r.URL.Query().Get("limit"); limitStr != "" {
			fmt.Sscanf(limitStr, "%d", &limit)
		}
		if offsetStr := r.URL.Query().Get("offset"); offsetStr != "" {
			fmt.Sscanf(offsetStr, "%d", &offset)
		}
		
		// Apply pagination
		total := len(records)
		end := offset + limit
		if end > total {
			end = total
		}
		if offset > total {
			offset = total
		}
		
		pageRecords := records[offset:end]
		
		response := map[string]interface{}{
			"data":   pageRecords,
			"total":  total,
			"limit":  limit,
			"offset": offset,
			"has_more": end < total,
		}
		json.NewEncoder(w).Encode(response)
	})(w, r)
}

// Schema handlers
func (m *MockOracleWMSServer) handleGetSchema(w http.ResponseWriter, r *http.Request) {
	m.middleware(func(w http.ResponseWriter, r *http.Request) {
		entityName := strings.TrimPrefix(r.URL.Path, "/api/v1/schema/")
		
		entity, ok := m.entities[entityName]
		if !ok {
			http.Error(w, "Entity not found", http.StatusNotFound)
			return
		}
		
		// Generate JSON schema
		schema := map[string]interface{}{
			"$schema":    "http://json-schema.org/draft-07/schema#",
			"type":       "object",
			"title":      entity.DisplayName,
			"properties": make(map[string]interface{}),
			"required":   []string{},
		}
		
		properties := schema["properties"].(map[string]interface{})
		required := []string{}
		
		for _, field := range entity.Fields {
			fieldSchema := map[string]interface{}{
				"type":        mapFieldTypeToJSONSchema(field.Type),
				"description": fmt.Sprintf("%s field", field.Name),
			}
			
			if field.MaxLength != nil {
				fieldSchema["maxLength"] = *field.MaxLength
			}
			
			properties[field.Name] = fieldSchema
			
			if field.Required {
				required = append(required, field.Name)
			}
		}
		
		schema["required"] = required
		json.NewEncoder(w).Encode(schema)
	})(w, r)
}

// WMS API requests handler (Oracle WMS specific)
func (m *MockOracleWMSServer) handleWMSRequests(w http.ResponseWriter, r *http.Request) {
	// Apply middleware for authentication, delay, and error simulation
	m.middleware(func(w http.ResponseWriter, r *http.Request) {
		// Route to appropriate handler based on path
		if strings.Contains(r.URL.Path, "/info") {
			m.handleWMSInfo(w, r)
		} else if strings.HasSuffix(r.URL.Path, "/entity") {
			// This is the entity list endpoint
			m.handleWMSEntity(w, r)
		} else if strings.Contains(r.URL.Path, "/entity/") {
			// This is an entity-specific request
			m.handleWMSEntitySpecific(w, r)
		} else {
			// Default to info endpoint
			m.handleWMSInfo(w, r)
		}
	})(w, r)
}

// WMS API Info handler (Oracle WMS specific)
func (m *MockOracleWMSServer) handleWMSInfo(w http.ResponseWriter, r *http.Request) {
	// Extract API version from path if present
	version := "v1" // default
	if strings.Contains(r.URL.Path, "/v2/") {
		version = "v2"
	}
	
	response := map[string]interface{}{
		"api_name":    "Oracle WMS API",
		"version":     version,
		"status":      "active",
		"timestamp":   time.Now().Format(time.RFC3339),
		"server_info": map[string]interface{}{
			"name":        "Mock Oracle WMS Server",
			"version":     "1.0.0",
			"environment": "test",
		},
		"capabilities": []string{
			"entity_discovery",
			"data_extraction",
			"schema_generation",
			"incremental_sync",
			"batch_processing",
		},
		"endpoints": map[string]interface{}{
			"authentication": "/auth/login",
			"entities":       "/api/v1/entities",
			"data":           "/api/v1/data",
			"schema":         "/api/v1/schema",
		},
	}
	json.NewEncoder(w).Encode(response)
}

// WMS Entity discovery handler (Oracle WMS specific)
func (m *MockOracleWMSServer) handleWMSEntity(w http.ResponseWriter, r *http.Request) {
	// Return list of available entity names as expected by WMS client
	entityNames := make([]string, 0, len(m.entities))
	for _, entity := range m.entities {
		entityNames = append(entityNames, entity.Name)
	}
	
	// Return response format expected by WMS client
	response := map[string]interface{}{
		"entities":     entityNames,
		"total_count":  len(entityNames),
		"api_version":  "v1",
		"timestamp":    time.Now().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(response)
}

// WMS Entity-specific requests handler (Oracle WMS specific entity operations)
func (m *MockOracleWMSServer) handleWMSEntitySpecific(w http.ResponseWriter, r *http.Request) {
	// Parse the entity request path: /wms/lgfapi/v10/entity/{entityName}[/describe]
	// Extract entity name from path like /wms/lgfapi/v10/entity/item_master or /wms/lgfapi/v10/entity/item_master/describe
	pathAfterEntity := strings.TrimPrefix(r.URL.Path, "/wms/lgfapi/v10/entity/")
	pathParts := strings.Split(pathAfterEntity, "/")
	
	if len(pathParts) == 0 || pathParts[0] == "" {
		http.Error(w, "Entity name required", http.StatusBadRequest)
		return
	}
	
	entityName := pathParts[0]
	entity, exists := m.entities[entityName]
	if !exists {
		http.Error(w, fmt.Sprintf("Entity %s not found", entityName), http.StatusNotFound)
		return
	}
	
	// Check if this is a describe request
	if len(pathParts) > 1 && pathParts[1] == "describe" {
		m.handleEntityDescribe(w, r, entity)
	} else {
		// This is a data request
		m.handleEntityData(w, r, entityName, entity)
	}
}

// Handle entity describe requests (schema/metadata)
func (m *MockOracleWMSServer) handleEntityDescribe(w http.ResponseWriter, r *http.Request, entity *MockEntity) {
	// Return entity metadata in expected format
	metadata := map[string]interface{}{
		"entity_name":    entity.Name,
		"display_name":   entity.DisplayName,
		"table_name":     entity.Metadata["table_name"],
		"schema_name":    entity.Metadata["schema"],
		"fields":         m.convertFieldsToMetadata(entity.Fields),
		"table_info": map[string]interface{}{
			"primary_keys": m.getPrimaryKeyFields(entity.Fields),
			"record_count": len(m.records[entity.Name]),
			"last_updated": time.Now().Add(-1 * time.Hour).Format(time.RFC3339),
		},
		"capabilities": []string{
			"select",
			"filter",
			"sort",
			"pagination",
			"incremental_sync",
		},
	}
	
	json.NewEncoder(w).Encode(metadata)
}

// Handle entity data requests (sample data or filtered data)
func (m *MockOracleWMSServer) handleEntityData(w http.ResponseWriter, r *http.Request, entityName string, entity *MockEntity) {
	records, exists := m.records[entityName]
	if !exists {
		records = []map[string]interface{}{}
	}
	
	// Handle pagination parameters
	pageSize := 1000 // default
	offset := 0
	
	if pageSizeStr := r.URL.Query().Get("page_size"); pageSizeStr != "" {
		fmt.Sscanf(pageSizeStr, "%d", &pageSize)
	}
	if limitStr := r.URL.Query().Get("limit"); limitStr != "" {
		fmt.Sscanf(limitStr, "%d", &pageSize)
	}
	if offsetStr := r.URL.Query().Get("offset"); offsetStr != "" {
		fmt.Sscanf(offsetStr, "%d", &offset)
	}
	
	// Apply pagination
	total := len(records)
	end := offset + pageSize
	if end > total {
		end = total
	}
	if offset > total {
		offset = total
	}
	
	pageRecords := records[offset:end]
	
	// Return in expected Oracle WMS format
	response := map[string]interface{}{
		"results":    pageRecords,
		"total":      total,
		"page_size":  pageSize,
		"offset":     offset,
		"has_more":   end < total,
		"entity":     entityName,
		"timestamp":  time.Now().Format(time.RFC3339),
	}
	
	json.NewEncoder(w).Encode(response)
}

// Helper functions for entity metadata
func (m *MockOracleWMSServer) convertFieldsToMetadata(fields []MockField) []map[string]interface{} {
	metadata := make([]map[string]interface{}, len(fields))
	for i, field := range fields {
		fieldMeta := map[string]interface{}{
			"name":         field.Name,
			"type":         field.Type,
			"required":     field.Required,
			"primary_key":  field.IsPrimaryKey,
			"nullable":     !field.Required,
			"description":  fmt.Sprintf("%s field for entity", field.Name),
		}
		
		if field.MaxLength != nil {
			fieldMeta["max_length"] = *field.MaxLength
		}
		
		metadata[i] = fieldMeta
	}
	return metadata
}

func (m *MockOracleWMSServer) getPrimaryKeyFields(fields []MockField) []string {
	var primaryKeys []string
	for _, field := range fields {
		if field.IsPrimaryKey {
			primaryKeys = append(primaryKeys, field.Name)
		}
	}
	return primaryKeys
}

// Health check handler
func (m *MockOracleWMSServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
		"version":   "mock-1.0.0",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Helper functions
func (m *MockOracleWMSServer) isAuthenticated(r *http.Request) bool {
	authHeader := r.Header.Get("Authorization")
	
	// Check Bearer token authentication
	if strings.HasPrefix(authHeader, "Bearer mock_token_") {
		return true
	}
	
	// Check Basic authentication
	if strings.HasPrefix(authHeader, "Basic ") {
		// Decode basic auth
		basicAuth := strings.TrimPrefix(authHeader, "Basic ")
		decoded, err := base64.StdEncoding.DecodeString(basicAuth)
		if err != nil {
			return false
		}
		
		credentials := string(decoded)
		parts := strings.SplitN(credentials, ":", 2)
		if len(parts) != 2 {
			return false
		}
		
		username, password := parts[0], parts[1]
		expectedPassword, ok := m.validCredentials[username]
		return ok && expectedPassword == password
	}
	
	return false
}

func (m *MockOracleWMSServer) shouldSimulateError() bool {
	return m.errorRate > 0 && (float64(time.Now().UnixNano()%1000)/1000.0) < m.errorRate
}

func mapFieldTypeToJSONSchema(fieldType string) string {
	switch fieldType {
	case "string":
		return "string"
	case "datetime":
		return "string" // with format: date-time
	case "decimal", "number":
		return "number"
	case "integer":
		return "integer"
	case "boolean":
		return "boolean"
	default:
		return "string"
	}
}

func intPtr(i int) *int {
	return &i
}