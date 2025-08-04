package main

import (
	"flag"
	"fmt"
	"context"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/flext-sh/flext/pkg/config"
	"github.com/flext-sh/flext/pkg/container"
	"github.com/flext-sh/flext/pkg/logging"
	"github.com/flext-sh/flext/pkg/server"
)

func main() {
	// Parse command line flags
	port := flag.Int("port", 8082, "Server port")
	host := flag.String("host", "0.0.0.0", "Server host")
	env := flag.String("env", "development", "Environment (development/production)")
	flag.Parse()

	// Initialize configuration
	cfg := &config.Config{}
	cfg.Server.Host = *host
	cfg.Server.Port = *port
	cfg.Server.Environment = *env
	cfg.Server.Debug = (*env != "production")
	cfg.FlexCore.URL = "http://localhost:8080"

	// Initialize logging
	if err := logging.Initialize("flext-server", "info"); err != nil {
		fmt.Printf("Failed to initialize logging: %v\n", err)
		os.Exit(1)
	}
	logger := logging.GetLogger()

	// Initialize DI container
	containerInstance, err := container.NewContainer(cfg)
	if err != nil {
		logger.Fatal("Failed to create container", logging.F("error", err))
	}

	// Create and configure server
	srv := server.NewServer(cfg, logger)
	srv.SetupBasicRoutes()

	// Register handlers with container
	srv.RegisterHandler(containerInstance.GetPluginHandler())
	srv.RegisterCleanHandler("meltano", containerInstance.GetUnifiedMeltanoHandler())
	srv.RegisterCleanHandler("flexcore", containerInstance.GetFlexcoreHandler())
	srv.RegisterCleanHandler("pipeline", containerInstance.GetPipelineHandler())

	logger.Info("Starting FLEXT Server", 
		logging.F("port", *port),
		logging.F("host", *host),
		logging.F("environment", *env))

	// Start server in a goroutine
	go func() {
		if err := srv.Start(); err != nil {
			logger.Error("Server failed to start", logging.F("error", err))
			os.Exit(1)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down FLEXT Server...")

	// Create context with timeout for graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Stop(ctx); err != nil {
		logger.Error("Server shutdown failed", logging.F("error", err))
		os.Exit(1)
	}

	logger.Info("FLEXT Server shutdown complete")
}
