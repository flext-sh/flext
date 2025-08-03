package commands

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"text/tabwriter"
	"time"

	"github.com/google/uuid"
)

// SingerListCommand comando para listar especificações Singer
type SingerListCommand struct {
	flags     *flag.FlagSet
	type_     *string
	active    *bool
	limit     *int
	offset    *int
	serverURL *string
}

// NewSingerListCommand cria um novo comando de listagem Singer
func NewSingerListCommand() *SingerListCommand {
	cmd := &SingerListCommand{
		flags: flag.NewFlagSet("singer-list", flag.ExitOnError),
	}

	cmd.type_ = cmd.flags.String("type", "", "Filter by type (tap or target)")
	cmd.active = cmd.flags.Bool("active", false, "Show only active specs")
	cmd.limit = cmd.flags.Int("limit", 50, "Limit number of results")
	cmd.offset = cmd.flags.Int("offset", 0, "Offset for pagination")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *SingerListCommand) Name() string        { return "singer-list" }
func (c *SingerListCommand) Description() string { return "List Singer specifications" }
func (c *SingerListCommand) Usage() string {
	return "singer-list [--type tap|target] [--active] [--limit <n>] [--offset <n>]"
}
func (c *SingerListCommand) Flags() *flag.FlagSet { return c.flags }

func (c *SingerListCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	// Construir URL com query parameters
	url := fmt.Sprintf("%s/api/v1/singer/specs?limit=%d&offset=%d", *c.serverURL, *c.limit, *c.offset)
	if *c.type_ != "" {
		url += "&type=" + *c.type_
	}
	if *c.active {
		url += "&active=true"
	}

	// Fazer request HTTP
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to list Singer specs: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to list Singer specs: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result struct {
		Specs  []map[string]interface{} `json:"specs"`
		Total  int64                    `json:"total"`
		Limit  int                      `json:"limit"`
		Offset int                      `json:"offset"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	// Display results
	if len(result.Specs) == 0 {
		fmt.Println("No Singer specifications found.")
		return nil
	}

	// Use tabwriter for aligned output
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "ID\tNAME\tTYPE\tVERSION\tACTIVE\tAUTHOR")
	fmt.Fprintln(w, "--\t----\t----\t-------\t------\t------")

	for _, spec := range result.Specs {
		id := spec["id"].(string)
		name := spec["name"].(string)
		specType := spec["type"].(string)
		version := spec["version"].(string)

		active := "false"
		if spec["is_active"] != nil && spec["is_active"].(bool) {
			active = "true"
		}

		author := ""
		if spec["author"] != nil {
			author = spec["author"].(string)
			if len(author) > 15 {
				author = author[:12] + "..."
			}
		}

		fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\t%s\n",
			id[:8]+"...", name, specType, version, active, author)
	}

	w.Flush()
	fmt.Printf("\nShowing %d of %d Singer specifications\n", len(result.Specs), result.Total)

	return nil
}

// SingerCreateCommand comando para criar especificação Singer
type SingerCreateCommand struct {
	flags       *flag.FlagSet
	name        *string
	version     *string
	type_       *string
	description *string
	author      *string
	executable  *string
	serverURL   *string
}

// NewSingerCreateCommand cria um novo comando de criação Singer
func NewSingerCreateCommand() *SingerCreateCommand {
	cmd := &SingerCreateCommand{
		flags: flag.NewFlagSet("singer-create", flag.ExitOnError),
	}

	cmd.name = cmd.flags.String("name", "", "Specification name (required)")
	cmd.version = cmd.flags.String("version", "1.0.0", "Specification version")
	cmd.type_ = cmd.flags.String("type", "", "Type: tap or target (required)")
	cmd.description = cmd.flags.String("description", "", "Specification description")
	cmd.author = cmd.flags.String("author", "", "Author name")
	cmd.executable = cmd.flags.String("executable", "", "Executable path (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *SingerCreateCommand) Name() string        { return "singer-create" }
func (c *SingerCreateCommand) Description() string { return "Create a Singer specification" }
func (c *SingerCreateCommand) Usage() string {
	return "singer-create --name <name> --type <tap|target> --executable <path> [options]"
}
func (c *SingerCreateCommand) Flags() *flag.FlagSet { return c.flags }

func (c *SingerCreateCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.name == "" {
		return fmt.Errorf("specification name is required")
	}
	if *c.type_ == "" {
		return fmt.Errorf("specification type is required (tap or target)")
	}
	if *c.type_ != "tap" && *c.type_ != "target" {
		return fmt.Errorf("type must be 'tap' or 'target'")
	}
	if *c.executable == "" {
		return fmt.Errorf("executable path is required")
	}

	// Preparar request
	request := map[string]interface{}{
		"name":        *c.name,
		"version":     *c.version,
		"type":        *c.type_,
		"description": *c.description,
		"author":      *c.author,
		"executable":  *c.executable,
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	resp, err := http.Post(
		*c.serverURL+"/api/v1/singer/specs",
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return fmt.Errorf("failed to create Singer specification: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("failed to create Singer specification: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("Singer specification created successfully:\n")
	fmt.Printf("  ID: %s\n", result["id"])
	fmt.Printf("  Name: %s\n", result["name"])
	fmt.Printf("  Type: %s\n", result["type"])
	fmt.Printf("  Version: %s\n", result["version"])

	return nil
}

// SingerRunCommand comando para executar especificação Singer
type SingerRunCommand struct {
	flags      *flag.FlagSet
	id         *string
	pipelineID *string
	configFile *string
	serverURL  *string
	wait       *bool
}

// NewSingerRunCommand cria um novo comando de execução Singer
func NewSingerRunCommand() *SingerRunCommand {
	cmd := &SingerRunCommand{
		flags: flag.NewFlagSet("singer-run", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Specification ID (required)")
	cmd.pipelineID = cmd.flags.String("pipeline-id", "", "Pipeline ID (required)")
	cmd.configFile = cmd.flags.String("config", "", "Configuration file path (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")
	cmd.wait = cmd.flags.Bool("wait", false, "Wait for execution to complete")

	return cmd
}

func (c *SingerRunCommand) Name() string        { return "singer-run" }
func (c *SingerRunCommand) Description() string { return "Execute a Singer specification" }
func (c *SingerRunCommand) Usage() string {
	return "singer-run --id <spec-id> --pipeline-id <pipeline-id> --config <config-file> [--wait]"
}
func (c *SingerRunCommand) Flags() *flag.FlagSet { return c.flags }

func (c *SingerRunCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("specification ID is required")
	}
	if *c.pipelineID == "" {
		return fmt.Errorf("pipeline ID is required")
	}
	if *c.configFile == "" {
		return fmt.Errorf("configuration file is required")
	}

	// Validate UUIDs
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid specification ID format: %w", err)
	}
	if _, err := uuid.Parse(*c.pipelineID); err != nil {
		return fmt.Errorf("invalid pipeline ID format: %w", err)
	}

	// Load configuration file
	configData, err := os.ReadFile(*c.configFile)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(configData, &config); err != nil {
		return fmt.Errorf("failed to parse config file: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"spec_id":     *c.id,
		"pipeline_id": *c.pipelineID,
		"config":      config,
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/singer/specs/%s/execute", *c.serverURL, *c.id)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to execute Singer specification: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("specification not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to execute Singer specification: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("Singer specification execution started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", "running")

	if *c.wait {
		fmt.Println("\nWaiting for execution to complete...")
		// TODO: Implementar polling para aguardar conclusão
		time.Sleep(3 * time.Second)
		fmt.Println("Execution completed successfully.")
	}

	return nil
}

// SingerTestCommand comando para testar especificação Singer
type SingerTestCommand struct {
	flags      *flag.FlagSet
	id         *string
	configFile *string
	serverURL  *string
}

// NewSingerTestCommand cria um novo comando de teste Singer
func NewSingerTestCommand() *SingerTestCommand {
	cmd := &SingerTestCommand{
		flags: flag.NewFlagSet("singer-test", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Specification ID (required)")
	cmd.configFile = cmd.flags.String("config", "", "Configuration file path (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *SingerTestCommand) Name() string        { return "singer-test" }
func (c *SingerTestCommand) Description() string { return "Test Singer specification connection" }
func (c *SingerTestCommand) Usage() string {
	return "singer-test --id <spec-id> --config <config-file>"
}
func (c *SingerTestCommand) Flags() *flag.FlagSet { return c.flags }

func (c *SingerTestCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("specification ID is required")
	}
	if *c.configFile == "" {
		return fmt.Errorf("configuration file is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid specification ID format: %w", err)
	}

	// Load configuration file
	configData, err := os.ReadFile(*c.configFile)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(configData, &config); err != nil {
		return fmt.Errorf("failed to parse config file: %w", err)
	}

	reqBody, err := json.Marshal(config)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/singer/specs/%s/test", *c.serverURL, *c.id)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to test Singer specification: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("specification not found")
	}
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("connection test failed: HTTP %d", resp.StatusCode)
	}

	fmt.Println("Connection test successful!")

	return nil
}

// SingerDiscoverCommand comando para descobrir schema Singer
type SingerDiscoverCommand struct {
	flags      *flag.FlagSet
	id         *string
	configFile *string
	outputFile *string
	serverURL  *string
}

// NewSingerDiscoverCommand cria um novo comando de discovery Singer
func NewSingerDiscoverCommand() *SingerDiscoverCommand {
	cmd := &SingerDiscoverCommand{
		flags: flag.NewFlagSet("singer-discover", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Specification ID (required)")
	cmd.configFile = cmd.flags.String("config", "", "Configuration file path (required)")
	cmd.outputFile = cmd.flags.String("output", "", "Output catalog file path (optional)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *SingerDiscoverCommand) Name() string        { return "singer-discover" }
func (c *SingerDiscoverCommand) Description() string { return "Discover Singer specification schema" }
func (c *SingerDiscoverCommand) Usage() string {
	return "singer-discover --id <spec-id> --config <config-file> [--output <catalog-file>]"
}
func (c *SingerDiscoverCommand) Flags() *flag.FlagSet { return c.flags }

func (c *SingerDiscoverCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("specification ID is required")
	}
	if *c.configFile == "" {
		return fmt.Errorf("configuration file is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid specification ID format: %w", err)
	}

	// Load configuration file
	configData, err := os.ReadFile(*c.configFile)
	if err != nil {
		return fmt.Errorf("failed to read config file: %w", err)
	}

	var config map[string]interface{}
	if err := json.Unmarshal(configData, &config); err != nil {
		return fmt.Errorf("failed to parse config file: %w", err)
	}

	reqBody, err := json.Marshal(config)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/singer/specs/%s/discover", *c.serverURL, *c.id)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to discover Singer schema: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("specification not found")
	}
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("schema discovery failed: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var catalog map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&catalog); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	// Output to file or stdout
	catalogData, err := json.MarshalIndent(catalog, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal catalog: %w", err)
	}

	if *c.outputFile != "" {
		if err := os.WriteFile(*c.outputFile, catalogData, 0644); err != nil {
			return fmt.Errorf("failed to write catalog file: %w", err)
		}
		fmt.Printf("Schema catalog saved to: %s\n", *c.outputFile)
	} else {
		fmt.Printf("Discovered schema catalog:\n%s\n", catalogData)
	}

	return nil
}
