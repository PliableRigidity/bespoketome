# JARVIS Image & Web Retrieval Enhancement

## What Changed

### A) Robust Web Retrieval Fix ✅
- **Updated `web_retrieval/search_client.py`**:
  - Added retry logic with exponential backoff (max 3 retries)
  - Implemented proper logging for debugging
  - Standardized output schema: `[{"title": str, "url": str, "snippet": str}]`
  - Added URL deduplication
  - Graceful error handling (returns `[]` on failure, never crashes)

- **Updated `tool_web.py`**:
  - Changed return type from `str` to `dict` with structure:
    ```python
    {
        "answer": str,
        "sources": [{"id": int, "title": str, "url": str}],
        "debug": dict  # optional
    }
    ```

### B) Image Retrieval Tool ✅
- **Created `tool_image.py`**:
  - `image_search(query)`: Fetches images from DuckDuckGo
  - `should_fetch_images(user_text)`: Heuristic to auto-trigger image search
  - Returns standardized schema:
    ```python
    [{
        "title": str,
        "image_url": str,
        "thumbnail_url": str,
        "source_url": str,
        "width": int | None,
        "height": int | None
    }]
    ```

- **Updated `web_retrieval/search_client.py`**:
  - Added `execute_image_search()` with retry logic
  - Deduplicates by image_url
  - Filters invalid entries

### C) Tool Wiring + Response Schema ✅
- **Updated `dispatcher.py`**:
  - Now returns structured dict:
    ```python
    {
        "text": str,
        "images": list,
        "sources": list
    }
    ```
  - Integrated `image_search` tool
  - Added heuristic-based image fetching for queries like "who is X", "show me X"

- **Updated `planner.py`**:
  - Added `image_search` tool definition
  - Added few-shot examples for image queries

### D) Frontend Rendering ✅
- **Updated `templates/index.html`**:
  - Modified `addMessage()` to accept `images` and `sources` parameters
  - Renders image gallery with:
    - Thumbnail preview (falls back to full image)
    - Click to open full image in new tab
    - Hover zoom effect
    - Graceful error handling (shows placeholder on broken images)
    - Caption overlay with image title
  - Renders sources list with:
    - Clickable citation links
    - Numbered references
    - Clean styling

- **Updated `web_server.py`**:
  - Modified `/api/chat` endpoint to handle structured responses
  - Ensures backward compatibility (converts string responses to dict)

### E) Developer UX / Debugging ✅
- **Added to `config.py`**:
  - `RETRIEVAL_DEBUG` flag (set via env var)
  - When enabled, includes debug info in responses

- **Logging**:
  - All retrieval functions use Python `logging` module
  - Logs include: query attempts, retry counts, errors, result counts

### F) Testing ✅
- **Created `tests/test_retrieval.py`**:
  - Tests for web search schema validation
  - Tests for image search schema validation
  - Tests for heuristic logic
  - Tests for error handling
  - All tests ensure graceful degradation

## How to Run

### 1. Install Dependencies
```bash
cd Alexa
pip install -r requirements_voice.txt
```

### 2. Start the Server
```bash
# Windows
.\run_web.bat

# Or manually
python web_server.py
```

### 3. Access the UI
Open browser to: `http://localhost:5000`

## How to Run Tests

```bash
cd Alexa
python tests/test_retrieval.py
```

Expected output:
```
============================================================
JARVIS RETRIEVAL TESTS
============================================================
[TEST] Testing execute_web_query...
✓ Returned list with 3 results
...
```

## Example Queries

### 1. Web Search with Sources
**Query**: `"what is quantum computing"`

**Expected Response**:
```json
{
  "text": "Quantum computing is a type of computation that harnesses...",
  "images": [],
  "sources": [
    {"id": 1, "title": "Quantum Computing - Wikipedia", "url": "https://..."},
    {"id": 2, "title": "What is Quantum Computing? - IBM", "url": "https://..."}
  ]
}
```

### 2. Image Search (Explicit)
**Query**: `"show me pictures of mars rover"`

**Expected Response**:
```json
{
  "text": "Here are the images I found.",
  "images": [
    {
      "title": "NASA Mars Rover",
      "image_url": "https://...",
      "thumbnail_url": "https://...",
      "source_url": "https://...",
      "width": 1200,
      "height": 800
    }
  ],
  "sources": []
}
```

### 3. Heuristic Image Fetch
**Query**: `"who is elon musk"`

**Expected Response**:
```json
{
  "text": "Elon Musk is a business magnate and entrepreneur...",
  "images": [
    {
      "title": "Elon Musk",
      "image_url": "https://...",
      ...
    }
  ],
  "sources": [
    {"id": 1, "title": "Elon Musk - Wikipedia", "url": "https://..."}
  ]
}
```

### 4. Combined Web + Images
**Query**: `"what does the eiffel tower look like"`

**Expected Response**:
```json
{
  "text": "The Eiffel Tower is a wrought-iron lattice tower...",
  "images": [
    {
      "title": "Eiffel Tower",
      "image_url": "https://...",
      ...
    }
  ],
  "sources": [
    {"id": 1, "title": "Eiffel Tower - Wikipedia", "url": "https://..."}
  ]
}
```

## Configuration

### Enable Debug Mode
Set environment variable:
```bash
# Windows
set RETRIEVAL_DEBUG=1

# Linux/Mac
export RETRIEVAL_DEBUG=1
```

Then restart the server. Debug info will be included in responses under the `debug` key.

## Error Handling

All retrieval functions are designed to **never crash**:

1. **Network failures**: Return empty list `[]`, log error
2. **Invalid responses**: Filter out bad entries, return valid ones
3. **Timeouts**: Retry with backoff, then return partial results
4. **Empty results**: Return empty list, no error

## Dependencies Added

No new dependencies required! Uses existing:
- `duckduckgo-search` (already in requirements)
- `trafilatura` (already in requirements)
- Standard library: `logging`, `time`

## Architecture

```
User Query
    ↓
planner.py (decides which tool to call)
    ↓
dispatcher.py (executes tools, aggregates results)
    ↓
    ├─→ tool_web.py → web_retrieval/pipeline.py → search_client.py
    ├─→ tool_image.py → search_client.py
    └─→ should_fetch_images() heuristic
    ↓
Structured Response: {text, images, sources}
    ↓
web_server.py (/api/chat endpoint)
    ↓
Frontend (index.html) renders images + sources
```

## Backward Compatibility

✅ All existing functionality preserved
✅ Old string responses automatically converted to new format
✅ No breaking changes to API endpoints
✅ Works on Windows and macOS

## Known Limitations

1. **Rate Limiting**: DuckDuckGo may rate-limit aggressive queries
2. **Image Quality**: Thumbnail quality varies by source
3. **Heuristic Accuracy**: May occasionally fetch images when not needed (conservative by design)

## Future Enhancements

- [ ] Add image caching
- [ ] Support for video results
- [ ] More sophisticated image selection (ML-based ranking)
- [ ] User preference for image count
- [ ] Image carousel navigation controls
