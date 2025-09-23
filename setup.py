#!/usr/bin/env python3
"""
Setup Script for Telegram Member Scraper SMM
Handles installation, configuration, and first-time setup

Author: VanZoel112
Version: 1.0.0
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any

def print_banner():
    """Display setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🚀 TELEGRAM MEMBER SCRAPER FOR SMM - SETUP              ║
║                                                                  ║
║        Professional-grade member extraction tool                 ║
║        Created by VanZoel112                                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = [
        'config',
        'data/exports',
        'data/logs',
        'data/cache',
        'data/sessions',
        'docs',
        'tests'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")

    try:
        # Read requirements
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip()

        # Install packages
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed successfully!")

    except subprocess.CalledProcessError:
        print("⚠️ Some dependencies failed to install. Please install manually:")
        print("pip install -r requirements.txt")
    except FileNotFoundError:
        print("⚠️ requirements.txt not found. Creating basic requirements...")
        create_basic_requirements()

def create_basic_requirements():
    """Create basic requirements file if missing"""
    basic_requirements = """
telethon>=1.35.0
asyncio-throttle>=1.0.0
aiofiles>=23.0.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
openpyxl>=3.1.0
rich>=13.0.0
click>=8.1.0
""".strip()

    with open('requirements.txt', 'w') as f:
        f.write(basic_requirements)
    print("📝 Created basic requirements.txt")

def get_telegram_credentials():
    """Get Telegram API credentials from user"""
    print("\n🔐 Telegram API Credentials Setup")
    print("To get your credentials:")
    print("1. Go to https://my.telegram.org")
    print("2. Login with your phone number")
    print("3. Go to 'API Development Tools'")
    print("4. Create a new application")
    print("5. Copy your api_id and api_hash")
    print()

    while True:
        api_id = input("Enter your API ID: ").strip()
        if api_id.isdigit():
            break
        print("❌ API ID must be a number!")

    while True:
        api_hash = input("Enter your API Hash: ").strip()
        if len(api_hash) == 32:  # Typical hash length
            break
        print("❌ API Hash should be 32 characters long!")

    phone = input("Enter your phone number (optional, for session): ").strip()

    return {
        'api_id': int(api_id),
        'api_hash': api_hash,
        'phone_number': phone if phone else None
    }

def create_configuration(telegram_creds: Dict[str, Any]):
    """Create configuration file"""
    config = {
        'telegram': {
            'api_id': telegram_creds['api_id'],
            'api_hash': telegram_creds['api_hash'],
            'session_name': 'scraper_session'
        },
        'scraping': {
            'delay_between_requests': 1.0,
            'batch_size': 100,
            'max_members_per_group': 10000,
            'timeout': 30,
            'retry_attempts': 3,
            'include_inactive': True,
            'filter_bots': False
        },
        'export': {
            'default_format': 'csv',
            'include_photos': False,
            'anonymize_data': False,
            'export_directory': 'data/exports',
            'timestamp_files': True
        },
        'analytics': {
            'track_activity': True,
            'estimate_demographics': True,
            'calculate_engagement': True,
            'extract_interests': True,
            'detect_language': True
        },
        'logging': {
            'level': 'INFO',
            'file': 'data/logs/scraper.log',
            'max_size': '10MB',
            'backup_count': 5
        }
    }

    # Add phone number if provided
    if telegram_creds.get('phone_number'):
        config['telegram']['phone_number'] = telegram_creds['phone_number']

    # Save configuration
    config_path = Path('config/settings.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print(f"✅ Configuration saved to {config_path}")

def create_sample_files():
    """Create sample configuration files"""

    # Sample groups file
    sample_groups = """# Sample groups to scrape
# Add one group per line (username or invite link)
@cryptogroup
@tradinggroup
@techgroup
@marketinggroup
# https://t.me/+invite_link_here
"""

    with open('config/groups.txt', 'w') as f:
        f.write(sample_groups.strip())
    print("📝 Created sample groups file: config/groups.txt")

    # Sample .env file
    env_content = """# Environment variables for Telegram Scraper
# You can use these instead of config file

# Telegram API Credentials
# TELEGRAM_API_ID=your_api_id
# TELEGRAM_API_HASH=your_api_hash
# TELEGRAM_SESSION_NAME=scraper_session

# Scraping Settings
# SCRAPER_DELAY=1.0
# SCRAPER_BATCH_SIZE=100
# SCRAPER_MAX_MEMBERS=10000

# Export Settings
# EXPORT_FORMAT=csv
# EXPORT_DIR=data/exports

# Logging
# LOG_LEVEL=INFO
"""

    with open('.env.example', 'w') as f:
        f.write(env_content.strip())
    print("📝 Created environment template: .env.example")

def create_docker_files():
    """Create Docker configuration files"""

    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/exports data/logs data/cache config

# Set environment variables
ENV PYTHONPATH=/app

# Run the scraper
CMD ["python", "scraper.py", "--help"]
"""

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)

    docker_compose = """version: '3.8'

services:
  telegram-scraper:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
    stdin_open: true
    tty: true
"""

    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)

    print("🐳 Created Docker configuration files")

def create_systemd_service():
    """Create systemd service file for Linux"""
    if os.name != 'posix':
        return

    current_dir = os.getcwd()
    user = os.getenv('USER', 'telegram-scraper')

    service_content = f"""[Unit]
Description=Telegram Member Scraper SMM
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={current_dir}
ExecStart=/usr/bin/python3 {current_dir}/scraper.py --help
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_file = Path('telegram-scraper.service')
    with open(service_file, 'w') as f:
        f.write(service_content)

    print(f"🔧 Created systemd service file: {service_file}")
    print(f"To install: sudo cp {service_file} /etc/systemd/system/")
    print("To enable: sudo systemctl enable telegram-scraper")

def create_startup_scripts():
    """Create startup scripts for different platforms"""

    # Linux/macOS startup script
    bash_script = """#!/bin/bash
# Telegram Member Scraper Startup Script

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the scraper
python3 scraper.py "$@"
"""

    with open('start.sh', 'w') as f:
        f.write(bash_script)
    os.chmod('start.sh', 0o755)

    # Windows batch script
    batch_script = """@echo off
REM Telegram Member Scraper Startup Script

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
)

REM Run the scraper
python scraper.py %*
pause
"""

    with open('start.bat', 'w') as f:
        f.write(batch_script)

    print("🚀 Created startup scripts: start.sh, start.bat")

def setup_git_repository():
    """Setup git repository with proper .gitignore"""
    gitignore_content = """# Telegram Scraper .gitignore

# Sensitive configuration
config/settings.yaml
.env
*.session
*.session-journal

# Data files
data/exports/*.csv
data/exports/*.json
data/exports/*.xlsx
data/logs/*.log
data/cache/*
data/sessions/*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/

# Coverage
.coverage
htmlcov/

# Docker
.dockerignore
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    print("📝 Created .gitignore file")

def test_installation():
    """Test if installation was successful"""
    print("\n🧪 Testing installation...")

    try:
        # Test imports
        import telethon
        import yaml
        import asyncio
        print("✅ Core dependencies imported successfully")

        # Test configuration loading
        from src.utils.config import Config
        config = Config('config/settings.yaml')
        print("✅ Configuration loading test passed")

        # Test scraper initialization (without connecting)
        from src.core.scraper import TelegramMemberScraper
        scraper = TelegramMemberScraper('config/settings.yaml')
        print("✅ Scraper initialization test passed")

        print("🎉 Installation test completed successfully!")

    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        print("Please check your configuration and dependencies")

def print_usage_guide():
    """Print usage guide"""
    guide = """
🎯 QUICK START GUIDE

1. Basic Usage:
   python scraper.py --group @cryptogroup --limit 1000

2. Batch Scraping:
   python scraper.py --groups config/groups.txt --format xlsx

3. With Analysis:
   python scraper.py --group @tradinggroup --analyze

4. Analysis Only:
   python scraper.py --analyze data/exports/members_data.json

5. Help:
   python scraper.py --help

📚 Configuration:
   - Edit config/settings.yaml for detailed settings
   - Add groups to config/groups.txt for batch processing
   - Check data/logs/ for detailed logs

🔗 Documentation:
   - GitHub: https://github.com/VanZoel112/telegram-member-scraper-smm
   - Issues: https://github.com/VanZoel112/telegram-member-scraper-smm/issues

Happy scraping! 🚀
"""
    print(guide)

def main():
    """Main setup function"""
    print_banner()

    print("Starting setup process...\n")

    # Step 1: Check Python version
    check_python_version()

    # Step 2: Create directories
    print("\n📁 Creating directories...")
    create_directories()

    # Step 3: Install dependencies
    print("\n📦 Setting up dependencies...")
    install_dependencies()

    # Step 4: Get Telegram credentials
    print("\n🔐 Configuring Telegram API...")
    telegram_creds = get_telegram_credentials()

    # Step 5: Create configuration
    print("\n⚙️ Creating configuration...")
    create_configuration(telegram_creds)

    # Step 6: Create sample files
    print("\n📝 Creating sample files...")
    create_sample_files()

    # Step 7: Create additional files
    print("\n🔧 Creating additional configuration...")
    create_docker_files()
    create_startup_scripts()
    setup_git_repository()

    # Step 8: Test installation
    test_installation()

    # Step 9: Show usage guide
    print_usage_guide()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)