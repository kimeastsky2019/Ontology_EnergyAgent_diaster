"""
데이터 저장 및 관리 도구

에너지 데이터와 분석 결과를 저장하고 관리합니다.
"""

import pandas as pd
import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiofiles
from sqlalchemy import create_engine, text
from fastmcp import FastMCP

class DataStorageTools:
    """데이터 저장 및 관리 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.tool
        async def save_energy_data(data: List[Dict], table_name: str = "energy_consumption",
                                 database_path: str = "energy_analysis.db") -> Dict[str, Any]:
            """
            에너지 데이터를 데이터베이스에 저장합니다.
            
            Args:
                data: 저장할 에너지 데이터
                table_name: 테이블 이름
                database_path: 데이터베이스 파일 경로
                
            Returns:
                저장 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                
                # 데이터베이스 연결
                engine = create_engine(f'sqlite:///{database_path}')
                
                # 데이터 저장 (덮어쓰기)
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                
                # 저장된 데이터 확인
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "database_path": database_path,
                    "records_saved": int(count),
                    "columns": list(df.columns)
                }
                
            except Exception as e:
                return {"error": f"데이터 저장 실패: {str(e)}"}
        
        @self.mcp.tool
        async def load_energy_data(table_name: str = "energy_consumption",
                                 database_path: str = "energy_analysis.db",
                                 limit: Optional[int] = None) -> Dict[str, Any]:
            """
            데이터베이스에서 에너지 데이터를 로드합니다.
            
            Args:
                table_name: 테이블 이름
                database_path: 데이터베이스 파일 경로
                limit: 로드할 레코드 수 제한
                
            Returns:
                로드된 데이터
            """
            try:
                # 데이터베이스 연결
                engine = create_engine(f'sqlite:///{database_path}')
                
                # 데이터 로드
                query = f"SELECT * FROM {table_name}"
                if limit:
                    query += f" LIMIT {limit}"
                
                df = pd.read_sql(query, engine)
                
                # datetime 컬럼 변환
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                
                # 데이터를 딕셔너리 리스트로 변환
                data = df.to_dict('records')
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "records_loaded": len(data),
                    "columns": list(df.columns),
                    "data": data
                }
                
            except Exception as e:
                return {"error": f"데이터 로드 실패: {str(e)}"}
        
        @self.mcp.tool
        async def export_data_to_csv(data: List[Dict], file_path: str) -> Dict[str, Any]:
            """
            데이터를 CSV 파일로 내보냅니다.
            
            Args:
                data: 내보낼 데이터
                file_path: 저장할 파일 경로
                
            Returns:
                내보내기 결과
            """
            try:
                # 데이터 준비
                df = pd.DataFrame(data)
                
                # CSV 파일로 저장
                df.to_csv(file_path, index=False)
                
                # 파일 크기 확인
                file_size = os.path.getsize(file_path)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "records_exported": len(data),
                    "file_size_bytes": file_size,
                    "columns": list(df.columns)
                }
                
            except Exception as e:
                return {"error": f"CSV 내보내기 실패: {str(e)}"}
        
        @self.mcp.tool
        async def export_data_to_json(data: List[Dict], file_path: str) -> Dict[str, Any]:
            """
            데이터를 JSON 파일로 내보냅니다.
            
            Args:
                data: 내보낼 데이터
                file_path: 저장할 파일 경로
                
            Returns:
                내보내기 결과
            """
            try:
                # JSON 파일로 저장
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, indent=2, default=str))
                
                # 파일 크기 확인
                file_size = os.path.getsize(file_path)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "records_exported": len(data),
                    "file_size_bytes": file_size
                }
                
            except Exception as e:
                return {"error": f"JSON 내보내기 실패: {str(e)}"}
        
        @self.mcp.tool
        async def save_analysis_results(analysis_type: str, results: Dict[str, Any],
                                      file_path: str) -> Dict[str, Any]:
            """
            분석 결과를 파일로 저장합니다.
            
            Args:
                analysis_type: 분석 유형
                results: 분석 결과
                file_path: 저장할 파일 경로
                
            Returns:
                저장 결과
            """
            try:
                # 분석 결과에 메타데이터 추가
                analysis_data = {
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }
                
                # JSON 파일로 저장
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(analysis_data, indent=2, default=str))
                
                # 파일 크기 확인
                file_size = os.path.getsize(file_path)
                
                return {
                    "success": True,
                    "analysis_type": analysis_type,
                    "file_path": file_path,
                    "file_size_bytes": file_size,
                    "timestamp": analysis_data["timestamp"]
                }
                
            except Exception as e:
                return {"error": f"분석 결과 저장 실패: {str(e)}"}
        
        @self.mcp.tool
        async def load_analysis_results(file_path: str) -> Dict[str, Any]:
            """
            저장된 분석 결과를 로드합니다.
            
            Args:
                file_path: 로드할 파일 경로
                
            Returns:
                로드된 분석 결과
            """
            try:
                # JSON 파일 로드
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    analysis_data = json.loads(content)
                
                return {
                    "success": True,
                    "analysis_type": analysis_data.get("analysis_type"),
                    "timestamp": analysis_data.get("timestamp"),
                    "results": analysis_data.get("results", {}),
                    "file_path": file_path
                }
                
            except Exception as e:
                return {"error": f"분석 결과 로드 실패: {str(e)}"}
        
        @self.mcp.tool
        async def create_database_schema(database_path: str = "energy_analysis.db") -> Dict[str, Any]:
            """
            에너지 분석용 데이터베이스 스키마를 생성합니다.
            
            Args:
                database_path: 데이터베이스 파일 경로
                
            Returns:
                스키마 생성 결과
            """
            try:
                # 데이터베이스 연결
                engine = create_engine(f'sqlite:///{database_path}')
                
                # 테이블 생성 SQL
                create_tables_sql = """
                -- 에너지 소비 데이터 테이블
                CREATE TABLE IF NOT EXISTS energy_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,
                    consumption REAL NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- 날씨 데이터 테이블
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    pressure REAL,
                    wind_speed REAL,
                    cloudiness REAL,
                    weather_description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- 분석 결과 테이블
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    analysis_name TEXT,
                    results TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- 예측 결과 테이블
                CREATE TABLE IF NOT EXISTS forecast_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_type TEXT NOT NULL,
                    forecast_date TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    confidence_lower REAL,
                    confidence_upper REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- 인덱스 생성
                CREATE INDEX IF NOT EXISTS idx_energy_datetime ON energy_consumption(datetime);
                CREATE INDEX IF NOT EXISTS idx_weather_datetime ON weather_data(datetime);
                CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecast_results(forecast_date);
                """
                
                # 스키마 실행
                with engine.connect() as conn:
                    conn.execute(text(create_tables_sql))
                    conn.commit()
                
                # 생성된 테이블 확인
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in result.fetchall()]
                
                return {
                    "success": True,
                    "database_path": database_path,
                    "tables_created": tables,
                    "schema_created": True
                }
                
            except Exception as e:
                return {"error": f"데이터베이스 스키마 생성 실패: {str(e)}"}
        
        @self.mcp.tool
        async def get_database_info(database_path: str = "energy_analysis.db") -> Dict[str, Any]:
            """
            데이터베이스 정보를 조회합니다.
            
            Args:
                database_path: 데이터베이스 파일 경로
                
            Returns:
                데이터베이스 정보
            """
            try:
                # 데이터베이스 연결
                engine = create_engine(f'sqlite:///{database_path}')
                
                # 테이블 정보 조회
                with engine.connect() as conn:
                    # 테이블 목록
                    tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in tables_result.fetchall()]
                    
                    # 각 테이블의 레코드 수
                    table_counts = {}
                    for table in tables:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        table_counts[table] = count_result.fetchone()[0]
                    
                    # 데이터베이스 파일 크기
                    file_size = os.path.getsize(database_path) if os.path.exists(database_path) else 0
                
                return {
                    "success": True,
                    "database_path": database_path,
                    "tables": tables,
                    "table_counts": table_counts,
                    "file_size_bytes": file_size,
                    "total_records": sum(table_counts.values())
                }
                
            except Exception as e:
                return {"error": f"데이터베이스 정보 조회 실패: {str(e)}"}

