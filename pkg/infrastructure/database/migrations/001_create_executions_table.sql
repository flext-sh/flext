-- Migration: 001_create_executions_table.sql
-- Description: Create executions table for pipeline execution tracking
-- Version: 001
-- Created: 2025-06-30

-- Create executions table
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms BIGINT,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    logs JSONB DEFAULT '[]'::jsonb,
    metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_pipeline_id ON executions(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_pipeline_created ON executions(pipeline_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_success ON executions(success);

-- Create partial index for recent executions (last 30 days)
CREATE INDEX IF NOT EXISTS idx_executions_recent 
ON executions(pipeline_id, created_at DESC) 
WHERE created_at >= NOW() - INTERVAL '30 days';

-- Add foreign key constraint to pipelines table if it exists
-- Note: This will be added when pipelines table is properly created
-- ALTER TABLE executions ADD CONSTRAINT fk_executions_pipeline_id 
-- FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON DELETE CASCADE;

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_executions_updated_at 
    BEFORE UPDATE ON executions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE executions IS 'Pipeline execution records with metrics and logs';
COMMENT ON COLUMN executions.id IS 'Unique execution identifier';
COMMENT ON COLUMN executions.pipeline_id IS 'Reference to the pipeline that was executed';
COMMENT ON COLUMN executions.status IS 'Execution status: pending, running, completed, failed, cancelled';
COMMENT ON COLUMN executions.started_at IS 'When the execution started';
COMMENT ON COLUMN executions.completed_at IS 'When the execution completed (success or failure)';
COMMENT ON COLUMN executions.duration_ms IS 'Execution duration in milliseconds';
COMMENT ON COLUMN executions.success IS 'Whether the execution completed successfully';
COMMENT ON COLUMN executions.error_message IS 'Error message if execution failed';
COMMENT ON COLUMN executions.logs IS 'JSON array of execution logs';
COMMENT ON COLUMN executions.metrics IS 'JSON object with execution metrics and metadata';
COMMENT ON COLUMN executions.created_at IS 'When the execution record was created';
COMMENT ON COLUMN executions.updated_at IS 'When the execution record was last updated';

-- Create view for execution statistics
CREATE OR REPLACE VIEW execution_stats AS
SELECT 
    pipeline_id,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE success = true) as successful_executions,
    COUNT(*) FILTER (WHERE success = false) as failed_executions,
    ROUND(
        (COUNT(*) FILTER (WHERE success = true)::float / COUNT(*) * 100)::numeric, 
        2
    ) as success_rate_percent,
    AVG(duration_ms) FILTER (WHERE duration_ms IS NOT NULL) as avg_duration_ms,
    MIN(created_at) as first_execution,
    MAX(created_at) as last_execution,
    MAX(started_at) as last_started_at
FROM executions 
GROUP BY pipeline_id;

COMMENT ON VIEW execution_stats IS 'Aggregated execution statistics per pipeline';

-- Create view for recent executions (last 7 days)
CREATE OR REPLACE VIEW recent_executions AS
SELECT *
FROM executions 
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

COMMENT ON VIEW recent_executions IS 'Executions from the last 7 days';

-- Insert sample data for testing (will be removed in production)
-- This helps validate the schema works correctly
INSERT INTO executions (
    id, 
    pipeline_id, 
    status, 
    started_at, 
    completed_at, 
    duration_ms, 
    success, 
    error_message, 
    logs, 
    metrics
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    'completed',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '2 hours' + INTERVAL '125 seconds',
    125000,
    true,
    NULL,
    '[{"timestamp": "2025-06-30T12:00:00Z", "level": "info", "message": "Execution started"}]'::jsonb,
    '{"steps_executed": 3, "data_processed": 1000}'::jsonb
),
(
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    '550e8400-e29b-41d4-a716-446655440000'::uuid,
    'failed',
    NOW() - INTERVAL '1 hour',
    NOW() - INTERVAL '1 hour' + INTERVAL '45 seconds',
    45000,
    false,
    'Connection timeout to database',
    '[{"timestamp": "2025-06-30T13:00:00Z", "level": "error", "message": "Database connection failed"}]'::jsonb,
    '{"steps_executed": 1, "error_step": "extract"}'::jsonb
)
ON CONFLICT (id) DO NOTHING;

-- Verify the schema works with a test query
-- This will fail the migration if there are issues
DO $$
DECLARE
    test_count INTEGER;
BEGIN
    -- Test basic operations
    SELECT COUNT(*) INTO test_count FROM executions;
    
    -- Test the statistics view
    SELECT COUNT(*) INTO test_count FROM execution_stats;
    
    -- Test the recent executions view  
    SELECT COUNT(*) INTO test_count FROM recent_executions;
    
    RAISE NOTICE 'Schema validation successful - executions table ready';
END $$;