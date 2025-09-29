#!/usr/bin/env python3
"""
Force Export - Emergency script to export member data
When main scraper collects data but fails to export
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append('.')

# Import setelah path setup
from src.core.scraper import TelegramMemberScraper
from src.models.member import Member

async def force_export_from_recent_scrape():
    """
    Force export by re-running collection on one group with immediate export
    """
    print("🚨 Emergency Export Mode")
    print("=" * 50)

    # Target groups yang berhasil sebelumnya
    target_groups = [
        "https://t.me/cari_temen_random_pacar",
        "https://t.me/friendwithbenefitbase"
    ]

    scraper = TelegramMemberScraper("config/target_config.yaml")

    try:
        await scraper.initialize()
        print("✅ Scraper initialized")

        for group_url in target_groups:
            print(f"\n🎯 Processing: {group_url}")
            print("-" * 40)

            # Collect members dengan limit kecil untuk test
            members = []
            count = 0

            try:
                async for member in scraper.scrape_group_members(group_url, limit=100):
                    members.append(member)
                    count += 1

                    if count % 25 == 0:
                        print(f"📊 Collected {count} members...")

                print(f"✅ Final count: {len(members)} members")

                # Force export multiple formats
                if members:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    group_name = group_url.split('/')[-1].replace('@', '')

                    # Manual CSV Export (more reliable)
                    csv_file = f"data/exports/force_export_{group_name}_{timestamp}.csv"
                    try:
                        import csv
                        from pathlib import Path

                        Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

                        # Get fieldnames from member
                        sample_dict = members[0].to_dict()
                        fieldnames = list(sample_dict.keys())

                        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()

                            for member in members:
                                member_dict = member.to_dict()
                                row_data = {field: member_dict.get(field, '') for field in fieldnames}
                                writer.writerow(row_data)

                        if Path(csv_file).exists():
                            size = Path(csv_file).stat().st_size
                            print(f"💾 CSV: {csv_file} ({size} bytes)")
                        else:
                            print(f"❌ CSV file not created: {csv_file}")

                    except Exception as csv_error:
                        print(f"❌ CSV export failed: {csv_error}")

                    # Manual JSON Export (more reliable)
                    json_file = f"data/exports/force_export_{group_name}_{timestamp}.json"
                    try:
                        with open(json_file, 'w', encoding='utf-8') as jsonfile:
                            data = {
                                'export_info': {
                                    'timestamp': timestamp,
                                    'total_members': len(members),
                                    'scraper_version': '1.0.0',
                                    'group_url': group_url
                                },
                                'members': [member.to_dict() for member in members]
                            }
                            json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

                        if Path(json_file).exists():
                            size = Path(json_file).stat().st_size
                            print(f"💾 JSON: {json_file} ({size} bytes)")
                        else:
                            print(f"❌ JSON file not created: {json_file}")

                    except Exception as json_error:
                        print(f"❌ JSON export failed: {json_error}")

                    # Manual backup
                    backup_file = f"data/exports/manual_backup_{group_name}_{timestamp}.json"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        member_data = [m.to_dict() for m in members]
                        json.dump({
                            'group_url': group_url,
                            'timestamp': timestamp,
                            'total_members': len(members),
                            'members': member_data
                        }, f, indent=2, ensure_ascii=False, default=str)
                    print(f"📦 Backup: {backup_file}")

                else:
                    print("❌ No members collected!")

            except Exception as e:
                print(f"❌ Error processing {group_url}: {e}")
                continue

        # List hasil export
        print(f"\n📁 Export Results:")
        print("=" * 50)
        export_files = list(Path("data/exports").glob("force_export_*"))
        for file in export_files:
            print(f"✅ {file}")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await scraper.close()

if __name__ == "__main__":
    print("🚨 FORCE EXPORT MODE")
    print("This will collect fresh data and force export")
    print("Press Ctrl+C to cancel, or wait 3 seconds...")

    try:
        import time
        time.sleep(3)
        asyncio.run(force_export_from_recent_scrape())
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")