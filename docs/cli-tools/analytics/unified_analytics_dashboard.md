# Unified Analytics Dashboard

## Overview

The Unified Analytics Dashboard is a comprehensive CLI tool for aggregating, analyzing, and reporting website analytics across the entire Agent Cellphone V2 swarm ecosystem. It provides unified insights into performance, SEO, user behavior, and business metrics from multiple data sources.

## Features

- 📊 **Multi-Source Aggregation** - GA4, SEO tools, performance monitors
- 🎯 **Real-time Dashboards** - Live metrics and trend analysis
- 🔍 **SEO Analytics** - Keyword rankings, backlinks, content performance
- ⚡ **Performance Monitoring** - Load times, Core Web Vitals, user experience
- 📈 **Business Intelligence** - Conversion tracking, revenue analytics, ROI
- 🚨 **Alert System** - Automated anomaly detection and notifications
- 📋 **Automated Reporting** - Scheduled reports and executive summaries

## Installation

### Prerequisites

- Python 3.11+
- Google Analytics 4 API credentials
- SEO tool API keys (optional)
- Database access for metrics storage
- Email/Slack for alert notifications

### Setup

1. **Install Dependencies**:
   ```bash
   pip install google-analytics-data
   pip install requests
   pip install pandas
   pip install matplotlib
   ```

2. **Configure APIs**:
   ```bash
   # Set up Google Analytics 4
   export GA4_PROPERTY_ID="your_property_id"
   export GA4_CREDENTIALS_PATH="/path/to/credentials.json"

   # Optional: SEO tools
   export AHREFS_API_KEY="your_ahrefs_key"
   export SEMRUSH_API_KEY="your_semrush_key"
   export MOZ_API_KEY="your_moz_key"
   ```

3. **Initialize Database** (if using local storage):
   ```bash
   python tools/analytics/unified_analytics_dashboard.py --action init-db
   ```

## Usage

### Basic Commands

#### View Dashboard
```bash
python tools/analytics/unified_analytics_dashboard.py --action dashboard
```

#### Generate Site Report
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action report \
  --site weareswarm.online
```

#### Check Alerts
```bash
python tools/analytics/unified_analytics_dashboard.py --action alerts
```

### Advanced Usage

#### Custom Date Range
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action report \
  --site weareswarm.online \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

#### Export Data
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action export \
  --site all \
  --format csv \
  --output analytics_export.csv
```

#### Performance Analysis
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action performance \
  --site weareswarm.online \
  --metric core-web-vitals
```

## Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--action` | Action: dashboard, report, alerts, export, performance | Yes | - |
| `--site` | Target website or 'all' | No | all |
| `--start-date` | Start date (YYYY-MM-DD) | No | 30 days ago |
| `--end-date` | End date (YYYY-MM-DD) | No | today |
| `--format` | Export format: csv, json, pdf | No | csv |
| `--output` | Output file path | No | auto-generated |
| `--metric` | Specific metric to analyze | No | all |
| `--alert-threshold` | Alert sensitivity (low/medium/high) | No | medium |

## Dashboard Views

### Executive Summary Dashboard

```
🌐 UNIFIED ANALYTICS DASHBOARD - EXECUTIVE SUMMARY
==================================================

📊 OVERALL METRICS (Last 30 Days)
─────────────────────────────────
Total Page Views:      125,430 (+12% vs last month)
Total Unique Visitors:  45,890 (+8% vs last month)
Average Bounce Rate:   42.3% (-2.1% vs last month)
Conversion Rate:       3.2% (+0.5% vs last month)

🔝 TOP PERFORMING SITES
───────────────────────
1. weareswarm.online     - 45,230 views (36%)
2. freerideinvestor.com  - 32,450 views (26%)
3. prismblossom.online   - 28,900 views (23%)
4. houstonsipqueen.com   - 12,340 views (10%)
5. southwestsecret.com   - 6,510 views (5%)

🚨 ACTIVE ALERTS
────────────────
⚠️  weareswarm.online: High bounce rate (52.1% > 50%)
⚠️  freerideinvestor.com: Traffic decline (-15% this week)
✅ prismblossom.online: SEO score improved (+5 points)
```

### Site-Specific Reports

#### Traffic Analysis
```
📈 TRAFFIC ANALYSIS - weareswarm.online
=======================================

PERIOD: 2024-01-01 to 2024-01-31

SESSIONS BY SOURCE:
• Organic Search:  12,340 (45%)
• Direct:          8,920 (32%)
• Social Media:    4,560 (17%)
• Referral:        1,890 (7%)
• Email:           890 (3%)

TOP LANDING PAGES:
/blog/swarm-intelligence-guide  2,340 visits
/features                      1,890 visits
/pricing                       1,560 visits
/about                         1,230 visits

GEOGRAPHIC DISTRIBUTION:
• United States:  45%
• United Kingdom: 15%
• Canada:         12%
• Australia:      8%
• Germany:        6%
```

#### SEO Performance
```
🔍 SEO PERFORMANCE - weareswarm.online
=====================================

OVERALL SEO SCORE: 78/100 (+3 pts)

KEYWORD RANKINGS:
#1-10:     23 keywords
#11-50:    45 keywords
#51-100:   67 keywords

TOP KEYWORDS:
1. swarm intelligence        Position: 3  Volume: 2.4K
2. ai agent systems          Position: 5  Volume: 1.8K
3. multi-agent coordination  Position: 7  Volume: 1.2K
4. autonomous agents         Position: 9  Volume: 990

BACKLINK PROFILE:
Total Backlinks:     1,234
Domain Authority:   45
Referring Domains:  89
New Backlinks:      +12 this month
```

#### Performance Metrics
```
⚡ PERFORMANCE METRICS - weareswarm.online
========================================

CORE WEB VITALS (Lighthouse Score: 85)
─────────────────────────────────────
Largest Contentful Paint:  1.8s (Good)
First Input Delay:         95ms (Good)
Cumulative Layout Shift:   0.12 (Needs Improvement)

LOADING PERFORMANCE:
───────────────────
First Contentful Paint:  1.2s
Speed Index:              2.1s
Time to Interactive:      2.8s
Total Blocking Time:      120ms

MOBILE PERFORMANCE:
──────────────────
Mobile Score:            82/100
Mobile-friendly:         ✅ Yes
Responsive Design:       ✅ Yes
Touch Targets Adequate:  ✅ Yes
```

## Alert System

### Alert Types

#### Traffic Alerts
- **Sudden Traffic Spikes**: >50% increase in 24 hours
- **Traffic Declines**: >20% decrease in 7 days
- **Unusual Patterns**: Weekend traffic > weekday average

#### Performance Alerts
- **Load Time Degradation**: >20% increase in average load time
- **Error Rate Spikes**: >5% increase in 4xx/5xx errors
- **Core Web Vitals Regression**: Any metric moves from Good to Poor

#### SEO Alerts
- **Ranking Drops**: Keywords dropping >3 positions
- **Backlink Losses**: >10 backlinks lost in 24 hours
- **SEO Score Decline**: >5 point drop in overall score

### Alert Configuration

```bash
# Configure alert thresholds
python tools/analytics/unified_analytics_dashboard.py \
  --action configure-alerts \
  --traffic-spike-threshold 50 \
  --traffic-decline-threshold 20 \
  --performance-degradation-threshold 20
```

## Data Sources

### Primary Data Sources

1. **Google Analytics 4**
   - Traffic metrics and user behavior
   - Conversion tracking and e-commerce
   - Custom events and goals

2. **Google Search Console**
   - Search performance and impressions
   - Keyword rankings and click-through rates
   - Crawl errors and indexing status

3. **Performance Monitoring**
   - Core Web Vitals from Lighthouse
   - Real User Monitoring (RUM)
   - Synthetic monitoring from multiple locations

### Optional Data Sources

1. **SEO Tools Integration**
   - Ahrefs: Backlink analysis and keyword tracking
   - SEMrush: Competitive analysis and content marketing
   - Moz: Domain authority and page optimization

2. **Social Media Analytics**
   - Facebook Insights, Twitter Analytics
   - LinkedIn Campaign Manager
   - Instagram Business Analytics

3. **Business Intelligence**
   - Salesforce CRM data
   - Email marketing platform metrics
   - E-commerce platform sales data

## Export & Integration

### Export Formats

#### CSV Export
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action export \
  --site all \
  --format csv \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --output monthly_report.csv
```

#### JSON Export
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action export \
  --site weareswarm.online \
  --format json \
  --output site_analytics.json
```

#### PDF Reports
```bash
python tools/analytics/unified_analytics_dashboard.py \
  --action report \
  --site weareswarm.online \
  --format pdf \
  --output monthly_report.pdf
```

### API Integration

```python
from tools.analytics.unified_analytics_dashboard import UnifiedAnalyticsDashboard

# Initialize dashboard
dashboard = UnifiedAnalyticsDashboard()

# Get real-time metrics
metrics = dashboard.get_real_time_metrics('weareswarm.online')

# Generate custom report
report = dashboard.generate_custom_report(
    site='weareswarm.online',
    metrics=['page_views', 'bounce_rate', 'conversions'],
    date_range=('2024-01-01', '2024-01-31')
)

# Check for alerts
alerts = dashboard.get_active_alerts()
```

## Automation & Scheduling

### Cron-based Automation

```bash
# Daily dashboard update (6 AM)
0 6 * * * python tools/analytics/unified_analytics_dashboard.py --action dashboard > /var/log/analytics/daily_dashboard.log

# Weekly reports (Monday 9 AM)
0 9 * * 1 python tools/analytics/unified_analytics_dashboard.py --action report --site all --format pdf --output weekly_report.pdf

# Hourly alert checks
0 * * * * python tools/analytics/unified_analytics_dashboard.py --action alerts >> /var/log/analytics/alerts.log
```

### CI/CD Integration

```yaml
# .github/workflows/analytics.yml
name: Analytics Pipeline
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  analytics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Update Analytics
        run: |
          python tools/analytics/unified_analytics_dashboard.py --action update-data
      - name: Check Alerts
        run: |
          python tools/analytics/unified_analytics_dashboard.py --action alerts
      - name: Generate Reports
        run: |
          python tools/analytics/unified_analytics_dashboard.py --action report --site all --format pdf
```

## Security & Privacy

### Data Protection

- **PII Masking**: Personal identifiable information automatically masked
- **Secure Storage**: Encrypted database storage for sensitive metrics
- **Access Control**: Role-based access to analytics data
- **Audit Logging**: All data access and modifications logged

### API Security

- **OAuth 2.0**: Secure authentication for external APIs
- **Rate Limiting**: API call limits to prevent abuse
- **Token Rotation**: Automatic refresh of API tokens
- **HTTPS Only**: All external communications encrypted

## Troubleshooting

### Common Issues

#### Data Not Loading
```
❌ Failed to fetch GA4 data: Invalid credentials
🔧 Solution: Verify GA4 credentials and property ID
```

#### Missing Metrics
```
⚠️  Warning: SEO data unavailable for weareswarm.online
🔧 Solution: Configure SEO API keys or check service status
```

#### Performance Issues
```
❌ Dashboard loading slow (>30 seconds)
🔧 Solution: Check database performance and API rate limits
```

### Debug Commands

```bash
# Test API connectivity
python tools/analytics/unified_analytics_dashboard.py --action test-apis

# Validate configuration
python tools/analytics/unified_analytics_dashboard.py --action validate-config

# Clear cache and refresh data
python tools/analytics/unified_analytics_dashboard.py --action clear-cache
```

## Performance Optimization

### Caching Strategy

- **Data Caching**: 1-hour cache for real-time metrics
- **Report Caching**: 24-hour cache for historical reports
- **API Response Caching**: Intelligent caching based on data freshness

### Query Optimization

- **Batch API Calls**: Multiple metrics fetched in single requests
- **Incremental Updates**: Only changed data refreshed
- **Parallel Processing**: Multiple sites processed simultaneously

### Resource Usage

- **Memory**: <200MB during normal operation
- **CPU**: <30% during report generation
- **Storage**: <1GB for 1 year of historical data
- **Network**: <100MB per daily update cycle

## Support & Maintenance

### Regular Maintenance Tasks

1. **API Token Rotation** (Monthly)
   ```bash
   python tools/analytics/unified_analytics_dashboard.py --action rotate-tokens
   ```

2. **Data Cleanup** (Weekly)
   ```bash
   python tools/analytics/unified_analytics_dashboard.py --action cleanup-data --older-than 90
   ```

3. **Performance Tuning** (Monthly)
   ```bash
   python tools/analytics/unified_analytics_dashboard.py --action optimize-db
   ```

### Getting Help

- **Command Help**: `python tools/analytics/unified_analytics_dashboard.py --help`
- **Configuration Guide**: Check inline documentation
- **API Documentation**: Visit Google Analytics and SEO tool documentation
- **Logs**: Check `logs/analytics/` for detailed error information

---

*Unified Analytics Dashboard - Agent Cellphone V2 Swarm Intelligence*

*V2 Compliant: Comprehensive Data Aggregation, Real-time Monitoring, Automated Alerting*