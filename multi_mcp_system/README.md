# A2A Multi-MCP Time Series Analysis System

This system provides an Agent-to-Agent (A2A) based multi-MCP (Model Context Protocol) architecture for time series forecasting and anomaly detection using various machine learning models.

## 🌟 Features

- **A2A Communication**: Agents can communicate and collaborate seamlessly
- **Intelligent Model Selection**: Automatic model selection based on data characteristics
- **Ensemble Methods**: Combine multiple models for better predictions
- **Real-time Processing**: Support for real-time data processing and analysis
- **Scalable Architecture**: Easy to add new models and agents
- **Comprehensive Evaluation**: Built-in metrics and performance comparison tools

## 🏗️ Architecture Overview

The system consists of three main MCP servers that communicate with each other:

1. **Forecasting MCP Server** - Handles time series forecasting using various models
2. **Anomaly Detection MCP Server** - Handles anomaly detection using various models  
3. **Coordinator MCP Server** - Orchestrates communication between agents and provides unified interface

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Forecasting   │    │   Anomaly       │    │   Coordinator   │
│   MCP Server    │◄──►│   Detection     │◄──►│   MCP Server    │
│                 │    │   MCP Server    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Client Apps   │
                    │   & Examples    │
                    └─────────────────┘
```

## 🤖 Models Available

### Forecasting Models
- **LSTM** - Long Short-Term Memory networks (single and multi-step)
- **CNN** - 1D Convolutional Neural Networks
- **Auto-Encoder** - Autoencoder-based forecasting
- **Multivariate LSTM** - Multivariate time series LSTM
- **Multivariate CNN-LSTM** - Hybrid CNN-LSTM for multivariate data
- **TimeGAN** - Generative Adversarial Network for time series generation

### Anomaly Detection Models
- **Prophet** - Facebook Prophet with anomaly detection
- **HMM** - Hidden Markov Model for anomaly detection
- **Transformer** - Transformer-based anomaly detection
- **Temporal Fusion Transformer** - Advanced transformer for time series
- **Temporal Transformer** - Custom temporal transformer implementation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the system
cd multi_mcp_system

# Run the setup script
python setup.py
```

### 2. Start the System

#### Option A: Docker (Recommended)
```bash
# Start all services with Docker
python run_service.py start

# Or use Docker Compose directly
docker-compose up -d
```

#### Option B: Local Development
```bash
# Start all services locally
python run_service.py start --service local

# Start individual services
python run_service.py start --service web
python run_service.py start --service api
python run_service.py start --service forecasting
python run_service.py start --service anomaly
python run_service.py start --service coordinator
```

### 3. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Web Dashboard** | http://localhost:5000 | Main web interface |
| **REST API** | http://localhost:5001 | API endpoints |
| **Prometheus** | http://localhost:9090 | Metrics monitoring |
| **Grafana** | http://localhost:3000 | Visualization (admin/admin) |

### 4. Run Examples

```bash
# Basic usage examples
python examples/basic_usage.py

# Advanced analysis examples
python examples/advanced_analysis.py
```

## 📁 Directory Structure

```
multi_mcp_system/
├── README.md
├── requirements.txt
├── setup.py                    # Setup script
├── forecasting_mcp_server.py   # Forecasting MCP server
├── anomaly_mcp_server.py       # Anomaly detection MCP server
├── coordinator_mcp_server.py   # Coordinator MCP server
├── models/                     # Model implementations
│   ├── forecasting/
│   │   ├── lstm_model.py
│   │   ├── cnn_model.py
│   │   ├── autoencoder_model.py
│   │   ├── multivariate_lstm.py
│   │   ├── cnn_lstm_model.py
│   │   └── timegan_model.py
│   └── anomaly_detection/
│       ├── prophet_model.py
│       ├── hmm_model.py
│       ├── transformer_model.py
│       ├── temporal_fusion_transformer.py
│       └── temporal_transformer.py
├── utils/                      # Utility functions
│   ├── data_preprocessing.py
│   ├── model_utils.py
│   └── communication.py
├── examples/                   # Example usage
│   ├── basic_usage.py
│   ├── advanced_analysis.py
│   └── real_time_analysis.py
├── config/                     # Configuration files
│   ├── forecasting_config.json
│   ├── anomaly_config.json
│   └── coordinator_config.json
├── start_all.sh               # Start all servers
├── start_forecasting.sh       # Start forecasting server
├── start_anomaly.sh          # Start anomaly detection server
└── start_coordinator.sh      # Start coordinator server
```

## 🔧 Configuration

The system uses JSON configuration files for each component:

- `config/forecasting_config.json` - Forecasting model parameters
- `config/anomaly_config.json` - Anomaly detection model parameters  
- `config/coordinator_config.json` - Coordinator and communication settings

## 📊 Usage Examples

### Basic Forecasting

```python
# Train a forecasting model
result = await forecasting_client.call_tool("train_forecasting_model", {
    "model_type": "lstm",
    "data": json.dumps(data.tolist()),
    "model_name": "my_lstm_model",
    "sequence_length": 30,
    "prediction_length": 1
})

# Make predictions
predictions = await forecasting_client.call_tool("predict_forecasting", {
    "model_name": "my_lstm_model",
    "data": json.dumps(test_data.tolist()),
    "steps_ahead": 10
})
```

### Anomaly Detection

```python
# Train an anomaly detection model
result = await anomaly_client.call_tool("train_anomaly_model", {
    "model_type": "prophet",
    "data": json.dumps(data.tolist()),
    "model_name": "my_prophet_model"
})

# Detect anomalies
anomalies = await anomaly_client.call_tool("detect_anomalies", {
    "model_name": "my_prophet_model",
    "data": json.dumps(new_data.tolist()),
    "threshold": 0.95
})
```

### Coordinated Analysis

```python
# Perform coordinated analysis
result = await coordinator_client.call_tool("coordinated_analysis", {
    "data": json.dumps(data.tolist()),
    "analysis_type": "forecast_and_detect",
    "forecasting_model": "lstm",
    "anomaly_model": "prophet"
})
```

## 🎯 Advanced Features

### Ensemble Forecasting

```python
# Create ensemble forecast
ensemble_result = await coordinator_client.call_tool("ensemble_forecast", {
    "data": json.dumps(data.tolist()),
    "models": ["lstm", "cnn", "multivariate_lstm"],
    "ensemble_method": "weighted_average"
})
```

### Anomaly-Aware Forecasting

```python
# Create anomaly-aware forecasts
anomaly_aware_result = await coordinator_client.call_tool("anomaly_aware_forecast", {
    "data": json.dumps(data.tolist()),
    "forecasting_model": "lstm",
    "anomaly_model": "prophet",
    "anomaly_threshold": 0.95
})
```

## 🔍 Model Selection

The system automatically selects the best model based on data characteristics:

- **Data size**: Larger datasets favor more complex models
- **Multivariate**: Multivariate data uses specialized models
- **Trend/Seasonality**: Prophet for data with trends/seasonality
- **Complex patterns**: Transformers for complex temporal patterns

## 📈 Performance Monitoring

The system includes built-in performance monitoring:

- Model training metrics (loss, accuracy, etc.)
- Prediction quality metrics (RMSE, MAE, R², etc.)
- Anomaly detection metrics (precision, recall, F1, etc.)
- System health monitoring

## 🛠️ Development

### Adding New Models

1. Create model class in appropriate directory (`models/forecasting/` or `models/anomaly_detection/`)
2. Implement required methods (`fit`, `predict`, etc.)
3. Add model to MCP server tool definitions
4. Update configuration files

### Adding New Agents

1. Create new MCP server following existing patterns
2. Register agent with coordinator
3. Update communication protocols
4. Add to startup scripts

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Model Training Fails**: Check data format and parameters
3. **Memory Issues**: Reduce batch size or sequence length
4. **Performance Issues**: Use appropriate model for data size

### Debug Mode

Enable debug logging by setting log level in configuration files:

```json
{
  "performance": {
    "log_level": "DEBUG"
  }
}
```

## 📚 API Reference

### Forecasting MCP Server Tools

- `train_forecasting_model` - Train a forecasting model
- `predict_forecasting` - Make predictions
- `evaluate_forecasting_model` - Evaluate model performance
- `select_best_forecasting_model` - Select best model for data
- `load_forecasting_model` - Load saved model
- `list_forecasting_models` - List available models

### Anomaly Detection MCP Server Tools

- `train_anomaly_model` - Train an anomaly detection model
- `detect_anomalies` - Detect anomalies in data
- `evaluate_anomaly_model` - Evaluate model performance
- `select_best_anomaly_model` - Select best model for data
- `load_anomaly_model` - Load saved model
- `list_anomaly_models` - List available models

### Coordinator MCP Server Tools

- `coordinated_analysis` - Perform coordinated analysis
- `ensemble_forecast` - Create ensemble forecasts
- `anomaly_aware_forecast` - Create anomaly-aware forecasts
- `send_agent_message` - Send message between agents
- `get_agent_messages` - Get messages for agent
- `get_analysis_history` - Get analysis history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Facebook Prophet team for the Prophet library
- TensorFlow team for deep learning capabilities
- MCP community for the Model Context Protocol
- Contributors and users of this system
