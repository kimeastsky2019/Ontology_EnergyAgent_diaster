"""
Model utility functions for time series analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
import pickle
import os
from pathlib import Path


class ModelEvaluator:
    """Utility class for evaluating time series models."""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate evaluation metrics for time series predictions.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        # Flatten arrays if needed
        y_true = y_true.flatten()
        y_pred = y_pred.flatten()
        
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'r2': float(r2)
        }
    
    @staticmethod
    def calculate_anomaly_metrics(y_true: np.ndarray, 
                                 y_pred: np.ndarray, 
                                 threshold: float = 0.1) -> Dict[str, float]:
        """
        Calculate metrics for anomaly detection.
        
        Args:
            y_true: True anomaly labels (0 or 1)
            y_pred: Predicted anomaly scores
            threshold: Threshold for anomaly classification
            
        Returns:
            Dictionary of anomaly detection metrics
        """
        y_pred_binary = (y_pred > threshold).astype(int)
        
        tp = np.sum((y_true == 1) & (y_pred_binary == 1))
        fp = np.sum((y_true == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true == 1) & (y_pred_binary == 0))
        tn = np.sum((y_true == 0) & (y_pred_binary == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else 0
        
        return {
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'accuracy': float(accuracy),
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn),
            'tn': int(tn)
        }


class ModelManager:
    """Utility class for managing model saving and loading."""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize model manager.
        
        Args:
            model_dir: Directory to store models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
    
    def save_model(self, model: Any, model_name: str, metadata: Dict[str, Any] = None) -> str:
        """
        Save model and metadata.
        
        Args:
            model: Model to save
            model_name: Name of the model
            metadata: Additional metadata to save
            
        Returns:
            Path to saved model
        """
        model_path = self.model_dir / f"{model_name}.pkl"
        metadata_path = self.model_dir / f"{model_name}_metadata.json"
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save metadata
        if metadata is None:
            metadata = {}
        
        metadata['model_name'] = model_name
        metadata['model_path'] = str(model_path)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(model_path)
    
    def load_model(self, model_name: str) -> tuple:
        """
        Load model and metadata.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Tuple of (model, metadata)
        """
        model_path = self.model_dir / f"{model_name}.pkl"
        metadata_path = self.model_dir / f"{model_name}_metadata.json"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_name} not found at {model_path}")
        
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load metadata
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        return model, metadata
    
    def list_models(self) -> List[str]:
        """
        List all available models.
        
        Returns:
            List of model names
        """
        model_files = list(self.model_dir.glob("*.pkl"))
        return [f.stem for f in model_files]


class ModelSelector:
    """Utility class for selecting the best model based on data characteristics."""
    
    @staticmethod
    def select_forecasting_model(data_shape: tuple, 
                                is_multivariate: bool = False,
                                sequence_length: int = 30,
                                prediction_length: int = 1) -> str:
        """
        Select the best forecasting model based on data characteristics.
        
        Args:
            data_shape: Shape of the data
            is_multivariate: Whether data is multivariate
            sequence_length: Length of input sequences
            prediction_length: Length of prediction sequences
            
        Returns:
            Recommended model name
        """
        n_samples, n_features = data_shape[0], data_shape[1] if len(data_shape) > 1 else 1
        
        if is_multivariate:
            if n_samples > 1000 and sequence_length > 20:
                return "multivariate_cnn_lstm"
            elif n_samples > 500:
                return "multivariate_lstm"
            else:
                return "cnn"
        else:
            if n_samples > 1000 and sequence_length > 20:
                return "lstm"
            elif n_samples > 500:
                return "cnn"
            else:
                return "autoencoder"
    
    @staticmethod
    def select_anomaly_model(data_shape: tuple,
                            is_multivariate: bool = False,
                            has_trend: bool = False,
                            has_seasonality: bool = False) -> str:
        """
        Select the best anomaly detection model based on data characteristics.
        
        Args:
            data_shape: Shape of the data
            is_multivariate: Whether data is multivariate
            has_trend: Whether data has trend
            has_seasonality: Whether data has seasonality
            
        Returns:
            Recommended model name
        """
        n_samples, n_features = data_shape[0], data_shape[1] if len(data_shape) > 1 else 1
        
        if has_trend or has_seasonality:
            return "prophet"
        elif is_multivariate and n_samples > 1000:
            return "temporal_fusion_transformer"
        elif n_samples > 1000:
            return "transformer"
        else:
            return "hmm"


def create_model_config(model_type: str, 
                       data_shape: tuple,
                       **kwargs) -> Dict[str, Any]:
    """
    Create configuration for a specific model type.
    
    Args:
        model_type: Type of model
        data_shape: Shape of the data
        **kwargs: Additional configuration parameters
        
    Returns:
        Model configuration dictionary
    """
    base_config = {
        'model_type': model_type,
        'data_shape': data_shape,
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    if model_type == 'lstm':
        config = {
            **base_config,
            'sequence_length': kwargs.get('sequence_length', 30),
            'prediction_length': kwargs.get('prediction_length', 1),
            'lstm_units': kwargs.get('lstm_units', [64, 32]),
            'dropout': kwargs.get('dropout', 0.2),
            'epochs': kwargs.get('epochs', 100),
            'batch_size': kwargs.get('batch_size', 32)
        }
    elif model_type == 'cnn':
        config = {
            **base_config,
            'sequence_length': kwargs.get('sequence_length', 30),
            'prediction_length': kwargs.get('prediction_length', 1),
            'filters': kwargs.get('filters', [64, 128, 256]),
            'kernel_sizes': kwargs.get('kernel_sizes', [2, 2, 2]),
            'dense_units': kwargs.get('dense_units', [50]),
            'epochs': kwargs.get('epochs', 100),
            'batch_size': kwargs.get('batch_size', 32)
        }
    elif model_type == 'prophet':
        config = {
            **base_config,
            'interval_width': kwargs.get('interval_width', 0.99),
            'changepoint_range': kwargs.get('changepoint_range', 0.8),
            'daily_seasonality': kwargs.get('daily_seasonality', False),
            'yearly_seasonality': kwargs.get('yearly_seasonality', False),
            'weekly_seasonality': kwargs.get('weekly_seasonality', False)
        }
    else:
        config = base_config
    
    return config


def validate_data(data: Union[np.ndarray, pd.DataFrame], 
                 model_type: str) -> bool:
    """
    Validate data for a specific model type.
    
    Args:
        data: Input data
        model_type: Type of model
        
    Returns:
        True if data is valid, False otherwise
    """
    if isinstance(data, pd.DataFrame):
        data = data.values
    
    if len(data) == 0:
        return False
    
    if model_type in ['lstm', 'cnn', 'autoencoder']:
        return len(data) >= 30  # Minimum samples for sequence models
    elif model_type == 'prophet':
        return len(data) >= 10  # Minimum samples for Prophet
    elif model_type in ['hmm', 'transformer']:
        return len(data) >= 50  # Minimum samples for complex models
    
    return True

