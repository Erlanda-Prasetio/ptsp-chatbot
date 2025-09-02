-- SQL functions to create in your Supabase SQL Editor
-- Go to: Supabase Dashboard → SQL Editor → New Query → Paste and run this

-- 1. Enable the vector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table (if not exists)
CREATE TABLE IF NOT EXISTS rag_chunks_jateng (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Enable RLS and create policy
ALTER TABLE rag_chunks_jateng ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all access to rag_chunks_jateng" ON rag_chunks_jateng;
CREATE POLICY "Allow all access to rag_chunks_jateng" ON rag_chunks_jateng
FOR ALL USING (true);

-- 4. Create index for vector similarity search
CREATE INDEX IF NOT EXISTS rag_chunks_jateng_embedding_idx 
ON rag_chunks_jateng USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 5. Create function for matching chunks
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

-- 6. Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON rag_chunks_jateng TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON rag_chunks_jateng TO anon;
GRANT EXECUTE ON FUNCTION match_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION match_chunks TO anon;
