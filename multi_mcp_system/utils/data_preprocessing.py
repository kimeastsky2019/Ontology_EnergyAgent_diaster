"""
Data preprocessing utilities for time series analysis.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional, Union
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import warnings
warnings.filterwarnings('ignore')


class TimeSeriesPreprocessor:
    """Preprocessing utilities for time series data."""
    
    def __init__(self, scaler_type: str = 'minmax'):
        """
        Initialize preprocessor.
        
        Args:
            scaler_type: Type of scaler ('minmax' or 'standard')
        """
        self.scaler_type = scaler_type
        self.scaler = MinMaxScaler() if scaler_type == 'minmax' else StandardScaler()
        self.is_fitted = False
        
    def fit_transform(self, data: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Fit scaler and transform data."""
        if isinstance(data, pd.DataFrame):
            data = data.values
            
        scaled_data = self.scaler.fit_transform(data)
        self.is_fitted = True
        return scaled_data.astype(np.float32)
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Transform data using fitted scaler."""
        if not self.is_fitted:
            raise ValueError("Scaler must be fitted before transforming data.")
            
        if isinstance(data, pd.DataFrame):
            data = data.values
            
        return self.scaler.transform(data).astype(np.float32)
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Inverse transform scaled data."""
        if not self.is_fitted:
            raise ValueError("Scaler must be fitted before inverse transforming data.")
            
        return self.scaler.inverse_transform(data)


def create_sequences(data: np.ndarray, 
                    sequence_length: int, 
                    prediction_length: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences for time series forecasting.
    
    Args:
        data: Input time series data
        sequence_length: Length of input sequences
        prediction_length: Length of prediction sequences
        
    Returns:
        Tuple of (X, y) where X is input sequences and y is target sequences
    """
    X, y = [], []
    
    for i in range(len(data) - sequence_length - prediction_length + 1):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length:i + sequence_length + prediction_length])
    
    return np.array(X), np.array(y)


def create_multivariate_sequences(data: np.ndarray, 
                                 sequence_length: int, 
                                 prediction_length: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences for multivariate time series forecasting.
    
    Args:
        data: Input multivariate time series data (samples, features)
        sequence_length: Length of input sequences
        prediction_length: Length of prediction sequences
        
    Returns:
        Tuple of (X, y) where X is input sequences and y is target sequences
    """
    X, y = [], []
    
    for i in range(len(data) - sequence_length - prediction_length + 1):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length:i + sequence_length + prediction_length])
    
    return np.array(X), np.array(y)


def split_time_series(data: Union[np.ndarray, pd.DataFrame], 
                     train_ratio: float = 0.8,
                     val_ratio: float = 0.1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Split time series data into train, validation, and test sets.
    
    Args:
        data: Time series data
        train_ratio: Ratio of data for training
        val_ratio: Ratio of data for validation
        
    Returns:
        Tuple of (train_data, val_data, test_data)
    """
    if isinstance(data, pd.DataFrame):
        data = data.values
        
    n_samples = len(data)
    train_size = int(n_samples * train_ratio)
    val_size = int(n_samples * val_ratio)
    
    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]
    
    return train_data, val_data, test_data


def detect_stationarity(data: np.ndarray, 
                       significance_level: float = 0.05) -> bool:
    """
    Simple stationarity check using rolling statistics.
    
    Args:
        data: Time series data
        significance_level: Significance level for stationarity test
        
    Returns:
        True if data appears stationary, False otherwise
    """
    # Simple heuristic: check if rolling mean and std are relatively constant
    window_size = min(50, len(data) // 4)
    
    if len(data) < window_size * 2:
        return True  # Assume stationary for very short series
    
    rolling_mean = pd.Series(data).rolling(window=window_size).mean()
    rolling_std = pd.Series(data).rolling(window=window_size).std()
    
    # Check if rolling statistics are relatively stable
    mean_std = rolling_mean.std()
    std_std = rolling_std.std()
    
    # If standard deviation of rolling statistics is small, consider stationary
    return mean_std < 0.1 and std_std < 0.1


def make_stationary(data: np.ndarray, 
                   method: str = 'diff') -> np.ndarray:
    """
    Make time series stationary.
    
    Args:
        data: Time series data
        method: Method to use ('diff', 'log_diff', 'detrend')
        
    Returns:
        Stationary time series data
    """
    if method == 'diff':
        return np.diff(data, axis=0)
    elif method == 'log_diff':
        log_data = np.log(data + 1e-8)  # Add small value to avoid log(0)
        return np.diff(log_data, axis=0)
    elif method == 'detrend':
        # Simple linear detrending
        x = np.arange(len(data))
        coeffs = np.polyfit(x, data, 1)
        trend = np.polyval(coeffs, x)
        return data - trend
    else:
        raise ValueError(f"Unknown method: {method}")


def prepare_forecasting_data(data: Union[np.ndarray, pd.DataFrame],
                           sequence_length: int,
                           prediction_length: int = 1,
                           scaler_type: str = 'minmax',
                           make_stationary: bool = False) -> dict:
    """
    Prepare data for forecasting models.
    
    Args:
        data: Input time series data
        sequence_length: Length of input sequences
        prediction_length: Length of prediction sequences
        scaler_type: Type of scaler to use
        make_stationary: Whether to make data stationary
        
    Returns:
        Dictionary containing prepared data and preprocessor
    """
    if isinstance(data, pd.DataFrame):
        data = data.values
    
    # Make stationary if requested
    if make_stationary:
        data = make_stationary(data)
    
    # Initialize preprocessor
    preprocessor = TimeSeriesPreprocessor(scaler_type=scaler_type)
    
    # Scale data
    scaled_data = preprocessor.fit_transform(data)
    
    # Create sequences
    X, y = create_sequences(scaled_data, sequence_length, prediction_length)
    
    # Split data
    train_X, val_X, test_X = split_time_series(X)
    train_y, val_y, test_y = split_time_series(y)
    
    return {
        'train_X': train_X,
        'train_y': train_y,
        'val_X': val_X,
        'val_y': val_y,
        'test_X': test_X,
        'test_y': test_y,
        'preprocessor': preprocessor,
        'original_data': data,
        'scaled_data': scaled_data
    }


def prepare_multivariate_forecasting_data(data: Union[np.ndarray, pd.DataFrame],
                                        sequence_length: int,
                                        prediction_length: int = 1,
                                        scaler_type: str = 'minmax') -> dict:
    """
    Prepare multivariate data for forecasting models.
    
    Args:
        data: Input multivariate time series data
        sequence_length: Length of input sequences
        prediction_length: Length of prediction sequences
        scaler_type: Type of scaler to use
        
    Returns:
        Dictionary containing prepared data and preprocessor
    """
    if isinstance(data, pd.DataFrame):
        data = data.values
    
    # Initialize preprocessor
    preprocessor = TimeSeriesPreprocessor(scaler_type=scaler_type)
    
    # Scale data
    scaled_data = preprocessor.fit_transform(data)
    
    # Create sequences
    X, y = create_multivariate_sequences(scaled_data, sequence_length, prediction_length)
    
    # Split data
    train_X, val_X, test_X = split_time_series(X)
    train_y, val_y, test_y = split_time_series(y)
    
    return {
        'train_X': train_X,
        'train_y': train_y,
        'val_X': val_X,
        'val_y': val_y,
        'test_X': test_X,
        'test_y': test_y,
        'preprocessor': preprocessor,
        'original_data': data,
        'scaled_data': scaled_data
    }

