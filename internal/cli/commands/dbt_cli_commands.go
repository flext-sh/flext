package commands

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/dbt"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/spf13/cobra"
)

// DBTCommands provides CLI commands for dbt operations
type DBTCommands struct {
	dbtManager *dbt.DBTManager
	logger     logging.Logger
}

// NewDBTCommands creates a new DBT commands instance
func NewDBTCommands(dbtManager *dbt.DBTManager, logger logging.Logger) *DBTCommands {
	return &DBTCommands{
		dbtManager: dbtManager,
		logger:     logger,
	}
}

// GetCommands returns all dbt CLI commands
func (dc *DBTCommands) GetCommands() []*cobra.Command {
	return []*cobra.Command{
		dc.createDBTInitCommand(),
		dc.createDBTRunCommand(),
		dc.createDBTTestCommand(),
		dc.createDBTCompileCommand(),
		dc.createDBTDocsCommand(),
		dc.createDBTSeedCommand(),
		dc.createDBTSnapshotCommand(),
		dc.createDBTListCommand(),
		dc.createDBTProfileCommand(),
		dc.createDBTConnectionCommand(),
		dc.createDBTInfoCommand(),
	}
}

// createDBTInitCommand creates the dbt init command
func (dc *DBTCommands) createDBTInitCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "dbt-init [project-name]",
		Short: "Initialize a new dbt project",
		Long:  "Initialize a new dbt project with the specified name",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			projectName := args[0]

			fmt.Printf("Initializing dbt project: %s\n", projectName)
			result, err := dc.dbtManager.InitProject(context.Background(), projectName)
			if err != nil {
				return fmt.Errorf("failed to initialize dbt project: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	return cmd
}

// createDBTRunCommand creates the dbt run command
func (dc *DBTCommands) createDBTRunCommand() *cobra.Command {
	var models []string
	var target string
	var outputFormat string

	cmd := &cobra.Command{
		Use:   "dbt-run",
		Short: "Run dbt models",
		Long:  "Execute dbt run command to build models in the data warehouse",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Running dbt models...\n")
			if len(models) > 0 {
				fmt.Printf("Models: %s\n", strings.Join(models, ", "))
			}
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.Run(context.Background(), models, target)
			if err != nil {
				return fmt.Errorf("dbt run failed: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&models, "models", "m", []string{}, "Specific models to run")
	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")
	cmd.Flags().StringVarP(&outputFormat, "output", "o", "table", "Output format (table, json)")

	return cmd
}

// createDBTTestCommand creates the dbt test command
func (dc *DBTCommands) createDBTTestCommand() *cobra.Command {
	var models []string
	var target string
	var outputFormat string

	cmd := &cobra.Command{
		Use:   "dbt-test",
		Short: "Run dbt tests",
		Long:  "Execute dbt test command to run data quality tests",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Running dbt tests...\n")
			if len(models) > 0 {
				fmt.Printf("Models: %s\n", strings.Join(models, ", "))
			}
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.Test(context.Background(), models, target)
			if err != nil {
				return fmt.Errorf("dbt test failed: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&models, "models", "m", []string{}, "Specific models to test")
	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")
	cmd.Flags().StringVarP(&outputFormat, "output", "o", "table", "Output format (table, json)")

	return cmd
}

// createDBTCompileCommand creates the dbt compile command
func (dc *DBTCommands) createDBTCompileCommand() *cobra.Command {
	var models []string
	var target string

	cmd := &cobra.Command{
		Use:   "dbt-compile",
		Short: "Compile dbt models",
		Long:  "Compile dbt models without running them",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Compiling dbt models...\n")
			if len(models) > 0 {
				fmt.Printf("Models: %s\n", strings.Join(models, ", "))
			}
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.Compile(context.Background(), models, target)
			if err != nil {
				return fmt.Errorf("dbt compile failed: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&models, "models", "m", []string{}, "Specific models to compile")
	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")

	return cmd
}

// createDBTDocsCommand creates the dbt docs command
func (dc *DBTCommands) createDBTDocsCommand() *cobra.Command {
	var serve bool
	var port int

	cmd := &cobra.Command{
		Use:   "dbt-docs",
		Short: "Generate dbt documentation",
		Long:  "Generate and optionally serve dbt documentation",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Generating dbt documentation...\n")
			if serve {
				fmt.Printf("Serving docs on port %d\n", port)
			}

			result, err := dc.dbtManager.Docs(context.Background(), serve, port)
			if err != nil {
				return fmt.Errorf("dbt docs failed: %w", err)
			}

			dc.printResult(result)

			if serve {
				fmt.Printf("\nDocumentation is being served at: http://localhost:%d\n", port)
				fmt.Printf("Press Ctrl+C to stop the server\n")
				// Keep the process alive if serving
				select {}
			}

			return nil
		},
	}

	cmd.Flags().BoolVarP(&serve, "serve", "s", false, "Serve documentation after generation")
	cmd.Flags().IntVarP(&port, "port", "p", 8080, "Port to serve documentation on")

	return cmd
}

// createDBTSeedCommand creates the dbt seed command
func (dc *DBTCommands) createDBTSeedCommand() *cobra.Command {
	var seeds []string
	var target string

	cmd := &cobra.Command{
		Use:   "dbt-seed",
		Short: "Load seed data",
		Long:  "Load CSV files into the data warehouse as tables",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Loading dbt seed data...\n")
			if len(seeds) > 0 {
				fmt.Printf("Seeds: %s\n", strings.Join(seeds, ", "))
			}
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.Seed(context.Background(), seeds, target)
			if err != nil {
				return fmt.Errorf("dbt seed failed: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&seeds, "seeds", "s", []string{}, "Specific seeds to load")
	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")

	return cmd
}

// createDBTSnapshotCommand creates the dbt snapshot command
func (dc *DBTCommands) createDBTSnapshotCommand() *cobra.Command {
	var snapshots []string
	var target string

	cmd := &cobra.Command{
		Use:   "dbt-snapshot",
		Short: "Run dbt snapshots",
		Long:  "Execute dbt snapshots to capture data changes over time",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Running dbt snapshots...\n")
			if len(snapshots) > 0 {
				fmt.Printf("Snapshots: %s\n", strings.Join(snapshots, ", "))
			}
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.Snapshot(context.Background(), snapshots, target)
			if err != nil {
				return fmt.Errorf("dbt snapshot failed: %w", err)
			}

			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringSliceVarP(&snapshots, "snapshots", "s", []string{}, "Specific snapshots to run")
	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")

	return cmd
}

// createDBTListCommand creates the dbt list command
func (dc *DBTCommands) createDBTListCommand() *cobra.Command {
	var resourceType string

	cmd := &cobra.Command{
		Use:   "dbt-list",
		Short: "List dbt resources",
		Long:  "List available dbt models, tests, or other resources",
		RunE: func(cmd *cobra.Command, args []string) error {
			switch resourceType {
			case "models":
				models, err := dc.dbtManager.ListModels(context.Background())
				if err != nil {
					return fmt.Errorf("failed to list models: %w", err)
				}
				fmt.Printf("Available models (%d):\n", len(models))
				for _, model := range models {
					fmt.Printf("  - %s\n", model)
				}

			case "tests":
				tests, err := dc.dbtManager.ListTests(context.Background())
				if err != nil {
					return fmt.Errorf("failed to list tests: %w", err)
				}
				fmt.Printf("Available tests (%d):\n", len(tests))
				for _, test := range tests {
					fmt.Printf("  - %s\n", test)
				}

			default:
				// List both models and tests
				models, err := dc.dbtManager.ListModels(context.Background())
				if err != nil {
					return fmt.Errorf("failed to list models: %w", err)
				}

				tests, err := dc.dbtManager.ListTests(context.Background())
				if err != nil {
					return fmt.Errorf("failed to list tests: %w", err)
				}

				fmt.Printf("Available models (%d):\n", len(models))
				for _, model := range models {
					fmt.Printf("  - %s\n", model)
				}

				fmt.Printf("\nAvailable tests (%d):\n", len(tests))
				for _, test := range tests {
					fmt.Printf("  - %s\n", test)
				}
			}

			return nil
		},
	}

	cmd.Flags().StringVarP(&resourceType, "resource-type", "r", "", "Resource type to list (models, tests)")

	return cmd
}

// createDBTProfileCommand creates the dbt profile command
func (dc *DBTCommands) createDBTProfileCommand() *cobra.Command {
	var profileName string

	cmd := &cobra.Command{
		Use:   "dbt-profile [profile-name]",
		Short: "Create dbt profile",
		Long:  "Create a new dbt profile configuration",
		Args:  cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			if len(args) > 0 {
				profileName = args[0]
			}
			if profileName == "" {
				profileName = "flext"
			}

			fmt.Printf("Creating dbt profile: %s\n", profileName)

			config := map[string]interface{}{
				"type": "postgres",
				"host": "localhost",
				"port": 5432,
				"user": "postgres",
				"password": "password",
				"dbname": "postgres",
				"schema": "public",
			}

			err := dc.dbtManager.CreateProfile(profileName, config)
			if err != nil {
				return fmt.Errorf("failed to create profile: %w", err)
			}

			fmt.Printf("Profile '%s' created successfully\n", profileName)
			return nil
		},
	}

	cmd.Flags().StringVarP(&profileName, "name", "n", "", "Profile name")

	return cmd
}

// createDBTConnectionCommand creates the dbt connection test command
func (dc *DBTCommands) createDBTConnectionCommand() *cobra.Command {
	var target string

	cmd := &cobra.Command{
		Use:   "dbt-connection",
		Short: "Test dbt database connection",
		Long:  "Test the connection to the dbt target database",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Testing dbt database connection...\n")
			if target != "" {
				fmt.Printf("Target: %s\n", target)
			}

			result, err := dc.dbtManager.CheckConnection(context.Background(), target)
			if err != nil {
				fmt.Printf("Connection test failed: %v\n", err)
				if result != nil {
					dc.printResult(result)
				}
				return err
			}

			fmt.Printf("Connection test successful!\n")
			dc.printResult(result)
			return nil
		},
	}

	cmd.Flags().StringVarP(&target, "target", "t", "", "Target environment")

	return cmd
}

// createDBTInfoCommand creates the dbt info command
func (dc *DBTCommands) createDBTInfoCommand() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "dbt-info",
		Short: "Show dbt project information",
		Long:  "Display information about the current dbt project",
		RunE: func(cmd *cobra.Command, args []string) error {
			info, err := dc.dbtManager.GetProjectInfo(context.Background())
			if err != nil {
				return fmt.Errorf("failed to get project info: %w", err)
			}

			fmt.Printf("DBT Project Information:\n")
			fmt.Printf("  Name: %s\n", info.Name)
			fmt.Printf("  Version: %s\n", info.Version)
			fmt.Printf("  Profile: %s\n", info.ProfileName)
			fmt.Printf("  Model Paths: %s\n", strings.Join(info.ModelPaths, ", "))
			fmt.Printf("  Test Paths: %s\n", strings.Join(info.TestPaths, ", "))
			fmt.Printf("  Macro Paths: %s\n", strings.Join(info.MacroPaths, ", "))

			if len(info.Vars) > 0 {
				fmt.Printf("  Variables:\n")
				for key, value := range info.Vars {
					fmt.Printf("    %s: %s\n", key, value)
				}
			}

			return nil
		},
	}

	return cmd
}

// printResult prints a dbt run result in a formatted way
func (dc *DBTCommands) printResult(result *dbt.DBTRunResult) {
	fmt.Printf("\n=== DBT Command Result ===\n")
	fmt.Printf("Command: %s %s\n", result.Command, strings.Join(result.Args, " "))
	fmt.Printf("Success: %t\n", result.Success)
	fmt.Printf("Exit Code: %d\n", result.ExitCode)
	fmt.Printf("Duration: %s\n", result.Duration.String())
	fmt.Printf("Started: %s\n", result.StartedAt.Format(time.RFC3339))
	fmt.Printf("Completed: %s\n", result.CompletedAt.Format(time.RFC3339))

	if len(result.Models) > 0 {
		fmt.Printf("\nModels (%d):\n", len(result.Models))
		for _, model := range result.Models {
			status := "✓"
			if model.Status != "success" {
				status = "✗"
			}
			fmt.Printf("  %s %s (%s) - %.2fs\n", status, model.Name, model.Status, model.ExecutionTime)
			if model.ErrorMessage != "" {
				fmt.Printf("    Error: %s\n", model.ErrorMessage)
			}
		}
	}

	if len(result.Tests) > 0 {
		fmt.Printf("\nTests (%d):\n", len(result.Tests))
		for _, test := range result.Tests {
			status := "✓"
			if test.Status != "pass" {
				status = "✗"
			}
			fmt.Printf("  %s %s (%s)\n", status, test.Name, test.Status)
			if test.ErrorMessage != "" {
				fmt.Printf("    Error: %s\n", test.ErrorMessage)
			}
		}
	}

	if result.Output != "" && len(result.Output) < 2000 {
		fmt.Printf("\nOutput:\n%s\n", result.Output)
	}

	if result.ErrorOutput != "" {
		fmt.Printf("\nErrors:\n%s\n", result.ErrorOutput)
	}

	fmt.Printf("========================\n")
}

// printResultJSON prints a dbt run result as JSON
func (dc *DBTCommands) printResultJSON(result *dbt.DBTRunResult) {
	jsonData, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		fmt.Printf("Error marshaling result to JSON: %v\n", err)
		return
	}
	fmt.Printf("%s\n", jsonData)
}