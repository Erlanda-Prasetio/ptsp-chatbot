-- SQL setup for multi-dataset Supabase tables
-- Go to: Supabase Dashboard → SQL Editor → New Query → Paste and run this

-- 1. Enable vector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create documents_new table (for NEW dataset)
CREATE TABLE IF NOT EXISTS documents_new (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    category TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create documents_old table (for OLD dataset)
CREATE TABLE IF NOT EXISTS documents_old (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    file TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create documents_combined table (for COMBINED dataset)
CREATE TABLE IF NOT EXISTS documents_combined (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    category TEXT,
    file TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Enable RLS on all tables
ALTER TABLE documents_new ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents_old ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents_combined ENABLE ROW LEVEL SECURITY;

-- 6. Create policies for all tables
DROP POLICY IF EXISTS "Allow all access to documents_new" ON documents_new;
CREATE POLICY "Allow all access to documents_new" ON documents_new
FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all access to documents_old" ON documents_old;
CREATE POLICY "Allow all access to documents_old" ON documents_old
FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow all access to documents_combined" ON documents_combined;
CREATE POLICY "Allow all access to documents_combined" ON documents_combined
FOR ALL USING (true);

-- 7. Create indexes for vector similarity search
CREATE INDEX IF NOT EXISTS documents_new_embedding_idx 
ON documents_new USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documents_old_embedding_idx 
ON documents_old USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documents_combined_embedding_idx 
ON documents_combined USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 8. Create text search indexes
CREATE INDEX IF NOT EXISTS documents_new_content_idx 
ON documents_new USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS documents_old_content_idx 
ON documents_old USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS documents_combined_content_idx 
ON documents_combined USING gin(to_tsvector('english', content));

-- 9. Create matching functions for each dataset
CREATE OR REPLACE FUNCTION match_documents_new(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
SELECT 
    documents_new.id,
    documents_new.title,
    documents_new.content,
    documents_new.source,
    1 - (documents_new.embedding <=> query_embedding) AS similarity
FROM documents_new
WHERE 1 - (documents_new.embedding <=> query_embedding) > match_threshold
ORDER BY documents_new.embedding <=> query_embedding
LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_documents_old(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
SELECT 
    documents_old.id,
    documents_old.title,
    documents_old.content,
    documents_old.source,
    1 - (documents_old.embedding <=> query_embedding) AS similarity
FROM documents_old
WHERE 1 - (documents_old.embedding <=> query_embedding) > match_threshold
ORDER BY documents_old.embedding <=> query_embedding
LIMIT match_count;
$$;

CREATE OR REPLACE FUNCTION match_documents_combined(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
SELECT 
    documents_combined.id,
    documents_combined.title,
    documents_combined.content,
    documents_combined.source,
    1 - (documents_combined.embedding <=> query_embedding) AS similarity
FROM documents_combined
WHERE 1 - (documents_combined.embedding <=> query_embedding) > match_threshold
ORDER BY documents_combined.embedding <=> query_embedding
LIMIT match_count;
$$;
