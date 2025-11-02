"""
에너지 데이터 분석 MCP 서버 설정

에너지 데이터 분석을 위한 서버 설정과 환경 변수를 관리합니다.
"""

import os
from typing import Optional, List

class EnergyAnalysisConfig:
    """에너지 데이터 분석 서버 설정 클래스"""
    
    # 서버 기본 설정
    SERVER_NAME: str = "Energy Analysis MCP Server"
    SERVER_VERSION: str = "1.0.0"
    SERVER_DESCRIPTION: str = "에너지 데이터 분석을 위한 MCP 서버 (시계열 분석, 예측 모델링, 대시보드, 날씨 데이터)"
    
    # 포트 설정
    DEFAULT_PORT: int = 8001
    HOST: str = "localhost"
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 데이터 저장 설정
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///energy_analysis.db")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # 날씨 API 설정
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    WEATHERAPI_API_KEY: str = os.getenv("WEATHERAPI_API_KEY", "")
    ACCUWEATHER_API_KEY: str = os.getenv("ACCUWEATHER_API_KEY", "")
    NOAA_API_KEY: str = os.getenv("NOAA_API_KEY", "")
    
    # API 기본 URL
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    WEATHERAPI_BASE_URL: str = "http://api.weatherapi.com/v1"
    ACCUWEATHER_BASE_URL: str = "http://dataservice.accuweather.com"
    NOAA_BASE_URL: str = "https://api.weather.gov"
    
    # 시계열 분석 설정
    DEFAULT_FORECAST_PERIODS: int = 30  # 기본 예측 기간 (일)
    SEASONAL_PERIODS: int = 24  # 계절성 주기 (시간)
    MIN_DATA_POINTS: int = 50  # 최소 데이터 포인트 수
    
    # 모델링 설정
    ARIMA_ORDER: tuple = (1, 1, 1)  # ARIMA 모델 기본 파라미터
    LSTM_UNITS: int = 50  # LSTM 유닛 수
    LSTM_EPOCHS: int = 100  # LSTM 훈련 에포크
    PROPHET_DAILY_SEASONALITY: bool = True
    PROPHET_WEEKLY_SEASONALITY: bool = True
    PROPHET_YEARLY_SEASONALITY: bool = True
    
    # 대시보드 설정
    CHART_WIDTH: int = 800
    CHART_HEIGHT: int = 400
    DASHBOARD_THEME: str = "plotly_white"
    
    # 에너지 특화 설정
    PEAK_DEMAND_THRESHOLD: float = 0.8  # 피크 수요 임계값 (80%)
    EFFICIENCY_THRESHOLD: float = 0.7  # 효율성 임계값 (70%)
    COST_PER_KWH: float = 0.12  # kWh당 비용 (USD)
    
    # 허용된 파일 형식
    ALLOWED_DATA_FORMATS: List[str] = ['.csv', '.json', '.xlsx', '.parquet']
    
    # API 요청 설정
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT: int = 100  # 분당 요청 수 제한
    
    # 외부 데이터 수집 설정
    CACHE_DURATION: int = 300  # 캐시 유지 시간 (초)
    MAX_CACHE_SIZE: int = 1000  # 최대 캐시 항목 수
    SCHEDULER_INTERVAL: int = 60  # 스케줄러 실행 간격 (초)
    DATA_QUALITY_THRESHOLD: float = 70.0  # 데이터 품질 임계값
    
    # 지원하는 데이터 소스
    SUPPORTED_WEATHER_SOURCES: List[str] = [
        "openweather", "weatherapi", "accuweather", "noaa"
    ]
    
    # 데이터 수집 스케줄 설정
    DEFAULT_COLLECTION_FREQUENCY: int = 60  # 기본 수집 주기 (분)
    MAX_SCHEDULES: int = 50  # 최대 스케줄 수
    
    @classmethod
    def get_port(cls) -> int:
        """환경 변수에서 포트를 가져오거나 기본값 반환"""
        return int(os.getenv("ENERGY_MCP_PORT", cls.DEFAULT_PORT))
    
    @classmethod
    def get_host(cls) -> str:
        """환경 변수에서 호스트를 가져오거나 기본값 반환"""
        return os.getenv("ENERGY_MCP_HOST", cls.HOST)
    
    @classmethod
    def get_port(cls) -> int:
        """포트 번호 반환"""
        return int(os.getenv("PORT", cls.DEFAULT_PORT))
    
    @classmethod
    def get_data_dir(cls) -> str:
        """데이터 디렉토리 경로 반환"""
        data_dir = os.path.abspath(cls.DATA_DIR)
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    @classmethod
    def validate_config(cls) -> bool:
        """설정 유효성 검사"""
        if not cls.OPENWEATHER_API_KEY:
            print("경고: OPENWEATHER_API_KEY가 설정되지 않았습니다. 날씨 데이터 수집 기능이 제한됩니다.")
        
        if cls.MIN_DATA_POINTS < 10:
            print("경고: MIN_DATA_POINTS가 너무 작습니다. 최소 10 이상을 권장합니다.")
            return False
        
        return True

