# Troubleshooting Guide

**Common Issues & Solutions**

---

## Getting Started Issues

### Issue: "docker: command not found"

**Cause:** Docker not installed or not in PATH

**Solution:**
```bash
# Verify Docker is installed
docker --version

# If not installed, install Docker
# macOS: brew install docker
# Ubuntu: sudo apt install docker.io
# Windows: Download Docker Desktop
```

### Issue: "Port 8000 or 3000 already in use"

**Cause:** Another service using the required ports

**Solution:**
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

### Issue: "Cannot connect to Docker daemon"

**Cause:** Docker service not running

**Solution:**
```bash
# macOS/Windows: Start Docker Desktop
# Linux: 
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker ps
```

---

## Startup Issues

### Issue: "docker-compose: file not found"

**Cause:** Docker Compose not installed or outdated

**Solution:**
```bash
# Update Docker Compose
sudo apt upgrade docker-compose

# Or install latest version
sudo curl -L "https://github.com/docker/compose/releases/latest" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

### Issue: "Build fails: No such file or directory"

**Cause:** Missing model files or code structure

**Solution:**
```bash
# Verify project structure
ls -la
# Should show: backend/, frontend/, models/, docker-compose.yml

# Verify model files
ls -la models/
# Should show: best_guitar_model.keras, best_transfer_model.keras

# Check file permissions
chmod 755 models/*.keras

# Rebuild
docker-compose down -v
docker-compose up -d --build
```

### Issue: "Container exits immediately"

**Cause:** Application error during startup

**Solution:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# View full error
docker-compose logs --tail=50 backend

# Rebuild with verbose output
docker-compose up --build 2>&1 | tee build.log
```

---

## Runtime Issues

### Issue: "Connection refused: localhost:8000"

**Cause:** Backend service not running or not ready

**Solution:**
```bash
# Check if service is running
docker-compose ps

# Restart service
docker-compose restart backend

# Check logs for errors
docker-compose logs backend

# Verify it's listening
curl http://localhost:8000/api/v1/health

# If still fails, rebuild
docker-compose down
docker-compose up -d --build
```

### Issue: "Frontend can't reach backend (CORS error)"

**Cause:** API URL configuration or CORS policy

**Solution:**
```bash
# Check .env API_URL
cat .env | grep API_URL

# Should be: http://localhost:8000

# Verify CORS is enabled in backend
curl -v http://localhost:8000/api/v1/health
# Look for: Access-Control-Allow-Origin

# Clear browser cache and reload
# Try incognito mode
```

### Issue: "API returns 500 error"

**Cause:** Backend processing error

**Solution:**
```bash
# Check backend logs
docker-compose logs backend | grep -i error

# Check if models are loaded
docker-compose exec backend ls -la models/

# Test simple health endpoint
curl http://localhost:8000/api/v1/health

# Check Python version and dependencies
docker-compose exec backend python --version
docker-compose exec backend pip list | grep tensorflow
```

---

## Image Classification Issues

### Issue: "Image upload fails with 400 error"

**Cause:** Invalid image format or file too large

**Solution:**
```bash
# Check file format
file your_image.jpg
# Should show: image/jpeg

# Check file size
ls -lh your_image.jpg
# Should be < 4MB (4194304 bytes)

# Try converting to PNG
# Linux: convert original.jpg result.png
# Python: from PIL import Image; Image.open('file.jpg').save('file.png')

# Test with curl
curl -X POST "http://localhost:8000/api/v1/classify" \
  -F "file=@your_image.jpg" -v
```

### Issue: "Image processing takes too long"

**Cause:** Large image, slow GPU, or system load

**Solution:**
```bash
# Check image dimensions
# Python:
from PIL import Image
img = Image.open('your_image.jpg')
print(img.size)  # Should resize to 224x224

# Monitor system resources
docker stats

# Reduce image size before upload
# Python:
from PIL import Image
img = Image.open('large.jpg')
img.thumbnail((1024, 1024))
img.save('resized.jpg')

# Check if models are loaded
curl http://localhost:8000/api/v1/health
```

### Issue: "Incorrect predictions"

**Cause:** Model limitations or unclear images

**Solution:**
```bash
# Verify model is loaded correctly
docker-compose logs backend | grep "Model"

# Test with known example
# Use images similar to training data

# Try ensemble model (better accuracy)
curl -X POST "http://localhost:8000/api/v1/classify-ensemble" \
  -F "file=@your_image.jpg"

# Check confidence score
# Low confidence = uncertain prediction
```

---

## Performance Issues

### Issue: "Slow response times (>300ms)"

**Cause:** System overload, slow hardware, or network

**Solution:**
```bash
# Check system resources
docker stats

# Check memory
free -h

# Check CPU
top

# Reduce model cache size if memory limited
# Edit .env: MODEL_CACHE_SIZE=1

# Monitor request timing
curl -v http://localhost:8000/api/v1/health | grep "X-Response-Time"

# Check disk I/O
iostat
```

### Issue: "Out of memory error"

**Cause:** Model too large, batch processing, or memory leak

**Solution:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
services:
  backend:
    mem_limit: 4g  # Increase as needed

# Reduce model cache size
# Edit .env: MODEL_CACHE_SIZE=1

# Clear Docker cache
docker system prune -a

# Monitor memory
docker stats --no-stream

# Restart service
docker-compose restart backend
```

### Issue: "Batch processing fails"

**Cause:** Too many images, memory limit

**Solution:**
```bash
# Process fewer images at once
# Reduce batch size in request

# Increase container memory
docker-compose down
# Edit memory limit in docker-compose.yml
docker-compose up -d

# Process images sequentially instead of parallel
```

---

## Docker Issues

### Issue: "Disk space full"

**Cause:** Docker images/containers/volumes taking space

**Solution:**
```bash
# Check Docker disk usage
docker system df

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all unused data
docker system prune -a

# Check system disk
df -h
```

### Issue: "Container memory leak"

**Cause:** Application memory not being freed

**Solution:**
```bash
# Monitor memory growth
watch -n 1 'docker stats'

# Restart container periodically
docker-compose restart backend

# Check logs for errors
docker-compose logs backend | grep -i error

# Rebuild fresh
docker-compose down -v
docker-compose up -d --build
```

### Issue: "Docker Compose version incompatibility"

**Cause:** Old docker-compose syntax or version mismatch

**Solution:**
```bash
# Update Docker Compose
docker-compose --version

# Should be 2.0 or newer

# If using old version:
# Linux: Install latest from GitHub releases
# macOS: brew upgrade docker-compose
# Windows: Update Docker Desktop

# Check docker-compose.yml syntax
docker-compose config
```

---

## Network Issues

### Issue: "Cannot reach localhost:3000 from browser"

**Cause:** Network/routing issue or service not responding

**Solution:**
```bash
# Verify service is running
docker-compose ps frontend

# Check if port is listening
lsof -i :3000

# Try localhost vs 127.0.0.1
# http://127.0.0.1:3000
# http://localhost:3000

# Check firewall
sudo ufw status

# Clear browser cache
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (macOS)
```

### Issue: "Slow network between containers"

**Cause:** Docker network congestion or misconfiguration

**Solution:**
```bash
# Check Docker network
docker network ls
docker network inspect bridge

# Restart network
docker-compose restart

# Use host network (if needed)
# Edit docker-compose.yml:
services:
  backend:
    network_mode: "host"
```

---

## Database Issues (If Added)

### Issue: "Cannot connect to database"

**Cause:** Database service not running or wrong credentials

**Solution:**
```bash
# Check database service
docker-compose ps | grep db

# Verify credentials
cat .env | grep DB_

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Issue: "Database connection timeout"

**Cause:** Network or database overload

**Solution:**
```bash
# Check database health
docker-compose exec db mysql -u root -p -e "SELECT 1;"

# Increase connection timeout
# Edit .env: DB_TIMEOUT=30

# Check network connectivity
docker-compose exec backend ping db

# Restart and reconnect
docker-compose restart db backend
```

---

## Logging & Debugging

### Enable Debug Logging

```bash
# Backend
export LOG_LEVEL=DEBUG
docker-compose up backend

# Frontend
npm start -- --log-level=debug
```

### View Detailed Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100

# Specific time range
docker-compose logs --since 10m
docker-compose logs --until 1h
```

### Test Components Individually

```bash
# Test backend health
curl -v http://localhost:8000/api/v1/health

# Test frontend connectivity
curl -v http://localhost:3000

# Test API endpoint
curl -X POST "http://localhost:8000/api/v1/classify" \
  -F "file=@test.jpg" -v

# Test with telnet
telnet localhost 8000
```

---

## Getting Help

### Debugging Steps

1. **Check Service Status:** `docker-compose ps`
2. **View Logs:** `docker-compose logs -f`
3. **Verify Configuration:** `cat .env`
4. **Test Endpoints:** `curl http://localhost:8000/api/v1/health`
5. **Check Resources:** `docker stats`
6. **Search Issues:** Look in documentation
7. **Create Issue:** Report with logs and environment

### Information to Provide When Reporting Issues

- Docker version: `docker --version`
- Docker Compose version: `docker-compose --version`
- OS/Platform: `uname -a`
- Full error message from logs
- Steps to reproduce
- Expected vs actual behavior

---

## Reset & Rebuild

### Complete Reset

```bash
# Stop all services
docker-compose down

# Remove all containers/volumes
docker-compose down -v

# Remove images (optional)
docker-compose down -v --rmi all

# Clean Docker system
docker system prune -a

# Rebuild everything
docker-compose up -d --build

# Verify
docker-compose ps
curl http://localhost:8000/api/v1/health
```

### Partial Reset

```bash
# Rebuild specific service
docker-compose down backend
docker-compose up -d --build backend

# Restart service
docker-compose restart backend

# Rebuild without rebuild
docker-compose up -d
```

---

*Troubleshooting Guide - Guitar Classification Platform*  
*Last Updated: March 16, 2026*
