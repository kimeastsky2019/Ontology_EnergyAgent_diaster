"""
Cache Service 모듈
"""

import json
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Cache Service 클래스"""
    
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                return data
            else:
                del self.cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """캐시에 데이터 저장"""
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    async def delete(self, key: str) -> None:
        """캐시에서 데이터 삭제"""
        if key in self.cache:
            del self.cache[key]
    
    async def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
