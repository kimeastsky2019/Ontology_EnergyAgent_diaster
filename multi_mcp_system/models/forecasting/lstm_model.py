"""
LSTM model for time series forecasting.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import warnings
warnings.filterwarnings('ignore')


class LSTMForecaster:
    """LSTM model for time series forecasting."""
    
    def __init__(self, 
                 sequence_length: int = 30,
                 prediction_length: int = 1,
                 lstm_units: list = [64, 32],
                 dropout: float = 0.2,
                 learning_rate: float = 0.001):
        """
        Initialize LSTM forecaster.
        
        Args:
            sequence_length: Length of input sequences
            prediction_length: Length of prediction sequences
            lstm_units: List of LSTM units for each layer
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.model = None
        self.is_fitted = False
        self.history = None
        
    def _build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build LSTM model architecture."""
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(
            units=self.lstm_units[0],
            return_sequences=len(self.lstm_units) > 1,
            input_shape=input_shape,
            dropout=self.dropout,
            recurrent_dropout=self.dropout
        ))
        
        # Additional LSTM layers
        for i, units in enumerate(self.lstm_units[1:], 1):
            is_last = i == len(self.lstm_units) - 1
            model.add(LSTM(
                units=units,
                return_sequences=not is_last,
                dropout=self.dropout,
                recurrent_dropout=self.dropout
            ))
        
        # Output layer
        model.add(Dense(self.prediction_length))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def fit(self, 
            X_train: np.ndarray, 
            y_train: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None,
            epochs: int = 100,
            batch_size: int = 32,
            verbose: int = 1) -> Dict[str, Any]:
        """
        Train the LSTM model.
        
        Args:
            X_train: Training input sequences
            y_train: Training target sequences
            X_val: Validation input sequences
            y_val: Validation target sequences
            epochs: Number of training epochs
            batch_size: Batch size
            verbose: Verbosity level
            
        Returns:
            Training history
        """
        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self._build_model(input_shape)
        
        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if validation_data else 'loss',
                patience=10,
                restore_best_weights=True
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose,
            shuffle=False
        )
        
        self.is_fitted = True
        
        return {
            'loss': self.history.history['loss'],
            'val_loss': self.history.history.get('val_loss', []),
            'mae': self.history.history['mae'],
            'val_mae': self.history.history.get('val_mae', [])
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.
        
        Args:
            X: Input sequences
            
        Returns:
            Predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions.")
        
        return self.model.predict(X, verbose=0)
    
    def predict_future(self, 
                      last_sequence: np.ndarray, 
                      steps: int) -> np.ndarray:
        """
        Predict future values using recursive prediction.
        
        Args:
            last_sequence: Last known sequence
            steps: Number of steps to predict ahead
            
        Returns:
            Future predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions.")
        
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            # Reshape for prediction
            X_pred = current_sequence.reshape(1, self.sequence_length, -1)
            
            # Make prediction
            pred = self.model.predict(X_pred, verbose=0)
            predictions.append(pred[0])
            
            # Update sequence for next prediction
            if self.prediction_length == 1:
                current_sequence = np.append(
                    current_sequence[1:], 
                    pred[0]
                ).reshape(-1, 1)
            else:
                current_sequence = np.append(
                    current_sequence[self.prediction_length:], 
                    pred[0]
                ).reshape(-1, 1)
        
        return np.array(predictions)
    
    def get_model_summary(self) -> str:
        """Get model architecture summary."""
        if self.model is None:
            return "Model not built yet."
        
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        self.model.summary()
        sys.stdout = old_stdout
        
        return buffer.getvalue()
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving.")
        
        self.model.save(filepath)
    
    def load_model(self, filepath: str) -> None:
        """Load a pre-trained model."""
        self.model = tf.keras.models.load_model(filepath)
        self.is_fitted = True


class MultiStepLSTMForecaster(LSTMForecaster):
    """Multi-step LSTM forecaster for longer prediction horizons."""
    
    def __init__(self, 
                 sequence_length: int = 60,
                 prediction_length: int = 7,
                 lstm_units: list = [128, 64],
                 dropout: float = 0.2,
                 learning_rate: float = 0.001):
        """
        Initialize multi-step LSTM forecaster.
        
        Args:
            sequence_length: Length of input sequences
            prediction_length: Length of prediction sequences
            lstm_units: List of LSTM units for each layer
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        super().__init__(
            sequence_length=sequence_length,
            prediction_length=prediction_length,
            lstm_units=lstm_units,
            dropout=dropout,
            learning_rate=learning_rate
        )
    
    def _build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build multi-step LSTM model architecture."""
        model = Sequential()
        
        # LSTM layers
        for i, units in enumerate(self.lstm_units):
            is_last = i == len(self.lstm_units) - 1
            model.add(LSTM(
                units=units,
                return_sequences=not is_last,
                input_shape=input_shape if i == 0 else None,
                dropout=self.dropout,
                recurrent_dropout=self.dropout
            ))
        
        # Output layer for multi-step prediction
        model.add(Dense(self.prediction_length))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model

