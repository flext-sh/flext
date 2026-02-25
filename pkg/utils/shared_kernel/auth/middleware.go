package auth

import (
	"context"
	"strings"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/errors"
	"github.com/labstack/echo/v4"
)

// ContextKey defines a custom type for context keys to avoid collisions
type ContextKey string

const (
	// UserContextKey is the key for storing user context in request context
	UserContextKey ContextKey = "user_context"
)

// UnifiedAuthMiddleware provides authentication middleware for Echo
type UnifiedAuthMiddleware struct {
	authService  *UnifiedAuthService
	logger       logging.Logger
	publicPaths  map[string]bool
	skipPrefixes []string
}

// MiddlewareConfig configuration for the auth middleware
type MiddlewareConfig struct {
	PublicPaths  []string `json:"public_paths"`
	SkipPrefixes []string `json:"skip_prefixes"`
	Required     bool     `json:"required"` // If true, authentication is required for all paths except public
}

// NewUnifiedAuthMiddleware creates a new unified auth middleware
func NewUnifiedAuthMiddleware(authService *UnifiedAuthService, config MiddlewareConfig, logger logging.Logger) *UnifiedAuthMiddleware {
	publicPaths := make(map[string]bool)
	for _, path := range config.PublicPaths {
		publicPaths[path] = true
	}

	// Add default public paths
	defaultPublicPaths := []string{
		"/health",
		"/metrics",
		"/api/v1/auth/login",
		"/api/v1/auth/register",
		"/api/v1/auth/refresh",
		"/docs",
		"/swagger",
	}

	for _, path := range defaultPublicPaths {
		publicPaths[path] = true
	}

	return &UnifiedAuthMiddleware{
		authService:  authService,
		logger:       logger.With(logging.F("component", "auth_middleware")),
		publicPaths:  publicPaths,
		skipPrefixes: config.SkipPrefixes,
	}
}

// Middleware returns the Echo middleware function
func (m *UnifiedAuthMiddleware) Middleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			path := c.Request().URL.Path

			// Check if path should be skipped
			if m.shouldSkipPath(path) {
				return next(c)
			}

			// Extract token from request
			token, authType := m.extractToken(c)
			if token == "" {
				m.logger.Debug("No authentication token found",
					logging.F("path", path),
					logging.F("method", c.Request().Method),
				)
				return m.handleUnauthorized(c, "Authentication token required")
			}

			// Validate token
			userContext, err := m.authService.ValidateToken(c.Request().Context(), token)
			if err != nil {
				m.logger.Warn("Token validation failed",
					logging.F("path", path),
					logging.F("auth_type", authType),
					logging.F("error", err.Error()),
				)
				return m.handleUnauthorized(c, "Invalid authentication token")
			}

			// Set user context in request context
			ctx := context.WithValue(c.Request().Context(), UserContextKey, userContext)
			c.SetRequest(c.Request().WithContext(ctx))

			// Set user information in Echo context for easy access
			c.Set("user_id", userContext.UserID)
			c.Set("username", userContext.Username)
			c.Set("user_roles", userContext.Roles)
			c.Set("user_permissions", userContext.Permissions)
			c.Set("auth_type", userContext.AuthType)

			m.logger.Debug("User authenticated",
				logging.F("user_id", userContext.UserID),
				logging.F("username", userContext.Username),
				logging.F("auth_type", userContext.AuthType),
				logging.F("path", path),
			)

			return next(c)
		}
	}
}

// RequireRole returns middleware that requires specific roles
func (m *UnifiedAuthMiddleware) RequireRole(roles ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			userContext, err := m.getUserContext(c)
			if err != nil {
				return m.handleForbidden(c, "User context not found")
			}

			if !m.hasAnyRole(userContext.Roles, roles) {
				m.logger.Warn("Access denied - insufficient roles",
					logging.F("user_id", userContext.UserID),
					logging.F("user_roles", userContext.Roles),
					logging.F("required_roles", roles),
					logging.F("path", c.Request().URL.Path),
				)
				return m.handleForbidden(c, "Insufficient permissions")
			}

			return next(c)
		}
	}
}

// RequirePermission returns middleware that requires specific permissions
func (m *UnifiedAuthMiddleware) RequirePermission(permissions ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			userContext, err := m.getUserContext(c)
			if err != nil {
				return m.handleForbidden(c, "User context not found")
			}

			if !m.hasAnyPermission(userContext.Permissions, permissions) && !m.hasAnyRole(userContext.Roles, []string{"REDACTED_LDAP_BIND_PASSWORD"}) {
				m.logger.Warn("Access denied - insufficient permissions",
					logging.F("user_id", userContext.UserID),
					logging.F("user_permissions", userContext.Permissions),
					logging.F("required_permissions", permissions),
					logging.F("path", c.Request().URL.Path),
				)
				return m.handleForbidden(c, "Insufficient permissions")
			}

			return next(c)
		}
	}
}

// extractToken extracts authentication token from request
func (m *UnifiedAuthMiddleware) extractToken(c echo.Context) (string, string) {
	// Try Authorization header first (Bearer token or Basic auth)
	authHeader := c.Request().Header.Get("Authorization")
	if authHeader != "" {
		if strings.HasPrefix(authHeader, "Bearer ") {
			return strings.TrimPrefix(authHeader, "Bearer "), "jwt"
		}
		if strings.HasPrefix(authHeader, "Basic ") {
			return authHeader, "basic"
		}
	}

	// Try API key header
	apiKey := c.Request().Header.Get("X-API-Key")
	if apiKey != "" {
		return apiKey, "api_key"
	}

	// Try API key in query parameter
	queryAPIKey := c.QueryParam("api_key")
	if queryAPIKey != "" {
		return queryAPIKey, "api_key"
	}

	// Try cookie for web sessions
	cookie, err := c.Cookie("flext_token")
	if err == nil && cookie.Value != "" {
		return cookie.Value, "jwt"
	}

	return "", ""
}

// shouldSkipPath determines if authentication should be skipped for a path
func (m *UnifiedAuthMiddleware) shouldSkipPath(path string) bool {
	// Check exact matches
	if m.publicPaths[path] {
		return true
	}

	// Check prefixes
	for _, prefix := range m.skipPrefixes {
		if strings.HasPrefix(path, prefix) {
			return true
		}
	}

	return false
}

// getUserContext extracts user context from Echo context
func (m *UnifiedAuthMiddleware) getUserContext(c echo.Context) (*UserContext, error) {
	userContext, ok := c.Request().Context().Value("user_context").(*UserContext)
	if !ok {
		return nil, &errors.DomainError{
			Code:    "USER_CONTEXT_NOT_FOUND",
			Message: "User context not found",
			Details: "Authentication middleware was not applied or user is not authenticated",
		}
	}
	return userContext, nil
}

// hasAnyRole checks if user has any of the required roles
func (m *UnifiedAuthMiddleware) hasAnyRole(userRoles, requiredRoles []string) bool {
	for _, requiredRole := range requiredRoles {
		for _, userRole := range userRoles {
			if userRole == requiredRole || userRole == "REDACTED_LDAP_BIND_PASSWORD" {
				return true
			}
		}
	}
	return false
}

// hasAnyPermission checks if user has any of the required permissions
func (m *UnifiedAuthMiddleware) hasAnyPermission(userPermissions, requiredPermissions []string) bool {
	for _, requiredPermission := range requiredPermissions {
		for _, userPermission := range userPermissions {
			if userPermission == requiredPermission || userPermission == "*" {
				return true
			}
		}
	}
	return false
}

// handleUnauthorized handles unauthorized access
func (m *UnifiedAuthMiddleware) handleUnauthorized(c echo.Context, message string) error {
	return c.JSON(401, map[string]interface{}{
		"error":     "Unauthorized",
		"message":   message,
		"code":      "UNAUTHORIZED",
		"timestamp": "2025-06-30T08:22:55Z",
	})
}

// handleForbidden handles forbidden access
func (m *UnifiedAuthMiddleware) handleForbidden(c echo.Context, message string) error {
	return c.JSON(403, map[string]interface{}{
		"error":     "Forbidden",
		"message":   message,
		"code":      "FORBIDDEN",
		"timestamp": "2025-06-30T08:22:55Z",
	})
}

// Optional: Helper functions for route-level authentication

// RequireAuthentication is a route-level helper
func (m *UnifiedAuthMiddleware) RequireAuthentication(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		userContext, err := m.getUserContext(c)
		if err != nil {
			return m.handleUnauthorized(c, "Authentication required")
		}

		m.logger.Debug("Route-level authentication check passed",
			logging.F("user_id", userContext.UserID),
			logging.F("path", c.Request().URL.Path),
		)

		return next(c)
	}
}

// RequireAdmin is a route-level helper for REDACTED_LDAP_BIND_PASSWORD access
func (m *UnifiedAuthMiddleware) RequireAdmin(next echo.HandlerFunc) echo.HandlerFunc {
	return m.RequireRole("REDACTED_LDAP_BIND_PASSWORD")(next)
}

// GetUserFromContext extracts user context from Echo context (utility function)
func GetUserFromContext(c echo.Context) (*UserContext, error) {
	userContext, ok := c.Request().Context().Value("user_context").(*UserContext)
	if !ok {
		return nil, &errors.DomainError{
			Code:    "USER_CONTEXT_NOT_FOUND",
			Message: "User context not found",
			Details: "No authenticated user found in request context",
		}
	}
	return userContext, nil
}
