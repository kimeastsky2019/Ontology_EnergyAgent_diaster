# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Integrated Energy Analysis System** - a comprehensive energy analysis platform combining time-series forecasting, climate prediction, anomaly detection, and multi-agent orchestration via CrewAI. The system provides 55+ MCP tools for energy data analysis with real-time monitoring, weather integration, and AI-powered insights.

**Key Technologies:**
- FastMCP v2.12.3 (MCP server framework)
- CrewAI v0.2.0 (multi-agent orchestration)
- TensorFlow Hub (DeepMind precipitation models)
- FastAPI (REST API server)
- React (weather dashboard frontend)
- Python 3.8+ with asyncio

## Development Commands

### Running the Servers

```bash
# Main MCP server (stdio mode)
python server.py

# FastAPI REST API server (port 8000)
cd api-server && python main.py

# CrewAI multi-agent system (port 8001)
python crewai_energy_system.py

# React weather dashboard (port 3000)
cd react-weather-app && npm start

# Flask-based web interface (port 5001)
python web_interface.py
```

### Testing

```bash
# Run all tests
pytest tests/

# Specific test suites
python test_simple_energy.py              # Basic energy analysis
python test_upgraded_features.py          # Advanced features
python test_external_data_collection.py   # External data sources
python test_climate_prediction.py         # Climate prediction models

# Run tests with asyncio support
pytest --asyncio-mode=auto tests/
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install React app dependencies
cd react-weather-app && npm install

# Required environment variables
export OPENAI_API_KEY="your_openai_api_key"
export OPENWEATHER_API_KEY="your_openweather_api_key"
export ENERGY_MCP_PORT=8001
export LOG_LEVEL=INFO
```

### Data Management

```bash
# Data directory structure
./data/              # Main data storage
./logs/              # Application logs
./examples/          # Example datasets

# Database
sqlite3 energy_analysis.db  # SQLite database (default)
```

## Architecture

### 1. MCP Server Architecture (server.py)

The core MCP server registers 13 tool modules organized into functional categories:

**Tool Modules:**
- `TimeSeriesTools` - Time-series analysis, trend detection, seasonality
- `ModelingTools` - ARIMA, Prophet, LSTM forecasting models
- `DashboardTools` - Plotly-based interactive visualizations
- `WeatherTools` - OpenWeatherMap API integration
- `EnergyAnalysisTools` - Peak demand, efficiency, pattern analysis
- `DataStorageTools` - CSV/JSON/SQLite persistence
- `SimpleAnalysisTools` - Simplified analysis interface
- `PromptTools` - Context-aware prompt generation
- `ExternalDataCollectionTools` - Multi-source data collection with caching
- `ClimatePredictionTools` - Precipitation nowcasting, synthetic radar data
- `TFHubModelTools` - DeepMind precipitation models (256x256, 512x512, 1536x1280)
- `ClimateVisualizationTools` - Cartopy-based geographic visualization
- `KMAWeatherTools` - Korean Meteorological Administration API

**Key Patterns:**
- All tools registered via FastMCP framework during initialization
- Tools registered in `_register_tools()` method in server.py:42-96
- Server runs in stdio mode via `mcp.run_stdio_async()` for Claude Desktop integration
- Async/await pattern used throughout for non-blocking operations

### 2. CrewAI Multi-Agent System (crewai_energy_system.py)

Implements 5 specialized agent crews that work sequentially or in parallel:

**Agent Crews:**
1. **Data Ingestion Crew** - Collects sensor/weather/generation/battery/tariff data
2. **Forecasting & Climate Crew** - Time-series prediction with climate integration
3. **Anomaly & Quality Crew** - Data quality assessment and anomaly detection
4. **Demand Response & Control Crew** - Demand-supply matching and optimization
5. **LLM-SLM Ops & Reporting Crew** - Report generation and model governance

**Architecture Pattern:**
- Each crew has dedicated Agent, Task factory methods, and MCP tools
- `EnergyCrewOrchestrator` coordinates sequential or parallel execution
- Event-based communication via `CrewEvent` dataclass and event queue
- FastAPI endpoints at `/run-workflow`, `/crew-status`, `/health`
- Runs on port 8001 (separate from main API server)

**Integration with MCP:**
- Custom tools (`MCPWeatherTool`, `MCPDataCollectionTool`, `MCPModelTestingTool`)
- Tools wrap MCP server functionality for CrewAI agents
- Results flow: Data → Forecasting → Anomaly → Control → Reporting

### 3. REST API Server (api-server/main.py)

FastAPI-based REST interface exposing MCP functionality via HTTP:

**Key Components:**
- `MCPClient` - Communicates with MCP server
- `AuthService` - JWT-based authentication
- `RateLimiter` - Request rate limiting per user
- `CacheService` - Response caching (5-minute default)

**Main Endpoints:**
- `POST /prediction/run` - Run energy predictions (ensemble, LSTM, CNN, Prophet, ARIMA)
- `POST /anomaly/detect` - Anomaly detection (Prophet, HMM, Isolation Forest)
- `POST /climate/analyze` - Climate analysis (comprehensive, seasonal, correlation)
- `GET /dashboard` - Dashboard data with caching
- `POST /auth/login`, `/auth/register` - User authentication

**Background Tasks:**
- Long-running predictions executed as background tasks via FastAPI BackgroundTasks
- Task status tracked in cache with task_id
- Query status via `GET /tasks/{task_id}`

### 4. Configuration System (config/settings.py)

Centralized configuration via `EnergyAnalysisConfig` class:

**Key Settings:**
- Port: 8001 (default), configurable via `ENERGY_MCP_PORT`
- Data directory: `./data` (auto-created)
- API keys: OpenWeather, WeatherAPI, AccuWeather, NOAA
- Model parameters: ARIMA order (1,1,1), LSTM units (50), epochs (100)
- Thresholds: Peak demand (80%), efficiency (70%), data quality (70%)
- Caching: 300s duration, 1000 max items

**Validation:**
- `validate_config()` checks for missing API keys and invalid parameters
- Accessed as class methods: `EnergyAnalysisConfig.get_port()`

### 5. Tool Implementation Pattern

All tools follow a consistent pattern (see tools/__init__.py:1-35):

```python
class ToolCategory:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def tool_name(param: Type) -> Dict[str, Any]:
            """Tool description for MCP discovery"""
            # Implementation
            return {"result": data}
```

**Important Patterns:**
- Tools are async functions decorated with `@self.mcp.tool()`
- Return structured dictionaries with consistent keys: `{"result": ..., "status": ..., "error": ...}`
- Error handling: wrap in try/except, return error info in response
- Type hints required for all parameters and return values

## Common Development Workflows

### Adding a New MCP Tool

1. Create tool in appropriate module (e.g., `tools/energy_analysis_tools.py`)
2. Follow the tool implementation pattern (async, type hints, error handling)
3. Register in `tools/__init__.py` if creating a new module
4. Import and register in `server.py` `_register_tools()` method
5. Add tests in appropriate test file

### Adding a New CrewAI Agent

1. Create crew class in `crewai_energy_system.py` (e.g., `NewAnalysisCrew`)
2. Define Agent with role, goal, backstory, tools
3. Create task factory method (e.g., `create_analysis_task()`)
4. Register in `EnergyCrewOrchestrator.__init__()` crews dict
5. Update workflow methods to include new crew

### Working with External APIs

**Weather APIs:**
- OpenWeatherMap: `OPENWEATHER_BASE_URL` = "https://api.openweathermap.org/data/2.5"
- WeatherAPI: `WEATHERAPI_BASE_URL` = "http://api.weatherapi.com/v1"
- KMA (Korea): Custom endpoints in `kma_weather_tools.py`

**Data Collection Pattern:**
- Use `ExternalDataCollectionTools` for multi-source collection
- Implements caching (300s default) to avoid rate limits
- Retry logic: 3 attempts with exponential backoff
- Quality validation: threshold 70% (configurable)

### Model Training and Testing

**Supported Models:**
- ARIMA (statsmodels) - `modeling_tools.py:arima_forecast`
- Prophet (Meta) - `modeling_tools.py:prophet_forecast`
- LSTM (TensorFlow/Keras) - `modeling_tools.py:lstm_forecast`
- TF-Hub models (DeepMind) - `tfhub_model_tools.py`

**Model Comparison:**
- Use `compare_models` tool in `modeling_tools.py`
- Metrics: RMSE, MAE, MAPE, R²
- Returns best model based on accuracy

## File Locations

**Core Server Files:**
- `server.py` - Main MCP server entry point
- `crewai_energy_system.py` - CrewAI multi-agent orchestration
- `crewai_config.py` - CrewAI configuration

**API Layer:**
- `api-server/main.py` - FastAPI REST server
- `api-server/mcp_client.py` - MCP client implementation
- `api-server/auth_service.py` - Authentication
- `api-server/rate_limiter.py` - Rate limiting
- `api-server/cache_service.py` - Caching

**Web Interfaces:**
- `web_interface.py` - Flask-based dashboard (port 5001)
- `react-weather-app/` - React weather dashboard
- `weather_dashboard.html` - Standalone weather dashboard

**Configuration:**
- `config/settings.py` - Main configuration
- `.env` - Environment variables (not in repo)

**Tool Modules (tools/):**
- `time_series_tools.py` - Time-series analysis
- `modeling_tools.py` - Forecasting models
- `dashboard_tools.py` - Visualization
- `weather_tools.py` - Weather data
- `energy_analysis_tools.py` - Energy-specific analysis
- `data_storage_tools.py` - Data persistence
- `simple_analysis_tools.py` - Simplified interface
- `prompt_tools.py` - Prompt generation
- `external_data_collection_tools.py` - External data sources
- `climate_prediction_tools.py` - Climate prediction
- `tfhub_model_tools.py` - TensorFlow Hub models
- `climate_visualization_tools.py` - Climate visualization
- `kma_weather_tools.py` - KMA API integration

## Important Implementation Notes

### Async/Await Usage

All MCP tools and API endpoints must be async:
- Use `async def` for all tool functions
- Use `await` for I/O operations (file, network, database)
- Use `asyncio.run()` for script entry points
- FastMCP expects async tools by default

### Error Handling

Consistent error handling pattern:
```python
try:
    # Tool implementation
    return {"result": data, "status": "success"}
except Exception as e:
    logger.error(f"Error in tool_name: {e}")
    return {"error": str(e), "status": "failed"}
```

### Data Validation

- Use Pydantic models for API request/response validation
- Check data types and ranges before processing
- Validate API keys before making external requests
- Check file size limits (100MB max) before loading

### Logging

- Use Python's logging module (configured in server.py:22-26)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log format includes timestamp, module name, level, message
- Logs written to `logs/crewai_energy_system.log` and stderr

### Testing Considerations

- Use `pytest-asyncio` for async test functions
- Mock external API calls to avoid rate limits
- Use sample data in `examples/` directory for tests
- Test both success and error cases
- Validate return types match type hints

### Performance Optimization

- Cache expensive operations (API calls, model predictions)
- Use batch processing for large datasets (chunk by 10k rows)
- Implement pagination for large result sets
- Use background tasks for long-running operations
- Monitor memory usage with large models (TF-Hub models are 50-500MB)

### Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "energy-analysis": {
      "command": "python",
      "args": ["/path/to/energy-analysis-mcp/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key",
        "ENERGY_MCP_PORT": "8001"
      }
    }
  }
}
```

## Deployment

**Supported Platforms:**
- Local development (Python + venv)
- Docker (see `docker/` directory)
- Railway (see `railway.json`)
- Vercel (see `vercel.json`)
- GCP (see `deploy_gcp.sh`)

**Deployment Scripts:**
- `oneclick_installer.sh` - Automated full stack setup
- `deploy_gcp.sh` - Google Cloud Platform deployment
- `setup_server.sh` - Server environment setup
- `upgrade_to_v3.sh` - Version upgrade script

**Health Checks:**
- MCP server: Check stdio communication
- API server: `GET /health` endpoint
- CrewAI system: `GET /health` endpoint

## Multi-Language Support (i18n)

The system includes comprehensive internationalization:
- `translations.py` - Translation management
- `i18n/` directory - Language files (en, ko, ja, zh, es)
- Use `translate(key, language)` for UI strings
- Supported languages: English, Korean, Japanese, Chinese, Spanish
