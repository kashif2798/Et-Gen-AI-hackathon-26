# 🚀 Vercel + Render Deployment Guide

> **Complete step-by-step guide to deploy E-newspaper Platform**

**Estimated Time:** 20 minutes  
**Cost:** Free tier available for both services

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ Code pushed to GitHub: `https://github.com/kashif2798/Et-Gen-AI-hackathon-26`
- ✅ GROQ API Key from [console.groq.com](https://console.groq.com)
- ✅ Pexels API Key from [pexels.com/api](https://www.pexels.com/api/)
- ✅ GitHub account
- ✅ Email for Vercel and Render accounts

---

## 🎯 Deployment Overview

```
┌─────────────────┐         ┌─────────────────┐
│     Vercel      │────────▶│     Render      │
│   (Frontend)    │  API    │    (Backend)    │
│   Next.js App   │  Calls  │   FastAPI App   │
└─────────────────┘         └─────────────────┘
```

We'll deploy:
1. **Backend First** (Render) - Get API URL
2. **Frontend Second** (Vercel) - Use backend URL

---

# PART 1: Deploy Backend to Render 🐳

## Step 1: Create Render Account

1. **Go to [render.com](https://render.com)**
2. Click **"Get Started"** (top right)
3. **Sign up with GitHub**
   - Click "Sign up with GitHub"
   - Authorize Render to access your GitHub
   - Complete email verification if prompted

✅ **You should now be on Render Dashboard**

---

## Step 2: Create New Web Service

1. **Click "New +" button** (top right)
2. **Select "Web Service"**
3. **Connect GitHub Repository**
   - If first time: Click "Configure account" → Select your GitHub username
   - Grant Render access to repositories
   - Search for: `Et-Gen-AI-hackathon-26`
   - Click **"Connect"** next to your repository

✅ **Render will analyze your repository**

---

## Step 3: Configure Web Service

Fill in the following details:

### Basic Settings

| Field | Value |
|-------|-------|
| **Name** | `enewspaper-backend` (or any name you want) |
| **Region** | Choose closest to you (e.g., Oregon, Frankfurt) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` (should auto-detect) |

### Build & Deploy Settings

| Field | Value |
|-------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port 10000` |

### Instance Type

| Field | Value |
|-------|-------|
| **Instance Type** | `Free` (sufficient for demo) |

---

## Step 4: Add Environment Variables

**Scroll down to "Environment Variables" section**

Click **"Add Environment Variable"** and add these **ONE BY ONE**:

### Variable 1: GROQ_API_KEY
```
Key:   GROQ_API_KEY
Value: your_actual_groq_api_key_here
```
👉 **Get from:** [console.groq.com](https://console.groq.com)
- Login → API Keys → Create API Key → Copy it

### Variable 2: PEXELS_API_KEY
```
Key:   PEXELS_API_KEY
Value: your_actual_pexels_api_key_here
```
👉 **Get from:** [pexels.com/api](https://www.pexels.com/api/)
- Login → Your API Key → Copy it

### Variable 3: HOST
```
Key:   HOST
Value: 0.0.0.0
```

⚠️ **Note:** Render automatically sets the PORT. We use port 10000 in the start command.

---

## Step 5: Advanced Settings (Optional but Recommended)

**Click "Advanced" to expand**

| Setting | Value |
|---------|-------|
| **Auto-Deploy** | Yes (default) |
| **Health Check Path** | `/health` |

---

## Step 6: Create Web Service

1. **Review all settings**
2. **Click "Create Web Service"** (bottom)
3. **Wait for deployment** (5-10 minutes first time)

### What Happens Now:

```
⏳ Render is:
   1. Pulling code from GitHub
   2. Installing Python 3.11
   3. Installing dependencies (pip install)
   4. Starting your FastAPI server
   5. Health checking /health endpoint
```

### Monitor Deployment:

You'll see logs in real-time:
```
==> Cloning from https://github.com/kashif2798/Et-Gen-AI-hackathon-26...
==> Installing dependencies...
==> Successfully installed fastapi uvicorn...
==> Starting server...
==> Your service is live 🎉
```

---

## Step 7: Get Backend URL

Once deployed (status shows "Live" with green dot):

1. **Copy the URL** at the top (looks like: `https://enewspaper-backend.onrender.com`)
2. **Test it** - Open in browser:
   ```
   https://your-backend-url.onrender.com/health
   ```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "E-newspaper API",
  "version": "0.1.0",
  "vector_store": {},
  "chatbot": "initializing"
}
```

✅ **If you see this, backend is working!**

---

## Step 8: Initial Data Ingestion (Important!)

Your backend needs articles. Let's load them:

**Open Command Prompt / Terminal and run:**

```bash
curl -X POST https://your-backend-url.onrender.com/ingest/live?quick=true
```

**Replace** `your-backend-url` with your actual Render URL.

**Example:**
```bash
curl -X POST https://enewspaper-backend.onrender.com/ingest/live?quick=true
```

⏳ **Wait 10-15 seconds**

**Expected Response:**
```json
{
  "status": "success",
  "articles_collected": 65,
  "articles_processed": 65,
  "chunks_stored": 156,
  "mode": "quick"
}
```

✅ **Backend is now ready with articles!**

---

# PART 2: Deploy Frontend to Vercel ⚡

## Step 1: Create Vercel Account

1. **Go to [vercel.com](https://vercel.com)**
2. Click **"Sign Up"** (top right)
3. **Sign up with GitHub**
   - Click "Continue with GitHub"
   - Authorize Vercel
   - Complete any verification if needed

✅ **You should now be on Vercel Dashboard**

---

## Step 2: Import Project

1. **Click "Add New..."** (top right)
2. **Select "Project"**
3. **Import Git Repository**
   - You should see your GitHub repositories
   - If not, click "Adjust GitHub App Permissions" → Grant access
   - Find: `Et-Gen-AI-hackathon-26`
   - Click **"Import"**

✅ **Vercel will analyze your repository**

---

## Step 3: Configure Project

### Framework Preset
```
Framework Preset: Next.js
(Should auto-detect)
```

### Root Directory
⚠️ **IMPORTANT:** Don't use default root!

1. **Click "Edit"** next to Root Directory
2. **Select:** `frontend`
3. **Click "Continue"**

---

## Step 4: Build & Output Settings

Vercel auto-detects these, but verify:

| Setting | Value |
|---------|-------|
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |

Leave as default if already set.

---

## Step 5: Add Environment Variables

**Click "Environment Variables" section**

### Add Your Backend URL:

```
Key:   NEXT_PUBLIC_API_URL
Value: https://your-backend-url.onrender.com
```

**Replace with your actual Render URL from Part 1, Step 7**

**Example:**
```
Key:   NEXT_PUBLIC_API_URL
Value: https://enewspaper-backend.onrender.com
```

⚠️ **Important Notes:**
- Do NOT add `/api` at the end
- Do NOT add trailing slash `/`
- Must start with `https://`

---

## Step 6: Deploy

1. **Review all settings**
2. **Click "Deploy"** (bottom)
3. **Wait for build** (2-3 minutes)

### What Happens Now:

```
⏳ Vercel is:
   1. Cloning your repository
   2. Installing Node.js dependencies
   3. Building Next.js app
   4. Optimizing production build
   5. Deploying to Edge Network
```

### Monitor Build:

You'll see build logs:
```
▲ Vercel CLI
  Installing dependencies...
  Building...
  Optimizing images...
  Generating static pages...
  ✓ Build completed
  🎉 Deployment ready
```

---

## Step 7: Get Frontend URL

Once deployed:

1. **Click "Visit"** or copy the URL
2. **URL format:** `https://et-gen-ai-hackathon-26.vercel.app`
3. **Open in browser**

✅ **You should see the E-newspaper welcome screen!**

---

## Step 8: Test Your Deployment

### Test Checklist:

1. **Welcome Screen**
   - [ ] Logo displays (E-newspaper gradient)
   - [ ] "Start Reading" button works

2. **Persona Selection**
   - [ ] Click "Start Reading"
   - [ ] See 4 personas (Student, Investor, etc.)
   - [ ] Click any persona

3. **Home Screen**
   - [ ] Articles load (may take 10 seconds first time)
   - [ ] Categories work (Markets, Tech, etc.)
   - [ ] Article cards display with images

4. **Article Detail**
   - [ ] Click any article
   - [ ] AI analysis starts automatically
   - [ ] Bull and Bear views appear (wait 10-15 seconds)
   - [ ] Moderator summary shows

5. **Chat Widget**
   - [ ] Click chat icon (bottom right)
   - [ ] Type a question
   - [ ] Get AI response

6. **Video Studio** (Optional - takes longer)
   - [ ] Click "Video Studio" from article
   - [ ] Select article
   - [ ] Click "Produce Briefing"
   - [ ] Wait 60 seconds
   - [ ] Video plays with audio

---

# PART 3: Post-Deployment Configuration 🔧

## Step 1: Update CORS (Important!)

Your backend needs to allow requests from your Vercel domain.

### On Render Dashboard:

1. **Go to your backend service**
2. **Click "Shell"** (left sidebar)
3. **Or use Environment Variables:**
   - Add new variable:
     ```
     Key:   ALLOWED_ORIGINS
     Value: https://et-gen-ai-hackathon-26.vercel.app
     ```
   - Click "Save Changes"

### Or Update Code (Better):

If CORS errors occur, update `backend/main.py`:

**Find this section:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Replace with:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://et-gen-ai-hackathon-26.vercel.app",  # Your Vercel URL
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Push changes:**
```bash
cd C:\Users\USER\OneDrive\Desktop\projects\ET_news
git add backend/main.py
git commit -m "Update CORS for Vercel domain"
git push origin main
```

Render will auto-redeploy (if auto-deploy enabled).

---

## Step 2: Custom Domain (Optional)

### For Vercel (Frontend):

1. **Go to Vercel Dashboard** → Your Project
2. **Click "Settings"** → "Domains"
3. **Add your domain:**
   - Enter: `your-domain.com`
   - Follow DNS instructions
   - Vercel provides SSL automatically

### For Render (Backend):

1. **Go to Render Dashboard** → Your Service
2. **Click "Settings"** → "Custom Domain"
3. **Add your domain:**
   - Enter: `api.your-domain.com`
   - Add CNAME record to DNS
   - Render provides SSL automatically

---

## Step 3: Performance Optimization

### Enable Vercel Analytics:

1. **Go to Vercel Project** → "Analytics"
2. **Click "Enable"**
3. **Free tier includes:**
   - Web Vitals monitoring
   - Page views
   - Unique visitors

### Monitor Render Logs:

1. **Go to Render Service** → "Logs"
2. **Watch for errors:**
   - GROQ API failures
   - Out of memory errors
   - Timeout errors

---

# Troubleshooting 🔧

## Backend Issues (Render)

### Problem: Build Fails

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
1. Check `requirements.txt` exists in `backend/` folder
2. Verify Build Command: `pip install -r requirements.txt`
3. Check logs for specific missing package
4. Verify Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Manually trigger redeploy: Dashboard → "Manual Deploy" → "Clear build cache & deploy"

---

### Problem: Health Check Fails

**Error:** `Health check failed: GET /health returned 404`

**Solution:**
1. Verify Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
2. Check Health Check Path is `/health` (not `/api/health`)
3. View logs for actual error
4. Ensure `main.py` has `@app.get("/health")` endpoint

---

### Problem: GROQ API Errors

**Error:** `401 Unauthorized` or `Invalid API key`

**Solution:**
1. Verify GROQ_API_KEY in Environment Variables
2. Check key has no extra spaces
3. Regenerate key at [console.groq.com](https://console.groq.com)
4. Update environment variable
5. Manually restart service

---

### Problem: Out of Memory

**Error:** `MemoryError` or service crashes

**Solution:**
1. Upgrade to Starter plan ($7/month) for more RAM
2. Or reduce `limit_per_feed` in ingestion (from 50 to 20)
3. Clear vector database: `curl -X POST your-url/reset`

---

### Problem: Slow Response Times

**Symptoms:** API calls take >30 seconds

**Solution:**
1. **Render free tier "spins down"** after inactivity
   - First request takes 30-50 seconds to wake up
   - Subsequent requests are fast
2. **Upgrade to Starter plan** for always-on service
3. **Or:** Set up a cron job to ping `/health` every 10 minutes

---

## Frontend Issues (Vercel)

### Problem: Build Fails

**Error:** `Module not found: Can't resolve '@/components/...'`

**Solution:**
1. Verify Root Directory is `frontend` (not project root)
2. Check `package.json` exists in `frontend/` folder
3. Clear build cache: Dashboard → Settings → General → "Clear Build Cache"
4. Redeploy

---

### Problem: API Calls Fail

**Error:** `Failed to fetch` or `Network Error`

**Solutions:**

1. **Check Environment Variable:**
   - Go to Vercel → Settings → Environment Variables
   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Must be: `https://your-backend.onrender.com` (no trailing slash)

2. **Redeploy after changing env vars:**
   - Deployments → Latest → "Redeploy"
   - Or push a new commit to trigger build

3. **Check CORS on backend** (see Part 3, Step 1)

---

### Problem: Articles Not Loading

**Symptoms:** Stuck on loading screen, no articles

**Solution:**
1. **Backend might be asleep** (Render free tier)
   - Wait 30 seconds for wake up
   - Refresh page

2. **No articles in database:**
   - Run ingestion: `curl -X POST your-backend-url/ingest/live?quick=true`
   - Wait 15 seconds
   - Refresh frontend

3. **Check backend health:**
   - Open: `your-backend-url/health`
   - Should see: `"status": "healthy"`

---

### Problem: Images Not Loading

**Symptoms:** Broken image icons, fallback thumbnails

**Solution:**
- This is **normal** - RSS feeds often have broken/missing images
- Frontend generates beautiful gradient fallback thumbnails
- Not a deployment issue

---

### Problem: Video Generation Fails

**Error:** `Video generation failed` or timeout

**Solution:**
1. **Verify Pexels API Key:**
   - Render → Environment Variables
   - Check `PEXELS_API_KEY` is correct

2. **Check disk space:**
   - Render free tier has limited storage
   - Old videos auto-delete after generation

3. **Increase timeout** (if needed):
   - Edit `frontend/app/page.tsx`
   - Find: `setTimeout(() => ..., 60000)`
   - Change to: `120000` (2 minutes)
   - Push changes

---

## CORS Errors

### Problem: CORS Policy Error

**Error in browser console:**
```
Access to fetch at 'https://backend.onrender.com/...' 
from origin 'https://app.vercel.app' has been blocked by CORS policy
```

**Solution:**

1. **Update backend CORS** (see Part 3, Step 1)
2. **Or add wildcard temporarily** (testing only):
   ```python
   allow_origins=["*"]
   ```
3. **Push changes and wait for Render to redeploy**

---

# Performance Tips 🚀

## Free Tier Limitations

### Render Free Tier:
- ⚠️ **Spins down after 15 min inactivity**
- ⚠️ **750 hours/month free** (about 31 days)
- ⚠️ **512 MB RAM**
- ✅ **Unlimited bandwidth**
- ✅ **SSL included**

**Recommendation:** Keep awake with UptimeRobot (free service):
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add monitor: Your backend URL + `/health`
3. Check every 5 minutes
4. Keeps backend always warm

### Vercel Free Tier:
- ✅ **100 GB bandwidth/month**
- ✅ **Unlimited requests**
- ✅ **100 build hours/month**
- ✅ **SSL included**
- ✅ **Edge Network (fast globally)**

---

## Speed Optimizations

1. **Enable Vercel Edge Caching:**
   - Already configured in `next.config.js`
   - Static assets cached on CDN

2. **Backend Caching:**
   - Article lists cached for 5 minutes
   - Reduces database queries

3. **Preload Critical Data:**
   - Frontend prefetches on persona selection
   - Smoother transitions

---

# Monitoring & Maintenance 📊

## Vercel Dashboard

**Monitor these metrics:**
1. **Deployments** - Build status, deploy times
2. **Analytics** - Page views, Web Vitals
3. **Logs** - Runtime errors, API call errors

**Access:** Vercel Dashboard → Your Project → Analytics/Logs

## Render Dashboard

**Monitor these metrics:**
1. **CPU Usage** - Should stay below 50%
2. **Memory Usage** - Watch for OOM errors
3. **Response Times** - Should be <2 seconds
4. **Logs** - Python errors, API errors

**Access:** Render Dashboard → Your Service → Metrics/Logs

---

# Updating Your Deployment 🔄

## When You Push Code to GitHub:

### Auto-Deploy (Default):
- **Render:** Automatically rebuilds and redeploys
- **Vercel:** Automatically rebuilds and redeploys
- **Time:** 2-3 minutes each

### Manual Deploy:
- **Render:** Dashboard → Manual Deploy
- **Vercel:** Dashboard → Deployments → Redeploy

---

# Cost Breakdown 💰

## Free Tier (Sufficient for Hackathon):

```
Render Free:     $0/month
Vercel Free:     $0/month
GROQ API:        $0/month (generous free tier)
Pexels API:      $0/month (unlimited)
───────────────────────────
TOTAL:           $0/month
```

**Limitations:**
- Backend sleeps after 15 min (30s wake time)
- 750 hours/month backend uptime
- Perfect for demo/hackathon

## Starter Tier (Production):

```
Render Starter:  $7/month (always-on, 512MB RAM)
Vercel Hobby:    $0/month (still free!)
GROQ API:        ~$5/month (pay-as-you-go)
Pexels API:      $0/month
───────────────────────────
TOTAL:           ~$12/month
```

**Benefits:**
- No sleep time
- Faster response
- More reliable

---

# Final Checklist ✅

Before sharing your app:

- [ ] Backend deployed on Render (green "Live" status)
- [ ] Backend health check passes: `your-url/health`
- [ ] Articles ingested (run `/ingest/live?quick=true`)
- [ ] Frontend deployed on Vercel
- [ ] Environment variable set correctly (`NEXT_PUBLIC_API_URL`)
- [ ] CORS configured with Vercel domain
- [ ] Welcome screen loads
- [ ] Can select persona
- [ ] Articles display on home
- [ ] AI analysis works (click article)
- [ ] Chat widget responds
- [ ] Video generation works (optional test)

---

# Your Deployment URLs 🌐

After completing this guide, you'll have:

```
🎯 Frontend (Vercel):
   https://et-gen-ai-hackathon-26.vercel.app

🔧 Backend (Render):
   https://enewspaper-backend.onrender.com

📊 Health Check:
   https://enewspaper-backend.onrender.com/health

📚 API Docs:
   https://enewspaper-backend.onrender.com/docs
```

---

# Support & Resources 📞

**If you get stuck:**

1. **Check Logs First:**
   - Render: Dashboard → Logs
   - Vercel: Dashboard → Deployments → Runtime Logs

2. **Common Issues:**
   - See Troubleshooting section above
   - Most issues are CORS or environment variables

3. **Documentation:**
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
   - [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

4. **GitHub Issues:**
   - [Report Bug](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues)

---

<div align="center">

# 🎉 Congratulations!

**Your E-newspaper Platform is now live!**

Share your Vercel URL with the world! 🌍

[View Documentation](./README.md) • 
[Report Issues](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues)

</div>
