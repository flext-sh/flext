package singer

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/queries"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/infrastructure/persistence"
)

// TestSingerBoundedContextIntegration tests the complete Singer bounded context flow
func TestSingerBoundedContextIntegration(t *testing.T) {
	// Setup
	ctx := context.Background()
	repo := persistence.NewMemoryTapRepository()
	tapService := services.NewTapService(repo)

	t.Run("Complete tap lifecycle", func(t *testing.T) {
		// Test Install Tap Command
		installCmd := commands.InstallTapCommand{
			Name:        "tap-postgres",
			DisplayName: "PostgreSQL Tap",
			Description: "Extract data from PostgreSQL databases",
			Type:        entities.TapTypeExtractor,
			PipName:     "pipelinewise-tap-postgres",
			Version:     "1.0.0",
			Repository:  "https://github.com/transferwise/pipelinewise-tap-postgres",
			Configuration: map[string]interface{}{
				"host":     "localhost",
				"port":     5432,
				"database": "test_db",
			},
		}

		// Install the tap
		installedTap, err := tapService.InstallTap(ctx, installCmd)
		require.NoError(t, err)
		require.NotNil(t, installedTap)

		// Verify installation
		assert.Equal(t, "tap-postgres", installedTap.Name)
		assert.Equal(t, "PostgreSQL Tap", installedTap.DisplayName)
		assert.Equal(t, entities.TapTypeExtractor, installedTap.Type)
		assert.Equal(t, entities.TapStatusInstalled, installedTap.Status)
		assert.NotEmpty(t, installedTap.ID)
		assert.NotEmpty(t, installedTap.InstallationPath)

		// Test Get Tap Query
		retrievedTap, err := tapService.GetTap(ctx, installedTap.ID)
		require.NoError(t, err)
		require.NotNil(t, retrievedTap)
		assert.Equal(t, installedTap.ID, retrievedTap.ID)
		assert.Equal(t, installedTap.Name, retrievedTap.Name)

		// Test List Taps Query
		listQuery := queries.ListTapsQuery{
			Page:     1,
			PageSize: 10,
		}
		listResponse, err := tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		require.NotNil(t, listResponse)
		assert.Len(t, listResponse.Taps, 1)
		assert.Equal(t, int64(1), listResponse.Pagination.TotalItems)

		// Test filtering by type
		listQuery.Type = string(entities.TapTypeExtractor)
		listResponse, err = tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 1)

		// Test filtering by non-existent type
		listQuery.Type = string(entities.TapTypeLoader)
		listResponse, err = tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 0)

		// Test search functionality
		listQuery = queries.ListTapsQuery{
			Page:     1,
			PageSize: 10,
			Search:   "postgres",
		}
		listResponse, err = tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 1)

		// Test non-matching search
		listQuery.Search = "mysql"
		listResponse, err = tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 0)

		// Test tap statistics
		stats, err := tapService.GetTapStats(ctx)
		require.NoError(t, err)
		require.NotNil(t, stats)
		assert.Equal(t, 1, stats.Total)
		assert.Equal(t, 1, stats.Active) // Installed taps are considered active
		assert.Equal(t, 0, stats.Inactive)
		assert.Equal(t, 1, stats.Installed)
		assert.Equal(t, 1, stats.ByType["extractor"])

		// Test health check
		err = tapService.HealthCheck(ctx)
		assert.NoError(t, err)
	})

	t.Run("Multiple taps scenario", func(t *testing.T) {
		// Install another tap of different type
		installCmd := commands.InstallTapCommand{
			Name:        "target-snowflake",
			DisplayName: "Snowflake Target",
			Description: "Load data to Snowflake",
			Type:        entities.TapTypeLoader,
			PipName:     "pipelinewise-target-snowflake",
			Version:     "1.5.0",
			Repository:  "https://github.com/transferwise/pipelinewise-target-snowflake",
			Configuration: map[string]interface{}{
				"account":   "test_account",
				"warehouse": "COMPUTE_WH",
				"database":  "ANALYTICS",
			},
		}

		// Install the target
		installedTarget, err := tapService.InstallTap(ctx, installCmd)
		require.NoError(t, err)
		require.NotNil(t, installedTarget)

		// Verify we now have 2 taps
		listQuery := queries.ListTapsQuery{
			Page:     1,
			PageSize: 10,
		}
		listResponse, err := tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 2)
		assert.Equal(t, int64(2), listResponse.Pagination.TotalItems)

		// Test filtering by loader type
		listQuery.Type = string(entities.TapTypeLoader)
		listResponse, err = tapService.ListTaps(ctx, listQuery)
		require.NoError(t, err)
		assert.Len(t, listResponse.Taps, 1)
		assert.Equal(t, "target-snowflake", listResponse.Taps[0].Name)

		// Test updated statistics
		stats, err := tapService.GetTapStats(ctx)
		require.NoError(t, err)
		assert.Equal(t, 2, stats.Total)
		assert.Equal(t, 2, stats.Active)
		assert.Equal(t, 2, stats.Installed)
		assert.Equal(t, 1, stats.ByType["extractor"])
		assert.Equal(t, 1, stats.ByType["loader"])
	})

	t.Run("Error handling scenarios", func(t *testing.T) {
		// Test invalid tap ID
		_, err := tapService.GetTap(ctx, "invalid-uuid")
		assert.Error(t, err)

		// Test duplicate installation
		duplicateCmd := commands.InstallTapCommand{
			Name:        "tap-postgres", // Same name as first tap
			DisplayName: "Duplicate PostgreSQL Tap",
			Type:        entities.TapTypeExtractor,
		}

		_, err = tapService.InstallTap(ctx, duplicateCmd)
		assert.Error(t, err) // Should fail because tap already exists

		// Test force installation (should work)
		duplicateCmd.Force = true
		_, err = tapService.InstallTap(ctx, duplicateCmd)
		assert.NoError(t, err) // Should work with force=true
	})

	t.Run("Repository operations", func(t *testing.T) {
		// Test direct repository operations
		taps, err := repo.GetInstalledTaps(ctx)
		require.NoError(t, err)
		assert.Len(t, taps, 2) // 2 installed taps

		// Test get by type
		extractors, err := repo.GetTapsByType(ctx, entities.TapTypeExtractor)
		require.NoError(t, err)
		assert.Len(t, extractors, 1)

		loaders, err := repo.GetTapsByType(ctx, entities.TapTypeLoader)
		require.NoError(t, err)
		assert.Len(t, loaders, 1)

		// Test search
		searchResult, err := repo.SearchTaps(ctx, "postgres", ports.QueryOptions{})
		require.NoError(t, err)
		assert.Len(t, searchResult, 1)
	})
}

// TestRepositoryMemoryImplementation tests the in-memory repository implementation
func TestRepositoryMemoryImplementation(t *testing.T) {
	ctx := context.Background()
	repo := persistence.NewMemoryTapRepository()

	// Create a test tap
	tap := entities.NewTap("test-tap", "Test Tap", "Test Description", entities.TapTypeExtractor)

	t.Run("Basic CRUD operations", func(t *testing.T) {
		// Save
		err := repo.Save(ctx, tap)
		require.NoError(t, err)

		// Get by ID
		retrieved, err := repo.GetByID(ctx, tap.ID)
		require.NoError(t, err)
		assert.Equal(t, tap.ID, retrieved.ID)
		assert.Equal(t, tap.Name, retrieved.Name)

		// Get by name
		retrievedByName, err := repo.GetByName(ctx, tap.Name)
		require.NoError(t, err)
		assert.Equal(t, tap.ID, retrievedByName.ID)

		// Update
		tap.Description = "Updated Description"
		updated, err := repo.Update(ctx, tap)
		require.NoError(t, err)
		assert.Equal(t, "Updated Description", updated.Description)

		// Delete
		err = repo.Delete(ctx, tap.ID)
		require.NoError(t, err)

		// Verify deletion
		_, err = repo.GetByID(ctx, tap.ID)
		assert.Error(t, err)
	})

	t.Run("Query operations with pagination", func(t *testing.T) {
		// Create multiple taps for testing
		for i := 0; i < 5; i++ {
			tap := entities.NewTap(fmt.Sprintf("tap-%d", i), fmt.Sprintf("Tap %d", i), "Description", entities.TapTypeExtractor)
			err := repo.Save(ctx, tap)
			require.NoError(t, err)
		}

		// Test list with pagination
		options := ports.QueryOptions{
			Limit:  2,
			Offset: 0,
		}
		taps, err := repo.List(ctx, options)
		require.NoError(t, err)
		assert.Len(t, taps, 2)

		// Test pagination offset
		options.Offset = 2
		taps, err = repo.List(ctx, options)
		require.NoError(t, err)
		assert.Len(t, taps, 2)

		// Test count
		count, err := repo.Count(ctx, ports.QueryOptions{})
		require.NoError(t, err)
		assert.Equal(t, 5, count)
	})
}
