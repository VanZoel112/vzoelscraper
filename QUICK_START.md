# 🚀 Quick Start Guide

## ✅ Your scraper is now working!

You successfully:
- ✅ Fixed YAML dependencies
- ✅ Created directory structure
- ✅ Authenticated with Telegram as **R (@koncillll)**
- ✅ Initialized scraper successfully

## 📝 Next Steps

### 1. Configure Target Groups

Edit the `groups.txt` file:
```bash
nano groups.txt
```

Add your target groups (one per line):
```
@your_target_group
https://t.me/another_group
group_username
```

### 2. Run the Scraper

```bash
# Basic run
python scraper.py --groups groups.txt

# With custom config
python scraper.py --config config/settings.yaml

# With specific output format
python scraper.py --groups groups.txt --format excel
```

### 3. Example Groups File

Copy from example:
```bash
cp groups_example.txt groups.txt
nano groups.txt  # Edit with your groups
```

## 📊 Output Formats

The scraper supports multiple output formats:
- **Excel** (.xlsx) - Default, best for analysis
- **CSV** (.csv) - Universal compatibility
- **JSON** (.json) - For developers
- **HTML** (.html) - For web viewing

## 🛡️ Important Notes

- **Privacy**: Only scrape groups where you have permission
- **Rate Limits**: The scraper includes automatic rate limiting
- **ToS Compliance**: Respect Telegram's Terms of Service
- **Data Security**: Handle exported data responsibly

## 📁 Output Location

Scraped data will be saved to:
- `data/exports/` - Member data files
- `data/logs/` - Log files
- `downloads/` - Any downloaded content

## 🔧 Troubleshooting

If you encounter issues:
1. Check `data/logs/scraper.log` for errors
2. Run `./setup_dirs.sh` if directories missing
3. See `TROUBLESHOOTING.md` for common fixes

## 🎯 Ready to Use!

Your scraper is fully operational. Just add your target groups to `groups.txt` and run!