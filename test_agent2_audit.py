#!/usr/bin/env python3

# Simple test of Agent-2 audit approach
import sys
import json
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_http():
    """Test basic HTTP fetching."""
    try:
        import urllib.request

        url = "https://weareswarm.online"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        print(f"Fetching {url}...")
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            print(f"✅ Fetched {len(content)} characters")
            print(f"Title: {content.split('<title>')[1].split('</title>')[0] if '<title>' in content else 'No title'}")
            return True

    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        return False

def test_regex_parsing():
    """Test HTML parsing with regex."""
    html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
    <h1>Main Heading</h1>
    <img src="test.jpg" alt="Test image">
    <a href="/internal">Internal Link</a>
    <a href="https://external.com">External Link</a>
    </body>
    </html>
    """

    # Test title extraction
    import re
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ""
    print(f"Title: '{title}'")

    # Test headings
    h1_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
    print(f"H1 headings: {h1_matches}")

    # Test images
    img_matches = re.findall(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
    alt_matches = re.findall(r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*>', html, re.IGNORECASE)
    print(f"Images: {len(img_matches)}, Alts: {len([a for a in alt_matches if a.strip()])}")

    return True

if __name__ == "__main__":
    print("🧪 Testing Agent-2 audit components...")

    print("\n1. Testing HTTP fetching:")
    test_basic_http()

    print("\n2. Testing regex parsing:")
    test_regex_parsing()

    print("\n✅ Basic tests complete!")