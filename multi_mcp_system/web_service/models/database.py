"""
데이터베이스 모델 및 스키마 - Multi-MCP Time Series Analysis System
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mcp_analysis.db')

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ForecastingModel(Base):
    """예측 모델 테이블"""
    __tablename__ = "forecasting_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True, nullable=False)
    model_type = Column(String(50), nullable=False)  # lstm, cnn, multivariate_lstm, etc.
    model_path = Column(String(255))  # 모델 파일 경로
    data_shape = Column(JSON)  # 훈련 데이터 형태
    parameters = Column(JSON)  # 모델 파라미터
    metrics = Column(JSON)  # 성능 지표 (RMSE, MAE, R² 등)
    training_data_hash = Column(String(64))  # 훈련 데이터 해시
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    description = Column(Text)


class AnomalyModel(Base):
    """이상치 탐지 모델 테이블"""
    __tablename__ = "anomaly_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True, nullable=False)
    model_type = Column(String(50), nullable=False)  # prophet, hmm, transformer, etc.
    model_path = Column(String(255))  # 모델 파일 경로
    data_shape = Column(JSON)  # 훈련 데이터 형태
    parameters = Column(JSON)  # 모델 파라미터
    metrics = Column(JSON)  # 성능 지표 (precision, recall, F1 등)
    training_data_hash = Column(String(64))  # 훈련 데이터 해시
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    description = Column(Text)


class AnalysisSession(Base):
    """분석 세션 테이블"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    analysis_type = Column(String(50), nullable=False)  # forecast_and_detect, ensemble_forecast, etc.
    data_shape = Column(JSON)  # 분석 데이터 형태
    parameters = Column(JSON)  # 분석 파라미터
    status = Column(String(20), default='running')  # running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    description = Column(Text)


class PredictionResult(Base):
    """예측 결과 테이블"""
    __tablename__ = "prediction_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    model_name = Column(String(100), index=True)
    model_type = Column(String(50))
    input_data_hash = Column(String(64))  # 입력 데이터 해시
    predictions = Column(JSON)  # 예측 결과
    confidence_scores = Column(JSON)  # 신뢰도 점수
    metrics = Column(JSON)  # 예측 성능 지표
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # 처리 시간 (초)


class AnomalyDetectionResult(Base):
    """이상치 탐지 결과 테이블"""
    __tablename__ = "anomaly_detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    model_name = Column(String(100), index=True)
    model_type = Column(String(50))
    input_data_hash = Column(String(64))  # 입력 데이터 해시
    anomaly_indices = Column(JSON)  # 이상치 인덱스
    anomaly_scores = Column(JSON)  # 이상치 점수
    threshold = Column(Float)  # 탐지 임계값
    metrics = Column(JSON)  # 탐지 성능 지표
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # 처리 시간 (초)


class DataSource(Base):
    """데이터 소스 테이블"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, index=True, nullable=False)
    source_type = Column(String(50), nullable=False)  # file, database, api, etc.
    source_path = Column(String(255))  # 데이터 소스 경로
    data_format = Column(String(20))  # csv, json, parquet, etc.
    data_shape = Column(JSON)  # 데이터 형태
    metadata = Column(JSON)  # 추가 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    description = Column(Text)


class SystemLog(Base):
    """시스템 로그 테이블"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(50), nullable=False)  # forecasting, anomaly, coordinator, api
    message = Column(Text, nullable=False)
    details = Column(JSON)  # 추가 세부사항
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100))  # 사용자 ID (선택사항)


class ModelPerformance(Base):
    """모델 성능 추적 테이블"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), index=True, nullable=False)
    model_type = Column(String(50), nullable=False)
    performance_type = Column(String(50), nullable=False)  # training, validation, test
    metrics = Column(JSON, nullable=False)  # 성능 지표
    data_size = Column(Integer)  # 데이터 크기
    training_time = Column(Float)  # 훈련 시간 (초)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    """사용자 세션 테이블"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True)
    ip_address = Column(String(45))  # IPv4/IPv6 주소
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


# 데이터베이스 초기화 함수
def init_database():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 데이터베이스 유틸리티 함수들
class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_forecasting_model(self, model_name: str, model_type: str, 
                               data_shape: tuple, parameters: dict, 
                               metrics: dict, model_path: str = None):
        """예측 모델 생성"""
        db = self.SessionLocal()
        try:
            model = ForecastingModel(
                model_name=model_name,
                model_type=model_type,
                data_shape=list(data_shape),
                parameters=parameters,
                metrics=metrics,
                model_path=model_path
            )
            db.add(model)
            db.commit()
            return model
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_anomaly_model(self, model_name: str, model_type: str,
                           data_shape: tuple, parameters: dict,
                           metrics: dict, model_path: str = None):
        """이상치 탐지 모델 생성"""
        db = self.SessionLocal()
        try:
            model = AnomalyModel(
                model_name=model_name,
                model_type=model_type,
                data_shape=list(data_shape),
                parameters=parameters,
                metrics=metrics,
                model_path=model_path
            )
            db.add(model)
            db.commit()
            return model
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_analysis_session(self, session_id: str, analysis_type: str,
                              data_shape: tuple, parameters: dict):
        """분석 세션 생성"""
        db = self.SessionLocal()
        try:
            session = AnalysisSession(
                session_id=session_id,
                analysis_type=analysis_type,
                data_shape=list(data_shape),
                parameters=parameters
            )
            db.add(session)
            db.commit()
            return session
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def log_system_event(self, level: str, component: str, message: str, 
                        details: dict = None, user_id: str = None):
        """시스템 이벤트 로깅"""
        db = self.SessionLocal()
        try:
            log = SystemLog(
                level=level,
                component=component,
                message=message,
                details=details,
                user_id=user_id
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_forecasting_models(self, active_only: bool = True):
        """예측 모델 목록 조회"""
        db = self.SessionLocal()
        try:
            query = db.query(ForecastingModel)
            if active_only:
                query = query.filter(ForecastingModel.is_active == True)
            return query.all()
        finally:
            db.close()
    
    def get_anomaly_models(self, active_only: bool = True):
        """이상치 탐지 모델 목록 조회"""
        db = self.SessionLocal()
        try:
            query = db.query(AnomalyModel)
            if active_only:
                query = query.filter(AnomalyModel.is_active == True)
            return query.all()
        finally:
            db.close()
    
    def get_analysis_history(self, limit: int = 10):
        """분석 히스토리 조회"""
        db = self.SessionLocal()
        try:
            return db.query(AnalysisSession).order_by(
                AnalysisSession.created_at.desc()
            ).limit(limit).all()
        finally:
            db.close()
    
    def get_model_performance(self, model_name: str = None, limit: int = 100):
        """모델 성능 조회"""
        db = self.SessionLocal()
        try:
            query = db.query(ModelPerformance)
            if model_name:
                query = query.filter(ModelPerformance.model_name == model_name)
            return query.order_by(
                ModelPerformance.created_at.desc()
            ).limit(limit).all()
        finally:
            db.close()


# 데이터베이스 초기화
if __name__ == "__main__":
    init_database()
    print("Database initialization completed!")


