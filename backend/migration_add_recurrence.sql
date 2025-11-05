-- Migration: Add recurrence columns to events table
-- Run this in Supabase SQL Editor

-- Add recurrence_type column (default: 'none')
ALTER TABLE events
ADD COLUMN IF NOT EXISTS recurrence_type VARCHAR DEFAULT 'none';

-- Add recurrence_interval column (default: 1)
ALTER TABLE events
ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1;

-- Add recurrence_end_date column (nullable)
ALTER TABLE events
ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP;

-- Update existing events to have recurrence_type = 'none' if NULL
UPDATE events
SET recurrence_type = 'none'
WHERE recurrence_type IS NULL;

-- Update existing events to have recurrence_interval = 1 if NULL
UPDATE events
SET recurrence_interval = 1
WHERE recurrence_interval IS NULL;
