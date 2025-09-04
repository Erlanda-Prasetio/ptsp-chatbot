# 🐉 Kali Linux VPS Deployment Guide

Deploy your PTSP Chatbot on Kali Linux VPS with enhanced security and performance.

## 🎯 Why Kali Linux for PTSP Chatbot?

### ✅ Advantages:
- **Latest packages**: Always up-to-date Python, Node.js
- **Security focused**: Built-in security tools and hardening
- **Performance**: Optimized for server workloads
- **Flexibility**: Full control over the system
- **Cost effective**: Many VPS providers offer Kali Linux

### 🛠️ Tools Available:
- Advanced networking tools
- Security monitoring
- Performance analysis tools
- Full customization capability

---

## 🚀 Quick Deployment Steps

### Step 1: Get Your Kali Linux VPS
Popular providers that support Kali Linux:
- **DigitalOcean**: Kali Linux droplet
- **Vultr**: Kali Linux instance
- **Linode**: Custom Kali Linux deployment
- **AWS EC2**: Kali Linux AMI
- **Any VPS**: Upload Kali Linux ISO

### Step 2: Initial VPS Setup
```bash
# SSH into your Kali Linux VPS
ssh root@your-vps-ip

# Download setup script
wget https://raw.githubusercontent.com/Erlanda-Prasetio/ptsp-chatbot/master/setup_kali.sh

# Make executable and run
chmod +x setup_kali.sh
./setup_kali.sh
```

### Step 3: Deploy the Chatbot
```bash
# Clone the project
cd /home/$(whoami)/ptspRag
git clone https://github.com/Erlanda-Prasetio/ptsp-chatbot.git .

# Deploy
chmod +x deploy_kali.sh
./deploy_kali.sh
```

**Result**: Your chatbot will be live at `http://your-vps-ip` 🎉

---

## 🔧 Kali Linux Specific Configurations

### Security Enhancements
```bash
# Install additional security tools
sudo apt install fail2ban aide rkhunter

# Configure fail2ban for SSH protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### Performance Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Check system performance
htop                    # CPU and memory usage
iotop                   # Disk I/O monitoring
nethogs                 # Network usage per process
```

### Firewall Configuration
```bash
# Enhanced firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check firewall status
sudo ufw status verbose
```

---

## 📊 System Requirements for Kali Linux

### Minimum Specs:
- **RAM**: 2GB (4GB recommended)
- **Storage**: 20GB (50GB recommended)
- **CPU**: 2 cores (4 cores recommended)
- **Network**: 1Gbps connection

### Recommended VPS Providers:
1. **DigitalOcean**: $6/month droplet
2. **Vultr**: $6/month instance
3. **Linode**: $5/month nanode
4. **AWS EC2**: t3.micro (free tier eligible)

---

## 🔐 Security Best Practices for Kali Linux

### 1. Secure SSH Access
```bash
# Change default SSH port
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart ssh
```

### 2. Regular Security Updates
```bash
# Create update script
echo '#!/bin/bash
apt update && apt upgrade -y
apt autoremove -y
apt autoclean' | sudo tee /usr/local/bin/security-update.sh

sudo chmod +x /usr/local/bin/security-update.sh

# Add to crontab for weekly updates
echo "0 2 * * 0 /usr/local/bin/security-update.sh" | sudo crontab -
```

### 3. Monitor System Logs
```bash
# Check important logs
sudo tail -f /var/log/auth.log      # Authentication attempts
sudo tail -f /var/log/nginx/access.log  # Web access
pm2 logs                            # Application logs
```

---

## 🚀 Advanced Deployment Options

### Option 1: Docker Deployment on Kali
```bash
# Install Docker
sudo apt install docker.io docker-compose
sudo systemctl enable docker

# Use the provided Dockerfile
sudo docker build -t ptsp-chatbot .
sudo docker run -d -p 80:8000 ptsp-chatbot
```

### Option 2: SSL/HTTPS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 3: Load Balancer Setup
```bash
# For multiple instances
sudo apt install haproxy

# Configure HAProxy for load balancing
# Edit /etc/haproxy/haproxy.cfg
```

---

## 📱 Expected Performance on Kali Linux

### Response Times:
- **Frontend Load**: < 500ms
- **API Response**: < 1s
- **Chat Response**: 1-3s (depending on vector store size)

### Resource Usage:
- **RAM**: 1-2GB (with full vector store)
- **CPU**: 20-40% during normal usage
- **Storage**: 5-10GB (including logs)

---

## 🛠️ Troubleshooting Kali Linux Specific Issues

### Common Issues:

**1. Permission Denied Errors**
```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) /home/$(whoami)/ptspRag
chmod -R 755 /home/$(whoami)/ptspRag
```

**2. Service Won't Start**
```bash
# Check systemd status
sudo systemctl status ptsp-chatbot
sudo journalctl -u ptsp-chatbot -f
```

**3. Nginx Configuration Issues**
```bash
# Test nginx config
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

**4. Network/Firewall Issues**
```bash
# Check listening ports
sudo netstat -tlnp

# Check firewall rules
sudo ufw status numbered
```

---

## 🔄 Maintenance Commands

### Daily Monitoring:
```bash
# Quick system check
./check_system_kali.sh

# PM2 status
pm2 status

# Check disk space
df -h

# Check memory usage
free -h
```

### Weekly Maintenance:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Clean logs
pm2 flush
sudo logrotate -f /etc/logrotate.conf

# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

---

## 🎉 Your PTSP Chatbot on Kali Linux

With Kali Linux, you get:
- ✅ **Enhanced Security**: Built-in security tools
- ✅ **Latest Packages**: Always up-to-date software
- ✅ **Performance**: Optimized for server workloads
- ✅ **Flexibility**: Full system control
- ✅ **Monitoring**: Advanced system monitoring tools

**Your chatbot will be production-ready with enterprise-level security!** 🔒🚀
