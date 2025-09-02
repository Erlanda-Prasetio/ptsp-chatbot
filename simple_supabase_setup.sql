-- Simple table creation for Supabase
-- Copy and paste this into your Supabase SQL Editor and click RUN

-- 1. Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table
CREATE TABLE IF NOT EXISTS rag_chunks_jateng (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Set up Row Level Security (allow all for now)
ALTER TABLE rag_chunks_jateng ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access" ON rag_chunks_jateng
FOR ALL USING (true);

-- 4. Create index for fast vector search
CREATE INDEX IF NOT EXISTS rag_chunks_jateng_embedding_idx 
ON rag_chunks_jateng USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 5. Create search function
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
SELECT 
    rag_chunks_jateng.id,
    rag_chunks_jateng.content,
    rag_chunks_jateng.metadata,
    1 - (rag_chunks_jateng.embedding <=> query_embedding) AS similarity
FROM rag_chunks_jateng
WHERE 1 - (rag_chunks_jateng.embedding <=> query_embedding) > match_threshold
ORDER BY rag_chunks_jateng.embedding <=> query_embedding
LIMIT match_count;
$$;
