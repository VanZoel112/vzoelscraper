# 🔧 Troubleshooting Guide

## Common Installation Issues

### ❌ "FileNotFoundError: data/logs/scraper.log" Error

**Problem**: Getting `FileNotFoundError: [Errno 2] No such file or directory: 'data/logs/scraper.log'`

**Solution**:
```bash
# Quick fix - create directories
mkdir -p data/logs data/exports downloads
touch data/logs/scraper.log

# Or run the setup script
chmod +x setup_dirs.sh
./setup_dirs.sh
```

**Why**: The scraper needs directory structure that may not exist

### ❌ "No module named 'yaml'" Error

**Problem**: Getting `ModuleNotFoundError: No module named 'yaml'`

**Solution**:
```bash
# Install PyYAML (not 'yaml')
pip install PyYAML

# Or force reinstall
pip install --force-reinstall PyYAML>=6.0.0
```

**Why**: The package name is `PyYAML` but imports as `yaml`

### ❌ "Could not find a version that satisfies the requirement yaml"

**Problem**: Trying to install `yaml` package

**Solution**:
```bash
# DON'T do this:
pip install yaml  # ❌ Wrong

# DO this instead:
pip install PyYAML  # ✅ Correct
```

### 🚀 Quick Fix Script

Run the installation script:
```bash
chmod +x install_deps.sh
./install_deps.sh
```

## Virtual Environment Issues

### Create Virtual Environment
```bash
# Python 3.8+
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Activate Existing Environment
```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## Dependency Issues

### Core Dependencies Installation Order
```bash
# 1. Install core first
pip install PyYAML telethon pyrogram

# 2. Install utilities
pip install aiofiles python-dotenv pandas

# 3. Install all requirements
pip install -r requirements.txt
```

### Version Conflicts
```bash
# Clear pip cache
pip cache purge

# Reinstall problematic packages
pip uninstall PyYAML -y
pip install PyYAML>=6.0.0
```

## Running the Scraper

### Basic Usage
```bash
# Make sure you're in virtual environment
source .venv/bin/activate

# Run with groups file
python scraper.py --groups groups.txt

# Run with config
python scraper.py --config config/scraper_config.yaml
```

### Configuration File
Create `config/scraper_config.yaml`:
```yaml
telegram:
  api_id: YOUR_API_ID
  api_hash: "YOUR_API_HASH"
  session_name: "scraper_session"

scraper:
  max_members: 1000
  delay_min: 1
  delay_max: 3
  output_format: "excel"
```

## File Permissions

### Make Scripts Executable
```bash
chmod +x install_deps.sh
chmod +x scraper.py
```

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, Windows
- **RAM**: Minimum 512MB, Recommended 1GB+
- **Storage**: 100MB+ for dependencies

## Support

If you still have issues:

1. **Check Python version**: `python --version`
2. **Check pip version**: `pip --version`
3. **Reinstall dependencies**: `./install_deps.sh`
4. **Create new virtual environment**
5. **Check system permissions**

## Contact

- **GitHub Issues**: Report bugs and issues
- **Documentation**: Check README.md for detailed setup
- **Version**: v1.0.0 by VanZoel112