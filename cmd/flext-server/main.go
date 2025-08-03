package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/flext-sh/flexcore/pkg/container"
	"github.com/flext-sh/flexcore/pkg/logging"
	"github.com/flext-sh/flexcore/pkg/server"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
)

func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "", "Path to configuration file")
		port       = flag.Int("port", 0, "Server port (overrides config)")
	)
	flag.Parse()

	// Create server bootstrap
	bootstrap := application.NewAppBootstrap(application.AppTypeServer, "flext-server", "2.0.0")
	if *configPath != "" {
		bootstrap = bootstrap.WithConfigPath(*configPath)
	}

	// Initialize application
	appConfig, err := bootstrap.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize application: %v\n", err)
		os.Exit(1)
	}

	// Override port if specified
	if *port > 0 {
		appConfig.Config.Server.Port = *port
	}

	// Create container with all features
	appContainer, err := container.NewContainer(appConfig.Config)
	if err != nil {
		appConfig.Logger.Error("Failed to initialize container", logging.F("error", err.Error()))
		os.Exit(1)
	}

	// Create and configure server
	srv := server.NewServer(appConfig.Config, appConfig.Logger)
	srv.SetupBasicRoutes() // Setup basic routes

	// Register all handlers from container (disabled temporarily for compilation)
	// if pipelineHandler := appContainer.GetPipelineHandler(); pipelineHandler != nil {
	//	srv.RegisterHandler(pipelineHandler)
	//	appConfig.Logger.Info("Pipeline handler registered")
	// }
	// if pluginHandler := appContainer.GetPluginHandler(); pluginHandler != nil {
	//	srv.RegisterHandler(pluginHandler)
	//	appConfig.Logger.Info("Plugin handler registered")
	// }
	if meltanoHandler := appContainer.GetMeltanoHandler(); meltanoHandler != nil {
		srv.RegisterHandler(meltanoHandler)
		appConfig.Logger.Info("Meltano handler registered")
	}
	if dbtHandler := appContainer.GetDBTHandler(); dbtHandler != nil {
		srv.RegisterHandler(dbtHandler)
		appConfig.Logger.Info("DBT handler registered")
	}
	if connectorsHandler := appContainer.GetConnectorsHandler(); connectorsHandler != nil {
		srv.RegisterHandler(connectorsHandler)
		appConfig.Logger.Info("Connectors handler registered")
	}

	// Setup graceful shutdown
	shutdown := application.NewGracefulShutdownHandler(appConfig.Logger, appConfig.Config.Server.ShutdownTimeout)
	shutdown.AddShutdownFunc("server", srv.Stop)
	shutdown.AddShutdownFunc("container", func(ctx context.Context) error {
		return appContainer.Shutdown()
	})

	// Start server
	go func() {
		appConfig.Logger.Info("Starting FLEXT server",
			logging.F("address", appConfig.Config.Address()),
			logging.F("mode", "server"),
			logging.F("version", "2.0.0"))
		if err := srv.Start(); err != nil {
			appConfig.Logger.Error("Server failed to start", logging.F("error", err.Error()))
			os.Exit(1)
		}
	}()

	// Wait for shutdown
	shutdown.WaitForShutdown()
}
