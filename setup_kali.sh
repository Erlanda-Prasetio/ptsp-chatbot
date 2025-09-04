#!/bin/bash

# PTSP Chatbot Kali Linux VPS Setup Script
# Optimized for Kali Linux environment

set -e

echo "🐉 Setting up PTSP Chatbot on Kali Linux VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/$(whoami)/ptspRag"
DOMAIN="your-domain.com"  # Change this to your domain or IP

echo -e "${BLUE}🐧 Kali Linux PTSP Chatbot Deployment${NC}"
echo -e "${YELLOW}📋 System Information:${NC}"
echo "User: $(whoami)"
echo "Home: $HOME"
echo "Project Directory: $PROJECT_DIR"
echo "Domain: $DOMAIN"
echo "OS: $(lsb_release -d | cut -f2)"
echo ""

# Update system
echo -e "${YELLOW}🔄 Updating Kali Linux packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install essential packages for Kali
echo -e "${YELLOW}📦 Installing essential packages...${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release

# Install Python 3.9+ (Kali usually has newer Python)
echo -e "${YELLOW}🐍 Installing Python and pip...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools

# Install Node.js 18+ for Kali Linux
echo -e "${YELLOW}📦 Installing Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js installation
echo -e "${YELLOW}✅ Node.js version: $(node --version)${NC}"
echo -e "${YELLOW}✅ npm version: $(npm --version)${NC}"

# Install PM2 globally
echo -e "${YELLOW}⚙️ Installing PM2 process manager...${NC}"
sudo npm install -g pm2

# Install Nginx
echo -e "${YELLOW}🌐 Installing Nginx...${NC}"
sudo apt install -y nginx

# Install additional tools useful for Kali
echo -e "${YELLOW}🛠️ Installing additional tools...${NC}"
sudo apt install -y \
    htop \
    nano \
    vim \
    unzip \
    tree \
    net-tools

# Configure firewall (UFW is available in Kali)
echo -e "${YELLOW}🔒 Configuring firewall...${NC}"
sudo apt install -y ufw
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 3000/tcp  # Next.js dev
sudo ufw allow 8000/tcp  # FastAPI
sudo ufw allow 8001/tcp  # FastAPI alt
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

# Upgrade pip in virtual environment
pip install --upgrade pip

# Install basic Python packages
pip install wheel setuptools

# Set proper permissions
echo -e "${YELLOW}🔐 Setting up permissions...${NC}"
sudo chown -R $(whoami):$(whoami) $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# Configure Git (if not already configured)
echo -e "${YELLOW}🔧 Configuring Git...${NC}"
if [ -z "$(git config --global user.name)" ]; then
    echo "Please configure Git:"
    read -p "Enter your Git username: " git_username
    read -p "Enter your Git email: " git_email
    git config --global user.name "$git_username"
    git config --global user.email "$git_email"
fi

echo ""
echo -e "${GREEN}✅ Kali Linux setup complete!${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Clone your project: git clone https://github.com/Erlanda-Prasetio/ptsp-chatbot.git ."
echo "2. Activate virtual environment: source $PROJECT_DIR/venv/bin/activate"
echo "3. Install dependencies: pip install -r requirements.txt"
echo "4. Configure Nginx: sudo cp nginx.conf /etc/nginx/sites-available/ptsp-chatbot"
echo "5. Start services: pm2 start ecosystem.config.js"
echo ""
echo -e "${YELLOW}📋 Useful commands for Kali:${NC}"
echo "- Activate venv: source $PROJECT_DIR/venv/bin/activate"
echo "- Check system: neofetch (install with: sudo apt install neofetch)"
echo "- Monitor processes: htop"
echo "- Check ports: netstat -tlnp"
echo "- PM2 status: pm2 status"
echo "- PM2 logs: pm2 logs"
echo "- Nginx status: sudo systemctl status nginx"
echo ""
echo -e "${BLUE}🐉 Kali Linux is ready for your PTSP Chatbot!${NC}"
