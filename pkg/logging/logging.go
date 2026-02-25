// Package logging - Structured logging for FLEXT Service
package logging

import (
	"log"
	"os"

	"github.com/rs/zerolog"
	zlog "github.com/rs/zerolog/log"
)

// Logger interface for structured logging
type Logger interface {
	Debug(msg string)
	Info(msg string, fields ...Field)
	Warn(msg string, fields ...Field)
	Error(msg string, fields ...Field)
	Fatal(msg string, fields ...Field)
}

// Field represents a logging field
type Field struct {
	Key   string
	Value interface{}
}

// F creates a logging field
func F(key string, value interface{}) Field {
	return Field{Key: key, Value: value}
}

// zerologLogger implements Logger using zerolog
type zerologLogger struct {
	logger zerolog.Logger
}

// Global logger instance
var globalLogger Logger

// Initialize initializes the logging system
func Initialize(service, level string) error {
	// Set log level
	logLevel, err := zerolog.ParseLevel(level)
	if err != nil {
		logLevel = zerolog.InfoLevel
	}

	zerolog.SetGlobalLevel(logLevel)

	// Configure console writer for development
	if os.Getenv("FLEXT_SERVER_ENVIRONMENT") == "development" {
		zlog.Logger = zlog.Logger.Output(zerolog.ConsoleWriter{Out: os.Stderr})
	}

	// Create logger with service context
	logger := zlog.Logger.With().
		Str("service", service).
		Logger()

	globalLogger = &zerologLogger{logger: logger}

	return nil
}

// GetLogger returns the global logger instance
func GetLogger() Logger {
	if globalLogger == nil {
		// Initialize with defaults if not already initialized
		if err := Initialize("flext", "info"); err != nil {
			// Fallback to basic logger if initialization fails
			log.Printf("Failed to initialize logger: %v", err)
		}
	}
	return globalLogger
}

// Debug logs a debug message
func (l *zerologLogger) Debug(msg string) {
	l.logger.Debug().Msg(msg)
}

// Info logs an info message with optional fields
func (l *zerologLogger) Info(msg string, fields ...Field) {
	event := l.logger.Info()
	for _, field := range fields {
		event = event.Interface(field.Key, field.Value)
	}
	event.Msg(msg)
}

// Warn logs a warning message with optional fields
func (l *zerologLogger) Warn(msg string, fields ...Field) {
	event := l.logger.Warn()
	for _, field := range fields {
		event = event.Interface(field.Key, field.Value)
	}
	event.Msg(msg)
}

// Error logs an error message with optional fields
func (l *zerologLogger) Error(msg string, fields ...Field) {
	event := l.logger.Error()
	for _, field := range fields {
		event = event.Interface(field.Key, field.Value)
	}
	event.Msg(msg)
}

// Fatal logs a fatal message with optional fields and exits
func (l *zerologLogger) Fatal(msg string, fields ...Field) {
	event := l.logger.Fatal()
	for _, field := range fields {
		event = event.Interface(field.Key, field.Value)
	}
	event.Msg(msg)
}
