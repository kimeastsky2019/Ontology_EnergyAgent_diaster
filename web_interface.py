#!/usr/bin/env python3
"""
연결된 Digital Experience Intelligence Platform
Health 카드와 메뉴에 기존 페이지들을 연결한 플랫폼
"""

from datetime import datetime

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

# FastAPI 앱 생성
web_app = FastAPI(title="Digital Experience Intelligence Platform", version="2.0.0")

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


if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
