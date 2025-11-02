"""
기후 예측 MCP 기능 테스트

새로 추가된 기후 예측 및 강수 nowcasting 기능들을 테스트합니다.
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# 테스트용 샘플 데이터 생성
def create_test_radar_data():
    """테스트용 레이더 데이터 생성"""
    # 24시간의 5분 간격 데이터 (288 프레임)
    time_steps = 288
    height, width = 256, 256
    
    # 합성 강수 패턴 생성
    radar_data = []
    timestamps = []
    
    base_time = datetime.now() - timedelta(hours=24)
    
    for t in range(time_steps):
        # 시간에 따른 강수 패턴
        time_factor = 1 + 0.3 * np.sin(2 * np.pi * t / 288)  # 일일 패턴
        
        # 공간적 강수 패턴
        x, y = np.meshgrid(np.linspace(0, 4*np.pi, width), np.linspace(0, 4*np.pi, height))
        spatial_pattern = np.sin(x) * np.cos(y) * np.exp(-(x-2*np.pi)**2/10 - (y-2*np.pi)**2/10)
        
        # 이동하는 강수 시스템
        shift_x = int(5 * np.sin(t * 0.1))
        shift_y = int(3 * np.cos(t * 0.1))
        spatial_pattern = np.roll(np.roll(spatial_pattern, shift_x, axis=1), shift_y, axis=0)
        
        # 강수 강도 적용
        intensity = time_factor * np.random.gamma(2, 1) * 10  # mm/hr
        precipitation = np.maximum(0, spatial_pattern * intensity)
        
        radar_data.append(precipitation.tolist())
        timestamps.append((base_time + timedelta(minutes=t*5)).isoformat())
    
    return radar_data, timestamps

def create_test_energy_data():
    """테스트용 에너지 데이터 생성"""
    # 24시간의 시간별 에너지 소비 데이터
    hours = 24
    energy_data = []
    
    base_time = datetime.now() - timedelta(hours=24)
    
    for h in range(hours):
        # 시간대별 패턴 (새벽 최소, 오후 최대)
        if 3 <= h <= 5:
            base_consumption = 50
        elif 14 <= h <= 16:
            base_consumption = 150
        elif 8 <= h <= 18:
            base_consumption = 100
        else:
            base_consumption = 80
        
        # 랜덤 변동
        consumption = base_consumption + np.random.normal(0, 10)
        
        energy_data.append({
            'datetime': (base_time + timedelta(hours=h)).isoformat(),
            'consumption': max(0, consumption),
            'temperature': 20 + 10 * np.sin(2 * np.pi * h / 24) + np.random.normal(0, 2),
            'humidity': 50 + 20 * np.sin(2 * np.pi * h / 24 + np.pi) + np.random.normal(0, 5)
        })
    
    return energy_data

async def test_climate_prediction_tools():
    """기후 예측 도구 테스트"""
    print("\n🌧️ 기후 예측 도구 테스트 시작...")
    
    try:
        # 테스트 데이터 생성
        radar_data, timestamps = create_test_radar_data()
        energy_data = create_test_energy_data()
        
        print("📋 테스트할 기후 예측 도구들:")
        test_tools = [
            "generate_synthetic_radar_data",
            "analyze_precipitation_patterns",
            "predict_precipitation_nowcasting",
            "create_precipitation_animation",
            "calculate_precipitation_metrics",
            "correlate_precipitation_energy"
        ]
        
        for tool in test_tools:
            print(f"  • {tool}")
        
        # 테스트 케이스들
        test_cases = {
            "generate_synthetic_radar_data": {
                "latitude": 37.5665,
                "longitude": 126.9780,
                "hours": 24,
                "resolution": "1km"
            },
            "analyze_precipitation_patterns": {
                "radar_data": radar_data,
                "timestamps": timestamps,
                "analysis_type": "advanced"
            },
            "predict_precipitation_nowcasting": {
                "radar_data": radar_data,
                "prediction_hours": 2,
                "model_type": "statistical"
            },
            "create_precipitation_animation": {
                "radar_data": radar_data,
                "timestamps": timestamps,
                "output_path": "test_precipitation_animation.gif",
                "animation_type": "enhanced"
            },
            "calculate_precipitation_metrics": {
                "radar_data": radar_data,
                "timestamps": timestamps,
                "metrics": ["total_precipitation", "max_intensity", "duration", "coverage"]
            },
            "correlate_precipitation_energy": {
                "radar_data": radar_data,
                "energy_data": energy_data,
                "correlation_type": "temporal"
            }
        }
        
        print("\n📊 테스트 케이스:")
        for tool, params in test_cases.items():
            print(f"  • {tool}: {list(params.keys())}")
        
        print("\n⚠️  실제 테스트를 위해서는 다음이 필요합니다:")
        print("  1. MCP 서버 실행: python server.py")
        print("  2. MCP 클라이언트를 사용하여 도구들 호출")
        print("  3. TensorFlow 및 Cartopy 설치 (선택사항)")
        
        print("\n✅ 기후 예측 도구 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

async def test_tfhub_model_tools():
    """TF-Hub 모델 도구 테스트"""
    print("\n🤖 TF-Hub 모델 도구 테스트 시작...")
    
    try:
        print("📋 테스트할 TF-Hub 모델 도구들:")
        tfhub_tools = [
            "load_tfhub_precipitation_model",
            "predict_with_tfhub_model",
            "evaluate_precipitation_forecast",
            "generate_ensemble_forecast",
            "get_model_info"
        ]
        
        for tool in tfhub_tools:
            print(f"  • {tool}")
        
        # 테스트 케이스들
        test_cases = {
            "load_tfhub_precipitation_model": {
                "model_size": "256x256",
                "use_local": False
            },
            "predict_with_tfhub_model": {
                "radar_data": "test_radar_data",  # 실제로는 데이터 전달
                "model_size": "256x256",
                "num_samples": 3,
                "include_input_frames": True
            },
            "evaluate_precipitation_forecast": {
                "predicted_data": "test_predicted_data",
                "ground_truth_data": "test_ground_truth_data",
                "metrics": ["mse", "mae", "rmse", "correlation"]
            },
            "generate_ensemble_forecast": {
                "radar_data": "test_radar_data",
                "model_sizes": ["256x256"],
                "num_samples_per_model": 2
            }
        }
        
        print("\n📊 테스트 케이스:")
        for tool, params in test_cases.items():
            print(f"  • {tool}: {list(params.keys())}")
        
        print("\n⚠️  실제 TF-Hub 모델 테스트를 위해서는:")
        print("  1. TensorFlow 및 TensorFlow Hub 설치")
        print("  2. 모델 다운로드 (선택사항)")
        print("  3. MCP 서버 실행")
        print("  4. MCP 클라이언트를 사용하여 도구들 호출")
        
        print("\n✅ TF-Hub 모델 도구 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ TF-Hub 모델 테스트 중 오류 발생: {e}")

async def test_climate_visualization_tools():
    """기후 시각화 도구 테스트"""
    print("\n📊 기후 시각화 도구 테스트 시작...")
    
    try:
        # 테스트 데이터 생성
        radar_data, timestamps = create_test_radar_data()
        energy_data = create_test_energy_data()
        
        print("📋 테스트할 기후 시각화 도구들:")
        viz_tools = [
            "create_precipitation_heatmap",
            "create_precipitation_animation",
            "create_climate_dashboard",
            "create_precipitation_forecast_plot",
            "create_climate_correlation_plot"
        ]
        
        for tool in viz_tools:
            print(f"  • {tool}")
        
        # 테스트 케이스들
        test_cases = {
            "create_precipitation_heatmap": {
                "radar_data": radar_data,
                "timestamps": timestamps,
                "output_path": "test_heatmap.png",
                "style": "enhanced"
            },
            "create_precipitation_animation": {
                "radar_data": radar_data,
                "timestamps": timestamps,
                "output_path": "test_animation.gif",
                "animation_style": "enhanced"
            },
            "create_climate_dashboard": {
                "radar_data": radar_data,
                "weather_data": energy_data,  # 온도, 습도 데이터로 사용
                "energy_data": energy_data,
                "output_path": "test_dashboard.png"
            },
            "create_precipitation_forecast_plot": {
                "predicted_data": radar_data[-10:],  # 마지막 10프레임을 예측으로 사용
                "ground_truth_data": radar_data[-10:],
                "timestamps": timestamps[-10:],
                "output_path": "test_forecast_plot.png"
            },
            "create_climate_correlation_plot": {
                "radar_data": radar_data,
                "energy_data": energy_data,
                "output_path": "test_correlation_plot.png"
            }
        }
        
        print("\n📊 테스트 케이스:")
        for tool, params in test_cases.items():
            print(f"  • {tool}: {list(params.keys())}")
        
        print("\n⚠️  실제 시각화 테스트를 위해서는:")
        print("  1. MCP 서버 실행: python server.py")
        print("  2. MCP 클라이언트를 사용하여 도구들 호출")
        print("  3. Cartopy 설치 (지도 시각화용, 선택사항)")
        
        print("\n✅ 기후 시각화 도구 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ 기후 시각화 테스트 중 오류 발생: {e}")

def test_data_generation():
    """데이터 생성 테스트"""
    print("\n📊 테스트 데이터 생성 테스트...")
    
    try:
        # 레이더 데이터 생성
        radar_data, timestamps = create_test_radar_data()
        print(f"✅ 레이더 데이터 생성 완료: {len(radar_data)} 프레임, {len(timestamps)} 타임스탬프")
        print(f"   데이터 형태: {np.array(radar_data).shape}")
        
        # 에너지 데이터 생성
        energy_data = create_test_energy_data()
        print(f"✅ 에너지 데이터 생성 완료: {len(energy_data)} 레코드")
        print(f"   컬럼: {list(energy_data[0].keys())}")
        
        # 데이터 품질 검사
        radar_array = np.array(radar_data)
        print(f"   레이더 데이터 통계:")
        print(f"     - 최대값: {np.max(radar_array):.2f} mm/hr")
        print(f"     - 평균값: {np.mean(radar_array):.2f} mm/hr")
        print(f"     - 0이 아닌 값의 비율: {np.mean(radar_array > 0):.2%}")
        
        energy_df = pd.DataFrame(energy_data)
        print(f"   에너지 데이터 통계:")
        print(f"     - 평균 소비량: {energy_df['consumption'].mean():.2f}")
        print(f"     - 최대 소비량: {energy_df['consumption'].max():.2f}")
        print(f"     - 최소 소비량: {energy_df['consumption'].min():.2f}")
        
        print("\n✅ 테스트 데이터 생성 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 데이터 생성 테스트 중 오류 발생: {e}")

async def test_integration_scenarios():
    """통합 시나리오 테스트"""
    print("\n🔗 통합 시나리오 테스트...")
    
    try:
        print("📋 테스트할 통합 시나리오들:")
        scenarios = [
            "1. 합성 레이더 데이터 생성 → 강수 패턴 분석 → 예측 수행",
            "2. 강수 데이터 → 에너지 데이터 상관관계 분석 → 시각화",
            "3. TF-Hub 모델 로드 → 예측 수행 → 성능 평가",
            "4. 다중 모델 앙상블 → 예측 정확도 비교",
            "5. 기후 대시보드 생성 (강수 + 날씨 + 에너지)"
        ]
        
        for scenario in scenarios:
            print(f"  {scenario}")
        
        print("\n💡 실제 통합 테스트를 위해서는:")
        print("  1. 모든 의존성 설치: pip install -r requirements.txt")
        print("  2. MCP 서버 실행: python server.py")
        print("  3. MCP 클라이언트를 사용하여 시나리오별 도구 호출")
        print("  4. 생성된 시각화 파일 확인")
        
        print("\n✅ 통합 시나리오 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ 통합 시나리오 테스트 중 오류 발생: {e}")

async def main():
    """메인 테스트 함수"""
    print("🌧️ 기후 예측 MCP 기능 테스트")
    print("=" * 60)
    
    # 1. 데이터 생성 테스트
    test_data_generation()
    
    # 2. 기후 예측 도구 테스트
    await test_climate_prediction_tools()
    
    # 3. TF-Hub 모델 도구 테스트
    await test_tfhub_model_tools()
    
    # 4. 기후 시각화 도구 테스트
    await test_climate_visualization_tools()
    
    # 5. 통합 시나리오 테스트
    await test_integration_scenarios()
    
    print("\n" + "=" * 60)
    print("🎉 모든 기후 예측 테스트 준비 완료!")
    print("\n📝 다음 단계:")
    print("1. pip install -r requirements.txt")
    print("2. python server.py (MCP 서버 실행)")
    print("3. MCP 클라이언트를 사용하여 기후 예측 기능 테스트")
    print("4. 생성된 시각화 파일 확인")

if __name__ == "__main__":
    asyncio.run(main())
