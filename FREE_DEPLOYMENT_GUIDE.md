# 🚀 Free Cloud Deployment Guide

Deploy your PTSP Chatbot to free cloud platforms without needing a VPS!

## 🎯 Recommended Approach: Railway + Vercel

### Option 1: Railway (Full Stack - Easiest)

**Step 1: Deploy Backend on Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your `ptsp-chatbot` repository
5. Railway will auto-detect Python and deploy the backend
6. Set environment variables:
   - `PYTHONPATH` = `/app`
   - `PORT` = `8000`
7. Your API will be at: `https://your-app.railway.app`

**Step 2: Deploy Frontend on Railway (Same Project)**
1. In the same Railway project, add a new service
2. Select "Deploy from GitHub repo" again
3. Choose the `ptsp-chat` folder
4. Set environment variables:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.railway.app`
5. Your frontend will be at: `https://your-frontend.railway.app`

---

### Option 2: Vercel (Frontend) + Railway (Backend)

**Step 1: Deploy Backend on Railway**
1. Follow Step 1 from Option 1 above
2. Note your backend URL: `https://your-backend.railway.app`

**Step 2: Deploy Frontend on Vercel**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your `ptsp-chatbot` repository
5. Set root directory to `ptsp-chat`
6. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.railway.app`
7. Deploy!

---

### Option 3: Render (Alternative)

**Deploy on Render**
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Create new "Web Service"
4. Select your repository
5. Configure:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn rag_api:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `PYTHONPATH` = `/opt/render/project/src`

---

## 📋 Before Deploying

### 1. Update requirements.txt
Make sure your `requirements.txt` includes all dependencies:
```bash
# Check current requirements
pip freeze > requirements_full.txt
```

### 2. Test Locally
```bash
# Test backend
cd ptspRag
python rag_api.py

# Test frontend
cd ptsp-chat
npm run build
npm start
```

### 3. Environment Variables Needed
- `PYTHONPATH` = `/app` (or `/opt/render/project/src` for Render)
- `NEXT_PUBLIC_API_URL` = Your backend URL
- `PORT` = `8000` (backend)

---

## 🔧 Troubleshooting

### Common Issues:

**1. Large Files Error**
- Vector store files might be too large
- Solution: Use smaller dataset or implement vector DB

**2. Memory Limits**
- Free tiers have limited RAM
- Solution: Optimize model loading

**3. Cold Starts**
- Free services sleep after inactivity
- Solution: Use health check endpoints

### Memory Optimization for Free Tiers:

```python
# Add this to your rag_api.py for memory optimization
import gc
import torch

# Add after model loading
if torch.cuda.is_available():
    torch.cuda.empty_cache()
gc.collect()
```

---

## 🎯 Recommended Deploy Order

1. **Start with Railway** (easiest, handles both services)
2. **If Railway limits exceeded**, use Vercel for frontend
3. **If need more control**, use Render

---

## 🔗 Expected URLs After Deployment

- **Backend API**: `https://your-app.railway.app/health`
- **Frontend**: `https://your-app.vercel.app`
- **Chat Interface**: `https://your-app.vercel.app`

Your PTSP chatbot will be live and accessible worldwide! 🌍
