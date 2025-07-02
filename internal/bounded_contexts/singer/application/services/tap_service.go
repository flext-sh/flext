package services

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/queries"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
)

// TapService provides high-level tap operations
type TapService struct {
	// Command handlers (only the ones that exist)
	installTapHandler *commands.InstallTapHandler

	// Query handlers
	getTapHandler  *queries.GetTapHandler
	listTapHandler *queries.ListTapsHandler

	// Repositories
	tapRepo ports.TapRepository
}

// NewTapService creates a new tap service
func NewTapService(tapRepo ports.TapRepository) *TapService {
	return &TapService{
		// Initialize command handlers (only existing ones)
		installTapHandler: commands.NewInstallTapHandler(tapRepo),

		// Initialize query handlers
		getTapHandler:  queries.NewGetTapHandler(tapRepo),
		listTapHandler: queries.NewListTapsHandler(tapRepo),

		// Store repository reference
		tapRepo: tapRepo,
	}
}

// Command operations (only the ones we have handlers for)

// InstallTap installs a tap
func (s *TapService) InstallTap(ctx context.Context, cmd commands.InstallTapCommand) (*queries.TapDTO, error) {
	if err := s.validateContext(ctx); err != nil {
		return nil, err
	}

	// Execute install command
	result, err := s.installTapHandler.Handle(ctx, cmd)
	if err != nil {
		return nil, fmt.Errorf("failed to install tap: %w", err)
	}

	// Return the installed tap
	return s.getTapHandler.Handle(ctx, queries.GetTapQuery{TapID: result.TapID})
}

// Query operations

// GetTap retrieves a tap by ID
func (s *TapService) GetTap(ctx context.Context, tapID string) (*queries.TapDTO, error) {
	if err := s.validateContext(ctx); err != nil {
		return nil, err
	}

	query := queries.GetTapQuery{TapID: tapID}
	return s.getTapHandler.Handle(ctx, query)
}

// ListTaps retrieves a list of taps with filtering and pagination
func (s *TapService) ListTaps(ctx context.Context, query queries.ListTapsQuery) (*queries.ListTapsResponse, error) {
	if err := s.validateContext(ctx); err != nil {
		return nil, err
	}

	return s.listTapHandler.Handle(ctx, query)
}

// Utility operations

// GetTapStats returns statistics about taps
func (s *TapService) GetTapStats(ctx context.Context) (*TapStats, error) {
	if err := s.validateContext(ctx); err != nil {
		return nil, err
	}

	// Get all taps with basic query
	listQuery := queries.ListTapsQuery{
		Page:     1,
		PageSize: 100, // Maximum allowed page size
	}

	response, err := s.listTapHandler.Handle(ctx, listQuery)
	if err != nil {
		return nil, fmt.Errorf("failed to get tap stats: %w", err)
	}

	// Calculate statistics
	stats := &TapStats{
		Total:     int(response.Pagination.TotalItems),
		Active:    0,
		Inactive:  0,
		Installed: 0,
		ByType:    make(map[string]int),
	}

	for _, tap := range response.Taps {
		// Count by status (convert enum to string)
		switch string(tap.Status) {
		case "installed":
			stats.Active++
		case "not_installed":
			stats.Inactive++
		}

		// Count installed taps
		if tap.InstallationPath != "" {
			stats.Installed++
		}

		// Count by type (convert enum to string)
		typeStr := string(tap.Type)
		if _, exists := stats.ByType[typeStr]; !exists {
			stats.ByType[typeStr] = 0
		}
		stats.ByType[typeStr]++
	}

	return stats, nil
}

// Health check for the service
func (s *TapService) HealthCheck(ctx context.Context) error {
	if err := s.validateContext(ctx); err != nil {
		return err
	}

	// Test basic repository connectivity using the port's QueryOptions
	options := ports.QueryOptions{
		Limit:  1,
		Offset: 0,
	}

	_, err := s.tapRepo.List(ctx, options)
	if err != nil {
		return &value_objects.DomainError{
			Code:        "HEALTH_CHECK_FAILED",
			Message:     "Tap service health check failed",
			Description: fmt.Sprintf("Repository connectivity test failed: %v", err),
		}
	}

	return nil
}

// validateContext ensures the context is valid
func (s *TapService) validateContext(ctx context.Context) error {
	if ctx == nil {
		return &value_objects.DomainError{
			Code:        "INVALID_CONTEXT",
			Message:     "Context is required",
			Description: "Context cannot be nil",
		}
	}

	// Check for context cancellation
	select {
	case <-ctx.Done():
		return &value_objects.DomainError{
			Code:        "CONTEXT_CANCELLED",
			Message:     "Operation cancelled",
			Description: ctx.Err().Error(),
		}
	default:
		return nil
	}
}

// TapStats represents tap statistics
type TapStats struct {
	Total     int            `json:"total"`
	Active    int            `json:"active"`
	Inactive  int            `json:"inactive"`
	Installed int            `json:"installed"`
	ByType    map[string]int `json:"by_type"`
}
