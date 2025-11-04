# 🏫 스마트 그리드 AI 에이전트 디지털 트윈 서비스

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [주요 기능](#주요-기능)
3. [AI 에이전트 아키텍처](#ai-에이전트-아키텍처)
4. [설치 및 실행](#설치-및-실행)
5. [시뮬레이션 결과 분석](#시뮬레이션-결과-분석)
6. [커스터마이징 가이드](#커스터마이징-가이드)

---

## 🎯 시스템 개요

본 디지털 트윈 서비스는 스마트 그리드 시스템의 **수요-공급 에너지 매칭**과 **제어 알고리즘 평가**를 실시간으로 시뮬레이션하는 AI 에이전트 기반 플랫폼입니다.

### 주요 특징
- ✅ **실시간 시뮬레이션**: 24시간 에너지 수요-공급 패턴 재현
- ✅ **3개의 AI 에이전트**: 수요 반응, 공급 최적화, 가격 결정
- ✅ **재생에너지 통합**: 태양광, 풍력 발전 시뮬레이션
- ✅ **ESS 최적 운영**: 충방전 전략 자동 결정
- ✅ **성능 지표 평가**: 재생에너지 비율, 안정성, 비용 효율성

---

## 🚀 주요 기능

### 1. 수요 측 시뮬레이션
학교 건물을 모델로 한 제어 가능 디바이스:
- **20개 교실**: 에어컨(3kW), 조명(0.5kW)
- **5개 사무실**: 복사기(2kW)
- **3개 급식실**: 전자레인지(1.5kW)

각 디바이스는 제어 모드를 가집니다:
- `제어가능`: 전력 부족 시 자동 차단 가능
- `선택제어`: 조건부 제어
- `제어불가`: 필수 디바이스

### 2. 공급 측 시뮬레이션
- **태양광 발전**: 최대 100kW (일사량 기반)
- **풍력 발전**: 최대 50kW (풍속 기반)
- **ESS**: 200kWh 용량, 50kW 충방전
- **전력망**: 500kW 백업 전원

### 3. 환경 센서 데이터
실시간 환경 변수 시뮬레이션:
- 온도 (일일 변화 패턴)
- 일사량 (주간 6-18시)
- 풍속 (랜덤 + 계절성)
- 재실 인원 (수업 시간 기반)

---

## 🤖 AI 에이전트 아키텍처

### 1️⃣ 수요 반응 에이전트 (Demand Response Agent)

**역할**: 전력 수요 제어 및 최적화

**알고리즘**:
```python
if 전력_부족:
    # 우선순위 낮은 디바이스부터 차단
    for device in sorted(devices, by='priority', reverse=True):
        if device.is_controllable:
            turn_off(device)
            
elif 전력_잉여 > 50kW:
    # 우선순위 높은 디바이스부터 활성화
    for device in sorted(devices, by='priority'):
        if device.is_controllable:
            turn_on(device)
```

**주요 지표**:
- 제어 디바이스 수
- 우선순위 기반 부하 관리
- 전력 절감량

### 2️⃣ 공급 최적화 에이전트 (Supply Optimization Agent)

**역할**: 전력 공급 최적화 및 재생에너지 활용 극대화

**우선순위 전략**:
1. **재생에너지 우선 사용** (태양광 → 풍력)
2. **ESS 충방전 전략**
   - 재생에너지 잉여 시 → ESS 충전
   - 전력 부족 시 → ESS 방전
3. **전력망 최소 사용** (최후 수단)

**알고리즘**:
```python
# 1단계: 재생에너지 발전량 예측
solar_power = predict_solar(일사량)
wind_power = predict_wind(풍속)

# 2단계: 재생에너지로 수요 충족
remaining = demand - (solar + wind)

# 3단계: ESS 활용
if 재생에너지_잉여 and ESS_SOC < 90%:
    ESS.charge(잉여_전력)
elif remaining > 0 and ESS_SOC > 20%:
    ESS.discharge(min(remaining, ESS_max_discharge))

# 4단계: 부족분은 전력망 사용
if remaining > 0:
    grid.supply(remaining)
```

### 3️⃣ 가격 결정 에이전트 (Pricing Agent)

**역할**: 동적 전력 가격 결정

**가격 결정 요소**:
- **수급 균형**: 공급 > 수요 → 가격 하락 (70%)
- **시간대**: 피크 시간(9-12, 18-21) → 가격 상승 (150%)
- **재생에너지 비율**: 50% 이상 → 할인 (80%)

**수식**:
```
최종_가격 = 기본가격 × 수급계수 × 시간계수 × 재생에너지할인
```

---

## 💻 설치 및 실행

### 필요 라이브러리
```bash
pip install numpy pandas --break-system-packages
```

### 실행 방법

#### 1. 기본 시뮬레이션
```bash
python smart_grid_digital_twin.py
```

#### 2. 커스텀 시뮬레이션
```python
from smart_grid_digital_twin import SmartGridDigitalTwin

# 디지털 트윈 생성
twin = SmartGridDigitalTwin()

# 48시간 시뮬레이션 (15분 간격)
results = twin.run_simulation(duration_hours=48, time_step_minutes=15)

# 결과 분석
df = twin.generate_report()

# 결과 저장
twin.export_results("custom_results.csv")
```

#### 3. 대시보드 실행
```bash
# 웹 서버 실행 (Python 내장)
python -m http.server 8000

# 브라우저에서 접속
http://localhost:8000/dashboard.html
```

---

## 📊 시뮬레이션 결과 분석

### 출력 데이터 구조

CSV 파일 컬럼:
- **시각**: 시뮬레이션 타임스탬프
- **환경 데이터**: 온도, 일사량, 풍속, 재실인원
- **전력 데이터**: 수요, 공급, 균형, ESS SOC
- **가격**: 동적 전력 가격
- **성능 지표**: 재생에너지 비율, 안정성, 비용 효율성, 종합 점수

### 핵심 성능 지표 (KPI)

#### 1. 재생에너지 비율
```
재생에너지_비율 = (태양광 + 풍력) / 총_수요 × 100
```
- **목표**: 50% 이상
- **우수**: 80% 이상

#### 2. 시스템 안정성
```
안정성 = 1 - |전력_균형| / 총_수요
```
- **목표**: 70% 이상
- **우수**: 90% 이상

#### 3. 비용 효율성
```
비용_효율성 = 1 - 실제_비용 / 최대_비용
```
- **목표**: 80% 이상
- **우수**: 95% 이상

#### 4. 종합 점수
```
종합 = (재생에너지 + 안정성 + 비용효율 + ESS활용) / 4
```
- **목표**: 70점 이상
- **우수**: 85점 이상

### 시뮬레이션 결과 예시

```
평균 전력 수요: 5.04 kW
평균 전력 공급: 6.06 kW
평균 재생에너지 비율: 81.17%  ✅ 우수
평균 안정성 점수: 65.76%      ⚠️ 개선 필요
평균 비용 효율성: 100.00%      ✅ 최고
평균 종합 점수: 82.36%         ✅ 우수
```

---

## 🔧 커스터마이징 가이드

### 1. 디바이스 추가/수정

```python
# 새로운 디바이스 추가
twin.devices.append(Device(
    device_id="new_device_1",
    device_type=DeviceType.FAN,
    control_mode=ControlMode.CONTROLLABLE,
    power_rating=2.5,  # kW
    priority=4,  # 1(높음) ~ 10(낮음)
    flexibility=0.7  # 제어 유연성 (0~1)
))
```

### 2. 재생에너지 용량 조정

```python
# 태양광 용량 변경
solar = next(s for s in twin.supplies if s.source_type == EnergySource.SOLAR)
solar.capacity = 200.0  # 100kW → 200kW

# ESS 용량 변경
twin.ess.capacity = 500.0  # 200kWh → 500kWh
```

### 3. AI 에이전트 알고리즘 수정

```python
class CustomDemandAgent(DemandResponseAgent):
    def decide(self, state: Dict) -> Dict:
        # 여기에 커스텀 알고리즘 구현
        # 예: 날씨 기반 예측 제어
        
        if state['environment'].temperature > 28:
            # 더운 날씨에 에어컨 우선 운영
            priority_boost = {'TEMPERATURE': -2}
        
        return super().decide(state)
```

### 4. 환경 시나리오 변경

```python
def update_environment_custom(self, hour: int):
    # 겨울철 시나리오
    self.environment.temperature = 5 + 5 * np.sin((hour - 6) * np.pi / 12)
    
    # 흐린 날 시나리오
    if 6 <= hour <= 18:
        self.environment.solar_radiation = 300 * np.sin((hour - 6) * np.pi / 12)
    
    # 강풍 시나리오
    self.environment.wind_speed = max(0, np.random.normal(10, 3))
```

---

## 📈 대시보드 기능

웹 대시보드(`dashboard.html`)는 다음 기능을 제공합니다:

### 실시간 모니터링
1. **메트릭 카드**: 주요 KPI 실시간 표시
2. **AI 에이전트 상태**: 각 에이전트 활동 모니터링
3. **차트 시각화**: 
   - 전력 수요-공급 추이
   - 재생에너지 발전량
   - ESS 상태
   - 성능 지표 추이

### 인터랙티브 기능
- 시간대별 데이터 줌인/줌아웃
- 호버로 상세 데이터 확인
- 범례 클릭으로 데이터 시리즈 토글

---

## 🎓 활용 사례

### 1. 제어 알고리즘 성능 비교
```python
# 알고리즘 A
twin_a = SmartGridDigitalTwin()
results_a = twin_a.run_simulation()

# 알고리즘 B (커스텀)
twin_b = SmartGridDigitalTwin()
twin_b.dr_agent = CustomDemandAgent()
results_b = twin_b.run_simulation()

# 성능 비교
compare_results(results_a, results_b)
```

### 2. 재생에너지 용량 최적화
```python
capacities = [50, 100, 150, 200]  # kW
results = []

for capacity in capacities:
    twin = SmartGridDigitalTwin()
    twin.supplies[0].capacity = capacity
    result = twin.run_simulation()
    results.append(result)

# 최적 용량 도출
optimal_capacity = find_optimal(results)
```

### 3. 비상 상황 시뮬레이션
```python
# 전력망 차단 시나리오
twin = SmartGridDigitalTwin()
twin.supplies = [s for s in twin.supplies if s.source_type != EnergySource.GRID]

# ESS만으로 운영 가능 여부 평가
results = twin.run_simulation()
evaluate_resilience(results)
```

---

## 📞 기술 지원

### 문제 해결

**Q: 시뮬레이션이 너무 느려요**
A: `time_step_minutes` 값을 늘리세요 (예: 30 → 60)

**Q: ESS SOC가 너무 빨리 소진돼요**
A: ESS 용량을 늘리거나(`ess.capacity`) 최대 방전율을 조정하세요

**Q: 재생에너지 비율이 낮아요**
A: 태양광/풍력 용량을 늘리거나, 환경 데이터를 더 유리하게 설정하세요

---

## 🔮 향후 계획

- [ ] 강화학습 기반 AI 에이전트 학습 기능
- [ ] 실제 IoT 센서 연동
- [ ] 다양한 건물 유형 템플릿 (병원, 공장, 아파트)
- [ ] 전력 시장 거래 시뮬레이션
- [ ] V2G (Vehicle-to-Grid) 통합
- [ ] 날씨 API 실시간 연동

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## ✨ 개발 정보

- **개발**: Claude AI Assistant
- **버전**: 1.0.0
- **날짜**: 2025-11-03
- **언어**: Python 3.10+
- **프레임워크**: Numpy, Pandas, Plotly

---

**🎉 스마트 그리드 AI 디지털 트윈으로 에너지 혁신을 경험하세요!**
