package execution

import (
	"context"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	pipelineServices "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/services"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
)

// DomainPluginExecutorAdapter adapta o PluginExecutor da infraestrutura para a interface do domínio
type DomainPluginExecutorAdapter struct {
	pluginExecutor *PluginExecutor
}

// NewDomainPluginExecutorAdapter cria um novo adapter
func NewDomainPluginExecutorAdapter(logger logging.Logger, workDir, pythonPath string) *DomainPluginExecutorAdapter {
	return &DomainPluginExecutorAdapter{
		pluginExecutor: NewPluginExecutor(logger, workDir, pythonPath),
	}
}

// ExecuteSource executa um plugin source através do adapter
func (a *DomainPluginExecutorAdapter) ExecuteSource(
	ctx context.Context,
	plugin *entities.Plugin,
	execCtx *pipelineServices.RealPluginExecutionContext,
) (*pipelineServices.RealPluginExecutionResult, error) {
	
	// Converter contexto do domínio para infraestrutura
	infraCtx := &PluginExecutionContext{
		ExecutionID: execCtx.ExecutionID,
		PipelineID:  execCtx.PipelineID,
		StepID:      execCtx.StepID,
		InputData:   execCtx.InputData,
		Config:      execCtx.Config,
		Environment: execCtx.Environment,
	}
	
	// Executar via infraestrutura
	result, err := a.pluginExecutor.Execute(ctx, plugin, infraCtx)
	if err != nil {
		return nil, err
	}
	
	// Converter resultado para domínio
	return &pipelineServices.RealPluginExecutionResult{
		Success:      result.Success,
		ExitCode:     result.ExitCode,
		Duration:     result.Duration,
		Data:         result.Data,
		RecordsCount: result.RecordsCount,
		Error:        result.Error,
	}, nil
}

// ExecuteTarget executa um plugin target através do adapter
func (a *DomainPluginExecutorAdapter) ExecuteTarget(
	ctx context.Context,
	plugin *entities.Plugin,
	execCtx *pipelineServices.RealPluginExecutionContext,
) (*pipelineServices.RealPluginExecutionResult, error) {
	
	// Converter contexto do domínio para infraestrutura
	infraCtx := &PluginExecutionContext{
		ExecutionID: execCtx.ExecutionID,
		PipelineID:  execCtx.PipelineID,
		StepID:      execCtx.StepID,
		InputData:   execCtx.InputData,
		Config:      execCtx.Config,
		Environment: execCtx.Environment,
	}
	
	// Executar via infraestrutura
	result, err := a.pluginExecutor.Execute(ctx, plugin, infraCtx)
	if err != nil {
		return nil, err
	}
	
	// Converter resultado para domínio
	return &pipelineServices.RealPluginExecutionResult{
		Success:      result.Success,
		ExitCode:     result.ExitCode,
		Duration:     result.Duration,
		Data:         result.Data,
		RecordsCount: result.RecordsCount,
		Error:        result.Error,
	}, nil
}

// ExecuteTransformer executa um plugin transformer através do adapter
func (a *DomainPluginExecutorAdapter) ExecuteTransformer(
	ctx context.Context,
	plugin *entities.Plugin,
	execCtx *pipelineServices.RealPluginExecutionContext,
) (*pipelineServices.RealPluginExecutionResult, error) {
	
	// Converter contexto do domínio para infraestrutura
	infraCtx := &PluginExecutionContext{
		ExecutionID: execCtx.ExecutionID,
		PipelineID:  execCtx.PipelineID,
		StepID:      execCtx.StepID,
		InputData:   execCtx.InputData,
		Config:      execCtx.Config,
		Environment: execCtx.Environment,
	}
	
	// Executar via infraestrutura
	result, err := a.pluginExecutor.Execute(ctx, plugin, infraCtx)
	if err != nil {
		return nil, err
	}
	
	// Converter resultado para domínio
	return &pipelineServices.RealPluginExecutionResult{
		Success:      result.Success,
		ExitCode:     result.ExitCode,
		Duration:     result.Duration,
		Data:         result.Data,
		RecordsCount: result.RecordsCount,
		Error:        result.Error,
	}, nil
}

// ExecuteUtility executa um plugin utility através do adapter
func (a *DomainPluginExecutorAdapter) ExecuteUtility(
	ctx context.Context,
	plugin *entities.Plugin,
	execCtx *pipelineServices.RealPluginExecutionContext,
) (*pipelineServices.RealPluginExecutionResult, error) {
	
	// Converter contexto do domínio para infraestrutura
	infraCtx := &PluginExecutionContext{
		ExecutionID: execCtx.ExecutionID,
		PipelineID:  execCtx.PipelineID,
		StepID:      execCtx.StepID,
		InputData:   execCtx.InputData,
		Config:      execCtx.Config,
		Environment: execCtx.Environment,
	}
	
	// Executar via infraestrutura
	result, err := a.pluginExecutor.Execute(ctx, plugin, infraCtx)
	if err != nil {
		return nil, err
	}
	
	// Converter resultado para domínio
	return &pipelineServices.RealPluginExecutionResult{
		Success:      result.Success,
		ExitCode:     result.ExitCode,
		Duration:     result.Duration,
		Data:         result.Data,
		RecordsCount: result.RecordsCount,
		Error:        result.Error,
	}, nil
}

// SetTimeout configura timeout do executor
func (a *DomainPluginExecutorAdapter) SetTimeout(timeout time.Duration) {
	a.pluginExecutor.SetTimeout(timeout)
}

// SetEnvironment configura variáveis de ambiente
func (a *DomainPluginExecutorAdapter) SetEnvironment(env map[string]string) {
	a.pluginExecutor.SetEnvironment(env)
}