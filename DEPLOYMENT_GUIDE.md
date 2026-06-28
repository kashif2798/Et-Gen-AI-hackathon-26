# 🚀 E-newspaper Deployment Guide

Complete guide for deploying the E-newspaper AI-Native News Platform to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Options](#deployment-options)
4. [Vercel + Railway (Recommended)](#vercel--railway-recommended)
5. [Docker Deployment](#docker-deployment)
6. [Manual Deployment](#manual-deployment)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- **Vercel Account** (for frontend) - [vercel.com](https://vercel.com)
- **Railway Account** (for backend) - [railway.app](https://railway.app)
- **GitHub Account** (for code hosting)

### Required API Keys
- **GROQ API Key** - Get from [console.groq.com](https://console.groq.com)
- **Pexels API Key** - Get from [pexels.com/api](https://www.pexels.com/api/)

### System Requirements
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Git

---

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# GROQ API (Required)
GROQ_API_KEY=your_groq_api_key_here

# Pexels API (Required for video generation)
PEXELS_API_KEY=your_pexels_api_key_here

# Qdrant Vector Store (Optional - uses local SQLite by default)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# OpenAI (Optional - only if using OpenAI models)
OPENAI_API_KEY=your_openai_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production, use your deployed backend URL:
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Deployment Options

### Option 1: Vercel + Railway (Recommended) ⭐

**Best for:** Quick deployment, auto-scaling, managed infrastructure

- **Frontend**: Vercel (zero-config Next.js deployment)
- **Backend**: Railway (Python/FastAPI deployment)
- **Database**: Embedded Qdrant (SQLite-based)
- **Cost**: Free tier available for both

### Option 2: Docker Deployment 🐳

**Best for:** Self-hosted, full control, consistent environments

- Deploy both services using Docker Compose
- Suitable for VPS, AWS EC2, DigitalOcean, etc.

### Option 3: Manual Deployment 🔧

**Best for:** Custom infrastructure, specific requirements

- Deploy frontend and backend separately
- More control over configuration

---

## Vercel + Railway (Recommended)

### Step 1: Deploy Backend to Railway

1. **Push Code to GitHub**
   ```bash
   cd C:\Users\USER\OneDrive\Desktop\projects\ET_news
   git add .
   git commit -m "Production ready deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python

3. **Configure Railway**
   - Set root directory: `backend`
   - Railway will auto-detect `requirements.txt`
   - Add environment variables in Railway dashboard:
     ```
     GROQ_API_KEY=your_key
     PEXELS_API_KEY=your_key
     HOST=0.0.0.0
     PORT=8000
     ```

4. **Set Start Command**
   - In Railway settings, set start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Generate Domain**
   - Click "Generate Domain" in Railway
   - Copy the URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Frontend to Vercel

1. **Import Project**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository

2. **Configure Build Settings**
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Add Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Get your production URL

### Step 3: Update CORS

Update `backend/main.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3000"  # Keep for local dev
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend after this change.

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Step 1: Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy application
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Start server
CMD ["npm", "start"]
```

### Step 3: Create Docker Compose

Create `docker-compose.yml` in root:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - PEXELS_API_KEY=${PEXELS_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./backend/et_nexus_db:/app/et_nexus_db
      - ./backend/static:/app/static
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

### Step 4: Deploy with Docker

```bash
# Create .env file with your keys
cat > .env << EOF
GROQ_API_KEY=your_groq_key
PEXELS_API_KEY=your_pexels_key
EOF

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Manual Deployment

### Backend (Ubuntu/Debian Server)

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Clone repository
git clone https://github.com/kashif2798/Et-Gen-AI-hackathon-26.git
cd Et-Gen-AI-hackathon-26/backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_key"
export PEXELS_API_KEY="your_key"

# Start with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (Ubuntu/Debian Server)

```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Navigate to frontend
cd frontend

# Install dependencies
npm ci

# Build
npm run build

# Start
npm start
```

### Process Management with PM2

```bash
# Install PM2
npm install -g pm2

# Start backend
cd backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name et-backend

# Start frontend
cd ../frontend
pm2 start npm --name et-frontend -- start

# Save PM2 config
pm2 save
pm2 startup
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/enewspaper`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        proxy_pass http://localhost:8000/static/;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/enewspaper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Post-Deployment

### 1. Test Backend Health

```bash
curl https://your-backend-url/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "E-newspaper API",
  "version": "0.1.0"
}
```

### 2. Initial Data Ingestion

```bash
# Quick ingestion (5 articles per category)
curl -X POST https://your-backend-url/ingest/live?quick=true

# Full ingestion (50 articles per category)
curl -X POST https://your-backend-url/ingest/live
```

### 3. Test Frontend

1. Open your Vercel URL
2. Should see welcome screen
3. Click "Start Reading"
4. Articles should load

### 4. Monitor Logs

**Railway (Backend):**
- Go to Railway dashboard
- Click on your service
- View "Deployments" tab
- Click "View Logs"

**Vercel (Frontend):**
- Go to Vercel dashboard
- Click on your project
- View "Deployments"
- Click latest deployment → "Runtime Logs"

---

## Troubleshooting

### Backend Issues

#### "No articles fetched"
- Check RSS feeds are accessible
- Try ingestion manually: `curl -X POST your-url/ingest/live`
- Check backend logs for errors

#### "GROQ API Error"
- Verify API key is correct
- Check key has sufficient credits
- Try regenerating key at console.groq.com

#### "Vector store error"
- Railway might need persistent storage volume
- Add volume in Railway settings
- Mount to `/app/et_nexus_db`

### Frontend Issues

#### "Failed to fetch articles"
- Check `NEXT_PUBLIC_API_URL` is correct
- Must include `https://` or `http://`
- Verify CORS settings in backend

#### "Analysis taking too long"
- GROQ API might be slow
- Check backend logs
- Increase timeout in frontend (currently 60s)

#### "Video generation fails"
- Check Pexels API key
- Verify backend has write access to `static/video`
- Check available disk space

### Network Issues

#### CORS Errors
Update backend `main.py`:
```python
allow_origins=["https://your-vercel-app.vercel.app"]
```

#### SSL/HTTPS Issues
- Railway provides SSL automatically
- Vercel provides SSL automatically
- For manual deployment, use Let's Encrypt

---

## Performance Optimization

### Backend

1. **Enable Response Caching**
   - Cache article lists for 5 minutes
   - Cache analysis results per user/article

2. **Database Optimization**
   - Use external Qdrant for better performance
   - Enable vector indexing

3. **Increase Workers**
   ```bash
   uvicorn main:app --workers 4
   ```

### Frontend

1. **Enable Next.js Caching**
   - Already configured in `next.config.js`
   - Uses ISR (Incremental Static Regeneration)

2. **Image Optimization**
   - Next.js Image component auto-optimizes
   - Vercel Edge Network CDN

3. **Bundle Optimization**
   - Already using dynamic imports
   - Code splitting enabled

---

## Monitoring & Analytics

### Recommended Tools

1. **Sentry** (Error Tracking)
   - [sentry.io](https://sentry.io)
   - Tracks errors in real-time

2. **LogRocket** (Session Replay)
   - [logrocket.com](https://logrocket.com)
   - See what users experience

3. **Vercel Analytics** (Frontend)
   - Built into Vercel
   - Web Vitals, page views

4. **Railway Metrics** (Backend)
   - CPU, Memory, Network usage
   - Built into Railway dashboard

---

## Security Checklist

- [ ] Environment variables not committed to Git
- [ ] CORS restricted to your domains only
- [ ] API keys rotated regularly
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection (React escapes by default)

---

## Cost Estimation

### Free Tier (Sufficient for Hackathon Demo)

- **Vercel**: Free (100GB bandwidth, 100 builds/month)
- **Railway**: $5 credit/month (sufficient for light usage)
- **GROQ API**: Free tier (generous limits)
- **Pexels API**: Free (unlimited for non-commercial)

**Total: ~$0-5/month**

### Production Tier

- **Vercel Pro**: $20/month (more bandwidth, better analytics)
- **Railway**: ~$20-50/month (depending on usage)
- **GROQ API**: Pay-as-you-go (very affordable)
- **Pexels API**: Free (even for commercial)

**Total: ~$40-70/month**

---

## Backup & Recovery

### Database Backup (Important!)

```bash
# Backup Qdrant database
tar -czf et_nexus_db_backup.tar.gz backend/et_nexus_db/

# Restore
tar -xzf et_nexus_db_backup.tar.gz -C backend/
```

### Automated Backups

Add to cron (Linux):
```bash
0 2 * * * cd /path/to/app && tar -czf backup_$(date +\%Y\%m\%d).tar.gz backend/et_nexus_db/
```

---

## Scaling Strategy

### Phase 1: Single Server (Current)
- Suitable for 100-1000 users
- Embedded Qdrant database
- Single backend instance

### Phase 2: Horizontal Scaling
- External Qdrant Cloud
- Multiple Railway instances
- Redis for caching
- Load balancer

### Phase 3: Microservices
- Separate video generation service
- Separate analysis service
- Message queue (RabbitMQ/Kafka)
- CDN for static assets

---

## Support & Resources

- **GitHub Issues**: [Report bugs](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **GROQ Docs**: [console.groq.com/docs](https://console.groq.com/docs)

---

## Quick Commands Reference

```bash
# Backend
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down

# Git
git pull origin main
git add .
git commit -m "Update"
git push origin main

# Railway CLI
railway login
railway link
railway up
railway logs

# Vercel CLI
vercel login
vercel
vercel --prod
vercel logs
```

---

## Next Steps

1. ✅ **Deploy Backend** to Railway
2. ✅ **Deploy Frontend** to Vercel
3. ✅ **Test All Features**
4. ✅ **Monitor Performance**
5. 🎉 **Share with Users!**

Good luck with your deployment! 🚀
