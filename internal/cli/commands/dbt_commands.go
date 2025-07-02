package commands

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"

	"github.com/google/uuid"
)

// DbtInitCommand comando para inicializar projeto dbt
type DbtInitCommand struct {
	flags       *flag.FlagSet
	projectName *string
	profileName *string
	projectDir  *string
	serverURL   *string
}

// NewDbtInitCommand cria um novo comando de inicialização dbt
func NewDbtInitCommand() *DbtInitCommand {
	cmd := &DbtInitCommand{
		flags: flag.NewFlagSet("dbt-init", flag.ExitOnError),
	}

	cmd.projectName = cmd.flags.String("name", "", "Project name (required)")
	cmd.profileName = cmd.flags.String("profile", "", "Profile name (optional)")
	cmd.projectDir = cmd.flags.String("dir", "", "Project directory (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtInitCommand) Name() string        { return "dbt-init" }
func (c *DbtInitCommand) Description() string { return "Initialize a new dbt project" }
func (c *DbtInitCommand) Usage() string {
	return "dbt-init --name <project-name> --dir <project-dir> [--profile <profile-name>]"
}
func (c *DbtInitCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtInitCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectName == "" {
		return fmt.Errorf("project name is required")
	}
	if *c.projectDir == "" {
		return fmt.Errorf("project directory is required")
	}

	// Default profile name to project name if not provided
	profileName := *c.profileName
	if profileName == "" {
		profileName = *c.projectName
	}

	// Preparar request
	request := map[string]interface{}{
		"name":         *c.projectName,
		"profile_name": profileName,
		"project_dir":  *c.projectDir,
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	resp, err := http.Post(
		*c.serverURL+"/api/v1/dbt/projects",
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return fmt.Errorf("failed to initialize dbt project: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("failed to initialize dbt project: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt project initialized successfully:\n")
	fmt.Printf("  ID: %s\n", result["id"])
	fmt.Printf("  Name: %s\n", result["name"])
	fmt.Printf("  Profile: %s\n", result["profile_name"])
	fmt.Printf("  Directory: %s\n", result["project_dir"])

	return nil
}

// DbtRunCommand comando para executar modelos dbt
type DbtRunCommand struct {
	flags     *flag.FlagSet
	projectID *string
	models    *string
	exclude   *string
	serverURL *string
}

// NewDbtRunCommand cria um novo comando de execução dbt
func NewDbtRunCommand() *DbtRunCommand {
	cmd := &DbtRunCommand{
		flags: flag.NewFlagSet("dbt-run", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.models = cmd.flags.String("models", "", "Specific models to run")
	cmd.exclude = cmd.flags.String("exclude", "", "Models to exclude")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtRunCommand) Name() string        { return "dbt-run" }
func (c *DbtRunCommand) Description() string { return "Run dbt models" }
func (c *DbtRunCommand) Usage() string {
	return "dbt-run --project-id <project-id> [--models <models>] [--exclude <models>]"
}
func (c *DbtRunCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtRunCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if err := c.validateParameters(); err != nil {
		return err
	}

	request := c.buildRequest()
	reqBody, err := c.marshalRequest(request)
	if err != nil {
		return err
	}

	resp, err := c.executeHTTPRequest(reqBody)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if err := c.validateResponse(resp); err != nil {
		return err
	}

	return c.parseAndDisplayResult(resp)
}

// DbtTestCommand comando para executar testes dbt
type DbtTestCommand struct {
	flags     *flag.FlagSet
	projectID *string
	models    *string
	serverURL *string
}

// NewDbtTestCommand cria um novo comando de teste dbt
func NewDbtTestCommand() *DbtTestCommand {
	cmd := &DbtTestCommand{
		flags: flag.NewFlagSet("dbt-test", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.models = cmd.flags.String("models", "", "Specific models to test")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtTestCommand) Name() string        { return "dbt-test" }
func (c *DbtTestCommand) Description() string { return "Run dbt tests" }
func (c *DbtTestCommand) Usage() string {
	return "dbt-test --project-id <project-id> [--models <models>]"
}
func (c *DbtTestCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtTestCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "test",
	}

	if *c.models != "" {
		request["models"] = *c.models
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to run dbt tests: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to run dbt tests: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt test started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// DbtCompileCommand comando para compilar modelos dbt
type DbtCompileCommand struct {
	flags     *flag.FlagSet
	projectID *string
	models    *string
	serverURL *string
}

// NewDbtCompileCommand cria um novo comando de compilação dbt
func NewDbtCompileCommand() *DbtCompileCommand {
	cmd := &DbtCompileCommand{
		flags: flag.NewFlagSet("dbt-compile", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.models = cmd.flags.String("models", "", "Specific models to compile")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtCompileCommand) Name() string        { return "dbt-compile" }
func (c *DbtCompileCommand) Description() string { return "Compile dbt models" }
func (c *DbtCompileCommand) Usage() string {
	return "dbt-compile --project-id <project-id> [--models <models>]"
}
func (c *DbtCompileCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtCompileCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "compile",
	}

	if *c.models != "" {
		request["models"] = *c.models
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to compile dbt models: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to compile dbt models: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt compile started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// DbtSeedCommand comando para executar seeds dbt
type DbtSeedCommand struct {
	flags     *flag.FlagSet
	projectID *string
	select_   *string
	serverURL *string
}

// NewDbtSeedCommand cria um novo comando de seed dbt
func NewDbtSeedCommand() *DbtSeedCommand {
	cmd := &DbtSeedCommand{
		flags: flag.NewFlagSet("dbt-seed", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.select_ = cmd.flags.String("select", "", "Specific seeds to run")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtSeedCommand) Name() string        { return "dbt-seed" }
func (c *DbtSeedCommand) Description() string { return "Run dbt seeds" }
func (c *DbtSeedCommand) Usage() string {
	return "dbt-seed --project-id <project-id> [--select <seeds>]"
}
func (c *DbtSeedCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtSeedCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "seed",
	}

	if *c.select_ != "" {
		request["select"] = *c.select_
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to run dbt seeds: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to run dbt seeds: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt seed started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// DbtSnapshotCommand comando para executar snapshots dbt
type DbtSnapshotCommand struct {
	flags     *flag.FlagSet
	projectID *string
	select_   *string
	serverURL *string
}

// NewDbtSnapshotCommand cria um novo comando de snapshot dbt
func NewDbtSnapshotCommand() *DbtSnapshotCommand {
	cmd := &DbtSnapshotCommand{
		flags: flag.NewFlagSet("dbt-snapshot", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.select_ = cmd.flags.String("select", "", "Specific snapshots to run")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtSnapshotCommand) Name() string        { return "dbt-snapshot" }
func (c *DbtSnapshotCommand) Description() string { return "Run dbt snapshots" }
func (c *DbtSnapshotCommand) Usage() string {
	return "dbt-snapshot --project-id <project-id> [--select <snapshots>]"
}
func (c *DbtSnapshotCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtSnapshotCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "snapshot",
	}

	if *c.select_ != "" {
		request["select"] = *c.select_
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to run dbt snapshots: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to run dbt snapshots: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt snapshot started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// DbtDebugCommand comando para debug de projeto dbt
type DbtDebugCommand struct {
	flags     *flag.FlagSet
	projectID *string
	serverURL *string
}

// NewDbtDebugCommand cria um novo comando de debug dbt
func NewDbtDebugCommand() *DbtDebugCommand {
	cmd := &DbtDebugCommand{
		flags: flag.NewFlagSet("dbt-debug", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtDebugCommand) Name() string        { return "dbt-debug" }
func (c *DbtDebugCommand) Description() string { return "Debug dbt project configuration" }
func (c *DbtDebugCommand) Usage() string       { return "dbt-debug --project-id <project-id>" }
func (c *DbtDebugCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtDebugCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/debug", *c.serverURL, *c.projectID)
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to debug dbt project: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to debug dbt project: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	// Display debug information
	fmt.Printf("dbt Project Debug Information:\n")
	fmt.Printf("==============================\n\n")

	if result["project"] != nil {
		project := result["project"].(map[string]interface{})
		fmt.Printf("Project: %s\n", project["name"])
		fmt.Printf("Profile: %s\n", project["profile_name"])
		fmt.Printf("Directory: %s\n", project["project_dir"])
	}

	if result["connection"] != nil {
		connection := result["connection"].(map[string]interface{})
		fmt.Printf("\nConnection Status: %s\n", connection["status"])
		if connection["error"] != nil {
			fmt.Printf("Error: %s\n", connection["error"])
		}
	}

	if result["dbt_version"] != nil {
		fmt.Printf("\ndbt Version: %s\n", result["dbt_version"])
	}

	return nil
}

// DbtDepsCommand comando para instalar dependências dbt
type DbtDepsCommand struct {
	flags     *flag.FlagSet
	projectID *string
	serverURL *string
}

// NewDbtDepsCommand cria um novo comando de deps dbt
func NewDbtDepsCommand() *DbtDepsCommand {
	cmd := &DbtDepsCommand{
		flags: flag.NewFlagSet("dbt-deps", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtDepsCommand) Name() string        { return "dbt-deps" }
func (c *DbtDepsCommand) Description() string { return "Install dbt dependencies" }
func (c *DbtDepsCommand) Usage() string       { return "dbt-deps --project-id <project-id>" }
func (c *DbtDepsCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtDepsCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "deps",
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to install dbt dependencies: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to install dbt dependencies: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt deps started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// DbtCleanCommand comando para limpar artefatos dbt
type DbtCleanCommand struct {
	flags     *flag.FlagSet
	projectID *string
	serverURL *string
}

// NewDbtCleanCommand cria um novo comando de clean dbt
func NewDbtCleanCommand() *DbtCleanCommand {
	cmd := &DbtCleanCommand{
		flags: flag.NewFlagSet("dbt-clean", flag.ExitOnError),
	}

	cmd.projectID = cmd.flags.String("project-id", "", "dbt project ID (required)")
	cmd.serverURL = cmd.flags.String("server", "http://localhost:8080", "FLEXT server URL")

	return cmd
}

func (c *DbtCleanCommand) Name() string        { return "dbt-clean" }
func (c *DbtCleanCommand) Description() string { return "Clean dbt artifacts" }
func (c *DbtCleanCommand) Usage() string       { return "dbt-clean --project-id <project-id>" }
func (c *DbtCleanCommand) Flags() *flag.FlagSet { return c.flags }

func (c *DbtCleanCommand) Run(ctx context.Context, args []string) error {
	if err := c.flags.Parse(args); err != nil {
		return err
	}

	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	// Validate UUID
	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	// Preparar request
	request := map[string]interface{}{
		"command": "clean",
	}

	reqBody, err := json.Marshal(request)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	// Fazer request HTTP
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return fmt.Errorf("failed to clean dbt artifacts: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to clean dbt artifacts: HTTP %d", resp.StatusCode)
	}

	// Parse response
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt clean started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

// Helper methods for DbtRunCommand

func (c *DbtRunCommand) validateParameters() error {
	if *c.projectID == "" {
		return fmt.Errorf("project ID is required")
	}

	if _, err := uuid.Parse(*c.projectID); err != nil {
		return fmt.Errorf("invalid project ID format: %w", err)
	}

	return nil
}

func (c *DbtRunCommand) buildRequest() map[string]interface{} {
	request := map[string]interface{}{
		"command": "run",
	}

	if *c.models != "" {
		request["models"] = *c.models
	}
	if *c.exclude != "" {
		request["exclude"] = *c.exclude
	}

	return request
}

func (c *DbtRunCommand) marshalRequest(request map[string]interface{}) ([]byte, error) {
	reqBody, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}
	return reqBody, nil
}

func (c *DbtRunCommand) executeHTTPRequest(reqBody []byte) (*http.Response, error) {
	url := fmt.Sprintf("%s/api/v1/dbt/projects/%s/execute", *c.serverURL, *c.projectID)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("failed to run dbt models: %w", err)
	}
	return resp, nil
}

func (c *DbtRunCommand) validateResponse(resp *http.Response) error {
	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("project not found")
	}
	if resp.StatusCode != http.StatusAccepted {
		return fmt.Errorf("failed to run dbt models: HTTP %d", resp.StatusCode)
	}
	return nil
}

func (c *DbtRunCommand) parseAndDisplayResult(resp *http.Response) error {
	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return fmt.Errorf("failed to parse response: %w", err)
	}

	fmt.Printf("dbt run started:\n")
	fmt.Printf("  Execution ID: %s\n", result["execution_id"])
	fmt.Printf("  Status: %s\n", result["status"])

	return nil
}

