#!/usr/bin/env python3
"""
Test force export with single group for verification
"""

import asyncio
import sys
sys.path.append('.')

from src.core.scraper import TelegramMemberScraper

async def test_single_group():
    """Test with one group and small limit"""
    print("🧪 Testing Force Export - Single Group")
    print("=" * 40)

    scraper = TelegramMemberScraper("config/target_config.yaml")

    try:
        await scraper.initialize()
        print("✅ Scraper initialized")

        # Test dengan grup pertama dan limit sangat kecil
        group_url = "https://t.me/cari_temen_random_pacar"
        print(f"🎯 Testing: {group_url}")

        members = []
        count = 0

        async for member in scraper.scrape_group_members(group_url, limit=5):
            members.append(member)
            count += 1
            print(f"  📊 Member {count}: {member.get_display_name()}")

        print(f"✅ Collected {len(members)} members")

        if members:
            # Manual export like debug_export.py
            from datetime import datetime
            from pathlib import Path
            import csv
            import json

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # CSV Export
            csv_file = f"data/exports/test_force_{timestamp}.csv"
            Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

            sample_dict = members[0].to_dict()
            fieldnames = list(sample_dict.keys())

            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for member in members:
                    member_dict = member.to_dict()
                    row_data = {field: member_dict.get(field, '') for field in fieldnames}
                    writer.writerow(row_data)

            print(f"💾 CSV created: {csv_file}")

            # JSON Export
            json_file = f"data/exports/test_force_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as jsonfile:
                data = {
                    'export_info': {
                        'timestamp': timestamp,
                        'total_members': len(members),
                        'group_url': group_url
                    },
                    'members': [member.to_dict() for member in members]
                }
                json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

            print(f"💾 JSON created: {json_file}")

        else:
            print("❌ No members collected!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_single_group())