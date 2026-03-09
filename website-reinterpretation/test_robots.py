#!/usr/bin/env python3
"""
Test robots.txt and User-Agent functionality
"""

import asyncio
import aiohttp
from website_proxy import WebsiteProxy, USER_AGENT


async def test_robots():
    """Test robots.txt checking."""
    proxy = WebsiteProxy()
    
    print("=" * 70)
    print("ROBOTS.TXT AND USER-AGENT TEST")
    print("=" * 70)
    print(f"\nUser-Agent: {USER_AGENT}\n")
    
    test_urls = [
        "https://en.wikipedia.org/wiki/Main_Page",
        "https://en.wikipedia.org/wiki/Special:Random",
        "https://example.com/",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            print(f"\nTesting: {url}")
            try:
                allowed = await proxy.robots_parser.check_robots(url, session)
                print(f"  ✓ Allowed by robots.txt: {allowed}")
                
                # Try fetching
                content = await proxy.fetch_website(url, check_robots=True)
                print(f"  ✓ Successfully fetched ({len(content)} bytes)")
            except ValueError as e:
                print(f"  ✗ Blocked: {e}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    # Show robots.txt info
    print("\n" + "=" * 70)
    print("ROBOTS.TXT CACHE")
    print("=" * 70)
    for domain, paths in proxy.robots_parser.disallowed_paths.items():
        print(f"\n{domain}:")
        print(f"  Disallowed paths: {list(paths)[:10]}")
        if domain in proxy.robots_parser.crawl_delays:
            print(f"  Crawl delay: {proxy.robots_parser.crawl_delays[domain]}s")


if __name__ == "__main__":
    asyncio.run(test_robots())
