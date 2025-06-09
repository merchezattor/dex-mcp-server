"""
Custom exceptions for the DEX MCP server.
"""


class DEXMCPError(Exception):
    """Base exception for all DEX MCP server errors."""
    pass


class ValidationError(DEXMCPError):
    """Exception raised for input validation errors."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field


class APIError(DEXMCPError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, endpoint: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint


class ConfigurationError(DEXMCPError):
    """Exception raised for configuration-related errors."""
    pass


class ConnectionError(DEXMCPError):
    """Exception raised for connection-related errors."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after 