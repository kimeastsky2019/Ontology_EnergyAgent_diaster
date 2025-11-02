"""
프롬프트 시스템 도구

LangGraph Agent와 함께 사용하기 위한 프롬프트 도구들을 제공합니다.
"""

from typing import List, Dict, Any
from fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

class PromptTools:
    """프롬프트 관련 도구들"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """도구들을 MCP 서버에 등록"""
        
        @self.mcp.prompt
        def energy_analysis_prompt(message: str) -> List[base.Message]:
            """
            에너지 데이터 분석을 위한 기본 프롬프트
            
            Args:
                message: 사용자 메시지
                
            Returns:
                프롬프트 메시지 리스트
            """
            return [
                base.AssistantMessage(
                    "안녕하세요! 저는 에너지 데이터 분석 전문가입니다. 🔋\n\n"
                    "다음과 같은 작업을 도와드릴 수 있습니다:\n"
                    "• 📊 에너지 데이터 통계 분석 및 시각화\n"
                    "• 🔮 에너지 소비량 예측 모델링\n"
                    "• 📈 시계열 분석 및 트렌드 분석\n"
                    "• 🌤️ 날씨 데이터와의 상관관계 분석\n"
                    "• ⚡ 에너지 효율성 및 절약 잠재력 분석\n"
                    "• 📋 대시보드 및 보고서 생성\n\n"
                    "분석하고 싶은 데이터 파일이나 구체적인 질문을 알려주세요!"
                ),
                base.UserMessage(message),
            ]
        
        @self.mcp.prompt
        def data_visualization_prompt(message: str) -> List[base.Message]:
            """
            데이터 시각화를 위한 프롬프트
            
            Args:
                message: 사용자 메시지
                
            Returns:
                프롬프트 메시지 리스트
            """
            return [
                base.AssistantMessage(
                    "📊 데이터 시각화 전문가입니다!\n\n"
                    "다음과 같은 시각화를 도와드릴 수 있습니다:\n"
                    "• 히스토그램 및 분포 차트\n"
                    "• 시계열 차트 및 트렌드 분석\n"
                    "• 상관관계 히트맵\n"
                    "• 박스플롯 및 이상치 탐지\n"
                    "• 에너지 소비 패턴 시각화\n"
                    "• 예측 결과 차트\n\n"
                    "어떤 데이터를 어떻게 시각화하고 싶으신가요?"
                ),
                base.UserMessage(message),
            ]
        
        @self.mcp.prompt
        def model_training_prompt(message: str) -> List[base.Message]:
            """
            모델 학습을 위한 프롬프트
            
            Args:
                message: 사용자 메시지
                
            Returns:
                프롬프트 메시지 리스트
            """
            return [
                base.AssistantMessage(
                    "🤖 머신러닝 모델링 전문가입니다!\n\n"
                    "다음과 같은 모델링을 도와드릴 수 있습니다:\n"
                    "• 자동 모델 선택 (분류/회귀)\n"
                    "• ARIMA 시계열 예측\n"
                    "• Prophet 예측 모델\n"
                    "• LSTM 신경망\n"
                    "• Random Forest, SVM 등\n"
                    "• 모델 성능 비교 및 평가\n\n"
                    "예측하고 싶은 데이터와 목표를 알려주세요!"
                ),
                base.UserMessage(message),
            ]
        
        @self.mcp.prompt
        def energy_insights_prompt(message: str) -> List[base.Message]:
            """
            에너지 인사이트 분석을 위한 프롬프트
            
            Args:
                message: 사용자 메시지
                
            Returns:
                프롬프트 메시지 리스트
            """
            return [
                base.AssistantMessage(
                    "⚡ 에너지 분석 전문가입니다!\n\n"
                    "다음과 같은 에너지 인사이트를 제공할 수 있습니다:\n"
                    "• 피크 수요 시간대 분석\n"
                    "• 에너지 효율성 지표 계산\n"
                    "• 계절별/시간별 사용 패턴 분석\n"
                    "• 절약 잠재력 평가\n"
                    "• 날씨와 에너지 소비의 상관관계\n"
                    "• 이상치 및 비정상 패턴 탐지\n\n"
                    "어떤 에너지 인사이트가 필요하신가요?"
                ),
                base.UserMessage(message),
            ]
        
        @self.mcp.prompt
        def general_analysis_prompt(message: str) -> List[base.Message]:
            """
            일반적인 데이터 분석을 위한 프롬프트
            
            Args:
                message: 사용자 메시지
                
            Returns:
                프롬프트 메시지 리스트
            """
            return [
                base.AssistantMessage(
                    "📈 데이터 분석 전문가입니다!\n\n"
                    "다음과 같은 분석을 도와드릴 수 있습니다:\n"
                    "• 데이터 탐색 및 기본 통계\n"
                    "• 상관관계 분석\n"
                    "• 데이터 품질 검사\n"
                    "• 시각화 및 차트 생성\n"
                    "• 모델링 및 예측\n"
                    "• 결과 해석 및 인사이트 제공\n\n"
                    "분석하고 싶은 데이터나 질문을 알려주세요!"
                ),
                base.UserMessage(message),
            ]
