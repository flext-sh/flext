-- FLEXT Database Initialization
-- Creates required tables and initial data for FLEXT platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS flext_core;
CREATE SCHEMA IF NOT EXISTS flext_pipelines;
CREATE SCHEMA IF NOT EXISTS flext_plugins;
CREATE SCHEMA IF NOT EXISTS flext_monitoring;

-- Grant permissions
GRANT USAGE ON SCHEMA flext_core TO flext;
GRANT USAGE ON SCHEMA flext_pipelines TO flext;
GRANT USAGE ON SCHEMA flext_plugins TO flext;
GRANT USAGE ON SCHEMA flext_monitoring TO flext;

GRANT CREATE ON SCHEMA flext_core TO flext;
GRANT CREATE ON SCHEMA flext_pipelines TO flext;
GRANT CREATE ON SCHEMA flext_plugins TO flext;
GRANT CREATE ON SCHEMA flext_monitoring TO flext;

-- Core system tables
CREATE TABLE IF NOT EXISTS flext_core.system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- FlexCore cluster management
CREATE TABLE IF NOT EXISTS flext_core.flexcore_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'unknown',
    node_count INTEGER DEFAULT 0,
    plugin_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_heartbeat TIMESTAMP WITH TIME ZONE
);

-- Plugin registry
CREATE TABLE IF NOT EXISTS flext_plugins.plugin_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    type VARCHAR(100) NOT NULL,
    cluster_id UUID REFERENCES flext_core.flexcore_clusters(id) ON DELETE CASCADE,
    config JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'registered',
    execution_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(name, version, cluster_id)
);

-- Job execution tracking
CREATE TABLE IF NOT EXISTS flext_pipelines.job_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL,
    cluster_id UUID REFERENCES flext_core.flexcore_clusters(id) ON DELETE CASCADE,
    config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'created',
    output JSONB DEFAULT '[]',
    error_log JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Pipeline definitions
CREATE TABLE IF NOT EXISTS flext_pipelines.pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    extractor VARCHAR(255) NOT NULL,
    loader VARCHAR(255) NOT NULL,
    config JSONB DEFAULT '{}',
    schedule VARCHAR(100),
    enabled BOOLEAN DEFAULT true,
    run_count INTEGER DEFAULT 0,
    last_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monitoring and metrics
CREATE TABLE IF NOT EXISTS flext_monitoring.service_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    version VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_flexcore_clusters_status ON flext_core.flexcore_clusters(status);
CREATE INDEX IF NOT EXISTS idx_flexcore_clusters_heartbeat ON flext_core.flexcore_clusters(last_heartbeat);
CREATE INDEX IF NOT EXISTS idx_plugin_registry_cluster ON flext_plugins.plugin_registry(cluster_id);
CREATE INDEX IF NOT EXISTS idx_plugin_registry_type ON flext_plugins.plugin_registry(type);
CREATE INDEX IF NOT EXISTS idx_job_executions_status ON flext_pipelines.job_executions(status);
CREATE INDEX IF NOT EXISTS idx_job_executions_cluster ON flext_pipelines.job_executions(cluster_id);
CREATE INDEX IF NOT EXISTS idx_pipelines_enabled ON flext_pipelines.pipelines(enabled);
CREATE INDEX IF NOT EXISTS idx_service_health_checked ON flext_monitoring.service_health(checked_at);

-- Insert initial configuration
INSERT INTO flext_core.system_config (key, value, description) VALUES 
    ('platform.version', '"2.0.0"', 'FLEXT platform version'),
    ('platform.environment', '"production"', 'Current environment'),
    ('features.auth_enabled', 'false', 'Whether authentication is enabled'),
    ('features.metrics_enabled', 'true', 'Whether metrics collection is enabled'),
    ('limits.max_concurrent_jobs', '10', 'Maximum concurrent job executions'),
    ('limits.job_timeout_seconds', '3600', 'Default job execution timeout')
ON CONFLICT (key) DO NOTHING;

-- Create update timestamp trigger function
CREATE OR REPLACE FUNCTION flext_core.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_flexcore_clusters_updated_at 
    BEFORE UPDATE ON flext_core.flexcore_clusters 
    FOR EACH ROW EXECUTE FUNCTION flext_core.update_updated_at_column();

CREATE TRIGGER update_plugin_registry_updated_at 
    BEFORE UPDATE ON flext_plugins.plugin_registry 
    FOR EACH ROW EXECUTE FUNCTION flext_core.update_updated_at_column();

CREATE TRIGGER update_pipelines_updated_at 
    BEFORE UPDATE ON flext_pipelines.pipelines 
    FOR EACH ROW EXECUTE FUNCTION flext_core.update_updated_at_column();

-- Grant permissions on all created objects
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA flext_core TO flext;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA flext_pipelines TO flext;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA flext_plugins TO flext;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA flext_monitoring TO flext;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA flext_core TO flext;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA flext_pipelines TO flext;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA flext_plugins TO flext;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA flext_monitoring TO flext;