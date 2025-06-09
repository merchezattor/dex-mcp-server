"""
Market statistics MCP tools for the DEX MCP server.
"""
import logging
from typing import Dict, Union

from mcp.server.fastmcp import FastMCP

from ..clients import BinanceClient
from ..validators import validate_symbol
from ..exceptions import ValidationError, APIError

logger = logging.getLogger(__name__)


def register_market_tools(server: FastMCP, binance_client: BinanceClient) -> None:
    """Register market-related tools with the MCP server."""
    
    @server.tool()
    async def get_24hr_stats(symbol: str = "BTCUSDT") -> Dict[str, Union[str, float]]:
        """
        Get 24hr ticker statistics for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT, ETHUSDT)
            
        Returns:
            Dictionary with comprehensive 24hr statistics
        """
        try:
            symbol = validate_symbol(symbol)
            stats = await binance_client.get_24hr_stats(symbol)
            
            return {
                "symbol": stats.symbol,
                "price_change": stats.price_change,
                "price_change_percent": stats.price_change_percent,
                "weighted_avg_price": stats.weighted_avg_price,
                "prev_close_price": stats.prev_close_price,
                "last_price": stats.last_price,
                "volume": stats.volume,
                "quote_volume": stats.quote_volume,
                "open_time": stats.open_time,
                "close_time": stats.close_time,
            }
        except (ValidationError, APIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_24hr_stats: {e}")
            raise APIError(f"Failed to get 24hr stats for {symbol}: {str(e)}") 