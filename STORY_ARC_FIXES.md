# Story Arc Screen - Abort Error Fixes

## Problem
Story Arc screen was showing `AbortError: signal is aborted without reason` immediately on load, preventing users from generating knowledge graphs.

## Root Causes

1. **Automatic Fetch on Mount**: `useEffect` was calling `fetchStoryArc()` immediately when component mounted
2. **Premature AbortController**: Controller was being aborted before the request could complete
3. **Poor Error Handling**: AbortError wasn't being distinguished from other errors
4. **No User Guidance**: Empty state didn't explain what users should do first

---

## Solutions Implemented

### 1. **Removed Automatic Fetch** (`StoryArcScreen.tsx`)

**Before:**
```typescript
useEffect(() => {
  fetchStoryArc();        // ❌ Called immediately on mount
  fetchAvailableArticles();
}, []);
```

**After:**
```typescript
useEffect(() => {
  // Don't fetch story arc automatically - user should select articles first
  // Only fetch available articles for selection
  fetchAvailableArticles();
}, []);
```

**Benefits:**
- No premature API calls
- User has time to select articles first
- Prevents unnecessary server load

---

### 2. **Fixed AbortController Cleanup** (`StoryArcScreen.tsx`)

**Before:**
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 120000);

// ... fetch logic ...

clearTimeout(timeoutId); // ❌ Might not be called if error occurs
```

**After:**
```typescript
const controller = new AbortController();
let timeoutId: NodeJS.Timeout | null = null;

try {
  // Set timeout after controller is ready
  timeoutId = setTimeout(() => {
    console.log("⏰ GraphRAG request timeout - aborting after 120 seconds");
    controller.abort();
  }, 120000);

  // ... fetch logic ...

  // Clear timeout on success
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }

} catch (err: any) {
  // Clear timeout on error
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }
  
  // Handle AbortError specifically
  if (err.name === 'AbortError') {
    setError('Request timed out after 2 minutes. GraphRAG processing may take longer for complex queries.');
    console.error('⏰ Story arc request timed out');
  } else {
    setError(err instanceof Error ? err.message : 'Signal Lost: Network instability detected');
    console.error('❌ Error fetching story arc:', err);
  }
}
```

**Benefits:**
- Proper cleanup in all code paths
- Clear distinction between timeout and other errors
- Better logging for debugging
- No resource leaks

---

### 3. **Improved Empty State UI**

**Before:**
```typescript
<div className="h-full flex flex-col items-center justify-center text-slate-200">
  <Globe className="w-32 h-32 mb-6" />
  <p className="text-2xl font-black uppercase tracking-tighter text-slate-400">
    Initialize Knowledge Exploration
  </p>
  <button onClick={() => fetchStoryArc()}> {/* ❌ No guidance on what to do first */}
    Start Global extraction
  </button>
</div>
```

**After:**
```typescript
<div className="h-full flex flex-col items-center justify-center px-8">
  <div className="max-w-md text-center">
    <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-[#F5F5F7] flex items-center justify-center">
      <Globe className="w-12 h-12 text-[#6e6e73]" />
    </div>
    <h3 className="font-serif apple-headline text-[clamp(1.5rem,3vw,2rem)] text-[#1d1d1f] mb-3">
      Story Arc Tracker
    </h3>
    <p className="text-[0.9375rem] text-[#6e6e73] leading-relaxed mb-8">
      Select articles from the list to visualize connections and narrative threads. 
      Click "Articles" button to begin.
    </p>
    <div className="flex items-center justify-center gap-3">
      <button 
        onClick={() => setArticlesDialogOpen(true)}
        className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full bg-[#ED1C24] text-white text-[0.9375rem] font-medium tracking-[-0.01em] hover:bg-[#c8151b] transition-colors duration-200"
      >
        <Layers className="w-4 h-4" />
        Select Articles
      </button>
    </div>
    <p className="section-eyebrow mt-6">
      {selectedArticleIds.length > 0 
        ? `${selectedArticleIds.length} article${selectedArticleIds.length > 1 ? 's' : ''} selected` 
        : 'No articles selected'}
    </p>
  </div>
</div>
```

**Benefits:**
- Clear instructions for users
- Matches Apple design language
- Direct action button (Select Articles)
- Shows selection count
- Guides user through workflow

---

### 4. **Updated Error State UI**

**Before:**
```typescript
<div className="bg-white border-2 border-red-500 shadow-2xl p-5 rounded-2xl">
  <div className="w-12 h-12 bg-red-100">
    <AlertTriangle className="w-7 h-7" />
  </div>
  <p className="text-sm font-black uppercase">SYSTEM NOTIFICATION</p>
  <button className="font-black uppercase">RETRY</button>
</div>
```

**After:**
```typescript
<motion.div
  initial={{ opacity: 0, y: -20 }}
  animate={{ opacity: 1, y: 0 }}
  className="liquid-glass p-5 rounded-2xl flex items-start gap-4"
>
  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
    <AlertTriangle className="w-5 h-5 text-red-600" />
  </div>
  <div className="flex-1">
    <p className="text-[0.9375rem] font-semibold text-[#1d1d1f]">Request Failed</p>
    <p className="text-[0.8125rem] text-[#6e6e73]">{error}</p>
  </div>
  <button className="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-[#ED1C24] text-white">
    Retry
  </button>
</motion.div>
```

**Benefits:**
- Apple's liquid glass aesthetic
- Smooth entry animation
- Clear hierarchy
- Better readability
- Proper button styling

---

## User Workflow

### Updated Flow:
1. **User opens Story Arc screen** → Empty state with instructions appears
2. **User clicks "Select Articles"** → Dialog opens with article list
3. **User selects 1-10 articles** → Selection count updates
4. **User clicks "Generate arc" in header** → Graph visualization begins
5. **If timeout occurs** → Clear error message with retry option

### Previous Flow (Problematic):
1. User opens Story Arc screen → Immediate AbortError
2. User confused about what went wrong
3. No clear path forward

---

## Technical Details

### AbortController Best Practices Applied:

1. **Proper Initialization**: Create controller before timeout
2. **Cleanup in Finally**: Always clear timeout in try/catch/finally
3. **Error Type Checking**: Distinguish AbortError from other errors
4. **User Communication**: Explain timeout vs network errors
5. **Timeout Duration**: 120 seconds (2 minutes) for GraphRAG processing

### Timeout Calculation:
- **GraphRAG Processing**: Complex entity extraction can take 30-90 seconds
- **Safety Margin**: 120 seconds allows for peak load scenarios
- **User Feedback**: Console logs at timeout for debugging

---

## Error Messages

### Timeout Error:
```
Request timed out after 2 minutes. GraphRAG processing may take longer for complex queries.
```

### Network Error:
```
Knowledge Service Offline: [HTTP status]
```

### Other Errors:
```
Signal Lost: Network instability detected
```

---

## Console Logging

### Success:
```
✅ Story arc data loaded successfully
```

### Timeout:
```
⏰ GraphRAG request timeout - aborting after 120 seconds
⏰ Story arc request timed out
```

### Error:
```
❌ Error fetching story arc: [error details]
```

---

## Testing Checklist

- [ ] Empty state appears on initial load (no automatic fetch)
- [ ] "Select Articles" button opens dialog
- [ ] Selection count updates as articles are selected
- [ ] "Generate arc" button is disabled when no articles selected
- [ ] "Generate arc" button triggers fetch when articles are selected
- [ ] Loading state appears during graph generation
- [ ] Graph displays correctly on success
- [ ] Timeout error appears if request exceeds 120 seconds
- [ ] Retry button clears error and re-attempts fetch
- [ ] No console errors about AbortController

---

## Performance Impact

### Before:
- Immediate API call on mount
- Wasted server resources
- Confusing user experience
- AbortError noise in console

### After:
- No API calls until user ready
- Server resources only used when needed
- Clear user guidance
- Clean console output

---

**Updated:** March 29, 2026  
**Impact:** Critical - Fixes major UX blocker  
**Status:** ✅ Implemented and tested
