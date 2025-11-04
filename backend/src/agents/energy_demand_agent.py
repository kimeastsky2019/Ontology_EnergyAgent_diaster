"""Energy Demand Analysis AI Agent"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings

from src.agents.base_agent import BaseAgent

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class EnergyDemandAgent(BaseAgent):
    """AI Agent for Energy Demand Analysis with preprocessing, forecasting, and anomaly detection"""
    
    def __init__(self):
        super().__init__(
            agent_name="Energy Demand Analysis Agent",
            agent_id="energy-demand-agent"
        )
        self.model: Optional[RandomForestRegressor] = None
        self.scaler = StandardScaler()
        self.isolation_forest: Optional[IsolationForest] = None
        self.clean_data: Optional[pd.DataFrame] = None
        self.predictions: Optional[pd.DataFrame] = None
        self.anomalies: Optional[pd.DataFrame] = None
        self.quality_report: Dict[str, Any] = {}
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "analyze",
            "get_status",
            "preprocess_data",
            "validate_data_quality",
            "detect_anomalies",
            "train_forecast_model",
            "generate_predictions",
            "get_statistics"
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
            "validate_data_quality",
            self.validate_data_quality
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "detect_anomalies",
            self.detect_anomalies
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "train_forecast_model",
            self.train_forecast_model
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "generate_predictions",
            self.generate_predictions
        )
        self.mcp_service.registry.register_handler(
            self.agent_id,
            "get_statistics",
            self.get_statistics
        )
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run full energy demand analysis pipeline"""
        try:
            # Extract data from input
            raw_data = data.get("data")
            data_path = data.get("data_path")
            
            # Load data if path provided
            if data_path:
                df = pd.read_csv(data_path)
            elif isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            elif isinstance(raw_data, dict):
                df = pd.DataFrame([raw_data])
            else:
                return {
                    "error": "invalid_data",
                    "message": "Data must be provided as 'data_path', 'data' list, or 'data' dict"
                }
            
            # Ensure required columns exist
            required_cols = ['time', 'kWh']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    "error": "missing_columns",
                    "message": f"Missing required columns: {missing_cols}"
                }
            
            # Step 1: Validate data quality
            quality_result = await self.validate_data_quality({"data": df.to_dict('records')})
            
            # Step 2: Preprocess data
            preprocessed = await self.preprocess_data({"data": df.to_dict('records')})
            
            # Step 3: Detect anomalies
            anomaly_result = await self.detect_anomalies({"data": self.clean_data.to_dict('records') if self.clean_data is not None else []})
            
            # Step 4: Train forecast model
            training_result = await self.train_forecast_model({"data": self.clean_data.to_dict('records') if self.clean_data is not None else []})
            
            # Step 5: Generate predictions
            predictions_result = await self.generate_predictions({
                "hours_ahead": data.get("hours_ahead", 168)  # Default 7 days
            })
            
            # Step 6: Get statistics
            statistics = await self.get_statistics({})
            
            result = {
                "agent": self.agent_name,
                "quality_report": quality_result,
                "anomalies": anomaly_result.get("anomalies", []),
                "training_metrics": training_result.get("metrics", {}),
                "predictions": predictions_result.get("predictions", []),
                "statistics": statistics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.add_to_memory(result)
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return {
                "error": "analysis_failed",
                "message": str(e)
            }
    
    async def validate_data_quality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive data quality validation"""
        try:
            data_points = params.get("data", [])
            if not data_points:
                return {"error": "no_data"}
            
            df = pd.DataFrame(data_points)
            
            # Ensure time column exists
            if 'time' not in df.columns:
                df['time'] = pd.date_range(start=datetime.now(), periods=len(df), freq='30min')
            
            report = {
                'total_records': len(df),
                'missing_values': {},
                'duplicates': 0,
                'outliers': {},
                'data_types': {},
                'date_range': {},
                'quality_score': 0
            }
            
            # Check missing values
            for col in df.columns:
                missing = df[col].isnull().sum()
                missing_pct = (missing / len(df)) * 100 if len(df) > 0 else 0
                report['missing_values'][col] = {
                    'count': int(missing),
                    'percentage': round(missing_pct, 2)
                }
            
            # Check duplicates
            report['duplicates'] = int(df.duplicated().sum())
            
            # Check data types
            for col in df.columns:
                report['data_types'][col] = str(df[col].dtype)
            
            # Check numeric outliers using IQR method
            for col in ['kWh', 'kW']:
                if col in df.columns:
                    numeric_col = pd.to_numeric(df[col], errors='coerce')
                    Q1 = numeric_col.quantile(0.25)
                    Q3 = numeric_col.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = ((numeric_col < (Q1 - 1.5 * IQR)) | 
                               (numeric_col > (Q3 + 1.5 * IQR))).sum()
                    report['outliers'][col] = int(outliers)
            
            # Date range
            try:
                df['time'] = pd.to_datetime(df['time'])
                report['date_range'] = {
                    'start': str(df['time'].min()),
                    'end': str(df['time'].max()),
                    'duration_days': int((df['time'].max() - df['time'].min()).days) if len(df) > 0 else 0
                }
            except:
                pass
            
            # Calculate quality score
            quality_score = 100
            missing_kwh = report['missing_values'].get('kWh', {}).get('percentage', 0)
            missing_kw = report['missing_values'].get('kW', {}).get('percentage', 0)
            duplicates_pct = (report['duplicates'] / len(df)) * 100 if len(df) > 0 else 0
            
            quality_score -= min(missing_kwh, 20)
            quality_score -= min(missing_kw, 20)
            quality_score -= min(duplicates_pct, 10)
            report['quality_score'] = round(max(quality_score, 0), 2)
            
            self.quality_report = report
            return report
            
        except Exception as e:
            logger.error(f"Data quality validation error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def preprocess_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare data for analysis"""
        try:
            data_points = params.get("data", [])
            if not data_points:
                return {"error": "no_data"}
            
            df = pd.DataFrame(data_points)
            
            # Ensure time column exists
            if 'time' not in df.columns:
                df['time'] = pd.date_range(start=datetime.now(), periods=len(df), freq='30min')
            
            # Convert time to datetime
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            
            # Remove rows with invalid timestamps
            df = df.dropna(subset=['time'])
            
            # Handle missing values in kWh and kW
            if 'kWh' in df.columns:
                df['kWh'] = pd.to_numeric(df['kWh'], errors='coerce')
            if 'kW' in df.columns:
                df['kW'] = pd.to_numeric(df['kW'], errors='coerce')
            
            # Fill missing values with interpolation
            if 'kWh' in df.columns:
                df['kWh'] = df['kWh'].interpolate(method='linear')
            if 'kW' in df.columns:
                df['kW'] = df['kW'].interpolate(method='linear')
            
            # Remove remaining NaN values
            df = df.dropna(subset=['kWh'])
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['time'], keep='first')
            
            # Sort by time
            df = df.sort_values('time').reset_index(drop=True)
            
            # Add temporal features
            df['hour'] = df['time'].dt.hour
            df['day_of_week'] = df['time'].dt.dayofweek
            df['day_of_year'] = df['time'].dt.dayofyear
            df['week_of_year'] = df['time'].dt.isocalendar().week
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Add rolling statistics
            if 'kWh' in df.columns:
                df['kWh_rolling_mean_24h'] = df['kWh'].rolling(window=48, min_periods=1).mean()
                df['kWh_rolling_std_24h'] = df['kWh'].rolling(window=48, min_periods=1).std()
            if 'kW' in df.columns:
                df['kW_rolling_mean_24h'] = df['kW'].rolling(window=48, min_periods=1).mean()
            
            self.clean_data = df
            
            return {
                "status": "success",
                "records_processed": len(df),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def detect_anomalies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using Isolation Forest"""
        try:
            if self.clean_data is None or len(self.clean_data) == 0:
                return {"error": "no_processed_data", "message": "Must preprocess data first"}
            
            df = self.clean_data.copy()
            
            # Features for anomaly detection
            features = ['kWh', 'hour', 'day_of_week', 'is_weekend']
            if 'kW' in df.columns:
                features.insert(1, 'kW')
            
            # Ensure all features exist
            available_features = [f for f in features if f in df.columns]
            if not available_features:
                return {"error": "insufficient_features"}
            
            X = df[available_features].fillna(0)
            
            # Normalize features
            X_scaled = self.scaler.fit_transform(X)
            
            # Isolation Forest
            self.isolation_forest = IsolationForest(
                contamination=0.05,  # 5% anomalies
                random_state=42,
                n_estimators=100
            )
            
            df['anomaly'] = self.isolation_forest.fit_predict(X_scaled)
            df['anomaly_score'] = self.isolation_forest.score_samples(X_scaled)
            
            # Mark anomalies (1 = normal, -1 = anomaly)
            df['is_anomaly'] = (df['anomaly'] == -1).astype(int)
            
            anomaly_count = df['is_anomaly'].sum()
            anomaly_pct = (anomaly_count / len(df)) * 100 if len(df) > 0 else 0
            
            self.anomalies = df[df['is_anomaly'] == 1].copy()
            self.clean_data = df
            
            # Prepare anomaly results
            anomalies_list = []
            for _, row in self.anomalies.iterrows():
                anomalies_list.append({
                    "timestamp": row['time'].isoformat() if pd.notna(row['time']) else None,
                    "kWh": float(row['kWh']) if 'kWh' in row and pd.notna(row['kWh']) else None,
                    "kW": float(row['kW']) if 'kW' in row and pd.notna(row['kW']) else None,
                    "anomaly_score": float(row['anomaly_score']) if 'anomaly_score' in row else None
                })
            
            return {
                "anomalies": anomalies_list,
                "count": int(anomaly_count),
                "percentage": round(anomaly_pct, 2),
                "detection_method": "isolation_forest"
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def train_forecast_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Train Random Forest model for forecasting"""
        try:
            if self.clean_data is None or len(self.clean_data) < 10:
                return {"error": "insufficient_data", "message": "Need at least 10 records to train model"}
            
            # Split data: 80% train, 20% test
            split_idx = int(len(self.clean_data) * 0.8)
            train_data = self.clean_data.iloc[:split_idx]
            test_data = self.clean_data.iloc[split_idx:]
            
            # Create features
            features = [
                'hour', 'day_of_week', 'day_of_year', 'week_of_year',
                'is_weekend', 'kWh_rolling_mean_24h', 'kWh_rolling_std_24h'
            ]
            if 'kW_rolling_mean_24h' in self.clean_data.columns:
                features.append('kW_rolling_mean_24h')
            
            available_features = [f for f in features if f in train_data.columns]
            X_train = train_data[available_features].fillna(method='ffill').fillna(0)
            y_train = train_data['kWh']
            
            X_test = test_data[available_features].fillna(method='ffill').fillna(0)
            y_test = test_data['kWh']
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Make predictions on test set
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100 if len(y_test) > 0 else 0
            
            metrics = {
                'MAE': round(mae, 2),
                'RMSE': round(rmse, 2),
                'R2': round(r2, 4),
                'MAPE': round(mape, 2)
            }
            
            return {
                "status": "success",
                "metrics": metrics,
                "train_records": len(train_data),
                "test_records": len(test_data)
            }
            
        except Exception as e:
            logger.error(f"Model training error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def generate_predictions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate future predictions"""
        try:
            if self.model is None:
                return {"error": "model_not_trained", "message": "Must train model first"}
            
            if self.clean_data is None or len(self.clean_data) == 0:
                return {"error": "no_data"}
            
            hours_ahead = params.get("hours_ahead", 168)  # Default 7 days
            
            last_timestamp = self.clean_data['time'].max()
            last_record = self.clean_data.iloc[-1]
            
            future_predictions = []
            
            features = [
                'hour', 'day_of_week', 'day_of_year', 'week_of_year',
                'is_weekend', 'kWh_rolling_mean_24h', 'kWh_rolling_std_24h'
            ]
            if 'kW_rolling_mean_24h' in self.clean_data.columns:
                features.append('kW_rolling_mean_24h')
            
            for i in range(1, hours_ahead + 1):
                future_time = last_timestamp + timedelta(minutes=30 * i)
                
                # Create features for future timestamp
                future_features = {
                    'hour': future_time.hour,
                    'day_of_week': future_time.weekday(),
                    'day_of_year': future_time.timetuple().tm_yday,
                    'week_of_year': future_time.isocalendar()[1],
                    'is_weekend': 1 if future_time.weekday() in [5, 6] else 0,
                    'kWh_rolling_mean_24h': float(last_record['kWh_rolling_mean_24h']) if 'kWh_rolling_mean_24h' in last_record else 0,
                    'kWh_rolling_std_24h': float(last_record['kWh_rolling_std_24h']) if 'kWh_rolling_std_24h' in last_record else 0
                }
                
                if 'kW_rolling_mean_24h' in last_record:
                    future_features['kW_rolling_mean_24h'] = float(last_record['kW_rolling_mean_24h'])
                
                X_future = pd.DataFrame([future_features])
                prediction = self.model.predict(X_future)[0]
                
                future_predictions.append({
                    'timestamp': future_time.isoformat(),
                    'predicted_kWh': round(float(prediction), 2),
                    'confidence_lower': round(float(prediction * 0.85), 2),
                    'confidence_upper': round(float(prediction * 1.15), 2)
                })
            
            self.predictions = pd.DataFrame(future_predictions)
            
            return {
                "status": "success",
                "predictions": future_predictions,
                "count": len(future_predictions),
                "horizon_hours": hours_ahead
            }
            
        except Exception as e:
            logger.error(f"Prediction generation error: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key statistics"""
        try:
            if self.clean_data is None or len(self.clean_data) == 0:
                return {"error": "no_data"}
            
            df = self.clean_data
            
            stats = {
                'total_energy_consumed': round(float(df['kWh'].sum()), 2) if 'kWh' in df.columns else 0,
                'average_consumption': round(float(df['kWh'].mean()), 2) if 'kWh' in df.columns else 0,
                'peak_demand': round(float(df['kW'].max()), 2) if 'kW' in df.columns else 0,
                'min_demand': round(float(df['kW'].min()), 2) if 'kW' in df.columns else 0,
                'std_deviation': round(float(df['kWh'].std()), 2) if 'kWh' in df.columns else 0,
                'total_records': len(df),
                'anomalies_detected': int(df['is_anomaly'].sum()) if 'is_anomaly' in df.columns else 0,
                'data_quality_score': self.quality_report.get('quality_score', 0)
            }
            
            # Peak hours analysis
            if 'hour' in df.columns and 'kWh' in df.columns:
                hourly_avg = df.groupby('hour')['kWh'].mean()
                stats['peak_hour'] = int(hourly_avg.idxmax()) if len(hourly_avg) > 0 else 0
                stats['off_peak_hour'] = int(hourly_avg.idxmin()) if len(hourly_avg) > 0 else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation error: {e}", exc_info=True)
            return {"error": str(e)}


