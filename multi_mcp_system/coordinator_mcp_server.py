"""
Coordinator MCP Server for A2A Communication.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("coordinator-mcp-server")

# Global variables for coordination
forecasting_agent = None
anomaly_agent = None
analysis_history = []


class AgentCommunication:
    """Handle communication between different MCP agents."""
    
    def __init__(self):
        self.agents = {}
        self.message_queue = []
    
    async def register_agent(self, agent_name: str, agent_connection):
        """Register an agent for communication."""
        self.agents[agent_name] = agent_connection
        logger.info(f"Registered agent: {agent_name}")
    
    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Send a message between agents."""
        message_data = {
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        self.message_queue.append(message_data)
        logger.info(f"Message sent from {from_agent} to {to_agent}")
        return message_data
    
    async def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get messages for a specific agent."""
        messages = [msg for msg in self.message_queue if msg["to"] == agent_name]
        return messages


# Initialize communication handler
communication = AgentCommunication()


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available coordination resources."""
    return [
        Resource(
            uri="coordinator://agents",
            name="Registered Agents",
            description="List of registered MCP agents",
            mimeType="application/json"
        ),
        Resource(
            uri="coordinator://analysis-history",
            name="Analysis History",
            description="History of coordinated analyses",
            mimeType="application/json"
        ),
        Resource(
            uri="coordinator://system-status",
            name="System Status",
            description="Current status of the multi-MCP system",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read coordination resources."""
    if uri == "coordinator://agents":
        agents_info = {
            "registered_agents": list(communication.agents.keys()),
            "total_agents": len(communication.agents),
            "agent_types": ["forecasting", "anomaly_detection"]
        }
        return json.dumps(agents_info, indent=2)
    
    elif uri == "coordinator://analysis-history":
        return json.dumps(analysis_history, indent=2)
    
    elif uri == "coordinator://system-status":
        status = {
            "forecasting_agent_connected": "forecasting" in communication.agents,
            "anomaly_agent_connected": "anomaly_detection" in communication.agents,
            "total_analyses": len(analysis_history),
            "pending_messages": len(communication.message_queue),
            "system_health": "healthy" if len(communication.agents) >= 2 else "degraded"
        }
        return json.dumps(status, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available coordination tools."""
    return [
        Tool(
            name="register_agent",
            description="Register a new agent for coordination",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to register"
                    },
                    "agent_type": {
                        "type": "string",
                        "enum": ["forecasting", "anomaly_detection", "other"],
                        "description": "Type of the agent"
                    }
                },
                "required": ["agent_name", "agent_type"]
            }
        ),
        Tool(
            name="coordinated_analysis",
            description="Perform coordinated analysis using multiple agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["forecast_and_detect", "ensemble_forecast", "anomaly_aware_forecast"],
                        "description": "Type of coordinated analysis to perform"
                    },
                    "forecasting_model": {
                        "type": "string",
                        "description": "Forecasting model to use"
                    },
                    "anomaly_model": {
                        "type": "string",
                        "description": "Anomaly detection model to use"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Additional parameters for the analysis"
                    }
                },
                "required": ["data", "analysis_type"]
            }
        ),
        Tool(
            name="ensemble_forecast",
            description="Create ensemble forecast using multiple models",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of forecasting models to use"
                    },
                    "ensemble_method": {
                        "type": "string",
                        "enum": ["average", "weighted_average", "voting"],
                        "default": "weighted_average",
                        "description": "Method for combining forecasts"
                    }
                },
                "required": ["data", "models"]
            }
        ),
        Tool(
            name="anomaly_aware_forecast",
            description="Create forecasts that account for detected anomalies",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "JSON string containing time series data"
                    },
                    "forecasting_model": {
                        "type": "string",
                        "description": "Forecasting model to use"
                    },
                    "anomaly_model": {
                        "type": "string",
                        "description": "Anomaly detection model to use"
                    },
                    "anomaly_threshold": {
                        "type": "number",
                        "default": 0.95,
                        "description": "Threshold for anomaly detection"
                    }
                },
                "required": ["data", "forecasting_model", "anomaly_model"]
            }
        ),
        Tool(
            name="send_agent_message",
            description="Send a message to a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_agent": {
                        "type": "string",
                        "description": "Name of the target agent"
                    },
                    "message": {
                        "type": "object",
                        "description": "Message content to send"
                    }
                },
                "required": ["to_agent", "message"]
            }
        ),
        Tool(
            name="get_agent_messages",
            description="Get messages for a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to get messages for"
                    }
                },
                "required": ["agent_name"]
            }
        ),
        Tool(
            name="get_analysis_history",
            description="Get history of coordinated analyses",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of analyses to return"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for coordination operations."""
    
    try:
        if name == "register_agent":
            return await register_agent(arguments)
        elif name == "coordinated_analysis":
            return await coordinated_analysis(arguments)
        elif name == "ensemble_forecast":
            return await ensemble_forecast(arguments)
        elif name == "anomaly_aware_forecast":
            return await anomaly_aware_forecast(arguments)
        elif name == "send_agent_message":
            return await send_agent_message(arguments)
        elif name == "get_agent_messages":
            return await get_agent_messages(arguments)
        elif name == "get_analysis_history":
            return await get_analysis_history(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def register_agent(arguments: Dict[str, Any]) -> List[TextContent]:
    """Register a new agent for coordination."""
    agent_name = arguments["agent_name"]
    agent_type = arguments["agent_type"]
    
    # In a real implementation, this would establish actual connections
    # For now, we'll just register the agent in our communication handler
    await communication.register_agent(agent_name, {"type": agent_type})
    
    result = {
        "status": "success",
        "agent_name": agent_name,
        "agent_type": agent_type,
        "registered_agents": list(communication.agents.keys())
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def coordinated_analysis(arguments: Dict[str, Any]) -> List[TextContent]:
    """Perform coordinated analysis using multiple agents."""
    data_json = arguments["data"]
    analysis_type = arguments["analysis_type"]
    forecasting_model = arguments.get("forecasting_model", "lstm")
    anomaly_model = arguments.get("anomaly_model", "prophet")
    parameters = arguments.get("parameters", {})
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    analysis_id = f"analysis_{len(analysis_history) + 1}"
    analysis_start_time = pd.Timestamp.now().isoformat()
    
    # Perform analysis based on type
    if analysis_type == "forecast_and_detect":
        result = await perform_forecast_and_detect(data, forecasting_model, anomaly_model, parameters)
    elif analysis_type == "ensemble_forecast":
        models = parameters.get("models", ["lstm", "cnn"])
        result = await perform_ensemble_forecast(data, models, parameters)
    elif analysis_type == "anomaly_aware_forecast":
        result = await perform_anomaly_aware_forecast(data, forecasting_model, anomaly_model, parameters)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    # Record analysis
    analysis_record = {
        "analysis_id": analysis_id,
        "analysis_type": analysis_type,
        "start_time": analysis_start_time,
        "end_time": pd.Timestamp.now().isoformat(),
        "data_shape": data.shape,
        "parameters": parameters,
        "result": result
    }
    
    analysis_history.append(analysis_record)
    
    # Send messages to agents (simulated)
    await communication.send_message(
        "coordinator", 
        "forecasting", 
        {"type": "analysis_completed", "analysis_id": analysis_id}
    )
    await communication.send_message(
        "coordinator", 
        "anomaly_detection", 
        {"type": "analysis_completed", "analysis_id": analysis_id}
    )
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def perform_forecast_and_detect(data: np.ndarray, forecasting_model: str, anomaly_model: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Perform both forecasting and anomaly detection."""
    # This is a simplified implementation
    # In a real system, this would call the actual MCP agents
    
    # Simulate forecasting
    forecast_result = {
        "model": forecasting_model,
        "predictions": np.random.random(10).tolist(),
        "confidence": 0.85
    }
    
    # Simulate anomaly detection
    anomaly_result = {
        "model": anomaly_model,
        "anomalies_detected": 2,
        "anomaly_rate": 0.1,
        "anomaly_indices": [5, 8]
    }
    
    return {
        "forecasting": forecast_result,
        "anomaly_detection": anomaly_result,
        "combined_analysis": {
            "anomaly_adjusted_forecast": "forecast_with_anomaly_corrections",
            "reliability_score": 0.8
        }
    }


async def perform_ensemble_forecast(data: np.ndarray, models: List[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Perform ensemble forecasting using multiple models."""
    ensemble_method = parameters.get("ensemble_method", "weighted_average")
    
    # Simulate individual model predictions
    individual_predictions = {}
    for model in models:
        individual_predictions[model] = {
            "predictions": np.random.random(10).tolist(),
            "confidence": np.random.random()
        }
    
    # Combine predictions
    if ensemble_method == "average":
        combined_predictions = np.mean([pred["predictions"] for pred in individual_predictions.values()], axis=0)
    elif ensemble_method == "weighted_average":
        weights = [pred["confidence"] for pred in individual_predictions.values()]
        weights = np.array(weights) / np.sum(weights)
        combined_predictions = np.average([pred["predictions"] for pred in individual_predictions.values()], 
                                        weights=weights, axis=0)
    else:
        combined_predictions = np.mean([pred["predictions"] for pred in individual_predictions.values()], axis=0)
    
    return {
        "ensemble_method": ensemble_method,
        "individual_predictions": individual_predictions,
        "combined_predictions": combined_predictions.tolist(),
        "ensemble_confidence": np.mean([pred["confidence"] for pred in individual_predictions.values()])
    }


async def perform_anomaly_aware_forecast(data: np.ndarray, forecasting_model: str, anomaly_model: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Perform forecasting that accounts for detected anomalies."""
    # Simulate anomaly detection
    anomaly_threshold = parameters.get("anomaly_threshold", 0.95)
    anomaly_scores = np.random.random(len(data))
    anomalies = anomaly_scores > anomaly_threshold
    
    # Simulate forecasting
    base_forecast = np.random.random(10)
    
    # Adjust forecast based on anomalies
    if np.any(anomalies):
        # Reduce confidence in areas with anomalies
        adjusted_forecast = base_forecast * 0.8
        confidence_adjustment = 0.7
    else:
        adjusted_forecast = base_forecast
        confidence_adjustment = 1.0
    
    return {
        "base_forecast": base_forecast.tolist(),
        "adjusted_forecast": adjusted_forecast.tolist(),
        "anomalies_detected": int(np.sum(anomalies)),
        "anomaly_scores": anomaly_scores.tolist(),
        "confidence_adjustment": confidence_adjustment,
        "anomaly_threshold": anomaly_threshold
    }


async def ensemble_forecast(arguments: Dict[str, Any]) -> List[TextContent]:
    """Create ensemble forecast using multiple models."""
    data_json = arguments["data"]
    models = arguments["models"]
    ensemble_method = arguments.get("ensemble_method", "weighted_average")
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    result = await perform_ensemble_forecast(data, models, {"ensemble_method": ensemble_method})
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def anomaly_aware_forecast(arguments: Dict[str, Any]) -> List[TextContent]:
    """Create forecasts that account for detected anomalies."""
    data_json = arguments["data"]
    forecasting_model = arguments["forecasting_model"]
    anomaly_model = arguments["anomaly_model"]
    anomaly_threshold = arguments.get("anomaly_threshold", 0.95)
    
    # Parse data
    data = json.loads(data_json)
    if isinstance(data, list):
        data = np.array(data)
    elif isinstance(data, dict) and "values" in data:
        data = np.array(data["values"])
    else:
        data = np.array(data)
    
    result = await perform_anomaly_aware_forecast(
        data, forecasting_model, anomaly_model, 
        {"anomaly_threshold": anomaly_threshold}
    )
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_agent_message(arguments: Dict[str, Any]) -> List[TextContent]:
    """Send a message to a specific agent."""
    to_agent = arguments["to_agent"]
    message = arguments["message"]
    
    result = await communication.send_message("coordinator", to_agent, message)
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_agent_messages(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get messages for a specific agent."""
    agent_name = arguments["agent_name"]
    
    messages = await communication.get_messages(agent_name)
    
    result = {
        "agent_name": agent_name,
        "messages": messages,
        "message_count": len(messages)
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_analysis_history(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get history of coordinated analyses."""
    limit = arguments.get("limit", 10)
    
    recent_analyses = analysis_history[-limit:] if analysis_history else []
    
    result = {
        "total_analyses": len(analysis_history),
        "returned_analyses": len(recent_analyses),
        "analyses": recent_analyses
    }
    
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main function to run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="coordinator-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

