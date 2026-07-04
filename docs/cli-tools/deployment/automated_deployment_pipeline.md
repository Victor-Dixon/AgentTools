# Automated Deployment Pipeline

## Overview

The Automated Deployment Pipeline is a comprehensive CLI tool for managing multi-website deployment orchestration across the Agent Cellphone V2 swarm ecosystem. It provides automated deployment, health checking, backup/rollback capabilities, and deployment status tracking.

## Features

- 🚀 **Multi-website Orchestration** - Deploy to multiple websites simultaneously
- 🩺 **Pre-deployment Health Checks** - SSL, DNS, and HTTP validation
- 🔄 **Backup & Rollback** - Automatic backups with one-click rollback
- 📊 **Status Tracking** - Real-time deployment monitoring and reporting
- 🧪 **Testing Integration** - Automated testing before and after deployment
- 🔒 **Security Validation** - SSL certificate and security checks
- 📈 **Performance Monitoring** - Load time and SEO score tracking

## Installation

### Prerequisites

- Python 3.11+
- Git
- Access to website repositories
- SSH keys configured for deployment servers
- Environment variables configured

### Setup

1. **Clone repositories** (if not already done):
   ```bash
   # Ensure all website repositories are cloned locally
   git clone https://github.com/Agent-7/weareswarm.online.git
   git clone https://github.com/Agent-7/freerideinvestor.com.git
   # ... etc for all swarm websites
   ```

2. **Configure environment**:
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with deployment credentials
   DEPLOYMENT_USER=your_deployment_user
   DEPLOYMENT_KEY_PATH=/path/to/ssh/key
   WEBSITE_REPO_BASE=/path/to/website/repos
   ```

## Usage

### Basic Commands

#### Deploy Single Website
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action deploy
```

#### Deploy All Websites
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --action deploy \
  --site all
```

#### Health Check
```bash
# Check single website
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action health-check

# Check all websites
python tools/deployment/automated_deployment_pipeline.py \
  --action health-check \
  --site all
```

#### Rollback Deployment
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action rollback
```

### Advanced Usage

#### Custom Deployment Script
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action deploy \
  --script custom_deploy.sh
```

#### Skip Health Checks
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action deploy \
  --skip-health-checks
```

#### Dry Run
```bash
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action deploy \
  --dry-run
```

## Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--action` | Action to perform (deploy, health-check, rollback, status) | Yes | - |
| `--site` | Target website or 'all' | Yes | - |
| `--script` | Custom deployment script path | No | - |
| `--skip-health-checks` | Skip pre-deployment health checks | No | False |
| `--dry-run` | Show what would be done without executing | No | False |
| `--verbose` | Enable verbose logging | No | False |
| `--timeout` | Deployment timeout in seconds | No | 300 |

## Configuration

### Website Configuration

The tool automatically detects and configures supported websites:

- **weareswarm.online** - Swarm intelligence platform
- **freerideinvestor.com** - Investment education
- **houstonsipqueen.com** - Local business
- **prismblossom.online** - Creative services
- **southwestsecret.com** - Travel/tourism

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEPLOYMENT_USER` | SSH deployment user | Yes |
| `DEPLOYMENT_KEY_PATH` | Path to SSH private key | Yes |
| `WEBSITE_REPO_BASE` | Base path for website repositories | Yes |
| `DEPLOYMENT_TIMEOUT` | Default deployment timeout | No |

## Health Checks

### Pre-deployment Checks

1. **SSL Certificate Validation**
   - Certificate validity (30+ days remaining)
   - Certificate authority verification
   - Domain matching

2. **DNS Resolution**
   - A record existence
   - CNAME record validation (if applicable)
   - DNS propagation check

3. **HTTP Response Validation**
   - Status code 200
   - Response time < 5 seconds
   - Content-type validation

4. **SEO Basics**
   - Meta title presence
   - Meta description length
   - H1 tag validation

### Post-deployment Checks

1. **Load Time Monitoring**
   - First contentful paint < 3 seconds
   - Time to interactive < 5 seconds

2. **Functionality Testing**
   - Contact forms operational
   - Navigation links working
   - Core functionality verification

## Backup & Rollback

### Automatic Backups

- **Pre-deployment**: Full website backup created automatically
- **Naming Convention**: `{site}_backup_{timestamp}`
- **Retention**: Last 5 backups maintained
- **Compression**: Automatic gzip compression

### Rollback Process

1. **Identify Target Backup**
   ```bash
   # List available backups
   ls backups/weareswarm.online_backup_*
   ```

2. **Execute Rollback**
   ```bash
   python tools/deployment/automated_deployment_pipeline.py \
     --site weareswarm.online \
     --action rollback
   ```

3. **Verification**
   - Health checks run automatically
   - Manual verification recommended
   - Rollback logged for audit trail

## Monitoring & Reporting

### Real-time Status

```bash
# Check deployment status
python tools/deployment/automated_deployment_pipeline.py --action status

# Output example:
# 🌐 Deployment Status Report
# ===============================
# weareswarm.online: ✅ DEPLOYED (2024-01-12 10:30:00)
# freerideinvestor.com: ⏳ DEPLOYING (45% complete)
# houstonsipqueen.com: ❌ FAILED (SSL certificate expired)
# prismblossom.online: ✅ HEALTHY
# southwestsecret.com: 🔄 ROLLBACK (Restoring backup)
```

### Deployment Logs

- **Location**: `logs/deployments/`
- **Format**: `{site}_{timestamp}.log`
- **Retention**: 30 days
- **Content**: Full deployment transcript

## Error Handling

### Common Issues

#### SSL Certificate Expired
```
❌ SSL certificate expired for weareswarm.online
🔧 Solution: Renew certificate through hosting provider
```

#### DNS Resolution Failed
```
❌ DNS resolution failed for freerideinvestor.com
🔧 Solution: Check DNS settings and propagation (may take 24-48 hours)
```

#### Deployment Timeout
```
❌ Deployment timeout for houstonsipqueen.com
🔧 Solution: Check server resources or increase timeout with --timeout option
```

### Troubleshooting Steps

1. **Check Logs**
   ```bash
   tail -f logs/deployments/weareswarm.online_20240112_103000.log
   ```

2. **Verify Environment**
   ```bash
   python tools/deployment/automated_deployment_pipeline.py --action verify-env
   ```

3. **Test Connectivity**
   ```bash
   ssh -i $DEPLOYMENT_KEY_PATH $DEPLOYMENT_USER@target-server
   ```

## Examples

### Complete Deployment Workflow

```bash
# 1. Health check all sites
python tools/deployment/automated_deployment_pipeline.py \
  --action health-check \
  --site all

# 2. Deploy single site
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action deploy

# 3. Monitor deployment status
python tools/deployment/automated_deployment_pipeline.py \
  --action status

# 4. Verify deployment success
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action health-check
```

### Emergency Rollback

```bash
# Immediate rollback if issues detected
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action rollback

# Verify rollback success
python tools/deployment/automated_deployment_pipeline.py \
  --site weareswarm.online \
  --action health-check
```

## Integration

### CI/CD Integration

The deployment pipeline integrates with CI/CD systems:

```yaml
# .github/workflows/deploy.yml
name: Deploy Website
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: |
          python tools/deployment/automated_deployment_pipeline.py \
            --site ${{ github.event.repository.name }} \
            --action deploy
```

### Monitoring Integration

Integrates with website health monitoring:

```bash
# Schedule regular health checks
crontab -e
# Add: 0 */4 * * * python tools/deployment/automated_deployment_pipeline.py --action health-check --site all
```

## Security

### Access Control

- SSH key-based authentication only
- No password authentication allowed
- Key rotation every 90 days
- Access logged and monitored

### Data Protection

- Backups encrypted at rest
- Sensitive data masked in logs
- SSL/TLS for all communications
- Compliance with security standards

## Performance

### Benchmarks

- **Single Site Deployment**: < 5 minutes
- **Multi-site Deployment**: < 15 minutes
- **Health Check**: < 30 seconds per site
- **Rollback**: < 3 minutes

### Resource Usage

- **Memory**: < 100MB during operation
- **CPU**: < 20% during deployment
- **Network**: < 50MB per deployment
- **Storage**: < 500MB for backups/logs

## Support

### Getting Help

- **Documentation**: This comprehensive guide
- **Logs**: Check `logs/deployments/` for detailed information
- **Status**: Use `--action status` for current deployment state
- **Health**: Use `--action health-check` for system diagnostics

### Common Support Scenarios

1. **Deployment Stuck**: Check server resources and network connectivity
2. **Health Check Failing**: Verify SSL certificates and DNS settings
3. **Rollback Issues**: Ensure backup integrity and server permissions
4. **Performance Issues**: Monitor server resources and optimize configurations

---

*Automated Deployment Pipeline - Agent Cellphone V2 Swarm Infrastructure*

*V2 Compliant: SOLID Architecture, Modular Design, Comprehensive Error Handling*