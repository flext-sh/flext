package services

import (
	"context"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/domain/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/wms/infrastructure/errors"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// WMSService provides application-level services for WMS operations
type WMSService struct {
	// Domain services
	schemaService       *services.WMSSchemaService
	queryBuilderFactory entities.QueryBuilderFactory
	errorHandlerFactory entities.ErrorHandlerFactory

	// Event publisher
	eventPublisher domain.EventPublisher

	// Logger
	logger *slog.Logger

	// Client registry
	clients      map[uuid.UUID]*entities.WMSClient
	clientsMutex sync.RWMutex

	// Extractor registry
	extractors      map[uuid.UUID]*entities.WMSExtractor
	extractorsMutex sync.RWMutex

	// Configuration
	config WMSServiceConfig

	// Background services
	backgroundCtx    context.Context
	backgroundCancel context.CancelFunc
	backgroundWG     sync.WaitGroup
}

// WMSServiceConfig configures the WMS service
type WMSServiceConfig struct {
	// Connection settings
	DefaultTimeout           time.Duration `json:"default_timeout"`
	MaxConcurrentConnections int           `json:"max_concurrent_connections"`
	ConnectionPoolSize       int           `json:"connection_pool_size"`

	// Discovery settings
	AutoDiscoveryEnabled bool          `json:"auto_discovery_enabled"`
	DiscoveryInterval    time.Duration `json:"discovery_interval"`
	EntityCacheTTL       time.Duration `json:"entity_cache_ttl"`

	// Extraction settings
	MaxConcurrentExtractions int `json:"max_concurrent_extractions"`
	DefaultBatchSize         int `json:"default_batch_size"`
	DefaultPageSize          int `json:"default_page_size"`

	// Monitoring settings
	MetricsEnabled        bool          `json:"metrics_enabled"`
	HealthCheckInterval   time.Duration `json:"health_check_interval"`
	PerformanceMonitoring bool          `json:"performance_monitoring"`

	// Error handling
	MaxRetries             int     `json:"max_retries"`
	RetryBackoffMultiplier float64 `json:"retry_backoff_multiplier"`
	CircuitBreakerEnabled  bool    `json:"circuit_breaker_enabled"`

	// Security settings
	TLSVerification   bool          `json:"tls_verification"`
	AuthTokenCacheTTL time.Duration `json:"auth_token_cache_ttl"`
}

// CreateClientRequest represents a request to create a new WMS client
type CreateClientRequest struct {
	BaseURL    string            `json:"base_url" validate:"required,url"`
	Username   string            `json:"username" validate:"required"`
	Password   string            `json:"password" validate:"required"`
	APIVersion string            `json:"api_version,omitempty"`
	Timeout    *time.Duration    `json:"timeout,omitempty"`
	Headers    map[string]string `json:"headers,omitempty"`

	// Advanced configuration
	CircuitBreakerConfig *entities.CircuitBreaker `json:"circuit_breaker_config,omitempty"`
	CacheConfig          *entities.CacheConfig    `json:"cache_config,omitempty"`

	// Connection options
	MaxRetries    *int  `json:"max_retries,omitempty"`
	VerifySSL     *bool `json:"verify_ssl,omitempty"`
	AutoDiscovery *bool `json:"auto_discovery,omitempty"`
}

// CreateExtractionRequest represents a request to create a new extraction
type CreateExtractionRequest struct {
	ClientID       uuid.UUID                         `json:"client_id" validate:"required"`
	EntityName     string                            `json:"entity_name" validate:"required"`
	ExtractionType entities.ExtractionType           `json:"extraction_type" validate:"required"`
	Configuration  *entities.ExtractionConfiguration `json:"configuration,omitempty"`

	// Output configuration
	OutputFormat string `json:"output_format,omitempty"`
	OutputPath   string `json:"output_path,omitempty"`

	// Performance settings
	BatchSize      *int `json:"batch_size,omitempty"`
	PageSize       *int `json:"page_size,omitempty"`
	MaxConcurrency *int `json:"max_concurrency,omitempty"`

	// Scheduling
	StartAt   *time.Time `json:"start_at,omitempty"`
	Recurring bool       `json:"recurring,omitempty"`
	Schedule  string     `json:"schedule,omitempty"` // cron expression
}

// EntityDiscoveryResult represents the result of entity discovery
type EntityDiscoveryResult struct {
	ClientID           uuid.UUID                      `json:"client_id"`
	EntitiesDiscovered map[string]*entities.WMSEntity `json:"entities_discovered"`
	TotalEntities      int                            `json:"total_entities"`
	DiscoveryDuration  time.Duration                  `json:"discovery_duration"`
	Errors             []string                       `json:"errors,omitempty"`
	Timestamp          time.Time                      `json:"timestamp"`
}

// ExtractionStatus represents the status of an extraction operation
type ExtractionStatus struct {
	ExtractorID uuid.UUID                   `json:"extractor_id"`
	ClientID    uuid.UUID                   `json:"client_id"`
	EntityName  string                      `json:"entity_name"`
	Status      entities.ExtractionStatus   `json:"status"`
	Progress    entities.ExtractionProgress `json:"progress"`
	Metrics     entities.ExtractionMetrics  `json:"metrics"`
	StartTime   *time.Time                  `json:"start_time,omitempty"`
	EndTime     *time.Time                  `json:"end_time,omitempty"`
	LastError   *entities.ExtractionError   `json:"last_error,omitempty"`
	Checkpoints []entities.StateCheckpoint  `json:"checkpoints"`
}

// ClientHealthStatus represents the health status of a WMS client
type ClientHealthStatus struct {
	ClientID          uuid.UUID              `json:"client_id"`
	Status            entities.ClientStatus  `json:"status"`
	LastConnected     *time.Time             `json:"last_connected,omitempty"`
	ConnectionID      string                 `json:"connection_id"`
	Metrics           entities.ClientMetrics `json:"metrics"`
	EntityCount       int                    `json:"entity_count"`
	ActiveExtractions int                    `json:"active_extractions"`
	LastError         string                 `json:"last_error,omitempty"`
	HealthScore       float64                `json:"health_score"` // 0.0 to 1.0
}

// NewWMSService creates a new WMS service with default configuration
func NewWMSService(eventPublisher domain.EventPublisher, logger *slog.Logger) *WMSService {
	// Create background context
	backgroundCtx, backgroundCancel := context.WithCancel(context.Background())

	service := &WMSService{
		schemaService:       services.NewWMSSchemaService(),
		queryBuilderFactory: services.NewWMSQueryBuilderFactory(),
		errorHandlerFactory: errors.NewWMSErrorHandlerFactory(),
		eventPublisher:      eventPublisher,
		logger:              logger,
		clients:             make(map[uuid.UUID]*entities.WMSClient),
		extractors:          make(map[uuid.UUID]*entities.WMSExtractor),
		backgroundCtx:       backgroundCtx,
		backgroundCancel:    backgroundCancel,

		// Default configuration
		config: WMSServiceConfig{
			DefaultTimeout:           30 * time.Second,
			MaxConcurrentConnections: 50,
			ConnectionPoolSize:       10,
			AutoDiscoveryEnabled:     true,
			DiscoveryInterval:        5 * time.Minute,
			EntityCacheTTL:           1 * time.Hour,
			MaxConcurrentExtractions: 10,
			DefaultBatchSize:         1000,
			DefaultPageSize:          1000,
			MetricsEnabled:           true,
			HealthCheckInterval:      30 * time.Second,
			PerformanceMonitoring:    true,
			MaxRetries:               3,
			RetryBackoffMultiplier:   2.0,
			CircuitBreakerEnabled:    true,
			TLSVerification:          true,
			AuthTokenCacheTTL:        1 * time.Hour,
		},
	}

	// Start background services
	service.startBackgroundServices()

	return service
}

// CreateClient creates and registers a new WMS client
func (s *WMSService) CreateClient(ctx context.Context, req CreateClientRequest) (*entities.WMSClient, error) {
	s.logger.Info("Creating new WMS client",
		"base_url", req.BaseURL,
		"username", req.Username,
		"api_version", req.APIVersion)

	// Validate request
	if err := s.validateCreateClientRequest(req); err != nil {
		return nil, fmt.Errorf("invalid create client request: %w", err)
	}

	// Create client
	client, err := entities.NewWMSClient(req.BaseURL, req.Username, req.Password)
	if err != nil {
		return nil, fmt.Errorf("failed to create WMS client: %w", err)
	}

	// Apply configuration
	if err := s.applyClientConfiguration(client, req); err != nil {
		return nil, fmt.Errorf("failed to apply client configuration: %w", err)
	}

	// Connect to WMS API
	if err := client.Connect(ctx); err != nil {
		return nil, fmt.Errorf("failed to connect to WMS API: %w", err)
	}

	// Register client
	s.clientsMutex.Lock()
	s.clients[client.GetID()] = client
	s.clientsMutex.Unlock()

	// Publish events
	for _, event := range client.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish client event", "error", err)
		}
	}
	client.MarkEventsAsCommitted()

	// Start auto-discovery if enabled
	if s.config.AutoDiscoveryEnabled && (req.AutoDiscovery == nil || *req.AutoDiscovery) {
		go s.performAutoDiscovery(client)
	}

	s.logger.Info("WMS client created and connected",
		"client_id", client.GetID(),
		"base_url", req.BaseURL)

	return client, nil
}

// GetClient retrieves a client by ID
func (s *WMSService) GetClient(clientID uuid.UUID) (*entities.WMSClient, error) {
	s.clientsMutex.RLock()
	defer s.clientsMutex.RUnlock()

	client, exists := s.clients[clientID]
	if !exists {
		return nil, fmt.Errorf("client %s not found", clientID)
	}

	return client, nil
}

// ListClients returns all registered clients
func (s *WMSService) ListClients() []*entities.WMSClient {
	s.clientsMutex.RLock()
	defer s.clientsMutex.RUnlock()

	clients := make([]*entities.WMSClient, 0, len(s.clients))
	for _, client := range s.clients {
		clients = append(clients, client)
	}

	return clients
}

// RemoveClient removes and disconnects a client
func (s *WMSService) RemoveClient(ctx context.Context, clientID uuid.UUID) error {
	s.clientsMutex.Lock()
	defer s.clientsMutex.Unlock()

	client, exists := s.clients[clientID]
	if !exists {
		return fmt.Errorf("client %s not found", clientID)
	}

	// Stop any active extractions for this client
	if err := s.stopClientExtractions(ctx, clientID); err != nil {
		s.logger.Error("Failed to stop client extractions", "client_id", clientID, "error", err)
	}

	// Disconnect client
	if err := client.Disconnect(); err != nil {
		s.logger.Error("Failed to disconnect client", "client_id", clientID, "error", err)
	}

	// Remove from registry
	delete(s.clients, clientID)

	s.logger.Info("WMS client removed", "client_id", clientID)

	return nil
}

// DiscoverEntities performs entity discovery for a client
func (s *WMSService) DiscoverEntities(ctx context.Context, clientID uuid.UUID, forceRefresh bool) (*EntityDiscoveryResult, error) {
	client, err := s.GetClient(clientID)
	if err != nil {
		return nil, err
	}

	startTime := time.Now()

	s.logger.Info("Starting entity discovery",
		"client_id", clientID,
		"force_refresh", forceRefresh)

	// Perform discovery
	if err := client.DiscoverEntities(ctx, forceRefresh); err != nil {
		return nil, fmt.Errorf("entity discovery failed: %w", err)
	}

	// Get discovered entities
	entities := client.GetAllEntities()

	result := &EntityDiscoveryResult{
		ClientID:           clientID,
		EntitiesDiscovered: entities,
		TotalEntities:      len(entities),
		DiscoveryDuration:  time.Since(startTime),
		Timestamp:          time.Now(),
	}

	// Publish discovery events
	for _, event := range client.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish discovery event", "error", err)
		}
	}
	client.MarkEventsAsCommitted()

	s.logger.Info("Entity discovery completed",
		"client_id", clientID,
		"entities_discovered", result.TotalEntities,
		"duration", result.DiscoveryDuration)

	return result, nil
}

// GenerateEntitySchema generates a JSON schema for a specific entity
func (s *WMSService) GenerateEntitySchema(ctx context.Context, clientID uuid.UUID, entityName string) (*entities.WMSEntitySchema, error) {
	client, err := s.GetClient(clientID)
	if err != nil {
		return nil, err
	}

	s.logger.Info("Generating entity schema",
		"client_id", clientID,
		"entity_name", entityName)

	// Generate schema using domain service
	schema, err := s.schemaService.GenerateSchema(ctx, client, entityName)
	if err != nil {
		return nil, fmt.Errorf("failed to generate schema for entity %s: %w", entityName, err)
	}

	s.logger.Info("Entity schema generated",
		"client_id", clientID,
		"entity_name", entityName,
		"generation_method", schema.GenerationMethod,
		"property_count", len(schema.Properties))

	return schema, nil
}

// CreateExtraction creates and starts a new data extraction
func (s *WMSService) CreateExtraction(ctx context.Context, req CreateExtractionRequest) (*entities.WMSExtractor, error) {
	s.logExtractionCreationStart(req)

	if err := s.validateCreateExtractionRequest(req); err != nil {
		return nil, fmt.Errorf("invalid create extraction request: %w", err)
	}

	client, err := s.validateClientAndEntity(req)
	if err != nil {
		return nil, err
	}

	extractor, err := s.createAndConfigureExtractor(client, req)
	if err != nil {
		return nil, err
	}

	s.registerExtractor(extractor)
	s.publishExtractorEvents(extractor)

	if err := s.startExtractionIfNeeded(ctx, extractor, req); err != nil {
		return nil, err
	}

	s.logExtractionCreationSuccess(extractor, req)
	return extractor, nil
}

// GetExtraction retrieves an extractor by ID
func (s *WMSService) GetExtraction(extractorID uuid.UUID) (*entities.WMSExtractor, error) {
	s.extractorsMutex.RLock()
	defer s.extractorsMutex.RUnlock()

	extractor, exists := s.extractors[extractorID]
	if !exists {
		return nil, fmt.Errorf("extractor %s not found", extractorID)
	}

	return extractor, nil
}

// GetExtractionStatus gets the current status of an extraction
func (s *WMSService) GetExtractionStatus(extractorID uuid.UUID) (*ExtractionStatus, error) {
	extractor, err := s.GetExtraction(extractorID)
	if err != nil {
		return nil, err
	}

	return &ExtractionStatus{
		ExtractorID: extractorID,
		ClientID:    extractor.Client.GetID(),
		EntityName:  extractor.EntityName,
		Status:      extractor.GetExtractionStatus(),
		Progress:    extractor.GetExtractionProgress(),
		Metrics:     extractor.GetExtractionMetrics(),
		StartTime:   extractor.StartTime,
		EndTime:     extractor.EndTime,
		LastError:   extractor.State.LastError,
		Checkpoints: extractor.State.StateCheckpoints,
	}, nil
}

// ListExtractions returns all registered extractors
func (s *WMSService) ListExtractions() []*entities.WMSExtractor {
	s.extractorsMutex.RLock()
	defer s.extractorsMutex.RUnlock()

	extractors := make([]*entities.WMSExtractor, 0, len(s.extractors))
	for _, extractor := range s.extractors {
		extractors = append(extractors, extractor)
	}

	return extractors
}

// StopExtraction stops a running extraction
func (s *WMSService) StopExtraction(ctx context.Context, extractorID uuid.UUID) error {
	extractor, err := s.GetExtraction(extractorID)
	if err != nil {
		return err
	}

	if err := extractor.StopExtraction(); err != nil {
		return fmt.Errorf("failed to stop extraction: %w", err)
	}

	// Publish stop events
	for _, event := range extractor.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish extraction stop event", "error", err)
		}
	}
	extractor.MarkEventsAsCommitted()

	s.logger.Info("Extraction stopped", "extractor_id", extractorID)

	return nil
}

// PauseExtraction pauses a running extraction
func (s *WMSService) PauseExtraction(ctx context.Context, extractorID uuid.UUID) error {
	extractor, err := s.GetExtraction(extractorID)
	if err != nil {
		return err
	}

	if err := extractor.PauseExtraction(); err != nil {
		return fmt.Errorf("failed to pause extraction: %w", err)
	}

	// Publish pause events
	for _, event := range extractor.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish extraction pause event", "error", err)
		}
	}
	extractor.MarkEventsAsCommitted()

	s.logger.Info("Extraction paused", "extractor_id", extractorID)

	return nil
}

// ResumeExtraction resumes a paused extraction
func (s *WMSService) ResumeExtraction(ctx context.Context, extractorID uuid.UUID) error {
	extractor, err := s.GetExtraction(extractorID)
	if err != nil {
		return err
	}

	if err := extractor.ResumeExtraction(ctx); err != nil {
		return fmt.Errorf("failed to resume extraction: %w", err)
	}

	// Publish resume events
	for _, event := range extractor.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish extraction resume event", "error", err)
		}
	}
	extractor.MarkEventsAsCommitted()

	s.logger.Info("Extraction resumed", "extractor_id", extractorID)

	return nil
}

// GetClientHealth returns the health status of a client
func (s *WMSService) GetClientHealth(clientID uuid.UUID) (*ClientHealthStatus, error) {
	client, err := s.GetClient(clientID)
	if err != nil {
		return nil, err
	}

	// Count active extractions for this client
	activeExtractions := s.countClientActiveExtractions(clientID)

	// Calculate health score
	healthScore := s.calculateClientHealthScore(client)

	return &ClientHealthStatus{
		ClientID:          clientID,
		Status:            client.Status,
		LastConnected:     client.LastConnected,
		ConnectionID:      client.ConnectionID,
		Metrics:           client.GetMetrics(),
		EntityCount:       len(client.GetAllEntities()),
		ActiveExtractions: activeExtractions,
		HealthScore:       healthScore,
	}, nil
}

// Shutdown gracefully shuts down the WMS service
func (s *WMSService) Shutdown(ctx context.Context) error {
	s.logger.Info("Shutting down WMS service")

	// Cancel background services
	s.backgroundCancel()

	// Stop all active extractions
	for _, extractor := range s.ListExtractions() {
		if extractor.GetExtractionStatus() == entities.ExtractionStatusRunning {
			if err := s.StopExtraction(ctx, extractor.GetID()); err != nil {
				s.logger.Error("Failed to stop extraction during shutdown",
					"extractor_id", extractor.GetID(),
					"error", err)
			}
		}
	}

	// Disconnect all clients
	for _, client := range s.ListClients() {
		if err := s.RemoveClient(ctx, client.GetID()); err != nil {
			s.logger.Error("Failed to remove client during shutdown",
				"client_id", client.GetID(),
				"error", err)
		}
	}

	// Wait for background services to finish
	s.backgroundWG.Wait()

	s.logger.Info("WMS service shutdown completed")

	return nil
}

// Private helper methods

func (s *WMSService) validateCreateClientRequest(req CreateClientRequest) error {
	if req.BaseURL == "" {
		return fmt.Errorf("base URL is required")
	}
	if req.Username == "" {
		return fmt.Errorf("username is required")
	}
	if req.Password == "" {
		return fmt.Errorf("password is required")
	}
	return nil
}

func (s *WMSService) validateCreateExtractionRequest(req CreateExtractionRequest) error {
	if req.ClientID == uuid.Nil {
		return fmt.Errorf("client ID is required")
	}
	if req.EntityName == "" {
		return fmt.Errorf("entity name is required")
	}
	if req.ExtractionType == "" {
		return fmt.Errorf("extraction type is required")
	}
	return nil
}

func (s *WMSService) applyClientConfiguration(client *entities.WMSClient, req CreateClientRequest) error {
	config := make(map[string]interface{})

	if req.Timeout != nil {
		config["timeout"] = *req.Timeout
	}

	if req.Headers != nil {
		config["headers"] = req.Headers
	}

	if req.CircuitBreakerConfig != nil {
		config["circuit_breaker"] = *req.CircuitBreakerConfig
	}

	if req.CacheConfig != nil {
		config["cache_config"] = *req.CacheConfig
	}

	if len(config) > 0 {
		return client.UpdateConfiguration(config)
	}

	return nil
}

func (s *WMSService) applyExtractorConfiguration(extractor *entities.WMSExtractor, req CreateExtractionRequest) error {
	if req.Configuration != nil {
		extractor.Configuration = req.Configuration
	}

	if req.BatchSize != nil {
		extractor.BatchSize = *req.BatchSize
	}

	if req.PageSize != nil && extractor.PaginationConfig != nil {
		extractor.PaginationConfig.PageSize = *req.PageSize
	}

	if req.MaxConcurrency != nil {
		extractor.MaxConcurrency = *req.MaxConcurrency
	}

	return nil
}

func (s *WMSService) startBackgroundServices() {
	if s.config.HealthCheckInterval > 0 {
		s.backgroundWG.Add(1)
		go s.healthCheckWorker()
	}

	if s.config.AutoDiscoveryEnabled && s.config.DiscoveryInterval > 0 {
		s.backgroundWG.Add(1)
		go s.autoDiscoveryWorker()
	}

	if s.config.MetricsEnabled {
		s.backgroundWG.Add(1)
		go s.metricsWorker()
	}
}

func (s *WMSService) healthCheckWorker() {
	defer s.backgroundWG.Done()

	ticker := time.NewTicker(s.config.HealthCheckInterval)
	defer ticker.Stop()

	for {
		select {
		case <-s.backgroundCtx.Done():
			return
		case <-ticker.C:
			s.performHealthChecks()
		}
	}
}

func (s *WMSService) autoDiscoveryWorker() {
	defer s.backgroundWG.Done()

	ticker := time.NewTicker(s.config.DiscoveryInterval)
	defer ticker.Stop()

	for {
		select {
		case <-s.backgroundCtx.Done():
			return
		case <-ticker.C:
			s.performScheduledDiscovery()
		}
	}
}

func (s *WMSService) metricsWorker() {
	defer s.backgroundWG.Done()

	ticker := time.NewTicker(1 * time.Minute) // Collect metrics every minute
	defer ticker.Stop()

	for {
		select {
		case <-s.backgroundCtx.Done():
			return
		case <-ticker.C:
			s.collectMetrics()
		}
	}
}

func (s *WMSService) performHealthChecks() {
	for _, client := range s.ListClients() {
		go func(client *entities.WMSClient) {
			health, err := s.GetClientHealth(client.GetID())
			if err != nil {
				s.logger.Error("Failed to get client health",
					"client_id", client.GetID(),
					"error", err)
				return
			}

			if health.HealthScore < 0.5 {
				s.logger.Warn("Client health is poor",
					"client_id", client.GetID(),
					"health_score", health.HealthScore)
			}
		}(client)
	}
}

func (s *WMSService) performScheduledDiscovery() {
	for _, client := range s.ListClients() {
		if client.IsConnected() {
			go s.performAutoDiscovery(client)
		}
	}
}

func (s *WMSService) performAutoDiscovery(client *entities.WMSClient) {
	ctx, cancel := context.WithTimeout(s.backgroundCtx, 5*time.Minute)
	defer cancel()

	if _, err := s.DiscoverEntities(ctx, client.GetID(), false); err != nil {
		s.logger.Error("Auto-discovery failed",
			"client_id", client.GetID(),
			"error", err)
	}
}

func (s *WMSService) collectMetrics() {
	// Collect and publish service-level metrics
	// Implementation would depend on metrics system
}

func (s *WMSService) stopClientExtractions(ctx context.Context, clientID uuid.UUID) error {
	for _, extractor := range s.ListExtractions() {
		if extractor.Client.GetID() == clientID {
			if extractor.GetExtractionStatus() == entities.ExtractionStatusRunning {
				if err := s.StopExtraction(ctx, extractor.GetID()); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

func (s *WMSService) countClientActiveExtractions(clientID uuid.UUID) int {
	count := 0
	for _, extractor := range s.ListExtractions() {
		if extractor.Client.GetID() == clientID {
			status := extractor.GetExtractionStatus()
			if status == entities.ExtractionStatusRunning || status == entities.ExtractionStatusPaused {
				count++
			}
		}
	}
	return count
}

func (s *WMSService) calculateClientHealthScore(client *entities.WMSClient) float64 {
	if !client.IsConnected() {
		return 0.0
	}

	metrics := client.GetMetrics()

	// Calculate success rate
	totalRequests := metrics.TotalRequests
	if totalRequests == 0 {
		return 1.0 // No requests yet, assume healthy
	}

	successRate := float64(metrics.SuccessfulRequests) / float64(totalRequests)

	// Factor in recent errors
	errorPenalty := 0.0
	if len(metrics.ErrorsByType) > 0 {
		totalErrors := 0
		for _, count := range metrics.ErrorsByType {
			totalErrors += count
		}
		errorPenalty = float64(totalErrors) / float64(totalRequests) * 0.5
	}

	// Factor in response time
	timePenalty := 0.0
	if metrics.AverageResponseTime > 5*time.Second {
		timePenalty = 0.2
	} else if metrics.AverageResponseTime > 2*time.Second {
		timePenalty = 0.1
	}

	healthScore := successRate - errorPenalty - timePenalty
	if healthScore < 0.0 {
		healthScore = 0.0
	}
	if healthScore > 1.0 {
		healthScore = 1.0
	}

	return healthScore
}


// Helper methods for CreateExtraction

func (s *WMSService) logExtractionCreationStart(req CreateExtractionRequest) {
	s.logger.Info("Creating new extraction",
		"client_id", req.ClientID,
		"entity_name", req.EntityName,
		"extraction_type", req.ExtractionType)
}

func (s *WMSService) validateClientAndEntity(req CreateExtractionRequest) (*entities.WMSClient, error) {
	client, err := s.GetClient(req.ClientID)
	if err != nil {
		return nil, err
	}

	if _, err := client.GetEntity(req.EntityName); err != nil {
		return nil, fmt.Errorf("entity %s not found in client: %w", req.EntityName, err)
	}

	return client, nil
}

func (s *WMSService) createAndConfigureExtractor(client *entities.WMSClient, req CreateExtractionRequest) (*entities.WMSExtractor, error) {
	extractor, err := entities.NewWMSExtractor(client, req.EntityName, req.ExtractionType, s.queryBuilderFactory, s.errorHandlerFactory)
	if err != nil {
		return nil, fmt.Errorf("failed to create extractor: %w", err)
	}

	if err := s.applyExtractorConfiguration(extractor, req); err != nil {
		return nil, fmt.Errorf("failed to apply extractor configuration: %w", err)
	}

	return extractor, nil
}

func (s *WMSService) registerExtractor(extractor *entities.WMSExtractor) {
	s.extractorsMutex.Lock()
	s.extractors[extractor.GetID()] = extractor
	s.extractorsMutex.Unlock()
}

func (s *WMSService) publishExtractorEvents(extractor *entities.WMSExtractor) {
	for _, event := range extractor.GetUncommittedEvents() {
		if err := s.eventPublisher.Publish(event); err != nil {
			s.logger.Error("Failed to publish extractor event", "error", err)
		}
	}
	extractor.MarkEventsAsCommitted()
}

func (s *WMSService) startExtractionIfNeeded(ctx context.Context, extractor *entities.WMSExtractor, req CreateExtractionRequest) error {
	if req.StartAt == nil || req.StartAt.Before(time.Now()) {
		if err := extractor.StartExtraction(ctx); err != nil {
			return fmt.Errorf("failed to start extraction: %w", err)
		}
	}
	return nil
}

func (s *WMSService) logExtractionCreationSuccess(extractor *entities.WMSExtractor, req CreateExtractionRequest) {
	s.logger.Info("Extraction created and started",
		"extractor_id", extractor.GetID(),
		"client_id", req.ClientID,
		"entity_name", req.EntityName)
}

