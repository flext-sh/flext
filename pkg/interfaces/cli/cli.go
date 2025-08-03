package cli

import (
	"context"
	"flag"
	"fmt"
	"strings"

	"github.com/flext-sh/flext/pkg/interfaces/cli/commands"
)

// CLI representa a interface de linha de comando do FLEXT
type CLI struct {
	commands map[string]Command
	version  string
}

// Command interface para comandos CLI
type Command interface {
	Name() string
	Description() string
	Usage() string
	Flags() *flag.FlagSet
	Run(ctx context.Context, args []string) error
}

// NewCLI cria uma nova instância do CLI
func NewCLI() *CLI {
	cli := &CLI{
		commands: make(map[string]Command),
		version:  "1.0.0",
	}

	// Registrar comandos
	cli.registerCommands()

	return cli
}

// registerCommands registra todos os comandos disponíveis
func (c *CLI) registerCommands() {
	// Pipeline commands
	c.RegisterCommand(commands.NewPipelineCreateCommand())
	c.RegisterCommand(commands.NewPipelineListCommand())
	c.RegisterCommand(commands.NewPipelineShowCommand())
	c.RegisterCommand(commands.NewPipelineRunCommand())
	c.RegisterCommand(commands.NewPipelineDeleteCommand())

	// Singer commands
	c.RegisterCommand(commands.NewSingerListCommand())
	c.RegisterCommand(commands.NewSingerCreateCommand())
	c.RegisterCommand(commands.NewSingerRunCommand())
	c.RegisterCommand(commands.NewSingerTestCommand())
	c.RegisterCommand(commands.NewSingerDiscoverCommand())

	// dbt commands
	c.RegisterCommand(commands.NewDbtInitCommand())
	c.RegisterCommand(commands.NewDbtRunCommand())
	c.RegisterCommand(commands.NewDbtTestCommand())
	c.RegisterCommand(commands.NewDbtCompileCommand())
	c.RegisterCommand(commands.NewDbtSeedCommand())
	c.RegisterCommand(commands.NewDbtSnapshotCommand())
	c.RegisterCommand(commands.NewDbtDebugCommand())
	c.RegisterCommand(commands.NewDbtDepsCommand())
	c.RegisterCommand(commands.NewDbtCleanCommand())

	// Server commands
	c.RegisterCommand(commands.NewServerStartCommand())
	c.RegisterCommand(commands.NewServerStatusCommand())
	c.RegisterCommand(commands.NewServerStopCommand())

	// Utility commands
	c.RegisterCommand(commands.NewVersionCommand(c.version))
	c.RegisterCommand(commands.NewHelpCommand(c))
}

// RegisterCommand registra um novo comando
func (c *CLI) RegisterCommand(cmd Command) {
	c.commands[cmd.Name()] = cmd
}

// Run executa o CLI com os argumentos fornecidos
func (c *CLI) Run(ctx context.Context, args []string) error {
	if len(args) < 2 {
		c.showUsage()
		return nil
	}

	commandName := args[1]
	commandArgs := args[2:]

	// Verificar se o comando existe
	cmd, exists := c.commands[commandName]
	if !exists {
		fmt.Printf("Unknown command: %s\n\n", commandName)
		c.showUsage()
		return fmt.Errorf("unknown command: %s", commandName)
	}

	// Executar comando
	return cmd.Run(ctx, commandArgs)
}

// showUsage mostra a informação de uso do CLI
func (c *CLI) showUsage() {
	fmt.Printf("FLEXT CLI v%s\n\n", c.version)
	fmt.Println("A comprehensive data pipeline and ETL management platform")
	fmt.Println()
	fmt.Println("USAGE:")
	fmt.Println("  flext-cli <command> [options]")
	fmt.Println()
	fmt.Println("AVAILABLE COMMANDS:")
	fmt.Println()

	// Agrupar comandos por categoria
	categories := map[string][]Command{
		"Pipeline Management": {},
		"Singer/Meltano":      {},
		"dbt Integration":     {},
		"Server Management":   {},
		"Utilities":           {},
	}

	// Categorizar comandos
	for _, cmd := range c.commands {
		switch {
		case strings.HasPrefix(cmd.Name(), "pipeline-"):
			categories["Pipeline Management"] = append(categories["Pipeline Management"], cmd)
		case strings.HasPrefix(cmd.Name(), "singer-"):
			categories["Singer/Meltano"] = append(categories["Singer/Meltano"], cmd)
		case strings.HasPrefix(cmd.Name(), "dbt-"):
			categories["dbt Integration"] = append(categories["dbt Integration"], cmd)
		case strings.HasPrefix(cmd.Name(), "server-"):
			categories["Server Management"] = append(categories["Server Management"], cmd)
		default:
			categories["Utilities"] = append(categories["Utilities"], cmd)
		}
	}

	// Mostrar comandos por categoria
	for category, cmds := range categories {
		if len(cmds) == 0 {
			continue
		}
		fmt.Printf("  %s:\n", category)
		for _, cmd := range cmds {
			fmt.Printf("    %-20s %s\n", cmd.Name(), cmd.Description())
		}
		fmt.Println()
	}

	fmt.Println("Use 'flext-cli help <command>' for more information about a specific command.")
	fmt.Println()
	fmt.Println("EXAMPLES:")
	fmt.Println("  flext-cli pipeline-create --name my-pipeline --description 'My ETL pipeline'")
	fmt.Println("  flext-cli pipeline-list")
	fmt.Println("  flext-cli singer-create --name tap-postgres --type tap")
	fmt.Println("  flext-cli dbt-run --project my-dbt-project")
	fmt.Println("  flext-cli server-start --port 8080")
	fmt.Println()
}

// GetCommands retorna todos os comandos registrados
func (c *CLI) GetCommands() map[string]commands.Command {
	result := make(map[string]commands.Command)
	for k, v := range c.commands {
		result[k] = v
	}
	return result
}

// GetCommand retorna um comando específico
func (c *CLI) GetCommand(name string) (commands.Command, bool) {
	cmd, exists := c.commands[name]
	return cmd, exists
}
