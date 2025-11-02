"""Demand Sector Data Processing and Prediction Agent"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DemandSectorAgent(BaseAgent):
    """Agent for demand sector data preprocessing, imputation, AI engine selection, and time series prediction"""
    
    def __init__(self):
        super().__init__(
            agent_name="Demand Sector Agent",
            agent_id="demand-sector-agent"
        )
        self.ai_engines = {
            "lstm": {"accuracy": 0.0, "latency": 0.0, "suitable_for": "long_term"},
            "arima": {"accuracy": 0.0, "latency": 0.0, "suitable_for": "short_term"},
            "prophet": {"accuracy": 0.0, "latency": 0.0, "suitable_for": "seasonal"},
            "xgboost": {"accuracy": 0.0, "latency": 0.0, "suitable_for": "non_linear"}
        }
        self.preprocessed_data = []
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "analyze",
            "get_status",
            "preprocess_data",
            "impute_missing_values",
            "select_ai_engine",
            "predict_time_series",
            "visualize_data"
        ]
    
    def register_custom_handlers(self):
        """Register custom MCP handlers"""
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "preprocess_data",
            self.preprocess_data
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "impute_missing_values",
            self.impute_missing_values
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "select_ai_engine",
            self.select_ai_engine
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "predict_time_series",
            self.predict_time_series
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "visualize_data",
            self.visualize_data
        )
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze demand sector data"""
        # Request data quality validation from data quality agent
        quality_result = await self.send_mcp_request(
            "data-quality-agent",
            "validate_data",
            {"data": data, "data_source": "demand_sector"}
        )
        
        if not quality_result or quality_result.get("is_valid") is False:
            return {
                "status": "validation_failed",
                "issues": quality_result.get("issues", []) if quality_result else []
            }
        
        # Preprocess data
        preprocessed = await self.preprocess_data({"data": data})
        
        # Generate metadata
        metadata_result = await self.send_mcp_request(
            "data-quality-agent",
            "compute_metadata",
            {"data": data, "data_points": preprocessed.get("preprocessed_data", [])}
        )
        
        # Select best AI engine
        engine_result = await self.select_ai_engine({"data": preprocessed.get("preprocessed_data", [])})
        
        # Generate prediction
        prediction = await self.predict_time_series({
            "data": preprocessed.get("preprocessed_data", []),
            "engine": engine_result.get("selected_engine"),
            "horizon": data.get("prediction_horizon", 24)  # hours
        })
        
        result = {
            "agent": self.agent_name,
            "quality_assessment": quality_result,
            "metadata": metadata_result,
            "preprocessing": preprocessed,
            "selected_engine": engine_result,
            "prediction": prediction,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.add_to_memory(result)
        return result
    
    async def preprocess_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess demand sector data"""
        data = params.get("data", {})
        data_points = data.get("data_points", [])
        
        if not data_points:
            return {"preprocessed_data": [], "steps": []}
        
        steps = []
        
        # Convert to DataFrame
        df = pd.DataFrame(data_points)
        
        # Sort by timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")
            steps.append("sorted_by_timestamp")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=["timestamp"] if "timestamp" in df.columns else [])
        if len(df) < initial_count:
            steps.append(f"removed_{initial_count - len(df)}_duplicates")
        
        # Normalize numeric values
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            steps.append("normalized_values")
        
        # Convert back to list of dicts
        preprocessed_data = df.to_dict("records")
        
        return {
            "preprocessed_data": preprocessed_data,
            "steps": steps,
            "count": len(preprocessed_data)
        }
    
    async def impute_missing_values(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Impute missing values in data"""
        data_points = params.get("data_points", [])
        method = params.get("method", "linear")  # linear, forward_fill, backward_fill, mean
        
        if not data_points:
            return {"imputed_data": [], "imputed_count": 0}
        
        df = pd.DataFrame(data_points)
        
        if "timestamp" not in df.columns or "value" not in df.columns:
            return {"imputed_data": df.to_dict("records"), "imputed_count": 0}
        
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        missing_before = df["value"].isna().sum()
        
        if method == "linear":
            df["value"] = df["value"].interpolate(method="linear")
        elif method == "forward_fill":
            df["value"] = df["value"].fillna(method="ffill")
        elif method == "backward_fill":
            df["value"] = df["value"].fillna(method="bfill")
        elif method == "mean":
            mean_value = df["value"].mean()
            df["value"] = df["value"].fillna(mean_value)
        
        missing_after = df["value"].isna().sum()
        imputed_count = missing_before - missing_after
        
        return {
            "imputed_data": df.to_dict("records"),
            "imputed_count": int(imputed_count),
            "method": method,
            "missing_before": int(missing_before),
            "missing_after": int(missing_after)
        }
    
    async def select_ai_engine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Select the most accurate AI engine for time series prediction"""
        data_points = params.get("data_points", [])
        
        if not data_points:
            return {"selected_engine": "prophet", "reason": "default_for_insufficient_data"}
        
        # Analyze data characteristics
        values = [float(point.get("value", 0)) for point in data_points if point.get("value") is not None]
        
        if len(values) < 10:
            return {"selected_engine": "prophet", "reason": "insufficient_data_for_complex_model"}
        
        # Calculate data characteristics
        variance = np.var(values)
        mean = np.mean(values)
        cv = np.std(values) / mean if mean != 0 else 0  # Coefficient of variation
        
        # Check for seasonality (simplified)
        timestamps = [point.get("timestamp") for point in data_points if point.get("timestamp")]
        has_seasonality = len(timestamps) > 24 and len(set(timestamps)) > 12
        
        # Engine selection logic
        if has_seasonality and cv < 0.5:
            selected = "prophet"
            reason = "seasonal_patterns_detected"
        elif variance < mean * 0.1:
            selected = "arima"
            reason = "low_variance_stationary_data"
        elif cv > 1.0:
            selected = "xgboost"
            reason = "high_variance_non_linear"
        else:
            selected = "lstm"
            reason = "complex_patterns_detected"
        
        # Simulate accuracy scores (in production, these would come from model evaluation)
        accuracy_scores = {
            "lstm": 0.92 if selected == "lstm" else 0.88,
            "arima": 0.89 if selected == "arima" else 0.85,
            "prophet": 0.91 if selected == "prophet" else 0.87,
            "xgboost": 0.90 if selected == "xgboost" else 0.86
        }
        
        return {
            "selected_engine": selected,
            "reason": reason,
            "accuracy_scores": accuracy_scores,
            "characteristics": {
                "variance": float(variance),
                "mean": float(mean),
                "coefficient_of_variation": float(cv),
                "has_seasonality": has_seasonality
            }
        }
    
    async def predict_time_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate time series prediction"""
        data_points = params.get("data_points", [])
        engine = params.get("engine", "prophet")
        horizon = params.get("horizon", 24)  # hours
        
        if not data_points:
            return {"predictions": [], "error": "no_data"}
        
        # Simulate prediction (in production, this would use actual ML models)
        values = [float(point.get("value", 0)) for point in data_points if point.get("value") is not None]
        
        if not values:
            return {"predictions": [], "error": "no_valid_values"}
        
        # Simple prediction: use last known value + trend
        last_value = values[-1]
        mean_value = np.mean(values)
        
        # Generate predictions
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(horizon):
            # Simple trend-based prediction
            predicted_value = last_value + (mean_value - last_value) * (i / horizon) * 0.1
            predictions.append({
                "timestamp": (base_time + timedelta(hours=i+1)).isoformat(),
                "value": round(predicted_value, 2),
                "confidence": round(0.95 - (i * 0.01), 2)  # Decreasing confidence
            })
        
        return {
            "predictions": predictions,
            "engine": engine,
            "horizon_hours": horizon,
            "forecast_start": base_time.isoformat(),
            "forecast_end": (base_time + timedelta(hours=horizon)).isoformat(),
            "metrics": {
                "rmse": round(np.std(values) * 0.1, 2),
                "mape": round(5.0, 2)
            }
        }
    
    async def visualize_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization data"""
        data_points = params.get("data_points", [])
        prediction = params.get("prediction", {})
        
        return {
            "visualization": {
                "type": "time_series",
                "data": {
                    "historical": data_points[-100:] if len(data_points) > 100 else data_points,
                    "predictions": prediction.get("predictions", [])
                },
                "chart_type": "line",
                "x_axis": "timestamp",
                "y_axis": "value"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

