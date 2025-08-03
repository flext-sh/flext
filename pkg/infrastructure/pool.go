package worker

import (
	"context"
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// Job represents a unit of work
type Job struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`
	Payload     map[string]interface{} `json:"payload"`
	Priority    int                    `json:"priority"`
	MaxRetries  int                    `json:"max_retries"`
	Retries     int                    `json:"retries"`
	CreatedAt   time.Time              `json:"created_at"`
	ScheduledAt time.Time              `json:"scheduled_at"`
	Timeout     time.Duration          `json:"timeout"`
}

// JobResult represents the result of job execution
type JobResult struct {
	JobID     string                 `json:"job_id"`
	Success   bool                   `json:"success"`
	Result    map[string]interface{} `json:"result"`
	Error     string                 `json:"error,omitempty"`
	Duration  time.Duration          `json:"duration"`
	WorkerID  string                 `json:"worker_id"`
	StartedAt time.Time              `json:"started_at"`
	EndedAt   time.Time              `json:"ended_at"`
}

// JobHandler defines the interface for job processing
type JobHandler interface {
	Handle(ctx context.Context, job *Job) (*JobResult, error)
	CanHandle(jobType string) bool
}

// Worker represents a single worker in the pool
type Worker struct {
	ID       string
	pool     *WorkerPool
	jobChan  chan *Job
	quitChan chan bool
	logger   logging.Logger
}

// WorkerPool manages a pool of workers for parallel job processing
type WorkerPool struct {
	maxWorkers    int
	minWorkers    int
	workers       []*Worker
	jobQueue      chan *Job
	resultQueue   chan *JobResult
	handlers      map[string]JobHandler
	handlersMutex sync.RWMutex
	ctx           context.Context
	cancel        context.CancelFunc
	wg            sync.WaitGroup
	logger        logging.Logger
	metrics       *PoolMetrics
	activeJobs    int64
	totalJobs     int64
	completedJobs int64
	failedJobs    int64
}

// PoolMetrics contains metrics about the worker pool
type PoolMetrics struct {
	ActiveWorkers    int           `json:"active_workers"`
	ActiveJobs       int64         `json:"active_jobs"`
	TotalJobs        int64         `json:"total_jobs"`
	CompletedJobs    int64         `json:"completed_jobs"`
	FailedJobs       int64         `json:"failed_jobs"`
	AverageJobTime   time.Duration `json:"average_job_time"`
	QueueLength      int           `json:"queue_length"`
	ThroughputPerSec float64       `json:"throughput_per_sec"`
}

// NewWorkerPool creates a new worker pool
func NewWorkerPool(maxWorkers, minWorkers int, queueSize int, logger logging.Logger) *WorkerPool {
	if maxWorkers <= 0 {
		maxWorkers = runtime.NumCPU()
	}
	if minWorkers <= 0 {
		minWorkers = 1
	}
	if minWorkers > maxWorkers {
		minWorkers = maxWorkers
	}
	if queueSize <= 0 {
		queueSize = maxWorkers * 10
	}

	ctx, cancel := context.WithCancel(context.Background())

	pool := &WorkerPool{
		maxWorkers:  maxWorkers,
		minWorkers:  minWorkers,
		jobQueue:    make(chan *Job, queueSize),
		resultQueue: make(chan *JobResult, queueSize),
		handlers:    make(map[string]JobHandler),
		ctx:         ctx,
		cancel:      cancel,
		logger:      logger,
		metrics: &PoolMetrics{
			ActiveWorkers: 0,
		},
	}

	return pool
}

// Start starts the worker pool
func (wp *WorkerPool) Start() error {
	wp.logger.Info("Starting worker pool",
		logging.F("max_workers", wp.maxWorkers),
		logging.F("min_workers", wp.minWorkers),
		logging.F("queue_size", cap(wp.jobQueue)),
	)

	// Start minimum number of workers
	for i := 0; i < wp.minWorkers; i++ {
		wp.startWorker()
	}

	// Start metrics collection
	go wp.metricsCollector()

	// Start auto-scaling monitor
	go wp.autoScaler()

	wp.logger.Info("Worker pool started successfully")
	return nil
}

// Stop stops the worker pool gracefully
func (wp *WorkerPool) Stop() error {
	wp.logger.Info("Stopping worker pool")

	wp.cancel()

	// Close job queue to signal workers to stop
	close(wp.jobQueue)

	// Wait for all workers to finish
	wp.wg.Wait()

	close(wp.resultQueue)

	wp.logger.Info("Worker pool stopped")
	return nil
}

// RegisterHandler registers a job handler for a specific job type
func (wp *WorkerPool) RegisterHandler(jobType string, handler JobHandler) {
	wp.handlersMutex.Lock()
	defer wp.handlersMutex.Unlock()

	wp.handlers[jobType] = handler
	wp.logger.Info("Job handler registered", logging.F("job_type", jobType))
}

// Submit submits a job to the worker pool
func (wp *WorkerPool) Submit(job *Job) error {
	if job.CreatedAt.IsZero() {
		job.CreatedAt = time.Now()
	}
	if job.ScheduledAt.IsZero() {
		job.ScheduledAt = time.Now()
	}
	if job.Timeout == 0 {
		job.Timeout = 5 * time.Minute // Default timeout
	}

	select {
	case wp.jobQueue <- job:
		atomic.AddInt64(&wp.totalJobs, 1)
		wp.logger.Debug("Job submitted",
			logging.F("job_id", job.ID),
			logging.F("job_type", job.Type),
			logging.F("priority", job.Priority),
		)
		return nil
	case <-wp.ctx.Done():
		return fmt.Errorf("worker pool is shutting down")
	default:
		return fmt.Errorf("job queue is full")
	}
}

// SubmitBatch submits multiple jobs as a batch
func (wp *WorkerPool) SubmitBatch(jobs []*Job) error {
	for _, job := range jobs {
		if err := wp.Submit(job); err != nil {
			return fmt.Errorf("failed to submit job %s: %w", job.ID, err)
		}
	}
	return nil
}

// GetResults returns a channel to receive job results
func (wp *WorkerPool) GetResults() <-chan *JobResult {
	return wp.resultQueue
}

// GetMetrics returns current pool metrics
func (wp *WorkerPool) GetMetrics() *PoolMetrics {
	metrics := *wp.metrics
	metrics.ActiveJobs = atomic.LoadInt64(&wp.activeJobs)
	metrics.TotalJobs = atomic.LoadInt64(&wp.totalJobs)
	metrics.CompletedJobs = atomic.LoadInt64(&wp.completedJobs)
	metrics.FailedJobs = atomic.LoadInt64(&wp.failedJobs)
	metrics.QueueLength = len(wp.jobQueue)
	metrics.ActiveWorkers = len(wp.workers)

	return &metrics
}

// startWorker creates and starts a new worker
func (wp *WorkerPool) startWorker() {
	workerID := fmt.Sprintf("worker-%d", len(wp.workers)+1)

	worker := &Worker{
		ID:       workerID,
		pool:     wp,
		jobChan:  make(chan *Job),
		quitChan: make(chan bool),
		logger:   wp.logger.With(logging.F("worker_id", workerID)),
	}

	wp.workers = append(wp.workers, worker)
	wp.wg.Add(1)

	go worker.start()

	wp.logger.Debug("Worker started", logging.F("worker_id", workerID))
}

// stopWorker stops and removes a worker
func (wp *WorkerPool) stopWorker() {
	if len(wp.workers) <= wp.minWorkers {
		return
	}

	worker := wp.workers[len(wp.workers)-1]
	wp.workers = wp.workers[:len(wp.workers)-1]

	worker.quitChan <- true
	wp.logger.Debug("Worker stopped", logging.F("worker_id", worker.ID))
}

// start starts the worker's main loop
func (w *Worker) start() {
	defer w.pool.wg.Done()

	for {
		select {
		case job := <-w.pool.jobQueue:
			if job != nil {
				w.processJob(job)
			}
		case <-w.quitChan:
			return
		case <-w.pool.ctx.Done():
			return
		}
	}
}

// processJob processes a single job
func (w *Worker) processJob(job *Job) {
	atomic.AddInt64(&w.pool.activeJobs, 1)
	defer atomic.AddInt64(&w.pool.activeJobs, -1)

	startTime := time.Now()

	w.logger.Debug("Processing job",
		logging.F("job_id", job.ID),
		logging.F("job_type", job.Type),
	)

	// Find handler for job type
	w.pool.handlersMutex.RLock()
	handler, exists := w.pool.handlers[job.Type]
	w.pool.handlersMutex.RUnlock()

	result := &JobResult{
		JobID:     job.ID,
		WorkerID:  w.ID,
		StartedAt: startTime,
	}

	if !exists {
		result.Success = false
		result.Error = fmt.Sprintf("no handler found for job type: %s", job.Type)
		result.EndedAt = time.Now()
		result.Duration = result.EndedAt.Sub(result.StartedAt)

		atomic.AddInt64(&w.pool.failedJobs, 1)
		w.sendResult(result)
		return
	}

	// Create context with timeout
	ctx, cancel := context.WithTimeout(w.pool.ctx, job.Timeout)
	defer cancel()

	// Process the job
	jobResult, err := handler.Handle(ctx, job)
	endTime := time.Now()

	if err != nil {
		result.Success = false
		result.Error = err.Error()
		atomic.AddInt64(&w.pool.failedJobs, 1)
	} else {
		result.Success = true
		if jobResult != nil {
			result.Result = jobResult.Result
		}
		atomic.AddInt64(&w.pool.completedJobs, 1)
	}

	result.EndedAt = endTime
	result.Duration = endTime.Sub(startTime)

	w.logger.Debug("Job completed",
		logging.F("job_id", job.ID),
		logging.F("success", result.Success),
		logging.F("duration", result.Duration),
	)

	w.sendResult(result)
}

// sendResult sends the job result to the result queue
func (w *Worker) sendResult(result *JobResult) {
	select {
	case w.pool.resultQueue <- result:
	case <-w.pool.ctx.Done():
	default:
		w.logger.Error("Result queue full, dropping result",
			logging.F("job_id", result.JobID))
	}
}

// metricsCollector collects and updates pool metrics
func (wp *WorkerPool) metricsCollector() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	var lastCompleted int64
	lastTime := time.Now()

	for {
		select {
		case <-wp.ctx.Done():
			return
		case <-ticker.C:
			now := time.Now()
			currentCompleted := atomic.LoadInt64(&wp.completedJobs)

			if lastCompleted > 0 {
				jobsProcessed := currentCompleted - lastCompleted
				duration := now.Sub(lastTime)
				wp.metrics.ThroughputPerSec = float64(jobsProcessed) / duration.Seconds()
			}

			lastCompleted = currentCompleted
			lastTime = now
		}
	}
}

// autoScaler automatically scales workers based on queue length and load
func (wp *WorkerPool) autoScaler() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-wp.ctx.Done():
			return
		case <-ticker.C:
			wp.scaleWorkers()
		}
	}
}

// scaleWorkers scales the number of workers based on current load
func (wp *WorkerPool) scaleWorkers() {
	queueLength := len(wp.jobQueue)
	currentWorkers := len(wp.workers)

	// Scale up if queue is getting full
	if queueLength > currentWorkers*2 && currentWorkers < wp.maxWorkers {
		wp.startWorker()
		wp.logger.Info("Scaled up workers",
			logging.F("current_workers", len(wp.workers)),
			logging.F("queue_length", queueLength),
		)
	}

	// Scale down if queue is nearly empty
	if queueLength < currentWorkers/4 && currentWorkers > wp.minWorkers {
		wp.stopWorker()
		wp.logger.Info("Scaled down workers",
			logging.F("current_workers", len(wp.workers)),
			logging.F("queue_length", queueLength),
		)
	}
}
