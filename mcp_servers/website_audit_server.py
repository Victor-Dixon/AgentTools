#!/usr/bin/env python3
"""
MCP Server for Website Auditing with Ollama LLM
Provides website auditing capabilities via screenshot analysis with local Ollama models.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

try:
    from tools.website_audit_ollama import WebsiteAuditOllama
    HAS_AUDIT_TOOL = True
except ImportError:
    HAS_AUDIT_TOOL = False
    WebsiteAuditOllama = None


def audit_website_screenshot(
    url: str,
    model_name: Optional[str] = "llava",
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Audit a website using screenshot analysis with Ollama LLM.

    Args:
        url: Website URL to audit
        model_name: Ollama model to use for analysis
        analysis_type: Type of analysis (comprehensive, design, ux, seo, performance)

    Returns:
        Audit results dictionary
    """
    if not HAS_AUDIT_TOOL:
        return {
            "success": False,
            "error": "Website auditing tool not available. Check installation."
        }

    async def run_audit():
        auditor = WebsiteAuditOllama(model_name=model_name)

        if analysis_type == "comprehensive":
            return await auditor.audit_website_comprehensive(url)
        else:
            # For specific analysis types, we could implement targeted prompts
            # For now, fall back to comprehensive
            return await auditor.audit_website_comprehensive(url)

    try:
        # Run the async audit
        result = asyncio.run(run_audit())
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Audit failed: {str(e)}",
            "url": url
        }


def audit_multiple_websites(
    urls: List[str],
    model_name: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    Audit multiple websites in batch.

    Args:
        urls: List of website URLs to audit
        model_name: Ollama model to use for analysis

    Returns:
        Batch audit results
    """
    if not HAS_AUDIT_TOOL:
        return {
            "success": False,
            "error": "Website auditing tool not available. Check installation."
        }

    async def run_batch_audit():
        auditor = WebsiteAuditOllama(model_name=model_name)
        return await auditor.audit_multiple_websites(urls)

    try:
        result = asyncio.run(run_batch_audit())
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch audit failed: {str(e)}",
            "urls_attempted": urls
        }


def get_available_ollama_models() -> Dict[str, Any]:
    """
    Get list of available Ollama models for vision analysis.

    Returns:
        Available models information
    """
    try:
        import ollama

        # Get running models
        running = ollama.list()

        # Filter for vision-capable models (models that can handle images)
        vision_models = []
        for model in running.models:
            model_name = model.model
            # Common vision-capable models
            if any(vision_model in model_name.lower() for vision_model in
                   ['llava', 'bakllava', 'moondream', 'llama-vision', 'gpt4v']):
                vision_models.append(model_name)

        return {
            "success": True,
            "available_models": vision_models,
            "total_models": len(running.models),
            "vision_capable": len(vision_models)
        }

    except ImportError:
        return {
            "success": False,
            "error": "Ollama package not installed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get Ollama models: {str(e)}"
        }


def analyze_website_design(
    url: str,
    model_name: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    Analyze website design quality from screenshot.

    Args:
        url: Website URL to analyze
        model_name: Ollama model to use

    Returns:
        Design analysis results
    """
    if not HAS_AUDIT_TOOL:
        return {
            "success": False,
            "error": "Website auditing tool not available"
        }

    async def run_design_analysis():
        auditor = WebsiteAuditOllama(model_name=model_name)

        # Capture screenshot
        filename, image_bytes = await auditor.capture_screenshot_playwright(url)
        image_path = auditor.save_screenshot(filename, image_bytes)

        # Design-specific analysis
        design_prompt = """
        Analyze this website screenshot focusing on design quality:

        1. VISUAL DESIGN & AESTHETICS
           - Color scheme effectiveness and harmony
           - Typography choices and hierarchy
           - Image quality and relevance
           - Overall visual appeal

        2. LAYOUT & COMPOSITION
           - Use of whitespace and balance
           - Content organization and flow
           - Visual hierarchy effectiveness
           - Responsive design indicators

        3. BRANDING & CONSISTENCY
           - Logo placement and prominence
           - Brand color usage
           - Consistent styling elements
           - Professional appearance

        4. DESIGN SCORE (1-10)
           Provide an overall design quality score with justification.

        5. SPECIFIC IMPROVEMENTS
           List 3-5 actionable design improvement recommendations.

        Be specific and constructive in your analysis.
        """

        result = await auditor.analyze_screenshot_ollama(image_path, design_prompt)
        result["analysis_type"] = "design"
        result["url"] = url
        return result

    try:
        result = asyncio.run(run_design_analysis())
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Design analysis failed: {str(e)}",
            "analysis_type": "design",
            "url": url
        }


def analyze_website_ux(
    url: str,
    model_name: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    Analyze website user experience from screenshot.

    Args:
        url: Website URL to analyze
        model_name: Ollama model to use

    Returns:
        UX analysis results
    """
    if not HAS_AUDIT_TOOL:
        return {
            "success": False,
            "error": "Website auditing tool not available"
        }

    async def run_ux_analysis():
        auditor = WebsiteAuditOllama(model_name=model_name)

        # Capture screenshot
        filename, image_bytes = await auditor.capture_screenshot_playwright(url)
        image_path = auditor.save_screenshot(filename, image_bytes)

        # UX-specific analysis
        ux_prompt = """
        Analyze this website screenshot focusing on user experience quality:

        1. NAVIGATION & USABILITY
           - Menu clarity and accessibility
           - Information architecture visibility
           - Search functionality presence
           - Wayfinding effectiveness

        2. CALL-TO-ACTION ELEMENTS
           - Primary CTA visibility and prominence
           - Button design and placement
           - Conversion funnel indicators
           - User guidance elements

        3. CONTENT ACCESSIBILITY
           - Text readability and contrast
           - Interactive element clarity
           - Error prevention indicators
           - User feedback mechanisms

        4. MOBILE RESPONSIVENESS
           - Touch-friendly element sizing
           - Content adaptation hints
           - Navigation accessibility
           - Loading performance indicators

        5. UX SCORE (1-10)
           Provide an overall user experience score with justification.

        6. UX IMPROVEMENT PRIORITIES
           List the top 3 UX issues that should be addressed first.

        Focus on user-centered analysis and actionable insights.
        """

        result = await auditor.analyze_screenshot_ollama(image_path, ux_prompt)
        result["analysis_type"] = "ux"
        result["url"] = url
        return result

    try:
        result = asyncio.run(run_ux_analysis())
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"UX analysis failed: {str(e)}",
            "analysis_type": "ux",
            "url": url
        }


def analyze_website_seo(
    url: str,
    model_name: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    Analyze website SEO readiness from screenshot.

    Args:
        url: Website URL to analyze
        model_name: Ollama model to use

    Returns:
        SEO analysis results
    """
    if not HAS_AUDIT_TOOL:
        return {
            "success": False,
            "error": "Website auditing tool not available"
        }

    async def run_seo_analysis():
        auditor = WebsiteAuditOllama(model_name=model_name)

        # Capture screenshot
        filename, image_bytes = await auditor.capture_screenshot_playwright(url)
        image_path = auditor.save_screenshot(filename, image_bytes)

        # SEO-specific analysis
        seo_prompt = """
        Analyze this website screenshot for SEO readiness and content optimization:

        1. TITLE & META ELEMENTS
           - Title tag visibility and optimization
           - Meta description presence indicators
           - URL structure hints
           - Page title effectiveness

        2. HEADING STRUCTURE
           - H1 tag usage and prominence
           - Heading hierarchy (H1-H6)
           - Content structure clarity
           - Keyword targeting visibility

        3. CONTENT QUALITY SIGNALS
           - Content depth and value indicators
           - Internal linking structure hints
           - User engagement elements
           - Content marketing effectiveness

        4. TECHNICAL SEO INDICATORS
           - HTTPS/security indicators
           - Mobile-friendliness signs
           - Page speed optimization hints
           - Core Web Vitals compliance clues

        5. SEO SCORE (1-10)
           Provide an overall SEO readiness score.

        6. SEO PRIORITY ACTIONS
           List the top 3 SEO improvements that would have the biggest impact.

        Focus on visible SEO elements and provide specific recommendations.
        """

        result = await auditor.analyze_screenshot_ollama(image_path, seo_prompt)
        result["analysis_type"] = "seo"
        result["url"] = url
        return result

    try:
        result = asyncio.run(run_seo_analysis())
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"SEO analysis failed: {str(e)}",
            "analysis_type": "seo",
            "url": url
        }


# MCP Server functions for Cursor integration
def audit_website_full(
    url: str,
    model: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    MCP function: Perform comprehensive website audit.
    """
    return audit_website_screenshot(url, model, "comprehensive")


def audit_website_batch(
    urls: List[str],
    model: Optional[str] = "llava"
) -> Dict[str, Any]:
    """
    MCP function: Audit multiple websites in batch.
    """
    return audit_multiple_websites(urls, model)


def check_ollama_status() -> Dict[str, Any]:
    """
    MCP function: Check Ollama availability and models.
    """
    return get_available_ollama_models()


# Export functions for MCP server
__all__ = [
    "audit_website_full",
    "audit_website_batch",
    "analyze_website_design",
    "analyze_website_ux",
    "analyze_website_seo",
    "check_ollama_status"
]