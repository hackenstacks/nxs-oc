# nxs-oc — NeXuS OpenCharacters

> OpenCharacters, integrated into the NeXuS Bifrost gateway. No API keys in the browser. No cloud accounts. Fully self-hosted, streaming AI characters through your own proxy.

**Author:** hackenstacks@protonmail.com  
**Base:** [OpenCharacters](https://github.com/josephrocca/OpenCharacters) by josephrocca  
**Status:** ✅ Operational — streaming confirmed  
**Principles:** Sane · Simple · Secure · Stealthy · Beautiful  

---

## What This Is

This is OpenCharacters wired into the [NeXuS Bifrost Bridge](https://github.com/hackenstacks/nexus-bifrost-bridge) proxy. The OC source is unmodified — the integration lives entirely server-side in Bifrost, injected at serve time.

**What Bifrost adds:**
- Intercepts all `fetch()` calls to `api.openai.com` and rewrites them to your local proxy
- Injects API keys server-side — the browser never sees a key
- Routes to Pollinations (free, keyless) by default — works with zero configuration
- Filters Pollinations SSE preamble chunks that would crash OC's streaming handler
- Seeds IndexedDB with NeXuS proxy endpoints so OC's key gate passes automatically

```
You type a message in OC
    ↓
OC: fetch('https://api.openai.com/v1/chat/completions', {stream: true, ...})
    ↓  [Bifrost fetch interceptor — injected into <head> at serve time]
fetch('https://localhost:8443/api/llm/pollinations/v1/chat/completions')
    ↓  [Bifrost proxy: key injected, preamble filtered, HTTP/1.1 chunked SSE]
OC: streaming reply renders in the chat window ✅
```

---

## Requirements

- [nexus-bifrost-bridge](https://github.com/hackenstacks/nexus-bifrost-bridge) running on `https://localhost:8443`
- Python 3.11+
- No API keys required (Pollinations is free and keyless by default)

---

## Setup

### 1. Set up Bifrost first

```bash
git clone https://github.com/hackenstacks/nexus-bifrost-bridge.git
cd nexus-bifrost-bridge
python3 server/nexus_web_server.py --root web --port 8443
```

Accept the self-signed cert in your browser once.

### 2. Drop nxs-oc into Bifrost's web root

```bash
git clone https://github.com/hackenstacks/nxs-oc.git
cp -r nxs-oc/ ~/NeXuS/bifrost-bridge/web/oc/
```

### 3. Open

```
https://localhost:8443/oc/index.html
```

No API key prompts. No configuration. Start chatting.

---

## First Run — Clear the Browser Database

If you previously used OpenCharacters in this browser, the IndexedDB may be at a higher schema version than `index.html` expects. Clear it once:

```javascript
// F12 → Console on https://localhost:8443/oc/index.html
indexedDB.deleteDatabase('chatbot-ui-v1').onsuccess = () => location.reload()
```

This is a one-time step. After this, OC loads cleanly every time.

---

## Supported AI Providers

Through Bifrost, nxs-oc can reach any configured provider. Default is Pollinations (no key needed).

| Provider | Key needed | How to enable |
|---|---|---|
| Pollinations | ❌ Free | Default — works immediately |
| Groq | ✅ | `GROQ_API_KEY=...` in `~/NeXuS/secrets/nexus.env` |
| Mistral | ✅ | `MISTRAL_API_KEY=...` |
| OpenRouter | ✅ | `OPENROUTER_API_KEY=...` — unlocks 200+ models |
| DeepSeek | ✅ | `DEEPSEEK_API_KEY=...` |
| Ollama | ❌ Local | Requires Ollama running on `:11434` |
| NeXuS Router | ❌ Local | Requires nexus-ai-router running on `:8810` |

All keys live in `~/NeXuS/secrets/nexus.env` — never in the browser, never in code.

---

## How the Integration Works

Bifrost injects this script into every HTML file served from `/oc/`:

```javascript
(function(){
  var BASE = window.location.origin;

  // 1. Fetch interceptor — rewrites AI provider URLs to local proxy
  var MAP = {
    "api.openai.com":  BASE+"/api/llm/pollinations",
    "api.mistral.ai":  BASE+"/api/llm/mistral",
    "api.groq.com":    BASE+"/api/llm/groq",
    "openrouter.ai":   BASE+"/api/llm/openrouter",
    "aihorde.net":     BASE+"/api/llm/aihorde",
  };
  var _f = window.fetch.bind(window);
  window.fetch = async function(url, opts) {
    if (typeof url === "string") {
      for (var host in MAP) {
        if (url.indexOf(host) !== -1) {
          url = MAP[host] + url.replace(/^https?:\/\/[^\/]+/, "");
          delete (opts.headers||{})["Authorization"];
          break;
        }
      }
      // Belt-and-suspenders: fix double /v1/v1/ from stale IndexedDB
      url = url.replace(/(\/api\/llm\/[^\/]+)\/v1\/v1\//, "$1/v1/");
    }
    return _f(url, opts);
  };

  // 2. Seed IndexedDB — dummy key + proxy endpoints so OC's gate passes
  setTimeout(function seedDB() { /* ... writes nexus-proxy config ... */ }, 1500);
})();
```

Bifrost also filters Pollinations' `choices:[]` SSE preamble chunks before they reach the browser — OC's `handleStreamingResponse` crashes on empty `choices` arrays without this filter.

---

## OC-Fix Log

Eight bugs were discovered and fixed during integration on 2026-10-14. Full technical details in [NEXUS_INTEGRATION.md](./NEXUS_INTEGRATION.md).

| # | Bug | Impact |
|---|---|---|
| 01 | Inject not applied to registry-served HTML | No proxy — calls went direct to OpenAI |
| 02 | Double `/v1/v1/` from stale IndexedDB | `unknown API route` error |
| 03 | `api.openai.com` routed to openai (no key) | Error JSON instead of SSE stream |
| 04 | `/v1` in fetch interceptor MAP values | Double-v1 from interceptor path |
| 05 | HTTP/1.0 — `response.body` null | `getReader()` unavailable |
| 06 | HTTP/1.1 keep-alive hung static responses | All links broken after HTTP/1.1 change |
| 07 | Raw 301 redirect missing `Content-Length: 0` | `/oc` showed "Blocked" in Firefox |
| 08 | Pollinations `choices:[]` preamble chunk | `TypeError` crash in `handleStreamingResponse` |

---

## Upstream

This repo tracks [josephrocca/OpenCharacters](https://github.com/josephrocca/OpenCharacters).  
The original upstream README is preserved at [OC_UPSTREAM_README.md](./OC_UPSTREAM_README.md).

To pull upstream OC updates:

```bash
git remote add upstream https://github.com/josephrocca/OpenCharacters.git
git fetch upstream
git merge upstream/main
# resolve any conflicts (unlikely — we don't modify OC source)
```

---

## File Structure

```
nxs-oc/
├── index.html              ← main OC interface (unmodified upstream)
├── play.html               ← OC play interface (unmodified upstream)
├── utils.js                ← OC utilities
├── plugins/                ← OC plugin system
├── docs/                   ← upstream OC documentation
├── README.md               ← this file (NeXuS integration guide)
├── NEXUS_INTEGRATION.md    ← full OC-Fix technical log
├── OC_UPSTREAM_README.md   ← original OC README preserved
├── CUSTOM_ENDPOINTS.md     ← upstream OC custom endpoints guide
└── .gitignore
```

---

## License

OpenCharacters is MIT licensed — see [LICENSE](./LICENSE).  
NeXuS integration and documentation: hackenstacks@protonmail.com  
*Together Everyone Achieves More — Sane · Simple · Secure · Stealthy · Beautiful*
