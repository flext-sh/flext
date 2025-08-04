package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/flext-sh/flext/pkg/interfaces/cli"
	// "github.com/flext-sh/flext/pkg/logging"  // TODO: Fix after shared_kernel issues
	// "github.com/flext-sh/flext/pkg/utils/shared_kernel" // TODO: Fix shared_kernel package conflicts
)

// basicLogger provides simple logging for CLI
type basicLogger struct{}

func (l *basicLogger) Info(msg string, fields ...interface{}) {
	fmt.Printf("[INFO] %s\n", msg)
}

func (l *basicLogger) Error(msg string, fields ...interface{}) {
	fmt.Printf("[ERROR] %s\n", msg)
}

func main() {
	// Parse command line flags
	flag.Parse()

	// TODO: Restore CLI bootstrap when shared_kernel is fixed
	// Simple initialization for now
	var appConfig struct {
		Logger interface {
			Info(msg string, fields ...interface{})
			Error(msg string, fields ...interface{})
		}
	}
	
	// Use basic logging
	appConfig.Logger = &basicLogger{}

	// Log CLI initialization
	appConfig.Logger.Info(fmt.Sprintf("Starting FLEXT CLI v2.0.0 with args: %v", os.Args[1:]))

	// Create CLI with enhanced error handling
	cliApp := cli.NewCLI()

	// Create context for graceful shutdown
	ctx := context.Background()

	// Run CLI
	if err := cliApp.Run(ctx, os.Args); err != nil {
		appConfig.Logger.Error(fmt.Sprintf("CLI execution failed: %v", err))
		fmt.Printf("CLI execution failed: %v\n", err)
		os.Exit(1)
	}

	appConfig.Logger.Info("CLI execution completed successfully")
}
