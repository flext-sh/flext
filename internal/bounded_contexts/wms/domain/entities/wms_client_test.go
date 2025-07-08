package entities

import (
	"context"
	"testing"
	"time"
)

func TestNewWMSClient_Simple(t *testing.T) {
	tests := []struct {
		name     string
		baseURL  string
		username string
		password string
		wantErr  bool
	}{
		{
			name:     "Valid client",
			baseURL:  "https://test-wms.oracle.com",
			username: "testuser",
			password: "testpass",
			wantErr:  false,
		},
		{
			name:     "Empty base URL",
			baseURL:  "",
			username: "testuser",
			password: "testpass",
			wantErr:  true,
		},
		{
			name:     "Empty username",
			baseURL:  "https://test-wms.oracle.com",
			username: "",
			password: "testpass",
			wantErr:  true,
		},
		{
			name:     "Empty password",
			baseURL:  "https://test-wms.oracle.com",
			username: "testuser",
			password: "",
			wantErr:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client, err := NewWMSClient(tt.baseURL, tt.username, tt.password)

			if tt.wantErr {
				if err == nil {
					t.Errorf("NewWMSClient() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("NewWMSClient() unexpected error: %v", err)
				return
			}

			if client == nil {
				t.Errorf("NewWMSClient() returned nil client")
				return
			}

			// Verify client properties
			if client.BaseURL != tt.baseURL {
				t.Errorf("BaseURL = %v, want %v", client.BaseURL, tt.baseURL)
			}

			if client.Username != tt.username {
				t.Errorf("Username = %v, want %v", client.Username, tt.username)
			}

			// Password should be set for authentication
			if client.Password == "" {
				t.Errorf("Password should be set")
			}

			// Verify initial status
			if client.Status != ClientStatusDisconnected {
				t.Errorf("Initial status = %v, want %v", client.Status, ClientStatusDisconnected)
			}

			// Verify default configuration
			if client.Timeout != 30*time.Second {
				t.Errorf("Default Timeout = %v, want %v", client.Timeout, 30*time.Second)
			}

			// Verify events were created
			events := client.GetUncommittedEvents()
			if len(events) == 0 {
				t.Errorf("Expected creation event to be emitted")
			}
		})
	}
}

func TestWMSClient_IsConnected_Simple(t *testing.T) {
	client, err := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	if err != nil {
		t.Fatalf("Failed to create test client: %v", err)
	}

	// Test initial disconnected state
	if client.IsConnected() {
		t.Errorf("Client should initially be disconnected")
	}

	// Test connected state
	client.Status = ClientStatusConnected
	now := time.Now()
	client.LastConnected = &now

	if !client.IsConnected() {
		t.Errorf("Client should be connected")
	}

	// Test error state
	client.Status = ClientStatusError
	if client.IsConnected() {
		t.Errorf("Client with error status should not be connected")
	}
}

func TestWMSClient_GetMetrics_Simple(t *testing.T) {
	client, err := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	if err != nil {
		t.Fatalf("Failed to create test client: %v", err)
	}

	// Test initial metrics
	metrics := client.GetMetrics()
	if metrics.TotalRequests != 0 {
		t.Errorf("Initial TotalRequests = %v, want 0", metrics.TotalRequests)
	}
	if metrics.SuccessfulRequests != 0 {
		t.Errorf("Initial SuccessfulRequests = %v, want 0", metrics.SuccessfulRequests)
	}
	if metrics.FailedRequests != 0 {
		t.Errorf("Initial FailedRequests = %v, want 0", metrics.FailedRequests)
	}

	// Test metrics update
	client.Metrics.TotalRequests = 100
	client.Metrics.SuccessfulRequests = 95
	client.Metrics.FailedRequests = 5
	client.Metrics.AverageResponseTime = 250 * time.Millisecond

	metrics = client.GetMetrics()
	if metrics.TotalRequests != 100 {
		t.Errorf("TotalRequests = %v, want 100", metrics.TotalRequests)
	}
	if metrics.SuccessfulRequests != 95 {
		t.Errorf("SuccessfulRequests = %v, want 95", metrics.SuccessfulRequests)
	}
	if metrics.FailedRequests != 5 {
		t.Errorf("FailedRequests = %v, want 5", metrics.FailedRequests)
	}
	if metrics.AverageResponseTime != 250*time.Millisecond {
		t.Errorf("AverageResponseTime = %v, want %v", metrics.AverageResponseTime, 250*time.Millisecond)
	}
}

// Test context handling
func TestWMSClient_ContextHandling_Simple(t *testing.T) {
	client, err := NewWMSClient("https://test-wms.oracle.com", "testuser", "testpass")
	if err != nil {
		t.Fatalf("Failed to create test client: %v", err)
	}

	// Test with canceled context
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // Cancel immediately

	// This should handle the canceled context gracefully
	err = client.Connect(ctx)
	if err == nil {
		t.Errorf("Connect() should fail with canceled context")
	}

	// Test with timeout context
	ctx, cancel = context.WithTimeout(context.Background(), 1*time.Millisecond)
	defer cancel()

	// Wait for timeout
	time.Sleep(2 * time.Millisecond)

	err = client.Connect(ctx)
	if err == nil {
		t.Errorf("Connect() should fail with timed out context")
	}
}
