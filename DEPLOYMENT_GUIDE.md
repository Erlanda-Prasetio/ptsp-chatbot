# PTSP Chatbot VPS Deployment Guide

## System Requirements

### Minimum VPS Specs:
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 10GB minimum (20GB recommended)
- **CPU**: 2 cores minimum
- **OS**: Ubuntu 20.04/22.04 LTS

### Software Dependencies:
- Python 3.9+
- Node.js 18+
- PM2 (Process Manager)
- Nginx (Reverse Proxy)
- Git

## Current System Status
- **Backend**: Smart Enhanced RAG with 16,772 chunks
- **Frontend**: Next.js with TypeScript
- **Data**: DPMPTSP Central Java government documents
- **Features**: Chat history, responsive UI, Indonesian language

## Migration Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget build-essential

# Install Python 3.9+
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Install Nginx
sudo apt install -y nginx
```

### 2. Project Upload
```bash
# Clone or upload project
git clone https://github.com/Erlanda-Prasetio/ptsp-chatbot.git
cd ptsp-chatbot

# Alternative: Upload via SCP
scp -r ptspRag/ user@your-vps-ip:/home/user/
```

### 3. Backend Setup
```bash
# Navigate to backend directory
cd /path/to/ptspRag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=/path/to/ptspRag
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd ptsp-chat

# Install dependencies
npm install

# Build for production
npm run build
```

### 5. Process Management with PM2
```bash
# Start backend with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

### 6. Nginx Configuration
```bash
# Configure reverse proxy
sudo nano /etc/nginx/sites-available/ptsp-chatbot
sudo ln -s /etc/nginx/sites-available/ptsp-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Security Considerations
- Configure firewall (UFW)
- Set up SSL certificates (Let's Encrypt)
- Secure file permissions
- Regular backups

## Monitoring
- PM2 logs: `pm2 logs`
- Nginx logs: `sudo tail -f /var/log/nginx/access.log`
- System resources: `htop`

## Backup Strategy
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup database/vector store
cp data/default_vector_store.npy backup/
```
