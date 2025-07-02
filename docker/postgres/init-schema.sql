-- FLEXT Database Schema Initialization
-- =====================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create pipelines table
CREATE TABLE IF NOT EXISTS pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'inactive',
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100),
    version INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create pipeline_steps table
CREATE TABLE IF NOT EXISTS pipeline_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    order_index INTEGER NOT NULL,
    configuration JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(pipeline_id, order_index)
);

-- Create plugins table
CREATE TABLE IF NOT EXISTS plugins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(80) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('source', 'transform', 'destination', 'utility')),
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author VARCHAR(100),
    entry_point VARCHAR(255) NOT NULL,
    dependencies TEXT[],
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending', 'deprecated')),
    configuration_schema JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(name, version)
);

-- Create pipeline_executions table
CREATE TABLE IF NOT EXISTS pipeline_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    execution_context JSONB DEFAULT '{}'::jsonb,
    metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    node_id VARCHAR(100),
    cluster_info JSONB DEFAULT '{}'::jsonb
);

-- Create step_executions table
CREATE TABLE IF NOT EXISTS step_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES pipeline_executions(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES pipeline_steps(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    input_data JSONB DEFAULT '{}'::jsonb,
    output_data JSONB DEFAULT '{}'::jsonb,
    metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    node_id VARCHAR(100)
);

-- Create cluster_nodes table for distributed coordination
CREATE TABLE IF NOT EXISTS cluster_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id VARCHAR(100) NOT NULL UNIQUE,
    node_name VARCHAR(100),
    address VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'joining', 'leaving', 'failed')),
    role VARCHAR(20) DEFAULT 'worker' CHECK (role IN ('leader', 'worker', 'candidate')),
    capabilities TEXT[],
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    version VARCHAR(20) DEFAULT '2.0.0'
);

-- Create distributed_tasks table
CREATE TABLE IF NOT EXISTS distributed_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(50) NOT NULL,
    task_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'running', 'completed', 'failed', 'cancelled')),
    assigned_node_id VARCHAR(100),
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    result JSONB,
    timeout_at TIMESTAMP WITH TIME ZONE,
    dependencies UUID[]
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);
CREATE INDEX IF NOT EXISTS idx_pipelines_tags ON pipelines USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_pipelines_created_at ON pipelines(created_at);

CREATE INDEX IF NOT EXISTS idx_pipeline_steps_pipeline_id ON pipeline_steps(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_steps_order ON pipeline_steps(pipeline_id, order_index);

CREATE INDEX IF NOT EXISTS idx_plugins_type ON plugins(type);
CREATE INDEX IF NOT EXISTS idx_plugins_status ON plugins(status);
CREATE INDEX IF NOT EXISTS idx_plugins_name_version ON plugins(name, version);

CREATE INDEX IF NOT EXISTS idx_executions_pipeline_id ON pipeline_executions(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON pipeline_executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON pipeline_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_executions_node_id ON pipeline_executions(node_id);

CREATE INDEX IF NOT EXISTS idx_step_executions_execution_id ON step_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_step_executions_step_id ON step_executions(step_id);
CREATE INDEX IF NOT EXISTS idx_step_executions_status ON step_executions(status);

CREATE INDEX IF NOT EXISTS idx_cluster_nodes_node_id ON cluster_nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_cluster_nodes_status ON cluster_nodes(status);
CREATE INDEX IF NOT EXISTS idx_cluster_nodes_role ON cluster_nodes(role);
CREATE INDEX IF NOT EXISTS idx_cluster_nodes_heartbeat ON cluster_nodes(last_heartbeat);

CREATE INDEX IF NOT EXISTS idx_distributed_tasks_status ON distributed_tasks(status);
CREATE INDEX IF NOT EXISTS idx_distributed_tasks_type ON distributed_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_distributed_tasks_assigned_node ON distributed_tasks(assigned_node_id);
CREATE INDEX IF NOT EXISTS idx_distributed_tasks_priority ON distributed_tasks(priority DESC);
CREATE INDEX IF NOT EXISTS idx_distributed_tasks_created_at ON distributed_tasks(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_pipelines_updated_at BEFORE UPDATE ON pipelines 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_steps_updated_at BEFORE UPDATE ON pipeline_steps 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plugins_updated_at BEFORE UPDATE ON plugins 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO pipelines (name, description, tags, status) VALUES 
    ('sample-etl-pipeline', 'Sample ETL pipeline for testing cluster functionality', ARRAY['etl', 'test', 'cluster'], 'active'),
    ('data-validation-pipeline', 'Data validation and quality checks', ARRAY['validation', 'quality'], 'active'),
    ('backup-pipeline', 'Automated backup pipeline', ARRAY['backup', 'maintenance'], 'inactive')
ON CONFLICT (name) DO NOTHING;

INSERT INTO plugins (name, type, version, description, author, entry_point) VALUES 
    ('postgres-source', 'source', '1.0.0', 'PostgreSQL source connector', 'FLEXT Team', 'plugins/postgres_source.py'),
    ('data-transformer', 'transform', '1.0.0', 'Generic data transformation plugin', 'FLEXT Team', 'plugins/data_transformer.py'),
    ('file-destination', 'destination', '1.0.0', 'File system destination connector', 'FLEXT Team', 'plugins/file_destination.py')
ON CONFLICT (name, version) DO NOTHING;

-- Create views for monitoring and analytics
CREATE OR REPLACE VIEW pipeline_execution_stats AS
SELECT 
    p.id as pipeline_id,
    p.name as pipeline_name,
    COUNT(pe.id) as total_executions,
    COUNT(CASE WHEN pe.status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN pe.status = 'failed' THEN 1 END) as failed_executions,
    COUNT(CASE WHEN pe.status = 'running' THEN 1 END) as running_executions,
    AVG(EXTRACT(EPOCH FROM (pe.completed_at - pe.started_at))) as avg_execution_time_seconds,
    MAX(pe.created_at) as last_execution_at
FROM pipelines p
LEFT JOIN pipeline_executions pe ON p.id = pe.pipeline_id
GROUP BY p.id, p.name;

CREATE OR REPLACE VIEW cluster_health AS
SELECT 
    COUNT(*) as total_nodes,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_nodes,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_nodes,
    COUNT(CASE WHEN role = 'leader' THEN 1 END) as leader_nodes,
    MAX(last_heartbeat) as last_cluster_activity,
    AVG(EXTRACT(EPOCH FROM (NOW() - last_heartbeat))) as avg_heartbeat_lag_seconds
FROM cluster_nodes;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flext;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO flext;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO flext;