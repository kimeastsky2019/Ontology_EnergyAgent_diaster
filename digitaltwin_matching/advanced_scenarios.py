"""
스마트 그리드 디지털 트윈 - 고급 사용 예제 및 시나리오
"""

import numpy as np
from smart_grid_digital_twin import (
    SmartGridDigitalTwin, 
    Device, 
    PowerSupply,
    ESSSystem,
    DeviceType, 
    ControlMode, 
    EnergySource
)

# ==================== 시나리오 1: 극한 더위 날씨 ====================

def scenario_extreme_heat():
    """
    시나리오: 폭염 대응 전력 관리
    - 온도: 35~40°C
    - 에어컨 수요 폭증
    - 태양광 발전 최대
    """
    print("\n" + "="*80)
    print("📊 시나리오 1: 극한 더위 날씨 시뮬레이션")
    print("="*80)
    
    twin = SmartGridDigitalTwin()
    
    # 환경 설정 - 폭염
    def extreme_heat_environment(self, hour):
        # 매우 높은 온도
        self.environment.temperature = 35 + 5 * np.sin((hour - 12) * np.pi / 12)
        
        # 강한 일사량
        if 6 <= hour <= 19:
            self.environment.solar_radiation = 1000 * np.sin((hour - 6) * np.pi / 13)
        else:
            self.environment.solar_radiation = 0
        
        # 약한 바람
        self.environment.wind_speed = max(0, np.random.normal(2, 1))
        
        # 재실 인원
        if 9 <= hour <= 16:
            self.environment.occupancy = 600  # 피서 인원 증가
        else:
            self.environment.occupancy = 100
    
    # 환경 업데이트 함수 교체
    twin.update_environment = extreme_heat_environment.__get__(twin, SmartGridDigitalTwin)
    
    # 에어컨 우선순위 상향 (더위 대응)
    for device in twin.devices:
        if device.device_type == DeviceType.TEMPERATURE:
            device.priority = 1  # 최고 우선순위
            device.is_active = True
            device.current_power = device.power_rating
    
    # 시뮬레이션 실행
    results = twin.run_simulation(duration_hours=24, time_step_minutes=30)
    df = twin.generate_report()
    
    print("\n🎯 폭염 시나리오 결과:")
    print(f"  - 최고 온도: {df['온도'].max():.1f}°C")
    print(f"  - 최대 전력 수요: {df['전력수요'].max():.1f} kW")
    print(f"  - 평균 재생에너지 활용: {df['재생에너지비율'].mean():.1f}%")
    print(f"  - 전력 부족 발생 횟수: {(df['전력균형'] < 0).sum()}회")
    
    return twin, df

# ==================== 시나리오 2: 전력망 차단 ====================

def scenario_grid_outage():
    """
    시나리오: 전력망 차단 - 독립 운영
    - 전력망 사용 불가
    - 재생에너지 + ESS만으로 운영
    - 시스템 복원력 테스트
    """
    print("\n" + "="*80)
    print("⚡ 시나리오 2: 전력망 차단 시뮬레이션")
    print("="*80)
    
    twin = SmartGridDigitalTwin()
    
    # 전력망 제거
    twin.supplies = [s for s in twin.supplies if s.source_type != EnergySource.GRID]
    
    # ESS 용량 증대 (독립 운영 대비)
    twin.ess = ESSSystem(
        capacity=400.0,  # 200 → 400kWh
        current_soc=0.8,  # 80% 충전 상태
        max_charge_rate=100.0,  # 50 → 100kW
        max_discharge_rate=100.0
    )
    
    print("\n⚙️ 독립 운영 설정:")
    print(f"  - 전력망: 차단됨")
    print(f"  - ESS 용량: {twin.ess.capacity}kWh")
    print(f"  - ESS 초기 SOC: {twin.ess.current_soc*100}%")
    print(f"  - 태양광: {[s.capacity for s in twin.supplies if s.source_type == EnergySource.SOLAR][0]}kW")
    print(f"  - 풍력: {[s.capacity for s in twin.supplies if s.source_type == EnergySource.WIND][0]}kW")
    
    # 시뮬레이션 실행
    results = twin.run_simulation(duration_hours=24, time_step_minutes=30)
    df = twin.generate_report()
    
    print("\n🎯 전력망 차단 시나리오 결과:")
    print(f"  - 최저 ESS SOC: {df['ESS_SOC'].min():.1f}%")
    print(f"  - 전력 부족 발생: {(df['전력균형'] < -1).sum()}회")
    print(f"  - 평균 재생에너지 비율: {df['재생에너지비율'].mean():.1f}%")
    print(f"  - 시스템 복원력 점수: {df['안정성점수'].mean():.1f}/100")
    
    if df['ESS_SOC'].min() > 10:
        print("  ✅ 독립 운영 성공!")
    else:
        print("  ⚠️ ESS 용량 부족 - 증설 필요")
    
    return twin, df

# ==================== 시나리오 3: 야간 전력 수요 급증 ====================

def scenario_night_peak():
    """
    시나리오: 야간 특별 행사로 인한 전력 수요 급증
    - 재생에너지 발전 불가
    - ESS 의존도 극대화
    - 야간 수요 관리 전략 평가
    """
    print("\n" + "="*80)
    print("🌙 시나리오 3: 야간 전력 수요 급증 시뮬레이션")
    print("="*80)
    
    twin = SmartGridDigitalTwin()
    
    # 야간 행사 시나리오
    def night_event_simulation(self, hour):
        if 18 <= hour <= 22:  # 야간 행사 시간
            # 모든 디바이스 활성화
            for device in self.devices:
                if np.random.random() < 0.9:  # 90% 가동률
                    device.is_active = True
                    device.current_power = device.power_rating
        else:
            # 일반 패턴
            active_ratio = 0.3 if 9 <= hour <= 16 else 0.1
            for device in self.devices:
                if np.random.random() < 0.3:
                    device.is_active = np.random.random() < active_ratio
                    device.current_power = device.power_rating if device.is_active else 0
    
    twin.simulate_device_usage = night_event_simulation.__get__(twin, SmartGridDigitalTwin)
    
    # ESS를 만충전 상태로
    twin.ess.current_soc = 0.95
    
    print("\n⚙️ 야간 행사 설정:")
    print(f"  - 행사 시간: 18:00 ~ 22:00")
    print(f"  - 예상 디바이스 가동률: 90%")
    print(f"  - ESS 초기 SOC: {twin.ess.current_soc*100}%")
    
    # 시뮬레이션 실행
    results = twin.run_simulation(duration_hours=24, time_step_minutes=30)
    df = twin.generate_report()
    
    # 야간(18-22시) 데이터 필터링
    df['시간'] = [int(t.split()[1].split(':')[0]) for t in df['시각']]
    night_df = df[(df['시간'] >= 18) & (df['시간'] <= 22)]
    
    print("\n🎯 야간 행사 시나리오 결과:")
    print(f"  - 야간 평균 전력 수요: {night_df['전력수요'].mean():.1f} kW")
    print(f"  - 야간 최대 전력 수요: {night_df['전력수요'].max():.1f} kW")
    print(f"  - ESS 방전량: {(twin.ess.current_soc - df['ESS_SOC'].min()/100) * twin.ess.capacity:.1f} kWh")
    print(f"  - 전력망 의존도: {(night_df['전력공급'] - night_df['전력수요']).mean():.1f} kW")
    
    return twin, df

# ==================== 시나리오 4: 알고리즘 A/B 테스트 ====================

def scenario_algorithm_comparison():
    """
    시나리오: 두 가지 수요 반응 알고리즘 비교
    - 알고리즘 A: 우선순위 기반 (기본)
    - 알고리즘 B: 예측 기반 (개선)
    """
    print("\n" + "="*80)
    print("🔬 시나리오 4: 알고리즘 A/B 테스트")
    print("="*80)
    
    # 알고리즘 A (기본)
    print("\n[알고리즘 A 실행 중...]")
    twin_a = SmartGridDigitalTwin()
    results_a = twin_a.run_simulation(duration_hours=24, time_step_minutes=30)
    df_a = twin_a.generate_report()
    
    # 알고리즘 B (개선 - 예측 기반)
    print("\n[알고리즘 B 실행 중...]")
    twin_b = SmartGridDigitalTwin()
    
    # 예측 기반 제어 추가
    class PredictiveDRAgent(twin_b.dr_agent.__class__):
        def decide(self, state):
            # 기본 결정
            basic_decision = super().decide(state)
            
            # 예측 강화: 다음 시간대 수요 예측
            current_hour = state['current_time'].hour
            
            # 수업 시작 직전 (8시) 디바이스 미리 켜기
            if current_hour == 8:
                for device in state['devices']:
                    if not device.is_active and device.control_mode == ControlMode.CONTROLLABLE:
                        basic_decision['decisions'].append({
                            'device_id': device.device_id,
                            'action': 'turn_on',
                            'reason': 'predictive_pre-start'
                        })
            
            return basic_decision
    
    twin_b.dr_agent = PredictiveDRAgent()
    results_b = twin_b.run_simulation(duration_hours=24, time_step_minutes=30)
    df_b = twin_b.generate_report()
    
    # 결과 비교
    print("\n📊 알고리즘 비교 결과:")
    print("="*60)
    print(f"{'지표':<25} {'알고리즘 A':<15} {'알고리즘 B':<15} {'개선율':<10}")
    print("-"*60)
    
    metrics = {
        '평균 재생에너지 비율 (%)': ('재생에너지비율', True),
        '평균 안정성 점수': ('안정성점수', True),
        '평균 비용 효율성 (%)': ('비용효율성', True),
        '종합 점수': ('종합점수', True),
        '평균 전력 가격 (원/kWh)': ('가격', False)
    }
    
    for metric_name, (col, higher_better) in metrics.items():
        val_a = df_a[col].mean()
        val_b = df_b[col].mean()
        improvement = ((val_b - val_a) / val_a * 100) if higher_better else ((val_a - val_b) / val_a * 100)
        
        print(f"{metric_name:<25} {val_a:>13.2f}  {val_b:>13.2f}  {improvement:>8.1f}%")
    
    print("="*60)
    
    winner = "알고리즘 B" if df_b['종합점수'].mean() > df_a['종합점수'].mean() else "알고리즘 A"
    print(f"\n🏆 우수 알고리즘: {winner}")
    
    return twin_a, twin_b, df_a, df_b

# ==================== 시나리오 5: 재생에너지 용량 최적화 ====================

def scenario_capacity_optimization():
    """
    시나리오: 최적 재생에너지 용량 도출
    - 태양광 용량: 50, 100, 150, 200kW 비교
    - ROI 및 성능 분석
    """
    print("\n" + "="*80)
    print("📈 시나리오 5: 재생에너지 용량 최적화")
    print("="*80)
    
    capacities = [50, 100, 150, 200]
    results = []
    
    for capacity in capacities:
        print(f"\n[태양광 {capacity}kW 테스트 중...]")
        twin = SmartGridDigitalTwin()
        
        # 태양광 용량 변경
        for supply in twin.supplies:
            if supply.source_type == EnergySource.SOLAR:
                supply.capacity = capacity
        
        twin.run_simulation(duration_hours=24, time_step_minutes=60)
        df = twin.generate_report()
        
        results.append({
            'capacity': capacity,
            'renewable_ratio': df['재생에너지비율'].mean(),
            'stability': df['안정성점수'].mean(),
            'cost_efficiency': df['비용효율성'].mean(),
            'overall_score': df['종합점수'].mean(),
            'avg_price': df['가격'].mean()
        })
    
    print("\n📊 용량별 성능 비교:")
    print("="*80)
    print(f"{'용량(kW)':<12} {'재생에너지(%)':<15} {'안정성':<12} {'비용효율(%)':<15} {'종합점수':<12}")
    print("-"*80)
    
    for r in results:
        print(f"{r['capacity']:<12} {r['renewable_ratio']:>13.1f}  {r['stability']:>10.1f}  "
              f"{r['cost_efficiency']:>13.1f}  {r['overall_score']:>10.1f}")
    
    # 최적 용량 선정
    optimal = max(results, key=lambda x: x['overall_score'])
    print(f"\n🎯 최적 용량: {optimal['capacity']}kW")
    print(f"   - 종합 점수: {optimal['overall_score']:.1f}")
    print(f"   - 재생에너지 비율: {optimal['renewable_ratio']:.1f}%")
    
    return results

# ==================== 메인 실행 ====================

def main():
    """모든 시나리오 실행"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     스마트 그리드 디지털 트윈 - 고급 시나리오 테스트         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    scenarios = [
        ("1. 극한 더위 날씨", scenario_extreme_heat),
        ("2. 전력망 차단", scenario_grid_outage),
        ("3. 야간 전력 수요 급증", scenario_night_peak),
        ("4. 알고리즘 A/B 테스트", scenario_algorithm_comparison),
        ("5. 재생에너지 용량 최적화", scenario_capacity_optimization)
    ]
    
    print("\n실행할 시나리오를 선택하세요:")
    for i, (name, _) in enumerate(scenarios, 1):
        print(f"  {name}")
    print("  6. 모든 시나리오 실행")
    print("  0. 종료")
    
    try:
        choice = input("\n선택 (0-6): ").strip()
        
        if choice == '0':
            print("\n프로그램을 종료합니다.")
            return
        elif choice == '6':
            print("\n모든 시나리오를 순차적으로 실행합니다...\n")
            for name, scenario_func in scenarios:
                scenario_func()
                input("\n다음 시나리오로 진행하려면 Enter를 누르세요...")
        elif 1 <= int(choice) <= 5:
            scenarios[int(choice)-1][1]()
        else:
            print("잘못된 선택입니다.")
    
    except (ValueError, KeyboardInterrupt):
        print("\n\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
