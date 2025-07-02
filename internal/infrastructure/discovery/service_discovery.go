package discovery

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
)

// ServiceInfo represents information about a service instance
type ServiceInfo struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Version     string            `json:"version"`
	Address     string            `json:"address"`
	Port        int               `json:"port"`
	Protocol    string            `json:"protocol"`
	Health      HealthStatus      `json:"health"`
	Metadata    map[string]string `json:"metadata"`
	Tags        []string          `json:"tags"`
	NodeID      string            `json:"node_id"`
	LastSeen    time.Time         `json:"last_seen"`
	RegisteredAt time.Time        `json:"registered_at"`
}

// HealthStatus represents the health status of a service
type HealthStatus string

const (
	HealthStatusHealthy   HealthStatus = "healthy"
	HealthStatusUnhealthy HealthStatus = "unhealthy"
	HealthStatusUnknown   HealthStatus = "unknown"
)

// ServiceRegistry manages service registration and discovery
type ServiceRegistry struct {
	nodeID       string
	redisClient  *redis.Client
	logger       logging.Logger
	services     map[string]*ServiceInfo
	servicesMutex sync.RWMutex
	ctx          context.Context
	cancel       context.CancelFunc
	healthChecks map[string]HealthChecker
	healthMutex  sync.RWMutex
}

// HealthChecker defines the interface for service health checking
type HealthChecker interface {
	CheckHealth(ctx context.Context, service *ServiceInfo) HealthStatus
}

// LoadBalancer manages load balancing between service instances
type LoadBalancer struct {
	registry *ServiceRegistry
	logger   logging.Logger
	strategy LoadBalancingStrategy
}

// LoadBalancingStrategy defines different load balancing strategies
type LoadBalancingStrategy string

const (
	StrategyRoundRobin    LoadBalancingStrategy = "round_robin"
	StrategyLeastLoad     LoadBalancingStrategy = "least_load"
	StrategyRandom        LoadBalancingStrategy = "random"
	StrategyWeighted      LoadBalancingStrategy = "weighted"
	StrategyGeoProximity  LoadBalancingStrategy = "geo_proximity"
)

// NewServiceRegistry creates a new service registry
func NewServiceRegistry(nodeID string, redisClient *redis.Client, logger logging.Logger) *ServiceRegistry {
	ctx, cancel := context.WithCancel(context.Background())

	return &ServiceRegistry{
		nodeID:       nodeID,
		redisClient:  redisClient,
		logger:       logger,
		services:     make(map[string]*ServiceInfo),
		ctx:          ctx,
		cancel:       cancel,
		healthChecks: make(map[string]HealthChecker),
	}
}

// Start starts the service registry
func (sr *ServiceRegistry) Start() error {
	sr.logger.Info("Starting service registry", logging.F("node_id", sr.nodeID))

	// Start service discovery
	go sr.serviceDiscoveryLoop()

	// Start health checking
	go sr.healthCheckLoop()

	// Start cleanup of stale services
	go sr.cleanupLoop()

	sr.logger.Info("Service registry started")
	return nil
}

// Stop stops the service registry
func (sr *ServiceRegistry) Stop() error {
	sr.logger.Info("Stopping service registry")

	sr.cancel()

	// Unregister all services from this node
	sr.servicesMutex.RLock()
	for _, service := range sr.services {
		if service.NodeID == sr.nodeID {
			sr.unregisterService(service.ID)
		}
	}
	sr.servicesMutex.RUnlock()

	sr.logger.Info("Service registry stopped")
	return nil
}

// RegisterService registers a new service instance
func (sr *ServiceRegistry) RegisterService(service *ServiceInfo) error {
	if service.RegisteredAt.IsZero() {
		service.RegisteredAt = time.Now()
	}
	service.LastSeen = time.Now()
	service.NodeID = sr.nodeID

	// Validate service info
	if err := sr.validateServiceInfo(service); err != nil {
		return fmt.Errorf("invalid service info: %w", err)
	}

	// Store in Redis
	if err := sr.storeServiceInRedis(service); err != nil {
		return fmt.Errorf("failed to store service in Redis: %w", err)
	}

	// Store locally
	sr.servicesMutex.Lock()
	sr.services[service.ID] = service
	sr.servicesMutex.Unlock()

	sr.logger.Info("Service registered",
		logging.F("service_id", service.ID),
		logging.F("service_name", service.Name),
		logging.F("address", fmt.Sprintf("%s:%d", service.Address, service.Port)),
	)

	return nil
}

// UnregisterService unregisters a service instance
func (sr *ServiceRegistry) UnregisterService(serviceID string) error {
	return sr.unregisterService(serviceID)
}

// unregisterService removes a service from registry
func (sr *ServiceRegistry) unregisterService(serviceID string) error {
	// Remove from Redis
	key := fmt.Sprintf("discovery:services:%s", serviceID)
	err := sr.redisClient.Del(sr.ctx, key).Err()
	if err != nil {
		sr.logger.Error("Failed to remove service from Redis",
			logging.F("service_id", serviceID),
			logging.F("error", err.Error()),
		)
	}

	// Remove locally
	sr.servicesMutex.Lock()
	delete(sr.services, serviceID)
	sr.servicesMutex.Unlock()

	sr.logger.Info("Service unregistered", logging.F("service_id", serviceID))
	return nil
}

// DiscoverServices discovers all instances of a service by name
func (sr *ServiceRegistry) DiscoverServices(serviceName string) ([]*ServiceInfo, error) {
	sr.servicesMutex.RLock()
	defer sr.servicesMutex.RUnlock()

	var services []*ServiceInfo
	for _, service := range sr.services {
		if service.Name == serviceName && service.Health == HealthStatusHealthy {
			services = append(services, service)
		}
	}

	return services, nil
}

// DiscoverServicesByTag discovers services by tag
func (sr *ServiceRegistry) DiscoverServicesByTag(tag string) ([]*ServiceInfo, error) {
	sr.servicesMutex.RLock()
	defer sr.servicesMutex.RUnlock()

	var services []*ServiceInfo
	for _, service := range sr.services {
		if sr.hasTag(service, tag) && service.Health == HealthStatusHealthy {
			services = append(services, service)
		}
	}

	return services, nil
}

// GetService returns a specific service by ID
func (sr *ServiceRegistry) GetService(serviceID string) (*ServiceInfo, error) {
	sr.servicesMutex.RLock()
	defer sr.servicesMutex.RUnlock()

	service, exists := sr.services[serviceID]
	if !exists {
		return nil, fmt.Errorf("service not found: %s", serviceID)
	}

	return service, nil
}

// GetAllServices returns all registered services
func (sr *ServiceRegistry) GetAllServices() map[string]*ServiceInfo {
	sr.servicesMutex.RLock()
	defer sr.servicesMutex.RUnlock()

	services := make(map[string]*ServiceInfo)
	for id, service := range sr.services {
		services[id] = service
	}

	return services
}

// RegisterHealthChecker registers a health checker for a service type
func (sr *ServiceRegistry) RegisterHealthChecker(serviceName string, checker HealthChecker) {
	sr.healthMutex.Lock()
	defer sr.healthMutex.Unlock()

	sr.healthChecks[serviceName] = checker
	sr.logger.Info("Health checker registered", logging.F("service_name", serviceName))
}

// validateServiceInfo validates service information
func (sr *ServiceRegistry) validateServiceInfo(service *ServiceInfo) error {
	if service.ID == "" {
		return fmt.Errorf("service ID is required")
	}
	if service.Name == "" {
		return fmt.Errorf("service name is required")
	}
	if service.Address == "" {
		return fmt.Errorf("service address is required")
	}
	if service.Port <= 0 || service.Port > 65535 {
		return fmt.Errorf("invalid service port: %d", service.Port)
	}

	return nil
}

// storeServiceInRedis stores service information in Redis
func (sr *ServiceRegistry) storeServiceInRedis(service *ServiceInfo) error {
	serviceData, err := json.Marshal(service)
	if err != nil {
		return fmt.Errorf("failed to marshal service: %w", err)
	}

	key := fmt.Sprintf("discovery:services:%s", service.ID)
	return sr.redisClient.Set(sr.ctx, key, serviceData, 60*time.Second).Err()
}

// serviceDiscoveryLoop discovers services from other nodes
func (sr *ServiceRegistry) serviceDiscoveryLoop() {
	ticker := time.NewTicker(15 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sr.ctx.Done():
			return
		case <-ticker.C:
			sr.discoverServices()
		}
	}
}

// discoverServices discovers services from Redis
func (sr *ServiceRegistry) discoverServices() {
	keys, err := sr.redisClient.Keys(sr.ctx, "discovery:services:*").Result()
	if err != nil {
		sr.logger.Error("Failed to discover services", logging.F("error", err.Error()))
		return
	}

	discoveredServices := make(map[string]*ServiceInfo)

	for _, key := range keys {
		serviceData, err := sr.redisClient.Get(sr.ctx, key).Result()
		if err != nil {
			continue
		}

		var service ServiceInfo
		if err := json.Unmarshal([]byte(serviceData), &service); err != nil {
			continue
		}

		// Check if service is still alive (within last 90 seconds)
		if time.Since(service.LastSeen) > 90*time.Second {
			service.Health = HealthStatusUnknown
		}

		discoveredServices[service.ID] = &service
	}

	// Update local service registry
	sr.servicesMutex.Lock()
	sr.services = discoveredServices
	sr.servicesMutex.Unlock()
}

// healthCheckLoop performs periodic health checks
func (sr *ServiceRegistry) healthCheckLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sr.ctx.Done():
			return
		case <-ticker.C:
			sr.performHealthChecks()
		}
	}
}

// performHealthChecks performs health checks on all services
func (sr *ServiceRegistry) performHealthChecks() {
	sr.servicesMutex.RLock()
	services := make([]*ServiceInfo, 0, len(sr.services))
	for _, service := range sr.services {
		services = append(services, service)
	}
	sr.servicesMutex.RUnlock()

	for _, service := range services {
		if service.NodeID == sr.nodeID {
			// Only health check our own services
			sr.healthMutex.RLock()
			checker, exists := sr.healthChecks[service.Name]
			sr.healthMutex.RUnlock()

			if exists {
				ctx, cancel := context.WithTimeout(sr.ctx, 10*time.Second)
				health := checker.CheckHealth(ctx, service)
				cancel()

				if health != service.Health {
					service.Health = health
					service.LastSeen = time.Now()
					sr.storeServiceInRedis(service)

					sr.logger.Info("Service health changed",
						logging.F("service_id", service.ID),
						logging.F("health", string(health)),
					)
				}
			}
		}
	}
}

// cleanupLoop removes stale services
func (sr *ServiceRegistry) cleanupLoop() {
	ticker := time.NewTicker(2 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-sr.ctx.Done():
			return
		case <-ticker.C:
			sr.cleanupStaleServices()
		}
	}
}

// cleanupStaleServices removes services that haven't been seen recently
func (sr *ServiceRegistry) cleanupStaleServices() {
	sr.servicesMutex.Lock()
	defer sr.servicesMutex.Unlock()

	staleThreshold := 5 * time.Minute
	now := time.Now()

	for serviceID, service := range sr.services {
		if now.Sub(service.LastSeen) > staleThreshold {
			delete(sr.services, serviceID)
			
			// Remove from Redis if it's our service
			if service.NodeID == sr.nodeID {
				key := fmt.Sprintf("discovery:services:%s", serviceID)
				sr.redisClient.Del(sr.ctx, key)
			}

			sr.logger.Info("Removed stale service",
				logging.F("service_id", serviceID),
				logging.F("last_seen", service.LastSeen),
			)
		}
	}
}

// hasTag checks if a service has a specific tag
func (sr *ServiceRegistry) hasTag(service *ServiceInfo, tag string) bool {
	for _, serviceTag := range service.Tags {
		if serviceTag == tag {
			return true
		}
	}
	return false
}

// NewLoadBalancer creates a new load balancer
func NewLoadBalancer(registry *ServiceRegistry, strategy LoadBalancingStrategy, logger logging.Logger) *LoadBalancer {
	return &LoadBalancer{
		registry: registry,
		strategy: strategy,
		logger:   logger,
	}
}

// SelectService selects a service instance based on the load balancing strategy
func (lb *LoadBalancer) SelectService(serviceName string) (*ServiceInfo, error) {
	services, err := lb.registry.DiscoverServices(serviceName)
	if err != nil {
		return nil, fmt.Errorf("failed to discover services: %w", err)
	}

	if len(services) == 0 {
		return nil, fmt.Errorf("no healthy instances found for service: %s", serviceName)
	}

	switch lb.strategy {
	case StrategyRoundRobin:
		return lb.selectRoundRobin(services), nil
	case StrategyLeastLoad:
		return lb.selectLeastLoad(services), nil
	case StrategyRandom:
		return lb.selectRandom(services), nil
	case StrategyWeighted:
		return lb.selectWeighted(services), nil
	default:
		return lb.selectRoundRobin(services), nil
	}
}

// selectRoundRobin selects a service using round-robin strategy
func (lb *LoadBalancer) selectRoundRobin(services []*ServiceInfo) *ServiceInfo {
	index := int(time.Now().UnixNano()) % len(services)
	return services[index]
}

// selectLeastLoad selects the service with the least load
func (lb *LoadBalancer) selectLeastLoad(services []*ServiceInfo) *ServiceInfo {
	// For now, just return the first service
	// In a real implementation, you would track load metrics
	return services[0]
}

// selectRandom selects a random service
func (lb *LoadBalancer) selectRandom(services []*ServiceInfo) *ServiceInfo {
	index := int(time.Now().UnixNano()) % len(services)
	return services[index]
}

// selectWeighted selects a service based on weights
func (lb *LoadBalancer) selectWeighted(services []*ServiceInfo) *ServiceInfo {
	// For now, just return the first service
	// In a real implementation, you would use weights from metadata
	return services[0]
}

// GetServiceURL returns the full URL for a service
func (lb *LoadBalancer) GetServiceURL(serviceName string) (string, error) {
	service, err := lb.SelectService(serviceName)
	if err != nil {
		return "", err
	}

	protocol := service.Protocol
	if protocol == "" {
		protocol = "http"
	}

	return fmt.Sprintf("%s://%s:%d", protocol, service.Address, service.Port), nil
}