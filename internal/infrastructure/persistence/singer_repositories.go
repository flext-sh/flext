package persistence

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/domain/entities"
	"github.com/google/uuid"
)

// InMemorySingerSpecRepository implementação em memória do repository de especificações Singer
type InMemorySingerSpecRepository struct {
	mu    sync.RWMutex
	specs map[uuid.UUID]*entities.SingerSpec
}

// NewInMemorySingerSpecRepository cria um novo repository em memória
func NewInMemorySingerSpecRepository() *InMemorySingerSpecRepository {
	return &InMemorySingerSpecRepository{
		specs: make(map[uuid.UUID]*entities.SingerSpec),
	}
}

// Save salva uma especificação
func (r *InMemorySingerSpecRepository) Save(ctx context.Context, spec *entities.SingerSpec) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.specs[spec.GetID()] = spec
	return nil
}

// FindByID busca uma especificação por ID
func (r *InMemorySingerSpecRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	spec, exists := r.specs[id]
	if !exists {
		return nil, nil
	}
	return spec, nil
}

// FindByName busca uma especificação por nome
func (r *InMemorySingerSpecRepository) FindByName(ctx context.Context, name string) (*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, spec := range r.specs {
		if spec.Name == name {
			return spec, nil
		}
	}
	return nil, nil
}

// FindAll retorna todas as especificações
func (r *InMemorySingerSpecRepository) FindAll(ctx context.Context) ([]*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	specs := make([]*entities.SingerSpec, 0, len(r.specs))
	for _, spec := range r.specs {
		specs = append(specs, spec)
	}
	return specs, nil
}

// Delete remove uma especificação
func (r *InMemorySingerSpecRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	delete(r.specs, id)
	return nil
}

// Update atualiza uma especificação
func (r *InMemorySingerSpecRepository) Update(ctx context.Context, spec *entities.SingerSpec) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.specs[spec.GetID()] = spec
	return nil
}

// FindByType busca especificações por tipo
func (r *InMemorySingerSpecRepository) FindByType(ctx context.Context, singerType entities.SingerType) ([]*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*entities.SingerSpec
	for _, spec := range r.specs {
		if spec.Type == singerType {
			result = append(result, spec)
		}
	}
	return result, nil
}

// FindActive busca especificações ativas
func (r *InMemorySingerSpecRepository) FindActive(ctx context.Context) ([]*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*entities.SingerSpec
	for _, spec := range r.specs {
		if spec.IsActive {
			result = append(result, spec)
		}
	}
	return result, nil
}

// FindByNameAndType busca especificação por nome e tipo
func (r *InMemorySingerSpecRepository) FindByNameAndType(ctx context.Context, name string, singerType entities.SingerType) (*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, spec := range r.specs {
		if spec.Name == name && spec.Type == singerType {
			return spec, nil
		}
	}
	return nil, nil
}

// Search busca especificações por consulta de texto
func (r *InMemorySingerSpecRepository) Search(ctx context.Context, query string) ([]*entities.SingerSpec, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	queryLower := strings.ToLower(query)
	var result []*entities.SingerSpec

	for _, spec := range r.specs {
		if strings.Contains(strings.ToLower(spec.Name), queryLower) ||
			strings.Contains(strings.ToLower(spec.Description), queryLower) ||
			strings.Contains(strings.ToLower(spec.Author), queryLower) {
			result = append(result, spec)
		}
	}
	return result, nil
}

// SaveAll salva múltiplas especificações
func (r *InMemorySingerSpecRepository) SaveAll(ctx context.Context, specs []*entities.SingerSpec) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	for _, spec := range specs {
		r.specs[spec.GetID()] = spec
	}
	return nil
}

// DeleteAll remove múltiplas especificações
func (r *InMemorySingerSpecRepository) DeleteAll(ctx context.Context, ids []uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	for _, id := range ids {
		delete(r.specs, id)
	}
	return nil
}

// Exists verifica se uma especificação existe
func (r *InMemorySingerSpecRepository) Exists(ctx context.Context, id uuid.UUID) (bool, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	_, exists := r.specs[id]
	return exists, nil
}

// ExistsByName verifica se uma especificação existe por nome
func (r *InMemorySingerSpecRepository) ExistsByName(ctx context.Context, name string) (bool, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, spec := range r.specs {
		if spec.Name == name {
			return true, nil
		}
	}
	return false, nil
}

// InMemorySingerExecutionRepository implementação em memória do repository de execuções Singer
type InMemorySingerExecutionRepository struct {
	mu         sync.RWMutex
	executions map[uuid.UUID]*entities.SingerExecution
}

// NewInMemorySingerExecutionRepository cria um novo repository em memória
func NewInMemorySingerExecutionRepository() *InMemorySingerExecutionRepository {
	return &InMemorySingerExecutionRepository{
		executions: make(map[uuid.UUID]*entities.SingerExecution),
	}
}

// Save salva uma execução
func (r *InMemorySingerExecutionRepository) Save(ctx context.Context, execution *entities.SingerExecution) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.executions[execution.GetID()] = execution
	return nil
}

// FindByID busca uma execução por ID
func (r *InMemorySingerExecutionRepository) FindByID(ctx context.Context, id uuid.UUID) (*entities.SingerExecution, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	execution, exists := r.executions[id]
	if !exists {
		return nil, nil
	}
	return execution, nil
}

// FindAll retorna todas as execuções
func (r *InMemorySingerExecutionRepository) FindAll(ctx context.Context) ([]*entities.SingerExecution, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	executions := make([]*entities.SingerExecution, 0, len(r.executions))
	for _, execution := range r.executions {
		executions = append(executions, execution)
	}
	return executions, nil
}

// Delete remove uma execução
func (r *InMemorySingerExecutionRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	delete(r.executions, id)
	return nil
}

// Update atualiza uma execução
func (r *InMemorySingerExecutionRepository) Update(ctx context.Context, execution *entities.SingerExecution) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.executions[execution.GetID()] = execution
	return nil
}

// FindBySpecID busca execuções por ID da especificação
func (r *InMemorySingerExecutionRepository) FindBySpecID(ctx context.Context, specID uuid.UUID) ([]*entities.SingerExecution, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*entities.SingerExecution
	for _, execution := range r.executions {
		if execution.SingerSpecID == specID {
			result = append(result, execution)
		}
	}
	return result, nil
}

// FindByPipelineID busca execuções por ID do pipeline
func (r *InMemorySingerExecutionRepository) FindByPipelineID(ctx context.Context, pipelineID uuid.UUID) ([]*entities.SingerExecution, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*entities.SingerExecution
	for _, execution := range r.executions {
		if execution.PipelineID == pipelineID {
			result = append(result, execution)
		}
	}
	return result, nil
}

// FindByStatus busca execuções por status
func (r *InMemorySingerExecutionRepository) FindByStatus(ctx context.Context, status entities.ExecutionStatus) ([]*entities.SingerExecution, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []*entities.SingerExecution
	for _, execution := range r.executions {
		if execution.Status == status {
			result = append(result, execution)
		}
	}
	return result, nil
}

// FindRunning busca execuções em andamento
func (r *InMemorySingerExecutionRepository) FindRunning(ctx context.Context) ([]*entities.SingerExecution, error) {
	return r.FindByStatus(ctx, entities.ExecutionStatusRunning)
}

// FindCompleted busca execuções completadas
func (r *InMemorySingerExecutionRepository) FindCompleted(ctx context.Context) ([]*entities.SingerExecution, error) {
	return r.FindByStatus(ctx, entities.ExecutionStatusCompleted)
}

// FindFailed busca execuções falhadas
func (r *InMemorySingerExecutionRepository) FindFailed(ctx context.Context) ([]*entities.SingerExecution, error) {
	return r.FindByStatus(ctx, entities.ExecutionStatusFailed)
}

// FindWithPagination busca execuções com paginação
func (r *InMemorySingerExecutionRepository) FindWithPagination(ctx context.Context, offset, limit int) ([]*entities.SingerExecution, int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var executions []*entities.SingerExecution
	for _, execution := range r.executions {
		executions = append(executions, execution)
	}

	total := int64(len(executions))

	// Aplicar offset e limit
	if offset > len(executions) {
		return []*entities.SingerExecution{}, total, nil
	}
	end := offset + limit
	if end > len(executions) {
		end = len(executions)
	}

	return executions[offset:end], total, nil
}

// FindBySpecIDWithPagination busca execuções por spec ID com paginação
func (r *InMemorySingerExecutionRepository) FindBySpecIDWithPagination(ctx context.Context, specID uuid.UUID, offset, limit int) ([]*entities.SingerExecution, int64, error) {
	specExecutions, err := r.FindBySpecID(ctx, specID)
	if err != nil {
		return nil, 0, err
	}

	total := int64(len(specExecutions))

	// Aplicar offset e limit
	if offset > len(specExecutions) {
		return []*entities.SingerExecution{}, total, nil
	}
	end := offset + limit
	if end > len(specExecutions) {
		end = len(specExecutions)
	}

	return specExecutions[offset:end], total, nil
}

// CountByStatus conta execuções por status
func (r *InMemorySingerExecutionRepository) CountByStatus(ctx context.Context, status entities.ExecutionStatus) (int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var count int64
	for _, execution := range r.executions {
		if execution.Status == status {
			count++
		}
	}
	return count, nil
}

// CountBySpecID conta execuções por spec ID
func (r *InMemorySingerExecutionRepository) CountBySpecID(ctx context.Context, specID uuid.UUID) (int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var count int64
	for _, execution := range r.executions {
		if execution.SingerSpecID == specID {
			count++
		}
	}
	return count, nil
}

// GetExecutionStats retorna estatísticas de execuções
func (r *InMemorySingerExecutionRepository) GetExecutionStats(ctx context.Context) (map[string]int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	stats := map[string]int64{
		"total":     0,
		"pending":   0,
		"running":   0,
		"completed": 0,
		"failed":    0,
		"cancelled": 0,
	}

	for _, execution := range r.executions {
		stats["total"]++
		switch execution.Status {
		case entities.ExecutionStatusPending:
			stats["pending"]++
		case entities.ExecutionStatusRunning:
			stats["running"]++
		case entities.ExecutionStatusCompleted:
			stats["completed"]++
		case entities.ExecutionStatusFailed:
			stats["failed"]++
		case entities.ExecutionStatusCanceled:
			stats["cancelled"]++
		}
	}

	return stats, nil
}

// DeleteOldExecutions remove execuções antigas
func (r *InMemorySingerExecutionRepository) DeleteOldExecutions(ctx context.Context, maxAge int) error {
	// Para implementação em memória, não implementamos limpeza automática
	return nil
}

// DeleteBySpecID remove todas as execuções de uma especificação
func (r *InMemorySingerExecutionRepository) DeleteBySpecID(ctx context.Context, specID uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	for id, execution := range r.executions {
		if execution.SingerSpecID == specID {
			delete(r.executions, id)
		}
	}
	return nil
}

// InMemorySingerStateRepository implementação em memória do repository de estados Singer
type InMemorySingerStateRepository struct {
	mu     sync.RWMutex
	states map[uuid.UUID]*entities.State
}

// NewInMemorySingerStateRepository cria um novo repository em memória
func NewInMemorySingerStateRepository() *InMemorySingerStateRepository {
	return &InMemorySingerStateRepository{
		states: make(map[uuid.UUID]*entities.State),
	}
}

// SaveState salva um estado
func (r *InMemorySingerStateRepository) SaveState(ctx context.Context, specID uuid.UUID, state *entities.State) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.states[specID] = state
	return nil
}

// GetState obtém um estado
func (r *InMemorySingerStateRepository) GetState(ctx context.Context, specID uuid.UUID) (*entities.State, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	state, exists := r.states[specID]
	if !exists {
		return nil, nil
	}
	return state, nil
}

// DeleteState remove um estado
func (r *InMemorySingerStateRepository) DeleteState(ctx context.Context, specID uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	delete(r.states, specID)
	return nil
}

// ListStates lista todos os estados
func (r *InMemorySingerStateRepository) ListStates(ctx context.Context) (map[uuid.UUID]*entities.State, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	states := make(map[uuid.UUID]*entities.State)
	for specID, state := range r.states {
		states[specID] = state
	}
	return states, nil
}

// SaveStreamState salva estado de um stream
func (r *InMemorySingerStateRepository) SaveStreamState(ctx context.Context, specID uuid.UUID, streamName string, state entities.StreamState) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if r.states[specID] == nil {
		r.states[specID] = &entities.State{
			Bookmarks: make(map[string]entities.StreamState),
		}
	}

	r.states[specID].Bookmarks[streamName] = state
	return nil
}

// GetStreamState obtém estado de um stream
func (r *InMemorySingerStateRepository) GetStreamState(ctx context.Context, specID uuid.UUID, streamName string) (*entities.StreamState, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	state, exists := r.states[specID]
	if !exists {
		return nil, nil
	}

	streamState, exists := state.Bookmarks[streamName]
	if !exists {
		return nil, nil
	}

	return &streamState, nil
}

// DeleteStreamState remove estado de um stream
func (r *InMemorySingerStateRepository) DeleteStreamState(ctx context.Context, specID uuid.UUID, streamName string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if r.states[specID] != nil {
		delete(r.states[specID].Bookmarks, streamName)
	}
	return nil
}

// ListStreamStates lista estados de streams
func (r *InMemorySingerStateRepository) ListStreamStates(ctx context.Context, specID uuid.UUID) (map[string]entities.StreamState, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	state, exists := r.states[specID]
	if !exists {
		return make(map[string]entities.StreamState), nil
	}

	return state.Bookmarks, nil
}

// BackupState cria backup de um estado
func (r *InMemorySingerStateRepository) BackupState(ctx context.Context, specID uuid.UUID, backupName string) error {
	// Para implementação em memória, não implementamos backup
	return fmt.Errorf("backup not implemented for in-memory repository")
}

// RestoreState restaura um estado de backup
func (r *InMemorySingerStateRepository) RestoreState(ctx context.Context, specID uuid.UUID, backupName string) error {
	// Para implementação em memória, não implementamos backup
	return fmt.Errorf("restore not implemented for in-memory repository")
}

// ListBackups lista backups disponíveis
func (r *InMemorySingerStateRepository) ListBackups(ctx context.Context, specID uuid.UUID) ([]string, error) {
	// Para implementação em memória, não implementamos backup
	return []string{}, nil
}

// DeleteBackup remove um backup
func (r *InMemorySingerStateRepository) DeleteBackup(ctx context.Context, specID uuid.UUID, backupName string) error {
	// Para implementação em memória, não implementamos backup
	return fmt.Errorf("delete backup not implemented for in-memory repository")
}

// Interface compliance verification
var _ ports.SingerSpecRepository = (*InMemorySingerSpecRepository)(nil)
var _ ports.SingerExecutionRepository = (*InMemorySingerExecutionRepository)(nil)
var _ ports.SingerStateRepository = (*InMemorySingerStateRepository)(nil)
