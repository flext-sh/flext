package config

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/logging"
)

// MeltanoConfig represents comprehensive Meltano configuration
type MeltanoConfig struct {
	// Python environment
	PythonPath string `json:"python_path"`
	VenvPath   string `json:"venv_path"`
	PipPath    string `json:"pip_path"`

	// Meltano configuration
	MeltanoPath    string `json:"meltano_path"`
	ProjectRoot    string `json:"project_root"`
	DefaultProject string `json:"default_project"`

	// Bridge configuration
	BridgeModule  string        `json:"bridge_module"`
	BridgeTimeout time.Duration `json:"bridge_timeout"`
	MaxRetries    int           `json:"max_retries"`
	RetryDelay    time.Duration `json:"retry_delay"`

	// Performance configuration
	MaxConcurrent int           `json:"max_concurrent"`
	PoolSize      int           `json:"pool_size"`
	IdleTimeout   time.Duration `json:"idle_timeout"`

	// Environment variables
	EnvVars map[string]string `json:"env_vars"`

	// State management
	StateBackend string `json:"state_backend"`
	StateDir     string `json:"state_dir"`

	// Validation status
	Validated        bool     `json:"validated"`
	ValidationErrors []string `json:"validation_errors"`
}

// DefaultMeltanoConfig creates a configuration with sensible defaults
func DefaultMeltanoConfig() *MeltanoConfig {
	return &MeltanoConfig{
		PythonPath:    "python3",
		VenvPath:      "",
		MeltanoPath:   "meltano",
		ProjectRoot:   ".",
		BridgeModule:  "meltano_bridge",
		BridgeTimeout: 30 * time.Second,
		MaxRetries:    3,
		RetryDelay:    1 * time.Second,
		MaxConcurrent: 5,
		PoolSize:      3,
		IdleTimeout:   5 * time.Minute,
		EnvVars:       make(map[string]string),
		StateBackend:  "filesystem",
		StateDir:      "./meltano_state",
		Validated:     false,
	}
}

// AutoDetectConfiguration automatically detects the best Meltano configuration
func AutoDetectConfiguration(logger logging.Logger) (*MeltanoConfig, error) {
	config := DefaultMeltanoConfig()

	logger.Info("Starting Meltano environment auto-detection")

	// 1. Detect Python environment
	if err := config.detectPythonEnvironment(logger); err != nil {
		return nil, fmt.Errorf("failed to detect Python environment: %w", err)
	}

	// 2. Detect Meltano installation
	if err := config.detectMeltanoInstallation(logger); err != nil {
		return nil, fmt.Errorf("failed to detect Meltano installation: %w", err)
	}

	// 3. Setup bridge module
	if err := config.setupBridgeModule(logger); err != nil {
		return nil, fmt.Errorf("failed to setup bridge module: %w", err)
	}

	// 4. Validate configuration
	if err := config.Validate(logger); err != nil {
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}

	config.Validated = true
	logger.Info("Meltano configuration auto-detection completed successfully")

	return config, nil
}

// detectPythonEnvironment finds the best Python environment
func (c *MeltanoConfig) detectPythonEnvironment(logger logging.Logger) error {
	logger.Debug("Detecting Python environment")

	// Priority order for Python detection
	pythonCandidates := []string{
		os.Getenv("PYTHON_PATH"),
		"./venv/bin/python3",
		"./venv/bin/python",
		"./.venv/bin/python3",
		"./.venv/bin/python",
		"/home/marlonsc/flext/.venv/bin/python3",
		"python3",
		"python",
	}

	for _, candidate := range pythonCandidates {
		if candidate == "" {
			continue
		}

		// Test if Python path is valid and has required modules
		if c.testPythonPath(candidate, logger) {
			c.PythonPath = candidate

			// Try to detect virtual environment
			if strings.Contains(candidate, "venv") || strings.Contains(candidate, ".venv") {
				c.VenvPath = filepath.Dir(filepath.Dir(candidate))
				c.PipPath = filepath.Join(filepath.Dir(candidate), "pip")
			}

			logger.Info("Python environment detected",
				logging.F("python_path", c.PythonPath),
				logging.F("venv_path", c.VenvPath))
			return nil
		}
	}

	return fmt.Errorf("no valid Python environment found")
}

// testPythonPath tests if a Python path is valid and has required modules
func (c *MeltanoConfig) testPythonPath(pythonPath string, logger logging.Logger) bool {
	// Test basic Python execution
	cmd := exec.Command(pythonPath, "-c", "import sys; print(sys.version)")
	if err := cmd.Run(); err != nil {
		logger.Debug("Python path test failed",
			logging.F("path", pythonPath),
			logging.F("error", err.Error()))
		return false
	}

	// Test required modules
	requiredModules := []string{"json", "subprocess", "pathlib"}
	for _, module := range requiredModules {
		cmd := exec.Command(pythonPath, "-c", fmt.Sprintf("import %s", module))
		if err := cmd.Run(); err != nil {
			logger.Debug("Required module test failed",
				logging.F("path", pythonPath),
				logging.F("module", module))
			return false
		}
	}

	return true
}

// detectMeltanoInstallation finds Meltano installation
func (c *MeltanoConfig) detectMeltanoInstallation(logger logging.Logger) error {
	logger.Debug("Detecting Meltano installation")

	// Try different Meltano command variations
	meltanoCandidates := []string{
		"meltano",
	}

	// If we have a venv, try meltano in that venv
	if c.VenvPath != "" {
		meltanoCandidates = append([]string{
			filepath.Join(c.VenvPath, "bin", "meltano"),
		}, meltanoCandidates...)
	}

	for _, candidate := range meltanoCandidates {
		if c.testMeltanoPath(candidate, logger) {
			c.MeltanoPath = candidate
			logger.Info("Meltano installation detected", logging.F("meltano_path", c.MeltanoPath))
			return nil
		}
	}

	// If not found, try to install via pip
	if c.PipPath != "" {
		logger.Info("Meltano not found, attempting to install via pip")
		if c.installMeltano(logger) {
			// Retry detection
			for _, candidate := range meltanoCandidates {
				if c.testMeltanoPath(candidate, logger) {
					c.MeltanoPath = candidate
					logger.Info("Meltano installed and detected", logging.F("meltano_path", c.MeltanoPath))
					return nil
				}
			}
		}
	}

	// Fallback: use meltano via Python module
	if c.testMeltanoViaPython(logger) {
		c.MeltanoPath = fmt.Sprintf("%s -m meltano", c.PythonPath)
		logger.Info("Meltano detected via Python module")
		return nil
	}

	return fmt.Errorf("Meltano installation not found")
}

// testMeltanoPath tests if a Meltano path is valid
func (c *MeltanoConfig) testMeltanoPath(meltanoPath string, logger logging.Logger) bool {
	cmd := exec.Command(meltanoPath, "--version")
	cmd.Env = c.buildEnvironment()
	if err := cmd.Run(); err != nil {
		logger.Debug("Meltano path test failed",
			logging.F("path", meltanoPath),
			logging.F("error", err.Error()))
		return false
	}
	return true
}

// testMeltanoViaPython tests if Meltano can be run via Python module
func (c *MeltanoConfig) testMeltanoViaPython(logger logging.Logger) bool {
	cmd := exec.Command(c.PythonPath, "-m", "meltano", "--version")
	cmd.Env = c.buildEnvironment()
	if err := cmd.Run(); err != nil {
		logger.Debug("Meltano via Python test failed", logging.F("error", err.Error()))
		return false
	}
	return true
}

// installMeltano attempts to install Meltano via pip
func (c *MeltanoConfig) installMeltano(logger logging.Logger) bool {
	if c.PipPath == "" {
		return false
	}

	logger.Info("Installing Meltano via pip")
	cmd := exec.Command(c.PipPath, "install", "meltano>=3.2.0")
	cmd.Env = c.buildEnvironment()

	if err := cmd.Run(); err != nil {
		logger.Warn("Failed to install Meltano via pip", logging.F("error", err.Error()))
		return false
	}

	logger.Info("Meltano installed successfully via pip")
	return true
}

// setupBridgeModule ensures the Python bridge module is available
func (c *MeltanoConfig) setupBridgeModule(logger logging.Logger) error {
	logger.Debug("Setting up bridge module")

	// Check if bridge module is importable
	cmd := exec.Command(c.PythonPath, "-c", fmt.Sprintf("import %s", c.BridgeModule))
	cmd.Env = c.buildEnvironment()

	if err := cmd.Run(); err != nil {
		// Try to install the bridge module
		bridgePath := "./python-meltano-bridge"
		if _, err := os.Stat(bridgePath); err == nil {
			logger.Info("Installing bridge module")
			cmd := exec.Command(c.PipPath, "install", "-e", bridgePath)
			cmd.Env = c.buildEnvironment()

			if err := cmd.Run(); err != nil {
				logger.Warn("Failed to install bridge module", logging.F("error", err.Error()))
			} else {
				logger.Info("Bridge module installed successfully")
			}
		}
	}

	return nil
}

// buildEnvironment builds the environment variables for subprocess execution
func (c *MeltanoConfig) buildEnvironment() []string {
	env := os.Environ()

	// Add custom environment variables
	for key, value := range c.EnvVars {
		env = append(env, fmt.Sprintf("%s=%s", key, value))
	}

	// Set Python path if using venv
	if c.VenvPath != "" {
		env = append(env, fmt.Sprintf("VIRTUAL_ENV=%s", c.VenvPath))
		env = append(env, fmt.Sprintf("PATH=%s:%s", filepath.Join(c.VenvPath, "bin"), os.Getenv("PATH")))
	}

	return env
}

// Validate validates the configuration
func (c *MeltanoConfig) Validate(logger logging.Logger) error {
	logger.Debug("Validating Meltano configuration")

	c.ValidationErrors = []string{}

	// Validate Python path
	if c.PythonPath == "" {
		c.ValidationErrors = append(c.ValidationErrors, "Python path is required")
	} else if !c.testPythonPath(c.PythonPath, logger) {
		c.ValidationErrors = append(c.ValidationErrors, "Python path is not valid or accessible")
	}

	// Validate Meltano path
	if c.MeltanoPath == "" {
		c.ValidationErrors = append(c.ValidationErrors, "Meltano path is required")
	}

	// Validate timeouts
	if c.BridgeTimeout <= 0 {
		c.ValidationErrors = append(c.ValidationErrors, "Bridge timeout must be positive")
	}

	// Validate concurrency settings
	if c.MaxConcurrent <= 0 {
		c.ValidationErrors = append(c.ValidationErrors, "Max concurrent must be positive")
	}

	if c.PoolSize <= 0 {
		c.ValidationErrors = append(c.ValidationErrors, "Pool size must be positive")
	}

	// Create state directory if needed
	if c.StateDir != "" {
		if err := os.MkdirAll(c.StateDir, 0755); err != nil {
			c.ValidationErrors = append(c.ValidationErrors, fmt.Sprintf("Cannot create state directory: %v", err))
		}
	}

	if len(c.ValidationErrors) > 0 {
		return fmt.Errorf("configuration validation failed: %v", c.ValidationErrors)
	}

	logger.Info("Meltano configuration validation successful",
		logging.F("python_path", c.PythonPath),
		logging.F("meltano_path", c.MeltanoPath),
		logging.F("bridge_timeout", c.BridgeTimeout),
		logging.F("max_concurrent", c.MaxConcurrent))

	return nil
}

// ToMap converts the configuration to a map for JSON serialization
func (c *MeltanoConfig) ToMap() map[string]interface{} {
	return map[string]interface{}{
		"python_path":       c.PythonPath,
		"venv_path":         c.VenvPath,
		"meltano_path":      c.MeltanoPath,
		"project_root":      c.ProjectRoot,
		"bridge_module":     c.BridgeModule,
		"bridge_timeout":    c.BridgeTimeout.String(),
		"max_retries":       c.MaxRetries,
		"max_concurrent":    c.MaxConcurrent,
		"pool_size":         c.PoolSize,
		"state_backend":     c.StateBackend,
		"state_dir":         c.StateDir,
		"validated":         c.Validated,
		"validation_errors": c.ValidationErrors,
	}
}
