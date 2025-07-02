package factory

// TEMPORARILY DISABLED due to interface mismatch between
// repositories.PipelineRepository.Count(context.Context, *value_objects.QueryOptions) (int64, error)
// and ports.PipelineRepository.Count(context.Context) (int, error)
// Will be re-enabled after resolving interface conflicts

// This factory is temporarily disabled to allow system compilation.
// The core pipeline functionality works with in-memory repositories.