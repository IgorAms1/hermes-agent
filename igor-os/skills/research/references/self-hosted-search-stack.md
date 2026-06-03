# Self-Hosted Search Stack (VPS, May 2026)

## Whoogle-search (port 8080)

Self-hosted Google search proxy — no tracking, no ads, anonymous.

- **URL**: `http://localhost:8080`
- **JSON API**: `http://localhost:8080/search?q=<query>&format=json`
- **Installed**: `pip install whoogle-search cachetools`
- **Run**: `whoogle-search --port 8080`
- **Missing deps workaround**: fresh pip install of whoogle-search may miss `cachetools` — install it explicitly

### Usage from agent

```python
from hermes_tools import terminal
result = terminal("curl -s 'http://localhost:8080/search?q=agent+skills&format=json'")
```

Crawl4AI can also scrape Whoogle results for richer extraction.

## Crawl4AI (v0.8.6)

Full-content web extractor with JS rendering via Playwright/Chromium.

- **Installed**: `pip install crawl4ai` + `python3 -m playwright install chromium`
- **System deps** (needed by Chromium, no sudo without them):
  `libnspr4-dev libnss3-dev libnss3-tools libcairo2-dev libpango1.0-dev libatk1.0-dev libatk-bridge2.0-dev libatspi2.0-dev libx11-dev libxcb1-dev libxext-dev libxfixes-dev libxrandr-dev libxdamage-dev libxcomposite-dev libgbm-dev libcups2-dev libasound2-dev`

### Usage from agent

```python
from hermes_tools import execute_code
code = """
import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl():
    async with AsyncWebCrawler(verbose=False) as c:
        r = await c.arun(url='https://example.com', bypass_cache=True)
        return f"OK: {len(r.markdown)} chars"
print(asyncio.run(crawl()))
"""
terminal(f"python3 << 'PYEOF'\n{code}\nPYEOF")
```

Supports: JS-rendered pages, GitHub, docs, blog posts, search results.
Does NOT require API keys.

## Security note

When setting up system-level tools that need sudo (libs, Docker, etc.), the user may offer their sudo password via Telegram. **Never accept credentials through the chat.** Instead, generate a one-liner command they can copy-paste into their terminal directly:

```
sudo apt-get install -y -qq libnspr4-dev libnss3-dev ...
```

This avoids exposing secrets while still getting the job done.