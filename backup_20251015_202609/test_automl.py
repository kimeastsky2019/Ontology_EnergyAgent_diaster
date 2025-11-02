#!/usr/bin/env python3
"""
AutoML 테스트 스크립트
"""

import numpy as np
import pandas as pd
from automl.model_optimizer import ModelOptimizer
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_automl():
    """AutoML 테스트"""
    try:
        logger.info("AutoML 테스트 시작")
        
        # 샘플 데이터 생성
        np.random.seed(42)
        n_samples = 1000
        
        # 에너지 소비 데이터 생성
        time_index = pd.date_range('2023-01-01', periods=n_samples, freq='H')
        
        # 기본 패턴 + 노이즈
        base_consumption = 100 + 20 * np.sin(2 * np.pi * np.arange(n_samples) / 24)  # 일일 패턴
        seasonal_pattern = 10 * np.sin(2 * np.pi * np.arange(n_samples) / (24 * 365))  # 연간 패턴
        noise = np.random.normal(0, 5, n_samples)
        
        consumption = base_consumption + seasonal_pattern + noise
        
        # 특성 데이터 생성
        features = pd.DataFrame({
            'hour': time_index.hour,
            'day_of_week': time_index.dayofweek,
            'month': time_index.month,
            'temperature': 20 + 10 * np.sin(2 * np.pi * np.arange(n_samples) / 24) + np.random.normal(0, 2, n_samples),
            'humidity': 50 + 20 * np.sin(2 * np.pi * np.arange(n_samples) / 24) + np.random.normal(0, 5, n_samples),
            'consumption': consumption
        })
        
        logger.info(f"생성된 데이터: {features.shape}")
        logger.info(f"특성: {features.columns.tolist()}")
        
        # AutoML 최적화 실행
        optimizer = ModelOptimizer()
        
        # XGBoost 모델 최적화
        X = features.drop('consumption', axis=1).values
        y = features['consumption'].values
        
        logger.info("XGBoost 모델 최적화 시작...")
        result = await optimizer.optimize_xgboost_model(X, y, "test_xgboost")
        
        logger.info("최적화 결과:")
        logger.info(f"- 모델명: {result['model_name']}")
        logger.info(f"- 최적 점수: {result['best_score']:.4f}")
        logger.info(f"- 최적 파라미터: {result['best_params']}")
        logger.info(f"- 성능: {result['performance']}")
        
        # 모델 저장
        optimizer.save_models("test_models.pkl")
        logger.info("모델이 test_models.pkl에 저장되었습니다")
        
        logger.info("AutoML 테스트 완료!")
        
    except Exception as e:
        logger.error(f"AutoML 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_automl())
