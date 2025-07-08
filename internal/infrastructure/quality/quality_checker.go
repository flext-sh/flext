package quality

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// QualityCheck represents a quality check result
type QualityCheck struct {
	ID           uuid.UUID              `json:"id"`
	Name         string                 `json:"name"`
	Type         string                 `json:"type"`
	Status       string                 `json:"status"`
	Score        float64                `json:"score"`
	MaxScore     float64                `json:"max_score"`
	Details      map[string]interface{} `json:"details"`
	Issues       []QualityIssue         `json:"issues"`
	Timestamp    time.Time              `json:"timestamp"`
	Duration     time.Duration          `json:"duration"`
	ResourceID   string                 `json:"resource_id"`
	ResourceType string                 `json:"resource_type"`
}

// QualityIssue represents a specific quality issue
type QualityIssue struct {
	ID         string    `json:"id"`
	Severity   string    `json:"severity"`
	Category   string    `json:"category"`
	Message    string    `json:"message"`
	Line       int       `json:"line,omitempty"`
	Column     int       `json:"column,omitempty"`
	File       string    `json:"file,omitempty"`
	Rule       string    `json:"rule"`
	Suggestion string    `json:"suggestion,omitempty"`
	Timestamp  time.Time `json:"timestamp"`
}

// QualityReport represents a comprehensive quality report
type QualityReport struct {
	ID              uuid.UUID      `json:"id"`
	ResourceID      string         `json:"resource_id"`
	ResourceType    string         `json:"resource_type"`
	OverallScore    float64        `json:"overall_score"`
	MaxScore        float64        `json:"max_score"`
	Status          string         `json:"status"`
	Checks          []QualityCheck `json:"checks"`
	Summary         QualitySummary `json:"summary"`
	Recommendations []string       `json:"recommendations"`
	Timestamp       time.Time      `json:"timestamp"`
	Duration        time.Duration  `json:"duration"`
}

// QualitySummary provides aggregated quality metrics
type QualitySummary struct {
	TotalChecks    int `json:"total_checks"`
	PassedChecks   int `json:"passed_checks"`
	WarningChecks  int `json:"warning_checks"`
	FailedChecks   int `json:"failed_checks"`
	CriticalIssues int `json:"critical_issues"`
	MajorIssues    int `json:"major_issues"`
	MinorIssues    int `json:"minor_issues"`
	InfoIssues     int `json:"info_issues"`
}

// QualityChecker interface defines quality checking functionality
type QualityChecker interface {
	RunCheck(ctx context.Context, resourceID, resourceType string, data interface{}) (*QualityCheck, error)
	GetName() string
	GetType() string
	GetDescription() string
}

// QualityManager manages all quality checking operations
type QualityManager struct {
	checkers map[string]QualityChecker
	reports  map[string]*QualityReport
	mu       sync.RWMutex
	logger   logging.Logger
}

// NewQualityManager creates a new quality manager
func NewQualityManager(logger logging.Logger) *QualityManager {
	qm := &QualityManager{
		checkers: make(map[string]QualityChecker),
		reports:  make(map[string]*QualityReport),
		logger:   logger,
	}

	// Register default checkers
	qm.RegisterChecker(NewCodeQualityChecker(logger))
	qm.RegisterChecker(NewDataQualityChecker(logger))
	qm.RegisterChecker(NewPipelineQualityChecker(logger))
	qm.RegisterChecker(NewSecurityQualityChecker(logger))
	qm.RegisterChecker(NewPerformanceQualityChecker(logger))

	return qm
}

// RegisterChecker registers a new quality checker
func (qm *QualityManager) RegisterChecker(checker QualityChecker) {
	qm.mu.Lock()
	defer qm.mu.Unlock()

	qm.checkers[checker.GetName()] = checker
	qm.logger.Info("Quality checker registered",
		logging.F("checker", checker.GetName()),
		logging.F("type", checker.GetType()),
	)
}

// RunQualityChecks runs all applicable quality checks for a resource
func (qm *QualityManager) RunQualityChecks(ctx context.Context, resourceID, resourceType string, data interface{}) (*QualityReport, error) {
	startTime := time.Now()

	report := &QualityReport{
		ID:           uuid.New(),
		ResourceID:   resourceID,
		ResourceType: resourceType,
		Status:       "running",
		Checks:       make([]QualityCheck, 0),
		Timestamp:    startTime,
	}

	qm.mu.Lock()
	qm.reports[report.ID.String()] = report
	qm.mu.Unlock()

	qm.logger.Info("Starting quality checks",
		logging.F("resource_id", resourceID),
		logging.F("resource_type", resourceType),
		logging.F("report_id", report.ID.String()),
	)

	// Run all applicable checkers
	var wg sync.WaitGroup
	checkResults := make(chan QualityCheck, len(qm.checkers))
	errors := make(chan error, len(qm.checkers))

	qm.mu.RLock()
	for _, checker := range qm.checkers {
		wg.Add(1)
		go func(c QualityChecker) {
			defer wg.Done()

			check, err := c.RunCheck(ctx, resourceID, resourceType, data)
			if err != nil {
				errors <- fmt.Errorf("checker %s failed: %w", c.GetName(), err)
				return
			}
			checkResults <- *check
		}(checker)
	}
	qm.mu.RUnlock()

	// Wait for all checks to complete
	go func() {
		wg.Wait()
		close(checkResults)
		close(errors)
	}()

	// Collect results
	for check := range checkResults {
		report.Checks = append(report.Checks, check)
	}

	// Collect errors
	var checkErrors []error
	for err := range errors {
		checkErrors = append(checkErrors, err)
		qm.logger.Error("Quality check error", logging.F("error", err.Error()))
	}

	// Calculate overall metrics
	report.Duration = time.Since(startTime)
	qm.calculateOverallScore(report)
	qm.generateSummary(report)
	qm.generateRecommendations(report)

	// Update status
	if len(checkErrors) > 0 {
		report.Status = "completed_with_errors"
	} else {
		report.Status = "completed"
	}

	qm.mu.Lock()
	qm.reports[report.ID.String()] = report
	qm.mu.Unlock()

	qm.logger.Info("Quality checks completed",
		logging.F("resource_id", resourceID),
		logging.F("overall_score", report.OverallScore),
		logging.F("status", report.Status),
		logging.F("duration", report.Duration.String()),
	)

	return report, nil
}

// GetQualityReport retrieves a quality report by ID
func (qm *QualityManager) GetQualityReport(reportID string) (*QualityReport, bool) {
	qm.mu.RLock()
	defer qm.mu.RUnlock()

	report, exists := qm.reports[reportID]
	return report, exists
}

// ListQualityReports returns all quality reports for a resource
func (qm *QualityManager) ListQualityReports(resourceID string) []*QualityReport {
	qm.mu.RLock()
	defer qm.mu.RUnlock()

	var reports []*QualityReport
	for _, report := range qm.reports {
		if report.ResourceID == resourceID {
			reports = append(reports, report)
		}
	}

	return reports
}

// calculateOverallScore computes the overall quality score
func (qm *QualityManager) calculateOverallScore(report *QualityReport) {
	if len(report.Checks) == 0 {
		report.OverallScore = 0
		report.MaxScore = 0
		return
	}

	totalScore := 0.0
	maxTotalScore := 0.0

	for _, check := range report.Checks {
		totalScore += check.Score
		maxTotalScore += check.MaxScore
	}

	report.OverallScore = totalScore
	report.MaxScore = maxTotalScore
}

// generateSummary creates a quality summary
func (qm *QualityManager) generateSummary(report *QualityReport) {
	summary := QualitySummary{
		TotalChecks: len(report.Checks),
	}

	for _, check := range report.Checks {
		switch check.Status {
		case "passed":
			summary.PassedChecks++
		case "warning":
			summary.WarningChecks++
		case "failed":
			summary.FailedChecks++
		}

		for _, issue := range check.Issues {
			switch issue.Severity {
			case "critical":
				summary.CriticalIssues++
			case "major":
				summary.MajorIssues++
			case "minor":
				summary.MinorIssues++
			case "info":
				summary.InfoIssues++
			}
		}
	}

	report.Summary = summary
}

// generateRecommendations creates actionable recommendations
func (qm *QualityManager) generateRecommendations(report *QualityReport) {
	var recommendations []string

	// Analyze patterns and suggest improvements
	if report.Summary.CriticalIssues > 0 {
		recommendations = append(recommendations,
			"Address critical issues immediately to ensure system stability")
	}

	if report.Summary.FailedChecks > report.Summary.PassedChecks {
		recommendations = append(recommendations,
			"Focus on improving code quality and data validation")
	}

	if report.OverallScore/report.MaxScore < 0.7 {
		recommendations = append(recommendations,
			"Consider implementing additional quality controls and testing")
	}

	// Security recommendations
	for _, check := range report.Checks {
		if check.Type == "security" && check.Status == "failed" {
			recommendations = append(recommendations,
				"Review and fix security vulnerabilities to prevent potential breaches")
			break
		}
	}

	// Performance recommendations
	for _, check := range report.Checks {
		if check.Type == "performance" && check.Score/check.MaxScore < 0.6 {
			recommendations = append(recommendations,
				"Optimize performance bottlenecks to improve system efficiency")
			break
		}
	}

	report.Recommendations = recommendations
}

// CleanupOldReports removes old quality reports
func (qm *QualityManager) CleanupOldReports(maxAge time.Duration) {
	qm.mu.Lock()
	defer qm.mu.Unlock()

	cutoff := time.Now().Add(-maxAge)

	for id, report := range qm.reports {
		if report.Timestamp.Before(cutoff) {
			delete(qm.reports, id)
		}
	}

	qm.logger.Info("Old quality reports cleaned up",
		logging.F("cutoff", cutoff.String()),
		logging.F("remaining_reports", len(qm.reports)),
	)
}

// GetQualityMetrics returns aggregated quality metrics
func (qm *QualityManager) GetQualityMetrics() map[string]interface{} {
	qm.mu.RLock()
	defer qm.mu.RUnlock()

	totalReports := len(qm.reports)
	if totalReports == 0 {
		return map[string]interface{}{
			"total_reports":  0,
			"avg_score":      0,
			"checkers_count": len(qm.checkers),
		}
	}

	totalScore := 0.0
	totalMaxScore := 0.0
	statusCounts := make(map[string]int)

	for _, report := range qm.reports {
		totalScore += report.OverallScore
		totalMaxScore += report.MaxScore
		statusCounts[report.Status]++
	}

	avgScore := 0.0
	if totalMaxScore > 0 {
		avgScore = (totalScore / totalMaxScore) * 100
	}

	return map[string]interface{}{
		"total_reports":    totalReports,
		"avg_score":        avgScore,
		"checkers_count":   len(qm.checkers),
		"status_breakdown": statusCounts,
	}
}
