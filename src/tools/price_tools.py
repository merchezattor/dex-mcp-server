"""
Price-related MCP tools for the DEX MCP server.
"""
import logging
from typing import Dict, List, Union

from mcp.server.fastmcp import FastMCP

from ..clients import BinanceClient
from ..validators import validate_symbol, validate_interval, validate_limit
from ..exceptions import ValidationError, APIError
from ..models import AveragePriceData

logger = logging.getLogger(__name__)


def register_price_tools(server: FastMCP, binance_client: BinanceClient) -> None:
    """Register price-related tools with the MCP server."""
    
    @server.tool()
    async def get_price(symbol: str = "BTCUSDT") -> Dict[str, Union[str, float]]:
        """
        Get the current price for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT, ETHUSDT)
            
        Returns:
            Dictionary with symbol and current price information
            
        Raises:
            ValidationError: If symbol format is invalid
            APIError: If API request fails
        """
        try:
            symbol = validate_symbol(symbol)
            price_data = await binance_client.get_price(symbol)
            
            return {
                "symbol": price_data.symbol,
                "price": price_data.price,
                "timestamp": price_data.timestamp
            }
        except (ValidationError, APIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_price: {e}")
            raise APIError(f"Failed to get price for {symbol}: {str(e)}")
    
    @server.tool()
    async def get_klines(
        symbol: str = "BTCUSDT", 
        interval: str = "1h", 
        limit: int = 100
    ) -> List[List[Union[int, float]]]:
        """
        Get candlestick (OHLCV) data for a trading pair.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (1m, 5m, 1h, 1d, etc.)
            limit: Number of klines to return (max 1000)
            
        Returns:
            List of klines: [timestamp, open, high, low, close, volume]
        """
        try:
            symbol = validate_symbol(symbol)
            interval = validate_interval(interval)
            limit = validate_limit(limit)
            
            klines = await binance_client.get_klines(symbol, interval, limit)
            
            # Convert to expected format
            return [
                [kline.timestamp, kline.open, kline.high, kline.low, kline.close, kline.volume]
                for kline in klines
            ]
        except (ValidationError, APIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_klines: {e}")
            raise APIError(f"Failed to get klines for {symbol}: {str(e)}")
    
    @server.tool()
    async def average_price(
        symbol: str = "BTCUSDT", 
        interval: str = "1h", 
        limit: int = 24
    ) -> Dict[str, Union[str, float, int]]:
        """
        Calculate the average close price over the last N candles.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval
            limit: Number of candles to average
            
        Returns:
            Dictionary with symbol, average price, and calculation metadata
        """
        try:
            symbol = validate_symbol(symbol)
            interval = validate_interval(interval)
            limit = validate_limit(limit)
            
            klines = await binance_client.get_klines(symbol, interval, limit)
            
            if not klines:
                raise APIError(f"No kline data available for {symbol}")
            
            closes = [kline.close for kline in klines]
            avg_price = sum(closes) / len(closes)
            
            avg_data = AveragePriceData(
                symbol=symbol,
                average_price=avg_price,
                interval=interval,
                period_count=len(closes),
                calculation_time=klines[-1].timestamp if klines else None
            )
            
            return {
                "symbol": avg_data.symbol,
                "average_price": avg_data.average_price,
                "interval": avg_data.interval,
                "period_count": avg_data.period_count,
                "calculation_time": avg_data.calculation_time
            }
        except (ValidationError, APIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in average_price: {e}")
            raise APIError(f"Failed to calculate average price for {symbol}: {str(e)}") 