#!/usr/bin/env python3
"""
Agent-2 Website Audit Tool - Best of Manual + LLM Analysis
Combines Agent-2's analysis capabilities with Ollama LLM insights.
Uses simple HTTP requests and focuses on actionable recommendations.
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

# Simple HTTP client without external dependencies
import urllib.request
import urllib.error

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    ollama = None


class Agent2WebsiteAuditor:
    """
    Agent-2's website auditing approach: Manual analysis + LLM insights.
    Focuses on practical, actionable recommendations for agents.
    """

    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama and HAS_OLLAMA
        if self.use_ollama:
            print("✅ Using Ollama for deep analysis")
        else:
            print("📝 Using manual analysis only")

    def fetch_url_content(self, url: str, timeout: int = 30) -> tuple[str | None, str | None]:
        """
        Fetch URL content using basic HTTP request (like curl).

        Returns:
            (content, error_message)
        """
        try:
            # Create request with user agent
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return content, None

        except urllib.error.HTTPError as e:
            return None, f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return None, f"URL Error: {e.reason}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    def analyze_html_content(self, html: str, url: str) -> Dict:
        """
        Analyze HTML content using Agent-2's expertise.

        Returns comprehensive analysis with scores and recommendations.
        """
        analysis = {
            'url': url,
            'timestamp': int(time.time()),
            'content_size': len(html),
            'word_count': len(html.split()),
        }

        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        analysis['title'] = title_match.group(1).strip() if title_match else ""

        # Extract meta description
        meta_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\'][^>]*>',
                              html, re.IGNORECASE)
        analysis['meta_description'] = meta_match.group(1).strip() if meta_match else ""

        # Count headings
        headings = {}
        for level in range(1, 7):
            pattern = f'<h{level}[^>]*>([^<]+)</h{level}>'
            matches = re.findall(pattern, html, re.IGNORECASE)
            headings[f'h{level}'] = [text.strip() for text in matches]

        analysis['headings'] = headings

        # Check for forms
        analysis['has_forms'] = '<form' in html.lower()

        # Check for common CTA patterns
        cta_patterns = [
            r'join\s+now', r'contact\s+us', r'learn\s+more', r'get\s+started',
            r'sign\s+up', r'contact', r'learn', r'start'
        ]
        analysis['has_cta'] = any(re.search(pattern, html, re.IGNORECASE) for pattern in cta_patterns)

        # Extract image info
        img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        images = re.findall(img_pattern, html, re.IGNORECASE)
        alt_pattern = r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*>'
        alts = re.findall(alt_pattern, html, re.IGNORECASE)

        analysis['images'] = {
            'count': len(images),
            'with_alt': len([alt for alt in alts if alt.strip()]),
            'missing_alt': len(images) - len([alt for alt in alts if alt.strip()])
        }

        # Extract links
        link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
        links = re.findall(link_pattern, html, re.IGNORECASE)
        analysis['links'] = {
            'total': len(links),
            'internal': sum(1 for href, _ in links if href.startswith('/') or urlparse(href).netloc == urlparse(url).netloc),
            'external': sum(1 for href, _ in links if href.startswith(('http://', 'https://')) and urlparse(href).netloc != urlparse(url).netloc)
        }

        return analysis

    def calculate_seo_score(self, analysis: Dict) -> Dict:
        """Calculate SEO score and provide recommendations."""
        score = 100
        issues = []
        recommendations = []

        # Title analysis
        title = analysis['title']
        if not title:
            score -= 25
            issues.append("Missing page title")
            recommendations.append("Add descriptive page title (30-60 characters)")
        elif len(title) < 30:
            score -= 10
            issues.append("Title too short")
            recommendations.append("Expand title to 30-60 characters")
        elif len(title) > 60:
            score -= 5
            issues.append("Title too long")
            recommendations.append("Shorten title to under 60 characters")

        # Meta description
        meta_desc = analysis['meta_description']
        if not meta_desc:
            score -= 20
            issues.append("Missing meta description")
            recommendations.append("Add meta description (120-160 characters)")
        elif len(meta_desc) < 120:
            score -= 10
            issues.append("Meta description too short")
            recommendations.append("Expand meta description to 120-160 characters")

        # Headings
        h1_count = len(analysis['headings']['h1'])
        if h1_count == 0:
            score -= 15
            issues.append("No H1 heading")
            recommendations.append("Add exactly one H1 heading")
        elif h1_count > 1:
            score -= 10
            issues.append("Multiple H1 headings")
            recommendations.append("Use only one H1 heading per page")

        # Images without alt text
        missing_alt = analysis['images']['missing_alt']
        if missing_alt > 0:
            score -= min(missing_alt * 5, 20)
            issues.append(f"{missing_alt} images missing alt text")
            recommendations.append("Add descriptive alt text to all images")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }

    def calculate_ux_score(self, analysis: Dict) -> Dict:
        """Calculate UX score and provide recommendations."""
        score = 100
        issues = []
        recommendations = []

        # CTA check
        if not analysis['has_cta']:
            score -= 20
            issues.append("No clear call-to-action")
            recommendations.append("Add prominent call-to-action buttons")

        # Form check
        if not analysis['has_forms']:
            score -= 10
            issues.append("No contact/lead forms")
            recommendations.append("Add contact or lead capture forms")

        # Content depth
        if analysis['word_count'] < 300:
            score -= 15
            issues.append("Content too short")
            recommendations.append("Expand content for better user engagement")

        # Internal linking
        internal_links = analysis['links']['internal']
        if internal_links < 3:
            score -= 10
            issues.append("Limited internal linking")
            recommendations.append("Add more internal links for better navigation")

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations
        }

    def get_ollama_insights(self, analysis: Dict, content_sample: str) -> Optional[str]:
        """Get deeper insights from Ollama LLM."""
        if not self.use_ollama:
            return None

        try:
            # Create focused prompt for actionable insights
            prompt = f"""Analyze this website's content and provide 3 specific, actionable recommendations for improvement:

URL: {analysis['url']}
Title: {analysis['title']}
Meta Description: {analysis['meta_description']}
Content Sample: {content_sample[:1000]}

Focus on practical improvements agents can implement. Be specific and actionable."""

            response = ollama.generate(
                model='llava',
                prompt=prompt,
                options={'temperature': 0.3, 'num_predict': 300}
            )

            return response['response']

        except Exception as e:
            print(f"⚠️  Ollama analysis failed: {e}")
            return None

    def audit_website(self, url: str) -> Dict:
        """
        Perform complete website audit using Agent-2's hybrid approach.

        Returns:
            Comprehensive audit results with scores and recommendations
        """
        print(f"🔍 Agent-2 auditing: {url}")

        # Fetch content
        html_content, error = self.fetch_url_content(url)
        if error:
            return {
                'url': url,
                'success': False,
                'error': error,
                'method': 'agent2_hybrid'
            }

        # Analyze content
        analysis = self.analyze_html_content(html_content, url)

        # Calculate scores
        seo_analysis = self.calculate_seo_score(analysis)
        ux_analysis = self.calculate_ux_score(analysis)

        # Get Ollama insights
        ollama_insights = self.get_ollama_insights(analysis, html_content)

        # Calculate overall score
        overall_score = (seo_analysis['score'] + ux_analysis['score']) / 2

        # Compile results
        result = {
            'url': url,
            'timestamp': analysis['timestamp'],
            'success': True,
            'method': 'agent2_hybrid',
            'content_stats': {
                'word_count': analysis['word_count'],
                'size_kb': round(analysis['content_size'] / 1024, 1),
                'images': analysis['images']['count'],
                'links': analysis['links']['total']
            },
            'seo_analysis': seo_analysis,
            'ux_analysis': ux_analysis,
            'ollama_insights': ollama_insights,
            'scores': {
                'overall_score': f"Overall Score: {overall_score:.1f}/100",
                'seo_score': f"SEO Score: {seo_analysis['score']}/100",
                'ux_score': f"UX Score: {ux_analysis['score']}/100"
            },
            'priority_actions': [],
            'recommendations': seo_analysis['recommendations'] + ux_analysis['recommendations']
        }

        # Determine priority actions for agents
        if seo_analysis['score'] < 80:
            result['priority_actions'].append("HIGH: Fix SEO issues - meta tags, headings, alt text")
        if ux_analysis['score'] < 80:
            result['priority_actions'].append("HIGH: Improve UX - add CTAs, forms, content depth")
        if analysis['images']['missing_alt'] > 0:
            result['priority_actions'].append(f"MEDIUM: Add alt text to {analysis['images']['missing_alt']} images")

        return result

    def audit_multiple_sites(self, urls: List[str]) -> Dict:
        """Audit multiple websites."""
        print(f"🔍 Agent-2 batch auditing {len(urls)} websites...")

        results = {}
        successful = 0

        for url in urls:
            result = self.audit_website(url)
            results[url] = result
            if result['success']:
                successful += 1

        # Calculate summary
        total_sites = len(urls)
        success_rate = (successful / total_sites * 100) if total_sites > 0 else 0

        # Average scores
        avg_scores = {'overall': 0, 'seo': 0, 'ux': 0}
        score_counts = {'overall': 0, 'seo': 0, 'ux': 0}

        for result in results.values():
            if result['success'] and 'scores' in result:
                for key in ['overall_score', 'seo_score', 'ux_score']:
                    if key in result['scores']:
                        score_text = result['scores'][key]
                        numbers = re.findall(r'(\d+(?:\.\d+)?)', score_text)
                        if numbers:
                            score = float(numbers[0])
                            score_key = key.replace('_score', '')
                            avg_scores[score_key] += score
                            score_counts[score_key] += 1

        for key in avg_scores:
            if score_counts[key] > 0:
                avg_scores[key] = round(avg_scores[key] / score_counts[key], 1)

        return {
            'batch_info': {
                'total_sites': total_sites,
                'successful_audits': successful,
                'failed_audits': total_sites - successful,
                'success_rate': success_rate,
                'timestamp': int(time.time()),
                'method': 'agent2_hybrid'
            },
            'summary': {
                'average_scores': avg_scores,
                'top_issues': self._extract_top_issues(results)
            },
            'audits': results
        }

    def _extract_top_issues(self, results: Dict) -> List[str]:
        """Extract most common issues across all sites."""
        issue_counts = {}

        for result in results.values():
            if not result['success']:
                continue

            for analysis_type in ['seo_analysis', 'ux_analysis']:
                if analysis_type in result:
                    for issue in result[analysis_type]['issues']:
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Return top 5 issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]


def main():
    """Command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent-2 Website Audit Tool")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--output", default="agent2_audit_results.json",
                       help="Output file for results")
    parser.add_argument("--batch", nargs="*", help="Audit multiple URLs")
    parser.add_argument("--no-ollama", action="store_true",
                       help="Skip Ollama analysis, use manual only")

    args = parser.parse_args()

    try:
        auditor = Agent2WebsiteAuditor(use_ollama=not args.no_ollama)

        if args.batch:
            print(f"🔍 Starting Agent-2 batch audit of {len(args.batch)} websites...")
            results = auditor.audit_multiple_sites(args.batch)
        else:
            print(f"🔍 Starting Agent-2 audit of: {args.url}")
            results = auditor.audit_website(args.url)

        # Save results
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Agent-2 audit complete! Results saved to {args.output}")

        # Print summary
        if "summary" in results:
            summary = results["summary"]
            print("\n📊 Summary:")
            print(f"   Sites audited: {results['batch_info']['total_sites']}")
            print(f"   Success rate: {results['batch_info']['success_rate']:.1f}%")
            if summary.get('average_scores'):
                print(f"   Average scores: {summary['average_scores']}")
            if summary.get('top_issues'):
                print("   Top issues:")
                for issue in summary['top_issues'][:3]:
                    print(f"     - {issue}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()