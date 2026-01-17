-- Supabase Schema for Caregiver's Fact-Check Companion
-- Run this in your Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql


-- Create the queries table
CREATE TABLE IF NOT EXISTS queries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),


    -- Video information
    platform TEXT NOT NULL CHECK (platform IN ('youtube', 'tiktok', 'unknown')),
    video_url TEXT NOT NULL,
    video_title TEXT NOT NULL,
    video_creator TEXT,


    -- Analysis
    claim_extracted TEXT,
    confidence TEXT CHECK (confidence IN ('high', 'medium', 'low')),
    explanation TEXT,
    sources TEXT[],
    channel_is_suspect BOOLEAN DEFAULT FALSE,


    -- Metadata
    fact_checks_found INTEGER DEFAULT 0,
    search_results_found INTEGER DEFAULT 0
);


-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queries_platform ON queries(platform);
CREATE INDEX IF NOT EXISTS idx_queries_confidence ON queries(confidence);


-- Enable Row Level Security
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;


-- Policy: Anyone can read (public dashboard)
CREATE POLICY "Public read access" ON queries
    FOR SELECT
    USING (true);


-- Policy: Only authenticated service role can insert
-- (Your backend uses the anon key, so we allow inserts from anon too)
CREATE POLICY "Allow inserts" ON queries
    FOR INSERT
    WITH CHECK (true);


-- Optional: Add a comment explaining the table
COMMENT ON TABLE queries IS 'Stores anonymized fact-check queries from the WhatsApp bot. No user identifiers (phone numbers, IPs) are ever stored.';





