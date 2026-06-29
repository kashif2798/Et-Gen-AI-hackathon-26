# ⚡ Quick Deploy Checklist - Vercel + Render

> **Fast reference for deploying E-newspaper Platform**

---

## 🎯 Prerequisites (Get These First!)

- [ ] GitHub repo pushed: `kashif2798/Et-Gen-AI-hackathon-26`
- [ ] GROQ API Key: [console.groq.com](https://console.groq.com)
- [ ] Pexels API Key: [pexels.com/api](https://www.pexels.com/api/)

---

## 🐳 PART 1: Render Backend (15 minutes)

### Step 1: Create Account
- Go to [render.com](https://render.com)
- Sign up with GitHub

### Step 2: New Web Service
- Click "New +" → "Web Service"
- Connect repo: `kashif2798/Et-Gen-AI-hackathon-26`

### Step 3: Configure
```
Name:           enewspaper-backend
Branch:         main
Root Directory: backend
Runtime:        Python 3
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn main:app --host 0.0.0.0 --port 10000
Instance:       Free
```

### Step 4: Environment Variables
```
GROQ_API_KEY      = your_groq_key
PEXELS_API_KEY    = your_pexels_key
HOST              = 0.0.0.0
```

### Step 5: Deploy & Test
- Click "Create Web Service"
- Wait 5-10 minutes
- Copy URL: `https://enewspaper-backend.onrender.com`
- Test: Open `your-url/health` in browser

### Step 6: Load Articles
```bash
curl -X POST https://your-backend-url.onrender.com/ingest/live?quick=true
```

✅ **Backend Ready!**

---

## ⚡ PART 2: Vercel Frontend (10 minutes)

### Step 1: Create Account
- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub

### Step 2: Import Project
- Click "Add New..." → "Project"
- Import: `kashif2798/Et-Gen-AI-hackathon-26`

### Step 3: Configure
```
Framework:      Next.js (auto-detect)
Root Directory: frontend (Click Edit to change!)
Build Command:  npm run build
```

### Step 4: Environment Variable
```
NEXT_PUBLIC_API_URL = https://your-backend-url.onrender.com
```
⚠️ Replace with YOUR actual Render URL!

### Step 5: Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Copy URL: `https://et-gen-ai-hackathon-26.vercel.app`

✅ **Frontend Ready!**

---

## 🔧 PART 3: Final Config (5 minutes)

### Update CORS on Backend

**Option A: Via Render Environment Variables**
```
Add new variable:
ALLOWED_ORIGINS = https://your-vercel-url.vercel.app
```

**Option B: Update Code (Better)**

Edit `backend/main.py`, find CORS section, replace with:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://et-gen-ai-hackathon-26.vercel.app",  # Your Vercel URL
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push to GitHub:
```bash
git add backend/main.py
git commit -m "Add CORS for Vercel"
git push origin main
```

Render auto-redeploys in 2-3 minutes.

---

## ✅ Testing Checklist

Open your Vercel URL and test:

- [ ] Welcome screen loads
- [ ] Click "Start Reading"
- [ ] Select any persona
- [ ] Articles load (wait 30 sec if first time - backend waking up)
- [ ] Click article → AI analysis appears (10-15 sec)
- [ ] Chat widget works (bottom right)
- [ ] Categories filter articles

---

## 🐛 Quick Troubleshooting

### Backend won't start
- Check Build Command: `pip install -r requirements.txt`
- Check Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- View logs: Render Dashboard → Logs

### Frontend "Failed to fetch"
- Check `NEXT_PUBLIC_API_URL` has correct backend URL
- Must have `https://` and NO trailing `/`
- Redeploy after changing env var

### No articles loading
- Backend sleeping (free tier) - wait 30 seconds
- Or run ingestion: `curl -X POST your-url/ingest/live?quick=true`

### CORS errors
- Update CORS in backend (see Part 3)
- Add your Vercel URL to `allow_origins`

---

## 📊 Your URLs

After deployment:

```
Frontend:  https://et-gen-ai-hackathon-26.vercel.app
Backend:   https://enewspaper-backend.onrender.com
Health:    https://enewspaper-backend.onrender.com/health
API Docs:  https://enewspaper-backend.onrender.com/docs
```

---

## 💰 Cost

```
Render Free:  $0/month (with sleep after 15 min)
Vercel Free:  $0/month
GROQ API:     $0/month (free tier)
Pexels:       $0/month
──────────────────────────
TOTAL:        $0/month
```

Perfect for hackathon demo! 🎉

---

## 📚 Full Documentation

For detailed step-by-step with screenshots and troubleshooting:

👉 **[VERCEL_RENDER_DEPLOYMENT.md](./VERCEL_RENDER_DEPLOYMENT.md)**

---

## 🆘 Need Help?

1. Check full guide: `VERCEL_RENDER_DEPLOYMENT.md`
2. Check logs on Render/Vercel dashboards
3. GitHub issues: [Report bug](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues)

---

<div align="center">

**Total Time: ~30 minutes**

🎉 **Good luck with your deployment!** 🎉

</div>
