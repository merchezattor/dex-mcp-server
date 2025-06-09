"""
Main server module for the DEX MCP server.
"""
import asyncio
import logging

import uvloop
from mcp.server.fastmcp import FastMCP

from .config import config
from .clients import BinanceClient
from .tools import register_price_tools, register_market_tools
from .utils import setup_logging, setup_lifecycle_handlers, register_cleanup_function

# Use uvloop for faster event loop on Unix systems
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


class DEXMCPServer:
    """Main DEX MCP Server class."""
    
    def __init__(self):
        self.server = FastMCP(config.server_name)
        self.binance_client = BinanceClient()
        
        # Setup logging and lifecycle management
        setup_logging()
        setup_lifecycle_handlers()
        
        # Register cleanup functions
        register_cleanup_function(self.cleanup)
        
        # Register tools
        self._register_tools()
        
        logger.info(f"DEX MCP Server initialized (version {config.server_version})")
    
    def _register_tools(self) -> None:
        """Register all MCP tools with the server."""
        register_price_tools(self.server, self.binance_client)
        register_market_tools(self.server, self.binance_client)
        logger.info("All MCP tools registered successfully")
    
    async def cleanup(self) -> None:
        """Cleanup server resources."""
        logger.info("Cleaning up DEX MCP Server resources...")
        await self.binance_client.close()
        logger.info("DEX MCP Server cleanup completed")
    
    def run(self) -> None:
        """Run the MCP server."""
        try:
            logger.info("Starting DEX MCP Server...")
            self.server.run()  # stdio transport by default
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            # Final cleanup
            logger.info("Server shutdown complete")


def create_server() -> DEXMCPServer:
    """Factory function to create a server instance."""
    return DEXMCPServer()


if __name__ == "__main__":
    server = create_server()
    server.run() 