#!/usr/bin/env python3
"""
Analytics Engine for Telegram Member Data
Advanced analytics and insights for SMM purposes

Author: VanZoel112
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import json
import csv
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

from ..models.member import Member, analyze_member_batch
from ..models.group import Group, analyze_group_batch

logger = logging.getLogger(__name__)


class TelegramAnalyzer:
    """
    Advanced analytics engine for Telegram member and group data

    Features:
    - Demographic analysis
    - Activity pattern analysis
    - Engagement scoring
    - Market insights
    - Competitor analysis
    - Growth predictions
    """

    def __init__(self):
        self.members_data = []
        self.groups_data = []
        self.analysis_cache = {}

    def add_members(self, members: List[Member]):
        """Add members to analysis dataset"""
        self.members_data.extend(members)
        logger.info(f"📊 Added {len(members)} members to analysis (Total: {len(self.members_data)})")

    def add_groups(self, groups: List[Group]):
        """Add groups to analysis dataset"""
        self.groups_data.extend(groups)
        logger.info(f"📊 Added {len(groups)} groups to analysis (Total: {len(self.groups_data)})")

    def analyze_demographics(self) -> Dict[str, Any]:
        """Analyze demographic patterns in member data"""
        if not self.members_data:
            return {"error": "No member data available for analysis"}

        analysis = {
            "total_members": len(self.members_data),
            "timestamp": datetime.now().isoformat()
        }

        # Basic demographics
        real_members = [m for m in self.members_data if m.is_likely_real_person()]
        bots = [m for m in self.members_data if m.is_bot]
        premium_users = [m for m in self.members_data if m.is_premium]
        verified_users = [m for m in self.members_data if m.is_verified]

        analysis.update({
            "real_members": len(real_members),
            "real_percentage": (len(real_members) / len(self.members_data)) * 100,
            "bots": len(bots),
            "bot_percentage": (len(bots) / len(self.members_data)) * 100,
            "premium_users": len(premium_users),
            "premium_percentage": (len(premium_users) / len(self.members_data)) * 100,
            "verified_users": len(verified_users),
            "verified_percentage": (len(verified_users) / len(self.members_data)) * 100
        })

        # Activity analysis
        activity_levels = Counter(m.get_activity_level() for m in self.members_data)
        analysis["activity_distribution"] = dict(activity_levels)

        # Language analysis
        languages = Counter(m.language_code for m in self.members_data if m.language_code)
        analysis["language_distribution"] = dict(languages.most_common(10))

        # Username patterns
        has_username = sum(1 for m in self.members_data if m.username)
        analysis["username_adoption"] = (has_username / len(self.members_data)) * 100

        # Bio analysis
        has_bio = sum(1 for m in self.members_data if m.bio)
        analysis["bio_adoption"] = (has_bio / len(self.members_data)) * 100

        # Interest analysis
        all_interests = []
        for member in self.members_data:
            if member.interests:
                all_interests.extend(member.interests)

        interest_counts = Counter(all_interests)
        analysis["top_interests"] = dict(interest_counts.most_common(20))

        # Marketing scores
        marketing_scores = [m.calculate_marketing_score() for m in real_members]
        if marketing_scores:
            analysis["marketing_scores"] = {
                "average": sum(marketing_scores) / len(marketing_scores),
                "median": sorted(marketing_scores)[len(marketing_scores) // 2],
                "high_potential": sum(1 for score in marketing_scores if score >= 70),
                "medium_potential": sum(1 for score in marketing_scores if 40 <= score < 70),
                "low_potential": sum(1 for score in marketing_scores if score < 40)
            }

        return analysis

    def analyze_activity_patterns(self) -> Dict[str, Any]:
        """Analyze member activity patterns"""
        if not self.members_data:
            return {"error": "No member data available"}

        real_members = [m for m in self.members_data if m.is_likely_real_person()]

        analysis = {
            "total_analyzed": len(real_members),
            "timestamp": datetime.now().isoformat()
        }

        # Activity level distribution
        activity_levels = Counter(m.get_activity_level() for m in real_members)
        total_real = len(real_members)

        analysis["activity_breakdown"] = {
            level: {
                "count": count,
                "percentage": (count / total_real) * 100
            }
            for level, count in activity_levels.items()
        }

        # Online status analysis
        online_status = Counter(m.last_seen for m in real_members if m.last_seen)
        analysis["online_status_distribution"] = dict(online_status)

        # Engagement potential
        high_engagement = sum(1 for m in real_members if m.get_activity_level() in ["very_active", "active"])
        analysis["high_engagement_potential"] = {
            "count": high_engagement,
            "percentage": (high_engagement / total_real) * 100
        }

        # Premium vs activity correlation
        premium_active = sum(1 for m in real_members if m.is_premium and m.get_activity_level() in ["very_active", "active"])
        premium_total = sum(1 for m in real_members if m.is_premium)

        if premium_total > 0:
            analysis["premium_activity_correlation"] = {
                "premium_active_rate": (premium_active / premium_total) * 100,
                "total_premium": premium_total
            }

        return analysis

    def analyze_group_performance(self) -> Dict[str, Any]:
        """Analyze group performance metrics"""
        if not self.groups_data:
            return {"error": "No group data available"}

        analysis = analyze_group_batch(self.groups_data)
        analysis["timestamp"] = datetime.now().isoformat()

        # Additional SMM-focused metrics
        high_potential_groups = [g for g in self.groups_data if g.calculate_marketing_potential() >= 70]
        medium_potential_groups = [g for g in self.groups_data if 40 <= g.calculate_marketing_potential() < 70]

        analysis["smm_insights"] = {
            "high_potential_groups": len(high_potential_groups),
            "medium_potential_groups": len(medium_potential_groups),
            "recommended_targets": [g.to_dict() for g in high_potential_groups[:5]]
        }

        # Growth potential analysis
        growth_potential = Counter(g.get_growth_potential() for g in self.groups_data)
        analysis["growth_potential_distribution"] = dict(growth_potential)

        return analysis

    def generate_competitor_analysis(self, target_groups: List[str]) -> Dict[str, Any]:
        """Generate competitor analysis report"""
        competitor_groups = [g for g in self.groups_data if g.username in target_groups or g.title in target_groups]

        if not competitor_groups:
            return {"error": "No competitor groups found in dataset"}

        analysis = {
            "competitors_analyzed": len(competitor_groups),
            "timestamp": datetime.now().isoformat(),
            "competitors": []
        }

        for group in competitor_groups:
            competitor_info = {
                "name": group.title,
                "username": group.username,
                "members": group.member_count,
                "quality_score": group.calculate_quality_score(),
                "marketing_potential": group.calculate_marketing_potential(),
                "competition_level": group.get_competition_level(),
                "category": group.category,
                "topics": group.topics,
                "strengths": [],
                "weaknesses": []
            }

            # Identify strengths and weaknesses
            if group.member_count > 10000:
                competitor_info["strengths"].append("Large audience")
            if group.is_verified:
                competitor_info["strengths"].append("Verified status")
            if group.calculate_quality_score() > 80:
                competitor_info["strengths"].append("High quality score")

            if not group.is_public:
                competitor_info["weaknesses"].append("Private group")
            if group.calculate_quality_score() < 50:
                competitor_info["weaknesses"].append("Low quality score")

            analysis["competitors"].append(competitor_info)

        # Market insights
        avg_members = sum(g.member_count for g in competitor_groups) / len(competitor_groups)
        avg_quality = sum(g.calculate_quality_score() for g in competitor_groups) / len(competitor_groups)

        analysis["market_insights"] = {
            "average_group_size": avg_members,
            "average_quality_score": avg_quality,
            "market_saturation": "high" if len(competitor_groups) > 10 else "medium" if len(competitor_groups) > 5 else "low"
        }

        return analysis

    def generate_targeting_recommendations(self) -> Dict[str, Any]:
        """Generate SMM targeting recommendations"""
        if not self.members_data:
            return {"error": "No member data available"}

        real_members = [m for m in self.members_data if m.is_likely_real_person()]
        high_potential = [m for m in real_members if m.calculate_marketing_score() >= 70]

        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "total_members": len(real_members),
            "high_potential_targets": len(high_potential)
        }

        if high_potential:
            # Demographic targeting
            languages = Counter(m.language_code for m in high_potential if m.language_code)
            activity_levels = Counter(m.get_activity_level() for m in high_potential)
            interests = []
            for member in high_potential:
                if member.interests:
                    interests.extend(member.interests)
            interest_counts = Counter(interests)

            recommendations["targeting_criteria"] = {
                "preferred_languages": dict(languages.most_common(5)),
                "activity_levels": dict(activity_levels),
                "top_interests": dict(interest_counts.most_common(10)),
                "premium_user_ratio": (sum(1 for m in high_potential if m.is_premium) / len(high_potential)) * 100
            }

            # Campaign recommendations
            recommendations["campaign_recommendations"] = {
                "primary_audience_size": len([m for m in high_potential if m.get_activity_level() == "very_active"]),
                "secondary_audience_size": len([m for m in high_potential if m.get_activity_level() == "active"]),
                "content_themes": list(interest_counts.most_common(5)),
                "engagement_strategy": "high_frequency" if len(high_potential) > 1000 else "personalized"
            }

        return recommendations

    def export_analysis_report(self, output_path: str, format_type: str = "json"):
        """Export comprehensive analysis report"""
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_members": len(self.members_data),
                "total_groups": len(self.groups_data),
                "analyzer_version": "1.0.0"
            },
            "demographic_analysis": self.analyze_demographics(),
            "activity_patterns": self.analyze_activity_patterns(),
            "group_performance": self.analyze_group_performance(),
            "targeting_recommendations": self.generate_targeting_recommendations()
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if format_type.lower() == "json":
            with open(f"{output_path}.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        elif format_type.lower() == "csv" and HAS_PANDAS:
            # Export key metrics to CSV
            self._export_csv_report(report, output_path)

        logger.info(f"📊 Analysis report exported to {output_path}.{format_type}")
        return report

    def _export_csv_report(self, report: Dict, output_path: str):
        """Export analysis report to CSV format"""
        # Members summary
        members_df = pd.DataFrame([{
            'metric': k,
            'value': v
        } for k, v in report['demographic_analysis'].items() if isinstance(v, (int, float))])

        members_df.to_csv(f"{output_path}_demographics.csv", index=False)

        # Activity patterns
        if 'activity_breakdown' in report['activity_patterns']:
            activity_data = []
            for level, data in report['activity_patterns']['activity_breakdown'].items():
                activity_data.append({
                    'activity_level': level,
                    'count': data['count'],
                    'percentage': data['percentage']
                })
            activity_df = pd.DataFrame(activity_data)
            activity_df.to_csv(f"{output_path}_activity.csv", index=False)

    def generate_visualization_data(self) -> Dict[str, Any]:
        """Generate data for visualization dashboards"""
        if not HAS_PANDAS:
            return {"error": "Pandas not available for visualization data generation"}

        viz_data = {}

        if self.members_data:
            # Activity distribution
            activity_counts = Counter(m.get_activity_level() for m in self.members_data)
            viz_data["activity_pie_chart"] = {
                "labels": list(activity_counts.keys()),
                "values": list(activity_counts.values())
            }

            # Marketing scores distribution
            scores = [m.calculate_marketing_score() for m in self.members_data if m.is_likely_real_person()]
            if scores:
                viz_data["marketing_scores_histogram"] = {
                    "scores": scores,
                    "bins": 20
                }

            # Interest trends
            all_interests = []
            for member in self.members_data:
                if member.interests:
                    all_interests.extend(member.interests)

            interest_counts = Counter(all_interests)
            viz_data["interest_bar_chart"] = {
                "interests": list(interest_counts.keys())[:10],
                "counts": list(interest_counts.values())[:10]
            }

        if self.groups_data:
            # Group size distribution
            group_sizes = [g.member_count for g in self.groups_data]
            viz_data["group_sizes_scatter"] = {
                "sizes": group_sizes,
                "quality_scores": [g.calculate_quality_score() for g in self.groups_data]
            }

        return viz_data

    async def real_time_analysis(self, update_interval: int = 300):
        """Run real-time analysis updates"""
        logger.info(f"🔄 Starting real-time analysis (update every {update_interval}s)")

        while True:
            try:
                # Generate fresh analysis
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "demographics": self.analyze_demographics(),
                    "activity": self.analyze_activity_patterns(),
                    "groups": self.analyze_group_performance()
                }

                # Cache the analysis
                self.analysis_cache = analysis

                logger.info(f"📊 Analysis updated: {len(self.members_data)} members, {len(self.groups_data)} groups")

                await asyncio.sleep(update_interval)

            except Exception as e:
                logger.error(f"❌ Error in real-time analysis: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    def clear_data(self):
        """Clear all analysis data"""
        self.members_data.clear()
        self.groups_data.clear()
        self.analysis_cache.clear()
        logger.info("🗑️ Analysis data cleared")


# Utility functions for advanced analytics
def calculate_engagement_score(member: Member) -> float:
    """Calculate engagement score for a member"""
    score = 0.0

    # Activity bonus
    activity_scores = {
        "very_active": 40,
        "active": 30,
        "moderate": 20,
        "low": 10,
        "inactive": 0
    }
    score += activity_scores.get(member.get_activity_level(), 0)

    # Profile completeness
    if member.first_name:
        score += 10
    if member.last_name:
        score += 10
    if member.username:
        score += 10
    if member.bio:
        score += 15

    # Premium indicators
    if member.is_premium:
        score += 15

    return min(score, 100.0)


def predict_churn_risk(member: Member) -> str:
    """Predict churn risk for a member"""
    risk_score = 0

    # Activity-based risk
    if member.get_activity_level() == "inactive":
        risk_score += 40
    elif member.get_activity_level() == "low":
        risk_score += 25
    elif member.get_activity_level() == "moderate":
        risk_score += 10

    # Account type risk
    if member.is_bot:
        risk_score += 50  # Bots are unpredictable

    # Profile completeness (inverse risk)
    if not member.first_name and not member.username:
        risk_score += 20

    if risk_score >= 50:
        return "high"
    elif risk_score >= 25:
        return "medium"
    else:
        return "low"


# Example usage
async def main():
    """Example usage of the analyzer"""
    analyzer = TelegramAnalyzer()

    # Sample data would be added here
    # analyzer.add_members(members_list)
    # analyzer.add_groups(groups_list)

    # Generate analysis
    demographics = analyzer.analyze_demographics()
    print("Demographics:", json.dumps(demographics, indent=2, default=str))

    # Export report
    analyzer.export_analysis_report("data/exports/analysis_report", "json")


if __name__ == "__main__":
    asyncio.run(main())