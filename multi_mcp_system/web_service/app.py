"""
Flask 웹 애플리케이션 - Multi-MCP Time Series Analysis System
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import threading
import queue
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from utils.model_utils import ModelEvaluator, ModelManager, ModelSelector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
forecasting_models = {}
anomaly_models = {}
analysis_history = []
model_manager = ModelManager("web_models")
model_evaluator = ModelEvaluator()

# Message queue for real-time updates
message_queue = queue.Queue()


class MCPServiceSimulator:
    """MCP 서비스 시뮬레이터 - 실제 MCP 서버와 통신하는 대신 시뮬레이션"""
    
    def __init__(self):
        self.forecasting_models = {}
        self.anomaly_models = {}
    
    async def train_forecasting_model(self, model_type, data, model_name, **kwargs):
        """예측 모델 훈련 시뮬레이션"""
        # 데이터 준비
        if isinstance(data, str):
            data = json.loads(data)
        data = np.array(data)
        
        # 시뮬레이션된 훈련 결과
        if model_type == "lstm":
            metrics = {"mse": 0.05, "rmse": 0.22, "mae": 0.18, "r2": 0.88}
        elif model_type == "cnn":
            metrics = {"mse": 0.08, "rmse": 0.28, "mae": 0.22, "r2": 0.82}
        else:
            metrics = {"mse": 0.06, "rmse": 0.24, "mae": 0.20, "r2": 0.85}
        
        self.forecasting_models[model_name] = {
            "model_type": model_type,
            "metrics": metrics,
            "trained_at": datetime.now().isoformat(),
            "data_shape": data.shape
        }
        
        return {
            "status": "success",
            "model_name": model_name,
            "model_type": model_type,
            "metrics": metrics
        }
    
    async def train_anomaly_model(self, model_type, data, model_name, **kwargs):
        """이상치 탐지 모델 훈련 시뮬레이션"""
        if isinstance(data, str):
            data = json.loads(data)
        data = np.array(data)
        
        # 시뮬레이션된 이상치 탐지 결과
        anomaly_count = np.random.randint(10, 50)
        total_points = len(data)
        anomaly_rate = anomaly_count / total_points
        
        self.anomaly_models[model_name] = {
            "model_type": model_type,
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_rate,
            "trained_at": datetime.now().isoformat(),
            "data_shape": data.shape
        }
        
        return {
            "status": "success",
            "model_name": model_name,
            "model_type": model_type,
            "anomaly_detection": {
                "anomaly_count": anomaly_count,
                "anomaly_rate": anomaly_rate
            }
        }
    
    async def predict_forecasting(self, model_name, data, steps_ahead=1):
        """예측 수행 시뮬레이션"""
        if model_name not in self.forecasting_models:
            return {"status": "error", "message": "Model not found"}
        
        if isinstance(data, str):
            data = json.loads(data)
        data = np.array(data)
        
        # 시뮬레이션된 예측값
        predictions = np.random.random(steps_ahead).tolist()
        
        return {
            "status": "success",
            "model_name": model_name,
            "predictions": predictions,
            "steps_ahead": steps_ahead
        }
    
    async def detect_anomalies(self, model_name, data, threshold=0.95):
        """이상치 탐지 시뮬레이션"""
        if model_name not in self.anomaly_models:
            return {"status": "error", "message": "Model not found"}
        
        if isinstance(data, str):
            data = json.loads(data)
        data = np.array(data)
        
        # 시뮬레이션된 이상치 탐지
        anomaly_scores = np.random.random(len(data))
        anomalies = anomaly_scores > threshold
        anomaly_indices = np.where(anomalies)[0].tolist()
        
        return {
            "status": "success",
            "model_name": model_name,
            "anomaly_detection": {
                "anomaly_count": len(anomaly_indices),
                "anomaly_rate": len(anomaly_indices) / len(data),
                "anomaly_indices": anomaly_indices,
                "anomaly_scores": anomaly_scores.tolist()
            }
        }


# MCP 서비스 인스턴스
mcp_service = MCPServiceSimulator()


def generate_sample_data(n_samples=1000, n_features=1, trend=True, seasonality=True, noise_level=0.1):
    """샘플 시계열 데이터 생성"""
    t = np.arange(n_samples)
    
    # 기본 신호
    signal = np.zeros(n_samples)
    
    # 트렌드 추가
    if trend:
        signal += 0.01 * t
    
    # 계절성 추가
    if seasonality:
        signal += 0.5 * np.sin(2 * np.pi * t / 50)
        signal += 0.3 * np.sin(2 * np.pi * t / 20)
    
    # 노이즈 추가
    noise = np.random.normal(0, noise_level, n_samples)
    signal += noise
    
    # 이상치 추가
    anomaly_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    signal[anomaly_indices] += np.random.normal(0, 2, len(anomaly_indices))
    
    if n_features > 1:
        data = np.zeros((n_samples, n_features))
        data[:, 0] = signal
        for i in range(1, n_features):
            correlation = 0.7
            data[:, i] = correlation * signal + (1 - correlation) * np.random.normal(0, 0.5, n_samples)
    else:
        data = signal.reshape(-1, 1)
    
    return data


@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/api/models/forecasting', methods=['GET'])
def get_forecasting_models():
    """예측 모델 목록 조회"""
    return jsonify({
        "models": list(mcp_service.forecasting_models.keys()),
        "available_types": ["lstm", "cnn", "multivariate_lstm", "multivariate_cnn_lstm"]
    })


@app.route('/api/models/anomaly', methods=['GET'])
def get_anomaly_models():
    """이상치 탐지 모델 목록 조회"""
    return jsonify({
        "models": list(mcp_service.anomaly_models.keys()),
        "available_types": ["prophet", "hmm", "transformer", "temporal_fusion_transformer"]
    })


@app.route('/api/models/forecasting/train', methods=['POST'])
def train_forecasting_model():
    """예측 모델 훈련"""
    data = request.json
    
    # 비동기 함수를 동기적으로 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            mcp_service.train_forecasting_model(
                model_type=data['model_type'],
                data=data['data'],
                model_name=data['model_name'],
                sequence_length=data.get('sequence_length', 30),
                prediction_length=data.get('prediction_length', 1),
                epochs=data.get('epochs', 100)
            )
        )
        
        # 실시간 업데이트 전송
        socketio.emit('model_trained', {
            'type': 'forecasting',
            'model_name': data['model_name'],
            'result': result
        })
        
        return jsonify(result)
    finally:
        loop.close()


@app.route('/api/models/anomaly/train', methods=['POST'])
def train_anomaly_model():
    """이상치 탐지 모델 훈련"""
    data = request.json
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            mcp_service.train_anomaly_model(
                model_type=data['model_type'],
                data=data['data'],
                model_name=data['model_name'],
                **data.get('model_params', {})
            )
        )
        
        socketio.emit('model_trained', {
            'type': 'anomaly',
            'model_name': data['model_name'],
            'result': result
        })
        
        return jsonify(result)
    finally:
        loop.close()


@app.route('/api/predict', methods=['POST'])
def predict():
    """예측 수행"""
    data = request.json
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            mcp_service.predict_forecasting(
                model_name=data['model_name'],
                data=data['data'],
                steps_ahead=data.get('steps_ahead', 1)
            )
        )
        
        socketio.emit('prediction_completed', {
            'model_name': data['model_name'],
            'result': result
        })
        
        return jsonify(result)
    finally:
        loop.close()


@app.route('/api/detect_anomalies', methods=['POST'])
def detect_anomalies():
    """이상치 탐지"""
    data = request.json
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            mcp_service.detect_anomalies(
                model_name=data['model_name'],
                data=data['data'],
                threshold=data.get('threshold', 0.95)
            )
        )
        
        socketio.emit('anomaly_detection_completed', {
            'model_name': data['model_name'],
            'result': result
        })
        
        return jsonify(result)
    finally:
        loop.close()


@app.route('/api/data/generate', methods=['POST'])
def generate_data():
    """샘플 데이터 생성"""
    params = request.json
    data = generate_sample_data(
        n_samples=params.get('n_samples', 1000),
        n_features=params.get('n_features', 1),
        trend=params.get('trend', True),
        seasonality=params.get('seasonality', True),
        noise_level=params.get('noise_level', 0.1)
    )
    
    return jsonify({
        "data": data.tolist(),
        "shape": data.shape,
        "generated_at": datetime.now().isoformat()
    })


@app.route('/api/analysis/coordinated', methods=['POST'])
def coordinated_analysis():
    """통합 분석 수행"""
    data = request.json
    
    # 예측 모델 훈련
    forecast_result = None
    if data.get('forecasting_model'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            forecast_result = loop.run_until_complete(
                mcp_service.train_forecasting_model(
                    model_type=data['forecasting_model'],
                    data=data['data'],
                    model_name=f"coord_{data['forecasting_model']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            )
        finally:
            loop.close()
    
    # 이상치 탐지 모델 훈련
    anomaly_result = None
    if data.get('anomaly_model'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            anomaly_result = loop.run_until_complete(
                mcp_service.train_anomaly_model(
                    model_type=data['anomaly_model'],
                    data=data['data'],
                    model_name=f"coord_{data['anomaly_model']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            )
        finally:
            loop.close()
    
    # 통합 결과
    result = {
        "status": "success",
        "analysis_type": data.get('analysis_type', 'forecast_and_detect'),
        "forecasting": forecast_result,
        "anomaly_detection": anomaly_result,
        "combined_analysis": {
            "reliability_score": 0.8,
            "anomaly_adjusted_forecast": "available" if forecast_result and anomaly_result else "not_available"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # 분석 히스토리에 추가
    analysis_history.append(result)
    
    socketio.emit('coordinated_analysis_completed', result)
    
    return jsonify(result)


@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    """분석 히스토리 조회"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        "history": analysis_history[-limit:],
        "total": len(analysis_history)
    })


@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 처리"""
    print('Client connected')
    emit('status', {'message': 'Connected to Multi-MCP System'})


@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 처리"""
    print('Client disconnected')


if __name__ == '__main__':
    print("🌟 Multi-MCP Time Series Analysis Web Service")
    print("=" * 50)
    print("Starting web server...")
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5000/api/")
    print("=" * 50)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


