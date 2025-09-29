#!/bin/bash
# Quick directory setup for vzoelscraper
# Fixes FileNotFoundError for log directories

echo "📁 Creating vzoelscraper directory structure..."

# Create all necessary directories
mkdir -p data/logs
mkdir -p data/exports
mkdir -p data/sessions
mkdir -p downloads
mkdir -p config

# Create empty log file if it doesn't exist
touch data/logs/scraper.log

# Set proper permissions
chmod 755 data/logs
chmod 644 data/logs/scraper.log

echo "✅ Directory structure created successfully!"
echo ""
echo "📂 Created directories:"
echo "   data/logs/       - Log files"
echo "   data/exports/    - Exported member data"
echo "   data/sessions/   - Telegram session files"
echo "   downloads/       - Downloaded files"
echo "   config/          - Configuration files"
echo ""
echo "🚀 You can now run: python scraper.py --groups groups.txt"