# Website Proxy Browser

Simple HTTP proxy that serves websites normally, like a regular browser. Uses browser automation (Playwright) for JavaScript-heavy sites and **heavily relies on persistent caching**.

## Features

- ✅ **Aggressive Persistent Caching** - File-based cache with 7-day default TTL
- ✅ **Multi-level Caching** - Memory cache (hot items) + disk cache (persistent)
- ✅ **Cache Statistics** - Track hits, misses, hit rate
- ✅ Regular browser proxy (no transformation)
- ✅ **Browser automation** - Uses Playwright for JavaScript-heavy sites
- ✅ **Real browser headers** - Mimics real Chrome browser
- ✅ **Cookie management** - Maintains sessions across requests
- ✅ **JavaScript execution** - Renders dynamic content
- ✅ SSL certificate handling (bypasses verification)
- ✅ **Proper User-Agent** following Wikimedia Foundation User-Agent Policy
- ✅ **Robots.txt support** - respects robots.txt directives (optional in browser mode)
- ✅ **Rate limiting** - respects 429 status codes and Retry-After headers
- ✅ **Gzip compression** - requests content with Accept-Encoding: gzip
- ✅ Clean browser-like interface
- ✅ URL bar with navigation
- ✅ Back/Forward/Reload buttons
- ✅ History tracking

## Installation

### 1. Install Dependencies

```bash
cd website-reinterpretation
pip install -r requirements.txt
```

### 2. Install Browser Support (Optional but Recommended)

For JavaScript-heavy websites, install Playwright and browser binaries:

```bash
./install_browser.sh
```

Or manually:
```bash
pip install playwright
python3 -m playwright install chromium
```

### 3. Run Proxy Server

```bash
# With browser support and aggressive caching (default)
python3 run_proxy.py

# Custom cache TTL (in seconds)
CACHE_TTL=86400 python3 run_proxy.py  # 1 day

# Custom cache directory
CACHE_DIR=/tmp/my_cache python3 run_proxy.py

# Without browser (HTTP only)
USE_BROWSER=false python3 run_proxy.py
```

Server runs on `http://localhost:8001`

### 4. Open Browser

Open `http://localhost:8001` in your browser

## Caching System

The proxy **heavily relies on caching** with a multi-level approach:

### Cache Levels

1. **Memory Cache** (Hot Items)
   - Keeps 100 most recently accessed items in memory
   - Instant access for frequently requested URLs
   - Automatically evicts oldest items when full

2. **Disk Cache** (Persistent)
   - File-based storage in `./cache/` directory
   - Organized by hash prefixes for efficient lookup
   - Survives server restarts
   - Default TTL: 7 days (configurable)

### Cache Features

- **Persistent Storage**: Cache survives server restarts
- **Automatic Expiration**: Expired entries are cleaned up automatically
- **Statistics Tracking**: Monitor hit rate, misses, evictions
- **Efficient Lookup**: Hash-based key system with directory structure
- **Memory Optimization**: Hot items in memory, rest on disk

### Cache Statistics

Check cache performance:

```bash
curl http://localhost:8001/api/cache/stats
```

Response:
```json
{
  "hits": 150,
  "misses": 25,
  "sets": 25,
  "evictions": 5,
  "hit_rate": 0.857,
  "total_entries": 20,
  "memory_entries": 20
}
```

### Cache Management

```bash
# View cache statistics
curl http://localhost:8001/api/cache/stats

# Clean up expired entries
curl -X POST http://localhost:8001/api/cache/cleanup

# Clear all cache
curl -X POST http://localhost:8001/api/cache/clear
```

## Usage

### Via Web Interface

1. Open `http://localhost:8001`
2. Enter URL in the address bar (e.g., `example.com` or `https://example.com`)
3. Click "Go" or press Enter
4. Website loads normally in the iframe
5. **Subsequent requests are served from cache** (much faster!)

### Via API

```bash
# Fetch website content (cached if available)
curl "http://localhost:8001/api/fetch?url=https://example.com"

# Proxy endpoint (for iframes)
curl "http://localhost:8001/proxy/https://example.com"
```

## How It Works

### Caching Flow

1. **Request comes in** → Check memory cache first
2. **Memory miss** → Check disk cache
3. **Disk hit** → Load into memory cache, return content
4. **Disk miss** → Fetch from website
5. **Fetch success** → Save to both memory and disk cache
6. **Return content** → Serve to client

### Browser Mode (Default)

For JavaScript-heavy websites, the proxy uses Playwright:
1. Checks cache first (heavily relies on caching)
2. If cache miss, launches headless Chromium browser
3. Sets realistic browser headers and viewport
4. Executes JavaScript and waits for page load
5. Captures final HTML after JavaScript execution
6. **Caches result** with 7-day TTL
7. Maintains cookies for session management

### HTTP Mode (Fallback)

For simple websites or when browser is unavailable:
1. Checks cache first (heavily relies on caching)
2. Uses aiohttp with browser-like headers
3. Handles redirects automatically
4. Manages cookies via cookie jar
5. **Caches result** with 7-day TTL
6. Falls back if browser mode fails

## API Endpoints

- `GET /` - Browser interface
- `GET /proxy/{url}` - Proxy website (for iframe embedding)
- `GET /api/fetch?url={url}` - Fetch website content
- `GET /api/cache/stats` - Get cache statistics
- `POST /api/cache/cleanup` - Clean up expired cache entries
- `POST /api/cache/clear` - Clear all cache

## Configuration

### Environment Variables

- `USE_BROWSER` - Enable browser mode (default: `true`)
- `CACHE_TTL` - Cache time-to-live in seconds (default: `604800` = 7 days)
- `CACHE_DIR` - Custom cache directory path

### Cache TTL Examples

```bash
# 1 hour cache
CACHE_TTL=3600 python3 run_proxy.py

# 1 day cache
CACHE_TTL=86400 python3 run_proxy.py

# 30 days cache
CACHE_TTL=2592000 python3 run_proxy.py

# 1 year cache (very aggressive)
CACHE_TTL=31536000 python3 run_proxy.py
```

## User-Agent Policy Compliance

The proxy uses proper User-Agent headers:

**Bot Mode** (for robots.txt compliance):
```
WebsiteProxy/1.0 (https://github.com/abhinavallam/notes-blackwall; abhinav@example.org) aiohttp/3.9.0
```

**Browser Mode** (for humanistic access):
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

## Robots.txt Support

The proxy automatically:
- Fetches and parses robots.txt files (in HTTP mode)
- Respects Disallow directives
- Applies Crawl-delay directives
- Caches robots.txt per domain
- **Note**: Browser mode skips robots.txt for humanistic access

## Rate Limiting

The proxy respects:
- HTTP 429 (Too Many Requests) status codes
- Retry-After headers
- Domain-specific rate limits
- **Caching reduces need for repeated requests**

## Performance Benefits

With aggressive caching:

- **Faster Response Times**: Cached requests are instant
- **Reduced Bandwidth**: Only fetch once per TTL period
- **Lower Server Load**: Fewer requests to target websites
- **Better Reliability**: Cached content available even if website is down
- **Cost Savings**: Fewer API calls and bandwidth usage

## Notes

- SSL certificate verification is disabled for compatibility
- **Websites are cached aggressively** (7 days default)
- Content is served as-is without any transformation
- Works like a regular browser proxy
- Browser mode provides humanistic access to JavaScript-heavy sites
- Automatically falls back to HTTP mode if browser fails
- Cache survives server restarts
- Expired cache entries are cleaned up automatically

## Troubleshooting

### Cache Directory Issues

If cache directory has permission issues:
```bash
mkdir -p cache
chmod 755 cache
```

### Cache Size Management

Monitor cache size:
```bash
du -sh cache/
```

Clean up old cache:
```bash
curl -X POST http://localhost:8001/api/cache/cleanup
```

### Playwright Not Available

If you see "Playwright available: False":
```bash
pip install playwright
python3 -m playwright install chromium
```

### Websites Not Loading

1. Check if browser mode is enabled: `USE_BROWSER=true python3 run_proxy.py`
2. Check logs: `tail -f /tmp/website-proxy.log`
3. Try HTTP mode: `USE_BROWSER=false python3 run_proxy.py`
4. Check cache stats: `curl http://localhost:8001/api/cache/stats`
