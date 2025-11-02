"""
CNN model for time series forecasting.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import warnings
warnings.filterwarnings('ignore')


class CNNForecaster:
    """1D CNN model for time series forecasting."""
    
    def __init__(self, 
                 sequence_length: int = 30,
                 prediction_length: int = 1,
                 filters: list = [64, 128, 256],
                 kernel_sizes: list = [2, 2, 2],
                 dense_units: list = [50],
                 dropout: float = 0.2,
                 learning_rate: float = 0.001):
        """
        Initialize CNN forecaster.
        
        Args:
            sequence_length: Length of input sequences
            prediction_length: Length of prediction sequences
            filters: List of filters for each Conv1D layer
            kernel_sizes: List of kernel sizes for each Conv1D layer
            dense_units: List of units for dense layers
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length
        self.filters = filters
        self.kernel_sizes = kernel_sizes
        self.dense_units = dense_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.model = None
        self.is_fitted = False
        self.history = None
        
    def _build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build CNN model architecture."""
        model = Sequential()
        
        # Conv1D layers
        for i, (filters, kernel_size) in enumerate(zip(self.filters, self.kernel_sizes)):
            model.add(Conv1D(
                filters=filters,
                kernel_size=kernel_size,
                activation='relu',
                input_shape=input_shape if i == 0 else None
            ))
            model.add(MaxPooling1D(pool_size=2))
        
        # Flatten layer
        model.add(Flatten())
        
        # Dense layers
        for units in self.dense_units:
            model.add(Dense(units, activation='relu'))
            model.add(Dropout(self.dropout))
        
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
        Train the CNN model.
        
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


class MultiStepCNNForecaster(CNNForecaster):
    """Multi-step CNN forecaster for longer prediction horizons."""
    
    def __init__(self, 
                 sequence_length: int = 60,
                 prediction_length: int = 7,
                 filters: list = [64, 128],
                 kernel_sizes: list = [2, 2],
                 dense_units: list = [50],
                 dropout: float = 0.2,
                 learning_rate: float = 0.001):
        """
        Initialize multi-step CNN forecaster.
        
        Args:
            sequence_length: Length of input sequences
            prediction_length: Length of prediction sequences
            filters: List of filters for each Conv1D layer
            kernel_sizes: List of kernel sizes for each Conv1D layer
            dense_units: List of units for dense layers
            dropout: Dropout rate
            learning_rate: Learning rate for optimizer
        """
        super().__init__(
            sequence_length=sequence_length,
            prediction_length=prediction_length,
            filters=filters,
            kernel_sizes=kernel_sizes,
            dense_units=dense_units,
            dropout=dropout,
            learning_rate=learning_rate
        )
    
    def _build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build multi-step CNN model architecture."""
        model = Sequential()
        
        # Conv1D layers
        for i, (filters, kernel_size) in enumerate(zip(self.filters, self.kernel_sizes)):
            model.add(Conv1D(
                filters=filters,
                kernel_size=kernel_size,
                activation='relu',
                input_shape=input_shape if i == 0 else None
            ))
            model.add(MaxPooling1D(pool_size=2))
        
        # Flatten layer
        model.add(Flatten())
        
        # Dense layers
        for units in self.dense_units:
            model.add(Dense(units, activation='relu'))
            model.add(Dropout(self.dropout))
        
        # Output layer for multi-step prediction
        model.add(Dense(self.prediction_length))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        return model

