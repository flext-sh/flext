package cluster

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
)

// NodeInfo represents information about a cluster node
type NodeInfo struct {
	ID           string            `json:"id"`
	Address      string            `json:"address"`
	Port         int               `json:"port"`
	Status       NodeStatus        `json:"status"`
	LastSeen     time.Time         `json:"last_seen"`
	Capabilities []string          `json:"capabilities"`
	Metadata     map[string]string `json:"metadata"`
	LoadFactor   float64           `json:"load_factor"`
	MaxJobs      int               `json:"max_jobs"`
	ActiveJobs   int               `json:"active_jobs"`
}

// NodeStatus represents the status of a cluster node
type NodeStatus string

const (
	NodeStatusOnline  NodeStatus = "online"
	NodeStatusOffline NodeStatus = "offline"
	NodeStatusDraining NodeStatus = "draining"
	NodeStatusBusy    NodeStatus = "busy"
)

// ClusterManager manages cluster operations
type ClusterManager struct {
	nodeID       string
	nodeInfo     *NodeInfo
	redisClient  *redis.Client
	logger       logging.Logger
	nodes        map[string]*NodeInfo
	nodesMutex   sync.RWMutex
	ctx          context.Context
	cancel       context.CancelFunc
	healthTicker *time.Ticker
}

// NewClusterManager creates a new cluster manager
func NewClusterManager(nodeID string, redisClient *redis.Client, logger logging.Logger) *ClusterManager {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &ClusterManager{
		nodeID:      nodeID,
		redisClient: redisClient,
		logger:      logger,
		nodes:       make(map[string]*NodeInfo),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start starts the cluster manager
func (cm *ClusterManager) Start(nodeInfo *NodeInfo) error {
	cm.nodeInfo = nodeInfo
	cm.nodeInfo.ID = cm.nodeID
	cm.nodeInfo.Status = NodeStatusOnline
	cm.nodeInfo.LastSeen = time.Now()

	// Register this node in the cluster
	if err := cm.registerNode(); err != nil {
		return fmt.Errorf("failed to register node: %w", err)
	}

	// Start health check ticker
	cm.healthTicker = time.NewTicker(15 * time.Second)
	go cm.healthCheckLoop()

	// Start node discovery
	go cm.nodeDiscoveryLoop()

	cm.logger.Info("Cluster manager started",
		logging.F("node_id", cm.nodeID),
		logging.F("address", nodeInfo.Address),
		logging.F("port", nodeInfo.Port),
	)

	return nil
}

// Stop stops the cluster manager
func (cm *ClusterManager) Stop() error {
	if cm.healthTicker != nil {
		cm.healthTicker.Stop()
	}
	
	cm.cancel()

	// Unregister this node
	if err := cm.unregisterNode(); err != nil {
		cm.logger.Error("Failed to unregister node", logging.F("error", err.Error()))
	}

	cm.logger.Info("Cluster manager stopped")
	return nil
}

// registerNode registers this node in the cluster
func (cm *ClusterManager) registerNode() error {
	nodeData, err := json.Marshal(cm.nodeInfo)
	if err != nil {
		return fmt.Errorf("failed to marshal node info: %w", err)
	}

	key := fmt.Sprintf("cluster:nodes:%s", cm.nodeID)
	err = cm.redisClient.Set(cm.ctx, key, nodeData, 30*time.Second).Err()
	if err != nil {
		return fmt.Errorf("failed to register node in Redis: %w", err)
	}

	return nil
}

// unregisterNode removes this node from the cluster
func (cm *ClusterManager) unregisterNode() error {
	key := fmt.Sprintf("cluster:nodes:%s", cm.nodeID)
	err := cm.redisClient.Del(cm.ctx, key).Err()
	if err != nil {
		return fmt.Errorf("failed to unregister node from Redis: %w", err)
	}

	return nil
}

// healthCheckLoop runs periodic health checks
func (cm *ClusterManager) healthCheckLoop() {
	for {
		select {
		case <-cm.ctx.Done():
			return
		case <-cm.healthTicker.C:
			cm.updateNodeHealth()
		}
	}
}

// updateNodeHealth updates this node's health status
func (cm *ClusterManager) updateNodeHealth() {
	cm.nodeInfo.LastSeen = time.Now()
	
	// Update load factor based on active jobs
	if cm.nodeInfo.MaxJobs > 0 {
		cm.nodeInfo.LoadFactor = float64(cm.nodeInfo.ActiveJobs) / float64(cm.nodeInfo.MaxJobs)
	}

	if err := cm.registerNode(); err != nil {
		cm.logger.Error("Failed to update node health", logging.F("error", err.Error()))
	}
}

// nodeDiscoveryLoop discovers other nodes in the cluster
func (cm *ClusterManager) nodeDiscoveryLoop() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-cm.ctx.Done():
			return
		case <-ticker.C:
			cm.discoverNodes()
		}
	}
}

// discoverNodes discovers and updates information about cluster nodes
func (cm *ClusterManager) discoverNodes() {
	keys, err := cm.getClusterNodeKeys()
	if err != nil {
		return
	}

	cm.nodesMutex.Lock()
	defer cm.nodesMutex.Unlock()

	cm.removeOfflineNodes(keys)
	cm.updateNodeInformation(keys)
}

// getClusterNodeKeys retrieves all cluster node keys from Redis
func (cm *ClusterManager) getClusterNodeKeys() ([]string, error) {
	keys, err := cm.redisClient.Keys(cm.ctx, "cluster:nodes:*").Result()
	if err != nil {
		cm.logger.Error("Failed to discover nodes", logging.F("error", err.Error()))
		return nil, err
	}
	return keys, nil
}

// removeOfflineNodes removes nodes that are no longer present in Redis
func (cm *ClusterManager) removeOfflineNodes(keys []string) {
	keySet := make(map[string]bool)
	for _, key := range keys {
		keySet[key] = true
	}

	for nodeID := range cm.nodes {
		expectedKey := fmt.Sprintf("cluster:nodes:%s", nodeID)
		if !keySet[expectedKey] {
			delete(cm.nodes, nodeID)
		}
	}
}

// updateNodeInformation updates information for all discovered nodes
func (cm *ClusterManager) updateNodeInformation(keys []string) {
	for _, key := range keys {
		nodeInfo := cm.fetchAndParseNodeInfo(key)
		if nodeInfo != nil {
			cm.updateNodeStatus(nodeInfo)
			cm.nodes[nodeInfo.ID] = nodeInfo
		}
	}
}

// fetchAndParseNodeInfo fetches and parses node information from Redis
func (cm *ClusterManager) fetchAndParseNodeInfo(key string) *NodeInfo {
	nodeData, err := cm.redisClient.Get(cm.ctx, key).Result()
	if err != nil {
		return nil
	}

	var nodeInfo NodeInfo
	if err := json.Unmarshal([]byte(nodeData), &nodeInfo); err != nil {
		return nil
	}

	return &nodeInfo
}

// updateNodeStatus updates the status of a node based on its last seen time
func (cm *ClusterManager) updateNodeStatus(nodeInfo *NodeInfo) {
	if time.Since(nodeInfo.LastSeen) > 45*time.Second {
		nodeInfo.Status = NodeStatusOffline
	}
}

// GetNodes returns all discovered nodes
func (cm *ClusterManager) GetNodes() map[string]*NodeInfo {
	cm.nodesMutex.RLock()
	defer cm.nodesMutex.RUnlock()

	nodes := make(map[string]*NodeInfo)
	for id, info := range cm.nodes {
		nodes[id] = info
	}
	return nodes
}

// GetAvailableNodes returns nodes that are available for work
func (cm *ClusterManager) GetAvailableNodes() []*NodeInfo {
	cm.nodesMutex.RLock()
	defer cm.nodesMutex.RUnlock()

	var available []*NodeInfo
	for _, node := range cm.nodes {
		if node.Status == NodeStatusOnline && node.LoadFactor < 0.8 {
			available = append(available, node)
		}
	}
	return available
}

// FindBestNode finds the best node for a given job based on capabilities and load
func (cm *ClusterManager) FindBestNode(requiredCapabilities []string) *NodeInfo {
	available := cm.GetAvailableNodes()
	
	var bestNode *NodeInfo
	bestScore := -1.0

	for _, node := range available {
		if cm.hasCapabilities(node, requiredCapabilities) {
			// Score based on inverse load factor (lower load = higher score)
			score := 1.0 - node.LoadFactor
			if score > bestScore {
				bestScore = score
				bestNode = node
			}
		}
	}

	return bestNode
}

// hasCapabilities checks if a node has all required capabilities
func (cm *ClusterManager) hasCapabilities(node *NodeInfo, required []string) bool {
	nodeCapabilities := make(map[string]bool)
	for _, cap := range node.Capabilities {
		nodeCapabilities[cap] = true
	}

	for _, req := range required {
		if !nodeCapabilities[req] {
			return false
		}
	}
	return true
}

// UpdateNodeStatus updates this node's status
func (cm *ClusterManager) UpdateNodeStatus(status NodeStatus) {
	cm.nodeInfo.Status = status
	cm.updateNodeHealth()
}

// UpdateActiveJobs updates the number of active jobs on this node
func (cm *ClusterManager) UpdateActiveJobs(activeJobs int) {
	cm.nodeInfo.ActiveJobs = activeJobs
	cm.updateNodeHealth()
}

// GetNodeID returns this node's ID
func (cm *ClusterManager) GetNodeID() string {
	return cm.nodeID
}

// GetNodeInfo returns this node's information
func (cm *ClusterManager) GetNodeInfo() *NodeInfo {
	return cm.nodeInfo
}

// IsLeader determines if this node should act as the cluster leader
func (cm *ClusterManager) IsLeader() bool {
	nodes := cm.GetNodes()
	var sortedNodes []*NodeInfo
	
	for _, node := range nodes {
		if node.Status == NodeStatusOnline {
			sortedNodes = append(sortedNodes, node)
		}
	}

	if len(sortedNodes) == 0 {
		return true // Only node, so it's the leader
	}

	// Simple leader election: node with lexicographically smallest ID
	leaderID := sortedNodes[0].ID
	for _, node := range sortedNodes {
		if node.ID < leaderID {
			leaderID = node.ID
		}
	}

	return cm.nodeID == leaderID
}