"""Core modules for Telegram Member Scraper"""

__all__ = ('TelegramMemberScraper', 'TelegramAnalyzer')


def __getattr__(name):
    if name == 'TelegramMemberScraper':
        from .scraper import TelegramMemberScraper as _TelegramMemberScraper
        return _TelegramMemberScraper
    if name == 'TelegramAnalyzer':
        from .analyzer import TelegramAnalyzer as _TelegramAnalyzer
        return _TelegramAnalyzer
    raise AttributeError(f"module 'src.core' has no attribute {name!r}")