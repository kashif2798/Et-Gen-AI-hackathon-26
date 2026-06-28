# Auto-Ingestion Setup - Complete Guide

## ✅ What's Been Configured

### 1. **Backend Auto-Ingestion on Startup**

When the backend starts:
1. Checks if vector database has articles
2. If **empty**: Automatically fetches **50 live articles per RSS category**
3. If **fetch fails**: Falls back to static dataset
4. If **data exists**: Skips ingestion (avoids duplicates)

**Benefits:**
- No manual button clicking needed
- Fresh articles on first startup
- Fallback protection if RSS fails

---

### 2. **Frontend Auto-Loading**

When you select a persona and reach the home screen:
1. Frontend checks if articles exist
2. If **no articles**: Automatically triggers live ingestion
3. Articles display immediately after ingestion

**Benefits:**
- Seamless user experience
- No "Load Data" button needed
- Articles appear automatically

---

### 3. **50 Articles Per Category**

Changed from 20 → **50 articles per RSS feed**

**RSS Feeds Configured:**
- Top Stories
- Markets
- Tech
- Politics
- Economy
- Startups
- Wealth
- Industry
- Environment
- International
- Opinion
- Mutual Funds
- Corporate Governance

**Expected Total:** ~650 articles (50 × 13 categories)

---

## 🚀 How to Use

### **Method 1: Fresh Start (Recommended)**

1. **Stop the backend** (Ctrl+C)

2. **Clear the old database:**
   ```bash
   # Windows
   rmdir /s /q backend\et_nexus_db
   
   # Or via Python
   curl -X DELETE http://localhost:8000/articles/clear
   ```

3. **Start the backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Watch the logs:**
   ```
   📭 Vector store is empty. Triggering auto-ingestion...
   🔴 AUTO-INGESTION: Fetching live articles on startup...
   📡 Fetching articles from RSS feeds...
   ✅ Fetched XXX articles
   ✅ AUTO-INGESTION COMPLETE: XXX articles, XXXX chunks stored
   ✅ E-newspaper Backend ready!
   ```

5. **Open frontend:**
   ```
   http://localhost:3000
   ```

6. **Navigate:**
   - Click "Begin Discovery"
   - Select a persona
   - Articles load automatically! ✨

---

### **Method 2: Keep Existing Data**

If backend already has 794 chunks (old data):

**Option A: Keep old data**
- Backend will skip auto-ingestion
- Old articles remain
- To get new articles, manually call: `POST /ingest/live`

**Option B: Clear and refresh**
- Use Method 1 above

---

## 🔧 Technical Details

### Backend Changes

**File:** `backend/main.py`

```python
# In lifespan() function:
if points > 0:
    print("💡 Skipping auto-ingestion (data already exists)")
else:
    # Auto-ingest on startup
    collector = DataCollector()
    articles_list = await collector.collect_from_rss(limit_per_feed=50)
    # ... process and store
```

**Ingestion endpoint updated:**
```python
@app.post("/ingest/live")
async def ingest_live_articles():
    # Changed: limit_per_feed=50 (was 20)
    articles_list = await collector.collect_from_rss(limit_per_feed=50)
```

---

### Frontend Changes

**File:** `frontend/app/page.tsx`

```typescript
// Auto-load articles on home screen
useEffect(() => {
  if (screen === "home") {
    loadArticles();
    
    // Auto-trigger ingestion if no articles
    if (articles.length === 0 && !ingested && !isIngesting) {
      handleIngest();
    }
  }
}, [screen]);
```

**Import added:**
```typescript
import { analyzeNews, fetchArticles, ingestFallback, ingestLive, generateVideo, API_BASE } from "@/lib/api";
```

---

## 📊 Expected Results

### Backend Startup (First Time)
```
🚀 E-newspaper Backend starting up...
📭 Vector store is empty. Triggering auto-ingestion...

======================================================================
🔴 AUTO-INGESTION: Fetching live articles on startup...
======================================================================
📡 Fetching articles from RSS feeds...
   Fetching category [Top Stories]: https://economictimes...
   → Scraping: Latest Economic News Article...
   ✅ Scraped 48 articles from feed

📊 Total unique articles scraped: 624

✅ Fetched 624 articles
🛠️  Preprocessing articles...
✂️  Chunking articles...
💾 Storing chunks in vector database...

✅ AUTO-INGESTION COMPLETE: 624 articles, 2080 chunks stored
======================================================================

✅ E-newspaper Backend ready!
```

### Backend Startup (Subsequent Times)
```
🚀 E-newspaper Backend starting up...
📊 Vector store ready with 2080 chunks
💡 Skipping auto-ingestion (data already exists)
✅ E-newspaper Backend ready!
```

### Frontend Console
```
📰 Loading articles...
✅ Loaded 624 articles
```

---

## 🎯 Testing Steps

### 1. Test Auto-Ingestion

```bash
# Clear database
rmdir /s /q backend\et_nexus_db

# Start backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Watch logs for auto-ingestion
# Should see "AUTO-INGESTION COMPLETE"
```

### 2. Test Frontend Auto-Load

```bash
# Open browser
http://localhost:3000

# Click "Begin Discovery"
# Select any persona
# Articles should appear automatically (no button needed)
```

### 3. Verify Article Count

```bash
# Check health endpoint
curl http://localhost:8000/health

# Look for "points_count" - should be ~2000-2500 (50 articles × 13 categories)
```

### 4. Verify Fresh Dates

```bash
# Get articles
curl http://localhost:8000/articles

# Check dates - should be 2026-06 (current month)
```

---

## 🐛 Troubleshooting

### Auto-Ingestion Not Triggering

**Symptom:** Backend shows "Vector store ready with 794 chunks"

**Cause:** Database already has data from previous ingestion

**Fix:**
```bash
# Clear database
curl -X DELETE http://localhost:8000/articles/clear

# Or delete folder
rmdir /s /q backend\et_nexus_db

# Restart backend
```

---

### RSS Fetch Fails

**Symptom:** "No articles fetched, loading fallback dataset..."

**Cause:** Network issues or RSS feeds blocked

**Fix:**
- Check internet connection
- Try accessing RSS in browser: `https://economictimes.indiatimes.com/rssfeeds/1221656.cms`
- Backend will automatically use fallback dataset

---

### Frontend Shows "No articles yet"

**Symptom:** Empty screen with "Load articles to get started"

**Cause:** 
1. Backend not running
2. Backend ingestion failed
3. CORS issues

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check articles exist
curl http://localhost:8000/articles

# If empty, manually trigger
curl -X POST http://localhost:8000/ingest/live
```

---

## 🎉 Success Indicators

✅ Backend logs show "AUTO-INGESTION COMPLETE"  
✅ Vector store has 2000+ chunks  
✅ Frontend shows articles immediately  
✅ Article dates are current (2026-06)  
✅ No manual button clicking needed  
✅ 50+ articles per category  

---

## 📝 Summary

**Before:**
- Manual "Load Data" button required
- Only 20 articles per category
- Old fallback articles (2026-03)

**After:**
- ✅ Auto-ingestion on backend startup
- ✅ 50 articles per category (~650 total)
- ✅ Frontend auto-loads articles
- ✅ Current dates (2026-06)
- ✅ Seamless user experience

**Next Steps:**
1. Clear old database
2. Restart backend
3. Watch auto-ingestion happen
4. Open frontend and enjoy fresh articles!
