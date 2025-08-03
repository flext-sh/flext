package services

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/pkg/domain/singer/application/ports"
	"github.com/flext-sh/flext/pkg/domain/singer/domain/entities"
	"github.com/flext-sh/flext/pkg/domain/singer/domain/services"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// SingerService coordena operações do bounded context Singer
type SingerService struct {
	specRepo       ports.SingerSpecRepository
	executionRepo  ports.SingerExecutionRepository
	stateRepo      ports.SingerStateRepository
	eventPublisher ports.EventPublisher
	executor       *services.SingerExecutor
	logger         logging.Logger
}

// CreateSpecRequest request para criar especificação Singer
type CreateSpecRequest struct {
	Name            string                      `json:"name" validate:"required,min=1,max=100"`
	Version         string                      `json:"version" validate:"required"`
	Type            entities.SingerType         `json:"type" validate:"required,oneof=tap target"`
	Description     string                      `json:"description" validate:"max=500"`
	Author          string                      `json:"author" validate:"max=100"`
	Executable      string                      `json:"executable" validate:"required"`
	Settings        entities.SingerSettings     `json:"settings"`
	Capabilities    entities.SingerCapabilities `json:"capabilities"`
	ConfigTemplate  map[string]interface{}      `json:"config_template"`
	EnvironmentVars map[string]string           `json:"environment_vars"`
}

// UpdateSpecRequest request para atualizar especificação Singer
type UpdateSpecRequest struct {
	Description     *string                      `json:"description,omitempty" validate:"omitempty,max=500"`
	Author          *string                      `json:"author,omitempty" validate:"omitempty,max=100"`
	Settings        *entities.SingerSettings     `json:"settings,omitempty"`
	Capabilities    *entities.SingerCapabilities `json:"capabilities,omitempty"`
	ConfigTemplate  map[string]interface{}       `json:"config_template,omitempty"`
	EnvironmentVars map[string]string            `json:"environment_vars,omitempty"`
}

// ExecuteSpecRequest request para executar especificação Singer
type ExecuteSpecRequest struct {
	SpecID     uuid.UUID              `json:"spec_id" validate:"required"`
	PipelineID uuid.UUID              `json:"pipeline_id" validate:"required"`
	Config     map[string]interface{} `json:"config" validate:"required"`
	Catalog    *entities.Catalog      `json:"catalog,omitempty"`
	State      *entities.State        `json:"state,omitempty"`
	Properties []string               `json:"properties,omitempty"`
	Discover   bool                   `json:"discover,omitempty"`
	Test       bool                   `json:"test,omitempty"`
}

// SpecResponse resposta com especificação Singer
type SpecResponse struct {
	*entities.SingerSpec
}

// ExecutionResponse resposta com execução Singer
type ExecutionResponse struct {
	*entities.SingerExecution
}

// ExecutionResult resultado de execução
type ExecutionResult struct {
	ExecutionID      uuid.UUID                 `json:"execution_id"`
	Success          bool                      `json:"success"`
	RecordsProcessed int64                     `json:"records_processed"`
	Duration         int64                     `json:"duration_ms"`
	OutputState      *entities.State           `json:"output_state,omitempty"`
	OutputFiles      []entities.OutputFile     `json:"output_files"`
	Metrics          entities.ExecutionMetrics `json:"metrics"`
	Error            string                    `json:"error,omitempty"`
}

// ListSpecsRequest request para listar especificações
type ListSpecsRequest struct {
	Type   *entities.SingerType `json:"type,omitempty"`
	Active *bool                `json:"active,omitempty"`
	Query  string               `json:"query,omitempty"`
	Limit  int                  `json:"limit,omitempty"`
	Offset int                  `json:"offset,omitempty"`
}

// ListSpecsResponse resposta para listagem de especificações
type ListSpecsResponse struct {
	Specs  []*entities.SingerSpec `json:"specs"`
	Total  int64                  `json:"total"`
	Limit  int                    `json:"limit"`
	Offset int                    `json:"offset"`
}

// SingerServiceDependencies contains all dependencies for SingerService
type SingerServiceDependencies struct {
	SpecRepo       ports.SingerSpecRepository
	ExecutionRepo  ports.SingerExecutionRepository
	StateRepo      ports.SingerStateRepository
	EventPublisher ports.EventPublisher
	Executor       *services.SingerExecutor
	Logger         logging.Logger
}

// NewSingerService cria um novo serviço Singer
func NewSingerService(deps SingerServiceDependencies) *SingerService {
	return &SingerService{
		specRepo:       deps.SpecRepo,
		executionRepo:  deps.ExecutionRepo,
		stateRepo:      deps.StateRepo,
		eventPublisher: deps.EventPublisher,
		executor:       deps.Executor,
		logger:         deps.Logger,
	}
}

// CreateSpec cria uma nova especificação Singer
func (s *SingerService) CreateSpec(ctx context.Context, req CreateSpecRequest) (*SpecResponse, error) {
	s.logger.Info("Creating Singer specification",
		logging.F("name", req.Name),
		logging.F("type", string(req.Type)),
		logging.F("version", req.Version),
	)

	// Verificar se já existe especificação com mesmo nome
	exists, err := s.specRepo.ExistsByName(ctx, req.Name)
	if err != nil {
		return nil, fmt.Errorf("failed to check if spec exists: %w", err)
	}
	if exists {
		return nil, fmt.Errorf("specification with name '%s' already exists", req.Name)
	}

	// Criar especificação
	spec, err := entities.NewSingerSpec(req.Name, req.Version, req.Type, req.Executable)
	if err != nil {
		return nil, fmt.Errorf("failed to create specification: %w", err)
	}

	// Aplicar campos opcionais
	spec.Description = req.Description
	spec.Author = req.Author
	spec.Settings = req.Settings
	spec.Capabilities = req.Capabilities
	if req.ConfigTemplate != nil {
		spec.ConfigTemplate = req.ConfigTemplate
	}
	if req.EnvironmentVars != nil {
		spec.EnvironmentVars = req.EnvironmentVars
	}

	// Salvar especificação
	if err := s.specRepo.Save(ctx, spec); err != nil {
		return nil, fmt.Errorf("failed to save specification: %w", err)
	}

	// Publicar eventos
	for _, event := range spec.GetEvents() {
		if err := s.eventPublisher.PublishEvent(ctx, event); err != nil {
			s.logger.Warn("Failed to publish event",
				logging.F("error", err.Error()),
				logging.F("event_type", event.GetEventType()),
			)
		}
	}
	spec.ClearEvents()

	s.logger.Info("Singer specification created successfully",
		logging.F("spec_id", spec.GetID().String()),
		logging.F("name", spec.Name),
	)

	return &SpecResponse{SingerSpec: spec}, nil
}

// GetSpec obtém uma especificação Singer por ID
func (s *SingerService) GetSpec(ctx context.Context, id uuid.UUID) (*SpecResponse, error) {
	spec, err := s.specRepo.FindByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return nil, fmt.Errorf("specification not found")
	}

	return &SpecResponse{SingerSpec: spec}, nil
}

// UpdateSpec atualiza uma especificação Singer
func (s *SingerService) UpdateSpec(ctx context.Context, id uuid.UUID, req UpdateSpecRequest) (*SpecResponse, error) {
	s.logger.Info("Updating Singer specification",
		logging.F("spec_id", id.String()),
	)

	// Buscar especificação existente
	spec, err := s.specRepo.FindByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return nil, fmt.Errorf("specification not found")
	}

	// Aplicar atualizações
	if req.Description != nil {
		spec.Description = *req.Description
	}
	if req.Author != nil {
		spec.Author = *req.Author
	}
	if req.Settings != nil {
		spec.UpdateSettings(*req.Settings)
	}
	if req.Capabilities != nil {
		spec.UpdateCapabilities(*req.Capabilities)
	}
	if req.ConfigTemplate != nil {
		spec.ConfigTemplate = req.ConfigTemplate
	}
	if req.EnvironmentVars != nil {
		spec.EnvironmentVars = req.EnvironmentVars
	}

	// Salvar atualizações
	if err := s.specRepo.Update(ctx, spec); err != nil {
		return nil, fmt.Errorf("failed to update specification: %w", err)
	}

	// Publicar eventos
	for _, event := range spec.GetEvents() {
		if err := s.eventPublisher.PublishEvent(ctx, event); err != nil {
			s.logger.Warn("Failed to publish event",
				logging.F("error", err.Error()),
				logging.F("event_type", event.GetEventType()),
			)
		}
	}
	spec.ClearEvents()

	s.logger.Info("Singer specification updated successfully",
		logging.F("spec_id", spec.GetID().String()),
	)

	return &SpecResponse{SingerSpec: spec}, nil
}

// DeleteSpec remove uma especificação Singer
func (s *SingerService) DeleteSpec(ctx context.Context, id uuid.UUID) error {
	s.logger.Info("Deleting Singer specification",
		logging.F("spec_id", id.String()),
	)

	// Verificar se especificação existe
	exists, err := s.specRepo.Exists(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to check if specification exists: %w", err)
	}
	if !exists {
		return fmt.Errorf("specification not found")
	}

	// Remover execuções relacionadas
	if err := s.executionRepo.DeleteBySpecID(ctx, id); err != nil {
		s.logger.Warn("Failed to delete related executions",
			logging.F("error", err.Error()),
			logging.F("spec_id", id.String()),
		)
	}

	// Remover estado relacionado
	if err := s.stateRepo.DeleteState(ctx, id); err != nil {
		s.logger.Warn("Failed to delete related state",
			logging.F("error", err.Error()),
			logging.F("spec_id", id.String()),
		)
	}

	// Remover especificação
	if err := s.specRepo.Delete(ctx, id); err != nil {
		return fmt.Errorf("failed to delete specification: %w", err)
	}

	s.logger.Info("Singer specification deleted successfully",
		logging.F("spec_id", id.String()),
	)

	return nil
}

// ListSpecs lista especificações Singer
func (s *SingerService) ListSpecs(ctx context.Context, req ListSpecsRequest) (*ListSpecsResponse, error) {
	specs, err := s.findSpecsByFilters(ctx, req)
	if err != nil {
		return nil, err
	}

	paginatedSpecs, total := s.applyPagination(specs, req.Offset, req.Limit)

	return &ListSpecsResponse{
		Specs:  paginatedSpecs,
		Total:  total,
		Limit:  req.Limit,
		Offset: req.Offset,
	}, nil
}

// findSpecsByFilters finds specifications based on the provided filters
func (s *SingerService) findSpecsByFilters(ctx context.Context, req ListSpecsRequest) ([]*entities.SingerSpec, error) {
	// Handle query-based search first
	if req.Query != "" {
		return s.specRepo.Search(ctx, req.Query)
	}

	// Handle type-based filtering
	if req.Type != nil {
		return s.findSpecsByType(ctx, *req.Type, req.Active)
	}

	// Handle active-only filtering
	if req.Active != nil && *req.Active {
		return s.specRepo.FindActive(ctx)
	}

	// Return all specs as fallback
	return s.specRepo.FindAll(ctx)
}

// findSpecsByType finds specifications by type with optional active filtering
func (s *SingerService) findSpecsByType(ctx context.Context, specType entities.SingerType, activeFilter *bool) ([]*entities.SingerSpec, error) {
	if activeFilter != nil && *activeFilter {
		return s.findActiveSpecsByType(ctx, specType)
	}
	return s.specRepo.FindByType(ctx, specType)
}

// findActiveSpecsByType finds active specifications of a specific type
func (s *SingerService) findActiveSpecsByType(ctx context.Context, specType entities.SingerType) ([]*entities.SingerSpec, error) {
	allActive, err := s.specRepo.FindActive(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to find active specifications: %w", err)
	}

	var filteredSpecs []*entities.SingerSpec
	for _, spec := range allActive {
		if spec.Type == specType {
			filteredSpecs = append(filteredSpecs, spec)
		}
	}
	return filteredSpecs, nil
}

// applyPagination applies offset and limit to the specifications list
func (s *SingerService) applyPagination(specs []*entities.SingerSpec, offset, limit int) ([]*entities.SingerSpec, int64) {
	total := int64(len(specs))

	// Apply offset
	if offset > 0 && offset < len(specs) {
		specs = specs[offset:]
	}

	// Apply limit
	if limit > 0 && limit < len(specs) {
		specs = specs[:limit]
	}

	return specs, total
}

// ExecuteSpec executa uma especificação Singer
func (s *SingerService) ExecuteSpec(ctx context.Context, req ExecuteSpecRequest) (*ExecutionResult, error) {
	s.logger.Info("Executing Singer specification",
		logging.F("spec_id", req.SpecID.String()),
		logging.F("pipeline_id", req.PipelineID.String()),
	)

	spec, err := s.validateAndPrepareSpec(ctx, req)
	if err != nil {
		return nil, err
	}

	execution, err := s.createAndSaveExecution(ctx, req, spec)
	if err != nil {
		return nil, err
	}

	result, err := s.executeWithHandling(ctx, spec, execution, req)
	if err != nil {
		return s.handleExecutionFailure(ctx, execution, err)
	}

	return s.handleExecutionSuccess(ctx, spec, execution, result, req.SpecID)
}

// validateAndPrepareSpec validates the specification and prepares it for execution
func (s *SingerService) validateAndPrepareSpec(ctx context.Context, req ExecuteSpecRequest) (*entities.SingerSpec, error) {
	spec, err := s.specRepo.FindByID(ctx, req.SpecID)
	if err != nil {
		return nil, fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return nil, fmt.Errorf("specification not found")
	}

	if !spec.IsActive {
		return nil, fmt.Errorf("specification is not active")
	}

	if err := spec.ValidateConfig(req.Config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	return spec, nil
}

// createAndSaveExecution creates and saves the execution record
func (s *SingerService) createAndSaveExecution(ctx context.Context, req ExecuteSpecRequest, spec *entities.SingerSpec) (*entities.SingerExecution, error) {
	// Prepare state
	singerState := s.prepareExecutionState(ctx, req, spec)

	execution, err := entities.NewSingerExecution(req.SpecID, req.PipelineID, "tap", "run", []string{}, req.Config, singerState)
	if err != nil {
		return nil, fmt.Errorf("failed to create execution: %w", err)
	}

	if err := s.executionRepo.Save(ctx, execution); err != nil {
		return nil, fmt.Errorf("failed to save execution: %w", err)
	}

	return execution, nil
}

// prepareExecutionState prepares the Singer state for execution
func (s *SingerService) prepareExecutionState(ctx context.Context, req ExecuteSpecRequest, spec *entities.SingerSpec) *entities.SingerState {
	// Fetch current state if not provided and it's a tap
	if req.State == nil && spec.Type == entities.SingerTypeTap {
		req.State, _ = s.stateRepo.GetState(ctx, req.SpecID)
	}

	// Convert State to SingerState if needed
	if req.State != nil && len(req.State.Bookmarks) > 0 {
		return s.convertToSingerState(req.State)
	}
	return nil
}

// convertToSingerState converts a State to SingerState
func (s *SingerService) convertToSingerState(state *entities.State) *entities.SingerState {
	bookmarks := make(map[string]interface{})
	for streamName, streamState := range state.Bookmarks {
		bookmarks[streamName] = map[string]interface{}{
			"replication_key_value": streamState.ReplicationKeyValue,
			"version":               streamState.Version,
			"last_sync_time":        streamState.LastSyncTime,
		}
	}
	return &entities.SingerState{
		Bookmarks: bookmarks,
	}
}

// executeWithHandling executes the specification with proper error handling
func (s *SingerService) executeWithHandling(ctx context.Context, spec *entities.SingerSpec, execution *entities.SingerExecution, req ExecuteSpecRequest) (*services.ExecutionResult, error) {
	options := services.ExecutionOptions{
		Config:     req.Config,
		Catalog:    req.Catalog,
		State:      req.State,
		Properties: req.Properties,
		Discover:   req.Discover,
		Test:       req.Test,
	}

	return s.executor.Execute(ctx, spec, execution, options)
}

// handleExecutionFailure handles failed execution scenarios
func (s *SingerService) handleExecutionFailure(ctx context.Context, execution *entities.SingerExecution, err error) (*ExecutionResult, error) {
	s.logger.Error("Singer execution failed",
		logging.F("error", err.Error()),
		logging.F("execution_id", execution.GetID().String()),
	)

	s.executionRepo.Update(ctx, execution)

	return &ExecutionResult{
		ExecutionID: execution.GetID(),
		Success:     false,
		Error:       err.Error(),
	}, err
}

// handleExecutionSuccess handles successful execution scenarios
func (s *SingerService) handleExecutionSuccess(ctx context.Context, spec *entities.SingerSpec, execution *entities.SingerExecution, result *services.ExecutionResult, specID uuid.UUID) (*ExecutionResult, error) {
	// Save final state if it's a tap
	s.saveFinalState(ctx, spec, result, specID)

	// Update execution in database
	s.updateExecution(ctx, execution)

	// Publish events
	s.publishExecutionEvents(ctx, execution)

	s.logger.Info("Singer execution completed",
		logging.F("execution_id", execution.GetID().String()),
		logging.F("success", result.Success),
		logging.F("records_processed", result.RecordsProcessed),
	)

	return &ExecutionResult{
		ExecutionID:      result.ExecutionID,
		Success:          result.Success,
		RecordsProcessed: result.RecordsProcessed,
		Duration:         result.Duration.Milliseconds(),
		OutputState:      result.OutputState,
		OutputFiles:      result.OutputFiles,
		Metrics:          result.Metrics,
	}, nil
}

// saveFinalState saves the final state for tap specifications
func (s *SingerService) saveFinalState(ctx context.Context, spec *entities.SingerSpec, result *services.ExecutionResult, specID uuid.UUID) {
	if result.OutputState != nil && spec.Type == entities.SingerTypeTap {
		if err := s.stateRepo.SaveState(ctx, specID, result.OutputState); err != nil {
			s.logger.Warn("Failed to save final state",
				logging.F("error", err.Error()),
				logging.F("spec_id", specID.String()),
			)
		}
	}
}

// updateExecution updates the execution record in the database
func (s *SingerService) updateExecution(ctx context.Context, execution *entities.SingerExecution) {
	if err := s.executionRepo.Update(ctx, execution); err != nil {
		s.logger.Warn("Failed to update execution",
			logging.F("error", err.Error()),
			logging.F("execution_id", execution.GetID().String()),
		)
	}
}

// publishExecutionEvents publishes all execution events
func (s *SingerService) publishExecutionEvents(ctx context.Context, execution *entities.SingerExecution) {
	for _, event := range execution.GetEvents() {
		if err := s.eventPublisher.PublishEvent(ctx, event); err != nil {
			s.logger.Warn("Failed to publish event",
				logging.F("error", err.Error()),
				logging.F("event_type", event.GetEventType()),
			)
		}
	}
	execution.ClearEvents()
}

// GetExecution obtém uma execução Singer por ID
func (s *SingerService) GetExecution(ctx context.Context, id uuid.UUID) (*ExecutionResponse, error) {
	execution, err := s.executionRepo.FindByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to find execution: %w", err)
	}
	if execution == nil {
		return nil, fmt.Errorf("execution not found")
	}

	return &ExecutionResponse{SingerExecution: execution}, nil
}

// ListExecutions lista execuções de uma especificação
func (s *SingerService) ListExecutions(ctx context.Context, specID uuid.UUID, limit, offset int) ([]*entities.SingerExecution, error) {
	if limit <= 0 {
		return s.executionRepo.FindBySpecID(ctx, specID)
	}

	executions, _, err := s.executionRepo.FindBySpecIDWithPagination(ctx, specID, offset, limit)
	return executions, err
}

// DiscoverSchema executa discovery em um tap
func (s *SingerService) DiscoverSchema(ctx context.Context, specID uuid.UUID, config map[string]interface{}) (*entities.Catalog, error) {
	s.logger.Info("Discovering schema for Singer tap",
		logging.F("spec_id", specID.String()),
	)

	// Buscar especificação
	spec, err := s.specRepo.FindByID(ctx, specID)
	if err != nil {
		return nil, fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return nil, fmt.Errorf("specification not found")
	}

	// Verificar se é um tap
	if spec.Type != entities.SingerTypeTap {
		return nil, fmt.Errorf("discovery is only available for tap specifications")
	}

	// Validar configuração
	if err := spec.ValidateConfig(config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	// Executar discovery
	catalog, err := s.executor.Discover(ctx, spec, config)
	if err != nil {
		return nil, fmt.Errorf("discovery failed: %w", err)
	}

	// Salvar catálogo na especificação
	spec.SetCatalog(catalog)
	if err := s.specRepo.Update(ctx, spec); err != nil {
		s.logger.Warn("Failed to save discovered catalog",
			logging.F("error", err.Error()),
			logging.F("spec_id", specID.String()),
		)
	}

	s.logger.Info("Schema discovery completed",
		logging.F("spec_id", specID.String()),
		logging.F("streams_count", len(catalog.Streams)),
	)

	return catalog, nil
}

// TestConnection testa a conexão de uma especificação
func (s *SingerService) TestConnection(ctx context.Context, specID uuid.UUID, config map[string]interface{}) error {
	s.logger.Info("Testing connection for Singer specification",
		logging.F("spec_id", specID.String()),
	)

	// Buscar especificação
	spec, err := s.specRepo.FindByID(ctx, specID)
	if err != nil {
		return fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return fmt.Errorf("specification not found")
	}

	// Validar configuração
	if err := spec.ValidateConfig(config); err != nil {
		return fmt.Errorf("invalid configuration: %w", err)
	}

	// Testar conexão
	if err := s.executor.TestConnection(ctx, spec, config); err != nil {
		return fmt.Errorf("connection test failed: %w", err)
	}

	s.logger.Info("Connection test successful",
		logging.F("spec_id", specID.String()),
	)

	return nil
}

// ActivateSpec ativa uma especificação Singer
func (s *SingerService) ActivateSpec(ctx context.Context, id uuid.UUID) error {
	spec, err := s.specRepo.FindByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return fmt.Errorf("specification not found")
	}

	if err := spec.Activate(); err != nil {
		return err
	}

	if err := s.specRepo.Update(ctx, spec); err != nil {
		return fmt.Errorf("failed to update specification: %w", err)
	}

	// Publicar eventos
	for _, event := range spec.GetEvents() {
		s.eventPublisher.PublishEvent(ctx, event)
	}
	spec.ClearEvents()

	return nil
}

// DeactivateSpec desativa uma especificação Singer
func (s *SingerService) DeactivateSpec(ctx context.Context, id uuid.UUID) error {
	spec, err := s.specRepo.FindByID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to find specification: %w", err)
	}
	if spec == nil {
		return fmt.Errorf("specification not found")
	}

	if err := spec.Deactivate(); err != nil {
		return err
	}

	if err := s.specRepo.Update(ctx, spec); err != nil {
		return fmt.Errorf("failed to update specification: %w", err)
	}

	// Publicar eventos
	for _, event := range spec.GetEvents() {
		s.eventPublisher.PublishEvent(ctx, event)
	}
	spec.ClearEvents()

	return nil
}
