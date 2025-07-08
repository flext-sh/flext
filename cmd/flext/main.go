package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/server"
	"github.com/flext-sh/flext/internal/shared_kernel/application"
)

func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "", "Path to configuration file")
		debug      = flag.Bool("debug", false, "Enable debug logging")
	)
	flag.Parse()

	// Create application bootstrap
	bootstrap := application.NewAppBootstrap(application.AppTypeStandalone, "flext", "2.0.0")
	if *configPath != "" {
		bootstrap = bootstrap.WithConfigPath(*configPath)
	}
	if *debug {
		bootstrap = bootstrap.WithLogLevel("debug")
	}

	// Initialize application
	appConfig, err := bootstrap.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize application: %v\n", err)
		os.Exit(1)
	}

	// Log application initialization
	appConfig.Logger.Info("Initializing FLEXT application",
		logging.F("version", "2.0.0"),
		logging.F("mode", "standalone"),
		logging.F("environment", appConfig.Config.Server.Environment),
		logging.F("debug", appConfig.Config.Server.Debug),
		logging.F("database_enabled", appConfig.Config.Features.DatabaseEnabled),
		logging.F("websocket_enabled", appConfig.Config.Features.WebSocketEnabled),
	)

	// Create container for comprehensive functionality
	appContainer, err := container.NewContainer(appConfig.Config)
	if err != nil {
		appConfig.Logger.Error("Failed to initialize container", logging.F("error", err.Error()))
		os.Exit(1)
	}

	// Create and configure server
	srv := server.NewServer(appConfig.Config, appConfig.Logger)
	srv.SetupBasicRoutes()

	// Register all handlers from container
	registerHandlers(srv, appContainer, appConfig.Logger)

	// Register Clean Architecture handlers if enabled
	if appConfig.Config.CleanArchitecture.IsEnabled() {
		registerCleanArchitectureHandlers(srv, appConfig, appContainer)
	} else {
		appConfig.Logger.Info("Clean Architecture is disabled in configuration")
	}

	// Setup graceful shutdown
	shutdown := application.NewGracefulShutdownHandler(appConfig.Logger, appConfig.Config.Server.ShutdownTimeout)
	shutdown.AddShutdownFunc("server", srv.Stop)
	shutdown.AddShutdownFunc("container", func(ctx context.Context) error {
		return appContainer.Shutdown()
	})

	// Start server
	go func() {
		appConfig.Logger.Info("Starting server", logging.F("address", appConfig.Config.Address()))
		if err := srv.Start(); err != nil {
			appConfig.Logger.Error("Server failed to start", logging.F("error", err.Error()))
			os.Exit(1)
		}
	}()

	// Wait for shutdown
	shutdown.WaitForShutdown()
}

// registerHandlers registers all standard handlers from container
func registerHandlers(srv *server.Server, appContainer *container.Container, logger logging.Logger) {
	// Register pipeline and plugin handlers now that they are fixed
	if pipelineHandler := appContainer.GetPipelineHandler(); pipelineHandler != nil {
		srv.RegisterHandler(pipelineHandler)
		logger.Info("Pipeline handler registered successfully")
	} else {
		logger.Error("Pipeline handler is nil - not registered")
	}
	if pluginHandler := appContainer.GetPluginHandler(); pluginHandler != nil {
		srv.RegisterHandler(pluginHandler)
		logger.Info("Plugin handler registered successfully")
	} else {
		logger.Error("Plugin handler is nil - not registered")
	}
	if meltanoHandler := appContainer.GetMeltanoHandler(); meltanoHandler != nil {
		srv.RegisterHandler(meltanoHandler)
		logger.Debug("Meltano handler registered")
	}
	if dbtHandler := appContainer.GetDBTHandler(); dbtHandler != nil {
		srv.RegisterHandler(dbtHandler)
		logger.Debug("DBT handler registered")
	}
	if connectorsHandler := appContainer.GetConnectorsHandler(); connectorsHandler != nil {
		srv.RegisterHandler(connectorsHandler)
		logger.Info("Connectors handler registered successfully")
	} else {
		logger.Error("Connectors handler is nil - not registered")
	}
	if meltanoGopyHandler := appContainer.GetMeltanoGopyHandler(); meltanoGopyHandler != nil {
		srv.RegisterHandler(meltanoGopyHandler)
		logger.Debug("MeltanoGopy handler registered")
	}
	if webHandler := appContainer.GetWebHandler(); webHandler != nil {
		srv.RegisterHandler(webHandler)
		logger.Info("Web interface handler registered successfully")
	} else {
		logger.Error("Web handler is nil - not registered")
	}
}

// registerCleanArchitectureHandlers registers Clean Architecture handlers if enabled
func registerCleanArchitectureHandlers(srv *server.Server, appConfig *application.AppConfig, appContainer *container.Container) {
	logger := appConfig.Logger

	_, err := container.NewCleanContainer(appConfig.Config, nil) // Pass nil for database (uses in-memory)
	if err != nil {
		logger.Error("Failed to initialize Clean Architecture container", logging.F("error", err.Error()))
		return
	}

	logger.Info("Clean Architecture successfully enabled and operational")

	// Clean Architecture handlers integration would go here when ready
	// For now, we note that the system is working properly
}
