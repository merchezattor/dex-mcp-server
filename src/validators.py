"""
Input validation utilities for the DEX MCP server.
"""
import re
from typing import Any

from .config import VALID_INTERVALS
from .exceptions import ValidationError


# Symbol pattern validation (basic validation for common trading pairs)
SYMBOL_PATTERN = re.compile(r'^[A-Z0-9]{6,12}$')


def validate_symbol(symbol: Any) -> str:
    """
    Validate and normalize trading symbol.
    
    Args:
        symbol: The symbol to validate
        
    Returns:
        Normalized symbol string
        
    Raises:
        ValidationError: If symbol format is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string", field="symbol")
    
    symbol = symbol.upper().strip()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(f"Invalid symbol format: {symbol}", field="symbol")
    
    return symbol


def validate_interval(interval: Any) -> str:
    """
    Validate trading interval.
    
    Args:
        interval: The interval to validate
        
    Returns:
        Validated interval string
        
    Raises:
        ValidationError: If interval is invalid
    """
    if not isinstance(interval, str):
        raise ValidationError("Interval must be a string", field="interval")
        
    if interval not in VALID_INTERVALS:
        valid_intervals_str = ', '.join(sorted(VALID_INTERVALS))
        raise ValidationError(
            f"Invalid interval: {interval}. Valid intervals: {valid_intervals_str}",
            field="interval"
        )
    return interval


def validate_limit(limit: Any, max_limit: int = 1000) -> int:
    """
    Validate limit parameter.
    
    Args:
        limit: The limit to validate
        max_limit: Maximum allowed limit
        
    Returns:
        Validated limit integer
        
    Raises:
        ValidationError: If limit is invalid
    """
    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            raise ValidationError("Limit must be a positive integer", field="limit")
    
    if limit <= 0:
        raise ValidationError("Limit must be a positive integer", field="limit")
    
    if limit > max_limit:
        raise ValidationError(f"Limit cannot exceed {max_limit}", field="limit")
    
    return limit


def validate_required_fields(data: dict, required_fields: list) -> None:
    """
    Validate that all required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            field="required_fields"
        ) 