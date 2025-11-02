"""
Energy Analysis API Server
FastAPI 기반 REST API 서버
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta
import uvicorn

# MCP 서버 연동
from mcp_client import MCPClient
from auth_service import AuthService
from rate_limiter import RateLimiter
from cache_service import CacheService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
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
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 의존성
security = HTTPBearer()
auth_service = AuthService()
rate_limiter = RateLimiter()
cache_service = CacheService()
mcp_client = MCPClient()

# Pydantic 모델들
class PredictionRequest(BaseModel):
    model_type: str = Field(..., description="모델 타입 (ensemble, lstm, cnn, prophet, arima)")
    prediction_hours: int = Field(24, ge=1, le=168, description="예측 시간 (1-168시간)")
    include_weather: bool = Field(True, description="날씨 데이터 포함 여부")
    include_anomaly_detection: bool = Field(True, description="이상치 탐지 포함 여부")

class AnomalyDetectionRequest(BaseModel):
    detection_method: str = Field(..., description="탐지 방법 (prophet, hmm, isolation_forest)")
    sensitivity: float = Field(0.95, ge=0.1, le=1.0, description="민감도 (0.1-1.0)")

class ClimateAnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="분석 타입 (comprehensive, seasonal, weather_correlation)")
    prediction_days: int = Field(7, ge=1, le=30, description="예측 일수 (1-30일)")

class DataGenerationRequest(BaseModel):
    sample_count: int = Field(1000, ge=100, le=10000, description="샘플 수 (100-10000)")
    include_weather: bool = Field(True, description="날씨 데이터 포함 여부")

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    organization: Optional[str] = None

# 인증 의존성
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Rate limiting 의존성
async def check_rate_limit(user_id: str = Depends(get_current_user)):
    if not await rate_limiter.check_limit(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return user_id

# API 엔드포인트들

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Energy Analysis API v2.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "energy_prediction",
            "anomaly_detection", 
            "climate_analysis",
            "real_time_monitoring",
            "ensemble_modeling"
        ]
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # MCP 서버 연결 상태 확인
        mcp_status = await mcp_client.check_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mcp_server": mcp_status,
                "database": "connected",
                "cache": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/auth/login", response_model=Dict[str, Any])
async def login(user_data: UserLogin):
    """사용자 로그인"""
    try:
        token = await auth_service.authenticate(user_data.username, user_data.password)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/register", response_model=Dict[str, Any])
async def register(user_data: UserRegister):
    """사용자 회원가입"""
    try:
        user = await auth_service.register_user(user_data)
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(user_id: str = Depends(check_rate_limit)):
    """대시보드 데이터 조회"""
    try:
        # 캐시에서 데이터 확인
        cached_data = await cache_service.get("dashboard_data")
        if cached_data:
            return cached_data
        
        # MCP 서버에서 데이터 조회
        dashboard_data = await mcp_client.get_dashboard_data()
        
        # 캐시에 저장 (5분)
        await cache_service.set("dashboard_data", dashboard_data, 300)
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.post("/prediction/run", response_model=Dict[str, Any])
async def run_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(check_rate_limit)
):
    """에너지 예측 실행"""
    try:
        # 백그라운드에서 예측 실행
        task_id = f"prediction_{user_id}_{datetime.now().timestamp()}"
        
        background_tasks.add_task(
            execute_prediction,
            task_id,
            request.model_type,
            request.prediction_hours,
            request.include_weather,
            request.include_anomaly_detection
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Prediction started in background"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start prediction")

@app.post("/anomaly/detect", response_model=Dict[str, Any])
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(check_rate_limit)
):
    """이상치 탐지 실행"""
    try:
        task_id = f"anomaly_{user_id}_{datetime.now().timestamp()}"
        
        background_tasks.add_task(
            execute_anomaly_detection,
            task_id,
            request.detection_method,
            request.sensitivity
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Anomaly detection started in background"
        }
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start anomaly detection")

@app.post("/climate/analyze", response_model=Dict[str, Any])
async def analyze_climate(
    request: ClimateAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(check_rate_limit)
):
    """기후 분석 실행"""
    try:
        task_id = f"climate_{user_id}_{datetime.now().timestamp()}"
        
        background_tasks.add_task(
            execute_climate_analysis,
            task_id,
            request.analysis_type,
            request.prediction_days
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "message": "Climate analysis started in background"
        }
    except Exception as e:
        logger.error(f"Climate analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start climate analysis")

@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str, user_id: str = Depends(check_rate_limit)):
    """작업 상태 조회"""
    try:
        status = await cache_service.get(f"task_{task_id}")
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return status
    except Exception as e:
        logger.error(f"Task status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")

@app.post("/data/generate", response_model=Dict[str, Any])
async def generate_sample_data(
    request: DataGenerationRequest,
    user_id: str = Depends(check_rate_limit)
):
    """샘플 데이터 생성"""
    try:
        data = await mcp_client.generate_sample_data(
            request.sample_count,
            request.include_weather
        )
        
        return {
            "message": "Sample data generated successfully",
            "sample_count": request.sample_count,
            "data": data
        }
    except Exception as e:
        logger.error(f"Data generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate sample data")

@app.get("/models", response_model=Dict[str, Any])
async def get_available_models(user_id: str = Depends(check_rate_limit)):
    """사용 가능한 모델 목록 조회"""
    try:
        models = await mcp_client.get_available_models()
        return {
            "models": models,
            "total_count": len(models)
        }
    except Exception as e:
        logger.error(f"Models error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")

@app.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(user_id: str = Depends(check_rate_limit)):
    """시스템 통계 조회"""
    try:
        stats = await mcp_client.get_system_statistics()
        return stats
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# 백그라운드 작업 함수들
async def execute_prediction(task_id: str, model_type: str, hours: int, include_weather: bool, include_anomaly: bool):
    """예측 실행 백그라운드 작업"""
    try:
        await cache_service.set(f"task_{task_id}", {"status": "running", "progress": 0})
        
        result = await mcp_client.run_prediction(
            model_type=model_type,
            prediction_hours=hours,
            include_weather=include_weather,
            include_anomaly_detection=include_anomaly
        )
        
        await cache_service.set(f"task_{task_id}", {
            "status": "completed",
            "progress": 100,
            "result": result
        })
        
    except Exception as e:
        await cache_service.set(f"task_{task_id}", {
            "status": "failed",
            "error": str(e)
        })

async def execute_anomaly_detection(task_id: str, method: str, sensitivity: float):
    """이상치 탐지 백그라운드 작업"""
    try:
        await cache_service.set(f"task_{task_id}", {"status": "running", "progress": 0})
        
        result = await mcp_client.run_anomaly_detection(
            detection_method=method,
            sensitivity=sensitivity
        )
        
        await cache_service.set(f"task_{task_id}", {
            "status": "completed",
            "progress": 100,
            "result": result
        })
        
    except Exception as e:
        await cache_service.set(f"task_{task_id}", {
            "status": "failed",
            "error": str(e)
        })

async def execute_climate_analysis(task_id: str, analysis_type: str, days: int):
    """기후 분석 백그라운드 작업"""
    try:
        await cache_service.set(f"task_{task_id}", {"status": "running", "progress": 0})
        
        result = await mcp_client.run_climate_analysis(
            analysis_type=analysis_type,
            prediction_days=days
        )
        
        await cache_service.set(f"task_{task_id}", {
            "status": "completed",
            "progress": 100,
            "result": result
        })
        
    except Exception as e:
        await cache_service.set(f"task_{task_id}", {
            "status": "failed",
            "error": str(e)
        })

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
