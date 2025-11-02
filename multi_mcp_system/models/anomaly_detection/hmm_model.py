"""
HMM model for anomaly detection in time series.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from hmmlearn.hmm import GaussianHMM
except ImportError:
    print("Warning: hmmlearn not installed. Please install hmmlearn.")
    GaussianHMM = None


class HMMAnomalyDetector:
    """Hidden Markov Model based anomaly detector for time series data."""
    
    def __init__(self, 
                 n_components: int = 10,
                 covariance_type: str = "diag",
                 n_iter: int = 1000,
                 random_state: Optional[int] = None):
        """
        Initialize HMM anomaly detector.
        
        Args:
            n_components: Number of hidden states
            covariance_type: Type of covariance parameters
            n_iter: Maximum number of iterations
            random_state: Random state for reproducibility
        """
        if GaussianHMM is None:
            raise ImportError("hmmlearn is not installed. Please install hmmlearn.")
        
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.n_iter = n_iter
        self.random_state = random_state
        self.model = None
        self.is_fitted = False
        self.hidden_states = None
        self.anomaly_scores = None
        
    def _prepare_data(self, data: np.ndarray, include_volume: bool = False) -> np.ndarray:
        """
        Prepare data for HMM.
        
        Args:
            data: Time series data
            include_volume: Whether to include volume-like features
            
        Returns:
            Prepared data for HMM
        """
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        
        # Calculate differences
        diff = np.diff(data, axis=0)
        
        if include_volume and data.shape[1] == 1:
            # Create volume-like feature (absolute difference)
            volume = np.abs(diff).reshape(-1, 1)
            X = np.column_stack([diff, volume])
        else:
            X = diff
        
        return X
    
    def fit(self, data: np.ndarray, include_volume: bool = False) -> Dict[str, Any]:
        """
        Fit HMM model to data.
        
        Args:
            data: Time series data
            include_volume: Whether to include volume-like features
            
        Returns:
            Training results
        """
        # Prepare data
        X = self._prepare_data(data, include_volume)
        
        # Initialize HMM model
        self.model = GaussianHMM(
            n_components=self.n_components,
            covariance_type=self.covariance_type,
            n_iter=self.n_iter,
            random_state=self.random_state
        )
        
        # Fit model
        self.model.fit(X)
        
        # Get hidden states
        self.hidden_states = self.model.predict(X)
        
        # Calculate anomaly scores
        self.anomaly_scores = self._calculate_anomaly_scores(X)
        
        self.is_fitted = True
        
        return {
            "status": "success",
            "data_points": len(data),
            "n_components": self.n_components,
            "converged": self.model.monitor_.converged,
            "n_iter": self.model.monitor_.iter
        }
    
    def _calculate_anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """Calculate anomaly scores based on state probabilities."""
        # Get log probabilities for each state
        log_probs = self.model.score_samples(X)
        
        # Convert to probabilities
        probs = np.exp(log_probs)
        
        # Calculate anomaly score as negative log probability
        anomaly_scores = -log_probs
        
        return anomaly_scores
    
    def detect_anomalies(self, threshold: float = 0.95) -> Dict[str, Any]:
        """
        Detect anomalies in the fitted data.
        
        Args:
            threshold: Percentile threshold for anomaly detection
            
        Returns:
            Anomaly detection results
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before detecting anomalies.")
        
        # Calculate threshold value
        threshold_value = np.percentile(self.anomaly_scores, threshold * 100)
        
        # Detect anomalies
        is_anomaly = self.anomaly_scores > threshold_value
        
        # Get anomaly statistics
        anomaly_count = np.sum(is_anomaly)
        total_points = len(is_anomaly)
        anomaly_rate = anomaly_count / total_points if total_points > 0 else 0
        
        # Get anomaly indices and scores
        anomaly_indices = np.where(is_anomaly)[0]
        anomaly_scores = self.anomaly_scores[is_anomaly]
        
        return {
            "anomaly_scores": self.anomaly_scores.tolist(),
            "is_anomaly": is_anomaly.tolist(),
            "anomaly_count": int(anomaly_count),
            "total_points": int(total_points),
            "anomaly_rate": float(anomaly_rate),
            "threshold_value": float(threshold_value),
            "anomaly_indices": anomaly_indices.tolist(),
            "anomaly_scores_values": anomaly_scores.tolist()
        }
    
    def predict_anomalies(self, 
                         new_data: np.ndarray, 
                         threshold: float = 0.95,
                         include_volume: bool = False) -> Dict[str, Any]:
        """
        Predict anomalies for new data.
        
        Args:
            new_data: New time series data
            threshold: Percentile threshold for anomaly detection
            include_volume: Whether to include volume-like features
            
        Returns:
            Anomaly prediction results
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions.")
        
        # Prepare new data
        X = self._prepare_data(new_data, include_volume)
        
        # Calculate anomaly scores
        anomaly_scores = self._calculate_anomaly_scores(X)
        
        # Calculate threshold value based on training data
        threshold_value = np.percentile(self.anomaly_scores, threshold * 100)
        
        # Detect anomalies
        is_anomaly = anomaly_scores > threshold_value
        
        # Get anomaly statistics
        anomaly_count = np.sum(is_anomaly)
        total_points = len(is_anomaly)
        anomaly_rate = anomaly_count / total_points if total_points > 0 else 0
        
        # Get anomaly indices and scores
        anomaly_indices = np.where(is_anomaly)[0]
        anomaly_scores_values = anomaly_scores[is_anomaly]
        
        return {
            "anomaly_scores": anomaly_scores.tolist(),
            "is_anomaly": is_anomaly.tolist(),
            "anomaly_count": int(anomaly_count),
            "total_points": int(total_points),
            "anomaly_rate": float(anomaly_rate),
            "threshold_value": float(threshold_value),
            "anomaly_indices": anomaly_indices.tolist(),
            "anomaly_scores_values": anomaly_scores_values.tolist()
        }
    
    def get_hidden_states(self) -> np.ndarray:
        """Get the hidden states for the fitted data."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting hidden states.")
        
        return self.hidden_states
    
    def get_state_transitions(self) -> np.ndarray:
        """Get the state transition matrix."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting state transitions.")
        
        return self.model.transmat_
    
    def get_state_means(self) -> np.ndarray:
        """Get the means for each hidden state."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting state means.")
        
        return self.model.means_
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get model summary information."""
        if not self.is_fitted:
            return {"status": "Model not fitted"}
        
        return {
            "status": "fitted",
            "n_components": self.n_components,
            "covariance_type": self.covariance_type,
            "converged": self.model.monitor_.converged,
            "n_iter": self.model.monitor_.iter,
            "log_likelihood": float(self.model.score(self._prepare_data(np.array([0, 1, 2, 3, 4, 5])))),
            "state_means": self.model.means_.tolist(),
            "transition_matrix": self.model.transmat_.tolist()
        }
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving.")
        
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'hidden_states': self.hidden_states,
                'anomaly_scores': self.anomaly_scores,
                'params': {
                    'n_components': self.n_components,
                    'covariance_type': self.covariance_type,
                    'n_iter': self.n_iter,
                    'random_state': self.random_state
                }
            }, f)
    
    def load_model(self, filepath: str) -> None:
        """Load a pre-trained model."""
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.model = data['model']
        self.hidden_states = data['hidden_states']
        self.anomaly_scores = data['anomaly_scores']
        params = data['params']
        
        self.n_components = params['n_components']
        self.covariance_type = params['covariance_type']
        self.n_iter = params['n_iter']
        self.random_state = params['random_state']
        
        self.is_fitted = True

