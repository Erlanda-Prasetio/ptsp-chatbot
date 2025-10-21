# Essential Files After Cleanup

## ✅ Backend (Core System)

### Main Files
- `rag_api.py` - Main API endpoint
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys, DB config)
- `.env.template` - Template for .env

### Source Code (`src/`)
- `ask.py` - Query LLM
- `chatbot.py` - Chatbot logic
- `chunk.py` - Text chunking
- `config.py` - Configuration
- `embed.py` - Embedding generation
- `hybrid_rag.py` - Hybrid RAG implementation
- `ingest.py` - Document ingestion
- `internet_search.py` - Web search fallback
- `rerank.py` - Result reranking
- `scrape.py` - Web scraping
- `smart_enhanced_rag.py` - Enhanced RAG system (current baseline)
- `vector_store.py` - Vector store interface
- `vector_store_supabase.py` - Supabase integration
- `vector_store_supabase_rest.py` - Supabase REST API

### Database Setup
- `init_supabase.py` - Initialize Supabase
- `setup_supabase.py` - Setup script
- `setup_supabase_sql.sql` - SQL schema
- `ingest_supabase.py` - Ingest to Supabase
- `scrape_dpmptsp_complete.py` - Scrape DPMPTSP data

---

## ✅ Frontend

### Mobile App (`ptsp_mobile_app/`)
- Flutter-based mobile application
- All files in this directory are essential

### Web Chat (Optional - `ptsp-chat/`)
- Keep if you're using the web chat interface
- Delete if you only use mobile app

---

## ✅ Deployment & Infrastructure

### Docker
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose setup
- `.dockerignore` - Docker ignore rules
- `nginx.conf` - Nginx configuration

### Process Management
- `ecosystem.config.js` - PM2 configuration

### Deployment Scripts
- `deploy.sh` - Deployment script

---

## ✅ Documentation
- `README.md` - Main documentation
- `DEPLOYMENT.md` - Deployment guide
- `DEPLOYMENT_GUIDE.md` - Extended deployment guide
- `SUPABASE_SETUP.md` - Supabase setup instructions

---

## ✅ Research & Development

### MADAM-RAG Research (`testing/madam-rag/`)
- `run_madam_rag.py` - Original MADAM-RAG implementation
- Keep this for your research paper

---

## ✅ Data
- `data/` - Raw and processed documents
- Keep all data files for ingestion

---

## ✅ Version Control
- `.git/` - Git repository
- `.gitignore` - Git ignore rules

---

## ✅ Python Environment
- `.venv/` - Virtual environment (can be recreated)
- Keep if already set up, or recreate with `python -m venv .venv`

---

## 🗑️ What Will Be Deleted

### Test Files (100+ files)
- All `test_*.py` files
- Duplicate test implementations
- Debug scripts

### Duplicate Implementations
- `enhanced_rag.py`, `enhanced_rag_system.py`
- `rag_api_enhanced.py`, `rag_api_light.py`, `rag_api_production.py`
- `lightweight_*.py` files
- Multiple ingestion scripts

### Outdated Documentation
- Enhancement/improvement markdown files
- Deployment guides for unused platforms (Kali, Railway, Render)
- Migration checklists

### Log Files
- All `.log` files
- Test result JSON files

### Unused Dependencies
- `requirements-*.txt` variants (keeping only `requirements.txt`)

---

## 📋 Final Structure

```
ptspRag/
├── .env                          # Config
├── .gitignore
├── README.md                     # Docs
├── DEPLOYMENT.md
├── SUPABASE_SETUP.md
├── requirements.txt              # Dependencies
├── docker-compose.yml            # Docker
├── Dockerfile
├── nginx.conf
├── ecosystem.config.js           # PM2
├── deploy.sh
├── rag_api.py                    # Main API
├── init_supabase.py              # DB setup
├── setup_supabase.py
├── setup_supabase_sql.sql
├── ingest_supabase.py
├── scrape_dpmptsp_complete.py
├── src/                          # Backend core
│   ├── ask.py
│   ├── chatbot.py
│   ├── chunk.py
│   ├── config.py
│   ├── embed.py
│   ├── hybrid_rag.py
│   ├── ingest.py
│   ├── internet_search.py
│   ├── rerank.py
│   ├── scrape.py
│   ├── smart_enhanced_rag.py
│   ├── vector_store.py
│   ├── vector_store_supabase.py
│   └── vector_store_supabase_rest.py
├── ptsp_mobile_app/              # Frontend
│   └── (all Flutter files)
├── data/                         # Data files
├── testing/
│   └── madam-rag/                # Research
│       └── run_madam_rag.py
└── .venv/                        # Virtual env
```

---

## 🚀 After Cleanup

To verify everything works:

```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start backend API
python rag_api.py

# 4. Start mobile app (in ptsp_mobile_app/)
cd ptsp_mobile_app
flutter run
```

---

## ⚠️ Before Running Cleanup

**Backup important files if needed:**
1. Any custom test queries in `test_*.py` files
2. Notes in outdated documentation
3. Custom configurations in duplicate files

**The cleanup script is safe** - it only deletes files listed in the script.
You can review `cleanup_workspace.py` before running.
