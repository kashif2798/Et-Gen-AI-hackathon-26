# How to Get Live Articles - Step by Step Guide

## Problem
The articles you're seeing are old articles from the previous ingestion (794 chunks in database). You need to fetch NEW articles from live RSS feeds.

## Solution - 2 Options

### Option 1: Use the Frontend (Recommended)

1. **Open the frontend**
   ```
   http://localhost:3000
   ```

2. **Click "Start Global Extraction"** button on the homepage
   - This will trigger live RSS ingestion
   - Wait 30-60 seconds for articles to be fetched
   - Articles will be displayed after ingestion completes

3. **Check the backend terminal logs** to see:
   ```
   🔴 LIVE INGESTION STARTED
   📡 Fetching articles from RSS feeds...
   ✅ Fetched XX articles from RSS
   💾 Storing XXX chunks in vector database...
   ✅ LIVE INGESTION COMPLETE
   ```

---

### Option 2: Use the Test Script (Direct Backend Testing)

1. **Make sure backend is running** on http://localhost:8000

2. **Run the test script**
   ```bash
   python test_live_ingestion.py
   ```

3. **Follow the prompts**
   - Script will check backend health
   - Will clear old articles
   - Will trigger live ingestion
   - Will show you the new articles

4. **Check the results**
   - Script will display the first 5 articles with dates
   - Verify dates are recent (2026)

---

### Option 3: Manual API Call (Advanced)

1. **Clear old articles first** (optional but recommended)
   ```bash
   curl -X DELETE http://localhost:8000/articles/clear
   ```

2. **Trigger live ingestion**
   ```bash
   curl -X POST http://localhost:8000/ingest/live
   ```

3. **Check the articles**
   ```bash
   curl http://localhost:8000/articles
   ```

---

## Why Are You Seeing Old Articles?

The backend loads with 794 chunks that were previously ingested (from fallback dataset). These are OLD articles.

When you:
1. Open http://localhost:3000
2. The frontend calls `/articles` endpoint
3. Backend returns what's ALREADY in the database (old articles)

You need to **trigger the "Start Global Extraction"** button to:
1. Fetch NEW articles from RSS feeds
2. Process and store them
3. Then they'll appear in the frontend

---

## Verification Steps

After ingestion, verify you have live articles:

1. **Check article dates**
   - Should be 2026-06 (current month)
   - NOT 2026-03 (which are fallback articles)

2. **Check backend logs**
   - Look for "LIVE INGESTION COMPLETE"
   - Should show "Articles: XX" where XX > 0

3. **Check the database**
   ```bash
   curl http://localhost:8000/health
   ```
   - Look at `points_count` - should increase after ingestion

---

## Troubleshooting

### If no articles are fetched:
1. **RSS feeds might be blocked** - Check if you can access:
   ```
   https://economictimes.indiatimes.com/rssfeeds/1221656.cms
   ```
   in your browser

2. **Network issues** - The backend fetches from live RSS, needs internet

3. **Check backend logs** for errors:
   ```
   ❌ LIVE INGESTION FAILED
   ```

### If ingestion is slow:
- Normal! Fetching 20 articles per category takes time
- Backend scrapes full article text with newspaper3k
- Be patient, wait for "✅ LIVE INGESTION COMPLETE"

---

## Quick Test Right Now

Run this to test immediately:

```bash
# In a new terminal (make sure backend is running)
python test_live_ingestion.py
```

Then open http://localhost:3000 and you should see NEW articles!

---

## Expected Backend Output

When ingestion works correctly, you'll see:

```
======================================================================
🔴 LIVE INGESTION STARTED
======================================================================
📡 Fetching articles from RSS feeds...
   Fetching category [Top Stories]: https://economictimes...
   → Scraping: Article Title Here...
   ✅ Scraped 18 articles from feed
📊 Total unique articles scraped: 156

✅ Fetched 156 articles from RSS
   Sample article: Latest Economic News from June 2026...
   Date: 2026-06-29

🛠️  Preprocessing articles...
✂️  Chunking articles...
💾 Storing 520 chunks in vector database...

======================================================================
✅ LIVE INGESTION COMPLETE
   Articles: 156
   Chunks: 520
======================================================================
```

If you see this, SUCCESS! Your articles are now live and current.
