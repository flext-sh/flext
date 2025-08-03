package quality

import (
	"context"
	"regexp"
	"strings"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// CodeQualityChecker checks code quality metrics
type CodeQualityChecker struct {
	logger logging.Logger
}

// NewCodeQualityChecker creates a new code quality checker
func NewCodeQualityChecker(logger logging.Logger) *CodeQualityChecker {
	return &CodeQualityChecker{
		logger: logger,
	}
}

func (c *CodeQualityChecker) GetName() string {
	return "code_quality"
}

func (c *CodeQualityChecker) GetType() string {
	return "code"
}

func (c *CodeQualityChecker) GetDescription() string {
	return "Analyzes code quality including complexity, maintainability, and best practices"
}

func (c *CodeQualityChecker) RunCheck(ctx context.Context, resourceID, resourceType string, data interface{}) (*QualityCheck, error) {
	startTime := time.Now()

	check := &QualityCheck{
		ID:           uuid.New(),
		Name:         c.GetName(),
		Type:         c.GetType(),
		ResourceID:   resourceID,
		ResourceType: resourceType,
		Timestamp:    startTime,
		MaxScore:     100.0,
		Details:      make(map[string]interface{}),
		Issues:       make([]QualityIssue, 0),
	}

	// Analyze based on resource type
	switch resourceType {
	case "pipeline":
		c.analyzePipelineCode(check, data)
	case "plugin":
		c.analyzePluginCode(check, data)
	case "config":
		c.analyzeConfigCode(check, data)
	default:
		c.analyzeGenericCode(check, data)
	}

	check.Duration = time.Since(startTime)
	c.determineStatus(check)

	c.logger.Debug("Code quality check completed",
		logging.F("resource_id", resourceID),
		logging.F("score", check.Score),
		logging.F("issues", len(check.Issues)),
	)

	return check, nil
}

// analyzePipelineCode analyzes pipeline-specific code quality
func (c *CodeQualityChecker) analyzePipelineCode(check *QualityCheck, data interface{}) {
	score := 100.0

	// Check for pipeline structure
	if c.checkPipelineStructure(data) {
		score -= 10
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "structure",
			Message:    "Pipeline structure is not well-defined",
			Rule:       "pipeline_structure",
			Suggestion: "Define clear pipeline steps with proper dependencies",
			Timestamp:  time.Now(),
		})
	}

	// Check for error handling
	if c.checkErrorHandling(data) {
		score -= 15
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "error_handling",
			Message:    "Insufficient error handling in pipeline",
			Rule:       "error_handling",
			Suggestion: "Add proper error handling and recovery mechanisms",
			Timestamp:  time.Now(),
		})
	}

	// Check for documentation
	if c.checkDocumentation(data) {
		score -= 5
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "minor",
			Category:   "documentation",
			Message:    "Pipeline lacks proper documentation",
			Rule:       "documentation",
			Suggestion: "Add comprehensive documentation for pipeline steps",
			Timestamp:  time.Now(),
		})
	}

	check.Score = score
	check.Details["pipeline_steps"] = c.countPipelineSteps(data)
	check.Details["complexity_score"] = c.calculateComplexity(data)
}

// analyzePluginCode analyzes plugin-specific code quality
func (c *CodeQualityChecker) analyzePluginCode(check *QualityCheck, data interface{}) {
	score := 100.0

	// Check for plugin interface compliance
	if c.checkPluginInterface(data) {
		score -= 20
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "critical",
			Category:   "interface",
			Message:    "Plugin does not implement required interface correctly",
			Rule:       "plugin_interface",
			Suggestion: "Ensure plugin implements all required interface methods",
			Timestamp:  time.Now(),
		})
	}

	// Check for plugin validation
	if c.checkPluginValidation(data) {
		score -= 10
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "validation",
			Message:    "Plugin lacks input validation",
			Rule:       "input_validation",
			Suggestion: "Add comprehensive input validation to plugin",
			Timestamp:  time.Now(),
		})
	}

	// Check for plugin testing
	if c.checkPluginTesting(data) {
		score -= 15
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "testing",
			Message:    "Plugin lacks adequate test coverage",
			Rule:       "test_coverage",
			Suggestion: "Add unit tests and integration tests for plugin",
			Timestamp:  time.Now(),
		})
	}

	check.Score = score
	check.Details["plugin_type"] = c.getPluginType(data)
	check.Details["test_coverage"] = c.calculateTestCoverage(data)
}

// analyzeConfigCode analyzes configuration quality
func (c *CodeQualityChecker) analyzeConfigCode(check *QualityCheck, data interface{}) {
	score := 100.0

	// Check for configuration completeness
	if c.checkConfigCompleteness(data) {
		score -= 15
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "completeness",
			Message:    "Configuration is incomplete",
			Rule:       "config_completeness",
			Suggestion: "Ensure all required configuration values are provided",
			Timestamp:  time.Now(),
		})
	}

	// Check for security configuration
	if c.checkSecurityConfig(data) {
		score -= 25
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "critical",
			Category:   "security",
			Message:    "Configuration contains security vulnerabilities",
			Rule:       "security_config",
			Suggestion: "Review and fix security configuration issues",
			Timestamp:  time.Now(),
		})
	}

	check.Score = score
	check.Details["config_size"] = c.getConfigSize(data)
	check.Details["security_score"] = c.calculateSecurityScore(data)
}

// analyzeGenericCode analyzes general code quality
func (c *CodeQualityChecker) analyzeGenericCode(check *QualityCheck, data interface{}) {
	score := 100.0

	// Basic code quality checks
	if c.checkCodeComplexity(data) {
		score -= 20
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "complexity",
			Message:    "Code complexity is too high",
			Rule:       "complexity",
			Suggestion: "Break down complex functions into smaller, manageable pieces",
			Timestamp:  time.Now(),
		})
	}

	if c.checkNamingConventions(data) {
		score -= 5
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "minor",
			Category:   "naming",
			Message:    "Inconsistent naming conventions",
			Rule:       "naming_conventions",
			Suggestion: "Follow consistent naming conventions throughout the code",
			Timestamp:  time.Now(),
		})
	}

	check.Score = score
	check.Details["lines_of_code"] = c.countLinesOfCode(data)
	check.Details["function_count"] = c.countFunctions(data)
}

// Helper methods for code analysis

func (c *CodeQualityChecker) checkPipelineStructure(data interface{}) bool {
	// Simulate pipeline structure analysis
	// In real implementation, this would analyze actual pipeline definition
	return false // Assume good structure for now
}

func (c *CodeQualityChecker) checkErrorHandling(data interface{}) bool {
	// Simulate error handling analysis
	if dataStr, ok := data.(string); ok {
		// Check for error handling patterns
		errorPatterns := []string{"try", "catch", "error", "exception", "panic", "recover"}
		lowerData := strings.ToLower(dataStr)

		foundPatterns := 0
		for _, pattern := range errorPatterns {
			if strings.Contains(lowerData, pattern) {
				foundPatterns++
			}
		}

		// If we find fewer than 2 error handling patterns, flag as issue
		return foundPatterns < 2
	}
	return true // Assume missing error handling if we can't analyze
}

func (c *CodeQualityChecker) checkDocumentation(data interface{}) bool {
	// Check for documentation patterns
	if dataStr, ok := data.(string); ok {
		docPatterns := []string{"//", "/*", "/**", "description", "comment"}
		lowerData := strings.ToLower(dataStr)

		for _, pattern := range docPatterns {
			if strings.Contains(lowerData, pattern) {
				return false // Found documentation
			}
		}
	}
	return true // Missing documentation
}

func (c *CodeQualityChecker) checkPluginInterface(data interface{}) bool {
	// Simulate plugin interface compliance check
	return false // Assume compliance for now
}

func (c *CodeQualityChecker) checkPluginValidation(data interface{}) bool {
	// Check for input validation in plugins
	if dataStr, ok := data.(string); ok {
		validationPatterns := []string{"validate", "check", "verify", "sanitize"}
		lowerData := strings.ToLower(dataStr)

		for _, pattern := range validationPatterns {
			if strings.Contains(lowerData, pattern) {
				return false // Found validation
			}
		}
	}
	return true // Missing validation
}

func (c *CodeQualityChecker) checkPluginTesting(data interface{}) bool {
	// Check for testing patterns
	if dataStr, ok := data.(string); ok {
		testPatterns := []string{"test", "spec", "assert", "expect", "mock"}
		lowerData := strings.ToLower(dataStr)

		for _, pattern := range testPatterns {
			if strings.Contains(lowerData, pattern) {
				return false // Found tests
			}
		}
	}
	return true // Missing tests
}

func (c *CodeQualityChecker) checkConfigCompleteness(data interface{}) bool {
	// Simulate configuration completeness check
	return false // Assume complete for now
}

func (c *CodeQualityChecker) checkSecurityConfig(data interface{}) bool {
	// Check for security issues in configuration
	if dataStr, ok := data.(string); ok {
		insecurePatterns := []string{"password=", "secret=", "token=", "key=", "http://"}
		lowerData := strings.ToLower(dataStr)

		for _, pattern := range insecurePatterns {
			if strings.Contains(lowerData, pattern) {
				return true // Found security issue
			}
		}
	}
	return false // No security issues found
}

func (c *CodeQualityChecker) checkCodeComplexity(data interface{}) bool {
	// Analyze code complexity using simple heuristics
	if dataStr, ok := data.(string); ok {
		// Count nested structures and complexity indicators
		complexityPatterns := []string{
			`if\s+.*\s+{.*if\s+.*\s+{`,                      // Nested if statements
			`for\s+.*\s+{.*for\s+.*\s+{`,                    // Nested loops
			`switch\s+.*\s+{.*case.*case.*case.*case.*case`, // Long switch statements
		}

		for _, pattern := range complexityPatterns {
			if matched, _ := regexp.MatchString(pattern, dataStr); matched {
				return true // High complexity found
			}
		}

		// Check for excessive line length (indication of complexity)
		lines := strings.Split(dataStr, "\n")
		for _, line := range lines {
			if len(line) > 120 {
				return true // Long lines indicate complexity
			}
		}
	}
	return false // Acceptable complexity
}

func (c *CodeQualityChecker) checkNamingConventions(data interface{}) bool {
	// Check naming conventions
	if dataStr, ok := data.(string); ok {
		// Look for inconsistent naming patterns
		camelCasePattern := regexp.MustCompile(`[a-z]+[A-Z][a-zA-Z]*`)
		snake_casePattern := regexp.MustCompile(`[a-z]+_[a-z_]*`)

		camelCaseMatches := camelCasePattern.FindAllString(dataStr, -1)
		snakeCaseMatches := snake_casePattern.FindAllString(dataStr, -1)

		// If both patterns exist significantly, flag as inconsistent
		if len(camelCaseMatches) > 3 && len(snakeCaseMatches) > 3 {
			return true // Inconsistent naming
		}
	}
	return false // Consistent naming
}

// Helper methods for metrics calculation

func (c *CodeQualityChecker) countPipelineSteps(data interface{}) int {
	// Count pipeline steps
	if dataStr, ok := data.(string); ok {
		stepPatterns := []string{"step", "stage", "phase", "task"}
		count := 0
		lowerData := strings.ToLower(dataStr)

		for _, pattern := range stepPatterns {
			count += strings.Count(lowerData, pattern)
		}
		return count
	}
	return 0
}

func (c *CodeQualityChecker) calculateComplexity(data interface{}) float64 {
	// Calculate complexity score (1-10, where 10 is most complex)
	if dataStr, ok := data.(string); ok {
		lines := strings.Split(dataStr, "\n")
		complexity := float64(len(lines)) / 100.0 // Base complexity on lines

		// Add complexity for control structures
		controlStructures := []string{"if", "for", "while", "switch", "case"}
		for _, structure := range controlStructures {
			complexity += float64(strings.Count(strings.ToLower(dataStr), structure)) * 0.1
		}

		if complexity > 10 {
			complexity = 10
		}
		return complexity
	}
	return 1.0
}

func (c *CodeQualityChecker) getPluginType(data interface{}) string {
	// Extract plugin type from data
	if dataStr, ok := data.(string); ok {
		lowerData := strings.ToLower(dataStr)
		if strings.Contains(lowerData, "source") {
			return "source"
		}
		if strings.Contains(lowerData, "target") {
			return "target"
		}
		if strings.Contains(lowerData, "transform") {
			return "transform"
		}
	}
	return "unknown"
}

func (c *CodeQualityChecker) calculateTestCoverage(data interface{}) float64 {
	// Calculate test coverage percentage
	if dataStr, ok := data.(string); ok {
		lines := strings.Split(dataStr, "\n")
		testLines := 0

		for _, line := range lines {
			lowerLine := strings.ToLower(strings.TrimSpace(line))
			if strings.Contains(lowerLine, "test") ||
				strings.Contains(lowerLine, "assert") ||
				strings.Contains(lowerLine, "expect") {
				testLines++
			}
		}

		if len(lines) > 0 {
			return (float64(testLines) / float64(len(lines))) * 100
		}
	}
	return 0.0
}

func (c *CodeQualityChecker) getConfigSize(data interface{}) int {
	// Get configuration size metrics
	if dataStr, ok := data.(string); ok {
		return len(strings.Split(dataStr, "\n"))
	}
	return 0
}

func (c *CodeQualityChecker) calculateSecurityScore(data interface{}) float64 {
	// Calculate security score (0-100, where 100 is most secure)
	score := 100.0

	if dataStr, ok := data.(string); ok {
		securityIssues := []string{
			"password=", "secret=", "token=", "key=",
			"http://", "REDACTED_LDAP_BIND_PASSWORD/REDACTED_LDAP_BIND_PASSWORD", "root/root",
		}

		for _, issue := range securityIssues {
			if strings.Contains(strings.ToLower(dataStr), issue) {
				score -= 20 // Deduct points for each security issue
			}
		}

		if score < 0 {
			score = 0
		}
	}

	return score
}

func (c *CodeQualityChecker) countLinesOfCode(data interface{}) int {
	// Count lines of code
	if dataStr, ok := data.(string); ok {
		lines := strings.Split(dataStr, "\n")
		nonEmptyLines := 0

		for _, line := range lines {
			if strings.TrimSpace(line) != "" {
				nonEmptyLines++
			}
		}
		return nonEmptyLines
	}
	return 0
}

func (c *CodeQualityChecker) countFunctions(data interface{}) int {
	// Count function definitions
	if dataStr, ok := data.(string); ok {
		functionPatterns := []string{"func ", "function ", "def ", "method "}
		count := 0

		for _, pattern := range functionPatterns {
			count += strings.Count(strings.ToLower(dataStr), pattern)
		}
		return count
	}
	return 0
}

func (c *CodeQualityChecker) determineStatus(check *QualityCheck) {
	percentage := (check.Score / check.MaxScore) * 100

	if percentage >= 80 {
		check.Status = "passed"
	} else if percentage >= 60 {
		check.Status = "warning"
	} else {
		check.Status = "failed"
	}
}
