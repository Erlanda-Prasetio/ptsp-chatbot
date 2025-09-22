# Deployment Guide for PTSP RAG Backend

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Free Tier)
1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Connect repo**: Click "New Project" → "Deploy from GitHub repo"
3. **Environment variables**: In Railway dashboard, add:
   ```
   OPENROUTER_API_KEY=your_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   PORT=8001
   ```
4. **Deploy**: Railway will automatically build and deploy!
5. **Get URL**: Copy the generated Railway URL (like `https://your-app.railway.app`)

### Option 2: Render (Free Tier)
1. **Sign up**: Go to [render.com](https://render.com) and connect GitHub
2. **New Web Service**: Choose "Web Service" → Connect your repo
3. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python rag_api.py`
   - **Environment**: Python 3.10
4. **Environment variables**: Add the same variables as Railway
5. **Deploy**: Render will build and deploy automatically

### Option 3: Docker + DigitalOcean/AWS/GCP
1. **Build locally**: `docker build -t ptsp-rag-backend .`
2. **Test locally**: `docker-compose up`
3. **Push to registry**: Docker Hub, AWS ECR, etc.
4. **Deploy to cloud**: Use your preferred cloud platform

## 🔧 Environment Variables Required

### Essential (Required for basic functionality):
- `OPENROUTER_API_KEY`: Get from [openrouter.ai](https://openrouter.ai)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key

### Optional (For enhanced features):
- `SERPER_API_KEY`: For Google search (get from [serper.dev](https://serper.dev))
- `BING_SEARCH_KEY`: For Bing search (Microsoft Azure)

## 📱 Update Flutter App

After deployment, update your Flutter app's API URL:

1. **Find the deployed URL** (Railway/Render will provide this)
2. **Update Flutter config**:
   ```dart
   // In lib/services/api_service.dart or similar
   static const String baseUrl = 'https://your-deployed-backend.railway.app';
   ```

## 🧪 Test Deployment

After deployment:
1. **Health check**: Visit `https://your-url/health`
2. **API docs**: Visit `https://your-url/docs`
3. **Test chat**: Use your Flutter app or curl:
   ```bash
   curl -X POST https://your-url/chat \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"Apa itu DPMPTSP?"}]}'
   ```

## 💰 Cost Estimates

### Free Tier Limits:
- **Railway**: 500 hours/month, $5 credit
- **Render**: 750 hours/month
- **Both**: Perfect for development/testing

### Production:
- **Railway**: ~$5-10/month for small apps
- **Render**: ~$7/month for starter plan
- **DigitalOcean**: ~$5/month for basic droplet

## 🔒 Security Notes

1. **Never commit `.env` files**
2. **Use environment variables** for all secrets
3. **Restrict CORS** in production:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```
4. **Enable HTTPS** (automatic on Railway/Render)

## 📊 Monitoring

Both Railway and Render provide:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, request counts
- **Alerts**: Downtime notifications

Your backend is ready to deploy! 🎉