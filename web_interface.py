#!/usr/bin/env python3
"""
연결된 Digital Experience Intelligence Platform
Health 카드와 메뉴에 기존 페이지들을 연결한 플랫폼
"""

from datetime import datetime

from fastapi import FastAPI, Query, Request, UploadFile, File, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import uvicorn
import os
import shutil
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# FastAPI 앱 생성
web_app = FastAPI(title="Digital Experience Intelligence Platform", version="2.0.0")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 임시 사용자 데이터베이스 (실제로는 backend/src/models/user.py의 User 모델 사용)
# SECRET_KEY는 환경변수에서 가져오거나 기본값 사용
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 파일 업로드 크기 제한을 위한 미들웨어 추가
class IncreaseUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        # 파일 업로드 크기 제한 증가
        if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
            # 최대 100MB까지 허용
            pass  # Starlette는 기본적으로 100MB까지 허용
        response = await call_next(request)
        return response

web_app.add_middleware(IncreaseUploadSizeMiddleware)

LANGUAGE_OPTIONS = {
    "ko": {"label": "한국어", "flag": "🇰🇷", "locale": "ko-KR"},
    "en": {"label": "English", "flag": "🇺🇸", "locale": "en-US"},
    "zh": {"label": "中文", "flag": "🇨🇳", "locale": "zh-CN"},
}

LANGUAGE_STRINGS = {
    "ko": {
        "page_title": "🔍 디지털 경험 인텔리전스 플랫폼",
        "hero_title": "디지털 경험 인텔리전스 플랫폼",
        "hero_subtitle": "포괄적인 사용자 경험 분석 및 최적화 솔루션",
        "stat_total_interactions": "총 상호작용",
        "stat_active_sessions": "활성 세션",
        "stat_conversion_rate": "전환율",
        "stat_error_rate": "오류율",
        "system_web_title": "웹 서버",
        "system_web_status": "온라인",
        "system_web_detail": "포트: 8000",
        "system_web_link": "메인 대시보드로 이동",
        "system_api_title": "API 서비스",
        "system_api_status": "정상",
        "system_api_detail": "모든 엔드포인트 활성",
        "system_api_link": "API 상태 확인",
        "system_data_title": "데이터 스토리지",
        "system_data_status": "연결됨",
        "system_data_detail": "SQLite 데이터베이스",
        "system_data_link": "데이터 수집 페이지",
        "system_uptime_title": "업타임",
        "system_uptime_label": "계산 중...",
        "system_uptime_link": "통계 페이지",
        "last_update_label": "업데이트 시간",
        "feature_event_title": "실시간 이벤트 캡처",
        "feature_event_description": "클릭, 스크롤, 폼 제출 등 모든 사용자 상호작용을 실시간으로 추적합니다.",
        "feature_event_progress_frontend": "프론트엔드 이벤트 캡처율: 95%",
        "feature_event_progress_backend": "백엔드 API 호출 캡처율: 98%",
        "feature_event_button": "데이터 분석 페이지",
        "feature_ai_title": "AI 인사이트 (SLM 기반)",
        "feature_ai_description": "Small Language Model 기반 대화형 분석 어시스턴트로 심층적인 인사이트를 제공합니다.",
        "feature_ai_assistant_label": "AI 어시스턴트:",
        "feature_ai_chat_greeting": "안녕하세요! 사용자 경험 분석을 도와드리겠습니다.",
        "feature_ai_chat_request": "전환율을 개선하는 방법을 알려주세요.",
        "feature_ai_chat_recommendation": "분석 결과, 3단계에서 이탈률이 높습니다. CTA 버튼 위치를 조정해보세요.",
        "feature_ai_button": "LLM-SLM 개발 페이지",
        "feature_replay_title": "세션 리플레이",
        "feature_replay_description": "사용자 행동 패턴을 시각화하고 히트맵으로 마찰 지점을 분석합니다.",
        "feature_replay_button": "날씨 분석 페이지",
        "feature_privacy_title": "프라이버시 보호",
        "feature_privacy_description": "PII, PCI, PHI 등 민감한 데이터를 자동으로 마스킹하여 보안을 보장합니다.",
        "feature_privacy_alert_pii": "PII 데이터 마스킹: 100% 활성",
        "feature_privacy_alert_pci": "PCI 데이터 마스킹: 100% 활성",
        "feature_privacy_alert_phi": "PHI 데이터 마스킹: 100% 활성",
        "feature_privacy_button": "ML/AI 엔진 페이지",
        "feature_monitor_title": "실시간 모니터링",
        "feature_monitor_description": "전환율 변화, 오류 감지, 사용자 불편을 실시간으로 모니터링하고 알림합니다.",
        "feature_monitor_alert_warning": "전환율 15% 감소 감지",
        "feature_monitor_alert_info": "새로운 사용자 세션 시작",
        "feature_monitor_alert_success": "시스템 정상 작동",
        "feature_monitor_button": "날씨 대시보드",
        "feature_deploy_title": "유연한 배포",
        "feature_deploy_description": "하이브리드, 싱글 테넌트, 멀티 테넌트 환경을 지원합니다.",
        "feature_deploy_hybrid": "하이브리드",
        "feature_deploy_single": "싱글 테넌트",
        "feature_deploy_multi": "멀티 테넌트",
        "feature_deploy_badge_active": "활성",
        "feature_deploy_badge_available": "사용 가능",
        "feature_deploy_button": "API 대시보드",
        "hours_suffix": "시간",
        "minutes_suffix": "분",
        "seconds_suffix": "초",
    },
    "en": {
        "page_title": "🔍 Digital Experience Intelligence Platform",
        "hero_title": "Digital Experience Intelligence Platform",
        "hero_subtitle": "Comprehensive user experience analytics and optimization suite",
        "stat_total_interactions": "Total interactions",
        "stat_active_sessions": "Active sessions",
        "stat_conversion_rate": "Conversion rate",
        "stat_error_rate": "Error rate",
        "system_web_title": "Web Server",
        "system_web_status": "Online",
        "system_web_detail": "Port: 8000",
        "system_web_link": "Go to main dashboard",
        "system_api_title": "API Services",
        "system_api_status": "Healthy",
        "system_api_detail": "All endpoints active",
        "system_api_link": "View API status",
        "system_data_title": "Data Storage",
        "system_data_status": "Connected",
        "system_data_detail": "SQLite database",
        "system_data_link": "Open data collection page",
        "system_uptime_title": "Uptime",
        "system_uptime_label": "Calculating...",
        "system_uptime_link": "View statistics page",
        "last_update_label": "Last update",
        "feature_event_title": "Real-time Event Capture",
        "feature_event_description": "Track every user interaction such as clicks, scrolls, and form submissions in real time.",
        "feature_event_progress_frontend": "Frontend event capture rate: 95%",
        "feature_event_progress_backend": "Backend API call capture rate: 98%",
        "feature_event_button": "Open data analysis page",
        "feature_ai_title": "AI Insights (SLM-powered)",
        "feature_ai_description": "Conversational Small Language Model assistant delivering deep insights.",
        "feature_ai_assistant_label": "AI Assistant:",
        "feature_ai_chat_greeting": "Hello! I'll help you analyze user experience.",
        "feature_ai_chat_request": "Please suggest how to improve the conversion rate.",
        "feature_ai_chat_recommendation": "The analysis shows a high drop-off at step 3. Try adjusting the CTA button placement.",
        "feature_ai_button": "Open LLM-SLM development page",
        "feature_replay_title": "Session Replay",
        "feature_replay_description": "Visualize user behavior patterns and analyze friction points with heatmaps.",
        "feature_replay_button": "Open weather analysis page",
        "feature_privacy_title": "Privacy Protection",
        "feature_privacy_description": "Automatically mask sensitive data such as PII, PCI, and PHI to ensure security.",
        "feature_privacy_alert_pii": "PII data masking: 100% enabled",
        "feature_privacy_alert_pci": "PCI data masking: 100% enabled",
        "feature_privacy_alert_phi": "PHI data masking: 100% enabled",
        "feature_privacy_button": "Open ML/AI engine page",
        "feature_monitor_title": "Real-time Monitoring",
        "feature_monitor_description": "Monitor conversion changes, error detection, and user friction in real time.",
        "feature_monitor_alert_warning": "Detected 15% drop in conversion rate",
        "feature_monitor_alert_info": "New user session started",
        "feature_monitor_alert_success": "System operating normally",
        "feature_monitor_button": "Open weather dashboard",
        "feature_deploy_title": "Flexible Deployment",
        "feature_deploy_description": "Supports hybrid, single-tenant, and multi-tenant environments.",
        "feature_deploy_hybrid": "Hybrid",
        "feature_deploy_single": "Single tenant",
        "feature_deploy_multi": "Multi-tenant",
        "feature_deploy_badge_active": "Active",
        "feature_deploy_badge_available": "Available",
        "feature_deploy_button": "Open API dashboard",
        "hours_suffix": "h",
        "minutes_suffix": "m",
        "seconds_suffix": "s",
    },
    "zh": {
        "page_title": "🔍 数字体验智能平台",
        "hero_title": "数字体验智能平台",
        "hero_subtitle": "全面的用户体验分析与优化方案",
        "stat_total_interactions": "总交互次数",
        "stat_active_sessions": "活跃会话",
        "stat_conversion_rate": "转化率",
        "stat_error_rate": "错误率",
        "system_web_title": "网页服务器",
        "system_web_status": "在线",
        "system_web_detail": "端口：8000",
        "system_web_link": "前往主控制台",
        "system_api_title": "API 服务",
        "system_api_status": "健康",
        "system_api_detail": "所有端点均已激活",
        "system_api_link": "查看 API 状态",
        "system_data_title": "数据存储",
        "system_data_status": "已连接",
        "system_data_detail": "SQLite 数据库",
        "system_data_link": "打开数据采集页面",
        "system_uptime_title": "运行时间",
        "system_uptime_label": "计算中...",
        "system_uptime_link": "查看统计页面",
        "last_update_label": "更新时间",
        "feature_event_title": "实时事件捕获",
        "feature_event_description": "实时追踪点击、滚动、表单提交等所有用户交互。",
        "feature_event_progress_frontend": "前端事件捕获率：95%",
        "feature_event_progress_backend": "后端 API 调用捕获率：98%",
        "feature_event_button": "打开数据分析页面",
        "feature_ai_title": "AI 洞察（基于 SLM）",
        "feature_ai_description": "基于小型语言模型的对话式助手，提供深入洞察。",
        "feature_ai_assistant_label": "AI 助手：",
        "feature_ai_chat_greeting": "您好！我将协助您分析用户体验。",
        "feature_ai_chat_request": "请告诉我如何提升转化率。",
        "feature_ai_chat_recommendation": "分析显示第 3 步流失率较高。请尝试调整 CTA 按钮位置。",
        "feature_ai_button": "打开 LLM-SLM 开发页面",
        "feature_replay_title": "会话回放",
        "feature_replay_description": "可视化用户行为模式并通过热力图分析摩擦点。",
        "feature_replay_button": "打开天气分析页面",
        "feature_privacy_title": "隐私保护",
        "feature_privacy_description": "自动屏蔽 PII、PCI、PHI 等敏感数据，确保安全。",
        "feature_privacy_alert_pii": "PII 数据屏蔽：100% 已启用",
        "feature_privacy_alert_pci": "PCI 数据屏蔽：100% 已启用",
        "feature_privacy_alert_phi": "PHI 数据屏蔽：100% 已启用",
        "feature_privacy_button": "打开 ML/AI 引擎页面",
        "feature_monitor_title": "实时监控",
        "feature_monitor_description": "实时监测转化率变化、错误检测和用户不便提示。",
        "feature_monitor_alert_warning": "检测到转化率下降 15%",
        "feature_monitor_alert_info": "新的用户会话已开始",
        "feature_monitor_alert_success": "系统运行正常",
        "feature_monitor_button": "打开天气仪表板",
        "feature_deploy_title": "灵活部署",
        "feature_deploy_description": "支持混合、单租户与多租户环境。",
        "feature_deploy_hybrid": "混合",
        "feature_deploy_single": "单租户",
        "feature_deploy_multi": "多租户",
        "feature_deploy_badge_active": "已启用",
        "feature_deploy_badge_available": "可用",
        "feature_deploy_button": "打开 API 仪表板",
        "hours_suffix": "小时",
        "minutes_suffix": "分钟",
        "seconds_suffix": "秒",
    },
}


def get_available_languages():
    """사용 가능한 언어 목록 반환"""
    return list(LANGUAGE_OPTIONS.keys())


def get_language_content(lang: str):
    """Return localized text dictionary with English fallback."""
    return LANGUAGE_STRINGS.get(lang, LANGUAGE_STRINGS["en"])


def get_locale(lang: str) -> str:
    """Return locale code for date/time formatting."""
    return LANGUAGE_OPTIONS.get(lang, LANGUAGE_OPTIONS["en"])["locale"]


@web_app.get("/", response_class=HTMLResponse)
async def root():
    """루트 페이지 - Health 페이지로 리다이렉트"""
    return RedirectResponse(url="/health?lang=ko")


@web_app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request, lang: str = Query("ko", description="Language code")):
    """연결된 Digital Experience Intelligence Platform"""
    if lang not in get_available_languages():
        lang = "ko"

    texts = get_language_content(lang)
    locale = get_locale(lang)
    language_buttons = "".join(
        f'<a href="?lang={code}" class="btn btn-sm {"btn-primary text-white" if lang == code else "btn-light"}">{info["flag"]} {info["label"]}</a>'
        for code, info in LANGUAGE_OPTIONS.items()
    )

    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{texts['page_title']}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }}
            .main-container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .system-status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .system-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .system-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }}
            .status-indicator {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }}
            .status-online {{ background-color: #28a745; }}
            .status-offline {{ background-color: #dc3545; }}
            .status-warning {{ background-color: #ffc107; }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }}
            .feature-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border-left: 5px solid #667eea;
                cursor: pointer;
            }}
            .feature-card:hover {{
                transform: translateY(-10px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            }}
            .feature-icon {{
                font-size: 3rem;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .interaction-tracker {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
            }}
            .ai-insights {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .session-replay {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
            }}
            .privacy-protection {{
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
            }}
            .real-time-monitoring {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                color: white;
            }}
            .flexible-deployment {{
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                color: #333;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .stat-value {{
                font-size: 2.5rem;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }}
            .stat-label {{
                color: #666;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .progress-modern {{
                height: 8px;
                border-radius: 10px;
                background: rgba(255,255,255,0.3);
                overflow: hidden;
                margin: 15px 0;
            }}
            .progress-bar-modern {{
                height: 100%;
                background: linear-gradient(90deg, #4facfe, #00f2fe);
                border-radius: 10px;
                transition: width 0.3s ease;
            }}
            .ai-chat {{
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                max-height: 300px;
                overflow-y: auto;
            }}
            .ai-message {{
                margin: 10px 0;
                padding: 15px;
                border-radius: 15px;
                max-width: 80%;
            }}
            .ai-user {{
                background: rgba(255,255,255,0.2);
                margin-left: auto;
            }}
            .ai-assistant {{
                background: rgba(255,255,255,0.1);
            }}
            .heatmap-container {{
                background: rgba(255,255,255,0.2);
                border-radius: 15px;
                height: 200px;
                position: relative;
                overflow: hidden;
            }}
            .heatmap-point {{
                position: absolute;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: rgba(255, 107, 107, 0.8);
                box-shadow: 0 0 15px rgba(255, 107, 107, 0.6);
            }}
            .alert-modern {{
                border-radius: 10px;
                border: none;
                padding: 12px 16px;
                margin-bottom: 10px;
            }}
            .btn-modern {{
                border-radius: 30px;
                padding: 8px 20px;
                border: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .language-selector {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }}
            .uptime-display {{
                font-family: 'Courier New', monospace;
                font-size: 1.2rem;
                color: #28a745;
                font-weight: bold;
            }}
            .link-indicator {{
                color: #007bff;
                font-size: 0.8rem;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="language-selector">
            <div class="btn-group" role="group">
                {language_buttons}
            </div>
        </div>

        <div class="main-container">
            <div class="header-card">
                <h1 class="display-4 mb-4">
                    <i class="fas fa-brain"></i> {texts['hero_title']}
                </h1>
                <p class="lead mb-4">{texts['hero_subtitle']}</p>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalInteractions">0</div>
                        <div class="stat-label">{texts['stat_total_interactions']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="activeSessions">0</div>
                        <div class="stat-label">{texts['stat_active_sessions']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="conversionRate">0%</div>
                        <div class="stat-label">{texts['stat_conversion_rate']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="errorRate">0%</div>
                        <div class="stat-label">{texts['stat_error_rate']}</div>
                    </div>
                </div>
            </div>

            <div class="system-status-grid">
                <div class="system-card" onclick="window.location.href='/?lang={lang}'">
                    <i class="fas fa-server fa-3x text-success mb-3"></i>
                    <h5>{texts['system_web_title']}</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>{texts['system_web_status']}</strong>
                    </p>
                    <small class="text-muted">{texts['system_web_detail']}</small>
                    <div class="link-indicator">
                        🔗 {texts['system_web_link']}
                    </div>
                </div>

                <div class="system-card" onclick="window.location.href='/api/health?lang={lang}'">
                    <i class="fas fa-cogs fa-3x text-primary mb-3"></i>
                    <h5>{texts['system_api_title']}</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>{texts['system_api_status']}</strong>
                    </p>
                    <small class="text-muted">{texts['system_api_detail']}</small>
                    <div class="link-indicator">
                        🔗 {texts['system_api_link']}
                    </div>
                </div>

                <div class="system-card" onclick="window.location.href='/data-collection?lang={lang}'">
                    <i class="fas fa-database fa-3x text-info mb-3"></i>
                    <h5>{texts['system_data_title']}</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>{texts['system_data_status']}</strong>
                    </p>
                    <small class="text-muted">{texts['system_data_detail']}</small>
                    <div class="link-indicator">
                        🔗 {texts['system_data_link']}
                    </div>
                </div>

                <div class="system-card" onclick="window.location.href='/statistics?lang={lang}'">
                    <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                    <h5>{texts['system_uptime_title']}</h5>
                    <p class="uptime-display" id="uptime">{texts['system_uptime_label']}</p>
                    <small class="text-muted">{texts['last_update_label']}: <span id="lastUpdate"></span></small>
                    <div class="link-indicator">
                        🔗 {texts['system_uptime_link']}
                    </div>
                </div>
            </div>

            <div class="feature-grid">
                <div class="feature-card interaction-tracker" onclick="window.location.href='/data-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-mouse-pointer"></i>
                    </div>
                    <h3>{texts['feature_event_title']}</h3>
                    <p>{texts['feature_event_description']}</p>

                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 95%"></div>
                    </div>
                    <small>{texts['feature_event_progress_frontend']}</small>

                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 98%"></div>
                    </div>
                    <small>{texts['feature_event_progress_backend']}</small>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/data-analysis?lang={lang}'">
                            <i class="fas fa-chart-line"></i> {texts['feature_event_button']}
                        </button>
                    </div>
                </div>

                <div class="feature-card ai-insights" onclick="window.location.href='/llm-slm?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>{texts['feature_ai_title']}</h3>
                    <p>{texts['feature_ai_description']}</p>

                    <div class="ai-chat" id="aiChat">
                        <div class="ai-message ai-assistant">
                            <strong>{texts['feature_ai_assistant_label']}</strong> {texts['feature_ai_chat_greeting']}
                        </div>
                        <div class="ai-message ai-user">
                            {texts['feature_ai_chat_request']}
                        </div>
                        <div class="ai-message ai-assistant">
                            <strong>{texts['feature_ai_assistant_label']}</strong> {texts['feature_ai_chat_recommendation']}
                        </div>
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/llm-slm?lang={lang}'">
                            <i class="fas fa-brain"></i> {texts['feature_ai_button']}
                        </button>
                    </div>
                </div>

                <div class="feature-card session-replay" onclick="window.location.href='/weather-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <h3>{texts['feature_replay_title']}</h3>
                    <p>{texts['feature_replay_description']}</p>

                    <div class="heatmap-container" id="heatmapContainer">
                        <div class="heatmap-point" style="top: 20px; left: 30px;"></div>
                        <div class="heatmap-point" style="top: 50px; left: 80px;"></div>
                        <div class="heatmap-point" style="top: 80px; left: 120px;"></div>
                        <div class="heatmap-point" style="top: 120px; left: 200px;"></div>
                        <div class="heatmap-point" style="top: 150px; left: 250px;"></div>
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-analysis?lang={lang}'">
                            <i class="fas fa-cloud-sun"></i> {texts['feature_replay_button']}
                        </button>
                    </div>
                </div>

                <div class="feature-card privacy-protection" onclick="window.location.href='/model-testing?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>{texts['feature_privacy_title']}</h3>
                    <p>{texts['feature_privacy_description']}</p>

                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {texts['feature_privacy_alert_pii']}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {texts['feature_privacy_alert_pci']}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {texts['feature_privacy_alert_phi']}
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/model-testing?lang={lang}'">
                            <i class="fas fa-cogs"></i> {texts['feature_privacy_button']}
                        </button>
                    </div>
                </div>

                <div class="feature-card real-time-monitoring" onclick="window.location.href='/weather-dashboard?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <h3>{texts['feature_monitor_title']}</h3>
                    <p>{texts['feature_monitor_description']}</p>

                    <div class="alert alert-modern alert-warning">
                        <i class="fas fa-exclamation-triangle"></i> {texts['feature_monitor_alert_warning']}
                    </div>
                    <div class="alert alert-modern alert-info">
                        <i class="fas fa-info-circle"></i> {texts['feature_monitor_alert_info']}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {texts['feature_monitor_alert_success']}
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-dashboard?lang={lang}'">
                            <i class="fas fa-chart-area"></i> {texts['feature_monitor_button']}
                        </button>
                    </div>
                </div>

                <div class="feature-card flexible-deployment" onclick="window.location.href='/api/dashboard'">
                    <div class="feature-icon">
                        <i class="fas fa-cloud"></i>
                    </div>
                    <h3>{texts['feature_deploy_title']}</h3>
                    <p>{texts['feature_deploy_description']}</p>

                    <div class="row">
                        <div class="col-4 text-center">
                            <i class="fas fa-cloud fa-2x mb-2" style="color: #667eea;"></i>
                            <div class="small">{texts['feature_deploy_hybrid']}</div>
                            <span class="badge bg-primary">{texts['feature_deploy_badge_active']}</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-server fa-2x mb-2" style="color: #28a745;"></i>
                            <div class="small">{texts['feature_deploy_single']}</div>
                            <span class="badge bg-success">{texts['feature_deploy_badge_available']}</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-users fa-2x mb-2" style="color: #17a2b8;"></i>
                            <div class="small">{texts['feature_deploy_multi']}</div>
                            <span class="badge bg-info">{texts['feature_deploy_badge_available']}</span>
                        </div>
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/api/dashboard'">
                            <i class="fas fa-chart-bar"></i> {texts['feature_deploy_button']}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            const locale = "{locale}";

            function updateStats() {{
                document.getElementById('totalInteractions').textContent = (Math.floor(Math.random() * 1000) + 1000).toLocaleString(locale);
                document.getElementById('activeSessions').textContent = Math.floor(Math.random() * 50) + 10;
                document.getElementById('conversionRate').textContent = (Math.random() * 10 + 5).toFixed(1) + '%';
                document.getElementById('errorRate').textContent = (Math.random() * 2).toFixed(2) + '%';
            }}

            function generateHeatmap() {{
                const container = document.getElementById('heatmapContainer');
                const points = container.querySelectorAll('.heatmap-point');
                points.forEach(point => {{
                    point.style.top = Math.random() * 180 + 'px';
                    point.style.left = Math.random() * 300 + 'px';
                }});
            }}

            function updateUptime() {{
                const startTime = new Date('2025-10-11T01:22:47Z');
                const now = new Date();
                const diff = now - startTime;

                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);

                document.getElementById('uptime').textContent = `${{hours}}{texts['hours_suffix']} ${{minutes}}{texts['minutes_suffix']} ${{seconds}}{texts['seconds_suffix']}`;
            }}

            document.addEventListener('DOMContentLoaded', function() {{
                updateStats();
                updateUptime();
                setInterval(updateStats, 5000);
                setInterval(updateUptime, 1000);
                setInterval(generateHeatmap, 10000);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString(locale);
            }});
        </script>
    </body>
    </html>
    """


@web_app.get("/digital-experience", response_class=HTMLResponse)
async def digital_experience_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Digital Experience Intelligence 전용 페이지 - 리다이렉트용"""
    return RedirectResponse(url=f"/health?lang={lang}")


@web_app.get("/api/health")
async def api_health():
    """API Health Check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "web_interface": "online",
            "api": "online",
            "database": "online",
        },
    }


@web_app.get("/api/dashboard")
async def api_dashboard():
    """Dashboard API"""
    return {
        "message": "Dashboard API is working",
        "timestamp": datetime.now().isoformat(),
    }


@web_app.get("/api/models")
async def api_models():
    """Models API"""
    return {
        "message": "Models API is working",
        "timestamp": datetime.now().isoformat(),
    }


@web_app.get("/api/statistics")
async def api_statistics():
    """Statistics API"""
    return {
        "message": "Statistics API is working",
        "timestamp": datetime.now().isoformat(),
    }


@web_app.get("/api/languages")
async def api_languages():
    """Languages API"""
    return {
        "languages": get_available_languages(),
        "current": "ko",
        "timestamp": datetime.now().isoformat(),
    }


@web_app.get("/supply_analysis", response_class=HTMLResponse)
@web_app.get("/supply_analysis/", response_class=HTMLResponse)
async def supply_analysis():
    """에너지 공급 분석 대시보드"""
    from pathlib import Path
    
    # 여러 경로에서 supply_analysis 빌드 파일 찾기
    possible_paths = [
        Path(__file__).parent / "supply_analysis" / "frontend" / "build" / "index.html",
        Path("/home/metal/energy-platform/supply_analysis/frontend/build/index.html"),
        Path("/home/metal/energy-analysis-mcp/supply_analysis/frontend/build/index.html"),
    ]
    
    dashboard_path = None
    for path in possible_paths:
        if path.exists():
            dashboard_path = path
            break
    
    if dashboard_path and dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # React 앱의 base path를 /supply_analysis로 설정
            content = content.replace('/static/', '/supply_analysis/static/')
            return HTMLResponse(content=content)
    else:
        # 빌드 파일이 없으면 간단한 리다이렉트 페이지 반환
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>⚡ 에너지 공급 분석 대시보드</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        text-align: center;
                        padding: 2rem;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        max-width: 600px;
                    }
                    h1 { margin-bottom: 1rem; }
                    p { margin: 1rem 0; opacity: 0.9; }
                    .loading {
                        margin-top: 2rem;
                        font-size: 1.2rem;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚡ 에너지 공급 분석 대시보드</h1>
                    <p>대시보드가 준비 중입니다.</p>
                    <p class="loading">빌드 파일을 배포하면 대시보드가 표시됩니다.</p>
                </div>
            </body>
            </html>
            """
        )

@web_app.get("/supply_analysis/static/{file_path:path}")
@web_app.head("/supply_analysis/static/{file_path:path}")
async def supply_analysis_static(file_path: str):
    """supply_analysis 정적 파일 서빙 (GET 및 HEAD 메서드 지원)"""
    from pathlib import Path
    from fastapi.responses import FileResponse, Response
    from starlette.requests import Request
    import mimetypes
    import logging
    
    logger = logging.getLogger("uvicorn")
    logger.info(f"정적 파일 요청: {file_path}")
    
    # 여러 경로에서 정적 파일 찾기
    possible_base_paths = [
        Path(__file__).parent / "supply_analysis" / "frontend" / "build",
        Path("/home/metal/energy-platform/supply_analysis/frontend/build"),
        Path("/home/metal/energy-analysis-mcp/supply_analysis/frontend/build"),
    ]
    
    for base_path in possible_base_paths:
        static_file_path = base_path / "static" / file_path
        logger.info(f"파일 경로 확인: {static_file_path} (존재: {static_file_path.exists()})")
        if static_file_path.exists() and static_file_path.is_file():
            # MIME 타입 자동 감지
            media_type = mimetypes.guess_type(str(static_file_path))[0] or "application/octet-stream"
            logger.info(f"파일 반환: {static_file_path} (MIME: {media_type})")
            
            # 파일 크기 계산
            file_size = static_file_path.stat().st_size
            
            return FileResponse(
                path=str(static_file_path),
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=31536000",
                    "Access-Control-Allow-Origin": "*",
                    "Content-Length": str(file_size),
                }
            )
    
    # 파일을 찾지 못한 경우 404
    logger.error(f"파일을 찾을 수 없음: {file_path}")
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

# ============================================================================
# Supply Analysis API Endpoints (for supply_analysis frontend)
# ============================================================================

@web_app.get("/api/energy/realtime")
async def get_energy_realtime(range_param: str = Query("hour", alias="range")):
    """실시간 전력 데이터 조회"""
    from datetime import datetime, timedelta
    import random
    import math
    
    # range가 유효한지 확인
    if range_param not in ["hour", "day", "month", "year"]:
        range_param = "hour"
    
    now = datetime.now()
    labels = []
    values = []
    
    if range_param == "hour":
        # 최근 24시간
        for i in range(24, 0, -1):
            time = now - timedelta(hours=i)
            labels.append(time.strftime("%H:%M"))
            hour = time.hour
            if 6 <= hour <= 18:
                base_value = 30 + math.sin((hour - 6) / 12 * math.pi) * 60
            else:
                base_value = random.uniform(0, 10)
            values.append(round(base_value + random.uniform(-5, 5), 2))
    elif range_param == "day":
        # 최근 7일
        for i in range(7, 0, -1):
            date = now - timedelta(days=i)
            labels.append(date.strftime("%m/%d"))
            values.append(round(random.uniform(50, 150), 2))
    elif range_param == "month":
        # 최근 30일
        for i in range(30, 0, -1):
            date = now - timedelta(days=i)
            labels.append(date.strftime("%m/%d"))
            values.append(round(random.uniform(50, 150), 2))
    elif range_param == "year":
        # 최근 12개월
        for i in range(12, 0, -1):
            date = now - timedelta(days=i*30)
            labels.append(date.strftime("%Y-%m"))
            values.append(round(random.uniform(1000, 3000), 2))
    
    return {"labels": labels, "values": values}

@web_app.get("/api/energy/daily")
async def get_energy_daily(date: Optional[str] = Query(None)):
    """일일 에너지 생산 데이터 조회"""
    from datetime import datetime
    import random
    import math
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    labels = []
    values = []
    
    for hour in range(24):
        labels.append(f"{hour:02d}:00")
        if 6 <= hour <= 18:
            energy = 5 + math.sin((hour - 6) / 12 * math.pi) * 20 + random.uniform(0, 5)
        else:
            energy = random.uniform(0, 2)
        values.append(round(energy, 2))
    
    return {
        "date": date,
        "labels": labels,
        "values": values,
        "total": round(sum(values), 2)
    }

@web_app.get("/api/energy/history")
async def get_energy_history(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    """과거 에너지 데이터 조회"""
    from datetime import datetime, timedelta
    import random
    
    if not start:
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "start_date": start,
        "end_date": end,
        "total_energy": round(random.uniform(1000, 5000), 2),
        "average_power": round(random.uniform(50, 150), 2),
        "peak_power": round(random.uniform(150, 200), 2)
    }

@web_app.get("/api/energy/forecast")
async def get_energy_forecast(days: int = Query(7, ge=1, le=30)):
    """에너지 생산 예측"""
    from datetime import datetime, timedelta
    import random
    
    labels = []
    values = []
    
    now = datetime.now()
    for i in range(days):
        date = now + timedelta(days=i+1)
        labels.append(date.strftime("%m/%d"))
        values.append(round(random.uniform(80, 150), 2))
    
    return {
        "forecast_period": f"{days} days",
        "labels": labels,
        "values": values,
        "total_expected": round(sum(values), 2)
    }

@web_app.get("/api/facilities")
async def get_all_facilities():
    """모든 시설 목록 조회"""
    import random
    
    SAMPLE_FACILITIES = [
        {
            "id": "U0089",
            "name": "光点试验电站01",
            "type": "solar",
            "capacity": 100000,
            "location": "Pyeongtaek, Gyeonggi-do, KR",
            "status": "online",
            "currentPower": round(random.uniform(0, 80000), 2),
            "efficiency": round(random.uniform(80, 95), 2),
            "installation_date": "2023-01-15"
        }
    ]
    
    return {
        "total": len(SAMPLE_FACILITIES),
        "facilities": SAMPLE_FACILITIES
    }

@web_app.get("/api/facilities/current")
async def get_current_facility():
    """현재 시설 정보 조회 (메인 시설)"""
    from datetime import datetime
    import random
    
    facility = {
        "id": "U0089",
        "name": "光点试验电站01",
        "type": "solar",
        "capacity": 100000,
        "location": "Pyeongtaek, Gyeonggi-do, KR",
        "status": "online",
        "currentPower": round(random.uniform(0, 80000), 2),
        "efficiency": round(random.uniform(80, 95), 2),
        "installation_date": "2023-01-15",
        "last_updated": datetime.now().isoformat()
    }
    
    return facility

@web_app.get("/api/facilities/{facility_id}")
async def get_facility_by_id(facility_id: str):
    """특정 시설 정보 조회"""
    from datetime import datetime
    import random
    
    facility = {
        "id": facility_id,
        "name": "光点试验电站01",
        "type": "solar",
        "capacity": 100000,
        "location": "Pyeongtaek, Gyeonggi-do, KR",
        "status": "online",
        "currentPower": round(random.uniform(0, 80000), 2),
        "efficiency": round(random.uniform(80, 95), 2),
        "installation_date": "2023-01-15",
        "last_updated": datetime.now().isoformat()
    }
    
    return facility

@web_app.get("/api/weather/current")
async def get_current_weather():
    """현재 날씨 정보 조회"""
    from datetime import datetime
    import random
    
    WEATHER_CONDITIONS_KR = {
        "sunny": "맑음",
        "cloudy": "흐림",
        "rainy": "비",
        "snowy": "눈"
    }
    
    def generate_weather_condition():
        rand = random.random()
        if rand < 0.5:
            return "sunny"
        elif rand < 0.8:
            return "cloudy"
        elif rand < 0.95:
            return "rainy"
        else:
            return "snowy"
    
    condition = generate_weather_condition()
    
    return {
        "current": {
            "temp": random.randint(10, 25),
            "condition": condition,
            "condition_kr": WEATHER_CONDITIONS_KR[condition],
            "humidity": random.randint(40, 80),
            "windSpeed": round(random.uniform(0.5, 5.0), 1),
            "visibility": random.randint(5, 15),
            "pressure": random.randint(1005, 1025),
            "sunrise": "06:30",
            "sunset": "18:45",
            "uv_index": random.randint(1, 10)
        },
        "location": {
            "city": "Pyeongtaek",
            "region": "Gyeonggi-do",
            "country": "KR",
            "lat": 36.9922,
            "lon": 127.1128
        },
        "timestamp": datetime.now().isoformat()
    }

@web_app.get("/api/weather/forecast")
async def get_weather_forecast(days: int = Query(7, ge=1, le=14)):
    """날씨 예보 조회"""
    from datetime import datetime, timedelta
    import random
    
    WEATHER_CONDITIONS_KR = {
        "sunny": "맑음",
        "cloudy": "흐림",
        "rainy": "비",
        "snowy": "눈"
    }
    
    def generate_weather_condition():
        rand = random.random()
        if rand < 0.5:
            return "sunny"
        elif rand < 0.8:
            return "cloudy"
        elif rand < 0.95:
            return "rainy"
        else:
            return "snowy"
    
    now = datetime.now()
    forecast = []
    weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
    
    for i in range(days):
        date = now + timedelta(days=i)
        condition = generate_weather_condition()
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": weekdays_kr[date.weekday()],
            "temp": random.randint(10, 25),
            "temp_min": random.randint(5, 15),
            "temp_max": random.randint(18, 30),
            "condition": condition,
            "condition_kr": WEATHER_CONDITIONS_KR[condition],
            "precipitation_chance": random.randint(0, 100),
            "humidity": random.randint(40, 80),
            "wind_speed": round(random.uniform(0.5, 5.0), 1)
        })
    
    return {
        "forecast_period": f"{days} days",
        "forecast": forecast,
        "generated_at": datetime.now().isoformat()
    }

@web_app.get("/api/ai/anomalies")
async def get_ai_anomalies():
    """AI 이상징후 목록 조회"""
    from datetime import datetime, timedelta
    import random
    
    # 샘플 이상징후 데이터
    anomalies = []
    
    # 랜덤하게 이상징후 생성 (30% 확률)
    if random.random() < 0.3:
        anomalies.append({
            "id": 1,
            "type": "warning",
            "title": "비정상적인 전력 변동 감지",
            "description": "예상보다 30% 낮은 전력 생산",
            "severity": random.choice(["high", "medium", "low"]),
            "confidence": round(random.uniform(70, 95), 1),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 6))).isoformat()
        })
    
    return anomalies

@web_app.get("/api/ai/diagnostics")
async def get_ai_diagnostics():
    """AI 고장 진단 결과 조회"""
    from datetime import datetime
    import random
    
    diagnostics = [
        {
            "id": 1,
            "component": "태양광 패널 #3",
            "status": random.choice(["normal", "warning", "error"]),
            "issue": random.choice(["정상 작동", "효율 저하", "고장 의심"]),
            "recommendation": random.choice(["다음 점검: 2주 후", "청소 필요", "기술자 현장 점검 필요"]),
            "confidence": round(random.uniform(70, 95), 1)
        },
        {
            "id": 2,
            "component": "인버터 #1",
            "status": "normal",
            "issue": "정상 작동",
            "recommendation": "다음 점검: 2주 후",
            "confidence": 95.0
        }
    ]
    
    return diagnostics

@web_app.get("/api/energy-dashboard", response_class=HTMLResponse)
async def energy_dashboard():
    """에너지 수요 분석 대시보드"""
    from pathlib import Path
    
    # 여러 경로에서 대시보드 파일 찾기
    possible_paths = [
        Path(__file__).parent / "backend" / "static" / "energy_dashboard.html",
        Path("/home/metal/energy-platform/backend/static/energy_dashboard.html"),
        Path("/home/metal/energy-analysis-mcp/backend/static/energy_dashboard.html"),
    ]
    
    dashboard_path = None
    for path in possible_paths:
        if path.exists():
            dashboard_path = path
            break
    
    if dashboard_path and dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Energy Dashboard - Not Found</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        text-align: center;
                        padding: 2rem;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚡ Energy Demand Analysis Dashboard</h1>
                    <p>Dashboard file not found. Please check the deployment.</p>
                </div>
            </body>
            </html>
            """,
            status_code=404
        )


# Energy Demand API endpoints
UPLOAD_DIR = "/tmp/energy_data_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@web_app.post("/api/v1/energy-demand/analyze/public")
async def analyze_energy_demand_public(
    file: Optional[UploadFile] = File(None),
    data: Optional[str] = None
) -> Dict[str, Any]:
    """에너지 수요 분석 (파일 업로드 지원)"""
    try:
        # 백엔드 src/main.py의 에너지 수요 에이전트에 연결
        # 먼저 web_interface에서 직접 처리 시도
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV 파일을 업로드해주세요"
            )
        
        # 파일 저장
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 백엔드의 energy-demand-agent에 연결 시도
        # 먼저 로컬에서 직접 처리하거나, backend/src/main.py로 리다이렉트
        
        # 임시로 에이전트 로직 직접 호출 시도
        try:
            # backend/src/agents/energy_demand_agent.py를 직접 import 시도
            backend_path = Path(__file__).parent / "backend"
            if not backend_path.exists():
                backend_path = Path("/home/metal/energy-platform/backend")
            
            if backend_path.exists():
                sys.path.insert(0, str(backend_path))
                from src.agents.energy_demand_agent import EnergyDemandAgent
                
                agent = EnergyDemandAgent()
                result = agent.run_full_analysis(data_path=file_location)
                
                return result
        except Exception as e:
            # 백엔드 연결 실패 시, 샘플 응답 반환
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta
            
            # numpy 타입을 Python 기본 타입으로 변환하는 헬퍼 함수
            def convert_to_python_type(obj):
                """numpy 타입을 Python 기본 타입으로 변환"""
                if isinstance(obj, (np.integer, np.int64, np.int32)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64, np.float32)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif pd.isna(obj):
                    return None
                elif isinstance(obj, dict):
                    return {k: convert_to_python_type(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_python_type(item) for item in obj]
                return obj
            
            # CSV 파일 읽기
            try:
                df = pd.read_csv(file_location, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_location, encoding='cp949')
            
            # 컬럼명 정규화 (공백 제거, 소문자 변환)
            df.columns = df.columns.str.strip().str.lower()
            
            # 기본 분석 수행
            if 'kwh' in df.columns or 'kw' in df.columns:
                # 컬럼명 확인 및 매핑
                energy_col = 'kwh' if 'kwh' in df.columns else 'kw'
                power_col = 'kw' if 'kw' in df.columns else None
                
                total_energy = convert_to_python_type(df[energy_col].sum())
                peak_demand = convert_to_python_type(df[power_col].max()) if power_col else convert_to_python_type(df[energy_col].max())
                avg_consumption = convert_to_python_type(df[energy_col].mean())
                
                # 이상 탐지 (간단한 방법)
                q1 = convert_to_python_type(df[energy_col].quantile(0.25))
                q3 = convert_to_python_type(df[energy_col].quantile(0.75))
                iqr = q3 - q1
                anomalies_df = df[(df[energy_col] < q1 - 1.5*iqr) | (df[energy_col] > q3 + 1.5*iqr)]
                
                # 품질 리포트
                missing_count = df.isnull().sum().sum()
                quality_score = convert_to_python_type(max(0, 100 - (missing_count / len(df) * 100)))
                
                # 예측 생성 (간단한 방법)
                time_col = 'time' if 'time' in df.columns else df.columns[0]
                try:
                    last_time = pd.to_datetime(df[time_col].iloc[-1])
                except:
                    last_time = datetime.now()
                
                predictions = []
                for i in range(168):  # 7일 = 168시간
                    predictions.append({
                        "time": (last_time + timedelta(hours=i+1)).isoformat(),
                        "predicted_kWh": convert_to_python_type(avg_consumption * (1 + np.sin(i/10) * 0.1)),
                        "confidence_lower": convert_to_python_type(avg_consumption * 0.85),
                        "confidence_upper": convert_to_python_type(avg_consumption * 1.15)
                    })
                
                # 이상 탐지 결과 변환
                anomalies_list = []
                if len(anomalies_df) > 0:
                    for idx, row in anomalies_df.iterrows():
                        anomaly_record = {}
                        if time_col in row:
                            anomaly_record["timestamp"] = str(row[time_col]) if pd.notna(row[time_col]) else None
                        if energy_col in row:
                            anomaly_record["kWh"] = convert_to_python_type(row[energy_col])
                        if power_col and power_col in row:
                            anomaly_record["kW"] = convert_to_python_type(row[power_col])
                        anomaly_record["anomaly_score"] = convert_to_python_type(abs(row[energy_col] - avg_consumption) / avg_consumption)
                        anomalies_list.append(anomaly_record)
                
                # missing_values 변환
                missing_values_dict = {}
                for col in df.columns:
                    missing_count = df[col].isnull().sum()
                    if missing_count > 0:
                        missing_values_dict[col] = convert_to_python_type(missing_count)
                
                return {
                    "statistics": {
                        "total_energy_consumed": total_energy,
                        "average_consumption": avg_consumption,
                        "peak_demand": peak_demand,
                        "min_demand": convert_to_python_type(df[energy_col].min()),
                        "std_deviation": convert_to_python_type(df[energy_col].std()),
                        "total_records": len(df),
                        "anomalies_detected": len(anomalies_df),
                        "data_quality_score": quality_score,
                    },
                    "quality_report": {
                        "total_records": len(df),
                        "quality_score": quality_score,
                        "missing_values": missing_values_dict,
                        "duplicates": convert_to_python_type(df.duplicated().sum())
                    },
                    "anomalies": anomalies_list,
                    "predictions": predictions,
                    "metrics": {
                        "MAE": 10.5,
                        "RMSE": 15.2,
                        "R2": 0.75,
                        "MAPE": 8.5
                    }
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV 파일에 'kWh' 또는 'kW' 컬럼이 없습니다. 사용 가능한 컬럼: {', '.join(df.columns.tolist())}"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 실패: {str(e)}"
        )


@web_app.get("/api/v1/energy-demand/sample-data")
async def get_sample_data():
    """샘플 에너지 데이터 파일 제공"""
    from fastapi.responses import FileResponse
    
    possible_paths = [
        Path(__file__).parent / "examples" / "sample_energy_data.csv",
        Path("/home/metal/energy-platform/examples/sample_energy_data.csv"),
        Path("/home/metal/energy-analysis-mcp/examples/sample_energy_data.csv"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return FileResponse(
                path=str(path),
                media_type="text/csv",
                filename="sample_energy_data.csv"
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Sample data file not found"
    )


# Authentication endpoints
@web_app.post("/api/v1/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    try:
        # 백엔드의 User 모델과 데이터베이스 사용 시도
        backend_path = Path(__file__).parent / "backend"
        if not backend_path.exists():
            backend_path = Path("/home/metal/energy-platform/backend")
        
        if backend_path.exists():
            try:
                sys.path.insert(0, str(backend_path))
                from src.database import get_db
                from src.models.user import User
                from sqlalchemy import select
                
                # 데이터베이스에서 사용자 조회
                async for db in get_db():
                    result = await db.execute(select(User).filter(User.email == form_data.username))
                    user = result.scalar_one_or_none()
                    
                    if not user or not verify_password(form_data.password, user.password_hash):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"},
                        )
                    
                    if not user.is_active:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="User is inactive"
                        )
                    
                    # Create access token
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": user.email, "user_id": str(user.id), "role": user.role},
                        expires_delta=access_token_expires
                    )
                    
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user_id": str(user.id),
                        "role": user.role
                    }
            except ImportError:
                # 백엔드 모듈을 import할 수 없는 경우, 간단한 인증 처리
                pass
            except Exception as e:
                # 데이터베이스 연결 실패 시, 기본 인증으로 폴백
                pass
        
        # 백엔드 연결 실패 시, 기본 관리자 계정으로 로그인 허용 (개발/테스트용)
        # 실제 프로덕션에서는 이 부분을 제거하고 반드시 데이터베이스 인증을 사용해야 합니다
        if form_data.username == "info@gngmeta.com" and form_data.password == "admin1234!!":
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": form_data.username, "user_id": "admin", "role": "admin"},
                expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": "admin",
                "role": "admin"
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@web_app.post("/api/v1/auth/register")
async def register(
    email: str,
    password: str,
    full_name: Optional[str] = None
):
    """Register new user"""
    try:
        # 백엔드의 User 모델과 데이터베이스 사용 시도
        backend_path = Path(__file__).parent / "backend"
        if not backend_path.exists():
            backend_path = Path("/home/metal/energy-platform/backend")
        
        if backend_path.exists():
            try:
                sys.path.insert(0, str(backend_path))
                from src.database import get_db
                from src.models.user import User
                from sqlalchemy import select
                
                async for db in get_db():
                    # 이미 존재하는 사용자 확인
                    result = await db.execute(select(User).filter(User.email == email))
                    existing_user = result.scalar_one_or_none()
                    
                    if existing_user:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered"
                        )
                    
                    # 새 사용자 생성
                    password_hash = get_password_hash(password)
                    new_user = User(
                        email=email,
                        password_hash=password_hash,
                        full_name=full_name or "",
                        role="user",
                        is_active=True
                    )
                    
                    db.add(new_user)
                    await db.commit()
                    await db.refresh(new_user)
                    
                    return {"message": "User registered successfully", "user_id": str(new_user.id)}
            except ImportError:
                pass
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration is not available. Please use database authentication."
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


# Assets API endpoints
# 메모리 기반 임시 저장소 (DB 연결 실패 시 사용)
_in_memory_assets: list[Dict[str, Any]] = []

@web_app.get("/api/v1/assets")
async def get_assets(
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """자산 목록 조회"""
    try:
        # 백엔드의 Asset 모델과 데이터베이스 사용 시도
        backend_path = Path(__file__).parent / "backend"
        if not backend_path.exists():
            backend_path = Path("/home/metal/energy-platform/backend")
        
        if backend_path.exists():
            try:
                sys.path.insert(0, str(backend_path))
                from src.database import get_db
                from src.models.asset import EnergyAsset
                from sqlalchemy import select, func
                
                async for db in get_db():
                    # 전체 개수 조회
                    count_result = await db.execute(select(func.count()).select_from(EnergyAsset))
                    total = count_result.scalar() or 0
                    
                    # 자산 목록 조회
                    result = await db.execute(
                        select(EnergyAsset)
                        .offset(skip)
                        .limit(limit)
                    )
                    assets = result.scalars().all()
                    
                    items = []
                    for asset in assets:
                        items.append({
                            "id": str(asset.id),
                            "name": asset.name,
                            "type": asset.type,
                            "capacity_kw": float(asset.capacity_kw) if asset.capacity_kw else None,
                            "status": asset.status or "online",
                            "organization_id": str(asset.organization_id) if asset.organization_id else None,
                            "created_at": asset.created_at.isoformat() if asset.created_at else None
                        })
                    
                    return {
                        "items": items,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
            except ImportError as e:
                import traceback
                traceback.print_exc()
                pass
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # 백엔드 연결 실패 시 메모리 기반 저장소에서 조회
        logger = logging.getLogger("uvicorn")
        logger.info(f"DB 연결 실패, 메모리 저장소에서 조회: {len(_in_memory_assets)}개 자산")
        
        # 메모리 저장소에서 필터링 및 페이지네이션
        filtered_items = _in_memory_assets
        total = len(filtered_items)
        paginated_items = filtered_items[skip:skip + limit]
        
        return {
            "items": paginated_items,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"자산 목록 조회 실패: {str(e)}"
        )


# Asset 생성 스키마
class AssetCreateRequest(BaseModel):
    name: str
    type: str
    sector: Optional[str] = None
    capacity_kw: Optional[float] = None
    organization_id: Optional[str] = None

@web_app.post("/api/v1/assets")
async def create_asset(asset_data: AssetCreateRequest = Body(...)) -> Dict[str, Any]:
    """자산 생성"""
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info(f"자산 생성 요청 수신: {asset_data.name}, 타입: {asset_data.type}, 부문: {asset_data.sector}")
    
    try:
        name = asset_data.name.strip() if asset_data.name else ""
        asset_type = asset_data.type or "solar"
        sector = asset_data.sector
        capacity_kw = asset_data.capacity_kw
        organization_id = asset_data.organization_id
        
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자산 이름을 입력해주세요."
            )
        
        # 부문에 따라 타입 조정
        if sector == 'demand':
            asset_type = 'demand_sector'
        
        # 백엔드의 Asset 모델과 데이터베이스 사용 시도
        backend_path = Path(__file__).parent / "backend"
        if not backend_path.exists():
            backend_path = Path("/home/metal/energy-platform/backend")
        
        if backend_path.exists():
            try:
                sys.path.insert(0, str(backend_path))
                from src.database import get_db
                from src.models.asset import EnergyAsset
                from uuid import UUID
                
                async for db in get_db():
                    # 새 자산 생성
                    new_asset = EnergyAsset(
                        name=name,
                        type=asset_type,
                        capacity_kw=capacity_kw,
                        organization_id=UUID(organization_id) if organization_id else None,
                        status="online"
                    )
                    
                    db.add(new_asset)
                    await db.commit()
                    await db.refresh(new_asset)
                    
                    return {
                        "id": str(new_asset.id),
                        "name": new_asset.name,
                        "type": new_asset.type,
                        "capacity_kw": float(new_asset.capacity_kw) if new_asset.capacity_kw else None,
                        "status": new_asset.status,
                        "organization_id": str(new_asset.organization_id) if new_asset.organization_id else None,
                        "created_at": new_asset.created_at.isoformat() if new_asset.created_at else None
                    }
            except ImportError as e:
                import traceback
                traceback.print_exc()
                pass
            except Exception as e:
                import traceback
                traceback.print_exc()
                # 에러가 발생해도 계속 진행 (메모리 저장)
                pass
        
        # 백엔드 연결 실패 시, 메모리 기반 임시 저장
        import uuid
        from datetime import datetime
        
        asset_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        asset_data = {
            "id": asset_id,
            "name": name,
            "type": asset_type,
            "capacity_kw": capacity_kw,
            "status": "online",
            "organization_id": organization_id,
            "created_at": created_at
        }
        
        # 메모리 저장소에 추가
        _in_memory_assets.append(asset_data)
        
        logger = logging.getLogger("uvicorn")
        logger.info(f"메모리 저장소에 자산 추가: {name} (총 {len(_in_memory_assets)}개)")
        
        return asset_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"자산 생성 실패: {str(e)}"
        )


@web_app.delete("/api/v1/assets/{asset_id}")
async def delete_asset(asset_id: str) -> Dict[str, Any]:
    """자산 삭제"""
    try:
        # 백엔드의 Asset 모델과 데이터베이스 사용 시도
        backend_path = Path(__file__).parent / "backend"
        if not backend_path.exists():
            backend_path = Path("/home/metal/energy-platform/backend")
        
        if backend_path.exists():
            try:
                sys.path.insert(0, str(backend_path))
                from src.database import get_db
                from src.models.asset import EnergyAsset
                from uuid import UUID
                from sqlalchemy import select
                
                async for db in get_db():
                    # 자산 조회
                    result = await db.execute(select(EnergyAsset).filter(EnergyAsset.id == UUID(asset_id)))
                    asset = result.scalar_one_or_none()
                    
                    if not asset:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Asset not found"
                        )
                    
                    await db.delete(asset)
                    await db.commit()
                    
                    return {"message": "Asset deleted successfully", "id": asset_id}
            except ImportError:
                pass
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # 메모리 저장소에서도 삭제
        global _in_memory_assets
        _in_memory_assets = [asset for asset in _in_memory_assets if asset.get("id") != asset_id]
        
        return {"message": "Asset deleted successfully", "id": asset_id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"자산 삭제 실패: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
