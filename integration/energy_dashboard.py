"""
통합 에너지 분석 대시보드 - Flask 기반 웹 인터페이스
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
import logging

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'multi_mcp_system'))

from energy_mcp_integration import EnergyMCPIntegration
from config.settings import EnergyAnalysisConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'energy-analysis-integration-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
integration_server = None
analysis_history = []
real_time_data = []
monitoring_active = False

class EnergyDashboardService:
    """에너지 대시보드 서비스 클래스"""
    
    def __init__(self):
        self.integration_server = EnergyMCPIntegration()
        self.config = EnergyAnalysisConfig()
        self.analysis_cache = {}
        self.model_cache = {}
    
    async def enhanced_forecast(self, data, model_type="ensemble", **kwargs):
        """향상된 예측 수행"""
        try:
            # MCP 도구 호출
            result = await self.integration_server.mcp.call_tool(
                "enhanced_energy_forecast",
                data=data,
                model_type=model_type,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Enhanced forecast error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def advanced_anomaly_detection(self, data, **kwargs):
        """고급 이상치 탐지"""
        try:
            result = await self.integration_server.mcp.call_tool(
                "advanced_anomaly_detection",
                data=data,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Advanced anomaly detection error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def climate_aware_analysis(self, data, **kwargs):
        """기후 인식 분석"""
        try:
            result = await self.integration_server.mcp.call_tool(
                "climate_aware_energy_analysis",
                data=data,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Climate aware analysis error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def ensemble_forecast(self, data, **kwargs):
        """앙상블 예측"""
        try:
            result = await self.integration_server.mcp.call_tool(
                "ensemble_energy_forecast",
                data=data,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Ensemble forecast error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def real_time_monitoring(self, **kwargs):
        """실시간 모니터링"""
        try:
            result = await self.integration_server.mcp.call_tool(
                "real_time_energy_monitoring",
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Real-time monitoring error: {e}")
            return {"status": "error", "message": str(e)}

# Initialize dashboard service
dashboard_service = EnergyDashboardService()

def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def generate_sample_energy_data(n_samples=1000, include_weather=True):
    """샘플 에너지 데이터 생성"""
    # 기본 에너지 소비 패턴
    t = np.arange(n_samples)
    
    # 계절성 패턴
    seasonal = 50 * np.sin(2 * np.pi * t / (24 * 30))  # 월별 계절성
    daily = 20 * np.sin(2 * np.pi * t / 24)  # 일별 패턴
    weekly = 10 * np.sin(2 * np.pi * t / (24 * 7))  # 주별 패턴
    
    # 트렌드
    trend = 0.01 * t
    
    # 노이즈
    noise = np.random.normal(0, 5, n_samples)
    
    # 기본 소비량
    base_consumption = 100
    consumption = base_consumption + seasonal + daily + weekly + trend + noise
    
    # 이상치 추가
    anomaly_indices = np.random.choice(n_samples, size=int(0.02 * n_samples), replace=False)
    consumption[anomaly_indices] += np.random.normal(0, 20, len(anomaly_indices))
    
    # 날씨 데이터 (선택사항)
    weather_data = {}
    if include_weather:
        temperature = 20 + 10 * np.sin(2 * np.pi * t / (24 * 365)) + np.random.normal(0, 3, n_samples)
        humidity = 60 + 20 * np.sin(2 * np.pi * t / (24 * 365)) + np.random.normal(0, 5, n_samples)
        weather_data = {
            'temperature': temperature.tolist(),
            'humidity': humidity.tolist()
        }
    
    # 데이터프레임 생성
    timestamps = pd.date_range(start='2024-01-01', periods=n_samples, freq='H')
    df = pd.DataFrame({
        'timestamp': timestamps,
        'consumption': consumption,
        **weather_data
    })
    
    return df

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('energy_dashboard.html')

@app.route('/api/energy/forecast', methods=['POST'])
def energy_forecast():
    """에너지 예측 API"""
    try:
        data = request.json
        
        # 샘플 데이터 생성 또는 사용자 데이터 사용
        if data.get('use_sample_data', True):
            df = generate_sample_energy_data(
                n_samples=data.get('n_samples', 1000),
                include_weather=data.get('include_weather', True)
            )
            data_str = df.to_csv(index=False)
        else:
            data_str = data.get('data', '')
        
        # 예측 수행
        result = run_async(dashboard_service.enhanced_forecast(
            data=data_str,
            model_type=data.get('model_type', 'ensemble'),
            prediction_hours=data.get('prediction_hours', 24),
            include_weather=data.get('include_weather', True),
            include_anomaly_detection=data.get('include_anomaly_detection', True),
            latitude=data.get('latitude', 37.5665),
            longitude=data.get('longitude', 126.9780)
        ))
        
        # 실시간 업데이트 전송
        socketio.emit('forecast_completed', {
            'model_type': data.get('model_type', 'ensemble'),
            'result': result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Energy forecast API error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/anomaly', methods=['POST'])
def energy_anomaly_detection():
    """에너지 이상치 탐지 API"""
    try:
        data = request.json
        
        # 샘플 데이터 생성 또는 사용자 데이터 사용
        if data.get('use_sample_data', True):
            df = generate_sample_energy_data(
                n_samples=data.get('n_samples', 1000),
                include_weather=data.get('include_weather', True)
            )
            data_str = df.to_csv(index=False)
        else:
            data_str = data.get('data', '')
        
        # 이상치 탐지 수행
        result = run_async(dashboard_service.advanced_anomaly_detection(
            data=data_str,
            detection_methods=data.get('detection_methods', ['prophet', 'hmm', 'isolation_forest']),
            sensitivity=data.get('sensitivity', 0.95),
            include_weather_correlation=data.get('include_weather_correlation', True),
            latitude=data.get('latitude', 37.5665),
            longitude=data.get('longitude', 126.9780)
        ))
        
        # 실시간 업데이트 전송
        socketio.emit('anomaly_detection_completed', {
            'detection_methods': data.get('detection_methods', ['prophet', 'hmm', 'isolation_forest']),
            'result': result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Energy anomaly detection API error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/climate-analysis', methods=['POST'])
def climate_aware_analysis():
    """기후 인식 에너지 분석 API"""
    try:
        data = request.json
        
        # 샘플 데이터 생성 또는 사용자 데이터 사용
        if data.get('use_sample_data', True):
            df = generate_sample_energy_data(
                n_samples=data.get('n_samples', 1000),
                include_weather=data.get('include_weather', True)
            )
            data_str = df.to_csv(index=False)
        else:
            data_str = data.get('data', '')
        
        # 기후 인식 분석 수행
        result = run_async(dashboard_service.climate_aware_analysis(
            data=data_str,
            analysis_type=data.get('analysis_type', 'comprehensive'),
            include_precipitation=data.get('include_precipitation', True),
            include_temperature=data.get('include_temperature', True),
            latitude=data.get('latitude', 37.5665),
            longitude=data.get('longitude', 126.9780),
            prediction_days=data.get('prediction_days', 7)
        ))
        
        # 실시간 업데이트 전송
        socketio.emit('climate_analysis_completed', {
            'analysis_type': data.get('analysis_type', 'comprehensive'),
            'result': result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Climate aware analysis API error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/ensemble', methods=['POST'])
def ensemble_forecast():
    """앙상블 예측 API"""
    try:
        data = request.json
        
        # 샘플 데이터 생성 또는 사용자 데이터 사용
        if data.get('use_sample_data', True):
            df = generate_sample_energy_data(
                n_samples=data.get('n_samples', 1000),
                include_weather=data.get('include_weather', True)
            )
            data_str = df.to_csv(index=False)
        else:
            data_str = data.get('data', '')
        
        # 앙상블 예측 수행
        result = run_async(dashboard_service.ensemble_forecast(
            data=data_str,
            models=data.get('models', ['lstm', 'cnn', 'prophet', 'arima']),
            weights=data.get('weights'),
            prediction_hours=data.get('prediction_hours', 24),
            include_uncertainty=data.get('include_uncertainty', True),
            latitude=data.get('latitude', 37.5665),
            longitude=data.get('longitude', 126.9780)
        ))
        
        # 실시간 업데이트 전송
        socketio.emit('ensemble_forecast_completed', {
            'models': data.get('models', ['lstm', 'cnn', 'prophet', 'arima']),
            'result': result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ensemble forecast API error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/monitoring', methods=['POST'])
def real_time_monitoring():
    """실시간 모니터링 API"""
    try:
        data = request.json
        
        # 실시간 모니터링 수행
        result = run_async(dashboard_service.real_time_monitoring(
            data_source=data.get('data_source', 'file'),
            data_path=data.get('data_path'),
            monitoring_interval=data.get('monitoring_interval', 300),
            alert_threshold=data.get('alert_threshold', 2.0),
            latitude=data.get('latitude', 37.5665),
            longitude=data.get('longitude', 126.9780)
        ))
        
        # 실시간 업데이트 전송
        socketio.emit('monitoring_update', {
            'result': result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Real-time monitoring API error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/sample-data', methods=['POST'])
def generate_sample_data():
    """샘플 데이터 생성 API"""
    try:
        data = request.json
        
        df = generate_sample_energy_data(
            n_samples=data.get('n_samples', 1000),
            include_weather=data.get('include_weather', True)
        )
        
        return jsonify({
            "status": "success",
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "shape": df.shape,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Sample data generation error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/energy/analysis-history', methods=['GET'])
def get_analysis_history():
    """분석 히스토리 조회 API"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        "history": analysis_history[-limit:],
        "total": len(analysis_history)
    })

@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 처리"""
    logger.info('Client connected to Energy Dashboard')
    emit('status', {'message': 'Connected to Energy Analysis Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 처리"""
    logger.info('Client disconnected from Energy Dashboard')

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """실시간 모니터링 시작"""
    global monitoring_active
    monitoring_active = True
    
    def monitoring_loop():
        while monitoring_active:
            try:
                result = run_async(dashboard_service.real_time_monitoring(
                    data_source=data.get('data_source', 'file'),
                    data_path=data.get('data_path'),
                    monitoring_interval=data.get('monitoring_interval', 300),
                    alert_threshold=data.get('alert_threshold', 2.0),
                    latitude=data.get('latitude', 37.5665),
                    longitude=data.get('longitude', 126.9780)
                ))
                
                socketio.emit('monitoring_data', result)
                analysis_history.append({
                    'type': 'monitoring',
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            
            time.sleep(data.get('monitoring_interval', 300))
    
    # 백그라운드에서 모니터링 시작
    thread = threading.Thread(target=monitoring_loop)
    thread.daemon = True
    thread.start()

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """실시간 모니터링 중지"""
    global monitoring_active
    monitoring_active = False
    emit('monitoring_stopped', {'message': 'Real-time monitoring stopped'})

if __name__ == '__main__':
    print("🔋 Energy Analysis Integration Dashboard")
    print("=" * 50)
    print("Starting integrated energy analysis dashboard...")
    print("Dashboard: http://localhost:5002")
    print("API: http://localhost:5002/api/energy/")
    print("=" * 50)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5002)


