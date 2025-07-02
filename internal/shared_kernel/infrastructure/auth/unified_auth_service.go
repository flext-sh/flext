package auth

import (
	"context"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// UnifiedAuthService provides centralized authentication and authorization
type UnifiedAuthService struct {
	jwtSecret     []byte
	tokenExpiry   time.Duration
	refreshExpiry time.Duration
	logger        logging.Logger
	providers     map[string]AuthProvider
}

// AuthProvider interface for different authentication mechanisms
type AuthProvider interface {
	Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error)
	GetProviderType() string
	Validate(ctx context.Context, token string) (*UserContext, error)
}

// Credentials represents authentication credentials
type Credentials struct {
	Type     string                 `json:"type"`     // jwt, oauth2, basic, api_key
	Username string                 `json:"username,omitempty"`
	Password string                 `json:"password,omitempty"`
	Token    string                 `json:"token,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// AuthResult represents authentication result
type AuthResult struct {
	UserID       uuid.UUID `json:"user_id"`
	Username     string    `json:"username"`
	Email        string    `json:"email"`
	Roles        []string  `json:"roles"`
	Permissions  []string  `json:"permissions"`
	AccessToken  string    `json:"access_token"`
	RefreshToken string    `json:"refresh_token"`
	ExpiresAt    time.Time `json:"expires_at"`
}

// UserContext represents authenticated user context
type UserContext struct {
	UserID      uuid.UUID `json:"user_id"`
	Username    string    `json:"username"`
	Email       string    `json:"email"`
	Roles       []string  `json:"roles"`
	Permissions []string  `json:"permissions"`
	SessionID   string    `json:"session_id"`
	AuthType    string    `json:"auth_type"`
}

// UnifiedAuthConfig configuration for the unified auth service
type UnifiedAuthConfig struct {
	JWTSecret           string        `json:"jwt_secret"`
	TokenExpiry         time.Duration `json:"token_expiry"`
	RefreshTokenExpiry  time.Duration `json:"refresh_token_expiry"`
	EnableOAuth2        bool          `json:"enable_oauth2"`
	EnableBasicAuth     bool          `json:"enable_basic_auth"`
	EnableAPIKeyAuth    bool          `json:"enable_api_key_auth"`
	OAuth2Config        OAuth2Config  `json:"oauth2_config,omitempty"`
}

// OAuth2Config OAuth2 provider configuration
type OAuth2Config struct {
	ClientID     string `json:"client_id"`
	ClientSecret string `json:"client_secret"`
	RedirectURL  string `json:"redirect_url"`
	AuthURL      string `json:"auth_url"`
	TokenURL     string `json:"token_url"`
	Scopes       []string `json:"scopes"`
}

// NewUnifiedAuthService creates a new unified authentication service
func NewUnifiedAuthService(config UnifiedAuthConfig, logger logging.Logger) (*UnifiedAuthService, error) {
	if config.JWTSecret == "" {
		return nil, &value_objects.DomainError{
			Code:        "AUTH_CONFIG_ERROR",
			Message:     "JWT secret is required",
			Description: "JWT secret must be provided for token signing",
		}
	}

	service := &UnifiedAuthService{
		jwtSecret:     []byte(config.JWTSecret),
		tokenExpiry:   config.TokenExpiry,
		refreshExpiry: config.RefreshTokenExpiry,
		logger:        logger.With(logging.F("component", "unified_auth")),
		providers:     make(map[string]AuthProvider),
	}

	// Set default expiry times if not provided
	if service.tokenExpiry == 0 {
		service.tokenExpiry = 24 * time.Hour
	}
	if service.refreshExpiry == 0 {
		service.refreshExpiry = 7 * 24 * time.Hour
	}

	// Initialize built-in providers
	if config.EnableBasicAuth {
		service.RegisterProvider(NewBasicAuthProvider(logger))
	}

	if config.EnableOAuth2 {
		oauth2Provider, err := NewOAuth2Provider(config.OAuth2Config, logger)
		if err != nil {
			return nil, fmt.Errorf("failed to initialize OAuth2 provider: %w", err)
		}
		service.RegisterProvider(oauth2Provider)
	}

	if config.EnableAPIKeyAuth {
		service.RegisterProvider(NewAPIKeyProvider(logger))
	}

	// Always register JWT provider for token validation
	service.RegisterProvider(NewJWTProvider(config.JWTSecret, logger))

	service.logger.Info("Unified auth service initialized",
		logging.F("providers", len(service.providers)),
		logging.F("token_expiry", service.tokenExpiry),
		logging.F("refresh_expiry", service.refreshExpiry),
	)

	return service, nil
}

// RegisterProvider registers an authentication provider
func (s *UnifiedAuthService) RegisterProvider(provider AuthProvider) {
	s.providers[provider.GetProviderType()] = provider
	s.logger.Info("Auth provider registered",
		logging.F("provider_type", provider.GetProviderType()),
	)
}

// Authenticate authenticates user using the specified provider
func (s *UnifiedAuthService) Authenticate(ctx context.Context, credentials Credentials) (*AuthResult, error) {
	provider, exists := s.providers[credentials.Type]
	if !exists {
		return nil, &value_objects.DomainError{
			Code:        "AUTH_PROVIDER_NOT_FOUND",
			Message:     fmt.Sprintf("Authentication provider '%s' not found", credentials.Type),
			Description: "The requested authentication provider is not registered",
		}
	}

	result, err := provider.Authenticate(ctx, credentials)
	if err != nil {
		s.logger.Warn("Authentication failed",
			logging.F("provider", credentials.Type),
			logging.F("username", credentials.Username),
			logging.F("error", err.Error()),
		)
		return nil, err
	}

	// Generate JWT tokens for successful authentication
	accessToken, err := s.generateAccessToken(result)
	if err != nil {
		return nil, fmt.Errorf("failed to generate access token: %w", err)
	}

	refreshToken, err := s.generateRefreshToken(result.UserID)
	if err != nil {
		return nil, fmt.Errorf("failed to generate refresh token: %w", err)
	}

	result.AccessToken = accessToken
	result.RefreshToken = refreshToken
	result.ExpiresAt = time.Now().Add(s.tokenExpiry)

	s.logger.Info("User authenticated successfully",
		logging.F("user_id", result.UserID),
		logging.F("username", result.Username),
		logging.F("provider", credentials.Type),
		logging.F("roles", result.Roles),
	)

	return result, nil
}

// ValidateToken validates an authentication token
func (s *UnifiedAuthService) ValidateToken(ctx context.Context, token string) (*UserContext, error) {
	// First try JWT validation
	if jwtProvider, exists := s.providers["jwt"]; exists {
		userContext, err := jwtProvider.Validate(ctx, token)
		if err == nil {
			return userContext, nil
		}
	}

	// Try other providers if JWT fails
	for providerType, provider := range s.providers {
		if providerType == "jwt" {
			continue // Already tried
		}

		userContext, err := provider.Validate(ctx, token)
		if err == nil {
			s.logger.Debug("Token validated by provider",
				logging.F("provider", providerType),
				logging.F("user_id", userContext.UserID),
			)
			return userContext, nil
		}
	}

	return nil, &value_objects.DomainError{
		Code:        "TOKEN_VALIDATION_FAILED",
		Message:     "Token validation failed",
		Description: "The provided token is invalid or expired",
	}
}

// RefreshToken refreshes an access token using a refresh token
func (s *UnifiedAuthService) RefreshToken(ctx context.Context, refreshToken string) (*AuthResult, error) {
	// Parse refresh token to get user ID
	token, err := jwt.Parse(refreshToken, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return s.jwtSecret, nil
	})

	if err != nil || !token.Valid {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_REFRESH_TOKEN",
			Message:     "Invalid refresh token",
			Description: "The provided refresh token is invalid or expired",
		}
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TOKEN_CLAIMS",
			Message:     "Invalid token claims",
			Description: "Unable to parse token claims",
		}
	}

	userIDStr, ok := claims["sub"].(string)
	if !ok {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_USER_ID",
			Message:     "Invalid user ID in token",
			Description: "User ID not found in token claims",
		}
	}

	userID, err := uuid.Parse(userIDStr)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_USER_ID_FORMAT",
			Message:     "Invalid user ID format",
			Description: "User ID is not a valid UUID",
		}
	}

	// TODO: Fetch user details from user repository
	// For now, create a basic result with the user ID
	result := &AuthResult{
		UserID:   userID,
		Username: claims["username"].(string),
		Roles:    []string{"user"}, // TODO: Fetch from user repository
	}

	// Generate new access token
	accessToken, err := s.generateAccessToken(result)
	if err != nil {
		return nil, fmt.Errorf("failed to generate new access token: %w", err)
	}

	result.AccessToken = accessToken
	result.ExpiresAt = time.Now().Add(s.tokenExpiry)

	s.logger.Info("Token refreshed successfully",
		logging.F("user_id", userID),
		logging.F("username", result.Username),
	)

	return result, nil
}

// generateAccessToken generates a JWT access token
func (s *UnifiedAuthService) generateAccessToken(authResult *AuthResult) (string, error) {
	claims := jwt.MapClaims{
		"sub":         authResult.UserID.String(),
		"username":    authResult.Username,
		"email":       authResult.Email,
		"roles":       authResult.Roles,
		"permissions": authResult.Permissions,
		"iat":         time.Now().Unix(),
		"exp":         time.Now().Add(s.tokenExpiry).Unix(),
		"type":        "access",
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.jwtSecret)
}

// generateRefreshToken generates a JWT refresh token
func (s *UnifiedAuthService) generateRefreshToken(userID uuid.UUID) (string, error) {
	claims := jwt.MapClaims{
		"sub":  userID.String(),
		"iat":  time.Now().Unix(),
		"exp":  time.Now().Add(s.refreshExpiry).Unix(),
		"type": "refresh",
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.jwtSecret)
}

// GetUserContext extracts user context from authenticated request
func (s *UnifiedAuthService) GetUserContext(ctx context.Context) (*UserContext, error) {
	// Try to get user context from context
	if userContext, ok := ctx.Value("user_context").(*UserContext); ok {
		return userContext, nil
	}

	return nil, &value_objects.DomainError{
		Code:        "USER_CONTEXT_NOT_FOUND",
		Message:     "User context not found",
		Description: "No authenticated user context found in request",
	}
}

// HasRole checks if the authenticated user has a specific role
func (s *UnifiedAuthService) HasRole(ctx context.Context, role string) bool {
	userContext, err := s.GetUserContext(ctx)
	if err != nil {
		return false
	}

	for _, userRole := range userContext.Roles {
		if userRole == role || userRole == "REDACTED_LDAP_BIND_PASSWORD" {
			return true
		}
	}

	return false
}

// HasPermission checks if the authenticated user has a specific permission
func (s *UnifiedAuthService) HasPermission(ctx context.Context, permission string) bool {
	userContext, err := s.GetUserContext(ctx)
	if err != nil {
		return false
	}

	for _, userPermission := range userContext.Permissions {
		if userPermission == permission {
			return true
		}
	}

	// Admin role has all permissions
	return s.HasRole(ctx, "REDACTED_LDAP_BIND_PASSWORD")
}