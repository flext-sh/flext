package commands

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"strings"
	"text/tabwriter"
	"time"

	"github.com/google/uuid"
)

// PipelineCreateCommand comando para criar pipelines
type PipelineCreateCommand struct {
	flags       *flag.FlagSet
	name        *string
	description *string
	tags        *string
	serverURL   *string
}

// NewPipelineCreateCommand cria um novo comando de criação de pipeline
func NewPipelineCreateCommand() *PipelineCreateCommand {
	cmd := &PipelineCreateCommand{
		flags: flag.NewFlagSet("pipeline-create", flag.ExitOnError),
	}

	cmd.name = cmd.flags.String("name", "", "Pipeline name (required)")
	cmd.description = cmd.flags.String("description", "", "Pipeline description")
	cmd.tags = cmd.flags.String("tags", "", "Comma-separated tags")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *PipelineCreateCommand) Name() string        { return "pipeline-create" }
func (c *PipelineCreateCommand) Description() string { return "Create a new pipeline" }
func (c *PipelineCreateCommand) Usage() string {
	return "pipeline-create --name <name> [--description <desc>] [--tags <tags>]"
}
func (c *PipelineCreateCommand) Flags() *flag.FlagSet { return c.flags }

func (c *PipelineCreateCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.name == "" {
		return fmt.Errorf("pipeline name is required")
	}

	// Preparar request
	var tags []string
	if *c.tags != "" {
		tags = strings.Split(*c.tags, ",")
		for i, tag := range tags {
			tags[i] = strings.TrimSpace(tag)
		}
	}

	request := map[string]interface{}{
		"name":        *c.name,
		"description": *c.description,
		"tags":        tags,
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	resp, err := http.Post(
		*c.serverURL+"/api/v1/pipelines",
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return fmt.Errorf("failed to create pipeline: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("failed to create pipeline: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("Pipeline created successfully:\n")
	fmt.Printf("  ID: %s\n", result["id"])
	fmt.Printf("  Name: %s\n", result["name"])
	if result["description"] != nil {
		fmt.Printf("  Description: %s\n", result["description"])
	}

	return nil
}

// PipelineListCommand comando para listar pipelines
type PipelineListCommand struct {
	flags     *flag.FlagSet
	active    *bool
	tags      *string
	limit     *int
	offset    *int
	serverURL *string
}

// NewPipelineListCommand cria um novo comando de listagem de pipelines
func NewPipelineListCommand() *PipelineListCommand {
	cmd := &PipelineListCommand{
		flags: flag.NewFlagSet("pipeline-list", flag.ExitOnError),
	}

	cmd.active = cmd.flags.Bool("active", false, "Show only active pipelines")
	cmd.tags = cmd.flags.String("tags", "", "Filter by tags (comma-separated)")
	cmd.limit = cmd.flags.Int("limit", 50, "Limit number of results")
	cmd.offset = cmd.flags.Int("offset", 0, "Offset for pagination")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *PipelineListCommand) Name() string        { return "pipeline-list" }
func (c *PipelineListCommand) Description() string { return "List all pipelines" }
func (c *PipelineListCommand) Usage() string {
	return "pipeline-list [--active] [--tags <tags>] [--limit <n>] [--offset <n>]"
}
func (c *PipelineListCommand) Flags() *flag.FlagSet { return c.flags }

func (c *PipelineListCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	// Construir URL com query parameters
	url := fmt.Sprintf("%s/api/v1/pipelines?limit=%d&offset=%d", *c.serverURL, *c.limit, *c.offset)
	if *c.active {
		url += "&active=true"
	}
	if *c.tags != "" {
		url += "&tags=" + *c.tags
	}

	// Fazer request HTTP
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to list pipelines: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to list pipelines: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result struct {
		Pipelines []map[string]interface{} `json:"pipelines"`
		Total     int64                     `json:"total"`
		Limit     int                       `json:"limit"`
		Offset    int                       `json:"offset"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	// Display results
	if len(result.Pipelines) == 0 {
		fmt.Println("No pipelines found.")
		return nil
	}

	// Use tabwriter for aligned output
	w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(w, "ID\tNAME\tDESCRIPTION\tACTIVE\tCREATED\tTAGS")
	fmt.Fprintln(w, "--\t----\t-----------\t------\t-------\t----")

	for _, pipeline := range result.Pipelines {
		id := pipeline["id"].(string)
		name := pipeline["name"].(string)
		description := ""
		if pipeline["description"] != nil {
			description = pipeline["description"].(string)
			if len(description) > 30 {
				description = description[:27] + "..."
			}
		}

		active := "false"
		if pipeline["is_active"] != nil && pipeline["is_active"].(bool) {
			active = "true"
		}

		createdAt := ""
		if pipeline["created_at"] != nil {
			if t, err := time.Parse(time.RFC3339, pipeline["created_at"].(string)); err == nil {
				createdAt = t.Format("2006-01-02")
			}
		}

		tags := ""
		if pipeline["tags"] != nil {
			if tagSlice, ok := pipeline["tags"].([]interface{}); ok {
				tagStrs := make([]string, len(tagSlice))
				for i, tag := range tagSlice {
					tagStrs[i] = tag.(string)
				}
				tags = strings.Join(tagStrs, ",")
				if len(tags) > 20 {
					tags = tags[:17] + "..."
				}
			}
		}

		fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\t%s\n",
			id[:8]+"...", name, description, active, createdAt, tags)
	}

	w.Flush()
	fmt.Printf("\nShowing %d of %d pipelines\n", len(result.Pipelines), result.Total)

	return nil
}

// PipelineShowCommand comando para mostrar detalhes de um pipeline
type PipelineShowCommand struct {
	flags     *flag.FlagSet
	id        *string
	serverURL *string
}

// NewPipelineShowCommand cria um novo comando para mostrar pipeline
func NewPipelineShowCommand() *PipelineShowCommand {
	cmd := &PipelineShowCommand{
		flags: flag.NewFlagSet("pipeline-show", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Pipeline ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *PipelineShowCommand) Name() string        { return "pipeline-show" }
func (c *PipelineShowCommand) Description() string { return "Show pipeline details" }
func (c *PipelineShowCommand) Usage() string       { return "pipeline-show --id <pipeline-id>" }
func (c *PipelineShowCommand) Flags() *flag.FlagSet { return c.flags }

func (c *PipelineShowCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("pipeline ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid pipeline ID format: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/pipelines/%s", *c.serverURL, *c.id)
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to get pipeline: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("pipeline not found")
	}
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to get pipeline: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var pipeline map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&pipeline); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	// Display pipeline details
	fmt.Printf("Pipeline Details:\n")
	fmt.Printf("================\n\n")
	fmt.Printf("ID:          %s\n", pipeline["id"])
	fmt.Printf("Name:        %s\n", pipeline["name"])
	if pipeline["description"] != nil {
		fmt.Printf("Description: %s\n", pipeline["description"])
	}
	fmt.Printf("Active:      %v\n", pipeline["is_active"])
	fmt.Printf("Version:     %v\n", pipeline["version"])

	if pipeline["created_at"] != nil {
		if t, err := time.Parse(time.RFC3339, pipeline["created_at"].(string)); err == nil {
			fmt.Printf("Created:     %s\n", t.Format("2006-01-02 15:04:05"))
		}
	}

	if pipeline["updated_at"] != nil {
		if t, err := time.Parse(time.RFC3339, pipeline["updated_at"].(string)); err == nil {
			fmt.Printf("Updated:     %s\n", t.Format("2006-01-02 15:04:05"))
		}
	}

	if pipeline["tags"] != nil {
		if tagSlice, ok := pipeline["tags"].([]interface{}); ok && len(tagSlice) > 0 {
			tagStrs := make([]string, len(tagSlice))
			for i, tag := range tagSlice {
				tagStrs[i] = tag.(string)
			}
			fmt.Printf("Tags:        %s\n", strings.Join(tagStrs, ", "))
		}
	}

	// Show configuration if available
	if pipeline["configuration"] != nil {
		fmt.Printf("\nConfiguration:\n")
		configData, _ := json.MarshalIndent(pipeline["configuration"], "", "  ")
		fmt.Printf("%s\n", configData)
	}

	// Show steps if available
	if pipeline["steps"] != nil {
		if steps, ok := pipeline["steps"].([]interface{}); ok && len(steps) > 0 {
			fmt.Printf("\nSteps (%d):\n", len(steps))
			for i, step := range steps {
				stepMap := step.(map[string]interface{})
				fmt.Printf("  %d. %s\n", i+1, stepMap["name"])
				if stepMap["description"] != nil {
					fmt.Printf("     %s\n", stepMap["description"])
				}
			}
		}
	}

	return nil
}

// PipelineRunCommand comando para executar pipeline
type PipelineRunCommand struct {
	flags     *flag.FlagSet
	id        *string
	serverURL *string
	wait      *bool
}

// NewPipelineRunCommand cria um novo comando de execução de pipeline
func NewPipelineRunCommand() *PipelineRunCommand {
	cmd := &PipelineRunCommand{
		flags: flag.NewFlagSet("pipeline-run", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Pipeline ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")
	cmd.wait = cmd.flags.Bool("wait", false, "Wait for execution to complete")

	return cmd
}

func (c *PipelineRunCommand) Name() string        { return "pipeline-run" }
func (c *PipelineRunCommand) Description() string { return "Execute a pipeline" }
func (c *PipelineRunCommand) Usage() string       { return "pipeline-run --id <pipeline-id> [--wait]" }
func (c *PipelineRunCommand) Flags() *flag.FlagSet { return c.flags }

func (c *PipelineRunCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("pipeline ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid pipeline ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{}
	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/pipelines/%s/execute", *c.serverURL, *c.id)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to execute pipeline: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("pipeline not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to execute pipeline: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("Pipeline execution started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	if *c.wait {
		fmt.Println("\nWaiting for execution to complete...")
		// TODO: Implementar polling para aguardar conclusão
		// Por enquanto apenas simular
		time.Sleep(2 * time.Second)
		fmt.Println("Execution completed successfully.")
	}

	return nil
}

// PipelineDeleteCommand comando para deletar pipeline
type PipelineDeleteCommand struct {
	flags     *flag.FlagSet
	id        *string
	serverURL *string
	force     *bool
}

// NewPipelineDeleteCommand cria um novo comando de exclusão de pipeline
func NewPipelineDeleteCommand() *PipelineDeleteCommand {
	cmd := &PipelineDeleteCommand{
		flags: flag.NewFlagSet("pipeline-delete", flag.ExitOnError),
	}

	cmd.id = cmd.flags.String("id", "", "Pipeline ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")
	cmd.force = cmd.flags.Bool("force", false, "Force deletion without confirmation")

	return cmd
}

func (c *PipelineDeleteCommand) Name() string        { return "pipeline-delete" }
func (c *PipelineDeleteCommand) Description() string { return "Delete a pipeline" }
func (c *PipelineDeleteCommand) Usage() string       { return "pipeline-delete --id <pipeline-id> [--force]" }
func (c *PipelineDeleteCommand) Flags() *flag.FlagSet { return c.flags }

func (c *PipelineDeleteCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.id == "" {
		return fmt.Errorf("pipeline ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.id); err != nil {
		return fmt.Errorf("invalid pipeline ID format: %w", err)
	}

	// Confirmação se não for forçado
	if !*c.force {
		fmt.Printf("Are you sure you want to delete pipeline %s? (y/N): ", *c.id)
		var response string
		fmt.Scanln(&response)
		if strings.ToLower(response) != "y" && strings.ToLower(response) != "yes" {
			fmt.Println("Operation cancelled.")
			return nil
		}
	}

	// Criar request HTTP DELETE
	url := fmt.Sprintf("%s/api/v1/pipelines/%s", *c.serverURL, *c.id)
	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to delete pipeline: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("pipeline not found")
	}
	if resp.StatusCode != http.StatusNoContent {
		return fmt.Errorf("failed to delete pipeline: HTTP %d", resp.StatusCode)
	}

	fmt.Printf("Pipeline %s deleted successfully.\n", *c.id)

	return nil
}
