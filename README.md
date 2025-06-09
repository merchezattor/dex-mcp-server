# DEX MCP Server

A robust and scalable Model Context Protocol (MCP) server that provides access to Binance cryptocurrency market data through a well-architected, modular design.

## 🏗️ Architecture

This server follows MCP best practices with a clean, modular architecture:

```
dex-mcp-server/
├── src/                          # Main application package
│   ├── __init__.py              # Package metadata
│   ├── config.py                # Configuration management
│   ├── exceptions.py            # Custom exceptions
│   ├── models.py                # Data models and schemas
│   ├── validators.py            # Input validation utilities
│   ├── server.py                # Main server class
│   ├── clients/                 # External API clients
│   │   ├── __init__.py
│   │   └── binance.py          # Binance API client
│   ├── tools/                   # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── price_tools.py      # Price-related tools
│   │   └── market_tools.py     # Market statistics tools
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       └── lifecycle.py        # Lifecycle management
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## ✨ Features

### MCP Tools Provided
1. **`get_price(symbol="BTCUSDT")`** - Get current price for a trading pair
2. **`get_klines(symbol="BTCUSDT", interval="1h", limit=100)`** - Get OHLCV candlestick data
3. **`average_price(symbol="BTCUSDT", interval="1h", limit=24)`** - Calculate average price over N candles
4. **`get_24hr_stats(symbol="BTCUSDT")`** - Get comprehensive 24hr ticker statistics

### Architecture Benefits
- **Modular Design**: Clean separation of concerns following MCP best practices
- **Robust Error Handling**: Comprehensive error handling with custom exceptions
- **Input Validation**: Thorough validation of all inputs with clear error messages
- **Connection Pooling**: Efficient HTTP session management with connection reuse
- **Retry Logic**: Automatic retries with exponential backoff for failed requests
- **Rate Limiting**: Proper handling of API rate limits
- **Logging**: Structured logging with configurable levels
- **Lifecycle Management**: Graceful shutdown with proper resource cleanup
- **Configuration**: Environment-based configuration management
- **Type Safety**: Full type hints for better IDE support and code quality

## 🚀 Quick Start

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd dex-mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python main.py
```

### Configuration

The server can be configured via environment variables:

```bash
# API Configuration
export BINANCE_API_URL="https://api.binance.com/api/v3"
export API_TIMEOUT="10"
export MAX_RETRIES="3"
export RATE_LIMIT_DELAY="0.1"

# Connection Pool Configuration
export CONNECTION_LIMIT="100"
export CONNECTION_LIMIT_PER_HOST="30"
export DNS_CACHE_TTL="300"

# Server Configuration
export SERVER_NAME="dex-mcp-server"
export SERVER_VERSION="1.0.0"
export LOG_LEVEL="INFO"
```

### Adding to Cursor

Add the server to Cursor via `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dex": {
      "command": "python",
      "args": ["/absolute/path/to/dex-mcp-server/main.py"]
    }
  }
}
```

## 🧪 Development

### Project Structure Principles

This project follows established MCP server architecture patterns:

1. **Configuration Management** (`src/config.py`)
   - Centralized configuration with environment variable support
   - Type-safe configuration classes
   - Validation of configuration values

2. **Error Handling** (`src/exceptions.py`)
   - Custom exception hierarchy for different error types
   - Rich error context for debugging
   - Proper error propagation through the stack

3. **Data Models** (`src/models.py`)
   - Strongly typed data models using dataclasses
   - Conversion methods for external API data
   - Validation of data structure integrity

4. **Input Validation** (`src/validators.py`)
   - Comprehensive input validation functions
   - Clear error messages for invalid inputs
   - Security-focused validation patterns

5. **External Clients** (`src/clients/`)
   - Abstracted API clients with connection pooling
   - Retry logic and error handling
   - Rate limiting and timeout management

6. **MCP Tools** (`src/tools/`)
   - Organized by functional domain
   - Consistent error handling and logging
   - Clear documentation and type hints

7. **Utilities** (`src/utils/`)
   - Logging configuration and management
   - Lifecycle management for graceful shutdown
   - Reusable utility functions

### Adding New Tools

To add a new MCP tool:

1. **Create the tool function** in the appropriate module under `src/tools/`
2. **Add validation** using functions from `src/validators.py`
3. **Handle errors** using exceptions from `src/exceptions.py`
4. **Register the tool** in the appropriate registration function
5. **Update the main server** to register your new tool category

Example:
```python
# In src/tools/new_category.py
def register_new_tools(server: FastMCP, binance_client: BinanceClient) -> None:
    @server.tool()
    async def my_new_tool(param: str) -> dict:
        # Validate input
        param = validate_symbol(param)
        
        # Call API
        result = await binance_client.some_method(param)
        
        # Return formatted response
        return {"result": result}

# In src/server.py
from .tools import register_new_tools

def _register_tools(self) -> None:
    register_price_tools(self.server, self.binance_client)
    register_market_tools(self.server, self.binance_client)
    register_new_tools(self.server, self.binance_client)  # Add this line
```

### Testing

The modular architecture makes testing straightforward:

```python
# Example test structure
import pytest
from src.validators import validate_symbol
from src.exceptions import ValidationError

def test_validate_symbol():
    # Test valid symbol
    assert validate_symbol("BTCUSDT") == "BTCUSDT"
    
    # Test invalid symbol
    with pytest.raises(ValidationError):
        validate_symbol("invalid")
```

## 📦 Dependencies

- **fastmcp**: MCP framework for Python
- **aiohttp**: Async HTTP client for API requests
- **uvloop**: High-performance event loop (Unix only)

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BINANCE_API_URL` | `https://api.binance.com/api/v3` | Binance API base URL |
| `API_TIMEOUT` | `10` | Request timeout in seconds |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `RATE_LIMIT_DELAY` | `0.1` | Base delay between retries |
| `CONNECTION_LIMIT` | `100` | Total connection pool size |
| `CONNECTION_LIMIT_PER_HOST` | `30` | Connections per host |
| `DNS_CACHE_TTL` | `300` | DNS cache TTL in seconds |
| `SERVER_NAME` | `dex-mcp-server` | Server identification |
| `SERVER_VERSION` | `1.0.0` | Server version |
| `LOG_LEVEL` | `INFO` | Logging level |

## 🤝 Contributing

This architecture makes contributions easier:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add your changes** following the established patterns
4. **Add tests** for new functionality
5. **Submit a pull request**

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

Built following MCP best practices and inspired by the AWS MCP Servers project architecture. 