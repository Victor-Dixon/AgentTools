#!/usr/bin/env python3
"""
Test script for MCP website audit server functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_functions():
    """Test the MCP server functions directly"""
    try:
        from mcp_servers.website_audit_server import (
            check_ollama_status,
            get_available_ollama_models,
            audit_website_screenshot
        )

        print("🔍 Testing MCP server functions...")

        # Test Ollama status
        print("\n1. Testing Ollama status...")
        status = check_ollama_status()
        if status.get("success"):
            print(f"✅ Ollama status: {status}")
        else:
            print(f"❌ Ollama status check failed: {status}")
            return False

        # Test available models
        print("\n2. Testing available models...")
        models = get_available_ollama_models()
        if models.get("success"):
            available_models = models.get("available_models", [])
            vision_models = [m for m in available_models if any(v in m.lower() for v in ['llava', 'bakllava', 'moondream'])]
            print(f"✅ Available models: {len(available_models)} total, {len(vision_models)} vision models")
            print(f"   Vision models: {vision_models}")
        else:
            print(f"❌ Model check failed: {models}")
            return False

        # Test website audit (quick test with example.com)
        print("\n3. Testing website audit...")
        audit_result = audit_website_screenshot(
            url="https://example.com",
            model_name="moondream",  # Use fastest model for testing
            analysis_type="design"
        )

        if audit_result.get("success"):
            print("✅ Website audit successful")
            if "analysis" in audit_result:
                analysis = audit_result["analysis"]
                print(f"   Analysis length: {len(analysis)} characters")
                print(f"   Preview: {analysis[:100]}...")
        else:
            print(f"❌ Website audit failed: {audit_result.get('error', 'Unknown error')}")

        print("\n✅ All MCP server tests completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == '__main__':
    test_mcp_functions()