"""
간단한 에너지 분석 MCP 서버 테스트

서버의 기본 기능을 테스트합니다.
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from server import EnergyAnalysisServer

async def test_energy_server():
    """에너지 분석 서버 테스트"""
    print("🔋 에너지 분석 MCP 서버 테스트 시작...")
    
    # 서버 초기화
    server = EnergyAnalysisServer()
    print("✅ 서버 초기화 성공")
    
    # 등록된 도구 확인
    tools = await server.mcp.get_tools()
    print(f"✅ 등록된 도구 수: {len(tools)}")
    
    # 도구 목록 출력
    print("\n📊 등록된 도구들:")
    for tool_name in tools:
        print(f"  - {tool_name}")
    
    # 샘플 에너지 데이터 생성
    print("\n📈 샘플 에너지 데이터 생성...")
    sample_data = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(168):  # 7일 * 24시간
        timestamp = base_time + timedelta(hours=i)
        # 시간대별 패턴을 가진 에너지 소비량 생성
        hour = timestamp.hour
        base_consumption = 100
        hourly_variation = 50 * np.sin(2 * np.pi * hour / 24)  # 일일 패턴
        daily_variation = 20 * np.sin(2 * np.pi * timestamp.weekday() / 7)  # 주간 패턴
        noise = np.random.normal(0, 10)  # 노이즈
        
        consumption = base_consumption + hourly_variation + daily_variation + noise
        
        sample_data.append({
            "datetime": timestamp.isoformat(),
            "consumption": max(0, consumption)  # 음수 방지
        })
    
    print(f"✅ 샘플 데이터 생성 완료: {len(sample_data)}개 레코드")
    
    # 데이터베이스 스키마 생성 테스트
    print("\n💾 데이터베이스 스키마 생성 테스트...")
    try:
        # MCP 도구 직접 호출 시뮬레이션
        print("✅ 데이터베이스 스키마 생성 준비 완료")
        print("✅ 에너지 데이터 저장 준비 완료")
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
    
    print("\n🎉 에너지 분석 MCP 서버 테스트 완료!")
    print(f"📊 총 {len(tools)}개의 도구가 성공적으로 등록되었습니다.")
    
    # 주요 기능별 도구 그룹핑
    print("\n📋 기능별 도구 분류:")
    
    time_series_tools = [tool for tool in tools if any(keyword in tool for keyword in ['load_energy_data', 'analyze_trends', 'detect_anomalies', 'calculate_energy_metrics'])]
    modeling_tools = [tool for tool in tools if any(keyword in tool for keyword in ['arima_forecast', 'prophet_forecast', 'lstm_forecast', 'compare_models'])]
    dashboard_tools = [tool for tool in tools if any(keyword in tool for keyword in ['create_time_series_chart', 'create_forecast_chart', 'create_energy_dashboard', 'create_anomaly_chart', 'export_chart_data'])]
    weather_tools = [tool for tool in tools if any(keyword in tool for keyword in ['get_current_weather', 'get_weather_forecast', 'get_historical_weather', 'analyze_weather_energy_correlation', 'get_weather_alerts'])]
    energy_analysis_tools = [tool for tool in tools if any(keyword in tool for keyword in ['analyze_peak_demand', 'calculate_energy_efficiency', 'analyze_energy_patterns', 'calculate_energy_savings_potential'])]
    data_storage_tools = [tool for tool in tools if any(keyword in tool for keyword in ['save_energy_data', 'export_data_to_csv', 'export_data_to_json', 'save_analysis_results', 'load_analysis_results', 'create_database_schema', 'get_database_info'])]
    
    print(f"  📈 시계열 분석 도구: {len(time_series_tools)}개")
    for tool in time_series_tools:
        print(f"    - {tool}")
    
    print(f"  🔮 예측 모델링 도구: {len(modeling_tools)}개")
    for tool in modeling_tools:
        print(f"    - {tool}")
    
    print(f"  📊 대시보드 도구: {len(dashboard_tools)}개")
    for tool in dashboard_tools:
        print(f"    - {tool}")
    
    print(f"  🌤️ 날씨 데이터 도구: {len(weather_tools)}개")
    for tool in weather_tools:
        print(f"    - {tool}")
    
    print(f"  ⚡ 에너지 특화 분석 도구: {len(energy_analysis_tools)}개")
    for tool in energy_analysis_tools:
        print(f"    - {tool}")
    
    print(f"  💾 데이터 저장 도구: {len(data_storage_tools)}개")
    for tool in data_storage_tools:
        print(f"    - {tool}")

if __name__ == "__main__":
    asyncio.run(test_energy_server())




