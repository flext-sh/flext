package main

import (
	"os"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/server"
)

func main() {
	// Carregar configuração
	cfg := config.LoadConfig()

	// Inicializar logging
	logging.InitLogger(cfg.Logging)
	logger := logging.GetLogger()

	logger.Info("Initializing FLEXT application",
		logging.F("version", "1.0.0"),
		logging.F("environment", os.Getenv("ENVIRONMENT")),
	)

	// Inicializar container de dependências
	appContainer := container.NewContainer()

	// Criar e configurar servidor
	srv := server.NewServer(cfg, appContainer)

	// Iniciar servidor com graceful shutdown
	if err := srv.Start(); err != nil {
		logger.Error("Server failed to start", logging.F("error", err.Error()))
		os.Exit(1)
	}

	logger.Info("Application shutdown complete")
}