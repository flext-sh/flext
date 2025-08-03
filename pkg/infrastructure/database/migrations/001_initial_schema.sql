-- Migration: 001_initial_schema
-- Description: Create initial tables for pipelines, plugins, and executions
-- Up migration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create pipelines table
CREATE TABLE IF NOT EXISTS pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    configuration JSONB NOT NULL DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT pipelines_name_length CHECK (LENGTH(name) > 0 AND LENGTH(name) <= 100)
);

-- Create pipeline_steps table
CREATE TABLE IF NOT EXISTS pipeline_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    plugin_id UUID NOT NULL,
    step_order INTEGER NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}',
    depends_on UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT pipeline_steps_name_length CHECK (LENGTH(name) > 0),
    CONSTRAINT pipeline_steps_order_positive CHECK (step_order >= 0),
    UNIQUE(pipeline_id, step_order),
    UNIQUE(pipeline_id, name)
);

-- Create plugins table
CREATE TABLE IF NOT EXISTS plugins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'registered',
    entry_point VARCHAR(200) NOT NULL,
    dependencies TEXT[] DEFAULT '{}',
    configuration JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT plugins_name_length CHECK (LENGTH(name) > 0 AND LENGTH(name) <= 100),
    CONSTRAINT plugins_type_valid CHECK (type IN ('source', 'target', 'transformer', 'utility')),
    CONSTRAINT plugins_status_valid CHECK (status IN ('registered', 'active', 'inactive', 'failed')),
    CONSTRAINT plugins_entry_point_length CHECK (LENGTH(entry_point) > 0)
);

-- Create plugin_ports table
CREATE TABLE IF NOT EXISTS plugin_ports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_id UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    required BOOLEAN NOT NULL DEFAULT false,
    description TEXT,
    schema JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT plugin_ports_name_length CHECK (LENGTH(name) > 0),
    UNIQUE(plugin_id, name)
);

-- Create pipeline_executions table
CREATE TABLE IF NOT EXISTS pipeline_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    context JSONB NOT NULL DEFAULT '{}',
    execution_number SERIAL,
    
    CONSTRAINT pipeline_executions_status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Create step_executions table
CREATE TABLE IF NOT EXISTS step_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_execution_id UUID NOT NULL REFERENCES pipeline_executions(id) ON DELETE CASCADE,
    step_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    output JSONB,
    logs TEXT[] DEFAULT '{}',
    
    CONSTRAINT step_executions_status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Create executions table for execution tracking (used by ExecutionRepository)
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration BIGINT DEFAULT 0, -- Duration in nanoseconds
    success BOOLEAN NOT NULL DEFAULT false,
    error_message TEXT,
    logs JSONB NOT NULL DEFAULT '[]',
    metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT executions_status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- Create domain_events table for event sourcing
CREATE TABLE IF NOT EXISTS domain_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    event_data JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT domain_events_type_length CHECK (LENGTH(event_type) > 0),
    CONSTRAINT domain_events_version_positive CHECK (event_version > 0)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pipelines_active ON pipelines(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_pipelines_tags ON pipelines USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_pipelines_created_at ON pipelines(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_pipeline_steps_pipeline_id ON pipeline_steps(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_steps_plugin_id ON pipeline_steps(plugin_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_steps_order ON pipeline_steps(pipeline_id, step_order);

CREATE INDEX IF NOT EXISTS idx_plugins_type ON plugins(type);
CREATE INDEX IF NOT EXISTS idx_plugins_status ON plugins(status);
CREATE INDEX IF NOT EXISTS idx_plugins_name ON plugins(name);

CREATE INDEX IF NOT EXISTS idx_plugin_ports_plugin_id ON plugin_ports(plugin_id);

CREATE INDEX IF NOT EXISTS idx_pipeline_executions_pipeline_id ON pipeline_executions(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_executions_status ON pipeline_executions(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_executions_started_at ON pipeline_executions(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_step_executions_pipeline_execution_id ON step_executions(pipeline_execution_id);
CREATE INDEX IF NOT EXISTS idx_step_executions_step_id ON step_executions(step_id);

CREATE INDEX IF NOT EXISTS idx_executions_pipeline_id ON executions(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_success ON executions(success);

CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate ON domain_events(aggregate_id, aggregate_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_type ON domain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_occurred_at ON domain_events(occurred_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_pipelines_updated_at BEFORE UPDATE ON pipelines 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_steps_updated_at BEFORE UPDATE ON pipeline_steps 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plugins_updated_at BEFORE UPDATE ON plugins 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO plugins (name, type, version, entry_point, description, author) VALUES 
    ('tap-postgres', 'source', '1.0.0', 'tap_postgres.main', 'PostgreSQL data extractor', 'FLEXT Team'),
    ('target-bigquery', 'target', '2.1.0', 'target_bigquery.main', 'BigQuery data loader', 'FLEXT Team'),
    ('transform-dbt', 'transformer', '1.5.0', 'dbt_transform.main', 'DBT transformer', 'FLEXT Team')
ON CONFLICT (name) DO NOTHING;

INSERT INTO pipelines (name, description, tags) VALUES 
    ('sample-etl-pipeline', 'Sample ETL pipeline for demonstration', ARRAY['sample', 'etl', 'demo'])
ON CONFLICT (name) DO NOTHING; 
