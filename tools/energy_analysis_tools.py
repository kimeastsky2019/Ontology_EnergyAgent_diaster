"""
에너지 특화 분석 도구

에너지 데이터의 특수한 분석 기능을 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from fastmcp import FastMCP

class EnergyAnalysisTools:
    """에너지 특화 분석 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def analyze_peak_demand(data: List[Dict], value_column: str = "consumption",
                                    threshold_percentile: float = 90) -> Dict[str, Any]:
            """
            피크 수요를 분석합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                threshold_percentile: 피크 임계값 백분위수
                
            Returns:
                피크 수요 분석 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 10:
                    return {"error": "피크 수요 분석을 위해서는 최소 10개의 데이터 포인트가 필요합니다."}
                
                # 피크 임계값 계산
                threshold = np.percentile(ts_data, threshold_percentile)
                
                # 피크 구간 식별
                peak_mask = ts_data >= threshold
                peak_periods = ts_data[peak_mask]
                
                # 피크 패턴 분석
                peak_hours = peak_periods.index.hour.value_counts()
                peak_days = peak_periods.index.date.value_counts()
                
                # 연속 피크 구간 분석
                peak_groups = []
                current_group = []
                
                for i, (timestamp, value) in enumerate(peak_periods.items()):
                    if i == 0 or (timestamp - peak_periods.index[i-1]).total_seconds() <= 3600:  # 1시간 이내
                        current_group.append((timestamp, value))
                    else:
                        if current_group:
                            peak_groups.append(current_group)
                        current_group = [(timestamp, value)]
                
                if current_group:
                    peak_groups.append(current_group)
                
                # 피크 그룹 분석
                peak_group_analysis = []
                for group in peak_groups:
                    if len(group) > 1:  # 연속 피크만 분석
                        start_time = group[0][0]
                        end_time = group[-1][0]
                        duration = (end_time - start_time).total_seconds() / 3600  # 시간 단위
                        max_value = max([v for _, v in group])
                        avg_value = np.mean([v for _, v in group])
                        
                        peak_group_analysis.append({
                            "start_time": str(start_time),
                            "end_time": str(end_time),
                            "duration_hours": float(duration),
                            "max_value": float(max_value),
                            "avg_value": float(avg_value),
                            "peak_count": len(group)
                        })
                
                # 피크 요금 계산 (가정: 피크 시간대 요금이 2배)
                base_rate = 0.12  # 기본 kWh당 요금
                peak_rate = base_rate * 2
                peak_cost = peak_periods.sum() * peak_rate
                total_cost = ts_data.sum() * base_rate
                peak_cost_percentage = (peak_cost / total_cost) * 100
                
                return {
                    "success": True,
                    "threshold_percentile": threshold_percentile,
                    "peak_threshold": float(threshold),
                    "peak_analysis": {
                        "total_peak_periods": len(peak_periods),
                        "peak_percentage": len(peak_periods) / len(ts_data) * 100,
                        "max_peak_value": float(peak_periods.max()),
                        "avg_peak_value": float(peak_periods.mean())
                    },
                    "peak_patterns": {
                        "peak_hours": {str(hour): int(count) for hour, count in peak_hours.items()},
                        "peak_days": {str(day): int(count) for day, count in peak_days.head(10).items()}
                    },
                    "peak_groups": peak_group_analysis,
                    "cost_analysis": {
                        "peak_cost": float(peak_cost),
                        "total_cost": float(total_cost),
                        "peak_cost_percentage": float(peak_cost_percentage)
                    }
                }
                
            except Exception as e:
                return {"error": f"피크 수요 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def calculate_energy_efficiency(data: List[Dict], value_column: str = "consumption",
                                            baseline_consumption: Optional[float] = None) -> Dict[str, Any]:
            """
            에너지 효율성을 계산합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                baseline_consumption: 기준 소비량 (없으면 평균 사용)
                
            Returns:
                에너지 효율성 분석 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 10:
                    return {"error": "효율성 분석을 위해서는 최소 10개의 데이터 포인트가 필요합니다."}
                
                # 기준 소비량 설정
                if baseline_consumption is None:
                    baseline_consumption = ts_data.mean()
                
                # 효율성 지표 계산
                current_consumption = ts_data.mean()
                efficiency_ratio = baseline_consumption / current_consumption
                efficiency_percentage = efficiency_ratio * 100
                
                # 변동성 분석
                coefficient_of_variation = ts_data.std() / ts_data.mean()
                
                # 시간대별 효율성 분석
                hourly_data = ts_data.groupby(ts_data.index.hour).agg(['mean', 'std'])
                hourly_efficiency = []
                
                for hour, (mean_val, std_val) in hourly_data.iterrows():
                    hour_efficiency = baseline_consumption / mean_val if mean_val > 0 else 0
                    hourly_efficiency.append({
                        "hour": int(hour),
                        "consumption": float(mean_val),
                        "efficiency": float(hour_efficiency),
                        "variability": float(std_val / mean_val) if mean_val > 0 else 0
                    })
                
                # 일별 효율성 분석
                daily_consumption = ts_data.resample('D').sum()
                daily_efficiency = []
                
                for date, consumption in daily_consumption.items():
                    daily_baseline = baseline_consumption * 24  # 일일 기준 (시간당 * 24)
                    efficiency = daily_baseline / consumption if consumption > 0 else 0
                    daily_efficiency.append({
                        "date": str(date.date()),
                        "consumption": float(consumption),
                        "efficiency": float(efficiency)
                    })
                
                # 효율성 등급 분류
                if efficiency_percentage >= 90:
                    efficiency_grade = "Excellent"
                elif efficiency_percentage >= 80:
                    efficiency_grade = "Good"
                elif efficiency_percentage >= 70:
                    efficiency_grade = "Fair"
                else:
                    efficiency_grade = "Poor"
                
                # 개선 권장사항
                recommendations = []
                if efficiency_percentage < 80:
                    recommendations.append("에너지 효율성 개선이 필요합니다.")
                if coefficient_of_variation > 0.3:
                    recommendations.append("소비 패턴의 변동성이 높습니다. 일정한 사용 패턴을 유지하세요.")
                
                # 가장 비효율적인 시간대 찾기
                worst_hour = min(hourly_efficiency, key=lambda x: x['efficiency'])
                if worst_hour['efficiency'] < 0.8:
                    recommendations.append(f"{worst_hour['hour']}시대의 에너지 사용을 줄이세요.")
                
                return {
                    "success": True,
                    "efficiency_metrics": {
                        "current_consumption": float(current_consumption),
                        "baseline_consumption": float(baseline_consumption),
                        "efficiency_ratio": float(efficiency_ratio),
                        "efficiency_percentage": float(efficiency_percentage),
                        "efficiency_grade": efficiency_grade,
                        "coefficient_of_variation": float(coefficient_of_variation)
                    },
                    "hourly_efficiency": hourly_efficiency,
                    "daily_efficiency": daily_efficiency[-7:],  # 최근 7일
                    "recommendations": recommendations
                }
                
            except Exception as e:
                return {"error": f"에너지 효율성 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def analyze_energy_patterns(data: List[Dict], value_column: str = "consumption") -> Dict[str, Any]:
            """
            에너지 사용 패턴을 분석합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                
            Returns:
                에너지 패턴 분석 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 24:
                    return {"error": "패턴 분석을 위해서는 최소 24개의 데이터 포인트가 필요합니다."}
                
                # 시간대별 패턴
                hourly_pattern = ts_data.groupby(ts_data.index.hour).agg(['mean', 'std', 'min', 'max'])
                
                # 요일별 패턴
                weekday_pattern = ts_data.groupby(ts_data.index.weekday).agg(['mean', 'std'])
                weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                # 월별 패턴 (데이터가 충분한 경우)
                monthly_pattern = None
                if len(ts_data) > 720:  # 30일 * 24시간
                    monthly_pattern = ts_data.groupby(ts_data.index.month).agg(['mean', 'std'])
                
                # 계절성 분석
                ts_data_with_hour = ts_data.copy()
                ts_data_with_hour.index = pd.to_datetime(ts_data_with_hour.index)
                
                # 주간 패턴 (요일별)
                weekly_pattern = ts_data.resample('W').agg(['mean', 'sum', 'std'])
                
                # 피크/오프피크 시간대 분석
                hourly_avg = hourly_pattern['mean']
                peak_hours = hourly_avg.nlargest(3).index.tolist()
                off_peak_hours = hourly_avg.nsmallest(3).index.tolist()
                
                # 패턴 일관성 분석
                hourly_cv = hourly_pattern['std'] / hourly_pattern['mean']
                pattern_consistency = 1 - hourly_cv.mean()  # 1에 가까울수록 일관적
                
                # 에너지 사용 집중도
                total_consumption = ts_data.sum()
                top_20_percent_hours = int(len(ts_data) * 0.2)
                top_consumption = ts_data.nlargest(top_20_percent_hours).sum()
                concentration_ratio = top_consumption / total_consumption
                
                return {
                    "success": True,
                    "hourly_patterns": {
                        str(hour): {
                            "mean": float(row['mean']),
                            "std": float(row['std']),
                            "min": float(row['min']),
                            "max": float(row['max'])
                        } for hour, row in hourly_pattern.iterrows()
                    },
                    "weekday_patterns": {
                        weekday_names[day]: {
                            "mean": float(row['mean']),
                            "std": float(row['std'])
                        } for day, row in weekday_pattern.iterrows()
                    },
                    "monthly_patterns": {
                        str(month): {
                            "mean": float(row['mean']),
                            "std": float(row['std'])
                        } for month, row in monthly_pattern.iterrows()
                    } if monthly_pattern is not None else None,
                    "peak_analysis": {
                        "peak_hours": peak_hours,
                        "off_peak_hours": off_peak_hours,
                        "peak_consumption": float(hourly_avg[peak_hours].mean()),
                        "off_peak_consumption": float(hourly_avg[off_peak_hours].mean())
                    },
                    "pattern_characteristics": {
                        "consistency_score": float(pattern_consistency),
                        "concentration_ratio": float(concentration_ratio),
                        "peak_off_peak_ratio": float(hourly_avg[peak_hours].mean() / hourly_avg[off_peak_hours].mean())
                    },
                    "weekly_summary": {
                        "avg_weekly_consumption": float(weekly_pattern['sum'].mean()),
                        "weekly_variability": float(weekly_pattern['sum'].std())
                    }
                }
                
            except Exception as e:
                return {"error": f"에너지 패턴 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def calculate_energy_savings_potential(data: List[Dict], value_column: str = "consumption",
                                                   target_reduction: float = 0.2) -> Dict[str, Any]:
            """
            에너지 절약 잠재력을 계산합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                target_reduction: 목표 절약률 (0.2 = 20%)
                
            Returns:
                에너지 절약 잠재력 분석 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 10:
                    return {"error": "절약 잠재력 분석을 위해서는 최소 10개의 데이터 포인트가 필요합니다."}
                
                # 현재 소비량 분석
                current_consumption = ts_data.sum()
                current_daily_avg = ts_data.resample('D').sum().mean()
                current_hourly_avg = ts_data.mean()
                
                # 목표 절약량 계산
                target_consumption = current_consumption * (1 - target_reduction)
                potential_savings = current_consumption - target_consumption
                
                # 시간대별 절약 잠재력 분석
                hourly_data = ts_data.groupby(ts_data.index.hour).mean()
                peak_hours = hourly_data.nlargest(8).index.tolist()  # 상위 8시간
                
                # 피크 시간대 절약 시뮬레이션
                peak_reduction_scenarios = []
                for reduction_rate in [0.1, 0.2, 0.3]:
                    peak_consumption = hourly_data[peak_hours].sum() * 24  # 일일 피크 소비량
                    peak_savings = peak_consumption * reduction_rate
                    total_savings = peak_savings
                    savings_percentage = (total_savings / current_consumption) * 100
                    
                    peak_reduction_scenarios.append({
                        "reduction_rate": reduction_rate,
                        "peak_savings": float(peak_savings),
                        "total_savings": float(total_savings),
                        "savings_percentage": float(savings_percentage)
                    })
                
                # 비용 절약 계산 (가정: kWh당 $0.12)
                cost_per_kwh = 0.12
                current_cost = current_consumption * cost_per_kwh
                target_cost = target_consumption * cost_per_kwh
                cost_savings = current_cost - target_cost
                
                # 연간 절약 잠재력 (데이터 기간을 연간으로 확장)
                data_days = (ts_data.index.max() - ts_data.index.min()).days + 1
                annual_scaling_factor = 365 / data_days if data_days > 0 else 1
                annual_savings = potential_savings * annual_scaling_factor
                annual_cost_savings = cost_savings * annual_scaling_factor
                
                # 절약 권장사항
                recommendations = []
                if hourly_data.max() / hourly_data.mean() > 2:
                    recommendations.append("피크 시간대 사용량이 평균의 2배 이상입니다. 피크 시간대 사용을 줄이세요.")
                
                if ts_data.std() / ts_data.mean() > 0.5:
                    recommendations.append("사용 패턴의 변동성이 높습니다. 일정한 사용 패턴을 유지하세요.")
                
                # 가장 절약 가능성이 높은 시간대
                worst_hours = hourly_data.nlargest(3).index.tolist()
                recommendations.append(f"{worst_hours}시대의 사용량을 줄이면 큰 절약 효과를 얻을 수 있습니다.")
                
                return {
                    "success": True,
                    "current_consumption": {
                        "total": float(current_consumption),
                        "daily_average": float(current_daily_avg),
                        "hourly_average": float(current_hourly_avg),
                        "current_cost": float(current_cost)
                    },
                    "savings_potential": {
                        "target_reduction": target_reduction,
                        "target_consumption": float(target_consumption),
                        "potential_savings": float(potential_savings),
                        "cost_savings": float(cost_savings),
                        "savings_percentage": float((potential_savings / current_consumption) * 100)
                    },
                    "annual_projection": {
                        "annual_savings": float(annual_savings),
                        "annual_cost_savings": float(annual_cost_savings),
                        "roi_period_months": float(annual_cost_savings / 12) if annual_cost_savings > 0 else None
                    },
                    "peak_reduction_scenarios": peak_reduction_scenarios,
                    "recommendations": recommendations,
                    "data_period_days": data_days
                }
                
            except Exception as e:
                return {"error": f"에너지 절약 잠재력 분석 실패: {str(e)}"}

