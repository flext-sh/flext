package monitoring

// WebSocketBroadcaster defines the interface for WebSocket broadcasting
type WebSocketBroadcaster interface {
	BroadcastToTopic(topic string, msgType string, data interface{})
	GetConnectedClients() map[string]interface{}
}