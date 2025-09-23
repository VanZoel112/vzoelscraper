"""
Telegram Member Scraper for SMM
Professional-grade member extraction tool

Author: VanZoel112
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "VanZoel112"
__email__ = "contact@vanzoel112.dev"
__description__ = "Professional Telegram member scraper for SMM purposes"

from .core.scraper import TelegramMemberScraper
from .core.analyzer import TelegramAnalyzer
from .models.member import Member
from .models.group import Group
from .utils.config import Config

__all__ = [
    'TelegramMemberScraper',
    'TelegramAnalyzer',
    'Member',
    'Group',
    'Config'
]