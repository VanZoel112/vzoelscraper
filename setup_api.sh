#!/bin/bash
# Setup API credentials for vzoelscraper

echo "🔑 Telegram API Setup"
echo "====================="
echo ""
echo "You need API credentials from https://my.telegram.org"
echo ""
echo "Steps to get API credentials:"
echo "1. Go to https://my.telegram.org"
echo "2. Login with your phone number (+6283199218070)"
echo "3. Go to 'API development tools'"
echo "4. Create an application (any name is fine)"
echo "5. Copy the API ID and API Hash"
echo ""

# Check if config file exists
CONFIG_FILE="config/target_config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "Enter your API credentials:"
echo ""

# Get API ID
read -p "API ID (numeric): " API_ID
if [ -z "$API_ID" ]; then
    echo "❌ API ID cannot be empty"
    exit 1
fi

# Get API Hash
read -p "API Hash (string): " API_HASH
if [ -z "$API_HASH" ]; then
    echo "❌ API Hash cannot be empty"
    exit 1
fi

# Update config file
echo "📝 Updating configuration file..."

# Create backup
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"

# Replace placeholders
sed -i "s/YOUR_API_ID_HERE/$API_ID/g" "$CONFIG_FILE"
sed -i "s/YOUR_API_HASH_HERE/$API_HASH/g" "$CONFIG_FILE"

echo "✅ Configuration updated successfully!"
echo ""
echo "📋 You can now run:"
echo "   python scraper.py --config config/target_config.yaml"
echo ""
echo "🔒 Your API credentials are saved in: $CONFIG_FILE"