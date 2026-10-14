# NeXuS Integration — Full OC-Fix Technical Log

**Date:** 2026-10-14  
**Author:** hackenstacks@protonmail.com  
**Related:** [nexus-bifrost-bridge](https://github.com/hackenstacks/nexus-bifrost-bridge)

This document details every bug encountered and fixed while integrating OpenCharacters with the NeXuS Bifrost Bridge proxy. Preserved here so future maintainers understand why the Bifrost server code is structured the way it is.

**All fixes are in Bifrost (`nexus_web_server.py`) — zero changes to OC source.**

---

## OC-Fix-01 — Inject not applied to registry-served HTML

**Error:** OC loaded but API calls hit `api.openai.com` directly — no proxying.

**Root cause:**  
Two code paths serve HTML files in Bifrost:
- `_serve_static()` — handles direct `/oc/*` URL requests. Had `_OC_INJECT` applied.
- `_registry_static()` — handles apps registered in the app registry (`static+static`). Did NOT have `_OC_INJECT` applied.

OC is registered in the Bifrost app registry as `static+static`, so it was served through `_registry_static()`, which never injected the proxy script.

**Fix:** Added inject block to `_registry_static()`:
```python
if app["prefix"] in ("/oc", "/oc/") and ctype == "text/html":
    if "NeXuS proxy auto-config" not in html_str:
        data = html_str.replace("<head>", "<head>\n" + self._OC_INJECT, 1).encode("utf-8")
```

**Why it works:** Injection now fires regardless of which code path serves the HTML.

---

## OC-Fix-02 — Double `/v1/v1/` in URL from stale IndexedDB

**Error:** `unknown API route /api/llm/pollinations/v1/v1/chat/completions`

**Root cause:**  
The Bifrost `seedDB` function seeds `customModelConfigs` into OC's IndexedDB with an `endpointUrl`. The original seeded URL was `BASE+"/api/llm/pollinations/v1"`. OC appends `/v1/chat/completions` to `endpointUrl` when making API calls, producing:

```
BASE+"/api/llm/pollinations/v1" + "/v1/chat/completions"
= BASE+"/api/llm/pollinations/v1/v1/chat/completions"  ← double /v1
```

Additionally, `seedDB` had a guard:
```javascript
if(e.target.result && e.target.result.value) return; // skip if already set
```
This prevented overwriting stale values from previous browser sessions, so old broken URLs persisted even after fixes.

**Fix (3 layers):**

1. Removed `/v1` from seeded `endpointUrl`:
   ```javascript
   endpointUrl: BASE+"/api/llm/pollinations"  // OC appends /v1/chat/completions
   ```

2. Removed the skip guard — `seedDB` always overwrites `customModelConfigs`.

3. Runtime belt-and-suspenders fixer in the fetch interceptor:
   ```javascript
   url = url.replace(/(\/api\/llm\/[^\/]+)\/v1\/v1\//, "$1/v1/");
   ```

**Why it works:** No `/v1` in seed + always-overwrite + runtime corrector = triple redundancy. Future stale DBs are auto-corrected at fetch time.

---

## OC-Fix-03 — `api.openai.com` routed to `openai` provider (no key)

**Error:** `handleStreamingResponse` crash — OC received error JSON instead of SSE stream.

**Root cause:**  
OC hardcodes `https://api.openai.com/v1/chat/completions` for **all** streaming chat calls, regardless of which model is selected in the UI. The Bifrost fetch interceptor MAP had:
```javascript
"api.openai.com": BASE+"/api/llm/openai/v1"
```
But the `openai` provider has no API key (`openai: false` in `/api/health`). Bifrost returned a JSON error object. OC's `handleStreamingResponse` tried to parse it as an SSE stream and crashed.

**Fix:**
```javascript
// Before
"api.openai.com": BASE+"/api/llm/openai/v1"

// After
"api.openai.com": BASE+"/api/llm/pollinations"
```

**Why it works:** Pollinations is keyless and always available. All OC streaming calls now route to a working provider regardless of which model is selected in the UI.

---

## OC-Fix-04 — `/v1` in fetch interceptor MAP values causing double-v1

**Error:** Same double-v1 error, but from the interceptor path rather than IndexedDB.

**Root cause:**  
The fetch interceptor rewrites URLs by concatenating the MAP value with the original URL's path:
```javascript
url = MAP[host] + url.replace(/^https?:\/\/[^\/]+/, "");
```

For `https://api.openai.com/v1/chat/completions`:
- Path extracted: `/v1/chat/completions`
- MAP value: `BASE+"/api/llm/openai/v1"` (had `/v1` baked in)
- Result: `BASE+"/api/llm/openai/v1"` + `/v1/chat/completions` = double `/v1`

**Fix:** Removed `/v1` from all MAP values:
```javascript
var MAP = {
  "api.openai.com":  BASE+"/api/llm/pollinations",  // no /v1
  "api.mistral.ai":  BASE+"/api/llm/mistral",
  "api.groq.com":    BASE+"/api/llm/groq",
  "openrouter.ai":   BASE+"/api/llm/openrouter",
  "aihorde.net":     BASE+"/api/llm/aihorde",
};
```

**Why it works:** OC always includes `/v1/chat/completions` in its URL path. MAP values only need the provider base. Bifrost's `LLM_PATH_RE` regex uses `(?:v1/)?` making the version prefix optional:
```python
LLM_PATH_RE = re.compile(r"^/api/llm/([A-Za-z0-9_.-]+)/(?:v1/)?chat/completions/?$")
```

---

## OC-Fix-05 — HTTP/1.0 made `response.body` unavailable

**Error:** `handleStreamingResponse` crash — `response.body` was null.

**Root cause:**  
Python's `BaseHTTPRequestHandler` defaults to HTTP/1.0. The Fetch API's streaming interface:
```javascript
const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
```
requires HTTP/1.1. In HTTP/1.0, modern browsers do not expose `response.body` as a `ReadableStream`. It is null. Calling `.pipeThrough()` on null throws immediately before `handleStreamingResponse` is even entered.

**Fix:**
```python
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
```

**Why it works:** HTTP/1.1 responses expose `response.body` as a proper `ReadableStream`, enabling `getReader()` and incremental chunk reading.

---

## OC-Fix-06 — HTTP/1.1 keep-alive hung all static responses

**Error:** After adding HTTP/1.1, all Bifrost links stopped working. Browser hung indefinitely.

**Root cause:**  
HTTP/1.1 uses persistent connections by default. After a response is sent, the server keeps the connection open waiting for the next request. For this to work, each response must include either `Content-Length` (so the client knows when the response body ends) or `Transfer-Encoding: chunked`. Bifrost's static file and JSON responses were setting `Content-Length`, but some code paths were not. The browser waited for a body end signal that never came.

**Fix:** In `_send()`, force connection close for all responses that don't explicitly set streaming headers:
```python
def _send(self, code, ctype, extra=None, sec_override=None):
    extra = extra or {}
    if "Connection" not in extra and "Transfer-Encoding" not in extra:
        self.close_connection = True  # close after this response
    ...
```

Streaming LLM responses explicitly set both `Transfer-Encoding: chunked` and `Connection: keep-alive` in their `extra` dict, so they are exempt from the forced close.

**Why it works:** Non-streaming responses close the TCP connection immediately after delivery. The browser no longer waits. Streaming responses stay open until the chunked response terminates with `0\r\n\r\n`.

---

## OC-Fix-07 — Raw 301 redirect missing `Content-Length: 0`

**Error:** Navigating to `https://localhost:8443/oc` (no trailing slash) showed "Blocked" in Firefox with 0 bytes transferred.

**Root cause:**  
The 301 redirect from `/oc` → `/oc/` is generated in `_dispatch_registry()` using raw `send_response(301)`, bypassing `_send()`. It sent no `Content-Length` header and did not set `close_connection`. With HTTP/1.1, the browser waited for a response body that never arrived.

```python
# Before — missing Content-Length and close_connection
self.send_response(301)
self.send_header("Location", pfx + "/")
self.end_headers()
```

**Fix:**
```python
self.close_connection = True
self.send_response(301)
self.send_header("Location", pfx + "/")
self.send_header("Content-Length", "0")
self.end_headers()
```

**Why it works:** `Content-Length: 0` tells the browser the redirect response has no body. `close_connection = True` closes the TCP connection immediately so the browser can follow the redirect without waiting.

---

## OC-Fix-08 — Pollinations `choices:[]` preamble chunk crashed OC

**Error:** `TypeError: Cannot read properties of undefined (reading 'text')` inside `handleStreamingResponse` at the line `if(json.choices[0].text)`.

**Root cause:**  
Pollinations always sends a first SSE event as a content-filter preamble before any actual content:
```
data: {"choices":[],"created":0,"id":"","model":"","prompt_filter_results":[{"prompt_index":0,"content_filter_results":{...}}]}
```

The `choices` array is empty. OC's `handleStreamingResponse` does:
```javascript
if(json.choices[0].text) { ... }
```
Without checking if `choices[0]` exists first. `choices[0]` on an empty array is `undefined`. `undefined.text` throws `TypeError`. OC has no try-catch around this specific line, so the entire reply dies silently.

**Fix:** Bifrost's streaming proxy filters SSE lines before forwarding to the browser:
```python
if line_s.startswith("data:") and line_s != "data: [DONE]":
    try:
        d = json.loads(line_s[5:].strip())
        if isinstance(d.get("choices"), list) and len(d["choices"]) == 0:
            continue  # drop — OC crashes on empty choices array
    except Exception:
        pass
```

**Why it works:** OC never sees the preamble chunk. The first SSE event it receives always has `choices[0]` populated with at least a `role: assistant` delta. No TypeError.

---

## Summary

All 8 fixes are server-side in `nexus_web_server.py`. Zero changes to OC source code. The complete flow that now works:

```
OC: fetch('https://api.openai.com/v1/chat/completions', {stream:true, ...})
  ↓  [_OC_INJECT fetch interceptor]
     - api.openai.com → BASE+"/api/llm/pollinations"
     - path /v1/chat/completions appended → correct single /v1
     - Authorization header stripped (key injected server-side)
fetch('https://localhost:8443/api/llm/pollinations/v1/chat/completions')
  ↓  [Bifrost LLM proxy]
     - is_stream=True: HTTP/1.1, Transfer-Encoding: chunked, Connection: keep-alive
     - Filter choices:[] preamble chunks
     - Forward remaining SSE chunks
OC: response.body.pipeThrough(TextDecoderStream()).getReader()  ← works (HTTP/1.1)
OC: handleStreamingResponse(reader) → streaming reply renders ✅
```
