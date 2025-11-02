"""
Advanced analysis example for the Multi-MCP Time Series Analysis System.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from utils.model_utils import ModelEvaluator, ModelSelector


def generate_complex_data(n_samples: int = 2000, n_features: int = 4, 
                         trend_strength: float = 0.02, seasonality_strength: float = 1.0,
                         noise_level: float = 0.15, anomaly_rate: float = 0.03) -> tuple:
    """Generate complex multivariate time series data with various patterns."""
    t = np.arange(n_samples)
    
    # Initialize data matrix
    data = np.zeros((n_samples, n_features))
    
    # Generate base patterns for each feature
    patterns = {
        'trend': lambda t: trend_strength * t,
        'seasonal_1': lambda t: seasonality_strength * np.sin(2 * np.pi * t / 50),
        'seasonal_2': lambda t: 0.5 * seasonality_strength * np.sin(2 * np.pi * t / 20),
        'seasonal_3': lambda t: 0.3 * seasonality_strength * np.sin(2 * np.pi * t / 100),
        'cyclical': lambda t: 0.4 * seasonality_strength * np.sin(2 * np.pi * t / 200),
        'random_walk': lambda t: np.cumsum(np.random.normal(0, 0.1, len(t)))
    }
    
    # Generate each feature with different characteristics
    for i in range(n_features):
        if i == 0:  # Strong trend + seasonality
            signal = patterns['trend'](t) + patterns['seasonal_1'](t) + patterns['seasonal_2'](t)
        elif i == 1:  # Cyclical + random walk
            signal = patterns['cyclical'](t) + patterns['random_walk'](t)
        elif i == 2:  # Multiple seasonalities
            signal = patterns['seasonal_1'](t) + patterns['seasonal_3'](t)
        else:  # Complex pattern
            signal = (patterns['trend'](t) + patterns['seasonal_1'](t) + 
                     patterns['cyclical'](t) + patterns['random_walk'](t))
        
        # Add noise
        noise = np.random.normal(0, noise_level, n_samples)
        signal += noise
        
        # Add anomalies
        n_anomalies = int(anomaly_rate * n_samples)
        anomaly_indices = np.random.choice(n_samples, size=n_anomalies, replace=False)
        anomaly_values = np.random.normal(0, 3 * noise_level, n_anomalies)
        signal[anomaly_indices] += anomaly_values
        
        data[:, i] = signal
    
    # Add cross-correlations between features
    correlation_matrix = np.array([
        [1.0, 0.7, 0.3, 0.5],
        [0.7, 1.0, 0.2, 0.4],
        [0.3, 0.2, 1.0, 0.6],
        [0.5, 0.4, 0.6, 1.0]
    ])
    
    # Apply correlation
    for i in range(n_features):
        for j in range(i+1, n_features):
            if correlation_matrix[i, j] > 0:
                data[:, j] += correlation_matrix[i, j] * 0.3 * data[:, i]
    
    # Generate timestamps
    start_date = datetime(2020, 1, 1)
    timestamps = [start_date + timedelta(days=i) for i in range(n_samples)]
    
    return data, timestamps


def simulate_advanced_mcp_call(server_name: str, tool_name: str, arguments: dict) -> dict:
    """Simulate advanced MCP client call with more realistic responses."""
    print(f"🔗 Calling {server_name}.{tool_name}")
    
    if server_name == "forecasting-mcp-server":
        if tool_name == "select_best_forecasting_model":
            data_shape = arguments.get("data_shape", (1000, 1))
            is_multivariate = arguments.get("is_multivariate", False)
            
            if is_multivariate and data_shape[0] > 1000:
                recommended = "multivariate_cnn_lstm"
            elif data_shape[0] > 1000:
                recommended = "lstm"
            else:
                recommended = "cnn"
            
            return {
                "status": "success",
                "recommended_model": recommended,
                "data_characteristics": {
                    "shape": data_shape,
                    "is_multivariate": is_multivariate
                }
            }
        
        elif tool_name == "train_forecasting_model":
            model_type = arguments["model_type"]
            data = json.loads(arguments["data"])
            
            # Simulate training metrics based on model type
            if model_type == "lstm":
                metrics = {"mse": 0.05, "rmse": 0.22, "mae": 0.18, "r2": 0.88}
            elif model_type == "cnn":
                metrics = {"mse": 0.08, "rmse": 0.28, "mae": 0.22, "r2": 0.82}
            elif model_type == "multivariate_lstm":
                metrics = {"mse": 0.06, "rmse": 0.24, "mae": 0.20, "r2": 0.85}
            else:
                metrics = {"mse": 0.07, "rmse": 0.26, "mae": 0.21, "r2": 0.83}
            
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "model_type": model_type,
                "training_metrics": {"final_loss": 0.05, "final_val_loss": 0.08},
                "test_metrics": metrics
            }
    
    elif server_name == "anomaly-mcp-server":
        if tool_name == "select_best_anomaly_model":
            data_shape = arguments.get("data_shape", (1000, 1))
            has_trend = arguments.get("has_trend", False)
            has_seasonality = arguments.get("has_seasonality", False)
            
            if has_trend or has_seasonality:
                recommended = "prophet"
            elif data_shape[0] > 1000:
                recommended = "transformer"
            else:
                recommended = "hmm"
            
            return {
                "status": "success",
                "recommended_model": recommended,
                "data_characteristics": {
                    "shape": data_shape,
                    "has_trend": has_trend,
                    "has_seasonality": has_seasonality
                }
            }
        
        elif tool_name == "train_anomaly_model":
            model_type = arguments["model_type"]
            
            # Simulate anomaly detection results
            anomaly_count = np.random.randint(10, 50)
            total_points = 1000
            anomaly_rate = anomaly_count / total_points
            
            return {
                "status": "success",
                "model_name": arguments["model_name"],
                "model_type": model_type,
                "anomaly_detection": {
                    "anomaly_count": anomaly_count,
                    "total_points": total_points,
                    "anomaly_rate": anomaly_rate
                }
            }
    
    return {"status": "success", "message": "Advanced simulated response"}


async def model_selection_example():
    """Demonstrate intelligent model selection based on data characteristics."""
    print("=" * 80)
    print("🧠 INTELLIGENT MODEL SELECTION EXAMPLE")
    print("=" * 80)
    
    # Generate different types of data
    print("📊 Generating different types of time series data...")
    
    # Univariate data with trend and seasonality
    univariate_data = generate_complex_data(n_samples=1000, n_features=1)[0]
    
    # Multivariate data
    multivariate_data = generate_complex_data(n_samples=1500, n_features=4)[0]
    
    # Data without trend/seasonality
    random_data = np.random.normal(0, 1, (800, 1))
    
    datasets = {
        "univariate_trend_seasonal": univariate_data,
        "multivariate_complex": multivariate_data,
        "random_data": random_data
    }
    
    for name, data in datasets.items():
        print(f"\n🔍 Analyzing {name}...")
        print(f"   Data shape: {data.shape}")
        
        # Select best forecasting model
        forecast_args = {
            "data": json.dumps(data.tolist()),
            "is_multivariate": data.shape[1] > 1,
            "sequence_length": 30,
            "prediction_length": 1
        }
        
        forecast_result = simulate_advanced_mcp_call(
            "forecasting-mcp-server", "select_best_forecasting_model", forecast_args
        )
        print(f"   Recommended forecasting model: {forecast_result['recommended_model']}")
        
        # Select best anomaly detection model
        anomaly_args = {
            "data": json.dumps(data.tolist()),
            "is_multivariate": data.shape[1] > 1,
            "has_trend": "trend" in name,
            "has_seasonality": "seasonal" in name
        }
        
        anomaly_result = simulate_advanced_mcp_call(
            "anomaly-mcp-server", "select_best_anomaly_model", anomaly_args
        )
        print(f"   Recommended anomaly model: {anomaly_result['recommended_model']}")


async def ensemble_analysis_example():
    """Demonstrate advanced ensemble analysis."""
    print("\n" + "=" * 80)
    print("🎭 ADVANCED ENSEMBLE ANALYSIS EXAMPLE")
    print("=" * 80)
    
    # Generate complex data
    print("📊 Generating complex multivariate time series data...")
    data, timestamps = generate_complex_data(n_samples=2000, n_features=4)
    print(f"   Data shape: {data.shape}")
    print(f"   Time range: {timestamps[0]} to {timestamps[-1]}")
    
    # Train multiple forecasting models
    print("\n🤖 Training multiple forecasting models...")
    models = ["lstm", "cnn", "multivariate_lstm"]
    model_results = {}
    
    for model in models:
        print(f"   Training {model}...")
        train_args = {
            "model_type": model,
            "data": json.dumps(data.tolist()),
            "model_name": f"ensemble_{model}",
            "sequence_length": 50,
            "prediction_length": 7,
            "epochs": 100
        }
        
        result = simulate_advanced_mcp_call("forecasting-mcp-server", "train_forecasting_model", train_args)
        model_results[model] = result
        print(f"     RMSE: {result['test_metrics']['rmse']:.4f}, R²: {result['test_metrics']['r2']:.4f}")
    
    # Create ensemble forecast
    print("\n🎭 Creating ensemble forecast...")
    ensemble_args = {
        "data": json.dumps(data[-100:].tolist()),  # Use last 100 points
        "models": models,
        "ensemble_method": "weighted_average"
    }
    
    ensemble_result = simulate_advanced_mcp_call("coordinator-mcp-server", "ensemble_forecast", ensemble_args)
    
    # Display ensemble results
    print(f"\n📊 Ensemble Results:")
    print(f"   Method: {ensemble_result['ensemble_method']}")
    print(f"   Ensemble confidence: {ensemble_result['ensemble_confidence']:.4f}")
    
    individual_predictions = ensemble_result['individual_predictions']
    print(f"\n📈 Individual Model Performance:")
    for model, pred in individual_predictions.items():
        print(f"   {model}: confidence={pred['confidence']:.4f}")
    
    return model_results, ensemble_result


async def anomaly_aware_forecasting_example():
    """Demonstrate anomaly-aware forecasting."""
    print("\n" + "=" * 80)
    print("🔍 ANOMALY-AWARE FORECASTING EXAMPLE")
    print("=" * 80)
    
    # Generate data with known anomalies
    print("📊 Generating data with known anomalies...")
    data, timestamps = generate_complex_data(n_samples=1500, n_features=2, anomaly_rate=0.05)
    print(f"   Data shape: {data.shape}")
    
    # Train anomaly detection model
    print("\n🔍 Training anomaly detection model...")
    anomaly_train_args = {
        "model_type": "prophet",
        "data": json.dumps(data[:, 0].tolist()),  # Use first feature
        "model_name": "anomaly_aware_prophet",
        "model_params": {
            "interval_width": 0.99,
            "changepoint_range": 0.8
        }
    }
    
    anomaly_result = simulate_advanced_mcp_call("anomaly-mcp-server", "train_anomaly_model", anomaly_train_args)
    print(f"   Anomalies detected in training: {anomaly_result['anomaly_detection']['anomaly_count']}")
    
    # Train forecasting model
    print("\n🤖 Training forecasting model...")
    forecast_train_args = {
        "model_type": "lstm",
        "data": json.dumps(data.tolist()),
        "model_name": "anomaly_aware_lstm",
        "sequence_length": 30,
        "prediction_length": 5
    }
    
    forecast_result = simulate_advanced_mcp_call("forecasting-mcp-server", "train_forecasting_model", forecast_train_args)
    print(f"   Forecasting model trained: RMSE={forecast_result['test_metrics']['rmse']:.4f}")
    
    # Perform anomaly-aware forecasting
    print("\n🎯 Performing anomaly-aware forecasting...")
    anomaly_aware_args = {
        "data": json.dumps(data[-100:].tolist()),
        "forecasting_model": "anomaly_aware_lstm",
        "anomaly_model": "anomaly_aware_prophet",
        "anomaly_threshold": 0.95
    }
    
    # Simulate anomaly-aware forecasting result
    anomaly_aware_result = {
        "status": "success",
        "base_forecast": np.random.random(10).tolist(),
        "adjusted_forecast": np.random.random(10).tolist(),
        "anomalies_detected": 3,
        "anomaly_scores": np.random.random(100).tolist(),
        "confidence_adjustment": 0.75,
        "anomaly_threshold": 0.95
    }
    
    print(f"   Anomalies detected: {anomaly_aware_result['anomalies_detected']}")
    print(f"   Confidence adjustment: {anomaly_aware_result['confidence_adjustment']:.2f}")
    print(f"   Base forecast: {anomaly_aware_result['base_forecast'][:3]}...")
    print(f"   Adjusted forecast: {anomaly_aware_result['adjusted_forecast'][:3]}...")
    
    return anomaly_aware_result


async def real_time_analysis_example():
    """Demonstrate real-time analysis capabilities."""
    print("\n" + "=" * 80)
    print("⏱️ REAL-TIME ANALYSIS EXAMPLE")
    print("=" * 80)
    
    # Simulate real-time data stream
    print("📡 Simulating real-time data stream...")
    base_data = generate_complex_data(n_samples=1000, n_features=2)[0]
    
    # Process data in chunks
    chunk_size = 50
    n_chunks = 5
    
    print(f"   Processing {n_chunks} chunks of {chunk_size} samples each...")
    
    for i in range(n_chunks):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        chunk_data = base_data[start_idx:end_idx]
        
        print(f"\n📊 Processing chunk {i+1}/{n_chunks} (samples {start_idx}-{end_idx-1})...")
        
        # Detect anomalies in real-time
        anomaly_args = {
            "model_name": "real_time_anomaly_model",
            "data": json.dumps(chunk_data.tolist()),
            "threshold": 0.9
        }
        
        # Simulate real-time anomaly detection
        anomaly_count = np.random.randint(0, 5)
        print(f"   Anomalies detected: {anomaly_count}")
        
        # Make real-time predictions
        if i > 0:  # Need some history for prediction
            predict_args = {
                "model_name": "real_time_forecast_model",
                "data": json.dumps(chunk_data.tolist()),
                "steps_ahead": 3
            }
            
            # Simulate real-time prediction
            predictions = np.random.random(3).tolist()
            print(f"   Next 3 predictions: {[f'{p:.3f}' for p in predictions]}")
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
    
    print("\n✅ Real-time analysis completed!")


async def performance_comparison_example():
    """Demonstrate performance comparison between different approaches."""
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE COMPARISON EXAMPLE")
    print("=" * 80)
    
    # Generate test data
    print("📊 Generating test data...")
    data = generate_complex_data(n_samples=2000, n_features=3)
    print(f"   Data shape: {data[0].shape}")
    
    # Test different approaches
    approaches = {
        "Single LSTM": {"model": "lstm", "ensemble": False},
        "Single CNN": {"model": "cnn", "ensemble": False},
        "Ensemble LSTM+CNN": {"models": ["lstm", "cnn"], "ensemble": True},
        "Anomaly-Aware LSTM": {"model": "lstm", "anomaly_aware": True}
    }
    
    results = {}
    
    for approach_name, config in approaches.items():
        print(f"\n🧪 Testing {approach_name}...")
        
        if config.get("ensemble", False):
            # Ensemble approach
            ensemble_args = {
                "data": json.dumps(data[0].tolist()),
                "models": config["models"],
                "ensemble_method": "weighted_average"
            }
            result = simulate_advanced_mcp_call("coordinator-mcp-server", "ensemble_forecast", ensemble_args)
            rmse = 0.25  # Simulated
            r2 = 0.85
        elif config.get("anomaly_aware", False):
            # Anomaly-aware approach
            rmse = 0.22  # Simulated - better due to anomaly awareness
            r2 = 0.88
        else:
            # Single model approach
            rmse = 0.28 if config["model"] == "cnn" else 0.25
            r2 = 0.82 if config["model"] == "cnn" else 0.85
        
        results[approach_name] = {"rmse": rmse, "r2": r2}
        print(f"   RMSE: {rmse:.4f}, R²: {r2:.4f}")
    
    # Display comparison
    print(f"\n📊 Performance Comparison:")
    print(f"{'Approach':<25} {'RMSE':<8} {'R²':<8}")
    print("-" * 45)
    for approach, metrics in results.items():
        print(f"{approach:<25} {metrics['rmse']:<8.4f} {metrics['r2']:<8.4f}")
    
    # Find best approach
    best_approach = min(results.items(), key=lambda x: x[1]['rmse'])
    print(f"\n🏆 Best approach: {best_approach[0]} (RMSE: {best_approach[1]['rmse']:.4f})")
    
    return results


async def main():
    """Main function to run all advanced examples."""
    print("🌟 Multi-MCP Time Series Analysis System - Advanced Analysis Examples")
    print("=" * 100)
    
    try:
        # Run advanced examples
        await model_selection_example()
        await ensemble_analysis_example()
        await anomaly_aware_forecasting_example()
        await real_time_analysis_example()
        await performance_comparison_example()
        
        print("\n" + "=" * 100)
        print("✅ All advanced examples completed successfully!")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ Error running advanced examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

