package flextservice

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/controlpanel/coordination"
	"github.com/flext-sh/flext/pkg/controlpanel/management/container"
	"github.com/flext-sh/flext/pkg/controlpanel/monitoring/server"
	"github.com/flext-sh/flext/pkg/logging"
)

// ServiceConfig holds configuration for FLEXT service
type ServiceConfig struct {
	Host        string
	Port        int
	Environment string
	ServiceName string
}

// FlextService represents the main FLEXT service
type FlextService struct {
	config      *ServiceConfig
	logger      logging.Logger
	coordinator *coordination.FlexCoreCoordinator 
	container   *container.Container
	server      *server.Server
}

// NewFlextService creates a new FLEXT service instance
func NewFlextService(cfg *ServiceConfig) (*FlextService, error) {
	// Initialize logging
	if err := logging.Initialize(cfg.ServiceName, "info"); err != nil {
		return nil, fmt.Errorf("failed to initialize logging: %w", err)
	}
	logger := logging.GetLogger()

	// Initialize configuration
	serviceCfg := &config.Config{}
	serviceCfg.Server.Host = cfg.Host
	serviceCfg.Server.Port = cfg.Port
	serviceCfg.Server.Environment = cfg.Environment
	serviceCfg.Server.Debug = (cfg.Environment != "production")
	serviceCfg.FlexCore.URL = "http://localhost:8080"

	// Initialize FlexCore coordinator
	coordinator := coordination.NewFlexCoreCoordinator()
	logger.Info("FlexCore coordinator initialized")

	// Initialize DI container
	containerInstance, err := container.NewContainer(serviceCfg)
	if err != nil {
		return nil, fmt.Errorf("failed to create container: %w", err)
	}
	logger.Info("Service container initialized")

	// Initialize monitoring server
	srv := server.NewServer(serviceCfg, logger)

	return &FlextService{
		config:      cfg,
		logger:      logger,
		coordinator: coordinator,
		container:   containerInstance,
		server:      srv,
	}, nil
}

// Start starts the FLEXT service
func (s *FlextService) Start() error {
	s.logger.Info(fmt.Sprintf("Starting %s on %s:%d (%s) - FlexCore URL: http://localhost:8080",
		s.config.ServiceName, s.config.Host, s.config.Port, s.config.Environment))

	// Start server in goroutine
	go func() {
		if err := s.server.Start(); err != nil {
			s.logger.Fatal("Server failed to start", logging.F("error", err))
		}
	}()

	// Setup graceful shutdown
	return s.waitForShutdown()
}

// waitForShutdown waits for shutdown signals and handles graceful shutdown
func (s *FlextService) waitForShutdown() error {
	// Setup signal channel
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Wait for signal
	sig := <-sigChan
	s.logger.Info("Received shutdown signal", logging.F("signal", sig.String()))

	// Create shutdown context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Shutdown server
	if err := s.server.Stop(ctx); err != nil {
		s.logger.Error("Server shutdown error", logging.F("error", err))
		return err
	}

	s.logger.Info("Service shutdown completed")
	return nil
}

// Stop stops the FLEXT service
func (s *FlextService) Stop() error {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Shutdown server
	if err := s.server.Stop(ctx); err != nil {
		return fmt.Errorf("server shutdown failed: %w", err)
	}

	return nil
}
