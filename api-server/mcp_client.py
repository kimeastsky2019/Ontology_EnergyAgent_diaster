"""
MCP 클라이언트 모듈
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def check_connection(self) -> bool:
        """MCP 서버 연결 상태 확인"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"MCP 서버 연결 실패: {e}")
            return False
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드 데이터 조회"""
        try:
            response = await self.client.get(f"{self.base_url}/dashboard")
            return response.json()
        except Exception as e:
            logger.error(f"대시보드 데이터 조회 실패: {e}")
            return {}
    
    async def run_prediction(self, model_type: str = "ensemble", 
                           prediction_hours: int = 24,
                           include_weather: bool = True,
                           include_anomaly_detection: bool = True) -> Dict[str, Any]:
        """예측 실행"""
        try:
            data = {
                "model_type": model_type,
                "prediction_hours": prediction_hours,
                "include_weather": include_weather,
                "include_anomaly_detection": include_anomaly_detection
            }
            response = await self.client.post(f"{self.base_url}/prediction", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"예측 실행 실패: {e}")
            return {"error": str(e)}
    
    async def run_anomaly_detection(self, detection_method: str = "prophet",
                                  sensitivity: float = 0.95) -> Dict[str, Any]:
        """이상치 탐지 실행"""
        try:
            data = {
                "detection_method": detection_method,
                "sensitivity": sensitivity
            }
            response = await self.client.post(f"{self.base_url}/anomaly", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"이상치 탐지 실행 실패: {e}")
            return {"error": str(e)}
    
    async def run_climate_analysis(self, analysis_type: str = "comprehensive",
                                 prediction_days: int = 7) -> Dict[str, Any]:
        """기후 분석 실행"""
        try:
            data = {
                "analysis_type": analysis_type,
                "prediction_days": prediction_days
            }
            response = await self.client.post(f"{self.base_url}/climate", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"기후 분석 실행 실패: {e}")
            return {"error": str(e)}
    
    async def generate_sample_data(self, sample_count: int = 1000,
                                 include_weather: bool = True) -> Dict[str, Any]:
        """샘플 데이터 생성"""
        try:
            data = {
                "sample_count": sample_count,
                "include_weather": include_weather
            }
            response = await self.client.post(f"{self.base_url}/data/generate", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"샘플 데이터 생성 실패: {e}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> Dict[str, Any]:
        """사용 가능한 모델 목록 조회"""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            return response.json()
        except Exception as e:
            logger.error(f"모델 목록 조회 실패: {e}")
            return {"models": []}
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        try:
            response = await self.client.get(f"{self.base_url}/statistics")
            return response.json()
        except Exception as e:
            logger.error(f"시스템 통계 조회 실패: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()
