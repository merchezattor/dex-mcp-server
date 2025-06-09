"""
Data models and schemas for the DEX MCP server.
"""
from dataclasses import dataclass
from typing import List, Union, Optional, Dict, Any
from datetime import datetime


@dataclass
class PriceData:
    """Model for price data response."""
    symbol: str
    price: float
    timestamp: Optional[int] = None


@dataclass
class KlineData:
    """Model for a single kline (candlestick) data point."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_binance_data(cls, raw_data: List[Union[str, float]]) -> "KlineData":
        """Create KlineData from Binance API response."""
        return cls(
            timestamp=int(raw_data[0]),
            open=float(raw_data[1]),
            high=float(raw_data[2]),
            low=float(raw_data[3]),
            close=float(raw_data[4]),
            volume=float(raw_data[5])
        )


@dataclass
class AveragePriceData:
    """Model for average price calculation response."""
    symbol: str
    average_price: float
    interval: str
    period_count: int
    calculation_time: Optional[int] = None


@dataclass
class TickerStats24hr:
    """Model for 24hr ticker statistics."""
    symbol: str
    price_change: float
    price_change_percent: float
    weighted_avg_price: float
    prev_close_price: float
    last_price: float
    volume: float
    quote_volume: float
    open_time: int
    close_time: int
    
    @classmethod
    def from_binance_data(cls, data: Dict[str, Any]) -> "TickerStats24hr":
        """Create TickerStats24hr from Binance API response."""
        return cls(
            symbol=data["symbol"],
            price_change=float(data["priceChange"]),
            price_change_percent=float(data["priceChangePercent"]),
            weighted_avg_price=float(data["weightedAvgPrice"]),
            prev_close_price=float(data["prevClosePrice"]),
            last_price=float(data["lastPrice"]),
            volume=float(data["volume"]),
            quote_volume=float(data["quoteVolume"]),
            open_time=int(data.get("openTime", 0)),
            close_time=int(data.get("closeTime", 0))
        )


@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()