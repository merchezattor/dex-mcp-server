"""
Lifecycle management utilities for the DEX MCP server.
"""
import asyncio
import signal
import logging
from typing import List, Callable, Awaitable

logger = logging.getLogger(__name__)

# Global list of cleanup functions
_cleanup_functions: List[Callable[[], Awaitable[None]]] = []


def register_cleanup_function(func: Callable[[], Awaitable[None]]) -> None:
    """
    Register a cleanup function to be called on shutdown.
    
    Args:
        func: Async function to call during cleanup
    """
    _cleanup_functions.append(func)
    logger.debug(f"Registered cleanup function: {func.__name__}")


async def cleanup_all() -> None:
    """Execute all registered cleanup functions."""
    logger.info("Starting cleanup process...")
    
    for cleanup_func in _cleanup_functions:
        try:
            await cleanup_func()
            logger.debug(f"Successfully executed cleanup: {cleanup_func.__name__}")
        except Exception as e:
            logger.error(f"Error during cleanup of {cleanup_func.__name__}: {e}")
    
    logger.info("Cleanup process completed")


def setup_lifecycle_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""
    
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        
        # Get the current event loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(cleanup_all())
        except RuntimeError:
            # No event loop running, create one
            asyncio.run(cleanup_all())
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Lifecycle handlers configured") 