package validation

import (
	"fmt"
	"net/mail"
	"regexp"
	"strings"
	"unicode"
	"unicode/utf8"
)

// ValidationError represents a validation error with context
type ValidationError struct {
	Field   string `json:"field"`
	Value   string `json:"value,omitempty"`
	Message string `json:"message"`
	Code    string `json:"code"`
}

func (e ValidationError) Error() string {
	if e.Field != "" {
		return fmt.Sprintf("validation failed for field '%s': %s", e.Field, e.Message)
	}
	return fmt.Sprintf("validation failed: %s", e.Message)
}

// ValidationErrors represents multiple validation errors
type ValidationErrors []ValidationError

func (e ValidationErrors) Error() string {
	if len(e) == 0 {
		return "no validation errors"
	}
	if len(e) == 1 {
		return e[0].Error()
	}

	var messages []string
	for _, err := range e {
		messages = append(messages, err.Error())
	}
	return fmt.Sprintf("multiple validation errors: %s", strings.Join(messages, "; "))
}

// HasErrors checks if there are any validation errors
func (e ValidationErrors) HasErrors() bool {
	return len(e) > 0
}

// Add adds a new validation error
func (e *ValidationErrors) Add(field, message, code string, value ...string) {
	val := ""
	if len(value) > 0 {
		val = value[0]
	}
	*e = append(*e, ValidationError{
		Field:   field,
		Value:   val,
		Message: message,
		Code:    code,
	})
}

// Validator provides comprehensive validation functionality
type Validator struct {
	errors ValidationErrors
}

// NewValidator creates a new validator instance
func NewValidator() *Validator {
	return &Validator{
		errors: make(ValidationErrors, 0),
	}
}

// HasErrors returns true if there are validation errors
func (v *Validator) HasErrors() bool {
	return v.errors.HasErrors()
}

// Errors returns all validation errors
func (v *Validator) Errors() ValidationErrors {
	return v.errors
}

// Error returns the validation errors as a single error
func (v *Validator) Error() error {
	if !v.HasErrors() {
		return nil
	}
	return v.errors
}

// Reset clears all validation errors
func (v *Validator) Reset() {
	v.errors = make(ValidationErrors, 0)
}

// String validation methods

// Required validates that a string field is not empty
func (v *Validator) Required(field, value string) *Validator {
	if strings.TrimSpace(value) == "" {
		v.errors.Add(field, "field is required", "required")
	}
	return v
}

// MinLength validates minimum string length
func (v *Validator) MinLength(field, value string, min int) *Validator {
	if utf8.RuneCountInString(value) < min {
		v.errors.Add(field, fmt.Sprintf("minimum length is %d characters", min), "min_length", value)
	}
	return v
}

// MaxLength validates maximum string length
func (v *Validator) MaxLength(field, value string, max int) *Validator {
	if utf8.RuneCountInString(value) > max {
		v.errors.Add(field, fmt.Sprintf("maximum length is %d characters", max), "max_length", value)
	}
	return v
}

// Length validates exact string length
func (v *Validator) Length(field, value string, length int) *Validator {
	if utf8.RuneCountInString(value) != length {
		v.errors.Add(field, fmt.Sprintf("length must be exactly %d characters", length), "exact_length", value)
	}
	return v
}

// Pattern validates string against regex pattern
func (v *Validator) Pattern(field, value, pattern, message string) *Validator {
	matched, err := regexp.MatchString(pattern, value)
	if err != nil {
		v.errors.Add(field, "invalid pattern", "invalid_pattern")
		return v
	}
	if !matched {
		v.errors.Add(field, message, "pattern_mismatch", value)
	}
	return v
}

// AlphaNumeric validates that string contains only alphanumeric characters and specific allowed chars
func (v *Validator) AlphaNumeric(field, value string, allowedChars ...string) *Validator {
	allowed := make(map[rune]bool)
	for _, chars := range allowedChars {
		for _, r := range chars {
			allowed[r] = true
		}
	}

	for _, r := range value {
		if !unicode.IsLetter(r) && !unicode.IsDigit(r) && !allowed[r] {
			v.errors.Add(field, "contains invalid characters (only letters, numbers, and specific symbols allowed)", "invalid_characters", value)
			break
		}
	}
	return v
}

// NoSpaces validates that string contains no spaces
func (v *Validator) NoSpaces(field, value string) *Validator {
	if strings.Contains(value, " ") {
		v.errors.Add(field, "spaces are not allowed", "no_spaces", value)
	}
	return v
}

// Email validates email format
func (v *Validator) Email(field, value string) *Validator {
	_, err := mail.ParseAddress(value)
	if err != nil {
		v.errors.Add(field, "invalid email format", "invalid_email", value)
	}
	return v
}

// URL validates URL format
func (v *Validator) URL(field, value string) *Validator {
	urlPattern := `^https?://[^\s/$.?#].[^\s]*$`
	matched, err := regexp.MatchString(urlPattern, value)
	if err != nil || !matched {
		v.errors.Add(field, "invalid URL format", "invalid_url", value)
	}
	return v
}

// Numeric validation methods

// Min validates minimum numeric value
func (v *Validator) Min(field string, value, min int) *Validator {
	if value < min {
		v.errors.Add(field, fmt.Sprintf("minimum value is %d", min), "min_value", fmt.Sprintf("%d", value))
	}
	return v
}

// Max validates maximum numeric value
func (v *Validator) Max(field string, value, max int) *Validator {
	if value > max {
		v.errors.Add(field, fmt.Sprintf("maximum value is %d", max), "max_value", fmt.Sprintf("%d", value))
	}
	return v
}

// Range validates numeric value within range
func (v *Validator) Range(field string, value, min, max int) *Validator {
	if value < min || value > max {
		v.errors.Add(field, fmt.Sprintf("value must be between %d and %d", min, max), "out_of_range", fmt.Sprintf("%d", value))
	}
	return v
}

// Positive validates that number is positive
func (v *Validator) Positive(field string, value int) *Validator {
	if value <= 0 {
		v.errors.Add(field, "value must be positive", "not_positive", fmt.Sprintf("%d", value))
	}
	return v
}

// NonNegative validates that number is not negative
func (v *Validator) NonNegative(field string, value int) *Validator {
	if value < 0 {
		v.errors.Add(field, "value cannot be negative", "negative", fmt.Sprintf("%d", value))
	}
	return v
}

// Array/Slice validation methods

// NotEmpty validates that slice is not empty
func (v *Validator) NotEmpty(field string, slice []string) *Validator {
	if len(slice) == 0 {
		v.errors.Add(field, "cannot be empty", "empty_array")
	}
	return v
}

// MaxItems validates maximum number of items in slice
func (v *Validator) MaxItems(field string, slice []string, max int) *Validator {
	if len(slice) > max {
		v.errors.Add(field, fmt.Sprintf("maximum %d items allowed", max), "too_many_items", fmt.Sprintf("%d items", len(slice)))
	}
	return v
}

// MinItems validates minimum number of items in slice
func (v *Validator) MinItems(field string, slice []string, min int) *Validator {
	if len(slice) < min {
		v.errors.Add(field, fmt.Sprintf("minimum %d items required", min), "too_few_items", fmt.Sprintf("%d items", len(slice)))
	}
	return v
}

// UniqueItems validates that all items in slice are unique
func (v *Validator) UniqueItems(field string, slice []string) *Validator {
	seen := make(map[string]bool)
	for _, item := range slice {
		if seen[item] {
			v.errors.Add(field, fmt.Sprintf("duplicate item '%s' found", item), "duplicate_item", item)
			return v
		}
		seen[item] = true
	}
	return v
}

// NoEmptyItems validates that no items in slice are empty
func (v *Validator) NoEmptyItems(field string, slice []string) *Validator {
	for i, item := range slice {
		if strings.TrimSpace(item) == "" {
			v.errors.Add(field, fmt.Sprintf("item at index %d is empty", i), "empty_item")
			return v
		}
	}
	return v
}

// Business logic validation methods

// ValidatePipelineName validates pipeline name according to business rules
func (v *Validator) ValidatePipelineName(name string) *Validator {
	v.Required("name", name).
		MinLength("name", name, 3).
		MaxLength("name", name, 100).
		AlphaNumeric("name", name, "-", "_").
		NoSpaces("name", name)

	// Additional business rules
	if strings.HasPrefix(name, "-") || strings.HasSuffix(name, "-") {
		v.errors.Add("name", "cannot start or end with hyphen", "invalid_name_format", name)
	}
	if strings.HasPrefix(name, "_") || strings.HasSuffix(name, "_") {
		v.errors.Add("name", "cannot start or end with underscore", "invalid_name_format", name)
	}

	return v
}

// ValidatePluginName validates plugin name according to business rules
func (v *Validator) ValidatePluginName(name string) *Validator {
	v.Required("name", name).
		MinLength("name", name, 2).
		MaxLength("name", name, 80).
		AlphaNumeric("name", name, "-", "_", ".")

	// Plugin-specific rules
	if strings.Contains(name, "..") {
		v.errors.Add("name", "consecutive dots are not allowed", "invalid_name_format", name)
	}

	return v
}

// ValidateVersion validates semantic version format
func (v *Validator) ValidateVersion(version string) *Validator {
	semverPattern := `^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$`
	v.Required("version", version).
		Pattern("version", version, semverPattern, "invalid semantic version format (expected: major.minor.patch)")

	return v
}

// ValidateDescription validates description field
func (v *Validator) ValidateDescription(description string, required bool) *Validator {
	if required {
		v.Required("description", description)
	}
	if description != "" {
		v.MaxLength("description", description, 1000)
	}
	return v
}

// ValidateTags validates tags array
func (v *Validator) ValidateTags(tags []string) *Validator {
	v.MaxItems("tags", tags, 20).
		UniqueItems("tags", tags).
		NoEmptyItems("tags", tags)

	// Validate each tag format
	for _, tag := range tags {
		v.MinLength("tag", tag, 1).
			MaxLength("tag", tag, 50).
			AlphaNumeric("tag", tag, "-", "_")
	}

	return v
}

// Security validation methods

// ValidateUserInput sanitizes and validates user input for security
func (v *Validator) ValidateUserInput(field, value string) *Validator {
	// Check for potential XSS patterns
	xssPatterns := []string{
		`<script`,
		`javascript:`,
		`onload=`,
		`onerror=`,
		`onclick=`,
		`eval(`,
		`document.`,
		`window.`,
	}

	lowerValue := strings.ToLower(value)
	for _, pattern := range xssPatterns {
		if strings.Contains(lowerValue, pattern) {
			v.errors.Add(field, "potentially unsafe content detected", "security_violation", value)
			break
		}
	}

	return v
}

// ValidateFilePath validates file path for security
func (v *Validator) ValidateFilePath(field, path string) *Validator {
	// Check for path traversal attempts
	dangerous := []string{
		"..",
		"/etc/",
		"/proc/",
		"/sys/",
		"~",
		"$",
	}

	for _, danger := range dangerous {
		if strings.Contains(path, danger) {
			v.errors.Add(field, "potentially unsafe path detected", "unsafe_path", path)
			break
		}
	}

	return v
}
