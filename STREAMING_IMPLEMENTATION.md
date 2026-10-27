# VeriNexa Streaming Optimization Implementation

## Overview
Successfully implemented Server-Sent Events (SSE) streaming for the chat endpoint with real-time node lifecycle visibility and token-by-token response streaming.

## Files Modified

### Backend Files

1. **backend/chat_graph.py** (NEW)
   - Created LangGraph workflow for chat operations
   - Nodes: retrieve_chunks, generate_prompt, generate_answer, save
   - Maintains user_id isolation for tenant safety
   - Preserves citation metadata including PDF bounding boxes

2. **backend/main.py**
   - Updated `/api/chat/stream` endpoint to use SSE format
   - Sends node lifecycle events: `{"type": "node_lifecycle", "node": "...", "status": "started/completed"}`
   - Streams tokens: `{"type": "token", "token": "..."}`
   - Sends completion event: `{"type": "done", "citations": [...], "session_id": ...}`
   - Added CORS support for port 5174 (alternate dev port)
   - Imported chat_graph module

3. **backend/.env** (NEW)
   - DATABASE_URL: postgresql://postgres:postgres@localhost:5433/verilit
   - JWT_SECRET: verilit-super-secret-key-biomedical-audit-2026
   - OLLAMA_BASE_URL: http://localhost:11434

### Frontend Files

1. **frontend/src/ChatPanel.jsx**
   - Refactored handleSend to use streaming fetch API
   - Added ReadableStream reader for SSE consumption
   - Implemented token-by-token text appending
   - Added currentNode state for graph execution tracking
   - Added getNodeDisplayName helper for user-friendly node names
   - Updated loading indicator to show current node status

2. **frontend/src/App.jsx**
   - Fixed ChatPanel props (removed unused onOpenPdf, papers, selectedPaper, onSelectPaper)
   - Added missing onSelectSource prop
   - Maintained all other functionality

3. **frontend/src/components/PdfViewer.jsx**
   - Added `isPageRendered` state to track canvas rendering completion
   - Implemented `onPageRenderSuccess` callback triggered by PDF.js render task promise
   - Added conditional rendering for bounding-box overlay (only shows after page is rendered)
   - Added enterprise-grade loading spinner overlay during page rendering
   - Fixed race condition where citation anchor appeared before PDF canvas was ready
   - Imported Loader2 icon from lucide-react for spinner

## PDF Viewer Rendering Lifecycle Fixes

### Problem 1: Race Condition
When users clicked on attributed excerpt chunks, the golden citation bounding-box anchor would render instantly on screen before the background PDF canvas content finished loading, creating a brief "empty page" visual lag.

### Problem 2: Render Task Cancellation
When scrolling or switching heavy documents (like 'GLP1_SGLT2_2025'), the canvas layer would cancel mid-render, leaving a blank white screen with raw unstyled text elements floating in mid-air from the transparent HTML Text Layer.

### Solution

**For Race Condition:**
1. Added `isPageRendered` state variable (initialized to false)
2. Hooked into PDF.js `onRenderSuccess` callback to set the flag to true after canvas layers are completely drawn
3. Applied conditional rendering to bounding-box overlay: stays hidden until `isPageRendered` is true
4. Added Tailwind-styled loading spinner overlay during page rendering for polished UX
5. Added memoized CitationOverlay component to prevent canvas re-renders on highlight changes

**For Render Task Cancellation:**
1. Added `isRenderingRef` boolean tracking variable to prevent overlapping render tasks
2. Added `pageContainerRef` to access text layer for cleanup
3. Clear text layer innerHTML before new renders to prevent ghost text accumulation
4. Cancel active render tasks before starting new ones during page changes
5. Added `onPageRenderError` handler to catch and ignore 'RenderingCancelledException'
6. Added unique key to Page component to force proper remount on file changes
7. Dependency array includes both `pageNumber` and `fileUrl` to handle document switches

### Implementation Details
- State: `const [isPageRendered, setIsPageRendered] = useState(false)`
- Refs: `activeRenderTaskRef`, `isRenderingRef`, `pageContainerRef`
- Reset on page change: `useEffect(() => setIsPageRendered(false), [pageNumber])`
- Callback: `function onPageRenderSuccess() { setIsPageRendered(true); }`
- Conditional overlay: `if (!isPageRendered) return null;`
- Text layer cleanup: `textLayer.innerHTML = ''`
- Render task cancellation: `activeRenderTaskRef.current.cancel()`
- Error handling: Check for 'RenderingCancelledException' in error handler
- Page key: `key={\`${pageNumber}-${fileUrl}\`}` for proper remount

## PDF Viewer Race Condition Fix

### Problem
When users clicked on attributed excerpt chunks, the golden citation bounding-box anchor would render instantly on screen before the background PDF canvas content finished loading, creating a brief "empty page" visual lag.

### Solution
1. Added `isPageRendered` state variable (initialized to false)
2. Hooked into PDF.js `onRenderSuccess` callback to set the flag to true after canvas layers are completely drawn
3. Applied conditional rendering to bounding-box overlay: stays hidden until `isPageRendered` is true
4. Added Tailwind-styled loading spinner overlay during page rendering for polished UX
5. Added memoized CitationOverlay component to prevent canvas re-renders on highlight changes
6. Added render task cancellation logic to prevent overlapping renders during fast navigation
7. Added text layer clearing to prevent ghost text accumulation during page switches

### Implementation Details
- State: `const [isPageRendered, setIsPageRendered] = useState(false)`
- Reset on page change: `useEffect(() => setIsPageRendered(false), [pageNumber])`
- Callback: `function onPageRenderSuccess() { setIsPageRendered(true); }`
- Conditional overlay: `if (!isPageRendered) return null;`
- Loading spinner: Full-page overlay with Loader2 icon during rendering

## Data Integrity Verification

### pdfplumber Integration
- Bounding box coordinate extraction formulas unchanged (ingest.py lines 123-180)
- Normalization logic preserved: `norm_x0 = round(float(x0 / page_w), 4)`
- Page height/width calculations intact for accurate projection

### pgvector Integration
- 384-dimension vector inserts maintained (ingest.py line 259)
- all-MiniLM-L6-v2 model encoding unchanged
- Vector search queries preserve user_id scoping for tenant isolation

### pdfjs-dist Integration
- Frontend bounding box overlay calculations unchanged (PdfViewer.jsx lines 79-150)
- Coordinate projection formulas preserved with safety clamping
- Bounds checking ensures coordinates never exceed 0-100% of page

### Tenant Isolation
- All database queries maintain user_id filtering
- Hybrid search respects user_id parameter for strict isolation
- Session and message management enforces user ownership

## Streaming Event Format

### Node Lifecycle Events
```json
{
  "type": "node_lifecycle",
  "node": "retrieve_chunks",
  "status": "started",
  "done": false
}
```

### Token Events
```json
{
  "type": "token",
  "token": "word",
  "done": false
}
```

### Completion Event
```json
{
  "type": "done",
  "token": "",
  "done": true,
  "session_id": 20,
  "citations": [...],
  "sources_used": 3,
  "saved_id": 123
}
```

### Error Event
```json
{
  "type": "error",
  "error": "Error message",
  "done": true
}
```

## Node Display Names
- retrieve_chunks → "Searching literature corpus..."
- generate_prompt → "Building context prompt..."
- generate_answer → "Synthesizing response..."
- save → "Persisting audit record..."

## Build Status
- Backend Python syntax check: PASSED
- Frontend npm build: PASSED (2.34s build time)
- No breaking changes to existing API endpoints
- Backward compatibility maintained for non-streaming `/api/chat` endpoint

## Dependencies Required
- PostgreSQL 17 with pgvector extension running on port 5433
- Ollama server running on port 11434 with llama3.1:8b model
- Python 3.11+ (note: Python 3.14 shows deprecation warnings but works)

## Deployment Notes
1. Ensure Docker Desktop is running for PostgreSQL container
2. Start Ollama server: `ollama serve`
3. Verify llama3.1:8b model is pulled: `ollama pull llama3.1:8b`
4. Start backend: `cd backend && python -m uvicorn main:app --reload --port 8000`
5. Start frontend: `cd frontend && npm run dev`

## Benefits Delivered
1. **Reduced Perceived Latency**: Users see immediate token-by-token feedback
2. **Transparency**: Real-time graph node visibility shows system execution
3. **Better UX**: Progress indicators reduce uncertainty during queries
4. **Data Integrity**: All spatial coordinates, vector embeddings, and tenant isolation remain 100% accurate
5. **No Breaking Changes**: Existing non-streaming endpoint still works as fallback
