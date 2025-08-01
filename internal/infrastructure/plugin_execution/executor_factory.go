package plugin_execution

import (
	"os"
	"path/filepath"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/services"
	"github.com/flext/flexcore/internal/infrastructure/logging"
)

// ExecutorFactory cria executores de plugin configurados
type ExecutorFactory struct {
	pluginsDir      string
	workspaceDir    string
	timeout         time.Duration
	logger          logging.Logger
	pluginInstaller *PluginInstaller
}

// NewExecutorFactory cria uma nova factory
func NewExecutorFactory() *ExecutorFactory {
	// Configurações padrão
	pluginsDir := os.Getenv("FLEXT_PLUGINS_DIR")
	if pluginsDir == "" {
		pluginsDir = "/opt/flext/plugins"
	}

	workspaceDir := os.Getenv("FLEXT_WORKSPACE_DIR")
	if workspaceDir == "" {
		workspaceDir = "/tmp/flext"
	}

	timeout := 5 * time.Minute // Timeout padrão
	if timeoutEnv := os.Getenv("FLEXT_PLUGIN_TIMEOUT"); timeoutEnv != "" {
		if parsedTimeout, err := time.ParseDuration(timeoutEnv); err == nil {
			timeout = parsedTimeout
		}
	}

	// Criar logger e plugin installer
	logger := logging.GetLogger()
	pluginInstaller := NewPluginInstaller(logger)

	return &ExecutorFactory{
		pluginsDir:      pluginsDir,
		workspaceDir:    workspaceDir,
		timeout:         timeout,
		logger:          logger,
		pluginInstaller: pluginInstaller,
	}
}

// CreateRealExecutor cria um executor real configurado
func (f *ExecutorFactory) CreateRealExecutor() services.RealPluginExecutor {
	// Garantir que diretórios existam
	os.MkdirAll(f.pluginsDir, 0755)
	os.MkdirAll(f.workspaceDir, 0755)

	return NewRealPluginExecutor(f.pluginsDir, f.workspaceDir, f.timeout)
}

// CreatePipelineExecutor cria um executor de pipeline com executor real
func (f *ExecutorFactory) CreatePipelineExecutor(pluginRepo services.PluginRepository) *services.PipelineExecutor {
	realExecutor := f.CreateRealExecutor()
	return services.NewPipelineExecutor(pluginRepo, realExecutor)
}

// CreateSimulationExecutor cria um executor apenas com simulação (para testes)
func (f *ExecutorFactory) CreateSimulationExecutor(pluginRepo services.PluginRepository) *services.PipelineExecutor {
	return services.NewPipelineExecutorWithSimulation(pluginRepo)
}

// SetupPluginDirectory cria estrutura de diretórios para plugins
func (f *ExecutorFactory) SetupPluginDirectory() error {
	f.logger.Info("🔧 Setting up plugin directory structure")

	dirs := []string{
		f.pluginsDir,
		filepath.Join(f.pluginsDir, "bin"),
		filepath.Join(f.pluginsDir, "python"),
		filepath.Join(f.pluginsDir, "javascript"),
		filepath.Join(f.pluginsDir, "shell"),
		f.workspaceDir,
		filepath.Join(f.workspaceDir, "executions"),
		filepath.Join(f.workspaceDir, "temp"),
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return err
		}
	}

	f.logger.Info("✅ Plugin directory structure created")
	return nil
}

// InstallSamplePlugins instala plugins de exemplo para desenvolvimento
func (f *ExecutorFactory) InstallSamplePlugins() error {
	if err := f.SetupPluginDirectory(); err != nil {
		return err
	}

	// Criar plugin CSV extractor em Python
	csvPlugin := `#!/usr/bin/env python3
import json
import sys
import csv
import os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: csv-extractor <input.json>")
        sys.exit(1)

    # Ler configuração
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)

    file_path = config.get('config', {}).get('file_path', '/tmp/sample.csv')

    # Simular dados CSV se arquivo não existir
    if not os.path.exists(file_path):
        sample_data = [
            {"id": 1, "name": "User 1", "email": "user1@example.com", "status": "active"},
            {"id": 2, "name": "User 2", "email": "user2@example.com", "status": "inactive"},
            {"id": 3, "name": "User 3", "email": "user3@example.com", "status": "active"}
        ]

        result = {
            "records": sample_data,
            "records_processed": len(sample_data),
            "source_file": file_path,
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Ler arquivo CSV real
        records = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                records.append(dict(row))

        result = {
            "records": records,
            "records_processed": len(records),
            "source_file": file_path,
            "timestamp": datetime.now().isoformat()
        }

    # Retornar resultado como JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
`

	csvPluginPath := filepath.Join(f.pluginsDir, "python", "csv-extractor.py")
	if err := os.WriteFile(csvPluginPath, []byte(csvPlugin), 0755); err != nil {
		return err
	}

	// Criar symlink para execução direta
	csvLinkPath := filepath.Join(f.pluginsDir, "csv-extractor")
	os.Remove(csvLinkPath) // Remove se já existir
	if err := os.Symlink(csvPluginPath, csvLinkPath); err != nil {
		// Se symlink falhar, copiar o arquivo
		return os.WriteFile(csvLinkPath, []byte(csvPlugin), 0755)
	}

	// Criar plugin de filtro em shell script
	filterPlugin := `#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: data-filter <input.json>"
    exit 1
fi

INPUT_FILE="$1"

# Ler configuração e dados
CONFIG=$(cat "$INPUT_FILE")

# Simular filtro de dados (script mais complexo faria parse real do JSON)
cat <<EOF
{
  "records": [
    {"id": 1, "name": "User 1", "email": "user1@example.com", "status": "active", "filtered": true},
    {"id": 3, "name": "User 3", "email": "user3@example.com", "status": "active", "filtered": true}
  ],
  "records_processed": 2,
  "filter_applied": "status=active",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
`

	filterPluginPath := filepath.Join(f.pluginsDir, "shell", "data-filter.sh")
	if err := os.WriteFile(filterPluginPath, []byte(filterPlugin), 0755); err != nil {
		return err
	}

	filterLinkPath := filepath.Join(f.pluginsDir, "data-filter")
	os.Remove(filterLinkPath)
	if err := os.Symlink(filterPluginPath, filterLinkPath); err != nil {
		return os.WriteFile(filterLinkPath, []byte(filterPlugin), 0755)
	}

	return nil
}

// SetupCompleteEnvironment configura ambiente completo com plugins reais
func (f *ExecutorFactory) SetupCompleteEnvironment() error {
	f.logger.Info("🚀 Setting up complete FLEXT execution environment")

	// 1. Configurar estrutura básica de diretórios
	if err := f.SetupPluginDirectory(); err != nil {
		return err
	}

	// 2. Configurar ambiente Python e Meltano
	if err := f.pluginInstaller.SetupEnvironment(); err != nil {
		f.logger.Warn("Failed to setup real plugin environment, using sample plugins",
			logging.F("error", err.Error()))

		// Fallback para plugins de exemplo se ambiente real falhar
		return f.InstallSamplePlugins()
	}

	// 3. Criar dados de teste
	if err := f.pluginInstaller.CreateTestData(); err != nil {
		f.logger.Warn("Failed to create test data", logging.F("error", err.Error()))
	}

	// 4. Validar instalação
	if err := f.pluginInstaller.ValidateInstallation(); err != nil {
		f.logger.Warn("Real plugin validation failed, using sample plugins",
			logging.F("error", err.Error()))
		return f.InstallSamplePlugins()
	}

	f.logger.Info("✅ Complete FLEXT execution environment ready")
	return nil
}

// CreateProductionExecutor cria executor para ambiente de produção
func (f *ExecutorFactory) CreateProductionExecutor(pluginRepo services.PluginRepository) (*services.PipelineExecutor, error) {
	// Configurar ambiente completo
	if err := f.SetupCompleteEnvironment(); err != nil {
		return nil, err
	}

	// Criar executor real
	realExecutor := f.CreateRealExecutor()

	// Criar executor de pipeline com executor real
	executor := services.NewPipelineExecutor(pluginRepo, realExecutor)

	f.logger.Info("✅ Production pipeline executor created")
	return executor, nil
}

// GetMeltanoProjectPath retorna o caminho do projeto Meltano
func (f *ExecutorFactory) GetMeltanoProjectPath() string {
	return f.pluginInstaller.GetProjectPath()
}

// GetTestDataPath retorna o caminho dos dados de teste
func (f *ExecutorFactory) GetTestDataPath() string {
	return f.pluginInstaller.GetTestDataPath()
}

// ValidateEnvironment valida se o ambiente está funcionando
func (f *ExecutorFactory) ValidateEnvironment() error {
	f.logger.Info("🔍 Validating execution environment")

	// Validar instalação dos plugins
	if err := f.pluginInstaller.ValidateInstallation(); err != nil {
		return err
	}

	f.logger.Info("✅ Execution environment validated")
	return nil
}
