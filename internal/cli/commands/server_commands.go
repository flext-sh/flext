package commands

import (
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"syscall"
	"time"
)

// ServerStartCommand comando para iniciar o servidor FLEXT
type ServerStartCommand struct {
	flags      *flag.FlagSet
	port       *int
	host       *string
	env        *string
	debug      *bool
	background *bool
}

// NewServerStartCommand cria um novo comando de start do servidor
func NewServerStartCommand() *ServerStartCommand {
	cmd := &ServerStartCommand{
		flags: flag.NewFlagSet("server-start", flag.ExitOnError),
	}

	cmd.port = cmd.flags.Int("port", 8080, "Server port")
	cmd.host = cmd.flags.String("host", "localhost", "Server host")
	cmd.env = cmd.flags.String("env", "development", "Environment (development, production)")
	cmd.debug = cmd.flags.Bool("debug", false, "Enable debug mode")
	cmd.background = cmd.flags.Bool("background", false, "Run server in background")

	return cmd
}

func (c *ServerStartCommand) Name() string        { return "server-start" }
func (c *ServerStartCommand) Description() string { return "Start the FLEXT server" }
func (c *ServerStartCommand) Usage() string {
	return "server-start [--port <port>] [--host <host>] [--env <env>] [--debug] [--background]"
}
func (c *ServerStartCommand) Flags() *flag.FlagSet { return c.flags }

func (c *ServerStartCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	// Set environment variables
	os.Setenv("FLEXT_SERVER_PORT", strconv.Itoa(*c.port))
	os.Setenv("FLEXT_SERVER_HOST", *c.host)
	os.Setenv("FLEXT_SERVER_ENVIRONMENT", *c.env)
	if *c.debug {
		os.Setenv("FLEXT_SERVER_DEBUG", "true")
	}

	// Check if server is already running
	if c.isServerRunning() {
		return fmt.Errorf("server is already running on %s:%d", *c.host, *c.port)
	}

	// Find server executable
	serverPath, err := c.findServerExecutable()
	if err != nil {
		return fmt.Errorf("failed to find server executable: %w", err)
	}

	fmt.Printf("Starting FLEXT server on %s:%d...\n", *c.host, *c.port)
	fmt.Printf("Environment: %s\n", *c.env)
	if *c.debug {
		fmt.Printf("Debug mode: enabled\n")
	}

	if *c.background {
		// Start server in background
		cmd := exec.Command(serverPath)
		cmd.Env = os.Environ()
		
		if err := cmd.Start(); err != nil {
			return fmt.Errorf("failed to start server: %w", err)
		}

		// Write PID file
		pidFile := "/tmp/flext-server.pid"
		if err := os.WriteFile(pidFile, []byte(strconv.Itoa(cmd.Process.Pid)), 0644); err != nil {
			fmt.Printf("Warning: failed to write PID file: %v\n", err)
		}

		fmt.Printf("Server started in background (PID: %d)\n", cmd.Process.Pid)
		fmt.Printf("PID file: %s\n", pidFile)
		
		// Wait a moment to check if server starts successfully
		time.Sleep(2 * time.Second)
		if !c.isServerRunning() {
			return fmt.Errorf("server failed to start")
		}
		
		fmt.Printf("Server is now running at http://%s:%d\n", *c.host, *c.port)
	} else {
		// Start server in foreground
		cmd := exec.Command(serverPath)
		cmd.Env = os.Environ()
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		fmt.Printf("Starting server...\n")
		if err := cmd.Run(); err != nil {
			return fmt.Errorf("server exited with error: %w", err)
		}
	}

	return nil
}

func (c *ServerStartCommand) isServerRunning() bool {
	url := fmt.Sprintf("http://%s:%d/health", *c.host, *c.port)
	client := &http.Client{Timeout: 2 * time.Second}
	
	resp, err := client.Get(url)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	
	return resp.StatusCode == http.StatusOK
}

func (c *ServerStartCommand) findServerExecutable() (string, error) {
	// Try common paths
	paths := []string{
		"./cmd/flext/flext",
		"./flext",
		"/usr/local/bin/flext",
		"/usr/bin/flext",
	}

	for _, path := range paths {
		if _, err := os.Stat(path); err == nil {
			return path, nil
		}
	}

	// Try building from source if go.mod exists
	if _, err := os.Stat("go.mod"); err == nil {
		fmt.Println("Building server from source...")
		buildCmd := exec.Command("go", "build", "-o", "./flext", "./cmd/flext")
		if err := buildCmd.Run(); err != nil {
			return "", fmt.Errorf("failed to build server: %w", err)
		}
		return "./flext", nil
	}

	return "", fmt.Errorf("server executable not found")
}

// ServerStatusCommand comando para verificar status do servidor
type ServerStatusCommand struct {
	flags     *flag.FlagSet
	port      *int
	host      *string
	serverURL *string
}

// NewServerStatusCommand cria um novo comando de status do servidor
func NewServerStatusCommand() *ServerStatusCommand {
	cmd := &ServerStatusCommand{
		flags: flag.NewFlagSet("server-status", flag.ExitOnError),
	}

	cmd.port = cmd.flags.Int("port", 8080, "Server port")
	cmd.host = cmd.flags.String("host", "localhost", "Server host")
	cmd.serverURL = cmd.flags.String("server", "", "Full server URL (overrides host:port)")

	return cmd
}

func (c *ServerStatusCommand) Name() string        { return "server-status" }
func (c *ServerStatusCommand) Description() string { return "Check FLEXT server status" }
func (c *ServerStatusCommand) Usage() string {
	return "server-status [--host <host>] [--port <port>] [--server <url>]"
}
func (c *ServerStatusCommand) Flags() *flag.FlagSet { return c.flags }

func (c *ServerStatusCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	baseURL := *c.serverURL
	if baseURL == "" {
		baseURL = fmt.Sprintf("http://%s:%d", *c.host, *c.port)
	}

	fmt.Printf("Checking server status at %s...\n", baseURL)

	// Check health endpoint
	healthURL := baseURL + "/health"
	client := &http.Client{Timeout: 5 * time.Second}
	
	resp, err := client.Get(healthURL)
	if err != nil {
		fmt.Printf("❌ Server is not reachable: %v\n", err)
		return nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ Server is not healthy (HTTP %d)\n", resp.StatusCode)
		return nil
	}

	fmt.Printf("✅ Server is running and healthy\n")

	// Try to get server info
	infoURL := baseURL + "/api/v1/info"
	resp, err = client.Get(infoURL)
	if err == nil && resp.StatusCode == http.StatusOK {
		defer resp.Body.Close()
		
		fmt.Printf("\nServer Information:\n")
		fmt.Printf("  URL: %s\n", baseURL)
		fmt.Printf("  Health: OK\n")
		
		// Check PID file if exists
		pidFile := "/tmp/flext-server.pid"
		if pidData, err := os.ReadFile(pidFile); err == nil {
			fmt.Printf("  PID: %s\n", string(pidData))
		}
	}

	// Check main endpoints
	endpoints := []string{
		"/api/v1/pipelines",
		"/api/v1/singer/specs",
		"/api/v1/dbt/projects",
	}

	fmt.Printf("\nEndpoint Status:\n")
	for _, endpoint := range endpoints {
		url := baseURL + endpoint
		resp, err := client.Get(url)
		if err != nil {
			fmt.Printf("  %s: ❌ Error\n", endpoint)
			continue
		}
		resp.Body.Close()
		
		if resp.StatusCode == http.StatusOK {
			fmt.Printf("  %s: ✅ OK\n", endpoint)
		} else {
			fmt.Printf("  %s: ⚠️  HTTP %d\n", endpoint, resp.StatusCode)
		}
	}

	return nil
}

// ServerStopCommand comando para parar o servidor
type ServerStopCommand struct {
	flags *flag.FlagSet
	port  *int
	host  *string
	force *bool
}

// NewServerStopCommand cria um novo comando de stop do servidor
func NewServerStopCommand() *ServerStopCommand {
	cmd := &ServerStopCommand{
		flags: flag.NewFlagSet("server-stop", flag.ExitOnError),
	}

	cmd.port = cmd.flags.Int("port", 8080, "Server port")
	cmd.host = cmd.flags.String("host", "localhost", "Server host")
	cmd.force = cmd.flags.Bool("force", false, "Force stop using SIGKILL")

	return cmd
}

func (c *ServerStopCommand) Name() string        { return "server-stop" }
func (c *ServerStopCommand) Description() string { return "Stop the FLEXT server" }
func (c *ServerStopCommand) Usage() string {
	return "server-stop [--host <host>] [--port <port>] [--force]"
}
func (c *ServerStopCommand) Flags() *flag.FlagSet { return c.flags }

func (c *ServerStopCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	// Check if server is running
	if !c.isServerRunning() {
		fmt.Printf("Server is not running on %s:%d\n", *c.host, *c.port)
		return nil
	}

	fmt.Printf("Stopping FLEXT server on %s:%d...\n", *c.host, *c.port)

	// Try to stop gracefully first via shutdown endpoint
	if !*c.force {
		shutdownURL := fmt.Sprintf("http://%s:%d/REDACTED_LDAP_BIND_PASSWORD/shutdown", *c.host, *c.port)
		client := &http.Client{Timeout: 5 * time.Second}
		
		resp, err := client.Post(shutdownURL, "application/json", nil)
		if err == nil {
			resp.Body.Close()
			if resp.StatusCode == http.StatusOK {
				fmt.Printf("Server shutdown initiated gracefully\n")
				
				// Wait for server to stop
				for i := 0; i < 10; i++ {
					if !c.isServerRunning() {
						fmt.Printf("✅ Server stopped successfully\n")
						return nil
					}
					time.Sleep(1 * time.Second)
				}
			}
		}
	}

	// Try to stop using PID file
	pidFile := "/tmp/flext-server.pid"
	if pidData, err := os.ReadFile(pidFile); err == nil {
		pidStr := string(pidData)
		if pid, err := strconv.Atoi(pidStr); err == nil {
			fmt.Printf("Found server PID: %d\n", pid)
			
			process, err := os.FindProcess(pid)
			if err != nil {
				return fmt.Errorf("failed to find process %d: %w", pid, err)
			}

			signal := syscall.SIGTERM
			if *c.force {
				signal = syscall.SIGKILL
				fmt.Printf("Force stopping server with SIGKILL...\n")
			} else {
				fmt.Printf("Stopping server with SIGTERM...\n")
			}

			if err := process.Signal(signal); err != nil {
				return fmt.Errorf("failed to send signal to process %d: %w", pid, err)
			}

			// Wait for process to stop
			for i := 0; i < 10; i++ {
				if !c.isServerRunning() {
					fmt.Printf("✅ Server stopped successfully\n")
					// Clean up PID file
					os.Remove(pidFile)
					return nil
				}
				time.Sleep(1 * time.Second)
			}

			if *c.force {
				return fmt.Errorf("failed to stop server even with SIGKILL")
			} else {
				fmt.Printf("Server didn't stop gracefully, use --force for SIGKILL\n")
				return fmt.Errorf("server didn't stop within timeout")
			}
		}
	}

	fmt.Printf("❌ Could not stop server: PID file not found\n")
	fmt.Printf("You may need to stop the server manually or use --force\n")
	
	return fmt.Errorf("failed to stop server")
}

func (c *ServerStopCommand) isServerRunning() bool {
	url := fmt.Sprintf("http://%s:%d/health", *c.host, *c.port)
	client := &http.Client{Timeout: 2 * time.Second}
	
	resp, err := client.Get(url)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	
	return resp.StatusCode == http.StatusOK
}