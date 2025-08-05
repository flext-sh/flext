package flextservice

import (
	"flag"
	"fmt"
	"os"
)

// ServiceInfo contains service-specific information
type ServiceInfo struct {
	Name        string
	DefaultPort int
	Description string
}

// LaunchService provides a common entry point for FLEXT services
// This eliminates code duplication between different service main.go files
func LaunchService(info ServiceInfo) {
	// Parse command line flags with service-specific defaults
	port := flag.Int("port", info.DefaultPort, fmt.Sprintf("%s port", info.Description))
	host := flag.String("host", "0.0.0.0", "Server host")
	env := flag.String("env", "development", "Environment (development/production)")
	flag.Parse()

	// Create service configuration
	cfg := &ServiceConfig{
		Host:        *host,
		Port:        *port,
		Environment: *env,
		ServiceName: info.Name,
	}

	// Create and start service
	service, err := NewFlextService(cfg)
	if err != nil {
		fmt.Printf("Failed to create %s service: %v\n", info.Description, err)
		os.Exit(1)
	}

	// Start service (blocks until shutdown)
	if err := service.Start(); err != nil {
		fmt.Printf("Service error: %v\n", err)
		os.Exit(1)
	}
}