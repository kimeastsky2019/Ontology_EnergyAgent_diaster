"""
Smart Grid Digital Twin Service with AI Agent
수요-공급 에너지 매칭 및 제어 알고리즘 평가 시뮬레이션 플랫폼
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum
import json

# ==================== 데이터 모델 정의 ====================

class DeviceType(Enum):
    """제어 가능한 디바이스 타입"""
    TEMPERATURE = "온도조절"
    LIGHT = "조명"
    FAN = "환풍기"
    COPY_MACHINE = "복사기"
    MICROWAVE = "전자레인지"
    TV = "TV"

class ControlMode(Enum):
    """제어 모드"""
    CONTROLLABLE = "제어가능"
    SELECTABLE = "선택제어"
    NOT_CONTROLLABLE = "제어불가"

class EnergySource(Enum):
    """에너지 공급원"""
    SOLAR = "태양광"
    WIND = "풍력"
    ESS = "ESS"
    GRID = "전력망"

@dataclass
class Device:
    """수요 측 디바이스"""
    device_id: str
    device_type: DeviceType
    control_mode: ControlMode
    power_rating: float  # kW
    current_power: float = 0.0
    is_active: bool = False
    priority: int = 5  # 1(높음) ~ 10(낮음)
    flexibility: float = 0.5  # 0~1, 제어 유연성
    
    def get_power_consumption(self) -> float:
        """현재 전력 소비량 반환"""
        return self.current_power if self.is_active else 0.0

@dataclass
class PowerSupply:
    """공급 측 전력원"""
    source_id: str
    source_type: EnergySource
    capacity: float  # kW
    current_output: float = 0.0
    efficiency: float = 0.95
    cost_per_kwh: float = 0.0
    
    def get_available_power(self) -> float:
        """사용 가능한 전력량"""
        return min(self.current_output, self.capacity) * self.efficiency

@dataclass
class EnvironmentalSensor:
    """환경 센서 데이터"""
    temperature: float = 25.0  # °C
    humidity: float = 50.0  # %
    solar_radiation: float = 0.0  # W/m²
    wind_speed: float = 0.0  # m/s
    occupancy: int = 0  # 재실 인원

@dataclass
class ESSSystem:
    """에너지 저장 시스템"""
    capacity: float  # kWh
    current_soc: float = 0.5  # State of Charge (0~1)
    max_charge_rate: float = 50.0  # kW
    max_discharge_rate: float = 50.0  # kW
    efficiency: float = 0.9
    
    def charge(self, power: float, duration_hours: float) -> float:
        """충전, 실제 충전된 에너지 반환"""
        actual_power = min(power, self.max_charge_rate)
        energy = actual_power * duration_hours * self.efficiency
        new_soc = self.current_soc + (energy / self.capacity)
        self.current_soc = min(new_soc, 1.0)
        return actual_power
    
    def discharge(self, power: float, duration_hours: float) -> float:
        """방전, 실제 방전된 에너지 반환"""
        actual_power = min(power, self.max_discharge_rate)
        energy = actual_power * duration_hours
        new_soc = self.current_soc - (energy / (self.capacity * self.efficiency))
        self.current_soc = max(new_soc, 0.0)
        return actual_power if new_soc >= 0 else 0.0

# ==================== AI 에이전트 ====================

class AIAgent:
    """에너지 제어를 위한 AI 에이전트 기반 클래스"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.learning_rate = 0.01
        self.state_history = []
        
    def decide(self, state: Dict) -> Dict:
        """상태 기반 결정 (하위 클래스에서 구현)"""
        raise NotImplementedError
    
    def learn(self, state: Dict, action: Dict, reward: float):
        """학습 (강화학습 기반)"""
        self.state_history.append({
            'state': state,
            'action': action,
            'reward': reward,
            'timestamp': datetime.now()
        })

class DemandResponseAgent(AIAgent):
    """수요 반응 AI 에이전트"""
    
    def __init__(self):
        super().__init__("DR_Agent", "수요반응 최적화 에이전트")
        self.priority_weights = {
            1: 1.0, 2: 0.9, 3: 0.8, 4: 0.7, 5: 0.6,
            6: 0.5, 7: 0.4, 8: 0.3, 9: 0.2, 10: 0.1
        }
    
    def decide(self, state: Dict) -> Dict:
        """
        수요 측 제어 결정
        - 전력 부족 시: 우선순위 낮은 기기부터 차단
        - 전력 잉여 시: 우선순위 높은 기기부터 활성화
        """
        total_demand = state.get('total_demand', 0)
        total_supply = state.get('total_supply', 0)
        devices = state.get('devices', [])
        
        power_gap = total_supply - total_demand
        
        decisions = []
        
        if power_gap < 0:  # 전력 부족
            # 우선순위 낮은 것부터 차단
            sorted_devices = sorted(
                [(d, d.priority) for d in devices if d.is_active],
                key=lambda x: x[1],
                reverse=True
            )
            
            reduced_power = 0
            for device, _ in sorted_devices:
                if reduced_power >= abs(power_gap):
                    break
                if device.control_mode != ControlMode.NOT_CONTROLLABLE:
                    decisions.append({
                        'device_id': device.device_id,
                        'action': 'turn_off',
                        'reason': 'power_shortage'
                    })
                    reduced_power += device.current_power
        
        elif power_gap > 50:  # 전력 잉여 (50kW 이상)
            # 우선순위 높은 것부터 활성화
            sorted_devices = sorted(
                [(d, d.priority) for d in devices if not d.is_active],
                key=lambda x: x[1]
            )
            
            used_power = 0
            for device, _ in sorted_devices:
                if used_power >= power_gap:
                    break
                if device.control_mode == ControlMode.CONTROLLABLE:
                    decisions.append({
                        'device_id': device.device_id,
                        'action': 'turn_on',
                        'reason': 'power_surplus'
                    })
                    used_power += device.power_rating
        
        return {
            'agent': self.name,
            'decisions': decisions,
            'power_gap': power_gap
        }

class SupplyOptimizationAgent(AIAgent):
    """공급 최적화 AI 에이전트"""
    
    def __init__(self):
        super().__init__("SO_Agent", "공급 최적화 에이전트")
    
    def decide(self, state: Dict) -> Dict:
        """
        공급 측 최적화 결정
        - 재생에너지 우선 사용
        - ESS 충방전 전략
        - 비용 최소화
        """
        total_demand = state.get('total_demand', 0)
        supplies = state.get('supplies', [])
        ess = state.get('ess')
        env = state.get('environment')
        
        # 재생에너지 예측
        solar_potential = self._predict_solar(env)
        wind_potential = self._predict_wind(env)
        
        # 공급 우선순위: 태양광 > 풍력 > ESS방전 > 전력망
        supply_plan = []
        remaining_demand = total_demand
        
        # 1. 재생에너지 활용
        for supply in supplies:
            if supply.source_type == EnergySource.SOLAR:
                output = min(solar_potential, remaining_demand)
                supply_plan.append({
                    'source_id': supply.source_id,
                    'output': output,
                    'cost': 0
                })
                remaining_demand -= output
            elif supply.source_type == EnergySource.WIND:
                output = min(wind_potential, remaining_demand)
                supply_plan.append({
                    'source_id': supply.source_id,
                    'output': output,
                    'cost': 0
                })
                remaining_demand -= output
        
        # 2. ESS 활용 결정
        if ess:
            renewable_surplus = (solar_potential + wind_potential) - total_demand
            
            if renewable_surplus > 0 and ess.current_soc < 0.9:
                # 잉여 재생에너지 저장
                supply_plan.append({
                    'ess_action': 'charge',
                    'power': renewable_surplus,
                    'reason': 'store_renewable'
                })
            elif remaining_demand > 0 and ess.current_soc > 0.2:
                # ESS 방전
                discharge_power = min(remaining_demand, ess.max_discharge_rate)
                supply_plan.append({
                    'ess_action': 'discharge',
                    'power': discharge_power,
                    'reason': 'meet_demand'
                })
                remaining_demand -= discharge_power
        
        # 3. 전력망 사용 (최후 수단)
        if remaining_demand > 0:
            supply_plan.append({
                'source_id': 'grid',
                'output': remaining_demand,
                'cost': remaining_demand * 150  # 원/kWh
            })
        
        return {
            'agent': self.name,
            'supply_plan': supply_plan,
            'renewable_ratio': (solar_potential + wind_potential) / max(total_demand, 1)
        }
    
    def _predict_solar(self, env: EnvironmentalSensor) -> float:
        """태양광 발전량 예측"""
        # 간단한 모델: 일사량 기반
        if env.solar_radiation > 0:
            return (env.solar_radiation / 1000) * 100 * 0.2  # 100kW 용량, 20% 효율
        return 0.0
    
    def _predict_wind(self, env: EnvironmentalSensor) -> float:
        """풍력 발전량 예측"""
        # 간단한 모델: 풍속 기반
        if env.wind_speed > 3:  # 최소 풍속 3m/s
            return min((env.wind_speed ** 3) / 100, 50)  # 최대 50kW
        return 0.0

class PricingAgent(AIAgent):
    """가격 결정 AI 에이전트 (MCP)"""
    
    def __init__(self):
        super().__init__("Price_Agent", "가격 결정 에이전트")
        self.base_price = 100  # 기본 가격 (원/kWh)
    
    def decide(self, state: Dict) -> Dict:
        """
        동적 가격 결정
        - 수요/공급 비율 기반
        - 피크 시간대 고려
        - 재생에너지 비율 고려
        """
        total_demand = state.get('total_demand', 0)
        total_supply = state.get('total_supply', 0)
        renewable_ratio = state.get('renewable_ratio', 0)
        current_time = state.get('current_time', datetime.now())
        
        # 수급 균형 계수
        supply_demand_ratio = total_supply / max(total_demand, 1)
        
        # 시간대 계수 (피크: 09-12, 18-21)
        hour = current_time.hour
        time_coefficient = 1.5 if (9 <= hour <= 12 or 18 <= hour <= 21) else 1.0
        
        # 재생에너지 할인
        renewable_discount = 0.8 if renewable_ratio > 0.5 else 1.0
        
        # 최종 가격 계산
        if supply_demand_ratio > 1.2:  # 공급 과잉
            price = self.base_price * 0.7 * renewable_discount
        elif supply_demand_ratio < 0.8:  # 공급 부족
            price = self.base_price * 1.5 * time_coefficient
        else:
            price = self.base_price * time_coefficient * renewable_discount
        
        return {
            'agent': self.name,
            'price_kwh': round(price, 2),
            'supply_demand_ratio': supply_demand_ratio,
            'time_coefficient': time_coefficient,
            'renewable_discount': renewable_discount
        }

# ==================== 디지털 트윈 시뮬레이터 ====================

class SmartGridDigitalTwin:
    """스마트 그리드 디지털 트윈 시뮬레이터"""
    
    def __init__(self):
        self.devices: List[Device] = []
        self.supplies: List[PowerSupply] = []
        self.ess: ESSSystem = None
        self.environment = EnvironmentalSensor()
        
        # AI 에이전트들
        self.dr_agent = DemandResponseAgent()
        self.so_agent = SupplyOptimizationAgent()
        self.price_agent = PricingAgent()
        
        # 시뮬레이션 상태
        self.current_time = datetime.now()
        self.simulation_log = []
        
        self._initialize_system()
    
    def _initialize_system(self):
        """시스템 초기화 - 학교 건물 모델"""
        
        # 수요 측 디바이스 (학교 건물 기준)
        # 교실 20개
        for i in range(20):
            self.devices.append(Device(
                device_id=f"temp_{i}",
                device_type=DeviceType.TEMPERATURE,
                control_mode=ControlMode.CONTROLLABLE,
                power_rating=3.0,  # 3kW 에어컨
                priority=2,
                flexibility=0.7
            ))
            self.devices.append(Device(
                device_id=f"light_{i}",
                device_type=DeviceType.LIGHT,
                control_mode=ControlMode.SELECTABLE,
                power_rating=0.5,  # 0.5kW LED
                priority=3,
                flexibility=0.5
            ))
        
        # 행정실/교무실 디바이스
        for i in range(5):
            self.devices.append(Device(
                device_id=f"copier_{i}",
                device_type=DeviceType.COPY_MACHINE,
                control_mode=ControlMode.CONTROLLABLE,
                power_rating=2.0,
                priority=6,
                flexibility=0.8
            ))
        
        # 급식실 디바이스
        for i in range(3):
            self.devices.append(Device(
                device_id=f"microwave_{i}",
                device_type=DeviceType.MICROWAVE,
                control_mode=ControlMode.CONTROLLABLE,
                power_rating=1.5,
                priority=4,
                flexibility=0.6
            ))
        
        # 공급 측
        self.supplies.append(PowerSupply(
            source_id="solar_1",
            source_type=EnergySource.SOLAR,
            capacity=100.0,  # 100kW
            cost_per_kwh=0
        ))
        
        self.supplies.append(PowerSupply(
            source_id="wind_1",
            source_type=EnergySource.WIND,
            capacity=50.0,  # 50kW
            cost_per_kwh=0
        ))
        
        self.supplies.append(PowerSupply(
            source_id="grid_1",
            source_type=EnergySource.GRID,
            capacity=500.0,  # 500kW
            cost_per_kwh=150
        ))
        
        # ESS
        self.ess = ESSSystem(
            capacity=200.0,  # 200kWh
            current_soc=0.6,
            max_charge_rate=50.0,
            max_discharge_rate=50.0
        )
        
        print("✅ 스마트 그리드 디지털 트윈 시스템 초기화 완료")
        print(f"   - 수요 측 디바이스: {len(self.devices)}개")
        print(f"   - 공급원: {len(self.supplies)}개")
        print(f"   - ESS 용량: {self.ess.capacity}kWh (SOC: {self.ess.current_soc*100:.1f}%)")
    
    def update_environment(self, hour: int):
        """환경 데이터 업데이트 (시간대별 시뮬레이션)"""
        # 온도 (일일 변화 패턴)
        self.environment.temperature = 20 + 10 * np.sin((hour - 6) * np.pi / 12)
        
        # 일사량 (주간에만)
        if 6 <= hour <= 18:
            self.environment.solar_radiation = 800 * np.sin((hour - 6) * np.pi / 12)
        else:
            self.environment.solar_radiation = 0
        
        # 풍속 (랜덤 + 계절성)
        self.environment.wind_speed = max(0, np.random.normal(5, 2))
        
        # 재실 인원 (수업 시간 기준)
        if 9 <= hour <= 16:  # 수업 시간
            self.environment.occupancy = 500 + np.random.randint(-50, 50)
        else:
            self.environment.occupancy = 50 + np.random.randint(-20, 20)
        
        self.environment.humidity = 50 + np.random.normal(0, 5)
    
    def simulate_device_usage(self, hour: int):
        """시간대별 디바이스 사용 패턴 시뮬레이션"""
        # 수업 시간 (9-16시) 대부분 켜짐
        active_ratio = 0.8 if 9 <= hour <= 16 else 0.2
        
        for device in self.devices:
            # 확률적으로 디바이스 상태 변경
            if np.random.random() < 0.3:  # 30% 확률로 상태 변경
                device.is_active = np.random.random() < active_ratio
                device.current_power = device.power_rating if device.is_active else 0
    
    def get_system_state(self) -> Dict:
        """현재 시스템 상태 수집"""
        total_demand = sum(d.get_power_consumption() for d in self.devices)
        total_supply = sum(s.get_available_power() for s in self.supplies)
        
        return {
            'current_time': self.current_time,
            'total_demand': total_demand,
            'total_supply': total_supply,
            'devices': self.devices,
            'supplies': self.supplies,
            'ess': self.ess,
            'environment': self.environment,
            'power_balance': total_supply - total_demand
        }
    
    def run_control_cycle(self) -> Dict:
        """제어 사이클 실행 (AI 에이전트 협업)"""
        # 1. 현재 상태 수집
        state = self.get_system_state()
        
        # 2. 공급 최적화 에이전트 실행
        so_decision = self.so_agent.decide(state)
        
        # 공급 계획 적용
        for plan in so_decision['supply_plan']:
            if 'source_id' in plan:
                supply = next((s for s in self.supplies if s.source_id == plan['source_id']), None)
                if supply:
                    supply.current_output = plan['output']
            elif 'ess_action' in plan:
                if plan['ess_action'] == 'charge':
                    self.ess.charge(plan['power'], 1/60)  # 1분 단위
                elif plan['ess_action'] == 'discharge':
                    self.ess.discharge(plan['power'], 1/60)
        
        # 상태 업데이트
        state = self.get_system_state()
        state['renewable_ratio'] = so_decision.get('renewable_ratio', 0)
        
        # 3. 수요 반응 에이전트 실행
        dr_decision = self.dr_agent.decide(state)
        
        # 수요 제어 적용
        for decision in dr_decision['decisions']:
            device = next((d for d in self.devices if d.device_id == decision['device_id']), None)
            if device:
                if decision['action'] == 'turn_off':
                    device.is_active = False
                    device.current_power = 0
                elif decision['action'] == 'turn_on':
                    device.is_active = True
                    device.current_power = device.power_rating
        
        # 4. 가격 결정 에이전트 실행
        state = self.get_system_state()
        state['renewable_ratio'] = so_decision.get('renewable_ratio', 0)
        price_decision = self.price_agent.decide(state)
        
        # 5. 결과 수집
        final_state = self.get_system_state()
        
        result = {
            'timestamp': self.current_time,
            'environment': {
                'temperature': self.environment.temperature,
                'solar_radiation': self.environment.solar_radiation,
                'wind_speed': self.environment.wind_speed,
                'occupancy': self.environment.occupancy
            },
            'power': {
                'total_demand': final_state['total_demand'],
                'total_supply': final_state['total_supply'],
                'balance': final_state['power_balance'],
                'ess_soc': self.ess.current_soc * 100
            },
            'supply_optimization': so_decision,
            'demand_response': dr_decision,
            'pricing': price_decision,
            'performance_metrics': self._calculate_metrics(final_state, so_decision, price_decision)
        }
        
        self.simulation_log.append(result)
        
        return result
    
    def _calculate_metrics(self, state: Dict, so_decision: Dict, price_decision: Dict) -> Dict:
        """성능 지표 계산"""
        # 재생에너지 활용률
        renewable_ratio = so_decision.get('renewable_ratio', 0)
        
        # 전력 균형 안정성
        balance = state['power_balance']
        stability = 1 - min(abs(balance) / max(state['total_demand'], 1), 1)
        
        # 비용 효율성 (낮을수록 좋음)
        total_cost = sum(
            plan.get('cost', 0) 
            for plan in so_decision.get('supply_plan', [])
        )
        max_cost = state['total_demand'] * 200
        cost_efficiency = 1 - min(total_cost / max(max_cost, 1), 1) if max_cost > 0 else 1
        
        # ESS 활용도
        ess_utilization = abs(0.5 - self.ess.current_soc) * 2  # 0.5 근처가 가장 좋음
        
        return {
            'renewable_ratio': round(renewable_ratio * 100, 2),
            'stability_score': round(stability * 100, 2),
            'cost_efficiency': round(cost_efficiency * 100, 2),
            'ess_utilization': round((1 - ess_utilization) * 100, 2),
            'overall_score': round((renewable_ratio + stability + cost_efficiency + (1-ess_utilization)) * 25, 2)
        }
    
    def run_simulation(self, duration_hours: int = 24, time_step_minutes: int = 30):
        """시뮬레이션 실행"""
        print(f"\n{'='*80}")
        print(f"🚀 스마트 그리드 디지털 트윈 시뮬레이션 시작")
        print(f"{'='*80}")
        print(f"시뮬레이션 기간: {duration_hours}시간 (간격: {time_step_minutes}분)")
        print(f"시작 시간: {self.current_time.strftime('%Y-%m-%d %H:%M')}\n")
        
        steps = int(duration_hours * 60 / time_step_minutes)
        
        for step in range(steps):
            # 시간 진행
            hour = self.current_time.hour
            
            # 환경 업데이트
            self.update_environment(hour)
            
            # 디바이스 사용 패턴 시뮬레이션
            self.simulate_device_usage(hour)
            
            # 제어 사이클 실행
            result = self.run_control_cycle()
            
            # 진행 상황 출력 (매 시간)
            if step % 2 == 0:
                print(f"[{result['timestamp'].strftime('%H:%M')}] "
                      f"수요: {result['power']['total_demand']:.1f}kW | "
                      f"공급: {result['power']['total_supply']:.1f}kW | "
                      f"균형: {result['power']['balance']:+.1f}kW | "
                      f"재생에너지: {result['performance_metrics']['renewable_ratio']:.1f}% | "
                      f"종합점수: {result['performance_metrics']['overall_score']:.1f}")
            
            # 시간 진행
            self.current_time += timedelta(minutes=time_step_minutes)
        
        print(f"\n{'='*80}")
        print("✅ 시뮬레이션 완료")
        print(f"{'='*80}\n")
        
        return self.simulation_log
    
    def generate_report(self) -> pd.DataFrame:
        """시뮬레이션 결과 리포트 생성"""
        if not self.simulation_log:
            return None
        
        # 데이터프레임으로 변환
        data = []
        for log in self.simulation_log:
            data.append({
                '시각': log['timestamp'].strftime('%Y-%m-%d %H:%M'),
                '온도': log['environment']['temperature'],
                '일사량': log['environment']['solar_radiation'],
                '풍속': log['environment']['wind_speed'],
                '재실인원': log['environment']['occupancy'],
                '전력수요': log['power']['total_demand'],
                '전력공급': log['power']['total_supply'],
                '전력균형': log['power']['balance'],
                'ESS_SOC': log['power']['ess_soc'],
                '가격': log['pricing']['price_kwh'],
                '재생에너지비율': log['performance_metrics']['renewable_ratio'],
                '안정성점수': log['performance_metrics']['stability_score'],
                '비용효율성': log['performance_metrics']['cost_efficiency'],
                'ESS활용도': log['performance_metrics']['ess_utilization'],
                '종합점수': log['performance_metrics']['overall_score']
            })
        
        df = pd.DataFrame(data)
        
        # 통계 요약
        print("\n📊 시뮬레이션 결과 요약")
        print("="*80)
        print(f"평균 전력 수요: {df['전력수요'].mean():.2f} kW")
        print(f"평균 전력 공급: {df['전력공급'].mean():.2f} kW")
        print(f"평균 재생에너지 비율: {df['재생에너지비율'].mean():.2f} %")
        print(f"평균 안정성 점수: {df['안정성점수'].mean():.2f} %")
        print(f"평균 비용 효율성: {df['비용효율성'].mean():.2f} %")
        print(f"평균 종합 점수: {df['종합점수'].mean():.2f} %")
        print(f"평균 전력 가격: {df['가격'].mean():.2f} 원/kWh")
        print("="*80)
        
        return df
    
    def export_results(self, filename: str = "simulation_results.csv"):
        """결과를 CSV로 내보내기"""
        df = self.generate_report()
        if df is not None:
            output_path = f"/mnt/user-data/outputs/{filename}"
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\n✅ 결과가 저장되었습니다: {output_path}")
            return output_path
        return None

# ==================== 메인 실행 ====================

def main():
    """메인 실행 함수"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║          🏫 스마트 그리드 AI 에이전트 디지털 트윈 서비스                  ║
    ║                                                                          ║
    ║  • 수요-공급 에너지 매칭 시뮬레이션                                       ║
    ║  • AI 에이전트 기반 실시간 제어 알고리즘                                  ║
    ║  • 재생에너지 최적화 및 ESS 운영                                         ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # 디지털 트윈 생성
    twin = SmartGridDigitalTwin()
    
    # 24시간 시뮬레이션 실행 (30분 간격)
    results = twin.run_simulation(duration_hours=24, time_step_minutes=30)
    
    # 결과 리포트 생성
    df = twin.generate_report()
    
    # 결과 저장
    output_file = twin.export_results("smart_grid_simulation_results.csv")
    
    print("\n📈 주요 성능 지표:")
    print("-" * 80)
    print(f"✓ 재생에너지 활용: 평균 {df['재생에너지비율'].mean():.1f}%")
    print(f"✓ 시스템 안정성: 평균 {df['안정성점수'].mean():.1f}%")
    print(f"✓ 비용 효율성: 평균 {df['비용효율성'].mean():.1f}%")
    print(f"✓ 종합 성능: 평균 {df['종합점수'].mean():.1f}%")
    
    return twin, df

if __name__ == "__main__":
    twin, results = main()
