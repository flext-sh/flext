package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/cluster"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/worker"
	"github.com/gorilla/websocket"
)

// AgentMessage represents a message between agents
type AgentMessage struct {
	ID        string                 `json:"id"`
	Type      AgentMessageType       `json:"type"`
	Payload   map[string]interface{} `json:"payload"`
	Timestamp time.Time              `json:"timestamp"`
	SenderID  string                 `json:"sender_id"`
	TargetID  string                 `json:"target_id,omitempty"`
}

// AgentMessageType defines the type of agent message
type AgentMessageType string

const (
	// Job-related messages
	MessageTypeJobSubmit AgentMessageType = "job_submit"
	MessageTypeJobResult AgentMessageType = "job_result"
	MessageTypeJobCancel AgentMessageType = "job_cancel"
	MessageTypeJobStatus AgentMessageType = "job_status"

	// Coordination messages
	MessageTypeHeartbeat  AgentMessageType = "heartbeat"
	MessageTypeElection   AgentMessageType = "election"
	MessageTypeCoordinate AgentMessageType = "coordinate"

	// Data synchronization
	MessageTypeDataSync    AgentMessageType = "data_sync"
	MessageTypeDataRequest AgentMessageType = "data_request"

	// System messages
	MessageTypeShutdown    AgentMessageType = "shutdown"
	MessageTypeHealthCheck AgentMessageType = "health_check"
)

// RemoteAgent manages communication with remote agents
type RemoteAgent struct {
	nodeID           string
	clusterManager   *cluster.ClusterManager
	workerPool       *worker.WorkerPool
	connections      map[string]*AgentConnection
	connectionsMutex sync.RWMutex
	messageHandlers  map[AgentMessageType]MessageHandler
	handlersMutex    sync.RWMutex
	logger           logging.Logger
	ctx              context.Context
	cancel           context.CancelFunc
	upgrader         websocket.Upgrader
}

// AgentConnection represents a connection to a remote agent
type AgentConnection struct {
	NodeID     string
	Conn       *websocket.Conn
	SendChan   chan *AgentMessage
	LastSeen   time.Time
	IsOutbound bool
	mutex      sync.RWMutex
}

// MessageHandler defines the interface for handling agent messages
type MessageHandler interface {
	Handle(ctx context.Context, message *AgentMessage, sender *AgentConnection) error
}

// MessageHandlerFunc is a function adapter for MessageHandler
type MessageHandlerFunc func(ctx context.Context, message *AgentMessage, sender *AgentConnection) error

func (f MessageHandlerFunc) Handle(ctx context.Context, message *AgentMessage, sender *AgentConnection) error {
	return f(ctx, message, sender)
}

// NewRemoteAgent creates a new remote agent
func NewRemoteAgent(nodeID string, clusterManager *cluster.ClusterManager, workerPool *worker.WorkerPool, logger logging.Logger) *RemoteAgent {
	ctx, cancel := context.WithCancel(context.Background())

	agent := &RemoteAgent{
		nodeID:          nodeID,
		clusterManager:  clusterManager,
		workerPool:      workerPool,
		connections:     make(map[string]*AgentConnection),
		messageHandlers: make(map[AgentMessageType]MessageHandler),
		logger:          logger,
		ctx:             ctx,
		cancel:          cancel,
		upgrader: websocket.Upgrader{
			CheckOrigin: func(r *http.Request) bool {
				return true // Allow all origins in development
			},
			ReadBufferSize:  1024,
			WriteBufferSize: 1024,
		},
	}

	// Register default message handlers
	agent.registerDefaultHandlers()

	return agent
}

// Start starts the remote agent
func (ra *RemoteAgent) Start() error {
	ra.logger.Info("Starting remote agent", logging.F("node_id", ra.nodeID))

	// Start connection monitor
	go ra.connectionMonitor()

	// Start auto-discovery and connection
	go ra.autoConnect()

	ra.logger.Info("Remote agent started")
	return nil
}

// Stop stops the remote agent
func (ra *RemoteAgent) Stop() error {
	ra.logger.Info("Stopping remote agent")

	ra.cancel()

	// Close all connections
	ra.connectionsMutex.Lock()
	for _, conn := range ra.connections {
		conn.Conn.Close()
	}
	ra.connectionsMutex.Unlock()

	ra.logger.Info("Remote agent stopped")
	return nil
}

// HandleWebSocket handles incoming WebSocket connections
func (ra *RemoteAgent) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := ra.upgrader.Upgrade(w, r, nil)
	if err != nil {
		ra.logger.Error("Failed to upgrade WebSocket connection", logging.F("error", err.Error()))
		return
	}

	// Get node ID from query parameter or header
	nodeID := r.URL.Query().Get("node_id")
	if nodeID == "" {
		nodeID = r.Header.Get("X-Node-ID")
	}

	if nodeID == "" {
		conn.Close()
		ra.logger.Error("No node ID provided in WebSocket connection")
		return
	}

	ra.handleConnection(nodeID, conn, false)
}

// ConnectTo establishes an outbound connection to a remote agent
func (ra *RemoteAgent) ConnectTo(nodeInfo *cluster.NodeInfo) error {
	if nodeInfo.ID == ra.nodeID {
		return nil // Don't connect to self
	}

	// Check if already connected
	ra.connectionsMutex.RLock()
	_, exists := ra.connections[nodeInfo.ID]
	ra.connectionsMutex.RUnlock()

	if exists {
		return nil // Already connected
	}

	// Establish WebSocket connection
	url := fmt.Sprintf("ws://%s:%d/agent/ws?node_id=%s", nodeInfo.Address, nodeInfo.Port, ra.nodeID)
	conn, _, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		return fmt.Errorf("failed to connect to agent %s: %w", nodeInfo.ID, err)
	}

	ra.handleConnection(nodeInfo.ID, conn, true)
	return nil
}

// handleConnection handles a new agent connection
func (ra *RemoteAgent) handleConnection(nodeID string, conn *websocket.Conn, isOutbound bool) {
	agentConn := &AgentConnection{
		NodeID:     nodeID,
		Conn:       conn,
		SendChan:   make(chan *AgentMessage, 100),
		LastSeen:   time.Now(),
		IsOutbound: isOutbound,
	}

	ra.connectionsMutex.Lock()
	ra.connections[nodeID] = agentConn
	ra.connectionsMutex.Unlock()

	ra.logger.Info("Agent connection established",
		logging.F("node_id", nodeID),
		logging.F("outbound", isOutbound),
	)

	// Start goroutines for this connection
	go ra.readMessages(agentConn)
	go ra.writeMessages(agentConn)
	go ra.pingConnection(agentConn)
}

// readMessages reads messages from an agent connection
func (ra *RemoteAgent) readMessages(conn *AgentConnection) {
	defer ra.closeConnection(conn)

	for {
		select {
		case <-ra.ctx.Done():
			return
		default:
			var message AgentMessage
			err := conn.Conn.ReadJSON(&message)
			if err != nil {
				ra.logger.Error("Failed to read message",
					logging.F("node_id", conn.NodeID),
					logging.F("error", err.Error()),
				)
				return
			}

			conn.mutex.Lock()
			conn.LastSeen = time.Now()
			conn.mutex.Unlock()

			ra.handleMessage(&message, conn)
		}
	}
}

// writeMessages writes messages to an agent connection
func (ra *RemoteAgent) writeMessages(conn *AgentConnection) {
	defer ra.closeConnection(conn)

	for {
		select {
		case <-ra.ctx.Done():
			return
		case message, ok := <-conn.SendChan:
			if !ok {
				return
			}

			err := conn.Conn.WriteJSON(message)
			if err != nil {
				ra.logger.Error("Failed to write message",
					logging.F("node_id", conn.NodeID),
					logging.F("error", err.Error()),
				)
				return
			}
		}
	}
}

// pingConnection sends periodic ping messages
func (ra *RemoteAgent) pingConnection(conn *AgentConnection) {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ra.ctx.Done():
			return
		case <-ticker.C:
			ping := &AgentMessage{
				ID:        fmt.Sprintf("ping-%d", time.Now().UnixNano()),
				Type:      MessageTypeHeartbeat,
				Timestamp: time.Now(),
				SenderID:  ra.nodeID,
				TargetID:  conn.NodeID,
				Payload:   make(map[string]interface{}),
			}

			select {
			case conn.SendChan <- ping:
			default:
				ra.logger.Warn("Send channel full, dropping ping",
					logging.F("node_id", conn.NodeID),
				)
			}
		}
	}
}

// closeConnection closes an agent connection
func (ra *RemoteAgent) closeConnection(conn *AgentConnection) {
	ra.connectionsMutex.Lock()
	delete(ra.connections, conn.NodeID)
	ra.connectionsMutex.Unlock()

	conn.Conn.Close()
	close(conn.SendChan)

	ra.logger.Info("Agent connection closed", logging.F("node_id", conn.NodeID))
}

// handleMessage handles an incoming message
func (ra *RemoteAgent) handleMessage(message *AgentMessage, sender *AgentConnection) {
	ra.handlersMutex.RLock()
	handler, exists := ra.messageHandlers[message.Type]
	ra.handlersMutex.RUnlock()

	if !exists {
		ra.logger.Warn("No handler for message type",
			logging.F("message_type", string(message.Type)),
			logging.F("sender", message.SenderID),
		)
		return
	}

	if err := handler.Handle(ra.ctx, message, sender); err != nil {
		ra.logger.Error("Failed to handle message",
			logging.F("message_type", string(message.Type)),
			logging.F("message_id", message.ID),
			logging.F("error", err.Error()),
		)
	}
}

// RegisterHandler registers a message handler
func (ra *RemoteAgent) RegisterHandler(messageType AgentMessageType, handler MessageHandler) {
	ra.handlersMutex.Lock()
	defer ra.handlersMutex.Unlock()

	ra.messageHandlers[messageType] = handler
}

// SendMessage sends a message to a specific agent
func (ra *RemoteAgent) SendMessage(targetNodeID string, message *AgentMessage) error {
	ra.connectionsMutex.RLock()
	conn, exists := ra.connections[targetNodeID]
	ra.connectionsMutex.RUnlock()

	if !exists {
		return fmt.Errorf("no connection to node %s", targetNodeID)
	}

	message.SenderID = ra.nodeID
	message.TargetID = targetNodeID
	message.Timestamp = time.Now()

	select {
	case conn.SendChan <- message:
		return nil
	default:
		return fmt.Errorf("send channel full for node %s", targetNodeID)
	}
}

// BroadcastMessage sends a message to all connected agents
func (ra *RemoteAgent) BroadcastMessage(message *AgentMessage) {
	ra.connectionsMutex.RLock()
	connections := make([]*AgentConnection, 0, len(ra.connections))
	for _, conn := range ra.connections {
		connections = append(connections, conn)
	}
	ra.connectionsMutex.RUnlock()

	message.SenderID = ra.nodeID
	message.Timestamp = time.Now()

	for _, conn := range connections {
		msg := *message // Copy message
		msg.TargetID = conn.NodeID

		select {
		case conn.SendChan <- &msg:
		default:
			ra.logger.Warn("Send channel full, dropping broadcast",
				logging.F("node_id", conn.NodeID),
			)
		}
	}
}

// connectionMonitor monitors connection health
func (ra *RemoteAgent) connectionMonitor() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-ra.ctx.Done():
			return
		case <-ticker.C:
			ra.checkConnectionHealth()
		}
	}
}

// checkConnectionHealth checks the health of all connections
func (ra *RemoteAgent) checkConnectionHealth() {
	ra.connectionsMutex.Lock()
	defer ra.connectionsMutex.Unlock()

	for nodeID, conn := range ra.connections {
		conn.mutex.RLock()
		lastSeen := conn.LastSeen
		conn.mutex.RUnlock()

		if time.Since(lastSeen) > 2*time.Minute {
			ra.logger.Warn("Connection timeout, closing",
				logging.F("node_id", nodeID),
				logging.F("last_seen", lastSeen),
			)
			conn.Conn.Close()
		}
	}
}

// autoConnect automatically connects to available nodes
func (ra *RemoteAgent) autoConnect() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ra.ctx.Done():
			return
		case <-ticker.C:
			nodes := ra.clusterManager.GetNodes()
			for _, node := range nodes {
				if node.Status == cluster.NodeStatusOnline {
					ra.ConnectTo(node)
				}
			}
		}
	}
}

// registerDefaultHandlers registers default message handlers
func (ra *RemoteAgent) registerDefaultHandlers() {
	ra.registerHeartbeatHandler()
	ra.registerJobSubmissionHandler()
	ra.registerHealthCheckHandler()
}

// registerHeartbeatHandler registers the heartbeat message handler
func (ra *RemoteAgent) registerHeartbeatHandler() {
	ra.RegisterHandler(MessageTypeHeartbeat, MessageHandlerFunc(func(ctx context.Context, message *AgentMessage, sender *AgentConnection) error {
		return nil // Just update last seen time
	}))
}

// registerJobSubmissionHandler registers the job submission message handler
func (ra *RemoteAgent) registerJobSubmissionHandler() {
	ra.RegisterHandler(MessageTypeJobSubmit, MessageHandlerFunc(func(ctx context.Context, message *AgentMessage, sender *AgentConnection) error {
		return ra.handleJobSubmission(message)
	}))
}

// registerHealthCheckHandler registers the health check message handler
func (ra *RemoteAgent) registerHealthCheckHandler() {
	ra.RegisterHandler(MessageTypeHealthCheck, MessageHandlerFunc(func(ctx context.Context, message *AgentMessage, sender *AgentConnection) error {
		return ra.handleHealthCheck(message)
	}))
}

// handleJobSubmission processes job submission messages
func (ra *RemoteAgent) handleJobSubmission(message *AgentMessage) error {
	jobData, err := json.Marshal(message.Payload)
	if err != nil {
		return fmt.Errorf("failed to marshal job data: %w", err)
	}

	var job worker.Job
	if err := json.Unmarshal(jobData, &job); err != nil {
		return fmt.Errorf("failed to unmarshal job: %w", err)
	}

	return ra.workerPool.Submit(&job)
}

// handleHealthCheck processes health check messages
func (ra *RemoteAgent) handleHealthCheck(message *AgentMessage) error {
	metrics := ra.workerPool.GetMetrics()

	response := &AgentMessage{
		ID:       fmt.Sprintf("health-response-%d", time.Now().UnixNano()),
		Type:     MessageTypeHealthCheck,
		Payload:  map[string]interface{}{"metrics": metrics},
		SenderID: ra.nodeID,
		TargetID: message.SenderID,
	}

	return ra.SendMessage(message.SenderID, response)
}

// GetConnections returns all active connections
func (ra *RemoteAgent) GetConnections() map[string]*AgentConnection {
	ra.connectionsMutex.RLock()
	defer ra.connectionsMutex.RUnlock()

	connections := make(map[string]*AgentConnection)
	for id, conn := range ra.connections {
		connections[id] = conn
	}
	return connections
}
