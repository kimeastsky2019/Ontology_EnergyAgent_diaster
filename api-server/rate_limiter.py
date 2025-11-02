"""
Rate Limiter 모듈
"""

import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate Limiter 클래스"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def check_limit(self, user_id: str) -> bool:
        """Rate limit 확인"""
        current_time = time.time()
        
        # 사용자별 요청 기록 초기화
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # 오래된 요청 기록 제거
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.window_seconds
        ]
        
        # 요청 수 확인
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # 새 요청 기록
        self.requests[user_id].append(current_time)
        return True
