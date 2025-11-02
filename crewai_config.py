#!/usr/bin/env python3
"""
CrewAI Configuration for Energy Analysis System
==============================================

Configuration settings for the CrewAI-based energy analysis system.
"""

import os
from typing import Dict, Any

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective model for crew operations

# Weather API Configuration
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///energy_analysis.db")

# MCP Server Configuration
MCP_SERVER_URL = "http://localhost:8000"
MCP_ENDPOINTS = {
    "weather": "/api/weather",
    "data_collection": "/api/data-collection",
    "model_testing": "/api/model-testing",
    "anomaly_detection": "/api/anomaly-detection"
}

# Crew Configuration
CREW_CONFIG = {
    "data_ingestion": {
        "max_iterations": 3,
        "timeout": 300,  # 5 minutes
        "retry_attempts": 2
    },
    "forecasting": {
        "max_iterations": 5,
        "timeout": 600,  # 10 minutes
        "retry_attempts": 3
    },
    "anomaly": {
        "max_iterations": 3,
        "timeout": 300,  # 5 minutes
        "retry_attempts": 2
    },
    "demand_control": {
        "max_iterations": 4,
        "timeout": 400,  # 6.7 minutes
        "retry_attempts": 2
    },
    "reporting": {
        "max_iterations": 3,
        "timeout": 300,  # 5 minutes
        "retry_attempts": 2
    }
}

# Event Configuration
EVENT_CONFIG = {
    "queue_size": 1000,
    "processing_interval": 30,  # seconds
    "priority_levels": {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/crewai_energy_system.log"
}

# Performance Monitoring
PERFORMANCE_CONFIG = {
    "metrics_collection": True,
    "response_time_threshold": 30,  # seconds
    "error_rate_threshold": 0.05,  # 5%
    "memory_usage_threshold": 0.8  # 80%
}

# Security Configuration
SECURITY_CONFIG = {
    "api_key_rotation": True,
    "rate_limiting": {
        "requests_per_minute": 60,
        "burst_limit": 10
    },
    "cors_origins": [
        "http://localhost:3000",
        "https://damcp.gngmeta.com"
    ]
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "openai": {
            "api_key": OPENAI_API_KEY,
            "model": OPENAI_MODEL
        },
        "weather": {
            "api_key": WEATHER_API_KEY,
            "base_url": WEATHER_BASE_URL
        },
        "database": {
            "url": DATABASE_URL
        },
        "mcp": {
            "server_url": MCP_SERVER_URL,
            "endpoints": MCP_ENDPOINTS
        },
        "crews": CREW_CONFIG,
        "events": EVENT_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "security": SECURITY_CONFIG
    }
