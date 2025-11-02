"""
REST API 서비스 - Multi-MCP Time Series Analysis System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime
import os
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from utils.model_utils import ModelEvaluator, ModelManager, ModelSelector

app = Flask(__name__)
CORS(app)

# Global variables
model_manager = ModelManager("api_models")
model_evaluator = ModelEvaluator()
active_models = {
    'forecasting': {},
    'anomaly': {}
}

# API 버전
API_VERSION = "v1"


class APIService:
    """API 서비스 클래스"""
    
    def __init__(self):
        self.forecasting_models = {}
        self.anomaly_models = {}
        self.analysis_history = []
    
    async def train_forecasting_model(self, model_type: str, data: np.ndarray, 
                                    model_name: str, **kwargs) -> Dict[str, Any]:
        """예측 모델 훈련"""
        try:
            # 데이터 준비
            sequence_length = kwargs.get('sequence_length', 30)
            prediction_length = kwargs.get('prediction_length', 1)
            
            if model_type in ['multivariate_lstm', 'multivariate_cnn_lstm']:
                prepared_data = prepare_multivariate_forecasting_data(
                    data, sequence_length, prediction_length
                )
            else:
                prepared_data = prepare_forecasting_data(
                    data, sequence_length, prediction_length
                )
            
            # 시뮬레이션된 훈련 (실제로는 MCP 서버와 통신)
            if model_type == "lstm":
                metrics = {"mse": 0.05, "rmse": 0.22, "mae": 0.18, "r2": 0.88}
            elif model_type == "cnn":
                metrics = {"mse": 0.08, "rmse": 0.28, "mae": 0.22, "r2": 0.82}
            elif model_type == "multivariate_lstm":
                metrics = {"mse": 0.06, "rmse": 0.24, "mae": 0.20, "r2": 0.85}
            else:
                metrics = {"mse": 0.07, "rmse": 0.26, "mae": 0.21, "r2": 0.83}
            
            # 모델 저장
            model_info = {
                "model_type": model_type,
                "model_name": model_name,
                "metrics": metrics,
                "data_shape": data.shape,
                "trained_at": datetime.now().isoformat(),
                "parameters": kwargs
            }
            
            self.forecasting_models[model_name] = model_info
            active_models['forecasting'][model_name] = model_info
            
            return {
                "status": "success",
                "model_name": model_name,
                "model_type": model_type,
                "metrics": metrics,
                "trained_at": model_info["trained_at"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def train_anomaly_model(self, model_type: str, data: np.ndarray, 
                                model_name: str, **kwargs) -> Dict[str, Any]:
        """이상치 탐지 모델 훈련"""
        try:
            # 시뮬레이션된 이상치 탐지 훈련
            anomaly_count = np.random.randint(10, 50)
            total_points = len(data)
            anomaly_rate = anomaly_count / total_points
            
            model_info = {
                "model_type": model_type,
                "model_name": model_name,
                "anomaly_count": anomaly_count,
                "anomaly_rate": anomaly_rate,
                "data_shape": data.shape,
                "trained_at": datetime.now().isoformat(),
                "parameters": kwargs
            }
            
            self.anomaly_models[model_name] = model_info
            active_models['anomaly'][model_name] = model_info
            
            return {
                "status": "success",
                "model_name": model_name,
                "model_type": model_type,
                "anomaly_detection": {
                    "anomaly_count": anomaly_count,
                    "anomaly_rate": anomaly_rate
                },
                "trained_at": model_info["trained_at"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def predict_forecasting(self, model_name: str, data: np.ndarray, 
                                steps_ahead: int = 1) -> Dict[str, Any]:
        """예측 수행"""
        if model_name not in self.forecasting_models:
            return {"status": "error", "message": "Model not found"}
        
        try:
            # 시뮬레이션된 예측
            predictions = np.random.random(steps_ahead).tolist()
            
            return {
                "status": "success",
                "model_name": model_name,
                "predictions": predictions,
                "steps_ahead": steps_ahead,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def detect_anomalies(self, model_name: str, data: np.ndarray, 
                             threshold: float = 0.95) -> Dict[str, Any]:
        """이상치 탐지"""
        if model_name not in self.anomaly_models:
            return {"status": "error", "message": "Model not found"}
        
        try:
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
                },
                "detected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def coordinated_analysis(self, data: np.ndarray, analysis_type: str,
                                 forecasting_model: str = None, anomaly_model: str = None,
                                 **kwargs) -> Dict[str, Any]:
        """통합 분석"""
        try:
            results = {
                "status": "success",
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "forecasting": None,
                "anomaly_detection": None,
                "combined_analysis": {}
            }
            
            # 예측 분석
            if forecasting_model and analysis_type in ['forecast_and_detect', 'anomaly_aware_forecast']:
                forecast_result = await self.predict_forecasting(forecasting_model, data)
                results["forecasting"] = forecast_result
            
            # 이상치 탐지
            if anomaly_model and analysis_type in ['forecast_and_detect', 'anomaly_aware_forecast']:
                anomaly_result = await self.detect_anomalies(anomaly_model, data)
                results["anomaly_detection"] = anomaly_result
            
            # 통합 분석 결과
            if results["forecasting"] and results["anomaly_detection"]:
                results["combined_analysis"] = {
                    "reliability_score": 0.8,
                    "anomaly_adjusted_forecast": "available",
                    "recommendations": [
                        "이상치가 감지된 구간에서는 예측 신뢰도를 낮게 평가하세요.",
                        "정기적인 모델 재훈련을 권장합니다."
                    ]
                }
            
            # 히스토리에 추가
            self.analysis_history.append(results)
            
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# API 서비스 인스턴스
api_service = APIService()


def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# API 엔드포인트들

@app.route(f'/api/{API_VERSION}/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": API_VERSION,
        "active_models": {
            "forecasting": len(active_models['forecasting']),
            "anomaly": len(active_models['anomaly'])
        }
    })


@app.route(f'/api/{API_VERSION}/models/forecasting', methods=['GET'])
def list_forecasting_models():
    """예측 모델 목록 조회"""
    return jsonify({
        "models": list(api_service.forecasting_models.keys()),
        "available_types": ["lstm", "cnn", "multivariate_lstm", "multivariate_cnn_lstm"],
        "count": len(api_service.forecasting_models)
    })


@app.route(f'/api/{API_VERSION}/models/anomaly', methods=['GET'])
def list_anomaly_models():
    """이상치 탐지 모델 목록 조회"""
    return jsonify({
        "models": list(api_service.anomaly_models.keys()),
        "available_types": ["prophet", "hmm", "transformer", "temporal_fusion_transformer"],
        "count": len(api_service.anomaly_models)
    })


@app.route(f'/api/{API_VERSION}/models/forecasting/train', methods=['POST'])
def train_forecasting_model():
    """예측 모델 훈련"""
    try:
        data = request.json
        
        # 데이터 파싱
        if isinstance(data['data'], str):
            data_array = np.array(json.loads(data['data']))
        else:
            data_array = np.array(data['data'])
        
        # 모델 훈련
        result = run_async(api_service.train_forecasting_model(
            model_type=data['model_type'],
            data=data_array,
            model_name=data['model_name'],
            sequence_length=data.get('sequence_length', 30),
            prediction_length=data.get('prediction_length', 1),
            epochs=data.get('epochs', 100),
            batch_size=data.get('batch_size', 32)
        ))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/models/anomaly/train', methods=['POST'])
def train_anomaly_model():
    """이상치 탐지 모델 훈련"""
    try:
        data = request.json
        
        # 데이터 파싱
        if isinstance(data['data'], str):
            data_array = np.array(json.loads(data['data']))
        else:
            data_array = np.array(data['data'])
        
        # 모델 훈련
        result = run_async(api_service.train_anomaly_model(
            model_type=data['model_type'],
            data=data_array,
            model_name=data['model_name'],
            **data.get('model_params', {})
        ))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/predict', methods=['POST'])
def predict():
    """예측 수행"""
    try:
        data = request.json
        
        # 데이터 파싱
        if isinstance(data['data'], str):
            data_array = np.array(json.loads(data['data']))
        else:
            data_array = np.array(data['data'])
        
        # 예측 수행
        result = run_async(api_service.predict_forecasting(
            model_name=data['model_name'],
            data=data_array,
            steps_ahead=data.get('steps_ahead', 1)
        ))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/detect_anomalies', methods=['POST'])
def detect_anomalies():
    """이상치 탐지"""
    try:
        data = request.json
        
        # 데이터 파싱
        if isinstance(data['data'], str):
            data_array = np.array(json.loads(data['data']))
        else:
            data_array = np.array(data['data'])
        
        # 이상치 탐지
        result = run_async(api_service.detect_anomalies(
            model_name=data['model_name'],
            data=data_array,
            threshold=data.get('threshold', 0.95)
        ))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/analysis/coordinated', methods=['POST'])
def coordinated_analysis():
    """통합 분석"""
    try:
        data = request.json
        
        # 데이터 파싱
        if isinstance(data['data'], str):
            data_array = np.array(json.loads(data['data']))
        else:
            data_array = np.array(data['data'])
        
        # 통합 분석 수행
        result = run_async(api_service.coordinated_analysis(
            data=data_array,
            analysis_type=data.get('analysis_type', 'forecast_and_detect'),
            forecasting_model=data.get('forecasting_model'),
            anomaly_model=data.get('anomaly_model'),
            **data.get('parameters', {})
        ))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/data/generate', methods=['POST'])
def generate_sample_data():
    """샘플 데이터 생성"""
    try:
        params = request.json or {}
        
        # 샘플 데이터 생성
        n_samples = params.get('n_samples', 1000)
        n_features = params.get('n_features', 1)
        trend = params.get('trend', True)
        seasonality = params.get('seasonality', True)
        noise_level = params.get('noise_level', 0.1)
        
        # 시계열 데이터 생성
        t = np.arange(n_samples)
        signal = np.zeros(n_samples)
        
        if trend:
            signal += 0.01 * t
        
        if seasonality:
            signal += 0.5 * np.sin(2 * np.pi * t / 50)
            signal += 0.3 * np.sin(2 * np.pi * t / 20)
        
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
        
        return jsonify({
            "data": data.tolist(),
            "shape": data.shape,
            "parameters": {
                "n_samples": n_samples,
                "n_features": n_features,
                "trend": trend,
                "seasonality": seasonality,
                "noise_level": noise_level
            },
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route(f'/api/{API_VERSION}/analysis/history', methods=['GET'])
def get_analysis_history():
    """분석 히스토리 조회"""
    limit = request.args.get('limit', 10, type=int)
    
    return jsonify({
        "history": api_service.analysis_history[-limit:],
        "total": len(api_service.analysis_history),
        "limit": limit
    })


@app.route(f'/api/{API_VERSION}/models/forecasting/<model_name>', methods=['GET'])
def get_forecasting_model(model_name):
    """특정 예측 모델 정보 조회"""
    if model_name not in api_service.forecasting_models:
        return jsonify({
            "status": "error",
            "message": "Model not found"
        }), 404
    
    return jsonify(api_service.forecasting_models[model_name])


@app.route(f'/api/{API_VERSION}/models/anomaly/<model_name>', methods=['GET'])
def get_anomaly_model(model_name):
    """특정 이상치 탐지 모델 정보 조회"""
    if model_name not in api_service.anomaly_models:
        return jsonify({
            "status": "error",
            "message": "Model not found"
        }), 404
    
    return jsonify(api_service.anomaly_models[model_name])


@app.route(f'/api/{API_VERSION}/models/forecasting/<model_name>', methods=['DELETE'])
def delete_forecasting_model(model_name):
    """예측 모델 삭제"""
    if model_name not in api_service.forecasting_models:
        return jsonify({
            "status": "error",
            "message": "Model not found"
        }), 404
    
    del api_service.forecasting_models[model_name]
    if model_name in active_models['forecasting']:
        del active_models['forecasting'][model_name]
    
    return jsonify({
        "status": "success",
        "message": f"Model {model_name} deleted"
    })


@app.route(f'/api/{API_VERSION}/models/anomaly/<model_name>', methods=['DELETE'])
def delete_anomaly_model(model_name):
    """이상치 탐지 모델 삭제"""
    if model_name not in api_service.anomaly_models:
        return jsonify({
            "status": "error",
            "message": "Model not found"
        }), 404
    
    del api_service.anomaly_models[model_name]
    if model_name in active_models['anomaly']:
        del active_models['anomaly'][model_name]
    
    return jsonify({
        "status": "success",
        "message": f"Model {model_name} deleted"
    })


if __name__ == '__main__':
    print("🚀 Multi-MCP Time Series Analysis REST API")
    print("=" * 50)
    print("API Server: http://localhost:5001")
    print("API Documentation: http://localhost:5001/api/v1/health")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)


