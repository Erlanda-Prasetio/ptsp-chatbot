#!/bin/bash

# PTSP Chatbot Deployment Script
# Run this after uploading project files to VPS

set -e

PROJECT_DIR="/home/$(whoami)/ptspRag"
cd $PROJECT_DIR

echo "🚀 Deploying PTSP Chatbot..."

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Setup frontend
echo "🌐 Setting up frontend..."
cd ptsp-chat
npm install
npm run build
cd ..

# Update ecosystem config with correct paths
echo "⚙️ Updating PM2 configuration..."
sed -i "s|/home/user/ptspRag|$PROJECT_DIR|g" ecosystem.config.js

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/ptsp-chatbot
sudo ln -sf /etc/nginx/sites-available/ptsp-chatbot /etc/nginx/sites-enabled/
sudo nginx -t

# Start services with PM2
echo "🚀 Starting services..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# Reload Nginx
sudo systemctl reload nginx

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your chatbot should be accessible at:"
echo "- Frontend: http://your-domain.com"
echo "- Backend API: http://your-domain.com/api/"
echo "- Health check: http://your-domain.com/health"
echo ""
echo "📋 Management commands:"
echo "- Check status: pm2 status"
echo "- View logs: pm2 logs"
echo "- Restart: pm2 restart all"
echo "- Stop: pm2 stop all"
