#!/bin/bash

# Kali Linux System Health Check for PTSP Chatbot
# Run this script to check system status

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐉 PTSP Chatbot System Check - Kali Linux${NC}"
echo "=============================================="
echo ""

# System Information
echo -e "${YELLOW}📊 System Information:${NC}"
echo "Hostname: $(hostname)"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime -p)"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Resource Usage
echo -e "${YELLOW}💾 Resource Usage:${NC}"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo ""

# Network Information
echo -e "${YELLOW}🌐 Network Status:${NC}"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "Active Connections:"
netstat -tuln | grep -E ':80|:443|:3000|:8000|:8001' | head -10
echo ""

# Service Status
echo -e "${YELLOW}⚙️ Service Status:${NC}"

# Check PM2
if command -v pm2 &> /dev/null; then
    echo "PM2 Processes:"
    pm2 jlist | jq -r '.[] | "\(.name): \(.pm2_env.status)"' 2>/dev/null || pm2 status
else
    echo -e "${RED}❌ PM2 not found${NC}"
fi
echo ""

# Check Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx: Running${NC}"
else
    echo -e "${RED}❌ Nginx: Not running${NC}"
fi

# Check UFW Firewall
if command -v ufw &> /dev/null; then
    echo "Firewall Status: $(sudo ufw status | head -1)"
else
    echo -e "${YELLOW}⚠️ UFW not installed${NC}"
fi
echo ""

# Application Health Checks
echo -e "${YELLOW}🔍 Application Health:${NC}"

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API (8000): Healthy${NC}"
elif curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API (8001): Healthy${NC}"
else
    echo -e "${RED}❌ Backend API: Not responding${NC}"
fi

# Check if frontend is responding
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend (3000): Healthy${NC}"
else
    echo -e "${RED}❌ Frontend: Not responding${NC}"
fi

# Check external access
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unknown")
echo "Public IP: $PUBLIC_IP"

if curl -s http://$PUBLIC_IP > /dev/null 2>&1; then
    echo -e "${GREEN}✅ External access: Working${NC}"
else
    echo -e "${YELLOW}⚠️ External access: Check firewall/nginx${NC}"
fi
echo ""

# Log Analysis
echo -e "${YELLOW}📝 Recent Logs:${NC}"
echo "Last 5 Nginx access logs:"
sudo tail -5 /var/log/nginx/access.log 2>/dev/null || echo "No nginx logs found"
echo ""

echo "PM2 logs (last 5 lines):"
pm2 logs --lines 5 --nostream 2>/dev/null || echo "No PM2 logs found"
echo ""

# Security Check
echo -e "${YELLOW}🔐 Security Status:${NC}"

# Check for failed login attempts
FAILED_LOGINS=$(sudo grep "Failed password" /var/log/auth.log | wc -l 2>/dev/null || echo "0")
echo "Failed login attempts today: $FAILED_LOGINS"

# Check if fail2ban is running
if systemctl is-active --quiet fail2ban; then
    echo -e "${GREEN}✅ Fail2ban: Active${NC}"
else
    echo -e "${YELLOW}⚠️ Fail2ban: Not active${NC}"
fi

# Check SSH configuration
SSH_PORT=$(grep "^Port" /etc/ssh/sshd_config | awk '{print $2}' 2>/dev/null || echo "22")
ROOT_LOGIN=$(grep "^PermitRootLogin" /etc/ssh/sshd_config | awk '{print $2}' 2>/dev/null || echo "unknown")
echo "SSH Port: $SSH_PORT"
echo "Root Login: $ROOT_LOGIN"
echo ""

# Recommendations
echo -e "${BLUE}💡 Recommendations:${NC}"

if [ "$FAILED_LOGINS" -gt 10 ]; then
    echo -e "${RED}⚠️ High number of failed logins. Consider reviewing security.${NC}"
fi

if [ "$ROOT_LOGIN" = "yes" ]; then
    echo -e "${YELLOW}⚠️ Consider disabling root SSH login for security.${NC}"
fi

if [ "$SSH_PORT" = "22" ]; then
    echo -e "${YELLOW}⚠️ Consider changing SSH port from default 22.${NC}"
fi

# Available memory check
AVAILABLE_MEM=$(free | grep Mem | awk '{print int($7/$2 * 100)}')
if [ "$AVAILABLE_MEM" -lt 20 ]; then
    echo -e "${RED}⚠️ Low available memory ($AVAILABLE_MEM%). Consider adding swap or upgrading.${NC}"
fi

# Disk space check
DISK_USAGE=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//g')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${RED}⚠️ Disk usage high ($DISK_USAGE%). Clean up logs or expand storage.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 System check complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Quick Commands:${NC}"
echo "- Restart services: pm2 restart all && sudo systemctl restart nginx"
echo "- View logs: pm2 logs"
echo "- Check processes: htop"
echo "- Monitor network: nethogs"
echo "- Update system: sudo apt update && sudo apt upgrade"
