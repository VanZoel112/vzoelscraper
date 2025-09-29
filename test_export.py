#!/usr/bin/env python3
"""
Test export functionality
"""

import asyncio
import sys
sys.path.append('.')

from src.core.scraper import TelegramMemberScraper
from src.models.member import Member
from datetime import datetime

async def test_export():
    """Test export functionality with dummy data"""
    print("🧪 Testing export functionality...")

    # Create dummy members
    members = []
    for i in range(5):
        member = Member(
            id=123456789 + i,
            username=f'testuser{i}',
            first_name=f'Test{i}',
            last_name='User',
            is_active=True,
            is_premium=(i % 2 == 0),
            group_title='Test Group',
            scraped_at=datetime.now()
        )
        members.append(member)

    print(f"📊 Created {len(members)} dummy members")

    # Test export
    scraper = TelegramMemberScraper()

    try:
        # Test CSV export
        await scraper._export_members(members, "data/exports/test_export", "csv")
        print("✅ CSV export test completed")

        # Test JSON export
        await scraper._export_members(members, "data/exports/test_export", "json")
        print("✅ JSON export test completed")

        # List export files
        import os
        export_files = [f for f in os.listdir('data/exports') if 'test_export' in f]
        print(f"📁 Export files created: {export_files}")

    except Exception as e:
        print(f"❌ Export test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_export())