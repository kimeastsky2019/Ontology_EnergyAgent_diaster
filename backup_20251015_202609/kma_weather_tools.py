"""
KMA(기상청) 날씨 데이터 수집 도구

한국 기상청의 공식 날씨 API를 사용하여 정확한 날씨 데이터를 수집하고 분석합니다.
"""

import httpx
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import json
from fastmcp import FastMCP

class KMAWeatherTools:
    """KMA(기상청) 날씨 데이터 수집 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def get_kma_current_weather(
            latitude: float, 
            longitude: float,
            api_key: str = ""
        ) -> Dict[str, Any]:
            """
            KMA 현재 날씨 정보를 가져옵니다.
            
            Args:
                latitude: 위도 (한국 내)
                longitude: 경도 (한국 내)
                api_key: KMA API 키
                
            Returns:
                KMA 현재 날씨 정보
            """
            try:
                if not api_key:
                    return {"error": "KMA API 키가 필요합니다."}
                
                # KMA API 엔드포인트 (실제 API URL로 변경 필요)
                url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
                
                # 격자 좌표 변환 (위경도 -> 격자)
                nx, ny = self._convert_latlon_to_grid(latitude, longitude)
                
                # 현재 시간 기준으로 base_date, base_time 설정
                now = datetime.now()
                base_date = now.strftime("%Y%m%d")
                base_time = now.strftime("%H00")
                
                params = {
                    "serviceKey": api_key,
                    "numOfRows": 100,
                    "pageNo": 1,
                    "dataType": "JSON",
                    "base_date": base_date,
                    "base_time": base_time,
                    "nx": nx,
                    "ny": ny
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                # KMA 응답 데이터 파싱
                if data.get("response", {}).get("header", {}).get("resultCode") != "00":
                    return {"error": f"KMA API 오류: {data.get('response', {}).get('header', {}).get('resultMsg', 'Unknown error')}"}
                
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                # 데이터 파싱
                weather_data = {}
                for item in items:
                    category = item.get("category")
                    value = item.get("obsrValue")
                    
                    if category == "T1H":  # 기온
                        weather_data["temperature"] = float(value)
                    elif category == "REH":  # 습도
                        weather_data["humidity"] = float(value)
                    elif category == "RN1":  # 1시간 강수량
                        weather_data["precipitation"] = float(value)
                    elif category == "UUU":  # 동서바람성분
                        weather_data["wind_u"] = float(value)
                    elif category == "VVV":  # 남북바람성분
                        weather_data["wind_v"] = float(value)
                    elif category == "WSD":  # 풍속
                        weather_data["wind_speed"] = float(value)
                    elif category == "PTY":  # 강수형태
                        weather_data["precipitation_type"] = int(value)
                
                # 풍향 계산
                if "wind_u" in weather_data and "wind_v" in weather_data:
                    wind_direction = self._calculate_wind_direction(
                        weather_data["wind_u"], weather_data["wind_v"]
                    )
                    weather_data["wind_direction"] = wind_direction
                
                # 강수형태 텍스트 변환
                pty_map = {0: "없음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기", 5: "빗방울", 6: "빗방울눈날림", 7: "눈날림"}
                weather_data["precipitation_type_text"] = pty_map.get(weather_data.get("precipitation_type", 0), "알 수 없음")
                
                return {
                    "success": True,
                    "source": "KMA",
                    "weather_data": {
                        **weather_data,
                        "timestamp": now.isoformat(),
                        "location": {
                            "latitude": latitude,
                            "longitude": longitude,
                            "grid_x": nx,
                            "grid_y": ny
                        }
                    }
                }
                
            except httpx.HTTPError as e:
                return {"error": f"KMA API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"KMA 날씨 데이터 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_kma_ultra_short_forecast(
            latitude: float, 
            longitude: float,
            api_key: str = ""
        ) -> Dict[str, Any]:
            """
            KMA 초단기예보 정보를 가져옵니다 (6시간 예보).
            
            Args:
                latitude: 위도 (한국 내)
                longitude: 경도 (한국 내)
                api_key: KMA API 키
                
            Returns:
                KMA 초단기예보 정보
            """
            try:
                if not api_key:
                    return {"error": "KMA API 키가 필요합니다."}
                
                url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
                
                # 격자 좌표 변환
                nx, ny = self._convert_latlon_to_grid(latitude, longitude)
                
                # 현재 시간 기준으로 base_date, base_time 설정
                now = datetime.now()
                base_date = now.strftime("%Y%m%d")
                base_time = now.strftime("%H00")
                
                params = {
                    "serviceKey": api_key,
                    "numOfRows": 1000,
                    "pageNo": 1,
                    "dataType": "JSON",
                    "base_date": base_date,
                    "base_time": base_time,
                    "nx": nx,
                    "ny": ny
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                if data.get("response", {}).get("header", {}).get("resultCode") != "00":
                    return {"error": f"KMA API 오류: {data.get('response', {}).get('header', {}).get('resultMsg', 'Unknown error')}"}
                
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                # 시간별 데이터 그룹화
                forecast_data = {}
                for item in items:
                    fcst_time = item.get("fcstTime")
                    if fcst_time not in forecast_data:
                        forecast_data[fcst_time] = {
                            "fcstDate": item.get("fcstDate"),
                            "fcstTime": fcst_time
                        }
                    
                    category = item.get("category")
                    value = item.get("fcstValue")
                    
                    if category == "T1H":  # 기온
                        forecast_data[fcst_time]["temperature"] = float(value)
                    elif category == "REH":  # 습도
                        forecast_data[fcst_time]["humidity"] = float(value)
                    elif category == "RN1":  # 1시간 강수량
                        forecast_data[fcst_time]["precipitation"] = float(value)
                    elif category == "UUU":  # 동서바람성분
                        forecast_data[fcst_time]["wind_u"] = float(value)
                    elif category == "VVV":  # 남북바람성분
                        forecast_data[fcst_time]["wind_v"] = float(value)
                    elif category == "WSD":  # 풍속
                        forecast_data[fcst_time]["wind_speed"] = float(value)
                    elif category == "PTY":  # 강수형태
                        forecast_data[fcst_time]["precipitation_type"] = int(value)
                    elif category == "SKY":  # 하늘상태
                        forecast_data[fcst_time]["sky_condition"] = int(value)
                
                # 예보 데이터 정리
                forecast_list = []
                for time_key, data in forecast_data.items():
                    if "temperature" in data:
                        # 풍향 계산
                        if "wind_u" in data and "wind_v" in data:
                            data["wind_direction"] = self._calculate_wind_direction(
                                data["wind_u"], data["wind_v"]
                            )
                        
                        # 강수형태 텍스트 변환
                        pty_map = {0: "없음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기", 5: "빗방울", 6: "빗방울눈날림", 7: "눈날림"}
                        data["precipitation_type_text"] = pty_map.get(data.get("precipitation_type", 0), "알 수 없음")
                        
                        # 하늘상태 텍스트 변환
                        sky_map = {1: "맑음", 3: "구름많음", 4: "흐림"}
                        data["sky_condition_text"] = sky_map.get(data.get("sky_condition", 1), "알 수 없음")
                        
                        forecast_list.append(data)
                
                # 시간순 정렬
                forecast_list.sort(key=lambda x: x["fcstTime"])
                
                return {
                    "success": True,
                    "source": "KMA",
                    "forecast_type": "ultra_short",
                    "forecast_data": forecast_list,
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "grid_x": nx,
                        "grid_y": ny
                    },
                    "base_time": f"{base_date} {base_time}"
                }
                
            except httpx.HTTPError as e:
                return {"error": f"KMA 초단기예보 API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"KMA 초단기예보 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_kma_short_term_forecast(
            latitude: float, 
            longitude: float,
            api_key: str = ""
        ) -> Dict[str, Any]:
            """
            KMA 단기예보 정보를 가져옵니다 (3일 예보).
            
            Args:
                latitude: 위도 (한국 내)
                longitude: 경도 (한국 내)
                api_key: KMA API 키
                
            Returns:
                KMA 단기예보 정보
            """
            try:
                if not api_key:
                    return {"error": "KMA API 키가 필요합니다."}
                
                url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
                
                # 격자 좌표 변환
                nx, ny = self._convert_latlon_to_grid(latitude, longitude)
                
                # 현재 시간 기준으로 base_date, base_time 설정
                now = datetime.now()
                base_date = now.strftime("%Y%m%d")
                base_time = now.strftime("%H00")
                
                params = {
                    "serviceKey": api_key,
                    "numOfRows": 1000,
                    "pageNo": 1,
                    "dataType": "JSON",
                    "base_date": base_date,
                    "base_time": base_time,
                    "nx": nx,
                    "ny": ny
                }
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                if data.get("response", {}).get("header", {}).get("resultCode") != "00":
                    return {"error": f"KMA API 오류: {data.get('response', {}).get('header', {}).get('resultMsg', 'Unknown error')}"}
                
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                # 시간별 데이터 그룹화
                forecast_data = {}
                for item in items:
                    fcst_time = item.get("fcstTime")
                    fcst_date = item.get("fcstDate")
                    key = f"{fcst_date}_{fcst_time}"
                    
                    if key not in forecast_data:
                        forecast_data[key] = {
                            "fcstDate": fcst_date,
                            "fcstTime": fcst_time
                        }
                    
                    category = item.get("category")
                    value = item.get("fcstValue")
                    
                    if category == "TMP":  # 기온
                        forecast_data[key]["temperature"] = float(value)
                    elif category == "TMN":  # 최저기온
                        forecast_data[key]["min_temperature"] = float(value)
                    elif category == "TMX":  # 최고기온
                        forecast_data[key]["max_temperature"] = float(value)
                    elif category == "REH":  # 습도
                        forecast_data[key]["humidity"] = float(value)
                    elif category == "POP":  # 강수확률
                        forecast_data[key]["precipitation_probability"] = float(value)
                    elif category == "PCP":  # 강수량
                        forecast_data[key]["precipitation"] = value
                    elif category == "WSD":  # 풍속
                        forecast_data[key]["wind_speed"] = float(value)
                    elif category == "VEC":  # 풍향
                        forecast_data[key]["wind_direction"] = float(value)
                    elif category == "PTY":  # 강수형태
                        forecast_data[key]["precipitation_type"] = int(value)
                    elif category == "SKY":  # 하늘상태
                        forecast_data[key]["sky_condition"] = int(value)
                
                # 예보 데이터 정리
                forecast_list = []
                for key, data in forecast_data.items():
                    if "temperature" in data:
                        # 강수형태 텍스트 변환
                        pty_map = {0: "없음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기", 5: "빗방울", 6: "빗방울눈날림", 7: "눈날림"}
                        data["precipitation_type_text"] = pty_map.get(data.get("precipitation_type", 0), "알 수 없음")
                        
                        # 하늘상태 텍스트 변환
                        sky_map = {1: "맑음", 3: "구름많음", 4: "흐림"}
                        data["sky_condition_text"] = sky_map.get(data.get("sky_condition", 1), "알 수 없음")
                        
                        forecast_list.append(data)
                
                # 시간순 정렬
                forecast_list.sort(key=lambda x: (x["fcstDate"], x["fcstTime"]))
                
                return {
                    "success": True,
                    "source": "KMA",
                    "forecast_type": "short_term",
                    "forecast_data": forecast_list,
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "grid_x": nx,
                        "grid_y": ny
                    },
                    "base_time": f"{base_date} {base_time}"
                }
                
            except httpx.HTTPError as e:
                return {"error": f"KMA 단기예보 API 요청 실패: {str(e)}"}
            except Exception as e:
                return {"error": f"KMA 단기예보 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def collect_kma_weather_data(
            latitude: float, 
            longitude: float,
            data_types: List[str] = ["current", "ultra_short", "short_term"],
            api_key: str = ""
        ) -> Dict[str, Any]:
            """
            KMA 날씨 데이터를 종합적으로 수집합니다.
            
            Args:
                latitude: 위도 (한국 내)
                longitude: 경도 (한국 내)
                data_types: 수집할 데이터 타입 목록
                api_key: KMA API 키
                
            Returns:
                종합 KMA 날씨 데이터
            """
            try:
                if not api_key:
                    return {"error": "KMA API 키가 필요합니다."}
                
                collected_data = {
                    "success": True,
                    "source": "KMA",
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "timestamp": datetime.now().isoformat(),
                    "data": {}
                }
                
                # 현재 날씨 수집
                if "current" in data_types:
                    current_result = await self.get_kma_current_weather(latitude, longitude, api_key)
                    if current_result.get("success"):
                        collected_data["data"]["current"] = current_result["weather_data"]
                    else:
                        collected_data["data"]["current"] = {"error": current_result.get("error")}
                
                # 초단기예보 수집
                if "ultra_short" in data_types:
                    ultra_short_result = await self.get_kma_ultra_short_forecast(latitude, longitude, api_key)
                    if ultra_short_result.get("success"):
                        collected_data["data"]["ultra_short_forecast"] = ultra_short_result["forecast_data"]
                    else:
                        collected_data["data"]["ultra_short_forecast"] = {"error": ultra_short_result.get("error")}
                
                # 단기예보 수집
                if "short_term" in data_types:
                    short_term_result = await self.get_kma_short_term_forecast(latitude, longitude, api_key)
                    if short_term_result.get("success"):
                        collected_data["data"]["short_term_forecast"] = short_term_result["forecast_data"]
                    else:
                        collected_data["data"]["short_term_forecast"] = {"error": short_term_result.get("error")}
                
                # 에너지 분석을 위한 요약 통계
                summary_stats = self._calculate_weather_summary(collected_data["data"])
                collected_data["summary"] = summary_stats
                
                return collected_data
                
            except Exception as e:
                return {"error": f"KMA 날씨 데이터 종합 수집 실패: {str(e)}"}
    
    def _convert_latlon_to_grid(self, lat: float, lon: float) -> tuple:
        """
        위경도를 KMA 격자 좌표로 변환합니다.
        
        Args:
            lat: 위도
            lon: 경도
            
        Returns:
            (nx, ny) 격자 좌표
        """
        # KMA 격자 좌표 변환 공식
        RE = 6371.00877  # 지구 반경(km)
        GRID = 5.0  # 격자 간격(km)
        SLAT1 = 30.0  # 투영 위도1(degree)
        SLAT2 = 60.0  # 투영 위도2(degree)
        OLON = 126.0  # 기준점 경도(degree)
        OLAT = 38.0  # 기준점 위도(degree)
        XO = 43  # 기준점 X좌표(GRID)
        YO = 136  # 기준점 Y좌표(GRID)
        
        DEGRAD = np.pi / 180.0
        RADDEG = 180.0 / np.pi
        
        re = RE / GRID
        slat1 = SLAT1 * DEGRAD
        slat2 = SLAT2 * DEGRAD
        olon = OLON * DEGRAD
        olat = OLAT * DEGRAD
        
        sn = np.tan(np.pi * 0.25 + slat2 * 0.5) / np.tan(np.pi * 0.25 + slat1 * 0.5)
        sn = np.log(np.cos(slat1) / np.cos(slat2)) / np.log(sn)
        sf = np.tan(np.pi * 0.25 + slat1 * 0.5)
        sf = sf ** sn * np.cos(slat1) / sn
        ro = np.tan(np.pi * 0.25 + olat * 0.5)
        ro = re * sf / (ro ** sn)
        
        ra = np.tan(np.pi * 0.25 + lat * DEGRAD * 0.5)
        theta = lon * DEGRAD - olon
        if theta > np.pi:
            theta -= 2.0 * np.pi
        if theta < -np.pi:
            theta += 2.0 * np.pi
        theta *= sn
        
        x = ra * np.sin(theta) + XO
        y = ro - ra * np.cos(theta) + YO
        
        return int(x + 1.5), int(y + 1.5)
    
    def _calculate_wind_direction(self, u: float, v: float) -> float:
        """
        바람 성분으로부터 풍향을 계산합니다.
        
        Args:
            u: 동서바람성분
            v: 남북바람성분
            
        Returns:
            풍향 (도)
        """
        if u == 0 and v == 0:
            return 0
        
        # 풍향 계산 (북쪽을 0도로 하는 기상학적 풍향)
        wind_direction = np.arctan2(u, v) * 180 / np.pi
        if wind_direction < 0:
            wind_direction += 360
        
        return round(wind_direction, 1)
    
    def _calculate_weather_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        날씨 데이터의 요약 통계를 계산합니다.
        
        Args:
            data: 수집된 날씨 데이터
            
        Returns:
            요약 통계
        """
        summary = {
            "current_conditions": {},
            "forecast_summary": {},
            "energy_impact": {}
        }
        
        # 현재 날씨 요약
        if "current" in data and "error" not in data["current"]:
            current = data["current"]
            summary["current_conditions"] = {
                "temperature": current.get("temperature", 0),
                "humidity": current.get("humidity", 0),
                "wind_speed": current.get("wind_speed", 0),
                "precipitation": current.get("precipitation", 0),
                "sky_condition": current.get("sky_condition_text", "알 수 없음")
            }
        
        # 예보 요약
        if "ultra_short_forecast" in data and "error" not in data["ultra_short_forecast"]:
            forecast = data["ultra_short_forecast"]
            if isinstance(forecast, list) and len(forecast) > 0:
                temps = [f.get("temperature", 0) for f in forecast if "temperature" in f]
                humidities = [f.get("humidity", 0) for f in forecast if "humidity" in f]
                
                if temps:
                    summary["forecast_summary"] = {
                        "avg_temperature": round(np.mean(temps), 1),
                        "min_temperature": round(min(temps), 1),
                        "max_temperature": round(max(temps), 1),
                        "avg_humidity": round(np.mean(humidities), 1) if humidities else 0,
                        "forecast_hours": len(forecast)
                    }
        
        # 에너지 영향 분석
        if summary["current_conditions"]:
            temp = summary["current_conditions"].get("temperature", 0)
            humidity = summary["current_conditions"].get("humidity", 0)
            
            # 온도 기반 에너지 소비 예측
            if temp < 18:
                energy_impact = "heating_high"
                impact_level = "높음"
            elif temp > 26:
                energy_impact = "cooling_high"
                impact_level = "높음"
            else:
                energy_impact = "comfortable"
                impact_level = "낮음"
            
            summary["energy_impact"] = {
                "impact_type": energy_impact,
                "impact_level": impact_level,
                "temperature_factor": temp,
                "humidity_factor": humidity,
                "recommendation": self._get_energy_recommendation(temp, humidity)
            }
        
        return summary
    
    def _get_energy_recommendation(self, temp: float, humidity: float) -> str:
        """
        날씨 조건에 따른 에너지 절약 권장사항을 제공합니다.
        
        Args:
            temp: 온도
            humidity: 습도
            
        Returns:
            권장사항
        """
        if temp < 18:
            return "난방 에너지 소비가 높을 것으로 예상됩니다. 단열을 강화하고 실내 온도를 적절히 유지하세요."
        elif temp > 26:
            return "냉방 에너지 소비가 높을 것으로 예상됩니다. 자연 환기를 활용하고 에어컨 설정 온도를 높이세요."
        elif humidity > 70:
            return "습도가 높아 쾌적성을 위해 환기나 제습이 필요할 수 있습니다."
        else:
            return "쾌적한 날씨로 에너지 소비가 낮을 것으로 예상됩니다."

