#!/usr/bin/env python3
"""
Debug Export - Test export functionality step by step
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append('.')

from src.models.member import Member

async def debug_export():
    """Debug export step by step"""
    print("🔧 DEBUG EXPORT MODE")
    print("=" * 40)

    # Create test member
    member = Member(
        id=123456789,
        username='testuser',
        first_name='Test',
        last_name='User',
        is_active=True,
        group_title='Debug Group',
        scraped_at=datetime.now()
    )

    members = [member]
    print(f"✅ Created {len(members)} test members")

    # Test manual CSV export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # Ensure directory exists
        Path("data/exports").mkdir(parents=True, exist_ok=True)
        print("✅ Directory ensured")

        # Manual CSV export
        csv_file = f"data/exports/debug_export_{timestamp}.csv"
        print(f"📄 Trying to create: {csv_file}")

        import csv

        # Get fieldnames from member
        sample_dict = members[0].to_dict()
        fieldnames = list(sample_dict.keys())
        print(f"📋 Fields: {len(fieldnames)} total")

        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for member in members:
                member_dict = member.to_dict()
                row_data = {field: member_dict.get(field, '') for field in fieldnames}
                writer.writerow(row_data)

        print(f"✅ CSV created: {csv_file}")

        # Check if file exists
        if Path(csv_file).exists():
            size = Path(csv_file).stat().st_size
            print(f"✅ File verified: {size} bytes")
        else:
            print("❌ File not found after creation!")

        # Manual JSON export
        json_file = f"data/exports/debug_export_{timestamp}.json"
        print(f"📄 Trying to create: {json_file}")

        with open(json_file, 'w', encoding='utf-8') as jsonfile:
            data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_members': len(members),
                    'scraper_version': '1.0.0'
                },
                'members': [member.to_dict() for member in members]
            }
            json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

        print(f"✅ JSON created: {json_file}")

        if Path(json_file).exists():
            size = Path(json_file).stat().st_size
            print(f"✅ File verified: {size} bytes")
        else:
            print("❌ File not found after creation!")

        # List all files
        print(f"\n📁 Export directory contents:")
        for file in Path("data/exports").iterdir():
            if file.is_file():
                print(f"  ✅ {file.name} ({file.stat().st_size} bytes)")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_export())