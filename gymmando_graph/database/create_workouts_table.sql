-- Create the workouts table for GYMMANDO
-- Run this in Supabase SQL Editor
-- This matches the WorkoutState schema

CREATE TABLE IF NOT EXISTS public.workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    exercise TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight TEXT NOT NULL,
    rest_time INTEGER,
    comments TEXT,
    intent TEXT,  -- "put" or "get"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON public.workouts(user_id);

-- Add index on created_at for date-based queries
CREATE INDEX IF NOT EXISTS idx_workouts_created_at ON public.workouts(created_at);

-- Add composite index for user-specific recent workouts
CREATE INDEX IF NOT EXISTS idx_workouts_user_created ON public.workouts(user_id, created_at DESC);

-- Disable Row Level Security for development/testing
-- (Enable RLS in production with proper policies)
ALTER TABLE public.workouts DISABLE ROW LEVEL SECURITY;

-- Verify the table was created
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_name = 'workouts'
ORDER BY ordinal_position;

