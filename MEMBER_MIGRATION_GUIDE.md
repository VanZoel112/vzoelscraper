# 🎯 Member Migration Operation Guide

## Target Configuration

**🎯 Target Group (Injection Destination):**
- `https://t.me/+3_lpGQGGGeA2NWJl`

**📥 Source Groups (Member Extraction):**
- `https://t.me/cari_temen_random_pacar`
- `https://t.me/friendwithbenefitbase`
- `https://t.me/fwbbase2`

## 📋 Step-by-Step Process

### Step 1: Scrape Members from Source Groups

```bash
# Run the scraper to extract members
python scraper.py --groups groups.txt --config config/target_config.yaml

# This will create export files in data/exports/
# Example: members_2024-09-29_10-30-45.xlsx
```

### Step 2: Review Scraped Data

```bash
# Check export directory
ls data/exports/

# View log for any issues
tail -f data/logs/scraper.log
```

### Step 3: Invite Members to Target Group

```bash
# Run invitation script
python invite_members.py

# Monitor progress
tail -f data/logs/invite_members.log
```

## ⚠️ Important Safety Settings

### Rate Limiting (CRITICAL)
- **30 seconds** between each invitation
- **Maximum 50 invitations** per session
- **100 members** per hour limit
- **500 members** daily limit

### Privacy Compliance
- Only invites members who allow it
- Respects user privacy settings
- Logs all actions for transparency
- Excludes bots automatically

## 🛡️ Security Recommendations

### Before Starting:
1. **Verify Permissions**: Ensure you're admin in target group
2. **Check Group Rules**: Respect group guidelines
3. **Test with Small Batch**: Start with 10-20 members
4. **Monitor for Restrictions**: Watch for Telegram limits

### During Operation:
- **Don't Rush**: Maintain delays between invitations
- **Monitor Logs**: Check for errors or restrictions
- **Stop if Issues**: Halt if getting flood errors
- **Respect Limits**: Don't exceed daily quotas

## 📊 Expected Results

### Scraping Phase:
- **3 source groups** will be analyzed
- **~500-1500 members** estimated total
- **Active members only** (filtered)
- **Export formats**: Excel, CSV, JSON

### Invitation Phase:
- **Success Rate**: ~60-80% typical
- **Failed Reasons**: Privacy restrictions, inactive users
- **Duration**: 2-4 hours for 100 members (with delays)
- **Logs**: Detailed success/failure tracking

## 🚨 Error Handling

### Common Issues & Solutions:

**FloodWaitError**: Too many requests
```bash
# Solution: Wait the specified time, script handles automatically
# The script will pause and resume after rate limit expires
```

**UserPrivacyRestrictedError**: User blocks invitations
```bash
# Solution: Automatic skip, normal behavior
# Some users don't allow group invitations
```

**PeerFloodError**: Account temporarily restricted
```bash
# Solution: Stop for 24 hours, resume later
# This indicates you've hit Telegram's daily limit
```

## 📝 Usage Commands

### Quick Start:
```bash
# 1. Scrape members
python scraper.py --groups groups.txt

# 2. Invite members
python invite_members.py
```

### With Custom Settings:
```bash
# Scrape with specific config
python scraper.py --config config/target_config.yaml

# Invite specific file
python invite_members.py --export-file members_2024-09-29.json
```

## 📁 File Locations

- **Groups Config**: `groups.txt`
- **Target Config**: `config/target_config.yaml`
- **Scraped Data**: `data/exports/`
- **Logs**: `data/logs/`
- **Sessions**: `data/sessions/`

## 🎯 Final Notes

1. **Legal Compliance**: Ensure you have rights to invite members
2. **Group Rules**: Respect target group guidelines
3. **User Consent**: Only invite users who would appreciate it
4. **Telegram ToS**: Follow Telegram's Terms of Service
5. **Rate Limiting**: Always respect API limits

**This process is designed to be safe, compliant, and effective for legitimate member growth.**