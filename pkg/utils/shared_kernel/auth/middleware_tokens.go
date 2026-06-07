package auth

import (
	"strings"

	"github.com/labstack/echo/v4"
)

// extractToken extracts authentication token from request
func (m *UnifiedAuthMiddleware) extractToken(c echo.Context) (string, string) {
	token, authType := authorizationHeaderToken(c.Request().Header.Get("Authorization"))
	if token == "" {
		if apiKey := c.Request().Header.Get("X-API-Key"); apiKey != "" {
			token, authType = apiKey, "api_key"
		}
	}
	if token == "" {
		if apiKey := c.QueryParam("api_key"); apiKey != "" {
			token, authType = apiKey, "api_key"
		}
	}
	if token == "" {
		if cookie, err := c.Cookie("flext_token"); err == nil && cookie.Value != "" {
			token, authType = cookie.Value, "jwt"
		}
	}
	return token, authType
}

func authorizationHeaderToken(authHeader string) (string, string) {
	token, authType := "", ""
	switch {
	case strings.HasPrefix(authHeader, "Bearer "):
		token, authType = strings.TrimPrefix(authHeader, "Bearer "), "jwt"
	case strings.HasPrefix(authHeader, "Basic "):
		token, authType = authHeader, "basic"
	}
	return token, authType
}
