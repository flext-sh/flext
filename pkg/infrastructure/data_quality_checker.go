package quality

import (
	"context"
	"fmt"
	"math"
	"reflect"
	"regexp"
	"strings"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// DataQualityChecker checks data quality metrics
type DataQualityChecker struct {
	logger logging.Logger
}

// NewDataQualityChecker creates a new data quality checker
func NewDataQualityChecker(logger logging.Logger) *DataQualityChecker {
	return &DataQualityChecker{
		logger: logger,
	}
}

func (d *DataQualityChecker) GetName() string {
	return "data_quality"
}

func (d *DataQualityChecker) GetType() string {
	return "data"
}

func (d *DataQualityChecker) GetDescription() string {
	return "Analyzes data quality including completeness, accuracy, consistency, and validity"
}

func (d *DataQualityChecker) RunCheck(ctx context.Context, resourceID, resourceType string, data interface{}) (*QualityCheck, error) {
	startTime := time.Now()

	check := d.initializeQualityCheck(resourceID, resourceType, startTime)
	scores := d.performQualityChecks(check, data)
	d.finalizeQualityCheck(check, scores, startTime, resourceID)

	return check, nil
}

// checkCompleteness evaluates data completeness
func (d *DataQualityChecker) checkCompleteness(check *QualityCheck, data interface{}) float64 {
	if data == nil {
		return d.handleNilData(check)
	}

	switch v := data.(type) {
	case string:
		return d.checkStringCompleteness(check, v)
	case map[string]interface{}:
		return d.checkMapCompleteness(check, v)
	case []interface{}:
		return d.checkArrayCompleteness(check, v)
	default:
		return 100.0
	}
}

// checkAccuracy evaluates data accuracy
func (d *DataQualityChecker) checkAccuracy(check *QualityCheck, data interface{}) float64 {
	switch v := data.(type) {
	case string:
		return d.checkStringAccuracy(check, v)
	case map[string]interface{}:
		return d.checkMapAccuracy(check, v)
	default:
		return 100.0
	}
}

// checkConsistency evaluates data consistency
func (d *DataQualityChecker) checkConsistency(check *QualityCheck, data interface{}) float64 {
	switch v := data.(type) {
	case map[string]interface{}:
		return d.checkMapConsistency(check, v)
	case []interface{}:
		return d.checkArrayConsistency(check, v)
	default:
		return 100.0
	}
}

// checkValidity evaluates data validity
func (d *DataQualityChecker) checkValidity(check *QualityCheck, data interface{}) float64 {
	switch v := data.(type) {
	case string:
		return d.checkStringValidity(check, v)
	case map[string]interface{}:
		return d.checkMapValidity(check, v)
	default:
		return 100.0
	}
}

// checkUniqueness evaluates data uniqueness
func (d *DataQualityChecker) checkUniqueness(check *QualityCheck, data interface{}) float64 {
	switch v := data.(type) {
	case []interface{}:
		return d.checkArrayUniqueness(check, v)
	case map[string]interface{}:
		return d.checkMapUniqueness(check, v)
	default:
		return 100.0
	}
}

// QualityScores holds the scores for all quality dimensions
type QualityScores struct {
	Completeness float64
	Accuracy     float64
	Consistency  float64
	Validity     float64
	Uniqueness   float64
}

// Helper methods for main quality check process

func (d *DataQualityChecker) initializeQualityCheck(resourceID, resourceType string, startTime time.Time) *QualityCheck {
	return &QualityCheck{
		ID:           uuid.New(),
		Name:         d.GetName(),
		Type:         d.GetType(),
		ResourceID:   resourceID,
		ResourceType: resourceType,
		Timestamp:    startTime,
		MaxScore:     100.0,
		Details:      make(map[string]interface{}),
		Issues:       make([]QualityIssue, 0),
	}
}

func (d *DataQualityChecker) performQualityChecks(check *QualityCheck, data interface{}) QualityScores {
	return QualityScores{
		Completeness: d.checkCompleteness(check, data),
		Accuracy:     d.checkAccuracy(check, data),
		Consistency:  d.checkConsistency(check, data),
		Validity:     d.checkValidity(check, data),
		Uniqueness:   d.checkUniqueness(check, data),
	}
}

func (d *DataQualityChecker) finalizeQualityCheck(check *QualityCheck, scores QualityScores, startTime time.Time, resourceID string) {
	// Calculate weighted average
	check.Score = (scores.Completeness*0.25 + scores.Accuracy*0.25 + scores.Consistency*0.2 + scores.Validity*0.2 + scores.Uniqueness*0.1)
	check.Duration = time.Since(startTime)
	d.determineStatus(check)

	// Store individual scores
	check.Details["completeness_score"] = scores.Completeness
	check.Details["accuracy_score"] = scores.Accuracy
	check.Details["consistency_score"] = scores.Consistency
	check.Details["validity_score"] = scores.Validity
	check.Details["uniqueness_score"] = scores.Uniqueness

	d.logger.Debug("Data quality check completed",
		logging.F("resource_id", resourceID),
		logging.F("score", check.Score),
		logging.F("issues", len(check.Issues)),
	)
}

// Helper methods for completeness checking

func (d *DataQualityChecker) handleNilData(check *QualityCheck) float64 {
	check.Issues = append(check.Issues, QualityIssue{
		ID:         uuid.New().String(),
		Severity:   "critical",
		Category:   "completeness",
		Message:    "Data is completely missing",
		Rule:       "data_presence",
		Suggestion: "Ensure data is provided and not null",
		Timestamp:  time.Now(),
	})
	return 0
}

func (d *DataQualityChecker) checkStringCompleteness(check *QualityCheck, value string) float64 {
	if strings.TrimSpace(value) == "" {
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "completeness",
			Message:    "String data is empty",
			Rule:       "empty_string",
			Suggestion: "Provide non-empty string data",
			Timestamp:  time.Now(),
		})
		return 50.0
	}
	return 100.0
}

func (d *DataQualityChecker) checkMapCompleteness(check *QualityCheck, data map[string]interface{}) float64 {
	emptyFields := d.countEmptyFields(data)
	totalFields := len(data)
	if totalFields > 0 {
		completenessRatio := float64(totalFields-emptyFields) / float64(totalFields)
		if completenessRatio < 0.8 {
			check.Issues = append(check.Issues, QualityIssue{
				ID:         uuid.New().String(),
				Severity:   "major",
				Category:   "completeness",
				Message:    fmt.Sprintf("Data has %d empty fields out of %d total", emptyFields, totalFields),
				Rule:       "field_completeness",
				Suggestion: "Fill in missing required fields",
				Timestamp:  time.Now(),
			})
			return completenessRatio * 100
		}
	}
	return 100.0
}

func (d *DataQualityChecker) checkArrayCompleteness(check *QualityCheck, data []interface{}) float64 {
	if len(data) == 0 {
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "completeness",
			Message:    "Array data is empty",
			Rule:       "empty_array",
			Suggestion: "Provide array with at least one element",
			Timestamp:  time.Now(),
		})
		return 70.0
	}
	return 100.0
}

// Helper methods for accuracy checking

func (d *DataQualityChecker) checkStringAccuracy(check *QualityCheck, value string) float64 {
	score := 100.0

	if d.hasCommonTypos(value) {
		score -= 10
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "minor",
			Category:   "accuracy",
			Message:    "Potential typos detected in text data",
			Rule:       "typo_detection",
			Suggestion: "Review and correct spelling errors",
			Timestamp:  time.Now(),
		})
	}

	if d.hasInvalidFormats(value) {
		score -= 20
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "accuracy",
			Message:    "Invalid data formats detected",
			Rule:       "format_validation",
			Suggestion: "Ensure data follows expected format patterns",
			Timestamp:  time.Now(),
		})
	}

	return score
}

func (d *DataQualityChecker) checkMapAccuracy(check *QualityCheck, data map[string]interface{}) float64 {
	if d.hasLogicalInconsistencies(data) {
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "accuracy",
			Message:    "Logical inconsistencies found in data",
			Rule:       "logical_consistency",
			Suggestion: "Review data for logical errors and correct them",
			Timestamp:  time.Now(),
		})
		return 75.0
	}
	return 100.0
}

// Helper methods for consistency checking

func (d *DataQualityChecker) checkMapConsistency(check *QualityCheck, data map[string]interface{}) float64 {
	score := 100.0

	if d.hasInconsistentTypes(data) {
		score -= 20
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "consistency",
			Message:    "Inconsistent data types detected",
			Rule:       "type_consistency",
			Suggestion: "Ensure consistent data types across similar fields",
			Timestamp:  time.Now(),
		})
	}

	if d.hasInconsistentNaming(data) {
		score -= 10
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "minor",
			Category:   "consistency",
			Message:    "Inconsistent naming conventions",
			Rule:       "naming_consistency",
			Suggestion: "Use consistent naming conventions for fields",
			Timestamp:  time.Now(),
		})
	}

	return score
}

func (d *DataQualityChecker) checkArrayConsistency(check *QualityCheck, data []interface{}) float64 {
	if d.hasInconsistentArrayStructure(data) {
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "consistency",
			Message:    "Inconsistent structure in array elements",
			Rule:       "array_consistency",
			Suggestion: "Ensure all array elements have consistent structure",
			Timestamp:  time.Now(),
		})
		return 85.0
	}
	return 100.0
}

// Helper methods for validity checking

func (d *DataQualityChecker) checkStringValidity(check *QualityCheck, value string) float64 {
	score := 100.0

	if !d.isValidUTF8(value) {
		score -= 30
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "validity",
			Message:    "Invalid UTF-8 encoding detected",
			Rule:       "utf8_encoding",
			Suggestion: "Ensure text uses valid UTF-8 encoding",
			Timestamp:  time.Now(),
		})
	}

	if d.hasDangerousCharacters(value) {
		score -= 40
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "critical",
			Category:   "validity",
			Message:    "Potentially dangerous characters detected",
			Rule:       "safe_characters",
			Suggestion: "Remove or escape potentially dangerous characters",
			Timestamp:  time.Now(),
		})
	}

	return score
}

func (d *DataQualityChecker) checkMapValidity(check *QualityCheck, data map[string]interface{}) float64 {
	score := 100.0

	if d.hasInvalidFieldNames(data) {
		score -= 15
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "validity",
			Message:    "Invalid field names detected",
			Rule:       "valid_field_names",
			Suggestion: "Use valid field names without special characters",
			Timestamp:  time.Now(),
		})
	}

	if d.hasInvalidValueRanges(data) {
		score -= 20
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "validity",
			Message:    "Values outside expected ranges",
			Rule:       "value_ranges",
			Suggestion: "Ensure values are within expected valid ranges",
			Timestamp:  time.Now(),
		})
	}

	return score
}

// Helper methods for uniqueness checking

func (d *DataQualityChecker) checkArrayUniqueness(check *QualityCheck, data []interface{}) float64 {
	duplicates := d.findDuplicates(data)
	if len(duplicates) > 0 {
		duplicateRatio := float64(len(duplicates)) / float64(len(data))
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "uniqueness",
			Message:    fmt.Sprintf("Found %d duplicate entries", len(duplicates)),
			Rule:       "duplicate_detection",
			Suggestion: "Remove or deduplicate identical entries",
			Timestamp:  time.Now(),
		})
		return (1 - duplicateRatio) * 100
	}
	return 100.0
}

func (d *DataQualityChecker) checkMapUniqueness(check *QualityCheck, data map[string]interface{}) float64 {
	if d.hasDuplicateValues(data) {
		check.Issues = append(check.Issues, QualityIssue{
			ID:         uuid.New().String(),
			Severity:   "major",
			Category:   "uniqueness",
			Message:    "Duplicate values found in fields that should be unique",
			Rule:       "unique_fields",
			Suggestion: "Ensure unique constraints are maintained",
			Timestamp:  time.Now(),
		})
		return 75.0
	}
	return 100.0
}

// Helper methods for data quality analysis

func (d *DataQualityChecker) countEmptyFields(data map[string]interface{}) int {
	count := 0
	for _, value := range data {
		if d.isEmpty(value) {
			count++
		}
	}
	return count
}

func (d *DataQualityChecker) isEmpty(value interface{}) bool {
	if value == nil {
		return true
	}

	switch v := value.(type) {
	case string:
		return strings.TrimSpace(v) == ""
	case []interface{}:
		return len(v) == 0
	case map[string]interface{}:
		return len(v) == 0
	default:
		return false
	}
}

func (d *DataQualityChecker) hasCommonTypos(text string) bool {
	// Check for common typos and misspellings
	commonTypos := []string{
		"teh", "adn", "hte", "youre", "ther", "recieve",
		"seperate", "definately", "occured", "accomodate",
	}

	lowerText := strings.ToLower(text)
	for _, typo := range commonTypos {
		if strings.Contains(lowerText, typo) {
			return true
		}
	}
	return false
}

func (d *DataQualityChecker) hasInvalidFormats(text string) bool {
	// Check for patterns that might indicate format issues

	// Check for email-like patterns that are invalid
	emailPattern := regexp.MustCompile(`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`)
	if emailPattern.MatchString(text) {
		// Basic email validation
		parts := strings.Split(text, "@")
		if len(parts) != 2 || strings.Contains(parts[0], "..") || strings.Contains(parts[1], "..") {
			return true
		}
	}

	// Check for phone-like patterns that are invalid
	phonePattern := regexp.MustCompile(`\d{3}-\d{3}-\d{4}|\(\d{3}\)\s*\d{3}-\d{4}`)
	if phonePattern.MatchString(text) {
		// Additional phone validation could be added here
	}

	// Check for date-like patterns that are invalid
	datePattern := regexp.MustCompile(`\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}`)
	if datePattern.MatchString(text) {
		// Try to parse as date
		formats := []string{"2006-01-02", "01/02/2006", "02/01/2006"}
		for _, format := range formats {
			if _, err := time.Parse(format, text); err == nil {
				return false // Valid date found
			}
		}
		return true // Date pattern but invalid date
	}

	return false
}

func (d *DataQualityChecker) hasLogicalInconsistencies(data map[string]interface{}) bool {
	// Check for logical inconsistencies like negative ages, future dates in the past, etc.

	for key, value := range data {
		lowerKey := strings.ToLower(key)

		// Check age-related fields
		if strings.Contains(lowerKey, "age") {
			if age, ok := value.(float64); ok {
				if age < 0 || age > 150 {
					return true
				}
			}
		}

		// Check date-related fields
		if strings.Contains(lowerKey, "birth") || strings.Contains(lowerKey, "created") {
			if dateStr, ok := value.(string); ok {
				if date, err := time.Parse("2006-01-02", dateStr); err == nil {
					if date.After(time.Now()) {
						return true // Birth date in the future
					}
				}
			}
		}

		// Check percentage values
		if strings.Contains(lowerKey, "percent") || strings.Contains(lowerKey, "rate") {
			if pct, ok := value.(float64); ok {
				if pct < 0 || pct > 100 {
					return true
				}
			}
		}
	}

	return false
}

func (d *DataQualityChecker) hasInconsistentTypes(data map[string]interface{}) bool {
	// Group fields by similar names and check for type consistency
	typeGroups := make(map[string][]reflect.Type)

	for key, value := range data {
		// Normalize key name (remove numbers, underscores)
		normalizedKey := regexp.MustCompile(`[0-9_]`).ReplaceAllString(strings.ToLower(key), "")
		typeGroups[normalizedKey] = append(typeGroups[normalizedKey], reflect.TypeOf(value))
	}

	// Check for inconsistencies within groups
	for _, types := range typeGroups {
		if len(types) > 1 {
			firstType := types[0]
			for _, t := range types[1:] {
				if t != firstType {
					return true
				}
			}
		}
	}

	return false
}

func (d *DataQualityChecker) hasInconsistentNaming(data map[string]interface{}) bool {
	// Check for mixed naming conventions
	camelCaseCount := 0
	snakeCaseCount := 0
	kebabCaseCount := 0

	for key := range data {
		if regexp.MustCompile(`[a-z]+[A-Z]`).MatchString(key) {
			camelCaseCount++
		} else if strings.Contains(key, "_") {
			snakeCaseCount++
		} else if strings.Contains(key, "-") {
			kebabCaseCount++
		}
	}

	// If multiple conventions are used significantly, it's inconsistent
	conventions := []int{camelCaseCount, snakeCaseCount, kebabCaseCount}
	nonZeroConventions := 0
	for _, count := range conventions {
		if count > 1 {
			nonZeroConventions++
		}
	}

	return nonZeroConventions > 1
}

func (d *DataQualityChecker) hasInconsistentArrayStructure(data []interface{}) bool {
	if len(data) < 2 {
		return false
	}

	// Compare structure of first element with others
	firstElement := data[0]
	firstType := reflect.TypeOf(firstElement)

	for i := 1; i < len(data); i++ {
		if reflect.TypeOf(data[i]) != firstType {
			return true
		}

		// For maps, check field consistency
		if firstMap, ok := firstElement.(map[string]interface{}); ok {
			if currentMap, ok := data[i].(map[string]interface{}); ok {
				if len(firstMap) != len(currentMap) {
					return true
				}
				for key := range firstMap {
					if _, exists := currentMap[key]; !exists {
						return true
					}
				}
			}
		}
	}

	return false
}

func (d *DataQualityChecker) isValidUTF8(text string) bool {
	// Check if string is valid UTF-8
	return len(text) == len([]rune(text))
}

func (d *DataQualityChecker) hasDangerousCharacters(text string) bool {
	// Check for potentially dangerous characters
	dangerousPatterns := []string{
		"<script", "javascript:", "onload=", "onerror=",
		"eval(", "document.", "window.", "alert(",
		"../", "..\\", "system(", "exec(",
	}

	lowerText := strings.ToLower(text)
	for _, pattern := range dangerousPatterns {
		if strings.Contains(lowerText, pattern) {
			return true
		}
	}

	return false
}

func (d *DataQualityChecker) hasInvalidFieldNames(data map[string]interface{}) bool {
	// Check for invalid field names
	validFieldPattern := regexp.MustCompile(`^[a-zA-Z][a-zA-Z0-9_]*$`)

	for key := range data {
		if !validFieldPattern.MatchString(key) {
			return true
		}
	}

	return false
}

func (d *DataQualityChecker) hasInvalidValueRanges(data map[string]interface{}) bool {
	// Check for values outside reasonable ranges
	for key, value := range data {
		lowerKey := strings.ToLower(key)

		// Check numeric ranges
		if numValue, ok := value.(float64); ok {
			if math.IsInf(numValue, 0) || math.IsNaN(numValue) {
				return true
			}

			// Check specific field ranges
			if strings.Contains(lowerKey, "score") && (numValue < 0 || numValue > 100) {
				return true
			}
			if strings.Contains(lowerKey, "count") && numValue < 0 {
				return true
			}
		}

		// Check string lengths
		if strValue, ok := value.(string); ok {
			if len(strValue) > 10000 { // Arbitrary large limit
				return true
			}
		}
	}

	return false
}

func (d *DataQualityChecker) findDuplicates(data []interface{}) []interface{} {
	seen := make(map[string]bool)
	duplicates := make([]interface{}, 0)

	for _, item := range data {
		// Convert to string for comparison
		itemStr := fmt.Sprintf("%v", item)
		if seen[itemStr] {
			duplicates = append(duplicates, item)
		} else {
			seen[itemStr] = true
		}
	}

	return duplicates
}

func (d *DataQualityChecker) hasDuplicateValues(data map[string]interface{}) bool {
	// Check if any fields that should typically be unique have duplicate values
	uniqueFields := []string{"id", "email", "username", "phone", "ssn"}

	for key, value := range data {
		lowerKey := strings.ToLower(key)
		for _, uniqueField := range uniqueFields {
			if strings.Contains(lowerKey, uniqueField) {
				// In a real implementation, this would check against a database
				// For now, we'll do a simple check for obvious duplicates
				if strValue, ok := value.(string); ok {
					if len(strValue) > 0 && strings.Count(strValue, strValue[:1]) == len(strValue) {
						return true // All same character (like "aaaa")
					}
				}
			}
		}
	}

	return false
}

func (d *DataQualityChecker) determineStatus(check *QualityCheck) {
	percentage := (check.Score / check.MaxScore) * 100

	if percentage >= 85 {
		check.Status = "passed"
	} else if percentage >= 70 {
		check.Status = "warning"
	} else {
		check.Status = "failed"
	}
}
