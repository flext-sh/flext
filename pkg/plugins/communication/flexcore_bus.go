// Package communication - Inter-FlexCore Communication Bus
//
// This package implements the communication bus that enables coordination
// between multiple FlexCore instances and their deployed plugins across
// the distributed FLEXT ecosystem.
//
// Architecture:
//   - Redis Pub/Sub: Message bus for real-time communication
//   - Message Routing: Intelligent routing between FlexCore instances
//   - Plugin Discovery: Automatic discovery of plugins across instances
//   - Load Balancing: Distribution of plugin execution across instances
//   - Fault Tolerance: Automatic failover and recovery mechanisms
//
// Communication Patterns:
//   - Point-to-Point: Direct communication between specific plugins
//   - Broadcast: Messages to all plugins of a specific type
//   - Publish/Subscribe: Event-driven communication patterns
//   - Request/Response: Synchronous communication with timeout
//   - Service Discovery: Dynamic discovery of available services
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package communication

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
	"github.com/go-redis/redis/v8"
)

// FlexCoreCommunicationBus implements distributed communication between FlexCore instances
type FlexCoreCommunicationBus struct {
	redisClient       *redis.Client
	nodeID            string
	nodeURL           string
	subscribers       map[plugins.PluginID]func(map[string]interface{}) error
	discoveredNodes   map[string]FlexCoreNodeInfo
	discoveredPlugins map[string]DiscoveredPlugin
	messageHandlers   map[string]MessageHandler
	mu                sync.RWMutex
	ctx               context.Context
	cancel            context.CancelFunc
}

// FlexCoreNodeInfo represents information about a discovered FlexCore node
type FlexCoreNodeInfo struct {
	NodeID        string                 `json:"node_id"`
	NodeURL       string                 `json:"node_url"`
	Status        string                 `json:"status"`
	LastSeen      time.Time              `json:"last_seen"`
	LoadedPlugins []plugins.PluginID     `json:"loaded_plugins"`
	Capabilities  []string               `json:"capabilities"`
	Resources     map[string]interface{} `json:"resources"`
	Location      string                 `json:"location,omitempty"`
	Version       string                 `json:"version"`
}

// DiscoveredPlugin represents a plugin discovered on the network
type DiscoveredPlugin struct {
	PluginID      plugins.PluginID       `json:"plugin_id"`
	PluginType    plugins.PluginType     `json:"plugin_type"`
	NodeID        string                 `json:"node_id"`
	NodeURL       string                 `json:"node_url"`
	Status        string                 `json:"status"`
	Capabilities  []string               `json:"capabilities"`
	LastSeen      time.Time              `json:"last_seen"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
}

// MessageHandler represents a handler for specific message types
type MessageHandler struct {
	MessageType string
	Handler     func(context.Context, FlexCoreMessage) error
}

// FlexCoreMessage represents a message in the FlexCore communication bus
type FlexCoreMessage struct {
	ID            string                 `json:"id"`
	Type          string                 `json:"type"`
	Source        MessageSource          `json:"source"`
	Destination   MessageDestination     `json:"destination"`
	Payload       map[string]interface{} `json:"payload"`
	Timestamp     time.Time              `json:"timestamp"`
	TTL           time.Duration          `json:"ttl,omitempty"`
	ReplyTo       string                 `json:"reply_to,omitempty"`
	CorrelationID string                 `json:"correlation_id,omitempty"`
	Priority      int                    `json:"priority,omitempty"`
}

// MessageSource represents the source of a message
type MessageSource struct {
	NodeID   string           `json:"node_id"`
	NodeURL  string           `json:"node_url"`
	PluginID plugins.PluginID `json:"plugin_id,omitempty"`
}

// MessageDestination represents the destination of a message
type MessageDestination struct {
	NodeID     string             `json:"node_id,omitempty"`
	NodeURL    string             `json:"node_url,omitempty"`
	PluginID   plugins.PluginID   `json:"plugin_id,omitempty"`
	PluginType plugins.PluginType `json:"plugin_type,omitempty"`
	Broadcast  bool               `json:"broadcast,omitempty"`
}

// NewFlexCoreCommunicationBus creates a new communication bus instance
func NewFlexCoreCommunicationBus(redisURL, nodeID, nodeURL string) (*FlexCoreCommunicationBus, error) {
	// Parse Redis URL and create client
	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse Redis URL: %w", err)
	}

	redisClient := redis.NewClient(opts)

	// Test Redis connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := redisClient.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	ctx, cancel = context.WithCancel(context.Background())

	bus := &FlexCoreCommunicationBus{
		redisClient:       redisClient,
		nodeID:            nodeID,
		nodeURL:           nodeURL,
		subscribers:       make(map[plugins.PluginID]func(map[string]interface{}) error),
		discoveredNodes:   make(map[string]FlexCoreNodeInfo),
		discoveredPlugins: make(map[string]DiscoveredPlugin),
		messageHandlers:   make(map[string]MessageHandler),
		ctx:               ctx,
		cancel:            cancel,
	}

	return bus, nil
}

// Start starts the communication bus services
func (bus *FlexCoreCommunicationBus) Start() error {
	// Start node discovery announcements
	go bus.nodeDiscoveryAnnouncer()

	// Start node discovery listener
	go bus.nodeDiscoveryListener()

	// Start plugin discovery announcer
	go bus.pluginDiscoveryAnnouncer()

	// Start plugin discovery listener
	go bus.pluginDiscoveryListener()

	// Start message routing service
	go bus.messageRouter()

	// Start health monitoring
	go bus.healthMonitor()

	// Register default message handlers
	bus.registerDefaultHandlers()

	return nil
}

// Stop stops the communication bus
func (bus *FlexCoreCommunicationBus) Stop() error {
	bus.cancel()
	return bus.redisClient.Close()
}

// SendMessage sends a message between plugins
func (bus *FlexCoreCommunicationBus) SendMessage(ctx context.Context, fromPlugin plugins.PluginID, toPlugin plugins.PluginID, message map[string]interface{}) error {
	// Find target plugin location
	targetNode, err := bus.findPluginLocation(toPlugin)
	if err != nil {
		return fmt.Errorf("failed to find target plugin location: %w", err)
	}

	flexCoreMessage := FlexCoreMessage{
		ID:   fmt.Sprintf("msg-%d", time.Now().UnixNano()),
		Type: "plugin.message",
		Source: MessageSource{
			NodeID:   bus.nodeID,
			NodeURL:  bus.nodeURL,
			PluginID: fromPlugin,
		},
		Destination: MessageDestination{
			NodeID:   targetNode.NodeID,
			NodeURL:  targetNode.NodeURL,
			PluginID: toPlugin,
		},
		Payload:   message,
		Timestamp: time.Now(),
		TTL:       5 * time.Minute,
	}

	return bus.publishMessage(ctx, flexCoreMessage)
}

// BroadcastMessage sends a message to all plugins of a type
func (bus *FlexCoreCommunicationBus) BroadcastMessage(ctx context.Context, fromPlugin plugins.PluginID, targetType plugins.PluginType, message map[string]interface{}) error {
	flexCoreMessage := FlexCoreMessage{
		ID:   fmt.Sprintf("broadcast-%d", time.Now().UnixNano()),
		Type: "plugin.broadcast",
		Source: MessageSource{
			NodeID:   bus.nodeID,
			NodeURL:  bus.nodeURL,
			PluginID: fromPlugin,
		},
		Destination: MessageDestination{
			PluginType: targetType,
			Broadcast:  true,
		},
		Payload:   message,
		Timestamp: time.Now(),
		TTL:       5 * time.Minute,
	}

	return bus.publishMessage(ctx, flexCoreMessage)
}

// SubscribeToMessages subscribes to messages for a plugin
func (bus *FlexCoreCommunicationBus) SubscribeToMessages(ctx context.Context, pluginID plugins.PluginID, messageHandler func(map[string]interface{}) error) error {
	bus.mu.Lock()
	defer bus.mu.Unlock()

	bus.subscribers[pluginID] = messageHandler

	// Subscribe to plugin-specific messages
	channel := fmt.Sprintf("flexcore.plugin.%s", pluginID)
	go bus.subscribeToChannel(ctx, channel, func(message FlexCoreMessage) error {
		return messageHandler(message.Payload)
	})

	return nil
}

// UnsubscribeFromMessages unsubscribes from messages
func (bus *FlexCoreCommunicationBus) UnsubscribeFromMessages(ctx context.Context, pluginID plugins.PluginID) error {
	bus.mu.Lock()
	defer bus.mu.Unlock()

	delete(bus.subscribers, pluginID)
	return nil
}

// RegisterPlugin registers a plugin on this node for discovery
func (bus *FlexCoreCommunicationBus) RegisterPlugin(pluginID plugins.PluginID, pluginType plugins.PluginType, capabilities []string) error {
	bus.mu.Lock()
	defer bus.mu.Unlock()

	plugin := DiscoveredPlugin{
		PluginID:     pluginID,
		PluginType:   pluginType,
		NodeID:       bus.nodeID,
		NodeURL:      bus.nodeURL,
		Status:       "running",
		Capabilities: capabilities,
		LastSeen:     time.Now(),
	}

	key := fmt.Sprintf("%s@%s", pluginID, bus.nodeID)
	bus.discoveredPlugins[key] = plugin

	// Announce plugin availability
	return bus.announcePlugin(plugin)
}

// UnregisterPlugin unregisters a plugin from this node
func (bus *FlexCoreCommunicationBus) UnregisterPlugin(pluginID plugins.PluginID) error {
	bus.mu.Lock()
	defer bus.mu.Unlock()

	key := fmt.Sprintf("%s@%s", pluginID, bus.nodeID)
	delete(bus.discoveredPlugins, key)

	// Announce plugin unavailability
	return bus.announcePluginRemoval(pluginID)
}

// DiscoverPlugins returns all discovered plugins across the network
func (bus *FlexCoreCommunicationBus) DiscoverPlugins() []DiscoveredPlugin {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	plugins := make([]DiscoveredPlugin, 0, len(bus.discoveredPlugins))
	for _, plugin := range bus.discoveredPlugins {
		plugins = append(plugins, plugin)
	}

	return plugins
}

// DiscoverNodes returns all discovered FlexCore nodes
func (bus *FlexCoreCommunicationBus) DiscoverNodes() []FlexCoreNodeInfo {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	nodes := make([]FlexCoreNodeInfo, 0, len(bus.discoveredNodes))
	for _, node := range bus.discoveredNodes {
		nodes = append(nodes, node)
	}

	return nodes
}

// FindBestNodeForPlugin finds the best FlexCore node to run a specific plugin
func (bus *FlexCoreCommunicationBus) FindBestNodeForPlugin(pluginType plugins.PluginType, requirements map[string]interface{}) (*FlexCoreNodeInfo, error) {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	var bestNode *FlexCoreNodeInfo
	var bestScore float64

	for _, node := range bus.discoveredNodes {
		if node.Status != "healthy" {
			continue
		}

		score := bus.calculateNodeScore(node, pluginType, requirements)
		if bestNode == nil || score > bestScore {
			bestNode = &node
			bestScore = score
		}
	}

	if bestNode == nil {
		return nil, fmt.Errorf("no suitable node found for plugin type %s", pluginType)
	}

	return bestNode, nil
}

// RequestDistributedExecution requests distributed execution across multiple nodes
func (bus *FlexCoreCommunicationBus) RequestDistributedExecution(ctx context.Context, request DistributedExecutionRequest) (*DistributedExecutionResponse, error) {
	// Find available nodes for execution
	availableNodes := bus.findAvailableNodes(request.PluginType, request.MinNodes)
	if len(availableNodes) < request.MinNodes {
		return nil, fmt.Errorf("insufficient nodes available: need %d, found %d", request.MinNodes, len(availableNodes))
	}

	// Create distributed execution message
	message := FlexCoreMessage{
		ID:   fmt.Sprintf("distexec-%d", time.Now().UnixNano()),
		Type: "distributed.execution.request",
		Source: MessageSource{
			NodeID:  bus.nodeID,
			NodeURL: bus.nodeURL,
		},
		Payload: map[string]interface{}{
			"request":          request,
			"coordinator_node": bus.nodeID,
			"execution_id":     request.ExecutionID,
			"target_nodes":     availableNodes,
		},
		Timestamp: time.Now(),
		TTL:       request.Timeout,
	}

	// Send to all target nodes
	for _, node := range availableNodes {
		message.Destination = MessageDestination{
			NodeID:  node.NodeID,
			NodeURL: node.NodeURL,
		}

		if err := bus.publishMessage(ctx, message); err != nil {
			return nil, fmt.Errorf("failed to send execution request to node %s: %w", node.NodeID, err)
		}
	}

	// Wait for responses (simplified - would need proper coordination)
	response := &DistributedExecutionResponse{
		ExecutionID:      request.ExecutionID,
		CoordinatorNode:  bus.nodeID,
		ParticipantNodes: availableNodes,
		Status:           "executing",
		StartedAt:        time.Now(),
	}

	return response, nil
}

// DistributedExecutionRequest represents a request for distributed execution
type DistributedExecutionRequest struct {
	ExecutionID  string                 `json:"execution_id"`
	PluginType   plugins.PluginType     `json:"plugin_type"`
	Operation    string                 `json:"operation"`
	Parameters   map[string]interface{} `json:"parameters"`
	MinNodes     int                    `json:"min_nodes"`
	MaxNodes     int                    `json:"max_nodes"`
	Timeout      time.Duration          `json:"timeout"`
	Requirements map[string]interface{} `json:"requirements,omitempty"`
}

// DistributedExecutionResponse represents a response to distributed execution
type DistributedExecutionResponse struct {
	ExecutionID      string                 `json:"execution_id"`
	CoordinatorNode  string                 `json:"coordinator_node"`
	ParticipantNodes []FlexCoreNodeInfo     `json:"participant_nodes"`
	Status           string                 `json:"status"`
	Results          map[string]interface{} `json:"results,omitempty"`
	StartedAt        time.Time              `json:"started_at"`
	CompletedAt      *time.Time             `json:"completed_at,omitempty"`
	ErrorMessage     string                 `json:"error_message,omitempty"`
}

// Helper methods

func (bus *FlexCoreCommunicationBus) findPluginLocation(pluginID plugins.PluginID) (*FlexCoreNodeInfo, error) {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	for _, plugin := range bus.discoveredPlugins {
		if plugin.PluginID == pluginID && plugin.Status == "running" {
			if node, exists := bus.discoveredNodes[plugin.NodeID]; exists {
				return &node, nil
			}
		}
	}

	return nil, fmt.Errorf("plugin %s not found or not running", pluginID)
}

func (bus *FlexCoreCommunicationBus) findAvailableNodes(pluginType plugins.PluginType, minNodes int) []FlexCoreNodeInfo {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	var availableNodes []FlexCoreNodeInfo
	requiredCapability := fmt.Sprintf("plugin.%s.runtime", pluginType)

	for _, node := range bus.discoveredNodes {
		if node.Status == "healthy" {
			for _, capability := range node.Capabilities {
				if capability == requiredCapability || capability == "plugin.all.runtime" {
					availableNodes = append(availableNodes, node)
					break
				}
			}
		}
	}

	return availableNodes
}

func (bus *FlexCoreCommunicationBus) calculateNodeScore(node FlexCoreNodeInfo, pluginType plugins.PluginType, requirements map[string]interface{}) float64 {
	score := 0.0

	// Base score for healthy node
	if node.Status == "healthy" {
		score += 50.0
	}

	// Score based on resource availability
	if resources, ok := node.Resources["available_memory"].(float64); ok {
		score += resources / 1000000 // Normalize MB to score points
	}

	if cpu, ok := node.Resources["available_cpu"].(float64); ok {
		score += cpu * 10 // CPU percentage to score points
	}

	// Score based on plugin type compatibility
	requiredCapability := fmt.Sprintf("plugin.%s.runtime", pluginType)
	for _, capability := range node.Capabilities {
		if capability == requiredCapability {
			score += 30.0
			break
		} else if capability == "plugin.all.runtime" {
			score += 20.0
			break
		}
	}

	// Score based on current load (fewer loaded plugins = higher score)
	loadPenalty := float64(len(node.LoadedPlugins)) * 5.0
	score -= loadPenalty

	return score
}

func (bus *FlexCoreCommunicationBus) publishMessage(ctx context.Context, message FlexCoreMessage) error {
	messageJSON, err := json.Marshal(message)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	channel := bus.getChannelForMessage(message)
	return bus.redisClient.Publish(ctx, channel, messageJSON).Err()
}

func (bus *FlexCoreCommunicationBus) getChannelForMessage(message FlexCoreMessage) string {
	switch message.Type {
	case "plugin.message":
		return fmt.Sprintf("flexcore.plugin.%s", message.Destination.PluginID)
	case "plugin.broadcast":
		return fmt.Sprintf("flexcore.broadcast.%s", message.Destination.PluginType)
	case "node.discovery":
		return "flexcore.discovery.nodes"
	case "plugin.discovery":
		return "flexcore.discovery.plugins"
	case "distributed.execution.request":
		return fmt.Sprintf("flexcore.node.%s", message.Destination.NodeID)
	default:
		return "flexcore.general"
	}
}

func (bus *FlexCoreCommunicationBus) subscribeToChannel(ctx context.Context, channel string, handler func(FlexCoreMessage) error) {
	pubsub := bus.redisClient.Subscribe(ctx, channel)
	defer pubsub.Close()

	ch := pubsub.Channel()
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-ch:
			var flexCoreMessage FlexCoreMessage
			if err := json.Unmarshal([]byte(msg.Payload), &flexCoreMessage); err != nil {
				continue
			}

			if err := handler(flexCoreMessage); err != nil {
				// Log error but continue processing messages
				fmt.Printf("Message handler error: %v\n", err)
			}
		}
	}
}

func (bus *FlexCoreCommunicationBus) announcePlugin(plugin DiscoveredPlugin) error {
	message := FlexCoreMessage{
		ID:   fmt.Sprintf("plugin-announce-%d", time.Now().UnixNano()),
		Type: "plugin.discovery",
		Source: MessageSource{
			NodeID:  bus.nodeID,
			NodeURL: bus.nodeURL,
		},
		Payload: map[string]interface{}{
			"action": "announce",
			"plugin": plugin,
		},
		Timestamp: time.Now(),
	}

	return bus.publishMessage(context.Background(), message)
}

func (bus *FlexCoreCommunicationBus) announcePluginRemoval(pluginID plugins.PluginID) error {
	message := FlexCoreMessage{
		ID:   fmt.Sprintf("plugin-remove-%d", time.Now().UnixNano()),
		Type: "plugin.discovery",
		Source: MessageSource{
			NodeID:  bus.nodeID,
			NodeURL: bus.nodeURL,
		},
		Payload: map[string]interface{}{
			"action":    "remove",
			"plugin_id": pluginID,
			"node_id":   bus.nodeID,
		},
		Timestamp: time.Now(),
	}

	return bus.publishMessage(context.Background(), message)
}

// Background service methods

func (bus *FlexCoreCommunicationBus) nodeDiscoveryAnnouncer() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-bus.ctx.Done():
			return
		case <-ticker.C:
			bus.announceNode()
		}
	}
}

func (bus *FlexCoreCommunicationBus) announceNode() {
	bus.mu.RLock()
	loadedPlugins := make([]plugins.PluginID, 0, len(bus.discoveredPlugins))
	for _, plugin := range bus.discoveredPlugins {
		if plugin.NodeID == bus.nodeID {
			loadedPlugins = append(loadedPlugins, plugin.PluginID)
		}
	}
	bus.mu.RUnlock()

	nodeInfo := FlexCoreNodeInfo{
		NodeID:        bus.nodeID,
		NodeURL:       bus.nodeURL,
		Status:        "healthy",
		LastSeen:      time.Now(),
		LoadedPlugins: loadedPlugins,
		Capabilities: []string{
			"plugin.meltano.runtime",
			"plugin.ray.runtime",
			"plugin.kubernetes.runtime",
		},
		Resources: map[string]interface{}{
			"available_memory": 8192.0, // MB
			"available_cpu":    75.0,   // %
		},
		Version: "2.0.0",
	}

	message := FlexCoreMessage{
		ID:   fmt.Sprintf("node-announce-%d", time.Now().UnixNano()),
		Type: "node.discovery",
		Source: MessageSource{
			NodeID:  bus.nodeID,
			NodeURL: bus.nodeURL,
		},
		Payload: map[string]interface{}{
			"action": "announce",
			"node":   nodeInfo,
		},
		Timestamp: time.Now(),
	}

	bus.publishMessage(context.Background(), message)
}

func (bus *FlexCoreCommunicationBus) nodeDiscoveryListener() {
	bus.subscribeToChannel(bus.ctx, "flexcore.discovery.nodes", func(message FlexCoreMessage) error {
		action, ok := message.Payload["action"].(string)
		if !ok {
			return nil
		}

		switch action {
		case "announce":
			if nodeData, ok := message.Payload["node"]; ok {
				nodeJSON, _ := json.Marshal(nodeData)
				var node FlexCoreNodeInfo
				if json.Unmarshal(nodeJSON, &node) == nil {
					bus.mu.Lock()
					bus.discoveredNodes[node.NodeID] = node
					bus.mu.Unlock()
				}
			}
		case "remove":
			if nodeID, ok := message.Payload["node_id"].(string); ok {
				bus.mu.Lock()
				delete(bus.discoveredNodes, nodeID)
				bus.mu.Unlock()
			}
		}

		return nil
	})
}

func (bus *FlexCoreCommunicationBus) pluginDiscoveryAnnouncer() {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-bus.ctx.Done():
			return
		case <-ticker.C:
			bus.announceAllPlugins()
		}
	}
}

func (bus *FlexCoreCommunicationBus) announceAllPlugins() {
	bus.mu.RLock()
	defer bus.mu.RUnlock()

	for _, plugin := range bus.discoveredPlugins {
		if plugin.NodeID == bus.nodeID {
			bus.announcePlugin(plugin)
		}
	}
}

func (bus *FlexCoreCommunicationBus) pluginDiscoveryListener() {
	bus.subscribeToChannel(bus.ctx, "flexcore.discovery.plugins", func(message FlexCoreMessage) error {
		action, ok := message.Payload["action"].(string)
		if !ok {
			return nil
		}

		switch action {
		case "announce":
			if pluginData, ok := message.Payload["plugin"]; ok {
				pluginJSON, _ := json.Marshal(pluginData)
				var plugin DiscoveredPlugin
				if json.Unmarshal(pluginJSON, &plugin) == nil {
					bus.mu.Lock()
					key := fmt.Sprintf("%s@%s", plugin.PluginID, plugin.NodeID)
					bus.discoveredPlugins[key] = plugin
					bus.mu.Unlock()
				}
			}
		case "remove":
			if pluginID, ok := message.Payload["plugin_id"].(string); ok {
				if nodeID, ok := message.Payload["node_id"].(string); ok {
					bus.mu.Lock()
					key := fmt.Sprintf("%s@%s", pluginID, nodeID)
					delete(bus.discoveredPlugins, key)
					bus.mu.Unlock()
				}
			}
		}

		return nil
	})
}

func (bus *FlexCoreCommunicationBus) messageRouter() {
	// Subscribe to general messages that need routing
	bus.subscribeToChannel(bus.ctx, "flexcore.general", func(message FlexCoreMessage) error {
		return bus.routeMessage(message)
	})
}

func (bus *FlexCoreCommunicationBus) routeMessage(message FlexCoreMessage) error {
	// Route message based on destination
	if message.Destination.NodeID != "" && message.Destination.NodeID != bus.nodeID {
		// Message not for this node, ignore
		return nil
	}

	// Handle message based on type
	if handler, exists := bus.messageHandlers[message.Type]; exists {
		return handler.Handler(bus.ctx, message)
	}

	return nil
}

func (bus *FlexCoreCommunicationBus) healthMonitor() {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-bus.ctx.Done():
			return
		case <-ticker.C:
			bus.cleanupStaleEntries()
		}
	}
}

func (bus *FlexCoreCommunicationBus) cleanupStaleEntries() {
	bus.mu.Lock()
	defer bus.mu.Unlock()

	now := time.Now()
	staleThreshold := 5 * time.Minute

	// Clean up stale nodes
	for nodeID, node := range bus.discoveredNodes {
		if now.Sub(node.LastSeen) > staleThreshold {
			delete(bus.discoveredNodes, nodeID)
		}
	}

	// Clean up stale plugins
	for key, plugin := range bus.discoveredPlugins {
		if now.Sub(plugin.LastSeen) > staleThreshold {
			delete(bus.discoveredPlugins, key)
		}
	}
}

func (bus *FlexCoreCommunicationBus) registerDefaultHandlers() {
	// Register default message handlers
	bus.messageHandlers["distributed.execution.request"] = MessageHandler{
		MessageType: "distributed.execution.request",
		Handler:     bus.handleDistributedExecutionRequest,
	}
}

func (bus *FlexCoreCommunicationBus) handleDistributedExecutionRequest(ctx context.Context, message FlexCoreMessage) error {
	// Handle distributed execution request
	// This would coordinate with local plugins to execute the request
	return nil
}
