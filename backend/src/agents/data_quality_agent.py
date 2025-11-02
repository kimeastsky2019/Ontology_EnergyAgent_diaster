"""Data Quality and Metadata Agent"""
from typing import Dict, Any, List
import logging
from datetime import datetime
import numpy as np
from typing import Optional

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DataQualityAgent(BaseAgent):
    """Agent for metadata computation and data quality validation"""
    
    def __init__(self):
        super().__init__(
            agent_name="Data Quality Agent",
            agent_id="data-quality-agent"
        )
        self.quality_metrics = {
            "completeness": 0.0,
            "accuracy": 0.0,
            "consistency": 0.0,
            "timeliness": 0.0,
            "validity": 0.0
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "analyze",
            "get_status",
            "validate_data",
            "compute_metadata",
            "assess_data_quality",
            "detect_anomalies"
        ]
    
    def register_custom_handlers(self):
        """Register custom MCP handlers"""
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "validate_data",
            self.validate_data
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "compute_metadata",
            self.compute_metadata
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "assess_data_quality",
            self.assess_data_quality
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "detect_anomalies",
            self.detect_anomalies
        )
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return quality assessment"""
        result = await self.assess_data_quality(data)
        self.add_to_memory(result)
        return result
    
    async def validate_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality"""
        data = params.get("data", {})
        data_source = params.get("data_source", "unknown")
        
        validation_result = {
            "data_source": data_source,
            "timestamp": datetime.utcnow().isoformat(),
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check for missing values
        missing_fields = []
        required_fields = ["timestamp", "value"]
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
                validation_result["is_valid"] = False
        
        if missing_fields:
            validation_result["issues"].append({
                "type": "missing_fields",
                "fields": missing_fields,
                "severity": "high"
            })
        
        # Validate data types
        if "value" in data:
            try:
                float(data["value"])
            except (ValueError, TypeError):
                validation_result["is_valid"] = False
                validation_result["issues"].append({
                    "type": "invalid_type",
                    "field": "value",
                    "expected": "number",
                    "severity": "high"
                })
        
        # Check timestamp validity
        if "timestamp" in data:
            try:
                datetime.fromisoformat(str(data["timestamp"]).replace("Z", "+00:00"))
            except (ValueError, TypeError):
                validation_result["warnings"].append({
                    "type": "timestamp_format",
                    "field": "timestamp",
                    "severity": "medium"
                })
        
        return validation_result
    
    async def compute_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compute metadata from data"""
        data = params.get("data", {})
        data_points = params.get("data_points", [])
        
        metadata = {
            "data_source": data.get("data_source", "unknown"),
            "record_count": len(data_points),
            "timestamp_range": None,
            "value_statistics": {},
            "data_quality": {},
            "computed_at": datetime.utcnow().isoformat()
        }
        
        if data_points:
            values = [float(point.get("value", 0)) for point in data_points if "value" in point]
            
            if values:
                metadata["value_statistics"] = {
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values)),
                    "count": len(values)
                }
            
            timestamps = [point.get("timestamp") for point in data_points if "timestamp" in point]
            if timestamps:
                metadata["timestamp_range"] = {
                    "start": min(timestamps),
                    "end": max(timestamps)
                }
        
        # Compute data quality metrics
        quality_assessment = await self.assess_data_quality({"data_points": data_points})
        metadata["data_quality"] = quality_assessment.get("quality_score", 0.0)
        
        return metadata
    
    async def assess_data_quality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall data quality"""
        data_points = params.get("data_points", [])
        
        if not data_points:
            return {
                "quality_score": 0.0,
                "status": "insufficient_data",
                "metrics": {}
            }
        
        metrics = {}
        
        # Completeness: percentage of non-null values
        total_fields = len(data_points) * 2  # timestamp + value
        non_null_count = sum(
            1 for point in data_points
            if point.get("timestamp") and point.get("value") is not None
        )
        metrics["completeness"] = (non_null_count / len(data_points)) * 100 if data_points else 0
        
        # Validity: percentage of valid numeric values
        valid_values = [
            float(point.get("value"))
            for point in data_points
            if point.get("value") is not None
        ]
        try:
            [float(v) for v in valid_values]
            metrics["validity"] = (len(valid_values) / len(data_points)) * 100 if data_points else 0
        except:
            metrics["validity"] = 0
        
        # Consistency: check for outliers (using IQR)
        if len(valid_values) > 4:
            q1 = np.percentile(valid_values, 25)
            q3 = np.percentile(valid_values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = [v for v in valid_values if v < lower_bound or v > upper_bound]
            metrics["consistency"] = ((len(valid_values) - len(outliers)) / len(valid_values)) * 100
        else:
            metrics["consistency"] = 100.0
        
        # Timeliness: check timestamp freshness
        if data_points:
            latest_timestamp = max(
                point.get("timestamp", "")
                for point in data_points
                if point.get("timestamp")
            )
            if latest_timestamp:
                try:
                    latest_dt = datetime.fromisoformat(str(latest_timestamp).replace("Z", "+00:00"))
                    age_hours = (datetime.utcnow() - latest_dt.replace(tzinfo=None)).total_seconds() / 3600
                    # Consider data fresh if less than 1 hour old
                    metrics["timeliness"] = max(0, 100 - (age_hours * 10))
                except:
                    metrics["timeliness"] = 50.0
            else:
                metrics["timeliness"] = 0.0
        else:
            metrics["timeliness"] = 0.0
        
        # Overall quality score (weighted average)
        weights = {
            "completeness": 0.3,
            "validity": 0.3,
            "consistency": 0.2,
            "timeliness": 0.2
        }
        
        quality_score = sum(
            metrics[key] * weights.get(key, 0)
            for key in weights.keys()
            if key in metrics
        )
        
        return {
            "quality_score": round(quality_score, 2),
            "status": "excellent" if quality_score >= 90 else "good" if quality_score >= 70 else "poor",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def detect_anomalies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in data"""
        data_points = params.get("data_points", [])
        threshold = params.get("threshold", 3.0)  # Z-score threshold
        
        if not data_points:
            return {"anomalies": [], "count": 0}
        
        values = [
            float(point.get("value"))
            for point in data_points
            if point.get("value") is not None
        ]
        
        if len(values) < 3:
            return {"anomalies": [], "count": 0}
        
        mean = np.mean(values)
        std = np.std(values)
        
        anomalies = []
        for i, point in enumerate(data_points):
            if point.get("value") is not None:
                value = float(point["value"])
                z_score = abs((value - mean) / std) if std > 0 else 0
                
                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "timestamp": point.get("timestamp"),
                        "value": value,
                        "z_score": round(z_score, 2),
                        "severity": "high" if z_score > 5 else "medium"
                    })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "detection_method": "z_score",
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }

