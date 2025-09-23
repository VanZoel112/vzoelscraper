#!/usr/bin/env python3
"""
Telegram Member Scraper for SMM - Main CLI Interface
Professional-grade member extraction tool with analytics

Author: VanZoel112
Version: 1.0.0
License: MIT
"""

import asyncio
import argparse
import sys
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from src.core.scraper import TelegramMemberScraper
from src.core.analyzer import TelegramAnalyzer
from src.utils.config import Config, setup_environment
from src.models.member import Member
from src.models.group import Group

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rich console if available
console = Console() if RICH_AVAILABLE else None


class TelegramScraperCLI:
    """
    Command-line interface for Telegram Member Scraper

    Provides easy-to-use commands for scraping, analyzing, and exporting
    Telegram member data for SMM purposes.
    """

    def __init__(self):
        self.config = None
        self.scraper = None
        self.analyzer = TelegramAnalyzer()

    async def initialize(self, config_path: Optional[str] = None):
        """Initialize the scraper with configuration"""
        try:
            self.config = Config(config_path)
            self.scraper = TelegramMemberScraper(config_path or "config/settings.yaml")
            await self.scraper.initialize()

            if console:
                console.print("✅ [green]Telegram scraper initialized successfully![/green]")
            else:
                print("✅ Telegram scraper initialized successfully!")

        except Exception as e:
            if console:
                console.print(f"❌ [red]Failed to initialize scraper: {e}[/red]")
            else:
                print(f"❌ Failed to initialize scraper: {e}")
            sys.exit(1)

    async def scrape_single_group(
        self,
        group: str,
        limit: Optional[int] = None,
        export_format: str = "csv",
        analyze: bool = False
    ):
        """Scrape a single group"""
        if console:
            console.print(f"🚀 [blue]Starting to scrape group: {group}[/blue]")

        members = []

        try:
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Scraping {group}...", total=limit or 1000)

                    async for member in self.scraper.scrape_group_members(
                        group, limit=limit
                    ):
                        members.append(member)
                        progress.advance(task, 1)

                        if len(members) % 50 == 0:
                            progress.update(task, description=f"Scraped {len(members)} members...")

            else:
                print(f"Scraping {group}...")
                async for member in self.scraper.scrape_group_members(group, limit=limit):
                    members.append(member)
                    if len(members) % 100 == 0:
                        print(f"Scraped {len(members)} members...")

            # Export members
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/exports/{group.replace('@', '').replace('/', '_')}_{timestamp}"

            await self.scraper._export_members(members, filename, export_format)

            # Display results
            self._display_scraping_results(group, members)

            # Optional analysis
            if analyze and members:
                await self._analyze_scraped_data([members], [])

        except Exception as e:
            if console:
                console.print(f"❌ [red]Error scraping {group}: {e}[/red]")
            else:
                print(f"❌ Error scraping {group}: {e}")

    async def scrape_multiple_groups(
        self,
        groups_file: str,
        export_format: str = "csv",
        delay: int = 5,
        analyze: bool = False
    ):
        """Scrape multiple groups from a file"""
        try:
            with open(groups_file, 'r') as f:
                groups = [line.strip() for line in f.readlines() if line.strip()]

            if console:
                console.print(f"📋 [blue]Loaded {len(groups)} groups from {groups_file}[/blue]")
            else:
                print(f"📋 Loaded {len(groups)} groups from {groups_file}")

            results = await self.scraper.batch_scrape_groups(
                groups, export_format=export_format, delay_between_groups=delay
            )

            # Display batch results
            self._display_batch_results(results)

            if analyze:
                # Collect all data for analysis
                all_members = []
                all_groups = []

                for group_name in groups:
                    try:
                        group_info = await self.scraper.get_group_info(group_name)
                        all_groups.append(group_info)
                    except:
                        continue

                if all_groups:
                    await self._analyze_scraped_data([], all_groups)

        except FileNotFoundError:
            if console:
                console.print(f"❌ [red]Groups file not found: {groups_file}[/red]")
            else:
                print(f"❌ Groups file not found: {groups_file}")
        except Exception as e:
            if console:
                console.print(f"❌ [red]Error in batch scraping: {e}[/red]")
            else:
                print(f"❌ Error in batch scraping: {e}")

    async def analyze_data(self, data_path: str):
        """Analyze existing scraped data"""
        try:
            # Load data from various formats
            members = self._load_members_data(data_path)

            if not members:
                if console:
                    console.print(f"❌ [red]No member data found in {data_path}[/red]")
                else:
                    print(f"❌ No member data found in {data_path}")
                return

            await self._analyze_scraped_data([members], [])

        except Exception as e:
            if console:
                console.print(f"❌ [red]Error analyzing data: {e}[/red]")
            else:
                print(f"❌ Error analyzing data: {e}")

    def _load_members_data(self, data_path: str) -> List[Member]:
        """Load members data from file"""
        members = []
        path = Path(data_path)

        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'members' in data:
                    for member_data in data['members']:
                        member = Member(**member_data)
                        members.append(member)

        elif path.suffix.lower() == '.csv':
            import csv
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert row to Member object
                    member = Member(
                        id=int(row.get('id', 0)),
                        username=row.get('username') or None,
                        first_name=row.get('first_name') or None,
                        last_name=row.get('last_name') or None,
                        is_bot=row.get('is_bot', '').lower() == 'true',
                        is_premium=row.get('is_premium', '').lower() == 'true',
                        is_active=row.get('is_active', '').lower() == 'true'
                    )
                    members.append(member)

        return members

    async def _analyze_scraped_data(self, member_batches: List[List[Member]], groups: List[Group]):
        """Analyze scraped data and display insights"""
        # Add data to analyzer
        for batch in member_batches:
            self.analyzer.add_members(batch)

        if groups:
            self.analyzer.add_groups(groups)

        # Generate analysis
        demographics = self.analyzer.analyze_demographics()
        activity = self.analyzer.analyze_activity_patterns()
        targeting = self.analyzer.generate_targeting_recommendations()

        # Display analysis results
        self._display_analysis_results(demographics, activity, targeting)

        # Export analysis report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"data/exports/analysis_report_{timestamp}"
        self.analyzer.export_analysis_report(report_path, "json")

        if console:
            console.print(f"📊 [green]Analysis report saved to {report_path}.json[/green]")
        else:
            print(f"📊 Analysis report saved to {report_path}.json")

    def _display_scraping_results(self, group: str, members: List[Member]):
        """Display scraping results"""
        real_members = [m for m in members if m.is_likely_real_person()]
        active_members = [m for m in members if m.is_active]

        if console:
            # Create results table
            table = Table(title=f"Scraping Results: {group}")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Percentage", style="yellow")

            total = len(members)
            table.add_row("Total Members", str(total), "100%")
            table.add_row("Real Members", str(len(real_members)), f"{(len(real_members)/total)*100:.1f}%")
            table.add_row("Active Members", str(len(active_members)), f"{(len(active_members)/total)*100:.1f}%")
            table.add_row("Bots", str(sum(1 for m in members if m.is_bot)), f"{(sum(1 for m in members if m.is_bot)/total)*100:.1f}%")
            table.add_row("Premium Users", str(sum(1 for m in members if m.is_premium)), f"{(sum(1 for m in members if m.is_premium)/total)*100:.1f}%")

            console.print(table)
        else:
            print(f"\n=== Scraping Results: {group} ===")
            print(f"Total Members: {len(members)}")
            print(f"Real Members: {len(real_members)} ({(len(real_members)/len(members))*100:.1f}%)")
            print(f"Active Members: {len(active_members)} ({(len(active_members)/len(members))*100:.1f}%)")
            print(f"Bots: {sum(1 for m in members if m.is_bot)}")
            print(f"Premium Users: {sum(1 for m in members if m.is_premium)}")

    def _display_batch_results(self, results: dict):
        """Display batch scraping results"""
        if console:
            table = Table(title="Batch Scraping Results")
            table.add_column("Group", style="cyan")
            table.add_column("Members Scraped", style="green")

            for group, count in results.items():
                table.add_row(group, str(count))

            total_scraped = sum(results.values())
            table.add_row("[bold]TOTAL", f"[bold]{total_scraped}")

            console.print(table)
        else:
            print("\n=== Batch Scraping Results ===")
            for group, count in results.items():
                print(f"{group}: {count} members")
            print(f"Total: {sum(results.values())} members")

    def _display_analysis_results(self, demographics: dict, activity: dict, targeting: dict):
        """Display analysis results"""
        if console:
            # Demographics table
            demo_table = Table(title="📊 Demographic Analysis")
            demo_table.add_column("Metric", style="cyan")
            demo_table.add_column("Value", style="green")

            demo_table.add_row("Total Members", str(demographics.get('total_members', 0)))
            demo_table.add_row("Real Members", f"{demographics.get('real_percentage', 0):.1f}%")
            demo_table.add_row("Premium Users", f"{demographics.get('premium_percentage', 0):.1f}%")
            demo_table.add_row("Active Members", f"{activity.get('activity_breakdown', {}).get('very_active', {}).get('percentage', 0):.1f}%")

            console.print(demo_table)

            # Top interests
            if 'top_interests' in demographics and demographics['top_interests']:
                interests_table = Table(title="🎯 Top Interests")
                interests_table.add_column("Interest", style="cyan")
                interests_table.add_column("Count", style="green")

                for interest, count in list(demographics['top_interests'].items())[:10]:
                    interests_table.add_row(interest, str(count))

                console.print(interests_table)

        else:
            print("\n=== Demographic Analysis ===")
            print(f"Total Members: {demographics.get('total_members', 0)}")
            print(f"Real Members: {demographics.get('real_percentage', 0):.1f}%")
            print(f"Premium Users: {demographics.get('premium_percentage', 0):.1f}%")

            if 'top_interests' in demographics:
                print("\nTop Interests:")
                for interest, count in list(demographics['top_interests'].items())[:5]:
                    print(f"  {interest}: {count}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.scraper:
            await self.scraper.close()


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Telegram Member Scraper for SMM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --group @cryptogroup --limit 1000 --analyze
  %(prog)s --groups groups.txt --format xlsx --delay 3
  %(prog)s --analyze data/exports/members_20241201_120000.json
  %(prog)s --setup  # Initial setup and configuration
        """
    )

    # Main commands
    parser.add_argument('--group', '-g', help='Single group to scrape (@username or ID)')
    parser.add_argument('--groups', help='File containing list of groups to scrape')
    parser.add_argument('--analyze', '-a', nargs='?', const=True, help='Analyze data (optionally specify data file)')

    # Scraping options
    parser.add_argument('--limit', '-l', type=int, help='Maximum members to scrape per group')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'xlsx'], default='csv', help='Export format')
    parser.add_argument('--delay', '-d', type=int, default=5, help='Delay between groups (seconds)')

    # Configuration
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')

    # Utility options
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Setup environment
    setup_environment()

    # Handle setup command
    if args.setup:
        print("🔧 Setting up Telegram Member Scraper...")
        config = Config()
        print("✅ Setup completed! Please edit config/settings.yaml with your API credentials.")
        return

    # Initialize CLI
    cli = TelegramScraperCLI()

    try:
        # Initialize scraper
        await cli.initialize(args.config)

        # Execute commands
        if args.group:
            await cli.scrape_single_group(
                args.group,
                limit=args.limit,
                export_format=args.format,
                analyze=bool(args.analyze)
            )

        elif args.groups:
            await cli.scrape_multiple_groups(
                args.groups,
                export_format=args.format,
                delay=args.delay,
                analyze=bool(args.analyze)
            )

        elif args.analyze and args.analyze != True:
            await cli.analyze_data(args.analyze)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        if console:
            console.print("\n⏹️ [yellow]Operation cancelled by user[/yellow]")
        else:
            print("\n⏹️ Operation cancelled by user")

    except Exception as e:
        if console:
            console.print(f"❌ [red]Unexpected error: {e}[/red]")
        else:
            print(f"❌ Unexpected error: {e}")

    finally:
        await cli.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)