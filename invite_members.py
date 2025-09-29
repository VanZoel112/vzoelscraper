#!/usr/bin/env python3
"""
Member Invitation Script for vzoelscraper
Invites scraped members to target group

Author: VanZoel112
Version: 1.0.0
"""

import asyncio
import logging
import time
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from telethon import TelegramClient, errors
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError

# Import config system
import sys
sys.path.append('.')
from src.utils.config import Config

# Setup logging
log_dir = Path('data/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'invite_members.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MemberInviter:
    """Member invitation system for target group"""

    def __init__(self, config_path: str = "config/target_config.yaml", session_name: str = "scraper_session"):
        self.config = Config(config_path)
        self.session_name = session_name
        self.client = None
        self.target_group = "https://t.me/+3_lpGQGGGeA2NWJl"
        self.invited_count = 0
        self.failed_count = 0
        self.rate_limit_delay = 30  # seconds between invitations

    async def initialize_client(self):
        """Initialize Telegram client"""
        try:
            # Use config like the successful scraper
            api_id = self.config.get('telegram.api_id')
            api_hash = self.config.get('telegram.api_hash')
            session_name = self.config.get('telegram.session_name', self.session_name)

            logger.info(f"🔧 Initializing client with session: {session_name}")

            self.client = TelegramClient(
                session=session_name,
                api_id=api_id,
                api_hash=api_hash
            )

            await self.client.start()

            me = await self.client.get_me()
            logger.info(f"📱 Logged in as: {me.first_name} (@{me.username})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            logger.error(f"🔧 Config path: {self.config.config_path if hasattr(self.config, 'config_path') else 'Unknown'}")
            return False

    async def load_scraped_members(self, export_file: str) -> List[Dict]:
        """Load members from scraped data"""
        members = []
        export_path = Path('data/exports') / export_file

        try:
            if export_file.endswith('.json'):
                with open(export_path, 'r') as f:
                    data = json.load(f)
                    members = data.get('members', [])
            elif export_file.endswith('.csv'):
                with open(export_path, 'r') as f:
                    reader = csv.DictReader(f)
                    members = list(reader)

            logger.info(f"📋 Loaded {len(members)} members from {export_file}")
            return members

        except Exception as e:
            logger.error(f"❌ Failed to load members: {e}")
            return []

    async def invite_member(self, username: str, user_id: int = None) -> bool:
        """Invite single member to target group"""
        try:
            # Get target group entity
            target_entity = await self.client.get_entity(self.target_group)

            # Get user entity
            if username:
                user_entity = await self.client.get_entity(username)
            elif user_id:
                user_entity = await self.client.get_entity(user_id)
            else:
                return False

            # Invite user to group
            await self.client(InviteToChannelRequest(
                channel=target_entity,
                users=[user_entity]
            ))

            self.invited_count += 1
            logger.info(f"✅ Invited {username or user_id} ({self.invited_count} total)")
            return True

        except UserPrivacyRestrictedError:
            logger.warning(f"🔒 Privacy restricted: {username or user_id}")
            self.failed_count += 1
            return False

        except PeerFloodError:
            logger.error("🚫 Peer flood error - too many invitations")
            await asyncio.sleep(3600)  # Wait 1 hour
            return False

        except FloodWaitError as e:
            logger.warning(f"⏰ Rate limited, waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return await self.invite_member(username, user_id)

        except Exception as e:
            logger.error(f"❌ Failed to invite {username or user_id}: {e}")
            self.failed_count += 1
            return False

    async def invite_members_batch(self, members: List[Dict], batch_size: int = 50):
        """Invite members in batches with rate limiting"""
        logger.info(f"🚀 Starting invitation process for {len(members)} members")
        logger.info(f"🎯 Target group: {self.target_group}")

        for i, member in enumerate(members[:batch_size]):
            try:
                username = member.get('username')
                user_id = member.get('user_id')

                if not username and not user_id:
                    continue

                success = await self.invite_member(username, user_id)

                # Rate limiting delay
                if success:
                    await asyncio.sleep(self.rate_limit_delay)
                else:
                    await asyncio.sleep(5)  # Shorter delay on failure

                # Progress update
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 Progress: {i + 1}/{len(members)} processed")
                    logger.info(f"✅ Invited: {self.invited_count} | ❌ Failed: {self.failed_count}")

            except Exception as e:
                logger.error(f"❌ Batch error for member {i}: {e}")
                continue

        # Final summary
        logger.info(f"🏁 Invitation process completed!")
        logger.info(f"✅ Successfully invited: {self.invited_count}")
        logger.info(f"❌ Failed invitations: {self.failed_count}")
        logger.info(f"📊 Success rate: {(self.invited_count/(self.invited_count+self.failed_count)*100):.1f}%")

    async def disconnect(self):
        """Disconnect client"""
        if self.client:
            await self.client.disconnect()
            logger.info("📱 Client disconnected")

async def main():
    """Main invitation process"""
    inviter = MemberInviter()

    try:
        # Initialize client
        if not await inviter.initialize_client():
            return

        # Load latest scraped members
        # You can specify a specific export file here
        export_files = list(Path('data/exports').glob('*.json'))
        if not export_files:
            export_files = list(Path('data/exports').glob('*.csv'))

        if not export_files:
            logger.error("❌ No export files found. Run scraper first!")
            return

        # Use the most recent export
        latest_export = max(export_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"📁 Using export file: {latest_export.name}")

        members = await inviter.load_scraped_members(latest_export.name)
        if not members:
            logger.error("❌ No members loaded")
            return

        # Start invitation process
        await inviter.invite_members_batch(members, batch_size=50)

    except Exception as e:
        logger.error(f"❌ Main process error: {e}")

    finally:
        await inviter.disconnect()

if __name__ == "__main__":
    print("🎯 Member Invitation System")
    print("Target Group: https://t.me/+3_lpGQGGGeA2NWJl")
    print("=" * 50)

    asyncio.run(main())