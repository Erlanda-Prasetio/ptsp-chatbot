# 🚀 VPS Migration Checklist for PTSP Chatbot

## ✅ Pre-Migration Tasks (Do this now)

### 1. Prepare Files for Upload
- [ ] All deployment scripts created (✅ Done)
- [ ] Check that all your data files are in `/data/` directory
- [ ] Verify `requirements.txt` is up to date
- [ ] Test that both frontend and backend work locally

### 2. VPS Information to Collect
- [ ] VPS IP address: `_________________`
- [ ] SSH username: `_________________`
- [ ] SSH password/key path: `_________________`
- [ ] Domain name (if any): `_________________`

### 3. File Upload Methods (Choose one)
**Option A: Git (Recommended)**
```bash
# On your local machine, push to GitHub first
git add .
git commit -m "Ready for VPS deployment"
git push origin main
```

**Option B: SCP Upload**
```bash
# From your local machine
scp -r ptspRag/ username@your-vps-ip:/home/username/
```

**Option C: FileZilla/WinSCP (GUI)**
- Upload entire `ptspRag` folder to `/home/username/`

---

## 🖥️ VPS Setup (Do this when VPS is ready)

### Step 1: Initial VPS Setup
```bash
# SSH into your VPS
ssh username@your-vps-ip

# Run the setup script
chmod +x setup_vps.sh
./setup_vps.sh
```

### Step 2: Upload Project Files
**If using Git:**
```bash
cd /home/username
git clone https://github.com/Erlanda-Prasetio/ptsp-chatbot.git ptspRag
```

**If using SCP/FileZilla:**
- Files should already be uploaded to `/home/username/ptspRag`

### Step 3: Deploy Application
```bash
cd /home/username/ptspRag
chmod +x deploy.sh
./deploy.sh
```

### Step 4: Configure Domain (If you have one)
```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/ptsp-chatbot
# Replace 'your-domain.com' with your actual domain

# Reload nginx
sudo systemctl reload nginx
```

### Step 5: Setup SSL (Optional but recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 Post-Deployment Verification

### Check Services
```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs

# Check nginx status
sudo systemctl status nginx

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:3000
```

### Access Your Chatbot
- **With Domain**: `http://your-domain.com`
- **With IP**: `http://your-vps-ip`
- **Backend API**: `http://your-domain.com/api/` or `http://your-vps-ip/api/`

---

## 🛠️ Troubleshooting Commands

```bash
# Restart everything
pm2 restart all
sudo systemctl restart nginx

# Check logs
pm2 logs ptsp-backend
pm2 logs ptsp-frontend
sudo tail -f /var/log/nginx/error.log

# Check ports
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8001

# Check disk space
df -h

# Check memory usage
free -h
htop
```

---

## 📋 Important Notes

1. **Data Persistence**: Your vector store (`data/default_vector_store.npy`) contains all your 16,772 chunks
2. **Chat History**: Will be stored in browser localStorage on the client side
3. **Memory Usage**: Monitor RAM usage, the vector store requires memory to load
4. **Backup**: Regularly backup your `/data/` directory

---

## 🆘 When You Need Help

**Message me with:**
1. VPS specifications (RAM, CPU, Storage)
2. Any error messages from the setup/deployment
3. Output of `pm2 logs` and `sudo nginx -t`
4. Your VPS IP or domain name

I'll be ready to help debug and get everything running smoothly! 🚀
