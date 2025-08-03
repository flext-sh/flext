-- Migration: 002_add_executions_table
-- Description: Create executions table for pipeline execution stats service
-- Up migration

-- Create executions table for the pipeline execution stats service
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms BIGINT,
    success BOOLEAN NOT NULL DEFAULT false,
    error_message TEXT DEFAULT '',
    logs JSONB DEFAULT '[]',
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT executions_status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'success')),
    CONSTRAINT executions_duration_positive CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_executions_pipeline_id ON executions(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_success ON executions(success);
CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_pipeline_created ON executions(pipeline_id, created_at DESC);

-- Trigger for automatic success flag calculation
CREATE OR REPLACE FUNCTION calculate_execution_success()
RETURNS TRIGGER AS $$
BEGIN
    -- Automatically set success flag based on status and error_message
    NEW.success = (NEW.status IN ('completed', 'success')) AND (NEW.error_message IS NULL OR NEW.error_message = '');
    
    -- Calculate duration if both start and completion times are available
    IF NEW.started_at IS NOT NULL AND NEW.completed_at IS NOT NULL AND NEW.duration_ms IS NULL THEN
        NEW.duration_ms = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at)) * 1000;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for the executions table
CREATE TRIGGER calculate_execution_success_trigger 
    BEFORE INSERT OR UPDATE ON executions 
    FOR EACH ROW EXECUTE FUNCTION calculate_execution_success();

-- Insert sample execution data for development/testing
DO $$
DECLARE
    sample_pipeline_id UUID;
BEGIN
    -- Get the sample pipeline ID if it exists
    SELECT id INTO sample_pipeline_id FROM pipelines WHERE name = 'sample-etl-pipeline' LIMIT 1;
    
    IF sample_pipeline_id IS NOT NULL THEN
        -- Insert some sample execution records
        INSERT INTO executions (pipeline_id, status, started_at, completed_at, error_message, logs, metrics) VALUES 
            (sample_pipeline_id, 'completed', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '50 minutes', '', 
             '[]'::jsonb, 
             '{"steps_executed": 3, "data_processed": 1000}'::jsonb),
            (sample_pipeline_id, 'failed', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes', 'Connection timeout',
             '[{"timestamp": "2024-01-01T12:00:00Z", "level": "error", "message": "Failed to connect to database"}]'::jsonb,
             '{"steps_executed": 1, "data_processed": 0}'::jsonb),
            (sample_pipeline_id, 'completed', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '2 hours 30 minutes', '',
             '[]'::jsonb,
             '{"steps_executed": 3, "data_processed": 2500}'::jsonb)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;