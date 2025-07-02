package auth

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// WMSAuthenticator handles authentication with Oracle WMS API
type WMSAuthenticator struct {
	baseURL      string
	username     string
	password     string
	apiVersion   string
	httpClient   *http.Client
	
	// Token management
	accessToken    string
	refreshToken   string
	tokenExpiry    time.Time
	tokenMutex     sync.RWMutex
	
	// Authentication type
	authType       AuthType
	
	// Session management
	sessionID      string
	sessionExpiry  time.Time
	
	// Configuration
	config         AuthConfig
}

// AuthType defines the authentication method
type AuthType string

const (
	AuthTypeBasic        AuthType = "basic"
	AuthTypeBearer       AuthType = "bearer"
	AuthTypeOAuth2       AuthType = "oauth2"
	AuthTypeSession      AuthType = "session"
	AuthTypeAPIKey       AuthType = "apikey"
	AuthTypeCustom       AuthType = "custom"
)

// AuthConfig configures authentication behavior
type AuthConfig struct {
	// Auth method configuration
	AuthType           AuthType      `json:"auth_type"`
	TokenEndpoint      string        `json:"token_endpoint"`
	RefreshEndpoint    string        `json:"refresh_endpoint"`
	SessionEndpoint    string        `json:"session_endpoint"`
	
	// OAuth2 specific
	ClientID           string        `json:"client_id"`
	ClientSecret       string        `json:"client_secret"`
	Scope              string        `json:"scope"`
	
	// API Key specific
	APIKey             string        `json:"api_key"`
	APIKeyHeader       string        `json:"api_key_header"`
	APIKeyParam        string        `json:"api_key_param"`
	
	// Token management
	TokenRefreshBuffer time.Duration `json:"token_refresh_buffer"`
	MaxRetries         int           `json:"max_retries"`
	RetryDelay         time.Duration `json:"retry_delay"`
	
	// TLS configuration
	SkipTLSVerify      bool          `json:"skip_tls_verify"`
	CertFile           string        `json:"cert_file"`
	KeyFile            string        `json:"key_file"`
	CAFile             string        `json:"ca_file"`
	
	// Custom headers
	CustomHeaders      map[string]string `json:"custom_headers"`
	
	// Timeout settings
	ConnectTimeout     time.Duration `json:"connect_timeout"`
	RequestTimeout     time.Duration `json:"request_timeout"`
}

// AuthResponse represents authentication response from Oracle WMS
type AuthResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	Scope        string `json:"scope"`
	
	// Session-based auth
	SessionID    string `json:"session_id"`
	SessionToken string `json:"session_token"`
	
	// Custom fields
	Custom       map[string]interface{} `json:"custom,omitempty"`
}

// NewWMSAuthenticator creates a new authenticator
func NewWMSAuthenticator(baseURL, username, password string, config AuthConfig) *WMSAuthenticator {
	// Default configuration
	if config.AuthType == "" {
		config.AuthType = AuthTypeBasic
	}
	if config.TokenRefreshBuffer == 0 {
		config.TokenRefreshBuffer = 5 * time.Minute
	}
	if config.MaxRetries == 0 {
		config.MaxRetries = 3
	}
	if config.RetryDelay == 0 {
		config.RetryDelay = 1 * time.Second
	}
	if config.ConnectTimeout == 0 {
		config.ConnectTimeout = 30 * time.Second
	}
	if config.RequestTimeout == 0 {
		config.RequestTimeout = 30 * time.Second
	}
	if config.CustomHeaders == nil {
		config.CustomHeaders = make(map[string]string)
	}

	// Create HTTP client with TLS configuration
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: config.SkipTLSVerify,
		},
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     90 * time.Second,
	}

	httpClient := &http.Client{
		Transport: transport,
		Timeout:   config.RequestTimeout,
	}

	return &WMSAuthenticator{
		baseURL:    strings.TrimRight(baseURL, "/"),
		username:   username,
		password:   password,
		apiVersion: "v10", // Default Oracle WMS API version
		httpClient: httpClient,
		config:     config,
	}
}

// Authenticate performs initial authentication
func (a *WMSAuthenticator) Authenticate(ctx context.Context) error {
	a.tokenMutex.Lock()
	defer a.tokenMutex.Unlock()

	switch a.config.AuthType {
	case AuthTypeBasic:
		return a.authenticateBasic(ctx)
	case AuthTypeBearer, AuthTypeOAuth2:
		return a.authenticateOAuth2(ctx)
	case AuthTypeSession:
		return a.authenticateSession(ctx)
	case AuthTypeAPIKey:
		return a.authenticateAPIKey(ctx)
	case AuthTypeCustom:
		return a.authenticateCustom(ctx)
	default:
		return fmt.Errorf("unsupported authentication type: %s", a.config.AuthType)
	}
}

// GetAuthHeaders returns headers for authenticated requests
func (a *WMSAuthenticator) GetAuthHeaders() (map[string]string, error) {
	a.tokenMutex.RLock()
	defer a.tokenMutex.RUnlock()

	headers := make(map[string]string)

	// Add custom headers
	for key, value := range a.config.CustomHeaders {
		headers[key] = value
	}

	switch a.config.AuthType {
	case AuthTypeBasic:
		auth := base64.StdEncoding.EncodeToString([]byte(a.username + ":" + a.password))
		headers["Authorization"] = "Basic " + auth

	case AuthTypeBearer, AuthTypeOAuth2:
		if a.accessToken == "" {
			return nil, fmt.Errorf("no access token available")
		}
		if a.isTokenExpired() {
			return nil, fmt.Errorf("access token expired")
		}
		headers["Authorization"] = "Bearer " + a.accessToken

	case AuthTypeSession:
		if a.sessionID == "" {
			return nil, fmt.Errorf("no session ID available")
		}
		if a.isSessionExpired() {
			return nil, fmt.Errorf("session expired")
		}
		headers["X-Session-ID"] = a.sessionID

	case AuthTypeAPIKey:
		if a.config.APIKey == "" {
			return nil, fmt.Errorf("no API key configured")
		}
		if a.config.APIKeyHeader != "" {
			headers[a.config.APIKeyHeader] = a.config.APIKey
		}
	}

	return headers, nil
}

// RefreshToken refreshes the authentication token if needed
func (a *WMSAuthenticator) RefreshToken(ctx context.Context) error {
	a.tokenMutex.Lock()
	defer a.tokenMutex.Unlock()

	switch a.config.AuthType {
	case AuthTypeBearer, AuthTypeOAuth2:
		if !a.shouldRefreshToken() {
			return nil // Token still valid
		}
		return a.refreshOAuth2Token(ctx)

	case AuthTypeSession:
		if !a.shouldRefreshSession() {
			return nil // Session still valid
		}
		return a.refreshSession(ctx)

	default:
		return nil // No refresh needed for other auth types
	}
}

// IsAuthenticated checks if current authentication is valid
func (a *WMSAuthenticator) IsAuthenticated() bool {
	a.tokenMutex.RLock()
	defer a.tokenMutex.RUnlock()

	switch a.config.AuthType {
	case AuthTypeBasic, AuthTypeAPIKey:
		return true // Always valid

	case AuthTypeBearer, AuthTypeOAuth2:
		return a.accessToken != "" && !a.isTokenExpired()

	case AuthTypeSession:
		return a.sessionID != "" && !a.isSessionExpired()

	default:
		return false
	}
}

// Private authentication methods

func (a *WMSAuthenticator) authenticateBasic(ctx context.Context) error {
	// Basic auth doesn't require initial authentication
	// Credentials are sent with each request
	return nil
}

func (a *WMSAuthenticator) authenticateOAuth2(ctx context.Context) error {
	tokenURL := a.config.TokenEndpoint
	if tokenURL == "" {
		tokenURL = a.baseURL + "/oauth/token"
	}

	data := url.Values{}
	data.Set("grant_type", "client_credentials")
	data.Set("username", a.username)
	data.Set("password", a.password)
	
	if a.config.ClientID != "" {
		data.Set("client_id", a.config.ClientID)
	}
	if a.config.ClientSecret != "" {
		data.Set("client_secret", a.config.ClientSecret)
	}
	if a.config.Scope != "" {
		data.Set("scope", a.config.Scope)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", tokenURL, strings.NewReader(data.Encode()))
	if err != nil {
		return fmt.Errorf("failed to create token request: %w", err)
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")

	// Add custom headers
	for key, value := range a.config.CustomHeaders {
		req.Header.Set(key, value)
	}

	resp, err := a.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("token request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("token request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var authResp AuthResponse
	if err := json.NewDecoder(resp.Body).Decode(&authResp); err != nil {
		return fmt.Errorf("failed to decode token response: %w", err)
	}

	a.accessToken = authResp.AccessToken
	a.refreshToken = authResp.RefreshToken
	a.tokenExpiry = time.Now().Add(time.Duration(authResp.ExpiresIn) * time.Second)

	return nil
}

func (a *WMSAuthenticator) authenticateSession(ctx context.Context) error {
	sessionURL := a.config.SessionEndpoint
	if sessionURL == "" {
		sessionURL = a.baseURL + "/wms/lgfapi/" + a.apiVersion + "/session"
	}

	loginData := map[string]string{
		"username": a.username,
		"password": a.password,
	}

	jsonData, err := json.Marshal(loginData)
	if err != nil {
		return fmt.Errorf("failed to marshal login data: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", sessionURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to create session request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	// Add custom headers
	for key, value := range a.config.CustomHeaders {
		req.Header.Set(key, value)
	}

	resp, err := a.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("session request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("session request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var authResp AuthResponse
	if err := json.NewDecoder(resp.Body).Decode(&authResp); err != nil {
		return fmt.Errorf("failed to decode session response: %w", err)
	}

	a.sessionID = authResp.SessionID
	if a.sessionID == "" {
		a.sessionID = authResp.SessionToken
	}
	
	// Oracle WMS sessions typically expire after 24 hours
	a.sessionExpiry = time.Now().Add(24 * time.Hour)

	return nil
}

func (a *WMSAuthenticator) authenticateAPIKey(ctx context.Context) error {
	// API Key auth doesn't require initial authentication
	// Key is sent with each request
	if a.config.APIKey == "" {
		return fmt.Errorf("API key not configured")
	}
	return nil
}

func (a *WMSAuthenticator) authenticateCustom(ctx context.Context) error {
	// Custom authentication logic would go here
	// This is a placeholder for custom authentication implementations
	return fmt.Errorf("custom authentication not implemented")
}

func (a *WMSAuthenticator) refreshOAuth2Token(ctx context.Context) error {
	if a.refreshToken == "" {
		// No refresh token, need to re-authenticate
		return a.authenticateOAuth2(ctx)
	}

	refreshURL := a.config.RefreshEndpoint
	if refreshURL == "" {
		refreshURL = a.baseURL + "/oauth/token"
	}

	data := url.Values{}
	data.Set("grant_type", "refresh_token")
	data.Set("refresh_token", a.refreshToken)
	
	if a.config.ClientID != "" {
		data.Set("client_id", a.config.ClientID)
	}
	if a.config.ClientSecret != "" {
		data.Set("client_secret", a.config.ClientSecret)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", refreshURL, strings.NewReader(data.Encode()))
	if err != nil {
		return fmt.Errorf("failed to create refresh request: %w", err)
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")

	resp, err := a.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("refresh request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		// Refresh failed, try re-authentication
		return a.authenticateOAuth2(ctx)
	}

	var authResp AuthResponse
	if err := json.NewDecoder(resp.Body).Decode(&authResp); err != nil {
		return fmt.Errorf("failed to decode refresh response: %w", err)
	}

	a.accessToken = authResp.AccessToken
	if authResp.RefreshToken != "" {
		a.refreshToken = authResp.RefreshToken
	}
	a.tokenExpiry = time.Now().Add(time.Duration(authResp.ExpiresIn) * time.Second)

	return nil
}

func (a *WMSAuthenticator) refreshSession(ctx context.Context) error {
	// Session refresh logic - might involve ping or extend session endpoints
	sessionURL := a.baseURL + "/wms/lgfapi/" + a.apiVersion + "/session/" + a.sessionID + "/extend"

	req, err := http.NewRequestWithContext(ctx, "POST", sessionURL, nil)
	if err != nil {
		return fmt.Errorf("failed to create session refresh request: %w", err)
	}

	req.Header.Set("X-Session-ID", a.sessionID)
	req.Header.Set("Accept", "application/json")

	resp, err := a.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("session refresh failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		// Session refresh failed, need to re-authenticate
		return a.authenticateSession(ctx)
	}

	// Extend session expiry
	a.sessionExpiry = time.Now().Add(24 * time.Hour)

	return nil
}

// Helper methods

func (a *WMSAuthenticator) isTokenExpired() bool {
	return time.Now().After(a.tokenExpiry.Add(-a.config.TokenRefreshBuffer))
}

func (a *WMSAuthenticator) isSessionExpired() bool {
	return time.Now().After(a.sessionExpiry.Add(-a.config.TokenRefreshBuffer))
}

func (a *WMSAuthenticator) shouldRefreshToken() bool {
	return a.accessToken != "" && a.isTokenExpired()
}

func (a *WMSAuthenticator) shouldRefreshSession() bool {
	return a.sessionID != "" && a.isSessionExpired()
}

// MakeAuthenticatedRequest makes an HTTP request with authentication
func (a *WMSAuthenticator) MakeAuthenticatedRequest(ctx context.Context, method, url string, body io.Reader) (*http.Response, error) {
	// Refresh token if needed
	if err := a.RefreshToken(ctx); err != nil {
		return nil, fmt.Errorf("failed to refresh token: %w", err)
	}

	// Create request
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Add authentication headers
	headers, err := a.GetAuthHeaders()
	if err != nil {
		return nil, fmt.Errorf("failed to get auth headers: %w", err)
	}

	for key, value := range headers {
		req.Header.Set(key, value)
	}

	// Set default headers
	if req.Header.Get("Accept") == "" {
		req.Header.Set("Accept", "application/json")
	}
	if req.Header.Get("User-Agent") == "" {
		req.Header.Set("User-Agent", "flext-wms-client/1.0")
	}

	// Add API key as query parameter if configured
	if a.config.AuthType == AuthTypeAPIKey && a.config.APIKeyParam != "" {
		q := req.URL.Query()
		q.Set(a.config.APIKeyParam, a.config.APIKey)
		req.URL.RawQuery = q.Encode()
	}

	// Execute request with retries
	var resp *http.Response
	var lastErr error

	for attempt := 0; attempt <= a.config.MaxRetries; attempt++ {
		resp, lastErr = a.httpClient.Do(req)
		
		if lastErr == nil {
			// Check for authentication errors
			if resp.StatusCode == http.StatusUnauthorized || resp.StatusCode == http.StatusForbidden {
				resp.Body.Close()
				
				// Try to re-authenticate on first auth error
				if attempt == 0 {
					if authErr := a.Authenticate(ctx); authErr != nil {
						lastErr = fmt.Errorf("re-authentication failed: %w", authErr)
						continue
					}
					
					// Update headers with new auth
					newHeaders, headerErr := a.GetAuthHeaders()
					if headerErr != nil {
						lastErr = fmt.Errorf("failed to get updated auth headers: %w", headerErr)
						continue
					}
					
					for key, value := range newHeaders {
						req.Header.Set(key, value)
					}
					continue
				}
				
				lastErr = fmt.Errorf("authentication failed with status %d", resp.StatusCode)
				continue
			}
			
			// Success or non-auth error
			return resp, nil
		}

		// Wait before retry
		if attempt < a.config.MaxRetries {
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(a.config.RetryDelay * time.Duration(attempt+1)):
				// Continue to next attempt
			}
		}
	}

	return nil, fmt.Errorf("request failed after %d attempts: %w", a.config.MaxRetries+1, lastErr)
}

// Logout terminates the current session
func (a *WMSAuthenticator) Logout(ctx context.Context) error {
	a.tokenMutex.Lock()
	defer a.tokenMutex.Unlock()

	switch a.config.AuthType {
	case AuthTypeSession:
		if a.sessionID != "" {
			logoutURL := a.baseURL + "/wms/lgfapi/" + a.apiVersion + "/session/" + a.sessionID
			
			req, err := http.NewRequestWithContext(ctx, "DELETE", logoutURL, nil)
			if err != nil {
				return fmt.Errorf("failed to create logout request: %w", err)
			}
			
			req.Header.Set("X-Session-ID", a.sessionID)
			
			resp, err := a.httpClient.Do(req)
			if err != nil {
				return fmt.Errorf("logout request failed: %w", err)
			}
			defer resp.Body.Close()
		}
	}

	// Clear stored credentials
	a.accessToken = ""
	a.refreshToken = ""
	a.sessionID = ""
	a.tokenExpiry = time.Time{}
	a.sessionExpiry = time.Time{}

	return nil
}