package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	pluginEntities "github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	sharedEntities "github.com/flext-sh/flext/internal/shared_kernel/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/persistence"
	"github.com/flext-sh/flext/internal/infrastructure/plugin_execution"
	"github.com/google/uuid"
)

func main() {
	fmt.Println("🚀 FLEXT Real Execution System Test")
	fmt.Println("===================================")

	ctx := context.Background()

	// Setup repositories
	pipelineRepo := persistence.NewInMemoryPipelineRepository()
	pluginRepo := persistence.NewInMemoryPluginRepository()
	executionRepo := persistence.NewInMemoryExecutionRepository()

	// Create execution stats service
	statsService := services.NewPipelineExecutionStatsService(executionRepo, pipelineRepo)

	// Create REAL plugin executor factory
	executorFactory := plugin_execution.NewExecutorFactory()
	
	fmt.Println("📁 Setting up plugin directories...")
	if err := executorFactory.SetupPluginDirectory(); err != nil {
		log.Printf("Warning: Failed to setup plugin directory: %v", err)
	}
	
	fmt.Println("📦 Installing sample plugins...")
	if err := executorFactory.InstallSamplePlugins(); err != nil {
		log.Printf("Warning: Failed to install sample plugins: %v", err)
	}

	// Create REAL pipeline executor (not simulation)
	pipelineExecutor := executorFactory.CreatePipelineExecutor(pluginRepo)

	// Create command handlers
	createHandler := commands.NewCreatePipelineCommandHandler(pipelineRepo)
	addStepHandler := commands.NewAddStepHandler(pipelineRepo, pluginRepo)
	updateHandler := commands.NewUpdatePipelineCommandHandler(pipelineRepo)
	executeHandler := commands.NewExecutePipelineHandler(pipelineRepo, pipelineExecutor, statsService)
	statusHandler := commands.NewGetPipelineStatusHandler(pipelineRepo, statsService)

	fmt.Println("\n🔧 Creating test pipeline...")

	// Step 1: Create pipeline
	createResult, err := createHandler.Handle(ctx, &commands.CreatePipelineCommand{
		Name:        "Real Execution Test Pipeline",
		Description: "Pipeline to test real plugin execution",
		Type:        "etl",
		Tags:        []string{"test", "real-execution"},
	})
	if err != nil {
		log.Fatal("Failed to create pipeline:", err)
	}

	pipelineID := uuid.MustParse(createResult.PipelineID)
	fmt.Printf("✅ Pipeline created: %s\n", pipelineID)

	// Step 2: Register real plugins
	fmt.Println("\n📋 Registering plugins...")
	
	csvPlugin := &pluginEntities.Plugin{
		BaseAggregateRoot: *sharedEntities.NewBaseAggregateRoot("plugin"),
		Name:              "csv-extractor",
		Description:       "Real CSV data extractor",
		Type:              pluginEntities.PluginTypeSource,
		Version:           "1.0.0",
		Status:            pluginEntities.PluginStatusActive,
		Configuration:     map[string]interface{}{"executable": "csv-extractor"},
	}

	filterPlugin := &pluginEntities.Plugin{
		BaseAggregateRoot: *sharedEntities.NewBaseAggregateRoot("plugin"),
		Name:              "data-filter",
		Description:       "Real data filter",
		Type:              pluginEntities.PluginTypeTransformer,
		Version:           "1.0.0",
		Status:            pluginEntities.PluginStatusActive,
		Configuration:     map[string]interface{}{"executable": "data-filter"},
	}

	postgresPlugin := &pluginEntities.Plugin{
		BaseAggregateRoot: *sharedEntities.NewBaseAggregateRoot("plugin"),
		Name:              "postgres-loader",
		Description:       "Real PostgreSQL loader",
		Type:              pluginEntities.PluginTypeTarget,
		Version:           "1.0.0",
		Status:            pluginEntities.PluginStatusActive,
		Configuration:     map[string]interface{}{"table": "processed_data"},
	}

	// Save plugins
	pluginRepo.Save(ctx, csvPlugin)
	pluginRepo.Save(ctx, filterPlugin)
	pluginRepo.Save(ctx, postgresPlugin)
	fmt.Printf("✅ Registered %d plugins\n", 3)

	// Step 3: Add pipeline steps
	fmt.Println("\n🔗 Adding pipeline steps...")

	_, err = addStepHandler.Handle(ctx, &commands.AddStepCommand{
		PipelineID:    pipelineID,
		Name:          "extract-csv",
		PluginID:      csvPlugin.GetID(),
		Configuration: map[string]interface{}{"file_path": "/tmp/test-data.csv"},
		Order:         1,
	})
	if err != nil {
		log.Fatal("Failed to add extract step:", err)
	}

	_, err = addStepHandler.Handle(ctx, &commands.AddStepCommand{
		PipelineID:    pipelineID,
		Name:          "filter-data",
		PluginID:      filterPlugin.GetID(),
		Configuration: map[string]interface{}{"filter": "status=active"},
		Order:         2,
	})
	if err != nil {
		log.Fatal("Failed to add filter step:", err)
	}

	_, err = addStepHandler.Handle(ctx, &commands.AddStepCommand{
		PipelineID:    pipelineID,
		Name:          "load-postgres",
		PluginID:      postgresPlugin.GetID(),
		Configuration: map[string]interface{}{"table": "active_users"},
		Order:         3,
	})
	if err != nil {
		log.Fatal("Failed to add load step:", err)
	}

	fmt.Printf("✅ Added 3 pipeline steps\n")

	// Step 4: Activate pipeline
	fmt.Println("\n🔄 Activating pipeline...")
	_, err = updateHandler.Handle(ctx, &commands.UpdatePipelineCommand{
		PipelineID: pipelineID,
		IsActive:   &[]bool{true}[0],
	})
	if err != nil {
		log.Fatal("Failed to activate pipeline:", err)
	}
	fmt.Printf("✅ Pipeline activated\n")

	// Step 5: Check status before execution
	fmt.Println("\n📊 Checking pipeline status...")
	statusResult, err := statusHandler.Handle(ctx, commands.GetPipelineStatusCommand{PipelineID: pipelineID})
	if err != nil {
		log.Fatal("Failed to get status:", err)
	}
	fmt.Printf("✅ Status: %s, Active: %v, Health: %s\n", 
		statusResult.Status, statusResult.IsActive, statusResult.HealthStatus)

	// Step 6: Execute pipeline with REAL execution
	fmt.Println("\n🚀 EXECUTING PIPELINE WITH REAL PLUGINS...")
	fmt.Println("=========================================")

	for i := 1; i <= 3; i++ {
		fmt.Printf("\n🔄 Execution #%d\n", i)
		start := time.Now()
		
		executeResult, err := executeHandler.Handle(ctx, &commands.ExecutePipelineCommand{
			PipelineID: pipelineID,
		})
		
		duration := time.Since(start)
		
		if err != nil {
			log.Printf("❌ Execution #%d failed: %v", i, err)
			continue
		}

		fmt.Printf("✅ Execution #%d completed in %v\n", i, duration)
		fmt.Printf("   • Execution ID: %s\n", executeResult.ExecutionID)
		fmt.Printf("   • Status: %s\n", executeResult.Status)
		fmt.Printf("   • Steps executed: %d/%d\n", executeResult.StepsExecuted, executeResult.StepsTotal)
		
		if executeResult.StepResults != nil {
			fmt.Printf("   • Step results:\n")
			for j, stepResult := range executeResult.StepResults {
				if success, ok := stepResult["execution_success"].(bool); ok && success {
					fmt.Printf("     - Step %d: ✅ Success\n", j+1)
					if records, ok := stepResult["records_processed"]; ok {
						fmt.Printf("       Records: %v\n", records)
					}
				} else {
					fmt.Printf("     - Step %d: ❌ Failed\n", j+1)
				}
			}
		}

		time.Sleep(100 * time.Millisecond)
	}

	// Step 7: Final status check
	fmt.Println("\n📈 FINAL SYSTEM STATUS")
	fmt.Println("=====================")

	finalStatus, err := statusHandler.Handle(ctx, commands.GetPipelineStatusCommand{PipelineID: pipelineID})
	if err != nil {
		log.Fatal("Failed to get final status:", err)
	}

	fmt.Printf("Pipeline: %s\n", finalStatus.Name)
	fmt.Printf("Status: %s\n", finalStatus.Status)
	fmt.Printf("Health: %s\n", finalStatus.HealthStatus)
	fmt.Printf("Total executions: %d\n", finalStatus.ExecutionCount)
	fmt.Printf("Successful: %d\n", finalStatus.SuccessCount)
	fmt.Printf("Failed: %d\n", finalStatus.FailureCount)

	if finalStatus.Metrics != nil {
		if successRate, ok := finalStatus.Metrics["execution_success_rate"]; ok {
			fmt.Printf("Success rate: %.1f%%\n", successRate)
		}
	}

	// Step 8: Plugin directory verification
	fmt.Println("\n📁 PLUGIN SYSTEM VERIFICATION")
	fmt.Println("=============================")

	pluginsDir := os.Getenv("FLEXT_PLUGINS_DIR")
	if pluginsDir == "" {
		pluginsDir = "/opt/flext/plugins"
	}

	if _, err := os.Stat(pluginsDir); err == nil {
		fmt.Printf("✅ Plugin directory exists: %s\n", pluginsDir)
		
		// Check for installed plugins
		plugins := []string{"csv-extractor", "data-filter"}
		for _, plugin := range plugins {
			pluginPath := fmt.Sprintf("%s/%s", pluginsDir, plugin)
			if _, err := os.Stat(pluginPath); err == nil {
				fmt.Printf("✅ Plugin installed: %s\n", plugin)
			} else {
				fmt.Printf("⚠️  Plugin not found: %s\n", plugin)
			}
		}
	} else {
		fmt.Printf("⚠️  Plugin directory not accessible: %s\n", pluginsDir)
	}

	fmt.Println("\n🎉 REAL EXECUTION SYSTEM TEST COMPLETED!")
	fmt.Printf("System Status: %s\n", getSystemStatus(finalStatus))
	
	os.Exit(getExitCode(finalStatus))
}

func getSystemStatus(status *commands.GetPipelineStatusResult) string {
	if status.ExecutionCount >= 3 && status.SuccessCount >= 2 {
		return "🟢 FULLY OPERATIONAL"
	} else if status.ExecutionCount >= 1 {
		return "🟡 PARTIALLY FUNCTIONAL"
	} else {
		return "🔴 NOT FUNCTIONAL"
	}
}

func getExitCode(status *commands.GetPipelineStatusResult) int {
	if status.ExecutionCount >= 3 && status.SuccessCount >= 2 {
		return 0 // Success
	} else {
		return 1 // Partial failure
	}
}