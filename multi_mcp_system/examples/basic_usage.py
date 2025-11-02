"""
Basic usage example for the Multi-MCP Time Series Analysis System.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from utils.model_utils import ModelEvaluator


def generate_sample_data(n_samples: int = 1000, n_features: int = 1, 
                        trend: bool = True, seasonality: bool = True, 
                        noise_level: float = 0.1) -> np.ndarray:
    """Generate sample time series data for testing."""
    t = np.arange(n_samples)
    
    # Base signal
    signal = np.zeros(n_samples)
    
    # Add trend
    if trend:
        signal += 0.01 * t
    
    # Add seasonality
    if seasonality:
        signal += 0.5 * np.sin(2 * np.pi * t / 50)  # 50-period seasonality
        signal += 0.3 * np.sin(2 * np.pi * t / 20)  # 20-period seasonality
    
    # Add noise
    noise = np.random.normal(0, noise_level, n_samples)
    signal += noise
    
    # Add some anomalies
    anomaly_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    signal[anomaly_indices] += np.random.normal(0, 2, len(anomaly_indices))
    
    if n_features > 1:
        # Generate multivariate data
        data = np.zeros((n_samples, n_features))
        data[:, 0] = signal
        
        for i in range(1, n_features):
            # Generate correlated features
            correlation = 0.7
            data[:, i] = correlation * signal + (1 - correlation) * np.random.normal(0, 0.5, n_samples)
    else:
        data = signal.reshape(-1, 1)
    
    return data


def simulate_mcp_client_call(server_name: str, tool_name: str, arguments: dict) -> dict:
    """
    Simulate MCP client call.
    In a real implementation, this would make actual MCP calls.
    """
    print(f"🔗 Calling {server_name}.{tool_name}")
    print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    
    # Simulate different responses based on the tool
    if server_name == "forecasting-mcp-server":
        if tool_name == "train_forecasting_model":
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "model_type": arguments["model_type"],
                "training_metrics": {
                    "final_loss": 0.05,
                    "final_val_loss": 0.08
                },
                "test_metrics": {
                    "mse": 0.08,
                    "rmse": 0.28,
                    "mae": 0.22,
                    "mape": 5.5,
                    "r2": 0.85
                }
            }
        elif tool_name == "predict_forecasting":
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "predictions": np.random.random(10).tolist(),
                "steps_ahead": arguments.get("steps_ahead", 1)
            }
    
    elif server_name == "anomaly-mcp-server":
        if tool_name == "train_anomaly_model":
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "model_type": arguments["model_type"],
                "anomaly_detection": {
                    "anomaly_count": 15,
                    "total_points": 1000,
                    "anomaly_rate": 0.015
                }
            }
        elif tool_name == "detect_anomalies":
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "anomaly_detection": {
                    "anomaly_count": 3,
                    "total_points": 100,
                    "anomaly_rate": 0.03,
                    "anomaly_indices": [15, 45, 78]
                }
            }
    
    elif server_name == "coordinator-mcp-server":
        if tool_name == "coordinated_analysis":
            return {
                "status": "success",
                "forecasting": {
                    "model": arguments.get("forecasting_model", "lstm"),
                    "predictions": np.random.random(10).tolist(),
                    "confidence": 0.85
                },
                "anomaly_detection": {
                    "model": arguments.get("anomaly_model", "prophet"),
                    "anomalies_detected": 2,
                    "anomaly_rate": 0.1,
                    "anomaly_indices": [5, 8]
                },
                "combined_analysis": {
                    "anomaly_adjusted_forecast": "forecast_with_anomaly_corrections",
                    "reliability_score": 0.8
                }
            }
    
    return {"status": "success", "message": "Simulated response"}


async def basic_forecasting_example():
    """Demonstrate basic forecasting capabilities."""
    print("=" * 60)
    print("🚀 BASIC FORECASTING EXAMPLE")
    print("=" * 60)
    
    # Generate sample data
    print("📊 Generating sample time series data...")
    data = generate_sample_data(n_samples=1000, n_features=1, trend=True, seasonality=True)
    print(f"   Generated data shape: {data.shape}")
    
    # Train forecasting model
    print("\n🤖 Training LSTM forecasting model...")
    train_args = {
        "model_type": "lstm",
        "data": json.dumps(data.tolist()),
        "model_name": "basic_lstm_model",
        "sequence_length": 30,
        "prediction_length": 1,
        "epochs": 50,
        "batch_size": 32
    }
    
    train_result = simulate_mcp_client_call("forecasting-mcp-server", "train_forecasting_model", train_args)
    print(f"   Training completed: {train_result['status']}")
    print(f"   Final loss: {train_result['training_metrics']['final_loss']:.4f}")
    print(f"   Test RMSE: {train_result['test_metrics']['rmse']:.4f}")
    
    # Make predictions
    print("\n🔮 Making predictions...")
    test_data = data[-50:]  # Use last 50 points for prediction
    predict_args = {
        "model_name": "basic_lstm_model",
        "data": json.dumps(test_data.tolist()),
        "steps_ahead": 10
    }
    
    predict_result = simulate_mcp_client_call("forecasting-mcp-server", "predict_forecasting", predict_args)
    print(f"   Predictions: {predict_result['predictions'][:5]}...")  # Show first 5 predictions
    
    return train_result, predict_result


async def basic_anomaly_detection_example():
    """Demonstrate basic anomaly detection capabilities."""
    print("\n" + "=" * 60)
    print("🔍 BASIC ANOMALY DETECTION EXAMPLE")
    print("=" * 60)
    
    # Generate sample data with anomalies
    print("📊 Generating sample data with anomalies...")
    data = generate_sample_data(n_samples=1000, n_features=1, trend=True, seasonality=True, noise_level=0.2)
    print(f"   Generated data shape: {data.shape}")
    
    # Train anomaly detection model
    print("\n🤖 Training Prophet anomaly detection model...")
    train_args = {
        "model_type": "prophet",
        "data": json.dumps(data.tolist()),
        "model_name": "basic_prophet_model",
        "model_params": {
            "interval_width": 0.99,
            "changepoint_range": 0.8,
            "daily_seasonality": False,
            "yearly_seasonality": False,
            "weekly_seasonality": False
        }
    }
    
    train_result = simulate_mcp_client_call("anomaly-mcp-server", "train_anomaly_model", train_args)
    print(f"   Training completed: {train_result['status']}")
    print(f"   Anomalies detected in training: {train_result['anomaly_detection']['anomaly_count']}")
    print(f"   Anomaly rate: {train_result['anomaly_detection']['anomaly_rate']:.3f}")
    
    # Detect anomalies in new data
    print("\n🔍 Detecting anomalies in new data...")
    new_data = data[-100:]  # Use last 100 points
    detect_args = {
        "model_name": "basic_prophet_model",
        "data": json.dumps(new_data.tolist()),
        "threshold": 0.1
    }
    
    detect_result = simulate_mcp_client_call("anomaly-mcp-server", "detect_anomalies", detect_args)
    print(f"   Anomalies detected: {detect_result['anomaly_detection']['anomaly_count']}")
    print(f"   Anomaly rate: {detect_result['anomaly_detection']['anomaly_rate']:.3f}")
    print(f"   Anomaly indices: {detect_result['anomaly_detection']['anomaly_indices']}")
    
    return train_result, detect_result


async def coordinated_analysis_example():
    """Demonstrate coordinated analysis using multiple agents."""
    print("\n" + "=" * 60)
    print("🤝 COORDINATED ANALYSIS EXAMPLE")
    print("=" * 60)
    
    # Generate sample data
    print("📊 Generating sample multivariate time series data...")
    data = generate_sample_data(n_samples=1000, n_features=3, trend=True, seasonality=True)
    print(f"   Generated data shape: {data.shape}")
    
    # Perform coordinated analysis
    print("\n🤝 Performing coordinated forecast and anomaly detection...")
    analysis_args = {
        "data": json.dumps(data.tolist()),
        "analysis_type": "forecast_and_detect",
        "forecasting_model": "lstm",
        "anomaly_model": "prophet",
        "parameters": {
            "sequence_length": 30,
            "prediction_length": 5,
            "anomaly_threshold": 0.95
        }
    }
    
    analysis_result = simulate_mcp_client_call("coordinator-mcp-server", "coordinated_analysis", analysis_args)
    print(f"   Analysis completed: {analysis_result['status']}")
    
    # Display results
    forecasting = analysis_result['forecasting']
    anomaly_detection = analysis_result['anomaly_detection']
    combined = analysis_result['combined_analysis']
    
    print(f"\n📈 Forecasting Results:")
    print(f"   Model: {forecasting['model']}")
    print(f"   Predictions: {forecasting['predictions'][:5]}...")
    print(f"   Confidence: {forecasting['confidence']:.2f}")
    
    print(f"\n🔍 Anomaly Detection Results:")
    print(f"   Model: {anomaly_detection['model']}")
    print(f"   Anomalies detected: {anomaly_detection['anomalies_detected']}")
    print(f"   Anomaly rate: {anomaly_detection['anomaly_rate']:.3f}")
    
    print(f"\n🎯 Combined Analysis:")
    print(f"   Reliability score: {combined['reliability_score']:.2f}")
    print(f"   Anomaly-adjusted forecast: {combined['anomaly_adjusted_forecast']}")
    
    return analysis_result


async def ensemble_forecasting_example():
    """Demonstrate ensemble forecasting capabilities."""
    print("\n" + "=" * 60)
    print("🎭 ENSEMBLE FORECASTING EXAMPLE")
    print("=" * 60)
    
    # Generate sample data
    print("📊 Generating sample time series data...")
    data = generate_sample_data(n_samples=1000, n_features=1, trend=True, seasonality=True)
    print(f"   Generated data shape: {data.shape}")
    
    # Perform ensemble forecasting
    print("\n🎭 Creating ensemble forecast...")
    ensemble_args = {
        "data": json.dumps(data.tolist()),
        "models": ["lstm", "cnn", "multivariate_lstm"],
        "ensemble_method": "weighted_average"
    }
    
    ensemble_result = simulate_mcp_client_call("coordinator-mcp-server", "ensemble_forecast", ensemble_args)
    print(f"   Ensemble forecast completed: {ensemble_result['ensemble_method']}")
    
    # Display results
    individual = ensemble_result['individual_predictions']
    combined = ensemble_result['combined_predictions']
    
    print(f"\n📊 Individual Model Predictions:")
    for model, pred in individual.items():
        print(f"   {model}: {pred['predictions'][:3]}... (confidence: {pred['confidence']:.2f})")
    
    print(f"\n🎯 Combined Predictions:")
    print(f"   Combined: {combined[:5]}...")
    print(f"   Ensemble confidence: {ensemble_result['ensemble_confidence']:.2f}")
    
    return ensemble_result


async def main():
    """Main function to run all examples."""
    print("🌟 Multi-MCP Time Series Analysis System - Basic Usage Examples")
    print("=" * 80)
    
    try:
        # Run examples
        await basic_forecasting_example()
        await basic_anomaly_detection_example()
        await coordinated_analysis_example()
        await ensemble_forecasting_example()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

