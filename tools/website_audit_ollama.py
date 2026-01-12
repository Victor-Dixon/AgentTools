#!/usr/bin/env python3
"""
Website Auditing Tool using Ollama Local LLM
Captures screenshots of websites and analyzes them with local Ollama models for comprehensive auditing.
"""

import asyncio
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
import requests
from PIL import Image
from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    ollama = None


class WebsiteAuditOllama:
    """
    Website auditing tool that captures screenshots and analyzes them with Ollama LLM.
    Provides comprehensive website analysis including design, UX, performance, and SEO insights.
    """

    def __init__(self, model_name: str = "llava", screenshot_dir: str = "screenshots"):
        """
        Initialize the website auditor.

        Args:
            model_name: Ollama model to use for analysis (default: llava for vision)
            screenshot_dir: Directory to store screenshots
        """
        self.model_name = model_name
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(exist_ok=True)

        if not HAS_OLLAMA:
            raise ImportError("ollama package not installed. Install with: pip install ollama")

    async def capture_screenshot_playwright(self, url: str, wait_time: int = 3) -> Tuple[str, bytes]:
        """
        Capture website screenshot using Playwright.

        Args:
            url: Website URL to capture
            wait_time: Time to wait for page load

        Returns:
            Tuple of (filename, image_bytes)
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Set viewport for consistent screenshots
            await page.set_viewport_size({"width": 1920, "height": 1080})

            try:
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(wait_time)  # Wait for dynamic content

                # Capture full page screenshot
                screenshot_bytes = await page.screenshot(full_page=True)

                # Generate filename
                domain = urlparse(url).netloc.replace(".", "_")
                timestamp = int(time.time())
                filename = f"{domain}_{timestamp}.png"

                return filename, screenshot_bytes

            finally:
                await browser.close()

    def capture_screenshot_selenium(self, url: str, wait_time: int = 3) -> Tuple[str, bytes]:
        """
        Capture website screenshot using Selenium (fallback method).

        Args:
            url: Website URL to capture
            wait_time: Time to wait for page load

        Returns:
            Tuple of (filename, image_bytes)
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(wait_time)  # Wait for dynamic content

            # Capture screenshot
            screenshot_bytes = driver.get_screenshot_as_png()

            # Generate filename
            domain = urlparse(url).netloc.replace(".", "_")
            timestamp = int(time.time())
            filename = f"{domain}_{timestamp}_selenium.png"

            return filename, screenshot_bytes

        finally:
            driver.quit()

    async def analyze_screenshot_ollama(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze screenshot using Ollama vision model.

        Args:
            image_path: Path to screenshot image
            prompt: Analysis prompt for the LLM

        Returns:
            Analysis results from Ollama
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_path]
                }]
            )

            return {
                "success": True,
                "analysis": response['message']['content'],
                "model": self.model_name,
                "prompt": prompt
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name,
                "prompt": prompt
            }

    def save_screenshot(self, filename: str, image_bytes: bytes) -> str:
        """
        Save screenshot to disk.

        Args:
            filename: Filename for the screenshot
            image_bytes: Image data as bytes

        Returns:
            Full path to saved screenshot
        """
        filepath = self.screenshot_dir / filename
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        return str(filepath)

    async def audit_website_comprehensive(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive website audit using screenshot analysis.

        Args:
            url: Website URL to audit

        Returns:
            Comprehensive audit results
        """
        audit_results = {
            "url": url,
            "timestamp": time.time(),
            "analyses": {},
            "recommendations": [],
            "scores": {},
            "errors": []
        }

        try:
            # Capture screenshot
            print(f"📸 Capturing screenshot of {url}...")
            filename, image_bytes = await self.capture_screenshot_playwright(url)

            # Save screenshot
            image_path = self.save_screenshot(filename, image_bytes)
            audit_results["screenshot"] = image_path

            # Define analysis prompts
            analysis_prompts = {
                "design_audit": """
                Analyze this website screenshot for design quality. Evaluate:
                1. Visual design and aesthetics
                2. Color scheme and branding consistency
                3. Typography and readability
                4. Layout and composition
                5. Use of whitespace and visual hierarchy
                6. Mobile responsiveness indicators
                7. Overall design quality score (1-10)

                Provide specific recommendations for improvement.
                """,

                "ux_audit": """
                Evaluate the user experience from this website screenshot:
                1. Navigation clarity and intuitiveness
                2. Call-to-action visibility and effectiveness
                3. Content organization and scannability
                4. Loading indicators and performance hints
                5. Accessibility considerations
                6. User engagement elements
                7. Overall UX quality score (1-10)

                Suggest UX improvements with specific examples.
                """,

                "seo_content_audit": """
                Assess SEO and content quality from this screenshot:
                1. Title and heading structure visibility
                2. Meta description and keyword optimization indicators
                3. Content quality and value proposition clarity
                4. Internal linking structure hints
                5. Social sharing elements
                6. Content marketing effectiveness
                7. Overall SEO readiness score (1-10)

                Provide SEO recommendations and content improvement suggestions.
                """,

                "performance_audit": """
                Analyze performance indicators from this screenshot:
                1. Image optimization and loading hints
                2. Resource loading indicators
                3. Caching and CDN usage signs
                4. JavaScript and CSS optimization indicators
                5. Core Web Vitals compliance hints
                6. Overall performance optimization score (1-10)

                Recommend performance improvements and optimization strategies.
                """
            }

            # Run analyses
            for analysis_type, prompt in analysis_prompts.items():
                print(f"🔍 Running {analysis_type} analysis...")
                result = await self.analyze_screenshot_ollama(image_path, prompt)

                if result["success"]:
                    audit_results["analyses"][analysis_type] = result["analysis"]

                    # Extract scores if present
                    analysis_text = result["analysis"].lower()
                    if "score" in analysis_text or "rating" in analysis_text:
                        # Simple score extraction (can be improved)
                        for line in result["analysis"].split('\n'):
                            if ('score' in line.lower() or 'rating' in line.lower()) and any(char.isdigit() for char in line):
                                audit_results["scores"][analysis_type] = line.strip()
                                break
                else:
                    audit_results["errors"].append(f"{analysis_type}: {result['error']}")

            # Generate consolidated recommendations
            audit_results["recommendations"] = self._generate_recommendations(audit_results)

            # Mark as successful if we have analyses and no critical errors
            audit_results["success"] = len(audit_results["analyses"]) > 0 and len([e for e in audit_results["errors"] if "failed" in e.lower()]) == 0

        except Exception as e:
            audit_results["errors"].append(f"Screenshot capture failed: {str(e)}")

            # Fallback to Selenium
            try:
                print("🔄 Falling back to Selenium screenshot capture...")
                filename, image_bytes = self.capture_screenshot_selenium(url)
                image_path = self.save_screenshot(filename, image_bytes)
                audit_results["screenshot"] = image_path
                audit_results["errors"].append("Used Selenium fallback for screenshot capture")
            except Exception as e2:
                audit_results["errors"].append(f"Selenium fallback also failed: {str(e2)}")

        # Set success based on whether we have any analyses
        audit_results["success"] = len(audit_results.get("analyses", {})) > 0

        return audit_results

    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """
        Generate consolidated recommendations from all analyses.

        Args:
            audit_results: Complete audit results

        Returns:
            List of prioritized recommendations
        """
        recommendations = []

        # Extract recommendations from each analysis
        for analysis_type, analysis in audit_results.get("analyses", {}).items():
            lines = analysis.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'improve', 'should', 'consider']):
                    if len(line) > 20:  # Filter out short/irrelevant lines
                        recommendations.append(f"[{analysis_type.upper()}] {line}")

        # Prioritize and deduplicate
        seen = set()
        prioritized = []
        for rec in recommendations:
            if rec not in seen:
                prioritized.append(rec)
                seen.add(rec)

        return prioritized[:10]  # Return top 10 recommendations

    async def audit_multiple_websites(self, urls: List[str]) -> Dict[str, Any]:
        """
        Audit multiple websites in batch.

        Args:
            urls: List of website URLs to audit

        Returns:
            Batch audit results
        """
        batch_results = {
            "batch_info": {
                "total_urls": len(urls),
                "timestamp": time.time(),
                "model": self.model_name
            },
            "audits": {},
            "summary": {}
        }

        for i, url in enumerate(urls, 1):
            print(f"\n🌐 Auditing website {i}/{len(urls)}: {url}")
            try:
                audit_result = await self.audit_website_comprehensive(url)
                batch_results["audits"][url] = audit_result
            except Exception as e:
                batch_results["audits"][url] = {
                    "error": str(e),
                    "url": url,
                    "timestamp": time.time()
                }

        # Generate batch summary
        batch_results["summary"] = self._generate_batch_summary(batch_results)

        # Convert to expected MCP format
        summary = batch_results["summary"]
        results = []
        for url, audit in batch_results["audits"].items():
            audit_result = audit.copy()
            audit_result["url"] = url
            results.append(audit_result)

        return {
            "success": summary["successful_audits"] > 0,
            "results": results,
            "summary": summary,
            "batch_info": batch_results["batch_info"]
        }

    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for batch audit.

        Args:
            batch_results: Complete batch audit results

        Returns:
            Summary statistics
        """
        audits = batch_results.get("audits", {})
        total_sites = len(audits)
        successful_audits = sum(1 for audit in audits.values() if "error" not in audit)
        failed_audits = total_sites - successful_audits

        # Calculate average scores if available
        total_scores = {}
        score_counts = {}

        for audit in audits.values():
            if "scores" in audit:
                for analysis_type, score_text in audit["scores"].items():
                    # Extract numeric score
                    import re
                    numbers = re.findall(r'\d+', score_text)
                    if numbers:
                        score = int(numbers[0])
                        if analysis_type not in total_scores:
                            total_scores[analysis_type] = 0
                            score_counts[analysis_type] = 0
                        total_scores[analysis_type] += score
                        score_counts[analysis_type] += 1

        avg_scores = {}
        for analysis_type in total_scores:
            avg_scores[analysis_type] = round(total_scores[analysis_type] / score_counts[analysis_type], 1)

        return {
            "total_sites": total_sites,
            "successful_audits": successful_audits,
            "failed_audits": failed_audits,
            "success_rate": round(successful_audits / total_sites * 100, 1) if total_sites > 0 else 0,
            "average_scores": avg_scores,
            "common_issues": [],  # Could be populated with frequent issues
            "recommendations": []  # Could be populated with common recommendations
        }


async def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Website Auditing Tool using Ollama LLM")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--model", default="llava", help="Ollama model to use (default: llava)")
    parser.add_argument("--output", default="audit_results.json", help="Output file for results")
    parser.add_argument("--batch", nargs="*", help="Audit multiple URLs")

    args = parser.parse_args()

    try:
        auditor = WebsiteAuditOllama(model_name=args.model)

        if args.batch:
            print(f"🌐 Starting batch audit of {len(args.batch)} websites...")
            results = await auditor.audit_multiple_websites(args.batch)
        else:
            print(f"🌐 Auditing single website: {args.url}")
            results = await auditor.audit_website_comprehensive(args.url)

        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"✅ Audit complete! Results saved to {args.output}")

        # Print summary
        if "summary" in results:
            summary = results["summary"]
            print("\n📊 Batch Summary:")
            print(f"   Sites audited: {summary['total_sites']}")
            print(f"   Success rate: {summary['success_rate']}%")
            if summary['average_scores']:
                print(f"   Average scores: {summary['average_scores']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())