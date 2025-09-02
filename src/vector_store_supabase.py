import psycopg
from typing import List, Dict
from config import (
    PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD, PG_TABLE
)
from embed import embed_texts

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {PG_TABLE} (
    id SERIAL PRIMARY KEY,
    source TEXT,
    chunk_index INT,
    content TEXT,
    embedding vector(384) -- all-MiniLM-L6-v2 outputs 384-dimensional vectors
);
CREATE INDEX IF NOT EXISTS {PG_TABLE}_embedding_idx ON {PG_TABLE} USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
"""

# Note: ensure pgvector extension installed: CREATE EXTENSION IF NOT EXISTS vector;

class SupabaseVectorStore:
    def __init__(self):
        self.conn = psycopg.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
        with self.conn, self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(CREATE_TABLE_SQL)

    def add_chunks(self, source: str, chunks: List[str]):
        embeddings = embed_texts(chunks)
        with self.conn, self.conn.cursor() as cur:
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                cur.execute(
                    f"INSERT INTO {PG_TABLE} (source, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)",
                    (source, i, chunk, emb)
                )

    def search(self, query: str, k: int = 6):
        q_emb = embed_texts([query])[0]
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT content, source, chunk_index, 1 - (embedding <=> %s::vector) AS score FROM {PG_TABLE} ORDER BY embedding <=> %s::vector LIMIT %s",
                (q_emb, q_emb, k)
            )
            rows = cur.fetchall()
        return [
            {"text": r[0], "meta": {"source": r[1], "chunk_index": r[2]}, "score": float(r[3])}
            for r in rows
        ]

    def close(self):
        self.conn.close()
