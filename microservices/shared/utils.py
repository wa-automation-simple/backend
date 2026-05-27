"""
Utility functions for the application
"""
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def calculate_token_cost(tokens: int, price_per_1000: float = 10.0) -> float:
    """Calculate cost for token usage with markup"""
    return (tokens / 1000) * price_per_1000


def generate_recovery_link(phone_number: str) -> str:
    """Generate WhatsApp recovery link"""
    # WhatsApp ban appeal link format
    return f"https://wa.me/+{phone_number}?text=Please%20review%20my%20account"


def get_warming_delays(level: int) -> tuple:
    """Get min and max delays based on warming level (1-10)"""
    # Lower levels have longer delays to appear more natural
    base_delay = 300 - (level * 25)  # 5 min to 30 sec
    min_delay = max(30, base_delay)
    max_delay = min_delay + 60
    return min_delay, max_delay


def get_warming_message_limit(level: int) -> int:
    """Get message limit per day based on warming level"""
    # Gradual increase from 10 to 200 messages per day
    return min(200, 10 + (level * 20))


def is_within_business_hours(hour: Optional[int] = None) -> bool:
    """Check if current time is within business hours (8 AM - 8 PM)"""
    if hour is None:
        hour = datetime.now().hour
    return 8 <= hour <= 20


def randomize_delay(min_seconds: int, max_seconds: int) -> int:
    """Generate a random delay within range"""
    return random.randint(min_seconds, max_seconds)


def parse_phone_number(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    # Ensure it starts with +
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    return cleaned


def estimate_ai_tokens(text: str) -> int:
    """Estimate token count for text (rough approximation)"""
    # Average 4 characters per token
    return len(text) // 4 + 1
