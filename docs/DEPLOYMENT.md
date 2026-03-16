# Deployment Guide

**Production Deployment Instructions**

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Linux server (Ubuntu 20.04+) or cloud VM
- Domain name (optional)
- SSL certificate (for HTTPS)

---

## Deployment Steps

### 1. Prepare Server

```bash
# SSH into server
ssh user@your-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install -y docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Application

```bash
# Create app directory
sudo mkdir -p /opt/guitar-app
cd /opt/guitar-app

# Clone repository
sudo git clone <repo-url> .

# Set permissions
sudo chown -R $USER:$USER /opt/guitar-app
```

### 3. Configure Environment

```bash
# Copy .env template
cp .env.example .env

# Edit configuration
nano .env
```

**Production .env:**
```bash
ENVIRONMENT=production
API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
TF_CPP_MIN_LOG_LEVEL=2
MODEL_CACHE_SIZE=2
DEBUG=False
```

### 4. Start Services

```bash
# Start in detached mode
docker-compose up -d --build

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### 5. Configure Web Server (Nginx)

```bash
# Install Nginx
sudo apt install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/guitar-app
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Frontend proxy
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Enable configuration:**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/guitar-app /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 7. Monitoring & Logging

```bash
# View application logs
docker-compose logs -f

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Monitor resources
docker stats

# Setup log rotation
sudo nano /etc/logrotate.d/docker-guitar-app
```

### 8. Health Checks

```bash
# Check API health
curl https://yourdomain.com/api/v1/health

# Check frontend
curl https://yourdomain.com

# Monitor continuously
watch -n 5 'curl -s https://yourdomain.com/api/v1/health | jq'
```

---

## Backup Strategy

### Database Backups (if added)

```bash
# Daily backup
0 2 * * * docker-compose exec db mysqldump -u root -p > /backups/db-$(date +\%Y\%m\%d).sql

# Weekly cleanup
0 3 * * 0 find /backups -name "db-*.sql" -mtime +30 -delete
```

### Model Backups

```bash
# Backup models
tar -czf /backups/models-$(date +%Y%m%d).tar.gz models/

# Restore if needed
tar -xzf /backups/models-*.tar.gz
```

---

## Scaling

### Load Balancing

```bash
# Run multiple backend instances
docker-compose up -d --scale backend=3

# Nginx will distribute traffic
```

### Performance Tuning

```bash
# Increase worker threads
# Edit docker-compose.yml
environment:
  - WORKERS=4
  
# Increase buffer sizes
# nginx.conf
client_max_body_size 10M;
proxy_buffer_size 128k;
```

---

## CI/CD Integration

### GitHub Actions (Optional)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build & Deploy
        run: |
          ssh user@server "cd /opt/guitar-app && git pull && docker-compose up -d --build"
```

---

## Disaster Recovery

### Backup Restore

```bash
# Restore from backup
docker-compose down
tar -xzf /backups/models-*.tar.gz
docker-compose up -d --build
```

### Database Failover

```bash
# Point to backup database
# Update .env with failover connection string
docker-compose restart backend
```

---

## Monitoring & Alerts

### Prometheus Metrics (Optional)

```bash
# Add metrics endpoint
# Update backend to export Prometheus metrics
# Monitor with Grafana dashboards
```

### Alert Configuration

```bash
# Setup email alerts for downtime
# Configure via Nginx/Docker monitoring tools
```

---

## Production Checklist

- [ ] SSL certificates installed
- [ ] Environment variables configured
- [ ] Models properly loaded
- [ ] Health checks passing
- [ ] API responding correctly
- [ ] Frontend accessible
- [ ] Nginx properly configured
- [ ] Logs being collected
- [ ] Backups scheduled
- [ ] Monitoring in place
- [ ] Security audit completed
- [ ] Performance tested

---

## Common Issues

### Issue: Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify models exist
ls -la models/

# Check disk space
df -h

# Rebuild
docker-compose down -v
docker-compose up -d --build
```

### Issue: Memory Leak

```bash
# Monitor memory
docker stats

# Clear Docker cache
docker system prune -a

# Restart services
docker-compose restart
```

### Issue: Slow Response

```bash
# Check CPU/Memory
docker stats

# Check network
ping yourdomain.com

# Monitor logs for errors
docker-compose logs | grep ERROR
```

---

## Maintenance

### Daily Tasks
- Monitor logs
- Check health endpoints
- Verify backups completed

### Weekly Tasks
- Review performance metrics
- Check disk usage
- Update OS packages

### Monthly Tasks
- Full system backup
- SSL certificate renewal
- Security audit

---

*Deployment Guide - Guitar Classification Platform*  
*Last Updated: March 16, 2026*
