# 🔧 Render Deployment - Troubleshooting Guide

## ✅ Your Backend is Deployed Successfully!

**URL:** https://et-gen-ai-hackathon-26.onrender.com

---

## Understanding the "Not Found" Message

When you visit the root URL, you see:
```json
{"detail":"Not Found"}
```

**This is now FIXED!** After the latest push, you'll see:
```json
{
  "message": "E-newspaper API",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs",
  "endpoints": { ... }
}
```

---

## ✅ How to Test Your Backend

### 1. Health Check
```bash
https://et-gen-ai-hackathon-26.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "E-newspaper API",
  "version": "0.1.0",
  "vector_store": { "points_count": 0 },
  "chatbot": "operational"
}
```

### 2. API Documentation
```bash
https://et-gen-ai-hackathon-26.onrender.com/docs
```
Opens interactive Swagger UI where you can test all endpoints.

---

## 📰 Loading Articles (IMPORTANT!)

Your backend needs articles. Here's how to load them:

### Method 1: Using Command Prompt (Windows)

**Open Command Prompt** (Win + R → type `cmd` → Enter)

```bash
curl -X POST https://et-gen-ai-hackathon-26.onrender.com/ingest/live?quick=true
```

### Method 2: Using PowerShell (Windows)

**Open PowerShell** (Win + X → Windows PowerShell)

```powershell
Invoke-WebRequest -Method POST -Uri "https://et-gen-ai-hackathon-26.onrender.com/ingest/live?quick=true"
```

### Method 3: Using Browser

Open this URL in Chrome/Edge:
```
https://et-gen-ai-hackathon-26.onrender.com/docs
```

1. Find `/ingest/live` endpoint
2. Click "Try it out"
3. Set `quick` parameter to `true`
4. Click "Execute"

---

## 🐛 502 Bad Gateway - Memory Issue (SOLVED)

### What Happened:
- Render free tier has **512 MB RAM limit**
- Your original code tried to load 50 articles per category (650+ articles)
- This caused memory overflow → crash → 502 error

### What I Fixed:
1. **Reduced article limits:**
   - Quick mode: 3 articles per category (~40 articles total)
   - Full mode: 20 articles per category (~260 articles total)

2. **Added batch processing:**
   - Processes chunks in batches of 50/100
   - Prevents memory spikes

3. **Optimized defaults:**
   - `quick=true` is now the default
   - Safer for free tier

### How to Use After Fix:

**Wait for Render to rebuild** (2-3 minutes after push):
1. Go to Render Dashboard
2. Your service will show "Deploying..."
3. Wait for "Live" status with green dot

**Then load articles:**
```bash
curl -X POST https://et-gen-ai-hackathon-26.onrender.com/ingest/live?quick=true
```

**Expected Response:**
```json
{
  "status": "success",
  "articles_collected": 39,
  "articles_processed": 39,
  "chunks_stored": 85,
  "mode": "quick"
}
```

---

## 🔄 If Service Crashes Again

### Check Render Logs:
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" (left sidebar)
4. Look for errors

### Common Issues:

#### Out of Memory (OOM)
**Symptom:** `MemoryError` or service restarts
**Solution:** 
- Use quick mode only: `?quick=true`
- Or upgrade to Starter plan ($7/month for 512 MB → 2 GB)

#### Service Won't Start
**Symptom:** Stuck in "Deploying" or immediate crash
**Solution:**
- Check environment variables (GROQ_API_KEY, PEXELS_API_KEY)
- Check start command: `uvicorn main:app --host 0.0.0.0 --port 10000`

#### Timeout Errors
**Symptom:** 504 Gateway Timeout
**Solution:**
- Render free tier "spins down" after 15 min inactivity
- First request takes 30-50 seconds to wake up
- Just wait and retry

---

## 📊 Monitoring Your Backend

### Check Status:
```bash
https://et-gen-ai-hackathon-26.onrender.com/health
```

### Check Article Count:
Look at `vector_store.points_count` in health response:
- `0` = No articles loaded yet
- `>0` = Articles loaded successfully

### Check Available Endpoints:
```bash
https://et-gen-ai-hackathon-26.onrender.com/
```

Now shows all available endpoints.

---

## 🎯 Next Steps

### 1. Wait for Redeploy (2-3 min)

Render will automatically rebuild with the fixes:
- ✅ Root endpoint added
- ✅ Memory optimized
- ✅ Batch processing added

### 2. Load Articles

Once "Live", run:
```bash
curl -X POST https://et-gen-ai-hackathon-26.onrender.com/ingest/live?quick=true
```

Wait ~10-15 seconds for response.

### 3. Verify Articles Loaded

```bash
curl https://et-gen-ai-hackathon-26.onrender.com/health
```

Check `vector_store.points_count` > 0

### 4. Test Article Endpoint

```bash
curl https://et-gen-ai-hackathon-26.onrender.com/articles?limit=5
```

Should return array of articles.

### 5. Deploy Frontend to Vercel

Now that backend is ready, deploy frontend:

See **VERCEL_RENDER_DEPLOYMENT.md** - Part 2

---

## 💡 Tips for Render Free Tier

### Keep Service Warm:
Free tier sleeps after 15 min inactivity.

**Solution:** Use UptimeRobot (free):
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add monitor: `https://et-gen-ai-hackathon-26.onrender.com/health`
3. Check every 5 minutes
4. Keeps backend always ready

### Reduce Memory Usage:
- Always use `?quick=true` for ingestion
- Don't run full mode on free tier
- Clear old data: `POST /reset` if needed

### Upgrade When Ready:
Starter plan ($7/month) gives:
- Always-on (no sleep)
- More memory (better performance)
- Faster response times

---

## 🆘 Still Having Issues?

### 1. Check Render Dashboard
- Service status (should be green "Live")
- Recent logs (last 100 lines)
- Metrics (CPU, memory usage)

### 2. Test Individual Endpoints

**Health:**
```bash
curl https://et-gen-ai-hackathon-26.onrender.com/health
```

**Root:**
```bash
curl https://et-gen-ai-hackathon-26.onrender.com/
```

**API Docs:**
Open in browser:
```
https://et-gen-ai-hackathon-26.onrender.com/docs
```

### 3. Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| 502 Bad Gateway | Service crashed | Wait 1 min, service auto-restarts |
| 503 Service Unavailable | Deploying or starting | Wait 2-3 min |
| 504 Gateway Timeout | Waking up from sleep | Wait 30s, retry |
| 404 Not Found | Wrong endpoint | Check URL spelling |

---

## ✅ Success Checklist

After fixes deploy, verify:

- [ ] Root URL shows endpoint list (not "Not Found")
- [ ] `/health` returns status "healthy"
- [ ] `/docs` opens Swagger UI
- [ ] Ingestion completes without 502 error
- [ ] `vector_store.points_count` > 0
- [ ] `/articles` returns article list

---

## 📞 Need More Help?

- **Logs:** Render Dashboard → Your Service → Logs
- **Docs:** [render.com/docs](https://render.com/docs)
- **Guide:** See VERCEL_RENDER_DEPLOYMENT.md

---

<div align="center">

**Your backend is now optimized for Render free tier!** 🎉

Next: Deploy frontend to Vercel

</div>
