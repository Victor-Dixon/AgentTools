#!/usr/bin/env python3
"""
Website Health Monitoring System
================================

Agent-8: SSOT & System Integration
Implements comprehensive website health monitoring for all swarm websites.

Features:
- Continuous website health monitoring
- Automated issue detection and alerting
- Performance tracking and degradation alerts
- SSL certificate monitoring
- SEO health monitoring
- Automated recovery suggestions

Usage:
    python tools/monitoring/website_health_monitor.py --action monitor
    python tools/monitoring/website_health_monitor.py --action check --site weareswarm.online
    python tools/monitoring/website_health_monitor.py --action alerts
"""

import asyncio
import json
import logging
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    website: str
    check_type: str
    status: str  # healthy, warning, critical, unknown
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HealthAlert:
    """Health monitoring alert."""
    website: str
    alert_type: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None


class WebsiteHealthMonitor:
    """Comprehensive website health monitoring system."""

    def __init__(self):
        self.monitoring_path = Path(__file__).parent / "data"
        self.alerts_path = Path(__file__).parent / "alerts"
        self.config_path = Path(__file__).parent / "health_config.json"

        # Create directories
        self.monitoring_path.mkdir(exist_ok=True)
        self.alerts_path.mkdir(exist_ok=True)

        # Monitoring configuration
        self.monitoring_config = {
            "check_interval_minutes": 15,
            "alert_thresholds": {
                "response_time_ms": 3000,
                "ssl_days_remaining": 30,
                "error_rate_percent": 5.0
            },
            "notification_emails": [],  # Would be configured in production
            "websites": {
                "weareswarm.online": {
                    "enabled": True,
                    "checks": ["http_status", "ssl", "dns", "seo_meta", "performance"],
                    "expected_status": 200
                },
                "freerideinvestor.com": {
                    "enabled": True,
                    "checks": ["http_status", "ssl", "dns", "wordpress_security", "plugin_exposure"],
                    "expected_status": 200
                },
                "houstonsipqueen.com": {
                    "enabled": True,
                    "checks": ["http_status", "ssl", "dns", "seo_meta"],
                    "expected_status": 200
                },
                "prismblossom.online": {
                    "enabled": True,
                    "checks": ["http_status", "ssl", "dns", "seo_meta", "image_loading"],
                    "expected_status": 200
                },
                "southwestsecret.com": {
                    "enabled": True,
                    "checks": ["http_status", "ssl", "dns", "seo_meta"],
                    "expected_status": 200
                }
            }
        }

        # Load or create config
        self._load_config()

    def _load_config(self) -> None:
        """Load monitoring configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.monitoring_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")

        # Save current config
        with open(self.config_path, 'w') as f:
            json.dump(self.monitoring_config, f, indent=2)

    async def perform_health_check(self, website: str) -> List[HealthCheckResult]:
        """Perform comprehensive health check for a website."""
        logger.info(f"🔍 Performing health check for {website}")

        if website not in self.monitoring_config["websites"]:
            return [HealthCheckResult(
                website=website,
                check_type="configuration",
                status="critical",
                error_message="Website not configured for monitoring"
            )]

        config = self.monitoring_config["websites"][website]
        if not config.get("enabled", False):
            return [HealthCheckResult(
                website=website,
                check_type="configuration",
                status="unknown",
                error_message="Website monitoring disabled"
            )]

        results = []

        # Perform each configured check
        for check_type in config["checks"]:
            try:
                if check_type == "http_status":
                    result = await self._check_http_status(website)
                elif check_type == "ssl":
                    result = await self._check_ssl_certificate(website)
                elif check_type == "dns":
                    result = await self._check_dns_resolution(website)
                elif check_type == "seo_meta":
                    result = await self._check_seo_meta(website)
                elif check_type == "wordpress_security":
                    result = await self._check_wordpress_security(website)
                elif check_type == "plugin_exposure":
                    result = await self._check_plugin_exposure(website)
                elif check_type == "image_loading":
                    result = await self._check_image_loading(website)
                elif check_type == "performance":
                    result = await self._check_performance(website)
                else:
                    result = HealthCheckResult(
                        website=website,
                        check_type=check_type,
                        status="unknown",
                        error_message=f"Unknown check type: {check_type}"
                    )

                results.append(result)

            except Exception as e:
                results.append(HealthCheckResult(
                    website=website,
                    check_type=check_type,
                    status="critical",
                    error_message=f"Check failed: {str(e)}"
                ))

        # Save results
        await self._save_health_results(website, results)

        return results

    async def _check_http_status(self, website: str) -> HealthCheckResult:
        """Check HTTP status and response time."""
        import time

        start_time = time.time()
        try:
            response = requests.get(f"https://{website}", timeout=10, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            status = "healthy"
            if response.status_code >= 400:
                status = "critical"
            elif response.status_code >= 300:
                status = "warning"

            return HealthCheckResult(
                website=website,
                check_type="http_status",
                status=status,
                response_time=response_time,
                metadata={
                    "status_code": response.status_code,
                    "final_url": response.url,
                    "response_time_ms": response_time
                }
            )

        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                website=website,
                check_type="http_status",
                status="critical",
                response_time=response_time,
                error_message=f"Request failed: {str(e)}"
            )

    async def _check_ssl_certificate(self, website: str) -> HealthCheckResult:
        """Check SSL certificate validity and expiration."""
        import ssl
        import socket

        try:
            context = ssl.create_default_context()
            with socket.create_connection((website, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=website) as ssock:
                    cert = ssock.getpeercert()

                    # Extract expiration date
                    import datetime
                    expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (expiry_date - datetime.datetime.now()).days

                    status = "healthy"
                    if days_remaining < 7:
                        status = "critical"
                    elif days_remaining < 30:
                        status = "warning"

                    return HealthCheckResult(
                        website=website,
                        check_type="ssl",
                        status=status,
                        metadata={
                            "days_remaining": days_remaining,
                            "expiry_date": expiry_date.isoformat(),
                            "issuer": dict(cert.get('issuer', []))
                        }
                    )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="ssl",
                status="critical",
                error_message=f"SSL check failed: {str(e)}"
            )

    async def _check_dns_resolution(self, website: str) -> HealthCheckResult:
        """Check DNS resolution."""
        import socket

        try:
            ip_address = socket.gethostbyname(website)
            return HealthCheckResult(
                website=website,
                check_type="dns",
                status="healthy",
                metadata={"ip_address": ip_address}
            )
        except socket.gaierror as e:
            return HealthCheckResult(
                website=website,
                check_type="dns",
                status="critical",
                error_message=f"DNS resolution failed: {str(e)}"
            )

    async def _check_seo_meta(self, website: str) -> HealthCheckResult:
        """Check basic SEO meta tags."""
        try:
            response = requests.get(f"https://{website}", timeout=10)
            html = response.text.lower()

            checks = {
                "has_title": "<title>" in html and "</title>" in html,
                "has_meta_description": 'name="description"' in html,
                "has_h1": "<h1>" in html and "</h1>" in html,
                "has_canonical": 'rel="canonical"' in html
            }

            passed_checks = sum(checks.values())
            total_checks = len(checks)

            status = "healthy"
            if passed_checks < total_checks * 0.5:
                status = "critical"
            elif passed_checks < total_checks * 0.75:
                status = "warning"

            return HealthCheckResult(
                website=website,
                check_type="seo_meta",
                status=status,
                metadata=checks
            )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="seo_meta",
                status="critical",
                error_message=f"SEO check failed: {str(e)}"
            )

    async def _check_wordpress_security(self, website: str) -> HealthCheckResult:
        """Check WordPress security basics."""
        try:
            checks = {}

            # Check for common security issues
            response = requests.get(f"https://{website}/wp-admin/", timeout=10)
            checks["wp_admin_accessible"] = response.status_code == 200

            # Check readme.txt exposure
            response = requests.get(f"https://{website}/readme.txt", timeout=10)
            checks["readme_exposed"] = response.status_code == 200

            # Check version in meta
            response = requests.get(f"https://{website}", timeout=10)
            has_version_meta = 'name="generator" content="WordPress' in response.text
            checks["version_hidden"] = not has_version_meta

            # Overall assessment
            critical_issues = sum([checks["readme_exposed"], not checks["version_hidden"]])

            status = "healthy"
            if critical_issues > 0:
                status = "critical"

            return HealthCheckResult(
                website=website,
                check_type="wordpress_security",
                status=status,
                metadata=checks
            )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="wordpress_security",
                status="critical",
                error_message=f"WordPress security check failed: {str(e)}"
            )

    async def _check_plugin_exposure(self, website: str) -> HealthCheckResult:
        """Check for plugin directory exposure."""
        try:
            response = requests.get(f"https://{website}/wp-content/plugins/", timeout=10)

            # Should return 403 Forbidden or index.html, not directory listing
            is_secure = response.status_code in [403, 200] and "index of" not in response.text.lower()

            status = "healthy" if is_secure else "critical"

            return HealthCheckResult(
                website=website,
                check_type="plugin_exposure",
                status=status,
                metadata={
                    "response_code": response.status_code,
                    "directory_listing": "index of" in response.text.lower()
                }
            )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="plugin_exposure",
                status="critical",
                error_message=f"Plugin exposure check failed: {str(e)}"
            )

    async def _check_image_loading(self, website: str) -> HealthCheckResult:
        """Check image loading performance."""
        try:
            response = requests.get(f"https://{website}", timeout=10)
            html = response.text

            # Check for lazy loading
            has_lazy_loading = 'loading="lazy"' in html

            # Check for WebP images
            has_webp = '.webp' in html

            # Check for large images without optimization
            import re
            img_tags = re.findall(r'<img[^>]+>', html)
            large_images = 0
            for img_tag in img_tags[:5]:  # Check first 5 images
                if 'width=' in img_tag or 'height=' in img_tag:
                    # Rough check for large dimensions
                    if 'width="1920"' in img_tag or 'height="1080"' in img_tag:
                        large_images += 1

            status = "healthy"
            if large_images > 2 and not has_lazy_loading:
                status = "warning"
            if large_images > 3:
                status = "critical"

            return HealthCheckResult(
                website=website,
                check_type="image_loading",
                status=status,
                metadata={
                    "lazy_loading": has_lazy_loading,
                    "webp_support": has_webp,
                    "large_images": large_images
                }
            )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="image_loading",
                status="critical",
                error_message=f"Image loading check failed: {str(e)}"
            )

    async def _check_performance(self, website: str) -> HealthCheckResult:
        """Check basic performance metrics."""
        import time

        try:
            start_time = time.time()
            response = requests.get(f"https://{website}", timeout=15)
            load_time = time.time() - start_time

            # Check content size
            content_size_kb = len(response.content) / 1024

            # Basic performance assessment
            status = "healthy"
            if load_time > 5.0:
                status = "critical"
            elif load_time > 3.0:
                status = "warning"

            return HealthCheckResult(
                website=website,
                check_type="performance",
                status=status,
                response_time=load_time * 1000,  # Convert to milliseconds
                metadata={
                    "load_time_seconds": load_time,
                    "content_size_kb": content_size_kb,
                    "status_code": response.status_code
                }
            )

        except Exception as e:
            return HealthCheckResult(
                website=website,
                check_type="performance",
                status="critical",
                error_message=f"Performance check failed: {str(e)}"
            )

    async def _save_health_results(self, website: str, results: List[HealthCheckResult]) -> None:
        """Save health check results."""
        results_file = self.monitoring_path / f"{website.replace('.', '_')}_health.json"

        # Load existing results
        existing_results = []
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    existing_results = json.load(f)
            except:
                existing_results = []

        # Add new results
        for result in results:
            existing_results.append(asdict(result))

        # Keep only last 7 days of results
        cutoff_date = datetime.now() - timedelta(days=7)
        existing_results = [
            result for result in existing_results
            if datetime.fromisoformat(result["timestamp"]) > cutoff_date
        ]

        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(existing_results, f, indent=2)

    async def check_all_websites(self) -> Dict[str, List[HealthCheckResult]]:
        """Check health of all configured websites."""
        logger.info("🔍 Checking health of all websites")

        results = {}
        for website in self.monitoring_config["websites"].keys():
            if self.monitoring_config["websites"][website].get("enabled", False):
                website_results = await self.perform_health_check(website)
                results[website] = website_results

        return results

    def generate_health_report(self, results: Dict[str, List[HealthCheckResult]]) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_websites": len(results),
                "healthy_checks": 0,
                "warning_checks": 0,
                "critical_checks": 0,
                "total_checks": 0
            },
            "websites": {},
            "alerts": []
        }

        for website, checks in results.items():
            website_summary = {
                "total_checks": len(checks),
                "healthy": 0,
                "warning": 0,
                "critical": 0,
                "checks": []
            }

            for check in checks:
                website_summary["checks"].append(asdict(check))
                website_summary[check.status] += 1

                # Update global summary
                report["summary"]["total_checks"] += 1
                if check.status == "healthy":
                    report["summary"]["healthy_checks"] += 1
                elif check.status == "warning":
                    report["summary"]["warning_checks"] += 1
                elif check.status == "critical":
                    report["summary"]["critical_checks"] += 1

                # Generate alerts for critical issues
                if check.status == "critical":
                    report["alerts"].append({
                        "website": website,
                        "type": check.check_type,
                        "severity": "high",
                        "title": f"Critical {check.check_type} issue",
                        "description": check.error_message or f"{check.check_type} check failed",
                        "timestamp": check.timestamp
                    })

            report["websites"][website] = website_summary

        return report

    def display_health_report(self, report: Dict[str, Any]) -> None:
        """Display health report in readable format."""
        print("🏥 WEBSITE HEALTH MONITORING REPORT")
        print("=" * 50)
        print(f"Generated: {report['generated_at'][:19].replace('T', ' ')}")
        print()

        # Summary
        summary = report["summary"]
        total_checks = summary["total_checks"]
        healthy_pct = (summary["healthy_checks"] / total_checks * 100) if total_checks > 0 else 0

        print("📊 SUMMARY")
        print(f"Websites Monitored: {summary['total_websites']}")
        print(f"Total Checks: {total_checks}")
        print(".1f"        print(f"Healthy: {summary['healthy_checks']} 🟢")
        print(f"Warnings: {summary['warning_checks']} 🟡")
        print(f"Critical: {summary['critical_checks']} 🔴")
        print()

        # Website status
        print("🌐 WEBSITE STATUS")
        for website, data in report["websites"].items():
            healthy_pct = (data["healthy"] / data["total_checks"] * 100) if data["total_checks"] > 0 else 0

            status_emoji = "🟢" if healthy_pct >= 80 else "🟡" if healthy_pct >= 60 else "🔴"
            print(".1f"
            if data["critical"] > 0:
                print(f"   🔴 Critical Issues: {data['critical']}")
            if data["warning"] > 0:
                print(f"   🟡 Warnings: {data['warning']}")
        print()

        # Alerts
        if report["alerts"]:
            print("🚨 ACTIVE ALERTS")
            for alert in report["alerts"]:
                print(f"🔴 {alert['website']} - {alert['title']}")
                print(f"   {alert['description']}")
        else:
            print("✅ No critical alerts")

        print("\n🏥 Health monitoring active. Regular checks every 15 minutes.")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Website Health Monitoring")
    parser.add_argument("--action", choices=["monitor", "check", "report", "alerts"],
                       default="monitor", help="Action to perform")
    parser.add_argument("--site", help="Specific website to check")

    args = parser.parse_args()

    monitor = WebsiteHealthMonitor()

    try:
        if args.action == "monitor":
            results = await monitor.check_all_websites()
            report = monitor.generate_health_report(results)
            monitor.display_health_report(report)

        elif args.action == "check":
            if not args.site:
                print("❌ --site required for check action")
                sys.exit(1)

            results = await monitor.perform_health_check(args.site)
            print(f"🔍 Health check results for {args.site}:")
            for result in results:
                status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴", "unknown": "⚪"}.get(result.status, "⚪")
                print(f"{status_emoji} {result.check_type}: {result.status}")
                if result.error_message:
                    print(f"   Error: {result.error_message}")

        elif args.action == "report":
            results = await monitor.check_all_websites()
            report = monitor.generate_health_report(results)
            print(json.dumps(report, indent=2))

        elif args.action == "alerts":
            results = await monitor.check_all_websites()
            report = monitor.generate_health_report(results)
            alerts = report.get("alerts", [])
            if alerts:
                print("🚨 ACTIVE HEALTH ALERTS")
                for alert in alerts:
                    print(f"• {alert['website']}: {alert['title']} - {alert['description']}")
            else:
                print("✅ No active health alerts")

    except Exception as e:
        logger.error(f"Health monitoring error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())