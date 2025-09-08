import sys
import requests
from embed import embed_texts
from vector_store import store
from config import OPENROUTER_API_KEY, GEN_MODEL, MAX_CONTEXT_TOKENS, VECTOR_BACKEND
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase import SupabaseVectorStore
else:
    SupabaseVectorStore = None  # type: ignore

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "ptspRag"
}

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
SYSTEM_INSTR = """You are an expert assistant for Central Java (Jawa Tengah) government information system DPMPTSP (Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu).

Guidelines:
- You have extensive knowledge about DPMPTSP services, procedures, permits, and Central Java government data
- Provide comprehensive answers using the information in the <context> section
- For Indonesian questions, respond in Indonesian with detailed explanations
- Be confident and thorough in your responses
- Use your knowledge to interpret and explain the context information clearly
- If specific details are not in the context but you can provide helpful general guidance about DPMPTSP procedures, do so
- Focus on DPMPTSP services, investment, permits, government procedures, and regional data
- Be detailed, informative, and professional
- Do NOT reference document numbers or file paths in your response
- Present information naturally as an expert would explain it"""


def build_context(chunks):
    """Build clean context without document references"""
    assembled = []
    total_est = 0
    
    # Filter for more relevant chunks first
    relevant_chunks = []
    for c in chunks:
        # Basic relevance filtering - score threshold
        if c.get('score', 0) >= 0.3:  # Only use chunks with decent similarity
            relevant_chunks.append(c)
    
    # If no relevant chunks, use top chunks anyway but with warning
    if not relevant_chunks:
        relevant_chunks = chunks[:3]  # Use only top 3 to avoid noise
    
    for i, c in enumerate(relevant_chunks):
        est = len(c['text']) / 4  # rough token estimate
        if total_est + est > MAX_CONTEXT_TOKENS * 1.5:
            break
        # Clean the text and add without document references
        text = c['text'].strip()
        assembled.append(text)
        total_est += est
    
    return "\n\n".join(assembled)


def query_llm(question: str, context: str):
    """Query LLM with improved settings for complete responses"""
    messages = [
        {"role": "system", "content": SYSTEM_INSTR},
        {"role": "user", "content": f"{question}\n<context>\n{context}\n</context>"}
    ]
    
    r = requests.post(CHAT_URL, headers=HEADERS, json={
        "model": GEN_MODEL,
        "messages": messages,
        "temperature": 0.6,  # Increased creativity
        "top_p": 0.9,
        "max_tokens": 3000,  # Increased for longer responses
        "stop": ["\nUser:", "\nSystem:"],
        "stream": False  # Ensure we get complete response
    })
    r.raise_for_status()
    
    response = r.json()['choices'][0]['message']['content'].strip()
    
    # Ensure response is complete (not truncated)
    if len(response) > 1400 and not response.endswith(('.', '!', '?', ':')):
        # If response seems truncated, add continuation indicator
        response += "\n\n[Respons mungkin terpotong karena batasan panjang. Untuk informasi lebih detail, silakan hubungi DPMPTSP Jawa Tengah langsung.]"
    
    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/ask.py ""<question>""")
        sys.exit(1)
    question = sys.argv[1]
    if VECTOR_BACKEND == 'supabase':
        supa = SupabaseVectorStore()
        hits = supa.search(question, k=8)
    else:
        store.load()
        if store.embeddings is None:
            print("Vector store empty. Run ingest first.")
            sys.exit(1)
        q_emb = embed_texts([question])[0]
        hits = store.search(q_emb, k=8)
    context = build_context(hits)
    answer = query_llm(question, context)
    print("Answer:\n", answer)
