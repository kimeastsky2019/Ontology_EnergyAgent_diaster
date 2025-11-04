from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agents import anomaly_detector, fault_diagnostics, production_forecaster
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

app = FastAPI(
    title="Energy AI Agent API",
    description="에너지 AI Agent - 이상징후 감지, 고장 진단, 생산량 예측",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 스케줄러 초기화
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🤖 AI Agent 서비스 시작...")
    
    # 주기적 작업 스케줄링
    # 이상징후 감지: 5분마다
    scheduler.add_job(
        anomaly_detector.detect_anomalies,
        'interval',
        minutes=5,
        id='anomaly_detection'
    )
    
    # 고장 진단: 10분마다
    scheduler.add_job(
        fault_diagnostics.diagnose_faults,
        'interval',
        minutes=10,
        id='fault_diagnostics'
    )
    
    # 생산량 예측: 1시간마다
    scheduler.add_job(
        production_forecaster.forecast_production,
        'interval',
        hours=1,
        id='production_forecast'
    )
    
    scheduler.start()
    print("✅ AI Agent 스케줄러 시작 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    scheduler.shutdown()
    print("🛑 AI Agent 서비스 종료")

# API 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Energy AI Agent API",
        "version": "1.0.0",
        "status": "active",
        "agents": {
            "anomaly_detection": "active",
            "fault_diagnostics": "active",
            "production_forecasting": "active"
        }
    }

@app.get("/api/ai/status")
async def get_ai_status():
    """AI Agent 상태 조회"""
    return {
        "status": "active",
        "agents": {
            "anomaly_detection": {
                "status": "active",
                "last_run": scheduler.get_job('anomaly_detection').next_run_time.isoformat() if scheduler.get_job('anomaly_detection') else None,
                "interval": "5 minutes"
            },
            "fault_diagnostics": {
                "status": "active",
                "last_run": scheduler.get_job('fault_diagnostics').next_run_time.isoformat() if scheduler.get_job('fault_diagnostics') else None,
                "interval": "10 minutes"
            },
            "production_forecasting": {
                "status": "active",
                "last_run": scheduler.get_job('production_forecast').next_run_time.isoformat() if scheduler.get_job('production_forecast') else None,
                "interval": "1 hour"
            }
        }
    }

@app.get("/api/ai/anomalies")
async def get_anomalies():
    """이상징후 목록 조회"""
    return anomaly_detector.get_recent_anomalies()

@app.get("/api/ai/diagnostics")
async def get_diagnostics():
    """고장 진단 결과 조회"""
    return fault_diagnostics.get_recent_diagnostics()

@app.post("/api/ai/analyze")
async def run_analysis():
    """즉시 분석 실행"""
    anomalies = await anomaly_detector.detect_anomalies()
    diagnostics = await fault_diagnostics.diagnose_faults()
    forecast = await production_forecaster.forecast_production()
    
    return {
        "status": "completed",
        "results": {
            "anomalies": anomalies,
            "diagnostics": diagnostics,
            "forecast": forecast
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
