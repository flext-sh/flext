package auth

import (
	"context"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// BasicAuthProvider provides basic username/password authentication
type BasicAuthProvider struct {
	logger logging.Logger
	users  map[string]UserCredentials // In production, this would be a database
}

// UserCredentials represents stored user credentials
type UserCredentials struct {
	UserID      uuid.UUID `json:"user_id"`
	Username    string    `json:"username"`
	Email       string    `json:"email"`
	PasswordHash string   `json:"password_hash"`
	Roles       []string  `json:"roles"`
	Permissions []string  `json:"permissions"`
	IsActive    bool      `json:"is_active"`
}

// NewBasicAuthProvider creates a new basic auth provider
func NewBasicAuthProvider(logger logging.Logger) *BasicAuthProvider {
	// Initialize with some test users
	testUsers := map[string]UserCredentials{
		"REDACTED_LDAP_BIND_PASSWORD": {
			UserID:       uuid.New(),
			Username:     "REDACTED_LDAP_BIND_PASSWORD",
			Email:        "REDACTED_LDAP_BIND_PASSWORD@internal.invalid",
			PasswordHash: "REDACTED_LDAP_BIND_PASSWORD", // In production, this would be properly hashed
			Roles:        []string{"REDACTED_LDAP_BIND_PASSWORD", "user"},
			Permissions:  []string{"*"},
			IsActive:     true,
		},
		"user": {
			UserID:       uuid.New(),
			Username:     "user",
			Email:        "user@internal.invalid",
			PasswordHash: "user", // In production, this would be properly hashed
			Roles:        []string{"user"},
			Permissions:  []string{"read", "execute"},
			IsActive:     true,
		},
	}

	return &BasicAuthProvider{
		logger: logger.With(logging.F("provider", "basic_auth")),
		users:  testUsers,
	}
}

// GetProviderType returns the provider type
func (p *BasicAuthProvider) GetProviderType() string {
	return "basic"
}

// Authenticate authenticates user with username/password
func (p *BasicAuthProvider) Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error) {
	if credentials.Username == "" || credentials.Password == "" {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_CREDENTIALS",
			Message:     "Username and password are required",
			Description: "Both username and password must be provided for basic authentication",
		}
	}

	user, exists := p.users[credentials.Username]
	if !exists {
		p.logger.Warn("User not found",
			logging.F("username", credentials.Username),
		)
		return nil, &value_objects.DomainError{
			Code:        "AUTHENTICATION_FAILED",
			Message:     "Invalid username or password",
			Description: "The provided credentials are incorrect",
		}
	}

	if !user.IsActive {
		return nil, &value_objects.DomainError{
			Code:        "USER_INACTIVE",
			Message:     "User account is inactive",
			Description: "The user account has been deactivated",
		}
	}

	// In production, use proper password hashing (bcrypt, argon2, etc.)
	if subtle.ConstantTimeCompare([]byte(credentials.Password), []byte(user.PasswordHash)) != 1 {
		p.logger.Warn("Password verification failed",
			logging.F("username", credentials.Username),
		)
		return nil, &value_objects.DomainError{
			Code:        "AUTHENTICATION_FAILED",
			Message:     "Invalid username or password",
			Description: "The provided credentials are incorrect",
		}
	}

	return &AuthResult{
		UserID:      user.UserID,
		Username:    user.Username,
		Email:       user.Email,
		Roles:       user.Roles,
		Permissions: user.Permissions,
	}, nil
}

// Validate validates a basic auth token (base64 encoded username:password)
func (p *BasicAuthProvider) Validate(ctx context.Context, token string) (*UserContext, error) {
	if !strings.HasPrefix(token, "Basic ") {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TOKEN_FORMAT",
			Message:     "Invalid basic auth token format",
			Description: "Basic auth token must start with 'Basic '",
		}
	}

	encodedCredentials := strings.TrimPrefix(token, "Basic ")
	decodedBytes, err := base64.StdEncoding.DecodeString(encodedCredentials)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TOKEN_ENCODING",
			Message:     "Invalid token encoding",
			Description: "Failed to decode base64 credentials",
		}
	}

	credentials := strings.SplitN(string(decodedBytes), ":", 2)
	if len(credentials) != 2 {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_CREDENTIALS_FORMAT",
			Message:     "Invalid credentials format",
			Description: "Credentials must be in format 'username:password'",
		}
	}

	authResult, err := p.Authenticate(ctx, Credentials{
		Username: credentials[0],
		Password: credentials[1],
	})
	if err != nil {
		return nil, err
	}

	return &UserContext{
		UserID:      authResult.UserID,
		Username:    authResult.Username,
		Email:       authResult.Email,
		Roles:       authResult.Roles,
		Permissions: authResult.Permissions,
		AuthType:    "basic",
	}, nil
}

// JWTProvider provides JWT token validation
type JWTProvider struct {
	jwtSecret []byte
	logger    logging.Logger
}

// NewJWTProvider creates a new JWT provider
func NewJWTProvider(jwtSecret string, logger logging.Logger) *JWTProvider {
	return &JWTProvider{
		jwtSecret: []byte(jwtSecret),
		logger:    logger.With(logging.F("provider", "jwt")),
	}
}

// GetProviderType returns the provider type
func (p *JWTProvider) GetProviderType() string {
	return "jwt"
}

// Authenticate authenticates using JWT token
func (p *JWTProvider) Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error) {
	if credentials.Token == "" {
		return nil, &value_objects.DomainError{
			Code:        "TOKEN_REQUIRED",
			Message:     "JWT token is required",
			Description: "A valid JWT token must be provided",
		}
	}

	userContext, err := p.Validate(ctx, credentials.Token)
	if err != nil {
		return nil, err
	}

	return &AuthResult{
		UserID:      userContext.UserID,
		Username:    userContext.Username,
		Email:       userContext.Email,
		Roles:       userContext.Roles,
		Permissions: userContext.Permissions,
	}, nil
}

// Validate validates a JWT token
func (p *JWTProvider) Validate(ctx context.Context, tokenString string) (*UserContext, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return p.jwtSecret, nil
	})

	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "TOKEN_PARSE_ERROR",
			Message:     "Failed to parse JWT token",
			Description: err.Error(),
		}
	}

	if !token.Valid {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TOKEN",
			Message:     "JWT token is invalid",
			Description: "The provided JWT token is not valid",
		}
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_CLAIMS",
			Message:     "Invalid JWT claims",
			Description: "Unable to parse JWT token claims",
		}
	}

	// Verify token type (should be access token for authentication)
	if tokenType, ok := claims["type"].(string); ok && tokenType != "access" {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TOKEN_TYPE",
			Message:     "Invalid token type",
			Description: fmt.Sprintf("Expected access token, got %s", tokenType),
		}
	}

	userIDStr, ok := claims["sub"].(string)
	if !ok {
		return nil, &value_objects.DomainError{
			Code:        "MISSING_USER_ID",
			Message:     "User ID not found in token",
			Description: "JWT token must contain a valid user ID in the 'sub' claim",
		}
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_USER_ID_FORMAT",
			Message:     "Invalid user ID format",
			Description: "User ID must be a valid UUID",
		}
	}

	username, _ := claims["username"].(string)
	email, _ := claims["email"].(string)

	// Parse roles and permissions
	var roles []string
	if rolesInterface, ok := claims["roles"].([]interface{}); ok {
		for _, role := range rolesInterface {
			if roleStr, ok := role.(string); ok {
				roles = append(roles, roleStr)
			}
		}
	}

	var permissions []string
	if permissionsInterface, ok := claims["permissions"].([]interface{}); ok {
		for _, permission := range permissionsInterface {
			if permissionStr, ok := permission.(string); ok {
				permissions = append(permissions, permissionStr)
			}
		}
	}

	return &UserContext{
		UserID:      userID,
		Username:    username,
		Email:       email,
		Roles:       roles,
		Permissions: permissions,
		AuthType:    "jwt",
	}, nil
}

// APIKeyProvider provides API key authentication
type APIKeyProvider struct {
	logger  logging.Logger
	apiKeys map[string]APIKeyInfo // In production, this would be a database
}

// APIKeyInfo represents API key information
type APIKeyInfo struct {
	KeyID       string    `json:"key_id"`
	UserID      uuid.UUID `json:"user_id"`
	Username    string    `json:"username"`
	Roles       []string  `json:"roles"`
	Permissions []string  `json:"permissions"`
	IsActive    bool      `json:"is_active"`
	ExpiresAt   time.Time `json:"expires_at"`
	CreatedAt   time.Time `json:"created_at"`
}

// NewAPIKeyProvider creates a new API key provider
func NewAPIKeyProvider(logger logging.Logger) *APIKeyProvider {
	// Initialize with some test API keys
	testKeys := map[string]APIKeyInfo{
		"flext-api-key-REDACTED_LDAP_BIND_PASSWORD-123": {
			KeyID:       "key-REDACTED_LDAP_BIND_PASSWORD-001",
			UserID:      uuid.New(),
			Username:    "api-REDACTED_LDAP_BIND_PASSWORD",
			Roles:       []string{"REDACTED_LDAP_BIND_PASSWORD", "api"},
			Permissions: []string{"*"},
			IsActive:    true,
			ExpiresAt:   time.Now().Add(365 * 24 * time.Hour), // 1 year
			CreatedAt:   time.Now(),
		},
		"flext-api-key-user-456": {
			KeyID:       "key-user-001",
			UserID:      uuid.New(),
			Username:    "api-user",
			Roles:       []string{"user", "api"},
			Permissions: []string{"read", "execute"},
			IsActive:    true,
			ExpiresAt:   time.Now().Add(90 * 24 * time.Hour), // 90 days
			CreatedAt:   time.Now(),
		},
	}

	return &APIKeyProvider{
		logger:  logger.With(logging.F("provider", "api_key")),
		apiKeys: testKeys,
	}
}

// GetProviderType returns the provider type
func (p *APIKeyProvider) GetProviderType() string {
	return "api_key"
}

// Authenticate authenticates using API key
func (p *APIKeyProvider) Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error) {
	if credentials.Token == "" {
		return nil, &value_objects.DomainError{
			Code:        "API_KEY_REQUIRED",
			Message:     "API key is required",
			Description: "A valid API key must be provided",
		}
	}

	userContext, err := p.Validate(ctx, credentials.Token)
	if err != nil {
		return nil, err
	}

	return &AuthResult{
		UserID:      userContext.UserID,
		Username:    userContext.Username,
		Roles:       userContext.Roles,
		Permissions: userContext.Permissions,
	}, nil
}

// Validate validates an API key
func (p *APIKeyProvider) Validate(ctx context.Context, apiKey string) (*UserContext, error) {
	keyInfo, exists := p.apiKeys[apiKey]
	if !exists {
		p.logger.Warn("API key not found",
			logging.F("key_prefix", apiKey[:min(len(apiKey), 10)]+"..."),
		)
		return nil, &value_objects.DomainError{
			Code:        "INVALID_API_KEY",
			Message:     "Invalid API key",
			Description: "The provided API key is not valid",
		}
	}

	if !keyInfo.IsActive {
		return nil, &value_objects.DomainError{
			Code:        "API_KEY_INACTIVE",
			Message:     "API key is inactive",
			Description: "The API key has been deactivated",
		}
	}

	if time.Now().After(keyInfo.ExpiresAt) {
		return nil, &value_objects.DomainError{
			Code:        "API_KEY_EXPIRED",
			Message:     "API key has expired",
			Description: "The API key has passed its expiration date",
		}
	}

	return &UserContext{
		UserID:      keyInfo.UserID,
		Username:    keyInfo.Username,
		Roles:       keyInfo.Roles,
		Permissions: keyInfo.Permissions,
		AuthType:    "api_key",
	}, nil
}

// OAuth2Provider provides OAuth2 authentication
type OAuth2Provider struct {
	config OAuth2Config
	logger logging.Logger
}

// NewOAuth2Provider creates a new OAuth2 provider
func NewOAuth2Provider(config OAuth2Config, logger logging.Logger) (*OAuth2Provider, error) {
	if config.ClientID == "" || config.ClientSecret == "" {
		return nil, &value_objects.DomainError{
			Code:        "OAUTH2_CONFIG_ERROR",
			Message:     "OAuth2 client ID and secret are required",
			Description: "OAuth2 provider requires valid client credentials",
		}
	}

	return &OAuth2Provider{
		config: config,
		logger: logger.With(logging.F("provider", "oauth2")),
	}, nil
}

// GetProviderType returns the provider type
func (p *OAuth2Provider) GetProviderType() string {
	return "oauth2"
}

// Authenticate authenticates using OAuth2 token
func (p *OAuth2Provider) Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error) {
	// This is a simplified implementation
	// In production, you would validate the OAuth2 token with the provider
	if credentials.Token == "" {
		return nil, &value_objects.DomainError{
			Code:        "OAUTH2_TOKEN_REQUIRED",
			Message:     "OAuth2 token is required",
			Description: "A valid OAuth2 access token must be provided",
		}
	}

	// TODO: Implement actual OAuth2 token validation with external provider
	// For now, return a mock user
	return &AuthResult{
		UserID:      uuid.New(),
		Username:    "oauth2_user",
		Email:       "oauth2@example.com",
		Roles:       []string{"user"},
		Permissions: []string{"read"},
	}, nil
}

// Validate validates an OAuth2 token
func (p *OAuth2Provider) Validate(ctx context.Context, token string) (*UserContext, error) {
	// TODO: Implement actual OAuth2 token validation
	// This would involve calling the OAuth2 provider's userinfo endpoint
	
	return &UserContext{
		UserID:   uuid.New(),
		Username: "oauth2_user",
		Email:    "oauth2@example.com",
		Roles:    []string{"user"},
		AuthType: "oauth2",
	}, nil
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}