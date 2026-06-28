Analyze the# ET News — Frontend Workflow (Page-by-Page) + Backend Contracts

This document describes how the current frontend UI flows “page by page” (screens in `frontend/app/page.tsx`), which backend endpoints it calls, and how the Remotion video player consumes the backend video payload. It is written to help you improve the UI in Figma using the real data + state transitions already implemented.

---

## 1) Tech Stack in This Project

- Frontend: `Next.js` (single main entry file) + `Remotion Player` for the video preview.
- Backend: `FastAPI` that orchestrates:
  - Director storyboard (LLM)
  - Voice generation (TTS with word timing)
  - Scene timeline mapping (word timestamps → frames)
  - Visual (B-roll) retrieval (Pexels)

---

## 2) Frontend Architecture (Where the workflow lives)

### Main entry / screen router
- File: `frontend/app/page.tsx`
- Routing model: one React component uses `screen` state to switch between:
  - `"welcome"`
  - `"persona"`
  - `"home"`
  - `"article"`
  - `"video_studio"`

### API client
- File: `frontend/lib/api.ts`
- Centralizes calls to backend endpoints:
  - `GET /personas`
  - `GET /articles`
  - `POST /ingest/fallback`
  - `POST /analyze`
  - `POST /video/generate`

### Video prefetch (reduces scene-change stalls)
- File: `frontend/lib/videoPrefetch.ts`
- Uses Remotion `prefetch()` to preload:
  - MP3 audio URL
  - each scene’s `broll_url`

### Remotion compositions (video rendering)
- File: `frontend/app/video-studio/compositions/NewsVideo.tsx`
- File: `frontend/app/video-studio/compositions/AnimatedCaptions.tsx`
- File: `frontend/app/video-studio/compositions/LowerThird.tsx`

---

## 3) Screens (Frontend Workflow Page-by-Page)

### Screen 1: Welcome (`screen === "welcome"`)
- File section: `WelcomeScreen`
- Backend calls: none
- Primary CTA:
  - “Begin Discovery” button → `setScreen("persona")`

**Figma notes**
- This screen is purely onboarding/branding; the improvement opportunities here are mostly visual.

---

### Screen 2: Persona Selection (`screen === "persona"`)
- File section: `PersonaScreen`
- Backend calls:
  - none in the current UI; personas come from a local `DEMO_PERSONAS` constant (static).

Actions:
- Clicking a persona runs:
  - `handleSelectPersona(p)` → sets `selectedPersona = p` and transitions to `"home"`

---

### Screen 3: Home / Article Grid (`screen === "home"`)
- File section: `HomeScreen`
- Backend calls:
  1. When entering `"home"`, `useEffect` triggers `loadArticles()`.
  2. `loadArticles(category?: string)` calls `GET /articles?category=...`

UI behavior:
- Category chips update `activeCategory`
- A `useEffect([activeCategory])` triggers `onRefresh(activeCategory)` which calls `loadArticles(activeCategory)`
- Buttons:
  - “Load Data” → calls `handleIngest()` → `POST /ingest/fallback` → then reloads articles.

Actions:
- Clicking an article card:
  - `setSelectedArticle(article)`
  - `setScreen("article")`
  - analysis runs automatically (see Screen 4)

---

### Screen 4: Article Detail + AI Agents (`screen === "article"`)
- File section: `ArticleScreen`
- Backend calls:
  1. Immediately when entering the screen: `handleSelectArticle()` auto-runs analysis:
     - `POST /analyze`
     - Request:
       - `query = article.title`
       - `user_profile = { user_id, persona, level, portfolio, interests }`

UI states:
- `isLoadingAnalysis` shows “Agents are synthesizing insights…”
- When `analysis` returns successfully:
  - render headline, summary
  - show “Bull Agent” / “Bear Agent” blocks reading:
    - `analysis.ui_metadata.bull`
    - `analysis.ui_metadata.bear`

Primary CTA:
- “Create Briefing”
  - calls `onGenerateVideo(article, analysis)`
  - transitions to `"video_studio"` (see Screen 5)

---

### Screen 5: Video Studio (`screen === "video_studio"`)
- File section: `VideoStudioScreen`
- Backend calls (triggered by “Create Briefing”):
  1. `POST /video/generate` via `generateVideo()`:
     - Request includes:
       - `article_title`
       - `summary`
       - `bull_view`
       - `bear_view`
  2. After the JSON response arrives, frontend also fetches the VTT file body:
     - `fetch(`${API_BASE}${payload.subtitles_url}`)` → `subtitles_text`
  3. Then frontend preloads assets:
     - `prefetchVideoJobAssets(data, API_BASE)`

Player mounting:
- Uses Remotion `<Player>` with:
  - `durationInFrames={videoJob.total_frames ?? 1800}`
  - `fps={30}`
  - `component={NewsVideo}`
  - `inputProps` contains:
    - `script={videoJob.script}`
    - `audio_url=http://localhost:8000${videoJob.audio_url}`
    - `subtitles_url=http://localhost:8000${videoJob.subtitles_url}`
    - `subtitles_text={videoJob.subtitles_text}`
    - `caption_words={videoJob.caption_words ?? []}`
    - `article_title=...`

Loading/empty states:
- While generating:
  - shows overlay “Synthesizing Video Briefing…”
- If `videoJob` is null:
  - shows “Studio Ready” placeholder.

---

## 4) Remotion Video Rendering (How the “script” becomes visuals + audio + captions)

### Composition: `NewsVideo`
- File: `frontend/app/video-studio/compositions/NewsVideo.tsx`

Inputs (`NewsVideoProps`):
- `script`: `VideoScene[]`
- `audio_url`: URL to MP3
- `subtitles_url`: URL to VTT
- `subtitles_text`: fetched VTT body text (client-side)
- `caption_words`: server-generated word timing frames
- `article_title`: fallback text in case there is no B-roll for a scene

Rendering logic:
1. **Per-scene sequences**
   - For each `scene` in `script`:
     - `<Sequence from={scene.start_frame} durationInFrames={scene.end_frame - scene.start_frame}>`
     - Inside the sequence:
       - If `scene.broll_url` exists:
         - `<Video src={scene.broll_url} loop ... />`
       - Else:
         - placeholder gradient background + `article_title`
       - Always:
         - `<LowerThird text={scene.overlay_text} sentiment=... />`

2. **Global overlays**
   - `<AnimatedCaptions ... />`
     - drives captions by matching `useCurrentFrame()` to server `caption_words` timings
     - uses segment grouping so text is readable

3. **Audio**
   - `<Audio src={audio_url} />`

---

### Captions: `AnimatedCaptions`
- File: `frontend/app/video-studio/compositions/AnimatedCaptions.tsx`

Caption data sources (priority order):
1. `captionWords` prop (`videoJob.caption_words`)
2. If missing, parse `subtitlesText` into word timings
3. (Optional fallback) fetch VTT when props are missing

Caption readability improvement:
- It groups word tokens into **caption segments** so the visible line doesn’t change every single frame.
- It highlights only the currently active word inside the segment.

Font:
- Uses Roboto via CSS variable set in `frontend/app/layout.tsx` (YouTube-like UI feel).

---

### Lower third overlay: `LowerThird`
- File: `frontend/app/video-studio/compositions/LowerThird.tsx`
- Animated UI:
  - slides in from left on early frames of the sequence
  - fades near the end of that sequence’s duration

---

## 5) Backend Endpoints Used by the Frontend

All listed endpoints are defined in `backend/main.py`.

### A) Personas
- `GET /personas`
- Used by: frontend helper `fetchPersonas()` (current UI may not always call it since personas are static in the demo flow).
- Returns:
  - `{ personas: UserProfile[] }`

---

### B) Articles
- `GET /articles?category=...`
- Used by: frontend `fetchArticles(category)`
- Returns:
  - list of `Article`-shaped objects (title/date/summary/tags/image_url/url depending on vector store state)
- If vector store is empty:
  - returns the static demo feed.

---

### C) Ingest fallback data
- `POST /ingest/fallback`
- Used by: frontend “Load Data”
- Returns:
  - `IngestResponse`:
    - `status`, `articles_scraped`, `chunks_stored`, `errors[]`

---

### D) Analysis (Bull/Bear + UI metadata)
- `POST /analyze`
- Used by: frontend when opening an article detail screen
- Request (`AnalysisRequest`):
  - `query: string`
  - `user_profile: UserProfile`
  - optional `article_url`
- Response (`AnalysisResponse`):
  - `headline`, `summary`
  - `ui_metadata` containing:
    - `bull`, `bear`, and optional `disclaimer`
  - plus `sources[]`, `confidence`, etc.

---

### E) Video Generation (Scenes + Audio + Captions)
- `POST /video/generate`
- Used by: frontend when user clicks “Create Briefing”
- Request (`VideoRequest`):
  - `article_title`, `summary`, `bull_view`, `bear_view`
- Response (`VideoResponse`):
  - `job_id`
  - `script`: `Scene[]` where each scene includes:
    - `scene_id`, `narration`, `search_keyword`, `overlay_text`, `composition`
    - `broll_url` (optional)
    - `start_frame`, `end_frame`
  - `audio_url`
  - `subtitles_url`
  - `total_frames`
  - `caption_words[]` where each item:
    - `text`, `start_frame`, `end_frame`

Backend internal orchestration (high-level):
1. DirectorAgent creates `scenes` JSON with strict narration length target
2. VoiceEngine produces:
   - MP3 narration
   - WEBVTT with word timing (or fallback synthetic timing)
3. Subtitle parsing + audio duration determine:
   - `total_frames`
   - scene start/end frames
4. Caption words are converted to `caption_words` for Remotion.
5. VisualEngine fetches Pexels B-roll per scene keyword.

---

## 6) Data Contract Summary (Quick Copy for Figma)

### Video Studio payload into Remotion
- `VideoResponse.total_frames` → Remotion `<Player durationInFrames />`
- `VideoResponse.script[]` → Remotion `<Sequence from start_frame durationInFrames />`
- `VideoResponse.audio_url` → Remotion `<Audio />`
- `VideoResponse.caption_words[]` → Remotion `<AnimatedCaptions />`
- `VideoResponse.subtitles_url` / `subtitles_text` → fallback caption parsing

---

## 7) Suggested Figma UX Improvement Targets (Based on Current Workflow)

These are “where to look” for UI improvements tied to current code behavior:

1. Loading states:
   - Screen 4 analysis spinner and Screen 5 video generation overlay should expose progress and estimated time.
2. Category browsing:
   - “All vs category” chips refetch immediately; consider debounced UX or explicit Apply button.
3. Video preview:
   - Add a “Scene list” / timeline scrubber side panel using `script[].start_frame/end_frame`.
4. Captions:
   - Use a caption style panel (font size, subtitle bar position, highlight intensity) since captions are already segment-grouped for readability.

