#!/usr/bin/env python3
"""
Advanced Telegram Member Scraper
Professional-grade member extraction with SMM focus

Author: VanZoel112
Version: 1.0.0
License: MIT
"""

import asyncio
import logging
import time
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, AsyncGenerator
from pathlib import Path

from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetParticipantsRequest, GetFullChannelRequest
from telethon.tl.types import (
    ChannelParticipantsSearch, ChannelParticipantsRecent,
    ChannelParticipantsAdmins, ChannelParticipantsBots,
    Channel, Chat, User, UserStatusOnline, UserStatusOffline,
    UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
)
from telethon.errors import FloodWaitError, ChannelPrivateError, ChatAdminRequiredError

from ..utils.rate_limiter import RateLimiter
from ..utils.config import Config
from ..models.member import Member
from ..models.group import Group

# Setup logging with directory creation
log_dir = Path('data/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramMemberScraper:
    """
    Advanced Telegram Member Scraper for SMM

    Features:
    - Multi-group scraping with rate limiting
    - Member activity analysis
    - Export to multiple formats
    - Resume interrupted sessions
    - Demographic insights
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = Config(config_path)
        self.client = None
        self.rate_limiter = RateLimiter(
            max_requests=50,
            time_window=60
        )
        self.session_data = {}
        self.scraped_members = []

    async def initialize(self):
        """Initialize Telegram client"""
        try:
            self.client = TelegramClient(
                session=self.config.get('telegram.session_name', 'scraper_session'),
                api_id=self.config.get('telegram.api_id'),
                api_hash=self.config.get('telegram.api_hash')
            )

            await self.client.start()
            logger.info("✅ Telegram client initialized successfully")

            # Get client info
            me = await self.client.get_me()
            logger.info(f"📱 Logged in as: {me.first_name} (@{me.username})")

        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            raise

    async def get_group_info(self, group_identifier: str) -> Group:
        """Get detailed group information"""
        try:
            # Get basic entity
            entity = await self.client.get_entity(group_identifier)

            # Get full channel info for additional details
            if hasattr(entity, 'id'):
                try:
                    full_info = await self.client(GetFullChannelRequest(entity))
                    full_chat = full_info.full_chat

                    group = Group(
                        id=entity.id,
                        title=entity.title,
                        username=getattr(entity, 'username', None),
                        member_count=getattr(full_chat, 'participants_count', 0),
                        description=getattr(full_chat, 'about', ''),
                        is_public=bool(getattr(entity, 'username', None)),
                        is_megagroup=getattr(entity, 'megagroup', False),
                        created_date=getattr(entity, 'date', None)
                    )

                    logger.info(f"📊 Group: {group.title} ({group.member_count:,} members)")
                    return group

                except Exception as e:
                    logger.warning(f"⚠️ Could not get full group info: {e}")
                    # Fallback to basic info
                    return Group(
                        id=entity.id,
                        title=entity.title,
                        username=getattr(entity, 'username', None),
                        member_count=0
                    )

        except ChannelPrivateError:
            logger.error(f"❌ Group {group_identifier} is private or not accessible")
            raise
        except Exception as e:
            logger.error(f"❌ Error getting group info: {e}")
            raise

    async def scrape_group_members(
        self,
        group_identifier: str,
        limit: Optional[int] = None,
        filter_type: str = "all",
        include_inactive: bool = True
    ) -> AsyncGenerator[Member, None]:
        """
        Scrape members from a Telegram group

        Args:
            group_identifier: Group username or ID
            limit: Maximum number of members to scrape
            filter_type: Type of members to scrape ('all', 'recent', 'admins', 'bots')
            include_inactive: Include inactive members
        """

        if not self.client:
            await self.initialize()

        try:
            # Get group info
            group = await self.get_group_info(group_identifier)
            entity = await self.client.get_entity(group_identifier)

            # Set up participant filter
            participant_filter = self._get_participant_filter(filter_type)

            # Scraping parameters
            offset = 0
            batch_size = self.config.get('scraping.batch_size', 100)
            max_members = limit or self.config.get('scraping.max_members_per_group', 10000)
            scraped_count = 0

            logger.info(f"🚀 Starting to scrape {group.title}")
            logger.info(f"📋 Filter: {filter_type}, Limit: {max_members:,}")

            while scraped_count < max_members:
                # Rate limiting
                await self.rate_limiter.wait()

                try:
                    # Get participants batch
                    participants = await self.client(GetParticipantsRequest(
                        channel=entity,
                        filter=participant_filter,
                        offset=offset,
                        limit=min(batch_size, max_members - scraped_count),
                        hash=0
                    ))

                    if not participants.users:
                        logger.info("✅ No more members to scrape")
                        break

                    # Process each member
                    for user in participants.users:
                        if scraped_count >= max_members:
                            break

                        if user.deleted:
                            continue

                        # Create member object
                        member = await self._process_member(user, group)

                        # Filter inactive members if requested
                        if not include_inactive and not member.is_active:
                            continue

                        scraped_count += 1
                        yield member

                        # Progress logging
                        if scraped_count % 100 == 0:
                            logger.info(f"📈 Scraped {scraped_count:,} members...")

                    offset += len(participants.users)

                    # Add delay between requests
                    await asyncio.sleep(self.config.get('scraping.delay_between_requests', 1.0))

                except FloodWaitError as e:
                    logger.warning(f"⏳ Rate limited. Waiting {e.seconds} seconds...")
                    await asyncio.sleep(e.seconds + 1)
                    continue

                except ChatAdminRequiredError:
                    logger.warning(f"⚠️ Admin privileges required to access full member list for {group.title}")
                    logger.info("💡 Trying alternative approach: fetching recent participants only...")

                    # Try with recent participants filter which sometimes works without admin
                    try:
                        participants = await self.client(GetParticipantsRequest(
                            channel=entity,
                            filter=ChannelParticipantsRecent(),
                            offset=offset,
                            limit=min(batch_size, max_members - scraped_count),
                            hash=0
                        ))

                        if not participants.users:
                            logger.warning("❌ No accessible members found - insufficient permissions")
                            break

                        # Process the accessible members
                        for user in participants.users:
                            if scraped_count >= max_members:
                                break

                            if user.deleted:
                                continue

                            member = await self._process_member(user, group)

                            if not include_inactive and not member.is_active:
                                continue

                            scraped_count += 1
                            yield member

                            if scraped_count % 100 == 0:
                                logger.info(f"📈 Scraped {scraped_count:,} members...")

                        offset += len(participants.users)

                    except Exception as e2:
                        logger.error(f"❌ Alternative approach also failed: {e2}")
                        break

                except Exception as e:
                    logger.error(f"❌ Error in batch scraping: {e}")
                    await asyncio.sleep(5)
                    continue

            logger.info(f"✅ Completed scraping {scraped_count:,} members from {group.title}")

        except Exception as e:
            logger.error(f"❌ Fatal error in group scraping: {e}")
            raise

    async def _process_member(self, user: User, group: Group) -> Member:
        """Process a user into a Member object with analytics"""

        # Determine activity status
        is_active = self._determine_activity_status(user.status)
        last_seen = self._get_last_seen_info(user.status)

        # Extract user information
        member = Member(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=getattr(user, 'phone', None),
            bio=getattr(user, 'about', ''),
            is_bot=user.bot,
            is_premium=getattr(user, 'premium', False),
            is_verified=user.verified,
            is_scam=user.scam,
            is_fake=user.fake,
            is_active=is_active,
            last_seen=last_seen,
            language_code=getattr(user, 'lang_code', None),
            group_id=group.id,
            group_title=group.title,
            scraped_at=datetime.now()
        )

        return member

    def _get_participant_filter(self, filter_type: str):
        """Get appropriate participant filter"""
        filters = {
            'all': ChannelParticipantsSearch(''),
            'recent': ChannelParticipantsRecent(),
            'admins': ChannelParticipantsAdmins(),
            'bots': ChannelParticipantsBots()
        }
        return filters.get(filter_type, ChannelParticipantsSearch(''))

    def _determine_activity_status(self, status) -> bool:
        """Determine if user is active based on status"""
        if isinstance(status, (UserStatusOnline, UserStatusRecently)):
            return True
        elif isinstance(status, UserStatusLastWeek):
            return True
        elif isinstance(status, UserStatusLastMonth):
            return False
        else:
            return False

    def _get_last_seen_info(self, status) -> Optional[str]:
        """Extract last seen information"""
        if isinstance(status, UserStatusOnline):
            return "online"
        elif isinstance(status, UserStatusRecently):
            return "recently"
        elif isinstance(status, UserStatusLastWeek):
            return "within_week"
        elif isinstance(status, UserStatusLastMonth):
            return "within_month"
        elif isinstance(status, UserStatusOffline):
            if hasattr(status, 'was_online'):
                return status.was_online.isoformat()
        return "unknown"

    async def batch_scrape_groups(
        self,
        group_list: List[str],
        export_format: str = "csv",
        delay_between_groups: int = 5
    ) -> Dict[str, int]:
        """
        Scrape multiple groups in batch

        Returns:
            Dictionary with group names and member counts
        """
        results = {}

        for i, group in enumerate(group_list, 1):
            logger.info(f"📊 Processing group {i}/{len(group_list)}: {group}")

            try:
                members = []
                member_count = 0
                async for member in self.scrape_group_members(group):
                    members.append(member)
                    member_count += 1

                    # Debug logging every 100 members
                    if member_count % 100 == 0:
                        logger.info(f"🔄 Collected {member_count} members so far in list...")

                logger.info(f"📊 Final collection: {len(members)} members in list for {group}")
                results[group] = len(members)

                # Export group data
                if members:
                    export_filename = f"data/exports/{group.replace('@', '').replace('/', '_')}"
                    logger.info(f"💾 Attempting to export {len(members)} members to: {export_filename}")
                    try:
                        await self._export_members(members, export_filename, export_format)
                        logger.info(f"✅ Successfully exported {len(members)} members")
                    except Exception as export_error:
                        logger.error(f"❌ Export failed: {export_error}")
                        # Try to save as backup JSON
                        try:
                            import json
                            backup_path = f"{export_filename}_backup.json"
                            with open(backup_path, 'w', encoding='utf-8') as f:
                                member_data = [m.to_dict() for m in members]
                                json.dump(member_data, f, indent=2, ensure_ascii=False, default=str)
                            logger.info(f"💾 Backup saved to: {backup_path}")
                        except Exception as backup_error:
                            logger.error(f"❌ Backup also failed: {backup_error}")
                else:
                    logger.warning(f"⚠️ No members to export for group: {group}")

                # Delay between groups
                if i < len(group_list):
                    logger.info(f"⏳ Waiting {delay_between_groups}s before next group...")
                    await asyncio.sleep(delay_between_groups)

            except Exception as e:
                logger.error(f"❌ Failed to scrape {group}: {e}")
                results[group] = 0
                continue

        return results

    async def _export_members(
        self,
        members: List[Member],
        filename_base: str,
        format_type: str = "csv"
    ):
        """Export members to various formats"""
        logger.info(f"🔧 Export function called: {len(members)} members, format: {format_type}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            if format_type.lower() == "csv":
                filename = f"{filename_base}_{timestamp}.csv"
                logger.info(f"📄 Creating CSV file: {filename}")
                await self._export_to_csv(members, filename)

            elif format_type.lower() == "json":
                filename = f"{filename_base}_{timestamp}.json"
                logger.info(f"📄 Creating JSON file: {filename}")
                await self._export_to_json(members, filename)

            elif format_type.lower() in ["xlsx", "excel"]:
                filename = f"{filename_base}_{timestamp}.xlsx"
                logger.info(f"📄 Creating Excel file: {filename}")
                await self._export_to_excel(members, filename)

            logger.info(f"💾 Successfully exported {len(members):,} members to {filename}")

        except Exception as e:
            logger.error(f"❌ Export error in _export_members: {e}")
            raise

    async def _export_to_csv(self, members: List[Member], filename: str):
        """Export members to CSV format"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all possible fieldnames from member dictionary
            if members:
                # Use the first member's dictionary keys as fieldnames
                sample_dict = members[0].to_dict()
                fieldnames = list(sample_dict.keys())
            else:
                # Fallback to basic fieldnames if no members
                fieldnames = [
                    'id', 'username', 'first_name', 'last_name', 'phone',
                    'bio', 'is_bot', 'is_premium', 'is_verified', 'is_active',
                    'last_seen', 'language_code', 'group_title', 'scraped_at'
                ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for member in members:
                # Get member dict and ensure all fields are present
                member_dict = member.to_dict()
                # Fill missing fields with None/empty values
                row_data = {field: member_dict.get(field, '') for field in fieldnames}
                writer.writerow(row_data)

    async def _export_to_json(self, members: List[Member], filename: str):
        """Export members to JSON format"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'total_members': len(members),
                'scraper_version': '1.0.0'
            },
            'members': [member.to_dict() for member in members]
        }

        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

    async def _export_to_excel(self, members: List[Member], filename: str):
        """Export members to Excel format"""
        try:
            import pandas as pd
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

            # Convert to DataFrame
            data = [member.to_dict() for member in members]
            df = pd.DataFrame(data)

            # Export to Excel with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Members', index=False)

                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Members']

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        except ImportError:
            logger.warning("⚠️ pandas not available, falling back to CSV export")
            csv_filename = filename.replace('.xlsx', '.csv')
            await self._export_to_csv(members, csv_filename)
            logger.info(f"📄 Excel export not available - data saved as CSV: {csv_filename}")
        except Exception as e:
            logger.error(f"❌ Excel export failed: {e}")
            logger.info("🔄 Falling back to CSV export...")
            csv_filename = filename.replace('.xlsx', '.csv')
            await self._export_to_csv(members, csv_filename)
            logger.info(f"📄 Fallback successful - data saved as CSV: {csv_filename}")

    async def close(self):
        """Close the Telegram client"""
        if self.client:
            await self.client.disconnect()
            logger.info("📱 Telegram client disconnected")


# CLI Usage Example
async def main():
    """Example usage of the scraper"""
    scraper = TelegramMemberScraper()

    try:
        await scraper.initialize()

        # Example: Scrape single group
        members = []
        async for member in scraper.scrape_group_members("@pythongroup", limit=1000):
            members.append(member)

        # Export results
        await scraper._export_members(members, "data/exports/python_group", "csv")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())