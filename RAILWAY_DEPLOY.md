## 🚀 Railway Deployment Instructions

### Step 1: Set Environment Variables in Railway Dashboard

Go to your Railway project dashboard and add these environment variables:

**Essential Variables:**
```
OPENROUTER_API_KEY=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
SUPABASE_URL=https://fgrltciphyzxzjqmdsdc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZncmx0Y2lwaHl6eHpqcW1kc2RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwNzc1MjMsImV4cCI6MjA3MTY1MzUyM30.IWRZqiWCz0w_CmaE8rDL2V7HqUyCkyHu6BPko-eMQb0
```

**Configuration Variables:**
```
PORT=8001
VECTOR_BACKEND=supabase
EMB_MODEL=sentence-transformers/all-MiniLM-L6-v2
USE_LOCAL_EMBEDDINGS=true
GEN_MODEL=mistralai/mistral-small-3.2-24b-instruct:free
MAX_CONTEXT_TOKENS=8000
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
PYTHONPATH=/app
```

**Database Variables (Supabase):**
```
PG_HOST=db.fgrltciphyzxzjqmdsdc.supabase.co
PG_PORT=5432
PG_DB=postgres
PG_USER=postgres
PG_PASSWORD=dpmptsppemprovjateng
PG_TABLE=rag_chunks_jateng
PG_TIMEOUT=30
```

### Step 2: Commit and Push Changes

```bash
git add .
git commit -m "Add production deployment configuration"
git push origin master
```

### Step 3: Railway Will Auto-Deploy

Railway will detect the changes and rebuild. The new version should:
1. ✅ Pass health checks quickly (< 30 seconds)
2. ✅ Initialize RAG system in background
3. ✅ Be ready to serve requests

### Step 4: Test Deployment

1. **Health Check**: `https://your-app.railway.app/health`
2. **API Docs**: `https://your-app.railway.app/docs`
3. **Test Chat**: 
   ```bash
   curl -X POST https://your-app.railway.app/chat \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"Apa itu DPMPTSP?"}]}'
   ```

### 🔧 Troubleshooting

If health checks still fail:
1. **Check Logs**: Railway dashboard → Deployments → View Logs
2. **Environment Variables**: Make sure all variables are set correctly
3. **Memory**: Upgrade to hobby plan if needed ($5/month for more memory)

### 📱 Update Flutter App

Once deployed, update your Flutter app:
```dart
// Replace with your Railway URL
static const String baseUrl = 'https://your-app-name.railway.app';
```

The production version loads much faster and should pass Railway's health checks! 🎉