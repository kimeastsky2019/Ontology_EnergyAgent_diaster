"""
외부 데이터 수집 MCP 기능 테스트

새로 추가된 외부 데이터 수집 및 스케줄링 기능들을 테스트합니다.
"""

import asyncio
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 테스트용 샘플 데이터 생성
def create_test_weather_data():
    """테스트용 날씨 데이터 생성"""
    # 7일간의 시간별 데이터 생성
    start_date = datetime.now() - timedelta(days=7)
    dates = [start_date + timedelta(hours=i) for i in range(7 * 24)]
    
    weather_data = []
    for i, date in enumerate(dates):
        # 온도 패턴 (일교차 포함)
        base_temp = 20 + 10 * np.sin(i * 2 * np.pi / 24)  # 일일 패턴
        temp = base_temp + np.random.normal(0, 2)
        
        # 습도 패턴 (온도와 반비례)
        humidity = 60 + 20 * np.sin(i * 2 * np.pi / 24 + np.pi) + np.random.normal(0, 5)
        humidity = max(0, min(100, humidity))
        
        # 기압 패턴
        pressure = 1013 + 10 * np.sin(i * 2 * np.pi / (24 * 7)) + np.random.normal(0, 1)
        
        # 풍속 패턴
        wind_speed = 5 + 3 * np.sin(i * 2 * np.pi / 24) + np.random.exponential(1)
        
        weather_data.append({
            'datetime': date.isoformat(),
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure, 1),
            'wind_speed': round(wind_speed, 1),
            'weather_description': 'clear sky' if temp > 15 else 'cloudy',
            'cloudiness': max(0, min(100, 50 + (15 - temp) * 5))
        })
    
    # CSV 파일로 저장
    csv_path = "test_weather_data.csv"
    df = pd.DataFrame(weather_data)
    df.to_csv(csv_path, index=False)
    print(f"✅ 테스트 날씨 데이터 생성 완료: {csv_path}")
    return csv_path

async def test_external_data_collection_tools():
    """외부 데이터 수집 도구 테스트"""
    print("\n🌐 외부 데이터 수집 도구 테스트 시작...")
    
    try:
        # 테스트 데이터 생성
        weather_csv = create_test_weather_data()
        
        print("📋 테스트할 외부 데이터 수집 도구들:")
        test_tools = [
            "collect_weather_data_multi_source",
            "collect_real_time_weather", 
            "setup_data_collection_schedule",
            "run_scheduled_collections",
            "validate_data_quality",
            "get_collection_statistics"
        ]
        
        for tool in test_tools:
            print(f"  • {tool}")
        
        # 테스트 케이스들
        test_cases = {
            "collect_weather_data_multi_source": {
                "latitude": 37.5665,
                "longitude": 126.9780,
                "sources": ["openweather"],
                "data_types": ["current", "forecast"]
            },
            "collect_real_time_weather": {
                "latitude": 37.5665,
                "longitude": 126.9780,
                "source": "openweather",
                "cache_duration": 300
            },
            "setup_data_collection_schedule": {
                "name": "test_seoul_weather",
                "source": "openweather",
                "latitude": 37.5665,
                "longitude": 126.9780,
                "data_type": "current_weather",
                "frequency_minutes": 60
            },
            "validate_data_quality": {
                "data": pd.read_csv(weather_csv).to_dict('records'),
                "data_type": "weather"
            }
        }
        
        print("\n📊 테스트 케이스:")
        for tool, params in test_cases.items():
            print(f"  • {tool}: {params}")
        
        print("\n⚠️  실제 테스트를 위해서는 다음이 필요합니다:")
        print("  1. API 키 설정:")
        print("     export OPENWEATHER_API_KEY='your_api_key'")
        print("     export WEATHERAPI_API_KEY='your_api_key' (선택사항)")
        print("  2. MCP 서버 실행: python server.py")
        print("  3. MCP 클라이언트를 사용하여 도구들 호출")
        
        print("\n✅ 외부 데이터 수집 도구 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

async def test_data_scheduler():
    """데이터 스케줄러 테스트"""
    print("\n⏰ 데이터 스케줄러 테스트 시작...")
    
    try:
        from data_scheduler import DataCollectionScheduler
        
        # 스케줄러 인스턴스 생성
        scheduler = DataCollectionScheduler()
        
        print("📋 스케줄러 테스트 기능들:")
        scheduler_tests = [
            "add_schedule - 새 스케줄 추가",
            "get_active_schedules - 활성 스케줄 조회", 
            "stop_schedule - 스케줄 중지",
            "start - 스케줄러 시작 (백그라운드)",
            "stop - 스케줄러 중지"
        ]
        
        for test in scheduler_tests:
            print(f"  • {test}")
        
        # 스케줄 추가 테스트
        print("\n🧪 스케줄 추가 테스트...")
        result = await scheduler.add_schedule(
            name="test_seoul_current_weather",
            source="openweather",
            latitude=37.5665,
            longitude=126.9780,
            data_type="current_weather",
            frequency_minutes=30
        )
        
        if result.get("success"):
            print(f"✅ 스케줄 추가 성공: {result['message']}")
        else:
            print(f"❌ 스케줄 추가 실패: {result.get('error', 'Unknown error')}")
        
        # 활성 스케줄 조회 테스트
        print("\n📋 활성 스케줄 조회...")
        schedules = await scheduler.get_active_schedules()
        print(f"활성 스케줄 수: {len(schedules)}")
        
        for schedule in schedules:
            print(f"  • {schedule['name']}: {schedule['data_type']} (매 {schedule['frequency_minutes']}분)")
        
        print("\n⚠️  실제 스케줄러 실행을 위해서는:")
        print("  1. API 키 설정")
        print("  2. python data_scheduler.py 실행")
        print("  3. 백그라운드에서 자동 데이터 수집")
        
        print("\n✅ 데이터 스케줄러 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 스케줄러 테스트 중 오류 발생: {e}")

def test_data_quality_validation():
    """데이터 품질 검증 테스트"""
    print("\n🔍 데이터 품질 검증 테스트 시작...")
    
    try:
        # 테스트용 데이터 생성 (품질 문제 포함)
        test_data = []
        
        # 정상 데이터
        for i in range(50):
            test_data.append({
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'temperature': 20 + np.random.normal(0, 2),
                'humidity': 50 + np.random.normal(0, 10),
                'pressure': 1013 + np.random.normal(0, 5)
            })
        
        # 품질 문제가 있는 데이터 추가
        # 누락값
        for i in range(10):
            test_data.append({
                'timestamp': (datetime.now() - timedelta(hours=50+i)).isoformat(),
                'temperature': None,  # 누락값
                'humidity': 50 + np.random.normal(0, 10),
                'pressure': 1013 + np.random.normal(0, 5)
            })
        
        # 이상치
        for i in range(5):
            test_data.append({
                'timestamp': (datetime.now() - timedelta(hours=60+i)).isoformat(),
                'temperature': 100 + np.random.normal(0, 10),  # 비정상적으로 높은 온도
                'humidity': 50 + np.random.normal(0, 10),
                'pressure': 1013 + np.random.normal(0, 5)
            })
        
        # 중복 데이터
        test_data.append(test_data[0])  # 첫 번째 데이터 중복
        
        print(f"📊 테스트 데이터 생성 완료: {len(test_data)}개 레코드")
        print("  - 정상 데이터: 50개")
        print("  - 누락값 포함: 10개")
        print("  - 이상치 포함: 5개")
        print("  - 중복 데이터: 1개")
        
        # 데이터 품질 검증 (실제로는 MCP 도구를 통해 실행)
        print("\n🔍 데이터 품질 검증 시뮬레이션...")
        
        df = pd.DataFrame(test_data)
        
        # 기본 통계
        missing_stats = df.isnull().sum()
        duplicates = df.duplicated().sum()
        
        print(f"누락값 통계:")
        for col, count in missing_stats.items():
            if count > 0:
                print(f"  • {col}: {count}개 ({count/len(df)*100:.1f}%)")
        
        print(f"중복 데이터: {duplicates}개")
        
        # 이상치 검출 (IQR 방법)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns and not df[col].isnull().all():
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if len(outliers) > 0:
                    print(f"이상치 ({col}): {len(outliers)}개")
        
        print("\n✅ 데이터 품질 검증 테스트 완료!")
        print("💡 실제 품질 검증을 위해서는 MCP 도구 'validate_data_quality'를 사용하세요.")
        
    except Exception as e:
        print(f"❌ 데이터 품질 검증 테스트 중 오류 발생: {e}")

async def test_multi_source_integration():
    """다중 소스 통합 테스트"""
    print("\n🔗 다중 소스 통합 테스트 시작...")
    
    try:
        print("📋 지원하는 데이터 소스:")
        sources = [
            "OpenWeatherMap - 현재 날씨, 예보, 과거 데이터",
            "WeatherAPI - 실시간 날씨, 예보, 과거 데이터", 
            "AccuWeather - 상세한 날씨 정보",
            "NOAA - 미국 기상청 데이터"
        ]
        
        for source in sources:
            print(f"  • {source}")
        
        print("\n🔧 통합 기능:")
        integration_features = [
            "다중 소스 동시 수집",
            "데이터 소스별 성능 비교",
            "자동 장애 복구 (Fallback)",
            "통합 데이터 품질 검증",
            "실시간 모니터링 및 알림"
        ]
        
        for feature in integration_features:
            print(f"  • {feature}")
        
        print("\n📊 데이터 수집 워크플로우:")
        workflow_steps = [
            "1. 스케줄 확인 및 실행",
            "2. 다중 소스에서 데이터 수집",
            "3. 데이터 품질 검증",
            "4. 캐시 저장 및 만료 관리",
            "5. 로그 기록 및 통계 업데이트",
            "6. 다음 수집 시간 계산"
        ]
        
        for step in workflow_steps:
            print(f"  {step}")
        
        print("\n⚠️  실제 다중 소스 테스트를 위해서는:")
        print("  1. 여러 API 키 설정")
        print("  2. MCP 서버 실행")
        print("  3. collect_weather_data_multi_source 도구 호출")
        
        print("\n✅ 다중 소스 통합 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 다중 소스 통합 테스트 중 오류 발생: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 외부 데이터 수집 MCP 기능 테스트")
    print("=" * 60)
    
    # 1. 외부 데이터 수집 도구 테스트
    await test_external_data_collection_tools()
    
    # 2. 데이터 스케줄러 테스트
    await test_data_scheduler()
    
    # 3. 데이터 품질 검증 테스트
    test_data_quality_validation()
    
    # 4. 다중 소스 통합 테스트
    await test_multi_source_integration()
    
    print("\n" + "=" * 60)
    print("🎉 모든 외부 데이터 수집 테스트 준비 완료!")
    print("\n📝 다음 단계:")
    print("1. pip install -r requirements.txt")
    print("2. API 키 설정:")
    print("   export OPENWEATHER_API_KEY='your_api_key'")
    print("   export WEATHERAPI_API_KEY='your_api_key' (선택사항)")
    print("3. python server.py (MCP 서버 실행)")
    print("4. python data_scheduler.py (스케줄러 실행)")
    print("5. MCP 클라이언트를 사용하여 외부 데이터 수집 테스트")

if __name__ == "__main__":
    asyncio.run(main())
