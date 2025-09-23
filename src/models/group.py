#!/usr/bin/env python3
"""
Group Data Model
Represents a Telegram group/channel with analytics data

Author: VanZoel112
Version: 1.0.0
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


@dataclass
class Group:
    """
    Represents a Telegram group/channel with comprehensive metadata

    This model includes both basic Telegram group data and
    additional analytics for SMM analysis.
    """

    # Basic Group Data
    id: int
    title: str
    username: Optional[str] = None
    description: Optional[str] = None

    # Group Statistics
    member_count: int = 0
    online_count: int = 0
    admin_count: int = 0
    bot_count: int = 0

    # Group Settings
    is_public: bool = False
    is_megagroup: bool = False
    is_channel: bool = False
    is_verified: bool = False
    is_restricted: bool = False
    is_scam: bool = False
    is_fake: bool = False

    # Dates
    created_date: Optional[datetime] = None
    scraped_at: Optional[datetime] = None

    # Analytics Data
    activity_score: float = 0.0
    growth_rate: float = 0.0
    engagement_rate: float = 0.0
    quality_score: float = 0.0

    # Content Analysis
    primary_language: Optional[str] = None
    topics: Optional[List[str]] = None
    category: Optional[str] = None

    # SMM Insights
    target_audience: Optional[str] = None
    marketing_potential: float = 0.0
    competition_level: str = "unknown"

    # Metadata
    scraper_version: str = "1.0.0"

    def __post_init__(self):
        """Post-initialization processing"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

        # Auto-categorize group type
        self.group_type = self._determine_group_type()

        # Analyze description for insights
        if self.description:
            self.topics = self._extract_topics_from_description()
            self.category = self._categorize_group()
            self.primary_language = self._detect_language()

    def _determine_group_type(self) -> str:
        """Determine the type of group/channel"""
        if self.is_channel:
            return "channel"
        elif self.is_megagroup:
            return "megagroup"
        else:
            return "group"

    def _extract_topics_from_description(self) -> List[str]:
        """Extract topics from group description"""
        if not self.description:
            return []

        # Topic keywords for categorization
        topic_keywords = {
            'crypto': ['bitcoin', 'crypto', 'ethereum', 'blockchain', 'defi', 'nft'],
            'trading': ['trading', 'forex', 'stocks', 'investment', 'finance'],
            'technology': ['tech', 'programming', 'ai', 'development', 'software'],
            'gaming': ['gaming', 'esports', 'games', 'steam', 'xbox', 'playstation'],
            'education': ['education', 'learning', 'course', 'tutorial', 'study'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'sales'],
            'entertainment': ['entertainment', 'movies', 'music', 'shows', 'celebrity'],
            'news': ['news', 'politics', 'world', 'breaking', 'updates'],
            'lifestyle': ['lifestyle', 'fashion', 'beauty', 'health', 'fitness'],
            'community': ['community', 'local', 'city', 'region', 'neighborhood']
        }

        desc_lower = self.description.lower()
        found_topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                found_topics.append(topic)

        return found_topics[:3]  # Limit to top 3 topics

    def _categorize_group(self) -> str:
        """Categorize group based on topics and other signals"""
        if not self.topics:
            return "general"

        # Priority categorization
        if 'crypto' in self.topics:
            return "cryptocurrency"
        elif 'trading' in self.topics:
            return "trading_finance"
        elif 'technology' in self.topics:
            return "technology"
        elif 'gaming' in self.topics:
            return "gaming"
        elif 'business' in self.topics:
            return "business"
        elif 'education' in self.topics:
            return "education"
        else:
            return self.topics[0] if self.topics else "general"

    def _detect_language(self) -> str:
        """Simple language detection from description"""
        if not self.description:
            return "unknown"

        # Simple heuristics for common languages
        desc_lower = self.description.lower()

        # English indicators
        english_words = ['the', 'and', 'for', 'with', 'this', 'that', 'channel', 'group']
        if any(word in desc_lower for word in english_words):
            return "en"

        # Russian indicators
        russian_words = ['канал', 'группа', 'чат', 'бот', 'для', 'все', 'наш']
        if any(word in desc_lower for word in russian_words):
            return "ru"

        # Spanish indicators
        spanish_words = ['canal', 'grupo', 'para', 'con', 'este', 'chat']
        if any(word in desc_lower for word in spanish_words):
            return "es"

        return "unknown"

    def calculate_quality_score(self) -> float:
        """Calculate overall group quality score (0-100)"""
        score = 0.0

        # Member count scoring (30% of score)
        if self.member_count >= 10000:
            score += 30
        elif self.member_count >= 1000:
            score += 25
        elif self.member_count >= 100:
            score += 20
        else:
            score += 10

        # Verification bonus (20% of score)
        if self.is_verified:
            score += 20

        # Public group bonus (15% of score)
        if self.is_public and self.username:
            score += 15

        # Description quality (15% of score)
        if self.description:
            if len(self.description) > 50:
                score += 15
            elif len(self.description) > 20:
                score += 10
            else:
                score += 5

        # Activity indicators (20% of score)
        if self.online_count > 0 and self.member_count > 0:
            activity_ratio = self.online_count / self.member_count
            score += min(activity_ratio * 100, 20)

        # Penalties
        if self.is_scam or self.is_fake:
            score -= 50

        return max(0, min(score, 100))

    def calculate_marketing_potential(self) -> float:
        """Calculate marketing potential score (0-100)"""
        potential = 0.0

        # Size factor (40% of potential)
        if self.member_count >= 50000:
            potential += 40
        elif self.member_count >= 10000:
            potential += 35
        elif self.member_count >= 1000:
            potential += 25
        elif self.member_count >= 100:
            potential += 15
        else:
            potential += 5

        # Quality factor (30% of potential)
        potential += (self.calculate_quality_score() * 0.3)

        # Public accessibility (15% of potential)
        if self.is_public:
            potential += 15

        # Activity factor (15% of potential)
        if self.online_count > 0 and self.member_count > 0:
            activity_ratio = self.online_count / self.member_count
            potential += min(activity_ratio * 50, 15)

        return min(potential, 100)

    def get_competition_level(self) -> str:
        """Assess competition level for marketing"""
        if self.member_count >= 100000:
            return "very_high"
        elif self.member_count >= 10000:
            return "high"
        elif self.member_count >= 1000:
            return "medium"
        elif self.member_count >= 100:
            return "low"
        else:
            return "very_low"

    def get_target_audience_size(self) -> str:
        """Categorize target audience size"""
        if self.member_count >= 100000:
            return "massive"
        elif self.member_count >= 10000:
            return "large"
        elif self.member_count >= 1000:
            return "medium"
        elif self.member_count >= 100:
            return "small"
        else:
            return "micro"

    def get_growth_potential(self) -> str:
        """Assess growth potential based on current metrics"""
        quality = self.calculate_quality_score()

        if quality >= 80 and self.member_count < 10000:
            return "high"
        elif quality >= 60 and self.member_count < 50000:
            return "medium"
        elif quality >= 40:
            return "low"
        else:
            return "very_low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary for export"""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        if self.created_date:
            data['created_date'] = self.created_date.isoformat()
        if self.scraped_at:
            data['scraped_at'] = self.scraped_at.isoformat()

        # Add computed fields
        data['group_type'] = self.group_type
        data['quality_score'] = self.calculate_quality_score()
        data['marketing_potential'] = self.calculate_marketing_potential()
        data['competition_level'] = self.get_competition_level()
        data['target_audience_size'] = self.get_target_audience_size()
        data['growth_potential'] = self.get_growth_potential()

        return data

    def to_json(self) -> str:
        """Convert group to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)

    def to_csv_row(self) -> list:
        """Convert group to CSV row format"""
        return [
            self.id,
            self.title,
            self.username or '',
            self.description or '',
            self.member_count,
            self.online_count,
            self.is_public,
            self.is_verified,
            self.group_type,
            self.category or '',
            ','.join(self.topics) if self.topics else '',
            self.primary_language or '',
            f"{self.calculate_quality_score():.1f}",
            f"{self.calculate_marketing_potential():.1f}",
            self.get_competition_level(),
            self.get_target_audience_size(),
            self.get_growth_potential(),
            self.scraped_at.isoformat() if self.scraped_at else ''
        ]

    @classmethod
    def csv_headers(cls) -> list:
        """Get CSV headers for group export"""
        return [
            'group_id', 'title', 'username', 'description', 'member_count',
            'online_count', 'is_public', 'is_verified', 'group_type',
            'category', 'topics', 'primary_language', 'quality_score',
            'marketing_potential', 'competition_level', 'target_audience_size',
            'growth_potential', 'scraped_at'
        ]

    def __str__(self) -> str:
        """String representation of group"""
        return f"Group({self.title}, {self.member_count:,} members)"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Group(id={self.id}, title='{self.title}', "
                f"members={self.member_count:,}, type='{self.group_type}', "
                f"quality={self.calculate_quality_score():.1f})")


# Utility functions for group analysis
def analyze_group_batch(groups: List[Group]) -> Dict[str, Any]:
    """Analyze a batch of groups and return summary statistics"""
    if not groups:
        return {}

    total_groups = len(groups)
    total_members = sum(g.member_count for g in groups)
    public_groups = sum(1 for g in groups if g.is_public)
    verified_groups = sum(1 for g in groups if g.is_verified)

    # Category distribution
    categories = {}
    for group in groups:
        cat = group.category or 'unknown'
        categories[cat] = categories.get(cat, 0) + 1

    # Size distribution
    size_distribution = {
        'micro': sum(1 for g in groups if g.member_count < 100),
        'small': sum(1 for g in groups if 100 <= g.member_count < 1000),
        'medium': sum(1 for g in groups if 1000 <= g.member_count < 10000),
        'large': sum(1 for g in groups if 10000 <= g.member_count < 100000),
        'massive': sum(1 for g in groups if g.member_count >= 100000)
    }

    # Average scores
    avg_quality = sum(g.calculate_quality_score() for g in groups) / total_groups
    avg_marketing_potential = sum(g.calculate_marketing_potential() for g in groups) / total_groups

    # Top groups by different metrics
    top_by_members = sorted(groups, key=lambda g: g.member_count, reverse=True)[:5]
    top_by_quality = sorted(groups, key=lambda g: g.calculate_quality_score(), reverse=True)[:5]

    return {
        'total_groups': total_groups,
        'total_members': total_members,
        'average_members_per_group': total_members / total_groups,
        'public_groups': public_groups,
        'public_percentage': (public_groups / total_groups) * 100,
        'verified_groups': verified_groups,
        'verified_percentage': (verified_groups / total_groups) * 100,
        'category_distribution': categories,
        'size_distribution': size_distribution,
        'average_quality_score': avg_quality,
        'average_marketing_potential': avg_marketing_potential,
        'top_groups_by_members': [g.to_dict() for g in top_by_members],
        'top_groups_by_quality': [g.to_dict() for g in top_by_quality]
    }