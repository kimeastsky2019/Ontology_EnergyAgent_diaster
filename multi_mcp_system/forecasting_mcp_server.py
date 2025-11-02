"""
MCP Server for Time Series Forecasting Models.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

# Import forecasting models
from models.forecasting.lstm_model import LSTMForecaster, MultiStepLSTMForecaster
from models.forecasting.cnn_model import CNNForecaster, MultiStepCNNForecaster
from utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from utils.model_utils import ModelEvaluator, ModelManager, ModelSelector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("forecasting-mcp-server")

# Global variables for model management
model_manager = ModelManager("forecasting_models")
model_evaluator = ModelEvaluator()
active_models = {}


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available forecasting resources."""
    return [
        Resource(
            uri="forecasting://models",
            name="Available Forecasting Models",
            description="List of available time series forecasting models",
            mimeType="application/json"
        ),
        Resource(
            uri="forecasting://trained-models",
            name="Trained Models",
            description="List of trained and saved forecasting models",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read forecasting resources."""
    if uri == "forecasting://models":
        models_info = {
            "available_models": [
                {
                    "name": "lstm",
                    "description": "Long Short-Term Memory network for time series forecasting",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "supports_multi_step": True
                },
                {
                    "name": "cnn",
                    "description": "1D Convolutional Neural Network for time series forecasting",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "supports_multi_step": True
                },
                {
                    "name": "multivariate_lstm",
                    "description": "Multivariate LSTM for multiple time series forecasting",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "supports_multi_step": True
                },
                {
                    "name": "multivariate_cnn_lstm",
                    "description": "Hybrid CNN-LSTM for multivariate time series forecasting",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "supports_multi_step": True
                }
            ]
        }
        return json.dumps(models_info, indent=2)
    
    elif uri == "forecasting://trained-models":
        trained_models = model_manager.list_models()
        models_info = {
            "trained_models": trained_models,
            "active_models": list(active_models.keys())
        }
        return json.dumps(models_info, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available forecasting tools."""
    return [
        Tool(
            name="train_forecasting_model",
            description="Train a time series forecasting model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "enum": ["lstm", "cnn", "multivariate_lstm", "multivariate_cnn_lstm"],
                        "description": "Type of forecasting model to train"
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "sequence_length": {
                        "type": "integer",
                        "default": 30,
                        "description": "Length of input sequences"
                    },
                    "prediction_length": {
                        "type": "integer",
                        "default": 1,
                        "description": "Length of prediction sequences"
                    },
                    "epochs": {
                        "type": "integer",
                        "default": 100,
                        "description": "Number of training epochs"
                    },
                    "batch_size": {
                        "type": "integer",
                        "default": 32,
                        "description": "Training batch size"
                    },
                    "model_name": {
                        "type": "string",
                        "description": "Name to save the trained model"
                    }
                },
                "required": ["model_type", "data", "model_name"]
            }
        ),
        Tool(
            name="predict_forecasting",
            description="Make predictions using a trained forecasting model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the trained model to use"
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string containing input data for prediction"
                    },
                    "steps_ahead": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of steps to predict ahead"
                    }
                },
                "required": ["model_name", "data"]
            }
        ),
        Tool(
            name="evaluate_forecasting_model",
            description="Evaluate a trained forecasting model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the trained model to evaluate"
                    },
                    "test_data": {
                        "type": "string",
                        "description": "JSON string containing test data"
                    }
                },
                "required": ["model_name", "test_data"]
            }
        ),
        Tool(
            name="select_best_forecasting_model",
            description="Select the best forecasting model based on data characteristics",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "is_multivariate": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether the data is multivariate"
                    },
                    "sequence_length": {
                        "type": "integer",
                        "default": 30,
                        "description": "Length of input sequences"
                    },
                    "prediction_length": {
                        "type": "integer",
                        "default": 1,
                        "description": "Length of prediction sequences"
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="load_forecasting_model",
            description="Load a previously trained forecasting model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the model to load"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="list_forecasting_models",
            description="List all available and trained forecasting models",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for forecasting operations."""
    
    try:
        if name == "train_forecasting_model":
            return await train_forecasting_model(arguments)
        elif name == "predict_forecasting":
            return await predict_forecasting(arguments)
        elif name == "evaluate_forecasting_model":
            return await evaluate_forecasting_model(arguments)
        elif name == "select_best_forecasting_model":
            return await select_best_forecasting_model(arguments)
        elif name == "load_forecasting_model":
            return await load_forecasting_model(arguments)
        elif name == "list_forecasting_models":
            return await list_forecasting_models(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def train_forecasting_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Train a forecasting model."""
    model_type = arguments["model_type"]
    data_json = arguments["data"]
    model_name = arguments["model_name"]
    sequence_length = arguments.get("sequence_length", 30)
    prediction_length = arguments.get("prediction_length", 1)
    epochs = arguments.get("epochs", 100)
    batch_size = arguments.get("batch_size", 32)
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Prepare data
    if model_type in ["multivariate_lstm", "multivariate_cnn_lstm"]:
        prepared_data = prepare_multivariate_forecasting_data(
            data, sequence_length, prediction_length
        )
    else:
        prepared_data = prepare_forecasting_data(
            data, sequence_length, prediction_length
        )
    
    # Initialize model
    if model_type == "lstm":
        model = LSTMForecaster(
            sequence_length=sequence_length,
            prediction_length=prediction_length
        )
    elif model_type == "cnn":
        model = CNNForecaster(
            sequence_length=sequence_length,
            prediction_length=prediction_length
        )
    elif model_type == "multivariate_lstm":
        model = MultiStepLSTMForecaster(
            sequence_length=sequence_length,
            prediction_length=prediction_length
        )
    elif model_type == "multivariate_cnn_lstm":
        model = MultiStepCNNForecaster(
            sequence_length=sequence_length,
            prediction_length=prediction_length
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Train model
    history = model.fit(
        prepared_data["train_X"],
        prepared_data["train_y"],
        prepared_data["val_X"],
        prepared_data["val_y"],
        epochs=epochs,
        batch_size=batch_size,
        verbose=0
    )
    
    # Save model
    metadata = {
        "model_type": model_type,
        "sequence_length": sequence_length,
        "prediction_length": prediction_length,
        "data_shape": data.shape,
        "training_history": history
    }
    
    model_path = model_manager.save_model(model, model_name, metadata)
    active_models[model_name] = model
    
    # Evaluate on test data
    test_predictions = model.predict(prepared_data["test_X"])
    test_metrics = model_evaluator.calculate_metrics(
        prepared_data["test_y"], test_predictions
    )
    
    result = {
        "status": "success",
        "model_name": model_name,
        "model_type": model_type,
        "model_path": model_path,
        "training_metrics": {
            "final_loss": history["loss"][-1],
            "final_val_loss": history["val_loss"][-1] if history["val_loss"] else None
        },
        "test_metrics": test_metrics,
        "model_summary": model.get_model_summary()
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def predict_forecasting(arguments: Dict[str, Any]) -> List[TextContent]:
    """Make predictions using a trained model."""
    model_name = arguments["model_name"]
    data_json = arguments["data"]
    steps_ahead = arguments.get("steps_ahead", 1)
    
    # Load model if not active
    if model_name not in active_models:
        model, metadata = model_manager.load_model(model_name)
        active_models[model_name] = model
    
    model = active_models[model_name]
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Make predictions
    if steps_ahead == 1:
        predictions = model.predict(data)
    else:
        # Use the last sequence for multi-step prediction
        last_sequence = data[-model.sequence_length:]
        predictions = model.predict_future(last_sequence, steps_ahead)
    
    result = {
        "status": "success",
        "model_name": model_name,
        "predictions": predictions.tolist(),
        "steps_ahead": steps_ahead
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def evaluate_forecasting_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Evaluate a trained model."""
    model_name = arguments["model_name"]
    test_data_json = arguments["test_data"]
    
    # Load model if not active
    if model_name not in active_models:
        model, metadata = model_manager.load_model(model_name)
        active_models[model_name] = model
    
    model = active_models[model_name]
    
    # Parse test data
    test_data = json.loads(test_data_json)
    if isinstance(test_data, list):
        test_data = np.array(test_data)
    elif isinstance(test_data, dict) and "values" in test_data:
        test_data = np.array(test_data["values"])
    else:
        test_data = np.array(test_data)
    
    # Make predictions
    predictions = model.predict(test_data)
    
    # Calculate metrics (assuming test_data contains both X and y)
    if len(test_data.shape) == 3:  # (samples, sequence_length, features)
        # For sequence data, we need to split X and y
        X_test = test_data
        # This is a simplified case - in practice, you'd need proper test data with targets
        y_test = np.zeros((X_test.shape[0], model.prediction_length))
    else:
        X_test = test_data
        y_test = np.zeros((X_test.shape[0], model.prediction_length))
    
    metrics = model_evaluator.calculate_metrics(y_test, predictions)
    
    result = {
        "status": "success",
        "model_name": model_name,
        "metrics": metrics,
        "predictions": predictions.tolist()
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def select_best_forecasting_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Select the best forecasting model based on data characteristics."""
    data_json = arguments["data"]
    is_multivariate = arguments.get("is_multivariate", False)
    sequence_length = arguments.get("sequence_length", 30)
    prediction_length = arguments.get("prediction_length", 1)
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Select best model
    recommended_model = ModelSelector.select_forecasting_model(
        data.shape, is_multivariate, sequence_length, prediction_length
    )
    
    result = {
        "status": "success",
        "recommended_model": recommended_model,
        "data_characteristics": {
            "shape": data.shape,
            "is_multivariate": is_multivariate,
            "sequence_length": sequence_length,
            "prediction_length": prediction_length
        }
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def load_forecasting_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Load a previously trained model."""
    model_name = arguments["model_name"]
    
    try:
        model, metadata = model_manager.load_model(model_name)
        active_models[model_name] = model
        
        result = {
            "status": "success",
            "model_name": model_name,
            "metadata": metadata
        }
        
    except Exception as e:
        result = {
            "status": "error",
            "error": str(e)
        }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def list_forecasting_models(arguments: Dict[str, Any]) -> List[TextContent]:
    """List all available and trained models."""
    trained_models = model_manager.list_models()
    active_model_names = list(active_models.keys())
    
    result = {
        "status": "success",
        "trained_models": trained_models,
        "active_models": active_model_names,
        "available_model_types": [
            "lstm", "cnn", "multivariate_lstm", "multivariate_cnn_lstm"
        ]
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main function to run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="forecasting-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

