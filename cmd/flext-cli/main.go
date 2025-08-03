package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/flext-sh/flext/pkg/interfaces/cli"
	"github.com/flext-sh/flexcore/pkg/logging"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
)

func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "", "Path to configuration file")
		verbose    = flag.Bool("verbose", false, "Enable verbose logging")
	)
	flag.Parse()

	// Create CLI bootstrap
	bootstrap := application.NewAppBootstrap(application.AppTypeCLI, "flext-cli", "2.0.0")
	if *configPath != "" {
		bootstrap = bootstrap.WithConfigPath(*configPath)
	}
	if *verbose {
		bootstrap = bootstrap.WithLogLevel("debug")
	}

	// Initialize application (for logging and configuration)
	appConfig, err := bootstrap.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize CLI application: %v\n", err)
		os.Exit(1)
	}

	// Log CLI initialization
	appConfig.Logger.Info("Starting FLEXT CLI",
		logging.F("version", "2.0.0"),
		logging.F("args", fmt.Sprintf("%v", os.Args[1:])))

	// Create CLI with enhanced error handling
	cliApp := cli.NewCLI()

	// Create context for graceful shutdown
	ctx := context.Background()

	// Run CLI
	if err := cliApp.Run(ctx, os.Args); err != nil {
		appConfig.Logger.Error("CLI execution failed", logging.F("error", err.Error()))
		fmt.Printf("CLI execution failed: %v\n", err)
		os.Exit(1)
	}

	appConfig.Logger.Info("CLI execution completed successfully")
}
