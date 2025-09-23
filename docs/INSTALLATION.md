# 📥 Installation Guide

Complete installation guide for Telegram Member Scraper SMM.

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, Windows
- **RAM**: Minimum 512MB, Recommended 2GB+
- **Storage**: 500MB for installation + data storage

## 🚀 Quick Installation

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/VanZoel112/telegram-member-scraper-smm.git
cd telegram-member-scraper-smm

# Run automated setup
python setup.py
```

The setup script will:
- ✅ Check Python version compatibility
- 📁 Create necessary directories
- 📦 Install all dependencies
- 🔐 Guide you through API configuration
- 📝 Create sample configuration files

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/VanZoel112/telegram-member-scraper-smm.git
cd telegram-member-scraper-smm

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p config data/{exports,logs,cache,sessions}

# Copy configuration template
cp config/settings.yaml.example config/settings.yaml
```

## 🔐 Telegram API Setup

### Step 1: Get API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Click "API Development Tools"
4. Create a new application:
   - **App title**: Telegram Member Scraper
   - **Short name**: scraper-smm
   - **Platform**: Desktop
   - **Description**: Member scraper for SMM research

5. Save your `api_id` and `api_hash`

### Step 2: Configure Credentials

Edit `config/settings.yaml`:

```yaml
telegram:
  api_id: YOUR_API_ID_HERE
  api_hash: YOUR_API_HASH_HERE
  session_name: scraper_session
```

Or use environment variables:

```bash
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash
```

## 🐳 Docker Installation

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/VanZoel112/telegram-member-scraper-smm.git
cd telegram-member-scraper-smm

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run with Docker Compose
docker-compose up -d
```

### Using Dockerfile

```bash
# Build image
docker build -t telegram-scraper-smm .

# Run container
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -e TELEGRAM_API_ID=your_api_id \
  -e TELEGRAM_API_HASH=your_api_hash \
  telegram-scraper-smm
```

## 📱 Termux Installation (Android)

```bash
# Update Termux
pkg update && pkg upgrade

# Install Python and Git
pkg install python git

# Clone repository
git clone https://github.com/VanZoel112/telegram-member-scraper-smm.git
cd telegram-member-scraper-smm

# Install dependencies (some may need compilation)
pip install -r requirements.txt

# Run setup
python setup.py
```

**Note**: Some packages may require compilation on Termux. Install build tools if needed:
```bash
pkg install clang openssl-dev libffi-dev
```

## 🖥️ Service Installation

### Systemd Service (Linux)

```bash
# After installation, copy service file
sudo cp telegram-scraper.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable telegram-scraper
sudo systemctl start telegram-scraper

# Check status
sudo systemctl status telegram-scraper
```

### Windows Service

Use NSSM (Non-Sucking Service Manager):

```cmd
# Download NSSM and add to PATH
nssm install TelegramScraper

# Set application path
nssm set TelegramScraper Application "C:\path\to\python.exe"
nssm set TelegramScraper AppParameters "C:\path\to\scraper.py"

# Start service
nssm start TelegramScraper
```

## 🔧 Configuration

### Basic Configuration

Edit `config/settings.yaml`:

```yaml
# Telegram API
telegram:
  api_id: YOUR_API_ID
  api_hash: YOUR_API_HASH

# Scraping behavior
scraping:
  delay_between_requests: 1.0
  max_members_per_group: 10000

# Export settings
export:
  default_format: csv
  export_directory: data/exports
```

### Environment Variables

Create `.env` file:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
SCRAPER_DELAY=1.0
EXPORT_FORMAT=csv
```

## 🧪 Testing Installation

```bash
# Test basic functionality
python scraper.py --help

# Test configuration
python -c "from src.utils.config import Config; print('✅ Config OK')"

# Test Telegram connection (will prompt for phone)
python scraper.py --group @telegram --limit 10
```

## 🔍 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Ensure you're in the right directory
cd telegram-member-scraper-smm

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**2. API Credentials Error**
```
✅ Check config/settings.yaml has correct credentials
✅ Verify API ID is numeric (no quotes in YAML)
✅ Ensure API hash is exactly 32 characters
```

**3. Permission Errors**
```bash
# Create directories with proper permissions
mkdir -p data/{exports,logs,cache,sessions}
chmod 755 data/
```

**4. Termux Compilation Issues**
```bash
# Install build dependencies
pkg install clang openssl-dev libffi-dev rust

# Try installing problematic packages individually
pip install --no-cache-dir telethon
```

**5. Rate Limiting Issues**
```yaml
# Adjust in config/settings.yaml
scraping:
  delay_between_requests: 2.0  # Increase delay
rate_limiting:
  max_requests_per_minute: 10  # Reduce requests
```

### Getting Help

1. **Check Logs**: `data/logs/scraper.log`
2. **GitHub Issues**: [Report Issues](https://github.com/VanZoel112/telegram-member-scraper-smm/issues)
3. **Documentation**: [Wiki](https://github.com/VanZoel112/telegram-member-scraper-smm/wiki)
4. **Telegram Support**: [@VzoelSupport](https://t.me/VzoelSupport)

## 🔄 Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Check for configuration changes
diff config/settings.yaml config/settings.yaml.example
```

## 🗑️ Uninstallation

```bash
# Stop services
sudo systemctl stop telegram-scraper
sudo systemctl disable telegram-scraper

# Remove files
rm -rf telegram-member-scraper-smm/

# Remove virtual environment
rm -rf venv/

# Remove systemd service
sudo rm /etc/systemd/system/telegram-scraper.service
```

---

**Next Steps**: After installation, check out the [Usage Guide](USAGE.md) to start scraping!