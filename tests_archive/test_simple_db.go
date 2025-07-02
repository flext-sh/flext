package main

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
)

func main() {
	fmt.Println("🔍 FLEXT DATABASE CONNECTION TEST")
	fmt.Println("============================================================")

	// Initialize logger
	logger := logging.GetLogger()

	// Try PostgreSQL configuration
	cfg := config.DefaultConfig()
	cfg.Features.DatabaseEnabled = true
	cfg.Database.Driver = "postgres"
	cfg.Database.Database = "flext_db"
	cfg.Database.Username = "flext"
	cfg.Database.Password = "flext"
	
	fmt.Println("\n📊 Testing PostgreSQL Connection")
	
	containerInstance, err := container.NewContainer(cfg)
	if err != nil {
		fmt.Printf("❌ Failed to create container: %v\n", err)
		return
	}
	
	// Test database health
	ctx := context.Background()
	if err := containerInstance.HealthCheck(ctx); err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	
	fmt.Println("✅ PostgreSQL connection and health check successful")
	
	// Test database connection directly
	dbConn := containerInstance.GetDatabaseConnection()
	if dbConn == nil {
		fmt.Printf("❌ Database connection is nil\n")
		return
	}
	
	fmt.Println("✅ Database connection available")
	
	// Test getting DB interface
	db := dbConn.GetDB()
	if db == nil {
		fmt.Printf("❌ DB interface is nil\n")
		return
	}
	
	fmt.Println("✅ DB interface available")
	
	// Test basic ping
	if err := db.PingContext(ctx); err != nil {
		fmt.Printf("❌ DB ping failed: %v\n", err)
		return
	}
	
	fmt.Println("✅ DB ping successful")
	
	// Test a simple query
	rows, err := db.QueryContext(ctx, "SELECT 1 as test")
	if err != nil {
		fmt.Printf("❌ Simple query failed: %v\n", err)
		return
	}
	defer rows.Close()
	
	if rows.Next() {
		var test int
		if err := rows.Scan(&test); err != nil {
			fmt.Printf("❌ Scan failed: %v\n", err)
			return
		}
		fmt.Printf("✅ Simple query successful: %d\n", test)
	}
	
	// Test table existence
	tableQuery := "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'pipelines')"
	var exists bool
	if err := db.QueryRowContext(ctx, tableQuery).Scan(&exists); err != nil {
		fmt.Printf("❌ Table check failed: %v\n", err)
		return
	}
	
	if exists {
		fmt.Println("✅ Pipelines table exists")
	} else {
		fmt.Println("⚠️  Pipelines table does not exist")
	}
	
	// Test repository
	pipelineService := containerInstance.GetPipelineService()
	if pipelineService == nil {
		fmt.Printf("❌ Pipeline service is nil\n")
		return
	}
	
	fmt.Println("✅ Pipeline service available")
	
	// Shutdown
	if err := containerInstance.Shutdown(); err != nil {
		fmt.Printf("❌ Shutdown failed: %v\n", err)
		return
	}
	
	fmt.Println("✅ Container shutdown successful")
	
	fmt.Println("\n============================================================")
	fmt.Println("🎉 DATABASE CONNECTION TEST COMPLETE")
	fmt.Println("✅ All basic database operations working")
	fmt.Println("============================================================")
}