#!/usr/bin/env python3
"""
Rate Limiter Module
Implements intelligent rate limiting for Telegram API requests

Author: VanZoel112
Version: 1.0.0
"""

import asyncio
import time
from collections import deque
from typing import Optional, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Information about current rate limiting status"""
    requests_made: int
    time_window: float
    time_until_reset: float
    requests_remaining: int
    is_limited: bool


class RateLimiter:
    """
    Intelligent rate limiter for Telegram API requests

    Features:
    - Token bucket algorithm for smooth rate limiting
    - Adaptive delays based on API responses
    - FloodWait error handling
    - Multiple rate limit tiers
    """

    def __init__(
        self,
        max_requests: int = 30,
        time_window: float = 60.0,
        burst_limit: Optional[int] = None,
        adaptive: bool = True
    ):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            burst_limit: Maximum burst requests (None = max_requests)
            adaptive: Enable adaptive rate limiting
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_limit = burst_limit or max_requests
        self.adaptive = adaptive

        # Token bucket for smooth rate limiting
        self.tokens = float(max_requests)
        self.last_refill = time.time()

        # Request tracking
        self.request_times = deque()
        self.total_requests = 0

        # Adaptive rate limiting
        self.adaptive_delay = 0.0
        self.flood_wait_count = 0
        self.last_flood_wait = 0.0

        # Statistics
        self.stats = {
            'total_requests': 0,
            'rate_limited_requests': 0,
            'flood_waits': 0,
            'total_wait_time': 0.0
        }

    async def wait(self) -> float:
        """
        Wait if necessary to respect rate limits

        Returns:
            Time waited in seconds
        """
        start_time = time.time()

        # Refill tokens
        self._refill_tokens()

        # Check if we need to wait
        wait_time = self._calculate_wait_time()

        if wait_time > 0:
            logger.debug(f"⏳ Rate limiting: waiting {wait_time:.2f}s")
            self.stats['rate_limited_requests'] += 1
            self.stats['total_wait_time'] += wait_time
            await asyncio.sleep(wait_time)

        # Record request
        self._record_request()

        actual_wait = time.time() - start_time
        return actual_wait

    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate tokens to add
        tokens_to_add = elapsed * (self.max_requests / self.time_window)
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)

        self.last_refill = now

    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request"""
        # Check token bucket
        if self.tokens < 1:
            # Calculate time to get one token
            time_per_token = self.time_window / self.max_requests
            wait_time = time_per_token * (1 - self.tokens)
        else:
            wait_time = 0.0

        # Add adaptive delay if enabled
        if self.adaptive and self.adaptive_delay > 0:
            wait_time += self.adaptive_delay

        return wait_time

    def _record_request(self):
        """Record that a request was made"""
        now = time.time()

        # Update token bucket
        if self.tokens >= 1:
            self.tokens -= 1
        else:
            self.tokens = 0

        # Track request timing
        self.request_times.append(now)
        self.total_requests += 1
        self.stats['total_requests'] += 1

        # Clean old request times
        cutoff = now - self.time_window
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

    async def handle_flood_wait(self, wait_seconds: int):
        """
        Handle FloodWaitError from Telegram API

        Args:
            wait_seconds: Seconds to wait as specified by Telegram
        """
        logger.warning(f"🌊 FloodWait: {wait_seconds}s")

        self.flood_wait_count += 1
        self.last_flood_wait = time.time()
        self.stats['flood_waits'] += 1
        self.stats['total_wait_time'] += wait_seconds

        # Update adaptive delay
        if self.adaptive:
            self._update_adaptive_delay(wait_seconds)

        # Wait the required time plus small buffer
        await asyncio.sleep(wait_seconds + 1)

    def _update_adaptive_delay(self, flood_wait_seconds: int):
        """Update adaptive delay based on FloodWait experience"""
        # Increase adaptive delay exponentially
        if flood_wait_seconds > 0:
            self.adaptive_delay = min(
                self.adaptive_delay + 0.5,
                5.0  # Max 5 second adaptive delay
            )
        else:
            # Gradually reduce adaptive delay
            self.adaptive_delay = max(
                self.adaptive_delay - 0.1,
                0.0
            )

    def get_status(self) -> RateLimitInfo:
        """Get current rate limiting status"""
        now = time.time()

        # Clean old requests
        cutoff = now - self.time_window
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        requests_made = len(self.request_times)
        requests_remaining = max(0, self.max_requests - requests_made)

        # Calculate time until next window
        if self.request_times:
            time_until_reset = self.time_window - (now - self.request_times[0])
        else:
            time_until_reset = 0.0

        is_limited = self.tokens < 1 or self.adaptive_delay > 0

        return RateLimitInfo(
            requests_made=requests_made,
            time_window=self.time_window,
            time_until_reset=max(0, time_until_reset),
            requests_remaining=requests_remaining,
            is_limited=is_limited
        )

    def reset(self):
        """Reset rate limiter state"""
        self.tokens = float(self.max_requests)
        self.last_refill = time.time()
        self.request_times.clear()
        self.adaptive_delay = 0.0
        self.flood_wait_count = 0

    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        return self.stats.copy()

    def __str__(self) -> str:
        """String representation of rate limiter"""
        status = self.get_status()
        return (f"RateLimiter(requests: {status.requests_made}/{self.max_requests}, "
                f"tokens: {self.tokens:.1f}, adaptive_delay: {self.adaptive_delay:.1f}s)")


class TelegramRateLimiter:
    """
    Specialized rate limiter for Telegram API with multiple tiers

    Implements Telegram's documented rate limits:
    - 30 requests per second for bots
    - 20 requests per minute for user accounts
    - Special handling for different endpoint types
    """

    def __init__(self, account_type: str = "user"):
        """
        Initialize Telegram-specific rate limiter

        Args:
            account_type: "user" or "bot"
        """
        self.account_type = account_type

        # Configure rate limits based on account type
        if account_type == "bot":
            # Bot limits: 30 requests per second
            self.primary_limiter = RateLimiter(30, 1.0, adaptive=True)
            self.secondary_limiter = RateLimiter(1800, 60.0, adaptive=True)  # Minute limit
        else:
            # User limits: More conservative
            self.primary_limiter = RateLimiter(20, 60.0, adaptive=True)
            self.secondary_limiter = RateLimiter(300, 3600.0, adaptive=True)  # Hourly limit

        # Special limiters for different operations
        self.message_limiter = RateLimiter(3, 1.0)  # Messages: 3 per second
        self.media_limiter = RateLimiter(1, 2.0)    # Media: 1 per 2 seconds
        self.member_limiter = RateLimiter(10, 60.0) # Member operations: 10 per minute

    async def wait_for_request(self, request_type: str = "general") -> float:
        """
        Wait for appropriate rate limits based on request type

        Args:
            request_type: Type of request ("general", "message", "media", "members")

        Returns:
            Time waited in seconds
        """
        total_wait = 0.0

        # Always check primary and secondary limiters
        total_wait += await self.primary_limiter.wait()
        total_wait += await self.secondary_limiter.wait()

        # Check specific limiter based on request type
        if request_type == "message":
            total_wait += await self.message_limiter.wait()
        elif request_type == "media":
            total_wait += await self.media_limiter.wait()
        elif request_type == "members":
            total_wait += await self.member_limiter.wait()

        return total_wait

    async def handle_flood_wait(self, wait_seconds: int, request_type: str = "general"):
        """Handle FloodWaitError for specific request type"""
        await self.primary_limiter.handle_flood_wait(wait_seconds)

        # Also update specific limiter
        if request_type == "message":
            await self.message_limiter.handle_flood_wait(wait_seconds // 2)
        elif request_type == "media":
            await self.media_limiter.handle_flood_wait(wait_seconds)
        elif request_type == "members":
            await self.member_limiter.handle_flood_wait(wait_seconds)

    def get_comprehensive_status(self) -> Dict:
        """Get status for all rate limiters"""
        return {
            'account_type': self.account_type,
            'primary': self.primary_limiter.get_status(),
            'secondary': self.secondary_limiter.get_status(),
            'message': self.message_limiter.get_status(),
            'media': self.media_limiter.get_status(),
            'members': self.member_limiter.get_status(),
            'stats': {
                'primary': self.primary_limiter.get_stats(),
                'secondary': self.secondary_limiter.get_stats(),
                'message': self.message_limiter.get_stats(),
                'media': self.media_limiter.get_stats(),
                'members': self.member_limiter.get_stats()
            }
        }


# Context manager for rate-limited operations
class RateLimitedOperation:
    """Context manager for rate-limited operations"""

    def __init__(self, rate_limiter: RateLimiter, operation_type: str = "general"):
        self.rate_limiter = rate_limiter
        self.operation_type = operation_type
        self.start_time = None
        self.wait_time = 0.0

    async def __aenter__(self):
        self.start_time = time.time()
        if isinstance(self.rate_limiter, TelegramRateLimiter):
            self.wait_time = await self.rate_limiter.wait_for_request(self.operation_type)
        else:
            self.wait_time = await self.rate_limiter.wait()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type and "FloodWaitError" in str(exc_type):
            # Extract wait time from FloodWaitError
            if hasattr(exc_val, 'seconds'):
                wait_seconds = exc_val.seconds
                await self.rate_limiter.handle_flood_wait(wait_seconds, self.operation_type)


# Usage example
async def example_usage():
    """Example of how to use the rate limiter"""
    limiter = TelegramRateLimiter("user")

    # Example 1: Simple rate limiting
    await limiter.wait_for_request("members")
    print("Making member request...")

    # Example 2: Using context manager
    async with RateLimitedOperation(limiter, "message") as op:
        print("Sending message...")

    # Example 3: Handling flood wait
    try:
        # Simulate API call
        pass
    except Exception as e:
        if "FloodWaitError" in str(e):
            await limiter.handle_flood_wait(30, "members")

    print("Rate limiter status:", limiter.get_comprehensive_status())


if __name__ == "__main__":
    asyncio.run(example_usage())