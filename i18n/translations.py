"""
다국어 지원 시스템
"""

from typing import Dict, Any
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TranslationManager:
    """번역 관리 클래스"""
    
    def __init__(self, default_language: str = "ko"):
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """번역 파일 로드"""
        try:
            # 지원 언어 목록
            supported_languages = ["ko", "en", "ja", "zh", "es", "fr", "de"]
            
            for lang in supported_languages:
                filepath = f"i18n/translations_{lang}.json"
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    logger.info(f"Loaded translations for {lang}")
                else:
                    logger.warning(f"Translation file not found: {filepath}")
            
            logger.info(f"Loaded translations for {len(self.translations)} languages")
            
        except Exception as e:
            logger.error(f"Failed to load translations: {e}")
    
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """번역된 텍스트 반환"""
        try:
            lang = language or self.current_language
            
            # 현재 언어에서 번역 찾기
            if lang in self.translations and key in self.translations[lang]:
                text = self.translations[lang][key]
            # 기본 언어에서 번역 찾기
            elif self.default_language in self.translations and key in self.translations[self.default_language]:
                text = self.translations[self.default_language][key]
            # 키 자체 반환
            else:
                text = key
            
            # 키워드 치환
            if kwargs:
                try:
                    text = text.format(**kwargs)
                except (KeyError, ValueError):
                    logger.warning(f"Failed to format text: {text} with kwargs: {kwargs}")
            
            return text
            
        except Exception as e:
            logger.error(f"Translation error for key '{key}': {e}")
            return key
    
    def set_language(self, language: str):
        """현재 언어 설정"""
        if language in self.translations:
            self.current_language = language
            logger.info(f"Language changed to {language}")
        else:
            logger.warning(f"Unsupported language: {language}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """지원 언어 목록 반환"""
        return {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch"
        }
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """언어 정보 반환"""
        language_names = self.get_supported_languages()
        
        return {
            "code": language,
            "name": language_names.get(language, language),
            "is_supported": language in self.translations,
            "translation_count": len(self.translations.get(language, {}))
        }

# 전역 번역 관리자 인스턴스
translation_manager = TranslationManager()

def t(key: str, language: str = None, **kwargs) -> str:
    """번역 함수 (간편 사용)"""
    return translation_manager.get_text(key, language, **kwargs)

def set_language(language: str):
    """언어 설정 함수"""
    translation_manager.set_language(language)

def get_supported_languages() -> Dict[str, str]:
    """지원 언어 목록 반환"""
    return translation_manager.get_supported_languages()
