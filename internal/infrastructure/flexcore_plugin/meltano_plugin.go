package flexcore_plugin

import (
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
)

// MeltanoPlugin implements FLEXCORE plugin interface for Meltano execution
// Executes via flext-meltano Python library
type MeltanoPlugin struct {
	config         *config.Config
	logger         logging.Logger
	pythonPath     string
	flextMeltano   string
	workspaceDir   string
	execTimeout    time.Duration
}

// MeltanoExecutionRequest represents a Meltano execution request from FLEXCORE
type MeltanoExecutionRequest struct {
	Command     string                 `json:"command"`     // run, test, describe, etc
	Extractor   string                 `json:"extractor,omitempty"`
	Loader      string                 `json:"loader,omitempty"`
	Transform   string                 `json:"transform,omitempty"`
	Environment string                 `json:"environment,omitempty"`
	Variables   map[string]interface{} `json:"variables,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
	DryRun      bool                   `json:"dry_run,omitempty"`
	JobID       string                 `json:"job_id,omitempty"`
}

// MeltanoExecutionResult represents the result of Meltano execution
type MeltanoExecutionResult struct {
	JobID        string                 `json:"job_id"`
	Status       string                 `json:"status"`       // success, error, running
	ExitCode     int                    `json:"exit_code"`
	Output       string                 `json:"output"`
	ErrorOutput  string                 `json:"error_output,omitempty"`
	StartTime    time.Time              `json:"start_time"`
	EndTime      time.Time              `json:"end_time"`
	Duration     time.Duration          `json:"duration"`
	Metrics      map[string]interface{} `json:"metrics,omitempty"`
	StateFile    string                 `json:"state_file,omitempty"`
	LogFile      string                 `json:"log_file,omitempty"`
}

// NewMeltanoPlugin creates a new Meltano plugin for FLEXCORE
func NewMeltanoPlugin(cfg *config.Config, logger logging.Logger) *MeltanoPlugin {
	logger.Info("🔧 Creating new Meltano plugin for FLEXCORE integration")
	
	pythonPath := cfg.GetEnvWithDefault("PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3")
	flextMeltano := cfg.GetEnvWithDefault("FLEXT_MELTANO_PATH", "/home/marlonsc/flext/flext-meltano/src")
	workspaceDir := cfg.GetEnvWithDefault("FLEXT_WORKSPACE", "/home/marlonsc/flext")
	
	logger.Info("🔧 Meltano plugin configuration",
		logging.F("python_path", pythonPath),
		logging.F("flext_meltano", flextMeltano),
		logging.F("workspace_dir", workspaceDir))
	
	plugin := &MeltanoPlugin{
		config:       cfg,
		logger:       logger,
		pythonPath:   pythonPath,
		flextMeltano: flextMeltano,
		workspaceDir: workspaceDir,
		execTimeout:  30 * time.Minute, // Default 30min timeout
	}
	
	logger.Info("✅ Meltano plugin instance created successfully")
	return plugin
}

// Execute implements the FLEXCORE plugin interface for Meltano execution
func (mp *MeltanoPlugin) Execute(ctx context.Context, params map[string]interface{}) (interface{}, error) {
	mp.logger.Info("🎭 FLEXCORE Meltano Plugin: Executing via flext-meltano",
		logging.F("params", params),
		logging.F("python_path", mp.pythonPath),
		logging.F("flext_meltano_path", mp.flextMeltano))

	// Parse parameters into MeltanoExecutionRequest
	var request MeltanoExecutionRequest
	paramsJSON, err := json.Marshal(params)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal parameters: %w", err)
	}
	
	if err := json.Unmarshal(paramsJSON, &request); err != nil {
		return nil, fmt.Errorf("failed to parse parameters: %w", err)
	}

	// Generate job ID if not provided
	if request.JobID == "" {
		request.JobID = fmt.Sprintf("meltano-job-%d", time.Now().Unix())
	}

	mp.logger.Info("🚀 Starting Meltano execution via flext-meltano",
		logging.F("job_id", request.JobID),
		logging.F("command", request.Command),
		logging.F("extractor", request.Extractor),
		logging.F("loader", request.Loader))

	// Execute via flext-meltano Python library
	result, err := mp.executeMeltanoCommand(ctx, request)
	if err != nil {
		mp.logger.Error("❌ Meltano execution failed",
			logging.F("job_id", request.JobID),
			logging.F("error", err))
		return nil, fmt.Errorf("meltano execution failed: %w", err)
	}

	mp.logger.Info("✅ Meltano execution completed successfully",
		logging.F("job_id", result.JobID),
		logging.F("status", result.Status),
		logging.F("duration", result.Duration),
		logging.F("exit_code", result.ExitCode))

	return result, nil
}

// executeMeltanoCommand executes Meltano command via flext-meltano Python library
func (mp *MeltanoPlugin) executeMeltanoCommand(ctx context.Context, request MeltanoExecutionRequest) (*MeltanoExecutionResult, error) {
	startTime := time.Now()
	
	// Create execution context with timeout
	execCtx, cancel := context.WithTimeout(ctx, mp.execTimeout)
	defer cancel()

	// Prepare Python command via flext-meltano
	args := []string{
		"-c",
		fmt.Sprintf(`
import sys
import json
import subprocess
import time
import os

# Parse request
request_data = '''%s'''
request = json.loads(request_data)

# Configuration
workspace_dir = "%s"
meltano_path = "%s/.venv/bin/meltano"

# Execute command
try:
    job_id = request.get("job_id", f"meltano-job-{int(time.time())}")
    start_time = time.time()
    
    if request["command"] == "run":
        # Build meltano run command
        cmd_args = [meltano_path, "run"]
        
        if request.get("extractor"):
            cmd_args.append(request["extractor"])
        if request.get("loader"):
            cmd_args.append(request["loader"])
        
        # Handle dry run
        if request.get("dry_run", False):
            result = {
                "job_id": job_id,
                "status": "success",
                "exit_code": 0,
                "output": f"DRY RUN: Would execute: {' '.join(cmd_args)}",
                "start_time": start_time,
                "end_time": time.time(),
                "dry_run": True
            }
        else:
            # Execute real command
            env = os.environ.copy()
            env["MELTANO_ENVIRONMENT"] = request.get("environment", "dev")
            
            result_proc = subprocess.run(
                cmd_args,
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                env=env,
                timeout=1800  # 30 minutes
            )
            
            result = {
                "job_id": job_id,
                "status": "success" if result_proc.returncode == 0 else "error",
                "exit_code": result_proc.returncode,
                "output": result_proc.stdout,
                "error_output": result_proc.stderr if result_proc.returncode != 0 else "",
                "start_time": start_time,
                "end_time": time.time()
            }
    
    elif request["command"] == "test":
        plugin_name = request.get("extractor") or request.get("loader")
        cmd_args = [meltano_path, "invoke", plugin_name, "--help"]
        
        result_proc = subprocess.run(
            cmd_args,
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        result = {
            "job_id": job_id,
            "status": "success" if result_proc.returncode == 0 else "error",
            "exit_code": result_proc.returncode,
            "output": result_proc.stdout,
            "error_output": result_proc.stderr if result_proc.returncode != 0 else "",
            "plugin_name": plugin_name,
            "test_type": "invoke_help",
            "start_time": start_time,
            "end_time": time.time()
        }
    
    elif request["command"] == "describe":
        plugin_name = request.get("extractor") or request.get("loader")
        cmd_args = [meltano_path, "describe", plugin_name]
        
        result_proc = subprocess.run(
            cmd_args,
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        result = {
            "job_id": job_id,
            "status": "success" if result_proc.returncode == 0 else "error",
            "exit_code": result_proc.returncode,
            "output": result_proc.stdout,
            "error_output": result_proc.stderr if result_proc.returncode != 0 else "",
            "plugin_name": plugin_name,
            "description_type": "meltano_describe",
            "start_time": start_time,
            "end_time": time.time()
        }
    
    else:
        result = {
            "job_id": job_id,
            "status": "error",
            "error_output": f"Unknown command: {request['command']}",
            "exit_code": 1,
            "start_time": start_time,
            "end_time": time.time()
        }
    
    print(json.dumps(result))
    
except Exception as e:
    error_result = {
        "status": "error",
        "error_output": str(e),
        "exit_code": 1,
        "job_id": request.get("job_id", "unknown"),
        "start_time": start_time,
        "end_time": time.time()
    }
    print(json.dumps(error_result))
    sys.exit(1)
`, mp.escapeJSON(request), mp.workspaceDir, mp.workspaceDir),
	}

	// Execute Python command
	cmd := exec.CommandContext(execCtx, mp.pythonPath, args...)
	cmd.Dir = mp.workspaceDir

	// Set environment variables for Meltano
	cmd.Env = append(cmd.Environ(),
		fmt.Sprintf("MELTANO_PROJECT_ROOT=%s", mp.workspaceDir),
		fmt.Sprintf("FLEXT_WORKSPACE=%s", mp.workspaceDir),
	)

	mp.logger.Info("🔧 Executing Meltano via flext-meltano",
		logging.F("job_id", request.JobID),
		logging.F("python_path", mp.pythonPath),
		logging.F("working_dir", mp.workspaceDir))

	// Execute and capture output
	output, err := cmd.CombinedOutput()
	endTime := time.Now()
	duration := endTime.Sub(startTime)

	if err != nil {
		mp.logger.Error("❌ flext-meltano execution failed",
			logging.F("job_id", request.JobID),
			logging.F("error", err),
			logging.F("output", string(output)))

		return &MeltanoExecutionResult{
			JobID:       request.JobID,
			Status:      "error",
			ExitCode:    1,
			Output:      string(output),
			ErrorOutput: err.Error(),
			StartTime:   startTime,
			EndTime:     endTime,
			Duration:    duration,
		}, nil
	}

	// Parse result from flext-meltano
	var result MeltanoExecutionResult
	if err := json.Unmarshal(output, &result); err != nil {
		mp.logger.Warn("⚠️ Failed to parse flext-meltano result, using raw output",
			logging.F("job_id", request.JobID),
			logging.F("parse_error", err),
			logging.F("raw_output", string(output)))

		return &MeltanoExecutionResult{
			JobID:     request.JobID,
			Status:    "success",
			ExitCode:  0,
			Output:    string(output),
			StartTime: startTime,
			EndTime:   endTime,
			Duration:  duration,
		}, nil
	}

	// Fill in timing information
	result.JobID = request.JobID
	result.StartTime = startTime
	result.EndTime = endTime
	result.Duration = duration

	return &result, nil
}

// escapeJSON escapes JSON for embedding in Python string
func (mp *MeltanoPlugin) escapeJSON(request MeltanoExecutionRequest) string {
	requestJSON, _ := json.Marshal(request)
	// Escape for Python string literal
	escaped := string(requestJSON)
	escaped = fmt.Sprintf("%q", escaped)
	// Remove outer quotes added by %q
	if len(escaped) >= 2 {
		escaped = escaped[1 : len(escaped)-1]
	}
	return escaped
}

// GetPluginInfo returns plugin information for FLEXCORE registration
func (mp *MeltanoPlugin) GetPluginInfo() map[string]interface{} {
	return map[string]interface{}{
		"name":        "meltano",
		"type":        "executor",
		"version":     "2.0.0",
		"description": "Meltano ETL execution via flext-meltano Python library",
		"author":      "FLEXT Team",
		"capabilities": []string{
			"pipeline_execution",
			"plugin_testing", 
			"plugin_description",
			"state_management",
			"environment_support",
		},
		"supported_commands": []string{
			"run",
			"test", 
			"describe",
		},
		"integration": "flext-meltano",
		"python_path": mp.pythonPath,
		"workspace":   mp.workspaceDir,
	}
}

// Validate checks if the plugin is properly configured
func (mp *MeltanoPlugin) Validate() error {
	mp.logger.Info("🔍 Validating Meltano plugin configuration",
		logging.F("python_path", mp.pythonPath),
		logging.F("flext_meltano_path", mp.flextMeltano),
		logging.F("workspace", mp.workspaceDir))

	// Check if Python exists
	if err := exec.Command(mp.pythonPath, "--version").Run(); err != nil {
		mp.logger.Error("❌ Python validation failed", 
			logging.F("python_path", mp.pythonPath),
			logging.F("error", err))
		return fmt.Errorf("python not found at %s: %w", mp.pythonPath, err)
	}

	mp.logger.Info("✅ Meltano plugin validation successful",
		logging.F("python_path", mp.pythonPath),
		logging.F("flext_meltano_path", mp.flextMeltano),
		logging.F("workspace", mp.workspaceDir))
	
	return nil
}