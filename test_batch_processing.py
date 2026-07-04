#!/usr/bin/env python3
"""
Test script for batch processing and error recovery
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_batch_processing():
    """Test batch processing with error recovery"""
    try:
        from mcp_servers.website_audit_server import audit_multiple_websites

        print("🔍 Testing batch processing with error recovery...")

        # Test with mix of valid and invalid URLs
        test_urls = [
            "https://example.com",        # Valid
            "https://httpbin.org",        # Valid
            "https://invalid-domain-that-does-not-exist-12345.com",  # Invalid
            "https://google.com",         # Valid
            "not-a-url",                  # Invalid format
        ]

        print(f"Testing batch with {len(test_urls)} URLs (some valid, some invalid)...")

        batch_result = audit_multiple_websites(
            urls=test_urls,
            model_name="moondream"  # Use fastest model for testing
        )

        if batch_result.get("success"):
            results = batch_result.get("results", [])
            print(f"✅ Batch processing successful: {len(results)} results")

            successful_audits = 0
            failed_audits = 0

            for i, result in enumerate(results):
                url = result.get("url", f"url_{i}")
                if result.get("success"):
                    successful_audits += 1
                    analyses = result.get("analyses", {})
                    print(f"   ✅ {url}: {len(analyses)} analyses completed")
                else:
                    failed_audits += 1
                    error = result.get("error", "Unknown error")
                    print(f"   ❌ {url}: {error}")

            print(f"\n📊 Batch Summary:")
            print(f"   Total URLs: {len(results)}")
            print(f"   Successful: {successful_audits}")
            print(f"   Failed: {failed_audits}")
            print(".1f")

            # Test error recovery - should have some successes and some failures
            if successful_audits > 0 and failed_audits > 0:
                print("✅ Error recovery working correctly (partial success)")
                return True
            elif successful_audits == len(results):
                print("⚠️ All audits successful (no error recovery needed)")
                return True
            else:
                print("❌ No successful audits - error recovery may have issues")
                return False
        else:
            print(f"❌ Batch processing failed: {batch_result.get('error', 'Unknown error')}")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_batch_processing()
    if success:
        print("\n✅ Batch processing test completed successfully!")
    else:
        print("\n❌ Batch processing test failed!")