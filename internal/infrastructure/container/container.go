package container

import (
	"sync"

	pipelineApp "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application"
	pipelinePorts "github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	
	pluginApp "github.com/flext-sh/flext/internal/bounded_contexts/plugin/application"
	pluginPorts "github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	
	"github.com/flext-sh/flext/internal/infrastructure/events"
	"github.com/flext-sh/flext/internal/infrastructure/http"
	"github.com/flext-sh/flext/internal/infrastructure/persistence"
)

// Container gerencia as dependências da aplicação
type Container struct {
	mu sync.RWMutex
	
	// Infrastructure
	eventPublisher events.EventPublisher
	pipelineRepo   persistence.InMemoryPipelineRepository
	pluginRepo     persistence.InMemoryPluginRepository
	
	// Application Services
	pipelineService *pipelineApp.PipelineService
	pluginService   *pluginApp.PluginService
	
	// HTTP Handlers
	pipelineHandler *http.PipelineHandler
	pluginHandler   *http.PluginHandler
}

// NewContainer cria um novo container de dependências
func NewContainer() *Container {
	c := &Container{}
	c.initializeServices()
	return c
}

func (c *Container) initializeServices() {
	// Infrastructure
	c.eventPublisher = events.NewInMemoryEventPublisher()
	c.pipelineRepo = *persistence.NewInMemoryPipelineRepository()
	c.pluginRepo = *persistence.NewInMemoryPluginRepository()
	
	// Application Services
	c.pipelineService = pipelineApp.NewPipelineService(
		&c.pipelineRepo,
		&c.eventPublisher,
	)
	
	c.pluginService = pluginApp.NewPluginService(
		&c.pluginRepo,
		&c.eventPublisher,
	)
	
	// HTTP Handlers
	c.pipelineHandler = http.NewPipelineHandler(c.pipelineService)
	c.pluginHandler = http.NewPluginHandler(c.pluginService)
}

// GetPipelineService retorna o serviço de pipeline
func (c *Container) GetPipelineService() *pipelineApp.PipelineService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineService
}

// GetPluginService retorna o serviço de plugin
func (c *Container) GetPluginService() *pluginApp.PluginService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginService
}

// GetPipelineHandler retorna o handler HTTP de pipeline
func (c *Container) GetPipelineHandler() *http.PipelineHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineHandler
}

// GetPluginHandler retorna o handler HTTP de plugin
func (c *Container) GetPluginHandler() *http.PluginHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginHandler
}

// Ensure interfaces are implemented
var _ pipelinePorts.PipelineRepository = (*persistence.InMemoryPipelineRepository)(nil)
var _ pipelinePorts.EventPublisher = (*events.InMemoryEventPublisher)(nil)
var _ pluginPorts.PluginRepository = (*persistence.InMemoryPluginRepository)(nil)
var _ pluginPorts.EventPublisher = (*events.InMemoryEventPublisher)(nil)