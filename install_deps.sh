#!/bin/bash
# Installation script for vzoelscraper dependencies
# Fixes common installation issues

echo "🚀 Installing vzoelscraper dependencies..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "📚 Installing core dependencies..."
pip install PyYAML>=6.0.0
pip install telethon>=1.35.0
pip install pyrogram>=2.0.0
pip install aiofiles>=23.0.0
pip install python-dotenv>=1.0.0

# Install all requirements
echo "📋 Installing all requirements..."
pip install -r requirements.txt

echo "✅ Installation complete!"
echo ""
echo "🎯 To run the scraper:"
echo "   python scraper.py --groups groups.txt"
echo ""
echo "🔧 If you still get YAML errors, run:"
echo "   pip install --force-reinstall PyYAML"