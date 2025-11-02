"""
Google Cloud Run용 에너지 분석 서버
"""

import asyncio
import logging
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import EnergyAnalysisConfig
from tools import (
    TimeSeriesTools, ModelingTools, DashboardTools, 
    WeatherTools, EnergyAnalysisTools, DataStorageTools,
    SimpleAnalysisTools, PromptTools, ExternalDataCollectionTools,
    ClimatePredictionTools, TFHubModelTools, ClimateVisualizationTools
)

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, EnergyAnalysisConfig.LOG_LEVEL),
    format=EnergyAnalysisConfig.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Energy Analysis API",
    description="통합 에너지 분석 시스템 API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
mcp_server = None
tools_registered = False

def register_tools():
    """도구들을 서버에 등록"""
    global mcp_server, tools_registered
    
    if tools_registered:
        return
    
    try:
        from fastmcp import FastMCP
        mcp_server = FastMCP()
        
        # 시계열 분석 도구 등록
        time_series_tools = TimeSeriesTools(mcp_server)
        logger.info("시계열 분석 도구 등록 완료")
        
        # 예측 모델링 도구 등록
        modeling_tools = ModelingTools(mcp_server)
        logger.info("예측 모델링 도구 등록 완료")
        
        # 대시보드 도구 등록
        dashboard_tools = DashboardTools(mcp_server)
        logger.info("대시보드 도구 등록 완료")
        
        # 날씨 데이터 도구 등록
        weather_tools = WeatherTools(mcp_server)
        logger.info("날씨 데이터 도구 등록 완료")
        
        # 에너지 특화 분석 도구 등록
        energy_analysis_tools = EnergyAnalysisTools(mcp_server)
        logger.info("에너지 특화 분석 도구 등록 완료")
        
        # 데이터 저장 도구 등록
        data_storage_tools = DataStorageTools(mcp_server)
        logger.info("데이터 저장 도구 등록 완료")
        
        # 간소화된 분석 도구 등록
        simple_analysis_tools = SimpleAnalysisTools(mcp_server)
        logger.info("간소화된 분석 도구 등록 완료")
        
        # 프롬프트 도구 등록
        prompt_tools = PromptTools(mcp_server)
        logger.info("프롬프트 도구 등록 완료")
        
        # 외부 데이터 수집 도구 등록
        external_data_tools = ExternalDataCollectionTools(mcp_server)
        logger.info("외부 데이터 수집 도구 등록 완료")
        
        # 기후 예측 도구 등록
        climate_prediction_tools = ClimatePredictionTools(mcp_server)
        logger.info("기후 예측 도구 등록 완료")
        
        # TF-Hub 모델 도구 등록
        tfhub_model_tools = TFHubModelTools(mcp_server)
        logger.info("TF-Hub 모델 도구 등록 완료")
        
        # 기후 시각화 도구 등록
        climate_visualization_tools = ClimateVisualizationTools(mcp_server)
        logger.info("기후 시각화 도구 등록 완료")
        
        tools_registered = True
        logger.info("모든 도구 등록 완료")
        
    except Exception as e:
        logger.error(f"도구 등록 실패: {e}")
        raise

# API 엔드포인트들

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Energy Analysis API v2.0.0",
        "status": "active",
        "domain": "damcp.gngmeta.com",
        "features": [
            "energy_prediction",
            "anomaly_detection", 
            "climate_analysis",
            "real_time_monitoring",
            "ensemble_modeling"
        ]
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        register_tools()
        return {
            "status": "healthy",
            "service": "energy-analysis-api",
            "version": "2.0.0",
            "domain": "damcp.gngmeta.com"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/dashboard")
async def get_dashboard_data():
    """대시보드 데이터 조회"""
    try:
        register_tools()
        # 실제 구현에서는 MCP 서버에서 데이터 조회
        return {
            "prediction_accuracy": 95.2,
            "anomaly_count": 3,
            "climate_correlation": 0.78,
            "active_models": 5,
            "energy_consumption": [100, 120, 110, 130, 125, 140],
            "predictions": [135, 142, 138, 145, 150],
            "anomalies": [
                {"timestamp": "2024-01-15T10:30:00Z", "severity": "medium"},
                {"timestamp": "2024-01-15T14:45:00Z", "severity": "low"},
                {"timestamp": "2024-01-15T18:20:00Z", "severity": "high"}
            ],
            "climate_data": [
                {"temperature": 22.5, "humidity": 65, "precipitation": 0.2},
                {"temperature": 24.1, "humidity": 58, "precipitation": 0.0},
                {"temperature": 23.8, "humidity": 62, "precipitation": 0.1}
            ]
        }
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.post("/prediction/run")
async def run_prediction():
    """에너지 예측 실행"""
    try:
        register_tools()
        return {
            "task_id": "prediction_12345",
            "status": "started",
            "message": "Prediction started successfully",
            "estimated_time": "5 minutes"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start prediction")

@app.post("/anomaly/detect")
async def detect_anomalies():
    """이상치 탐지 실행"""
    try:
        register_tools()
        return {
            "task_id": "anomaly_12345",
            "status": "started",
            "message": "Anomaly detection started successfully",
            "estimated_time": "3 minutes"
        }
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start anomaly detection")

@app.post("/climate/analyze")
async def analyze_climate():
    """기후 분석 실행"""
    try:
        register_tools()
        return {
            "task_id": "climate_12345",
            "status": "started",
            "message": "Climate analysis started successfully",
            "estimated_time": "7 minutes"
        }
    except Exception as e:
        logger.error(f"Climate analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start climate analysis")

@app.get("/models")
async def get_available_models():
    """사용 가능한 모델 목록 조회"""
    try:
        register_tools()
        return {
            "models": [
                {"name": "Ensemble", "type": "ensemble", "accuracy": 95.2, "status": "active"},
                {"name": "LSTM", "type": "lstm", "accuracy": 92.8, "status": "active"},
                {"name": "XGBoost", "type": "xgboost", "accuracy": 94.1, "status": "active"},
                {"name": "Prophet", "type": "prophet", "accuracy": 89.5, "status": "active"},
                {"name": "ARIMA", "type": "arima", "accuracy": 87.3, "status": "active"}
            ],
            "total_count": 5
        }
    except Exception as e:
        logger.error(f"Models error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")

@app.get("/statistics")
async def get_statistics():
    """시스템 통계 조회"""
    try:
        register_tools()
        return {
            "total_predictions": 1250,
            "successful_predictions": 1180,
            "anomalies_detected": 45,
            "models_trained": 12,
            "data_points_processed": 50000,
            "uptime_hours": 168,
            "average_response_time": "2.3s"
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# 서버 시작 시 도구 등록
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("🚀 Energy Analysis API 서버 시작 중...")
    register_tools()
    logger.info("✅ 서버 시작 완료!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
