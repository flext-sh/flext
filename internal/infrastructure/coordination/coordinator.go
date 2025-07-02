package coordination

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/agent"
	"github.com/flext-sh/flext/internal/infrastructure/cluster"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/worker"
	"github.com/go-redis/redis/v8"
)

// DistributedTask represents a task that can be distributed across the cluster
type DistributedTask struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`
	Payload     map[string]interface{} `json:"payload"`
	Priority    int                    `json:"priority"`
	Sharding    ShardingStrategy       `json:"sharding"`
	Dependencies []string              `json:"dependencies"`
	MaxNodes    int                    `json:"max_nodes"`
	CreatedAt   time.Time              `json:"created_at"`
	Deadline    time.Time              `json:"deadline,omitempty"`
	Status      TaskStatus             `json:"status"`
	AssignedTo  string                 `json:"assigned_to,omitempty"`
	Result      map[string]interface{} `json:"result,omitempty"`
	Error       string                 `json:"error,omitempty"`
}

// TaskStatus represents the status of a distributed task
type TaskStatus string

const (
	TaskStatusPending    TaskStatus = "pending"
	TaskStatusAssigned   TaskStatus = "assigned"
	TaskStatusRunning    TaskStatus = "running"
	TaskStatusCompleted  TaskStatus = "completed"
	TaskStatusFailed     TaskStatus = "failed"
	TaskStatusCancelled  TaskStatus = "cancelled"
)

// ShardingStrategy defines how tasks should be distributed
type ShardingStrategy string

const (
	ShardingNone     ShardingStrategy = "none"      // No sharding, run on single node
	ShardingRoundRobin ShardingStrategy = "round_robin" // Distribute evenly
	ShardingCapability ShardingStrategy = "capability" // Based on node capabilities
	ShardingLoad       ShardingStrategy = "load"       // Based on current load
)

// LeaderElection manages leader election for the cluster
type LeaderElection struct {
	nodeID       string
	redisClient  *redis.Client
	logger       logging.Logger
	isLeader     bool
	leaderTerm   int64
	mutex        sync.RWMutex
	ctx          context.Context
	cancel       context.CancelFunc
}

// Coordinator manages distributed task coordination
type Coordinator struct {
	nodeID          string
	clusterManager  *cluster.ClusterManager
	remoteAgent     *agent.RemoteAgent
	workerPool      *worker.WorkerPool
	redisClient     *redis.Client
	logger          logging.Logger
	leaderElection  *LeaderElection
	pendingTasks    map[string]*DistributedTask
	runningTasks    map[string]*DistributedTask
	taskHandlers    map[string]TaskHandler
	mutex           sync.RWMutex
	ctx             context.Context
	cancel          context.CancelFunc
}

// TaskHandler defines the interface for handling distributed tasks
type TaskHandler interface {
	Handle(ctx context.Context, task *DistributedTask) (map[string]interface{}, error)
	CanHandle(taskType string) bool
	RequiredCapabilities() []string
}

// NewCoordinator creates a new distributed coordinator
func NewCoordinator(
	nodeID string,
	clusterManager *cluster.ClusterManager,
	remoteAgent *agent.RemoteAgent,
	workerPool *worker.WorkerPool,
	redisClient *redis.Client,
	logger logging.Logger,
) *Coordinator {
	ctx, cancel := context.WithCancel(context.Background())

	return &Coordinator{
		nodeID:          nodeID,
		clusterManager:  clusterManager,
		remoteAgent:     remoteAgent,
		workerPool:      workerPool,
		redisClient:     redisClient,
		logger:          logger,
		leaderElection:  NewLeaderElection(nodeID, redisClient, logger),
		pendingTasks:    make(map[string]*DistributedTask),
		runningTasks:    make(map[string]*DistributedTask),
		taskHandlers:    make(map[string]TaskHandler),
		ctx:             ctx,
		cancel:          cancel,
	}
}

// NewLeaderElection creates a new leader election manager
func NewLeaderElection(nodeID string, redisClient *redis.Client, logger logging.Logger) *LeaderElection {
	ctx, cancel := context.WithCancel(context.Background())

	return &LeaderElection{
		nodeID:      nodeID,
		redisClient: redisClient,
		logger:      logger,
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start starts the coordinator
func (c *Coordinator) Start() error {
	c.logger.Info("Starting distributed coordinator", logging.F("node_id", c.nodeID))

	// Start leader election
	if err := c.leaderElection.Start(); err != nil {
		return fmt.Errorf("failed to start leader election: %w", err)
	}

	// Register message handlers for coordination
	c.registerMessageHandlers()

	// Start task scheduler
	go c.taskScheduler()

	// Start task monitor
	go c.taskMonitor()

	// Start distributed task processing
	go c.processDistributedTasks()

	c.logger.Info("Distributed coordinator started")
	return nil
}

// Stop stops the coordinator
func (c *Coordinator) Stop() error {
	c.logger.Info("Stopping distributed coordinator")

	c.cancel()
	c.leaderElection.Stop()

	c.logger.Info("Distributed coordinator stopped")
	return nil
}

// SubmitTask submits a distributed task
func (c *Coordinator) SubmitTask(task *DistributedTask) error {
	if task.CreatedAt.IsZero() {
		task.CreatedAt = time.Now()
	}
	task.Status = TaskStatusPending

	// Store task in Redis for persistence
	taskData, err := json.Marshal(task)
	if err != nil {
		return fmt.Errorf("failed to marshal task: %w", err)
	}

	key := fmt.Sprintf("coordination:tasks:%s", task.ID)
	err = c.redisClient.Set(c.ctx, key, taskData, 24*time.Hour).Err()
	if err != nil {
		return fmt.Errorf("failed to store task in Redis: %w", err)
	}

	// Add to pending tasks locally
	c.mutex.Lock()
	c.pendingTasks[task.ID] = task
	c.mutex.Unlock()

	c.logger.Info("Distributed task submitted",
		logging.F("task_id", task.ID),
		logging.F("task_type", task.Type),
		logging.F("sharding", string(task.Sharding)),
	)

	return nil
}

// RegisterTaskHandler registers a handler for distributed tasks
func (c *Coordinator) RegisterTaskHandler(taskType string, handler TaskHandler) {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	c.taskHandlers[taskType] = handler
	c.logger.Info("Task handler registered", logging.F("task_type", taskType))
}

// taskScheduler schedules pending tasks to available nodes
func (c *Coordinator) taskScheduler() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-c.ctx.Done():
			return
		case <-ticker.C:
			if c.leaderElection.IsLeader() {
				c.schedulePendingTasks()
			}
		}
	}
}

// schedulePendingTasks schedules pending tasks based on their sharding strategy
func (c *Coordinator) schedulePendingTasks() {
	c.mutex.Lock()
	tasksToSchedule := make([]*DistributedTask, 0, len(c.pendingTasks))
	for _, task := range c.pendingTasks {
		tasksToSchedule = append(tasksToSchedule, task)
	}
	c.mutex.Unlock()

	for _, task := range tasksToSchedule {
		if err := c.scheduleTask(task); err != nil {
			c.logger.Error("Failed to schedule task",
				logging.F("task_id", task.ID),
				logging.F("error", err.Error()),
			)
		}
	}
}

// scheduleTask schedules a single task to an appropriate node
func (c *Coordinator) scheduleTask(task *DistributedTask) error {
	// Find available nodes
	availableNodes := c.clusterManager.GetAvailableNodes()
	if len(availableNodes) == 0 {
		return fmt.Errorf("no available nodes for task %s", task.ID)
	}

	// Check task handler availability
	c.mutex.RLock()
	handler, exists := c.taskHandlers[task.Type]
	c.mutex.RUnlock()

	var requiredCapabilities []string
	if exists {
		requiredCapabilities = handler.RequiredCapabilities()
	}

	var targetNode *cluster.NodeInfo

	switch task.Sharding {
	case ShardingNone, ShardingLoad:
		targetNode = c.clusterManager.FindBestNode(requiredCapabilities)
	case ShardingRoundRobin:
		targetNode = c.selectRoundRobinNode(availableNodes, requiredCapabilities)
	case ShardingCapability:
		targetNode = c.selectCapabilityNode(availableNodes, requiredCapabilities)
	default:
		targetNode = c.clusterManager.FindBestNode(requiredCapabilities)
	}

	if targetNode == nil {
		return fmt.Errorf("no suitable node found for task %s", task.ID)
	}

	// Assign task to node
	task.Status = TaskStatusAssigned
	task.AssignedTo = targetNode.ID

	// Update task in Redis
	if err := c.updateTaskInRedis(task); err != nil {
		return fmt.Errorf("failed to update task in Redis: %w", err)
	}

	// Send task to assigned node
	if targetNode.ID == c.nodeID {
		// Execute locally
		c.executeTaskLocally(task)
	} else {
		// Send to remote node
		message := &agent.AgentMessage{
			ID:   fmt.Sprintf("task-%s", task.ID),
			Type: agent.MessageTypeJobSubmit,
			Payload: map[string]interface{}{
				"task": task,
			},
		}

		if err := c.remoteAgent.SendMessage(targetNode.ID, message); err != nil {
			return fmt.Errorf("failed to send task to node %s: %w", targetNode.ID, err)
		}
	}

	// Move from pending to running
	c.mutex.Lock()
	delete(c.pendingTasks, task.ID)
	c.runningTasks[task.ID] = task
	c.mutex.Unlock()

	c.logger.Info("Task scheduled",
		logging.F("task_id", task.ID),
		logging.F("assigned_to", targetNode.ID),
	)

	return nil
}

// executeTaskLocally executes a task on the local node
func (c *Coordinator) executeTaskLocally(task *DistributedTask) {
	c.mutex.RLock()
	_, exists := c.taskHandlers[task.Type]
	c.mutex.RUnlock()

	if !exists {
		c.completeTask(task, nil, fmt.Errorf("no handler for task type %s", task.Type))
		return
	}

	// Create job for worker pool
	job := &worker.Job{
		ID:         task.ID,
		Type:       task.Type,
		Payload:    task.Payload,
		Priority:   task.Priority,
		MaxRetries: 3,
		Timeout:    time.Hour, // Default timeout
	}

	// Submit to worker pool
	if err := c.workerPool.Submit(job); err != nil {
		c.completeTask(task, nil, fmt.Errorf("failed to submit job: %w", err))
		return
	}

	task.Status = TaskStatusRunning
	c.updateTaskInRedis(task)
}

// completeTask marks a task as completed or failed
func (c *Coordinator) completeTask(task *DistributedTask, result map[string]interface{}, err error) {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	delete(c.runningTasks, task.ID)

	if err != nil {
		task.Status = TaskStatusFailed
		task.Error = err.Error()
	} else {
		task.Status = TaskStatusCompleted
		task.Result = result
	}

	c.updateTaskInRedis(task)

	c.logger.Info("Task completed",
		logging.F("task_id", task.ID),
		logging.F("status", string(task.Status)),
		logging.F("assigned_to", task.AssignedTo),
	)
}

// updateTaskInRedis updates task information in Redis
func (c *Coordinator) updateTaskInRedis(task *DistributedTask) error {
	taskData, err := json.Marshal(task)
	if err != nil {
		return fmt.Errorf("failed to marshal task: %w", err)
	}

	key := fmt.Sprintf("coordination:tasks:%s", task.ID)
	return c.redisClient.Set(c.ctx, key, taskData, 24*time.Hour).Err()
}

// selectRoundRobinNode selects a node using round-robin strategy
func (c *Coordinator) selectRoundRobinNode(nodes []*cluster.NodeInfo, requiredCapabilities []string) *cluster.NodeInfo {
	// Simple round-robin based on current time
	index := int(time.Now().Unix()) % len(nodes)
	
	for i := 0; i < len(nodes); i++ {
		node := nodes[(index+i)%len(nodes)]
		if c.clusterManager.FindBestNode(requiredCapabilities) != nil {
			return node
		}
	}
	return nil
}

// selectCapabilityNode selects the best node based on capabilities
func (c *Coordinator) selectCapabilityNode(nodes []*cluster.NodeInfo, requiredCapabilities []string) *cluster.NodeInfo {
	var bestNode *cluster.NodeInfo
	bestCapabilityCount := -1

	for _, node := range nodes {
		capabilityCount := 0
		nodeCapabilities := make(map[string]bool)
		for _, cap := range node.Capabilities {
			nodeCapabilities[cap] = true
		}

		hasRequired := true
		for _, req := range requiredCapabilities {
			if !nodeCapabilities[req] {
				hasRequired = false
				break
			}
			capabilityCount++
		}

		if hasRequired && capabilityCount > bestCapabilityCount {
			bestCapabilityCount = capabilityCount
			bestNode = node
		}
	}

	return bestNode
}

// taskMonitor monitors running tasks for timeouts and failures
func (c *Coordinator) taskMonitor() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-c.ctx.Done():
			return
		case <-ticker.C:
			c.checkTaskTimeouts()
		}
	}
}

// checkTaskTimeouts checks for timed-out tasks
func (c *Coordinator) checkTaskTimeouts() {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	now := time.Now()
	for _, task := range c.runningTasks {
		if !task.Deadline.IsZero() && now.After(task.Deadline) {
			c.logger.Warn("Task deadline exceeded",
				logging.F("task_id", task.ID),
				logging.F("deadline", task.Deadline),
			)
			task.Status = TaskStatusFailed
			task.Error = "deadline exceeded"
			c.updateTaskInRedis(task)
		}
	}
}

// processDistributedTasks processes results from distributed tasks
func (c *Coordinator) processDistributedTasks() {
	results := c.workerPool.GetResults()

	for result := range results {
		c.mutex.Lock()
		task, exists := c.runningTasks[result.JobID]
		c.mutex.Unlock()

		if exists {
			if result.Success {
				c.completeTask(task, result.Result, nil)
			} else {
				c.completeTask(task, nil, fmt.Errorf("%s", result.Error))
			}
		}
	}
}

// registerMessageHandlers registers message handlers for coordination
func (c *Coordinator) registerMessageHandlers() {
	// Task result handler
	c.remoteAgent.RegisterHandler(agent.MessageTypeJobResult, agent.MessageHandlerFunc(
		func(ctx context.Context, message *agent.AgentMessage, sender *agent.AgentConnection) error {
			taskID, ok := message.Payload["task_id"].(string)
			if !ok {
				return fmt.Errorf("invalid task_id in job result")
			}

			c.mutex.Lock()
			task, exists := c.runningTasks[taskID]
			c.mutex.Unlock()

			if !exists {
				return fmt.Errorf("task %s not found in running tasks", taskID)
			}

			success, _ := message.Payload["success"].(bool)
			if success {
				result, _ := message.Payload["result"].(map[string]interface{})
				c.completeTask(task, result, nil)
			} else {
				errorMsg, _ := message.Payload["error"].(string)
				c.completeTask(task, nil, fmt.Errorf("%s", errorMsg))
			}

			return nil
		},
	))
}

// Start starts the leader election process
func (le *LeaderElection) Start() error {
	le.logger.Info("Starting leader election", logging.F("node_id", le.nodeID))

	go le.leaderElectionLoop()

	return nil
}

// Stop stops the leader election process
func (le *LeaderElection) Stop() error {
	le.cancel()
	return nil
}

// IsLeader returns true if this node is the current leader
func (le *LeaderElection) IsLeader() bool {
	le.mutex.RLock()
	defer le.mutex.RUnlock()
	return le.isLeader
}

// leaderElectionLoop runs the leader election algorithm
func (le *LeaderElection) leaderElectionLoop() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-le.ctx.Done():
			return
		case <-ticker.C:
			le.attemptLeadership()
		}
	}
}

// attemptLeadership attempts to become the leader
func (le *LeaderElection) attemptLeadership() {
	key := "coordination:leader"
	
	// Try to set leader key with expiration
	result := le.redisClient.SetNX(le.ctx, key, le.nodeID, 15*time.Second)
	
	if result.Err() != nil {
		le.logger.Error("Failed to attempt leadership", logging.F("error", result.Err().Error()))
		return
	}

	if result.Val() {
		// Successfully became leader
		le.mutex.Lock()
		wasLeader := le.isLeader
		le.isLeader = true
		le.leaderTerm++
		le.mutex.Unlock()

		if !wasLeader {
			le.logger.Info("Became cluster leader", logging.F("term", le.leaderTerm))
		}
	} else {
		// Check current leader
		currentLeader := le.redisClient.Get(le.ctx, key)
		if currentLeader.Err() == nil && currentLeader.Val() == le.nodeID {
			// Still the leader, extend lease
			le.redisClient.Expire(le.ctx, key, 15*time.Second)
		} else {
			// Not the leader
			le.mutex.Lock()
			wasLeader := le.isLeader
			le.isLeader = false
			le.mutex.Unlock()

			if wasLeader {
				le.logger.Info("Lost leadership")
			}
		}
	}
}

// GetTaskStatus returns the status of a task
func (c *Coordinator) GetTaskStatus(taskID string) (*DistributedTask, error) {
	// Check local tasks first
	c.mutex.RLock()
	if task, exists := c.pendingTasks[taskID]; exists {
		c.mutex.RUnlock()
		return task, nil
	}
	if task, exists := c.runningTasks[taskID]; exists {
		c.mutex.RUnlock()
		return task, nil
	}
	c.mutex.RUnlock()

	// Check Redis
	key := fmt.Sprintf("coordination:tasks:%s", taskID)
	result := c.redisClient.Get(c.ctx, key)
	if result.Err() != nil {
		return nil, fmt.Errorf("task not found: %s", taskID)
	}

	var task DistributedTask
	if err := json.Unmarshal([]byte(result.Val()), &task); err != nil {
		return nil, fmt.Errorf("failed to unmarshal task: %w", err)
	}

	return &task, nil
}