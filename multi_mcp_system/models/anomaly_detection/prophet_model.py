"""
Prophet model for anomaly detection in time series.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from fbprophet import Prophet
except ImportError:
    try:
        from prophet import Prophet
    except ImportError:
        print("Warning: Prophet not installed. Please install fbprophet or prophet.")
        Prophet = None


class ProphetAnomalyDetector:
    """Prophet-based anomaly detector for time series data."""
    
    def __init__(self, 
                 interval_width: float = 0.99,
                 changepoint_range: float = 0.8,
                 daily_seasonality: bool = False,
                 yearly_seasonality: bool = False,
                 weekly_seasonality: bool = False,
                 seasonality_mode: str = 'multiplicative'):
        """
        Initialize Prophet anomaly detector.
        
        Args:
            interval_width: Width of the uncertainty intervals
            changepoint_range: Proportion of history in which trend changepoints will be estimated
            daily_seasonality: Whether to include daily seasonality
            yearly_seasonality: Whether to include yearly seasonality
            weekly_seasonality: Whether to include weekly seasonality
            seasonality_mode: 'additive' or 'multiplicative'
        """
        if Prophet is None:
            raise ImportError("Prophet is not installed. Please install fbprophet or prophet.")
        
        self.interval_width = interval_width
        self.changepoint_range = changepoint_range
        self.daily_seasonality = daily_seasonality
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.seasonality_mode = seasonality_mode
        self.model = None
        self.is_fitted = False
        self.forecast = None
        
    def _prepare_data(self, data: np.ndarray, timestamps: Optional[np.ndarray] = None) -> pd.DataFrame:
        """Prepare data for Prophet."""
        if timestamps is None:
            timestamps = pd.date_range(start='2020-01-01', periods=len(data), freq='D')
        
        df = pd.DataFrame({
            'ds': timestamps,
            'y': data
        })
        
        return df
    
    def fit(self, data: np.ndarray, timestamps: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Fit Prophet model to data.
        
        Args:
            data: Time series data
            timestamps: Optional timestamps for the data
            
        Returns:
            Training results
        """
        # Prepare data
        df = self._prepare_data(data, timestamps)
        
        # Initialize Prophet model
        self.model = Prophet(
            interval_width=self.interval_width,
            changepoint_range=self.changepoint_range,
            daily_seasonality=self.daily_seasonality,
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            seasonality_mode=self.seasonality_mode
        )
        
        # Fit model
        self.model.fit(df)
        
        # Make forecast
        self.forecast = self.model.predict(df)
        
        self.is_fitted = True
        
        return {
            "status": "success",
            "data_points": len(data),
            "model_params": self.model.params
        }
    
    def detect_anomalies(self, threshold: float = 0.1) -> Dict[str, Any]:
        """
        Detect anomalies in the fitted data.
        
        Args:
            threshold: Threshold for anomaly detection (as fraction of data range)
            
        Returns:
            Anomaly detection results
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before detecting anomalies.")
        
        # Calculate anomaly scores
        forecasted = self.forecast[['ds', 'trend', 'yhat', 'yhat_lower', 'yhat_upper', 'y']].copy()
        
        # Detect anomalies
        forecasted['anomaly'] = 0
        forecasted.loc[forecasted['y'] > forecasted['yhat_upper'], 'anomaly'] = 1
        forecasted.loc[forecasted['y'] < forecasted['yhat_lower'], 'anomaly'] = -1
        
        # Calculate anomaly importance
        forecasted['importance'] = 0
        forecasted.loc[forecasted['anomaly'] == 1, 'importance'] = \
            (forecasted['y'] - forecasted['yhat_upper']) / forecasted['y']
        forecasted.loc[forecasted['anomaly'] == -1, 'importance'] = \
            (forecasted['yhat_lower'] - forecasted['y']) / forecasted['y']
        
        # Filter by threshold
        data_range = forecasted['y'].max() - forecasted['y'].min()
        threshold_value = threshold * data_range
        
        forecasted['is_anomaly'] = (forecasted['importance'].abs() > threshold_value) & (forecasted['anomaly'] != 0)
        
        # Get anomaly statistics
        anomalies = forecasted[forecasted['is_anomaly']]
        anomaly_count = len(anomalies)
        total_points = len(forecasted)
        anomaly_rate = anomaly_count / total_points if total_points > 0 else 0
        
        return {
            "anomaly_data": forecasted.to_dict('records'),
            "anomaly_count": anomaly_count,
            "total_points": total_points,
            "anomaly_rate": anomaly_rate,
            "anomalies": anomalies.to_dict('records')
        }
    
    def predict_anomalies(self, 
                         new_data: np.ndarray, 
                         timestamps: Optional[np.ndarray] = None,
                         threshold: float = 0.1) -> Dict[str, Any]:
        """
        Predict anomalies for new data.
        
        Args:
            new_data: New time series data
            timestamps: Optional timestamps for the new data
            threshold: Threshold for anomaly detection
            
        Returns:
            Anomaly prediction results
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions.")
        
        # Prepare new data
        new_df = self._prepare_data(new_data, timestamps)
        
        # Make forecast for new data
        new_forecast = self.model.predict(new_df)
        
        # Detect anomalies
        forecasted = new_forecast[['ds', 'trend', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        forecasted['y'] = new_data
        
        # Detect anomalies
        forecasted['anomaly'] = 0
        forecasted.loc[forecasted['y'] > forecasted['yhat_upper'], 'anomaly'] = 1
        forecasted.loc[forecasted['y'] < forecasted['yhat_lower'], 'anomaly'] = -1
        
        # Calculate anomaly importance
        forecasted['importance'] = 0
        forecasted.loc[forecasted['anomaly'] == 1, 'importance'] = \
            (forecasted['y'] - forecasted['yhat_upper']) / forecasted['y']
        forecasted.loc[forecasted['anomaly'] == -1, 'importance'] = \
            (forecasted['yhat_lower'] - forecasted['y']) / forecasted['y']
        
        # Filter by threshold
        data_range = forecasted['y'].max() - forecasted['y'].min()
        threshold_value = threshold * data_range
        
        forecasted['is_anomaly'] = (forecasted['importance'].abs() > threshold_value) & (forecasted['anomaly'] != 0)
        
        # Get anomaly statistics
        anomalies = forecasted[forecasted['is_anomaly']]
        anomaly_count = len(anomalies)
        total_points = len(forecasted)
        anomaly_rate = anomaly_count / total_points if total_points > 0 else 0
        
        return {
            "anomaly_data": forecasted.to_dict('records'),
            "anomaly_count": anomaly_count,
            "total_points": total_points,
            "anomaly_rate": anomaly_rate,
            "anomalies": anomalies.to_dict('records')
        }
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get model summary information."""
        if not self.is_fitted:
            return {"status": "Model not fitted"}
        
        return {
            "status": "fitted",
            "interval_width": self.interval_width,
            "changepoint_range": self.changepoint_range,
            "seasonality_mode": self.seasonality_mode,
            "daily_seasonality": self.daily_seasonality,
            "yearly_seasonality": self.yearly_seasonality,
            "weekly_seasonality": self.weekly_seasonality
        }
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving.")
        
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'forecast': self.forecast,
                'params': {
                    'interval_width': self.interval_width,
                    'changepoint_range': self.changepoint_range,
                    'daily_seasonality': self.daily_seasonality,
                    'yearly_seasonality': self.yearly_seasonality,
                    'weekly_seasonality': self.weekly_seasonality,
                    'seasonality_mode': self.seasonality_mode
                }
            }, f)
    
    def load_model(self, filepath: str) -> None:
        """Load a pre-trained model."""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.model = data['model']
        self.forecast = data['forecast']
        params = data['params']
        
        self.interval_width = params['interval_width']
        self.changepoint_range = params['changepoint_range']
        self.daily_seasonality = params['daily_seasonality']
        self.yearly_seasonality = params['yearly_seasonality']
        self.weekly_seasonality = params['weekly_seasonality']
        self.seasonality_mode = params['seasonality_mode']
        
        self.is_fitted = True

