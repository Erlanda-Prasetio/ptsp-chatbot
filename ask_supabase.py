"""
Production RAG Chatbot with Supabase Backend
Usage: python ask_supabase.py "Your question here"
"""
import sys
import os
sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts
import requests
from dotenv import load_dotenv

load_dotenv()

def get_llm_response(context: str, question: str) -> str:
    """Get response from OpenRouter LLM"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    model = os.getenv('GEN_MODEL', 'mistralai/mistral-small')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/your-repo',
        'X-Title': 'Central Java RAG System'
    }
    
    prompt = f"""Based on the following context about Central Java government data, answer the user's question.

Context:
{context}

Question: {question}

Please provide a helpful and accurate answer based on the context provided. If the context doesn't contain enough information to answer the question, say so clearly."""

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 1000,
        'temperature': 0.1
    }
    
    try:
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', 
                               headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating response: {e}"

def ask_supabase_rag(question: str):
    """Ask a question to the Supabase RAG system"""
    print(f"🤔 Question: {question}")
    print("🔍 Searching Supabase database...")
    
    try:
        # Initialize Supabase store
        store = SupabaseRestVectorStore()
        count = store.get_count()
        print(f"📊 Database contains {count} chunks")
        
        if count == 0:
            print("❌ No data found in Supabase.")
            return
        
        # Get question embedding
        question_embedding = embed_texts([question])[0]
        
        # Search for relevant chunks
        results = store.search(question_embedding, top_k=5)
        
        if not results:
            print("❌ No relevant information found.")
            return
        
        # Build context from results
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown source')
            context_parts.append(f"Document {i} ({source}):\n{content}")
        
        context = "\n\n".join(context_parts)
        
        print("🤖 Generating response...")
        
        # Get LLM response
        response = get_llm_response(context, question)
        
        print(f"\n💡 Answer:\n{response}")
        
        # Show sources
        print(f"\n📚 Sources ({len(results)} documents):")
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            similarity = result.get('similarity', 'N/A')
            if isinstance(similarity, float):
                similarity = f"{similarity:.3f}"
            print(f"  {i}. {source} (similarity: {similarity})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        ask_supabase_rag(question)
    else:
        print("Usage: python ask_supabase.py \"Your question here\"")
        print("Example: python ask_supabase.py \"What employment data is available for Central Java?\"")

# Example usage:
# python ask_supabase.py "What data is available about employment in Central Java?"
# python ask_supabase.py "Show me population statistics for Central Java"
