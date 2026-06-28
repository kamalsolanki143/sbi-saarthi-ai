"""
SAARTHI AI — Formatters
Shared formatting utilities for currency, dates, and Indian conventions.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_inr(amount: float) -> str:
    """
    Format a float as Indian Rupees with the ₹ symbol.
    Uses Indian numbering: 1,00,000 (lakhs) not 100,000.

    >>> format_inr(125000)
    '₹1,25,000.00'
    """
    # Split integer and decimal parts
    amount_str = f"{amount:.2f}"
    integer_part, decimal_part = amount_str.split(".")

    # Convert to Indian number format
    s = integer_part
    if len(s) > 3:
        last_three = s[-3:]
        rest = s[:-3]
        # Group remaining digits in pairs from right
        groups = []
        while len(rest) > 2:
            groups.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.append(rest)
        groups.reverse()
        formatted = ",".join(groups) + "," + last_three
    else:
        formatted = s

    return f"₹{formatted}.{decimal_part}"


def format_inr_short(amount: float) -> str:
    """
    Short-form Indian currency (for display cards).

    >>> format_inr_short(125000)  -> '₹1.25 Lakh'
    >>> format_inr_short(12500000) -> '₹1.25 Crore'
    """
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Crore"
    if amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} Lakh"
    if amount >= 1_000:
        return f"₹{amount / 1_000:.1f}K"
    return f"₹{amount:.0f}"


def format_date(dt: datetime, locale: str = "en") -> str:
    """Format a datetime for display (DD MMM YYYY)."""
    return dt.strftime("%d %b %Y")


def format_datetime(dt: datetime) -> str:
    """Format a datetime for display (DD MMM YYYY, HH:MM)."""
    return dt.strftime("%d %b %Y, %H:%M")


def format_tenure(months: int) -> str:
    """
    Convert months to a human-readable tenure string.

    >>> format_tenure(12) -> '1 Year'
    >>> format_tenure(18) -> '1 Year 6 Months'
    >>> format_tenure(6) -> '6 Months'
    """
    years = months // 12
    rem_months = months % 12

    if years > 0 and rem_months > 0:
        return f"{years} Year{'s' if years > 1 else ''} {rem_months} Month{'s' if rem_months > 1 else ''}"
    if years > 0:
        return f"{years} Year{'s' if years > 1 else ''}"
    return f"{rem_months} Month{'s' if rem_months > 1 else ''}"


def format_interest_rate(rate: float) -> str:
    """Format interest rate as percentage string.

    >>> format_interest_rate(6.8) -> '6.80% p.a.'
    """
    return f"{rate:.2f}% p.a."


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text for compressed-text / basic network mode."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def mask_account_number(account_number: str) -> str:
    """Mask an account number for display — show only last 4 digits."""
    if len(account_number) <= 4:
        return account_number
    return "*" * (len(account_number) - 4) + account_number[-4:]


def mask_phone(phone: str) -> str:
    """Mask phone number for display — show only last 4 digits."""
    if len(phone) <= 4:
        return phone
    return "*" * (len(phone) - 4) + phone[-4:]
