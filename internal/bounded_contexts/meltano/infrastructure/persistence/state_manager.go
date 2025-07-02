package persistence

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/pkg/errors"
)

// StateRecord represents a persisted state record
type StateRecord struct {
	ID          string                 `json:"id"`
	ProjectName string                 `json:"project_name"`
	PluginName  string                 `json:"plugin_name"`
	State       map[string]interface{} `json:"state"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
	Version     int                    `json:"version"`
}

// ExecutionRecord represents a pipeline execution record
type ExecutionRecord struct {
	ID          string                 `json:"id"`
	ProjectName string                 `json:"project_name"`
	Pipeline    string                 `json:"pipeline"`
	Status      string                 `json:"status"` // running, completed, failed
	StartedAt   time.Time              `json:"started_at"`
	CompletedAt *time.Time             `json:"completed_at,omitempty"`
	Duration    *time.Duration         `json:"duration,omitempty"`
	Error       string                 `json:"error,omitempty"`
	Metrics     map[string]interface{} `json:"metrics,omitempty"`
	Logs        []string               `json:"logs,omitempty"`
}

// StateManager manages persistent state for Meltano operations
type StateManager struct {
	stateDir         string
	executionsDir    string
	mu               sync.RWMutex
	logger           logging.Logger
	maxExecutions    int
	cleanupInterval  time.Duration
	stopCleanup      chan struct{}
	cleanupStopped   chan struct{}
}

// NewStateManager creates a new state manager
func NewStateManager(stateDir string, logger logging.Logger) (*StateManager, error) {
	sm := &StateManager{
		stateDir:        filepath.Join(stateDir, "state"),
		executionsDir:   filepath.Join(stateDir, "executions"),
		logger:          logger.With(logging.F("component", "state_manager")),
		maxExecutions:   1000,
		cleanupInterval: 1 * time.Hour,
		stopCleanup:     make(chan struct{}),
		cleanupStopped:  make(chan struct{}),
	}

	// Create directories
	if err := os.MkdirAll(sm.stateDir, 0755); err != nil {
		return nil, errors.Wrap(err, "failed to create state directory")
	}
	
	if err := os.MkdirAll(sm.executionsDir, 0755); err != nil {
		return nil, errors.Wrap(err, "failed to create executions directory")
	}

	// Start cleanup routine
	go sm.cleanupRoutine()

	sm.logger.Info("State manager initialized",
		logging.F("state_dir", sm.stateDir),
		logging.F("executions_dir", sm.executionsDir))

	return sm, nil
}

// SaveState saves plugin state
func (sm *StateManager) SaveState(ctx context.Context, projectName, pluginName string, state map[string]interface{}) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	stateID := fmt.Sprintf("%s_%s", projectName, pluginName)
	now := time.Now()

	// Load existing state to get version
	existing, _ := sm.loadStateRecord(stateID)
	version := 1
	if existing != nil {
		version = existing.Version + 1
	}

	record := &StateRecord{
		ID:          stateID,
		ProjectName: projectName,
		PluginName:  pluginName,
		State:       state,
		CreatedAt:   now,
		UpdatedAt:   now,
		Version:     version,
	}

	if existing != nil {
		record.CreatedAt = existing.CreatedAt
	}

	if err := sm.saveStateRecord(record); err != nil {
		return errors.Wrap(err, "failed to save state record")
	}

	sm.logger.Debug("State saved",
		logging.F("project", projectName),
		logging.F("plugin", pluginName),
		logging.F("version", version))

	return nil
}

// LoadState loads plugin state
func (sm *StateManager) LoadState(ctx context.Context, projectName, pluginName string) (map[string]interface{}, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	stateID := fmt.Sprintf("%s_%s", projectName, pluginName)
	record, err := sm.loadStateRecord(stateID)
	if err != nil {
		if os.IsNotExist(err) {
			sm.logger.Debug("No state found",
				logging.F("project", projectName),
				logging.F("plugin", pluginName))
			return make(map[string]interface{}), nil
		}
		return nil, errors.Wrap(err, "failed to load state record")
	}

	sm.logger.Debug("State loaded",
		logging.F("project", projectName),
		logging.F("plugin", pluginName),
		logging.F("version", record.Version))

	return record.State, nil
}

// DeleteState deletes plugin state
func (sm *StateManager) DeleteState(ctx context.Context, projectName, pluginName string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	stateID := fmt.Sprintf("%s_%s", projectName, pluginName)
	statePath := filepath.Join(sm.stateDir, stateID+".json")

	if err := os.Remove(statePath); err != nil && !os.IsNotExist(err) {
		return errors.Wrap(err, "failed to delete state file")
	}

	sm.logger.Debug("State deleted",
		logging.F("project", projectName),
		logging.F("plugin", pluginName))

	return nil
}

// StartExecution records the start of a pipeline execution
func (sm *StateManager) StartExecution(ctx context.Context, projectName, pipeline string) (string, error) {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	executionID := fmt.Sprintf("%s_%s_%d", projectName, pipeline, time.Now().UnixNano())
	
	record := &ExecutionRecord{
		ID:          executionID,
		ProjectName: projectName,
		Pipeline:    pipeline,
		Status:      "running",
		StartedAt:   time.Now(),
		Metrics:     make(map[string]interface{}),
		Logs:        make([]string, 0),
	}

	if err := sm.saveExecutionRecord(record); err != nil {
		return "", errors.Wrap(err, "failed to save execution record")
	}

	sm.logger.Info("Execution started",
		logging.F("execution_id", executionID),
		logging.F("project", projectName),
		logging.F("pipeline", pipeline))

	return executionID, nil
}

// CompleteExecution records the completion of a pipeline execution
func (sm *StateManager) CompleteExecution(ctx context.Context, executionID string, status string, errorMsg string, metrics map[string]interface{}) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	record, err := sm.loadExecutionRecord(executionID)
	if err != nil {
		return errors.Wrap(err, "failed to load execution record")
	}

	now := time.Now()
	duration := now.Sub(record.StartedAt)
	
	record.Status = status
	record.CompletedAt = &now
	record.Duration = &duration
	record.Error = errorMsg
	
	if metrics != nil {
		for k, v := range metrics {
			record.Metrics[k] = v
		}
	}

	if err := sm.saveExecutionRecord(record); err != nil {
		return errors.Wrap(err, "failed to save updated execution record")
	}

	sm.logger.Info("Execution completed",
		logging.F("execution_id", executionID),
		logging.F("status", status),
		logging.F("duration", duration.String()))

	return nil
}

// AddExecutionLog adds a log entry to an execution
func (sm *StateManager) AddExecutionLog(ctx context.Context, executionID string, logEntry string) error {
	sm.mu.Lock()
	defer sm.mu.Unlock()

	record, err := sm.loadExecutionRecord(executionID)
	if err != nil {
		return errors.Wrap(err, "failed to load execution record")
	}

	record.Logs = append(record.Logs, fmt.Sprintf("[%s] %s", time.Now().Format("15:04:05"), logEntry))
	
	// Keep only last 1000 log entries
	if len(record.Logs) > 1000 {
		record.Logs = record.Logs[len(record.Logs)-1000:]
	}

	return sm.saveExecutionRecord(record)
}

// GetExecution retrieves an execution record
func (sm *StateManager) GetExecution(ctx context.Context, executionID string) (*ExecutionRecord, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	return sm.loadExecutionRecord(executionID)
}

// ListExecutions lists recent executions for a project
func (sm *StateManager) ListExecutions(ctx context.Context, projectName string, limit int) ([]*ExecutionRecord, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	files, err := os.ReadDir(sm.executionsDir)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read executions directory")
	}

	executions := sm.loadMatchingExecutions(files, projectName)
	sm.sortExecutionsByStartTime(executions)
	
	return sm.applyLimitToExecutions(executions, limit), nil
}

// loadMatchingExecutions loads execution records that match the project filter
func (sm *StateManager) loadMatchingExecutions(files []os.DirEntry, projectName string) []*ExecutionRecord {
	var executions []*ExecutionRecord
	
	for _, file := range files {
		if !sm.isExecutionFile(file) {
			continue
		}
		
		record := sm.loadExecutionRecordSafely(file.Name())
		if record != nil && sm.matchesProjectFilter(record, projectName) {
			executions = append(executions, record)
		}
	}
	
	return executions
}

// isExecutionFile checks if a file entry is a valid execution JSON file
func (sm *StateManager) isExecutionFile(file os.DirEntry) bool {
	return !file.IsDir() && filepath.Ext(file.Name()) == ".json"
}

// loadExecutionRecordSafely loads an execution record with error handling
func (sm *StateManager) loadExecutionRecordSafely(fileName string) *ExecutionRecord {
	recordID := fileName[:len(fileName)-5] // Remove .json extension
	record, err := sm.loadExecutionRecord(recordID)
	if err != nil {
		sm.logger.Warn("Failed to load execution record",
			logging.F("file", fileName),
			logging.F("error", err.Error()))
		return nil
	}
	return record
}

// matchesProjectFilter checks if a record matches the project name filter
func (sm *StateManager) matchesProjectFilter(record *ExecutionRecord, projectName string) bool {
	return projectName == "" || record.ProjectName == projectName
}

// sortExecutionsByStartTime sorts executions by start time (most recent first)
func (sm *StateManager) sortExecutionsByStartTime(executions []*ExecutionRecord) {
	for i := 0; i < len(executions)-1; i++ {
		for j := i + 1; j < len(executions); j++ {
			if executions[i].StartedAt.Before(executions[j].StartedAt) {
				executions[i], executions[j] = executions[j], executions[i]
			}
		}
	}
}

// applyLimitToExecutions applies a limit to the executions slice
func (sm *StateManager) applyLimitToExecutions(executions []*ExecutionRecord, limit int) []*ExecutionRecord {
	if limit > 0 && len(executions) > limit {
		return executions[:limit]
	}
	return executions
}

// GetStats returns statistics about the state manager
func (sm *StateManager) GetStats(ctx context.Context) (map[string]interface{}, error) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()

	stateStats, err := sm.getStateDirectoryStats()
	if err != nil {
		return nil, err
	}

	executionStats, err := sm.getExecutionDirectoryStats()
	if err != nil {
		return nil, err
	}

	return sm.buildStatsResponse(stateStats, executionStats), nil
}

// DirectoryStats holds statistics for a directory
type DirectoryStats struct {
	FileCount    int
	StatusCounts map[string]int
}

// getStateDirectoryStats collects statistics from the state directory
func (sm *StateManager) getStateDirectoryStats() (*DirectoryStats, error) {
	stateFiles, err := os.ReadDir(sm.stateDir)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read state directory")
	}

	return &DirectoryStats{
		FileCount:    len(stateFiles),
		StatusCounts: make(map[string]int),
	}, nil
}

// getExecutionDirectoryStats collects statistics from the executions directory
func (sm *StateManager) getExecutionDirectoryStats() (*DirectoryStats, error) {
	executionFiles, err := os.ReadDir(sm.executionsDir)
	if err != nil {
		return nil, errors.Wrap(err, "failed to read executions directory")
	}

	statusCounts := sm.countExecutionsByStatus(executionFiles)

	return &DirectoryStats{
		FileCount:    len(executionFiles),
		StatusCounts: statusCounts,
	}, nil
}

// countExecutionsByStatus counts executions by their status
func (sm *StateManager) countExecutionsByStatus(files []os.DirEntry) map[string]int {
	statusCounts := make(map[string]int)
	
	for _, file := range files {
		if !sm.isExecutionFile(file) {
			continue
		}
		
		record := sm.loadExecutionRecordSafely(file.Name())
		if record != nil {
			statusCounts[record.Status]++
		}
	}
	
	return statusCounts
}

// buildStatsResponse creates the final statistics response
func (sm *StateManager) buildStatsResponse(stateStats, executionStats *DirectoryStats) map[string]interface{} {
	return map[string]interface{}{
		"state_records":      stateStats.FileCount,
		"execution_records":  executionStats.FileCount,
		"execution_by_status": executionStats.StatusCounts,
		"state_dir":          sm.stateDir,
		"executions_dir":     sm.executionsDir,
		"cleanup_interval":   sm.cleanupInterval.String(),
		"max_executions":     sm.maxExecutions,
	}
}

// Private helper methods

func (sm *StateManager) saveStateRecord(record *StateRecord) error {
	data, err := json.MarshalIndent(record, "", "  ")
	if err != nil {
		return errors.Wrap(err, "failed to marshal state record")
	}

	filePath := filepath.Join(sm.stateDir, record.ID+".json")
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return errors.Wrap(err, "failed to write state file")
	}

	return nil
}

func (sm *StateManager) loadStateRecord(stateID string) (*StateRecord, error) {
	filePath := filepath.Join(sm.stateDir, stateID+".json")
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var record StateRecord
	if err := json.Unmarshal(data, &record); err != nil {
		return nil, errors.Wrap(err, "failed to unmarshal state record")
	}

	return &record, nil
}

func (sm *StateManager) saveExecutionRecord(record *ExecutionRecord) error {
	data, err := json.MarshalIndent(record, "", "  ")
	if err != nil {
		return errors.Wrap(err, "failed to marshal execution record")
	}

	filePath := filepath.Join(sm.executionsDir, record.ID+".json")
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return errors.Wrap(err, "failed to write execution file")
	}

	return nil
}

func (sm *StateManager) loadExecutionRecord(executionID string) (*ExecutionRecord, error) {
	filePath := filepath.Join(sm.executionsDir, executionID+".json")
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var record ExecutionRecord
	if err := json.Unmarshal(data, &record); err != nil {
		return nil, errors.Wrap(err, "failed to unmarshal execution record")
	}

	return &record, nil
}

func (sm *StateManager) cleanupRoutine() {
	ticker := time.NewTicker(sm.cleanupInterval)
	defer ticker.Stop()
	defer close(sm.cleanupStopped)

	for {
		select {
		case <-ticker.C:
			sm.performCleanup()
		case <-sm.stopCleanup:
			sm.logger.Info("State manager cleanup routine stopped")
			return
		}
	}
}

func (sm *StateManager) performCleanup() {
	sm.logger.Debug("Performing state manager cleanup")

	files, err := sm.readExecutionFiles()
	if err != nil {
		return
	}

	if !sm.needsCleanup(files) {
		return
	}

	fileInfos := sm.loadFileInfoWithTimestamps(files)
	sm.sortFileInfosByStartTime(fileInfos)
	sm.removeOldestFiles(fileInfos)
}

// readExecutionFiles reads the execution directory files
func (sm *StateManager) readExecutionFiles() ([]os.DirEntry, error) {
	files, err := os.ReadDir(sm.executionsDir)
	if err != nil {
		sm.logger.Error("Failed to read executions directory for cleanup",
			logging.F("error", err.Error()))
		return nil, err
	}
	return files, nil
}

// needsCleanup checks if cleanup is needed based on file count
func (sm *StateManager) needsCleanup(files []os.DirEntry) bool {
	return len(files) > sm.maxExecutions
}

// fileInfo holds file metadata for cleanup operations
type fileInfo struct {
	name      string
	startedAt time.Time
}

// loadFileInfoWithTimestamps loads execution records with their timestamps
func (sm *StateManager) loadFileInfoWithTimestamps(files []os.DirEntry) []fileInfo {
	var fileInfos []fileInfo
	
	for _, file := range files {
		if !sm.isExecutionFile(file) {
			continue
		}
		
		record, err := sm.loadExecutionRecord(file.Name()[:len(file.Name())-5])
		if err == nil {
			fileInfos = append(fileInfos, fileInfo{
				name:      file.Name(),
				startedAt: record.StartedAt,
			})
		}
	}
	
	return fileInfos
}

// sortFileInfosByStartTime sorts file infos by start time (oldest first)
func (sm *StateManager) sortFileInfosByStartTime(fileInfos []fileInfo) {
	for i := 0; i < len(fileInfos)-1; i++ {
		for j := i + 1; j < len(fileInfos); j++ {
			if fileInfos[i].startedAt.After(fileInfos[j].startedAt) {
				fileInfos[i], fileInfos[j] = fileInfos[j], fileInfos[i]
			}
		}
	}
}

// removeOldestFiles removes the oldest execution files to maintain the limit
func (sm *StateManager) removeOldestFiles(fileInfos []fileInfo) {
	toRemove := len(fileInfos) - sm.maxExecutions
	
	for i := 0; i < toRemove; i++ {
		filePath := filepath.Join(sm.executionsDir, fileInfos[i].name)
		if err := os.Remove(filePath); err != nil {
			sm.logger.Warn("Failed to remove old execution file",
				logging.F("file", fileInfos[i].name),
				logging.F("error", err.Error()))
		}
	}

	sm.logger.Info("Cleaned up old execution records",
		logging.F("removed", toRemove),
		logging.F("remaining", len(fileInfos)-toRemove))
}

// Close shuts down the state manager
func (sm *StateManager) Close() error {
	sm.logger.Info("Shutting down state manager")
	
	close(sm.stopCleanup)
	
	// Wait for cleanup routine to stop
	select {
	case <-sm.cleanupStopped:
		sm.logger.Info("State manager shutdown completed")
	case <-time.After(5 * time.Second):
		sm.logger.Warn("State manager shutdown timeout")
	}
	
	return nil
}