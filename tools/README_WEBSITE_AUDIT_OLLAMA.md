# Website Audit Tool with Ollama LLM

A powerful website auditing tool that captures screenshots and analyzes them using local Ollama Large Language Models for comprehensive website analysis.

## Features

- **Screenshot Capture**: Uses Playwright (primary) or Selenium (fallback) for high-quality website screenshots
- **Local LLM Analysis**: Leverages Ollama models (like LLaVA) for intelligent analysis without API costs
- **Comprehensive Audits**: Design, UX, SEO, and performance analysis in one tool
- **Batch Processing**: Audit multiple websites simultaneously
- **MCP Integration**: Available as a Model Context Protocol server for Cursor IDE integration

## Installation

### Prerequisites

1. **Python Dependencies**:
```bash
pip install ollama playwright pillow requests httpx
playwright install chromium
```

2. **Ollama Setup**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull vision-capable models
ollama pull llava          # Primary model for vision analysis
ollama pull bakllava       # Alternative vision model
ollama pull moondream      # Lightweight vision model
```

3. **Optional - Selenium Setup**:
```bash
pip install selenium webdriver-manager
# ChromeDriver will be managed automatically
```

## Usage

### Command Line

#### Single Website Audit
```bash
python tools/website_audit_ollama.py https://example.com --output audit_results.json
```

#### Batch Website Audit
```bash
python tools/website_audit_ollama.py --batch https://site1.com https://site2.com https://site3.com --output batch_results.json
```

#### Custom Model
```bash
python tools/website_audit_ollama.py https://example.com --model bakllava
```

### MCP Server Integration

The tool is available as an MCP server for Cursor IDE integration:

```json
{
  "mcpServers": {
    "website-audit": {
      "command": "python",
      "args": ["mcp_servers/website_audit_server.py"],
      "description": "🔍 Website auditing with Ollama LLM screenshot analysis"
    }
  }
}
```

### MCP Functions

#### `audit_website_full(url, model)`
Perform comprehensive website audit with all analysis types.

#### `audit_website_batch(urls, model)`
Audit multiple websites in batch.

#### `analyze_website_design(url, model)`
Focus analysis on design quality.

#### `analyze_website_ux(url, model)`
Focus analysis on user experience.

#### `analyze_website_seo(url, model)`
Focus analysis on SEO and content optimization.

#### `check_ollama_status()`
Check available Ollama models and connection status.

## Analysis Types

### 1. Design Audit
- Visual design and aesthetics
- Color scheme and branding
- Typography and readability
- Layout and composition
- Mobile responsiveness
- Overall design score (1-10)

### 2. UX Audit
- Navigation clarity
- Call-to-action effectiveness
- Content organization
- Accessibility considerations
- Mobile UX indicators
- Overall UX score (1-10)

### 3. SEO & Content Audit
- Title and heading structure
- Meta elements optimization
- Content quality signals
- Internal linking hints
- Social sharing elements
- Overall SEO score (1-10)

### 4. Performance Audit
- Image optimization indicators
- Resource loading efficiency
- Caching and CDN usage
- JavaScript/CSS optimization
- Core Web Vitals compliance
- Overall performance score (1-10)

## Output Format

### Single Website Audit
```json
{
  "url": "https://example.com",
  "timestamp": 1703123456.789,
  "screenshot": "/path/to/screenshots/example_com_1703123456.png",
  "analyses": {
    "design_audit": "Detailed design analysis...",
    "ux_audit": "Comprehensive UX evaluation...",
    "seo_content_audit": "SEO readiness assessment...",
    "performance_audit": "Performance optimization analysis..."
  },
  "recommendations": [
    "[DESIGN] Consider improving color contrast ratios...",
    "[UX] Add more prominent call-to-action buttons...",
    "[SEO] Optimize title tag for better keyword targeting...",
    "[PERFORMANCE] Implement image lazy loading..."
  ],
  "scores": {
    "design_audit": "Design Score: 8/10 - Modern and clean design...",
    "ux_audit": "UX Score: 7/10 - Good navigation but could improve CTAs...",
    "seo_content_audit": "SEO Score: 6/10 - Title optimization needed...",
    "performance_audit": "Performance Score: 8/10 - Good optimization practices..."
  },
  "errors": []
}
```

### Batch Audit Summary
```json
{
  "batch_info": {
    "total_urls": 3,
    "timestamp": 1703123456.789,
    "model": "llava"
  },
  "summary": {
    "total_sites": 3,
    "successful_audits": 3,
    "failed_audits": 0,
    "success_rate": 100.0,
    "average_scores": {
      "design_audit": 7.7,
      "ux_audit": 7.3,
      "seo_content_audit": 6.7,
      "performance_audit": 8.0
    }
  },
  "audits": {
    "https://site1.com": { /* full audit results */ },
    "https://site2.com": { /* full audit results */ },
    "https://site3.com": { /* full audit results */ }
  }
}
```

## Configuration

### Screenshot Settings
- **Resolution**: 1920x1080 (full HD)
- **Format**: PNG with transparency
- **Wait Time**: 3 seconds for dynamic content loading
- **Full Page**: Captures entire scrollable content

### Ollama Model Selection
- **Primary**: `llava` - Best balance of speed and accuracy
- **Alternative**: `bakllava` - Higher accuracy for detailed analysis
- **Lightweight**: `moondream` - Faster for basic audits

## Troubleshooting

### Common Issues

#### Ollama Connection Failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify model is available
ollama pull llava
```

#### Screenshot Capture Failed
- **Playwright fallback**: Automatically falls back to Selenium
- **Network issues**: Check internet connection and website availability
- **Browser issues**: Ensure Playwright browsers are installed

#### Memory Issues with Large Screenshots
- Reduce viewport size in the code
- Use Selenium fallback for smaller screenshots
- Process one website at a time for batch audits

### Performance Optimization

#### For Large Batch Audits
```bash
# Process in smaller batches
python tools/website_audit_ollama.py --batch site1.com site2.com site3.com

# Use faster model for basic audits
python tools/website_audit_ollama.py --batch sites.txt --model moondream
```

#### For Quick Analysis
```python
# Use specific analysis type instead of comprehensive
from tools.website_audit_ollama import WebsiteAuditOllama
import asyncio

auditor = WebsiteAuditOllama()
result = asyncio.run(auditor.analyze_website_design("https://example.com"))
```

## Integration Examples

### Cursor IDE MCP Integration
```json
{
  "mcpServers": {
    "website-audit": {
      "command": "python",
      "args": ["mcp_servers/website_audit_server.py"]
    }
  }
}
```

### Python Script Integration
```python
import asyncio
from tools.website_audit_ollama import WebsiteAuditOllama

async def audit_my_sites():
    auditor = WebsiteAuditOllama(model_name="llava")

    # Single site audit
    result = await auditor.audit_website_comprehensive("https://mysite.com")

    # Batch audit
    sites = ["https://site1.com", "https://site2.com", "https://site3.com"]
    batch_result = await auditor.audit_multiple_websites(sites)

    return result, batch_result

# Run the audit
results = asyncio.run(audit_my_sites())
```

## Contributing

### Adding New Analysis Types
1. Add new analysis method to `WebsiteAuditOllama` class
2. Create specific prompt for the analysis type
3. Add to `audit_website_comprehensive()` method
4. Update MCP server with new function

### Improving Prompts
Analysis quality depends on the prompts given to the LLM. Refine prompts based on:
- Analysis accuracy vs. hallucination
- Specificity of recommendations
- Actionability of suggestions
- Scoring consistency

## License

This tool is part of the agent-tools suite. See main project LICENSE for details.

## Support

For issues with:
- **Ollama models**: Check Ollama documentation
- **Screenshot capture**: Verify Playwright/Selenium installation
- **MCP integration**: Check Cursor IDE MCP configuration
- **Analysis quality**: Review and refine analysis prompts