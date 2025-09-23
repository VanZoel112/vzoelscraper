#!/usr/bin/env python3
"""
Configuration Management Module
Handles configuration loading and validation

Author: VanZoel112
Version: 1.0.0
"""

import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class TelegramConfig:
    """Telegram API configuration"""
    api_id: int
    api_hash: str
    session_name: str = "scraper_session"
    phone_number: Optional[str] = None


@dataclass
class ScrapingConfig:
    """Scraping behavior configuration"""
    delay_between_requests: float = 1.0
    batch_size: int = 100
    max_members_per_group: int = 10000
    timeout: int = 30
    retry_attempts: int = 3
    include_inactive: bool = True
    filter_bots: bool = False


@dataclass
class ExportConfig:
    """Export settings configuration"""
    default_format: str = "csv"
    include_photos: bool = False
    anonymize_data: bool = False
    export_directory: str = "data/exports"
    timestamp_files: bool = True


@dataclass
class AnalyticsConfig:
    """Analytics features configuration"""
    track_activity: bool = True
    estimate_demographics: bool = True
    calculate_engagement: bool = True
    extract_interests: bool = True
    detect_language: bool = True


class Config:
    """
    Centralized configuration management for the Telegram scraper

    Supports YAML, JSON, and environment variable configuration.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/settings.yaml"
        self.config_data = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file and environment variables"""
        # Load from file if exists
        if Path(self.config_path).exists():
            self._load_from_file()
        else:
            # Create default config if none exists
            self._create_default_config()

        # Override with environment variables
        self._load_from_env()

        # Validate configuration
        self._validate_config()

    def _load_from_file(self):
        """Load configuration from YAML or JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    self.config_data = yaml.safe_load(f) or {}
                elif self.config_path.endswith('.json'):
                    self.config_data = json.load(f) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {self.config_path}")

            print(f"✅ Configuration loaded from {self.config_path}")

        except Exception as e:
            print(f"⚠️ Error loading config file: {e}")
            self.config_data = {}

    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'telegram': {
                'api_id': 'YOUR_API_ID',
                'api_hash': 'YOUR_API_HASH',
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

        # Create config directory if it doesn't exist
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)

        # Save default config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        self.config_data = default_config
        print(f"📝 Default configuration created at {self.config_path}")
        print("⚠️ Please update the Telegram API credentials in the config file!")

    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'TELEGRAM_API_ID': 'telegram.api_id',
            'TELEGRAM_API_HASH': 'telegram.api_hash',
            'TELEGRAM_SESSION_NAME': 'telegram.session_name',
            'TELEGRAM_PHONE': 'telegram.phone_number',
            'SCRAPER_DELAY': 'scraping.delay_between_requests',
            'SCRAPER_BATCH_SIZE': 'scraping.batch_size',
            'SCRAPER_MAX_MEMBERS': 'scraping.max_members_per_group',
            'EXPORT_FORMAT': 'export.default_format',
            'EXPORT_DIR': 'export.export_directory'
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(config_path, value)

    def _set_nested_value(self, path: str, value: Any):
        """Set a nested configuration value using dot notation"""
        keys = path.split('.')
        current = self.config_data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)

        current[keys[-1]] = value

    def _validate_config(self):
        """Validate configuration values"""
        required_fields = [
            'telegram.api_id',
            'telegram.api_hash'
        ]

        for field in required_fields:
            value = self.get(field)
            if not value or value in ('YOUR_API_ID', 'YOUR_API_HASH'):
                raise ValueError(f"Required configuration field '{field}' is missing or not configured")

        # Validate data types
        try:
            api_id = self.get('telegram.api_id')
            if isinstance(api_id, str):
                self._set_nested_value('telegram.api_id', int(api_id))
        except ValueError:
            raise ValueError("telegram.api_id must be a valid integer")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        current = self.config_data

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        self._set_nested_value(key, value)

    def get_telegram_config(self) -> TelegramConfig:
        """Get Telegram configuration object"""
        return TelegramConfig(
            api_id=self.get('telegram.api_id'),
            api_hash=self.get('telegram.api_hash'),
            session_name=self.get('telegram.session_name', 'scraper_session'),
            phone_number=self.get('telegram.phone_number')
        )

    def get_scraping_config(self) -> ScrapingConfig:
        """Get scraping configuration object"""
        return ScrapingConfig(
            delay_between_requests=self.get('scraping.delay_between_requests', 1.0),
            batch_size=self.get('scraping.batch_size', 100),
            max_members_per_group=self.get('scraping.max_members_per_group', 10000),
            timeout=self.get('scraping.timeout', 30),
            retry_attempts=self.get('scraping.retry_attempts', 3),
            include_inactive=self.get('scraping.include_inactive', True),
            filter_bots=self.get('scraping.filter_bots', False)
        )

    def get_export_config(self) -> ExportConfig:
        """Get export configuration object"""
        return ExportConfig(
            default_format=self.get('export.default_format', 'csv'),
            include_photos=self.get('export.include_photos', False),
            anonymize_data=self.get('export.anonymize_data', False),
            export_directory=self.get('export.export_directory', 'data/exports'),
            timestamp_files=self.get('export.timestamp_files', True)
        )

    def get_analytics_config(self) -> AnalyticsConfig:
        """Get analytics configuration object"""
        return AnalyticsConfig(
            track_activity=self.get('analytics.track_activity', True),
            estimate_demographics=self.get('analytics.estimate_demographics', True),
            calculate_engagement=self.get('analytics.calculate_engagement', True),
            extract_interests=self.get('analytics.extract_interests', True),
            detect_language=self.get('analytics.detect_language', True)
        )

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            print(f"💾 Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary"""
        return self.config_data.copy()

    def __str__(self) -> str:
        """String representation of configuration"""
        # Hide sensitive data
        safe_config = self.config_data.copy()
        if 'telegram' in safe_config:
            safe_config['telegram'] = safe_config['telegram'].copy()
            if 'api_hash' in safe_config['telegram']:
                safe_config['telegram']['api_hash'] = '*' * 20

        return yaml.dump(safe_config, default_flow_style=False, indent=2)


# Global configuration instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def reload_config():
    """Reload configuration from file"""
    global _config_instance
    if _config_instance:
        _config_instance.load_config()


# Environment setup helper
def setup_environment():
    """Setup required directories and environment"""
    directories = [
        'config',
        'data/exports',
        'data/logs',
        'data/cache',
        'data/sessions'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("📁 Environment directories created")


if __name__ == "__main__":
    # Test configuration loading
    setup_environment()
    config = Config()
    print("Configuration loaded successfully!")
    print(config)