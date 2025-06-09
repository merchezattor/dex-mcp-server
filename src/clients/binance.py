"""
Binance API client for the DEX MCP server.
"""
import asyncio
import logging
from typing import Dict, List, Optional

import aiohttp

from ..config import config
from ..exceptions import APIError, RateLimitError, ConnectionError
from ..models import PriceData, KlineData, TickerStats24hr

logger = logging.getLogger(__name__)


class BinanceClient:
    """Async client for Binance API with connection pooling and error handling."""
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=config.connection_limit,
                limit_per_host=config.connection_limit_per_host,
                ttl_dns_cache=config.dns_cache_ttl,
                use_dns_cache=True,
            )
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": f"{config.server_name}/{config.server_version}"}
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Binance client session closed")
    
    async def _fetch_json_with_retry(self, endpoint: str, params: Dict) -> Dict:
        """Fetch JSON data with retry logic and error handling."""
        session = await self.get_session()
        url = f"{config.base_url}/{endpoint}"
        
        last_exception = None
        for attempt in range(config.max_retries):
            try:
                logger.debug(f"Fetching {url} with params {params} (attempt {attempt + 1})")
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.debug(f"Successfully fetched data from {endpoint}")
                        return data
                    elif resp.status == 429:  # Rate limit
                        retry_after = int(resp.headers.get('Retry-After', config.rate_limit_delay))
                        logger.warning(f"Rate limited on {endpoint}, retrying after {retry_after}s")
                        await asyncio.sleep(retry_after * (2 ** attempt))
                        continue
                    else:
                        error_text = await resp.text()
                        raise APIError(
                            f"HTTP {resp.status}: {error_text}",
                            status_code=resp.status,
                            endpoint=endpoint
                        )
                        
            except asyncio.TimeoutError as e:
                last_exception = APIError(f"Request timeout for {endpoint}", endpoint=endpoint)
                logger.warning(f"Timeout on attempt {attempt + 1} for {endpoint}")
            except aiohttp.ClientError as e:
                last_exception = ConnectionError(f"Network error: {str(e)}")
                logger.warning(f"Network error on attempt {attempt + 1} for {endpoint}: {e}")
            except Exception as e:
                last_exception = APIError(f"Unexpected error: {str(e)}", endpoint=endpoint)
                logger.error(f"Unexpected error on attempt {attempt + 1} for {endpoint}: {e}")
            
            if attempt < config.max_retries - 1:
                await asyncio.sleep(config.rate_limit_delay * (2 ** attempt))
        
        # If we get here, all retries failed
        raise last_exception or APIError(
            f"Failed to fetch data from {endpoint} after {config.max_retries} attempts",
            endpoint=endpoint
        )
    
    async def get_price(self, symbol: str) -> PriceData:
        """
        Get current price for a trading pair.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            
        Returns:
            PriceData object with current price
            
        Raises:
            APIError: If API request fails
        """
        data = await self._fetch_json_with_retry("ticker/price", {"symbol": symbol})
        
        if "price" not in data:
            raise APIError(f"Invalid response format for symbol {symbol}")
        
        return PriceData(
            symbol=symbol,
            price=float(data["price"]),
            timestamp=data.get("timestamp")
        )
    
    async def get_klines(self, symbol: str, interval: str, limit: int) -> List[KlineData]:
        """
        Get candlestick data for a trading pair.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (e.g., "1h", "1d")
            limit: Number of klines to return
            
        Returns:
            List of KlineData objects
            
        Raises:
            APIError: If API request fails
        """
        raw_data = await self._fetch_json_with_retry(
            "klines",
            {"symbol": symbol, "interval": interval, "limit": limit}
        )
        
        if not isinstance(raw_data, list):
            raise APIError(f"Invalid response format for klines")
        
        klines = []
        for raw_kline in raw_data:
            if len(raw_kline) < 6:
                logger.warning(f"Incomplete kline data: {raw_kline}")
                continue
            try:
                klines.append(KlineData.from_binance_data(raw_kline))
            except (ValueError, IndexError) as e:
                logger.warning(f"Error processing kline {raw_kline}: {e}")
                continue
        
        return klines
    
    async def get_24hr_stats(self, symbol: str) -> TickerStats24hr:
        """
        Get 24hr ticker statistics for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            TickerStats24hr object with statistics
            
        Raises:
            APIError: If API request fails
        """
        data = await self._fetch_json_with_retry("ticker/24hr", {"symbol": symbol})
        
        # Validate response format
        required_fields = [
            "priceChange", "priceChangePercent", "weightedAvgPrice",
            "prevClosePrice", "lastPrice", "volume", "quoteVolume"
        ]
        
        for field in required_fields:
            if field not in data:
                raise APIError(f"Missing field {field} in 24hr stats response")
        
        return TickerStats24hr.from_binance_data(data) 