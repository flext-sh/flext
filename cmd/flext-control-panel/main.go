package main

import (
	"context"
	"flag"
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

func main() {
	// Parse command line flags
	port := flag.Int("port", 8081, "FLEXT Control Panel port")
	host := flag.String("host", "0.0.0.0", "Server host")
	env := flag.String("env", "development", "Environment (development/production)")
	flag.Parse()

	// Initialize configuration for FLEXT Control Panel
	cfg := &config.Config{}
	cfg.Server.Host = *host
	cfg.Server.Port = *port
	cfg.Server.Environment = *env
	cfg.Server.Debug = (*env != "production")
	cfg.FlexCore.URL = "http://localhost:8080" // FlexCore runtime URL

	// Initialize logging for FLEXT Control Panel
	if err := logging.Initialize("flext-control-panel", "info"); err != nil {
		fmt.Printf("Failed to initialize logging: %v\n", err)
		os.Exit(1)
	}
	logger := logging.GetLogger()

	// Initialize FlexCore coordinator
	coordinator := coordination.NewFlexCoreCoordinator()
	logger.Info("FlexCore coordinator initialized")

	// Initialize DI container
	containerInstance, err := container.NewContainer(cfg)
	if err != nil {
		logger.Fatal("Failed to create container", logging.F("error", err))
	}

	// Create and configure FLEXT Control Panel server
	srv := server.NewServer(cfg, logger)
	srv.SetupBasicRoutes()

	// Register handlers with container
	srv.RegisterHandler(containerInstance.GetPluginHandler())
	srv.RegisterCleanHandler("meltano", containerInstance.GetUnifiedMeltanoHandler())
	srv.RegisterCleanHandler("flexcore", containerInstance.GetFlexcoreHandler())
	srv.RegisterCleanHandler("pipeline", containerInstance.GetPipelineHandler())

		logger.Info(fmt.Sprintf("Starting FLEXT Control Panel on %s:%d (%s) - FlexCore URL: %s", 
		*host, *port, *env, cfg.FlexCore.URL))

	// Start server in a goroutine
	go func() {
		if err := srv.Start(); err != nil {
			logger.Error("Server failed to start: " + err.Error())
			os.Exit(1)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down FLEXT Control Panel...")

	// Create context with timeout for graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Perform health check on FlexCore instances before shutdown
	if err := coordinator.HealthCheck(ctx); err != nil {
		logger.Warn("FlexCore health check failed during shutdown: " + err.Error())
	}

	if err := srv.Stop(ctx); err != nil {
		logger.Error("Control Panel shutdown failed: " + err.Error())
		os.Exit(1)
	}

	logger.Info("FLEXT Control Panel shutdown complete")
}
