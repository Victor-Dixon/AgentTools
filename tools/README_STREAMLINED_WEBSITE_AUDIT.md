# Streamlined Website Audit CLI Documentation

## Overview

The Streamlined Website Audit tool (`streamlined_website_audit.py`) provides comprehensive website analysis combining manual expertise with optional AI-powered insights. Designed by Agent-2, it focuses on actionable recommendations for website optimization.

## Features

- **Manual Analysis**: Structured content analysis without AI dependencies
- **AI Enhancement**: Optional Ollama integration for deeper insights
- **SEO Assessment**: Comprehensive on-page SEO evaluation
- **Performance Metrics**: Core Web Vitals and loading analysis
- **Security Checks**: Basic security header validation
- **Content Quality**: Readability and structure assessment
- **Mobile Optimization**: Responsive design validation

## Installation & Setup

### Prerequisites
```bash
pip install ollama  # Optional, for AI-enhanced analysis
```

### Basic Setup
```bash
cd /path/to/agent-tools
# Tool is ready to use - no additional configuration required
```

## Command Line Usage

### Basic Audit
```bash
python tools/streamlined_website_audit.py <url>
```

### AI-Enhanced Audit
```bash
python tools/streamlined_website_audit.py <url> --ollama
```

### JSON Output
```bash
python tools/streamlined_website_audit.py <url> --json --output results.json
```

### Disable AI Analysis
```bash
python tools/streamlined_website_audit.py <url> --no-ollama
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | Target website URL (required) | - |
| `--ollama` | Enable Ollama AI analysis | Auto-detect |
| `--no-ollama` | Disable Ollama analysis | - |
| `--json` | Output results in JSON format | Pretty print |
| `--output FILE` | Save results to file | Console output |
| `--verbose` | Show detailed analysis steps | Normal output |
| `--timeout SECONDS` | Request timeout | 15 seconds |

## Analysis Categories

### SEO Analysis
- **Title Tags**: Length, uniqueness, keyword optimization
- **Meta Descriptions**: Length, relevance, call-to-action
- **Heading Structure**: H1-H6 hierarchy and distribution
- **Keyword Analysis**: Primary keywords and density
- **Internal Linking**: Link structure and navigation
- **Schema Markup**: Structured data implementation

### Technical Performance
- **Page Load Speed**: Response times and bottlenecks
- **Mobile Friendliness**: Responsive design validation
- **HTTPS Security**: SSL certificate and security headers
- **Core Web Vitals**: FID, LCP, CLS metrics
- **Resource Optimization**: Image compression, minification

### Content Quality
- **Readability Scores**: Flesch-Kincaid analysis
- **Content Structure**: Logical flow and organization
- **Multimedia Optimization**: Alt tags, captions, transcripts
- **User Experience**: Navigation ease and accessibility

### AI-Enhanced Insights (Optional)
- **Content Recommendations**: AI-powered improvement suggestions
- **Competitor Analysis**: Market positioning insights
- **Trend Analysis**: Industry benchmark comparisons
- **Conversion Optimization**: Funnel improvement recommendations

## Output Formats

### Standard Output (Default)
```
🔍 Agent-2 Website Auditor (Ollama: ✅)

📊 AUDIT RESULTS: example.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SEO SCORE: 8.5/10
📈 PERF SCORE: 7.2/10
📝 CONTENT SCORE: 9.1/10
🔒 SECURITY SCORE: 8.8/10

📋 KEY FINDINGS:
├── ✅ Title tag optimized (45 chars)
├── ⚠️  Meta description could be more compelling
├── ✅ Mobile-friendly design detected
└── ✅ SSL certificate valid

💡 RECOMMENDATIONS:
├── Optimize meta description for better CTR
├── Consider adding schema markup
└── Improve image alt tags
```

### JSON Output
```bash
python tools/streamlined_website_audit.py example.com --json
```
```json
{
  "url": "example.com",
  "timestamp": "2026-01-12T19:45:00Z",
  "scores": {
    "seo": 8.5,
    "performance": 7.2,
    "content": 9.1,
    "security": 8.8
  },
  "findings": [
    {"type": "success", "category": "seo", "message": "Title tag optimized (45 chars)"},
    {"type": "warning", "category": "seo", "message": "Meta description could be more compelling"}
  ],
  "recommendations": [
    "Optimize meta description for better CTR",
    "Consider adding schema markup"
  ],
  "ollama_insights": {
    "content_quality": "High-quality, well-structured content",
    "improvement_suggestions": ["Add more specific keywords", "Improve internal linking"]
  }
}
```

## Integration Examples

### Batch Processing
```bash
# Audit multiple sites
echo -e "site1.com\nsite2.com\nsite3.com" | \
while read url; do
    echo "Auditing $url..."
    python tools/streamlined_website_audit.py $url --json --output "audit_$url.json"
done
```

### CI/CD Integration
```yaml
# .github/workflows/website-audit.yml
name: Website Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Website Audit
        run: |
          python tools/streamlined_website_audit.py ${{ secrets.WEBSITE_URL }} --json --output audit-results.json
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: audit-results
          path: audit-results.json
```

### Monitoring Script
```bash
#!/bin/bash
URL="$1"
THRESHOLD="${2:-7.0}"

SCORE=$(python tools/streamlined_website_audit.py "$URL" --json | jq '.scores.seo')

if (( $(echo "$SCORE < $THRESHOLD" | bc -l) )); then
    echo "⚠️  SEO score ($SCORE) below threshold ($THRESHOLD)"
    exit 1
else
    echo "✅ SEO score ($SCORE) meets threshold ($THRESHOLD)"
fi
```

## Scoring System

### Score Ranges
- **9.0-10.0**: Excellent - Industry leading
- **7.0-8.9**: Good - Above average performance
- **5.0-6.9**: Average - Meets basic requirements
- **3.0-4.9**: Poor - Significant improvements needed
- **0.0-2.9**: Critical - Immediate attention required

### Category Weights
- **SEO**: 40% (Title, meta, keywords, structure)
- **Performance**: 30% (Speed, mobile, technical)
- **Content**: 20% (Quality, readability, engagement)
- **Security**: 10% (HTTPS, headers, certificates)

## Troubleshooting

### Common Issues

#### Ollama Not Available
```
🔍 Agent-2 Website Auditor (Ollama: ❌)
```
**Solution:** Install Ollama or use `--no-ollama` flag

#### Timeout Errors
```
Error: HTTP timeout after 15 seconds
```
**Solution:** Use `--timeout 30` for slower sites

#### SSL Certificate Issues
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution:** Check SSL certificate validity or use HTTP for testing

### Debug Mode
```bash
python tools/streamlined_website_audit.py example.com --verbose
```
Shows detailed analysis steps and intermediate results.

## Performance Considerations

### Resource Usage
- **Memory**: ~50-100MB per audit
- **Network**: 1-2 requests per audit
- **CPU**: Minimal (mostly I/O bound)
- **Time**: 10-30 seconds per site

### Optimization Tips
- Use `--no-ollama` for faster results
- Batch process during off-peak hours
- Cache results for repeated audits
- Use JSON output for programmatic processing

## Development

### Extending Analysis
```python
# Add custom analysis in analyze_content method
def analyze_custom_metric(self, html: str, url: str) -> Dict:
    # Your custom analysis logic
    return {"score": 8.5, "findings": [], "recommendations": []}
```

### Adding New Checks
```python
# Add to the analysis pipeline
custom_results = self.analyze_custom_metric(html, url)
results["custom"] = custom_results
```

## License & Credits

Created by Agent-2 for streamlined, reliable website auditing.
Combines manual analysis expertise with optional AI enhancement for comprehensive insights.