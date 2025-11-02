#!/usr/bin/env python3
"""
통합 에너지 분석 시스템 테스트
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from energy_mcp_integration import EnergyMCPIntegration

def generate_test_data(n_samples=1000):
    """테스트용 에너지 데이터 생성"""
    t = np.arange(n_samples)
    
    # 계절성 패턴
    seasonal = 50 * np.sin(2 * np.pi * t / (24 * 30))
    daily = 20 * np.sin(2 * np.pi * t / 24)
    weekly = 10 * np.sin(2 * np.pi * t / (24 * 7))
    
    # 트렌드
    trend = 0.01 * t
    
    # 노이즈
    noise = np.random.normal(0, 5, n_samples)
    
    # 기본 소비량
    base_consumption = 100
    consumption = base_consumption + seasonal + daily + weekly + trend + noise
    
    # 이상치 추가
    anomaly_indices = np.random.choice(n_samples, size=int(0.02 * n_samples), replace=False)
    consumption[anomaly_indices] += np.random.normal(0, 20, len(anomaly_indices))
    
    # 날씨 데이터
    temperature = 20 + 10 * np.sin(2 * np.pi * t / (24 * 365)) + np.random.normal(0, 3, n_samples)
    humidity = 60 + 20 * np.sin(2 * np.pi * t / (24 * 365)) + np.random.normal(0, 5, n_samples)
    
    # 데이터프레임 생성
    timestamps = pd.date_range(start='2024-01-01', periods=n_samples, freq='H')
    df = pd.DataFrame({
        'timestamp': timestamps,
        'consumption': consumption,
        'temperature': temperature,
        'humidity': humidity
    })
    
    return df

async def test_enhanced_forecast():
    """향상된 예측 테스트"""
    print("🧪 향상된 예측 테스트...")
    
    try:
        integration = EnergyMCPIntegration()
        
        # 테스트 데이터 생성
        df = generate_test_data(500)
        data_str = df.to_csv(index=False)
        
        # 예측 수행
        result = await integration.mcp.call_tool(
            "enhanced_energy_forecast",
            data=data_str,
            model_type="ensemble",
            prediction_hours=24,
            include_weather=True,
            include_anomaly_detection=True,
            latitude=37.5665,
            longitude=126.9780
        )
        
        if result.get('status') == 'success':
            print("  ✅ 향상된 예측 테스트 성공")
            print(f"    - 사용된 모델: {list(result.get('predictions', {}).keys())}")
            print(f"    - 예측 시간: {result.get('model_performance', {}).get('prediction_hours', 'N/A')}시간")
            return True
        else:
            print(f"  ❌ 향상된 예측 테스트 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 향상된 예측 테스트 오류: {e}")
        return False

async def test_advanced_anomaly_detection():
    """고급 이상치 탐지 테스트"""
    print("🧪 고급 이상치 탐지 테스트...")
    
    try:
        integration = EnergyMCPIntegration()
        
        # 테스트 데이터 생성
        df = generate_test_data(500)
        data_str = df.to_csv(index=False)
        
        # 이상치 탐지 수행
        result = await integration.mcp.call_tool(
            "advanced_anomaly_detection",
            data=data_str,
            detection_methods=["prophet", "hmm", "isolation_forest"],
            sensitivity=0.95,
            include_weather_correlation=True,
            latitude=37.5665,
            longitude=126.9780
        )
        
        if result.get('status') == 'success':
            print("  ✅ 고급 이상치 탐지 테스트 성공")
            print(f"    - 탐지된 이상치 수: {result.get('total_anomalies_detected', 0)}")
            print(f"    - 사용된 방법: {result.get('detection_methods_used', [])}")
            return True
        else:
            print(f"  ❌ 고급 이상치 탐지 테스트 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 고급 이상치 탐지 테스트 오류: {e}")
        return False

async def test_climate_aware_analysis():
    """기후 인식 분석 테스트"""
    print("🧪 기후 인식 분석 테스트...")
    
    try:
        integration = EnergyMCPIntegration()
        
        # 테스트 데이터 생성
        df = generate_test_data(500)
        data_str = df.to_csv(index=False)
        
        # 기후 인식 분석 수행
        result = await integration.mcp.call_tool(
            "climate_aware_energy_analysis",
            data=data_str,
            analysis_type="comprehensive",
            include_precipitation=True,
            include_temperature=True,
            latitude=37.5665,
            longitude=126.9780,
            prediction_days=7
        )
        
        if result.get('status') == 'success':
            print("  ✅ 기후 인식 분석 테스트 성공")
            print(f"    - 분석 타입: {result.get('analysis_metadata', {}).get('analysis_type', 'N/A')}")
            print(f"    - 예측 일수: {result.get('analysis_metadata', {}).get('prediction_days', 'N/A')}일")
            return True
        else:
            print(f"  ❌ 기후 인식 분석 테스트 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 기후 인식 분석 테스트 오류: {e}")
        return False

async def test_ensemble_forecast():
    """앙상블 예측 테스트"""
    print("🧪 앙상블 예측 테스트...")
    
    try:
        integration = EnergyMCPIntegration()
        
        # 테스트 데이터 생성
        df = generate_test_data(500)
        data_str = df.to_csv(index=False)
        
        # 앙상블 예측 수행
        result = await integration.mcp.call_tool(
            "ensemble_energy_forecast",
            data=data_str,
            models=["lstm", "cnn", "prophet", "arima"],
            prediction_hours=24,
            include_uncertainty=True,
            latitude=37.5665,
            longitude=126.9780
        )
        
        if result.get('status') == 'success':
            print("  ✅ 앙상블 예측 테스트 성공")
            print(f"    - 사용된 모델: {result.get('prediction_metadata', {}).get('models_used', [])}")
            print(f"    - 모델 가중치: {len(result.get('model_weights', {}))}개")
            return True
        else:
            print(f"  ❌ 앙상블 예측 테스트 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 앙상블 예측 테스트 오류: {e}")
        return False

async def test_real_time_monitoring():
    """실시간 모니터링 테스트"""
    print("🧪 실시간 모니터링 테스트...")
    
    try:
        integration = EnergyMCPIntegration()
        
        # 실시간 모니터링 수행
        result = await integration.mcp.call_tool(
            "real_time_energy_monitoring",
            data_source="file",
            monitoring_interval=300,
            alert_threshold=2.0,
            latitude=37.5665,
            longitude=126.9780
        )
        
        if result.get('status') == 'success':
            print("  ✅ 실시간 모니터링 테스트 성공")
            print(f"    - 현재 소비량: {result.get('monitoring_data', {}).get('current_consumption', 'N/A')}")
            print(f"    - 탐지된 이상치: {result.get('monitoring_data', {}).get('anomalies_detected', 0)}")
            return True
        else:
            print(f"  ❌ 실시간 모니터링 테스트 실패: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ❌ 실시간 모니터링 테스트 오류: {e}")
        return False

async def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 통합 에너지 분석 시스템 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("향상된 예측", test_enhanced_forecast),
        ("고급 이상치 탐지", test_advanced_anomaly_detection),
        ("기후 인식 분석", test_climate_aware_analysis),
        ("앙상블 예측", test_ensemble_forecast),
        ("실시간 모니터링", test_real_time_monitoring)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📊 {test_name} 테스트 중...")
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ❌ {test_name} 테스트 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 30)
    
    successful = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status} {test_name}")
        if success:
            successful += 1
    
    print(f"\n총 {total}개 테스트 중 {successful}개 성공 ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("🎉 모든 테스트가 성공했습니다!")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        return False

def test_data_generation():
    """데이터 생성 테스트"""
    print("🧪 데이터 생성 테스트...")
    
    try:
        df = generate_test_data(100)
        
        # 기본 검증
        assert len(df) == 100, f"예상 길이: 100, 실제: {len(df)}"
        assert 'consumption' in df.columns, "consumption 컬럼이 없습니다"
        assert 'temperature' in df.columns, "temperature 컬럼이 없습니다"
        assert 'humidity' in df.columns, "humidity 컬럼이 없습니다"
        
        # 데이터 타입 검증
        assert df['consumption'].dtype in [np.float64, np.int64], "consumption이 숫자형이 아닙니다"
        assert df['temperature'].dtype in [np.float64, np.int64], "temperature가 숫자형이 아닙니다"
        assert df['humidity'].dtype in [np.float64, np.int64], "humidity가 숫자형이 아닙니다"
        
        # 이상치 검증 (일부 이상치가 있어야 함)
        consumption_std = df['consumption'].std()
        consumption_mean = df['consumption'].mean()
        outliers = df[abs(df['consumption'] - consumption_mean) > 2 * consumption_std]
        
        print(f"  ✅ 데이터 생성 테스트 성공")
        print(f"    - 데이터 포인트: {len(df)}")
        print(f"    - 컬럼: {list(df.columns)}")
        print(f"    - 이상치 수: {len(outliers)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 데이터 생성 테스트 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🔋 통합 에너지 분석 시스템 테스트")
    print("=" * 50)
    
    # 1. 데이터 생성 테스트
    print("\n1. 데이터 생성 테스트")
    data_test_success = test_data_generation()
    
    if not data_test_success:
        print("❌ 데이터 생성 테스트가 실패했습니다. 다른 테스트를 건너뜁니다.")
        return False
    
    # 2. 통합 시스템 테스트
    print("\n2. 통합 시스템 테스트")
    integration_test_success = await run_all_tests()
    
    # 최종 결과
    print("\n" + "=" * 50)
    print("🎯 최종 테스트 결과")
    print("=" * 50)
    
    if data_test_success and integration_test_success:
        print("🎉 모든 테스트가 성공했습니다!")
        print("통합 에너지 분석 시스템이 정상적으로 작동합니다.")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("시스템을 점검하고 다시 테스트해주세요.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


