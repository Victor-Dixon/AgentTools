#!/usr/bin/env python3
"""
Unified Analytics Dashboard for Swarm Websites
==============================================

Agent-8: SSOT & System Integration
Builds unified analytics dashboard aggregating data from all swarm websites.

Features:
- Multi-website analytics aggregation
- Performance metrics tracking
- SEO analytics integration
- Real-time monitoring dashboard
- Automated reporting

Usage:
    python tools/analytics/unified_analytics_dashboard.py --action dashboard
    python tools/analytics/unified_analytics_dashboard.py --action report --site weareswarm.online
    python tools/analytics/unified_analytics_dashboard.py --action alerts
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class WebsiteAnalytics:
    """Analytics data for a single website."""
    domain: str
    timestamp: str
    page_views: Optional[int] = None
    unique_visitors: Optional[int] = None
    bounce_rate: Optional[float] = None
    avg_session_duration: Optional[float] = None
    top_pages: List[Dict[str, Any]] = None
    traffic_sources: Dict[str, Any] = None
    seo_score: Optional[int] = None
    performance_score: Optional[int] = None

    def __post_init__(self):
        if self.top_pages is None:
            self.top_pages = []
        if self.traffic_sources is None:
            self.traffic_sources = {}


@dataclass
class AnalyticsAlert:
    """Analytics alert for monitoring."""
    website: str
    alert_type: str  # traffic_drop, performance_decline, seo_issue, etc.
    severity: str  # low, medium, high, critical
    message: str
    threshold: Any
    current_value: Any
    timestamp: str


class UnifiedAnalyticsDashboard:
    """Unified analytics dashboard for all swarm websites."""

    def __init__(self):
        self.data_path = Path(__file__).parent / "data"
        self.reports_path = Path(__file__).parent / "reports"
        self.config_path = Path(__file__).parent / "analytics_config.json"

        # Create directories
        self.data_path.mkdir(exist_ok=True)
        self.reports_path.mkdir(exist_ok=True)

        # Website configurations with analytics tracking
        self.websites = {
            "weareswarm.online": {
                "analytics_id": None,  # Would be GA4 measurement ID
                "search_console": None,  # Would be GSC site URL
                "social_tracking": True,
                "performance_monitoring": True
            },
            "freerideinvestor.com": {
                "analytics_id": None,
                "search_console": None,
                "social_tracking": True,
                "performance_monitoring": True
            },
            "houstonsipqueen.com": {
                "analytics_id": None,
                "search_console": None,
                "social_tracking": True,
                "performance_monitoring": True
            },
            "prismblossom.online": {
                "analytics_id": None,
                "search_console": None,
                "social_tracking": True,
                "performance_monitoring": True
            },
            "southwestsecret.com": {
                "analytics_id": None,
                "search_console": None,
                "social_tracking": True,
                "performance_monitoring": True
            }
        }

    def collect_website_analytics(self, domain: str) -> WebsiteAnalytics:
        """
        Collect analytics data for a specific website.

        In production, this would integrate with:
        - Google Analytics 4
        - Google Search Console
        - Social media APIs
        - Performance monitoring tools
        """
        logger.info(f"📊 Collecting analytics for {domain}")

        # Mock data for demonstration - in production this would call real APIs
        analytics = WebsiteAnalytics(
            domain=domain,
            timestamp=datetime.now().isoformat(),
            page_views=self._mock_page_views(domain),
            unique_visitors=self._mock_unique_visitors(domain),
            bounce_rate=self._mock_bounce_rate(domain),
            avg_session_duration=self._mock_session_duration(domain),
            top_pages=self._mock_top_pages(domain),
            traffic_sources=self._mock_traffic_sources(domain),
            seo_score=self._calculate_seo_score(domain),
            performance_score=self._calculate_performance_score(domain)
        )

        # Save to data file
        self._save_analytics_data(analytics)

        return analytics

    def _mock_page_views(self, domain: str) -> int:
        """Mock page views data."""
        # In production: call Google Analytics API
        base_views = {"weareswarm.online": 1200, "freerideinvestor.com": 800,
                     "houstonsipqueen.com": 600, "prismblossom.online": 400,
                     "southwestsecret.com": 300}
        return base_views.get(domain, 100)

    def _mock_unique_visitors(self, domain: str) -> int:
        """Mock unique visitors data."""
        # In production: call Google Analytics API
        base_visitors = {"weareswarm.online": 800, "freerideinvestor.com": 500,
                        "houstonsipqueen.com": 400, "prismblossom.online": 250,
                        "southwestsecret.com": 200}
        return base_visitors.get(domain, 50)

    def _mock_bounce_rate(self, domain: str) -> float:
        """Mock bounce rate data."""
        # In production: call Google Analytics API
        base_rates = {"weareswarm.online": 0.65, "freerideinvestor.com": 0.55,
                     "houstonsipqueen.com": 0.70, "prismblossom.online": 0.60,
                     "southwestsecret.com": 0.75}
        return base_rates.get(domain, 0.80)

    def _mock_session_duration(self, domain: str) -> float:
        """Mock session duration data."""
        # In production: call Google Analytics API
        base_duration = {"weareswarm.online": 180, "freerideinvestor.com": 240,
                        "houstonsipqueen.com": 120, "prismblossom.online": 300,
                        "southwestsecret.com": 90}
        return base_duration.get(domain, 60)

    def _mock_top_pages(self, domain: str) -> List[Dict[str, Any]]:
        """Mock top pages data."""
        # In production: call Google Analytics API
        if "weareswarm" in domain:
            return [
                {"page": "/", "views": 450, "bounce_rate": 0.60},
                {"page": "/about", "views": 180, "bounce_rate": 0.70},
                {"page": "/contact", "views": 120, "bounce_rate": 0.80}
            ]
        elif "freerideinvestor" in domain:
            return [
                {"page": "/", "views": 320, "bounce_rate": 0.50},
                {"page": "/blog", "views": 200, "bounce_rate": 0.55},
                {"page": "/contact", "views": 80, "bounce_rate": 0.75}
            ]
        else:
            return [
                {"page": "/", "views": 150, "bounce_rate": 0.65},
                {"page": "/about", "views": 80, "bounce_rate": 0.70}
            ]

    def _mock_traffic_sources(self, domain: str) -> Dict[str, Any]:
        """Mock traffic sources data."""
        # In production: call Google Analytics API
        return {
            "organic_search": 0.45,
            "direct": 0.30,
            "social": 0.15,
            "referral": 0.08,
            "email": 0.02
        }

    def _calculate_seo_score(self, domain: str) -> int:
        """Calculate SEO score based on known factors."""
        # In production: integrate with SEO tools or manual audit data
        base_scores = {
            "weareswarm.online": 75,
            "freerideinvestor.com": 82,
            "houstonsipqueen.com": 68,
            "prismblossom.online": 71,
            "southwestsecret.com": 65
        }
        return base_scores.get(domain, 50)

    def _calculate_performance_score(self, domain: str) -> int:
        """Calculate performance score."""
        # In production: integrate with performance monitoring tools
        base_scores = {
            "weareswarm.online": 85,
            "freerideinvestor.com": 78,
            "houstonsipqueen.com": 82,
            "prismblossom.online": 75,
            "southwestsecret.com": 80
        }
        return base_scores.get(domain, 70)

    def _save_analytics_data(self, analytics: WebsiteAnalytics) -> None:
        """Save analytics data to file."""
        data_file = self.data_path / f"{analytics.domain.replace('.', '_')}_analytics.json"

        # Load existing data
        existing_data = []
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []

        # Add new data point
        existing_data.append(asdict(analytics))

        # Keep only last 30 days of data
        cutoff_date = datetime.now() - timedelta(days=30)
        existing_data = [
            data for data in existing_data
            if datetime.fromisoformat(data["timestamp"]) > cutoff_date
        ]

        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

    def generate_unified_dashboard(self) -> Dict[str, Any]:
        """Generate unified analytics dashboard for all websites."""
        logger.info("📊 Generating unified analytics dashboard")

        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_websites": len(self.websites),
                "total_page_views": 0,
                "total_unique_visitors": 0,
                "average_bounce_rate": 0.0,
                "average_seo_score": 0.0,
                "average_performance_score": 0.0
            },
            "websites": {},
            "trends": {},
            "alerts": []
        }

        # Collect data for each website
        for domain in self.websites.keys():
            analytics = self.collect_website_analytics(domain)

            dashboard["websites"][domain] = {
                "current": asdict(analytics),
                "status": self._determine_website_status(analytics),
                "recommendations": self._generate_recommendations(analytics)
            }

            # Update summary
            dashboard["summary"]["total_page_views"] += analytics.page_views or 0
            dashboard["summary"]["total_unique_visitors"] += analytics.unique_visitors or 0

        # Calculate averages
        website_count = len(dashboard["websites"])
        if website_count > 0:
            dashboard["summary"]["average_bounce_rate"] = sum(
                site["current"]["bounce_rate"] or 0
                for site in dashboard["websites"].values()
            ) / website_count

            dashboard["summary"]["average_seo_score"] = sum(
                site["current"]["seo_score"] or 0
                for site in dashboard["websites"].values()
            ) / website_count

            dashboard["summary"]["average_performance_score"] = sum(
                site["current"]["performance_score"] or 0
                for site in dashboard["websites"].values()
            ) / website_count

        # Generate alerts
        dashboard["alerts"] = self._generate_alerts(dashboard["websites"])

        # Save dashboard
        self._save_dashboard(dashboard)

        return dashboard

    def _determine_website_status(self, analytics: WebsiteAnalytics) -> str:
        """Determine overall website status."""
        if not analytics.seo_score or not analytics.performance_score:
            return "unknown"

        avg_score = (analytics.seo_score + analytics.performance_score) / 2

        if avg_score >= 85:
            return "excellent"
        elif avg_score >= 75:
            return "good"
        elif avg_score >= 65:
            return "needs_improvement"
        else:
            return "critical_attention_needed"

    def _generate_recommendations(self, analytics: WebsiteAnalytics) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []

        if analytics.bounce_rate and analytics.bounce_rate > 0.70:
            recommendations.append("High bounce rate - improve page content and user engagement")

        if analytics.seo_score and analytics.seo_score < 70:
            recommendations.append("SEO score needs improvement - check meta tags and content optimization")

        if analytics.performance_score and analytics.performance_score < 75:
            recommendations.append("Performance issues detected - optimize images and loading times")

        if not recommendations:
            recommendations.append("Website performing well - continue monitoring")

        return recommendations

    def _generate_alerts(self, websites: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on analytics data."""
        alerts = []

        for domain, data in websites.items():
            analytics = data["current"]

            # Bounce rate alert
            if analytics.get("bounce_rate", 0) > 0.80:
                alerts.append({
                    "website": domain,
                    "type": "high_bounce_rate",
                    "severity": "high",
                    "message": f"Critical bounce rate: {analytics['bounce_rate']:.1%}",
                    "threshold": 0.80,
                    "current_value": analytics["bounce_rate"]
                })

            # SEO score alert
            if analytics.get("seo_score", 100) < 60:
                alerts.append({
                    "website": domain,
                    "type": "low_seo_score",
                    "severity": "medium",
                    "message": f"Low SEO score: {analytics['seo_score']}",
                    "threshold": 60,
                    "current_value": analytics["seo_score"]
                })

            # Performance alert
            if analytics.get("performance_score", 100) < 70:
                alerts.append({
                    "website": domain,
                    "type": "performance_issue",
                    "severity": "medium",
                    "message": f"Poor performance score: {analytics['performance_score']}",
                    "threshold": 70,
                    "current_value": analytics["performance_score"]
                })

        return alerts

    def _save_dashboard(self, dashboard: Dict[str, Any]) -> None:
        """Save dashboard data."""
        dashboard_file = self.reports_path / f"unified_dashboard_{datetime.now().strftime('%Y%m%d')}.json"

        with open(dashboard_file, 'w') as f:
            json.dump(dashboard, f, indent=2)

    def generate_analytics_report(self, domain: Optional[str] = None,
                                days: int = 7) -> Dict[str, Any]:
        """Generate detailed analytics report."""
        logger.info(f"📊 Generating analytics report for {domain or 'all websites'}")

        report = {
            "generated_at": datetime.now().isoformat(),
            "report_period_days": days,
            "websites": {}
        }

        websites_to_report = [domain] if domain else list(self.websites.keys())

        for site_domain in websites_to_report:
            # Load historical data
            data_file = self.data_path / f"{site_domain.replace('.', '_')}_analytics.json"
            historical_data = []

            if data_file.exists():
                try:
                    with open(data_file, 'r') as f:
                        historical_data = json.load(f)
                except:
                    pass

            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = [
                data for data in historical_data
                if datetime.fromisoformat(data["timestamp"]) > cutoff_date
            ]

            if recent_data:
                report["websites"][site_domain] = {
                    "data_points": len(recent_data),
                    "date_range": {
                        "start": recent_data[0]["timestamp"] if recent_data else None,
                        "end": recent_data[-1]["timestamp"] if recent_data else None
                    },
                    "metrics": self._calculate_metrics_summary(recent_data),
                    "trends": self._calculate_trends(recent_data)
                }

        return report

    def _calculate_metrics_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics from historical data."""
        if not data:
            return {}

        page_views = [d.get("page_views", 0) for d in data if d.get("page_views")]
        bounce_rates = [d.get("bounce_rate", 0) for d in data if d.get("bounce_rate")]
        seo_scores = [d.get("seo_score", 0) for d in data if d.get("seo_score")]
        perf_scores = [d.get("performance_score", 0) for d in data if d.get("performance_score")]

        return {
            "avg_page_views": sum(page_views) / len(page_views) if page_views else 0,
            "avg_bounce_rate": sum(bounce_rates) / len(bounce_rates) if bounce_rates else 0,
            "avg_seo_score": sum(seo_scores) / len(seo_scores) if seo_scores else 0,
            "avg_performance_score": sum(perf_scores) / len(perf_scores) if perf_scores else 0,
            "data_points": len(data)
        }

    def _calculate_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends from historical data."""
        if len(data) < 2:
            return {"insufficient_data": True}

        # Simple trend calculation (most recent vs average of previous)
        recent = data[-1]
        previous_avg = data[:-1]

        trends = {}

        for metric in ["page_views", "bounce_rate", "seo_score", "performance_score"]:
            recent_val = recent.get(metric)
            if recent_val is not None and previous_avg:
                prev_vals = [d.get(metric) for d in previous_avg if d.get(metric) is not None]
                if prev_vals:
                    prev_avg = sum(prev_vals) / len(prev_vals)
                    change = recent_val - prev_avg
                    percent_change = (change / prev_avg) * 100 if prev_avg != 0 else 0

                    trends[metric] = {
                        "change": change,
                        "percent_change": percent_change,
                        "direction": "up" if change > 0 else "down" if change < 0 else "stable"
                    }

        return trends

    def display_dashboard(self, dashboard: Dict[str, Any]) -> None:
        """Display dashboard in readable format."""
        print("🐝 UNIFIED ANALYTICS DASHBOARD")
        print("=" * 50)
        print(f"Generated: {dashboard['generated_at'][:19].replace('T', ' ')}")
        print()

        # Summary
        summary = dashboard["summary"]
        print("📊 SUMMARY")
        print(f"Total Websites: {summary['total_websites']}")
        print(","
        print(","
        print(".1f")
        print(".1f")
        print()

        # Website status
        print("🌐 WEBSITE STATUS")
        for domain, data in dashboard["websites"].items():
            status = data["status"]
            status_emoji = {"excellent": "🟢", "good": "🟡", "needs_improvement": "🟠", "critical_attention_needed": "🔴"}.get(status, "⚪")
            print(f"{status_emoji} {domain}: {status.replace('_', ' ').title()}")

            # Show top recommendations
            if data["recommendations"]:
                print(f"   💡 {data['recommendations'][0]}")
        print()

        # Alerts
        if dashboard["alerts"]:
            print("🚨 ALERTS")
            for alert in dashboard["alerts"]:
                severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}.get(alert["severity"], "⚪")
                print(f"{severity_emoji} {alert['website']}: {alert['message']}")
        else:
            print("✅ No critical alerts")

        print("\n🐝 WE. ARE. SWARM. Analytics driving optimization.")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Analytics Dashboard")
    parser.add_argument("--action", choices=["dashboard", "report", "alerts"],
                       default="dashboard", help="Action to perform")
    parser.add_argument("--site", help="Specific website for report")
    parser.add_argument("--days", type=int, default=7, help="Days for report (default: 7)")

    args = parser.parse_args()

    dashboard = UnifiedAnalyticsDashboard()

    try:
        if args.action == "dashboard":
            data = dashboard.generate_unified_dashboard()
            dashboard.display_dashboard(data)

        elif args.action == "report":
            report = dashboard.generate_analytics_report(args.site, args.days)
            print(json.dumps(report, indent=2))

        elif args.action == "alerts":
            data = dashboard.generate_unified_dashboard()
            alerts = data.get("alerts", [])
            if alerts:
                print("🚨 ACTIVE ALERTS")
                for alert in alerts:
                    print(f"• {alert['website']}: {alert['message']}")
            else:
                print("✅ No active alerts")

    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())