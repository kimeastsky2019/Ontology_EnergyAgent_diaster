"""
에너지 데이터 분석 MCP 서버

시계열 분석, 예측 모델링, 대시보드, 날씨 데이터 수집을 통합한 에너지 분석 서비스
"""

import asyncio
import logging
from typing import Dict, Any
from fastmcp import FastMCP

from config.settings import EnergyAnalysisConfig
from tools import (
    TimeSeriesTools, ModelingTools, DashboardTools, 
    WeatherTools, EnergyAnalysisTools, DataStorageTools,
    SimpleAnalysisTools, PromptTools, ExternalDataCollectionTools,
    ClimatePredictionTools, TFHubModelTools, ClimateVisualizationTools
)
from tools.kma_weather_tools import KMAWeatherTools

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, EnergyAnalysisConfig.LOG_LEVEL),
    format=EnergyAnalysisConfig.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class EnergyAnalysisServer:
    """에너지 데이터 분석 MCP 서버 클래스"""
    
    def __init__(self):
        self.mcp = FastMCP()
        self.config = EnergyAnalysisConfig()
        self._validate_config()
        self._register_tools()
    
    def _validate_config(self):
        """설정 유효성 검사"""
        if not self.config.validate_config():
            logger.warning("설정 검증에서 경고가 발생했습니다.")
    
    def _register_tools(self):
        """도구들을 서버에 등록"""
        try:
            # 시계열 분석 도구 등록
            self.time_series_tools = TimeSeriesTools(self.mcp)
            logger.info("시계열 분석 도구 등록 완료")
            
            # 예측 모델링 도구 등록
            self.modeling_tools = ModelingTools(self.mcp)
            logger.info("예측 모델링 도구 등록 완료")
            
            # 대시보드 도구 등록
            self.dashboard_tools = DashboardTools(self.mcp)
            logger.info("대시보드 도구 등록 완료")
            
            # 날씨 데이터 도구 등록
            self.weather_tools = WeatherTools(self.mcp)
            logger.info("날씨 데이터 도구 등록 완료")
            
            # 에너지 특화 분석 도구 등록
            self.energy_analysis_tools = EnergyAnalysisTools(self.mcp)
            logger.info("에너지 특화 분석 도구 등록 완료")
            
            # 데이터 저장 도구 등록
            self.data_storage_tools = DataStorageTools(self.mcp)
            logger.info("데이터 저장 도구 등록 완료")
            
            # 간소화된 분석 도구 등록
            self.simple_analysis_tools = SimpleAnalysisTools(self.mcp)
            logger.info("간소화된 분석 도구 등록 완료")
            
            # 프롬프트 도구 등록
            self.prompt_tools = PromptTools(self.mcp)
            logger.info("프롬프트 도구 등록 완료")
            
            # 외부 데이터 수집 도구 등록
            self.external_data_tools = ExternalDataCollectionTools(self.mcp)
            logger.info("외부 데이터 수집 도구 등록 완료")
            
            # 기후 예측 도구 등록
            self.climate_prediction_tools = ClimatePredictionTools(self.mcp)
            logger.info("기후 예측 도구 등록 완료")
            
            # TF-Hub 모델 도구 등록
            self.tfhub_model_tools = TFHubModelTools(self.mcp)
            logger.info("TF-Hub 모델 도구 등록 완료")
            
            # 기후 시각화 도구 등록
            self.climate_visualization_tools = ClimateVisualizationTools(self.mcp)
            logger.info("기후 시각화 도구 등록 완료")
            
            # KMA 날씨 도구 등록
            self.kma_weather_tools = KMAWeatherTools(self.mcp)
            logger.info("KMA 날씨 도구 등록 완료")
            
        except Exception as e:
            logger.error(f"도구 등록 실패: {e}")
            raise
    
    async def start(self):
        """서버 시작"""
        try:
            logger.info(f"에너지 분석 서버 시작 중... (포트: {self.config.get_port()})")
            
            # 데이터 디렉토리 생성
            data_dir = self.config.get_data_dir()
            logger.info(f"데이터 디렉토리: {data_dir}")
            
            # 서버 실행 (stdio 모드)
            await self.mcp.run_stdio_async()
            
        except Exception as e:
            logger.error(f"서버 시작 실패: {e}")
            raise
    
    async def stop(self):
        """서버 중지"""
        logger.info("에너지 분석 서버 중지 중...")

async def main():
    """메인 함수"""
    server = EnergyAnalysisServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 서버 중지 요청됨")
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {e}")
    finally:
        await server.stop()

if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())

