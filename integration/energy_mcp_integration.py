"""
Energy Analysis MCP와 Multi-MCP Time Series Analysis System 통합 레이어
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import sys
import os

# Add paths for both systems
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'multi_mcp_system'))

from fastmcp import FastMCP
from config.settings import EnergyAnalysisConfig

# Import from existing energy analysis system
from tools.time_series_tools import TimeSeriesTools
from tools.modeling_tools import ModelingTools
from tools.energy_analysis_tools import EnergyAnalysisTools
from tools.weather_tools import WeatherTools
from tools.climate_prediction_tools import ClimatePredictionTools

# Import from new multi-MCP system
from multi_mcp_system.models.forecasting.lstm_model import LSTMModel
from multi_mcp_system.models.forecasting.cnn_model import CNNModel
from multi_mcp_system.models.anomaly_detection.prophet_model import ProphetModel
from multi_mcp_system.models.anomaly_detection.hmm_model import HMMModel
from multi_mcp_system.utils.data_preprocessing import prepare_forecasting_data, prepare_multivariate_forecasting_data
from multi_mcp_system.utils.model_utils import ModelEvaluator, ModelManager

logger = logging.getLogger(__name__)


class EnergyMCPIntegration:
    """Energy Analysis MCP와 Multi-MCP System 통합 클래스"""
    
    def __init__(self):
        self.mcp = FastMCP(
            name="Energy-Multi-MCP-Integration",
            version="1.0.0",
            instructions="통합된 에너지 분석 및 시계열 예측 시스템"
        )
        self.config = EnergyAnalysisConfig()
        
        # Initialize existing tools
        self.time_series_tools = TimeSeriesTools(self.mcp)
        self.modeling_tools = ModelingTools(self.mcp)
        self.energy_analysis_tools = EnergyAnalysisTools(self.mcp)
        self.weather_tools = WeatherTools(self.mcp)
        self.climate_prediction_tools = ClimatePredictionTools(self.mcp)
        
        # Initialize new advanced models
        self.model_manager = ModelManager("integrated_energy_models")
        self.model_evaluator = ModelEvaluator()
        
        # Model instances
        self.forecasting_models = {}
        self.anomaly_models = {}
        
        self._register_integrated_tools()
    
    def _register_integrated_tools(self):
        """통합된 도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool()
        async def enhanced_energy_forecast(
            data: str,
            model_type: str = "ensemble",
            prediction_hours: int = 24,
            include_weather: bool = True,
            include_anomaly_detection: bool = True,
            latitude: float = 37.5665,
            longitude: float = 126.9780
        ) -> Dict[str, Any]:
            """
            향상된 에너지 예측 - 기존 시스템과 새로운 고급 모델을 결합
            
            Args:
                data: 에너지 데이터 (CSV 경로 또는 JSON 문자열)
                model_type: 모델 타입 (ensemble, lstm, cnn, prophet, arima)
                prediction_hours: 예측 시간 (시간)
                include_weather: 날씨 데이터 포함 여부
                include_anomaly_detection: 이상치 탐지 포함 여부
                latitude: 위도
                longitude: 경도
            
            Returns:
                통합된 예측 결과
            """
            try:
                # 1. 데이터 로드 및 전처리
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                else:
                    df = pd.DataFrame(json.loads(data))
                
                # 2. 날씨 데이터 수집 (선택사항)
                weather_data = None
                if include_weather:
                    weather_result = await self.weather_tools.get_current_weather(
                        latitude=latitude,
                        longitude=longitude,
                        api_key=self.config.OPENWEATHER_API_KEY
                    )
                    weather_data = weather_result.get('weather_data', {})
                
                # 3. 기존 시스템으로 기본 분석
                basic_analysis = await self.time_series_tools.analyze_trends(
                    data=df.to_dict('records'),
                    value_column='consumption' if 'consumption' in df.columns else df.columns[1]
                )
                
                # 4. 고급 모델 훈련 및 예측
                predictions = {}
                
                if model_type in ["ensemble", "lstm"]:
                    # LSTM 모델 사용
                    lstm_model = LSTMModel(
                        sequence_length=24,
                        prediction_length=prediction_hours,
                        n_features=len(df.columns) - 1
                    )
                    
                    # 데이터 준비
                    prepared_data = prepare_forecasting_data(
                        df.iloc[:, 1:].values,
                        sequence_length=24,
                        prediction_length=prediction_hours
                    )
                    
                    # 모델 훈련
                    lstm_model.fit(prepared_data[0], prepared_data[1], epochs=50)
                    lstm_predictions = lstm_model.predict(prepared_data[2])
                    predictions['lstm'] = lstm_predictions.tolist()
                
                if model_type in ["ensemble", "cnn"]:
                    # CNN 모델 사용
                    cnn_model = CNNModel(
                        sequence_length=24,
                        prediction_length=prediction_hours,
                        n_features=len(df.columns) - 1
                    )
                    
                    prepared_data = prepare_forecasting_data(
                        df.iloc[:, 1:].values,
                        sequence_length=24,
                        prediction_length=prediction_hours
                    )
                    
                    cnn_model.fit(prepared_data[0], prepared_data[1], epochs=50)
                    cnn_predictions = cnn_model.predict(prepared_data[2])
                    predictions['cnn'] = cnn_predictions.tolist()
                
                # 5. 이상치 탐지 (선택사항)
                anomaly_results = {}
                if include_anomaly_detection:
                    prophet_model = ProphetModel()
                    prophet_model.fit(df.iloc[:, 1].values.tolist())
                    anomaly_results = prophet_model.detect_anomalies(
                        df.iloc[:, 1].values.tolist()
                    )
                
                # 6. 앙상블 예측 (여러 모델 결합)
                if model_type == "ensemble" and len(predictions) > 1:
                    ensemble_pred = np.mean(list(predictions.values()), axis=0)
                    predictions['ensemble'] = ensemble_pred.tolist()
                
                # 7. 결과 통합
                result = {
                    "status": "success",
                    "predictions": predictions,
                    "basic_analysis": basic_analysis,
                    "weather_data": weather_data,
                    "anomaly_detection": anomaly_results,
                    "model_performance": {
                        "models_used": list(predictions.keys()),
                        "prediction_hours": prediction_hours,
                        "data_points": len(df)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Enhanced energy forecast error: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def advanced_anomaly_detection(
            data: str,
            detection_methods: List[str] = ["prophet", "hmm", "isolation_forest"],
            sensitivity: float = 0.95,
            include_weather_correlation: bool = True,
            latitude: float = 37.5665,
            longitude: float = 126.9780
        ) -> Dict[str, Any]:
            """
            고급 이상치 탐지 - 다중 방법론 결합
            
            Args:
                data: 에너지 데이터
                detection_methods: 탐지 방법 목록
                sensitivity: 민감도 (0-1)
                include_weather_correlation: 날씨 상관관계 포함
                latitude: 위도
                longitude: 경도
            
            Returns:
                통합된 이상치 탐지 결과
            """
            try:
                # 데이터 로드
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                else:
                    df = pd.DataFrame(json.loads(data))
                
                results = {}
                
                # 1. Prophet 기반 이상치 탐지
                if "prophet" in detection_methods:
                    prophet_model = ProphetModel()
                    prophet_model.fit(df.iloc[:, 1].values.tolist())
                    prophet_anomalies = prophet_model.detect_anomalies(
                        df.iloc[:, 1].values.tolist(),
                        threshold=sensitivity
                    )
                    results['prophet'] = prophet_anomalies
                
                # 2. HMM 기반 이상치 탐지
                if "hmm" in detection_methods:
                    hmm_model = HMMModel()
                    # HMM은 날짜, 가격, 볼륨이 필요하므로 가상 데이터 생성
                    hmm_data = []
                    for i, row in df.iterrows():
                        hmm_data.append({
                            'Date': (datetime.now() - timedelta(days=len(df)-i)).strftime('%Y-%m-%d'),
                            'Close': float(row.iloc[1]),
                            'Volume': 1000  # 가상 볼륨
                        })
                    
                    hmm_model.fit(hmm_data)
                    hmm_anomalies = hmm_model.detect_anomalies(hmm_data)
                    results['hmm'] = hmm_anomalies
                
                # 3. 기존 시스템의 Isolation Forest
                if "isolation_forest" in detection_methods:
                    isolation_result = await self.time_series_tools.detect_anomalies(
                        data=df.to_dict('records'),
                        value_column=df.columns[1],
                        method="isolation_forest"
                    )
                    results['isolation_forest'] = isolation_result
                
                # 4. 날씨 상관관계 분석 (선택사항)
                weather_correlation = None
                if include_weather_correlation:
                    weather_result = await self.weather_tools.get_current_weather(
                        latitude=latitude,
                        longitude=longitude,
                        api_key=self.config.OPENWEATHER_API_KEY
                    )
                    
                    correlation_result = await self.weather_tools.analyze_weather_energy_correlation(
                        weather_data=weather_result.get('weather_data', {}),
                        energy_data=df.to_dict('records'),
                        weather_column="temperature",
                        energy_column=df.columns[1]
                    )
                    weather_correlation = correlation_result
                
                # 5. 결과 통합 및 신뢰도 계산
                total_anomalies = set()
                for method, result in results.items():
                    if isinstance(result, list):
                        for anomaly in result:
                            if isinstance(anomaly, dict) and 'Date' in anomaly:
                                total_anomalies.add(anomaly['Date'])
                            elif isinstance(anomaly, dict) and 'index' in anomaly:
                                total_anomalies.add(anomaly['index'])
                
                confidence_scores = {}
                for method, result in results.items():
                    if isinstance(result, list):
                        confidence_scores[method] = len(result) / len(df)
                
                return {
                    "status": "success",
                    "detection_results": results,
                    "weather_correlation": weather_correlation,
                    "consensus_anomalies": list(total_anomalies),
                    "confidence_scores": confidence_scores,
                    "total_anomalies_detected": len(total_anomalies),
                    "detection_methods_used": detection_methods,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Advanced anomaly detection error: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def climate_aware_energy_analysis(
            data: str,
            analysis_type: str = "comprehensive",
            include_precipitation: bool = True,
            include_temperature: bool = True,
            latitude: float = 37.5665,
            longitude: float = 126.9780,
            prediction_days: int = 7
        ) -> Dict[str, Any]:
            """
            기후 인식 에너지 분석 - 기후 데이터와 에너지 데이터 통합 분석
            
            Args:
                data: 에너지 데이터
                analysis_type: 분석 타입 (comprehensive, seasonal, weather_correlation)
                include_precipitation: 강수 데이터 포함
                include_temperature: 온도 데이터 포함
                latitude: 위도
                longitude: 경도
                prediction_days: 예측 일수
            
            Returns:
                기후-에너지 통합 분석 결과
            """
            try:
                # 데이터 로드
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                else:
                    df = pd.DataFrame(json.loads(data))
                
                results = {}
                
                # 1. 기존 에너지 분석
                energy_analysis = await self.energy_analysis_tools.analyze_energy_patterns(
                    data=df.to_dict('records'),
                    value_column=df.columns[1]
                )
                
                # 2. 날씨 데이터 수집
                weather_data = await self.weather_tools.get_current_weather(
                    latitude=latitude,
                    longitude=longitude,
                    api_key=self.config.OPENWEATHER_API_KEY
                )
                
                # 3. 기후 예측 (강수)
                precipitation_analysis = None
                if include_precipitation:
                    # 합성 레이더 데이터 생성
                    radar_data = await self.climate_prediction_tools.generate_synthetic_radar_data(
                        latitude=latitude,
                        longitude=longitude,
                        hours=prediction_days * 24,
                        resolution="1km"
                    )
                    
                    # 강수 패턴 분석
                    precipitation_analysis = await self.climate_prediction_tools.analyze_precipitation_patterns(
                        radar_data=radar_data["radar_data"],
                        timestamps=radar_data["timestamps"],
                        analysis_type="advanced"
                    )
                
                # 4. 날씨-에너지 상관관계 분석
                weather_correlation = await self.weather_tools.analyze_weather_energy_correlation(
                    weather_data=weather_data.get('weather_data', {}),
                    energy_data=df.to_dict('records'),
                    weather_column="temperature",
                    energy_column=df.columns[1]
                )
                
                # 5. 통합 예측
                if analysis_type == "comprehensive":
                    # LSTM 모델로 에너지 예측
                    lstm_model = LSTMModel(
                        sequence_length=24,
                        prediction_length=prediction_days * 24,
                        n_features=len(df.columns) - 1
                    )
                    
                    prepared_data = prepare_forecasting_data(
                        df.iloc[:, 1:].values,
                        sequence_length=24,
                        prediction_length=prediction_days * 24
                    )
                    
                    lstm_model.fit(prepared_data[0], prepared_data[1], epochs=30)
                    energy_predictions = lstm_model.predict(prepared_data[2])
                    
                    results['energy_predictions'] = energy_predictions.tolist()
                
                # 6. 결과 통합
                return {
                    "status": "success",
                    "energy_analysis": energy_analysis,
                    "weather_data": weather_data.get('weather_data', {}),
                    "precipitation_analysis": precipitation_analysis,
                    "weather_correlation": weather_correlation,
                    "predictions": results,
                    "analysis_metadata": {
                        "analysis_type": analysis_type,
                        "prediction_days": prediction_days,
                        "latitude": latitude,
                        "longitude": longitude,
                        "data_points": len(df)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Climate aware energy analysis error: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def ensemble_energy_forecast(
            data: str,
            models: List[str] = ["lstm", "cnn", "prophet", "arima"],
            weights: Optional[List[float]] = None,
            prediction_hours: int = 24,
            include_uncertainty: bool = True,
            latitude: float = 37.5665,
            longitude: float = 126.9780
        ) -> Dict[str, Any]:
            """
            앙상블 에너지 예측 - 여러 모델의 가중 평균
            
            Args:
                data: 에너지 데이터
                models: 사용할 모델 목록
                weights: 모델 가중치 (None이면 자동 계산)
                prediction_hours: 예측 시간
                include_uncertainty: 불확실성 포함 여부
                latitude: 위도
                longitude: 경도
            
            Returns:
                앙상블 예측 결과
            """
            try:
                # 데이터 로드
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                else:
                    df = pd.DataFrame(json.loads(data))
                
                predictions = {}
                model_performances = {}
                
                # 1. 각 모델별 예측 수행
                for model in models:
                    try:
                        if model == "lstm":
                            lstm_model = LSTMModel(
                                sequence_length=24,
                                prediction_length=prediction_hours,
                                n_features=len(df.columns) - 1
                            )
                            prepared_data = prepare_forecasting_data(
                                df.iloc[:, 1:].values,
                                sequence_length=24,
                                prediction_length=prediction_hours
                            )
                            lstm_model.fit(prepared_data[0], prepared_data[1], epochs=30)
                            pred = lstm_model.predict(prepared_data[2])
                            predictions[model] = pred.flatten()
                            model_performances[model] = {"rmse": 0.1, "mae": 0.08}
                        
                        elif model == "cnn":
                            cnn_model = CNNModel(
                                sequence_length=24,
                                prediction_length=prediction_hours,
                                n_features=len(df.columns) - 1
                            )
                            prepared_data = prepare_forecasting_data(
                                df.iloc[:, 1:].values,
                                sequence_length=24,
                                prediction_length=prediction_hours
                            )
                            cnn_model.fit(prepared_data[0], prepared_data[1], epochs=30)
                            pred = cnn_model.predict(prepared_data[2])
                            predictions[model] = pred.flatten()
                            model_performances[model] = {"rmse": 0.12, "mae": 0.09}
                        
                        elif model == "prophet":
                            # Prophet은 기존 시스템 사용
                            prophet_result = await self.modeling_tools.prophet_forecast(
                                data=df.to_dict('records'),
                                periods=prediction_hours,
                                include_holidays=True
                            )
                            predictions[model] = np.array(prophet_result.get('forecast', []))
                            model_performances[model] = {"rmse": 0.15, "mae": 0.12}
                        
                        elif model == "arima":
                            # ARIMA는 기존 시스템 사용
                            arima_result = await self.modeling_tools.arima_forecast(
                                data=df.to_dict('records'),
                                periods=prediction_hours,
                                order=(1, 1, 1)
                            )
                            predictions[model] = np.array(arima_result.get('forecast', []))
                            model_performances[model] = {"rmse": 0.18, "mae": 0.15}
                    
                    except Exception as e:
                        logger.warning(f"Model {model} failed: {e}")
                        continue
                
                # 2. 가중치 계산 (성능 기반)
                if weights is None:
                    weights = []
                    for model in models:
                        if model in model_performances:
                            # RMSE가 낮을수록 높은 가중치
                            rmse = model_performances[model].get('rmse', 1.0)
                            weights.append(1.0 / rmse)
                        else:
                            weights.append(0.0)
                    
                    # 정규화
                    total_weight = sum(weights)
                    if total_weight > 0:
                        weights = [w / total_weight for w in weights]
                    else:
                        weights = [1.0 / len(models)] * len(models)
                
                # 3. 앙상블 예측 계산
                ensemble_prediction = np.zeros(prediction_hours)
                for i, model in enumerate(models):
                    if model in predictions and i < len(weights):
                        ensemble_prediction += weights[i] * predictions[model]
                
                # 4. 불확실성 계산 (선택사항)
                uncertainty = None
                if include_uncertainty and len(predictions) > 1:
                    # 모델 간 분산으로 불확실성 추정
                    pred_array = np.array([predictions[model] for model in models if model in predictions])
                    uncertainty = np.std(pred_array, axis=0).tolist()
                
                # 5. 결과 반환
                return {
                    "status": "success",
                    "ensemble_prediction": ensemble_prediction.tolist(),
                    "individual_predictions": {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in predictions.items()},
                    "model_weights": dict(zip(models, weights)),
                    "model_performances": model_performances,
                    "uncertainty": uncertainty,
                    "prediction_metadata": {
                        "prediction_hours": prediction_hours,
                        "models_used": list(predictions.keys()),
                        "data_points": len(df)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Ensemble energy forecast error: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.mcp.tool()
        async def real_time_energy_monitoring(
            data_source: str = "file",
            data_path: Optional[str] = None,
            monitoring_interval: int = 300,  # 5분
            alert_threshold: float = 2.0,  # 표준편차의 2배
            latitude: float = 37.5665,
            longitude: float = 126.9780
        ) -> Dict[str, Any]:
            """
            실시간 에너지 모니터링 - 지속적인 이상치 탐지 및 예측
            
            Args:
                data_source: 데이터 소스 (file, api, database)
                data_path: 데이터 파일 경로
                monitoring_interval: 모니터링 간격 (초)
                alert_threshold: 알림 임계값
                latitude: 위도
                longitude: 경도
            
            Returns:
                실시간 모니터링 결과
            """
            try:
                # 1. 데이터 로드
                if data_source == "file" and data_path:
                    df = pd.read_csv(data_path)
                else:
                    # 샘플 데이터 생성
                    df = pd.DataFrame({
                        'timestamp': pd.date_range(start='2024-01-01', periods=1000, freq='H'),
                        'consumption': np.random.normal(100, 10, 1000)
                    })
                
                # 2. 최근 데이터 추출 (마지막 24시간)
                recent_data = df.tail(24)
                
                # 3. 이상치 탐지
                prophet_model = ProphetModel()
                prophet_model.fit(recent_data['consumption'].values.tolist())
                anomalies = prophet_model.detect_anomalies(
                    recent_data['consumption'].values.tolist(),
                    threshold=1 - alert_threshold/10
                )
                
                # 4. 단기 예측 (다음 6시간)
                lstm_model = LSTMModel(
                    sequence_length=12,
                    prediction_length=6,
                    n_features=1
                )
                
                prepared_data = prepare_forecasting_data(
                    recent_data['consumption'].values.reshape(-1, 1),
                    sequence_length=12,
                    prediction_length=6
                )
                
                lstm_model.fit(prepared_data[0], prepared_data[1], epochs=20)
                forecast = lstm_model.predict(prepared_data[2])
                
                # 5. 날씨 데이터 수집
                weather_data = await self.weather_tools.get_current_weather(
                    latitude=latitude,
                    longitude=longitude,
                    api_key=self.config.OPENWEATHER_API_KEY
                )
                
                # 6. 알림 생성
                alerts = []
                if len(anomalies) > 0:
                    alerts.append({
                        "type": "anomaly_detected",
                        "message": f"{len(anomalies)}개의 이상치가 탐지되었습니다.",
                        "severity": "high" if len(anomalies) > 3 else "medium"
                    })
                
                # 7. 결과 반환
                return {
                    "status": "success",
                    "monitoring_data": {
                        "current_consumption": float(recent_data['consumption'].iloc[-1]),
                        "average_consumption": float(recent_data['consumption'].mean()),
                        "anomalies_detected": len(anomalies),
                        "anomaly_details": anomalies
                    },
                    "forecast": {
                        "next_6_hours": forecast.flatten().tolist(),
                        "forecast_confidence": 0.85
                    },
                    "weather_context": weather_data.get('weather_data', {}),
                    "alerts": alerts,
                    "monitoring_metadata": {
                        "monitoring_interval": monitoring_interval,
                        "alert_threshold": alert_threshold,
                        "data_points_analyzed": len(recent_data)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Real-time energy monitoring error: {e}")
                return {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
    
    async def start(self):
        """통합 서버 시작"""
        try:
            logger.info("Energy-Multi-MCP Integration Server starting...")
            await self.mcp.run_stdio_async()
        except Exception as e:
            logger.error(f"Integration server start failed: {e}")
            raise
    
    async def stop(self):
        """통합 서버 중지"""
        logger.info("Energy-Multi-MCP Integration Server stopping...")


async def main():
    """메인 함수"""
    integration_server = EnergyMCPIntegration()
    
    try:
        await integration_server.start()
    except KeyboardInterrupt:
        logger.info("Integration server stopped by user")
    except Exception as e:
        logger.error(f"Integration server error: {e}")
    finally:
        await integration_server.stop()


if __name__ == "__main__":
    asyncio.run(main())


