package logging

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
)

// LogLevel define níveis de log
type LogLevel string

const (
	DEBUG LogLevel = "debug"
	INFO  LogLevel = "info"
	WARN  LogLevel = "warn"
	ERROR LogLevel = "error"
)

// Logger interface for structured logging
type Logger interface {
	Debug(msg string, fields ...Field)
	Info(msg string, fields ...Field)
	Warn(msg string, fields ...Field)
	Error(msg string, fields ...Field)
	With(fields ...Field) Logger
}

// Field representa um campo de log estruturado
type Field struct {
	Key   string      `json:"key"`
	Value interface{} `json:"value"`
}

// F helper function para criar campos
func F(key string, value interface{}) Field {
	return Field{Key: key, Value: value}
}

// StructuredLogger implementa logging estruturado
type StructuredLogger struct {
	config   config.LoggingConfig
	fields   []Field
	minLevel LogLevel
}

// LogEntry representa uma entrada de log
type LogEntry struct {
	Timestamp time.Time              `json:"timestamp"`
	Level     LogLevel               `json:"level"`
	Message   string                 `json:"message"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
}

// NewLogger cria um novo logger estruturado
func NewLogger(cfg config.LoggingConfig) Logger {
	return &StructuredLogger{
		config:   cfg,
		fields:   make([]Field, 0),
		minLevel: LogLevel(cfg.Level),
	}
}

// Debug log debug message
func (l *StructuredLogger) Debug(msg string, fields ...Field) {
	l.log(DEBUG, msg, fields...)
}

// Info log info message
func (l *StructuredLogger) Info(msg string, fields ...Field) {
	l.log(INFO, msg, fields...)
}

// Warn log warning message
func (l *StructuredLogger) Warn(msg string, fields ...Field) {
	l.log(WARN, msg, fields...)
}

// Error log error message
func (l *StructuredLogger) Error(msg string, fields ...Field) {
	l.log(ERROR, msg, fields...)
}

// With adiciona campos contextuais
func (l *StructuredLogger) With(fields ...Field) Logger {
	newFields := make([]Field, len(l.fields)+len(fields))
	copy(newFields, l.fields)
	copy(newFields[len(l.fields):], fields)
	
	return &StructuredLogger{
		config:   l.config,
		fields:   newFields,
		minLevel: l.minLevel,
	}
}

// log método interno para fazer o log
func (l *StructuredLogger) log(level LogLevel, msg string, fields ...Field) {
	if !l.shouldLog(level) {
		return
	}

	entry := LogEntry{
		Timestamp: time.Now(),
		Level:     level,
		Message:   msg,
		Fields:    make(map[string]interface{}),
	}

	// Adicionar campos contextuais
	for _, field := range l.fields {
		entry.Fields[field.Key] = field.Value
	}

	// Adicionar campos da mensagem
	for _, field := range fields {
		entry.Fields[field.Key] = field.Value
	}

	l.output(entry)
}

// shouldLog verifica se deve fazer log baseado no nível
func (l *StructuredLogger) shouldLog(level LogLevel) bool {
	levels := map[LogLevel]int{
		DEBUG: 0,
		INFO:  1,
		WARN:  2,
		ERROR: 3,
	}
	
	return levels[level] >= levels[l.minLevel]
}

// output escreve a entrada de log
func (l *StructuredLogger) output(entry LogEntry) {
	if l.config.Structured {
		// Log estruturado em JSON
		if data, err := json.Marshal(entry); err == nil {
			log.Printf("%s", data)
		}
	} else {
		// Log em formato simples
		fieldsStr := ""
		if len(entry.Fields) > 0 {
			if data, err := json.Marshal(entry.Fields); err == nil {
				fieldsStr = fmt.Sprintf(" %s", data)
			}
		}
		log.Printf("[%s] %s: %s%s", 
			entry.Level, 
			entry.Timestamp.Format(time.RFC3339), 
			entry.Message, 
			fieldsStr,
		)
	}
}

// Global logger instance
var defaultLogger Logger

// InitLogger inicializa o logger global com zerolog
func InitLogger(cfg config.LoggingConfig) {
	defaultLogger = NewZerologLogger(cfg)
}

// GetLogger retorna o logger global
func GetLogger() Logger {
	if defaultLogger == nil {
		// Fallback para logger zerolog padrão
		defaultLogger = NewZerologLogger(config.LoggingConfig{
			Level:      "info",
			Format:     "json",
			Output:     "stdout",
			Structured: true,
		})
	}
	return defaultLogger
}

// Context helpers

// ContextLogger adiciona contexto ao logger
func ContextLogger(ctx context.Context, fields ...Field) Logger {
	logger := GetLogger()
	
	// Adicionar campos do contexto se existirem
	if requestID := ctx.Value("request_id"); requestID != nil {
		fields = append(fields, F("request_id", requestID))
	}
	
	if userID := ctx.Value("user_id"); userID != nil {
		fields = append(fields, F("user_id", userID))
	}
	
	return logger.With(fields...)
}