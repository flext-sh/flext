package commands

import (
	"context"
	"flag"
	"fmt"
	"runtime"
	"strings"
)

// VersionCommand comando para mostrar versão
type VersionCommand struct {
	flags   *flag.FlagSet
	version string
}

// NewVersionCommand cria um novo comando de versão
func NewVersionCommand(version string) *VersionCommand {
	cmd := &VersionCommand{
		flags:   flag.NewFlagSet("version", flag.ExitOnError),
		version: version,
	}

	return cmd
}

func (c *VersionCommand) Name() string         { return "version" }
func (c *VersionCommand) Description() string  { return "Show version information" }
func (c *VersionCommand) Usage() string        { return "version" }
func (c *VersionCommand) Flags() *flag.FlagSet { return c.flags }

func (c *VersionCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	fmt.Printf("FLEXT CLI %s\n", c.version)
	fmt.Printf("Go version: %s\n", runtime.Version())
	fmt.Printf("OS/Arch: %s/%s\n", runtime.GOOS, runtime.GOARCH)
	fmt.Printf("\nA comprehensive data pipeline and ETL management platform\n")
	fmt.Printf("Built with Hexagonal Architecture + DDD + Singer/Meltano + dbt\n")

	return nil
}

// HelpCommand comando para mostrar ajuda
type HelpCommand struct {
	flags *flag.FlagSet
	cli   CLIInterface
}

// CLIInterface interface para acessar CLI
type CLIInterface interface {
	GetCommands() map[string]Command
	GetCommand(name string) (Command, bool)
}

// Command interface (redeclaration for this package)
type Command interface {
	Name() string
	Description() string
	Usage() string
	Flags() *flag.FlagSet
	Run(ctx context.Context, args []string) error
}

// NewHelpCommand cria um novo comando de ajuda
func NewHelpCommand(cli CLIInterface) *HelpCommand {
	cmd := &HelpCommand{
		flags: flag.NewFlagSet("help", flag.ExitOnError),
		cli:   cli,
	}

	return cmd
}

func (c *HelpCommand) Name() string         { return "help" }
func (c *HelpCommand) Description() string  { return "Show help information" }
func (c *HelpCommand) Usage() string        { return "help [command]" }
func (c *HelpCommand) Flags() *flag.FlagSet { return c.flags }

func (c *HelpCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	// Se um comando específico foi fornecido
	if len(args) > 0 {
		commandName := args[0]
		if cmd, exists := c.cli.GetCommand(commandName); exists {
			c.showCommandHelp(cmd)
			return nil
		} else {
			fmt.Printf("Unknown command: %s\n\n", commandName)
		}
	}

	// Mostrar ajuda geral
	c.showGeneralHelp()
	return nil
}

func (c *HelpCommand) showCommandHelp(cmd Command) {
	fmt.Printf("Command: %s\n", cmd.Name())
	fmt.Printf("Description: %s\n\n", cmd.Description())
	fmt.Printf("Usage: flext-cli %s\n\n", cmd.Usage())

	// Show flags if available
	flags := cmd.Flags()
	if flags != nil {
		fmt.Printf("Options:\n")
		flags.VisitAll(func(f *flag.Flag) {
			fmt.Printf("  --%s", f.Name)
			if f.DefValue != "" {
				fmt.Printf(" (default: %s)", f.DefValue)
			}
			fmt.Printf("\n      %s\n", f.Usage)
		})
		fmt.Printf("\n")
	}

	// Add examples based on command type
	c.showCommandExamples(cmd)
}

func (c *HelpCommand) showCommandExamples(cmd Command) {
	commandName := cmd.Name()

	fmt.Printf("Examples:\n")

	switch {
	case strings.HasPrefix(commandName, "pipeline-"):
		switch commandName {
		case "pipeline-create":
			fmt.Printf("  # Create a simple pipeline\n")
			fmt.Printf("  flext-cli pipeline-create --name \"my-etl-pipeline\" --description \"Data extraction pipeline\"\n\n")
			fmt.Printf("  # Create a pipeline with tags\n")
			fmt.Printf("  flext-cli pipeline-create --name \"sales-pipeline\" --tags \"sales,daily,etl\"\n\n")
		case "pipeline-list":
			fmt.Printf("  # List all pipelines\n")
			fmt.Printf("  flext-cli pipeline-list\n\n")
			fmt.Printf("  # List only active pipelines\n")
			fmt.Printf("  flext-cli pipeline-list --active\n\n")
			fmt.Printf("  # List pipelines with specific tags\n")
			fmt.Printf("  flext-cli pipeline-list --tags \"sales,etl\"\n\n")
		case "pipeline-show":
			fmt.Printf("  # Show pipeline details\n")
			fmt.Printf("  flext-cli pipeline-show --id 123e4567-e89b-12d3-a456-426614174000\n\n")
		case "pipeline-run":
			fmt.Printf("  # Run a pipeline\n")
			fmt.Printf("  flext-cli pipeline-run --id 123e4567-e89b-12d3-a456-426614174000\n\n")
			fmt.Printf("  # Run and wait for completion\n")
			fmt.Printf("  flext-cli pipeline-run --id 123e4567-e89b-12d3-a456-426614174000 --wait\n\n")
		case "pipeline-delete":
			fmt.Printf("  # Delete a pipeline (with confirmation)\n")
			fmt.Printf("  flext-cli pipeline-delete --id 123e4567-e89b-12d3-a456-426614174000\n\n")
			fmt.Printf("  # Force delete without confirmation\n")
			fmt.Printf("  flext-cli pipeline-delete --id 123e4567-e89b-12d3-a456-426614174000 --force\n\n")
		}

	case strings.HasPrefix(commandName, "singer-"):
		switch commandName {
		case "singer-create":
			fmt.Printf("  # Create a tap specification\n")
			fmt.Printf("  flext-cli singer-create --name \"tap-postgres\" --type tap --executable \"/usr/local/bin/tap-postgres\"\n\n")
			fmt.Printf("  # Create a target specification\n")
			fmt.Printf("  flext-cli singer-create --name \"target-jsonl\" --type target --executable \"/usr/local/bin/target-jsonl\"\n\n")
		case "singer-list":
			fmt.Printf("  # List all Singer specs\n")
			fmt.Printf("  flext-cli singer-list\n\n")
			fmt.Printf("  # List only taps\n")
			fmt.Printf("  flext-cli singer-list --type tap\n\n")
			fmt.Printf("  # List only active specs\n")
			fmt.Printf("  flext-cli singer-list --active\n\n")
		case "singer-run":
			fmt.Printf("  # Run a Singer specification\n")
			fmt.Printf("  flext-cli singer-run --id abc123 --pipeline-id def456 --config config.json\n\n")
			fmt.Printf("  # Run and wait for completion\n")
			fmt.Printf("  flext-cli singer-run --id abc123 --pipeline-id def456 --config config.json --wait\n\n")
		case "singer-test":
			fmt.Printf("  # Test a Singer connection\n")
			fmt.Printf("  flext-cli singer-test --id abc123 --config config.json\n\n")
		case "singer-discover":
			fmt.Printf("  # Discover schema and save to file\n")
			fmt.Printf("  flext-cli singer-discover --id abc123 --config config.json --output catalog.json\n\n")
			fmt.Printf("  # Discover schema to stdout\n")
			fmt.Printf("  flext-cli singer-discover --id abc123 --config config.json\n\n")
		}

	case strings.HasPrefix(commandName, "dbt-"):
		switch commandName {
		case "dbt-init":
			fmt.Printf("  # Initialize a new dbt project\n")
			fmt.Printf("  flext-cli dbt-init --name \"analytics\" --dir \"/path/to/project\"\n\n")
			fmt.Printf("  # Initialize with custom profile\n")
			fmt.Printf("  flext-cli dbt-init --name \"analytics\" --dir \"/path/to/project\" --profile \"prod_analytics\"\n\n")
		case "dbt-run":
			fmt.Printf("  # Run all models\n")
			fmt.Printf("  flext-cli dbt-run --project-id abc123\n\n")
			fmt.Printf("  # Run specific models\n")
			fmt.Printf("  flext-cli dbt-run --project-id abc123 --models \"staging,marts.sales\"\n\n")
		case "dbt-test":
			fmt.Printf("  # Run all tests\n")
			fmt.Printf("  flext-cli dbt-test --project-id abc123\n\n")
			fmt.Printf("  # Test specific models\n")
			fmt.Printf("  flext-cli dbt-test --project-id abc123 --models \"staging\"\n\n")
		case "dbt-debug":
			fmt.Printf("  # Debug project configuration\n")
			fmt.Printf("  flext-cli dbt-debug --project-id abc123\n\n")
		}

	case strings.HasPrefix(commandName, "server-"):
		switch commandName {
		case "server-start":
			fmt.Printf("  # Start server on default port\n")
			fmt.Printf("  flext-cli server-start\n\n")
			fmt.Printf("  # Start on custom port\n")
			fmt.Printf("  flext-cli server-start --port 9090\n\n")
			fmt.Printf("  # Start in background with debug\n")
			fmt.Printf("  flext-cli server-start --background --debug\n\n")
		case "server-status":
			fmt.Printf("  # Check server status\n")
			fmt.Printf("  flext-cli server-status\n\n")
			fmt.Printf("  # Check custom server\n")
			fmt.Printf("  flext-cli server-status --host prod.example.com --port 8080\n\n")
		case "server-stop":
			fmt.Printf("  # Stop server gracefully\n")
			fmt.Printf("  flext-cli server-stop\n\n")
			fmt.Printf("  # Force stop server\n")
			fmt.Printf("  flext-cli server-stop --force\n\n")
		}

	default:
		switch commandName {
		case "version":
			fmt.Printf("  # Show version information\n")
			fmt.Printf("  flext-cli version\n\n")
		case "help":
			fmt.Printf("  # Show general help\n")
			fmt.Printf("  flext-cli help\n\n")
			fmt.Printf("  # Show help for specific command\n")
			fmt.Printf("  flext-cli help pipeline-create\n\n")
		}
	}
}

func (c *HelpCommand) showGeneralHelp() {
	fmt.Printf("FLEXT CLI - A comprehensive data pipeline and ETL management platform\n\n")
	fmt.Printf("USAGE:\n")
	fmt.Printf("  flext-cli <command> [options]\n\n")
	fmt.Printf("AVAILABLE COMMANDS:\n\n")

	// Group commands by category
	categories := map[string][]Command{
		"Pipeline Management": {},
		"Singer/Meltano":      {},
		"dbt Integration":     {},
		"Server Management":   {},
		"Utilities":           {},
	}

	// Categorize commands
	for _, cmd := range c.cli.GetCommands() {
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

	// Show commands by category
	for category, cmds := range categories {
		if len(cmds) == 0 {
			continue
		}
		fmt.Printf("  %s:\n", category)
		for _, cmd := range cmds {
			fmt.Printf("    %-20s %s\n", cmd.Name(), cmd.Description())
		}
		fmt.Printf("\n")
	}

	fmt.Printf("Use 'flext-cli help <command>' for more information about a specific command.\n\n")

	fmt.Printf("EXAMPLES:\n")
	fmt.Printf("  # Create and run a simple pipeline\n")
	fmt.Printf("  flext-cli pipeline-create --name \"my-pipeline\"\n")
	fmt.Printf("  flext-cli pipeline-run --id <pipeline-id>\n\n")

	fmt.Printf("  # Work with Singer specifications\n")
	fmt.Printf("  flext-cli singer-create --name \"tap-postgres\" --type tap --executable \"/usr/bin/tap-postgres\"\n")
	fmt.Printf("  flext-cli singer-discover --id <spec-id> --config config.json\n\n")

	fmt.Printf("  # Manage dbt projects\n")
	fmt.Printf("  flext-cli dbt-init --name \"analytics\" --dir \"/path/to/project\"\n")
	fmt.Printf("  flext-cli dbt-run --project-id <project-id>\n\n")

	fmt.Printf("  # Server management\n")
	fmt.Printf("  flext-cli server-start --port 8080\n")
	fmt.Printf("  flext-cli server-status\n")
	fmt.Printf("  flext-cli server-stop\n\n")

	fmt.Printf("For more information, visit: https://github.com/flext-sh/flexcore\n")
}
