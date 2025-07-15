# FLEXT Go API Dockerfile
# =======================

# Build stage
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY cmd/ ./cmd/
COPY internal/ ./internal/

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o flext cmd/flext/main.go

# Final stage
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates tzdata curl

# Create non-root user
RUN addgroup -g 1001 -S flext \
    && adduser -u 1001 -S flext -G flext

# Set working directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/flext .

# Create directories
RUN mkdir -p /var/log/flext \
    && chown -R flext:flext /app /var/log/flext

# Switch to non-root user
USER flext

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Set default environment variables
ENV FLEXT_PORT=8081
ENV FLEXT_LOG_LEVEL=info
ENV FLEXT_LOG_FORMAT=json

# Run the application
CMD ["./flext"]