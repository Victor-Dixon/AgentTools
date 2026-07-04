# Website Health Monitor

## Overview

The Website Health Monitor is a comprehensive CLI tool for continuous monitoring and health assessment of all websites in the Agent Cellphone V2 swarm ecosystem. It provides automated issue detection, performance tracking, SSL monitoring, and intelligent alerting with recovery suggestions.

## Features

- 🩺 **Continuous Monitoring** - 24/7 website health surveillance
- 🚨 **Intelligent Alerting** - Automated issue detection and notifications
- 📊 **Performance Tracking** - Response times, uptime, and degradation alerts
- 🔒 **SSL Certificate Monitoring** - Certificate validity and renewal tracking
- 🔍 **SEO Health Checks** - Search engine visibility and ranking monitoring
- 🔧 **Automated Recovery** - Intelligent suggestions for issue resolution
- 📈 **Historical Analysis** - Trend analysis and predictive alerting
- 📧 **Multi-channel Notifications** - Email, Slack, Discord, and webhook alerts

## Installation

### Prerequisites

- Python 3.11+
- Internet connectivity for website monitoring
- Email/SMTP configuration for alerts
- Optional: Slack/Discord webhooks for notifications

### Setup

1. **Install Dependencies**:
   ```bash
   pip install requests
   pip install aiohttp  # For async monitoring
   pip install python-dotenv
   pip install schedule  # For scheduled monitoring
   ```

2. **Configure Environment**:
   ```bash
   # Copy environment template
   cp .env.example .env

   # Configure monitoring settings
   MONITORING_INTERVAL=300  # 5 minutes
   ALERT_EMAIL_FROM=alerts@agent-cellphone.com
   ALERT_EMAIL_TO=admin@agent-cellphone.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password

   # Optional: Webhook notifications
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

3. **Initialize Monitoring Database**:
   ```bash
   python tools/monitoring/website_health_monitor.py --action init-db
   ```

## Usage

### Basic Commands

#### Start Continuous Monitoring
```bash
python tools/monitoring/website_health_monitor.py --action monitor
```

#### Check Single Website
```bash
python tools/monitoring/website_health_monitor.py \
  --action check \
  --site weareswarm.online
```

#### View Active Alerts
```bash
python tools/monitoring/website_health_monitor.py --action alerts
```

#### Generate Health Report
```bash
python tools/monitoring/website_health_monitor.py \
  --action report \
  --site all \
  --format html
```

### Advanced Usage

#### Custom Monitoring Interval
```bash
python tools/monitoring/website_health_monitor.py \
  --action monitor \
  --interval 600  # 10 minutes
```

#### Alert Threshold Configuration
```bash
python tools/monitoring/website_health_monitor.py \
  --action configure \
  --response-time-threshold 5000 \
  --error-rate-threshold 5
```

#### Historical Analysis
```bash
python tools/monitoring/website_health_monitor.py \
  --action history \
  --site weareswarm.online \
  --days 30
```

## Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--action` | Action: monitor, check, alerts, report, history, configure | Yes | - |
| `--site` | Target website or 'all' | No | all |
| `--interval` | Monitoring interval in seconds | No | 300 |
| `--format` | Report format: text, html, json | No | text |
| `--days` | Days of history for analysis | No | 7 |
| `--response-time-threshold` | Alert threshold in milliseconds | No | 3000 |
| `--error-rate-threshold` | Error rate alert threshold percentage | No | 2 |
| `--ssl-days-warning` | SSL expiration warning days | No | 30 |

## Health Checks Performed

### Core Health Checks

#### HTTP Response Monitoring
- **Status Code Validation**: 200, 301, 302 acceptable
- **Response Time Tracking**: < 3 seconds target, < 5 seconds warning
- **Content Verification**: Page loads successfully with expected content
- **Header Analysis**: Security headers, caching, compression

#### SSL Certificate Monitoring
- **Certificate Validity**: Expiration date tracking
- **Certificate Authority**: Valid CA verification
- **Domain Matching**: Certificate matches domain
- **Renewal Alerts**: 30-day warning, 7-day critical

#### DNS Resolution
- **A Record Validation**: IP address resolution
- **CNAME Verification**: Correct CNAME records (if applicable)
- **Propagation Monitoring**: DNS changes tracking
- **Nameserver Health**: Authoritative NS response

### Performance Monitoring

#### Load Time Analysis
- **First Contentful Paint**: < 1.5 seconds target
- **Largest Contentful Paint**: < 2.5 seconds target
- **Time to Interactive**: < 3.5 seconds target
- **Speed Index**: < 3 seconds target

#### Core Web Vitals
- **Cumulative Layout Shift**: < 0.1 score
- **First Input Delay**: < 100 milliseconds
- **Interaction to Next Paint**: < 200 milliseconds

### SEO Health Monitoring

#### Search Engine Visibility
- **Robots.txt Accessibility**: Proper robots.txt file
- **Sitemap.xml Validation**: Working XML sitemap
- **Meta Tags Presence**: Title, description, canonical tags
- **Structured Data**: Schema markup validation

#### Crawling & Indexing
- **HTTP Status for Search Engines**: No 4xx/5xx errors
- **Page Speed for Crawlers**: Reasonable crawl budget usage
- **Internal Linking**: Proper link structure
- **Mobile Friendliness**: Mobile-responsive design

### Security Monitoring

#### SSL/TLS Security
- **Protocol Version**: TLS 1.2+ requirement
- **Cipher Strength**: Strong cipher suites only
- **HSTS Headers**: HTTP Strict Transport Security
- **Certificate Transparency**: CT log monitoring

#### Web Application Security
- **XSS Protection**: XSS filter headers
- **CSRF Protection**: Anti-CSRF measures
- **Content Security Policy**: CSP header implementation
- **Secure Cookies**: Secure and HttpOnly flags

## Alert System

### Alert Severity Levels

#### Critical Alerts 🚨
- **Website Down**: HTTP 5xx errors or no response
- **SSL Certificate Expired**: Certificate no longer valid
- **DNS Failure**: Domain not resolving
- **Security Breach**: XSS/CSRF vulnerabilities detected

#### Warning Alerts ⚠️
- **High Response Time**: > 5 seconds consistently
- **SSL Expiring Soon**: < 30 days remaining
- **Performance Degradation**: 20%+ slowdown
- **SEO Issues**: Missing meta tags or broken links

#### Info Alerts ℹ️
- **Maintenance Windows**: Scheduled downtime
- **Performance Improvements**: Speed optimizations
- **SSL Renewed**: New certificate installed
- **Updates Applied**: Software/security updates

### Alert Channels

#### Email Notifications
```python
# Configure SMTP settings in .env
ALERT_EMAIL_FROM=alerts@agent-cellphone.com
ALERT_EMAIL_TO=admin@agent-cellphone.com,dev@agent-cellphone.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Slack Integration
```python
# Add webhook URL to .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Alert format:
🔴 CRITICAL: weareswarm.online is DOWN
Status: 500 Internal Server Error
Response Time: Timeout
Timestamp: 2024-01-12 14:30:00 UTC
Suggested Action: Check server logs and restart services
```

#### Discord Integration
```python
# Discord webhook for alerts
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
```

#### Webhook Integration
```python
# Generic webhook for custom integrations
WEBHOOK_URL=https://your-monitoring-system.com/webhook
WEBHOOK_SECRET=your_webhook_secret
```

## Monitoring Dashboard

### Real-time Status Dashboard

```
🌐 WEBSITE HEALTH MONITORING DASHBOARD
========================================

Last Updated: 2024-01-12 14:30:00 UTC
Monitoring Interval: 5 minutes

📊 OVERALL STATUS
─────────────────
Total Websites: 5
Healthy: 4 (80%)
Warning: 1 (20%)
Critical: 0 (0%)
Offline: 0 (0%)

🔴 CRITICAL ISSUES (0)
⚠️  WARNING ISSUES (1)
✅ HEALTHY SITES (4)

⚠️  WARNINGS
───────────
weareswarm.online
├── High Response Time: 4.2s (Target: <3.0s)
├── SSL Expires: 2024-02-15 (23 days remaining)
└── Core Web Vitals: CLS = 0.15 (Target: <0.1)

✅ HEALTHY SITES
───────────────
freerideinvestor.com     ✅ All checks passed
houstonsipqueen.com      ✅ All checks passed
prismblossom.online      ✅ All checks passed
southwestsecret.com      ✅ All checks passed

📈 PERFORMANCE SUMMARY (Last 24h)
─────────────────────────────────
Average Response Time: 1.8s
Uptime: 99.97%
SSL Certificates: 4/5 valid (>30 days)
Core Web Vitals: 3/5 passing
```

### Detailed Site Reports

#### Individual Site Health Report
```
🔍 DETAILED HEALTH REPORT - weareswarm.online
============================================

PERIOD: 2024-01-12 00:00:00 - 14:30:00 UTC

📊 RESPONSE TIME TREND
──────────────────────
Current: 4.2s ⚠️
Average (24h): 2.1s
Average (7d): 1.8s
Peak: 6.7s (2024-01-12 11:45:00)

🛡️  SSL CERTIFICATE STATUS
─────────────────────────
Status: ✅ Valid
Issuer: Let's Encrypt
Expires: 2024-02-15 (23 days)
Renewal: Automatic
SAN Domains: weareswarm.online, www.weareswarm.online

🔍 SEO HEALTH CHECKS
───────────────────
Meta Title: ✅ Present (58 chars)
Meta Description: ✅ Present (145 chars)
Canonical URL: ✅ Set
Robots.txt: ✅ Accessible
Sitemap.xml: ✅ Valid
Mobile Friendly: ✅ Yes

⚡ CORE WEB VITALS
─────────────────
Largest Contentful Paint: 2.8s ⚠️ (Target: <2.5s)
First Input Delay: 95ms ✅ (Target: <100ms)
Cumulative Layout Shift: 0.15 ⚠️ (Target: <0.1)

🔧 RECOMMENDED ACTIONS
─────────────────────
1. Optimize images and reduce page weight
2. Implement lazy loading for below-fold content
3. Review and optimize CSS delivery
4. Consider CDN for static assets
```

## Automated Recovery Suggestions

### Intelligent Recommendations

#### Performance Issues
- **High Response Time**: "Implement caching, optimize images, use CDN"
- **Slow LCP**: "Lazy load images, optimize font loading, remove unused CSS"
- **High CLS**: "Reserve space for dynamic content, avoid inserting content above fold"

#### SSL Issues
- **Certificate Expiring**: "Renew certificate automatically via ACME"
- **Weak Cipher**: "Update server configuration to use strong ciphers only"
- **Missing HSTS**: "Add HTTP Strict Transport Security header"

#### SEO Issues
- **Missing Meta Tags**: "Add title and description meta tags to all pages"
- **Broken Links**: "Run link checker and fix 404 errors"
- **Slow Mobile**: "Implement responsive design and optimize mobile assets"

### Automated Actions

#### SSL Certificate Renewal
```bash
# Automatic Let's Encrypt renewal
certbot renew --quiet

# Manual renewal if needed
certbot certonly --webroot -w /var/www/html -d weareswarm.online
```

#### Performance Optimization
```bash
# Enable compression
a2enmod deflate
systemctl restart apache2

# Configure caching headers
# Add to .htaccess or nginx config
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

## Historical Analysis & Trends

### Trend Analysis
```bash
# Analyze performance trends
python tools/monitoring/website_health_monitor.py \
  --action trends \
  --site weareswarm.online \
  --metric response_time \
  --days 30
```

### Predictive Alerting
- **Machine Learning**: Anomaly detection using historical data
- **Trend Analysis**: Predict performance degradation before it happens
- **Capacity Planning**: Forecast resource needs based on growth trends

### Reporting Features
```bash
# Monthly health report
python tools/monitoring/website_health_monitor.py \
  --action monthly-report \
  --site all \
  --format pdf \
  --email admin@agent-cellphone.com
```

## Configuration Management

### Website Configuration

The monitor automatically discovers and configures supported websites:

```python
WEBSITES = {
    "weareswarm.online": {
        "url": "https://weareswarm.online",
        "expected_status": 200,
        "timeout": 10,
        "ssl_required": True,
        "seo_checks": True,
        "performance_checks": True,
        "security_checks": True
    },
    # ... additional sites
}
```

### Alert Thresholds

```python
THRESHOLDS = {
    "response_time_warning": 3000,    # ms
    "response_time_critical": 5000,   # ms
    "ssl_warning_days": 30,
    "ssl_critical_days": 7,
    "error_rate_warning": 2,          # %
    "error_rate_critical": 5,         # %
    "uptime_warning": 99.5,           # %
    "uptime_critical": 99.0           # %
}
```

## Integration & Automation

### CI/CD Integration

```yaml
# .github/workflows/health-check.yml
name: Website Health Check
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Health Checks
        run: |
          python tools/monitoring/website_health_monitor.py --action check --site all
      - name: Send Alerts on Failure
        if: failure()
        run: |
          python tools/monitoring/website_health_monitor.py --action alerts --send-notifications
```

### Monitoring Dashboard Integration

```bash
# Export metrics for external monitoring
python tools/monitoring/website_health_monitor.py \
  --action export-metrics \
  --format prometheus \
  --output /var/lib/prometheus/metrics.txt
```

### Log Aggregation

```bash
# Send logs to centralized logging system
python tools/monitoring/website_health_monitor.py \
  --action export-logs \
  --format json \
  --destination syslog://logserver:514
```

## Security Considerations

### Access Control
- **API Authentication**: Secure API keys for external services
- **Network Security**: Monitor only allows outbound connections
- **Data Encryption**: Sensitive alert data encrypted in transit
- **Audit Logging**: All monitoring activities logged for compliance

### Data Privacy
- **PII Masking**: No personal data collected or stored
- **Minimal Data Retention**: Health data retained for 90 days only
- **Secure Storage**: Encrypted database for historical data
- **Compliance**: GDPR and privacy regulation compliant

## Troubleshooting

### Common Issues

#### Monitor Not Starting
```
❌ Failed to start monitoring: Permission denied
🔧 Solution: Check file permissions and user access rights
```

#### False Positive Alerts
```
⚠️  False alerts for temporary network issues
🔧 Solution: Adjust alert thresholds and add retry logic
```

#### High Resource Usage
```
❌ Monitor consuming too much CPU/memory
🔧 Solution: Reduce monitoring frequency or optimize check logic
```

### Debug Commands

```bash
# Test single check
python tools/monitoring/website_health_monitor.py \
  --action test-check \
  --site weareswarm.online

# Validate configuration
python tools/monitoring/website_health_monitor.py --action validate-config

# Reset monitoring state
python tools/monitoring/website_health_monitor.py --action reset
```

## Performance Optimization

### Monitoring Efficiency
- **Parallel Checks**: Multiple websites checked simultaneously
- **Smart Scheduling**: Different intervals for different check types
- **Caching**: Results cached to reduce redundant checks
- **Async Operations**: Non-blocking I/O for better performance

### Resource Usage
- **Memory**: <50MB during normal operation
- **CPU**: <5% average usage
- **Network**: <10MB per hour for all sites
- **Storage**: <100MB for 90 days of historical data

## Support & Maintenance

### Regular Maintenance

1. **SSL Certificate Updates** (Monthly)
   ```bash
   python tools/monitoring/website_health_monitor.py --action update-ssl-config
   ```

2. **Performance Tuning** (Weekly)
   ```bash
   python tools/monitoring/website_health_monitor.py --action optimize-checks
   ```

3. **Alert Threshold Review** (Monthly)
   ```bash
   python tools/monitoring/website_health_monitor.py --action review-thresholds
   ```

### Getting Help

- **Built-in Help**: `python tools/monitoring/website_health_monitor.py --help`
- **Configuration Guide**: Check inline documentation and comments
- **Logs**: Monitor `logs/monitoring/` for detailed information
- **Status Checks**: Use `--action status` for current system state

---

*Website Health Monitor - Agent Cellphone V2 Swarm Infrastructure*

*V2 Compliant: Continuous Monitoring, Intelligent Alerting, Automated Recovery*