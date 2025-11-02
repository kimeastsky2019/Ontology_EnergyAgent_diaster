"""
시계열 데이터 분석 도구

에너지 데이터의 시계열 분석을 위한 도구들을 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from scipy import stats
from fastmcp import FastMCP

class TimeSeriesTools:
    """시계열 분석 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def load_energy_data(file_path: str, datetime_column: str = "datetime", 
                                 value_column: str = "consumption") -> Dict[str, Any]:
            """
            에너지 데이터를 로드하고 시계열로 변환합니다.
            
            Args:
                file_path: 데이터 파일 경로
                datetime_column: 날짜/시간 컬럼명
                value_column: 에너지 소비량 컬럼명
                
            Returns:
                로드된 데이터 정보
            """
            try:
                # 파일 확장자에 따라 로드 방법 결정
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.json'):
                    df = pd.read_json(file_path)
                else:
                    return {"error": "지원하지 않는 파일 형식입니다. CSV, XLSX, JSON만 지원됩니다."}
                
                # 날짜/시간 컬럼 변환
                if datetime_column in df.columns:
                    df[datetime_column] = pd.to_datetime(df[datetime_column])
                    df = df.set_index(datetime_column)
                else:
                    return {"error": f"날짜/시간 컬럼 '{datetime_column}'을 찾을 수 없습니다."}
                
                # 값 컬럼 확인
                if value_column not in df.columns:
                    return {"error": f"값 컬럼 '{value_column}'을 찾을 수 없습니다."}
                
                # 시계열 데이터 정리
                ts_data = df[value_column].dropna()
                
                return {
                    "success": True,
                    "data_points": len(ts_data),
                    "date_range": {
                        "start": str(ts_data.index.min()),
                        "end": str(ts_data.index.max())
                    },
                    "frequency": pd.infer_freq(ts_data.index),
                    "statistics": {
                        "mean": float(ts_data.mean()),
                        "std": float(ts_data.std()),
                        "min": float(ts_data.min()),
                        "max": float(ts_data.max())
                    },
                    "missing_values": int(ts_data.isnull().sum())
                }
                
            except Exception as e:
                return {"error": f"데이터 로드 실패: {str(e)}"}
        
        @self.mcp.tool
        async def analyze_trends(data: List[Dict], value_column: str = "consumption") -> Dict[str, Any]:
            """
            시계열 데이터의 트렌드를 분석합니다.
            
            Args:
                data: 시계열 데이터 (datetime, value 형태의 딕셔너리 리스트)
                value_column: 값 컬럼명
                
            Returns:
                트렌드 분석 결과
            """
            try:
                # 데이터를 DataFrame으로 변환
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                if len(ts_data) < 10:
                    return {"error": "트렌드 분석을 위해서는 최소 10개의 데이터 포인트가 필요합니다."}
                
                # 선형 트렌드 분석
                x = np.arange(len(ts_data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, ts_data.values)
                
                # 계절성 분석
                decomposition = seasonal_decompose(ts_data, model='additive', period=24)
                
                # 정상성 검정 (ADF 테스트)
                adf_result = adfuller(ts_data.dropna())
                
                # KPSS 테스트
                kpss_result = kpss(ts_data.dropna(), regression='c')
                
                return {
                    "success": True,
                    "trend_analysis": {
                        "slope": float(slope),
                        "intercept": float(intercept),
                        "r_squared": float(r_value ** 2),
                        "p_value": float(p_value),
                        "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                    },
                    "seasonality": {
                        "trend_strength": float(np.var(decomposition.trend.dropna())),
                        "seasonal_strength": float(np.var(decomposition.seasonal.dropna())),
                        "residual_strength": float(np.var(decomposition.resid.dropna()))
                    },
                    "stationarity_tests": {
                        "adf_test": {
                            "statistic": float(adf_result[0]),
                            "p_value": float(adf_result[1]),
                            "is_stationary": adf_result[1] < 0.05
                        },
                        "kpss_test": {
                            "statistic": float(kpss_result[0]),
                            "p_value": float(kpss_result[1]),
                            "is_stationary": kpss_result[1] > 0.05
                        }
                    }
                }
                
            except Exception as e:
                return {"error": f"트렌드 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def detect_anomalies(data: List[Dict], value_column: str = "consumption", 
                                 method: str = "iqr", threshold: float = 1.5) -> Dict[str, Any]:
            """
            시계열 데이터에서 이상치를 탐지합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                method: 이상치 탐지 방법 ("iqr", "zscore", "isolation_forest")
                threshold: 임계값
                
            Returns:
                이상치 탐지 결과
            """
            try:
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                anomalies = []
                
                if method == "iqr":
                    Q1 = ts_data.quantile(0.25)
                    Q3 = ts_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    anomaly_mask = (ts_data < lower_bound) | (ts_data > upper_bound)
                    anomalies = ts_data[anomaly_mask].to_dict()
                    
                elif method == "zscore":
                    z_scores = np.abs(stats.zscore(ts_data))
                    anomaly_mask = z_scores > threshold
                    anomalies = ts_data[anomaly_mask].to_dict()
                    
                elif method == "isolation_forest":
                    from sklearn.ensemble import IsolationForest
                    
                    # 2D 배열로 변환 (시간 인덱스와 값)
                    X = np.column_stack([np.arange(len(ts_data)), ts_data.values])
                    
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    anomaly_mask = iso_forest.fit_predict(X) == -1
                    anomalies = ts_data[anomaly_mask].to_dict()
                
                else:
                    return {"error": f"지원하지 않는 이상치 탐지 방법입니다: {method}"}
                
                return {
                    "success": True,
                    "method": method,
                    "threshold": threshold,
                    "total_points": len(ts_data),
                    "anomaly_count": len(anomalies),
                    "anomaly_percentage": len(anomalies) / len(ts_data) * 100,
                    "anomalies": {str(k): v for k, v in anomalies.items()}
                }
                
            except Exception as e:
                return {"error": f"이상치 탐지 실패: {str(e)}"}
        
        @self.mcp.tool
        async def calculate_energy_metrics(data: List[Dict], value_column: str = "consumption") -> Dict[str, Any]:
            """
            에너지 데이터의 주요 지표를 계산합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                
            Returns:
                에너지 지표 계산 결과
            """
            try:
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                # 기본 통계
                mean_consumption = ts_data.mean()
                peak_consumption = ts_data.max()
                min_consumption = ts_data.min()
                
                # 피크 시간대 분석
                peak_hour = ts_data.idxmax().hour
                peak_day = ts_data.idxmax().date()
                
                # 일별 집계
                daily_consumption = ts_data.resample('D').sum()
                daily_mean = daily_consumption.mean()
                daily_peak = daily_consumption.max()
                
                # 주간 패턴 분석
                ts_data_with_hour = ts_data.copy()
                ts_data_with_hour.index = pd.to_datetime(ts_data_with_hour.index)
                hourly_pattern = ts_data_with_hour.groupby(ts_data_with_hour.index.hour).mean()
                
                # 변동성 분석
                coefficient_of_variation = ts_data.std() / ts_data.mean()
                
                # 효율성 지표 (가정: 이상적인 소비량이 평균의 80%라고 가정)
                ideal_consumption = mean_consumption * 0.8
                efficiency = (ideal_consumption / mean_consumption) * 100
                
                return {
                    "success": True,
                    "basic_metrics": {
                        "mean_consumption": float(mean_consumption),
                        "peak_consumption": float(peak_consumption),
                        "min_consumption": float(min_consumption),
                        "coefficient_of_variation": float(coefficient_of_variation)
                    },
                    "peak_analysis": {
                        "peak_hour": int(peak_hour),
                        "peak_day": str(peak_day),
                        "peak_value": float(peak_consumption)
                    },
                    "daily_metrics": {
                        "daily_mean": float(daily_mean),
                        "daily_peak": float(daily_peak),
                        "total_days": len(daily_consumption)
                    },
                    "efficiency_metrics": {
                        "efficiency_percentage": float(efficiency),
                        "ideal_consumption": float(ideal_consumption),
                        "actual_consumption": float(mean_consumption)
                    },
                    "hourly_pattern": {str(hour): float(value) for hour, value in hourly_pattern.items()}
                }
                
            except Exception as e:
                return {"error": f"에너지 지표 계산 실패: {str(e)}"}

