from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import energy, facilities, weather
import uvicorn

app = FastAPI(
    title="Energy Monitoring API",
    description="에너지 모니터링 및 AI 기반 이상징후 감지 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(energy.router, prefix="/api/energy", tags=["Energy"])
app.include_router(facilities.router, prefix="/api/facilities", tags=["Facilities"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])

@app.get("/")
async def root():
    return {
        "message": "Energy Monitoring API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
