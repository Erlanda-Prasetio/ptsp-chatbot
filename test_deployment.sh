#!/bin/bash

# Quick deployment test script
echo "🚀 Testing deployment readiness..."

echo "📋 Checking backend..."
cd "$(dirname "$0")"

# Check if all required files exist
if [ ! -f "rag_api.py" ]; then
    echo "❌ rag_api.py not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Test backend startup (without data loading)
echo "🔍 Testing backend imports..."
python3 -c "
try:
    import fastapi, uvicorn
    print('✅ FastAPI and Uvicorn available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

echo "📋 Checking frontend..."
cd ptsp-chat

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found"
    exit 1
fi

# Test if build works
echo "🔍 Testing frontend build..."
if command -v npm &> /dev/null; then
    npm run build
    if [ $? -eq 0 ]; then
        echo "✅ Frontend build successful"
    else
        echo "❌ Frontend build failed"
        exit 1
    fi
else
    echo "⚠️ npm not found, skipping frontend test"
fi

echo ""
echo "✅ Deployment readiness check complete!"
echo "🚀 Ready to deploy to:"
echo "   - Railway: https://railway.app"
echo "   - Vercel: https://vercel.com"
echo "   - Render: https://render.com"
