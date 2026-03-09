"""
Website Proxy: Regular browser proxy that serves websites normally.
Acts as a simple HTTP proxy without transformation.
Respects robots.txt and uses proper User-Agent per Wikimedia policy.
"""

import sys
import os
import ssl
import re
import json
import hashlib
import asyncio
import aiohttp
import pickle
from pathlib import Path
from typing import Dict, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Import existing grainrad/advanced theme components
try:
    from blackwall.worktrees.mcp_integration.advanced_theme import (
        AdvancedTheme,
        AdvancedThemeTransformer,
        DitheringEngine,
        ASCIIConverter,
        ShaderEngine,
        AdBlocker
    )
    ADVANCED_THEME_AVAILABLE = True
except ImportError:
    ADVANCED_THEME_AVAILABLE = False
    AdvancedTheme = None
    AdvancedThemeTransformer = None

# User-Agent following Wikimedia Foundation User-Agent Policy
# Format: <client name>/<version> (<contact information>) <library/framework name>/<version>
# For bot-like behavior (robots.txt compliance)
BOT_USER_AGENT = "WebsiteProxy/1.0 (https://github.com/abhinavallam/cequence-blackwall; abhinav@example.org) aiohttp/3.9.0"

# Real browser User-Agent for humanistic access
BROWSER_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Try to import Playwright for JavaScript rendering
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class RobotsTxtParser:
    """Simple robots.txt parser."""
    
    def __init__(self):
        self.disallowed_paths: Dict[str, Set[str]] = {}  # domain -> set of disallowed paths
        self.crawl_delays: Dict[str, float] = {}  # domain -> delay in seconds
        self.cache: Dict[str, bool] = {}  # url -> is_allowed
    
    async def fetch_robots_txt(self, base_url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch robots.txt for a domain."""
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    return await response.text()
        except Exception:
            pass
        return None
    
    def parse_robots_txt(self, robots_content: str, user_agent: str = "*") -> Tuple[Set[str], float]:
        """
        Parse robots.txt content.
        
        Returns:
            Tuple of (disallowed_paths, crawl_delay)
        """
        disallowed = set()
        delay = 0.0
        current_agent = None
        in_our_section = False
        
        for line in robots_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # User-agent directive
            if line.lower().startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
                if agent == '*' or 'bot' in user_agent.lower() or user_agent.lower() in agent.lower():
                    in_our_section = True
                    current_agent = agent
                else:
                    in_our_section = False
            
            # Disallow directive
            elif line.lower().startswith('disallow:') and in_our_section:
                path = line.split(':', 1)[1].strip()
                if path:
                    disallowed.add(path)
            
            # Crawl-delay directive
            elif line.lower().startswith('crawl-delay:') and in_our_section:
                try:
                    delay = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
        
        return disallowed, delay
    
    def is_allowed(self, url: str, disallowed_paths: Set[str]) -> bool:
        """Check if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        path = parsed.path
        
        for disallowed in disallowed_paths:
            if path.startswith(disallowed):
                return False
        return True
    
    async def check_robots(self, url: str, session: aiohttp.ClientSession) -> bool:
        """Check if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check cache
        if url in self.cache:
            return self.cache[url]
        
        # Fetch robots.txt if not cached
        if domain not in self.disallowed_paths:
            robots_content = await self.fetch_robots_txt(url, session)
            if robots_content:
                disallowed, delay = self.parse_robots_txt(robots_content, BOT_USER_AGENT)
                self.disallowed_paths[domain] = disallowed
                if delay > 0:
                    self.crawl_delays[domain] = delay
            else:
                # No robots.txt or error - allow by default
                self.disallowed_paths[domain] = set()
        
        # Check if allowed
        allowed = self.is_allowed(url, self.disallowed_paths.get(domain, set()))
        self.cache[url] = allowed
        return allowed


class PersistentCache:
    """Persistent file-based cache with expiration."""
    
    def __init__(self, cache_dir: Path = None, default_ttl: int = 86400 * 7):  # 7 days default
        """
        Initialize persistent cache.
        
        Args:
            cache_dir: Directory for cache files (default: ./cache)
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent / "cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        self.default_ttl = default_ttl
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata: Dict[str, dict] = self._load_metadata()
        
        # In-memory cache for hot items
        self.memory_cache: Dict[str, bytes] = {}
        self.memory_cache_max_size = 100  # Keep 100 items in memory
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
        }
    
    def _load_metadata(self) -> Dict[str, dict]:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception:
            pass
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache entry."""
        # Use first 2 chars for directory structure
        subdir = self.cache_dir / cache_key[:2]
        subdir.mkdir(exist_ok=True)
        return subdir / cache_key
    
    def get(self, url: str) -> Optional[bytes]:
        """
        Get cached content.
        
        Args:
            url: URL to retrieve
            
        Returns:
            Cached content or None if not found/expired
        """
        cache_key = self._get_cache_key(url)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            self.stats["hits"] += 1
            return self.memory_cache[cache_key]
        
        # Check metadata
        if cache_key not in self.metadata:
            self.stats["misses"] += 1
            return None
        
        entry = self.metadata[cache_key]
        
        # Check expiration
        expires_at = datetime.fromisoformat(entry["expires_at"])
        if datetime.now() > expires_at:
            # Expired, remove it
            self._remove(cache_key)
            self.stats["misses"] += 1
            return None
        
        # Load from disk
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                content = cache_path.read_bytes()
                
                # Add to memory cache if space available
                if len(self.memory_cache) < self.memory_cache_max_size:
                    self.memory_cache[cache_key] = content
                
                self.stats["hits"] += 1
                return content
            except Exception:
                self._remove(cache_key)
                self.stats["misses"] += 1
                return None
        
        self.stats["misses"] += 1
        return None
    
    def set(self, url: str, content: bytes, ttl: Optional[int] = None):
        """
        Cache content.
        
        Args:
            url: URL being cached
            content: Content to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._get_cache_key(url)
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # Save metadata
        self.metadata[cache_key] = {
            "url": url,
            "expires_at": expires_at.isoformat(),
            "size": len(content),
            "cached_at": datetime.now().isoformat(),
        }
        
        # Save to disk
        cache_path = self._get_cache_path(cache_key)
        try:
            cache_path.write_bytes(content)
            
            # Add to memory cache if space available
            if len(self.memory_cache) < self.memory_cache_max_size:
                self.memory_cache[cache_key] = content
            else:
                # Evict oldest (simple FIFO)
                if self.memory_cache:
                    oldest_key = next(iter(self.memory_cache))
                    del self.memory_cache[oldest_key]
                    self.stats["evictions"] += 1
                self.memory_cache[cache_key] = content
            
            self.stats["sets"] += 1
            self._save_metadata()
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def _remove(self, cache_key: str):
        """Remove cache entry."""
        if cache_key in self.metadata:
            del self.metadata[cache_key]
        
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                cache_path.unlink()
            except Exception:
                pass
        
        self._save_metadata()
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = []
        
        for cache_key, entry in self.metadata.items():
            expires_at = datetime.fromisoformat(entry["expires_at"])
            if now > expires_at:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove(cache_key)
        
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "total_entries": len(self.metadata),
            "memory_entries": len(self.memory_cache),
        }


class WebsiteProxy:
    """Simple website proxy that serves websites normally."""
    
    def __init__(self, use_browser: bool = True, cache_dir: Path = None, cache_ttl: int = 86400 * 7,
                 enable_effects: bool = False, effect_preset: str = "grainrad"):
        """
        Initialize website proxy.
        
        Args:
            use_browser: Use browser (Playwright) for JavaScript-heavy sites
            cache_dir: Directory for persistent cache
            cache_ttl: Cache time-to-live in seconds (default: 7 days)
            enable_effects: Enable grainrad-style effects (dithering, ASCII, shaders)
            effect_preset: Effect preset name ("grainrad", "retro", "none")
        """
        # Create SSL context that doesn't verify certificates
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Robots.txt parser
        self.robots_parser = RobotsTxtParser()
        
        # Persistent cache
        self.cache = PersistentCache(cache_dir=cache_dir, default_ttl=cache_ttl)
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, float] = {}  # domain -> retry_after timestamp
        
        # Browser instance (Playwright)
        self.use_browser = use_browser and PLAYWRIGHT_AVAILABLE
        self.browser: Optional[Browser] = None
        self.playwright = None
        
        # Cookie jar for session management
        self.cookies: Dict[str, list] = {}  # domain -> list of cookies
        
        # Grainrad-style effects (use existing advanced_theme.py)
        self.enable_effects = enable_effects and ADVANCED_THEME_AVAILABLE
        self.effect_preset = effect_preset
        self.theme_transformer = None
        
        if self.enable_effects:
            self._init_effects()
        
        # Cleanup expired cache entries on startup
        expired_count = self.cache.cleanup_expired()
        if expired_count > 0:
            print(f"Cleaned up {expired_count} expired cache entries")
    
    def _init_effects(self):
        """Initialize grainrad-style effects using existing advanced_theme.py."""
        if not ADVANCED_THEME_AVAILABLE or AdvancedTheme is None:
            print("Warning: Advanced theme not available, effects disabled")
            self.enable_effects = False
            return
        
        # Create grainrad-style theme
        theme = AdvancedTheme(
            name="grainrad-proxy",
            dithering={
                "method": "floyd_steinberg",
                "intensity": 0.7
            },
            ascii_config={
                "width": 80,
                "extended": True,
                "contrast": 1.2
            },
            shader_config={
                "noise": 0.15,
                "grain": 0.08,
                "scanlines": True,
                "crt_effect": True
            },
            ad_blocking={
                "patterns": [
                    "advertisement",
                    "ad-banner",
                    "sponsor",
                    "promo",
                    "adsbygoogle"
                ],
                "enabled": True
            },
            graphics_mode="hybrid",  # ASCII + Dither + Shader
            metadata={
                "inspiration": "grainrad.com",
                "aesthetic": "retro-terminal"
            }
        )
        
        self.theme_transformer = AdvancedThemeTransformer(theme)
    
    async def _init_browser(self):
        """Initialize Playwright browser if available."""
        if self.use_browser and not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
    
    async def _close_browser(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def _fetch_with_browser(self, url: str) -> bytes:
        """Fetch website using Playwright browser (for JavaScript-heavy sites)."""
        await self._init_browser()
        
        context = await self.browser.new_context(
            user_agent=BROWSER_USER_AGENT,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Los_Angeles',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
        )
        
        # Restore cookies for this domain
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain in self.cookies:
            await context.add_cookies(self.cookies[domain])
        
        page = await context.new_page()
        
        try:
            # Navigate and wait for network to be idle
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit for any remaining JavaScript
            await asyncio.sleep(1)
            
            # Get final HTML after JavaScript execution
            html = await page.content()
            
            # Save cookies
            cookies = await context.cookies()
            self.cookies[domain] = cookies
            
            await context.close()
            
            return html.encode('utf-8')
        except Exception as e:
            await context.close()
            raise
    
    async def fetch_website(self, url: str, use_cache: bool = True, check_robots: bool = True, force_browser: Optional[bool] = None) -> bytes:
        """
        Fetch website content normally.
        
        Args:
            url: Website URL
            use_cache: Use cached content if available
            check_robots: Check robots.txt before fetching (only for bot mode)
            force_browser: Force browser mode (True) or HTTP mode (False), None = auto
            
        Returns:
            Raw HTML content as bytes
            
        Raises:
            ValueError: If robots.txt disallows the URL
            aiohttp.ClientResponseError: On HTTP errors
        """
        # Check cache first (heavily rely on caching)
        if use_cache:
            cached_content = self.cache.get(url)
            if cached_content is not None:
                return cached_content
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check rate limits
        if domain in self.rate_limits:
            retry_after = self.rate_limits[domain]
            if retry_after > asyncio.get_event_loop().time():
                wait_time = retry_after - asyncio.get_event_loop().time()
                raise ValueError(f"Rate limited. Retry after {wait_time:.1f} seconds")
        
        # Determine fetch method
        use_browser_mode = force_browser if force_browser is not None else self.use_browser
        
        # Try browser mode first if enabled
        if use_browser_mode:
            try:
                content = await self._fetch_with_browser(url)
                # Cache with long TTL (7 days default)
                self.cache.set(url, content)
                return content
            except Exception as browser_error:
                # Fall back to HTTP if browser fails
                print(f"Browser fetch failed, falling back to HTTP: {browser_error}")
        
        # HTTP fetch with browser-like headers
        # Note: aiohttp handles gzip/deflate automatically, but we need Brotli support
        headers = {
            "User-Agent": BROWSER_USER_AGENT,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        # Try to import Brotli for br encoding support
        try:
            import brotli
            BROTLI_AVAILABLE = True
        except ImportError:
            BROTLI_AVAILABLE = False
            # Remove br from Accept-Encoding if Brotli not available
            headers["Accept-Encoding"] = "gzip, deflate"
        
        # Add cookies if available
        cookie_header = None
        if domain in self.cookies:
            cookie_parts = [f"{c['name']}={c['value']}" for c in self.cookies[domain]]
            if cookie_parts:
                cookie_header = "; ".join(cookie_parts)
                headers["Cookie"] = cookie_header
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=self.ssl_context),
            headers=headers,
            cookie_jar=aiohttp.CookieJar()
        ) as session:
            # Check robots.txt (only in bot mode, skip for browser mode)
            if check_robots and not use_browser_mode:
                allowed = await self.robots_parser.check_robots(url, session)
                if not allowed:
                    raise ValueError(f"URL disallowed by robots.txt: {url}")
                
                # Apply crawl delay if specified
                if domain in self.robots_parser.crawl_delays:
                    delay = self.robots_parser.crawl_delays[domain]
                    await asyncio.sleep(delay)
            
            async with session.get(url, allow_redirects=True, max_redirects=10) as response:
                # Handle rate limiting (429)
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            delay_seconds = float(retry_after)
                            self.rate_limits[domain] = asyncio.get_event_loop().time() + delay_seconds
                        except ValueError:
                            pass
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=429,
                        message="Too Many Requests"
                    )
                
                # Raise for other errors
                response.raise_for_status()
                
                # Handle Brotli decompression if needed
                content_encoding = response.headers.get('Content-Encoding', '').lower()
                content = await response.read()
                
                if content_encoding == 'br' and BROTLI_AVAILABLE:
                    try:
                        import brotli
                        content = brotli.decompress(content)
                    except Exception as e:
                        # If decompression fails, try to continue with compressed content
                        print(f"Brotli decompression warning: {e}")
                elif content_encoding == 'br' and not BROTLI_AVAILABLE:
                    # If server sent br but we can't decode it, try without br in Accept-Encoding
                    raise ValueError("Server sent Brotli-compressed content but Brotli library not installed. Install with: pip install brotli")
                
                # Save cookies from response
                cookies = []
                for cookie in session.cookie_jar:
                    cookies.append({
                        'name': cookie.key,
                        'value': cookie.value,
                        'domain': cookie.get('domain', domain),
                        'path': cookie.get('path', '/'),
                    })
                if cookies:
                    self.cookies[domain] = cookies
                
                # Cache result with long TTL (heavily rely on caching)
                self.cache.set(url, content)
                
                return content
    
    def _apply_effects(self, html_content: bytes) -> bytes:
        """
        Apply combined grainrad-style effects to HTML content.
        
        Args:
            html_content: Original HTML content
            
        Returns:
            Transformed HTML content
        """
        if not self.enable_effects:
            return html_content
        
        try:
            # Import combined effects processor
            try:
                # Try relative import first (same directory)
                import sys
                from pathlib import Path
                combined_effects_path = Path(__file__).parent / "combined_effects.py"
                if combined_effects_path.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("combined_effects", combined_effects_path)
                    combined_effects_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(combined_effects_module)
                    CombinedEffectsProcessor = combined_effects_module.CombinedEffectsProcessor
                else:
                    raise ImportError("combined_effects.py not found")
            except Exception as e:
                # Fallback to basic effects
                print(f"Combined effects import failed: {e}, using basic effects")
                if not self.theme_transformer:
                    return html_content
                return self._apply_basic_effects(html_content)
            
            # Convert bytes to string
            html_str = html_content.decode('utf-8', errors='ignore')
            
            # Create combined effects processor with selected effects
            # Default: combine dithering, ascii, scanlines, grain, halftone, vhs
            combined_effects = CombinedEffectsProcessor(
                effects=["dithering", "ascii", "scanlines", "grain", "halftone", "vhs", "dots", "matrix_rain"]
            )
            
            # Process HTML with combined effects
            html_str = combined_effects.process_html(html_str)
            
            # Apply ad blocking if enabled
            if self.theme_transformer and self.theme_transformer.theme.ad_blocking.get('enabled'):
                ad_blocker = self.theme_transformer.ad_blocker
                html_str = ad_blocker.remove_ads_from_html(html_str)
            
            # Convert back to bytes
            return html_str.encode('utf-8')
        
        except Exception as e:
            # If effects fail, return original
            print(f"Effect application error: {e}")
            import traceback
            traceback.print_exc()
            return html_content
    
    def _apply_basic_effects(self, html_content: bytes) -> bytes:
        """Fallback to basic effects if combined effects not available."""
        if not self.theme_transformer:
            return html_content
        
        try:
            html_str = html_content.decode('utf-8', errors='ignore')
            
            # Get shader CSS from theme transformer
            shader_engine = self.theme_transformer.shader_engine
            shader_css = shader_engine.generate_shader_css(self.theme_transformer.theme)
            
            # Inject CSS into HTML head
            if '<head>' in html_str:
                html_str = html_str.replace('<head>', f'<head>\n<style>\n{shader_css}\n</style>')
            elif '<html>' in html_str:
                html_str = html_str.replace('<html>', f'<html>\n<head>\n<style>\n{shader_css}\n</style>\n</head>')
            else:
                html_str = f'<head><style>{shader_css}</style></head>{html_str}'
            
            # Apply ad blocking
            if self.theme_transformer.theme.ad_blocking.get('enabled'):
                ad_blocker = self.theme_transformer.ad_blocker
                html_str = ad_blocker.remove_ads_from_html(html_str)
            
            return html_str.encode('utf-8')
        except Exception as e:
            print(f"Basic effect error: {e}")
            return html_content
    
    async def proxy_request(self, url: str, request: Request) -> Response:
        """
        Proxy a request to the target URL.
        
        Args:
            url: Target URL
            request: Original FastAPI request
            
        Returns:
            Response with proxied content
        """
        try:
            # Fetch content (skip robots.txt check in browser mode for humanistic access)
            content = await self.fetch_website(url, check_robots=False)
            
            # Apply grainrad-style effects if enabled
            if self.enable_effects:
                content = self._apply_effects(content)
            
            # Determine content type
            content_type = request.headers.get("Accept", "text/html")
            if "text/html" in content_type or not content_type:
                content_type = "text/html; charset=utf-8"
            
            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600"
                }
            )
        except ValueError as e:
            # Robots.txt or rate limit error
            return Response(
                content=f"<h1>Access Denied</h1><p>{str(e)}</p>",
                status_code=403,
                media_type="text/html"
            )
        except aiohttp.ClientResponseError as e:
            # HTTP error
            status_code = e.status
            return Response(
                content=f"<h1>Error {status_code}</h1><p>{e.message}</p>",
                status_code=status_code,
                media_type="text/html"
            )
        except Exception as e:
            return Response(
                content=f"<h1>Error</h1><p>{str(e)}</p>",
                status_code=500,
                media_type="text/html"
            )


def create_proxy_app(use_browser: bool = True, cache_dir: Path = None, cache_ttl: int = 86400 * 7,
                     enable_effects: bool = False, effect_preset: str = "grainrad") -> FastAPI:
    """
    Create FastAPI app for regular browser proxy.
    
    Args:
        use_browser: Use browser (Playwright) for JavaScript-heavy sites
        cache_dir: Directory for persistent cache
        cache_ttl: Cache time-to-live in seconds (default: 7 days)
        enable_effects: Enable grainrad-style effects
        effect_preset: Effect preset name
    
    Returns:
        FastAPI app
    """
    proxy = WebsiteProxy(use_browser=use_browser, cache_dir=cache_dir, cache_ttl=cache_ttl,
                        enable_effects=enable_effects, effect_preset=effect_preset)
    
    app = FastAPI(title="Website Proxy")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/proxy/{url:path}")
    async def proxy_website(url: str, request: Request):
        """Proxy endpoint for serving websites normally."""
        # Reconstruct full URL
        if not url.startswith("http://") and not url.startswith("https://"):
            full_url = f"https://{url}"
        else:
            full_url = url
        
        return await proxy.proxy_request(full_url, request)
    
    @app.get("/api/fetch")
    async def fetch_website(request: Request):
        """API endpoint for fetching websites."""
        url = request.query_params.get("url")
        
        if not url:
            return {"error": "URL parameter required"}
        
        try:
            content = await proxy.fetch_website(url, check_robots=False)
            return Response(
                content=content,
                media_type="text/html; charset=utf-8"
            )
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @app.get("/api/cache/stats")
    async def cache_stats():
        """Get cache statistics."""
        return proxy.cache.get_stats()
    
    @app.post("/api/cache/clear")
    async def clear_cache():
        """Clear cache."""
        # Clear metadata and memory cache
        proxy.cache.metadata = {}
        proxy.cache.memory_cache = {}
        proxy.cache._save_metadata()
        
        # Optionally delete cache files
        import shutil
        if proxy.cache.cache_dir.exists():
            for item in proxy.cache.cache_dir.iterdir():
                if item.is_dir() and item.name != "cache_metadata.json":
                    shutil.rmtree(item)
        
        return {"success": True, "message": "Cache cleared"}
    
    @app.post("/api/cache/cleanup")
    async def cleanup_cache():
        """Clean up expired cache entries."""
        expired_count = proxy.cache.cleanup_expired()
        return {
            "success": True,
            "expired_removed": expired_count,
            "stats": proxy.cache.get_stats()
        }
    
    return app


def create_website_proxy(use_browser: bool = True, cache_dir: Path = None, cache_ttl: int = 86400 * 7) -> WebsiteProxy:
    """Create website proxy instance."""
    return WebsiteProxy(use_browser=use_browser, cache_dir=cache_dir, cache_ttl=cache_ttl)
