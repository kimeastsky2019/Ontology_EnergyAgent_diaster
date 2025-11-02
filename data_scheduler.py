"""
데이터 수집 스케줄러

외부 데이터 소스에서 자동으로 데이터를 수집하는 스케줄러입니다.
"""

import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import signal
import sys
from tools.external_data_collection_tools import ExternalDataCollectionTools
from fastmcp import FastMCP

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    """데이터 수집 스케줄러"""
    
    def __init__(self, db_path: str = "./data/external_data.db"):
        self.db_path = db_path
        self.is_running = False
        self.tasks = []
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"시그널 {signum} 수신. 스케줄러를 종료합니다...")
        self.is_running = False
    
    async def start(self):
        """스케줄러 시작"""
        logger.info("데이터 수집 스케줄러를 시작합니다...")
        self.is_running = True
        
        try:
            while self.is_running:
                # 실행할 스케줄 확인
                await self._check_and_run_schedules()
                
                # 1분 대기
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"스케줄러 실행 중 오류: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """스케줄러 중지"""
        logger.info("스케줄러를 중지합니다...")
        self.is_running = False
        
        # 실행 중인 태스크 취소
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
    
    async def _check_and_run_schedules(self):
        """스케줄 확인 및 실행"""
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
            
            if schedules:
                logger.info(f"{len(schedules)}개의 스케줄을 실행합니다...")
                
                # 각 스케줄을 비동기로 실행
                for schedule in schedules:
                    task = asyncio.create_task(self._run_schedule(schedule))
                    self.tasks.append(task)
                
                # 완료된 태스크 정리
                self.tasks = [task for task in self.tasks if not task.done()]
            
            conn.close()
            
        except Exception as e:
            logger.error(f"스케줄 확인 중 오류: {e}")
    
    async def _run_schedule(self, schedule):
        """개별 스케줄 실행"""
        schedule_id, name, source, location, data_type, frequency = schedule
        
        try:
            logger.info(f"스케줄 '{name}' 실행 중...")
            
            # 위치 정보 파싱
            lat, lon = map(float, location.split('_'))
            
            # MCP 도구를 사용하여 데이터 수집
            mcp = FastMCP("Scheduler")
            tools = ExternalDataCollectionTools(mcp)
            
            # 데이터 수집 실행
            if data_type == "current_weather":
                result = await tools._collect_current_weather(source, lat, lon)
            elif data_type == "forecast":
                result = await tools._collect_forecast_weather(source, lat, lon)
            else:
                result = {"error": f"지원하지 않는 데이터 타입: {data_type}"}
            
            # 다음 실행 시간 업데이트
            await self._update_schedule_next_run(schedule_id, frequency)
            
            if result.get("success"):
                logger.info(f"스케줄 '{name}' 실행 성공")
            else:
                logger.error(f"스케줄 '{name}' 실행 실패: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"스케줄 '{name}' 실행 중 오류: {e}")
            await self._update_schedule_next_run(schedule_id, frequency)
    
    async def _update_schedule_next_run(self, schedule_id: int, frequency: int):
        """스케줄의 다음 실행 시간 업데이트"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            next_run = datetime.now() + timedelta(minutes=frequency)
            
            cursor.execute("""
                UPDATE collection_schedules 
                SET last_run = ?, next_run = ?
                WHERE id = ?
            """, (datetime.now(), next_run, schedule_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"스케줄 업데이트 실패: {e}")
    
    async def add_schedule(self, name: str, source: str, latitude: float, longitude: float,
                          data_type: str, frequency_minutes: int) -> Dict[str, Any]:
        """새로운 스케줄 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            location_key = f"{latitude}_{longitude}"
            next_run = datetime.now() + timedelta(minutes=frequency_minutes)
            
            cursor.execute("""
                INSERT OR REPLACE INTO collection_schedules 
                (name, source, location, data_type, frequency_minutes, next_run)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, source, location_key, data_type, frequency_minutes, next_run))
            
            conn.commit()
            conn.close()
            
            logger.info(f"스케줄 '{name}' 추가됨")
            
            return {
                "success": True,
                "message": f"스케줄 '{name}'이 성공적으로 추가되었습니다.",
                "next_run": next_run.isoformat()
            }
            
        except Exception as e:
            logger.error(f"스케줄 추가 실패: {e}")
            return {"error": f"스케줄 추가 실패: {str(e)}"}
    
    async def get_active_schedules(self) -> List[Dict[str, Any]]:
        """활성 스케줄 목록 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, source, location, data_type, frequency_minutes, 
                       last_run, next_run, created_at
                FROM collection_schedules 
                WHERE is_active = TRUE
                ORDER BY next_run
            """)
            
            schedules = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": schedule[0],
                    "name": schedule[1],
                    "source": schedule[2],
                    "location": schedule[3],
                    "data_type": schedule[4],
                    "frequency_minutes": schedule[5],
                    "last_run": schedule[6],
                    "next_run": schedule[7],
                    "created_at": schedule[8]
                }
                for schedule in schedules
            ]
            
        except Exception as e:
            logger.error(f"스케줄 조회 실패: {e}")
            return []
    
    async def stop_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """스케줄 중지"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE collection_schedules 
                SET is_active = FALSE 
                WHERE id = ?
            """, (schedule_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"스케줄 ID {schedule_id} 중지됨")
            
            return {
                "success": True,
                "message": f"스케줄 ID {schedule_id}이 중지되었습니다."
            }
            
        except Exception as e:
            logger.error(f"스케줄 중지 실패: {e}")
            return {"error": f"스케줄 중지 실패: {str(e)}"}

async def main():
    """메인 함수"""
    scheduler = DataCollectionScheduler()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 스케줄러가 중지되었습니다.")
    except Exception as e:
        logger.error(f"스케줄러 실행 중 오류: {e}")
    finally:
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
