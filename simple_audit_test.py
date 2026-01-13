#!/usr/bin/env python3

import json
import re
import time
import urllib.request
import urllib.error

def fetch_and_analyze(url):
    """Simple fetch and analyze."""
    print(f"Fetching {url}...")

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        print(f"✅ Fetched {len(html)} characters")

        # Basic analysis
        analysis = {
            'url': url,
            'timestamp': int(time.time()),
            'content_length': len(html),
            'word_count': len(html.split())
        }

        # Title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        analysis['title'] = title_match.group(1).strip() if title_match else ""

        # Meta desc
        meta_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
        analysis['meta_desc'] = meta_match.group(1).strip() if meta_match else ""

        # Headings
        analysis['h1_count'] = len(re.findall(r'<h1[^>]*>.*?</h1>', html, re.IGNORECASE))

        # Content checks
        analysis['has_forms'] = '<form' in html.lower()
        analysis['has_buttons'] = '<button' in html.lower()

        # CTA detection
        cta_words = ['join', 'contact', 'learn', 'start', 'signup']
        analysis['has_cta'] = any(word in html.lower() for word in cta_words)

        # Images
        img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        analysis['image_count'] = len(img_tags)
        analysis['images_with_alt'] = len([img for img in img_tags if 'alt=' in img])

        # Calculate scores
        seo_score = 100
        ux_score = 100

        if not analysis['title']:
            seo_score -= 25
        if not analysis['meta_desc']:
            seo_score -= 20
        if analysis['h1_count'] == 0:
            seo_score -= 15
        if analysis['image_count'] > analysis['images_with_alt']:
            seo_score -= 10

        if not analysis['has_cta']:
            ux_score -= 20
        if not analysis['has_forms']:
            ux_score -= 10
        if analysis['word_count'] < 300:
            ux_score -= 15

        analysis['seo_score'] = max(0, seo_score)
        analysis['ux_score'] = max(0, ux_score)
        analysis['overall_score'] = (seo_score + ux_score) / 2

        return analysis

    except Exception as e:
        return {'error': str(e), 'url': url}

if __name__ == "__main__":
    result = fetch_and_analyze("https://weareswarm.online")

    with open('simple_test_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("✅ Analysis complete!")
    if 'error' not in result:
        print(f"Title: {result['title']}")
        print(f"SEO Score: {result['seo_score']}/100")
        print(f"UX Score: {result['ux_score']}/100")
        print(f"Overall: {result['overall_score']:.1f}/100")