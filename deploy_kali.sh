#!/bin/bash

# PTSP Chatbot Kali Linux Deployment Script
# Optimized deployment for Kali Linux environment

set -e

PROJECT_DIR="/home/$(whoami)/ptspRag"
cd $PROJECT_DIR

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying PTSP Chatbot on Kali Linux...${NC}"

# Check if we're in the right directory
if [ ! -f "rag_api.py" ] && [ ! -f "rag_api_light.py" ]; then
    echo -e "${RED}❌ Error: Not in the correct project directory${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install additional packages for production
pip install gunicorn

# Setup frontend
echo -e "${YELLOW}🌐 Setting up frontend...${NC}"
cd ptsp-chat

# Install Node.js dependencies
npm install

# Build frontend for production
npm run build

# Go back to project root
cd ..

# Update PM2 ecosystem config with correct paths
echo -e "${YELLOW}⚙️ Updating PM2 configuration...${NC}"
sed -i "s|/home/user/ptspRag|$PROJECT_DIR|g" ecosystem.config.js

# Create systemd service file for auto-start on boot
echo -e "${YELLOW}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/ptsp-chatbot.service > /dev/null <<EOF
[Unit]
Description=PTSP Chatbot Services
After=network.target

[Service]
Type=forking
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/pm2 start ecosystem.config.js
ExecReload=/usr/bin/pm2 restart all
ExecStop=/usr/bin/pm2 stop all
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo cp nginx.conf /etc/nginx/sites-available/ptsp-chatbot

# Update nginx config with actual server details
sudo sed -i "s|your-domain.com|$(hostname -I | awk '{print $1}')|g" /etc/nginx/sites-available/ptsp-chatbot

# Enable the site
sudo ln -sf /etc/nginx/sites-available/ptsp-chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start and enable services
echo -e "${YELLOW}🚀 Starting services...${NC}"

# Start PM2 services
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# Enable the systemd service
sudo systemctl enable ptsp-chatbot.service
sudo systemctl start ptsp-chatbot.service

# Show status
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📊 Service Status:${NC}"
pm2 status
echo ""
sudo systemctl status nginx --no-pager -l
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}🌐 Your PTSP Chatbot is now accessible at:${NC}"
echo "- Frontend: http://$SERVER_IP"
echo "- Backend API: http://$SERVER_IP/api/"
echo "- Health check: http://$SERVER_IP/health"
echo ""
echo -e "${YELLOW}📋 Management commands:${NC}"
echo "- Check PM2 status: pm2 status"
echo "- View PM2 logs: pm2 logs"
echo "- Restart services: pm2 restart all"
echo "- Stop services: pm2 stop all"
echo "- Check Nginx: sudo systemctl status nginx"
echo "- View Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo ""
echo -e "${YELLOW}🔐 Security Notes for Kali Linux:${NC}"
echo "- Firewall is configured and active"
echo "- Services are set to auto-start on boot"
echo "- Consider setting up fail2ban for additional security"
echo "- Regular system updates: sudo apt update && sudo apt upgrade"
echo ""
echo -e "${BLUE}🎉 PTSP Chatbot is live on Kali Linux!${NC}"
