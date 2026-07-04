#!/usr/bin/env python3
"""
Test script for Ollama vision model capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.website_audit_ollama import WebsiteAuditOllama

async def test_ollama_vision():
    auditor = WebsiteAuditOllama()

    # Find the screenshot file we just created
    screenshot_dir = 'screenshots'
    screenshots = [f for f in os.listdir(screenshot_dir) if f.endswith('.png')]
    if not screenshots:
        print('❌ No screenshot files found')
        return

    screenshot_path = os.path.join(screenshot_dir, screenshots[0])
    print(f'🔍 Testing Ollama vision analysis on: {screenshot_path}')

    # Test different vision models
    models_to_test = ['llava', 'bakllava', 'moondream']

    for model in models_to_test:
        auditor.model_name = model
        print(f'\n🤖 Testing model: {model}')

        try:
            result = await auditor.analyze_screenshot_ollama(
                image_path=screenshot_path,
                prompt='Analyze this website screenshot. Describe the layout, design, and main content elements you can see.'
            )

            if result['success']:
                print('✅ Analysis successful')
                analysis_len = len(result['analysis'])
                preview = result['analysis'][:150]
                print(f'   Analysis length: {analysis_len} characters')
                print(f'   Preview: {preview}...')
            else:
                print(f'❌ Analysis failed: {result["error"]}')

        except Exception as e:
            print(f'❌ Test failed with exception: {e}')

if __name__ == '__main__':
    asyncio.run(test_ollama_vision())