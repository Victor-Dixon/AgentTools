#!/usr/bin/env python3
"""
Hybrid Website Auditing Tool - Agent-2 Enhanced Version
Combines automated Ollama LLM analysis with manual inspection capabilities.
Uses HTTP requests instead of browser screenshots for better reliability.
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

import httpx
import requests
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    ollama = None


class HybridWebsiteAuditor:
    """
    Hybrid website auditor that combines automated analysis with manual inspection.
    Uses HTTP requests for content fetching and both automated + manual analysis.
    """

    def __init__(self, model_name: str = "llava", timeout: int = 30):
        """
        Initialize the hybrid auditor.

        Args:
            model_name: Ollama model to use for analysis
            timeout: HTTP request timeout in seconds
        """
        self.model_name = model_name
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if not HAS_OLLAMA:
            print("⚠️  Ollama not available - running manual analysis only")
        else:
            print(f"✅ Using Ollama model: {model_name}")

    def fetch_page_content(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch page content using HTTP requests (curl equivalent).

        Args:
            url: Website URL to fetch

        Returns:
            Tuple of (html_content, error_message)
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return None, f"Non-HTML content type: {content_type}"

            return response.text, None

        except requests.exceptions.RequestException as e:
            return None, f"HTTP Error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

    def parse_html_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract key elements for analysis.

        Args:
            html: Raw HTML content
            url: Original URL for context

        Returns:
            Parsed content dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract key elements
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name', '').lower() == 'description':
                meta_desc = tag.get('content', '').strip()
                break

        # Extract headings
        headings = {
            'h1': [h.get_text().strip() for h in soup.find_all('h1')],
            'h2': [h.get_text().strip() for h in soup.find_all('h2')],
            'h3': [h.get_text().strip() for h in soup.find_all('h3')]
        }

        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip()
            # Convert relative URLs to absolute
            if not href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                href = urljoin(url, href)
            links.append({'url': href, 'text': text})

        # Check for common elements
        has_cta = bool(soup.find_all(['button', 'a'], string=re.compile(r'(join|contact|learn|start|buy|signup)', re.I)))
        has_form = bool(soup.find_all('form'))

        # Extract image info
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and not src.startswith(('http://', 'https://')):
                src = urljoin(url, src)
            images.append({'src': src, 'alt': alt})

        return {
            'title': title,
            'meta_description': meta_desc,
            'headings': headings,
            'links': links[:50],  # Limit to first 50 links
            'has_cta': has_cta,
            'has_form': has_form,
            'images': images[:20],  # Limit to first 20 images
            'word_count': len(html.split()),
            'html_size': len(html)
        }

    def manual_seo_analysis(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform manual SEO analysis based on parsed content.

        Args:
            parsed_content: Parsed HTML content

        Returns:
            SEO analysis results
        """
        issues = []
        score = 100

        # Title analysis
        title = parsed_content['title']
        if not title:
            issues.append("Missing page title")
            score -= 20
        elif len(title) < 30:
            issues.append("Title too short (< 30 characters)")
            score -= 10
        elif len(title) > 60:
            issues.append("Title too long (> 60 characters)")
            score -= 5

        # Meta description analysis
        meta_desc = parsed_content['meta_description']
        if not meta_desc:
            issues.append("Missing meta description")
            score -= 15
        elif len(meta_desc) < 120:
            issues.append("Meta description too short (< 120 characters)")
            score -= 10
        elif len(meta_desc) > 160:
            issues.append("Meta description too long (> 160 characters)")
            score -= 5

        # Heading structure
        h1_count = len(parsed_content['headings']['h1'])
        if h1_count == 0:
            issues.append("No H1 heading found")
            score -= 15
        elif h1_count > 1:
            issues.append("Multiple H1 headings (should have only one)")
            score -= 10

        # Image alt text
        images_without_alt = sum(1 for img in parsed_content['images'] if not img['alt'])
        if images_without_alt > 0:
            issues.append(f"{images_without_alt} images missing alt text")
            score -= min(images_without_alt * 5, 20)

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                "Add descriptive meta description (120-160 characters)",
                "Ensure single H1 heading per page",
                "Add alt text to all images",
                "Optimize title length (30-60 characters)"
            ] if issues else ["SEO structure looks good"]
        }

    def manual_ux_analysis(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform manual UX analysis.

        Args:
            parsed_content: Parsed HTML content

        Returns:
            UX analysis results
        """
        issues = []
        score = 100

        # CTA analysis
        if not parsed_content['has_cta']:
            issues.append("No clear call-to-action elements found")
            score -= 20

        # Form analysis
        if not parsed_content['has_form']:
            issues.append("No contact/lead capture forms found")
            score -= 10

        # Content analysis
        word_count = parsed_content['word_count']
        if word_count < 300:
            issues.append("Page content appears too short for meaningful engagement")
            score -= 15

        # Link analysis
        internal_links = sum(1 for link in parsed_content['links']
                           if 'url' in link and urlparse(link['url']).netloc == urlparse('').netloc)
        if internal_links < 3:
            issues.append("Limited internal linking structure")
            score -= 10

        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': [
                "Add prominent call-to-action buttons",
                "Include contact/lead capture forms",
                "Expand content depth and quality",
                "Improve internal linking structure"
            ] if issues else ["UX elements well implemented"]
        }

    async def ollama_deep_analysis(self, content_sample: str, analysis_type: str) -> Optional[str]:
        """
        Use Ollama for deeper analysis of specific aspects.

        Args:
            content_sample: Sample of page content
            analysis_type: Type of analysis (design, performance, etc.)

        Returns:
            Ollama analysis result or None if failed
        """
        if not HAS_OLLAMA:
            return None

        prompts = {
            'design': f"Analyze this website's design quality based on this HTML sample. Rate 1-10 and provide specific recommendations:\n\n{content_sample[:2000]}",
            'performance': f"Analyze potential performance issues in this HTML. Focus on images, scripts, and loading optimization:\n\n{content_sample[:2000]}",
            'accessibility': f"Check for accessibility issues in this HTML content. Look for missing alt text, semantic structure, etc.:\n\n{content_sample[:2000]}"
        }

        try:
            prompt = prompts.get(analysis_type, f"Analyze this web content for {analysis_type}:\n\n{content_sample[:2000]}")

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={'temperature': 0.3, 'num_predict': 200}
                )
            )

            return response['response']

        except Exception as e:
            print(f"⚠️  Ollama {analysis_type} analysis failed: {e}")
            return None

    async def audit_website_comprehensive(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive website audit using hybrid approach.

        Args:
            url: Website URL to audit

        Returns:
            Complete audit results
        """
        print(f"🌐 Starting hybrid audit of: {url}")

        # Fetch content
        html_content, error = self.fetch_page_content(url)
        if error:
            return {
                'url': url,
                'timestamp': int(time.time()),
                'error': error,
                'success': False
            }

        # Parse content
        parsed_content = self.parse_html_content(html_content, url)

        # Manual analyses
        seo_analysis = self.manual_seo_analysis(parsed_content)
        ux_analysis = self.manual_ux_analysis(parsed_content)

        # Ollama deep analyses (run concurrently)
        ollama_tasks = [
            self.ollama_deep_analysis(html_content, 'design'),
            self.ollama_deep_analysis(html_content, 'performance'),
            self.ollama_deep_analysis(html_content, 'accessibility')
        ]

        ollama_results = await asyncio.gather(*ollama_tasks, return_exceptions=True)

        # Calculate overall score
        manual_avg = (seo_analysis['score'] + ux_analysis['score']) / 2
        overall_score = manual_avg  # Could be adjusted based on Ollama results

        # Compile results
        result = {
            'url': url,
            'timestamp': int(time.time()),
            'success': True,
            'parsed_content': parsed_content,
            'analyses': {
                'seo_analysis': seo_analysis,
                'ux_analysis': ux_analysis,
                'design_analysis': ollama_results[0] if not isinstance(ollama_results[0], Exception) else None,
                'performance_analysis': ollama_results[1] if not isinstance(ollama_results[1], Exception) else None,
                'accessibility_analysis': ollama_results[2] if not isinstance(ollama_results[2], Exception) else None
            },
            'scores': {
                'overall_score': f"Overall Score: {overall_score:.1f}/100",
                'seo_score': f"SEO Score: {seo_analysis['score']}/100 - {', '.join(seo_analysis['issues'][:2])}",
                'ux_score': f"UX Score: {ux_analysis['score']}/100 - {', '.join(ux_analysis['issues'][:2])}"
            },
            'recommendations': seo_analysis['recommendations'] + ux_analysis['recommendations'],
            'method': 'hybrid_manual_ollama'
        }

        return result

    async def audit_multiple_websites(self, urls: List[str]) -> Dict[str, Any]:
        """
        Audit multiple websites concurrently.

        Args:
            urls: List of URLs to audit

        Returns:
            Batch audit results
        """
        print(f"🌐 Starting batch audit of {len(urls)} websites...")

        # Audit all sites concurrently
        tasks = [self.audit_website_comprehensive(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        audits = {}
        successful_audits = 0

        for i, result in enumerate(results):
            url = urls[i]
            if isinstance(result, Exception):
                audits[url] = {'error': str(result), 'success': False}
            else:
                audits[url] = result
                if result.get('success', False):
                    successful_audits += 1

        # Calculate summary
        total_sites = len(urls)
        success_rate = (successful_audits / total_sites * 100) if total_sites > 0 else 0

        # Calculate average scores
        avg_scores = {}
        score_counts = {'overall': 0, 'seo': 0, 'ux': 0}
        total_scores = {'overall': 0, 'seo': 0, 'ux': 0}

        for audit in audits.values():
            if audit.get('success') and 'scores' in audit:
                scores = audit['scores']
                # Extract numeric scores
                for key in ['overall_score', 'seo_score', 'ux_score']:
                    if key in scores:
                        score_text = scores[key]
                        numbers = re.findall(r'(\d+(?:\.\d+)?)', score_text)
                        if numbers:
                            score = float(numbers[0])
                            score_key = key.replace('_score', '')
                            total_scores[score_key] += score
                            score_counts[score_key] += 1

        for key in avg_scores:
            if score_counts[key] > 0:
                avg_scores[key] = round(total_scores[key] / score_counts[key], 1)

        return {
            'batch_info': {
                'total_urls': total_sites,
                'timestamp': int(time.time()),
                'model': self.model_name if HAS_OLLAMA else 'manual_only'
            },
            'summary': {
                'total_sites': total_sites,
                'successful_audits': successful_audits,
                'failed_audits': total_sites - successful_audits,
                'success_rate': success_rate,
                'average_scores': avg_scores
            },
            'audits': audits
        }


async def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Website Auditing Tool")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--model", default="llava", help="Ollama model to use (default: llava)")
    parser.add_argument("--output", default="hybrid_audit_results.json", help="Output file for results")
    parser.add_argument("--batch", nargs="*", help="Audit multiple URLs")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")

    args = parser.parse_args()

    try:
        auditor = HybridWebsiteAuditor(model_name=args.model, timeout=args.timeout)

        if args.batch:
            print(f"🌐 Starting hybrid batch audit of {len(args.batch)} websites...")
            results = await auditor.audit_multiple_websites(args.batch)
        else:
            print(f"🌐 Starting hybrid audit of: {args.url}")
            results = await auditor.audit_website_comprehensive(args.url)

        # Save results
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print(f"✅ Hybrid audit complete! Results saved to {args.output}")

        # Print summary
        if "summary" in results:
            summary = results["summary"]
            print("\n📊 Batch Summary:")
            print(f"   Sites audited: {summary['total_sites']}")
            print(f"   Success rate: {summary['success_rate']:.1f}%")
            if summary.get('average_scores'):
                print(f"   Average scores: {summary['average_scores']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())