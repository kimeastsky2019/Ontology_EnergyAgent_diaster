"""
기후 데이터 시각화 MCP 도구

기후 및 강수 데이터의 고급 시각화 도구들을 제공합니다.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import os
import logging
from fastmcp import FastMCP
import warnings
warnings.filterwarnings('ignore')

# Cartopy 관련 import (선택적)
try:
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import shapely.geometry as sgeom
    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False
    print("Warning: Cartopy not available. Map visualization features will be limited.")

logger = logging.getLogger(__name__)

class ClimateVisualizationTools:
    """기후 데이터 시각화 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._setup_colormaps()
        self._register_tools()
    
    def _setup_colormaps(self):
        """기후 데이터용 컬러맵 설정"""
        # 강수용 컬러맵
        colors = ['#FFFFFF', '#E6F3FF', '#CCE7FF', '#99D6FF', '#66C2FF', 
                 '#33ADFF', '#0099FF', '#0080CC', '#006699', '#004D66',
                 '#FFFF00', '#FFCC00', '#FF9900', '#FF6600', '#FF3300',
                 '#CC0000', '#990000', '#660000']
        self.precipitation_cmap = LinearSegmentedColormap.from_list('precipitation', colors)
        
        # 온도용 컬러맵
        temp_colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', 
                      '#FF8000', '#FF0000', '#800000']
        self.temperature_cmap = LinearSegmentedColormap.from_list('temperature', temp_colors)
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def create_precipitation_heatmap(radar_data: List[List[List]], 
                                             timestamps: List[str],
                                             output_path: str = "precipitation_heatmap.png",
                                             style: str = "basic") -> Dict[str, Any]:
            """
            강수 데이터의 히트맵을 생성합니다.
            
            Args:
                radar_data: 레이더 데이터
                timestamps: 시간 정보
                output_path: 출력 파일 경로
                style: 시각화 스타일 ("basic", "enhanced", "interactive")
                
            Returns:
                히트맵 생성 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                if style == "basic":
                    return await self._create_basic_heatmap(radar_array, timestamps, output_path)
                elif style == "enhanced":
                    return await self._create_enhanced_heatmap(radar_array, timestamps, output_path)
                elif style == "interactive":
                    return await self._create_interactive_heatmap(radar_array, timestamps, output_path)
                else:
                    return {"error": f"지원하지 않는 스타일: {style}"}
                
            except Exception as e:
                return {"error": f"히트맵 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_precipitation_animation(radar_data: List[List[List]], 
                                               timestamps: List[str],
                                               output_path: str = "precipitation_animation.gif",
                                               animation_style: str = "basic") -> Dict[str, Any]:
            """
            강수 데이터의 애니메이션을 생성합니다.
            
            Args:
                radar_data: 레이더 데이터
                timestamps: 시간 정보
                output_path: 출력 파일 경로
                animation_style: 애니메이션 스타일 ("basic", "enhanced", "map")
                
            Returns:
                애니메이션 생성 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                if animation_style == "basic":
                    return await self._create_basic_animation(radar_array, timestamps, output_path)
                elif animation_style == "enhanced":
                    return await self._create_enhanced_animation(radar_array, timestamps, output_path)
                elif animation_style == "map" and CARTOPY_AVAILABLE:
                    return await self._create_map_animation(radar_array, timestamps, output_path)
                else:
                    return {"error": f"지원하지 않는 애니메이션 스타일: {animation_style}"}
                
            except Exception as e:
                return {"error": f"애니메이션 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_climate_dashboard(radar_data: List[List[List]], 
                                         weather_data: List[Dict] = None,
                                         energy_data: List[Dict] = None,
                                         output_path: str = "climate_dashboard.png") -> Dict[str, Any]:
            """
            기후 데이터 대시보드를 생성합니다.
            
            Args:
                radar_data: 레이더 데이터
                weather_data: 날씨 데이터
                energy_data: 에너지 데이터
                output_path: 출력 파일 경로
                
            Returns:
                대시보드 생성 결과
            """
            try:
                radar_array = np.array(radar_data)
                
                # 대시보드 레이아웃 설정
                fig, axes = plt.subplots(2, 3, figsize=(15, 10))
                fig.suptitle('Climate Data Dashboard', fontsize=16, fontweight='bold')
                
                # 1. 현재 강수 상황
                current_precip = radar_array[-1] if len(radar_array) > 0 else np.zeros((256, 256))
                im1 = axes[0, 0].imshow(current_precip, cmap=self.precipitation_cmap, vmin=0, vmax=20)
                axes[0, 0].set_title('Current Precipitation')
                axes[0, 0].set_axis_off()
                plt.colorbar(im1, ax=axes[0, 0], label='mm/hr')
                
                # 2. 누적 강수량
                cumulative_precip = np.sum(radar_array, axis=0)
                im2 = axes[0, 1].imshow(cumulative_precip, cmap='Reds', vmin=0)
                axes[0, 1].set_title('Cumulative Precipitation')
                axes[0, 1].set_axis_off()
                plt.colorbar(im2, ax=axes[0, 1], label='mm')
                
                # 3. 시간별 강수량
                hourly_precip = np.sum(radar_array, axis=(1, 2))
                axes[0, 2].plot(hourly_precip, 'b-', linewidth=2)
                axes[0, 2].set_title('Hourly Precipitation')
                axes[0, 2].set_xlabel('Time Steps')
                axes[0, 2].set_ylabel('Precipitation (mm)')
                axes[0, 2].grid(True, alpha=0.3)
                
                # 4. 강수 강도 분포
                precip_flat = radar_array.flatten()
                precip_flat = precip_flat[precip_flat > 0]  # 0이 아닌 값만
                if len(precip_flat) > 0:
                    axes[1, 0].hist(precip_flat, bins=50, alpha=0.7, color='blue', edgecolor='black')
                    axes[1, 0].set_title('Precipitation Intensity Distribution')
                    axes[1, 0].set_xlabel('Intensity (mm/hr)')
                    axes[1, 0].set_ylabel('Frequency')
                    axes[1, 0].grid(True, alpha=0.3)
                
                # 5. 날씨 데이터 (있는 경우)
                if weather_data:
                    weather_df = pd.DataFrame(weather_data)
                    if 'temperature' in weather_df.columns:
                        axes[1, 1].plot(weather_df['temperature'], 'r-', linewidth=2, label='Temperature')
                        axes[1, 1].set_title('Temperature')
                        axes[1, 1].set_ylabel('Temperature (°C)')
                        axes[1, 1].grid(True, alpha=0.3)
                        axes[1, 1].legend()
                
                # 6. 에너지 데이터 (있는 경우)
                if energy_data:
                    energy_df = pd.DataFrame(energy_data)
                    if 'consumption' in energy_df.columns:
                        axes[1, 2].plot(energy_df['consumption'], 'g-', linewidth=2, label='Energy Consumption')
                        axes[1, 2].set_title('Energy Consumption')
                        axes[1, 2].set_ylabel('Consumption')
                        axes[1, 2].grid(True, alpha=0.3)
                        axes[1, 2].legend()
                
                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "dashboard_type": "climate_energy",
                    "components": ["precipitation", "weather", "energy"]
                }
                
            except Exception as e:
                return {"error": f"대시보드 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_precipitation_forecast_plot(predicted_data: List[List[List]], 
                                                   ground_truth_data: List[List[List]] = None,
                                                   timestamps: List[str] = None,
                                                   output_path: str = "forecast_plot.png") -> Dict[str, Any]:
            """
            강수 예측 결과를 시각화합니다.
            
            Args:
                predicted_data: 예측된 데이터
                ground_truth_data: 실제 데이터 (선택사항)
                timestamps: 시간 정보
                output_path: 출력 파일 경로
                
            Returns:
                예측 플롯 생성 결과
            """
            try:
                pred_array = np.array(predicted_data)
                
                if ground_truth_data:
                    truth_array = np.array(ground_truth_data)
                    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
                    
                    # 예측 데이터
                    im1 = axes[0].imshow(pred_array[-1], cmap=self.precipitation_cmap, vmin=0, vmax=20)
                    axes[0].set_title('Predicted Precipitation')
                    axes[0].set_axis_off()
                    plt.colorbar(im1, ax=axes[0], label='mm/hr')
                    
                    # 실제 데이터
                    im2 = axes[1].imshow(truth_array[-1], cmap=self.precipitation_cmap, vmin=0, vmax=20)
                    axes[1].set_title('Ground Truth')
                    axes[1].set_axis_off()
                    plt.colorbar(im2, ax=axes[1], label='mm/hr')
                    
                    # 차이 (예측 - 실제)
                    diff = pred_array[-1] - truth_array[-1]
                    im3 = axes[2].imshow(diff, cmap='RdBu_r', vmin=-10, vmax=10)
                    axes[2].set_title('Prediction Error')
                    axes[2].set_axis_off()
                    plt.colorbar(im3, ax=axes[2], label='mm/hr')
                    
                else:
                    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                    im = ax.imshow(pred_array[-1], cmap=self.precipitation_cmap, vmin=0, vmax=20)
                    ax.set_title('Predicted Precipitation')
                    ax.set_axis_off()
                    plt.colorbar(im, ax=ax, label='mm/hr')
                
                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "plot_type": "forecast_comparison" if ground_truth_data else "forecast_only"
                }
                
            except Exception as e:
                return {"error": f"예측 플롯 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_climate_correlation_plot(radar_data: List[List[List]], 
                                                energy_data: List[Dict],
                                                output_path: str = "correlation_plot.png") -> Dict[str, Any]:
            """
            기후 데이터와 에너지 데이터의 상관관계를 시각화합니다.
            
            Args:
                radar_data: 레이더 데이터
                energy_data: 에너지 데이터
                output_path: 출력 파일 경로
                
            Returns:
                상관관계 플롯 생성 결과
            """
            try:
                radar_array = np.array(radar_data)
                energy_df = pd.DataFrame(energy_data)
                
                # 시간별 강수량 계산
                hourly_precip = np.sum(radar_array, axis=(1, 2))
                
                # 에너지 소비 데이터 추출
                if 'consumption' not in energy_df.columns:
                    return {"error": "에너지 데이터에 'consumption' 컬럼이 없습니다."}
                
                energy_consumption = energy_df['consumption'].values
                
                # 데이터 길이 맞추기
                min_length = min(len(hourly_precip), len(energy_consumption))
                precip_subset = hourly_precip[:min_length]
                energy_subset = energy_consumption[:min_length]
                
                # 상관관계 플롯 생성
                fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                fig.suptitle('Climate-Energy Correlation Analysis', fontsize=16, fontweight='bold')
                
                # 1. 시간별 강수량과 에너지 소비
                axes[0, 0].scatter(precip_subset, energy_subset, alpha=0.6, s=50)
                axes[0, 0].set_xlabel('Precipitation (mm)')
                axes[0, 0].set_ylabel('Energy Consumption')
                axes[0, 0].set_title('Precipitation vs Energy Consumption')
                axes[0, 0].grid(True, alpha=0.3)
                
                # 상관계수 계산 및 표시
                correlation = np.corrcoef(precip_subset, energy_subset)[0, 1]
                axes[0, 0].text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                               transform=axes[0, 0].transAxes, fontsize=12,
                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                
                # 2. 시간별 추이
                time_axis = range(min_length)
                ax2_twin = axes[0, 1].twinx()
                line1 = axes[0, 1].plot(time_axis, precip_subset, 'b-', label='Precipitation', linewidth=2)
                line2 = ax2_twin.plot(time_axis, energy_subset, 'r-', label='Energy Consumption', linewidth=2)
                
                axes[0, 1].set_xlabel('Time Steps')
                axes[0, 1].set_ylabel('Precipitation (mm)', color='b')
                ax2_twin.set_ylabel('Energy Consumption', color='r')
                axes[0, 1].set_title('Temporal Trends')
                
                # 범례 통합
                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                axes[0, 1].legend(lines, labels, loc='upper left')
                
                # 3. 강수 강도별 에너지 소비
                precip_bins = np.percentile(precip_subset, [0, 25, 50, 75, 100])
                energy_by_precip = []
                bin_labels = []
                
                for i in range(len(precip_bins) - 1):
                    mask = (precip_subset >= precip_bins[i]) & (precip_subset < precip_bins[i+1])
                    if np.any(mask):
                        energy_by_precip.append(np.mean(energy_subset[mask]))
                        bin_labels.append(f'{precip_bins[i]:.1f}-{precip_bins[i+1]:.1f}')
                
                axes[1, 0].bar(bin_labels, energy_by_precip, alpha=0.7, color='skyblue', edgecolor='black')
                axes[1, 0].set_xlabel('Precipitation Range (mm)')
                axes[1, 0].set_ylabel('Average Energy Consumption')
                axes[1, 0].set_title('Energy Consumption by Precipitation Range')
                axes[1, 0].tick_params(axis='x', rotation=45)
                
                # 4. 히트맵 (시간별 상관관계)
                # 시간 윈도우별 상관관계 계산
                window_size = min(24, min_length // 4)  # 24시간 또는 전체의 1/4
                correlations = []
                time_windows = []
                
                for i in range(0, min_length - window_size, window_size):
                    window_precip = precip_subset[i:i+window_size]
                    window_energy = energy_subset[i:i+window_size]
                    if len(window_precip) > 1 and len(window_energy) > 1:
                        corr = np.corrcoef(window_precip, window_energy)[0, 1]
                        correlations.append(corr)
                        time_windows.append(f'{i}-{i+window_size}')
                
                if correlations:
                    im = axes[1, 1].imshow([correlations], cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
                    axes[1, 1].set_title('Correlation by Time Window')
                    axes[1, 1].set_xlabel('Time Window')
                    axes[1, 1].set_ylabel('Correlation')
                    axes[1, 1].set_xticks(range(len(time_windows)))
                    axes[1, 1].set_xticklabels(time_windows, rotation=45)
                    plt.colorbar(im, ax=axes[1, 1], label='Correlation')
                
                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "correlation_coefficient": float(correlation),
                    "data_points": min_length
                }
                
            except Exception as e:
                return {"error": f"상관관계 플롯 생성 실패: {str(e)}"}
    
    async def _create_basic_heatmap(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """기본 히트맵 생성"""
        # 평균 강수량 히트맵
        mean_precip = np.mean(radar_array, axis=0)
        
        plt.figure(figsize=(10, 8))
        im = plt.imshow(mean_precip, cmap=self.precipitation_cmap, vmin=0, vmax=np.max(mean_precip))
        plt.colorbar(im, label='Precipitation (mm/hr)')
        plt.title('Average Precipitation Pattern')
        plt.axis('off')
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "style": "basic",
            "max_intensity": float(np.max(mean_precip))
        }
    
    async def _create_enhanced_heatmap(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """향상된 히트맵 생성"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Enhanced Precipitation Analysis', fontsize=16, fontweight='bold')
        
        # 1. 평균 강수량
        mean_precip = np.mean(radar_array, axis=0)
        im1 = axes[0, 0].imshow(mean_precip, cmap=self.precipitation_cmap, vmin=0)
        axes[0, 0].set_title('Average Precipitation')
        axes[0, 0].set_axis_off()
        plt.colorbar(im1, ax=axes[0, 0], label='mm/hr')
        
        # 2. 최대 강수량
        max_precip = np.max(radar_array, axis=0)
        im2 = axes[0, 1].imshow(max_precip, cmap=self.precipitation_cmap, vmin=0)
        axes[0, 1].set_title('Maximum Precipitation')
        axes[0, 1].set_axis_off()
        plt.colorbar(im2, ax=axes[0, 1], label='mm/hr')
        
        # 3. 강수 발생 빈도
        precip_frequency = np.mean(radar_array > 0.1, axis=0)  # 0.1 mm/hr 이상인 비율
        im3 = axes[1, 0].imshow(precip_frequency, cmap='Blues', vmin=0, vmax=1)
        axes[1, 0].set_title('Precipitation Frequency')
        axes[1, 0].set_axis_off()
        plt.colorbar(im3, ax=axes[1, 0], label='Frequency')
        
        # 4. 강수 강도 분포
        precip_flat = radar_array.flatten()
        precip_flat = precip_flat[precip_flat > 0]
        if len(precip_flat) > 0:
            axes[1, 1].hist(precip_flat, bins=50, alpha=0.7, color='blue', edgecolor='black')
            axes[1, 1].set_title('Precipitation Intensity Distribution')
            axes[1, 1].set_xlabel('Intensity (mm/hr)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "style": "enhanced",
            "max_intensity": float(np.max(mean_precip))
        }
    
    async def _create_interactive_heatmap(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """인터랙티브 히트맵 생성 (HTML)"""
        # 간단한 HTML 히트맵 생성
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interactive Precipitation Heatmap</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div id="heatmap" style="width:100%;height:600px;"></div>
            <script>
                var data = {{
                    z: {radar_array.tolist()},
                    type: 'heatmap',
                    colorscale: 'Blues',
                    showscale: true
                }};
                var layout = {{
                    title: 'Interactive Precipitation Heatmap',
                    xaxis: {{title: 'Longitude'}},
                    yaxis: {{title: 'Latitude'}}
                }};
                Plotly.newPlot('heatmap', [data], layout);
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return {
            "success": True,
            "output_path": output_path,
            "style": "interactive",
            "format": "html"
        }
    
    async def _create_basic_animation(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """기본 애니메이션 생성"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_axis_off()
        
        im = ax.imshow(radar_array[0], cmap=self.precipitation_cmap, vmin=0, vmax=np.max(radar_array))
        plt.colorbar(im, ax=ax, label='Precipitation (mm/hr)')
        
        def animate(frame):
            im.set_array(radar_array[frame])
            ax.set_title(f'Precipitation - {timestamps[frame] if frame < len(timestamps) else f"Frame {frame}"}')
            return [im]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_array), 
                                     interval=200, blit=True, repeat=True)
        
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "animation_style": "basic",
            "frames": len(radar_array)
        }
    
    async def _create_enhanced_animation(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """향상된 애니메이션 생성"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 왼쪽: 강수 데이터
        im1 = ax1.imshow(radar_array[0], cmap=self.precipitation_cmap, vmin=0, vmax=np.max(radar_array))
        ax1.set_title('Precipitation')
        ax1.set_axis_off()
        plt.colorbar(im1, ax=ax1, label='mm/hr')
        
        # 오른쪽: 누적 강수량
        cumulative = np.cumsum(radar_array, axis=0)
        im2 = ax2.imshow(cumulative[0], cmap='Reds', vmin=0, vmax=np.max(cumulative))
        ax2.set_title('Cumulative Precipitation')
        ax2.set_axis_off()
        plt.colorbar(im2, ax=ax2, label='mm')
        
        def animate(frame):
            im1.set_array(radar_array[frame])
            im2.set_array(cumulative[frame])
            ax1.set_title(f'Precipitation - {timestamps[frame] if frame < len(timestamps) else f"Frame {frame}"}')
            ax2.set_title(f'Cumulative - {timestamps[frame] if frame < len(timestamps) else f"Frame {frame}"}')
            return [im1, im2]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_array), 
                                     interval=200, blit=True, repeat=True)
        
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "animation_style": "enhanced",
            "frames": len(radar_array)
        }
    
    async def _create_map_animation(self, radar_array: np.ndarray, timestamps: List[str], output_path: str) -> Dict[str, Any]:
        """지도 기반 애니메이션 생성"""
        if not CARTOPY_AVAILABLE:
            return {"error": "Cartopy가 설치되지 않았습니다."}
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        
        # 기본 지도 설정
        ax.coastlines()
        ax.gridlines()
        ax.add_feature(cfeature.BORDERS)
        
        # 강수 데이터 표시
        im = ax.imshow(radar_array[0], cmap=self.precipitation_cmap, vmin=0, vmax=np.max(radar_array),
                      transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])
        
        def animate(frame):
            im.set_array(radar_array[frame])
            ax.set_title(f'Global Precipitation - {timestamps[frame] if frame < len(timestamps) else f"Frame {frame}"}')
            return [im]
        
        anim = animation.FuncAnimation(fig, animate, frames=len(radar_array), 
                                     interval=200, blit=True, repeat=True)
        
        anim.save(output_path, writer='pillow', fps=5)
        plt.close()
        
        return {
            "success": True,
            "output_path": output_path,
            "animation_style": "map",
            "frames": len(radar_array)
        }
