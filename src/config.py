"""
Configuration management for the DEX MCP server.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Configuration for the DEX MCP server."""
    
    # API Configuration
    base_url: str = "https://api.binance.com/api/v3"
    timeout: int = 10
    max_retries: int = 3
    rate_limit_delay: float = 0.1  # seconds between requests
    
    # Connection Pool Configuration
    connection_limit: int = 100
    connection_limit_per_host: int = 30
    dns_cache_ttl: int = 300
    
    # Server Configuration
    server_name: str = "dex-mcp-server"
    server_version: str = "1.0.0"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("BINANCE_API_URL", "https://api.binance.com/api/v3"),
            timeout=int(os.getenv("API_TIMEOUT", "10")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "0.1")),
            connection_limit=int(os.getenv("CONNECTION_LIMIT", "100")),
            connection_limit_per_host=int(os.getenv("CONNECTION_LIMIT_PER_HOST", "30")),
            dns_cache_ttl=int(os.getenv("DNS_CACHE_TTL", "300")),
            server_name=os.getenv("SERVER_NAME", "dex-mcp-server"),
            server_version=os.getenv("SERVER_VERSION", "1.0.0"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Global configuration instance
config = ServerConfig.from_env()

# Valid intervals for Binance API
VALID_INTERVALS = {
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h",
    "1d", "3d", "1w", "1M"
} 