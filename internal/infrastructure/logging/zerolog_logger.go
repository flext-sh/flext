package logging

import (
	"os"
	"strings"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

// ZerologLogger implements Logger interface using zerolog for high performance
type ZerologLogger struct {
	logger zerolog.Logger
}

// NewZerologLogger creates a new zerolog-based logger
func NewZerologLogger(cfg config.LoggingConfig) Logger {
	// Configure zerolog based on config
	zerolog.TimeFieldFormat = time.RFC3339

	// Set log level
	level := parseLogLevel(cfg.Level)
	zerolog.SetGlobalLevel(level)

	// Create base logger
	var logger zerolog.Logger

	if cfg.Format == "json" || cfg.Structured {
		// JSON structured output
		logger = zerolog.New(os.Stdout).With().Timestamp().Logger()
	} else {
		// Pretty console output for development
		logger = log.Output(zerolog.ConsoleWriter{
			Out:        os.Stdout,
			TimeFormat: time.RFC3339,
			NoColor:    cfg.Output != "stdout",
		}).With().Timestamp().Logger()
	}

	// Add service identifier
	logger = logger.With().Str("service", "flext").Logger()

	return &ZerologLogger{
		logger: logger,
	}
}

// Debug logs debug messages
func (l *ZerologLogger) Debug(msg string, fields ...Field) {
	event := l.logger.Debug()
	l.addFields(event, fields...)
	event.Msg(msg)
}

// Info logs info messages
func (l *ZerologLogger) Info(msg string, fields ...Field) {
	event := l.logger.Info()
	l.addFields(event, fields...)
	event.Msg(msg)
}

// Warn logs warning messages
func (l *ZerologLogger) Warn(msg string, fields ...Field) {
	event := l.logger.Warn()
	l.addFields(event, fields...)
	event.Msg(msg)
}

// Error logs error messages
func (l *ZerologLogger) Error(msg string, fields ...Field) {
	event := l.logger.Error()
	l.addFields(event, fields...)
	event.Msg(msg)
}

// With creates a child logger with additional fields
func (l *ZerologLogger) With(fields ...Field) Logger {
	ctx := l.logger.With()
	for _, field := range fields {
		ctx = ctx.Interface(field.Key, field.Value)
	}

	return &ZerologLogger{
		logger: ctx.Logger(),
	}
}

// addFields adds fields to a zerolog event
func (l *ZerologLogger) addFields(event *zerolog.Event, fields ...Field) {
	for _, field := range fields {
		event.Interface(field.Key, field.Value)
	}
}

// parseLogLevel converts string log level to zerolog level
func parseLogLevel(level string) zerolog.Level {
	switch strings.ToLower(level) {
	case "debug":
		return zerolog.DebugLevel
	case "info":
		return zerolog.InfoLevel
	case "warn", "warning":
		return zerolog.WarnLevel
	case "error":
		return zerolog.ErrorLevel
	case "fatal":
		return zerolog.FatalLevel
	case "panic":
		return zerolog.PanicLevel
	default:
		return zerolog.InfoLevel
	}
}

// Convenience functions for global logger
func Debug(msg string, fields ...Field) {
	GetLogger().Debug(msg, fields...)
}

func Info(msg string, fields ...Field) {
	GetLogger().Info(msg, fields...)
}

func Warn(msg string, fields ...Field) {
	GetLogger().Warn(msg, fields...)
}

func Error(msg string, fields ...Field) {
	GetLogger().Error(msg, fields...)
}

func With(fields ...Field) Logger {
	return GetLogger().With(fields...)
}
