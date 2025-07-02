package server

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/labstack/echo/v4"
)

// WebSocketManager gerencia conexões WebSocket
type WebSocketManager struct {
	clients    map[string]*WebSocketClient
	register   chan *WebSocketClient
	unregister chan *WebSocketClient
	broadcast  chan []byte
	mu         sync.RWMutex
	logger     logging.Logger
}

// WebSocketClient representa um cliente conectado
type WebSocketClient struct {
	ID      string
	UserID  string
	Conn    *websocket.Conn
	Send    chan []byte
	Manager *WebSocketManager
	Topics  map[string]bool // subscribed topics
}

// WebSocketMessage representa uma mensagem WebSocket
type WebSocketMessage struct {
	Type      string      `json:"type"`
	Topic     string      `json:"topic"`
	Data      interface{} `json:"data"`
	Timestamp time.Time   `json:"timestamp"`
	MessageID string      `json:"message_id"`
}

// NewWebSocketManager cria um novo gerenciador WebSocket
func NewWebSocketManager(logger logging.Logger) *WebSocketManager {
	return &WebSocketManager{
		clients:    make(map[string]*WebSocketClient),
		register:   make(chan *WebSocketClient),
		unregister: make(chan *WebSocketClient),
		broadcast:  make(chan []byte),
		logger:     logger,
	}
}

// Run inicia o loop principal do WebSocket manager
func (m *WebSocketManager) Run(ctx context.Context) {
	m.logger.Info("Starting WebSocket manager")

	for {
		select {
		case client := <-m.register:
			m.mu.Lock()
			m.clients[client.ID] = client
			m.mu.Unlock()

			m.logger.Info("Client connected",
				logging.F("client_id", client.ID),
				logging.F("user_id", client.UserID),
			)

			// Send welcome message
			welcomeMsg := WebSocketMessage{
				Type:      "welcome",
				Topic:     "system",
				Data:      map[string]string{"message": "Connected to FLEXT WebSocket"},
				Timestamp: time.Now(),
				MessageID: uuid.New().String(),
			}
			client.SendMessage(welcomeMsg)

		case client := <-m.unregister:
			m.mu.Lock()
			if _, ok := m.clients[client.ID]; ok {
				delete(m.clients, client.ID)
				close(client.Send)
			}
			m.mu.Unlock()

			m.logger.Info("Client disconnected",
				logging.F("client_id", client.ID),
				logging.F("user_id", client.UserID),
			)

		case message := <-m.broadcast:
			m.mu.RLock()
			for _, client := range m.clients {
				select {
				case client.Send <- message:
				default:
					close(client.Send)
					delete(m.clients, client.ID)
				}
			}
			m.mu.RUnlock()

		case <-ctx.Done():
			m.logger.Info("Shutting down WebSocket manager")
			return
		}
	}
}

// HandleWebSocket lida com conexões WebSocket
func (m *WebSocketManager) HandleWebSocket(c echo.Context) error {
	userID := c.Get("user_id")
	if userID == nil {
		userID = "anonymous"
	}

	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow all origins in development
		},
	}

	conn, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
	if err != nil {
		m.logger.Error("WebSocket upgrade failed", logging.F("error", err.Error()))
		return err
	}

	client := &WebSocketClient{
		ID:      uuid.New().String(),
		UserID:  fmt.Sprintf("%v", userID),
		Conn:    conn,
		Send:    make(chan []byte, 256),
		Manager: m,
		Topics:  make(map[string]bool),
	}

	client.Manager.register <- client

	// Start client handlers
	go client.writePump()
	go client.readPump()

	return nil
}

// SendMessage envia uma mensagem para um cliente específico
func (c *WebSocketClient) SendMessage(msg WebSocketMessage) {
	data, err := json.Marshal(msg)
	if err != nil {
		c.Manager.logger.Error("Failed to marshal WebSocket message",
			logging.F("error", err.Error()))
		return
	}

	select {
	case c.Send <- data:
	default:
		close(c.Send)
	}
}

// readPump trata mensagens recebidas do cliente
func (c *WebSocketClient) readPump() {
	defer func() {
		c.Manager.unregister <- c
		c.Conn.Close()
	}()

	c.Conn.SetReadLimit(512)
	c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.Conn.SetPongHandler(func(string) error {
		c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		_, messageBytes, err := c.Conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				c.Manager.logger.Error("WebSocket error", logging.F("error", err.Error()))
			}
			break
		}

		var msg WebSocketMessage
		if err := json.Unmarshal(messageBytes, &msg); err != nil {
			c.Manager.logger.Error("Failed to unmarshal WebSocket message",
				logging.F("error", err.Error()))
			continue
		}

		// Handle different message types
		c.handleMessage(msg)
	}
}

// writePump envia mensagens para o cliente
func (c *WebSocketClient) writePump() {
	ticker := time.NewTicker(54 * time.Second)
	defer func() {
		ticker.Stop()
		c.Conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.Send:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			if err := c.Conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}

		case <-ticker.C:
			c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// handleMessage processa mensagens recebidas do cliente
func (c *WebSocketClient) handleMessage(msg WebSocketMessage) {
	switch msg.Type {
	case "subscribe":
		topic := fmt.Sprintf("%v", msg.Data)
		c.Topics[topic] = true
		c.Manager.logger.Info("Client subscribed to topic",
			logging.F("client_id", c.ID),
			logging.F("topic", topic),
		)

		// Send confirmation
		confirmMsg := WebSocketMessage{
			Type:      "subscribed",
			Topic:     topic,
			Data:      map[string]string{"message": fmt.Sprintf("Subscribed to %s", topic)},
			Timestamp: time.Now(),
			MessageID: uuid.New().String(),
		}
		c.SendMessage(confirmMsg)

	case "unsubscribe":
		topic := fmt.Sprintf("%v", msg.Data)
		delete(c.Topics, topic)
		c.Manager.logger.Info("Client unsubscribed from topic",
			logging.F("client_id", c.ID),
			logging.F("topic", topic),
		)

	case "ping":
		pongMsg := WebSocketMessage{
			Type:      "pong",
			Topic:     "system",
			Data:      map[string]string{"message": "pong"},
			Timestamp: time.Now(),
			MessageID: uuid.New().String(),
		}
		c.SendMessage(pongMsg)
	}
}

// BroadcastToTopic envia uma mensagem para todos os clientes inscritos em um tópico
func (m *WebSocketManager) BroadcastToTopic(topic string, msgType string, data interface{}) {
	msg := WebSocketMessage{
		Type:      msgType,
		Topic:     topic,
		Data:      data,
		Timestamp: time.Now(),
		MessageID: uuid.New().String(),
	}

	msgBytes, err := json.Marshal(msg)
	if err != nil {
		m.logger.Error("Failed to marshal broadcast message",
			logging.F("error", err.Error()))
		return
	}

	m.mu.RLock()
	for _, client := range m.clients {
		if client.Topics[topic] {
			select {
			case client.Send <- msgBytes:
			default:
				close(client.Send)
				delete(m.clients, client.ID)
			}
		}
	}
	m.mu.RUnlock()
}

// NotifyDomainEvent envia eventos de domínio via WebSocket
func (m *WebSocketManager) NotifyDomainEvent(event domain.DomainEvent) {
	eventData := map[string]interface{}{
		"event_type":   event.GetEventType(),
		"aggregate_id": event.GetAggregateID(),
		"occurred_at":  event.GetEventTime(),
		"version":      event.GetVersion(),
		"data":         event.GetData(),
	}

	// Broadcast to relevant topics based on event type
	topics := []string{"events", "all"}

	// Add specific topics based on event type
	switch event.GetEventType() {
	case "PipelineCreated", "PipelineUpdated", "PipelineDeleted", "PipelineExecuted":
		topics = append(topics, "pipelines")
	case "PluginRegistered", "PluginUpdated", "PluginDeleted":
		topics = append(topics, "plugins")
	}

	for _, topic := range topics {
		m.BroadcastToTopic(topic, "domain_event", eventData)
	}
}

// GetConnectedClients retorna estatísticas dos clientes conectados
func (m *WebSocketManager) GetConnectedClients() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()

	stats := map[string]interface{}{
		"total_clients": len(m.clients),
		"clients":       make([]map[string]interface{}, 0),
	}

	for _, client := range m.clients {
		clientInfo := map[string]interface{}{
			"id":      client.ID,
			"user_id": client.UserID,
			"topics":  client.Topics,
		}
		stats["clients"] = append(stats["clients"].([]map[string]interface{}), clientInfo)
	}

	return stats
}
