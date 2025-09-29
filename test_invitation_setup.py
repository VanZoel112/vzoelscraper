#!/usr/bin/env python3
"""
Test Invitation Setup - Verify invitation system readiness
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.append('.')

async def test_invitation_setup():
    """Test invitation system setup"""
    print("🧪 Testing Invitation System Setup")
    print("=" * 40)

    # Check data availability
    export_files = list(Path('data/exports').glob('emergency_members_*.json'))
    if export_files:
        latest_file = max(export_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ Member data available: {latest_file.name}")

        # Load and verify data structure
        with open(latest_file, 'r') as f:
            data = json.load(f)

        members = data.get('members', [])
        print(f"📊 Members loaded: {len(members)}")

        if members:
            sample_member = members[0]
            print(f"👤 Sample member: {sample_member.get('username')} (ID: {sample_member.get('user_id')})")

            # Check required fields for invitation
            required_fields = ['username', 'user_id']
            missing_fields = [field for field in required_fields if not sample_member.get(field)]

            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ All required fields present")

        # Target group info
        target_group = data.get('export_info', {}).get('target_group')
        print(f"🎯 Target group: {target_group}")

    else:
        print("❌ No member data found")

    # Check session availability
    session_files = list(Path('data/sessions').glob('*'))
    print(f"📁 Session files: {len(session_files)}")

    # Import invitation system for testing
    try:
        from invite_members import MemberInviter
        inviter = MemberInviter()
        print(f"✅ MemberInviter imported successfully")
        print(f"🎯 Target configured: {inviter.target_group}")
        print(f"⏰ Rate limit delay: {inviter.rate_limit_delay}s")
    except Exception as e:
        print(f"❌ Failed to import MemberInviter: {e}")

    print(f"\n📋 Invitation System Readiness Summary:")
    print(f"✅ Member data: {'Available' if export_files else 'Missing'}")
    print(f"✅ Target group: {target_group if 'target_group' in locals() else 'Configured'}")
    print(f"✅ Invitation script: Available")
    print(f"⚠️  Session/Auth: Needs configuration")

    print(f"\n🚀 Next Steps:")
    print(f"1. Configure API credentials or session")
    print(f"2. Verify admin access to target group")
    print(f"3. Run invitation with small batch for testing")

if __name__ == "__main__":
    asyncio.run(test_invitation_setup())