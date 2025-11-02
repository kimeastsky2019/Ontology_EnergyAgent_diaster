"""
날씨 데이터 수집 도구

에너지 소비와 관련된 날씨 데이터를 수집하고 분석합니다.
"""

import httpx
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from fastmcp import FastMCP

class WeatherTools:
    """날씨 데이터 수집 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def get_current_weather(latitude: float, longitude: float, 
                                    api_key: str = "") -> Dict[str, Any]:
            """
            현재 날씨 정보를 가져옵니다.
            
            Args:
                latitude: 위도
                longitude: 경도
                api_key: OpenWeatherMap API 키
                
            Returns:
                현재 날씨 정보
            """
            try:
                if not api_key:
                    return {"error": "OpenWeatherMap API 키가 필요합니다."}
                
                url = f"https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                    "units": "metric"
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                # 에너지 분석에 유용한 데이터 추출
                weather_data = {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "cloudiness": data["clouds"]["all"],
                    "visibility": data.get("visibility", 0),
                    "weather_description": data["weather"][0]["description"],
                    "weather_main": data["weather"][0]["main"],
                    "timestamp": datetime.now().isoformat(),
                    "location": {
                        "name": data["name"],
                        "country": data["sys"]["country"],
                        "latitude": data["coord"]["lat"],
                        "longitude": data["coord"]["lon"]
                    }
                }
                
                return {
                    "success": True,
                    "weather_data": weather_data
                }
                
            except httpx.HTTPError as e:
                return {"error": f"날씨 API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"날씨 데이터 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_weather_forecast(latitude: float, longitude: float, 
                                     days: int = 5, api_key: str = "") -> Dict[str, Any]:
            """
            날씨 예보 정보를 가져옵니다.
            
            Args:
                latitude: 위도
                longitude: 경도
                days: 예보 일수 (최대 5일)
                api_key: OpenWeatherMap API 키
                
            Returns:
                날씨 예보 정보
            """
            try:
                if not api_key:
                    return {"error": "OpenWeatherMap API 키가 필요합니다."}
                
                url = f"https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                    "units": "metric",
                    "cnt": min(days * 8, 40)  # 3시간마다 데이터, 최대 40개
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                # 예보 데이터 처리
                forecast_data = []
                for item in data["list"]:
                    forecast_data.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "humidity": item["main"]["humidity"],
                        "pressure": item["main"]["pressure"],
                        "wind_speed": item["wind"]["speed"],
                        "wind_direction": item["wind"].get("deg", 0),
                        "cloudiness": item["clouds"]["all"],
                        "weather_description": item["weather"][0]["description"],
                        "weather_main": item["weather"][0]["main"],
                        "rain_3h": item.get("rain", {}).get("3h", 0),
                        "snow_3h": item.get("snow", {}).get("3h", 0)
                    })
                
                return {
                    "success": True,
                    "forecast_days": days,
                    "forecast_data": forecast_data,
                    "location": {
                        "name": data["city"]["name"],
                        "country": data["city"]["country"],
                        "latitude": data["city"]["coord"]["lat"],
                        "longitude": data["city"]["coord"]["lon"]
                    }
                }
                
            except httpx.HTTPError as e:
                return {"error": f"날씨 예보 API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"날씨 예보 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_historical_weather(latitude: float, longitude: float, 
                                       start_date: str, end_date: str, 
                                       api_key: str = "") -> Dict[str, Any]:
            """
            과거 날씨 데이터를 가져옵니다. (OpenWeatherMap One Call API 필요)
            
            Args:
                latitude: 위도
                longitude: 경도
                start_date: 시작 날짜 (YYYY-MM-DD)
                end_date: 종료 날짜 (YYYY-MM-DD)
                api_key: OpenWeatherMap API 키
                
            Returns:
                과거 날씨 데이터
            """
            try:
                if not api_key:
                    return {"error": "OpenWeatherMap API 키가 필요합니다."}
                
                # 날짜 범위 계산
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                days_diff = (end_dt - start_dt).days
                
                if days_diff > 5:
                    return {"error": "과거 날씨 데이터는 최대 5일까지만 조회 가능합니다."}
                
                # One Call API 사용 (유료 플랜 필요)
                url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine"
                
                historical_data = []
                current_date = start_dt
                
                while current_date <= end_dt:
                    timestamp = int(current_date.timestamp())
                    
                    params = {
                        "lat": latitude,
                        "lon": longitude,
                        "dt": timestamp,
                        "appid": api_key,
                        "units": "metric"
                    }
                    
                    try:
                        async with httpx.AsyncClient(timeout=30) as client:
                            response = await client.get(url, params=params)
                            response.raise_for_status()
                            data = response.json()
                        
                        historical_data.append({
                            "datetime": current_date.isoformat(),
                            "temperature": data["current"]["temp"],
                            "humidity": data["current"]["humidity"],
                            "pressure": data["current"]["pressure"],
                            "wind_speed": data["current"]["wind_speed"],
                            "cloudiness": data["current"]["clouds"],
                            "weather_description": data["current"]["weather"][0]["description"]
                        })
                        
                    except httpx.HTTPError:
                        # 무료 플랜에서는 과거 데이터 접근 제한
                        break
                    
                    current_date += timedelta(days=1)
                    await asyncio.sleep(0.1)  # API 제한 방지
                
                return {
                    "success": True,
                    "start_date": start_date,
                    "end_date": end_date,
                    "historical_data": historical_data,
                    "data_points": len(historical_data)
                }
                
            except Exception as e:
                return {"error": f"과거 날씨 데이터 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def analyze_weather_energy_correlation(weather_data: List[Dict], 
                                                   energy_data: List[Dict],
                                                   weather_column: str = "temperature",
                                                   energy_column: str = "consumption") -> Dict[str, Any]:
            """
            날씨 데이터와 에너지 소비량의 상관관계를 분석합니다.
            
            Args:
                weather_data: 날씨 데이터
                energy_data: 에너지 소비 데이터
                weather_column: 분석할 날씨 컬럼
                energy_column: 분석할 에너지 컬럼
                
            Returns:
                상관관계 분석 결과
            """
            try:
                # 데이터 준비
                weather_df = pd.DataFrame(weather_data)
                energy_df = pd.DataFrame(energy_data)
                
                # 날짜 컬럼 처리
                if 'datetime' in weather_df.columns:
                    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])
                    weather_df = weather_df.set_index('datetime')
                
                if 'datetime' in energy_df.columns:
                    energy_df['datetime'] = pd.to_datetime(energy_df['datetime'])
                    energy_df = energy_df.set_index('datetime')
                
                # 시간별로 데이터 병합
                merged_data = pd.merge(weather_df, energy_df, left_index=True, right_index=True, how='inner')
                
                if len(merged_data) < 10:
                    return {"error": "상관관계 분석을 위해서는 최소 10개의 매칭된 데이터 포인트가 필요합니다."}
                
                # 상관계수 계산
                correlation = merged_data[weather_column].corr(merged_data[energy_column])
                
                # 선형 회귀 분석
                from scipy import stats
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    merged_data[weather_column], merged_data[energy_column]
                )
                
                # 온도별 에너지 소비 패턴 분석
                temp_bins = pd.cut(merged_data[weather_column], bins=5)
                temp_energy_pattern = merged_data.groupby(temp_bins)[energy_column].agg(['mean', 'std', 'count'])
                
                # 계절별 분석 (월별)
                merged_data['month'] = merged_data.index.month
                monthly_pattern = merged_data.groupby('month').agg({
                    weather_column: 'mean',
                    energy_column: 'mean'
                })
                
                return {
                    "success": True,
                    "correlation_analysis": {
                        "correlation_coefficient": float(correlation),
                        "correlation_strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak",
                        "r_squared": float(r_value ** 2),
                        "p_value": float(p_value),
                        "slope": float(slope),
                        "intercept": float(intercept)
                    },
                    "temperature_patterns": {
                        str(interval): {
                            "mean_energy": float(row['mean']),
                            "std_energy": float(row['std']),
                            "count": int(row['count'])
                        } for interval, row in temp_energy_pattern.iterrows()
                    },
                    "monthly_patterns": {
                        str(month): {
                            "avg_temperature": float(row[weather_column]),
                            "avg_energy": float(row[energy_column])
                        } for month, row in monthly_pattern.iterrows()
                    },
                    "data_points": len(merged_data)
                }
                
            except Exception as e:
                return {"error": f"날씨-에너지 상관관계 분석 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_weather_alerts(latitude: float, longitude: float, 
                                   api_key: str = "") -> Dict[str, Any]:
            """
            날씨 경보 정보를 가져옵니다.
            
            Args:
                latitude: 위도
                longitude: 경도
                api_key: OpenWeatherMap API 키
                
            Returns:
                날씨 경보 정보
            """
            try:
                if not api_key:
                    return {"error": "OpenWeatherMap API 키가 필요합니다."}
                
                url = f"https://api.openweathermap.org/data/2.5/onecall"
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "appid": api_key,
                    "exclude": "minutely,hourly,daily",
                    "units": "metric"
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                alerts = data.get("alerts", [])
                
                alert_data = []
                for alert in alerts:
                    alert_data.append({
                        "sender": alert.get("sender_name", "Unknown"),
                        "event": alert.get("event", "Unknown"),
                        "description": alert.get("description", ""),
                        "start": alert.get("start", 0),
                        "end": alert.get("end", 0),
                        "tags": alert.get("tags", [])
                    })
                
                return {
                    "success": True,
                    "alerts_count": len(alerts),
                    "alerts": alert_data
                }
                
            except httpx.HTTPError as e:
                return {"error": f"날씨 경보 API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"날씨 경보 수집 실패: {str(e)}"}

