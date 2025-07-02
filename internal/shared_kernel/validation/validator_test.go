package validation

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestValidator_Required tests required field validation
func TestValidator_Required(t *testing.T) {
	tests := []struct {
		name        string
		field       string
		value       string
		expectError bool
	}{
		{"valid value", "name", "test-value", false},
		{"empty string", "name", "", true},
		{"whitespace only", "name", "   ", true},
		{"tab and newline", "name", "\t\n", true},
		{"single space", "name", " ", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.Required(tt.field, tt.value)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				assert.Contains(t, validator.Error().Error(), "field is required")
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_Length tests length validation methods
func TestValidator_Length(t *testing.T) {
	t.Run("MinLength", func(t *testing.T) {
		tests := []struct {
			name        string
			value       string
			min         int
			expectError bool
		}{
			{"valid length", "hello", 3, false},
			{"exact minimum", "hi", 2, false},
			{"too short", "a", 3, true},
			{"empty string", "", 1, true},
			{"unicode characters", "🌟⭐", 2, false},
			{"unicode too short", "🌟", 2, true},
		}

		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				validator := NewValidator()
				validator.MinLength("field", tt.value, tt.min)

				if tt.expectError {
					assert.True(t, validator.HasErrors())
					assert.Contains(t, validator.Error().Error(), "minimum length")
				} else {
					assert.False(t, validator.HasErrors())
				}
			})
		}
	})

	t.Run("MaxLength", func(t *testing.T) {
		tests := []struct {
			name        string
			value       string
			max         int
			expectError bool
		}{
			{"valid length", "hello", 10, false},
			{"exact maximum", "hello", 5, false},
			{"too long", "hello world", 5, true},
			{"empty string", "", 0, false},
			{"unicode within limit", "🌟⭐", 3, false},
			{"unicode exceeds limit", "🌟⭐⚡", 2, true},
		}

		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				validator := NewValidator()
				validator.MaxLength("field", tt.value, tt.max)

				if tt.expectError {
					assert.True(t, validator.HasErrors())
					assert.Contains(t, validator.Error().Error(), "maximum length")
				} else {
					assert.False(t, validator.HasErrors())
				}
			})
		}
	})
}

// TestValidator_AlphaNumeric tests alphanumeric validation
func TestValidator_AlphaNumeric(t *testing.T) {
	tests := []struct {
		name         string
		value        string
		allowedChars []string
		expectError  bool
	}{
		{"letters only", "hello", nil, false},
		{"numbers only", "12345", nil, false},
		{"mixed alphanumeric", "hello123", nil, false},
		{"with allowed hyphen", "hello-world", []string{"-"}, false},
		{"with allowed underscore", "hello_world", []string{"_"}, false},
		{"with multiple allowed", "hello-world_123", []string{"-", "_"}, false},
		{"with spaces", "hello world", nil, true},
		{"with special chars", "hello@world", nil, true},
		{"with disallowed chars", "hello-world", nil, true},
		{"empty string", "", nil, false},
		{"unicode letters", "héllo", nil, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.AlphaNumeric("field", tt.value, tt.allowedChars...)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				assert.Contains(t, validator.Error().Error(), "invalid characters")
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_Pattern tests regex pattern validation
func TestValidator_Pattern(t *testing.T) {
	tests := []struct {
		name        string
		value       string
		pattern     string
		expectError bool
	}{
		{"valid email pattern", "test@example.com", `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`, false},
		{"invalid email", "invalid-email", `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`, true},
		{"version pattern", "1.2.3", `^\d+\.\d+\.\d+$`, false},
		{"invalid version", "1.2", `^\d+\.\d+\.\d+$`, true},
		{"empty string", "", `^.+$`, true},
		{"valid empty pattern", "", `^.*$`, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.Pattern("field", tt.value, tt.pattern, "pattern does not match")

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				assert.Contains(t, validator.Error().Error(), "pattern")
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_Email tests email validation
func TestValidator_Email(t *testing.T) {
	tests := []struct {
		name        string
		email       string
		expectError bool
	}{
		{"valid email", "test@example.com", false},
		{"valid email with plus", "test+tag@example.com", false},
		{"valid email with subdomain", "test@mail.example.com", false},
		{"invalid email - missing @", "testexample.com", true},
		{"invalid email - missing domain", "test@", true},
		{"invalid email - missing user", "@example.com", true},
		{"invalid email - spaces", "test @example.com", true},
		{"empty email", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.Email("email", tt.email)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				assert.Contains(t, validator.Error().Error(), "invalid email")
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_NumericValidation tests numeric validation methods
func TestValidator_NumericValidation(t *testing.T) {
	t.Run("Min", func(t *testing.T) {
		validator := NewValidator()
		validator.Min("port", 80, 1024)
		assert.True(t, validator.HasErrors())
		assert.Contains(t, validator.Error().Error(), "minimum value is 1024")

		validator.Reset()
		validator.Min("port", 8080, 1024)
		assert.False(t, validator.HasErrors())
	})

	t.Run("Max", func(t *testing.T) {
		validator := NewValidator()
		validator.Max("port", 70000, 65535)
		assert.True(t, validator.HasErrors())
		assert.Contains(t, validator.Error().Error(), "maximum value is 65535")

		validator.Reset()
		validator.Max("port", 8080, 65535)
		assert.False(t, validator.HasErrors())
	})

	t.Run("Range", func(t *testing.T) {
		validator := NewValidator()
		validator.Range("port", 80, 1024, 65535)
		assert.True(t, validator.HasErrors())

		validator.Reset()
		validator.Range("port", 70000, 1024, 65535)
		assert.True(t, validator.HasErrors())

		validator.Reset()
		validator.Range("port", 8080, 1024, 65535)
		assert.False(t, validator.HasErrors())
	})

	t.Run("Positive", func(t *testing.T) {
		validator := NewValidator()
		validator.Positive("count", 0)
		assert.True(t, validator.HasErrors())

		validator.Reset()
		validator.Positive("count", -5)
		assert.True(t, validator.HasErrors())

		validator.Reset()
		validator.Positive("count", 5)
		assert.False(t, validator.HasErrors())
	})
}

// TestValidator_ArrayValidation tests array/slice validation methods
func TestValidator_ArrayValidation(t *testing.T) {
	t.Run("UniqueItems", func(t *testing.T) {
		validator := NewValidator()
		validator.UniqueItems("tags", []string{"tag1", "tag2", "tag1"})
		assert.True(t, validator.HasErrors())
		assert.Contains(t, validator.Error().Error(), "duplicate item")

		validator.Reset()
		validator.UniqueItems("tags", []string{"tag1", "tag2", "tag3"})
		assert.False(t, validator.HasErrors())
	})

	t.Run("NoEmptyItems", func(t *testing.T) {
		validator := NewValidator()
		validator.NoEmptyItems("tags", []string{"tag1", "", "tag3"})
		assert.True(t, validator.HasErrors())
		assert.Contains(t, validator.Error().Error(), "empty")

		validator.Reset()
		validator.NoEmptyItems("tags", []string{"tag1", "tag2", "tag3"})
		assert.False(t, validator.HasErrors())
	})

	t.Run("MaxItems", func(t *testing.T) {
		validator := NewValidator()
		validator.MaxItems("tags", []string{"a", "b", "c"}, 2)
		assert.True(t, validator.HasErrors())
		assert.Contains(t, validator.Error().Error(), "maximum 2 items")

		validator.Reset()
		validator.MaxItems("tags", []string{"a", "b"}, 2)
		assert.False(t, validator.HasErrors())
	})
}

// TestValidator_PipelineValidation tests pipeline-specific validation
func TestValidator_PipelineValidation(t *testing.T) {
	tests := []struct {
		name          string
		pipelineName  string
		expectError   bool
		errorContains string
	}{
		{"valid name", "my-pipeline", false, ""},
		{"valid with underscore", "my_pipeline", false, ""},
		{"valid with numbers", "pipeline-123", false, ""},
		{"too short", "ab", true, "minimum length"},
		{"too long", strings.Repeat("a", 101), true, "maximum length"},
		{"with spaces", "my pipeline", true, "spaces"},
		{"starts with hyphen", "-pipeline", true, "cannot start"},
		{"ends with hyphen", "pipeline-", true, "cannot start or end"},
		{"starts with underscore", "_pipeline", true, "cannot start"},
		{"ends with underscore", "pipeline_", true, "cannot start or end"},
		{"empty name", "", true, "required"},
		{"special characters", "pipeline@test", true, "invalid characters"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.ValidatePipelineName(tt.pipelineName)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				if tt.errorContains != "" {
					assert.Contains(t, validator.Error().Error(), tt.errorContains)
				}
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_PluginValidation tests plugin-specific validation
func TestValidator_PluginValidation(t *testing.T) {
	tests := []struct {
		name          string
		pluginName    string
		expectError   bool
		errorContains string
	}{
		{"valid name", "my-plugin", false, ""},
		{"valid with dots", "my.plugin", false, ""},
		{"valid short name", "ab", false, ""},
		{"too short", "a", true, "minimum length"},
		{"too long", strings.Repeat("a", 81), true, "maximum length"},
		{"consecutive dots", "my..plugin", true, "consecutive dots"},
		{"empty name", "", true, "required"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.ValidatePluginName(tt.pluginName)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				if tt.errorContains != "" {
					assert.Contains(t, validator.Error().Error(), tt.errorContains)
				}
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_VersionValidation tests semantic version validation
func TestValidator_VersionValidation(t *testing.T) {
	tests := []struct {
		name        string
		version     string
		expectError bool
	}{
		{"valid version", "1.2.3", false},
		{"valid with v prefix", "v1.2.3", false},
		{"valid with prerelease", "1.2.3-alpha", false},
		{"valid with build", "1.2.3+build.1", false},
		{"valid complex", "1.2.3-alpha.1+build.123", false},
		{"missing patch", "1.2", true},
		{"missing minor", "1", true},
		{"invalid format", "1.2.3.4", true},
		{"non-numeric", "a.b.c", true},
		{"empty version", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			validator := NewValidator()
			validator.ValidateVersion(tt.version)

			if tt.expectError {
				assert.True(t, validator.HasErrors())
				assert.Contains(t, validator.Error().Error(), "version")
			} else {
				assert.False(t, validator.HasErrors())
			}
		})
	}
}

// TestValidator_SecurityValidation tests security-related validation
func TestValidator_SecurityValidation(t *testing.T) {
	t.Run("XSS Detection", func(t *testing.T) {
		maliciousInputs := []string{
			"<script>alert('xss')</script>",
			"javascript:alert('xss')",
			"<img onload='alert(1)'>",
			"<div onclick='evil()'>",
			"eval(dangerous_code)",
			"document.write('hack')",
			"window.location='evil.com'",
		}

		for _, input := range maliciousInputs {
			validator := NewValidator()
			validator.ValidateUserInput("field", input)
			assert.True(t, validator.HasErrors(), "Should detect XSS in: %s", input)
			if validator.HasErrors() {
				assert.Contains(t, validator.Error().Error(), "unsafe content")
			}
		}
	})

	t.Run("Path Traversal Detection", func(t *testing.T) {
		dangerousPaths := []string{
			"../../../etc/passwd",
			"/etc/passwd",
			"~/secret",
			"$HOME/secret",
			"/proc/version",
			"/sys/kernel",
		}

		for _, path := range dangerousPaths {
			validator := NewValidator()
			validator.ValidateFilePath("path", path)
			assert.True(t, validator.HasErrors(), "Should detect dangerous path: %s", path)
			assert.Contains(t, validator.Error().Error(), "unsafe path")
		}
	})
}

// TestValidator_MultipleErrors tests handling of multiple validation errors
func TestValidator_MultipleErrors(t *testing.T) {
	validator := NewValidator()

	// Add multiple validation errors
	validator.Required("name", "").
		MinLength("description", "ab", 5).
		Max("port", 70000, 65535).
		UniqueItems("tags", []string{"a", "b", "a"})

	require.True(t, validator.HasErrors())

	errors := validator.Errors()
	assert.Len(t, errors, 4)

	// Check that all errors are present
	errorStr := validator.Error().Error()
	assert.Contains(t, errorStr, "name")
	assert.Contains(t, errorStr, "description")
	assert.Contains(t, errorStr, "port")
	assert.Contains(t, errorStr, "tags")
}

// TestValidationErrors tests ValidationErrors type
func TestValidationErrors(t *testing.T) {
	t.Run("Empty errors", func(t *testing.T) {
		var errors ValidationErrors
		assert.False(t, errors.HasErrors())
		assert.Equal(t, "no validation errors", errors.Error())
	})

	t.Run("Single error", func(t *testing.T) {
		var errors ValidationErrors
		errors.Add("name", "is required", "required")
		assert.True(t, errors.HasErrors())
		assert.Contains(t, errors.Error(), "name")
		assert.Contains(t, errors.Error(), "is required")
	})

	t.Run("Multiple errors", func(t *testing.T) {
		var errors ValidationErrors
		errors.Add("name", "is required", "required")
		errors.Add("email", "invalid format", "invalid_email")
		assert.True(t, errors.HasErrors())
		assert.Contains(t, errors.Error(), "multiple validation errors")
		assert.Contains(t, errors.Error(), "name")
		assert.Contains(t, errors.Error(), "email")
	})
}

// TestSanitization tests string sanitization functions
func TestSanitization(t *testing.T) {
	t.Run("SanitizeString", func(t *testing.T) {
		tests := []struct {
			name     string
			input    string
			expected string
		}{
			{"trim whitespace", "  hello world  ", "hello world"},
			{"remove null bytes", "hello\x00world", "helloworld"},
			{"preserve newlines", "hello\nworld", "hello\nworld"},
			{"preserve tabs", "hello\tworld", "hello\tworld"},
			{"remove control chars", "hello\x01\x02world", "helloworld"},
			{"unicode safe", "héllo wörld 🌟", "héllo wörld 🌟"},
		}

		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				result := SanitizeString(tt.input)
				assert.Equal(t, tt.expected, result)
			})
		}
	})

	t.Run("SanitizeName", func(t *testing.T) {
		tests := []struct {
			name     string
			input    string
			expected string
		}{
			{"simple name", "Hello World", "hello-world"},
			{"with special chars", "My@Project#Name!", "myprojectname"},
			{"multiple spaces", "hello    world", "hello-world"},
			{"trim hyphens", "-hello-world-", "hello-world"},
			{"trim underscores", "_hello_world_", "hello_world"},
			{"unicode to ascii", "héllo wörld", "hello-world"},
			{"preserve valid chars", "my-project_123", "my-project_123"},
		}

		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				result := SanitizeName(tt.input)
				assert.Equal(t, tt.expected, result)
			})
		}
	})
}

// TestValidateCreatePipelineRequest tests complete pipeline validation
func TestValidateCreatePipelineRequest(t *testing.T) {
	tests := []struct {
		name         string
		pipelineName string
		description  string
		tags         []string
		expectError  bool
	}{
		{
			name:         "valid request",
			pipelineName: "my-pipeline",
			description:  "A test pipeline",
			tags:         []string{"test", "example"},
			expectError:  false,
		},
		{
			name:         "invalid name",
			pipelineName: "",
			description:  "A test pipeline",
			tags:         []string{"test"},
			expectError:  true,
		},
		{
			name:         "duplicate tags",
			pipelineName: "my-pipeline",
			description:  "A test pipeline",
			tags:         []string{"test", "test"},
			expectError:  true,
		},
		{
			name:         "too long description",
			pipelineName: "my-pipeline",
			description:  strings.Repeat("a", 1001),
			tags:         []string{"test"},
			expectError:  true,
		},
		{
			name:         "security violation",
			pipelineName: "my-pipeline",
			description:  "<script>alert('xss')</script>",
			tags:         []string{"test"},
			expectError:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateCreatePipelineRequest(tt.pipelineName, tt.description, tt.tags)

			if tt.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

// TestValidateRegisterPluginRequest tests complete plugin validation
func TestValidateRegisterPluginRequest(t *testing.T) {
	tests := []struct {
		name         string
		pluginName   string
		pluginType   string
		version      string
		description  string
		author       string
		entryPoint   string
		dependencies []string
		expectError  bool
	}{
		{
			name:         "valid request",
			pluginName:   "my-plugin",
			pluginType:   "source",
			version:      "1.0.0",
			description:  "A test plugin",
			author:       "Test Author",
			entryPoint:   "main.py",
			dependencies: []string{"requests", "pandas"},
			expectError:  false,
		},
		{
			name:         "invalid type",
			pluginName:   "my-plugin",
			pluginType:   "invalid",
			version:      "1.0.0",
			description:  "A test plugin",
			author:       "Test Author",
			entryPoint:   "main.py",
			dependencies: []string{},
			expectError:  true,
		},
		{
			name:         "invalid version",
			pluginName:   "my-plugin",
			pluginType:   "source",
			version:      "invalid",
			description:  "A test plugin",
			author:       "Test Author",
			entryPoint:   "main.py",
			dependencies: []string{},
			expectError:  true,
		},
		{
			name:         "dangerous entry point",
			pluginName:   "my-plugin",
			pluginType:   "source",
			version:      "1.0.0",
			description:  "A test plugin",
			author:       "Test Author",
			entryPoint:   "../../../etc/passwd",
			dependencies: []string{},
			expectError:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateRegisterPluginRequest(
				tt.pluginName,
				tt.pluginType,
				tt.version,
				tt.description,
				tt.author,
				tt.entryPoint,
				tt.dependencies,
			)

			if tt.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

// BenchmarkValidation benchmarks validation performance
func BenchmarkValidation(b *testing.B) {
	b.Run("PipelineName", func(b *testing.B) {
		validator := NewValidator()
		for i := 0; i < b.N; i++ {
			validator.Reset()
			validator.ValidatePipelineName("my-test-pipeline")
		}
	})

	b.Run("CompleteRequest", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			_ = ValidateCreatePipelineRequest(
				"my-pipeline",
				"A test pipeline description",
				[]string{"test", "benchmark"},
			)
		}
	})

	b.Run("SecurityValidation", func(b *testing.B) {
		validator := NewValidator()
		maliciousInput := "<script>alert('xss')</script>with some additional text"
		for i := 0; i < b.N; i++ {
			validator.Reset()
			validator.ValidateUserInput("field", maliciousInput)
		}
	})
}
