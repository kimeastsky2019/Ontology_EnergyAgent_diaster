"""
MCP Server for Anomaly Detection Models.
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

# Import anomaly detection models
from models.anomaly_detection.prophet_model import ProphetAnomalyDetector
from models.anomaly_detection.hmm_model import HMMAnomalyDetector
from utils.model_utils import ModelEvaluator, ModelManager, ModelSelector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("anomaly-mcp-server")

# Global variables for model management
model_manager = ModelManager("anomaly_models")
model_evaluator = ModelEvaluator()
active_models = {}


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available anomaly detection resources."""
    return [
        Resource(
            uri="anomaly://models",
            name="Available Anomaly Detection Models",
            description="List of available time series anomaly detection models",
            mimeType="application/json"
        ),
        Resource(
            uri="anomaly://trained-models",
            name="Trained Models",
            description="List of trained and saved anomaly detection models",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read anomaly detection resources."""
    if uri == "anomaly://models":
        models_info = {
            "available_models": [
                {
                    "name": "prophet",
                    "description": "Facebook Prophet with anomaly detection capabilities",
                    "type": "statistical",
                    "supports_multivariate": False,
                    "handles_trend_seasonality": True
                },
                {
                    "name": "hmm",
                    "description": "Hidden Markov Model for anomaly detection",
                    "type": "statistical",
                    "supports_multivariate": True,
                    "handles_trend_seasonality": False
                },
                {
                    "name": "transformer",
                    "description": "Transformer-based anomaly detection",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "handles_trend_seasonality": True
                },
                {
                    "name": "temporal_fusion_transformer",
                    "description": "Temporal Fusion Transformer for anomaly detection",
                    "type": "neural_network",
                    "supports_multivariate": True,
                    "handles_trend_seasonality": True
                }
            ]
        }
        return json.dumps(models_info, indent=2)
    
    elif uri == "anomaly://trained-models":
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
    """List available anomaly detection tools."""
    return [
        Tool(
            name="train_anomaly_model",
            description="Train an anomaly detection model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "enum": ["prophet", "hmm", "transformer", "temporal_fusion_transformer"],
                        "description": "Type of anomaly detection model to train"
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "timestamps": {
                        "type": "string",
                        "description": "JSON string containing timestamps (optional)"
                    },
                    "model_name": {
                        "type": "string",
                        "description": "Name to save the trained model"
                    },
                    "model_params": {
                        "type": "object",
                        "description": "Model-specific parameters"
                    }
                },
                "required": ["model_type", "data", "model_name"]
            }
        ),
        Tool(
            name="detect_anomalies",
            description="Detect anomalies using a trained model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the trained model to use"
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON string containing data for anomaly detection"
                    },
                    "timestamps": {
                        "type": "string",
                        "description": "JSON string containing timestamps (optional)"
                    },
                    "threshold": {
                        "type": "number",
                        "default": 0.95,
                        "description": "Threshold for anomaly detection"
                    }
                },
                "required": ["model_name", "data"]
            }
        ),
        Tool(
            name="evaluate_anomaly_model",
            description="Evaluate an anomaly detection model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the trained model to evaluate"
                    },
                    "test_data": {
                        "type": "string",
                        "description": "JSON string containing test data with known anomalies"
                    },
                    "test_labels": {
                        "type": "string",
                        "description": "JSON string containing true anomaly labels"
                    },
                    "threshold": {
                        "type": "number",
                        "default": 0.95,
                        "description": "Threshold for anomaly detection"
                    }
                },
                "required": ["model_name", "test_data", "test_labels"]
            }
        ),
        Tool(
            name="select_best_anomaly_model",
            description="Select the best anomaly detection model based on data characteristics",
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
                    "has_trend": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether the data has trend"
                    },
                    "has_seasonality": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether the data has seasonality"
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="load_anomaly_model",
            description="Load a previously trained anomaly detection model",
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
            name="list_anomaly_models",
            description="List all available and trained anomaly detection models",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for anomaly detection operations."""
    
    try:
        if name == "train_anomaly_model":
            return await train_anomaly_model(arguments)
        elif name == "detect_anomalies":
            return await detect_anomalies(arguments)
        elif name == "evaluate_anomaly_model":
            return await evaluate_anomaly_model(arguments)
        elif name == "select_best_anomaly_model":
            return await select_best_anomaly_model(arguments)
        elif name == "load_anomaly_model":
            return await load_anomaly_model(arguments)
        elif name == "list_anomaly_models":
            return await list_anomaly_models(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def train_anomaly_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Train an anomaly detection model."""
    model_type = arguments["model_type"]
    data_json = arguments["data"]
    model_name = arguments["model_name"]
    timestamps_json = arguments.get("timestamps")
    model_params = arguments.get("model_params", {})
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Parse timestamps if provided
    timestamps = None
    if timestamps_json:
        timestamps = json.loads(timestamps_json)
        if isinstance(timestamps, list):
            timestamps = np.array(timestamps)
        else:
            timestamps = np.array(timestamps)
    
    # Initialize model
    if model_type == "prophet":
        model = ProphetAnomalyDetector(
            interval_width=model_params.get("interval_width", 0.99),
            changepoint_range=model_params.get("changepoint_range", 0.8),
            daily_seasonality=model_params.get("daily_seasonality", False),
            yearly_seasonality=model_params.get("yearly_seasonality", False),
            weekly_seasonality=model_params.get("weekly_seasonality", False),
            seasonality_mode=model_params.get("seasonality_mode", "multiplicative")
        )
    elif model_type == "hmm":
        model = HMMAnomalyDetector(
            n_components=model_params.get("n_components", 10),
            covariance_type=model_params.get("covariance_type", "diag"),
            n_iter=model_params.get("n_iter", 1000),
            random_state=model_params.get("random_state", None)
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Train model
    if model_type == "prophet":
        training_result = model.fit(data, timestamps)
    elif model_type == "hmm":
        include_volume = model_params.get("include_volume", False)
        training_result = model.fit(data, include_volume)
    
    # Save model
    metadata = {
        "model_type": model_type,
        "data_shape": data.shape,
        "training_result": training_result,
        "model_params": model_params
    }
    
    model_path = model_manager.save_model(model, model_name, metadata)
    active_models[model_name] = model
    
    # Detect anomalies on training data
    if model_type == "prophet":
        anomaly_result = model.detect_anomalies(threshold=0.1)
    elif model_type == "hmm":
        anomaly_result = model.detect_anomalies(threshold=0.95)
    
    result = {
        "status": "success",
        "model_name": model_name,
        "model_type": model_type,
        "model_path": model_path,
        "training_result": training_result,
        "anomaly_detection": anomaly_result,
        "model_summary": model.get_model_summary()
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def detect_anomalies(arguments: Dict[str, Any]) -> List[TextContent]:
    """Detect anomalies using a trained model."""
    model_name = arguments["model_name"]
    data_json = arguments["data"]
    timestamps_json = arguments.get("timestamps")
    threshold = arguments.get("threshold", 0.95)
    
    # Load model if not active
    if model_name not in active_models:
        model, metadata = model_manager.load_model(model_name)
        active_models[model_name] = model
    
    model = active_models[model_name]
    model_type = metadata.get("model_type", "unknown")
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Parse timestamps if provided
    timestamps = None
    if timestamps_json:
        timestamps = json.loads(timestamps_json)
        if isinstance(timestamps, list):
            timestamps = np.array(timestamps)
        else:
            timestamps = np.array(timestamps)
    
    # Detect anomalies
    if model_type == "prophet":
        anomaly_result = model.predict_anomalies(data, timestamps, threshold)
    elif model_type == "hmm":
        include_volume = metadata.get("model_params", {}).get("include_volume", False)
        anomaly_result = model.predict_anomalies(data, threshold, include_volume)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    result = {
        "status": "success",
        "model_name": model_name,
        "model_type": model_type,
        "anomaly_detection": anomaly_result
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def evaluate_anomaly_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Evaluate an anomaly detection model."""
    model_name = arguments["model_name"]
    test_data_json = arguments["test_data"]
    test_labels_json = arguments["test_labels"]
    threshold = arguments.get("threshold", 0.95)
    
    # Load model if not active
    if model_name not in active_models:
        model, metadata = model_manager.load_model(model_name)
        active_models[model_name] = model
    
    model = active_models[model_name]
    model_type = metadata.get("model_type", "unknown")
    
    # Parse test data
    test_data = json.loads(test_data_json)
    if isinstance(test_data, list):
        test_data = np.array(test_data)
    elif isinstance(test_data, dict) and "values" in test_data:
        test_data = np.array(test_data["values"])
    else:
        test_data = np.array(test_data)
    
    # Parse test labels
    test_labels = json.loads(test_labels_json)
    if isinstance(test_labels, list):
        test_labels = np.array(test_labels)
    else:
        test_labels = np.array(test_labels)
    
    # Detect anomalies
    if model_type == "prophet":
        anomaly_result = model.predict_anomalies(test_data, None, threshold)
    elif model_type == "hmm":
        include_volume = metadata.get("model_params", {}).get("include_volume", False)
        anomaly_result = model.predict_anomalies(test_data, threshold, include_volume)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Calculate evaluation metrics
    predicted_anomalies = np.array(anomaly_result["is_anomaly"])
    true_anomalies = test_labels.astype(bool)
    
    metrics = model_evaluator.calculate_anomaly_metrics(
        true_anomalies.astype(int), 
        predicted_anomalies.astype(int)
    )
    
    result = {
        "status": "success",
        "model_name": model_name,
        "model_type": model_type,
        "metrics": metrics,
        "anomaly_detection": anomaly_result
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def select_best_anomaly_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Select the best anomaly detection model based on data characteristics."""
    data_json = arguments["data"]
    is_multivariate = arguments.get("is_multivariate", False)
    has_trend = arguments.get("has_trend", False)
    has_seasonality = arguments.get("has_seasonality", False)
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    # Select best model
    recommended_model = ModelSelector.select_anomaly_model(
        data.shape, is_multivariate, has_trend, has_seasonality
    )
    
    result = {
        "status": "success",
        "recommended_model": recommended_model,
        "data_characteristics": {
            "shape": data.shape,
            "is_multivariate": is_multivariate,
            "has_trend": has_trend,
            "has_seasonality": has_seasonality
        }
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def load_anomaly_model(arguments: Dict[str, Any]) -> List[TextContent]:
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


async def list_anomaly_models(arguments: Dict[str, Any]) -> List[TextContent]:
    """List all available and trained models."""
    trained_models = model_manager.list_models()
    active_model_names = list(active_models.keys())
    
    result = {
        "status": "success",
        "trained_models": trained_models,
        "active_models": active_model_names,
        "available_model_types": [
            "prophet", "hmm", "transformer", "temporal_fusion_transformer"
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
                server_name="anomaly-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

