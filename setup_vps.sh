#!/bin/bash

# PTSP Chatbot VPS Setup Script
# Run this script on your VPS to set up the environment

set -e

echo "🚀 Setting up PTSP Chatbot on VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/$(whoami)/ptspRag"
DOMAIN="your-domain.com"  # Change this to your domain or IP

echo -e "${YELLOW}📋 System Information:${NC}"
echo "User: $(whoami)"
echo "Home: $HOME"
echo "Project Directory: $PROJECT_DIR"
echo "Domain: $DOMAIN"
echo ""

# Update system
echo -e "${YELLOW}🔄 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo -e "${YELLOW}📦 Installing essential packages...${NC}"
sudo apt install -y git curl wget build-essential software-properties-common

# Install Python 3.9+
echo -e "${YELLOW}🐍 Installing Python...${NC}"
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Node.js 18+
echo -e "${YELLOW}📦 Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
echo -e "${YELLOW}⚙️ Installing PM2...${NC}"
sudo npm install -g pm2

# Install Nginx
echo -e "${YELLOW}🌐 Installing Nginx...${NC}"
sudo apt install -y nginx

# Configure firewall
echo -e "${YELLOW}🔒 Configuring firewall...${NC}"
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create project directory
echo -e "${YELLOW}📁 Creating project directory...${NC}"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create logs directory
mkdir -p logs

# Create virtual environment
echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}✅ Basic setup complete!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Upload your project files to: $PROJECT_DIR"
echo "2. Run: source $PROJECT_DIR/venv/bin/activate"
echo "3. Run: pip install -r requirements.txt"
echo "4. Configure Nginx with the provided nginx.conf"
echo "5. Start services with PM2"
echo ""
echo -e "${YELLOW}📋 Useful commands:${NC}"
echo "- Activate venv: source $PROJECT_DIR/venv/bin/activate"
echo "- Start services: pm2 start ecosystem.config.js"
echo "- Check logs: pm2 logs"
echo "- Restart services: pm2 restart all"
echo "- Stop services: pm2 stop all"
