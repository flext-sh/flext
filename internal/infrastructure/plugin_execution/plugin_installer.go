package plugin_execution

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
)

// PluginInstaller instala e gerencia plugins Singer reais
type PluginInstaller struct {
	logger      logging.Logger
	pluginsDir  string
	pythonPath  string
	venvPath    string
	meltanoPath string
}

// NewPluginInstaller cria um novo instalador de plugins
func NewPluginInstaller(logger logging.Logger) *PluginInstaller {
	pluginsDir := os.Getenv("FLEXT_PLUGINS_DIR")
	if pluginsDir == "" {
		pluginsDir = "/opt/flext/plugins"
	}

	pythonPath := os.Getenv("PYTHON_PATH")
	if pythonPath == "" {
		pythonPath = "python3"
	}

	venvPath := os.Getenv("FLEXT_VENV_PATH")
	if venvPath == "" {
		venvPath = "/home/marlonsc/flext/.venv"
	}

	meltanoPath := os.Getenv("MELTANO_PATH")
	if meltanoPath == "" {
		meltanoPath = "meltano"
	}

	return &PluginInstaller{
		logger:      logger,
		pluginsDir:  pluginsDir,
		pythonPath:  pythonPath,
		venvPath:    venvPath,
		meltanoPath: meltanoPath,
	}
}

// SetupEnvironment configura o ambiente completo
func (pi *PluginInstaller) SetupEnvironment() error {
	pi.logger.Info("🚀 Setting up complete FLEXT plugin environment")

	// 1. Verificar/criar diretório de plugins
	if err := pi.ensurePluginsDirectory(); err != nil {
		return fmt.Errorf("failed to setup plugins directory: %w", err)
	}

	// 2. Verificar Python e virtual environment
	if err := pi.setupPythonEnvironment(); err != nil {
		return fmt.Errorf("failed to setup Python environment: %w", err)
	}

	// 3. Instalar Meltano
	if err := pi.installMeltano(); err != nil {
		return fmt.Errorf("failed to install Meltano: %w", err)
	}

	// 4. Criar projeto Meltano
	if err := pi.setupMeltanoProject(); err != nil {
		return fmt.Errorf("failed to setup Meltano project: %w", err)
	}

	// 5. Instalar plugins Singer essenciais
	if err := pi.installEssentialPlugins(); err != nil {
		return fmt.Errorf("failed to install essential plugins: %w", err)
	}

	pi.logger.Info("✅ FLEXT plugin environment setup completed successfully")
	return nil
}

// ensurePluginsDirectory garante que o diretório de plugins existe
func (pi *PluginInstaller) ensurePluginsDirectory() error {
	pi.logger.Info("📁 Ensuring plugins directory", logging.F("path", pi.pluginsDir))

	if err := os.MkdirAll(pi.pluginsDir, 0755); err != nil {
		return fmt.Errorf("failed to create plugins directory: %w", err)
	}

	// Criar subdiretórios
	subdirs := []string{"extractors", "loaders", "transformers", "utilities", "bin", "data"}
	for _, subdir := range subdirs {
		if err := os.MkdirAll(filepath.Join(pi.pluginsDir, subdir), 0755); err != nil {
			return fmt.Errorf("failed to create subdir %s: %w", subdir, err)
		}
	}

	pi.logger.Info("✅ Plugins directory structure created")
	return nil
}

// setupPythonEnvironment configura o ambiente Python
func (pi *PluginInstaller) setupPythonEnvironment() error {
	pi.logger.Info("🐍 Setting up Python environment", logging.F("venv", pi.venvPath))

	// Verificar se Python existe
	if err := pi.runCommand("python3", "--version"); err != nil {
		return fmt.Errorf("Python 3 not found: %w", err)
	}

	// Verificar se virtual environment existe
	if _, err := os.Stat(pi.venvPath); os.IsNotExist(err) {
		pi.logger.Info("Creating Python virtual environment")
		if err := pi.runCommand("python3", "-m", "venv", pi.venvPath); err != nil {
			return fmt.Errorf("failed to create virtual environment: %w", err)
		}
	}

	// Ativar venv e atualizar pip
	if err := pi.runCommandInVenv("pip", "install", "--upgrade", "pip", "setuptools", "wheel"); err != nil {
		return fmt.Errorf("failed to upgrade pip: %w", err)
	}

	pi.logger.Info("✅ Python environment ready")
	return nil
}

// installMeltano instala o Meltano
func (pi *PluginInstaller) installMeltano() error {
	pi.logger.Info("📦 Installing Meltano")

	// Verificar se Meltano já está instalado
	if err := pi.runCommandInVenv("meltano", "--version"); err == nil {
		pi.logger.Info("✅ Meltano already installed")
		return nil
	}

	// Instalar Meltano
	if err := pi.runCommandInVenv("pip", "install", "meltano"); err != nil {
		return fmt.Errorf("failed to install Meltano: %w", err)
	}

	// Verificar instalação
	if err := pi.runCommandInVenv("meltano", "--version"); err != nil {
		return fmt.Errorf("Meltano installation verification failed: %w", err)
	}

	pi.logger.Info("✅ Meltano installed successfully")
	return nil
}

// setupMeltanoProject cria o projeto Meltano
func (pi *PluginInstaller) setupMeltanoProject() error {
	projectPath := filepath.Join(pi.pluginsDir, "meltano-project")
	pi.logger.Info("🏗️ Setting up Meltano project", logging.F("path", projectPath))

	// Verificar se projeto já existe
	if _, err := os.Stat(filepath.Join(projectPath, "meltano.yml")); err == nil {
		pi.logger.Info("✅ Meltano project already exists")
		return nil
	}

	// Criar diretório do projeto
	if err := os.MkdirAll(projectPath, 0755); err != nil {
		return fmt.Errorf("failed to create project directory: %w", err)
	}

	// Inicializar projeto Meltano
	if err := pi.runCommandInVenvAtPath(projectPath, "meltano", "init", "."); err != nil {
		return fmt.Errorf("failed to initialize Meltano project: %w", err)
	}

	pi.logger.Info("✅ Meltano project created")
	return nil
}

// installEssentialPlugins instala plugins Singer essenciais
func (pi *PluginInstaller) installEssentialPlugins() error {
	pi.logger.Info("🔌 Installing essential Singer plugins")

	projectPath := filepath.Join(pi.pluginsDir, "meltano-project")

	// Lista de plugins essenciais para teste
	plugins := []struct {
		name    string
		variant string
		pip     string
	}{
		{"tap-csv", "meltanolabs", "pipelinewise-tap-csv"},
		{"target-jsonl", "andyh1203", "target-jsonl"},
		{"target-postgres", "meltanolabs", "pipelinewise-target-postgres"},
	}

	for _, plugin := range plugins {
		pi.logger.Info("Installing plugin", 
			logging.F("name", plugin.name), 
			logging.F("variant", plugin.variant))

		// Adicionar plugin ao Meltano
		if err := pi.runCommandInVenvAtPath(projectPath, "meltano", "add", "extractor", plugin.name, "--variant", plugin.variant); err != nil {
			pi.logger.Warn("Failed to add plugin via Meltano, trying pip install", 
				logging.F("plugin", plugin.name), 
				logging.F("error", err.Error()))

			// Fallback: instalar via pip
			if err := pi.runCommandInVenv("pip", "install", plugin.pip); err != nil {
				pi.logger.Warn("Failed to install plugin via pip", 
					logging.F("plugin", plugin.pip), 
					logging.F("error", err.Error()))
				continue
			}
		}

		pi.logger.Info("✅ Plugin installed", logging.F("name", plugin.name))
	}

	return nil
}

// CreateTestData cria dados de teste para validação
func (pi *PluginInstaller) CreateTestData() error {
	pi.logger.Info("📊 Creating test data")

	dataDir := filepath.Join(pi.pluginsDir, "data")
	csvFile := filepath.Join(dataDir, "test-users.csv")

	// Criar arquivo CSV de teste
	csvContent := `id,name,email,status,created_at
1,João Silva,joao@example.com,active,2025-01-01
2,Maria Santos,maria@example.com,active,2025-01-02
3,Pedro Lima,pedro@example.com,inactive,2025-01-03
4,Ana Costa,ana@example.com,active,2025-01-04
5,Carlos Pereira,carlos@example.com,active,2025-01-05
`

	if err := os.WriteFile(csvFile, []byte(csvContent), 0644); err != nil {
		return fmt.Errorf("failed to create test CSV: %w", err)
	}

	pi.logger.Info("✅ Test data created", logging.F("file", csvFile))
	return nil
}

// runCommand executa um comando no sistema
func (pi *PluginInstaller) runCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Env = os.Environ()
	
	pi.logger.Debug("Running command", 
		logging.F("cmd", name), 
		logging.F("args", strings.Join(args, " ")))

	output, err := cmd.CombinedOutput()
	if err != nil {
		pi.logger.Error("Command failed", 
			logging.F("cmd", name), 
			logging.F("error", err.Error()),
			logging.F("output", string(output)))
		return err
	}

	return nil
}

// runCommandInVenv executa comando no virtual environment
func (pi *PluginInstaller) runCommandInVenv(name string, args ...string) error {
	// Ativar venv usando source
	activateScript := filepath.Join(pi.venvPath, "bin", "activate")
	
	var cmdStr string
	if name == "pip" || name == "python" || name == "meltano" {
		// Usar executável do venv diretamente
		venvBin := filepath.Join(pi.venvPath, "bin", name)
		if _, err := os.Stat(venvBin); err == nil {
			name = venvBin
		}
	}
	
	cmdStr = fmt.Sprintf("source %s && %s %s", activateScript, name, strings.Join(args, " "))
	
	cmd := exec.Command("bash", "-c", cmdStr)
	cmd.Env = os.Environ()

	pi.logger.Debug("Running venv command", logging.F("cmd", cmdStr))

	output, err := cmd.CombinedOutput()
	if err != nil {
		pi.logger.Error("Venv command failed", 
			logging.F("cmd", cmdStr), 
			logging.F("error", err.Error()),
			logging.F("output", string(output)))
		return err
	}

	return nil
}

// runCommandInVenvAtPath executa comando no venv em um diretório específico
func (pi *PluginInstaller) runCommandInVenvAtPath(workDir, name string, args ...string) error {
	activateScript := filepath.Join(pi.venvPath, "bin", "activate")
	
	if name == "meltano" {
		venvBin := filepath.Join(pi.venvPath, "bin", name)
		if _, err := os.Stat(venvBin); err == nil {
			name = venvBin
		}
	}
	
	cmdStr := fmt.Sprintf("cd %s && source %s && %s %s", workDir, activateScript, name, strings.Join(args, " "))
	
	cmd := exec.Command("bash", "-c", cmdStr)
	cmd.Env = os.Environ()

	pi.logger.Debug("Running venv command at path", 
		logging.F("path", workDir),
		logging.F("cmd", cmdStr))

	output, err := cmd.CombinedOutput()
	if err != nil {
		pi.logger.Error("Venv command at path failed", 
			logging.F("path", workDir),
			logging.F("cmd", cmdStr), 
			logging.F("error", err.Error()),
			logging.F("output", string(output)))
		return err
	}

	return nil
}

// ValidateInstallation valida se tudo foi instalado corretamente
func (pi *PluginInstaller) ValidateInstallation() error {
	pi.logger.Info("🔍 Validating plugin installation")

	// Verificar Meltano
	if err := pi.runCommandInVenv("meltano", "--version"); err != nil {
		return fmt.Errorf("Meltano validation failed: %w", err)
	}

	// Verificar projeto Meltano
	projectPath := filepath.Join(pi.pluginsDir, "meltano-project")
	if _, err := os.Stat(filepath.Join(projectPath, "meltano.yml")); err != nil {
		return fmt.Errorf("Meltano project validation failed: %w", err)
	}

	// Verificar dados de teste
	csvFile := filepath.Join(pi.pluginsDir, "data", "test-users.csv")
	if _, err := os.Stat(csvFile); err != nil {
		return fmt.Errorf("test data validation failed: %w", err)
	}

	pi.logger.Info("✅ Plugin installation validated successfully")
	return nil
}

// GetProjectPath retorna o caminho do projeto Meltano
func (pi *PluginInstaller) GetProjectPath() string {
	return filepath.Join(pi.pluginsDir, "meltano-project")
}

// GetTestDataPath retorna o caminho dos dados de teste
func (pi *PluginInstaller) GetTestDataPath() string {
	return filepath.Join(pi.pluginsDir, "data", "test-users.csv")
}