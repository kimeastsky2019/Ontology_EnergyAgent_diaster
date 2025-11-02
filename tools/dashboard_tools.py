"""
대시보드 및 가시화 도구

에너지 데이터 분석 결과를 시각화하고 대시보드를 생성합니다.
"""

import pandas as pd
import numpy as np
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import io
import matplotlib
matplotlib.use('Agg')  # GUI 없는 환경에서 사용
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from fastmcp import FastMCP

class DashboardTools:
    """대시보드 및 가시화 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def create_time_series_chart(data: List[Dict], value_column: str = "consumption",
                                         chart_type: str = "line", title: str = "Energy Consumption Over Time") -> Dict[str, Any]:
            """
            시계열 데이터를 차트로 시각화합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                chart_type: 차트 유형 ("line", "bar", "area")
                title: 차트 제목
                
            Returns:
                차트 이미지 (base64 인코딩)
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                # Plotly 차트 생성
                fig = go.Figure()
                
                if chart_type == "line":
                    fig.add_trace(go.Scatter(
                        x=ts_data.index,
                        y=ts_data.values,
                        mode='lines',
                        name=value_column,
                        line=dict(color='blue', width=2)
                    ))
                elif chart_type == "bar":
                    fig.add_trace(go.Bar(
                        x=ts_data.index,
                        y=ts_data.values,
                        name=value_column,
                        marker_color='blue'
                    ))
                elif chart_type == "area":
                    fig.add_trace(go.Scatter(
                        x=ts_data.index,
                        y=ts_data.values,
                        mode='lines',
                        fill='tonexty',
                        name=value_column,
                        line=dict(color='blue', width=2)
                    ))
                
                # 차트 레이아웃 설정
                fig.update_layout(
                    title=title,
                    xaxis_title="Time",
                    yaxis_title=value_column,
                    template="plotly_white",
                    width=800,
                    height=400
                )
                
                # JSON으로 변환
                chart_json = fig.to_json()
                
                return {
                    "success": True,
                    "chart_type": chart_type,
                    "chart_data": json.loads(chart_json),
                    "data_points": len(ts_data)
                }
                
            except Exception as e:
                return {"error": f"차트 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_forecast_chart(historical_data: List[Dict], forecast_data: List[Dict],
                                      value_column: str = "consumption") -> Dict[str, Any]:
            """
            과거 데이터와 예측 데이터를 함께 표시하는 차트를 생성합니다.
            
            Args:
                historical_data: 과거 데이터
                forecast_data: 예측 데이터
                value_column: 값 컬럼명
                
            Returns:
                예측 차트 데이터
            """
            try:
                # 과거 데이터 준비
                hist_df = pd.DataFrame(historical_data)
                hist_df['datetime'] = pd.to_datetime(hist_df['datetime'])
                hist_df = hist_df.set_index('datetime')
                hist_ts = hist_df[value_column].dropna()
                
                # 예측 데이터 준비
                forecast_df = pd.DataFrame(forecast_data)
                forecast_df['datetime'] = pd.to_datetime(forecast_df['datetime'])
                forecast_df = forecast_df.set_index('datetime')
                
                # Plotly 차트 생성
                fig = go.Figure()
                
                # 과거 데이터
                fig.add_trace(go.Scatter(
                    x=hist_ts.index,
                    y=hist_ts.values,
                    mode='lines',
                    name='Historical Data',
                    line=dict(color='blue', width=2)
                ))
                
                # 예측 데이터
                if 'forecast' in forecast_df.columns:
                    fig.add_trace(go.Scatter(
                        x=forecast_df.index,
                        y=forecast_df['forecast'],
                        mode='lines',
                        name='Forecast',
                        line=dict(color='red', width=2, dash='dash')
                    ))
                
                # 신뢰 구간
                if 'lower_bound' in forecast_df.columns and 'upper_bound' in forecast_df.columns:
                    fig.add_trace(go.Scatter(
                        x=forecast_df.index,
                        y=forecast_df['upper_bound'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=forecast_df.index,
                        y=forecast_df['lower_bound'],
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(255,0,0,0.2)',
                        name='Confidence Interval',
                        hoverinfo='skip'
                    ))
                
                # 차트 레이아웃 설정
                fig.update_layout(
                    title="Energy Consumption Forecast",
                    xaxis_title="Time",
                    yaxis_title=value_column,
                    template="plotly_white",
                    width=800,
                    height=400
                )
                
                # JSON으로 변환
                chart_json = fig.to_json()
                
                return {
                    "success": True,
                    "chart_data": json.loads(chart_json),
                    "historical_points": len(hist_ts),
                    "forecast_points": len(forecast_df)
                }
                
            except Exception as e:
                return {"error": f"예측 차트 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_energy_dashboard(data: List[Dict], value_column: str = "consumption") -> Dict[str, Any]:
            """
            에너지 데이터 분석 대시보드를 생성합니다.
            
            Args:
                data: 시계열 데이터
                value_column: 값 컬럼명
                
            Returns:
                대시보드 구성 요소들
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                # 시간별 패턴 분석
                ts_data_with_hour = ts_data.copy()
                ts_data_with_hour.index = pd.to_datetime(ts_data_with_hour.index)
                hourly_pattern = ts_data_with_hour.groupby(ts_data_with_hour.index.hour).mean()
                
                # 일별 패턴 분석
                daily_pattern = ts_data.resample('D').sum()
                
                # 주간 패턴 분석
                weekly_pattern = ts_data.resample('W').mean()
                
                # 서브플롯 생성
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Time Series', 'Hourly Pattern', 'Daily Pattern', 'Weekly Pattern'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                # 1. 시계열 차트
                fig.add_trace(
                    go.Scatter(x=ts_data.index, y=ts_data.values, mode='lines', name='Consumption'),
                    row=1, col=1
                )
                
                # 2. 시간별 패턴
                fig.add_trace(
                    go.Bar(x=hourly_pattern.index, y=hourly_pattern.values, name='Hourly Avg'),
                    row=1, col=2
                )
                
                # 3. 일별 패턴
                fig.add_trace(
                    go.Scatter(x=daily_pattern.index, y=daily_pattern.values, mode='lines', name='Daily Total'),
                    row=2, col=1
                )
                
                # 4. 주간 패턴
                fig.add_trace(
                    go.Scatter(x=weekly_pattern.index, y=weekly_pattern.values, mode='lines', name='Weekly Avg'),
                    row=2, col=2
                )
                
                # 레이아웃 설정
                fig.update_layout(
                    title="Energy Consumption Dashboard",
                    template="plotly_white",
                    height=600,
                    showlegend=False
                )
                
                # JSON으로 변환
                dashboard_json = fig.to_json()
                
                # 주요 통계 계산
                stats = {
                    "total_consumption": float(ts_data.sum()),
                    "average_consumption": float(ts_data.mean()),
                    "peak_consumption": float(ts_data.max()),
                    "min_consumption": float(ts_data.min()),
                    "peak_hour": int(hourly_pattern.idxmax()),
                    "data_points": len(ts_data)
                }
                
                return {
                    "success": True,
                    "dashboard_data": json.loads(dashboard_json),
                    "statistics": stats,
                    "patterns": {
                        "hourly": {str(hour): float(value) for hour, value in hourly_pattern.items()},
                        "daily_avg": float(daily_pattern.mean()),
                        "weekly_avg": float(weekly_pattern.mean())
                    }
                }
                
            except Exception as e:
                return {"error": f"대시보드 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_anomaly_chart(data: List[Dict], anomalies: List[str], 
                                     value_column: str = "consumption") -> Dict[str, Any]:
            """
            이상치가 표시된 시계열 차트를 생성합니다.
            
            Args:
                data: 시계열 데이터
                anomalies: 이상치 날짜/시간 리스트
                value_column: 값 컬럼명
                
            Returns:
                이상치 차트 데이터
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                ts_data = df[value_column].dropna()
                
                # 이상치 마스크 생성
                anomaly_dates = pd.to_datetime(anomalies)
                anomaly_mask = ts_data.index.isin(anomaly_dates)
                
                # 정상 데이터와 이상치 분리
                normal_data = ts_data[~anomaly_mask]
                anomaly_data = ts_data[anomaly_mask]
                
                # Plotly 차트 생성
                fig = go.Figure()
                
                # 정상 데이터
                fig.add_trace(go.Scatter(
                    x=normal_data.index,
                    y=normal_data.values,
                    mode='lines',
                    name='Normal Data',
                    line=dict(color='blue', width=2)
                ))
                
                # 이상치 데이터
                if len(anomaly_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=anomaly_data.index,
                        y=anomaly_data.values,
                        mode='markers',
                        name='Anomalies',
                        marker=dict(color='red', size=8, symbol='x')
                    ))
                
                # 차트 레이아웃 설정
                fig.update_layout(
                    title="Energy Consumption with Anomalies",
                    xaxis_title="Time",
                    yaxis_title=value_column,
                    template="plotly_white",
                    width=800,
                    height=400
                )
                
                # JSON으로 변환
                chart_json = fig.to_json()
                
                return {
                    "success": True,
                    "chart_data": json.loads(chart_json),
                    "total_points": len(ts_data),
                    "anomaly_count": len(anomaly_data),
                    "anomaly_percentage": len(anomaly_data) / len(ts_data) * 100
                }
                
            except Exception as e:
                return {"error": f"이상치 차트 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def export_chart_data(chart_data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
            """
            차트 데이터를 다양한 형식으로 내보냅니다.
            
            Args:
                chart_data: 차트 데이터
                format: 내보내기 형식 ("json", "csv", "html")
                
            Returns:
                내보낸 데이터
            """
            try:
                if format == "json":
                    return {
                        "success": True,
                        "format": format,
                        "data": chart_data
                    }
                
                elif format == "csv":
                    # Plotly 차트에서 데이터 추출하여 CSV로 변환
                    if 'data' in chart_data:
                        csv_data = []
                        for trace in chart_data['data']:
                            if 'x' in trace and 'y' in trace:
                                for x, y in zip(trace['x'], trace['y']):
                                    csv_data.append({
                                        'datetime': x,
                                        'value': y,
                                        'series': trace.get('name', 'unknown')
                                    })
                        
                        df = pd.DataFrame(csv_data)
                        csv_string = df.to_csv(index=False)
                        
                        return {
                            "success": True,
                            "format": format,
                            "data": csv_string
                        }
                
                elif format == "html":
                    # HTML 형태로 차트 데이터 반환
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Energy Analysis Chart</title>
                        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                    </head>
                    <body>
                        <div id="chart"></div>
                        <script>
                            var chartData = {json.dumps(chart_data)};
                            Plotly.newPlot('chart', chartData.data, chartData.layout);
                        </script>
                    </body>
                    </html>
                    """
                    
                    return {
                        "success": True,
                        "format": format,
                        "data": html_content
                    }
                
                else:
                    return {"error": f"지원하지 않는 형식입니다: {format}"}
                
            except Exception as e:
                return {"error": f"차트 데이터 내보내기 실패: {str(e)}"}

