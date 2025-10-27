import sys
import requests
import time
from embed import embed_texts
from vector_store import store
from config import GROQ_API_KEY, OPENROUTER_API_KEY, GEN_MODEL, MAX_CONTEXT_TOKENS, VECTOR_BACKEND, USE_GROQ
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase import SupabaseVectorStore
else:
    SupabaseVectorStore = None  # type: ignore

# Configure API based on which key is available
if USE_GROQ:
    HEADERS = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
else:
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
    """Query LLM with retry logic and fallback handling"""
    messages = [
        {"role": "system", "content": SYSTEM_INSTR},
        {"role": "user", "content": f"{question}\n<context>\n{context}\n</context>"}
    ]
    
    # Retry configuration
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            api_name = "Groq" if USE_GROQ else "OpenRouter"
            print(f"🤖 Attempting {api_name} API call (attempt {attempt + 1}/{max_retries})")
            
            r = requests.post(CHAT_URL, headers=HEADERS, json={
                "model": GEN_MODEL,
                "messages": messages,
                "temperature": 0.6,
                "top_p": 0.9,
                "max_tokens": 3000,
                "stop": ["\nUser:", "\nSystem:"],
                "stream": False
            }, timeout=30)  # Add timeout
            
            r.raise_for_status()
            response_json = r.json()
            response_text = response_json['choices'][0]['message']['content'].strip()
            
            # Ensure response is complete (not truncated)
            if len(response_text) > 1400 and not response_text.endswith(('.', '!', '?', ':')):
                response_text += "\n\n[Respons mungkin terpotong karena batasan panjang. Untuk informasi lebih detail, silakan hubungi DPMPTSP Jawa Tengah langsung.]"
            
            # Extract usage metadata
            usage = response_json.get('usage', {})
            model_used = response_json.get('model', GEN_MODEL)
            
            print(f"✅ {api_name} API call successful")
            print(f"📊 Tokens: {usage.get('total_tokens', 0)} (prompt: {usage.get('prompt_tokens', 0)}, completion: {usage.get('completion_tokens', 0)})")
            
            return {
                'text': response_text,
                'model': model_used,
                'usage': usage
            }
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            api_name = "Groq" if USE_GROQ else "OpenRouter"
            print(f"❌ HTTP error {status_code}: {e}")
            
            if status_code == 503:  # Service Unavailable
                print(f"🔄 {api_name} service temporarily unavailable")
            elif status_code == 429:  # Rate limit
                print("⏳ Rate limit hit, waiting longer...")
                time.sleep(base_delay * 2 * (attempt + 1))
            elif status_code >= 500:  # Server errors
                print("🔧 Server error, retrying...")
            else:
                # Client errors (4xx) - don't retry
                return _generate_fallback_response(question, context, f"API error: {status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout on attempt {attempt + 1}")
            
        except requests.exceptions.ConnectionError:
            print(f"🌐 Connection error on attempt {attempt + 1}")
            
        except Exception as e:
            print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
        
        # Wait before retrying (exponential backoff)
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            print(f"⏳ Waiting {delay}s before retry...")
            time.sleep(delay)
    
    # All retries failed - generate fallback response
    api_name = "Groq" if USE_GROQ else "OpenRouter"
    print(f"💔 All {api_name} retry attempts failed, generating fallback response")
    return _generate_fallback_response(question, context, "Service temporarily unavailable")


def _generate_fallback_response(question: str, context: str, error_reason: str = ""):
    """Generate a helpful response when LLM is unavailable"""
    
    # Extract key information from context for manual response
    context_lower = context.lower()
    question_lower = question.lower()
    
    # Common PTSP topics and responses
    if any(word in question_lower for word in ['siup', 'tdp', 'izin usaha', 'toko', 'retail']):
        return f"""**Informasi SIUP dan TDP untuk Usaha Retail**

Untuk membuka toko retail pakaian di Jawa Tengah, Anda memerlukan:

**1. SIUP (Surat Izin Usaha Perdagangan)**
- Persyaratan: KTP, NPWP, Akta pendirian, Surat domisili usaha
- Diproses melalui DPMPTSP atau OSS (Online Single Submission)
- Biaya sesuai skala usaha

**2. TDP (Tanda Daftar Perusahaan)**
- Persyaratan: SIUP, Akta pendirian, NPWP perusahaan
- Wajib untuk perusahaan dengan modal di atas Rp 50 juta
- Berlaku 5 tahun

**Prosedur:**
1. Daftar akun OSS di oss.go.id
2. Upload dokumen persyaratan
3. Bayar biaya administrasi
4. Tunggu verifikasi (3-7 hari kerja)

**Kontak DPMPTSP Jawa Tengah:**
- Website: dpmptsp.jatengprov.go.id
- Telepon: (024) 3569961
- Email: info@dpmptsp.jatengprov.go.id

*Catatan: Layanan AI sedang mengalami gangguan teknis ({error_reason}). Untuk informasi terkini, silakan hubungi langsung DPMPTSP Jawa Tengah.*"""
    
    elif any(word in question_lower for word in ['investasi', 'penanaman modal']):
        return f"""**Informasi Investasi dan Penanaman Modal**

DPMPTSP Jawa Tengah melayani perizinan investasi dengan prosedur:

**Persyaratan Umum:**
- Proposal investasi
- Identitas investor
- Dokumen perusahaan
- Studi kelayakan
- Izin lokasi

**Proses:**
1. Konsultasi awal dengan DPMPTSP
2. Pengajuan dokumen lengkap
3. Evaluasi dan verifikasi
4. Penerbitan izin

**Fasilitas untuk Investor:**
- Pelayanan satu pintu
- Konsultasi gratis
- Pendampingan proses

**Kontak:**
- Website: dpmptsp.jatengprov.go.id
- Hotline: (024) 3569961

*Catatan: Layanan AI sedang mengalami gangguan teknis ({error_reason}). Untuk informasi detail, hubungi langsung DPMPTSP.*"""
    
    else:
        return f"""**Layanan DPMPTSP Jawa Tengah**

Maaf, layanan AI sedang mengalami gangguan teknis ({error_reason}), namun DPMPTSP Jawa Tengah tetap siap melayani Anda.

**Layanan Utama:**
- Perizinan usaha dan investasi
- Pelayanan terpadu satu pintu
- Konsultasi bisnis
- Pendaftaran perusahaan

**Cara Menghubungi:**
- **Website:** dpmptsp.jatengprov.go.id
- **Telepon:** (024) 3569961
- **Email:** info@dpmptsp.jatengprov.go.id
- **Alamat:** Jl. Menteri Supeno No. 2, Semarang

**Jam Layanan:**
- Senin-Jumat: 08.00-15.00 WIB
- Sabtu: 08.00-12.00 WIB

Untuk pertanyaan spesifik tentang "{question}", silakan hubungi langsung staf DPMPTSP yang akan memberikan informasi terkini dan akurat.

*Sistem akan kembali normal secepatnya. Terima kasih atas pengertian Anda.*"""

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
