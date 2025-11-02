"""
업그레이드된 에너지 분석 MCP 기능 테스트

새로 추가된 LangGraph Agent 및 간소화된 분석 도구들을 테스트합니다.
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 테스트용 샘플 데이터 생성
def create_sample_energy_data():
    """테스트용 에너지 데이터 생성"""
    # 30일간의 시간별 데이터 생성
    start_date = datetime.now() - timedelta(days=30)
    dates = [start_date + timedelta(hours=i) for i in range(30 * 24)]
    
    # 에너지 소비량 데이터 (시간대별 패턴 포함)
    consumption = []
    for i, date in enumerate(dates):
        # 기본 소비량
        base_consumption = 100
        
        # 시간대별 패턴 (새벽 3-5시 최소, 오후 2-4시 최대)
        hour = date.hour
        if 3 <= hour <= 5:
            hour_factor = 0.3
        elif 14 <= hour <= 16:
            hour_factor = 1.8
        elif 8 <= hour <= 18:
            hour_factor = 1.2
        else:
            hour_factor = 0.8
        
        # 요일별 패턴 (주말 감소)
        weekday_factor = 0.7 if date.weekday() >= 5 else 1.0
        
        # 온도 영향 (더운 날과 추운 날 에너지 소비 증가)
        temperature = 20 + 10 * np.sin(i * 2 * np.pi / (24 * 7)) + np.random.normal(0, 2)
        temp_factor = 1 + 0.01 * abs(temperature - 20)
        
        # 랜덤 노이즈
        noise = np.random.normal(0, 0.1)
        
        consumption_value = base_consumption * hour_factor * weekday_factor * temp_factor * (1 + noise)
        consumption.append(max(0, consumption_value))
    
    # 데이터프레임 생성
    df = pd.DataFrame({
        'datetime': dates,
        'consumption': consumption,
        'temperature': [20 + 10 * np.sin(i * 2 * np.pi / (24 * 7)) + np.random.normal(0, 2) for i in range(len(dates))],
        'humidity': [50 + 20 * np.sin(i * 2 * np.pi / (24 * 7)) + np.random.normal(0, 5) for i in range(len(dates))],
        'hour': [d.hour for d in dates],
        'day_of_week': [d.weekday() for d in dates],
        'is_weekend': [d.weekday() >= 5 for d in dates]
    })
    
    # CSV 파일로 저장
    csv_path = "test_energy_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ 테스트 데이터 생성 완료: {csv_path}")
    return csv_path

async def test_simple_analysis_tools():
    """간소화된 분석 도구 테스트"""
    print("\n🔍 간소화된 분석 도구 테스트 시작...")
    
    # 테스트 데이터 생성
    csv_path = create_sample_energy_data()
    
    try:
        # MCP 서버와 연결 (실제로는 별도 프로세스에서 실행되어야 함)
        print("⚠️  실제 테스트를 위해서는 MCP 서버가 별도로 실행되어야 합니다.")
        print("   다음 명령어로 서버를 실행하세요: python server.py")
        print("   그 다음 다른 터미널에서 이 테스트를 실행하세요.")
        
        # 테스트할 도구들 목록
        test_tools = [
            "describe_energy_column",
            "plot_energy_distribution", 
            "train_energy_model",
            "analyze_energy_correlation",
            "get_energy_data_info"
        ]
        
        print(f"\n📋 테스트할 도구들: {', '.join(test_tools)}")
        print(f"📁 테스트 데이터: {csv_path}")
        
        # 각 도구별 테스트 케이스
        test_cases = {
            "describe_energy_column": {
                "csv_path": csv_path,
                "column": "consumption"
            },
            "plot_energy_distribution": {
                "csv_path": csv_path,
                "column": "consumption",
                "chart_type": "histogram"
            },
            "train_energy_model": {
                "csv_path": csv_path,
                "x_columns": ["temperature", "humidity", "hour"],
                "y_column": "consumption"
            },
            "analyze_energy_correlation": {
                "csv_path": csv_path,
                "columns": ["consumption", "temperature", "humidity", "hour"]
            },
            "get_energy_data_info": {
                "csv_path": csv_path
            }
        }
        
        print("\n📊 테스트 케이스:")
        for tool, params in test_cases.items():
            print(f"  • {tool}: {params}")
        
        print("\n✅ 테스트 준비 완료!")
        print("   실제 테스트를 위해서는 MCP 클라이언트를 사용하여 도구들을 호출하세요.")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

async def test_langgraph_agent():
    """LangGraph Agent 테스트"""
    print("\n🤖 LangGraph Agent 테스트 시작...")
    
    try:
        # 에이전트 클라이언트 테스트
        print("📋 에이전트 테스트 케이스:")
        
        test_queries = [
            "test_energy_data.csv 파일의 consumption 컬럼 통계를 분석해주세요",
            "에너지 소비 패턴을 시각화해주세요",
            "temperature와 consumption의 상관관계를 분석해주세요",
            "consumption을 예측하는 모델을 만들어주세요",
            "주말과 평일의 에너지 소비 차이를 분석해주세요"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"  {i}. {query}")
        
        print("\n⚠️  실제 테스트를 위해서는 다음을 실행하세요:")
        print("   1. python server.py (MCP 서버 실행)")
        print("   2. python energy_agent_client.py (에이전트 실행)")
        print("   3. 위의 질문들을 에이전트에게 입력")
        
        print("\n✅ 에이전트 테스트 준비 완료!")
        
    except Exception as e:
        print(f"❌ 에이전트 테스트 중 오류 발생: {e}")

def test_prompt_system():
    """프롬프트 시스템 테스트"""
    print("\n💬 프롬프트 시스템 테스트 시작...")
    
    try:
        from tools.prompt_tools import PromptTools
        from fastmcp import FastMCP
        
        # FastMCP 인스턴스 생성
        mcp = FastMCP("TestPrompt")
        prompt_tools = PromptTools(mcp)
        
        # 프롬프트 타입들
        prompt_types = [
            "energy_analysis_prompt",
            "data_visualization_prompt", 
            "model_training_prompt",
            "energy_insights_prompt",
            "general_analysis_prompt"
        ]
        
        print("📋 사용 가능한 프롬프트 타입:")
        for prompt_type in prompt_types:
            print(f"  • {prompt_type}")
        
        # 각 프롬프트 타입별 테스트
        test_message = "에너지 데이터를 분석해주세요"
        
        print(f"\n🧪 테스트 메시지: '{test_message}'")
        print("\n📊 프롬프트 응답:")
        
        for prompt_type in prompt_types:
            try:
                # 프롬프트 함수 가져오기
                prompt_func = getattr(prompt_tools, prompt_type)
                messages = prompt_func(test_message)
                
                print(f"\n  {prompt_type}:")
                for msg in messages:
                    print(f"    {type(msg).__name__}: {msg.content[:100]}...")
                    
            except Exception as e:
                print(f"    ❌ {prompt_type}: {e}")
        
        print("\n✅ 프롬프트 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 프롬프트 시스템 테스트 중 오류 발생: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 업그레이드된 에너지 분석 MCP 기능 테스트")
    print("=" * 60)
    
    # 1. 간소화된 분석 도구 테스트
    await test_simple_analysis_tools()
    
    # 2. LangGraph Agent 테스트
    await test_langgraph_agent()
    
    # 3. 프롬프트 시스템 테스트
    test_prompt_system()
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 준비 완료!")
    print("\n📝 다음 단계:")
    print("1. pip install -r requirements.txt")
    print("2. export OPENAI_API_KEY='your_api_key'")
    print("3. python server.py")
    print("4. python energy_agent_client.py")
    print("5. 테스트 질문들을 에이전트에게 입력")

if __name__ == "__main__":
    asyncio.run(main())
