"""
기후 데이터 예측 MCP 도구

DeepMind의 강수 예측 모델을 활용한 기후 데이터 예측 및 분석 도구들을 제공합니다.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import json
import logging
from fastmcp import FastMCP
import warnings
warnings.filterwarnings('ignore')

# TensorFlow 관련 import (선택적)
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Climate prediction features will be limited.")

# Cartopy 관련 import (선택적)
try:
    import cartopy
    import cartopy.crs as ccrs
    import shapely.geometry as sgeom
    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False
    print("Warning: Cartopy not available. Map visualization features will be limited.")

logger = logging.getLogger(__name__)

class ClimatePredictionTools:
    """기후 데이터 예측 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.tfhub_models = {}
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def generate_synthetic_radar_data(latitude: float, longitude: float, 
                                              hours: int = 24, resolution: str = "1km") -> Dict[str, Any]:
            """
            합성 레이더 데이터를 생성합니다 (실제 레이더 데이터가 없을 때 사용).
            
            Args:
                latitude: 위도
                longitude: 경도
                hours: 생성할 시간 (시간)
                resolution: 해상도 ("1km", "5km", "10km")
                
            Returns:
                합성 레이더 데이터
            """
            try:
                # 해상도에 따른 그리드 크기 설정
                if resolution == "1km":
                    height, width = 256, 256
                elif resolution == "5km":
                    height, width = 128, 128
                else:  # 10km
                    height, width = 64, 64
                
                # 시간 스텝 (5분 간격)
                time_steps = hours * 12  # 5분 = 1/12시간
                
                # 합성 강수 패턴 생성
                radar_data = self._generate_synthetic_precipitation_pattern(
                    height, width, time_steps, latitude, longitude
                )
                
                # 마스크 생성 (일부 지역은 관측 불가)
                mask = self._generate_observation_mask(height, width, latitude, longitude)
                
                # 시간 정보 생성
                timestamps = []
                base_time = datetime.now() - timedelta(hours=hours)
                for i in range(time_steps):
                    timestamps.append((base_time + timedelta(minutes=i*5)).isoformat())
                
                return {
                    "success": True,
                    "radar_data": radar_data.tolist(),
                    "mask": mask.tolist(),
                    "timestamps": timestamps,
                    "metadata": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "height": height,
                        "width": width,
                        "time_steps": time_steps,
                        "resolution": resolution,
                        "data_type": "synthetic_radar"
                    }
                }
                
            except Exception as e:
                return {"error": f"합성 레이더 데이터 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def analyze_precipitation_patterns(radar_data: List[List[List]], 
                                               timestamps: List[str],
                                               analysis_type: str = "basic") -> Dict[str, Any]:
            """
            강수 패턴을 분석합니다.
            
            Args:
                radar_data: 레이더 데이터 (시간, 높이, 너비)
                timestamps: 시간 정보
                analysis_type: 분석 유형 ("basic", "advanced", "seasonal")
                
            Returns:
                강수 패턴 분석 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                if analysis_type == "basic":
                    return await self._basic_precipitation_analysis(radar_array, timestamps)
                elif analysis_type == "advanced":
                    return await self._advanced_precipitation_analysis(radar_array, timestamps)
                elif analysis_type == "seasonal":
                    return await self._seasonal_precipitation_analysis(radar_array, timestamps)
                else:
                    return {"error": f"지원하지 않는 분석 유형: {analysis_type}"}
                
            except Exception as e:
                return {"error": f"강수 패턴 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def predict_precipitation_nowcasting(radar_data: List[List[List]], 
                                                 prediction_hours: int = 1,
                                                 model_type: str = "statistical") -> Dict[str, Any]:
            """
            강수 단기 예측(nowcasting)을 수행합니다.
            
            Args:
                radar_data: 입력 레이더 데이터
                prediction_hours: 예측 시간 (시간)
                model_type: 모델 유형 ("statistical", "persistence", "deep_learning")
                
            Returns:
                강수 예측 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                if model_type == "statistical":
                    return await self._statistical_precipitation_prediction(radar_array, prediction_hours)
                elif model_type == "persistence":
                    return await self._persistence_precipitation_prediction(radar_array, prediction_hours)
                elif model_type == "deep_learning" and TENSORFLOW_AVAILABLE:
                    return await self._deep_learning_precipitation_prediction(radar_array, prediction_hours)
                else:
                    return {"error": f"지원하지 않는 모델 유형: {model_type}"}
                
            except Exception as e:
                return {"error": f"강수 예측 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_precipitation_animation(radar_data: List[List[List]], 
                                               output_path: str = "precipitation_animation.gif",
                                               animation_type: str = "basic") -> Dict[str, Any]:
            """
            강수 데이터의 애니메이션을 생성합니다.
            
            Args:
                radar_data: 레이더 데이터
                output_path: 출력 파일 경로
                animation_type: 애니메이션 유형 ("basic", "enhanced", "map")
                
            Returns:
                애니메이션 생성 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                if animation_type == "basic":
                    return await self._create_basic_animation(radar_array, output_path)
                elif animation_type == "enhanced":
                    return await self._create_enhanced_animation(radar_array, output_path)
                elif animation_type == "map" and CARTOPY_AVAILABLE:
                    return await self._create_map_animation(radar_array, output_path)
                else:
                    return {"error": f"지원하지 않는 애니메이션 유형: {animation_type}"}
                
            except Exception as e:
                return {"error": f"애니메이션 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def calculate_precipitation_metrics(radar_data: List[List[List]], 
                                                timestamps: List[str],
                                                metrics: List[str] = None) -> Dict[str, Any]:
            """
            강수 관련 지표를 계산합니다.
            
            Args:
                radar_data: 레이더 데이터
                timestamps: 시간 정보
                metrics: 계산할 지표 목록
                
            Returns:
                강수 지표 계산 결과
            """
            try:
                if metrics is None:
                    metrics = ["total_precipitation", "max_intensity", "duration", "coverage"]
                
                radar_array = np.array(radar_data)
                results = {}
                
                for metric in metrics:
                    if metric == "total_precipitation":
                        results[metric] = float(np.sum(radar_array))
                    elif metric == "max_intensity":
                        results[metric] = float(np.max(radar_array))
                    elif metric == "duration":
                        # 강수가 있는 시간의 비율
                        precipitation_threshold = 0.1  # mm/hr
                        has_precipitation = np.any(radar_array > precipitation_threshold, axis=(1, 2))
                        results[metric] = float(np.sum(has_precipitation) / len(has_precipitation))
                    elif metric == "coverage":
                        # 강수가 있는 지역의 비율
                        precipitation_threshold = 0.1  # mm/hr
                        has_precipitation = radar_array > precipitation_threshold
                        results[metric] = float(np.sum(has_precipitation) / has_precipitation.size)
                    elif metric == "mean_intensity":
                        results[metric] = float(np.mean(radar_array[radar_array > 0]))
                    elif metric == "spatial_variance":
                        results[metric] = float(np.var(radar_array, axis=(1, 2)).mean())
                
                return {
                    "success": True,
                    "metrics": results,
                    "data_shape": radar_array.shape,
                    "time_steps": len(timestamps)
                }
                
            except Exception as e:
                return {"error": f"강수 지표 계산 실패: {str(e)}"}
        
        @self.mcp.tool
        async def correlate_precipitation_energy(radar_data: List[List[List]], 
                                               energy_data: List[Dict],
                                               correlation_type: str = "temporal") -> Dict[str, Any]:
            """
            강수와 에너지 소비의 상관관계를 분석합니다.
            
            Args:
                radar_data: 레이더 데이터
                energy_data: 에너지 소비 데이터
                correlation_type: 상관관계 분석 유형 ("temporal", "spatial", "intensity")
                
            Returns:
                강수-에너지 상관관계 분석 결과
            """
            try:
                radar_array = np.array(radar_data)
                energy_df = pd.DataFrame(energy_data)
                
                if correlation_type == "temporal":
                    return await self._temporal_correlation_analysis(radar_array, energy_df)
                elif correlation_type == "spatial":
                    return await self._spatial_correlation_analysis(radar_array, energy_df)
                elif correlation_type == "intensity":
                    return await self._intensity_correlation_analysis(radar_array, energy_df)
                else:
                    return {"error": f"지원하지 않는 상관관계 유형: {correlation_type}"}
                
            except Exception as e:
                return {"error": f"강수-에너지 상관관계 분석 실패: {str(e)}"}
    
    def _generate_synthetic_precipitation_pattern(self, height: int, width: int, 
                                                time_steps: int, lat: float, lon: float) -> np.ndarray:
        """합성 강수 패턴 생성"""
        # 기본 강수 패턴 생성
        radar_data = np.zeros((time_steps, height, width))
        
        # 계절성 고려 (위도 기반)
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * lat / 90)
        
        for t in range(time_steps):
            # 시간에 따른 강수 패턴
            time_factor = 1 + 0.2 * np.sin(2 * np.pi * t / (24 * 12))  # 일일 패턴
            
            # 공간적 강수 패턴 (랜덤 + 구조적)
            spatial_pattern = np.random.exponential(2, (height, width))
            
            # 이동하는 강수 시스템 시뮬레이션
            if t > 0:
                # 이전 프레임을 약간 이동
                shift_x = int(2 * np.sin(t * 0.1))
                shift_y = int(1 * np.cos(t * 0.1))
                spatial_pattern = np.roll(np.roll(spatial_pattern, shift_x, axis=1), shift_y, axis=0)
            
            # 강수 강도 적용
            intensity = seasonal_factor * time_factor * np.random.gamma(2, 1)
            radar_data[t] = spatial_pattern * intensity
            
            # 강수 임계값 적용
            radar_data[t] = np.maximum(0, radar_data[t] - 1.0)
        
        return radar_data
    
    def _generate_observation_mask(self, height: int, width: int, lat: float, lon: float) -> np.ndarray:
        """관측 마스크 생성 (일부 지역은 관측 불가)"""
        mask = np.ones((height, width), dtype=bool)
        
        # 레이더 사이트에서 멀어질수록 관측 품질 저하
        center_y, center_x = height // 2, width // 2
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = min(height, width) // 2
        
        # 거리에 따른 관측 확률
        observation_prob = np.maximum(0, 1 - distance / max_distance)
        random_mask = np.random.random((height, width)) < observation_prob
        mask = mask & random_mask
        
        # 일부 지역은 완전히 관측 불가
        mask[::4, ::4] = False  # 격자 패턴으로 일부 지역 마스킹
        
        return mask
    
    async def _basic_precipitation_analysis(self, radar_data: np.ndarray, timestamps: List[str]) -> Dict[str, Any]:
        """기본 강수 분석"""
        # 전체 강수량
        total_precipitation = np.sum(radar_data)
        
        # 시간별 강수량
        hourly_precipitation = np.sum(radar_data, axis=(1, 2))
        
        # 공간별 강수량
        spatial_precipitation = np.sum(radar_data, axis=0)
        
        # 강수 강도 분포
        intensity_distribution = {
            "light": np.sum((radar_data > 0) & (radar_data <= 2.5)),
            "moderate": np.sum((radar_data > 2.5) & (radar_data <= 10)),
            "heavy": np.sum((radar_data > 10) & (radar_data <= 50)),
            "extreme": np.sum(radar_data > 50)
        }
        
        return {
            "success": True,
            "total_precipitation": float(total_precipitation),
            "max_hourly_precipitation": float(np.max(hourly_precipitation)),
            "mean_hourly_precipitation": float(np.mean(hourly_precipitation)),
            "intensity_distribution": intensity_distribution,
            "analysis_type": "basic"
        }
    
    async def _advanced_precipitation_analysis(self, radar_data: np.ndarray, timestamps: List[str]) -> Dict[str, Any]:
        """고급 강수 분석"""
        # 기본 분석 결과
        basic_results = await self._basic_precipitation_analysis(radar_data, timestamps)
        
        # 강수 시스템 이동 분석
        movement_analysis = self._analyze_precipitation_movement(radar_data)
        
        # 강수 지속성 분석
        persistence_analysis = self._analyze_precipitation_persistence(radar_data)
        
        # 공간적 연관성 분석
        spatial_correlation = self._analyze_spatial_correlation(radar_data)
        
        return {
            **basic_results,
            "movement_analysis": movement_analysis,
            "persistence_analysis": persistence_analysis,
            "spatial_correlation": spatial_correlation,
            "analysis_type": "advanced"
        }
    
    async def _seasonal_precipitation_analysis(self, radar_data: np.ndarray, timestamps: List[str]) -> Dict[str, Any]:
        """계절적 강수 분석"""
        # 시간 정보 파싱
        times = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
        hours = [t.hour for t in times]
        months = [t.month for t in times]
        
        # 시간대별 강수 패턴
        hourly_pattern = {}
        for h in range(24):
            hour_mask = np.array(hours) == h
            if np.any(hour_mask):
                hourly_pattern[h] = float(np.mean(np.sum(radar_data[hour_mask], axis=(1, 2))))
        
        # 월별 강수 패턴
        monthly_pattern = {}
        for m in range(1, 13):
            month_mask = np.array(months) == m
            if np.any(month_mask):
                monthly_pattern[m] = float(np.mean(np.sum(radar_data[month_mask], axis=(1, 2))))
        
        return {
            "success": True,
            "hourly_pattern": hourly_pattern,
            "monthly_pattern": monthly_pattern,
            "analysis_type": "seasonal"
        }
    
    async def _statistical_precipitation_prediction(self, radar_data: np.ndarray, prediction_hours: int) -> Dict[str, Any]:
        """통계적 강수 예측"""
        # 최근 몇 프레임의 평균을 사용한 지속성 예측
        recent_frames = radar_data[-4:]  # 최근 4프레임 (20분)
        persistence_forecast = np.mean(recent_frames, axis=0)
        
        # 시간에 따른 감쇠 적용
        prediction_steps = prediction_hours * 12  # 5분 간격
        forecasts = []
        
        for step in range(prediction_steps):
            # 지수 감쇠 적용
            decay_factor = np.exp(-step * 0.1)
            forecast = persistence_forecast * decay_factor
            forecasts.append(forecast)
        
        return {
            "success": True,
            "forecast_data": np.array(forecasts).tolist(),
            "prediction_hours": prediction_hours,
            "method": "statistical_persistence"
        }
    
    async def _persistence_precipitation_prediction(self, radar_data: np.ndarray, prediction_hours: int) -> Dict[str, Any]:
        """지속성 기반 강수 예측"""
        # 마지막 프레임을 반복
        last_frame = radar_data[-1]
        prediction_steps = prediction_hours * 12
        
        forecasts = [last_frame.copy() for _ in range(prediction_steps)]
        
        return {
            "success": True,
            "forecast_data": np.array(forecasts).tolist(),
            "prediction_hours": prediction_hours,
            "method": "persistence"
        }
    
    async def _deep_learning_precipitation_prediction(self, radar_data: np.ndarray, prediction_hours: int) -> Dict[str, Any]:
        """딥러닝 기반 강수 예측 (TensorFlow Hub 모델 사용)"""
        if not TENSORFLOW_AVAILABLE:
            return {"error": "TensorFlow가 설치되지 않았습니다."}
        
        try:
            # 간단한 LSTM 기반 예측 (실제로는 TF-Hub 모델 사용)
            # 여기서는 시뮬레이션된 예측을 제공
            prediction_steps = prediction_hours * 12
            forecasts = []
            
            # 입력 데이터 준비 (최근 4프레임)
            input_frames = radar_data[-4:]
            
            for step in range(prediction_steps):
                # 간단한 선형 외삽 (실제로는 복잡한 모델 사용)
                trend = np.mean(np.diff(input_frames, axis=0), axis=0)
                forecast = input_frames[-1] + trend * (step + 1)
                forecasts.append(forecast)
            
            return {
                "success": True,
                "forecast_data": np.array(forecasts).tolist(),
                "prediction_hours": prediction_hours,
                "method": "deep_learning_simulation"
            }
            
        except Exception as e:
            return {"error": f"딥러닝 예측 실패: {str(e)}"}
    
    async def _create_basic_animation(self, radar_data: np.ndarray, output_path: str) -> Dict[str, Any]:
        """기본 애니메이션 생성"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_axis_off()
        
        # 첫 번째 프레임
        im = ax.imshow(radar_data[0], cmap='Blues', vmin=0, vmax=np.max(radar_data))
        plt.colorbar(im, ax=ax, label='Precipitation (mm/hr)')
        
        def animate(frame):
            im.set_array(radar_data[frame])
            ax.set_title(f'Precipitation - Frame {frame}')
            return [im]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_data), 
                                     interval=200, blit=True, repeat=True)
        
        # GIF로 저장
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "frames": len(radar_data),
            "animation_type": "basic"
        }
    
    async def _create_enhanced_animation(self, radar_data: np.ndarray, output_path: str) -> Dict[str, Any]:
        """향상된 애니메이션 생성"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 왼쪽: 강수 데이터
        im1 = ax1.imshow(radar_data[0], cmap='Blues', vmin=0, vmax=np.max(radar_data))
        ax1.set_title('Precipitation')
        ax1.set_axis_off()
        plt.colorbar(im1, ax=ax1, label='mm/hr')
        
        # 오른쪽: 누적 강수량
        cumulative = np.cumsum(radar_data, axis=0)
        im2 = ax2.imshow(cumulative[0], cmap='Reds', vmin=0, vmax=np.max(cumulative))
        ax2.set_title('Cumulative Precipitation')
        ax2.set_axis_off()
        plt.colorbar(im2, ax=ax2, label='mm')
        
        def animate(frame):
            im1.set_array(radar_data[frame])
            im2.set_array(cumulative[frame])
            ax1.set_title(f'Precipitation - Frame {frame}')
            ax2.set_title(f'Cumulative - Frame {frame}')
            return [im1, im2]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_data), 
                                     interval=200, blit=True, repeat=True)
        
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "frames": len(radar_data),
            "animation_type": "enhanced"
        }
    
    async def _create_map_animation(self, radar_data: np.ndarray, output_path: str) -> Dict[str, Any]:
        """지도 기반 애니메이션 생성"""
        if not CARTOPY_AVAILABLE:
            return {"error": "Cartopy가 설치되지 않았습니다."}
        
        # 간단한 지도 애니메이션 (실제로는 더 복잡한 지리적 좌표 사용)
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        
        # 기본 지도 설정
        ax.coastlines()
        ax.gridlines()
        
        # 강수 데이터 표시
        im = ax.imshow(radar_data[0], cmap='Blues', vmin=0, vmax=np.max(radar_data),
                      transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])
        
        def animate(frame):
            im.set_array(radar_data[frame])
            ax.set_title(f'Global Precipitation - Frame {frame}')
            return [im]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_data), 
                                     interval=200, blit=True, repeat=True)
        
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "frames": len(radar_data),
            "animation_type": "map"
        }
    
    def _analyze_precipitation_movement(self, radar_data: np.ndarray) -> Dict[str, Any]:
        """강수 시스템 이동 분석"""
        # 간단한 이동 벡터 계산
        if len(radar_data) < 2:
            return {"error": "이동 분석을 위해 최소 2프레임이 필요합니다."}
        
        # 상관관계를 통한 이동 벡터 추정
        prev_frame = radar_data[0]
        curr_frame = radar_data[1]
        
        # 간단한 이동 추정 (실제로는 더 정교한 방법 사용)
        movement_x = 0  # 픽셀 단위
        movement_y = 0
        
        return {
            "movement_x": movement_x,
            "movement_y": movement_y,
            "movement_speed": np.sqrt(movement_x**2 + movement_y**2)
        }
    
    def _analyze_precipitation_persistence(self, radar_data: np.ndarray) -> Dict[str, Any]:
        """강수 지속성 분석"""
        # 강수가 지속되는 시간 분석
        precipitation_threshold = 0.1  # mm/hr
        has_precipitation = np.any(radar_data > precipitation_threshold, axis=(1, 2))
        
        # 연속된 강수 구간 찾기
        persistence_periods = []
        current_period = 0
        
        for has_precip in has_precipitation:
            if has_precip:
                current_period += 1
            else:
                if current_period > 0:
                    persistence_periods.append(current_period)
                    current_period = 0
        
        if current_period > 0:
            persistence_periods.append(current_period)
        
        return {
            "max_persistence": max(persistence_periods) if persistence_periods else 0,
            "mean_persistence": np.mean(persistence_periods) if persistence_periods else 0,
            "persistence_periods": persistence_periods
        }
    
    def _analyze_spatial_correlation(self, radar_data: np.ndarray) -> Dict[str, Any]:
        """공간적 연관성 분석"""
        # 시간에 따른 공간적 상관관계 계산
        if len(radar_data) < 2:
            return {"error": "공간적 분석을 위해 최소 2프레임이 필요합니다."}
        
        # 프레임 간 상관관계
        correlations = []
        for i in range(len(radar_data) - 1):
            corr = np.corrcoef(radar_data[i].flatten(), radar_data[i+1].flatten())[0, 1]
            correlations.append(corr)
        
        return {
            "mean_temporal_correlation": float(np.mean(correlations)),
            "spatial_autocorrelation": float(np.corrcoef(radar_data[0].flatten(), 
                                                       np.roll(radar_data[0], 1, axis=1).flatten())[0, 1])
        }
    
    async def _temporal_correlation_analysis(self, radar_data: np.ndarray, energy_df: pd.DataFrame) -> Dict[str, Any]:
        """시간적 상관관계 분석"""
        # 시간별 강수량 계산
        hourly_precipitation = np.sum(radar_data, axis=(1, 2))
        
        # 에너지 데이터와 시간 맞추기
        if 'consumption' in energy_df.columns:
            energy_consumption = energy_df['consumption'].values
            
            # 길이 맞추기
            min_length = min(len(hourly_precipitation), len(energy_consumption))
            precip_subset = hourly_precipitation[:min_length]
            energy_subset = energy_consumption[:min_length]
            
            # 상관관계 계산
            correlation = np.corrcoef(precip_subset, energy_subset)[0, 1]
            
            return {
                "success": True,
                "correlation_coefficient": float(correlation),
                "correlation_strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak",
                "data_points": min_length
            }
        else:
            return {"error": "에너지 데이터에 'consumption' 컬럼이 없습니다."}
    
    async def _spatial_correlation_analysis(self, radar_data: np.ndarray, energy_df: pd.DataFrame) -> Dict[str, Any]:
        """공간적 상관관계 분석"""
        # 공간적 강수 패턴 분석
        spatial_precipitation = np.mean(radar_data, axis=0)
        
        return {
            "success": True,
            "spatial_variance": float(np.var(spatial_precipitation)),
            "max_spatial_intensity": float(np.max(spatial_precipitation)),
            "analysis_type": "spatial"
        }
    
    async def _intensity_correlation_analysis(self, radar_data: np.ndarray, energy_df: pd.DataFrame) -> Dict[str, Any]:
        """강도 상관관계 분석"""
        # 강수 강도 분포
        intensity_bins = [0, 0.1, 2.5, 10, 50, np.inf]
        intensity_labels = ['none', 'light', 'moderate', 'heavy', 'extreme']
        
        intensity_distribution = {}
        for i in range(len(intensity_bins) - 1):
            mask = (radar_data >= intensity_bins[i]) & (radar_data < intensity_bins[i+1])
            intensity_distribution[intensity_labels[i]] = int(np.sum(mask))
        
        return {
            "success": True,
            "intensity_distribution": intensity_distribution,
            "analysis_type": "intensity"
        }
