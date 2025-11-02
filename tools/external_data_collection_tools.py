"""
외부 데이터 수집 MCP 도구

다양한 외부 데이터 소스에서 실시간 데이터를 수집하고 관리하는 도구들을 제공합니다.
"""

import httpx
import pandas as pd
import numpy as np
import asyncio
import json
import sqlite3
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import aiofiles
import os
from dataclasses import dataclass
from enum import Enum
import logging
from fastmcp import FastMCP

# 로깅 설정
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """지원하는 데이터 소스"""
    OPENWEATHER = "openweather"
    WEATHERAPI = "weatherapi"
    ACCUWEATHER = "accuweather"
    NOAA = "noaa"
    CUSTOM = "custom"

@dataclass
class DataCollectionConfig:
    """데이터 수집 설정"""
    source: DataSource
    api_key: str
    base_url: str
    rate_limit: int = 60  # 분당 요청 수
    timeout: int = 30
    retry_count: int = 3
    cache_duration: int = 300  # 캐시 유지 시간 (초)

class ExternalDataCollectionTools:
    """외부 데이터 수집 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.cache_dir = "./data/cache"
        self.db_path = "./data/external_data.db"
        self._ensure_directories()
        self._init_database()
        self._register_tools()
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs("./data", exist_ok=True)
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 데이터 수집 로그 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_collection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                location TEXT NOT NULL,
                data_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                data_points INTEGER DEFAULT 0
            )
        """)
        
        # 캐시된 데이터 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                location TEXT NOT NULL,
                data_type TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                data_json TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 스케줄 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                location TEXT NOT NULL,
                data_type TEXT NOT NULL,
                frequency_minutes INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_run DATETIME,
                next_run DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def collect_weather_data_multi_source(latitude: float, longitude: float, 
                                                  sources: List[str] = None,
                                                  data_types: List[str] = None) -> Dict[str, Any]:
            """
            여러 날씨 데이터 소스에서 데이터를 수집합니다.
            
            Args:
                latitude: 위도
                longitude: 경도
                sources: 사용할 데이터 소스 목록
                data_types: 수집할 데이터 타입 목록
                
            Returns:
                수집된 날씨 데이터
            """
            try:
                if sources is None:
                    sources = ["openweather", "weatherapi"]
                
                if data_types is None:
                    data_types = ["current", "forecast", "historical"]
                
                location_key = f"{latitude}_{longitude}"
                collected_data = {}
                
                for source in sources:
                    try:
                        source_data = await self._collect_from_source(
                            source, latitude, longitude, data_types
                        )
                        collected_data[source] = source_data
                        
                        # 로그 기록
                        await self._log_collection(
                            source, location_key, "weather", True, 
                            len(source_data.get("data", []))
                        )
                        
                    except Exception as e:
                        logger.error(f"데이터 소스 {source}에서 수집 실패: {e}")
                        await self._log_collection(
                            source, location_key, "weather", False, 0, str(e)
                        )
                        collected_data[source] = {"error": str(e)}
                
                return {
                    "success": True,
                    "location": {"latitude": latitude, "longitude": longitude},
                    "sources": sources,
                    "collected_data": collected_data,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": f"다중 소스 데이터 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def collect_real_time_weather(latitude: float, longitude: float,
                                          source: str = "openweather",
                                          cache_duration: int = 300) -> Dict[str, Any]:
            """
            실시간 날씨 데이터를 수집합니다 (캐싱 포함).
            
            Args:
                latitude: 위도
                longitude: 경도
                source: 데이터 소스
                cache_duration: 캐시 유지 시간 (초)
                
            Returns:
                실시간 날씨 데이터
            """
            try:
                location_key = f"{latitude}_{longitude}"
                
                # 캐시 확인
                cached_data = await self._get_cached_data(
                    source, location_key, "current_weather", cache_duration
                )
                
                if cached_data:
                    return {
                        "success": True,
                        "data": cached_data,
                        "cached": True,
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 실시간 데이터 수집
                weather_data = await self._collect_current_weather(source, latitude, longitude)
                
                if weather_data.get("success"):
                    # 캐시 저장
                    await self._cache_data(
                        source, location_key, "current_weather", 
                        weather_data["data"], cache_duration
                    )
                    
                    # 로그 기록
                    await self._log_collection(
                        source, location_key, "current_weather", True, 1
                    )
                
                return weather_data
                
            except Exception as e:
                return {"error": f"실시간 날씨 데이터 수집 실패: {str(e)}"}
        
        @self.mcp.tool
        async def setup_data_collection_schedule(name: str, source: str, 
                                                latitude: float, longitude: float,
                                                data_type: str, frequency_minutes: int) -> Dict[str, Any]:
            """
            자동 데이터 수집 스케줄을 설정합니다.
            
            Args:
                name: 스케줄 이름
                source: 데이터 소스
                latitude: 위도
                longitude: 경도
                data_type: 수집할 데이터 타입
                frequency_minutes: 수집 주기 (분)
                
            Returns:
                스케줄 설정 결과
            """
            try:
                location_key = f"{latitude}_{longitude}"
                next_run = datetime.now() + timedelta(minutes=frequency_minutes)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO collection_schedules 
                    (name, source, location, data_type, frequency_minutes, next_run)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, source, location_key, data_type, frequency_minutes, next_run))
                
                conn.commit()
                conn.close()
                
                return {
                    "success": True,
                    "schedule_name": name,
                    "source": source,
                    "location": location_key,
                    "data_type": data_type,
                    "frequency_minutes": frequency_minutes,
                    "next_run": next_run.isoformat()
                }
                
            except Exception as e:
                return {"error": f"스케줄 설정 실패: {str(e)}"}
        
        @self.mcp.tool
        async def run_scheduled_collections() -> Dict[str, Any]:
            """
            예약된 데이터 수집 작업을 실행합니다.
            
            Returns:
                실행 결과
            """
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 실행할 스케줄 조회
                cursor.execute("""
                    SELECT id, name, source, location, data_type, frequency_minutes
                    FROM collection_schedules 
                    WHERE is_active = TRUE AND next_run <= ?
                """, (datetime.now(),))
                
                schedules = cursor.fetchall()
                results = []
                
                for schedule in schedules:
                    schedule_id, name, source, location, data_type, frequency = schedule
                    
                    try:
                        # 위치 정보 파싱
                        lat, lon = map(float, location.split('_'))
                        
                        # 데이터 수집
                        if data_type == "current_weather":
                            data = await self._collect_current_weather(source, lat, lon)
                        elif data_type == "forecast":
                            data = await self._collect_forecast_weather(source, lat, lon)
                        else:
                            data = {"error": f"지원하지 않는 데이터 타입: {data_type}"}
                        
                        # 다음 실행 시간 업데이트
                        next_run = datetime.now() + timedelta(minutes=frequency)
                        cursor.execute("""
                            UPDATE collection_schedules 
                            SET last_run = ?, next_run = ?
                            WHERE id = ?
                        """, (datetime.now(), next_run, schedule_id))
                        
                        results.append({
                            "schedule_name": name,
                            "success": data.get("success", False),
                            "data_points": len(data.get("data", [])),
                            "next_run": next_run.isoformat()
                        })
                        
                    except Exception as e:
                        results.append({
                            "schedule_name": name,
                            "success": False,
                            "error": str(e)
                        })
                
                conn.commit()
                conn.close()
                
                return {
                    "success": True,
                    "executed_schedules": len(schedules),
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {"error": f"스케줄 실행 실패: {str(e)}"}
        
        @self.mcp.tool
        async def validate_data_quality(data: List[Dict], data_type: str = "weather") -> Dict[str, Any]:
            """
            수집된 데이터의 품질을 검증합니다.
            
            Args:
                data: 검증할 데이터
                data_type: 데이터 타입
                
            Returns:
                데이터 품질 검증 결과
            """
            try:
                if not data:
                    return {"error": "검증할 데이터가 없습니다."}
                
                df = pd.DataFrame(data)
                quality_report = {
                    "total_records": len(df),
                    "missing_values": {},
                    "data_types": {},
                    "outliers": {},
                    "duplicates": 0,
                    "quality_score": 0
                }
                
                # 누락값 검사
                for column in df.columns:
                    missing_count = df[column].isnull().sum()
                    quality_report["missing_values"][column] = {
                        "count": int(missing_count),
                        "percentage": float(missing_count / len(df) * 100)
                    }
                
                # 데이터 타입 검사
                for column in df.columns:
                    quality_report["data_types"][column] = str(df[column].dtype)
                
                # 중복 검사
                duplicates = df.duplicated().sum()
                quality_report["duplicates"] = int(duplicates)
                
                # 이상치 검사 (수치형 컬럼만)
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for column in numeric_columns:
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                    quality_report["outliers"][column] = {
                        "count": len(outliers),
                        "percentage": float(len(outliers) / len(df) * 100)
                    }
                
                # 품질 점수 계산 (0-100)
                missing_penalty = sum(quality_report["missing_values"][col]["percentage"] for col in quality_report["missing_values"]) / len(df.columns)
                duplicate_penalty = quality_report["duplicates"] / len(df) * 100
                outlier_penalty = sum(quality_report["outliers"][col]["percentage"] for col in quality_report["outliers"]) / len(numeric_columns) if numeric_columns.any() else 0
                
                quality_score = max(0, 100 - missing_penalty - duplicate_penalty - outlier_penalty)
                quality_report["quality_score"] = float(quality_score)
                
                return {
                    "success": True,
                    "quality_report": quality_report,
                    "recommendations": self._generate_quality_recommendations(quality_report)
                }
                
            except Exception as e:
                return {"error": f"데이터 품질 검증 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_collection_statistics(days: int = 7) -> Dict[str, Any]:
            """
            데이터 수집 통계를 조회합니다.
            
            Args:
                days: 조회할 기간 (일)
                
            Returns:
                수집 통계
            """
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 기간 설정
                start_date = datetime.now() - timedelta(days=days)
                
                # 수집 로그 통계
                cursor.execute("""
                    SELECT source, 
                           COUNT(*) as total_attempts,
                           SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) as successful,
                           SUM(data_points) as total_data_points
                    FROM data_collection_logs 
                    WHERE timestamp >= ?
                    GROUP BY source
                """, (start_date,))
                
                collection_stats = cursor.fetchall()
                
                # 소스별 성공률
                source_stats = {}
                for row in collection_stats:
                    source, total, successful, data_points = row
                    success_rate = (successful / total * 100) if total > 0 else 0
                    source_stats[source] = {
                        "total_attempts": total,
                        "successful_attempts": successful,
                        "success_rate": float(success_rate),
                        "total_data_points": data_points
                    }
                
                # 활성 스케줄 조회
                cursor.execute("""
                    SELECT COUNT(*) FROM collection_schedules WHERE is_active = TRUE
                """)
                active_schedules = cursor.fetchone()[0]
                
                # 최근 오류 조회
                cursor.execute("""
                    SELECT source, error_message, timestamp
                    FROM data_collection_logs 
                    WHERE success = FALSE AND timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                """, (start_date,))
                
                recent_errors = cursor.fetchall()
                
                conn.close()
                
                return {
                    "success": True,
                    "period_days": days,
                    "source_statistics": source_stats,
                    "active_schedules": active_schedules,
                    "recent_errors": [
                        {
                            "source": error[0],
                            "error": error[1],
                            "timestamp": error[2]
                        } for error in recent_errors
                    ],
                    "total_sources": len(source_stats),
                    "overall_success_rate": float(
                        sum(stats["successful_attempts"] for stats in source_stats.values()) /
                        sum(stats["total_attempts"] for stats in source_stats.values()) * 100
                    ) if source_stats else 0
                }
                
            except Exception as e:
                return {"error": f"통계 조회 실패: {str(e)}"}
    
    async def _collect_from_source(self, source: str, latitude: float, longitude: float, data_types: List[str]) -> Dict[str, Any]:
        """특정 소스에서 데이터 수집"""
        if source == "openweather":
            return await self._collect_openweather_data(latitude, longitude, data_types)
        elif source == "weatherapi":
            return await self._collect_weatherapi_data(latitude, longitude, data_types)
        else:
            return {"error": f"지원하지 않는 데이터 소스: {source}"}
    
    async def _collect_openweather_data(self, latitude: float, longitude: float, data_types: List[str]) -> Dict[str, Any]:
        """OpenWeatherMap에서 데이터 수집"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "OpenWeatherMap API 키가 설정되지 않았습니다."}
        
        collected_data = {}
        
        if "current" in data_types:
            current_data = await self._collect_current_weather("openweather", latitude, longitude)
            collected_data["current"] = current_data
        
        if "forecast" in data_types:
            forecast_data = await self._collect_forecast_weather("openweather", latitude, longitude)
            collected_data["forecast"] = forecast_data
        
        return collected_data
    
    async def _collect_weatherapi_data(self, latitude: float, longitude: float, data_types: List[str]) -> Dict[str, Any]:
        """WeatherAPI에서 데이터 수집"""
        api_key = os.getenv("WEATHERAPI_API_KEY")
        if not api_key:
            return {"error": "WeatherAPI API 키가 설정되지 않았습니다."}
        
        # WeatherAPI 구현 (예시)
        return {"error": "WeatherAPI 구현 예정"}
    
    async def _collect_current_weather(self, source: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """현재 날씨 데이터 수집"""
        if source == "openweather":
            api_key = os.getenv("OPENWEATHER_API_KEY")
            url = "https://api.openweathermap.org/data/2.5/weather"
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
            
            return {
                "success": True,
                "data": {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "weather_description": data["weather"][0]["description"],
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        return {"error": f"지원하지 않는 소스: {source}"}
    
    async def _collect_forecast_weather(self, source: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """예보 날씨 데이터 수집"""
        if source == "openweather":
            api_key = os.getenv("OPENWEATHER_API_KEY")
            url = "https://api.openweathermap.org/data/2.5/forecast"
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
            
            forecast_data = []
            for item in data["list"]:
                forecast_data.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "weather_description": item["weather"][0]["description"]
                })
            
            return {
                "success": True,
                "data": forecast_data
            }
        
        return {"error": f"지원하지 않는 소스: {source}"}
    
    async def _get_cached_data(self, source: str, location: str, data_type: str, cache_duration: int) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_json FROM cached_data 
                WHERE source = ? AND location = ? AND data_type = ? 
                AND expires_at > ?
                ORDER BY created_at DESC LIMIT 1
            """, (source, location, data_type, datetime.now()))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            return None
    
    async def _cache_data(self, source: str, location: str, data_type: str, data: Dict, cache_duration: int):
        """데이터 캐시 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(seconds=cache_duration)
            
            cursor.execute("""
                INSERT INTO cached_data 
                (source, location, data_type, timestamp, data_json, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (source, location, data_type, datetime.now(), json.dumps(data), expires_at))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
    
    async def _log_collection(self, source: str, location: str, data_type: str, success: bool, data_points: int = 0, error_message: str = None):
        """수집 로그 기록"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO data_collection_logs 
                (source, location, data_type, success, error_message, data_points)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (source, location, data_type, success, error_message, data_points))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"로그 기록 실패: {e}")
    
    def _generate_quality_recommendations(self, quality_report: Dict) -> List[str]:
        """데이터 품질 개선 권장사항 생성"""
        recommendations = []
        
        # 누락값 권장사항
        high_missing = [col for col, stats in quality_report["missing_values"].items() 
                       if stats["percentage"] > 20]
        if high_missing:
            recommendations.append(f"높은 누락값 비율 컬럼: {', '.join(high_missing)} - 데이터 수집 과정 검토 필요")
        
        # 중복 데이터 권장사항
        if quality_report["duplicates"] > 0:
            recommendations.append(f"중복 데이터 {quality_report['duplicates']}개 발견 - 중복 제거 권장")
        
        # 이상치 권장사항
        high_outliers = [col for col, stats in quality_report["outliers"].items() 
                        if stats["percentage"] > 10]
        if high_outliers:
            recommendations.append(f"높은 이상치 비율 컬럼: {', '.join(high_outliers)} - 데이터 검증 강화 권장")
        
        # 품질 점수 권장사항
        if quality_report["quality_score"] < 70:
            recommendations.append("전체 데이터 품질이 낮습니다 - 데이터 수집 및 전처리 과정 전면 검토 필요")
        elif quality_report["quality_score"] < 85:
            recommendations.append("데이터 품질이 보통 수준입니다 - 일부 개선 여지가 있습니다")
        else:
            recommendations.append("데이터 품질이 우수합니다 - 현재 상태 유지 권장")
        
        return recommendations
