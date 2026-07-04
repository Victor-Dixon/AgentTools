#!/usr/bin/env python3
"""
Streamlined Website Audit - Agent-2's Best Approach
Combines manual analysis expertise with optional LLM insights.
Simple, reliable, and focused on actionable agent recommendations.
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List
from urllib.parse import urljoin, urlparse
import urllib.request
import urllib.error

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


class StreamlinedWebsiteAuditor:
    """Streamlined auditor focusing on Agent-2's strengths."""

    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama and HAS_OLLAMA
        print(f"🔍 Agent-2 Website Auditor (Ollama: {'✅' if self.use_ollama else '❌'})")

    def fetch_content(self, url: str) -> tuple[str | None, str | None]:
        """Simple HTTP fetch like curl."""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return content, None
        except Exception as e:
            return None, str(e)

    def analyze_content(self, html: str, url: str) -> Dict:
        """Agent-2's manual analysis approach."""
        analysis = {
            'url': url,
            'timestamp': int(time.time()),
            'content_length': len(html),
            'word_count': len(html.split())
        }

        # Extract key elements
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        analysis['title'] = title_match.group(1).strip() if title_match else ""

        meta_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
        analysis['meta_desc'] = meta_match.group(1).strip() if meta_match else ""

        # Headings
        analysis['h1_count'] = len(re.findall(r'<h1[^>]*>.*?</h1>', html, re.IGNORECASE))
        analysis['h2_count'] = len(re.findall(r'<h2[^>]*>.*?</h2>', html, re.IGNORECASE))

        # Content checks
        analysis['has_forms'] = '<form' in html.lower()
        analysis['has_buttons'] = '<button' in html.lower() or 'button' in html.lower()

        # CTA detection
        cta_words = ['join', 'contact', 'learn', 'start', 'signup', 'download']
        analysis['has_cta'] = any(word in html.lower() for word in cta_words)

        # Images
        img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        analysis['image_count'] = len(img_tags)
        analysis['images_with_alt'] = len([img for img in img_tags if 'alt=' in img])

        # Links
        link_tags = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>.*?</a>', html, re.IGNORECASE)
        analysis['link_count'] = len(link_tags)
        analysis['internal_links'] = sum(1 for href in link_tags if href.startswith('/') or urlparse(href).netloc == urlparse(url).netloc)
        analysis['external_links'] = sum(1 for href in link_tags if href.startswith(('http://', 'https://')) and urlparse(href).netloc != urlparse(url).netloc)

        return analysis

    def calculate_scores(self, analysis: Dict) -> Dict:
        """Calculate SEO and UX scores with Agent-2's expertise."""
        seo_score = 100
        ux_score = 100
        issues = []
        recommendations = []

        # SEO Scoring
        if not analysis['title']:
            seo_score -= 25
            issues.append("Missing page title")
            recommendations.append("Add descriptive page title (30-60 characters)")
        elif len(analysis['title']) < 30:
            seo_score -= 10
            issues.append("Title too short")
        elif len(analysis['title']) > 60:
            seo_score -= 5
            issues.append("Title too long")

        if not analysis['meta_desc']:
            seo_score -= 20
            issues.append("Missing meta description")
            recommendations.append("Add meta description (120-160 characters)")
        elif len(analysis['meta_desc']) < 120:
            seo_score -= 10
            issues.append("Meta description too short")

        if analysis['h1_count'] == 0:
            seo_score -= 15
            issues.append("No H1 heading")
            recommendations.append("Add one H1 heading")
        elif analysis['h1_count'] > 1:
            seo_score -= 10
            issues.append("Multiple H1 headings")

        missing_alt = analysis['image_count'] - analysis['images_with_alt']
        if missing_alt > 0:
            seo_score -= min(missing_alt * 5, 20)
            issues.append(f"{missing_alt} images missing alt text")
            recommendations.append("Add alt text to all images")

        # UX Scoring
        if not analysis['has_cta']:
            ux_score -= 20
            issues.append("No clear call-to-action")
            recommendations.append("Add prominent CTA buttons")

        if not analysis['has_forms']:
            ux_score -= 10
            issues.append("No contact forms")
            recommendations.append("Add contact/lead capture forms")

        if analysis['word_count'] < 300:
            ux_score -= 15
            issues.append("Content too short")
            recommendations.append("Expand content depth")

        if analysis['internal_links'] < 3:
            ux_score -= 10
            issues.append("Limited internal linking")
            recommendations.append("Add more internal navigation links")

        return {
            'seo_score': max(0, seo_score),
            'ux_score': max(0, ux_score),
            'overall_score': max(0, (seo_score + ux_score) / 2),
            'issues': issues,
            'recommendations': recommendations
        }

    def get_ollama_insights(self, analysis: Dict, content_sample: str) -> str | None:
        """Get targeted LLM insights."""
        if not self.use_ollama:
            return None

        try:
            prompt = f"""Analyze this website and provide 2-3 specific recommendations for agents to implement:

URL: {analysis['url']}
Title: {analysis['title']}
Meta: {analysis['meta_desc'][:100]}...
Content words: {analysis['word_count']}
Has forms: {analysis['has_forms']}, Has CTA: {analysis['has_cta']}
Images: {analysis['image_count']}, Links: {analysis['link_count']}

Focus on practical, implementable improvements. Be specific."""

            response = ollama.generate(
                model='llava',
                prompt=prompt,
                options={'temperature': 0.3, 'num_predict': 200}
            )
            return response['response']
        except Exception as e:
            return f"Ollama analysis failed: {e}"

    def audit_website(self, url: str) -> Dict:
        """Complete website audit using Agent-2's approach."""
        print(f"🔍 Auditing: {url}")

        # Fetch content
        html, error = self.fetch_content(url)
        if error:
            return {
                'url': url,
                'success': False,
                'error': error,
                'method': 'agent2_streamlined'
            }

        # Analyze
        analysis = self.analyze_content(html, url)
        scores = self.calculate_scores(analysis)
        ollama_insights = self.get_ollama_insights(analysis, html[:1000]) if self.use_ollama else None

        # Compile results
        result = {
            'url': url,
            'timestamp': analysis['timestamp'],
            'success': True,
            'method': 'agent2_streamlined',
            'content_stats': {
                'words': analysis['word_count'],
                'size_kb': round(analysis['content_length'] / 1024, 1),
                'images': analysis['image_count'],
                'links': analysis['link_count']
            },
            'scores': {
                'overall': f"Overall Score: {scores['overall_score']:.1f}/100",
                'seo': f"SEO Score: {scores['seo_score']}/100",
                'ux': f"UX Score: {scores['ux_score']}/100"
            },
            'issues': scores['issues'],
            'recommendations': scores['recommendations'],
            'ollama_insights': ollama_insights,
            'priority_actions': self._get_priority_actions(scores)
        }

        return result

    def _get_priority_actions(self, scores: Dict) -> List[str]:
        """Determine priority actions for agents."""
        actions = []

        if scores['seo_score'] < 80:
            actions.append("HIGH: Fix SEO issues - titles, meta descriptions, headings")
        if scores['ux_score'] < 80:
            actions.append("HIGH: Improve UX - add CTAs, forms, expand content")
        if scores['overall_score'] < 70:
            actions.append("CRITICAL: Major improvements needed - coordinate with Agent-7")

        return actions

    def audit_batch(self, urls: List[str]) -> Dict:
        """Audit multiple websites."""
        print(f"🔍 Batch auditing {len(urls)} websites...")

        results = {}
        successful = 0

        for url in urls:
            result = self.audit_website(url)
            results[url] = result
            if result['success']:
                successful += 1

        # Calculate summary
        total = len(urls)
        success_rate = (successful / total * 100) if total > 0 else 0

        # Average scores
        avg_scores = {'overall': 0, 'seo': 0, 'ux': 0}
        counts = {'overall': 0, 'seo': 0, 'ux': 0}

        for result in results.values():
            if result['success'] and 'scores' in result:
                for key in ['overall', 'seo', 'ux']:
                    score_text = result['scores'][key]
                    numbers = re.findall(r'(\d+(?:\.\d+)?)', score_text)
                    if numbers:
                        score = float(numbers[0])
                        avg_scores[key] += score
                        counts[key] += 1

        for key in avg_scores:
            if counts[key] > 0:
                avg_scores[key] = round(avg_scores[key] / counts[key], 1)

        return {
            'batch_summary': {
                'total_sites': total,
                'successful': successful,
                'success_rate': success_rate,
                'average_scores': avg_scores,
                'timestamp': int(time.time())
            },
            'results': results
        }


def main():
    """Command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent-2 Streamlined Website Audit")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--output", default="streamlined_audit.json", help="Output file")
    parser.add_argument("--batch", nargs="*", help="Multiple URLs")
    parser.add_argument("--no-ollama", action="store_true", help="Skip Ollama analysis")

    args = parser.parse_args()

    auditor = StreamlinedWebsiteAuditor(use_ollama=not args.no_ollama)

    if args.batch:
        results = auditor.audit_batch(args.batch)
    else:
        results = auditor.audit_website(args.url)
        # Wrap single result for consistency
        results = {'results': {args.url: results}}

    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ Audit complete! Saved to {args.output}")

    # Print summary
    if 'batch_summary' in results:
        summary = results['batch_summary']
        print(f"📊 Audited {summary['total_sites']} sites ({summary['success_rate']:.1f}% success)")
        print(f"Average scores: {summary['average_scores']}")


if __name__ == "__main__":
    main()