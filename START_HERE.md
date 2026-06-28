# 🚀 START HERE - E-newspaper Quick Setup

> **Get your E-newspaper platform running in 5 minutes!**

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Configure API Keys

Create `backend/.env`:
```bash
GROQ_API_KEY=your_groq_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

**Get Free API Keys:**
- GROQ: https://console.groq.com/ (sign up → create API key)
- Pexels: https://www.pexels.com/api/ (sign up → generate key)

### Step 3: Run the App

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload
```
✅ Backend: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✅ Frontend: http://localhost:3000

---

## 🎯 First Time Usage

1. Open http://localhost:3000
2. Click "Start Reading"
3. Select a persona (e.g., "Student")
4. Wait 10 seconds for quick article ingestion
5. Browse and analyze articles!

---

## 📚 Documentation

- **[README.md](./README.md)** - Complete project overview
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[FRONTEND_DESIGN.md](./FRONTEND_DESIGN.md)** - Design system docs
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical architecture

---

## 🐛 Troubleshooting

### Backend won't start
- ✅ Check Python version: `python --version` (need 3.11+)
- ✅ Activate virtual environment: `.venv\Scripts\activate`
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check API keys in `.env` file

### Frontend won't start
- ✅ Check Node version: `node --version` (need 18+)
- ✅ Install dependencies: `npm install`
- ✅ Clear cache: `rm -rf .next` then `npm run dev`

### No articles loading
- ✅ Backend must be running first
- ✅ Wait 10 seconds for auto-ingestion
- ✅ Or manually ingest: `curl -X POST http://localhost:8000/ingest/live?quick=true`

### GROQ API errors
- ✅ Check API key is correct in `.env`
- ✅ Verify key has credits: https://console.groq.com/
- ✅ Try regenerating the key

---

## 🎉 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Articles loading on home screen
- [ ] AI analysis working (click an article)
- [ ] Chatbot responding (click chat icon)
- [ ] Video generation working (click "Video Studio")

---

## 🚀 Deploy to Production

Ready to deploy? Follow the **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**

**Recommended:**
- Frontend: Vercel (free, zero-config)
- Backend: Railway (free $5 credit)

**Total time:** 15 minutes

---

## 📞 Need Help?

- **Issues:** https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues
- **Documentation:** See `docs/` folder
- **GitHub:** https://github.com/kashif2798

---

## 🎓 What's Next?

1. ✅ **Explore Features:**
   - Try all 4 personas
   - Generate a video briefing
   - Create a story arc
   - Chat with articles

2. ✅ **Customize:**
   - Add more RSS feeds (see `backend/ingestion/data_collector.py`)
   - Modify personas (see `frontend/app/page.tsx`)
   - Adjust design (see `frontend/app/globals.css`)

3. ✅ **Deploy:**
   - Follow DEPLOYMENT_GUIDE.md
   - Share your URL!

---

<div align="center">

**Happy Building! 🎉**

[Report Bug](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues) • 
[Request Feature](https://github.com/kashif2798/Et-Gen-AI-hackathon-26/issues)

</div>
