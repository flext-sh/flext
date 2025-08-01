package auth

import (
	"fmt"
	"strings"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	sharedErrors "github.com/flext/flexcore/internal/shared_kernel/errors"
	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

// UserClaims representa as claims do usuário no JWT
type UserClaims struct {
	UserID   string   `json:"user_id"`
	Username string   `json:"username"`
	Email    string   `json:"email"`
	Roles    []string `json:"roles"`
	jwt.RegisteredClaims
}

// AuthService provê funcionalidades de autenticação
type AuthService struct {
	secretKey []byte
	logger    logging.Logger
}

// NewAuthService cria um novo serviço de autenticação
func NewAuthService(cfg config.Config, logger logging.Logger) *AuthService {
	// Usar chave do ambiente ou uma padrão para desenvolvimento
	secretKey := []byte("flext-secret-key-change-in-production")
	if envKey := cfg.JWT.SecretKey; envKey != "" {
		secretKey = []byte(envKey)
	}

	return &AuthService{
		secretKey: secretKey,
		logger:    logger,
	}
}

// GenerateToken gera um token JWT para um usuário
func (a *AuthService) GenerateToken(userID, username, email string, roles []string) (string, error) {
	claims := UserClaims{
		UserID:   userID,
		Username: username,
		Email:    email,
		Roles:    roles,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
			Issuer:    "flext-api",
			Subject:   userID,
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString(a.secretKey)
	if err != nil {
		a.logger.Error("Failed to generate token", logging.F("error", err.Error()))
		return "", fmt.Errorf("failed to generate token: %w", err)
	}

	return tokenString, nil
}

// ValidateToken valida um token JWT
func (a *AuthService) ValidateToken(tokenString string) (*UserClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &UserClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return a.secretKey, nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to parse token: %w", err)
	}

	if claims, ok := token.Claims.(*UserClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("invalid token")
}

// AuthMiddleware middleware de autenticação
func (a *AuthService) AuthMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if a.isPublicEndpoint(c.Request().URL.Path) {
				return next(c)
			}

			claims, err := a.extractAndValidateToken(c)
			if err != nil {
				return err
			}

			a.setUserContextClaims(c, claims)
			a.logSuccessfulAuthentication(claims)

			return next(c)
		}
	}
}

// extractAndValidateToken extracts and validates the JWT token from the request
func (a *AuthService) extractAndValidateToken(c echo.Context) (*UserClaims, error) {
	authHeader := c.Request().Header.Get("Authorization")
	if authHeader == "" {
		return nil, echo.NewHTTPError(401, sharedErrors.NewUnauthorizedError("Missing authorization header"))
	}

	tokenString := strings.TrimPrefix(authHeader, "Bearer ")
	if tokenString == authHeader {
		return nil, echo.NewHTTPError(401, sharedErrors.NewUnauthorizedError("Invalid authorization header format"))
	}

	claims, err := a.ValidateToken(tokenString)
	if err != nil {
		a.logger.Warn("Token validation failed",
			logging.F("error", err.Error()),
			logging.F("remote_ip", c.RealIP()),
		)
		return nil, echo.NewHTTPError(401, sharedErrors.NewUnauthorizedError("Invalid token"))
	}

	return claims, nil
}

// setUserContextClaims sets user claims in the request context
func (a *AuthService) setUserContextClaims(c echo.Context, claims *UserClaims) {
	c.Set("user_claims", claims)
	c.Set("user_id", claims.UserID)
	c.Set("username", claims.Username)
	c.Set("user_roles", claims.Roles)
}

// logSuccessfulAuthentication logs successful authentication
func (a *AuthService) logSuccessfulAuthentication(claims *UserClaims) {
	a.logger.Info("User authenticated",
		logging.F("user_id", claims.UserID),
		logging.F("username", claims.Username),
		logging.F("roles", claims.Roles),
	)
}

// RoleMiddleware middleware de autorização por role
func (a *AuthService) RoleMiddleware(requiredRoles ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			userRoles, err := a.getUserRolesFromContext(c)
			if err != nil {
				return err
			}

			if !a.hasRequiredRole(userRoles, requiredRoles) {
				return a.handleInsufficientPermissions(c, userRoles, requiredRoles)
			}

			return next(c)
		}
	}
}

// getUserRolesFromContext extracts user roles from the context
func (a *AuthService) getUserRolesFromContext(c echo.Context) ([]string, error) {
	userRoles, ok := c.Get("user_roles").([]string)
	if !ok {
		return nil, echo.NewHTTPError(403, sharedErrors.NewUnauthorizedError("User roles not found"))
	}
	return userRoles, nil
}

// hasRequiredRole checks if user has at least one of the required roles
func (a *AuthService) hasRequiredRole(userRoles, requiredRoles []string) bool {
	for _, requiredRole := range requiredRoles {
		for _, userRole := range userRoles {
			if userRole == requiredRole || userRole == "admin" {
				return true
			}
		}
	}
	return false
}

// handleInsufficientPermissions handles access denied due to insufficient permissions
func (a *AuthService) handleInsufficientPermissions(c echo.Context, userRoles, requiredRoles []string) error {
	a.logger.Warn("Access denied - insufficient permissions",
		logging.F("user_roles", userRoles),
		logging.F("required_roles", requiredRoles),
		logging.F("user_id", c.Get("user_id")),
	)
	return echo.NewHTTPError(403, sharedErrors.NewUnauthorizedError("Insufficient permissions"))
}

// isPublicEndpoint verifica se um endpoint é público
func (a *AuthService) isPublicEndpoint(path string) bool {
	publicEndpoints := []string{
		"/health",
		"/metrics",
		"/",
		"/api/v1/auth/login",
		"/api/v1/auth/register",
		"/swagger",
		"/docs",
	}

	for _, endpoint := range publicEndpoints {
		if strings.HasPrefix(path, endpoint) {
			return true
		}
	}

	return false
}

// GetUserFromContext extrai claims do usuário do contexto
func GetUserFromContext(c echo.Context) (*UserClaims, error) {
	claims, ok := c.Get("user_claims").(*UserClaims)
	if !ok {
		return nil, fmt.Errorf("user claims not found in context")
	}
	return claims, nil
}

// HasRole verifica se usuário tem uma role específica
func HasRole(c echo.Context, role string) bool {
	userRoles, ok := c.Get("user_roles").([]string)
	if !ok {
		return false
	}

	for _, userRole := range userRoles {
		if userRole == role || userRole == "admin" {
			return true
		}
	}

	return false
}

// User representa um usuário do sistema
type User struct {
	ID       string   `json:"id"`
	Username string   `json:"username"`
	Email    string   `json:"email"`
	Roles    []string `json:"roles"`
	Active   bool     `json:"active"`
}

// LoginRequest representa uma requisição de login
type LoginRequest struct {
	Username string `json:"username" validate:"required"`
	Password string `json:"password" validate:"required"`
}

// LoginResponse representa a resposta de login
type LoginResponse struct {
	Token     string    `json:"token"`
	ExpiresAt time.Time `json:"expires_at"`
	User      User      `json:"user"`
}

// RegisterRequest representa uma requisição de registro
type RegisterRequest struct {
	Username string `json:"username" validate:"required,min=3,max=50"`
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required,min=8"`
}
