#!/usr/bin/env python3
"""
Member Data Model
Represents a Telegram group member with analytics data

Author: VanZoel112
Version: 1.0.0
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Member:
    """
    Represents a Telegram group member with comprehensive data

    This model includes both basic Telegram user data and
    additional analytics information for SMM purposes.
    """

    # Basic Telegram Data
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

    # Account Status
    is_bot: bool = False
    is_premium: bool = False
    is_verified: bool = False
    is_scam: bool = False
    is_fake: bool = False
    is_deleted: bool = False

    # Activity Data
    is_active: bool = False
    last_seen: Optional[str] = None
    language_code: Optional[str] = None

    # Group Context
    group_id: Optional[int] = None
    group_title: Optional[str] = None
    join_date: Optional[datetime] = None

    # Analytics Data
    message_count_estimate: int = 0
    engagement_score: float = 0.0
    activity_pattern: Optional[str] = None
    estimated_age_group: Optional[str] = None
    estimated_location: Optional[str] = None
    interests: Optional[list] = None

    # Metadata
    scraped_at: Optional[datetime] = None
    scraper_version: str = "1.0.0"

    def __post_init__(self):
        """Post-initialization processing"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()

        # Auto-generate display name
        self.display_name = self.get_display_name()

        # Analyze bio for insights
        if self.bio:
            self.interests = self._extract_interests_from_bio()
            self.estimated_location = self._extract_location_from_bio()

    def get_display_name(self) -> str:
        """Get the best available display name for the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.id}"

    def get_full_name(self) -> str:
        """Get full name or fallback to username"""
        if self.first_name or self.last_name:
            parts = [part for part in [self.first_name, self.last_name] if part]
            return " ".join(parts)
        return self.username or f"user_{self.id}"

    def is_likely_real_person(self) -> bool:
        """Heuristic to determine if this is likely a real person (not bot/fake)"""
        if self.is_bot or self.is_fake or self.is_scam or self.is_deleted:
            return False

        # Additional heuristics
        has_human_name = bool(self.first_name and len(self.first_name) > 1)
        has_reasonable_username = bool(
            self.username and
            len(self.username) > 3 and
            not self.username.lower().endswith('bot')
        )

        return has_human_name or has_reasonable_username

    def get_activity_level(self) -> str:
        """Categorize user activity level"""
        if self.last_seen == "online":
            return "very_active"
        elif self.last_seen == "recently":
            return "active"
        elif self.last_seen == "within_week":
            return "moderate"
        elif self.last_seen == "within_month":
            return "low"
        else:
            return "inactive"

    def calculate_marketing_score(self) -> float:
        """Calculate a marketing potential score (0-100)"""
        score = 0.0

        # Activity bonus (40% of score)
        activity_scores = {
            "very_active": 40,
            "active": 35,
            "moderate": 25,
            "low": 15,
            "inactive": 5
        }
        score += activity_scores.get(self.get_activity_level(), 0)

        # Real person bonus (30% of score)
        if self.is_likely_real_person():
            score += 30

        # Premium user bonus (10% of score)
        if self.is_premium:
            score += 10

        # Verified user bonus (10% of score)
        if self.is_verified:
            score += 10

        # Complete profile bonus (10% of score)
        profile_completeness = 0
        if self.first_name:
            profile_completeness += 3
        if self.last_name:
            profile_completeness += 3
        if self.username:
            profile_completeness += 2
        if self.bio:
            profile_completeness += 2

        score += profile_completeness

        return min(score, 100.0)

    def _extract_interests_from_bio(self) -> list:
        """Extract potential interests from bio text"""
        if not self.bio:
            return []

        # Simple keyword extraction (can be enhanced with NLP)
        interest_keywords = [
            'crypto', 'bitcoin', 'ethereum', 'nft', 'defi',
            'trading', 'forex', 'stocks', 'investment',
            'startup', 'entrepreneur', 'business',
            'marketing', 'smm', 'social media',
            'tech', 'ai', 'programming', 'developer',
            'design', 'art', 'music', 'photography',
            'travel', 'food', 'fitness', 'health',
            'gaming', 'esports', 'streaming'
        ]

        bio_lower = self.bio.lower()
        found_interests = [
            keyword for keyword in interest_keywords
            if keyword in bio_lower
        ]

        return found_interests[:5]  # Limit to top 5

    def _extract_location_from_bio(self) -> Optional[str]:
        """Extract potential location from bio text"""
        if not self.bio:
            return None

        # Simple location extraction (can be enhanced)
        common_locations = [
            'usa', 'united states', 'america',
            'uk', 'united kingdom', 'britain',
            'canada', 'australia', 'germany',
            'france', 'italy', 'spain',
            'russia', 'china', 'japan',
            'india', 'brazil', 'mexico',
            'new york', 'london', 'paris',
            'tokyo', 'moscow', 'beijing'
        ]

        bio_lower = self.bio.lower()
        for location in common_locations:
            if location in bio_lower:
                return location.title()

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert member to dictionary for export"""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        if self.scraped_at:
            data['scraped_at'] = self.scraped_at.isoformat()
        if self.join_date:
            data['join_date'] = self.join_date.isoformat()

        # Add computed fields
        data['display_name'] = self.display_name
        data['full_name'] = self.get_full_name()
        data['activity_level'] = self.get_activity_level()
        data['marketing_score'] = self.calculate_marketing_score()
        data['is_likely_real'] = self.is_likely_real_person()

        return data

    def to_json(self) -> str:
        """Convert member to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)

    def to_csv_row(self) -> list:
        """Convert member to CSV row format"""
        return [
            self.id,
            self.username or '',
            self.first_name or '',
            self.last_name or '',
            self.phone or '',
            self.bio or '',
            self.is_bot,
            self.is_premium,
            self.is_verified,
            self.is_scam,
            self.is_fake,
            self.is_active,
            self.last_seen or '',
            self.language_code or '',
            self.group_title or '',
            self.get_activity_level(),
            f"{self.calculate_marketing_score():.1f}",
            self.is_likely_real_person(),
            ','.join(self.interests) if self.interests else '',
            self.estimated_location or '',
            self.scraped_at.isoformat() if self.scraped_at else ''
        ]

    @classmethod
    def csv_headers(cls) -> list:
        """Get CSV headers for member export"""
        return [
            'user_id', 'username', 'first_name', 'last_name', 'phone',
            'bio', 'is_bot', 'is_premium', 'is_verified', 'is_scam', 'is_fake',
            'is_active', 'last_seen', 'language_code', 'group_title',
            'activity_level', 'marketing_score', 'is_likely_real',
            'interests', 'estimated_location', 'scraped_at'
        ]

    def __str__(self) -> str:
        """String representation of member"""
        return f"Member({self.get_display_name()}, ID: {self.id}, Active: {self.is_active})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Member(id={self.id}, username='{self.username}', "
                f"name='{self.get_full_name()}', active={self.is_active}, "
                f"score={self.calculate_marketing_score():.1f})")


# Utility functions for member analysis
def analyze_member_batch(members: list) -> dict:
    """Analyze a batch of members and return summary statistics"""
    if not members:
        return {}

    total_members = len(members)
    active_members = sum(1 for m in members if m.is_active)
    real_members = sum(1 for m in members if m.is_likely_real_person())
    premium_members = sum(1 for m in members if m.is_premium)
    verified_members = sum(1 for m in members if m.is_verified)
    bot_members = sum(1 for m in members if m.is_bot)

    # Activity distribution
    activity_levels = {}
    for member in members:
        level = member.get_activity_level()
        activity_levels[level] = activity_levels.get(level, 0) + 1

    # Average marketing score
    avg_marketing_score = sum(m.calculate_marketing_score() for m in members) / total_members

    # Top interests
    all_interests = []
    for member in members:
        if member.interests:
            all_interests.extend(member.interests)

    interest_counts = {}
    for interest in all_interests:
        interest_counts[interest] = interest_counts.get(interest, 0) + 1

    top_interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        'total_members': total_members,
        'active_members': active_members,
        'active_percentage': (active_members / total_members) * 100,
        'real_members': real_members,
        'real_percentage': (real_members / total_members) * 100,
        'premium_members': premium_members,
        'verified_members': verified_members,
        'bot_members': bot_members,
        'activity_distribution': activity_levels,
        'average_marketing_score': avg_marketing_score,
        'top_interests': top_interests
    }