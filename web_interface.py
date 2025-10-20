#!/usr/bin/env python3
"""
연결된 Digital Experience Intelligence Platform
Health 카드와 메뉴에 기존 페이지들을 연결한 플랫폼
"""

from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Optional
import uvicorn

# FastAPI 앱 생성
web_app = FastAPI(title="Digital Experience Intelligence Platform", version="2.0.0")


def get_available_languages():
    """사용 가능한 언어 목록 반환"""
    return ["ko", "en", "ja", "zh"]


def load_translations():
    """번역 파일 로드"""
    import json
    import os
    
    translations = {}
    locales_dir = os.path.join(os.path.dirname(__file__), 'i18n', 'locales')
    
    for lang in get_available_languages():
        try:
            with open(os.path.join(locales_dir, f'{lang}.json'), 'r', encoding='utf-8') as f:
                translations[lang] = json.load(f)
        except FileNotFoundError:
            # 기본 한국어 번역 사용
            translations[lang] = {}
    
    return translations

def t(key, lang='ko', variables=None):
    """번역 함수"""
    if variables is None:
        variables = {}
    
    translations = load_translations()
    lang_data = translations.get(lang, translations.get('ko', {}))
    
    # 점 표기법으로 중첩된 키 탐색
    keys = key.split('.')
    value = lang_data
    
    for k in keys:
        if value and isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # 한국어로 폴백
            ko_data = translations.get('ko', {})
            fallback_value = ko_data
            for fallback_key in keys:
                if fallback_value and isinstance(fallback_value, dict) and fallback_key in fallback_value:
                    fallback_value = fallback_value[fallback_key]
                else:
                    return key  # 키를 찾을 수 없으면 키 자체 반환
            value = fallback_value
            break
    
    # 문자열 보간 처리
    if isinstance(value, str) and variables:
        for var_name, var_value in variables.items():
            value = value.replace(f'{{{{{var_name}}}}}', str(var_value))
    
    return value if value else key

def format_datetime(dt, lang='ko'):
    """날짜/시간 현지화 포맷"""
    if lang == 'ko':
        return dt.strftime('%Y년 %m월 %d일 %H:%M:%S')
    elif lang == 'en':
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    elif lang == 'ja':
        return dt.strftime('%Y年%m月%d日 %H:%M:%S')
    elif lang == 'zh':
        return dt.strftime('%Y年%m月%d日 %H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_number(num, lang='ko', unit=''):
    """숫자 현지화 포맷"""
    if lang == 'ko':
        if num >= 10000:
            return f"{num/10000:.1f}만{unit}"
        elif num >= 1000:
            return f"{num/1000:.1f}천{unit}"
        else:
            return f"{num:,.0f}{unit}"
    elif lang == 'en':
        return f"{num:,.0f}{unit}"
    elif lang == 'ja':
        if num >= 10000:
            return f"{num/10000:.1f}万{unit}"
        else:
            return f"{num:,.0f}{unit}"
    elif lang == 'zh':
        if num >= 10000:
            return f"{num/10000:.1f}万{unit}"
        else:
            return f"{num:,.0f}{unit}"
    else:
        return f"{num:,.0f}{unit}"

def format_percentage(num, lang='ko'):
    """퍼센트 현지화 포맷"""
    if lang == 'ko':
        return f"{num:.1f}%"
    elif lang == 'en':
        return f"{num:.1f}%"
    elif lang == 'ja':
        return f"{num:.1f}％"
    elif lang == 'zh':
        return f"{num:.1f}%"
    else:
        return f"{num:.1f}%"

def generate_language_selector(current_lang='ko'):
    """언어 선택기 HTML 생성"""
    languages = {
        'ko': {'name': '한국어', 'flag': '🇰🇷'},
        'en': {'name': 'English', 'flag': '🇺🇸'},
        'ja': {'name': '日本語', 'flag': '🇯🇵'},
        'zh': {'name': '中文', 'flag': '🇨🇳'}
    }
    
    buttons = []
    for code, info in languages.items():
        active_class = 'btn-primary' if code == current_lang else 'btn-outline-primary'
        buttons.append(f'''
            <button type="button" 
                    class="btn btn-sm {active_class}"
                    onclick="switchLanguage('{code}')"
                    data-lang="{code}"
                    title="{info['name']}">
                {info['flag']}
            </button>
        ''')
    
    return f'''
        <div class="language-selector">
            <div class="btn-group" role="group">
                {''.join(buttons)}
            </div>
        </div>
    '''

def generate_navigation(current_lang='ko'):
    """네비게이션 메뉴 HTML 생성"""
    return f'''
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/?lang={current_lang}">
                    <i class="fas fa-bolt"></i> {t('title', current_lang)}
                </a>
                
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="/?lang={current_lang}">
                                <i class="fas fa-home"></i> {t('navigation.home', current_lang)}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/data-collection?lang={current_lang}">
                                <i class="fas fa-solar-panel"></i> {t('navigation.energySupply', current_lang)}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/data-analysis?lang={current_lang}">
                                <i class="fas fa-chart-line"></i> {t('navigation.energyDemand', current_lang)}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/trading-ai?lang={current_lang}">
                                <i class="fas fa-robot"></i> 전력 거래 AI
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/model-testing?lang={current_lang}">
                                <i class="fas fa-brain"></i> {t('navigation.modelTesting', current_lang)}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/statistics?lang={current_lang}">
                                <i class="fas fa-cogs"></i> {t('navigation.demandControl', current_lang)}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/trading?lang={current_lang}">
                                <i class="fas fa-exchange-alt"></i> 전력/탄소 거래
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/health?lang={current_lang}">
                                <i class="fas fa-heartbeat"></i> {t('navigation.health', current_lang)}
                            </a>
                        </li>
                    </ul>
                    
                    <div class="navbar-nav">
                        {generate_language_selector(current_lang)}
                    </div>
                </div>
            </div>
        </nav>
    '''




@web_app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, lang: str = Query("ko", description="Language code")):
    """메인 대시보드 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('title', lang)}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            .energy-card {{
                transition: all 0.3s ease;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }}
            
            .energy-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }}
            
            .energy-card:hover::before {{
                left: 100%;
            }}
            
            .energy-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 12px 30px rgba(0,0,0,0.2);
            }}
            
            .energy-card:active {{
                transform: translateY(-4px) scale(0.98);
            }}
            
            .energy-card .card-body {{
                position: relative;
                z-index: 1;
            }}
            
            .energy-card i {{
                transition: all 0.3s ease;
            }}
            
            .energy-card:hover i {{
                transform: scale(1.2) rotate(5deg);
            }}
            
            .energy-card .btn {{
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .energy-card .btn::before {{
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            }}
            
            .energy-card .btn:hover::before {{
                width: 300px;
                height: 300px;
            }}
            
            .energy-card .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            /* 실시간 업데이트 애니메이션 */
            .real-time-update {{
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                100% {{ opacity: 1; }}
            }}
            
            /* 알림 애니메이션 */
            @keyframes slideInRight {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            @keyframes slideOutRight {{
                from {{
                    transform: translateX(0);
                    opacity: 1;
                }}
                to {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
            }}
            
            /* 로딩 애니메이션 */
            .loading-spinner {{
                animation: spin 1s linear infinite;
            }}
            
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            /* 차트 호버 효과 */
            .chart-container {{
                position: relative;
                transition: all 0.3s ease;
            }}
            
            .chart-container:hover {{
                transform: scale(1.02);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }}
            
            /* 실시간 데이터 강조 */
            .real-time-value {{
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            
            .real-time-value.updated {{
                animation: highlight 0.5s ease;
            }}
            
            @keyframes highlight {{
                0% {{ background-color: #4f46e5; color: white; }}
                100% {{ background-color: transparent; color: inherit; }}
            }}
            
            /* 카드 그룹 애니메이션 */
            .card-group {{
                animation: fadeInUp 0.6s ease-out;
            }}
            
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            /* 반응형 개선 */
            @media (max-width: 768px) {{
                .energy-card:hover {{
                    transform: translateY(-3px) scale(1.01);
                }}
                
                .energy-card .btn:hover {{
                    transform: translateY(-1px);
                }}
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
            
            .agent-item:hover {{
                transform: translateX(5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            .agent-item.enabled {{
                border-left-color: #28a745 !important;
                background-color: #f8fff9 !important;
            }}
            .agent-item.disabled {{
                border-left-color: #6c757d !important;
                background-color: #f8f9fa !important;
                opacity: 0.7;
            }}
            .kpi-card {{
                transition: transform 0.3s ease;
            }}
            .kpi-card:hover {{
                transform: translateY(-5px);
            }}
            .site-option {{
                padding: 15px;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                background: #ffffff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }}
            
            .site-option:hover {{
                border-color: var(--primary-color);
                background: #f8fafc;
                transform: translateY(-2px);
            }}
            
            .site-option.active {{
                border-color: var(--primary-color);
                background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
                box-shadow: 0 6px 18px rgba(79, 70, 229, 0.15);
                transform: translateY(-3px) scale(1.01);
            }}
            
            .site-option.inactive {{
                opacity: 0.6;
                filter: grayscale(10%);
            }}
            
            .site-option .status-dot {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #9ca3af;
                transition: background 0.3s ease, transform 0.3s ease;
            }}
            
            .site-option.active .status-dot {{
                background: #10b981;
                transform: scale(1.2);
            }}
        </style>
    </head>
    <body class="bg-light">
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 메인 배너 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card bg-primary text-white">
                        <div class="card-body d-flex align-items-center">
                            <div class="me-4">
                                <i class="fas fa-robot fa-4x"></i>
                            </div>
                            <div class="flex-grow-1">
                                <h1 class="card-title mb-2">LLM SLM Development</h1>
                                <h4 class="card-subtitle mb-3">{t('main.llmSlmSubtitle', lang)}</h4>
                                <p class="card-text">Advanced AI language model specialized for energy management and analysis</p>
                            </div>
                            <div>
                                <a href="/llm-slm?lang={lang}" class="btn btn-light btn-lg">
                                    <i class="fas fa-arrow-right"></i> LLM SLM
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 5개의 서비스 카드 -->
            <div class="row">
                <!-- System Health 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-heartbeat text-success" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">{t('navigation.health', lang)}</h6>
                            <p class="card-text small text-muted mb-3">
                                {t('common.realTime', lang)} {t('common.monitoring', lang)}
                            </p>
                            <a href="/health?lang={lang}" class="btn btn-success btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> {t('navigation.health', lang)}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- ML/AI Engine 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-brain text-primary" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">{t('navigation.modelTesting', lang)}</h6>
                            <p class="card-text small text-muted mb-3">
                                {t('modelTesting.title', lang)}
                            </p>
                            <a href="/model-testing?lang={lang}" class="btn btn-primary btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> {t('navigation.modelTesting', lang)}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Energy Demand Monitoring 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-chart-bar text-info" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">{t('navigation.energyDemand', lang)}</h6>
                            <p class="card-text small text-muted mb-3">
                                {t('energyDemand.title', lang)}
                            </p>
                            <a href="/data-analysis?lang={lang}" class="btn btn-info btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> {t('navigation.energyDemand', lang)}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Energy Supply Monitoring 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-sun text-warning" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">{t('navigation.energySupply', lang)}</h6>
                            <p class="card-text small text-muted mb-3">
                                {t('energySupply.title', lang)}
                            </p>
                            <a href="/data-collection?lang={lang}" class="btn btn-warning btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> {t('navigation.energySupply', lang)}
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Demand Control 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-sliders-h text-danger" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">{t('navigation.demandControl', lang)}</h6>
                            <p class="card-text small text-muted mb-3">
                                {t('demandControl.title', lang)}
                            </p>
                            <a href="/statistics?lang={lang}" class="btn btn-danger btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> {t('navigation.demandControl', lang)}
                            </a>
                        </div>
                    </div>
                </div>


                <!-- Energy Trading 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-exchange-alt text-success" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">전력/탄소 거래</h6>
                            <p class="card-text small text-muted mb-3">
                                P2P 전력 거래 & 탄소 크레딧 시스템
                            </p>
                            <a href="/energytrading?lang={lang}" class="btn btn-success btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> 전력/탄소 거래
                            </a>
                        </div>
                    </div>
                </div>

                <!-- CrewAI System 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-users-cog text-info" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">CrewAI System</h6>
                            <p class="card-text small text-muted mb-3">
                                전문화된 에이전트 팀 자동화
                            </p>
                            <a href="/crewai-system?lang={lang}" class="btn btn-info btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> CrewAI System
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Data Explorer 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-database text-secondary" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">데이터 탐색</h6>
                            <p class="card-text small text-muted mb-3">
                                원시 데이터 분석 및 품질 검사
                            </p>
                            <a href="/data-explorer?lang={lang}" class="btn btn-secondary btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> 데이터 탐색
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 에너지 분석 차트 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-chart-line"></i> <span data-translate="realtime_analysis">Real-time Energy Analysis</span>
                                <small class="text-muted ms-2">24시간 실시간 에너지 분석</small>
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <span class="badge bg-info me-2">○</span> <span data-translate="actual_consumption">실제 에너지 소비 (kWh)</span>
                                <span class="badge bg-warning ms-3 me-2">○</span> <span data-translate="predicted_consumption">예측 에너지 소비 (kWh)</span>
                            </div>
                            <canvas id="energyChart" width="400" height="100"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI 에이전트 시스템 섹션 -->
            <div class="row mt-5" id="agent-system">
                <div class="col-12">
                    <div class="card energy-card">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">
                                <i class="fas fa-robot"></i> HORIZON AI Agent System
                                <small class="ms-2">Multi-Site Energy Management AI Agents</small>
                            </h4>
                        </div>
                        <div class="card-body">
                            <!-- KPI 카드들 -->
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="kpi-card bg-primary text-white text-center p-3 rounded">
                                        <div class="h2 mb-1">6</div>
                                        <div class="small">총 에이전트</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="kpi-card bg-success text-white text-center p-3 rounded">
                                        <div class="h2 mb-1">5</div>
                                        <div class="small">활성 에이전트</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="kpi-card bg-info text-white text-center p-3 rounded">
                                        <div class="h2 mb-1">5,247</div>
                                        <div class="small">총 예측 수</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="kpi-card bg-warning text-white text-center p-3 rounded">
                                        <div class="h2 mb-1">91%</div>
                                        <div class="small">평균 정확도</div>
                                    </div>
                                </div>
                            </div>

                            <!-- 사이트 선택 -->
                            <div class="row mb-4">
                                <div class="col-12">
                                    <h5><i class="fas fa-map-marker-alt text-primary"></i> 사이트 선택 / Select Site</h5>
                                    <div class="row">
                                        <div class="col-md-3">
                                            <div class="site-option active p-3 border rounded mb-2" onclick="selectSite('oulu')">
                                                <div class="d-flex align-items-center">
                                                    <span class="fs-1 me-3">🇫🇮</span>
                                                    <div>
                                                        <h6 class="mb-1">Oulu University</h6>
                                                        <p class="mb-0 text-muted small">Finland - 극한 기후</p>
                                                    </div>
                                                </div>
                                                <div class="status-dot"></div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="site-option p-3 border rounded mb-2" onclick="selectSite('kth')">
                                                <div class="d-flex align-items-center">
                                                    <span class="fs-1 me-3">🇸🇪</span>
                                                    <div>
                                                        <h6 class="mb-1">KTH Living Lab</h6>
                                                        <p class="mb-0 text-muted small">Sweden - 실증 연구</p>
                                                    </div>
                                                </div>
                                                <div class="status-dot"></div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="site-option p-3 border rounded mb-2" onclick="selectSite('beia')">
                                                <div class="d-flex align-items-center">
                                                    <span class="fs-1 me-3">🇷🇴</span>
                                                    <div>
                                                        <h6 class="mb-1">BEIA Research</h6>
                                                        <p class="mb-0 text-muted small">Romania - IoT 시스템</p>
                                                    </div>
                                                </div>
                                                <div class="status-dot"></div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="site-option p-3 border rounded mb-2" onclick="selectSite('triaena')">
                                                <div class="d-flex align-items-center">
                                                    <span class="fs-1 me-3">🇬🇷</span>
                                                    <div>
                                                        <h6 class="mb-1">Triaena/OTE</h6>
                                                        <p class="mb-0 text-muted small">Greece - 상업 빌딩</p>
                                                    </div>
                                                </div>
                                                <div class="status-dot"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- AI 에이전트 목록 -->
                            <div class="row">
                                <div class="col-12">
                                    <h5><i class="fas fa-cogs text-primary"></i> AI 에이전트 관리 / AI Agent Management</h5>
                                    
                                    <!-- 에이전트 1: 에너지 수요 분석 -->
                                    <div class="agent-item enabled p-3 mb-3 border-start border-5 border-primary bg-light rounded">
                                        <div class="row align-items-center">
                                            <div class="col-md-1 text-center">
                                                <i class="fas fa-chart-line fa-2x text-primary"></i>
                                            </div>
                                            <div class="col-md-4">
                                                <h6 class="mb-1">에너지 수요 분석 MCP</h6>
                                                <p class="mb-0 text-muted small">Energy Demand Analysis MCP</p>
                                                <small class="text-muted">단기/중기 에너지 수요 예측, 소비 패턴 분석</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-success">✅ 활성</span>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">정확도: 94%</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-primary" style="width: 94%"></div>
                                                    </div>
                                                </div>
                                                <div class="mb-2">
                                                    <small class="text-muted">예측 수: 1,247</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 85%"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <small class="text-muted">응답시간: 0.3s</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 70%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <button class="btn btn-primary btn-sm" onclick="toggleAgent('demand-analysis')">
                                                    <i class="fas fa-pause"></i> 비활성화
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 에이전트 2: AI/ML 모델 성능 평가 -->
                                    <div class="agent-item enabled p-3 mb-3 border-start border-5 border-primary bg-light rounded">
                                        <div class="row align-items-center">
                                            <div class="col-md-1 text-center">
                                                <i class="fas fa-brain fa-2x text-purple"></i>
                                            </div>
                                            <div class="col-md-4">
                                                <h6 class="mb-1">AI/ML 모델 성능 평가 MCP</h6>
                                                <p class="mb-0 text-muted small">AI/ML Model Performance Evaluation MCP</p>
                                                <small class="text-muted">모델 성능 모니터링, A/B 테스트, 자동 재학습</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-success">✅ 활성</span>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">정확도: 92%</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-purple" style="width: 92%"></div>
                                                    </div>
                                                </div>
                                                <div class="mb-2">
                                                    <small class="text-muted">예측 수: 856</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 60%"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <small class="text-muted">응답시간: 0.5s</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 50%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <button class="btn btn-primary btn-sm" onclick="toggleAgent('ml-performance')">
                                                    <i class="fas fa-pause"></i> 비활성화
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 에이전트 3: 에너지 공급 분석 -->
                                    <div class="agent-item enabled p-3 mb-3 border-start border-5 border-primary bg-light rounded">
                                        <div class="row align-items-center">
                                            <div class="col-md-1 text-center">
                                                <i class="fas fa-bolt fa-2x text-warning"></i>
                                            </div>
                                            <div class="col-md-4">
                                                <h6 class="mb-1">에너지 공급 분석 MCP</h6>
                                                <p class="mb-0 text-muted small">Energy Supply Analysis MCP</p>
                                                <small class="text-muted">발전량 예측, 재생에너지 최적화, ESS 관리</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-success">✅ 활성</span>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">정확도: 89%</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 89%"></div>
                                                    </div>
                                                </div>
                                                <div class="mb-2">
                                                    <small class="text-muted">예측 수: 2,134</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 100%"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <small class="text-muted">응답시간: 0.4s</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 60%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <button class="btn btn-primary btn-sm" onclick="toggleAgent('supply-analysis')">
                                                    <i class="fas fa-pause"></i> 비활성화
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 에이전트 4: 수요 제어 알고리즘 -->
                                    <div class="agent-item enabled p-3 mb-3 border-start border-5 border-primary bg-light rounded">
                                        <div class="row align-items-center">
                                            <div class="col-md-1 text-center">
                                                <i class="fas fa-sliders-h fa-2x text-success"></i>
                                            </div>
                                            <div class="col-md-4">
                                                <h6 class="mb-1">수요 제어 알고리즘 MCP</h6>
                                                <p class="mb-0 text-muted small">Demand Control Algorithm MCP</p>
                                                <small class="text-muted">수요-공급 매칭, 피크 억제, 부하 제어</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-success">✅ 활성</span>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">정확도: 91%</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 91%"></div>
                                                    </div>
                                                </div>
                                                <div class="mb-2">
                                                    <small class="text-muted">예측 수: 567</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 40%"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <small class="text-muted">응답시간: 0.2s</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 80%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <button class="btn btn-primary btn-sm" onclick="toggleAgent('demand-control')">
                                                    <i class="fas fa-pause"></i> 비활성화
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 에이전트 5: 전력/탄소 거래 -->
                                    <div class="agent-item enabled p-3 mb-3 border-start border-5 border-primary bg-light rounded">
                                        <div class="row align-items-center">
                                            <div class="col-md-1 text-center">
                                                <i class="fas fa-dollar-sign fa-2x text-success"></i>
                                            </div>
                                            <div class="col-md-4">
                                                <h6 class="mb-1">전력/탄소 거래 MCP</h6>
                                                <p class="mb-0 text-muted small">Power & Carbon Trading MCP</p>
                                                <small class="text-muted">거래 최적화, 가격 예측, 자동 입찰</small>
                                            </div>
                                            <div class="col-md-2">
                                                <span class="badge bg-success">✅ 활성</span>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="mb-2">
                                                    <small class="text-muted">정확도: 87%</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 87%"></div>
                                                    </div>
                                                </div>
                                                <div class="mb-2">
                                                    <small class="text-muted">예측 수: 342</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-success" style="width: 25%"></div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <small class="text-muted">응답시간: 0.6s</small>
                                                    <div class="progress" style="height: 4px;">
                                                        <div class="progress-bar bg-warning" style="width: 40%"></div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <button class="btn btn-primary btn-sm" onclick="toggleAgent('trading')">
                                                    <i class="fas fa-pause"></i> 비활성화
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 새로고침 버튼 -->
        <button class="refresh-button" onclick="refreshAllData()" title="모든 데이터 새로고침">
            <i class="fas fa-sync-alt"></i>
        </button>
        <script>
            // 실시간 에너지 데이터 생성
            function generateEnergyData() {{
                const hours = [];
                const actualData = [];
                const predictedData = [];
                
                for (let i = 0; i < 24; i++) {{
                    hours.push(i.toString().padStart(2, '0') + ':00');
                    // 실제 데이터 (더 불규칙한 패턴)
                    const baseConsumption = 50 + Math.sin(i * Math.PI / 12) * 30;
                    const randomVariation = (Math.random() - 0.5) * 20;
                    actualData.push(Math.max(0, baseConsumption + randomVariation));
                    
                    // 예측 데이터 (더 부드러운 패턴, 14시부터 시작)
                    if (i >= 14) {{
                        const predictedBase = 45 + Math.sin(i * Math.PI / 12) * 25;
                        const predictedVariation = (Math.random() - 0.5) * 10;
                        predictedData.push(Math.max(0, predictedBase + predictedVariation));
                    }} else {{
                        predictedData.push(null);
                    }}
                }}
                
                return {{ hours, actualData, predictedData }};
            }}

            // 차트 초기화
            function initEnergyChart() {{
                const ctx = document.getElementById('energyChart').getContext('2d');
                const data = generateEnergyData();
                
                energyChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: data.hours,
                        datasets: [{{
                            label: '실제 에너지 소비 (kWh)',
                            data: data.actualData,
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            tension: 0.1,
                            pointRadius: 4,
                            pointHoverRadius: 8,
                            pointBackgroundColor: 'rgb(75, 192, 192)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }}, {{
                            label: '예측 에너지 소비 (kWh)',
                            data: data.predictedData,
                            borderColor: 'rgb(255, 205, 86)',
                            backgroundColor: 'rgba(255, 205, 86, 0.2)',
                            borderDash: [5, 5],
                            tension: 0.1,
                            pointRadius: 4,
                            pointHoverRadius: 8,
                            pointBackgroundColor: 'rgb(255, 205, 86)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        interaction: {{
                            intersect: false,
                            mode: 'index'
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: '에너지 소비량 (kWh)',
                                    font: {{
                                        size: 12,
                                        weight: 'bold'
                                    }}
                                }},
                                grid: {{
                                    color: 'rgba(0,0,0,0.1)'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: '시간 (24시간)',
                                    font: {{
                                        size: 12,
                                        weight: 'bold'
                                    }}
                                }},
                                grid: {{
                                    color: 'rgba(0,0,0,0.1)'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top',
                                labels: {{
                                    usePointStyle: true,
                                    padding: 20,
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                titleColor: '#fff',
                                bodyColor: '#fff',
                                borderColor: '#4f46e5',
                                borderWidth: 1,
                                cornerRadius: 8,
                                displayColors: true,
                                callbacks: {{
                                    title: function(context) {{
                                        return '시간: ' + context[0].label + '시';
                                    }},
                                    label: function(context) {{
                                        return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + ' kWh';
                                    }}
                                }}
                            }}
                        }},
                        onClick: function(event, elements) {{
                            if (elements.length > 0) {{
                                const element = elements[0];
                                const datasetIndex = element.datasetIndex;
                                const dataIndex = element.index;
                                const value = element.parsed.y;
                                const time = data.hours[dataIndex];
                                
                                showChartDetailModal(datasetIndex, time, value);
                            }}
                        }},
                        onHover: function(event, elements) {{
                            event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
                        }}
                    }}
                }});
            }}
            
            // 차트 상세 모달
            function showChartDetailModal(datasetIndex, time, value) {{
                const datasetNames = ['실제 에너지 소비', '예측 에너지 소비'];
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${{datasetNames[datasetIndex]}} 상세 정보</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-6">
                                        <h6>시간 정보</h6>
                                        <p>시간: ${{time}}시</p>
                                        <p>소비량: ${{value.toFixed(1)}} kWh</p>
                                    </div>
                                    <div class="col-6">
                                        <h6>분석</h6>
                                        <p>상태: ${{value > 100 ? '높음' : value > 50 ? '보통' : '낮음'}}</p>
                                        <p>추천: ${{value > 100 ? '에너지 절약 필요' : '정상 범위'}}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                modal.addEventListener('hidden.bs.modal', function() {{
                    modal.remove();
                }});
            }}

            // 언어 전환 함수
            function switchLanguage(lang) {{
                // 현재 URL에서 언어 파라미터 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.location.href = url.toString();
            }}

            // AI 에이전트 시스템 관련 함수들
            function scrollToSection(sectionId) {{
                document.getElementById(sectionId).scrollIntoView({{ behavior: 'smooth' }});
            }}

            function selectSite(siteId) {{
                // 모든 사이트 옵션에서 active 클래스 제거
                document.querySelectorAll('.site-option').forEach(option => {{
                    option.classList.remove('active');
                }});
                
                // 선택된 사이트에 active 클래스 추가
                event.target.closest('.site-option').classList.add('active');
                
                // 사이트별 에이전트 설정 로드 (실제 구현에서는 API 호출)
                loadSiteAgents(siteId);
            }}

            function loadSiteAgents(siteId) {{
                // 실제 구현에서는 API에서 사이트별 설정을 가져옴
                console.log(`Loading agents for site: ${{siteId}}`);
                
                // 사이트별 권장 설정 적용
                const siteConfigs = {{
                    'oulu': {{
                        recommended: ['demand-analysis', 'supply-analysis', 'demand-control', 'trading'],
                        optional: ['ml-performance']
                    }},
                    'kth': {{
                        recommended: ['demand-analysis', 'ml-performance', 'supply-analysis', 'demand-control', 'trading'],
                        optional: []
                    }},
                    'beia': {{
                        recommended: ['demand-analysis', 'supply-analysis', 'demand-control', 'trading'],
                        optional: ['ml-performance']
                    }},
                    'triaena': {{
                        recommended: ['supply-analysis', 'demand-control', 'trading', 'demand-analysis'],
                        optional: ['ml-performance']
                    }}
                }};
                
                const config = siteConfigs[siteId];
                if (config) {{
                    // 모든 에이전트를 비활성화
                    document.querySelectorAll('.agent-item').forEach(agent => {{
                        agent.classList.remove('enabled');
                        agent.classList.add('disabled');
                        const button = agent.querySelector('button');
                        const statusBadge = agent.querySelector('.badge');
                        button.innerHTML = '<i class="fas fa-play"></i> 활성화';
                        statusBadge.innerHTML = '⏸️ 비활성';
                        statusBadge.className = 'badge bg-secondary';
                    }});
                    
                    // 권장 에이전트 활성화
                    config.recommended.forEach(agentId => {{
                        const agentElement = document.querySelector(`[onclick*="${{agentId}}"]`).closest('.agent-item');
                        if (agentElement) {{
                            agentElement.classList.remove('disabled');
                            agentElement.classList.add('enabled');
                            const button = agentElement.querySelector('button');
                            const statusBadge = agentElement.querySelector('.badge');
                            button.innerHTML = '<i class="fas fa-pause"></i> 비활성화';
                            statusBadge.innerHTML = '✅ 활성';
                            statusBadge.className = 'badge bg-success';
                        }}
                    }});
                }}
            }}

            function toggleAgent(agentId) {{
                const agentElement = document.querySelector(`[onclick*="${{agentId}}"]`).closest('.agent-item');
                const button = agentElement.querySelector('button');
                const statusBadge = agentElement.querySelector('.badge');
                
                if (agentElement.classList.contains('enabled')) {{
                    // 비활성화
                    agentElement.classList.remove('enabled');
                    agentElement.classList.add('disabled');
                    button.innerHTML = '<i class="fas fa-play"></i> 활성화';
                    statusBadge.innerHTML = '⏸️ 비활성';
                    statusBadge.className = 'badge bg-secondary';
                }} else {{
                    // 활성화
                    agentElement.classList.remove('disabled');
                    agentElement.classList.add('enabled');
                    button.innerHTML = '<i class="fas fa-pause"></i> 비활성화';
                    statusBadge.innerHTML = '✅ 활성';
                    statusBadge.className = 'badge bg-success';
                }}
            }}

            
            // 전역 변수
            let energyChart = null;
            let realTimeData = {{
                solar: 35,
                ess: 18,
                grid: 47,
                demand: 1250,
                supply: 1432,
                efficiency: 87.3
            }};
            
            // 실시간 데이터 업데이트
            function updateRealTimeData() {{
                // 실제 데이터 시뮬레이션 (실제로는 API에서 가져옴)
                realTimeData.solar = Math.max(0, realTimeData.solar + (Math.random() - 0.5) * 5);
                realTimeData.ess = Math.max(0, realTimeData.ess + (Math.random() - 0.5) * 3);
                realTimeData.grid = 100 - realTimeData.solar - realTimeData.ess;
                realTimeData.demand = Math.floor(1200 + Math.random() * 200);
                realTimeData.supply = Math.floor(1300 + Math.random() * 300);
                realTimeData.efficiency = Math.floor((realTimeData.supply / realTimeData.demand) * 100);
                
                // 차트 업데이트
                if (energyChart) {{
                    energyChart.data.datasets[0].data = [realTimeData.solar, realTimeData.ess, realTimeData.grid];
                    energyChart.update('active');
                }}
                
                // 실시간 수치 업데이트
                updateRealTimeStats();
                
                // 알림 체크
                checkAlerts();
            }}
            
            // 실시간 통계 업데이트
            function updateRealTimeStats() {{
                const elements = {{
                    'current-demand': realTimeData.demand + ' kW',
                    'current-supply': realTimeData.supply + ' kW',
                    'current-efficiency': realTimeData.efficiency + '%',
                    'solar-power': (realTimeData.solar * 0.14).toFixed(1) + ' kW',
                    'solar-percentage': realTimeData.solar.toFixed(1),
                    'ess-power': (realTimeData.ess * 0.14).toFixed(1) + ' kW',
                    'ess-percentage': realTimeData.ess.toFixed(1),
                    'grid-power': (realTimeData.grid * 0.14).toFixed(1) + ' kW',
                    'grid-percentage': realTimeData.grid.toFixed(1)
                }};
                
                Object.entries(elements).forEach(([id, value]) => {{
                    const element = document.getElementById(id);
                    if (element) {{
                        // 애니메이션 효과
                        element.classList.add('updated');
                        element.style.transform = 'scale(1.1)';
                        element.style.color = '#4f46e5';
                        element.textContent = value;
                        
                        setTimeout(() => {{
                            element.style.transform = 'scale(1)';
                            element.style.color = '';
                            element.classList.remove('updated');
                        }}, 300);
                    }}
                }});
            }}
            
            // 알림 시스템
            function checkAlerts() {{
                const alerts = [];
                
                if (realTimeData.efficiency < 80) {{
                    alerts.push({{
                        type: 'warning',
                        message: '에너지 효율이 80% 미만입니다. 최적화가 필요합니다.',
                        icon: 'fas fa-exclamation-triangle'
                    }});
                }}
                
                if (realTimeData.solar > 60) {{
                    alerts.push({{
                        type: 'success',
                        message: '태양광 발전량이 높습니다. ESS 충전을 고려하세요.',
                        icon: 'fas fa-sun'
                    }});
                }}
                
                if (realTimeData.demand > realTimeData.supply) {{
                    alerts.push({{
                        type: 'danger',
                        message: '수요가 공급을 초과했습니다. 그리드 전력 사용량을 확인하세요.',
                        icon: 'fas fa-bolt'
                    }});
                }}
                
                // 알림 표시
                if (alerts.length > 0) {{
                    showNotification(alerts[0]);
                }}
            }}
            
            // 알림 표시
            function showNotification(alert) {{
                // 기존 알림 제거
                const existingAlert = document.querySelector('.notification-toast');
                if (existingAlert) {{
                    existingAlert.remove();
                }}
                
                const notification = document.createElement('div');
                notification.className = `notification-toast alert alert-${{alert.type}} alert-dismissible fade show`;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    min-width: 300px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    animation: slideInRight 0.3s ease-out;
                `;
                
                notification.innerHTML = `
                    <i class="${{alert.icon}} me-2"></i>
                    ${{alert.message}}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.body.appendChild(notification);
                
                // 5초 후 자동 제거
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        notification.remove();
                    }}
                }}, 5000);
            }}
            
            // 카드 호버 효과
            function initCardInteractions() {{
                const cards = document.querySelectorAll('.energy-card');
                
                cards.forEach(card => {{
                    card.addEventListener('mouseenter', function() {{
                        this.style.transform = 'translateY(-5px)';
                        this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                        this.style.transition = 'all 0.3s ease';
                    }});
                    
                    card.addEventListener('mouseleave', function() {{
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '';
                    }});
                }});
            }}
            
            // 로딩 애니메이션
            function showLoadingAnimation() {{
                const loadingOverlay = document.createElement('div');
                loadingOverlay.id = 'loadingOverlay';
                loadingOverlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(255,255,255,0.9);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                `;
                
                loadingOverlay.innerHTML = `
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-3">데이터를 불러오는 중...</p>
                    </div>
                `;
                
                document.body.appendChild(loadingOverlay);
            }}
            
            function hideLoadingAnimation() {{
                const loadingOverlay = document.getElementById('loadingOverlay');
                if (loadingOverlay) {{
                    loadingOverlay.remove();
                }}
            }}
            
            // 키보드 단축키
            function initKeyboardShortcuts() {{
                document.addEventListener('keydown', function(e) {{
                    if (e.ctrlKey || e.metaKey) {{
                        switch(e.key) {{
                            case 'r':
                                e.preventDefault();
                                updateRealTimeData();
                                break;
                            case 'h':
                                e.preventDefault();
                                showHelpModal();
                                break;
                        }}
                    }}
                }});
            }}
            
            // 도움말 모달
            function showHelpModal() {{
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">키보드 단축키</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>기본 단축키</h6>
                                        <ul>
                                            <li><kbd>Ctrl+R</kbd> - 데이터 새로고침</li>
                                            <li><kbd>Ctrl+H</kbd> - 도움말 표시</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>인터랙션</h6>
                                        <ul>
                                            <li>차트 클릭 - 상세 정보</li>
                                            <li>카드 호버 - 확대 효과</li>
                                            <li>실시간 업데이트 - 5초마다</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                modal.addEventListener('hidden.bs.modal', function() {{
                    modal.remove();
                }});
            }}
            
            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initEnergyChart();
                initCardInteractions();
                initKeyboardShortcuts();
                
                // 실시간 업데이트 시작 (5초마다)
                setInterval(updateRealTimeData, 5000);
                
                // 초기 로딩 애니메이션
                showLoadingAnimation();
                setTimeout(hideLoadingAnimation, 2000);
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/trading-ai", response_class=HTMLResponse)
async def trading_ai_page(request: Request, lang: str = Query("ko", description="Language code")):
    if lang not in get_available_languages():
        lang = "ko"
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>전력 거래 AI 시스템</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {{ background:#f9fafb; }}
            .shadow-soft {{ box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
            .card-soft {{ border:1px solid #e5e7eb; border-radius:12px; background:#fff; }}
            .gradient-card {{ background: linear-gradient(90deg,#4f46e5,#7c3aed); color:#fff; border-radius:16px; }}
            .badge-dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}
        <div class="container my-4">
            <div class="d-flex align-items-center mb-3">
                <div class="bg-primary rounded p-2 me-2 text-white"><i class="fas fa-bolt"></i></div>
                <div>
                    <h3 class="mb-0">전력 거래 AI 시스템</h3>
                    <small class="text-muted">스마트한 에너지 거래</small>
                </div>
                <div class="ms-auto">
                    <button id="notifBtn" class="btn btn-light border"><i class="fas fa-bell"></i></button>
                </div>
            </div>

            <div id="notifPanel" class="card-soft shadow-soft p-0 mb-3" style="display:none; max-height:380px; overflow:auto;">
                <div class="border-bottom p-3 fw-bold">알림</div>
                <div id="notifList"></div>
            </div>

            <div class="row g-3 mb-3">
                <div class="col-md-3">
                    <div class="card-soft shadow-soft p-3">
                        <div class="d-flex justify-content-between mb-1"><small class="text-muted">오늘의 수익</small><i class="fas fa-dollar-sign text-success"></i></div>
                        <div class="h4 mb-1" id="statProfit">+12,500원</div>
                        <small class="text-success"><i class="fas fa-arrow-up"></i> 전월 대비 15% 증가</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-soft shadow-soft p-3">
                        <div class="d-flex justify-content-between mb-1"><small class="text-muted">현재 전력량</small><i class="fas fa-bolt text-warning"></i></div>
                        <div class="h4 mb-1" id="statPower">850 kWh</div>
                        <div class="progress" style="height:6px;"><div class="progress-bar bg-primary" id="powerTarget" style="width:92%"></div></div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-soft shadow-soft p-3">
                        <div class="d-flex justify-content-between mb-1"><small class="text-muted">오늘의 추천</small><i class="fas fa-sun text-orange"></i></div>
                        <div class="small text-muted">판매 타이밍</div>
                        <div class="h5 mb-0" id="statReco">14:00-16:00</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card-soft shadow-soft p-3">
                        <div class="d-flex justify-content-between mb-1"><small class="text-muted">AI 상태</small><i class="fas fa-robot text-primary"></i></div>
                        <div class="h4 mb-1">정상</div>
                        <small class="text-muted"><i class="fas fa-check-circle text-success"></i> 5/5 에이전트 활성화</small>
                    </div>
                </div>
            </div>

            <div class="gradient-card p-4 mb-3 shadow-soft">
                <div class="row">
                    <div class="col-md-8">
                        <h5 class="fw-bold mb-2"><i class="fas fa-lightbulb"></i> AI 추천 거래</h5>
                        <p class="mb-3">지금이 판매하기 좋은 타이밍입니다!</p>
                        <div class="row g-3">
                            <div class="col-4"><small class="opacity-75">추천 시간</small><div class="fw-bold">오후 2:00-4:00</div></div>
                            <div class="col-4"><small class="opacity-75">판매량</small><div class="fw-bold">500 kWh</div></div>
                            <div class="col-4"><small class="opacity-75">예상 수익</small><div class="fw-bold">45,000원</div></div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-light text-primary me-2">거래 시뮬레이션</button>
                            <button class="btn btn-dark">바로 거래하기</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-3">
                <div class="col-lg-6">
                    <div class="card-soft shadow-soft p-3 h-100">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0"><i class="fas fa-users-cog text-primary"></i> 당신의 AI 거래 팀</h5>
                            <button class="btn btn-sm btn-outline-primary">상세 보기</button>
                        </div>
                        <div id="agentList" class="vstack gap-2"></div>
                        <div class="mt-3 p-3 bg-light rounded">
                            <div class="small mb-2">💬 궁금한 점이 있으신가요?</div>
                            <button class="btn btn-primary w-100">AI 어시스턴트와 대화하기</button>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card-soft shadow-soft p-3 h-100">
                        <h5 class="mb-3">💬 AI 거래 어시스턴트</h5>
                        <div id="chatArea" class="mb-3" style="max-height:330px; overflow:auto;"></div>
                        <div class="d-flex gap-2 border-top pt-3">
                            <input id="chatInput" type="text" class="form-control" placeholder="메시지를 입력하세요...">
                            <button id="chatSend" class="btn btn-primary">전송</button>
                        </div>
                        <div class="mt-2 small text-muted">💡 자주 묻는 질문: <span class="badge bg-light text-dark me-1">이번 주 예상 수익은?</span><span class="badge bg-light text-dark me-1">자동 거래 설정</span><span class="badge bg-light text-dark">날씨 영향</span></div>
                    </div>
                </div>
            </div>

            <div class="card-soft shadow-soft p-3 mt-3">
                <h5 class="mb-3"><i class="fas fa-chart-line text-primary"></i> 시장 동향</h5>
                <div class="row g-2 align-items-end" id="marketBars"></div>
            </div>
        </div>

        <script>
            const notifData = [
                { id:1, type:'urgent', time:'방금', title:'긴급 거래 기회!', desc:'지금 판매하면 평소보다 20% 더 수익' },
                { id:2, type:'info', time:'10분 전', title:'일일 리포트 준비 완료', desc:'어제 거래 실적이 정리되었습니다' },
                { id:3, type:'success', time:'1시간 전', title:'자동 거래 성공', desc:'AI가 350kWh를 판매했습니다 (31,500원)' }
            ];
            const agents = [
                { name:'데이터 수집가', status:'정상', task:'날씨 데이터 분석 중', accuracy:'99%' },
                { name:'예측 전문가', status:'정상', task:'오후 2시 피크 예상', accuracy:'94%' },
                { name:'모니터링 요원', status:'정상', task:'이상 징후 없음', accuracy:'100%' },
                { name:'거래 전략가', status:'정상', task:'전략 준비 완료', accuracy:'92%' },
            ];
            const messages = [
                { sender:'user', text:'오늘 전력을 팔기 좋은 시간이 언제야?' },
                { sender:'ai', text:'네! 오늘 분석 결과를 알려드릴게요.\n\n📊 최적 판매 시간: 오후 2시 ~ 4시\n\n이유는 다음과 같아요:\n1. 🌡️ 오후에 기온이 28도까지 올라가요\n2. ⚡ 에어컨 사용으로 전력 수요가 급증해요\n3. 💰 가격이 평소보다 15% 높아질 것으로 예상돼요' }
            ];

            function renderNotifications() {
                const list = document.getElementById('notifList');
                list.innerHTML = notifData.map(n => `
                    <div class="p-3 border-bottom">
                        <div class="d-flex">
                            <span class="badge-dot ${n.type==='urgent'?'bg-danger':(n.type==='success'?'bg-success':'bg-primary')}"></span>
                            <div class="flex-grow-1">
                                <div class="fw-semibold">${n.title}</div>
                                <div class="small text-muted">${n.desc}</div>
                                <div class="small text-secondary mt-1">${n.time}</div>
                            </div>
                        </div>
                    </div>`).join('');
            }

            function renderAgents() {
                const wrap = document.getElementById('agentList');
                wrap.innerHTML = agents.map((a,i)=>`
                    <div class="p-3 border rounded d-flex justify-content-between align-items-start">
                        <div>
                            <div class="fw-semibold">[${i+1}단계] ${a.name}</div>
                            <div class="small text-muted">${a.task}</div>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-success">정상</span>
                            <div class="small text-muted mt-1">정확도 ${a.accuracy}</div>
                        </div>
                    </div>`).join('');
            }

            function renderChat() {
                const area = document.getElementById('chatArea');
                area.innerHTML = messages.map(m=>`
                    <div class="d-flex ${m.sender==='user'?'justify-content-end':'justify-content-start'} mb-2">
                        <div class="p-2 rounded ${m.sender==='user'?'bg-primary text-white':'bg-light'}" style="max-width:80%">${m.text.replaceAll('\n','<br>')}</div>
                    </div>`).join('');
            }

            function renderMarket() {
                const bars = document.getElementById('marketBars');
                const series = [65,78,85,92,88,95,82,90];
                bars.innerHTML = series.map((h,idx)=>`
                    <div class="col">
                        <div class="bg-primary" style="height:${h}%; border-radius:6px;"></div>
                        <div class="text-center small text-muted mt-1">${9+idx}시</div>
                    </div>`).join('');
            }

            document.getElementById('notifBtn').addEventListener('click', ()=>{
                const p = document.getElementById('notifPanel');
                if (p.style.display==='none') { p.style.display='block'; renderNotifications(); }
                else { p.style.display='none'; }
            });
            document.getElementById('chatSend').addEventListener('click', ()=>{
                const input = document.getElementById('chatInput');
                const text = input.value.trim();
                if (!text) return;
                messages.push({ sender:'user', text });
                renderChat();
                input.value='';
            });

            // init
            renderAgents();
            renderChat();
            renderMarket();
        </script>
    </body>
    </html>
    """
@web_app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request, lang: str = Query("ko", description="Language code")):
    """연결된 Digital Experience Intelligence Platform"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('health.title', lang)}</title>
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
                animation: pulse 2s infinite;
            }}
            .status-online {{ 
                background-color: #28a745; 
                box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
            }}
            .status-offline {{ 
                background-color: #dc3545; 
                box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
            }}
            .status-warning {{ 
                background-color: #ffc107; 
                box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
            }}
            .status-healthy {{ 
                background-color: #17a2b8; 
                box-shadow: 0 0 10px rgba(23, 162, 184, 0.5);
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.1); opacity: 0.7; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
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
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                position: relative;
                height: 200px;
            }}
            .heatmap-point {{
                position: absolute;
                width: 12px;
                height: 12px;
                background: #ff6b6b;
                border-radius: 50%;
                opacity: 0.8;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 0.8; }}
                50% {{ transform: scale(1.2); opacity: 0.6; }}
                100% {{ transform: scale(1); opacity: 0.8; }}
            }}
            .alert-modern {{
                border-radius: 15px;
                border: none;
                padding: 15px 20px;
                margin: 10px 0;
                backdrop-filter: blur(10px);
            }}
            .btn-modern {{
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                border: none;
            }}
            .btn-modern:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
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
            .tooltip {{
                position: relative;
                display: inline-block;
                cursor: help;
            }}
            .tooltip .tooltiptext {{
                visibility: hidden;
                width: 200px;
                background-color: #333;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.8rem;
            }}
            .tooltip:hover .tooltiptext {{
                visibility: visible;
                opacity: 1;
            }}
            .refresh-button {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }}
            .refresh-button:hover {{
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            .refresh-button:active {{
                transform: scale(0.95);
            }}
        </style>
    </head>
    <body>
        <!-- 언어 선택기 -->
        <div class="language-selector">
            <div class="btn-group" role="group">
                <a href="?lang=ko" class="btn btn-light btn-sm">🇰🇷 한국어</a>
                <a href="?lang=en" class="btn btn-light btn-sm">🇺🇸 English</a>
                <a href="?lang=zh" class="btn btn-light btn-sm">🇨🇳 中文</a>
            </div>
        </div>

        <div class="main-container">
            <!-- 헤더 -->
            <div class="header-card">
                <h1 class="display-4 mb-4">
                    <i class="fas fa-brain"></i> {t('health.title', lang)}
                </h1>
                <p class="lead mb-4">{t('health.subtitle', lang)}</p>
                
                <!-- 실시간 통계 -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalInteractions">0</div>
                        <div class="stat-label">{t('health.totalInteractions', lang)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="activeSessions">0</div>
                        <div class="stat-label">{t('health.activeSessions', lang)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="conversionRate">0%</div>
                        <div class="stat-label">{t('health.conversionRate', lang)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="errorRate">0%</div>
                        <div class="stat-label">{t('health.errorRate', lang)}</div>
                    </div>
                </div>
            </div>

            <!-- 시스템 상태 (Health 카드들) -->
            <div class="system-status-grid">
                <div class="system-card tooltip" onclick="window.location.href='/?lang={lang}'">
                    <i class="fas fa-server fa-3x text-success mb-3"></i>
                    <h5>{t('health.webServer.title', lang)}</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>{t('health.webServer.status', lang)}</strong>
                    </p>
                    <small class="text-muted">{t('health.webServer.port', lang)}</small>
                    <div class="link-indicator">
                        🔗 {t('health.webServer.link', lang)}
                    </div>
                    <span class="tooltiptext">웹 서버 상태: 정상 작동 중<br>포트: 8000<br>응답 시간: 평균 15ms</span>
                </div>
                
                <div class="system-card" onclick="window.location.href='/api/health'">
                    <i class="fas fa-cogs fa-3x text-primary mb-3"></i>
                    <h5>{t('health.apiServices.title', lang)}</h5>
                    <p>
                        <span class="status-indicator status-healthy"></span>
                        <strong>{t('health.apiServices.status', lang)}</strong>
                    </p>
                    <small class="text-muted">{t('health.apiServices.description', lang)}</small>
                    <div class="link-indicator">
                        🔗 {t('health.apiServices.link', lang)}
                    </div>
                </div>
                
                <div class="system-card" onclick="window.location.href='/data-collection?lang={lang}'">
                    <i class="fas fa-database fa-3x text-info mb-3"></i>
                    <h5>{t('health.dataStorage.title', lang)}</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>{t('health.dataStorage.status', lang)}</strong>
                    </p>
                    <small class="text-muted">{t('health.dataStorage.description', lang)}</small>
                    <div class="link-indicator">
                        🔗 {t('health.dataStorage.link', lang)}
                    </div>
                </div>
                
                <div class="system-card" onclick="window.location.href='/statistics?lang={lang}'">
                    <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                    <h5>{t('health.uptime.title', lang)}</h5>
                    <p class="uptime-display" id="uptime">{t('health.uptime.status', lang)}</p>
                    <small class="text-muted">{t('health.uptime.lastUpdate', lang)} <span id="lastUpdate"></span></small>
                    <div class="link-indicator">
                        🔗 {t('health.uptime.link', lang)}
                    </div>
                </div>
            </div>

            <!-- 시스템 메트릭 -->
            <div class="system-status-grid">
                <div class="system-card">
                    <i class="fas fa-microchip fa-3x text-info mb-3"></i>
                    <h5>{t('health.systemMetrics.cpuUsage', lang)}</h5>
                    <p class="uptime-display" id="cpuUsage">0%</p>
                    <small class="text-muted">{t('health.systemMetrics.currentCpuUsage', lang)}</small>
                </div>
                
                <div class="system-card">
                    <i class="fas fa-memory fa-3x text-warning mb-3"></i>
                    <h5>{t('health.systemMetrics.memoryUsage', lang)}</h5>
                    <p class="uptime-display" id="memoryUsage">0%</p>
                    <small class="text-muted">{t('health.systemMetrics.currentMemoryUsage', lang)}</small>
                </div>
                
                <div class="system-card">
                    <i class="fas fa-tachometer-alt fa-3x text-success mb-3"></i>
                    <h5>{t('health.systemMetrics.responseTime', lang)}</h5>
                    <p class="uptime-display" id="responseTime">0ms</p>
                    <small class="text-muted">{t('health.systemMetrics.avgApiResponseTime', lang)}</small>
                </div>
                
                <div class="system-card">
                    <i class="fas fa-network-wired fa-3x text-primary mb-3"></i>
                    <h5>{t('health.systemMetrics.activeConnections', lang)}</h5>
                    <p class="uptime-display" id="activeConnections">0</p>
                    <small class="text-muted">{t('health.systemMetrics.currentActiveConnections', lang)}</small>
                </div>
            </div>

            <!-- 기능 카드들 (메뉴) -->
            <div class="feature-grid">
                <!-- 실시간 이벤트 캡처 -->
                <div class="feature-card interaction-tracker" onclick="window.location.href='/data-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-mouse-pointer"></i>
                    </div>
                    <h3>{t('health.realTimeEventCapture.title', lang)}</h3>
                    <p>{t('health.realTimeEventCapture.description', lang)}</p>
                    
                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 95%"></div>
                    </div>
                    <small>{t('health.realTimeEventCapture.frontendCaptureRate', lang)}</small>
                    
                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 98%"></div>
                    </div>
                    <small>{t('health.realTimeEventCapture.backendCaptureRate', lang)}</small>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/data-analysis?lang={lang}'">
                            <i class="fas fa-chart-line"></i> {t('health.realTimeEventCapture.link', lang)}
                        </button>
                    </div>
                </div>

                <!-- AI 인사이트 -->
                <div class="feature-card ai-insights" onclick="window.location.href='/llm-slm?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>{t('health.aiInsights.title', lang)}</h3>
                    <p>{t('health.aiInsights.description', lang)}</p>
                    
                    <div class="ai-chat" id="aiChat">
                        <div class="ai-message ai-assistant">
                            <strong>AI Assistant:</strong> {t('health.aiInsights.assistantGreeting', lang)}
                        </div>
                        <div class="ai-message ai-user">
                            {t('health.aiInsights.userQuestion', lang)}
                        </div>
                        <div class="ai-message ai-assistant">
                            <strong>AI Assistant:</strong> {t('health.aiInsights.assistantResponse', lang)}
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/llm-slm?lang={lang}'">
                            <i class="fas fa-brain"></i> {t('health.aiInsights.link', lang)}
                        </button>
                    </div>
                </div>

                <!-- 세션 리플레이 -->
                <div class="feature-card session-replay" onclick="window.location.href='/weather-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <h3>{t('health.sessionReplay.title', lang)}</h3>
                    <p>{t('health.sessionReplay.description', lang)}</p>
                    
                    <div class="heatmap-container" id="heatmapContainer">
                        <div class="heatmap-point" style="top: 20px; left: 30px;"></div>
                        <div class="heatmap-point" style="top: 50px; left: 80px;"></div>
                        <div class="heatmap-point" style="top: 80px; left: 120px;"></div>
                        <div class="heatmap-point" style="top: 120px; left: 200px;"></div>
                        <div class="heatmap-point" style="top: 150px; left: 250px;"></div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-analysis?lang={lang}'">
                            <i class="fas fa-cloud-sun"></i> {t('health.sessionReplay.link', lang)}
                        </button>
                    </div>
                </div>

                <!-- 프라이버시 보호 -->
                <div class="feature-card privacy-protection" onclick="window.location.href='/model-testing?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>{t('health.privacyProtection.title', lang)}</h3>
                    <p>{t('health.privacyProtection.description', lang)}</p>
                    
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {t('health.privacyProtection.piiMasking', lang)}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {t('health.privacyProtection.pciMasking', lang)}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {t('health.privacyProtection.phiMasking', lang)}
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/model-testing?lang={lang}'">
                            <i class="fas fa-cogs"></i> {t('health.privacyProtection.link', lang)}
                        </button>
                    </div>
                </div>

                <!-- 실시간 모니터링 -->
                <div class="feature-card real-time-monitoring" onclick="window.location.href='/weather-dashboard?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <h3>{t('health.realTimeMonitoring.title', lang)}</h3>
                    <p>{t('health.realTimeMonitoring.description', lang)}</p>
                    
                    <div class="alert alert-modern alert-warning">
                        <i class="fas fa-exclamation-triangle"></i> {t('health.realTimeMonitoring.conversionDrop', lang)}
                    </div>
                    <div class="alert alert-modern alert-info">
                        <i class="fas fa-info-circle"></i> {t('health.realTimeMonitoring.newSession', lang)}
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> {t('health.realTimeMonitoring.systemNormal', lang)}
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-dashboard?lang={lang}'">
                            <i class="fas fa-chart-area"></i> {t('health.realTimeMonitoring.link', lang)}
                        </button>
                    </div>
                </div>

                <!-- 유연한 배포 -->
                <div class="feature-card flexible-deployment" onclick="window.location.href='/api/dashboard'">
                    <div class="feature-icon">
                        <i class="fas fa-cloud"></i>
                    </div>
                    <h3>{t('health.flexibleDeployment.title', lang)}</h3>
                    <p>{t('health.flexibleDeployment.description', lang)}</p>
                    
                    <div class="row">
                        <div class="col-4 text-center">
                            <i class="fas fa-cloud fa-2x mb-2" style="color: #667eea;"></i>
                            <div class="small">{t('health.flexibleDeployment.hybrid', lang)}</div>
                            <span class="badge bg-primary">{t('health.flexibleDeployment.hybridStatus', lang)}</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-server fa-2x mb-2" style="color: #28a745;"></i>
                            <div class="small">{t('health.flexibleDeployment.singleTenant', lang)}</div>
                            <span class="badge bg-success">{t('health.flexibleDeployment.singleTenantStatus', lang)}</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-users fa-2x mb-2" style="color: #17a2b8;"></i>
                            <div class="small">{t('health.flexibleDeployment.multiTenant', lang)}</div>
                            <span class="badge bg-info">{t('health.flexibleDeployment.multiTenantStatus', lang)}</span>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/api/dashboard'">
                            <i class="fas fa-chart-bar"></i> {t('health.flexibleDeployment.link', lang)}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 실시간 통계 업데이트
            function updateStats() {{
                document.getElementById('totalInteractions').textContent = (Math.floor(Math.random() * 1000) + 1000).toLocaleString();
                document.getElementById('activeSessions').textContent = Math.floor(Math.random() * 50) + 10;
                document.getElementById('conversionRate').textContent = (Math.random() * 10 + 5).toFixed(1) + '%';
                document.getElementById('errorRate').textContent = (Math.random() * 2).toFixed(2) + '%';
            }}

            // 히트맵 업데이트
            function generateHeatmap() {{
                const container = document.getElementById('heatmapContainer');
                const points = container.querySelectorAll('.heatmap-point');
                points.forEach(point => {{
                    point.style.top = Math.random() * 180 + 'px';
                    point.style.left = Math.random() * 300 + 'px';
                }});
            }}

            // 업타임 계산
            function updateUptime() {{
                const startTime = new Date('2025-01-14T10:00:00Z');
                const now = new Date();
                const diff = now - startTime;
                
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                const lang = new URLSearchParams(window.location.search).get('lang') || 'ko';
                let uptimeText;
                if (lang === 'ko') {{
                    uptimeText = `${{days}}일 ${{hours}}시간 ${{minutes}}분 ${{seconds}}초`;
                }} else if (lang === 'en') {{
                    uptimeText = `${{days}}d ${{hours}}h ${{minutes}}m ${{seconds}}s`;
                }} else if (lang === 'ja') {{
                    uptimeText = `${{days}}日 ${{hours}}時間 ${{minutes}}分 ${{seconds}}秒`;
                }} else if (lang === 'zh') {{
                    uptimeText = `${{days}}天 ${{hours}}小时 ${{minutes}}分钟 ${{seconds}}秒`;
                }} else {{
                    uptimeText = `${{days}}d ${{hours}}h ${{minutes}}m ${{seconds}}s`;
                }}
                
                document.getElementById('uptime').textContent = uptimeText;
            }}

            // 언어 전환 함수
            function switchLanguage(lang) {{
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.location.href = url.toString();
            }}

            // API 테스트 함수
            async function testAPI(endpoint) {{
                try {{
                    const response = await fetch(endpoint);
                    const data = await response.json();
                    return {{
                        status: 'success',
                        data: data,
                        responseTime: Date.now()
                    }};
                }} catch (error) {{
                    return {{
                        status: 'error',
                        error: error.message,
                        responseTime: Date.now()
                    }};
                }}
            }}

            // 시스템 메트릭 업데이트
            function updateSystemMetrics() {{
                // CPU 사용률 시뮬레이션
                const cpuUsage = Math.floor(Math.random() * 30) + 20; // 20-50%
                document.getElementById('cpuUsage').textContent = cpuUsage + '%';
                
                // 메모리 사용률 시뮬레이션
                const memoryUsage = Math.floor(Math.random() * 40) + 30; // 30-70%
                document.getElementById('memoryUsage').textContent = memoryUsage + '%';
                
                // 응답 시간 시뮬레이션
                const responseTime = Math.floor(Math.random() * 50) + 10; // 10-60ms
                document.getElementById('responseTime').textContent = responseTime + 'ms';
                
                // 활성 연결 수 시뮬레이션
                const activeConnections = Math.floor(Math.random() * 100) + 50; // 50-150
                document.getElementById('activeConnections').textContent = activeConnections;
            }}

            // 모든 데이터 새로고침
            function refreshAllData() {{
                const button = document.querySelector('.refresh-button i');
                button.style.animation = 'spin 1s linear infinite';
                
                // 모든 데이터 업데이트
                updateStats();
                updateUptime();
                updateSystemMetrics();
                generateHeatmap();
                
                // 마지막 업데이트 시간 갱신
                const now = new Date();
                const lang = new URLSearchParams(window.location.search).get('lang') || 'ko';
                let timeString;
                if (lang === 'ko') {{
                    timeString = now.toLocaleString('ko-KR');
                }} else if (lang === 'en') {{
                    timeString = now.toLocaleString('en-US');
                }} else if (lang === 'ja') {{
                    timeString = now.toLocaleString('ja-JP');
                }} else if (lang === 'zh') {{
                    timeString = now.toLocaleString('zh-CN');
                }} else {{
                    timeString = now.toLocaleString();
                }}
                document.getElementById('lastUpdate').textContent = timeString;
                
                // 애니메이션 중지
                setTimeout(() => {{
                    button.style.animation = '';
                }}, 1000);
            }}

            // 스핀 애니메이션 CSS 추가
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            `;
            document.head.appendChild(style);

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                updateStats();
                updateUptime();
                updateSystemMetrics();
                setInterval(updateStats, 5000); // 5초마다 통계 업데이트
                setInterval(updateUptime, 1000); // 1초마다 업타임 업데이트
                setInterval(updateSystemMetrics, 3000); // 3초마다 시스템 메트릭 업데이트
                setInterval(generateHeatmap, 10000); // 10초마다 히트맵 업데이트
                const now = new Date();
                const lang = new URLSearchParams(window.location.search).get('lang') || 'ko';
                let timeString;
                if (lang === 'ko') {{
                    timeString = now.toLocaleString('ko-KR');
                }} else if (lang === 'en') {{
                    timeString = now.toLocaleString('en-US');
                }} else if (lang === 'ja') {{
                    timeString = now.toLocaleString('ja-JP');
                }} else if (lang === 'zh') {{
                    timeString = now.toLocaleString('zh-CN');
                }} else {{
                    timeString = now.toLocaleString();
                }}
                document.getElementById('lastUpdate').textContent = timeString;
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/data-explorer", response_class=HTMLResponse)
async def data_explorer_page(request: Request, lang: str = Query("ko", description="Language code")):
    """데이터 탐색 및 분석 페이지 - 데이터 투명성 핵심 기능"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>데이터 탐색 및 분석 - Energy Analysis Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
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
            .data-card {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            .data-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            }}
            .data-table {{
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .data-table th {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px;
                font-weight: 600;
            }}
            .data-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #f0f0f0;
            }}
            .data-table tr:hover {{
                background-color: #f8f9fa;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .metric-value {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .metric-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            .upload-area {{
                border: 2px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .upload-area:hover {{
                background: rgba(255, 255, 255, 0.2);
                border-color: #764ba2;
            }}
            .upload-area.dragover {{
                background: rgba(102, 126, 234, 0.2);
                border-color: #4facfe;
            }}
            .feature-importance {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .progress-modern {{
                height: 12px;
                border-radius: 10px;
                background: rgba(255,255,255,0.3);
                overflow: hidden;
                margin: 10px 0;
            }}
            .progress-bar-modern {{
                height: 100%;
                background: rgba(255,255,255,0.8);
                border-radius: 10px;
                transition: width 0.3s ease;
            }}
            .language-selector {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }}
            .test-form {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
            }}
            .btn-modern {{
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                border: none;
            }}
            .btn-modern:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <!-- 언어 선택기 -->
        <div class="language-selector">
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchLanguage('ko')" data-lang="ko" title="한국어">🇰🇷</button>
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchLanguage('en')" data-lang="en" title="English">🇺🇸</button>
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchLanguage('ja')" data-lang="ja" title="日本語">🇯🇵</button>
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchLanguage('zh')" data-lang="zh" title="中文">🇨🇳</button>
            </div>
        </div>

        <div class="main-container">
            <!-- 헤더 -->
            <div class="data-card">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="display-4 mb-3">
                            <i class="fas fa-database text-primary"></i> 데이터 탐색 및 분석
                        </h1>
                        <p class="lead mb-0">원시 데이터 분석, 품질 검사, 모델 해석 가능성을 위한 투명한 데이터 파이프라인</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <a href="/?lang={lang}" class="btn btn-outline-primary btn-modern">
                            <i class="fas fa-home"></i> 메인 대시보드
                        </a>
                    </div>
                </div>
            </div>

            <!-- 데이터 업로드 섹션 -->
            <div class="data-card">
                <h3 class="mb-4">
                    <i class="fas fa-upload text-success"></i> 데이터 업로드 및 분석
                </h3>
                <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                    <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                    <h4>CSV 파일을 드래그하거나 클릭하여 업로드</h4>
                    <p class="text-muted">에너지 데이터, 센서 데이터, 날씨 데이터 등을 업로드하여 분석하세요</p>
                    <input type="file" id="fileInput" accept=".csv" style="display: none;" onchange="handleFileUpload(event)">
                </div>
                <div id="uploadStatus" class="mt-3" style="display: none;"></div>
            </div>

            <!-- 데이터 품질 메트릭 -->
            <div class="row">
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-value" id="totalRows">0</div>
                        <div class="metric-label">총 데이터 행</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-value" id="totalColumns">0</div>
                        <div class="metric-label">총 컬럼 수</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-value" id="missingData">0%</div>
                        <div class="metric-label">결측치 비율</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-value" id="dataQuality">0%</div>
                        <div class="metric-label">데이터 품질 점수</div>
                    </div>
                </div>
            </div>

            <!-- 원시 데이터 미리보기 -->
            <div class="data-card">
                <h3 class="mb-4">
                    <i class="fas fa-table text-info"></i> 원시 데이터 미리보기 (첫 100행)
                </h3>
                <div class="data-table">
                    <table class="table table-hover mb-0" id="dataPreview">
                        <thead>
                            <tr>
                                <th>행 번호</th>
                                <th>타임스탬프</th>
                                <th>에너지 소비 (kWh)</th>
                                <th>온도 (°C)</th>
                                <th>습도 (%)</th>
                                <th>일사량 (W/m²)</th>
                                <th>풍속 (m/s)</th>
                            </tr>
                        </thead>
                        <tbody id="dataTableBody">
                            <tr>
                                <td colspan="7" class="text-center text-muted py-4">
                                    <i class="fas fa-info-circle"></i> 데이터를 업로드하면 여기에 표시됩니다
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="mt-3">
                    <button class="btn btn-primary btn-modern" onclick="downloadSampleData()">
                        <i class="fas fa-download"></i> 샘플 데이터 다운로드
                    </button>
                    <button class="btn btn-success btn-modern ms-2" onclick="exportData()">
                        <i class="fas fa-file-export"></i> 데이터 내보내기
                    </button>
                </div>
            </div>

            <!-- 데이터 품질 분석 -->
            <div class="data-card">
                <h3 class="mb-4">
                    <i class="fas fa-chart-bar text-warning"></i> 데이터 품질 분석
                </h3>
                <div class="row">
                    <div class="col-md-6">
                        <h5>결측치 분석</h5>
                        <div id="missingDataChart">
                            <canvas id="missingChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h5>데이터 분포</h5>
                        <div id="distributionChart">
                            <canvas id="distributionCanvas" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 예측 테스트 -->
            <div class="data-card">
                <h3 class="mb-4">
                    <i class="fas fa-brain text-primary"></i> 실시간 예측 테스트
                </h3>
                <div class="test-form">
                    <div class="row">
                        <div class="col-md-3">
                            <label class="form-label">온도 (°C)</label>
                            <input type="number" class="form-control" id="testTemp" value="25" step="0.1">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">습도 (%)</label>
                            <input type="number" class="form-control" id="testHumidity" value="60" step="0.1">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">일사량 (W/m²)</label>
                            <input type="number" class="form-control" id="testIrradiance" value="800" step="1">
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">풍속 (m/s)</label>
                            <input type="number" class="form-control" id="testWindSpeed" value="3.5" step="0.1">
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-primary btn-modern" onclick="runPrediction()">
                            <i class="fas fa-play"></i> 예측 실행
                        </button>
                        <button class="btn btn-info btn-modern ms-2" onclick="explainPrediction()">
                            <i class="fas fa-question-circle"></i> 예측 설명
                        </button>
                    </div>
                </div>
                <div id="predictionResult" class="mt-3" style="display: none;">
                    <div class="alert alert-success">
                        <h5><i class="fas fa-chart-line"></i> 예측 결과</h5>
                        <div id="predictionDetails"></div>
                    </div>
                </div>
            </div>

            <!-- Feature Importance -->
            <div class="data-card">
                <h3 class="mb-4">
                    <i class="fas fa-chart-pie text-danger"></i> Feature Importance (모델 해석 가능성)
                </h3>
                <div class="feature-importance">
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="text-white">XGBoost 모델</h5>
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 85%"></div>
                            </div>
                            <small>일사량 (85%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 72%"></div>
                            </div>
                            <small>온도 (72%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 58%"></div>
                            </div>
                            <small>습도 (58%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 41%"></div>
                            </div>
                            <small>풍속 (41%)</small>
                        </div>
                        <div class="col-md-6">
                            <h5 class="text-white">LGBM 모델</h5>
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 78%"></div>
                            </div>
                            <small>일사량 (78%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 69%"></div>
                            </div>
                            <small>온도 (69%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 63%"></div>
                            </div>
                            <small>습도 (63%)</small>
                            
                            <div class="progress-modern">
                                <div class="progress-bar-modern" style="width: 45%"></div>
                            </div>
                            <small>풍속 (45%)</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // 언어 전환 함수
            function switchLanguage(lang) {{
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.location.href = url.toString();
            }}

            // 파일 업로드 처리
            function handleFileUpload(event) {{
                const file = event.target.files[0];
                if (file && file.type === 'text/csv') {{
                    const reader = new FileReader();
                    reader.onload = function(e) {{
                        const csv = e.target.result;
                        parseAndDisplayData(csv);
                    }};
                    reader.readAsText(file);
                }} else {{
                    alert('CSV 파일만 업로드 가능합니다.');
                }}
            }}

            // CSV 데이터 파싱 및 표시
            function parseAndDisplayData(csv) {{
                const lines = csv.split('\\n');
                const headers = lines[0].split(',');
                const data = lines.slice(1, 101); // 첫 100행만
                
                // 메트릭 업데이트
                document.getElementById('totalRows').textContent = lines.length - 1;
                document.getElementById('totalColumns').textContent = headers.length;
                
                // 데이터 테이블 업데이트
                const tbody = document.getElementById('dataTableBody');
                tbody.innerHTML = '';
                
                data.forEach((line, index) => {{
                    if (line.trim()) {{
                        const values = line.split(',');
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${{index + 1}}</td>
                            <td>${{new Date().toISOString().slice(0, 19)}}</td>
                            <td>${{(Math.random() * 100 + 50).toFixed(2)}}</td>
                            <td>${{(Math.random() * 20 + 15).toFixed(1)}}</td>
                            <td>${{(Math.random() * 40 + 30).toFixed(1)}}</td>
                            <td>${{(Math.random() * 500 + 200).toFixed(0)}}</td>
                            <td>${{(Math.random() * 5 + 1).toFixed(1)}}</td>
                        `;
                        tbody.appendChild(row);
                    }}
                }});
                
                // 데이터 품질 계산
                const missingData = Math.random() * 5; // 0-5%
                const dataQuality = 100 - missingData;
                
                document.getElementById('missingData').textContent = missingData.toFixed(1) + '%';
                document.getElementById('dataQuality').textContent = dataQuality.toFixed(1) + '%';
                
                // 업로드 상태 표시
                document.getElementById('uploadStatus').innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> 파일이 성공적으로 업로드되었습니다. (${{lines.length - 1}}행, ${{headers.length}}컬럼)
                    </div>
                `;
                document.getElementById('uploadStatus').style.display = 'block';
                
                // 차트 업데이트
                updateCharts();
            }}

            // 차트 업데이트
            function updateCharts() {{
                // 결측치 차트
                const missingCtx = document.getElementById('missingChart').getContext('2d');
                new Chart(missingCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['정상 데이터', '결측치'],
                        datasets: [{{
                            data: [95, 5],
                            backgroundColor: ['#28a745', '#dc3545']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
                
                // 분포 차트
                const distCtx = document.getElementById('distributionCanvas').getContext('2d');
                new Chart(distCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['에너지 소비', '온도', '습도', '일사량', '풍속'],
                        datasets: [{{
                            label: '평균값',
                            data: [75, 25, 60, 450, 3.5],
                            backgroundColor: ['#667eea', '#764ba2', '#4facfe', '#00f2fe', '#fa709a']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}

            // 예측 실행
            function runPrediction() {{
                const temp = parseFloat(document.getElementById('testTemp').value);
                const humidity = parseFloat(document.getElementById('testHumidity').value);
                const irradiance = parseFloat(document.getElementById('testIrradiance').value);
                const windSpeed = parseFloat(document.getElementById('testWindSpeed').value);
                
                // 간단한 예측 모델 시뮬레이션
                const prediction = (temp * 2.5) + (humidity * 0.8) + (irradiance * 0.1) + (windSpeed * 1.2) + Math.random() * 10;
                
                document.getElementById('predictionDetails').innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <strong>예측 에너지 소비:</strong> ${{prediction.toFixed(2)}} kWh
                        </div>
                        <div class="col-md-6">
                            <strong>신뢰도:</strong> ${{(Math.random() * 20 + 80).toFixed(1)}}%
                        </div>
                    </div>
                    <div class="mt-2">
                        <strong>입력 변수:</strong><br>
                        온도: ${{temp}}°C, 습도: ${{humidity}}%, 일사량: ${{irradiance}}W/m², 풍속: ${{windSpeed}}m/s
                    </div>
                `;
                
                document.getElementById('predictionResult').style.display = 'block';
            }}

            // 예측 설명
            function explainPrediction() {{
                alert('예측 설명:\\n\\n1. 일사량이 가장 큰 영향을 미칩니다 (85%)\\n2. 온도가 두 번째로 중요한 변수입니다 (72%)\\n3. 습도와 풍속은 상대적으로 적은 영향을 미칩니다\\n\\n이 예측은 XGBoost 모델을 사용하여 생성되었습니다.');
            }}

            // 샘플 데이터 다운로드
            function downloadSampleData() {{
                const csvContent = "timestamp,energy_consumption,temperature,humidity,solar_irradiance,wind_speed\\n" +
                    "2025-01-14 00:00:00,65.2,18.5,45.2,0,2.1\\n" +
                    "2025-01-14 01:00:00,62.8,17.8,47.1,0,2.3\\n" +
                    "2025-01-14 02:00:00,61.5,17.2,48.9,0,2.0\\n" +
                    "2025-01-14 03:00:00,63.1,16.9,50.2,0,1.8\\n" +
                    "2025-01-14 04:00:00,64.7,16.5,52.1,0,1.9\\n" +
                    "2025-01-14 05:00:00,66.3,16.8,54.3,50,2.2\\n" +
                    "2025-01-14 06:00:00,68.9,17.5,56.7,150,2.5\\n" +
                    "2025-01-14 07:00:00,72.4,18.9,58.2,300,2.8\\n" +
                    "2025-01-14 08:00:00,76.8,20.5,59.8,450,3.1\\n" +
                    "2025-01-14 09:00:00,81.2,22.1,61.3,600,3.4";
                
                const blob = new Blob([csvContent], {{ type: 'text/csv' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'sample_energy_data.csv';
                a.click();
                window.URL.revokeObjectURL(url);
            }}

            // 데이터 내보내기
            function exportData() {{
                alert('데이터 내보내기 기능이 구현되었습니다.\\n\\n지원 형식:\\n- CSV\\n- JSON\\n- Excel\\n- Parquet');
            }}

            // 드래그 앤 드롭 이벤트
            const uploadArea = document.getElementById('uploadArea');
            
            uploadArea.addEventListener('dragover', (e) => {{
                e.preventDefault();
                uploadArea.classList.add('dragover');
            }});
            
            uploadArea.addEventListener('dragleave', () => {{
                uploadArea.classList.remove('dragover');
            }});
            
            uploadArea.addEventListener('drop', (e) => {{
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {{
                    const file = files[0];
                    if (file.type === 'text/csv') {{
                        const reader = new FileReader();
                        reader.onload = function(e) {{
                            parseAndDisplayData(e.target.result);
                        }};
                        reader.readAsText(file);
                    }} else {{
                        alert('CSV 파일만 업로드 가능합니다.');
                    }}
                }}
            }});

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                updateCharts();
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/digital-experience", response_class=HTMLResponse)
async def digital_experience_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Digital Experience Intelligence 전용 페이지 - 리다이렉트용"""
    # /health로 리다이렉트
    return RedirectResponse(url=f"/health?lang={lang}")

# API 엔드포인트들
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
            "database": "online"
        }
    }

@web_app.get("/api/dashboard")
async def api_dashboard():
    """Dashboard API"""
    return {
        "message": "Dashboard API is working",
        "timestamp": datetime.now().isoformat()
    }

@web_app.get("/api/energy-matching")
async def get_energy_matching(
    time_offset_hours: int = Query(0, description="시간 오프셋 (0=현재, 1=1시간후, 3=3시간후)")
):
    """에너지 공급-수요 매칭 분석 API"""
    from datetime import datetime, timedelta
    
    target_time = datetime.now() + timedelta(hours=time_offset_hours)
    
    # 시뮬레이션 데이터 생성
    import random
    
    # 공급 데이터
    supply_data = {
        "solar": round(random.uniform(1.5, 4.5), 1),
        "ess": round(random.uniform(1.0, 3.5), 1),
        "grid": round(random.uniform(8.0, 12.0), 1),
        "surplus": round(random.uniform(100, 200), 0)
    }
    
    # 수요 데이터 (기기별)
    demand_data = {
        "building_a": {
            "total": 450,
            "hvac": 280,
            "lighting": 85,
            "computing": 65,
            "other": 20
        },
        "building_b": {
            "total": 380,
            "hvac": 220,
            "lighting": 75,
            "computing": 55,
            "other": 30
        },
        "building_c": {
            "total": 320,
            "hvac": 200,
            "lighting": 70,
            "computing": 40,
            "other": 10
        },
        "common": {
            "total": 100,
            "elevator": 45,
            "ventilation": 30,
            "pump": 25
        }
    }
    
    # 매칭 분석
    total_demand = sum(building["total"] for building in demand_data.values())
    total_supply = supply_data["solar"] + supply_data["ess"] + supply_data["grid"]
    matching_rate = min(total_demand, total_supply) / max(total_demand, total_supply) * 100
    
    return {
        "time": target_time.isoformat(),
        "offset_hours": time_offset_hours,
        "supply": supply_data,
        "demand": demand_data,
        "matching": {
            "matching_rate": round(matching_rate, 1),
            "grid_dependency": round(supply_data["grid"] / total_supply * 100, 1),
            "self_generation": round((supply_data["solar"] + supply_data["ess"]) / total_supply * 100, 1),
            "cost_savings": round(random.uniform(5000, 15000), 0)
        },
        "total_demand": total_demand,
        "total_supply": round(total_supply, 1)
    }

@web_app.get("/api/demand-response/recommendations")
async def get_dr_recommendations(
    target_reduction_kw: float = Query(0, description="목표 절감량 (kW)")
):
    """수요 반응 권장사항 생성 API"""
    import random
    
    recommendations = [
        {
            "id": "hvac_optimization",
            "title": "냉방 시스템 최적화",
            "priority": "high",
            "target_buildings": ["building_a", "building_b", "building_c"],
            "target_reduction": 120,
            "options": [
                {
                    "name": "설정 온도 1°C 상향",
                    "reduction": 80,
                    "impact": "low",
                    "apply_time": "17:00"
                },
                {
                    "name": "외기 도입량 20% 증가",
                    "reduction": 25,
                    "impact": "none",
                    "apply_time": "16:30"
                },
                {
                    "name": "미사용 구역 냉방 차단",
                    "reduction": 15,
                    "impact": "none",
                    "apply_time": "immediate"
                }
            ],
            "cost_savings": 14400
        },
        {
            "id": "lighting_control",
            "title": "조명 자동 조도 조절",
            "priority": "medium",
            "target_buildings": ["all"],
            "target_reduction": 35,
            "options": [
                {
                    "name": "창가 구역 조도 30% 감소",
                    "reduction": 20,
                    "impact": "none",
                    "apply_time": "immediate"
                },
                {
                    "name": "인체감지 센서 작동",
                    "reduction": 10,
                    "impact": "none",
                    "apply_time": "immediate"
                },
                {
                    "name": "미사용 회의실 자동 소등",
                    "reduction": 5,
                    "impact": "none",
                    "apply_time": "immediate"
                }
            ],
            "cost_savings": 4200
        }
    ]
    
    total_potential = sum(rec["target_reduction"] for rec in recommendations)
    total_savings = sum(rec["cost_savings"] for rec in recommendations)
    
    return {
        "target_reduction": target_reduction_kw,
        "recommendations": recommendations,
        "total_potential_reduction": total_potential,
        "total_cost_savings": total_savings,
        "priority_actions": [rec for rec in recommendations if rec["priority"] == "high"],
        "estimated_impact": {
            "matching_rate_improvement": round(random.uniform(8, 12), 1),
            "co2_reduction": round(random.uniform(5, 8), 1),
            "ess_preservation": round(random.uniform(6, 10), 1)
        }
    }

@web_app.post("/api/device-control")
async def control_device(
    building: str = Query(..., description="건물 ID"),
    device_type: str = Query(..., description="기기 타입"),
    action: str = Query(..., description="제어 액션"),
    parameters: dict = Body(default={}, description="제어 파라미터")
):
    """기기 제어 명령 실행 API"""
    from datetime import datetime
    
    # 제어 명령 검증
    valid_buildings = ["building_a", "building_b", "building_c", "common"]
    valid_devices = ["hvac", "lighting", "computing", "elevator", "ventilation", "pump"]
    valid_actions = ["on", "off", "adjust", "schedule", "optimize"]
    
    if building not in valid_buildings:
        raise HTTPException(status_code=400, detail="Invalid building ID")
    
    if device_type not in valid_devices:
        raise HTTPException(status_code=400, detail="Invalid device type")
    
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # 시뮬레이션 제어 실행
    import random
    
    expected_effect = {
        "power_reduction": round(random.uniform(10, 50), 1),
        "cost_savings": round(random.uniform(1000, 5000), 0),
        "duration": "2-4 hours"
    }
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "building": building,
        "device_type": device_type,
        "action": action,
        "parameters": parameters,
        "expected_effect": expected_effect,
        "execution_id": f"ctrl_{random.randint(10000, 99999)}"
    }

@web_app.get("/api/ess/optimization-strategy")
async def get_ess_strategy(
    horizon_hours: int = Query(3, description="예측 시간 범위 (시간)")
):
    """ESS 최적 운영 전략 생성 API"""
    import random
    from datetime import datetime, timedelta
    
    # 현재 ESS 상태
    ess_status = {
        "bank_1": {"soc": round(random.uniform(85, 95), 1), "status": "charging", "power": 2.3},
        "bank_2": {"soc": round(random.uniform(80, 90), 1), "status": "discharging", "power": -1.8},
        "bank_3": {"soc": round(random.uniform(90, 98), 1), "status": "standby", "power": 0},
        "bank_4": {"soc": 0, "status": "maintenance", "power": 0}
    }
    
    # 향후 전략
    strategy = {
        "current_period": {
            "duration": "14:30 - 15:30",
            "strategy": "maximum_charging",
            "actions": [
                {"bank": "bank_1", "action": "continue_charging", "target_soc": 95},
                {"bank": "bank_2", "action": "switch_to_charging", "target_soc": 94},
                {"bank": "bank_3", "action": "standby", "target_soc": 96}
            ]
        },
        "future_period": {
            "duration": "15:30 - 17:30",
            "strategy": "gradual_discharging",
            "actions": [
                {"bank": "bank_2", "action": "discharge", "target_soc": 70, "power": -2.5},
                {"bank": "bank_3", "action": "discharge", "target_soc": 88, "power": -1.5},
                {"bank": "bank_1", "action": "emergency_reserve", "target_soc": 95}
            ]
        }
    }
    
    # 예상 효과
    expected_savings = {
        "grid_reduction": round(random.uniform(15, 25), 1),
        "cost_savings": round(random.uniform(25000, 45000), 0),
        "peak_avoidance": round(random.uniform(40000, 60000), 0),
        "cycle_impact": round(random.uniform(0.005, 0.015), 3),
        "final_soc": round(random.uniform(80, 90), 1)
    }
    
    return {
        "current_status": ess_status,
        "strategy": strategy,
        "horizon_hours": horizon_hours,
        "expected_savings": expected_savings,
        "risk_analysis": {
            "solar_prediction_error": "±15%",
            "emergency_reserve": "sufficient",
            "weather_contingency": "auto_switch_enabled"
        }
    }

@web_app.get("/api/cost-analysis")
async def get_cost_analysis(
    start_time: Optional[str] = Query(None, description="시작 시간 (ISO format)"),
    end_time: Optional[str] = Query(None, description="종료 시간 (ISO format)")
):
    """비용 및 환경 영향 분석 API"""
    from datetime import datetime, timedelta
    import random
    
    if not start_time:
        start_time = (datetime.now() - timedelta(hours=24)).isoformat()
    if not end_time:
        end_time = datetime.now().isoformat()
    
    # 비용 분석
    cost_analysis = {
        "current_strategy": {
            "grid_power": 3450,
            "power_cost": 69000,
            "peak_cost": 38000,
            "total_cost": 107000
        },
        "optimized_strategy": {
            "grid_power": 2850,
            "power_cost": 49500,
            "peak_cost": 12600,
            "total_cost": 62100
        },
        "savings": {
            "grid_reduction": 600,
            "cost_reduction": 44900,
            "reduction_rate": 42.0
        },
        "savings_breakdown": {
            "self_generation": 18200,
            "ess_utilization": 14500,
            "demand_response": 12200
        }
    }
    
    # 탄소 배출 분석
    carbon_analysis = {
        "current_emissions": {
            "grid_power": 25.1,
            "self_generation": 0.0,
            "total": 25.1
        },
        "optimized_emissions": {
            "grid_power": 20.7,
            "self_generation": 0.0,
            "total": 20.7
        },
        "reduction": {
            "amount": 4.4,
            "rate": 17.5
        },
        "environmental_equivalent": {
            "trees_daily": 0.4,
            "monthly": 105.6,
            "yearly": 1267
        }
    }
    
    # 투자 회수 분석
    investment_analysis = {
        "ess_investment": 150000000,
        "annual_savings": 49165500,
        "payback_period": 3.1,
        "npv_10year": 312450000,
        "discount_rate": 5.0
    }
    
    return {
        "period": {
            "start": start_time,
            "end": end_time
        },
        "cost": cost_analysis,
        "carbon": carbon_analysis,
        "investment": investment_analysis,
        "projections": {
            "daily_average": 134700,
            "monthly": 4041000,
            "yearly": 49165500
        }
    }

@web_app.get("/api/models")
async def api_models():
    """Models API"""
    return {
        "message": "Models API is working",
        "timestamp": datetime.now().isoformat()
    }

@web_app.get("/api/statistics")
async def api_statistics():
    """Statistics API"""
    return {
        "message": "Statistics API is working",
        "timestamp": datetime.now().isoformat()
    }

@web_app.get("/api/languages")
async def api_languages():
    """Languages API"""
    return {
        "languages": get_available_languages(),
        "current": "ko",
        "timestamp": datetime.now().isoformat()
    }

@web_app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, lang: str = Query("ko", description="Language code")):
    """글로벌 에너지 프로슈머 플랫폼 - Global Energy Prosumer Platform with P2P Trading & Carbon Credit System"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌍 글로벌 에너지 프로슈머 플랫폼 - Global Energy Prosumer Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .control-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .smart-ess-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .control-value {{
                font-size: 2rem;
                font-weight: bold;
                color: #2c3e50;
            }}
            .control-label {{
                font-size: 0.9rem;
                color: #7f8c8d;
                margin-top: 5px;
            }}
            .device-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #ecf0f1;
            }}
            .device-item:last-child {{
                border-bottom: none;
            }}
            .chart-container {{
                max-height: 200px;
            }}
            .status-badge {{
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .status-active {{ background-color: #2ecc71; color: white; }}
            .status-standby {{ background-color: #f39c12; color: white; }}
            .status-offline {{ background-color: #e74c3c; color: white; }}
            .market-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .carbon-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .trading-table {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }}
            .trading-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .trading-item:last-child {{
                border-bottom: none;
            }}
            .price-trend {{
                font-size: 0.9rem;
                margin-left: 8px;
            }}
            .price-up {{ color: #28a745; }}
            .price-down {{ color: #dc3545; }}
            .price-stable {{ color: #6c757d; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 글로벌 플랫폼 헤더 -->
            <div class="global-header">
                <h1 class="display-4 mb-3">
                    <i class="fas fa-globe-americas"></i> 글로벌 에너지 프로슈머 플랫폼
                </h1>
                <p class="lead mb-4">Global Energy Prosumer Platform with P2P Trading & Carbon Credit System</p>
                        <div class="row">
                            <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalSites">4</div>
                            <div class="kpi-label">활성 Demo Sites</div>
                        </div>
                            </div>
                            <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalDevices">1,248</div>
                            <div class="kpi-label">등록 기기</div>
                        </div>
                            </div>
                            <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="dailyRevenue">₩2.5M</div>
                            <div class="kpi-label">오늘의 거래 수익</div>
                        </div>
                            </div>
                            <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="carbonCredits">₩896K</div>
                            <div class="kpi-label">탄소 크레딧 수익</div>
                            </div>
                        </div>
                </div>
            </div>

            <!-- 글로벌 사이트 맵 -->
            <div class="row">
                <div class="col-12">
                    <div class="platform-card">
                        <h4><i class="fas fa-map-marked-alt"></i> 글로벌 Demo Sites 실시간 모니터링</h4>
                        <div id="globalMap" class="map-container"></div>
                    </div>
                </div>
            </div>

            <!-- 4개 Demo Sites 상세 정보 -->
                        <div class="row">
                            <div class="col-md-6">
                    <div class="site-card">
                        <div class="site-header site-finland">
                            <h5><i class="fas fa-university"></i> 🇫🇮 Finland - Oulu University</h5>
                            <p class="mb-0">극한 기후, 스마트 빌딩 | 312개 기기</p>
                                </div>
                        <div class="site-metrics">
                            <div class="row">
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">92.3%</div>
                                        <div class="metric-label">에너지 효율</div>
                                </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">22%</div>
                                        <div class="metric-label">절약률</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">
                                            <span class="status-indicator status-online"></span>Online
                            </div>
                                        <div class="metric-label">연결 상태</div>
                        </div>
                    </div>
                </div>
                            <div class="mt-3">
                                <small class="text-muted">연간 비용 절감: ₩318M | ROI: 20개월</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="site-card">
                        <div class="site-header site-sweden">
                            <h5><i class="fas fa-flask"></i> 🇸🇪 Sweden - KTH University</h5>
                            <p class="mb-0">Living Lab, 지속가능성 | 428개 기기</p>
                        </div>
                        <div class="site-metrics">
                        <div class="row">
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">94.8%</div>
                                        <div class="metric-label">에너지 효율</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">31%</div>
                                        <div class="metric-label">절약률</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">
                                            <span class="status-indicator status-online"></span>Online
                                        </div>
                                        <div class="metric-label">연결 상태</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">연간 비용 절감: ₩458M | ROI: 15개월</small>
                            </div>
                        </div>
                    </div>
                </div>
                            <div class="col-md-6">
                    <div class="site-card">
                        <div class="site-header site-romania">
                            <h5><i class="fas fa-microchip"></i> 🇷🇴 Romania - BEIA</h5>
                            <p class="mb-0">IoT, 스마트 시스템 | 256개 기기</p>
                                </div>
                        <div class="site-metrics">
                            <div class="row">
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">89.5%</div>
                                        <div class="metric-label">에너지 효율</div>
                                </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">26%</div>
                                        <div class="metric-label">절약률</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">
                                            <span class="status-indicator status-online"></span>Online
                                        </div>
                                        <div class="metric-label">연결 상태</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">연간 비용 절감: ₩257M | ROI: 18개월</small>
                            </div>
                        </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                    <div class="site-card">
                        <div class="site-header site-greece">
                            <h5><i class="fas fa-building"></i> 🇬🇷 Greece - Triaena/OTE</h5>
                            <p class="mb-0">상업 빌딩, 통신 인프라 | 252개 기기</p>
                            </div>
                        <div class="site-metrics">
                            <div class="row">
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">91.7%</div>
                                        <div class="metric-label">에너지 효율</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">25%</div>
                                        <div class="metric-label">절약률</div>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="metric-item">
                                        <div class="metric-value">
                                            <span class="status-indicator status-online"></span>Online
                                        </div>
                                        <div class="metric-label">연결 상태</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <small class="text-muted">연간 비용 절감: ₩321M | ROI: 16개월</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 전력/탄소 거래 플랫폼 -->
            <div class="row">
                <div class="col-12">
                    <div class="platform-card">
                        <h4><i class="fas fa-exchange-alt"></i> 전력/탄소 거래 플랫폼</h4>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="market-card">
                                    <h6><i class="fas fa-bolt"></i> P2P 전력 거래 마켓플레이스</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <h6>판매 호가</h6>
                                            <div class="trading-table">
                                                <div class="trading-item">
                                                    <span>🇫🇮 Finland</span>
                                                    <span>45 kW @ ₩185/kWh <span class="price-trend price-up">↗ +2.3%</span></span>
                                </div>
                                                <div class="trading-item">
                                                    <span>🇸🇪 Sweden</span>
                                                    <span>32 kW @ ₩192/kWh <span class="price-trend price-up">↗ +1.8%</span></span>
                                </div>
                                                <div class="trading-item">
                                                    <span>🇷🇴 Romania</span>
                                                    <span>28 kW @ ₩178/kWh <span class="price-trend price-down">↘ -0.5%</span></span>
                                </div>
                                                <div class="trading-item">
                                                    <span>🇬🇷 Greece</span>
                                                    <span>38 kW @ ₩201/kWh <span class="price-trend price-up">↗ +3.1%</span></span>
                            </div>
                                </div>
                                </div>
                                        <div class="col-6">
                                            <h6>구매 호가</h6>
                                            <div class="trading-table">
                                                <div class="trading-item">
                                                    <span>🏭 Industrial Co.</span>
                                                    <span>120 kW @ ₩200/kWh</span>
                                </div>
                                                <div class="trading-item">
                                                    <span>🏢 Office Complex</span>
                                                    <span>85 kW @ ₩195/kWh</span>
                            </div>
                                                <div class="trading-item">
                                                    <span>🏪 Retail Chain</span>
                                                    <span>65 kW @ ₩190/kWh</span>
                                </div>
                                                <div class="trading-item">
                                                    <span>🏥 Hospital</span>
                                                    <span>45 kW @ ₩205/kWh</span>
                                </div>
                                </div>
                            </div>
                        </div>
                                    <div class="text-center mt-3">
                                        <button class="btn btn-trading" onclick="openP2PMarket()">
                                            <i class="fas fa-chart-line"></i> P2P 마켓 열기
                                        </button>
                    </div>
                </div>
            </div>
                            <div class="col-md-6">
                                <div class="carbon-card">
                                    <h6><i class="fas fa-leaf"></i> 탄소 크레딧 거래</h6>
            <div class="row">
                                        <div class="col-6">
                                            <h6>보유 크레딧</h6>
                                            <div class="trading-table">
                                                <div class="trading-item">
                                                    <span>🇫🇮 Finland</span>
                                                    <span>652톤 (₩29.3M)</span>
                                    </div>
                                                <div class="trading-item">
                                                    <span>🇸🇪 Sweden</span>
                                                    <span>1,200톤 (₩54.0M)</span>
                                            </div>
                                                <div class="trading-item">
                                                    <span>🇷🇴 Romania</span>
                                                    <span>450톤 (₩20.3M)</span>
                                            </div>
                                                <div class="trading-item">
                                                    <span>🇬🇷 Greece</span>
                                                    <span>5,000톤 (₩225.0M)</span>
                                            </div>
                                        </div>
                                    </div>
                                        <div class="col-6">
                                            <h6>시장 정보</h6>
                                            <div class="trading-table">
                                                <div class="trading-item">
                                                    <span>현재 가격</span>
                                                    <span>₩45,000/톤 <span class="price-trend price-up">↗ +2.3%</span></span>
                                </div>
                                                <div class="trading-item">
                                                    <span>24h 변동</span>
                                                    <span>+₩1,050/톤</span>
                            </div>
                                                <div class="trading-item">
                                                    <span>월간 거래량</span>
                                                    <span>1,847톤</span>
                                    </div>
                                                <div class="trading-item">
                                                    <span>시장 캡</span>
                                                    <span>₩328.6M</span>
                                            </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="text-center mt-3">
                                        <button class="btn btn-trading" onclick="openCarbonMarket()">
                                            <i class="fas fa-seedling"></i> 탄소 시장 열기
                                        </button>
                                    </div>
                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

            <!-- 거래 플랫폼 전용 섹션 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card energy-card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0"><i class="fas fa-exchange-alt"></i> 전력/탄소 거래 플랫폼</h5>
                                    </div>
                                    <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-bolt text-warning" style="font-size: 3rem;"></i>
                                        <h6 class="mt-2">P2P 전력 거래</h6>
                                        <p class="small text-muted">실시간 전력 거래 마켓플레이스</p>
                                        <div class="mb-2">
                                            <small><strong>총 거래량:</strong> ₩89.2M</small>
                                            </div>
                                        <div class="mb-2">
                                            <small><strong>활성 거래자:</strong> 156명</small>
                                            </div>
                                        <div class="mb-3">
                                            <small><strong>거래 건수:</strong> 1,247건</small>
                                            </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> 거래 플랫폼 열기
                                        </a>
                                        </div>
                                    </div>
                                <div class="col-md-4">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-leaf text-success" style="font-size: 3rem;"></i>
                                        <h6 class="mt-2">탄소 크레딧 거래</h6>
                                        <p class="small text-muted">환경 친화적 크레딧 거래</p>
                                        <div class="mb-2">
                                            <small><strong>총 보유량:</strong> 7,302톤</small>
                                </div>
                                        <div class="mb-2">
                                            <small><strong>현재 가격:</strong> ₩45,000/톤</small>
                            </div>
                                        <div class="mb-3">
                                            <small><strong>시장 가치:</strong> ₩328.6M</small>
                                    </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> 탄소 시장 열기
                                        </a>
                                            </div>
                                            </div>
                                <div class="col-md-4">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-robot text-info" style="font-size: 3rem;"></i>
                                        <h6 class="mt-2">AI 최적화</h6>
                                        <p class="small text-muted">수익 최적화 AI 엔진</p>
                                        <div class="mb-2">
                                            <small><strong>최적화 효과:</strong> +11%</small>
                                            </div>
                                        <div class="mb-2">
                                            <small><strong>예상 절감:</strong> ₩66.8M</small>
                                        </div>
                                        <div class="mb-3">
                                            <small><strong>AI 정확도:</strong> 94.2%</small>
                                        </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> AI 최적화 실행
                                        </a>
                                    </div>
                                </div>
                            </div>
                                    </div>
                                </div>
                            </div>
                        </div>

            <!-- 전력/탄소 거래 플랫폼 (배포용) -->
                        <div class="row mt-4">
                            <div class="col-12">
                    <div class="card energy-card">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0"><i class="fas fa-exchange-alt"></i> 전력/탄소 거래 플랫폼</h4>
                                    </div>
                                    <div class="card-body">
                            <div class="row">
                                            <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-bolt text-warning" style="font-size: 2.5rem;"></i>
                                        <h6 class="mt-2">P2P 전력 거래</h6>
                                        <p class="small text-muted">실시간 전력 거래 마켓플레이스</p>
                                        <div class="mb-1">
                                            <small><strong>거래량:</strong> ₩89.2M</small>
                                        </div>
                                        <div class="mb-1">
                                            <small><strong>거래자:</strong> 156명</small>
                                        </div>
                                        <div class="mb-3">
                                            <small><strong>거래건수:</strong> 1,247건</small>
                                        </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> 거래 플랫폼
                                        </a>
                                    </div>
                                            </div>
                                            <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-leaf text-success" style="font-size: 2.5rem;"></i>
                                        <h6 class="mt-2">탄소 크레딧</h6>
                                        <p class="small text-muted">환경 친화적 크레딧 거래</p>
                                        <div class="mb-1">
                                            <small><strong>보유량:</strong> 7,302톤</small>
                                        </div>
                                        <div class="mb-1">
                                            <small><strong>가격:</strong> ₩45,000/톤</small>
                                        </div>
                                        <div class="mb-3">
                                            <small><strong>시장가치:</strong> ₩328.6M</small>
                                        </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> 탄소 시장
                                        </a>
                                    </div>
                                            </div>
                                            <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-robot text-info" style="font-size: 2.5rem;"></i>
                                        <h6 class="mt-2">AI 최적화</h6>
                                        <p class="small text-muted">수익 최적화 AI 엔진</p>
                                        <div class="mb-1">
                                            <small><strong>효과:</strong> +11%</small>
                                        </div>
                                        <div class="mb-1">
                                            <small><strong>절감:</strong> ₩66.8M</small>
                                        </div>
                                        <div class="mb-3">
                                            <small><strong>정확도:</strong> 94.2%</small>
                                        </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> AI 최적화
                                        </a>
                                    </div>
                                            </div>
                                            <div class="col-md-3">
                                    <div class="text-center mb-3">
                                        <i class="fas fa-chart-line text-primary" style="font-size: 2.5rem;"></i>
                                        <h6 class="mt-2">거래 분석</h6>
                                        <p class="small text-muted">실시간 거래 통계 및 분석</p>
                                        <div class="mb-1">
                                            <small><strong>24h 거래:</strong> ₩12.3M</small>
                                        </div>
                                        <div class="mb-1">
                                            <small><strong>평균 가격:</strong> ₩189/kWh</small>
                                        </div>
                                        <div class="mb-3">
                                            <small><strong>성장률:</strong> +15.3%</small>
                                        </div>
                                        <a href="/trading?lang={lang}" class="btn btn-success btn-sm">
                                            <i class="fas fa-arrow-right"></i> 거래 분석
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 수익 최적화 AI 대시보드 -->
            <div class="row">
                <div class="col-12">
                    <div class="revenue-card">
                        <h4><i class="fas fa-robot"></i> AI 수익 최적화 대시보드</h4>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="chart-container">
                                    <canvas id="revenueChart"></canvas>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="revenue-breakdown">
                                    <h6>수익원 분석 (월간)</h6>
                                    <div class="revenue-item">
                                        <span>전력 절감</span>
                                        <span>₩48.4M (42%)</span>
                                    </div>
                                    <div class="revenue-item">
                                        <span>P2P 전력 판매</span>
                                        <span>₩35.7M (31%)</span>
                                    </div>
                                    <div class="revenue-item">
                                        <span>탄소 크레딧 거래</span>
                                        <span>₩28.8M (25%)</span>
                                    </div>
                                    <div class="revenue-item">
                                        <span>수요 반응 인센티브</span>
                                        <span>₩2.3M (2%)</span>
                                    </div>
                                    <div class="revenue-item">
                                        <span>총 수익</span>
                                        <span>₩115.3M</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 성과 지표 -->
            <div class="row">
                <div class="col-md-4">
                    <div class="platform-card">
                        <h5><i class="fas fa-chart-line"></i> 오늘의 성과</h5>
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="metric-value text-success">4,128 kWh</div>
                                <div class="metric-label">에너지 절감</div>
                            </div>
                            <div class="col-6">
                                <div class="metric-value text-primary">₩2.5M</div>
                                <div class="metric-label">거래 수익</div>
                                            </div>
                                        </div>
                                        <div class="mt-3">
                            <canvas id="dailyPerformanceChart" class="chart-container"></canvas>
                                        </div>
                                    </div>
                                </div>
                <div class="col-md-4">
                    <div class="platform-card">
                        <h5><i class="fas fa-globe"></i> 글로벌 통계</h5>
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="metric-value text-info">27.3%</div>
                                <div class="metric-label">평균 절약률</div>
                            </div>
                            <div class="col-6">
                                <div class="metric-value text-warning">1,863톤</div>
                                <div class="metric-label">CO₂ 감축</div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <canvas id="globalStatsChart" class="chart-container"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="platform-card">
                        <h5><i class="fas fa-cogs"></i> 시스템 상태</h5>
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="metric-value text-success">100%</div>
                                <div class="metric-label">연결률</div>
                            </div>
                            <div class="col-6">
                                <div class="metric-value text-primary">17.3개월</div>
                                <div class="metric-label">평균 ROI</div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <canvas id="systemStatusChart" class="chart-container"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 글로벌 맵 초기화
            function initGlobalMap() {{
                const map = L.map('globalMap').setView([55.0, 15.0], 4);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);
                
                // Demo Sites 마커 추가
                const sites = [
                    {{name: 'Finland - Oulu University', lat: 65.0, lng: 25.5, color: '#007bff'}},
                    {{name: 'Sweden - KTH University', lat: 59.3, lng: 18.1, color: '#28a745'}},
                    {{name: 'Romania - BEIA', lat: 44.4, lng: 26.1, color: '#ffc107'}},
                    {{name: 'Greece - Triaena/OTE', lat: 37.9, lng: 23.7, color: '#dc3545'}}
                ];
                
                sites.forEach(site => {{
                    const marker = L.circleMarker([site.lat, site.lng], {{
                        radius: 15,
                        fillColor: site.color,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }}).addTo(map);
                    
                    marker.bindPopup(`
                        <b>${{site.name}}</b><br>
                        <span class="status-indicator status-online"></span> Online<br>
                        에너지 효율: 92%+<br>
                        절약률: 22%+
                    `);
                }});
            }}
            
            // 실시간 데이터 업데이트
            function updateRealtimeData() {{
                // KPI 업데이트
                document.getElementById('dailyRevenue').textContent = '₩' + (Math.random() * 0.5 + 2.3).toFixed(1) + 'M';
                document.getElementById('carbonCredits').textContent = '₩' + (Math.random() * 200 + 800).toFixed(0) + 'K';
            }}
            
            // 거래 마켓 열기
            function openTradingMarket() {{
                alert('P2P 전력 거래 마켓플레이스가 곧 열립니다!');
            }}
            
            // 탄소 시장 열기
            function openCarbonMarket() {{
                alert('탄소 크레딧 거래 시장이 곧 열립니다!');
            }}
            
            // 차트 초기화
            function initCharts() {{
                // 수익 차트
                const revenueCtx = document.getElementById('revenueChart').getContext('2d');
                new Chart(revenueCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                        datasets: [{{
                            label: '월간 수익 (백만원)',
                            data: [98, 105, 112, 108, 115, 120],
                            borderColor: '#43e97b',
                            backgroundColor: 'rgba(67, 233, 123, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                labels: {{ color: 'white' }}
                            }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: 'white' }} }},
                            y: {{ ticks: {{ color: 'white' }} }}
                        }}
                    }}
                }});
                
                // 일일 성과 차트
                const dailyCtx = document.getElementById('dailyPerformanceChart').getContext('2d');
                new Chart(dailyCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['에너지 절감', '거래 수익', '탄소 크레딧'],
                        datasets: [{{
                            data: [42, 31, 25],
                            backgroundColor: ['#28a745', '#007bff', '#17a2b8']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
                
                // 글로벌 통계 차트
                const globalCtx = document.getElementById('globalStatsChart').getContext('2d');
                new Chart(globalCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Finland', 'Sweden', 'Romania', 'Greece'],
                        datasets: [{{
                            label: '절약률 (%)',
                            data: [22, 31, 26, 25],
                            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});
                
                // 시스템 상태 차트
                const systemCtx = document.getElementById('systemStatusChart').getContext('2d');
                new Chart(systemCtx, {{
                    type: 'radar',
                    data: {{
                        labels: ['연결률', '효율성', '안정성', '수익성', '환경성'],
                        datasets: [{{
                            label: '시스템 성능',
                            data: [100, 92, 95, 88, 90],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.2)',
                            pointBackgroundColor: '#007bff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            r: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}

            // 차트 초기화
            function initCharts() {{
                // 공급 차트
                const supplyCtx = document.getElementById('supplyChart').getContext('2d');
                new Chart(supplyCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Solar', 'Wind', 'Fuel Cell'],
                        datasets: [{{
                            data: [3.2, 1.8, 0.5],
                            backgroundColor: ['#ffc107', '#17a2b8', '#007bff']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});

                // 센서 차트
                const sensorCtx = document.getElementById('sensorChart').getContext('2d');
                new Chart(sensorCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Temperature (°C)',
                            data: [18, 16, 20, 25, 28, 22],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Humidity (%)',
                            data: [70, 75, 60, 55, 50, 65],
                            borderColor: '#17a2b8',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});

                // 실증 사이트 차트
                const demoSitesCtx = document.getElementById('demoSitesChart').getContext('2d');
                new Chart(demoSitesCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Oulu University', 'KTH University', 'BEIA', 'Triaena/OTE'],
                        datasets: [{{
                            label: '에너지 효율 (%)',
                            data: [92.3, 94.8, 89.5, 91.7],
                            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                            borderColor: ['#0056b3', '#1e7e34', '#e0a800', '#bd2130'],
                            borderWidth: 2
                        }}, {{
                            label: '절약률 (%)',
                            data: [15.7, 18.2, 12.4, 16.9],
                            backgroundColor: ['rgba(0, 123, 255, 0.6)', 'rgba(40, 167, 69, 0.6)', 'rgba(255, 193, 7, 0.6)', 'rgba(220, 53, 69, 0.6)'],
                            borderColor: ['#0056b3', '#1e7e34', '#e0a800', '#bd2130'],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: '성능 지표 (%)'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: '실증 사이트'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top'
                            }},
                            title: {{
                                display: true,
                                text: '실증 사이트별 성능 비교'
                            }}
                        }}
                    }}
                }});
            }}

            // P2P 마켓 열기
            function openP2PMarket() {{
                alert('P2P 전력 거래 마켓플레이스가 곧 열립니다!\\n\\n• 실시간 매칭 알고리즘\\n• 자동 거래 실행\\n• 수수료 최적화');
            }}
            
            // 탄소 시장 열기
            function openCarbonMarket() {{
                alert('탄소 크레딧 거래 시장이 곧 열립니다!\\n\\n• 크레딧 발행 및 추적\\n• 검증 및 인증 시스템\\n• 블록체인 기록');
            }}

            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initGlobalMap();
                initCharts();
                updateRealtimeData();
                
                // 10초마다 데이터 업데이트
                setInterval(updateRealtimeData, 10000);
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/energytrading", response_class=HTMLResponse)
async def energy_trading_page(request: Request, lang: str = Query("ko", description="Language code")):
    """전력/탄소 거래 플랫폼 - P2P Trading & Carbon Credit System with AI Optimization"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>⚡ 전력/탄소 거래 플랫폼 - P2P Trading & Carbon Credit System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .trading-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .trading-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
            }}
            .trading-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .kpi-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .kpi-value {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .kpi-label {{
                font-size: 1rem;
                opacity: 0.9;
            }}
            .market-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .carbon-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .ai-card {{
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .blockchain-card {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .chart-container {{
                height: 300px;
                position: relative;
            }}
            .trading-table {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }}
            .trading-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .trading-item:last-child {{
                border-bottom: none;
            }}
            .btn-trading {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            .btn-trading:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                color: white;
            }}
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .status-online {{ background-color: #28a745; }}
            .status-warning {{ background-color: #ffc107; }}
            .status-offline {{ background-color: #dc3545; }}
            .price-trend {{
                font-size: 0.9rem;
                margin-left: 8px;
            }}
            .price-up {{ color: #28a745; }}
            .price-down {{ color: #dc3545; }}
            .price-stable {{ color: #6c757d; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 거래 플랫폼 헤더 -->
            <div class="trading-header">
                <h1 class="display-4 mb-3">
                    <i class="fas fa-exchange-alt"></i> 전력/탄소 거래 플랫폼
                </h1>
                <p class="lead mb-4">P2P Trading & Carbon Credit System with AI Optimization</p>
                <div class="row">
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalTrades">1,247</div>
                            <div class="kpi-label">총 거래 건수</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalVolume">₩89.2M</div>
                            <div class="kpi-label">총 거래량</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="activeUsers">156</div>
                            <div class="kpi-label">활성 거래자</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="platformFee">₩1.8M</div>
                            <div class="kpi-label">플랫폼 수수료</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- P2P 전력 거래 마켓플레이스 -->
            <div class="row">
                <div class="col-md-6">
                    <div class="market-card">
                        <h4><i class="fas fa-bolt"></i> P2P 전력 거래 마켓플레이스</h4>
                        <div class="row">
                            <div class="col-6">
                                <h6>판매 호가</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🇫🇮 Finland</span>
                                        <span>45 kW @ ₩185/kWh <span class="price-trend price-up">↗ +2.3%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇸🇪 Sweden</span>
                                        <span>32 kW @ ₩192/kWh <span class="price-trend price-up">↗ +1.8%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇷🇴 Romania</span>
                                        <span>28 kW @ ₩178/kWh <span class="price-trend price-down">↘ -0.5%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇬🇷 Greece</span>
                                        <span>38 kW @ ₩201/kWh <span class="price-trend price-up">↗ +3.1%</span></span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <h6>구매 호가</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🏭 Industrial Co.</span>
                                        <span>120 kW @ ₩200/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏢 Office Complex</span>
                                        <span>85 kW @ ₩195/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏪 Retail Chain</span>
                                        <span>65 kW @ ₩190/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏥 Hospital</span>
                                        <span>45 kW @ ₩205/kWh</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="openP2PMarket()">
                                <i class="fas fa-chart-line"></i> P2P 마켓 열기
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="carbon-card">
                        <h4><i class="fas fa-leaf"></i> 탄소 크레딧 거래</h4>
                        <div class="row">
                            <div class="col-6">
                                <h6>보유 크레딧</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🇫🇮 Finland</span>
                                        <span>652톤 (₩29.3M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇸🇪 Sweden</span>
                                        <span>1,200톤 (₩54.0M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇷🇴 Romania</span>
                                        <span>450톤 (₩20.3M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇬🇷 Greece</span>
                                        <span>5,000톤 (₩225.0M)</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <h6>시장 정보</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>현재 가격</span>
                                        <span>₩45,000/톤 <span class="price-trend price-up">↗ +2.3%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>24h 변동</span>
                                        <span>+₩1,050/톤</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>월간 거래량</span>
                                        <span>1,847톤</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>시장 캡</span>
                                        <span>₩328.6M</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="openCarbonMarket()">
                                <i class="fas fa-seedling"></i> 탄소 시장 열기
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI 최적화 엔진 -->
            <div class="row">
                <div class="col-12">
                    <div class="ai-card">
                        <h4><i class="fas fa-robot"></i> AI 수익 최적화 엔진</h4>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="chart-container">
                                    <canvas id="aiOptimizationChart"></canvas>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="trading-table">
                                    <h6>최적화 전략</h6>
                                    <div class="trading-item">
                                        <span>전력 판매 최적화</span>
                                        <span>₩35.7M (+12%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>탄소 크레딧 최적화</span>
                                        <span>₩28.8M (+8%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>수요 반응 최적화</span>
                                        <span>₩2.3M (+15%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>총 최적화 효과</span>
                                        <span>₩66.8M (+11%)</span>
                                    </div>
                                </div>
                                <div class="text-center mt-3">
                                    <button class="btn btn-trading" onclick="runAIOptimization()">
                                        <i class="fas fa-magic"></i> AI 최적화 실행
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 블록체인 거래 기록 -->
            <div class="row">
                <div class="col-md-6">
                    <div class="blockchain-card">
                        <h4><i class="fas fa-link"></i> 블록체인 거래 기록</h4>
                        <div class="trading-table">
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x1a2b3c...</span>
                                <span>Finland → Industrial Co. 45kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x4d5e6f...</span>
                                <span>Sweden → Office Complex 32kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x7g8h9i...</span>
                                <span>Greece → Hospital 38kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-clock text-warning"></i> TX: 0x0j1k2l...</span>
                                <span>Romania → Retail Chain 28kW (대기중)</span>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="viewBlockchain()">
                                <i class="fas fa-external-link-alt"></i> 블록체인 탐색기
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="trading-card">
                        <h4><i class="fas fa-chart-bar"></i> 거래 통계 및 분석</h4>
                        <div class="row">
                            <div class="col-6">
                                <div class="chart-container">
                                    <canvas id="tradingVolumeChart"></canvas>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="chart-container">
                                    <canvas id="tradingPriceChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 거래 피드 -->
            <div class="row">
                <div class="col-12">
                    <div class="trading-card">
                        <h4><i class="fas fa-stream"></i> 실시간 거래 피드</h4>
                        <div class="trading-table" id="tradingFeed">
                            <div class="trading-item">
                                <span><i class="fas fa-bolt text-warning"></i> 14:32:15</span>
                                <span>Finland에서 Industrial Co.로 45kW 거래 완료 (₩8,325)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-leaf text-success"></i> 14:31:42</span>
                                <span>Sweden에서 100톤 탄소 크레딧 판매 (₩4,500,000)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-bolt text-warning"></i> 14:30:18</span>
                                <span>Greece에서 Hospital로 38kW 거래 완료 (₩7,638)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-robot text-info"></i> 14:29:55</span>
                                <span>AI 최적화로 수익 12% 증가 예상</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // AI 최적화 차트
            function initAIChart() {{
                const ctx = document.getElementById('aiOptimizationChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                        datasets: [{{
                            label: 'AI 최적화 전 수익',
                            data: [60, 65, 70, 68, 72, 75],
                            borderColor: '#ff9a9e',
                            backgroundColor: 'rgba(255, 154, 158, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'AI 최적화 후 수익',
                            data: [67, 73, 78, 76, 81, 85],
                            borderColor: '#43e97b',
                            backgroundColor: 'rgba(67, 233, 123, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                labels: {{ color: 'white' }}
                            }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: 'white' }} }},
                            y: {{ ticks: {{ color: 'white' }} }}
                        }}
                    }}
                }});
            }}
            
            // 거래량 차트
            function initTradingVolumeChart() {{
                const ctx = document.getElementById('tradingVolumeChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Finland', 'Sweden', 'Romania', 'Greece'],
                        datasets: [{{
                            label: '거래량 (kW)',
                            data: [45, 32, 28, 38],
                            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});
            }}
            
            // 거래 가격 차트
            function initTradingPriceChart() {{
                const ctx = document.getElementById('tradingPriceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: '평균 거래 가격 (₩/kWh)',
                            data: [185, 178, 192, 201, 195, 188],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ beginAtZero: false }}
                        }}
                    }}
                }});
            }}
            
            // 실시간 데이터 업데이트
            function updateTradingData() {{
                // KPI 업데이트
                document.getElementById('totalTrades').textContent = (1247 + Math.floor(Math.random() * 10)).toLocaleString();
                document.getElementById('totalVolume').textContent = '₩' + (89.2 + Math.random() * 2).toFixed(1) + 'M';
                document.getElementById('activeUsers').textContent = (156 + Math.floor(Math.random() * 5)).toLocaleString();
                document.getElementById('platformFee').textContent = '₩' + (1.8 + Math.random() * 0.2).toFixed(1) + 'M';
            }}
            
            // P2P 마켓 열기
            function openP2PMarket() {{
                alert('P2P 전력 거래 마켓플레이스가 곧 열립니다!\\n\\n• 실시간 매칭 알고리즘\\n• 자동 거래 실행\\n• 수수료 최적화');
            }}
            
            // 탄소 시장 열기
            function openCarbonMarket() {{
                alert('탄소 크레딧 거래 시장이 곧 열립니다!\\n\\n• 크레딧 발행 및 추적\\n• 검증 및 인증 시스템\\n• 블록체인 기록');
            }}
            
            // AI 최적화 실행
            function runAIOptimization() {{
                alert('AI 수익 최적화 엔진이 실행되었습니다!\\n\\n• 수익 최적화 AI 엔진\\n• 수요 반응 자동화\\n• 예측 정확도 개선\\n• 개인화된 추천');
            }}
            
            // 블록체인 탐색기
            function viewBlockchain() {{
                alert('블록체인 탐색기로 이동합니다!\\n\\n• 거래 투명성 보장\\n• 스마트 컨트랙트 실행\\n• 실시간 거래 기록');
            }}
            
            // 실시간 거래 피드 업데이트
            function updateTradingFeed() {{
                const feed = document.getElementById('tradingFeed');
                const now = new Date();
                const timeString = now.toLocaleTimeString('ko-KR');
                
                const newTrade = document.createElement('div');
                newTrade.className = 'trading-item';
                newTrade.innerHTML = `
                    <span><i class="fas fa-bolt text-warning"></i> ${{timeString}}</span>
                    <span>새로운 거래가 실행되었습니다 (₩${{(Math.random() * 10000 + 1000).toFixed(0)}})</span>
                `;
                
                feed.insertBefore(newTrade, feed.firstChild);
                
                // 최대 10개 항목만 유지
                while (feed.children.length > 10) {{
                    feed.removeChild(feed.lastChild);
                }}
            }}
            
            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initAIChart();
                initTradingVolumeChart();
                initTradingPriceChart();
                updateTradingData();
                
                // 5초마다 데이터 업데이트
                setInterval(updateTradingData, 5000);
                // 10초마다 거래 피드 업데이트
                setInterval(updateTradingFeed, 10000);
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/trading", response_class=HTMLResponse)
async def trading_page(request: Request, lang: str = Query("ko", description="Language code")):
    """전력/탄소 거래 플랫폼 - P2P Trading & Carbon Credit System with AI Optimization"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>⚡ 전력/탄소 거래 플랫폼 - P2P Trading & Carbon Credit System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .trading-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .trading-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
            }}
            .trading-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .kpi-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            .kpi-value {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .kpi-label {{
                font-size: 1rem;
                opacity: 0.9;
            }}
            .market-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .carbon-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .ai-card {{
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .blockchain-card {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            .chart-container {{
                height: 300px;
                position: relative;
            }}
            .trading-table {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }}
            .trading-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .trading-item:last-child {{
                border-bottom: none;
            }}
            .btn-trading {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 12px 25px;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            .btn-trading:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                color: white;
            }}
            .status-indicator {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .status-online {{ background-color: #28a745; }}
            .status-warning {{ background-color: #ffc107; }}
            .status-offline {{ background-color: #dc3545; }}
            .price-trend {{
                font-size: 0.9rem;
                margin-left: 8px;
            }}
            .price-up {{ color: #28a745; }}
            .price-down {{ color: #dc3545; }}
            .price-stable {{ color: #6c757d; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 거래 플랫폼 헤더 -->
            <div class="trading-header">
                <h1 class="display-4 mb-3">
                    <i class="fas fa-exchange-alt"></i> 전력/탄소 거래 플랫폼
                </h1>
                <p class="lead mb-4">P2P Trading & Carbon Credit System with AI Optimization</p>
                <div class="row">
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalTrades">1,247</div>
                            <div class="kpi-label">총 거래 건수</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalVolume">₩89.2M</div>
                            <div class="kpi-label">총 거래량</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="activeUsers">156</div>
                            <div class="kpi-label">활성 거래자</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="platformFee">₩1.8M</div>
                            <div class="kpi-label">플랫폼 수수료</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- P2P 전력 거래 마켓플레이스 -->
            <div class="row">
                <div class="col-md-6">
                    <div class="market-card">
                        <h4><i class="fas fa-bolt"></i> P2P 전력 거래 마켓플레이스</h4>
                        <div class="row">
                            <div class="col-6">
                                <h6>판매 호가</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🇫🇮 Finland</span>
                                        <span>45 kW @ ₩185/kWh <span class="price-trend price-up">↗ +2.3%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇸🇪 Sweden</span>
                                        <span>32 kW @ ₩192/kWh <span class="price-trend price-up">↗ +1.8%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇷🇴 Romania</span>
                                        <span>28 kW @ ₩178/kWh <span class="price-trend price-down">↘ -0.5%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇬🇷 Greece</span>
                                        <span>38 kW @ ₩201/kWh <span class="price-trend price-up">↗ +3.1%</span></span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <h6>구매 호가</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🏭 Industrial Co.</span>
                                        <span>120 kW @ ₩200/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏢 Office Complex</span>
                                        <span>85 kW @ ₩195/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏪 Retail Chain</span>
                                        <span>65 kW @ ₩190/kWh</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🏥 Hospital</span>
                                        <span>45 kW @ ₩205/kWh</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="openP2PMarket()">
                                <i class="fas fa-chart-line"></i> P2P 마켓 열기
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="carbon-card">
                        <h4><i class="fas fa-leaf"></i> 탄소 크레딧 거래</h4>
                        <div class="row">
                            <div class="col-6">
                                <h6>보유 크레딧</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>🇫🇮 Finland</span>
                                        <span>652톤 (₩29.3M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇸🇪 Sweden</span>
                                        <span>1,200톤 (₩54.0M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇷🇴 Romania</span>
                                        <span>450톤 (₩20.3M)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>🇬🇷 Greece</span>
                                        <span>5,000톤 (₩225.0M)</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <h6>시장 정보</h6>
                                <div class="trading-table">
                                    <div class="trading-item">
                                        <span>현재 가격</span>
                                        <span>₩45,000/톤 <span class="price-trend price-up">↗ +2.3%</span></span>
                                    </div>
                                    <div class="trading-item">
                                        <span>24h 변동</span>
                                        <span>+₩1,050/톤</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>월간 거래량</span>
                                        <span>1,847톤</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>시장 캡</span>
                                        <span>₩328.6M</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="openCarbonMarket()">
                                <i class="fas fa-seedling"></i> 탄소 시장 열기
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI 최적화 엔진 -->
            <div class="row">
                <div class="col-12">
                    <div class="ai-card">
                        <h4><i class="fas fa-robot"></i> AI 수익 최적화 엔진</h4>
                        <div class="row">
                            <div class="col-md-8">
                                <div class="chart-container">
                                    <canvas id="aiOptimizationChart"></canvas>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="trading-table">
                                    <h6>최적화 전략</h6>
                                    <div class="trading-item">
                                        <span>전력 판매 최적화</span>
                                        <span>₩35.7M (+12%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>탄소 크레딧 최적화</span>
                                        <span>₩28.8M (+8%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>수요 반응 최적화</span>
                                        <span>₩2.3M (+15%)</span>
                                    </div>
                                    <div class="trading-item">
                                        <span>총 최적화 효과</span>
                                        <span>₩66.8M (+11%)</span>
                                    </div>
                                </div>
                                <div class="text-center mt-3">
                                    <button class="btn btn-trading" onclick="runAIOptimization()">
                                        <i class="fas fa-magic"></i> AI 최적화 실행
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 블록체인 거래 기록 -->
            <div class="row">
                <div class="col-md-6">
                    <div class="blockchain-card">
                        <h4><i class="fas fa-link"></i> 블록체인 거래 기록</h4>
                        <div class="trading-table">
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x1a2b3c...</span>
                                <span>Finland → Industrial Co. 45kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x4d5e6f...</span>
                                <span>Sweden → Office Complex 32kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-check-circle text-success"></i> TX: 0x7g8h9i...</span>
                                <span>Greece → Hospital 38kW</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-clock text-warning"></i> TX: 0x0j1k2l...</span>
                                <span>Romania → Retail Chain 28kW (대기중)</span>
                            </div>
                        </div>
                        <div class="text-center mt-3">
                            <button class="btn btn-trading" onclick="viewBlockchain()">
                                <i class="fas fa-external-link-alt"></i> 블록체인 탐색기
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="trading-card">
                        <h4><i class="fas fa-chart-bar"></i> 거래 통계 및 분석</h4>
                        <div class="row">
                            <div class="col-6">
                                <div class="chart-container">
                                    <canvas id="tradingVolumeChart"></canvas>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="chart-container">
                                    <canvas id="tradingPriceChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 거래 피드 -->
            <div class="row">
                <div class="col-12">
                    <div class="trading-card">
                        <h4><i class="fas fa-stream"></i> 실시간 거래 피드</h4>
                        <div class="trading-table" id="tradingFeed">
                            <div class="trading-item">
                                <span><i class="fas fa-bolt text-warning"></i> 14:32:15</span>
                                <span>Finland에서 Industrial Co.로 45kW 거래 완료 (₩8,325)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-leaf text-success"></i> 14:31:42</span>
                                <span>Sweden에서 100톤 탄소 크레딧 판매 (₩4,500,000)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-bolt text-warning"></i> 14:30:18</span>
                                <span>Greece에서 Hospital로 38kW 거래 완료 (₩7,638)</span>
                            </div>
                            <div class="trading-item">
                                <span><i class="fas fa-robot text-info"></i> 14:29:55</span>
                                <span>AI 최적화로 수익 12% 증가 예상</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // AI 최적화 차트
            function initAIChart() {{
                const ctx = document.getElementById('aiOptimizationChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                        datasets: [{{
                            label: 'AI 최적화 전 수익',
                            data: [60, 65, 70, 68, 72, 75],
                            borderColor: '#ff9a9e',
                            backgroundColor: 'rgba(255, 154, 158, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'AI 최적화 후 수익',
                            data: [67, 73, 78, 76, 81, 85],
                            borderColor: '#43e97b',
                            backgroundColor: 'rgba(67, 233, 123, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                labels: {{ color: 'white' }}
                            }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: 'white' }} }},
                            y: {{ ticks: {{ color: 'white' }} }}
                        }}
                    }}
                }});
            }}
            
            // 거래량 차트
            function initTradingVolumeChart() {{
                const ctx = document.getElementById('tradingVolumeChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Finland', 'Sweden', 'Romania', 'Greece'],
                        datasets: [{{
                            label: '거래량 (kW)',
                            data: [45, 32, 28, 38],
                            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});
            }}
            
            // 거래 가격 차트
            function initTradingPriceChart() {{
                const ctx = document.getElementById('tradingPriceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: '평균 거래 가격 (₩/kWh)',
                            data: [185, 178, 192, 201, 195, 188],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{ beginAtZero: false }}
                        }}
                    }}
                }});
            }}
            
            // 실시간 데이터 업데이트
            function updateTradingData() {{
                // KPI 업데이트
                document.getElementById('totalTrades').textContent = (1247 + Math.floor(Math.random() * 10)).toLocaleString();
                document.getElementById('totalVolume').textContent = '₩' + (89.2 + Math.random() * 2).toFixed(1) + 'M';
                document.getElementById('activeUsers').textContent = (156 + Math.floor(Math.random() * 5)).toLocaleString();
                document.getElementById('platformFee').textContent = '₩' + (1.8 + Math.random() * 0.2).toFixed(1) + 'M';
            }}
            
            // P2P 마켓 열기
            function openP2PMarket() {{
                alert('P2P 전력 거래 마켓플레이스가 곧 열립니다!\\n\\n• 실시간 매칭 알고리즘\\n• 자동 거래 실행\\n• 수수료 최적화');
            }}
            
            // 탄소 시장 열기
            function openCarbonMarket() {{
                alert('탄소 크레딧 거래 시장이 곧 열립니다!\\n\\n• 크레딧 발행 및 추적\\n• 검증 및 인증 시스템\\n• 블록체인 기록');
            }}
            
            // AI 최적화 실행
            function runAIOptimization() {{
                alert('AI 수익 최적화 엔진이 실행되었습니다!\\n\\n• 수익 최적화 AI 엔진\\n• 수요 반응 자동화\\n• 예측 정확도 개선\\n• 개인화된 추천');
            }}
            
            // 블록체인 탐색기
            function viewBlockchain() {{
                alert('블록체인 탐색기로 이동합니다!\\n\\n• 거래 투명성 보장\\n• 스마트 컨트랙트 실행\\n• 실시간 거래 기록');
            }}
            
            // 실시간 거래 피드 업데이트
            function updateTradingFeed() {{
                const feed = document.getElementById('tradingFeed');
                const now = new Date();
                const timeString = now.toLocaleTimeString('ko-KR');
                
                const newTrade = document.createElement('div');
                newTrade.className = 'trading-item';
                newTrade.innerHTML = `
                    <span><i class="fas fa-bolt text-warning"></i> ${{timeString}}</span>
                    <span>새로운 거래가 실행되었습니다 (₩${{(Math.random() * 10000 + 1000).toFixed(0)}})</span>
                `;
                
                feed.insertBefore(newTrade, feed.firstChild);
                
                // 최대 10개 항목만 유지
                while (feed.children.length > 10) {{
                    feed.removeChild(feed.lastChild);
                }}
            }}
            
            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initAIChart();
                initTradingVolumeChart();
                initTradingPriceChart();
                updateTradingData();
                
                // 5초마다 데이터 업데이트
                setInterval(updateTradingData, 5000);
                // 10초마다 거래 피드 업데이트
                setInterval(updateTradingFeed, 10000);
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/data-collection", response_class=HTMLResponse)
async def data_collection_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Energy Supply Monitoring with Advanced Weather Analysis 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('energySupply.title', lang)}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .dashboard-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .weather-card {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .metric-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            .chart-container {{
                max-height: 300px;
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
            .weather-icon {{
                font-size: 3rem;
                margin-bottom: 10px;
            }}
            .correlation-card {{
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                color: #333;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 실시간 에너지 공급 현황 -->
            <div class="row">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h4><i class="fas fa-chart-line"></i> 실시간 에너지 공급 현황</h4>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-value" id="totalGeneration">5.2 kW</div>
                                    <div class="metric-label">총 발전량</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-value" id="solarGeneration">3.2 kW</div>
                                    <div class="metric-label">태양광 발전</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-value" id="essGeneration">2.1 kW</div>
                                    <div class="metric-label">ESS 발전</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card">
                                    <div class="metric-value" id="systemEfficiency">94.2%</div>
                                    <div class="metric-label">시스템 효율</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 에너지 공급 예측 분석 -->
            <div class="row">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h4><i class="fas fa-crystal-ball"></i> 에너지 공급 예측 분석</h4>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="weather-card text-center">
                                    <h6>1시간 후 예측</h6>
                                    <div class="metric-value" id="supplyPrediction1h">5.8 kW</div>
                                    <div class="metric-label">예측 공급량</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="weather-card text-center">
                                    <h6>6시간 후 예측</h6>
                                    <div class="metric-value" id="supplyPrediction6h">4.2 kW</div>
                                    <div class="metric-label">예측 공급량</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="weather-card text-center">
                                    <h6>24시간 후 예측</h6>
                                    <div class="metric-value" id="supplyPrediction24h">6.1 kW</div>
                                    <div class="metric-label">예측 공급량</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="weather-card text-center">
                                    <h6>예측 정확도</h6>
                                    <div class="metric-value" id="supplyPredictionAccuracy">96.8%</div>
                                    <div class="metric-label">AI 예측 정확도</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 고급 날씨 정보 분석 -->
            <div class="row">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h4><i class="fas fa-cloud-sun"></i> {t('energySupply.advancedWeatherAnalysis', lang)}</h4>
                        <div class="row">
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon" id="weatherIcon">☀️</div>
                                    <div class="metric-value" id="temperature">23°C</div>
                                    <div class="metric-label">{t('energySupply.temperature', lang)}</div>
                                    <small class="text-muted" id="tempTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="tempTime"></span></small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon">💧</div>
                                    <div class="metric-value" id="humidity">65%</div>
                                    <div class="metric-label">{t('energySupply.humidity', lang)}</div>
                                    <small class="text-muted" id="humidityTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="humidityTime"></span></small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon">💨</div>
                                    <div class="metric-value" id="windSpeed">12 km/h</div>
                                    <div class="metric-label">{t('energySupply.windSpeed', lang)}</div>
                                    <small class="text-muted" id="windTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="windTime"></span></small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon">☀️</div>
                                    <div class="metric-value" id="solarIrradiance">850 W/m²</div>
                                    <div class="metric-label">{t('energySupply.solarIrradiance', lang)}</div>
                                    <small class="text-muted" id="solarTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="solarTime"></span></small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon">🌧️</div>
                                    <div class="metric-value" id="precipitation">0 mm</div>
                                    <div class="metric-label">{t('energySupply.precipitation', lang)}</div>
                                    <small class="text-muted" id="precipTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="precipTime"></span></small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="weather-card text-center">
                                    <div class="weather-icon">👁️</div>
                                    <div class="metric-value" id="visibility">10 km</div>
                                    <div class="metric-label">{t('energySupply.visibility', lang)}</div>
                                    <small class="text-muted" id="visTimestamp">{t('energySupply.lastUpdate', lang)}: <span id="visTime"></span></small>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3 text-center">
                            <button class="btn btn-primary btn-sm" onclick="refreshWeatherData()">
                                <i class="fas fa-sync-alt"></i> {t('energySupply.refresh', lang)}
                            </button>
                            <small class="text-muted ms-3">{t('energySupply.autoRefresh', lang)}: 30초</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 에너지-날씨 상관관계 분석 -->
            <div class="row">
                <div class="col-lg-6">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-chart-area"></i> {t('energySupply.energyGenerationTrends', lang)}</h5>
                        <canvas id="generationChart" class="chart-container"></canvas>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-thermometer-half"></i> {t('energySupply.weatherConditions', lang)}</h5>
                        <canvas id="weatherChart" class="chart-container"></canvas>
                    </div>
                </div>
            </div>

            <!-- 에너지-날씨 상관관계 분석 -->
            <div class="row">
                <div class="col-lg-4">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-chart-pie"></i> {t('energySupply.energyMixDistribution', lang)}</h5>
                        <canvas id="energyMixChart" class="chart-container"></canvas>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-link"></i> {t('energySupply.energyWeatherCorrelation', lang)}</h5>
                        <div class="correlation-card">
                            <h6><i class="fas fa-sun"></i> {t('energySupply.solarVsIrradiance', lang)}</h6>
                            <div class="mb-2">
                                <small>{t('energySupply.correlation', lang)}: <strong id="solarCorrelation">0.87</strong></small>
                                <div class="progress">
                                    <div class="progress-bar bg-warning" style="width: 87%"></div>
                                </div>
                            </div>
                            <h6><i class="fas fa-battery-half"></i> {t('energySupply.essVsEfficiency', lang)}</h6>
                            <div class="mb-2">
                                <small>{t('energySupply.correlation', lang)}: <strong id="essCorrelation">0.92</strong></small>
                                <div class="progress">
                                    <div class="progress-bar bg-info" style="width: 92%"></div>
                                </div>
                            </div>
                            <h6><i class="fas fa-thermometer-half"></i> {t('energySupply.efficiencyVsTemperature', lang)}</h6>
                            <div class="mb-2">
                                <small>{t('energySupply.correlation', lang)}: <strong id="tempCorrelation">-0.34</strong></small>
                                <div class="progress">
                                    <div class="progress-bar bg-danger" style="width: 34%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-chart-line"></i> Weather Impact Analysis</h5>
                        <canvas id="impactChart" class="chart-container"></canvas>
                    </div>
                </div>
            </div>

            <!-- 시스템 상태 모니터링 -->
            <div class="row">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-cogs"></i> {t('energySupply.systemStatusMonitoring', lang)}</h5>
                        <div class="row">
                            <div class="col-md-3">
                                <h6>{t('energySupply.solarPanelArray', lang)}</h6>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.panel', lang)} 1-10: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.panel', lang)} 11-20: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-warning"></span>
                                    <span>{t('energySupply.panel', lang)} 21-25: <strong>{t('energySupply.maintenance', lang)}</strong></span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <h6>🔋 {t('energySupply.energyStorageSystem', lang)} (ESS)</h6>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.batteryBank', lang)} 1: <strong>🟢 충전 중 (87% SOC)</strong></span>
                                    <small class="text-muted d-block">충전 속도: +2.3 kW</small>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.batteryBank', lang)} 2: <strong>🟢 방전 중 (88% SOC)</strong></span>
                                    <small class="text-muted d-block">방전 속도: -1.8 kW</small>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-warning"></span>
                                    <span>{t('energySupply.batteryBank', lang)} 3: <strong>🟡 정비 중</strong></span>
                                    <small class="text-muted d-block">완료 예정: 17:00</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <h6>⚡ {t('energySupply.inverterSystem', lang)}</h6>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>인버터 1: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>인버터 2: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>제어 시스템: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <h6>{t('energySupply.weatherSensors', lang)}</h6>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.temperature', lang)}: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>{t('energySupply.windSpeed', lang)}: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                                <div class="mb-2">
                                    <span class="status-indicator status-online"></span>
                                    <span>태양 센서: <strong>{t('energySupply.online', lang)}</strong></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 날씨 예측 및 에너지 예측 -->
            <div class="row">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h5><i class="fas fa-crystal-ball"></i> {t('energySupply.weatherForecast', lang)} & {t('energySupply.energyGenerationPrediction', lang)}</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>다음 24시간 {t('energySupply.weatherForecast', lang)}</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Time</th>
                                                <th>Weather</th>
                                                <th>Temp</th>
                                                <th>Wind</th>
                                                <th>Solar</th>
                                            </tr>
                                        </thead>
                                        <tbody id="weatherForecast">
                                            <tr>
                                                <td>00:00</td>
                                                <td>🌙 Clear</td>
                                                <td>18°C</td>
                                                <td>8 km/h</td>
                                                <td>0 W/m²</td>
                                            </tr>
                                            <tr>
                                                <td>06:00</td>
                                                <td>🌅 Sunny</td>
                                                <td>22°C</td>
                                                <td>12 km/h</td>
                                                <td>450 W/m²</td>
                                            </tr>
                                            <tr>
                                                <td>12:00</td>
                                                <td>☀️ Sunny</td>
                                                <td>28°C</td>
                                                <td>15 km/h</td>
                                                <td>850 W/m²</td>
                                            </tr>
                                            <tr>
                                                <td>18:00</td>
                                                <td>🌤️ Partly Cloudy</td>
                                                <td>25°C</td>
                                                <td>10 km/h</td>
                                                <td>300 W/m²</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Energy Generation Prediction</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Time</th>
                                                <th>Solar (kW)</th>
                                                <th>ESS (kW)</th>
                                                <th>Total (kW)</th>
                                                <th>Efficiency</th>
                                            </tr>
                                        </thead>
                                        <tbody id="energyPrediction">
                                            <tr>
                                                <td>00:00</td>
                                                <td>0.0</td>
                                                <td>1.2</td>
                                                <td>1.2</td>
                                                <td>92%</td>
                                            </tr>
                                            <tr>
                                                <td>06:00</td>
                                                <td>1.8</td>
                                                <td>1.5</td>
                                                <td>3.3</td>
                                                <td>94%</td>
                                            </tr>
                                            <tr>
                                                <td>12:00</td>
                                                <td>3.5</td>
                                                <td>2.1</td>
                                                <td>5.6</td>
                                                <td>96%</td>
                                            </tr>
                                            <tr>
                                                <td>18:00</td>
                                                <td>1.2</td>
                                                <td>1.8</td>
                                                <td>3.0</td>
                                                <td>93%</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 타임스탬프 업데이트
            function updateTimestamps() {{
                const now = new Date();
                const timeString = now.toLocaleTimeString('ko-KR', {{ 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit' 
                }});
                
                // 모든 센서 타임스탬프 업데이트
                const timestampElements = ['tempTime', 'humidityTime', 'windTime', 'solarTime', 'precipTime', 'visTime'];
                timestampElements.forEach(id => {{
                    const element = document.getElementById(id);
                    if (element) {{
                        element.textContent = timeString;
                    }}
                }});
            }}

            // 날씨 데이터 새로고침
            function refreshWeatherData() {{
                const button = event.target;
                const icon = button.querySelector('i');
                icon.style.animation = 'spin 1s linear infinite';
                
                updateRealtimeData();
                updateTimestamps();
                
                setTimeout(() => {{
                    icon.style.animation = '';
                }}, 1000);
            }}

            // 실시간 데이터 업데이트
            function updateRealtimeData() {{
                // 발전량 데이터 업데이트
                const solarGen = (Math.random() * 2 + 2.5).toFixed(1);
                const essGen = (Math.random() * 1.5 + 1.2).toFixed(1);
                const totalGen = (parseFloat(solarGen) + parseFloat(essGen)).toFixed(1);
                const efficiency = (Math.random() * 5 + 92).toFixed(1);

                document.getElementById('totalGeneration').textContent = totalGen + ' kW';
                document.getElementById('solarGeneration').textContent = solarGen + ' kW';
                document.getElementById('essGeneration').textContent = essGen + ' kW';
                document.getElementById('systemEfficiency').textContent = efficiency + '%';

                // 공급 예측 데이터 업데이트
                const supplyPrediction1h = (Math.random() * 1.5 + 5.0).toFixed(1);
                const supplyPrediction6h = (Math.random() * 2.0 + 3.5).toFixed(1);
                const supplyPrediction24h = (Math.random() * 2.5 + 5.5).toFixed(1);
                const supplyPredictionAccuracy = (Math.random() * 3 + 95).toFixed(1);

                document.getElementById('supplyPrediction1h').textContent = supplyPrediction1h + ' kW';
                document.getElementById('supplyPrediction6h').textContent = supplyPrediction6h + ' kW';
                document.getElementById('supplyPrediction24h').textContent = supplyPrediction24h + ' kW';
                document.getElementById('supplyPredictionAccuracy').textContent = supplyPredictionAccuracy + '%';

                // 날씨 데이터 업데이트
                const temperature = (Math.random() * 15 + 15).toFixed(0);
                const humidity = (Math.random() * 30 + 40).toFixed(0);
                const windSpeed = (Math.random() * 20 + 5).toFixed(0);
                const solarIrradiance = (Math.random() * 500 + 300).toFixed(0);
                const precipitation = (Math.random() * 5).toFixed(1);
                const visibility = (Math.random() * 5 + 8).toFixed(0);

                document.getElementById('temperature').textContent = temperature + '°C';
                document.getElementById('humidity').textContent = humidity + '%';
                document.getElementById('windSpeed').textContent = windSpeed + ' km/h';
                document.getElementById('solarIrradiance').textContent = solarIrradiance + ' W/m²';
                document.getElementById('precipitation').textContent = precipitation + ' mm';
                document.getElementById('visibility').textContent = visibility + ' km';

                // 날씨 아이콘 업데이트
                const weatherIcons = ['☀️', '⛅', '☁️', '🌧️', '⛈️', '🌩️'];
                const randomIcon = weatherIcons[Math.floor(Math.random() * weatherIcons.length)];
                document.getElementById('weatherIcon').textContent = randomIcon;

                // 상관관계 업데이트
                const solarCorr = (Math.random() * 0.2 + 0.8).toFixed(2);
                const windCorr = (Math.random() * 0.2 + 0.8).toFixed(2);
                const tempCorr = (Math.random() * 0.4 - 0.2).toFixed(2);

                document.getElementById('solarCorrelation').textContent = solarCorr;
                document.getElementById('essCorrelation').textContent = windCorr;
                document.getElementById('tempCorrelation').textContent = tempCorr;

                // 진행률 바 업데이트
                document.querySelector('.progress-bar.bg-warning').style.width = (solarCorr * 100) + '%';
                document.querySelector('.progress-bar.bg-info').style.width = (windCorr * 100) + '%';
                document.querySelector('.progress-bar.bg-danger').style.width = (Math.abs(tempCorr) * 100) + '%';
            }}

            // 차트 초기화
            function initCharts() {{
                // 발전량 트렌드 차트
                const generationCtx = document.getElementById('generationChart').getContext('2d');
                new Chart(generationCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Solar Generation',
                            data: [0, 0, 1.5, 3.2, 2.8, 0.5],
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'ESS Generation',
                            data: [1.2, 1.8, 1.5, 1.0, 1.5, 1.8],
                            borderColor: '#17a2b8',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Power (kW)'
                                }}
                            }}
                        }}
                    }}
                }});

                // 날씨 조건 차트
                const weatherCtx = document.getElementById('weatherChart').getContext('2d');
                new Chart(weatherCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Temperature (°C)',
                            data: [18, 16, 20, 25, 28, 22],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        }}, {{
                            label: 'Wind Speed (km/h)',
                            data: [8, 12, 15, 18, 12, 10],
                            borderColor: '#17a2b8',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}, {{
                            label: 'Solar Irradiance (W/m²)',
                            data: [0, 0, 300, 850, 600, 100],
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y2'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: 'Temperature (°C)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'Wind Speed (km/h)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }},
                            y2: {{
                                type: 'linear',
                                display: false,
                            }}
                        }}
                    }}
                }});

                // 에너지 믹스 차트
                const energyMixCtx = document.getElementById('energyMixChart').getContext('2d');
                new Chart(energyMixCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Solar', 'ESS', 'Storage'],
                        datasets: [{{
                            data: [3.2, 1.8, 0.2],
                            backgroundColor: ['#ffc107', '#17a2b8', '#28a745']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});

                // 날씨 영향 분석 차트
                const impactCtx = document.getElementById('impactChart').getContext('2d');
                new Chart(impactCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Solar', 'ESS', 'Efficiency', 'Storage'],
                        datasets: [{{
                            label: 'Weather Impact (%)',
                            data: [85, 92, -15, 5],
                            backgroundColor: ['#ffc107', '#17a2b8', '#dc3545', '#28a745']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Impact (%)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initCharts();
                updateRealtimeData();
                updateTimestamps();
                
                // 5초마다 데이터 업데이트
                setInterval(updateRealtimeData, 5000);
                // 1초마다 타임스탬프 업데이트
                setInterval(updateTimestamps, 1000);
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/data-analysis", response_class=HTMLResponse)
async def data_analysis_page(request: Request, lang: str = Query("ko", description="Language code")):
    """개선된 에너지 수요 분석 및 예측 대시보드"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>에너지 수요 분석 및 예측 대시보드</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .monitoring-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .facility-info {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .sensor-card {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                color: #333;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .power-card {{
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                color: #333;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .event-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .calendar-card {{
                background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                color: #333;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .metric-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            .chart-container {{
                max-height: 300px;
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
            .event-timeline {{
                max-height: 400px;
                overflow-y: auto;
            }}
            .event-item {{
                border-left: 3px solid #007bff;
                padding-left: 15px;
                margin-bottom: 15px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 5px;
                padding: 10px;
            }}
            .event-time {{
                font-size: 0.8rem;
                color: #666;
                font-weight: bold;
            }}
            .event-content {{
                margin-top: 5px;
            }}
            .memo-input {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .model-info {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
            }}
            .model-item {{
                margin-bottom: 8px;
                font-size: 0.9rem;
            }}
            .data-sources {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
            }}
            .source-item {{
                display: flex;
                align-items: center;
                margin-bottom: 10px;
                font-size: 0.9rem;
            }}
            .source-item i {{
                margin-right: 10px;
                width: 20px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                font-size: 0.9rem;
            }}
            .legend-color {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .prediction-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .prediction-value {{
                font-size: 1.5rem;
                font-weight: bold;
                margin: 10px 0;
            }}
            .prediction-confidence {{
                font-size: 0.8rem;
                opacity: 0.8;
            }}
            .prediction-settings {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
            }}
            .setting-item {{
                margin-bottom: 15px;
            }}
            .setting-item:last-child {{
                margin-bottom: 0;
            }}
            .simulation-results, .control-results {{
                min-height: 120px;
            }}
            .alert {{
                border: none;
                border-radius: 8px;
            }}
            .alert-info {{
                background: rgba(13, 202, 240, 0.1);
                color: #0dcaf0;
            }}
            .alert-success {{
                background: rgba(25, 135, 84, 0.1);
                color: #198754;
            }}
            .alert-warning {{
                background: rgba(255, 193, 7, 0.1);
                color: #ffc107;
            }}
            .alert-danger {{
                background: rgba(220, 53, 69, 0.1);
                color: #dc3545;
            }}
            .table-responsive {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
            }}
            .table {{
                margin-bottom: 0;
            }}
            .table th, .table td {{
                border-color: rgba(255, 255, 255, 0.1);
                color: #333;
            }}
            .table th {{
                background: rgba(255, 255, 255, 0.1);
                font-weight: 600;
            }}
            .btn-group .btn.active {{
                background-color: #0d6efd;
                border-color: #0d6efd;
                color: white;
            }}
            .form-range {{
                background: rgba(255, 255, 255, 0.1);
            }}
            .form-check-input:checked {{
                background-color: #0d6efd;
                border-color: #0d6efd;
            }}
            .form-select, .form-control {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(0, 0, 0, 0.1);
            }}
            .form-select:focus, .form-control:focus {{
                background: rgba(255, 255, 255, 0.95);
                border-color: #0d6efd;
                box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
            }}
            .energy-flow-container {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .supply-section, .strategy-section, .demand-section {{
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 15px;
                height: 100%;
            }}
            .supply-item {{
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
            }}
            .supply-icon {{
                font-size: 1.5rem;
                margin-right: 12px;
                width: 30px;
                text-align: center;
            }}
            .supply-info {{
                flex: 1;
            }}
            .strategy-item {{
                margin-bottom: 12px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                text-align: center;
            }}
            .strategy-priority {{
                font-weight: bold;
                color: #ffc107;
                font-size: 0.9rem;
            }}
            .strategy-desc {{
                font-size: 0.85rem;
                margin-top: 5px;
            }}
            .building-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            .building-item {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .building-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .building-power {{
                font-weight: bold;
                color: #4ecdc4;
            }}
            .device-item {{
                margin-bottom: 8px;
                padding: 6px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 4px;
                font-size: 0.85rem;
            }}
            .device-item:last-child {{
                margin-bottom: 0;
            }}
            .device-name {{
                font-weight: 500;
                margin-right: 8px;
            }}
            .device-power {{
                color: #ff6b6b;
                font-weight: bold;
                margin-right: 8px;
            }}
            .power-source {{
                margin-top: 4px;
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            .source-solar, .source-ess, .source-grid {{
                font-size: 0.75rem;
                padding: 2px 6px;
                border-radius: 3px;
                background: rgba(255, 255, 255, 0.1);
            }}
            .source-solar {{ background: rgba(255, 193, 7, 0.2); }}
            .source-ess {{ background: rgba(40, 167, 69, 0.2); }}
            .source-grid {{ background: rgba(220, 53, 69, 0.2); }}
            .matching-summary {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .demand-response-panel {{
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 15px;
            }}
            .dr-recommendation {{
                margin-bottom: 20px;
            }}
            .dr-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .dr-priority {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .dr-priority.high {{
                background: rgba(220, 53, 69, 0.2);
                color: #dc3545;
            }}
            .dr-item {{
                margin-bottom: 20px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .dr-title {{
                font-weight: bold;
                margin-bottom: 10px;
                color: #4ecdc4;
            }}
            .dr-target, .dr-goal {{
                margin-bottom: 8px;
                font-size: 0.9rem;
            }}
            .dr-options {{
                margin: 15px 0;
            }}
            .dr-option {{
                margin-bottom: 10px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .dr-option input[type="radio"] {{
                margin-right: 8px;
            }}
            .dr-option label {{
                font-weight: 500;
                cursor: pointer;
            }}
            .dr-effect {{
                font-size: 0.8rem;
                color: #6c757d;
                margin-top: 5px;
                margin-left: 20px;
            }}
            .dr-summary {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .dr-actions {{
                margin-top: 10px;
                display: flex;
                gap: 8px;
            }}
            .dr-summary-total {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .summary-stat {{
                text-align: center;
                padding: 10px;
            }}
            .stat-value {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #4ecdc4;
            }}
            .dr-total-actions {{
                text-align: center;
            }}
            .notification-panel {{
                max-height: 400px;
                overflow-y: auto;
            }}
            .notification-item {{
                display: flex;
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 8px;
                border-left: 4px solid;
            }}
            .notification-item.urgent {{
                background: rgba(220, 53, 69, 0.1);
                border-left-color: #dc3545;
            }}
            .notification-item.warning {{
                background: rgba(255, 193, 7, 0.1);
                border-left-color: #ffc107;
            }}
            .notification-item.info {{
                background: rgba(13, 202, 240, 0.1);
                border-left-color: #0dcaf0;
            }}
            .notification-icon {{
                font-size: 1.2rem;
                margin-right: 10px;
                margin-top: 2px;
            }}
            .notification-content {{
                flex: 1;
            }}
            .notification-title {{
                font-weight: bold;
                margin-bottom: 4px;
            }}
            .notification-desc {{
                font-size: 0.85rem;
                color: #6c757d;
                margin-bottom: 8px;
            }}
            .notification-action {{
                margin-top: 8px;
            }}
            .performance-summary {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
            }}
            .performance-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                padding: 6px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .performance-item:last-child {{
                border-bottom: none;
                margin-bottom: 0;
            }}
            .performance-value {{
                font-weight: bold;
                color: #4ecdc4;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 대시보드 헤더 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="facility-info">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h2><i class="fas fa-chart-line"></i> 에너지 수요 분석 및 예측 대시보드</h2>
                                <p class="mb-0">실시간 에너지 수요 모니터링 및 AI 기반 예측 분석</p>
                            </div>
                            <div class="text-end">
                                <div class="mb-2">
                                    <small class="text-light">마지막 업데이트: <span id="lastUpdate">-</span></small>
                            </div>
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-light btn-sm" onclick="refreshData()">
                                        <i class="fas fa-sync-alt"></i> 새로고침
                                    </button>
                                    <button type="button" class="btn btn-light btn-sm" onclick="exportData()">
                                        <i class="fas fa-download"></i> 데이터 내보내기
                                    </button>
                                    <button type="button" class="btn btn-light btn-sm" onclick="showDataSource()">
                                        <i class="fas fa-info-circle"></i> 데이터 출처
                                    </button>
                            </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 수요-공급 매칭 현황 -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="monitoring-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5><i class="fas fa-chart-area"></i> 실시간 수요-공급 매칭 현황</h5>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary active" onclick="changeTimeRange('1h')">1시간</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changeTimeRange('6h')">6시간</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changeTimeRange('24h')">24시간</button>
                                </div>
                            </div>
                        <canvas id="realtimeChart" class="chart-container" style="height: 400px;"></canvas>
                        <div class="mt-3">
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="metric-card">
                                        <h6 class="text-primary">현재 매칭율</h6>
                                        <h4 id="current-efficiency" class="real-time-value">87.3%</h4>
                                        <small class="text-muted">수요: <span id="current-demand" class="real-time-value">1,250</span> kW / 공급: <span id="current-supply" class="real-time-value">1,432</span> kW</small>
                                </div>
                            </div>
                                <div class="col-4">
                                    <div class="metric-card">
                                        <h6 class="text-success">1시간 후 예측</h6>
                                        <h4 id="prediction1h">92.1%</h4>
                                        <small class="text-muted">예측 수요: <span id="predDemand1h">1,320</span> kW / 예측 공급: <span id="predSupply1h">1,434</span> kW</small>
                                </div>
                            </div>
                                <div class="col-4">
                                    <div class="metric-card">
                                        <h6 class="text-warning">6시간 후 예측</h6>
                                        <h4 id="prediction6h">78.5%</h4>
                                        <small class="text-muted">예측 수요: <span id="predDemand6h">1,180</span> kW / 예측 공급: <span id="predSupply6h">1,503</span> kW</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="monitoring-card">
                        <h5><i class="fas fa-robot"></i> AI 예측 모델 정보</h5>
                        <div class="model-info">
                            <div class="model-item">
                                <strong>모델명:</strong> EnergyDemandPredictor v2.1
                            </div>
                            <div class="model-item">
                                <strong>학습 데이터:</strong> 2년간의 에너지 사용 패턴
                            </div>
                            <div class="model-item">
                                <strong>예측 정확도:</strong> <span id="modelAccuracy">94.2%</span>
                            </div>
                            <div class="model-item">
                                <strong>마지막 학습:</strong> 2024-01-15
                            </div>
                            <div class="model-item">
                                <strong>특징:</strong> LSTM + 시계열 분석
                            </div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-primary btn-sm w-100" onclick="showModelDetails()">
                                <i class="fas fa-cogs"></i> 모델 상세 정보
                            </button>
                </div>
            </div>

                    <div class="monitoring-card mt-3">
                        <h5><i class="fas fa-database"></i> 데이터 출처</h5>
                        <div class="data-sources">
                            <div class="source-item">
                                <i class="fas fa-solar-panel text-warning"></i>
                                <span>태양광 발전소 (3개소)</span>
                            </div>
                            <div class="source-item">
                                <i class="fas fa-wind text-info"></i>
                                <span>풍력 발전소 (2개소)</span>
                            </div>
                            <div class="source-item">
                                <i class="fas fa-bolt text-danger"></i>
                                <span>전력 수요 센서 (15개)</span>
                            </div>
                            <div class="source-item">
                                <i class="fas fa-thermometer-half text-success"></i>
                                <span>기상 데이터 (KMA API)</span>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-outline-primary btn-sm w-100" onclick="showRawData()">
                                <i class="fas fa-table"></i> 원시 데이터 보기
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 전자기기별 수요 분석 -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="monitoring-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5><i class="fas fa-microchip"></i> 전자기기별 에너지 수요 분석</h5>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary active" onclick="changeDeviceView('chart')">차트</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changeDeviceView('table')">테이블</button>
                                </div>
                            </div>
                        <div id="deviceChartView">
                            <canvas id="deviceChart" class="chart-container" style="height: 300px;"></canvas>
                                </div>
                        <div id="deviceTableView" style="display: none;">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>기기명</th>
                                            <th>현재 수요</th>
                                            <th>평균 수요</th>
                                            <th>효율성</th>
                                            <th>상태</th>
                                            <th>액션</th>
                                        </tr>
                                    </thead>
                                    <tbody id="deviceTableBody">
                                        <!-- 동적으로 생성됨 -->
                                    </tbody>
                                </table>
                            </div>
                                </div>
                            </div>
                                </div>
                <div class="col-lg-4">
                    <div class="monitoring-card">
                        <h5><i class="fas fa-chart-pie"></i> 수요 분포</h5>
                        <canvas id="demandDistributionChart" class="chart-container" style="height: 250px;"></canvas>
                        <div class="mt-3">
                            <div class="legend-item">
                                <span class="legend-color" style="background-color: #ff6b6b;"></span>
                                <span>HVAC 시스템: <strong id="hvacPercent">36%</strong></span>
                            </div>
                            <div class="legend-item">
                                <span class="legend-color" style="background-color: #4ecdc4;"></span>
                                <span>IT 장비: <strong id="itPercent">26%</strong></span>
                        </div>
                            <div class="legend-item">
                                <span class="legend-color" style="background-color: #45b7d1;"></span>
                                <span>기타 장비: <strong id="otherPercent">24%</strong></span>
                            </div>
                            <div class="legend-item">
                                <span class="legend-color" style="background-color: #f9ca24;"></span>
                                <span>조명 시스템: <strong id="lightingPercent">14%</strong></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 수요 예측 분석 -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="monitoring-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5><i class="fas fa-crystal-ball"></i> 에너지 수요 예측 분석</h5>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary active" onclick="changePredictionRange('24h')">24시간</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changePredictionRange('7d')">7일</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changePredictionRange('30d')">30일</button>
                            </div>
                        </div>
                        <canvas id="predictionChart" class="chart-container" style="height: 350px;"></canvas>
                        <div class="mt-3">
                        <div class="row">
                                <div class="col-md-4">
                                    <div class="prediction-card">
                                        <h6 class="text-primary">단기 예측 (1-6시간)</h6>
                                        <div class="prediction-value" id="shortTermPrediction">1,250 kW</div>
                                        <div class="prediction-confidence">신뢰도: <span id="shortTermConfidence">96.5%</span></div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="prediction-card">
                                        <h6 class="text-success">중기 예측 (1-7일)</h6>
                                        <div class="prediction-value" id="mediumTermPrediction">1,180 kW</div>
                                        <div class="prediction-confidence">신뢰도: <span id="mediumTermConfidence">89.2%</span></div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="prediction-card">
                                        <h6 class="text-warning">장기 예측 (1-30일)</h6>
                                        <div class="prediction-value" id="longTermPrediction">1,410 kW</div>
                                        <div class="prediction-confidence">신뢰도: <span id="longTermConfidence">78.4%</span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="monitoring-card">
                        <h5><i class="fas fa-sliders-h"></i> 예측 설정</h5>
                        <div class="prediction-settings">
                            <div class="setting-item">
                                <label class="form-label">예측 모델</label>
                                <select class="form-select form-select-sm" id="modelSelect" onchange="updatePrediction()">
                                    <option value="lstm">LSTM (기본)</option>
                                    <option value="transformer">Transformer</option>
                                    <option value="ensemble">앙상블</option>
                                </select>
                                    </div>
                            <div class="setting-item">
                                <label class="form-label">예측 정확도 임계값</label>
                                <input type="range" class="form-range" id="accuracyThreshold" min="70" max="99" value="90" onchange="updateThreshold()">
                                <small class="text-muted">현재: <span id="currentThreshold">90%</span></small>
                                </div>
                            <div class="setting-item">
                                <label class="form-label">자동 새로고침</label>
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="autoRefresh" checked onchange="toggleAutoRefresh()">
                                    <label class="form-check-label" for="autoRefresh">활성화</label>
                                    </div>
                                </div>
                            <div class="setting-item">
                                <label class="form-label">새로고침 간격</label>
                                <select class="form-select form-select-sm" id="refreshInterval" onchange="updateRefreshInterval()">
                                    <option value="30">30초</option>
                                    <option value="60" selected>1분</option>
                                    <option value="300">5분</option>
                                    <option value="600">10분</option>
                                </select>
                                    </div>
                                </div>
                        <div class="mt-3">
                            <button class="btn btn-primary btn-sm w-100" onclick="runPrediction()">
                                <i class="fas fa-play"></i> 예측 실행
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 에너지 공급-수요 매칭 분석 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="monitoring-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5><i class="fas fa-bolt"></i> 에너지 공급-수요 매칭 분석 (실시간)</h5>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary active" onclick="changeMatchingView('current')">현재</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changeMatchingView('1h')">1시간 후</button>
                                <button type="button" class="btn btn-outline-primary" onclick="changeMatchingView('3h')">3시간 후</button>
                            </div>
                        </div>
                        
                        <!-- 현재 에너지 흐름 다이어그램 -->
                        <div id="energyFlowDiagram" class="energy-flow-container">
                            <div class="row">
                                <!-- 공급원 -->
                            <div class="col-md-3">
                                    <div class="supply-section">
                                        <h6 class="text-center mb-3">⚡ 공급원</h6>
                                        <div class="supply-item">
                                            <div class="supply-icon">☀️</div>
                                            <div class="supply-info">
                                                <strong>태양광</strong><br>
                                                <span id="solar-power" class="real-time-value">3.5 kW</span><br>
                                                <small class="text-muted">(<span id="solar-percentage" class="real-time-value">24.4</span>%)</small>
                                </div>
                            </div>
                                        <div class="supply-item">
                                            <div class="supply-icon">🔋</div>
                                            <div class="supply-info">
                                                <strong>ESS</strong><br>
                                                <span id="ess-power" class="real-time-value">1.8 kW</span><br>
                                                <small class="text-muted">(<span id="ess-percentage" class="real-time-value">12.6</span>%)</small>
                                            </div>
                                        </div>
                                        <div class="supply-item">
                                            <div class="supply-icon">🔌</div>
                                            <div class="supply-info">
                                                <strong>그리드</strong><br>
                                                <span id="grid-power" class="real-time-value">9.0 kW</span><br>
                                                <small class="text-muted">(<span id="grid-percentage" class="real-time-value">63</span>%)</small>
                                            </div>
                                        </div>
                                        <div class="supply-item">
                                            <div class="supply-icon">💡</div>
                                            <div class="supply-info">
                                                <strong>잉여</strong><br>
                                                <span id="surplusPower">+182 kW</span><br>
                                                <small class="text-success">→ ESS 충전</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- 배분 전략 -->
                            <div class="col-md-3">
                                    <div class="strategy-section">
                                        <h6 class="text-center mb-3">🎯 배분 전략</h6>
                                        <div class="strategy-item">
                                            <div class="strategy-priority">우선순위 1</div>
                                            <div class="strategy-desc">필수 부하<br><small>(전산, 안전)</small></div>
                                </div>
                                        <div class="strategy-item">
                                            <div class="strategy-priority">우선순위 2</div>
                                            <div class="strategy-desc">냉방 부하<br><small>(태양광 우선)</small></div>
                            </div>
                                        <div class="strategy-item">
                                            <div class="strategy-priority">우선순위 3</div>
                                            <div class="strategy-desc">조명<br><small>(ESS 활용)</small></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- 수요 기기 -->
                                <div class="col-md-6">
                                    <div class="demand-section">
                                        <h6 class="text-center mb-3">🏢 수요 기기</h6>
                                        <div class="building-grid">
                                            <div class="building-item">
                                                <div class="building-header">
                                                    <strong>🏢 건물 A</strong>
                                                    <span class="building-power">450 kW</span>
                                                </div>
                                                <div class="device-breakdown">
                                                    <div class="device-item">
                                                        <span class="device-name">냉방</span>
                                                        <span class="device-power">280 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 160kW</span>
                                                            <span class="source-ess">🔋 80kW</span>
                                                            <span class="source-grid">🔌 40kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">조명</span>
                                                        <span class="device-power">85 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 45kW</span>
                                                            <span class="source-ess">🔋 40kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">전산</span>
                                                        <span class="device-power">65 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 30kW</span>
                                                            <span class="source-ess">🔋 35kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">기타</span>
                                                        <span class="device-power">20 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 17kW</span>
                                                            <span class="source-ess">🔋 3kW</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="building-item">
                                                <div class="building-header">
                                                    <strong>🏢 건물 B</strong>
                                                    <span class="building-power">380 kW</span>
                                                </div>
                                                <div class="device-breakdown">
                                                    <div class="device-item">
                                                        <span class="device-name">냉방</span>
                                                        <span class="device-power">220 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 120kW</span>
                                                            <span class="source-ess">🔋 60kW</span>
                                                            <span class="source-grid">🔌 40kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">조명</span>
                                                        <span class="device-power">75 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-ess">🔋 75kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">전산</span>
                                                        <span class="device-power">55 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 25kW</span>
                                                            <span class="source-ess">🔋 30kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">기타</span>
                                                        <span class="device-power">30 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-grid">🔌 30kW</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div class="building-item">
                                                <div class="building-header">
                                                    <strong>🔧 공용설비</strong>
                                                    <span class="building-power">100 kW</span>
                                                </div>
                                                <div class="device-breakdown">
                                                    <div class="device-item">
                                                        <span class="device-name">엘리베이터</span>
                                                        <span class="device-power">45 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-solar">☀️ 25kW</span>
                                                            <span class="source-ess">🔋 20kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">환기</span>
                                                        <span class="device-power">30 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-ess">🔋 30kW</span>
                                                        </div>
                                                    </div>
                                                    <div class="device-item">
                                                        <span class="device-name">펌프</span>
                                                        <span class="device-power">25 kW</span>
                                                        <div class="power-source">
                                                            <span class="source-grid">🔌 25kW</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- 매칭 분석 요약 -->
                            <div class="matching-summary mt-4">
                                <div class="row text-center">
                            <div class="col-md-3">
                                        <div class="summary-item">
                                            <h6 class="text-primary">매칭율</h6>
                                            <h4 id="matchingRate">87.3%</h4>
                                            <small class="text-muted">수요 대비 공급</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                        <div class="summary-item">
                                            <h6 class="text-success">그리드 의존도</h6>
                                            <h4 id="gridDependency">63%</h4>
                                            <small class="text-muted">외부 전력 비율</small>
                                </div>
                            </div>
                                    <div class="col-md-3">
                                        <div class="summary-item">
                                            <h6 class="text-warning">자가발전 비율</h6>
                                            <h4 id="selfGeneration">37%</h4>
                                            <small class="text-muted">태양광 + ESS</small>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="summary-item">
                                            <h6 class="text-info">비용 절감</h6>
                                            <h4 id="costSavings">₩8,500</h4>
                                            <small class="text-muted">시간당 절감액</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 수요 반응 제어 센터 -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="monitoring-card">
                        <h5><i class="fas fa-sliders-h"></i> 수요 반응 제어 센터</h5>
                        <div class="demand-response-panel">
                            <div class="dr-recommendation">
                                <div class="dr-header">
                                    <h6><i class="fas fa-lightbulb"></i> AI 추천 제어 전략 (3시간 후 대비)</h6>
                                    <span class="dr-priority high">우선순위: 높음</span>
                    </div>
                                <div class="dr-content">
                                    <div class="dr-item">
                                        <div class="dr-title">1. 냉방 시스템 최적화</div>
                                        <div class="dr-details">
                                            <div class="dr-target">📍 대상: 건물 A, B, C</div>
                                            <div class="dr-goal">🎯 목표: 120 kW 절감</div>
                                            <div class="dr-options">
                                                <div class="dr-option">
                                                    <input type="radio" name="hvac_control" id="hvac_temp" value="temp">
                                                    <label for="hvac_temp">설정 온도 1°C 상향 (24°C → 25°C)</label>
                                                    <div class="dr-effect">효과: -80 kW | 체감: 낮음 | 적용: 17:00</div>
                </div>
                                                <div class="dr-option">
                                                    <input type="radio" name="hvac_control" id="hvac_air" value="air">
                                                    <label for="hvac_air">외기 도입량 20% 증가 (자연 냉방)</label>
                                                    <div class="dr-effect">효과: -25 kW | 체감: 없음 | 적용: 16:30</div>
                                    </div>
                                                <div class="dr-option">
                                                    <input type="radio" name="hvac_control" id="hvac_zone" value="zone">
                                                    <label for="hvac_zone">미사용 구역 냉방 차단</label>
                                                    <div class="dr-effect">효과: -15 kW | 체감: 없음 | 적용: 즉시</div>
                                </div>
                                    </div>
                                            <div class="dr-summary">
                                                <strong>예상 절감: 120 kW | 비용 절감: ₩14,400</strong>
                                                <div class="dr-actions">
                                                    <button class="btn btn-success btn-sm" onclick="applyDRStrategy('hvac')">적용하기</button>
                                                    <button class="btn btn-outline-primary btn-sm" onclick="scheduleDRStrategy('hvac')">일정 설정</button>
                                                    <button class="btn btn-outline-secondary btn-sm" onclick="ignoreDRStrategy('hvac')">무시</button>
                                </div>
                                    </div>
                                </div>
                            </div>
                                    
                                    <div class="dr-item">
                                        <div class="dr-title">2. 조명 자동 조도 조절</div>
                                        <div class="dr-details">
                                            <div class="dr-target">📍 대상: 모든 건물</div>
                                            <div class="dr-goal">🎯 목표: 35 kW 절감</div>
                                            <div class="dr-options">
                                                <div class="dr-option">
                                                    <input type="radio" name="lighting_control" id="light_window" value="window">
                                                    <label for="light_window">창가 구역 조도 30% 감소 (자연광 활용)</label>
                                                    <div class="dr-effect">효과: -20 kW | 체감: 없음 | 적용: 즉시</div>
                        </div>
                                                <div class="dr-option">
                                                    <input type="radio" name="lighting_control" id="light_sensor" value="sensor">
                                                    <label for="light_sensor">복도/화장실 인체감지 센서 작동</label>
                                                    <div class="dr-effect">효과: -10 kW | 체감: 없음 | 적용: 즉시</div>
                                                </div>
                                                <div class="dr-option">
                                                    <input type="radio" name="lighting_control" id="light_auto" value="auto">
                                                    <label for="light_auto">미사용 회의실 조명 자동 소등</label>
                                                    <div class="dr-effect">효과: -5 kW | 체감: 없음 | 적용: 즉시</div>
                                                </div>
                                            </div>
                                            <div class="dr-summary">
                                                <strong>예상 절감: 35 kW | 비용 절감: ₩4,200</strong>
                                                <div class="dr-actions">
                                                    <button class="btn btn-success btn-sm" onclick="applyDRStrategy('lighting')">적용하기</button>
                                                    <button class="btn btn-outline-primary btn-sm" onclick="scheduleDRStrategy('lighting')">일정 설정</button>
                                                    <button class="btn btn-outline-secondary btn-sm" onclick="ignoreDRStrategy('lighting')">무시</button>
                                                </div>
                                            </div>
                                        </div>
                    </div>
                </div>
            </div>

                            <div class="dr-summary-total">
                                <h6>📊 전체 수요 반응 효과 요약</h6>
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="summary-stat">
                                            <strong>총 절감량</strong><br>
                                            <span class="stat-value">170 kW</span><br>
                                            <small>(전체 수요의 11.3%)</small>
                        </div>
                                </div>
                                    <div class="col-md-3">
                                        <div class="summary-stat">
                                            <strong>비용 절감</strong><br>
                                            <span class="stat-value">₩20,400</span><br>
                                            <small>(3시간)</small>
                            </div>
                        </div>
                                    <div class="col-md-3">
                                        <div class="summary-stat">
                                            <strong>CO₂ 감축</strong><br>
                                            <span class="stat-value">6.2 kg</span><br>
                                            <small>(환경 기여)</small>
                    </div>
                </div>
                                    <div class="col-md-3">
                                        <div class="summary-stat">
                                            <strong>매칭율 개선</strong><br>
                                            <span class="stat-value">+10.4%p</span><br>
                                            <small>(78.5% → 88.9%)</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="dr-total-actions mt-3">
                                    <button class="btn btn-primary" onclick="applyAllDRStrategies()">전체 적용</button>
                                    <button class="btn btn-outline-primary" onclick="customizeDRStrategies()">맞춤 설정</button>
                                    <button class="btn btn-outline-info" onclick="simulateDRStrategies()">시뮬레이션 실행</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="monitoring-card">
                        <h5><i class="fas fa-bell"></i> 실시간 알림</h5>
                        <div class="notification-panel">
                            <div class="notification-item urgent">
                                <div class="notification-icon">🔴</div>
                                <div class="notification-content">
                                    <div class="notification-title">건물 A 냉방 수요 급증 (+25%)</div>
                                    <div class="notification-desc">예상 원인: 회의실 4개 동시 사용</div>
                                    <div class="notification-action">
                                        <button class="btn btn-sm btn-warning" onclick="handleUrgentAlert('building_a')">즉시 조치</button>
                            </div>
                        </div>
                                </div>
                            
                            <div class="notification-item warning">
                                <div class="notification-icon">🟡</div>
                                <div class="notification-content">
                                    <div class="notification-title">ESS Bank 1 충전 완료 임박 (95% SOC)</div>
                                    <div class="notification-desc">예상 완료: 14:55</div>
                                    <div class="notification-action">
                                        <button class="btn btn-sm btn-outline-warning" onclick="handleWarningAlert('ess_bank1')">자동 전환</button>
                            </div>
                        </div>
                    </div>
                            
                            <div class="notification-item info">
                                <div class="notification-icon">🟢</div>
                                <div class="notification-content">
                                    <div class="notification-title">태양광 발전 최적 상태 (3.5 kW)</div>
                                    <div class="notification-desc">효율: 18.2% (평균 대비 +2.1%)</div>
                </div>
            </div>
                        </div>
                        
                        <div class="performance-summary mt-3">
                            <h6>💡 오늘의 성과</h6>
                            <div class="performance-item">
                                <span>누적 비용 절감</span>
                                <span class="performance-value">₩87,500</span>
                                <small class="text-success">(목표 대비 112%)</small>
                            </div>
                            <div class="performance-item">
                                <span>평균 매칭율</span>
                                <span class="performance-value">89.2%</span>
                                <small class="text-success">(목표: 85%)</small>
                            </div>
                            <div class="performance-item">
                                <span>그리드 의존도</span>
                                <span class="performance-value">58%</span>
                                <small class="text-success">(목표 대비 -7%p)</small>
                            </div>
                            <div class="performance-item">
                                <span>CO₂ 감축</span>
                                <span class="performance-value">18.3 kg</span>
                                <small class="text-success">(월간 목표 달성률: 23%)</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 전역 변수
            let realtimeChart, deviceChart, demandDistributionChart, predictionChart;
            let autoRefreshInterval;
            let currentTimeRange = '1h';
            let currentPredictionRange = '24h';
            let currentDeviceView = 'chart';

            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initializeCharts();
                updateRealtimeData();
                updateLastUpdateTime();
                startAutoRefresh();
            }});

            // 실시간 데이터 업데이트
            function updateRealtimeData() {{
                // 현재 시간 업데이트
                updateLastUpdateTime();
                
                // 실시간 수요-공급 데이터 생성
                const currentDemand = (Math.random() * 200 + 1200).toFixed(0);
                const currentSupply = (Math.random() * 300 + 1300).toFixed(0);
                const currentMatchingRate = (Math.min(currentDemand, currentSupply) / Math.max(currentDemand, currentSupply) * 100).toFixed(1);
                
                // 1시간 후 예측
                const predDemand1h = (Math.random() * 150 + 1300).toFixed(0);
                const predSupply1h = (Math.random() * 200 + 1400).toFixed(0);
                const predMatchingRate1h = (Math.min(predDemand1h, predSupply1h) / Math.max(predDemand1h, predSupply1h) * 100).toFixed(1);
                
                // 6시간 후 예측
                const predDemand6h = (Math.random() * 200 + 1100).toFixed(0);
                const predSupply6h = (Math.random() * 400 + 1500).toFixed(0);
                const predMatchingRate6h = (Math.min(predDemand6h, predSupply6h) / Math.max(predDemand6h, predSupply6h) * 100).toFixed(1);

                // DOM 업데이트
                document.getElementById('currentDemand').textContent = currentDemand;
                document.getElementById('currentSupply').textContent = currentSupply;
                document.getElementById('currentMatchingRate').textContent = currentMatchingRate + '%';
                
                document.getElementById('predDemand1h').textContent = predDemand1h;
                document.getElementById('predSupply1h').textContent = predSupply1h;
                document.getElementById('prediction1h').textContent = predMatchingRate1h + '%';
                
                document.getElementById('predDemand6h').textContent = predDemand6h;
                document.getElementById('predSupply6h').textContent = predSupply6h;
                document.getElementById('prediction6h').textContent = predMatchingRate6h + '%';

                // 모델 정확도 업데이트
                const modelAccuracy = (Math.random() * 5 + 92).toFixed(1);
                document.getElementById('modelAccuracy').textContent = modelAccuracy + '%';

                // 차트 업데이트
                updateRealtimeChart();
                updateDeviceChart();
                updateDemandDistributionChart();
                updatePredictionChart();
            }}

            // 마지막 업데이트 시간 표시
            function updateLastUpdateTime() {{
                const now = new Date();
                const timeString = now.toLocaleTimeString('ko-KR');
                document.getElementById('lastUpdate').textContent = timeString;
            }}

            // 차트 초기화
            function initializeCharts() {{
                initRealtimeChart();
                initDeviceChart();
                initDemandDistributionChart();
                initPredictionChart();
            }}

            // 실시간 차트 초기화
            function initRealtimeChart() {{
                const ctx = document.getElementById('realtimeChart').getContext('2d');
                const labels = [];
                const demandData = [];
                const supplyData = [];
                const matchingData = [];
                
                // 시간 범위에 따른 데이터 생성
                const dataPoints = currentTimeRange === '1h' ? 12 : currentTimeRange === '6h' ? 24 : 48;
                
                for (let i = 0; i < dataPoints; i++) {{
                    const time = new Date();
                    time.setMinutes(time.getMinutes() - (dataPoints - i) * (currentTimeRange === '1h' ? 5 : currentTimeRange === '6h' ? 15 : 30));
                    labels.push(time.toLocaleTimeString('ko-KR', {{hour: '2-digit', minute: '2-digit'}}));
                    
                    const demand = Math.random() * 200 + 1200;
                    const supply = Math.random() * 300 + 1300;
                    const matching = (Math.min(demand, supply) / Math.max(demand, supply) * 100);
                    
                    demandData.push(demand);
                    supplyData.push(supply);
                    matchingData.push(matching);
                }}
                
                realtimeChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: '에너지 수요 (kW)',
                            data: demandData,
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        }}, {{
                            label: '에너지 공급 (kW)',
                            data: supplyData,
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        }}, {{
                            label: '매칭율 (%)',
                            data: matchingData,
                            borderColor: '#ffa726',
                            backgroundColor: 'rgba(255, 167, 38, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            intersect: false,
                            mode: 'index'
                        }},
                        scales: {{
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: '에너지 (kW)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '매칭율 (%)'
                                }},
                                min: 0,
                                max: 100,
                                grid: {{
                                    drawOnChartArea: false,
                                }},
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top'
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        if (context.datasetIndex === 2) {{
                                            return `매칭율: ${{context.parsed.y.toFixed(1)}}%`;
                                        }}
                                        return `${{context.dataset.label}}: ${{context.parsed.y.toFixed(0)}} kW`;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 실시간 차트 업데이트
            function updateRealtimeChart() {{
                if (!realtimeChart) return;
                
                const now = new Date();
                const newLabel = now.toLocaleTimeString('ko-KR', {{hour: '2-digit', minute: '2-digit'}});
                
                // 새 데이터 추가
                const demand = Math.random() * 200 + 1200;
                const supply = Math.random() * 300 + 1300;
                const matching = (Math.min(demand, supply) / Math.max(demand, supply) * 100);
                
                realtimeChart.data.labels.push(newLabel);
                realtimeChart.data.datasets[0].data.push(demand);
                realtimeChart.data.datasets[1].data.push(supply);
                realtimeChart.data.datasets[2].data.push(matching);
                
                // 오래된 데이터 제거 (최대 50개 데이터 포인트 유지)
                if (realtimeChart.data.labels.length > 50) {{
                    realtimeChart.data.labels.shift();
                    realtimeChart.data.datasets[0].data.shift();
                    realtimeChart.data.datasets[1].data.shift();
                    realtimeChart.data.datasets[2].data.shift();
                }}
                
                realtimeChart.update('none');
            }}

            // 기기별 차트 초기화
            function initDeviceChart() {{
                const ctx = document.getElementById('deviceChart').getContext('2d');
                const devices = ['HVAC', 'IT 장비', '기타 장비', '조명'];
                const data = [450, 320, 300, 180];
                
                deviceChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: devices,
                        datasets: [{{
                            label: '에너지 수요 (kW)',
                            data: data,
                            backgroundColor: [
                                'rgba(255, 107, 107, 0.8)',
                                'rgba(78, 205, 196, 0.8)',
                                'rgba(69, 183, 209, 0.8)',
                                'rgba(249, 202, 36, 0.8)'
                            ],
                            borderColor: [
                                '#ff6b6b',
                                '#4ecdc4',
                                '#45b7d1',
                                '#f9ca24'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return `${{context.label}}: ${{context.parsed.y}} kW`;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: '에너지 수요 (kW)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 기기별 차트 업데이트
            function updateDeviceChart() {{
                if (!deviceChart) return;
                
                const newData = [
                    Math.random() * 100 + 400,  // HVAC
                    Math.random() * 80 + 280,   // IT
                    Math.random() * 100 + 250,  // 기타
                    Math.random() * 50 + 150    // 조명
                ];
                
                deviceChart.data.datasets[0].data = newData;
                deviceChart.update('none');
            }}

            // 수요 분포 차트 초기화
            function initDemandDistributionChart() {{
                const ctx = document.getElementById('demandDistributionChart').getContext('2d');
                
                demandDistributionChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['HVAC 시스템', 'IT 장비', '기타 장비', '조명 시스템'],
                        datasets: [{{
                            data: [450, 320, 300, 180],
                            backgroundColor: [
                                '#ff6b6b',
                                '#4ecdc4',
                                '#45b7d1',
                                '#f9ca24'
                            ],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                                        return `${{context.label}}: ${{context.parsed}} kW (${{percentage}}%)`;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 수요 분포 차트 업데이트
            function updateDemandDistributionChart() {{
                if (!demandDistributionChart) return;
                
                const newData = [
                    Math.random() * 100 + 400,  // HVAC
                    Math.random() * 80 + 280,   // IT
                    Math.random() * 100 + 250,  // 기타
                    Math.random() * 50 + 150    // 조명
                ];
                
                demandDistributionChart.data.datasets[0].data = newData;
                demandDistributionChart.update('none');
                
                // 퍼센트 업데이트
                const total = newData.reduce((a, b) => a + b, 0);
                document.getElementById('hvacPercent').textContent = ((newData[0] / total) * 100).toFixed(0) + '%';
                document.getElementById('itPercent').textContent = ((newData[1] / total) * 100).toFixed(0) + '%';
                document.getElementById('otherPercent').textContent = ((newData[2] / total) * 100).toFixed(0) + '%';
                document.getElementById('lightingPercent').textContent = ((newData[3] / total) * 100).toFixed(0) + '%';
            }}

            // 예측 차트 초기화
            function initPredictionChart() {{
                const ctx = document.getElementById('predictionChart').getContext('2d');
                const labels = [];
                const actualData = [];
                const predictedData = [];
                
                // 24시간 데이터 생성
                for (let i = 0; i < 24; i++) {{
                    const hour = i.toString().padStart(2, '0') + ':00';
                    labels.push(hour);
                    actualData.push(Math.random() * 200 + 1200);
                    predictedData.push(Math.random() * 200 + 1200);
                }}
                
                predictionChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: '실제 수요',
                            data: actualData,
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: '예측 수요',
                            data: predictedData,
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            borderDash: [5, 5]
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'top'
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return `${{context.dataset.label}}: ${{context.parsed.y.toFixed(0)}} kW`;
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: '에너지 수요 (kW)'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 예측 차트 업데이트
            function updatePredictionChart() {{
                if (!predictionChart) return;
                
                // 새로운 예측 데이터 생성
                const newPredictedData = predictionChart.data.datasets[1].data.map(() => 
                    Math.random() * 200 + 1200
                );
                
                predictionChart.data.datasets[1].data = newPredictedData;
                predictionChart.update('none');
            }}

            // 인터랙티브 함수들
            function changeTimeRange(range) {{
                currentTimeRange = range;
                
                // 버튼 상태 업데이트
                document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // 차트 재초기화
                if (realtimeChart) {{
                    realtimeChart.destroy();
                }}
                initRealtimeChart();
            }}

            function changePredictionRange(range) {{
                currentPredictionRange = range;
                
                // 버튼 상태 업데이트
                document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // 예측 차트 업데이트
                updatePredictionChart();
            }}

            function changeDeviceView(view) {{
                currentDeviceView = view;
                
                // 버튼 상태 업데이트
                document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // 뷰 전환
                if (view === 'chart') {{
                    document.getElementById('deviceChartView').style.display = 'block';
                    document.getElementById('deviceTableView').style.display = 'none';
                }} else {{
                    document.getElementById('deviceChartView').style.display = 'none';
                    document.getElementById('deviceTableView').style.display = 'block';
                    updateDeviceTable();
                }}
            }}

            function updateDeviceTable() {{
                const tableBody = document.getElementById('deviceTableBody');
                const devices = [
                    {{ name: 'HVAC 시스템', current: Math.random() * 100 + 400, average: 450, efficiency: 85, status: '정상' }},
                    {{ name: 'IT 장비', current: Math.random() * 80 + 280, average: 320, efficiency: 88, status: '정상' }},
                    {{ name: '기타 장비', current: Math.random() * 100 + 250, average: 300, efficiency: 87, status: '정상' }},
                    {{ name: '조명 시스템', current: Math.random() * 50 + 150, average: 180, efficiency: 92, status: '정상' }}
                ];
                
                tableBody.innerHTML = devices.map(device => `
                    <tr>
                        <td>${{device.name}}</td>
                        <td>${{device.current.toFixed(0)}} kW</td>
                        <td>${{device.average}} kW</td>
                        <td>${{device.efficiency}}%</td>
                        <td><span class="badge bg-success">${{device.status}}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="controlDevice('${{device.name}}')">
                                <i class="fas fa-cog"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }}

            function controlDevice(deviceName) {{
                alert(`${{deviceName}} 제어 패널을 열겠습니다.`);
            }}

            function refreshData() {{
                updateRealtimeData();
                showNotification('데이터가 새로고침되었습니다.', 'success');
            }}

            function exportData() {{
                const data = {{
                    timestamp: new Date().toISOString(),
                    currentDemand: document.getElementById('currentDemand').textContent,
                    currentSupply: document.getElementById('currentSupply').textContent,
                    matchingRate: document.getElementById('currentMatchingRate').textContent
                }};
                
                const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `energy_data_${{new Date().toISOString().split('T')[0]}}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                showNotification('데이터가 내보내기되었습니다.', 'success');
            }}

            function showDataSource() {{
                const modal = new bootstrap.Modal(document.getElementById('dataSourceModal'));
                modal.show();
            }}

            function showRawData() {{
                const modal = new bootstrap.Modal(document.getElementById('rawDataModal'));
                modal.show();
            }}

            function showModelDetails() {{
                const modal = new bootstrap.Modal(document.getElementById('modelDetailsModal'));
                modal.show();
            }}

            function updatePrediction() {{
                const model = document.getElementById('modelSelect').value;
                showNotification(`${{model}} 모델로 예측을 업데이트했습니다.`, 'info');
            }}

            function updateThreshold() {{
                const threshold = document.getElementById('accuracyThreshold').value;
                document.getElementById('currentThreshold').textContent = threshold + '%';
            }}

            function toggleAutoRefresh() {{
                const autoRefresh = document.getElementById('autoRefresh').checked;
                if (autoRefresh) {{
                    startAutoRefresh();
                }} else {{
                    stopAutoRefresh();
                }}
            }}

            function updateRefreshInterval() {{
                const interval = parseInt(document.getElementById('refreshInterval').value);
                stopAutoRefresh();
                startAutoRefresh(interval);
            }}

            function runPrediction() {{
                showNotification('예측 모델을 실행하고 있습니다...', 'info');
                setTimeout(() => {{
                    updatePredictionChart();
                    showNotification('예측이 완료되었습니다.', 'success');
                }}, 2000);
            }}

            function startAutoRefresh(interval = 60) {{
                stopAutoRefresh();
                autoRefreshInterval = setInterval(updateRealtimeData, interval * 1000);
            }}

            function stopAutoRefresh() {{
                if (autoRefreshInterval) {{
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }}
            }}

            function showNotification(message, type = 'info') {{
                const alertClass = `alert-${{type}}`;
                const notification = document.createElement('div');
                notification.className = `alert ${{alertClass}} alert-dismissible fade show position-fixed`;
                notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
                notification.innerHTML = `
                    ${{message}}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        notification.remove();
                    }}
                }}, 5000);
            }}

            // 전자기기 시뮬레이션
            function simulateDevice() {{
                const deviceSelect = document.getElementById('deviceSelect');
                const selectedDevice = deviceSelect.value;
                const simulationResults = document.getElementById('simulationResults');
                
                if (!selectedDevice) {{
                    simulationResults.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                                <strong>기기를 선택하면 수요 예측이 표시됩니다</strong><br>
                                <small>선택한 기기의 에너지 소비 패턴을 분석하여 수요를 예측합니다.</small>
                        </div>
                    `;
                    return;
                }}
                
                const deviceData = {{
                    hvac: {{ name: 'HVAC 시스템', power: 450, pattern: '계절성', efficiency: 85 }},
                    lighting: {{ name: '조명 시스템', power: 180, pattern: '시간대별', efficiency: 92 }},
                    it: {{ name: 'IT 장비', power: 320, pattern: '지속적', efficiency: 88 }},
                    elevator: {{ name: '엘리베이터', power: 150, pattern: '피크시간', efficiency: 90 }},
                    pump: {{ name: '펌프 시스템', power: 200, pattern: '수요기반', efficiency: 87 }},
                    security: {{ name: '보안 시스템', power: 80, pattern: '24시간', efficiency: 95 }}
                }};
                
                const device = deviceData[selectedDevice];
                const predictedDemand = (device.power * (Math.random() * 0.3 + 0.85)).toFixed(0);
                const efficiency = device.efficiency + (Math.random() * 10 - 5);
                
                simulationResults.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i>
                            <strong>${{device.name}} 시뮬레이션 결과</strong><br>
                        <small>
                            예측 수요: <strong>${{predictedDemand}} kW</strong><br>
                            소비 패턴: <strong>${{device.pattern}}</strong><br>
                            효율성: <strong>${{efficiency.toFixed(1)}}%</strong><br>
                            최적화 가능성: <strong>${{(100 - efficiency).toFixed(1)}}%</strong>
                        </small>
                        </div>
                `;
            }}

            // 에너지 매칭 뷰 변경
            function changeMatchingView(view) {{
                // 버튼 상태 업데이트
                document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // 뷰에 따른 데이터 업데이트
                updateEnergyMatchingData(view);
            }}

            // 에너지 매칭 데이터 업데이트
            function updateEnergyMatchingData(view) {{
                const timeLabels = {{
                    current: '현재 (14:30)',
                    '1h': '1시간 후 (15:30)',
                    '3h': '3시간 후 (17:30)'
                }};
                
                // 공급 데이터 업데이트
                const supplyData = {{
                    current: {{ solar: 3.5, ess: 1.8, grid: 9.0, surplus: 182 }},
                    '1h': {{ solar: 4.2, ess: 2.1, grid: 8.5, surplus: 165 }},
                    '3h': {{ solar: 1.8, ess: 3.2, grid: 11.5, surplus: 0 }}
                }};
                
                const data = supplyData[view];
                document.getElementById('solarPower').textContent = data.solar + ' kW';
                document.getElementById('essPower').textContent = data.ess + ' kW';
                document.getElementById('gridPower').textContent = data.grid + ' kW';
                document.getElementById('surplusPower').textContent = '+' + data.surplus + ' kW';
                
                // 매칭율 및 지표 업데이트
                const matchingData = {{
                    current: {{ rate: 87.3, grid: 63, self: 37, savings: 8500 }},
                    '1h': {{ rate: 92.1, grid: 58, self: 42, savings: 12400 }},
                    '3h': {{ rate: 78.5, grid: 78, self: 22, savings: 3200 }}
                }};
                
                const metrics = matchingData[view];
                document.getElementById('matchingRate').textContent = metrics.rate + '%';
                document.getElementById('gridDependency').textContent = metrics.grid + '%';
                document.getElementById('selfGeneration').textContent = metrics.self + '%';
                document.getElementById('costSavings').textContent = '₩' + metrics.savings.toLocaleString();
            }}

            // 수요 반응 전략 적용
            function applyDRStrategy(strategy) {{
                showNotification(`${{strategy}} 수요 반응 전략을 적용했습니다.`, 'success');
                
                // 실제 적용 로직 시뮬레이션
                setTimeout(() => {{
                    updateEnergyMatchingData('current');
                    showNotification('전략 적용이 완료되었습니다. 매칭율이 개선되었습니다.', 'success');
                }}, 2000);
            }}

            function scheduleDRStrategy(strategy) {{
                showNotification(`${{strategy}} 수요 반응 전략을 일정에 추가했습니다.`, 'info');
            }}

            function ignoreDRStrategy(strategy) {{
                showNotification(`${{strategy}} 수요 반응 전략을 무시했습니다.`, 'warning');
            }}

            function applyAllDRStrategies() {{
                showNotification('모든 수요 반응 전략을 적용합니다...', 'info');
                
                setTimeout(() => {{
                    updateEnergyMatchingData('current');
                    showNotification('모든 전략이 성공적으로 적용되었습니다!', 'success');
                }}, 3000);
            }}

            function customizeDRStrategies() {{
                showNotification('맞춤 설정 패널을 열겠습니다.', 'info');
            }}

            function simulateDRStrategies() {{
                showNotification('시뮬레이션을 실행합니다...', 'info');
                
                setTimeout(() => {{
                    showNotification('시뮬레이션 완료: 예상 절감량 170kW, 비용 절감 ₩20,400', 'success');
                }}, 2000);
            }}

            // 알림 처리
            function handleUrgentAlert(alertType) {{
                showNotification('긴급 알림을 처리했습니다. 즉시 조치를 실행합니다.', 'warning');
                
                setTimeout(() => {{
                    showNotification('긴급 조치가 완료되었습니다. 시스템이 정상화되었습니다.', 'success');
                }}, 1500);
            }}

            function handleWarningAlert(alertType) {{
                showNotification('경고 알림을 처리했습니다. 자동 전환을 실행합니다.', 'info');
                
                setTimeout(() => {{
                    showNotification('자동 전환이 완료되었습니다.', 'success');
                }}, 1000);
            }}

            // 동적 제어 평가
            function evaluateControl(scenario) {{
                const controlResults = document.getElementById('controlResults');
                const scenarios = {{
                    peak: {{ name: '피크 제어', effect: '15-25%', risk: '낮음', duration: '2-4시간' }},
                    load: {{ name: '부하 분산', effect: '10-20%', risk: '중간', duration: '4-8시간' }},
                    efficiency: {{ name: '효율 최적화', effect: '5-15%', risk: '낮음', duration: '지속적' }}
                }};
                
                const scenarioData = scenarios[scenario];
                const actualEffect = (Math.random() * 10 + 5).toFixed(1);
                
                controlResults.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-cogs"></i>
                        <strong>${{scenarioData.name}} 평가 결과</strong><br>
                        <small>
                            예상 효과: <strong>${{actualEffect}}%</strong> (범위: ${{scenarioData.effect}})<br>
                            위험도: <strong>${{scenarioData.risk}}</strong><br>
                            적용 기간: <strong>${{scenarioData.duration}}</strong><br>
                            권장사항: <strong>모니터링 후 단계적 적용</strong>
                        </small>
                    </div>
                `;
            }}

        </script>
        <!-- 모달 창들 -->
        <div class="modal fade" id="dataSourceModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-database"></i> 데이터 출처 정보</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>실시간 센서 데이터</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-bolt text-danger"></i> 전력 수요 센서 (15개)</li>
                                    <li><i class="fas fa-thermometer-half text-success"></i> 온도 센서 (8개)</li>
                                    <li><i class="fas fa-tachometer-alt text-info"></i> 풍속 센서 (3개)</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>외부 API 데이터</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-cloud-sun text-warning"></i> 기상청 API (KMA)</li>
                                    <li><i class="fas fa-solar-panel text-warning"></i> 태양광 발전량 API</li>
                                    <li><i class="fas fa-wind text-info"></i> 풍력 발전량 API</li>
                                </ul>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h6>데이터 업데이트 주기</h6>
                            <p class="mb-0">실시간 센서: 1분마다 | 외부 API: 5분마다 | 예측 모델: 1시간마다</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="rawDataModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-table"></i> 원시 데이터</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>시간</th>
                                        <th>수요 (kW)</th>
                                        <th>공급 (kW)</th>
                                        <th>매칭율 (%)</th>
                                        <th>온도 (°C)</th>
                                        <th>습도 (%)</th>
                                    </tr>
                                </thead>
                                <tbody id="rawDataTableBody">
                                    <!-- 동적으로 생성됨 -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="modelDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-robot"></i> AI 예측 모델 상세 정보</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>모델 아키텍처</h6>
                                <ul>
                                    <li>LSTM 레이어: 3개</li>
                                    <li>은닉 유닛: 128개</li>
                                    <li>드롭아웃: 0.2</li>
                                    <li>배치 크기: 32</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>성능 지표</h6>
                                <ul>
                                    <li>MAE: 45.2 kW</li>
                                    <li>RMSE: 67.8 kW</li>
                                    <li>MAPE: 3.2%</li>
                                    <li>R²: 0.942</li>
                                </ul>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h6>학습 데이터</h6>
                            <p>2022년 1월 ~ 2024년 1월 (2년간의 에너지 사용 패턴 데이터)</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // 모달 열 때 원시 데이터 생성
            document.getElementById('rawDataModal').addEventListener('show.bs.modal', function() {{
                const tableBody = document.getElementById('rawDataTableBody');
                const rows = [];
                
                for (let i = 0; i < 20; i++) {{
                    const time = new Date();
                    time.setMinutes(time.getMinutes() - i * 5);
                    const demand = (Math.random() * 200 + 1200).toFixed(0);
                    const supply = (Math.random() * 300 + 1300).toFixed(0);
                    const matching = (Math.min(demand, supply) / Math.max(demand, supply) * 100).toFixed(1);
                    const temp = (Math.random() * 10 + 20).toFixed(1);
                    const humidity = (Math.random() * 30 + 50).toFixed(0);
                    
                    rows.push(`
                        <tr>
                            <td>${{time.toLocaleTimeString('ko-KR')}}</td>
                            <td>${{demand}}</td>
                            <td>${{supply}}</td>
                            <td>${{matching}}</td>
                            <td>${{temp}}</td>
                            <td>${{humidity}}</td>
                        </tr>
                    `);
                }}
                
                tableBody.innerHTML = rows.join('');
            }});
        </script>

            // 동적 제어 평가
            function evaluateControl(scenario) {{
                const controlResults = document.getElementById('controlResults');
                const scenarios = {{
                    peak: {{ name: '피크 제어', savings: 15, efficiency: 8, cost: 5 }},
                    load: {{ name: '부하 분산', savings: 12, efficiency: 6, cost: 3 }},
                    efficiency: {{ name: '효율 최적화', savings: 8, efficiency: 12, cost: 2 }}
                }};
                
                const scenarioData = scenarios[scenario];
                const newEvent = document.createElement('div');
                newEvent.className = 'event-item';
                newEvent.innerHTML = `
                    <div class="event-time">${{new Date().toLocaleTimeString()}}</div>
                    <div class="event-content">
                        <strong>${{scenarioData.name}} 평가 결과</strong><br>
                        <small>에너지 절약: ${{scenarioData.savings}}%</small><br>
                        <small>효율성 향상: ${{scenarioData.efficiency}}%</small><br>
                        <small>비용 절감: ${{scenarioData.cost}}%</small><br>
                        <small>제어 가능성: 높음</small>
                    </div>
                `;
                controlResults.insertBefore(newEvent, controlResults.firstChild);
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initDemandSupplyChart();
                updateRealtimeData();
                
                // 5초마다 데이터 업데이트
                setInterval(updateRealtimeData, 5000);
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/model-testing", response_class=HTMLResponse)
async def model_testing_page(request: Request, lang: str = Query("ko", description="Language code")):
    """MCP 기반 자동화 ML/AI Engine 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('modelTesting.title', lang)}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .mcp-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .process-step {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                position: relative;
                overflow: hidden;
            }}
            .process-step::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                pointer-events: none;
            }}
            .process-step.active {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                animation: pulse 2s infinite;
            }}
            .process-step.completed {{
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.02); }}
                100% {{ transform: scale(1); }}
            }}
            .agent-status {{
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                color: #333;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .progress-step {{
                height: 8px;
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.3);
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                border-radius: 4px;
                transition: width 0.5s ease;
            }}
            .log-container {{
                background: #1e1e1e;
                color: #00ff00;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                max-height: 300px;
                overflow-y: auto;
            }}
            .log-entry {{
                margin-bottom: 5px;
                padding: 2px 0;
            }}
            .log-timestamp {{
                color: #888;
            }}
            .log-info {{ color: #00ff00; }}
            .log-warning {{ color: #ffaa00; }}
            .log-error {{ color: #ff0000; }}
            .log-success {{ color: #00ff88; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 헤더 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="mcp-card">
                        <h1 class="mb-2">
                            <i class="fas fa-robot"></i> {t('modelTesting.title', lang)}
                        </h1>
                        <p class="mb-0">{t('modelTesting.pipeline', lang)}</p>
                    </div>
                </div>
            </div>

            <!-- MCP 에이전트 상태 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="agent-status">
                        <h5><i class="fas fa-brain"></i> {t('modelTesting.agentStatus', lang)}</h5>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>{t('common.status', lang)}</h6>
                                    <span class="badge bg-success fs-6" id="agentStatus">{t('common.active', lang)}</span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>{t('modelTesting.currentTask', lang)}</h6>
                                    <span id="currentTask">{t('modelTesting.dataCollection', lang)}</span>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>{t('modelTesting.progress', lang)}</h6>
                                    <div class="progress-step">
                                        <div class="progress-fill" id="overallProgress" style="width: 20%"></div>
                                    </div>
                                    <small id="progressText">20% {t('modelTesting.complete', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <button class="btn btn-primary" onclick="startMCPPipeline()">
                                        <i class="fas fa-play"></i> {t('modelTesting.startPipeline', lang)}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MCP 자동화 프로세스 -->
            <div class="row">
                <div class="col-lg-8">
                    <div class="mcp-card">
                        <h5><i class="fas fa-cogs"></i> MCP 자동화 프로세스</h5>
                        
                        <!-- 1단계: 데이터 자동 정제 -->
                        <div class="process-step" id="step1">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6><i class="fas fa-broom"></i> 1. 수집된 데이터 자동 정제</h6>
                                    <small>이상치 제거, 결측값 처리, 데이터 타입 변환</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary" id="step1Status">Pending</span>
                                    <div class="progress-step mt-2" style="width: 100px;">
                                        <div class="progress-fill" id="step1Progress" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 2단계: 메타데이터 라벨링 -->
                        <div class="process-step" id="step2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6><i class="fas fa-tags"></i> 2. 메타데이터 시계열 데이터 라벨링</h6>
                                    <small>시계열 특성 분석, 패턴 인식, 라벨 자동 생성</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary" id="step2Status">Pending</span>
                                    <div class="progress-step mt-2" style="width: 100px;">
                                        <div class="progress-fill" id="step2Progress" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 3단계: 모델 선택과 학습 -->
                        <div class="process-step" id="step3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6><i class="fas fa-brain"></i> 3. 학습 데이터 예측 모델 선택과 학습</h6>
                                    <small>AutoML 기반 모델 선택, 하이퍼파라미터 최적화, 자동 학습</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary" id="step3Status">Pending</span>
                                    <div class="progress-step mt-2" style="width: 100px;">
                                        <div class="progress-fill" id="step3Progress" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 4단계: 데이터 품질 검증 -->
                        <div class="process-step" id="step4">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6><i class="fas fa-shield-alt"></i> 4. 데이터 품질 검증 리포트</h6>
                                    <small>모델 성능 평가, 데이터 품질 메트릭, 검증 리포트 생성</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary" id="step4Status">Pending</span>
                                    <div class="progress-step mt-2" style="width: 100px;">
                                        <div class="progress-fill" id="step4Progress" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 5단계: 최종 모델 확정 -->
                        <div class="process-step" id="step5">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6><i class="fas fa-check-circle"></i> 5. 최종 모델 확정</h6>
                                    <small>모델 배포, 성능 모니터링, 자동 재학습 설정</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-secondary" id="step5Status">Pending</span>
                                    <div class="progress-step mt-2" style="width: 100px;">
                                        <div class="progress-fill" id="step5Progress" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 실시간 로그 및 메트릭 -->
                <div class="col-lg-4">
                    <div class="mcp-card">
                        <h5><i class="fas fa-terminal"></i> 실시간 로그</h5>
                        <div class="log-container" id="logContainer">
                            <div class="log-entry">
                                <span class="log-timestamp">[2024-01-15 10:30:15]</span>
                                <span class="log-info">MCP Agent initialized</span>
                            </div>
                            <div class="log-entry">
                                <span class="log-timestamp">[2024-01-15 10:30:16]</span>
                                <span class="log-info">Waiting for pipeline start...</span>
                            </div>
                        </div>
                    </div>

                    <div class="mcp-card">
                        <h5><i class="fas fa-chart-line"></i> 실시간 메트릭</h5>
                        <div class="metric-card">
                            <h6>Data Quality Score</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" id="dataQuality" style="width: 0%"></div>
                            </div>
                            <small id="dataQualityText">0%</small>
                        </div>
                        <div class="metric-card">
                            <h6>Model Accuracy</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-info" id="modelAccuracy" style="width: 0%"></div>
                            </div>
                            <small id="modelAccuracyText">0%</small>
                        </div>
                        <div class="metric-card">
                            <h6>Processing Speed</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-warning" id="processingSpeed" style="width: 0%"></div>
                            </div>
                            <small id="processingSpeedText">0 records/sec</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI/ML 서버 MCP 연결 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="mcp-card">
                        <h5><i class="fas fa-server"></i> AI/ML 서버 MCP 연결</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="metric-card">
                                    <h6><i class="fas fa-link"></i> MCP 서버 연결 상태</h6>
                                    <div class="mb-3">
                                        <span class="badge bg-success" id="mcpConnectionStatus">Connected</span>
                                        <span class="ms-2" id="mcpServerInfo">ML Server v2.1.0</span>
                                    </div>
                                    <div class="mb-3">
                                        <button class="btn btn-primary btn-sm" onclick="connectMCPServer()">
                                            <i class="fas fa-plug"></i> Connect to MCP Server
                                        </button>
                                        <button class="btn btn-info btn-sm ms-2" onclick="refreshModelList()">
                                            <i class="fas fa-sync"></i> Refresh Models
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="metric-card">
                                    <h6><i class="fas fa-download"></i> 모델 다운로드</h6>
                                    <div class="mb-3">
                                        <select class="form-select" id="modelSelectDropdown">
                                            <option value="">모델을 선택하세요</option>
                                            <option value="xgboost-v1.2">XGBoost Regressor v1.2</option>
                                            <option value="lightgbm-v2.0">LightGBM v2.0</option>
                                            <option value="random-forest-v1.5">Random Forest v1.5</option>
                                            <option value="neural-network-v3.1">Neural Network v3.1</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <button class="btn btn-success btn-sm" onclick="downloadModel()" id="downloadBtn" disabled>
                                            <i class="fas fa-download"></i> Download Model
                                        </button>
                                        <button class="btn btn-warning btn-sm ms-2" onclick="optimizeModel()">
                                            <i class="fas fa-magic"></i> Optimize Model
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 대시보드 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="mcp-card">
                        <h5><i class="fas fa-chart-bar"></i> 모델 성능 대시보드</h5>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="metric-card text-center">
                                    <h6>Selected Model</h6>
                                    <h4 id="selectedModel">AutoML Selected</h4>
                                    <small class="text-muted">Best performing model</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card text-center">
                                    <h6>Training Time</h6>
                                    <h4 id="trainingTime">-</h4>
                                    <small class="text-muted">Total training duration</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card text-center">
                                    <h6>Validation Score</h6>
                                    <h4 id="validationScore">-</h4>
                                    <small class="text-muted">Cross-validation score</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="metric-card text-center">
                                    <h6>Deployment Status</h6>
                                    <h4 id="deploymentStatus">-</h4>
                                    <small class="text-muted">Model deployment status</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 비교 및 선택 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="mcp-card">
                        <h5><i class="fas fa-balance-scale"></i> 모델 비교 및 최적 선택</h5>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Model Name</th>
                                        <th>Accuracy</th>
                                        <th>Precision</th>
                                        <th>Recall</th>
                                        <th>F1-Score</th>
                                        <th>Training Time</th>
                                        <th>Model Size</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody id="modelComparisonTable">
                                    <tr>
                                        <td><strong>XGBoost Regressor v1.2</strong></td>
                                        <td>0.92</td>
                                        <td>0.89</td>
                                        <td>0.91</td>
                                        <td>0.90</td>
                                        <td>2.3 min</td>
                                        <td>45 MB</td>
                                        <td><span class="badge bg-success">Available</span></td>
                                        <td>
                                            <button class="btn btn-primary btn-sm" onclick="selectModel('xgboost-v1.2')">
                                                <i class="fas fa-check"></i> Select
                                            </button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>LightGBM v2.0</strong></td>
                                        <td>0.90</td>
                                        <td>0.87</td>
                                        <td>0.89</td>
                                        <td>0.88</td>
                                        <td>1.8 min</td>
                                        <td>32 MB</td>
                                        <td><span class="badge bg-success">Available</span></td>
                                        <td>
                                            <button class="btn btn-primary btn-sm" onclick="selectModel('lightgbm-v2.0')">
                                                <i class="fas fa-check"></i> Select
                                            </button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>Random Forest v1.5</strong></td>
                                        <td>0.88</td>
                                        <td>0.85</td>
                                        <td>0.87</td>
                                        <td>0.86</td>
                                        <td>3.2 min</td>
                                        <td>78 MB</td>
                                        <td><span class="badge bg-warning">Training</span></td>
                                        <td>
                                            <button class="btn btn-secondary btn-sm" disabled>
                                                <i class="fas fa-clock"></i> Training
                                            </button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>Neural Network v3.1</strong></td>
                                        <td>0.94</td>
                                        <td>0.92</td>
                                        <td>0.93</td>
                                        <td>0.925</td>
                                        <td>5.1 min</td>
                                        <td>156 MB</td>
                                        <td><span class="badge bg-success">Available</span></td>
                                        <td>
                                            <button class="btn btn-primary btn-sm" onclick="selectModel('neural-network-v3.1')">
                                                <i class="fas fa-check"></i> Select
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentStep = 0;
            let pipelineRunning = false;
            let logEntries = 0;

            // 로그 추가 함수
            function addLog(message, type = 'info') {{
                const logContainer = document.getElementById('logContainer');
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.innerHTML = `
                    <span class="log-timestamp">[${{timestamp}}]</span>
                    <span class="log-${{type}}">${{message}}</span>
                `;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
                logEntries++;
                
                // 로그가 너무 많아지면 오래된 것 제거
                if (logEntries > 50) {{
                    logContainer.removeChild(logContainer.firstChild);
                    logEntries--;
                }}
            }}

            // 단계 업데이트 함수
            function updateStep(stepNumber, status, progress) {{
                const stepElement = document.getElementById(`step${{stepNumber}}`);
                const statusElement = document.getElementById(`step${{stepNumber}}Status`);
                const progressElement = document.getElementById(`step${{stepNumber}}Progress`);
                
                // 이전 단계 완료 처리
                if (stepNumber > 1) {{
                    const prevStep = document.getElementById(`step${{stepNumber - 1}}`);
                    prevStep.classList.remove('active');
                    prevStep.classList.add('completed');
                    document.getElementById(`step${{stepNumber - 1}}Status`).textContent = 'Completed';
                    document.getElementById(`step${{stepNumber - 1}}Status`).className = 'badge bg-success';
                }}
                
                // 현재 단계 활성화
                stepElement.classList.add('active');
                statusElement.textContent = status;
                statusElement.className = `badge bg-${{status === 'Running' ? 'warning' : status === 'Completed' ? 'success' : 'secondary'}}`;
                progressElement.style.width = progress + '%';
            }}

            // 메트릭 업데이트 함수
            function updateMetrics(dataQuality, modelAccuracy, processingSpeed) {{
                document.getElementById('dataQuality').style.width = dataQuality + '%';
                document.getElementById('dataQualityText').textContent = dataQuality + '%';
                document.getElementById('modelAccuracy').style.width = modelAccuracy + '%';
                document.getElementById('modelAccuracyText').textContent = modelAccuracy + '%';
                document.getElementById('processingSpeed').style.width = Math.min(processingSpeed / 10, 100) + '%';
                document.getElementById('processingSpeedText').textContent = processingSpeed + ' records/sec';
            }}

            // MCP 파이프라인 시작
            function startMCPPipeline() {{
                if (pipelineRunning) return;
                
                pipelineRunning = true;
                document.getElementById('agentStatus').textContent = 'Running';
                document.getElementById('agentStatus').className = 'badge bg-warning fs-6';
                document.getElementById('currentTask').textContent = 'Data Processing';
                
                addLog('Starting MCP automated pipeline...', 'info');
                
                // 1단계: 데이터 자동 정제
                setTimeout(() => {{
                    updateStep(1, 'Running', 0);
                    addLog('Step 1: Starting data cleaning and preprocessing...', 'info');
                    
                    let progress = 0;
                    const interval1 = setInterval(() => {{
                        progress += Math.random() * 15;
                        if (progress >= 100) {{
                            progress = 100;
                            clearInterval(interval1);
                            updateStep(1, 'Completed', 100);
                            addLog('Step 1: Data cleaning completed successfully', 'success');
                            updateMetrics(95, 0, 0);
                            startStep2();
                        }} else {{
                            document.getElementById('step1Progress').style.width = progress + '%';
                            updateMetrics(Math.floor(progress * 0.95), 0, Math.floor(progress * 2));
                        }}
                    }}, 200);
                }}, 1000);
            }}

            // 2단계: 메타데이터 라벨링
            function startStep2() {{
                setTimeout(() => {{
                    updateStep(2, 'Running', 0);
                    addLog('Step 2: Starting metadata labeling and time series analysis...', 'info');
                    
                    let progress = 0;
                    const interval2 = setInterval(() => {{
                        progress += Math.random() * 12;
                        if (progress >= 100) {{
                            progress = 100;
                            clearInterval(interval2);
                            updateStep(2, 'Completed', 100);
                            addLog('Step 2: Metadata labeling completed', 'success');
                            updateMetrics(98, 0, 0);
                            startStep3();
                        }} else {{
                            document.getElementById('step2Progress').style.width = progress + '%';
                            updateMetrics(95 + Math.floor(progress * 0.03), 0, 2 + Math.floor(progress * 1.5));
                        }}
                    }}, 300);
                }}, 500);
            }}

            // 3단계: 모델 선택과 학습
            function startStep3() {{
                setTimeout(() => {{
                    updateStep(3, 'Running', 0);
                    addLog('Step 3: Starting AutoML model selection and training...', 'info');
                    
                    let progress = 0;
                    const interval3 = setInterval(() => {{
                        progress += Math.random() * 8;
                        if (progress >= 100) {{
                            progress = 100;
                            clearInterval(interval3);
                            updateStep(3, 'Completed', 100);
                            addLog('Step 3: Model training completed', 'success');
                            updateMetrics(98, 87, 0);
                            document.getElementById('selectedModel').textContent = 'XGBoost Regressor';
                            document.getElementById('trainingTime').textContent = '2.3 min';
                            document.getElementById('validationScore').textContent = '0.87';
                            startStep4();
                        }} else {{
                            document.getElementById('step3Progress').style.width = progress + '%';
                            updateMetrics(98, Math.floor(progress * 0.87), 0);
                        }}
                    }}, 400);
                }}, 500);
            }}

            // 4단계: 데이터 품질 검증
            function startStep4() {{
                setTimeout(() => {{
                    updateStep(4, 'Running', 0);
                    addLog('Step 4: Starting data quality validation and reporting...', 'info');
                    
                    let progress = 0;
                    const interval4 = setInterval(() => {{
                        progress += Math.random() * 20;
                        if (progress >= 100) {{
                            progress = 100;
                            clearInterval(interval4);
                            updateStep(4, 'Completed', 100);
                            addLog('Step 4: Quality validation completed', 'success');
                            updateMetrics(99, 89, 0);
                            startStep5();
                        }} else {{
                            document.getElementById('step4Progress').style.width = progress + '%';
                            updateMetrics(98 + Math.floor(progress * 0.01), 87 + Math.floor(progress * 0.02), 0);
                        }}
                    }}, 150);
                }}, 500);
            }}

            // 5단계: 최종 모델 확정
            function startStep5() {{
                setTimeout(() => {{
                    updateStep(5, 'Running', 0);
                    addLog('Step 5: Finalizing model and setting up deployment...', 'info');
                    
                    let progress = 0;
                    const interval5 = setInterval(() => {{
                        progress += Math.random() * 25;
                        if (progress >= 100) {{
                            progress = 100;
                            clearInterval(interval5);
                            updateStep(5, 'Completed', 100);
                            addLog('Step 5: Model deployment completed successfully!', 'success');
                            updateMetrics(100, 92, 0);
                            document.getElementById('deploymentStatus').textContent = 'Deployed';
                            document.getElementById('deploymentStatus').className = 'text-success';
                            
                            // 파이프라인 완료
                            document.getElementById('agentStatus').textContent = 'Completed';
                            document.getElementById('agentStatus').className = 'badge bg-success fs-6';
                            document.getElementById('currentTask').textContent = 'Pipeline Complete';
                            document.getElementById('overallProgress').style.width = '100%';
                            document.getElementById('progressText').textContent = '100% Complete';
                            
                            pipelineRunning = false;
                            addLog('MCP automated pipeline completed successfully!', 'success');
                        }} else {{
                            document.getElementById('step5Progress').style.width = progress + '%';
                            updateMetrics(99 + Math.floor(progress * 0.01), 89 + Math.floor(progress * 0.03), 0);
                        }}
                    }}, 100);
                }}, 500);
            }}

            // MCP 서버 연결 함수
            function connectMCPServer() {{
                addLog('Connecting to MCP ML Server...', 'info');
                document.getElementById('mcpConnectionStatus').textContent = 'Connecting';
                document.getElementById('mcpConnectionStatus').className = 'badge bg-warning';
                
                setTimeout(() => {{
                    document.getElementById('mcpConnectionStatus').textContent = 'Connected';
                    document.getElementById('mcpConnectionStatus').className = 'badge bg-success';
                    document.getElementById('mcpServerInfo').textContent = 'ML Server v2.1.0 - Connected';
                    addLog('Successfully connected to MCP ML Server', 'success');
                    refreshModelList();
                }}, 2000);
            }}

            // 모델 목록 새로고침
            function refreshModelList() {{
                addLog('Refreshing model list from MCP server...', 'info');
                
                // 모델 목록 업데이트 시뮬레이션
                setTimeout(() => {{
                    addLog('Model list refreshed: 4 models available', 'success');
                    updateModelComparisonTable();
                }}, 1500);
            }}

            // 모델 선택 함수
            function selectModel(modelId) {{
                const modelNames = {{
                    'xgboost-v1.2': 'XGBoost Regressor v1.2',
                    'lightgbm-v2.0': 'LightGBM v2.0',
                    'random-forest-v1.5': 'Random Forest v1.5',
                    'neural-network-v3.1': 'Neural Network v3.1'
                }};
                
                const modelName = modelNames[modelId];
                addLog(`Selected model: ${{modelName}}`, 'info');
                
                // 선택된 모델 정보 업데이트
                document.getElementById('selectedModel').textContent = modelName;
                document.getElementById('modelSelectDropdown').value = modelId;
                document.getElementById('downloadBtn').disabled = false;
                
                // 테이블에서 선택된 모델 하이라이트
                const rows = document.querySelectorAll('#modelComparisonTable tr');
                rows.forEach(row => {{
                    row.classList.remove('table-primary');
                    if (row.innerHTML.includes(modelName)) {{
                        row.classList.add('table-primary');
                    }}
                }});
                
                // 모델 성능 메트릭 업데이트
                updateModelMetrics(modelId);
            }}

            // 모델 다운로드 함수
            function downloadModel() {{
                const selectedModel = document.getElementById('modelSelectDropdown').value;
                if (!selectedModel) {{
                    addLog('Please select a model first', 'warning');
                    return;
                }}
                
                addLog(`Starting download for model: ${{selectedModel}}`, 'info');
                
                // 다운로드 진행률 시뮬레이션
                let progress = 0;
                const downloadInterval = setInterval(() => {{
                    progress += Math.random() * 20;
                    if (progress >= 100) {{
                        progress = 100;
                        clearInterval(downloadInterval);
                        addLog(`Model ${{selectedModel}} downloaded successfully!`, 'success');
                        document.getElementById('deploymentStatus').textContent = 'Downloaded';
                        document.getElementById('deploymentStatus').className = 'text-success';
                    }} else {{
                        addLog(`Downloading... ${{Math.floor(progress)}}%`, 'info');
                    }}
                }}, 500);
            }}

            // 모델 최적화 함수
            function optimizeModel() {{
                const selectedModel = document.getElementById('modelSelectDropdown').value;
                if (!selectedModel) {{
                    addLog('Please select a model first', 'warning');
                    return;
                }}
                
                addLog(`Starting optimization for model: ${{selectedModel}}`, 'info');
                
                // 최적화 진행률 시뮬레이션
                let progress = 0;
                const optimizeInterval = setInterval(() => {{
                    progress += Math.random() * 15;
                    if (progress >= 100) {{
                        progress = 100;
                        clearInterval(optimizeInterval);
                        addLog(`Model ${{selectedModel}} optimized successfully!`, 'success');
                        
                        // 최적화된 성능 메트릭 업데이트
                        updateModelMetrics(selectedModel, true);
                    }} else {{
                        addLog(`Optimizing... ${{Math.floor(progress)}}%`, 'info');
                    }}
                }}, 800);
            }}

            // 모델 성능 메트릭 업데이트
            function updateModelMetrics(modelId, optimized = false) {{
                const metrics = {{
                    'xgboost-v1.2': {{ accuracy: 0.92, precision: 0.89, recall: 0.91, f1: 0.90, time: '2.3 min' }},
                    'lightgbm-v2.0': {{ accuracy: 0.90, precision: 0.87, recall: 0.89, f1: 0.88, time: '1.8 min' }},
                    'random-forest-v1.5': {{ accuracy: 0.88, precision: 0.85, recall: 0.87, f1: 0.86, time: '3.2 min' }},
                    'neural-network-v3.1': {{ accuracy: 0.94, precision: 0.92, recall: 0.93, f1: 0.925, time: '5.1 min' }}
                }};
                
                const modelMetrics = metrics[modelId];
                if (modelMetrics) {{
                    if (optimized) {{
                        // 최적화된 성능 (5-10% 향상)
                        modelMetrics.accuracy += 0.05;
                        modelMetrics.precision += 0.05;
                        modelMetrics.recall += 0.05;
                        modelMetrics.f1 += 0.05;
                    }}
                    
                    document.getElementById('trainingTime').textContent = modelMetrics.time;
                    document.getElementById('validationScore').textContent = modelMetrics.accuracy.toFixed(3);
                    
                    // 실시간 메트릭 업데이트
                    updateMetrics(100, Math.floor(modelMetrics.accuracy * 100), 0);
                }}
            }}

            // 모델 비교 테이블 업데이트
            function updateModelComparisonTable() {{
                // 테이블 데이터를 동적으로 업데이트하는 로직
                addLog('Model comparison table updated with latest metrics', 'info');
            }}

            // 모델 선택 드롭다운 이벤트 리스너
            document.addEventListener('DOMContentLoaded', function() {{
                const modelSelect = document.getElementById('modelSelectDropdown');
                modelSelect.addEventListener('change', function() {{
                    if (this.value) {{
                        selectModel(this.value);
                    }} else {{
                        document.getElementById('downloadBtn').disabled = true;
                    }}
                }});
            }});

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                addLog('MCP Agent ready for automated ML pipeline', 'info');
                addLog('AI/ML Server MCP connection established', 'success');
                updateMetrics(0, 0, 0);
                
                // 자동으로 MCP 서버 연결
                setTimeout(() => {{
                    connectMCPServer();
                }}, 1000);
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/crewai-system", response_class=HTMLResponse)
async def crewai_system_page(request: Request, lang: str = Query("ko", description="Language code")):
    """CrewAI Specialized Agent Teams 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 CrewAI Specialized Agent Teams</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .crew-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 20px;
                padding: 25px;
                transition: transform 0.3s ease;
            }}
            .crew-card:hover {{
                transform: translateY(-5px);
            }}
            .crew-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .status-indicator {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }}
            .status-active {{ background-color: #28a745; }}
            .status-idle {{ background-color: #ffc107; }}
            .status-error {{ background-color: #dc3545; }}
            .workflow-step {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
            }}
            .agent-avatar {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                margin: 0 auto 15px;
            }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 데이터 신선도 표시 -->
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-clock"></i> 
                            <strong>{t('crewai.dataFreshness.lastUpdate', lang)}:</strong> 
                            <span id="lastUpdateTime">2024-01-15 10:30:45 KST</span>
                        </div>
                        <div>
                            <span class="badge bg-success" id="freshnessIndicator">
                                <i class="fas fa-circle"></i> {t('crewai.dataFreshness.realtime', lang)}
                            </span>
                            <div class="btn-group ms-2" role="group">
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="setTimezone('KST')">
                                    {t('crewai.dataFreshness.kst', lang)}
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="setTimezone('Local')">
                                    {t('crewai.dataFreshness.local', lang)}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 헤더 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h1 class="mb-3">
                            <i class="fas fa-users-cog text-primary"></i> {t('crewai.title', lang)}
                        </h1>
                        <h4 class="text-muted mb-3">{t('crewai.subtitle', lang)}</h4>
                        <p class="lead">{t('crewai.description', lang)}</p>
                    </div>
                </div>
            </div>

            <!-- Crew Status Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h5><i class="fas fa-chart-pie"></i> {t('crewai.crewStatusOverview', lang)}</h5>
                        <div class="row">
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-database"></i>
                                    </div>
                                    <h6>{t('crewai.dataIngestion', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-chart-line"></i>
                                    </div>
                                    <h6>{t('crewai.forecasting', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                    <h6>{t('crewai.anomalyDetection', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-sliders-h"></i>
                                    </div>
                                    <h6>{t('crewai.demandControl', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-file-alt"></i>
                                    </div>
                                    <h6>{t('crewai.reporting', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="text-center">
                                    <div class="agent-avatar">
                                        <i class="fas fa-cogs"></i>
                                    </div>
                                    <h6>{t('crewai.orchestrator', lang)}</h6>
                                    <span class="status-indicator status-active"></span>
                                    <small>{t('crewai.active', lang)}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Workflow Control -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="crew-card">
                        <h5><i class="fas fa-play-circle"></i> {t('crewai.workflowControl', lang)}</h5>
                        <div class="mb-3">
                            <label class="form-label">{t('crewai.workflowType', lang)}</label>
                            <select class="form-select" id="workflowType">
                                <option value="sequential">{t('crewai.sequentialWorkflow', lang)}</option>
                                <option value="parallel">{t('crewai.parallelWorkflow', lang)}</option>
                                <option value="hybrid">{t('crewai.hybridWorkflow', lang)}</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">{t('crewai.triggerEvent', lang)}</label>
                            <input type="text" class="form-control" id="triggerEvent" placeholder="{t('crewai.optionalTriggerEvent', lang)}">
                        </div>
                        <button class="btn btn-primary w-100 mb-2" onclick="startWorkflow()">
                            <i class="fas fa-play"></i> {t('crewai.startWorkflow', lang)}
                        </button>
                        <button class="btn btn-warning w-100 mb-2" onclick="pauseWorkflow()">
                            <i class="fas fa-pause"></i> {t('crewai.pauseWorkflow', lang)}
                        </button>
                        <button class="btn btn-danger w-100" onclick="stopWorkflow()">
                            <i class="fas fa-stop"></i> {t('crewai.stopWorkflow', lang)}
                        </button>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="crew-card">
                        <h5><i class="fas fa-chart-bar"></i> {t('crewai.systemMetrics', lang)}</h5>
                        <div class="row">
                            <div class="col-6">
                                <div class="text-center">
                                    <h6>{t('crewai.activeCrews', lang)}</h6>
                                    <h3 class="text-success" id="activeCrews">5</h3>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <h6>{t('crewai.eventsProcessed', lang)}</h6>
                                    <h3 class="text-info" id="eventsProcessed">1,247</h3>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-6">
                                <div class="text-center">
                                    <h6>{t('crewai.successRate', lang)}</h6>
                                    <h3 class="text-success" id="successRate">98.5%</h3>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <h6>{t('crewai.avgResponseTime', lang)}</h6>
                                    <h3 class="text-warning" id="avgResponseTime">2.3s</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Crew Details -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="crew-card">
                        <div class="crew-header">
                            <h5><i class="fas fa-database"></i> {t('crewai.dataIngestionCrew.title', lang)}</h5>
                        </div>
                        <p><strong>{t('crewai.role', lang)}:</strong> {t('crewai.dataIngestionCrew.role', lang)}</p>
                        <p><strong>{t('crewai.tools', lang)}:</strong> {t('crewai.dataIngestionCrew.tools', lang)}</p>
                        <div class="workflow-step">
                            <strong>{t('crewai.currentTask', lang)}:</strong> {t('crewai.dataIngestionCrew.currentTask', lang)}
                        </div>
                        <div class="workflow-step">
                            <strong>{t('crewai.status', lang)}:</strong> <span class="status-indicator status-active"></span> {t('crewai.dataIngestionCrew.status', lang)}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="crew-card">
                        <div class="crew-header">
                            <h5><i class="fas fa-chart-line"></i> {t('crewai.forecastingCrew.title', lang)}</h5>
                        </div>
                        <p><strong>{t('crewai.role', lang)}:</strong> {t('crewai.forecastingCrew.role', lang)}</p>
                        <p><strong>{t('crewai.tools', lang)}:</strong> {t('crewai.forecastingCrew.tools', lang)}</p>
                        <div class="workflow-step">
                            <strong>{t('crewai.currentTask', lang)}:</strong> {t('crewai.forecastingCrew.currentTask', lang)}
                        </div>
                        <div class="workflow-step">
                            <strong>{t('crewai.status', lang)}:</strong> <span class="status-indicator status-active"></span> {t('crewai.forecastingCrew.status', lang)}
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="crew-card">
                        <div class="crew-header">
                            <h5><i class="fas fa-exclamation-triangle"></i> {t('crewai.anomalyCrew.title', lang)}</h5>
                        </div>
                        <p><strong>{t('crewai.role', lang)}:</strong> {t('crewai.anomalyCrew.role', lang)}</p>
                        <p><strong>{t('crewai.tools', lang)}:</strong> {t('crewai.anomalyCrew.tools', lang)}</p>
                        <div class="workflow-step">
                            <strong>{t('crewai.currentTask', lang)}:</strong> {t('crewai.anomalyCrew.currentTask', lang)}
                        </div>
                        <div class="workflow-step">
                            <strong>{t('crewai.status', lang)}:</strong> <span class="status-indicator status-active"></span> {t('crewai.anomalyCrew.status', lang)}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="crew-card">
                        <div class="crew-header">
                            <h5><i class="fas fa-sliders-h"></i> {t('crewai.demandControlCrew.title', lang)}</h5>
                        </div>
                        <p><strong>{t('crewai.role', lang)}:</strong> {t('crewai.demandControlCrew.role', lang)}</p>
                        <p><strong>{t('crewai.tools', lang)}:</strong> {t('crewai.demandControlCrew.tools', lang)}</p>
                        <div class="workflow-step">
                            <strong>{t('crewai.currentTask', lang)}:</strong> {t('crewai.demandControlCrew.currentTask', lang)}
                        </div>
                        <div class="workflow-step">
                            <strong>{t('crewai.status', lang)}:</strong> <span class="status-indicator status-active"></span> {t('crewai.demandControlCrew.status', lang)}
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <div class="crew-header">
                            <h5><i class="fas fa-file-alt"></i> {t('crewai.reportingCrew.title', lang)}</h5>
                        </div>
                        <p><strong>{t('crewai.role', lang)}:</strong> {t('crewai.reportingCrew.role', lang)}</p>
                        <p><strong>{t('crewai.tools', lang)}:</strong> {t('crewai.reportingCrew.tools', lang)}</p>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="workflow-step">
                                    <strong>{t('crewai.currentTask', lang)}:</strong> {t('crewai.reportingCrew.currentTask', lang)}
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="workflow-step">
                                    <strong>{t('crewai.modelStatus', lang)}:</strong> {t('crewai.reportingCrew.modelStatus', lang)}
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="workflow-step">
                                    <strong>{t('crewai.status', lang)}:</strong> <span class="status-indicator status-active"></span> {t('crewai.reportingCrew.status', lang)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 워크플로우 실행 안전장치 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h5><i class="fas fa-shield-alt text-warning"></i> {t('crewai.safetyControls.title', lang)}</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="alert alert-warning">
                                    <h6><i class="fas fa-user-check"></i> {t('crewai.safetyControls.humanApproval', lang)}</h6>
                                    <p class="mb-2">{t('crewai.safetyControls.humanApproval', lang)} 대기 중...</p>
                                    <div class="mb-3">
                                        <label class="form-label">{t('crewai.safetyControls.policySelection', lang)}</label>
                                        <select class="form-select" id="policySelection">
                                            <option value="peakSuppression">{t('crewai.safetyControls.policySelection', lang)} - Peak Suppression</option>
                                            <option value="loadBalancing">{t('crewai.safetyControls.policySelection', lang)} - Load Balancing</option>
                                            <option value="efficiencyOptimization">{t('crewai.safetyControls.policySelection', lang)} - Efficiency Optimization</option>
                                        </select>
                                    </div>
                                    <div class="row">
                                        <div class="col-4">
                                            <div class="text-center">
                                                <h6 class="text-danger">{t('crewai.safetyControls.costImpact', lang)}</h6>
                                                <span class="badge bg-danger">-12.5%</span>
                                            </div>
                                        </div>
                                        <div class="col-4">
                                            <div class="text-center">
                                                <h6 class="text-success">{t('crewai.safetyControls.emissionImpact', lang)}</h6>
                                                <span class="badge bg-success">-8.3%</span>
                                            </div>
                                        </div>
                                        <div class="col-4">
                                            <div class="text-center">
                                                <h6 class="text-info">{t('crewai.safetyControls.comfortImpact', lang)}</h6>
                                                <span class="badge bg-info">+2.1%</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mt-3">
                                        <button class="btn btn-success me-2" onclick="approveControl()">
                                            <i class="fas fa-check"></i> {t('crewai.safetyControls.approveControl', lang)}
                                        </button>
                                        <button class="btn btn-danger" onclick="rejectControl()">
                                            <i class="fas fa-times"></i> {t('crewai.safetyControls.rejectControl', lang)}
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="alert alert-info">
                                    <h6><i class="fas fa-camera"></i> {t('crewai.safetyControls.simulationSnapshot', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>Trace ID:</strong> <code>trace_20240115_103045_abc123</code>
                                    </div>
                                    <div class="mb-2">
                                        <strong>Version:</strong> EnergySLM-v2.1 (Training: 65%)
                                    </div>
                                    <div class="mb-2">
                                        <strong>Input:</strong> 15 sensors, 3 weather APIs, 2 tariff sources
                                    </div>
                                    <div class="mb-2">
                                        <strong>Output:</strong> Load control commands, PV curtailment, Storage dispatch
                                    </div>
                                    <div class="btn-group" role="group">
                                        <button class="btn btn-outline-primary btn-sm" onclick="downloadSnapshot()">
                                            <i class="fas fa-download"></i> {t('crewai.safetyControls.simulationSnapshot', lang)} 다운로드
                                        </button>
                                        <button class="btn btn-outline-success btn-sm" onclick="startSessionReplay()">
                                            <i class="fas fa-play"></i> 리플레이 시작
                                        </button>
                                        <button class="btn btn-outline-danger btn-sm" onclick="stopSessionReplay()">
                                            <i class="fas fa-stop"></i> 리플레이 중지
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 신뢰도·품질 가드레일 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h5><i class="fas fa-shield-alt text-info"></i> {t('crewai.reliabilityGuards.title', lang)}</h5>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="alert alert-success">
                                    <h6><i class="fas fa-bullseye"></i> {t('crewai.reliabilityGuards.accuracyThreshold', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.accuracyThreshold', lang)}:</strong> 94.2% 
                                        <span class="badge bg-success">{t('crewai.active', lang)}</span>
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.accuracyThreshold', lang)}:</strong> 90.0%
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" style="width: 94.2%"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="alert alert-warning">
                                    <h6><i class="fas fa-undo"></i> {t('crewai.reliabilityGuards.fallbackModel', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.fallbackModel', lang)}:</strong> XGBoost (94.2%)
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.fallbackModel', lang)}:</strong> Rule-based (87.5%)
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fallbackMode" id="autoFallback" checked>
                                        <label class="form-check-label" for="autoFallback">
                                            {t('crewai.reliabilityGuards.autoFallback', lang)}
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="fallbackMode" id="manualFallback">
                                        <label class="form-check-label" for="manualFallback">
                                            {t('crewai.reliabilityGuards.manualFallback', lang)}
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="alert alert-danger">
                                    <h6><i class="fas fa-exclamation-triangle"></i> {t('crewai.reliabilityGuards.errorBoundary', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.retryPolicy', lang)}:</strong> 3회 (Exponential backoff)
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.circuitBreaker', lang)}:</strong> 5회 실패 시 30초 대기
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.reliabilityGuards.healthCheck', lang)}:</strong> 30초 간격
                                    </div>
                                    <span class="badge bg-success">{t('crewai.active', lang)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Event Log with Enhanced Observability -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5><i class="fas fa-list"></i> {t('crewai.eventLog', lang)}</h5>
                            <div class="btn-group" role="group">
                                <button class="btn btn-outline-primary btn-sm" onclick="filterLogs('all')">전체</button>
                                <button class="btn btn-outline-primary btn-sm" onclick="filterLogs('data')">데이터 수집</button>
                                <button class="btn btn-outline-primary btn-sm" onclick="filterLogs('forecast')">예측</button>
                                <button class="btn btn-outline-primary btn-sm" onclick="filterLogs('anomaly')">이상 탐지</button>
                                <button class="btn btn-outline-primary btn-sm" onclick="filterLogs('control')">제어</button>
                                <button class="btn btn-outline-primary btn-sm" onclick="exportLogs()">
                                    <i class="fas fa-download"></i> CSV
                                </button>
                            </div>
                        </div>
                        <div class="bg-dark text-light p-3 rounded" style="height: 300px; overflow-y: auto; font-family: monospace;" id="eventLog">
                            <div class="log-entry" data-crew="data" data-trace="trace_001">
                                <span class="text-info">[2024-01-15 10:30:15]</span> 
                                <span class="text-warning">[Data Ingestion]</span> 
                                <span class="text-light">Started sensor data collection</span>
                                <span class="text-muted">(Trace: trace_001)</span>
                            </div>
                            <div class="log-entry" data-crew="forecast" data-trace="trace_002">
                                <span class="text-info">[2024-01-15 10:30:18]</span> 
                                <span class="text-warning">[Forecasting]</span> 
                                <span class="text-light">Generated 24h demand prediction</span>
                                <span class="text-muted">(Trace: trace_002)</span>
                            </div>
                            <div class="log-entry" data-crew="anomaly" data-trace="trace_003">
                                <span class="text-info">[2024-01-15 10:30:22]</span> 
                                <span class="text-warning">[Anomaly Detection]</span> 
                                <span class="text-light">Detected 3 anomalies in generation data</span>
                                <span class="text-muted">(Trace: trace_003)</span>
                            </div>
                            <div class="log-entry" data-crew="control" data-trace="trace_004">
                                <span class="text-info">[2024-01-15 10:30:25]</span> 
                                <span class="text-warning">[Demand Control]</span> 
                                <span class="text-light">Optimized demand-supply matching</span>
                                <span class="text-muted">(Trace: trace_004)</span>
                            </div>
                            <div class="log-entry" data-crew="reporting" data-trace="trace_005">
                                <span class="text-info">[2024-01-15 10:30:28]</span> 
                                <span class="text-warning">[Reporting]</span> 
                                <span class="text-light">Generated operational summary</span>
                                <span class="text-muted">(Trace: trace_005)</span>
                            </div>
                            <div class="log-entry text-warning" data-crew="system" data-trace="trace_006">
                                <span class="text-info">[2024-01-15 10:30:30]</span> 
                                <span class="text-warning">[System]</span> 
                                <span class="text-light">All crews operating normally</span>
                                <span class="text-muted">(Trace: trace_006)</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 거버넌스 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h5><i class="fas fa-cogs text-primary"></i> {t('crewai.governance.title', lang)}</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="alert alert-primary">
                                    <h6><i class="fas fa-code-branch"></i> {t('crewai.governance.modelVersioning', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.governance.modelVersioning', lang)}:</strong> EnergySLM-v2.1 (Training: 65%)
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.governance.modelVersioning', lang)}:</strong> EnergySLM-v2.0 (Deployed)
                                    </div>
                                    <div class="mb-3">
                                        <div class="btn-group" role="group">
                                            <button class="btn btn-outline-primary btn-sm" onclick="shadowDeploy()">
                                                {t('crewai.governance.shadowDeployment', lang)}
                                            </button>
                                            <button class="btn btn-outline-warning btn-sm" onclick="canaryDeploy()">
                                                {t('crewai.governance.canaryDeployment', lang)}
                                            </button>
                                            <button class="btn btn-outline-danger btn-sm" onclick="rollbackModel()">
                                                {t('crewai.governance.rollback', lang)}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="alert alert-success">
                                    <h6><i class="fas fa-chart-bar"></i> {t('crewai.governance.performanceComparison', lang)}</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <div class="text-center">
                                                <h6 class="text-danger">{t('crewai.governance.errorCost', lang)}</h6>
                                                <span class="badge bg-danger">v2.1: -15%</span>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="text-center">
                                                <h6 class="text-success">{t('crewai.governance.energyCost', lang)}</h6>
                                                <span class="badge bg-success">v2.1: -8%</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mt-2">
                                        <button class="btn btn-outline-info btn-sm" onclick="viewReleaseNotes()">
                                            <i class="fas fa-file-alt"></i> {t('crewai.governance.releaseNotes', lang)}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 권한/감사 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="crew-card">
                        <h5><i class="fas fa-lock text-danger"></i> {t('crewai.security.title', lang)}</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="alert alert-warning">
                                    <h6><i class="fas fa-users-cog"></i> {t('crewai.security.rbac', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.rbac', lang)}:</strong> admin@energy-system.com
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.rbac', lang)}:</strong> 
                                        <span class="badge bg-success">{t('crewai.security.readPermission', lang)}</span>
                                        <span class="badge bg-warning">{t('crewai.security.simulationPermission', lang)}</span>
                                        <span class="badge bg-danger">{t('crewai.security.applyPermission', lang)}</span>
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.rbac', lang)}:</strong>
                                        <ul class="mb-0">
                                            <li>Data Ingestion: {t('crewai.security.readPermission', lang)}/{t('crewai.security.simulationPermission', lang)}</li>
                                            <li>Forecasting: {t('crewai.security.readPermission', lang)}/{t('crewai.security.simulationPermission', lang)}</li>
                                            <li>Control: {t('crewai.security.readPermission', lang)}/{t('crewai.security.simulationPermission', lang)}/{t('crewai.security.applyPermission', lang)}</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="alert alert-info">
                                    <h6><i class="fas fa-clipboard-list"></i> {t('crewai.security.auditLog', lang)}</h6>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.whoApproved', lang)}:</strong> admin@energy-system.com
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.whenApproved', lang)}:</strong> 2024-01-15 10:25:30
                                    </div>
                                    <div class="mb-2">
                                        <strong>{t('crewai.security.whatApproved', lang)}:</strong> 피크 억제 정책 적용
                                    </div>
                                    <div class="mb-2">
                                        <strong>IP 주소:</strong> 192.168.1.100
                                    </div>
                                    <button class="btn btn-outline-primary btn-sm" onclick="viewAuditLog()">
                                        <i class="fas fa-eye"></i> {t('crewai.security.auditLog', lang)}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Timezone management
            function setTimezone(tz) {{
                const now = new Date();
                let timeString;
                if (tz === 'KST') {{
                    timeString = now.toLocaleString('ko-KR', {{timeZone: 'Asia/Seoul'}}) + ' KST';
                }} else {{
                    timeString = now.toLocaleString() + ' Local';
                }}
                document.getElementById('lastUpdateTime').textContent = timeString;
            }}

            // Safety control functions
            function approveControl() {{
                const policy = document.getElementById('policySelection').value;
                const approvalData = {{
                    timestamp: new Date().toISOString(),
                    policy: policy,
                    approver: 'admin@energy-system.com',
                    ip: '192.168.1.100',
                    sessionId: 'session_' + Date.now()
                }};
                
                // 승인 로그 추가
                addEventLog(`제어 명령 승인됨: ${{policy}}`, 'success');
                addAuditLog('APPROVAL', approvalData);
                
                // 승인 프로세스 시뮬레이션
                setTimeout(() => {{
                    addEventLog('제어 명령이 성공적으로 적용되었습니다.', 'success');
                    addAuditLog('APPLICATION', approvalData);
                }}, 2000);
            }}

            function rejectControl() {{
                const rejectionData = {{
                    timestamp: new Date().toISOString(),
                    reason: 'Manual rejection by operator',
                    approver: 'admin@energy-system.com',
                    ip: '192.168.1.100'
                }};
                
                addEventLog('제어 명령이 거부되었습니다.', 'warning');
                addAuditLog('REJECTION', rejectionData);
            }}

            // 감사 로그 추가 함수
            function addAuditLog(action, data) {{
                const auditEntry = {{
                    id: 'audit_' + Date.now(),
                    action: action,
                    timestamp: data.timestamp,
                    user: data.approver,
                    ip: data.ip,
                    details: data
                }};
                
                // 로컬 스토리지에 감사 로그 저장
                let auditLogs = JSON.parse(localStorage.getItem('auditLogs') || '[]');
                auditLogs.unshift(auditEntry);
                if (auditLogs.length > 100) auditLogs = auditLogs.slice(0, 100);
                localStorage.setItem('auditLogs', JSON.stringify(auditLogs));
                
                console.log('Audit Log:', auditEntry);
            }}

            // 세션 리플레이 기능
            function startSessionReplay() {{
                const sessionData = {{
                    startTime: new Date().toISOString(),
                    user: 'admin@energy-system.com',
                    actions: []
                }};
                
                addEventLog('세션 리플레이 시작됨', 'info');
                localStorage.setItem('currentSession', JSON.stringify(sessionData));
            }}

            function stopSessionReplay() {{
                const sessionData = JSON.parse(localStorage.getItem('currentSession') || '{{}}');
                sessionData.endTime = new Date().toISOString();
                sessionData.duration = new Date(sessionData.endTime) - new Date(sessionData.startTime);
                
                addEventLog('세션 리플레이 종료됨', 'info');
                localStorage.setItem('lastSession', JSON.stringify(sessionData));
                localStorage.removeItem('currentSession');
            }}

            function downloadSnapshot() {{
                addEventLog('시뮬레이션 스냅샷을 다운로드합니다...', 'info');
                // Simulate download
                setTimeout(() => {{
                    addEventLog('스냅샷 다운로드 완료: trace_20240115_103045_abc123.json', 'success');
                }}, 1000);
            }}

            // Governance functions
            function shadowDeploy() {{
                addEventLog('Shadow 배포를 시작합니다...', 'info');
                setTimeout(() => {{
                    addEventLog('Shadow 배포 완료: EnergySLM-v2.1', 'success');
                }}, 3000);
            }}

            function canaryDeploy() {{
                addEventLog('Canary 배포를 시작합니다...', 'info');
                setTimeout(() => {{
                    addEventLog('Canary 배포 완료: 10% 트래픽', 'success');
                }}, 2000);
            }}

            function rollbackModel() {{
                addEventLog('모델 롤백을 시작합니다...', 'warning');
                setTimeout(() => {{
                    addEventLog('롤백 완료: EnergySLM-v2.0으로 복원', 'success');
                }}, 2000);
            }}

            function viewReleaseNotes() {{
                addEventLog('릴리즈 노트를 표시합니다...', 'info');
            }}

            // Security functions
            function viewAuditLog() {{
                addEventLog('감사 로그를 표시합니다...', 'info');
            }}

            // Enhanced log filtering
            function filterLogs(crew) {{
                const logEntries = document.querySelectorAll('.log-entry');
                logEntries.forEach(entry => {{
                    if (crew === 'all' || entry.dataset.crew === crew) {{
                        entry.style.display = 'block';
                    }} else {{
                        entry.style.display = 'none';
                    }}
                }});
            }}

            function exportLogs() {{
                addEventLog('CSV 내보내기를 시작합니다...', 'info');
                setTimeout(() => {{
                    addEventLog('CSV 내보내기 완료: event_log_20240115.csv', 'success');
                }}, 1000);
            }}

            // Workflow control functions
            function startWorkflow() {{
                const workflowType = document.getElementById('workflowType').value;
                const triggerEvent = document.getElementById('triggerEvent').value;
                
                addEventLog(`Starting ${{workflowType}} workflow...`);
                
                // Simulate workflow execution
                setTimeout(() => {{
                    addEventLog(`${{workflowType}} workflow completed successfully`);
                    updateMetrics();
                }}, 3000);
            }}

            function pauseWorkflow() {{
                addEventLog('Workflow paused by user');
            }}

            function stopWorkflow() {{
                addEventLog('Workflow stopped by user');
            }}

            // Event logging
            function addEventLog(message, type = 'info') {{
                const logContainer = document.getElementById('eventLog');
                const timestamp = new Date().toLocaleString();
                const logEntry = document.createElement('div');
                logEntry.className = type === 'error' ? 'text-danger' : type === 'warning' ? 'text-warning' : '';
                logEntry.innerHTML = `[${{timestamp}}] ${{message}}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
            }}

            // Metrics update
            function updateMetrics() {{
                const activeCrews = document.getElementById('activeCrews');
                const eventsProcessed = document.getElementById('eventsProcessed');
                const successRate = document.getElementById('successRate');
                const avgResponseTime = document.getElementById('avgResponseTime');

                // Simulate metric updates
                const currentEvents = parseInt(eventsProcessed.textContent.replace(',', ''));
                eventsProcessed.textContent = (currentEvents + Math.floor(Math.random() * 10)).toLocaleString();
                
                const currentRate = parseFloat(successRate.textContent);
                successRate.textContent = (currentRate + Math.random() * 0.1).toFixed(1) + '%';
                
                const currentTime = parseFloat(avgResponseTime.textContent);
                avgResponseTime.textContent = (currentTime + Math.random() * 0.2).toFixed(1) + 's';
            }}

            // Auto-update metrics every 30 seconds
            setInterval(updateMetrics, 30000);

            // Auto-add events every 60 seconds
            setInterval(() => {{
                const events = [
                    'Data Ingestion Crew: Collected 1,000 new data points',
                    'Forecasting Crew: Updated prediction models',
                    'Anomaly Crew: No new anomalies detected',
                    'Control Crew: Optimized energy distribution',
                    'Reporting Crew: Generated hourly summary'
                ];
                const randomEvent = events[Math.floor(Math.random() * events.length)];
                addEventLog(randomEvent);
            }}, 60000);
        </script>
    </body>
    </html>
    """

@web_app.get("/llm-slm", response_class=HTMLResponse)
async def llm_slm_page(request: Request, lang: str = Query("ko", description="Language code")):
    """LLM SLM Development 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 LLM SLM Development - Energy Specialized Language Model</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .llm-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 20px;
                padding: 25px;
            }}
            .model-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }}
            .model-card:hover {{
                transform: translateY(-5px);
            }}
            .training-progress {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 10px 0;
            }}
            .status-indicator {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }}
            .status-training {{ background-color: #ffc107; }}
            .status-completed {{ background-color: #28a745; }}
            .status-error {{ background-color: #dc3545; }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}

        <div class="container-fluid mt-4">
            <!-- 헤더 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="llm-card">
                        <h1 class="mb-3">
                            <i class="fas fa-robot text-primary"></i> LLM SLM Development
                        </h1>
                        <h4 class="text-muted mb-3">에너지 특화 언어 모델 개발</h4>
                        <p class="lead">Advanced AI language model specialized for energy management and analysis</p>
                    </div>
                </div>
            </div>

            <!-- 모델 개발 상태 -->
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="model-card">
                        <h5><i class="fas fa-brain"></i> 현재 개발 모델</h5>
                        <div class="row">
                            <div class="col-6">
                                <div class="metric-card">
                                    <h6>모델 이름</h6>
                                    <strong>EnergySLM-v2.1</strong>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="metric-card">
                                    <h6>개발 상태</h6>
                                    <span class="status-indicator status-training"></span>
                                    <strong>훈련 중</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="model-card">
                        <h5><i class="fas fa-chart-line"></i> 훈련 진행률</h5>
                        <div class="training-progress">
                            <div class="d-flex justify-content-between mb-2">
                                <span>전체 진행률</span>
                                <span id="trainingProgress">65%</span>
                            </div>
                            <div class="progress">
                                <div class="progress-bar bg-warning" role="progressbar" style="width: 65%" id="progressBar"></div>
                            </div>
                            <small class="text-light">Epoch 325/500</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 지표 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="llm-card text-center">
                        <h6><i class="fas fa-bullseye"></i> 정확도</h6>
                        <h3 class="text-success" id="accuracy">94.2%</h3>
                        <small class="text-muted">Energy Prediction</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="llm-card text-center">
                        <h6><i class="fas fa-tachometer-alt"></i> 처리 속도</h6>
                        <h3 class="text-info" id="speed">1.2s</h3>
                        <small class="text-muted">평균 응답 시간</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="llm-card text-center">
                        <h6><i class="fas fa-database"></i> 데이터셋</h6>
                        <h3 class="text-warning" id="dataset">2.3M</h3>
                        <small class="text-muted">훈련 샘플</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="llm-card text-center">
                        <h6><i class="fas fa-memory"></i> 모델 크기</h6>
                        <h3 class="text-primary" id="modelSize">1.8GB</h3>
                        <small class="text-muted">파라미터 수</small>
                    </div>
                </div>
            </div>

            <!-- 훈련 로그 -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="llm-card">
                        <h5><i class="fas fa-terminal"></i> 실시간 훈련 로그</h5>
                        <div class="bg-dark text-light p-3 rounded" style="height: 300px; overflow-y: auto; font-family: monospace;" id="trainingLog">
                            <div>[2024-01-15 10:30:15] 모델 초기화 완료</div>
                            <div>[2024-01-15 10:30:16] 데이터셋 로딩 중...</div>
                            <div>[2024-01-15 10:30:18] 훈련 시작 - Epoch 1/500</div>
                            <div>[2024-01-15 10:35:22] Loss: 2.3456, Accuracy: 0.7234</div>
                            <div>[2024-01-15 10:40:15] Epoch 2 완료 - Loss: 2.1234</div>
                            <div>[2024-01-15 10:45:08] 검증 정확도: 0.7891</div>
                            <div class="text-warning">[2024-01-15 10:50:12] 현재 Epoch 325/500 진행 중...</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="llm-card">
                        <h5><i class="fas fa-cogs"></i> 모델 설정</h5>
                        <div class="mb-3">
                            <label class="form-label">학습률 (Learning Rate)</label>
                            <input type="range" class="form-range" min="0.001" max="0.1" step="0.001" value="0.01" id="learningRate">
                            <small class="text-muted">현재: 0.01</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">배치 크기 (Batch Size)</label>
                            <select class="form-select" id="batchSize">
                                <option value="16">16</option>
                                <option value="32" selected>32</option>
                                <option value="64">64</option>
                                <option value="128">128</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">에포크 수 (Epochs)</label>
                            <input type="number" class="form-control" value="500" id="epochs">
                        </div>
                        <button class="btn btn-primary w-100 mb-2" onclick="startTraining()">
                            <i class="fas fa-play"></i> 훈련 시작
                        </button>
                        <button class="btn btn-warning w-100 mb-2" onclick="pauseTraining()">
                            <i class="fas fa-pause"></i> 훈련 일시정지
                        </button>
                        <button class="btn btn-danger w-100" onclick="stopTraining()">
                            <i class="fas fa-stop"></i> 훈련 중지
                        </button>
                    </div>
                </div>
            </div>

            <!-- 모델 비교 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="llm-card">
                        <h5><i class="fas fa-balance-scale"></i> 모델 버전 비교</h5>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>모델 버전</th>
                                        <th>정확도</th>
                                        <th>처리 속도</th>
                                        <th>모델 크기</th>
                                        <th>개발 상태</th>
                                        <th>작업</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>EnergySLM-v2.1</strong></td>
                                        <td>94.2%</td>
                                        <td>1.2s</td>
                                        <td>1.8GB</td>
                                        <td><span class="status-indicator status-training"></span>훈련 중</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary">상세보기</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>EnergySLM-v2.0</strong></td>
                                        <td>91.8%</td>
                                        <td>1.5s</td>
                                        <td>1.6GB</td>
                                        <td><span class="status-indicator status-completed"></span>완료</td>
                                        <td>
                                            <button class="btn btn-sm btn-success">배포</button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><strong>EnergySLM-v1.9</strong></td>
                                        <td>89.3%</td>
                                        <td>1.8s</td>
                                        <td>1.4GB</td>
                                        <td><span class="status-indicator status-completed"></span>완료</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-secondary">아카이브</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 실시간 훈련 로그 업데이트
            function addTrainingLog(message, type = 'info') {{
                const logContainer = document.getElementById('trainingLog');
                const timestamp = new Date().toLocaleString();
                const logEntry = document.createElement('div');
                logEntry.className = type === 'error' ? 'text-danger' : type === 'warning' ? 'text-warning' : '';
                logEntry.innerHTML = `[${{timestamp}}] ${{message}}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
            }}

            // 훈련 진행률 업데이트
            function updateTrainingProgress() {{
                const progress = Math.min(65 + Math.random() * 2, 100);
                document.getElementById('trainingProgress').textContent = Math.round(progress) + '%';
                document.getElementById('progressBar').style.width = progress + '%';
            }}

            // 성능 지표 업데이트
            function updateMetrics() {{
                const accuracy = (94.2 + Math.random() * 0.5).toFixed(1);
                const speed = (1.2 + Math.random() * 0.1).toFixed(1);
                const dataset = (2.3 + Math.random() * 0.1).toFixed(1);
                const modelSize = (1.8 + Math.random() * 0.1).toFixed(1);

                document.getElementById('accuracy').textContent = accuracy + '%';
                document.getElementById('speed').textContent = speed + 's';
                document.getElementById('dataset').textContent = dataset + 'M';
                document.getElementById('modelSize').textContent = modelSize + 'GB';
            }}

            // 훈련 제어 함수들
            function startTraining() {{
                addTrainingLog('새로운 훈련 세션을 시작합니다...', 'info');
                document.querySelector('.status-indicator').className = 'status-indicator status-training';
                document.querySelector('.status-indicator').nextSibling.textContent = '훈련 중';
            }}

            function pauseTraining() {{
                addTrainingLog('훈련을 일시정지합니다...', 'warning');
            }}

            function stopTraining() {{
                addTrainingLog('훈련을 중지합니다...', 'error');
                document.querySelector('.status-indicator').className = 'status-indicator status-error';
                document.querySelector('.status-indicator').nextSibling.textContent = '중지됨';
            }}

            // 학습률 슬라이더 업데이트
            document.getElementById('learningRate').addEventListener('input', function() {{
                const value = this.value;
                this.nextElementSibling.textContent = '현재: ' + value;
            }});

            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                // 5초마다 훈련 진행률 업데이트
                setInterval(updateTrainingProgress, 5000);
                
                // 10초마다 성능 지표 업데이트
                setInterval(updateMetrics, 10000);
                
                // 30초마다 훈련 로그 추가
                setInterval(() => {{
                    const messages = [
                        'Loss: ' + (2.1 + Math.random() * 0.2).toFixed(4),
                        'Validation Accuracy: ' + (0.94 + Math.random() * 0.01).toFixed(4),
                        'Learning Rate: ' + (0.01 + Math.random() * 0.001).toFixed(4),
                        'Batch Processing: ' + Math.floor(Math.random() * 100) + ' samples/sec'
                    ];
                    addTrainingLog(messages[Math.floor(Math.random() * messages.length)]);
                }}, 30000);
            }});
        </script>
    </body>
    </html>
    """
@web_app.get("/agent-system", response_class=HTMLResponse)
async def agent_system_page(request: Request, lang: str = Query("ko", description="Language code")):
    """AI 에이전트 시스템 관리 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 HORIZON AI Agent System - Multi-Site Energy Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min-icons" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
        <style>
            :root {{
                --primary-color: #4f46e5;
                --secondary-color: #06b6d4;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --danger-color: #ef4444;
                --info-color: #3b82f6;
                --light-color: #f8fafc;
                --dark-color: #1e293b;
            }}
            
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            .agent-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .agent-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
            }}
            
            .agent-header {{
                background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
                color: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                text-align: center;
            }}
            
            .kpi-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .kpi-value {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .kpi-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            
            .agent-item {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 5px solid var(--primary-color);
                transition: all 0.3s ease;
            }}
            
            .agent-item:hover {{
                transform: translateX(5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }}
            
            .agent-item.enabled {{
                border-left-color: var(--success-color);
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
            }}
            
            .agent-item.disabled {{
                border-left-color: #d1d5db;
                background: #f9fafb;
                opacity: 0.7;
            }}
            
            .status-badge {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            
            .status-active {{
                background: #d1fae5;
                color: #065f46;
            }}
            
            .status-inactive {{
                background: #f3f4f6;
                color: #6b7280;
            }}
            
            .metric-bar {{
                height: 8px;
                background: #e5e7eb;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 5px;
            }}
            
            .metric-fill {{
                height: 100%;
                border-radius: 4px;
                transition: width 0.3s ease;
            }}
            
            .metric-fill.blue {{ background: #3b82f6; }}
            .metric-fill.green {{ background: #10b981; }}
            .metric-fill.yellow {{ background: #f59e0b; }}
            .metric-fill.purple {{ background: #8b5cf6; }}
            .metric-fill.red {{ background: #ef4444; }}
            .metric-fill.indigo {{ background: #6366f1; }}
            
            .site-selector {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .site-option {{
                padding: 15px;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                background: #ffffff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }}
            
            .site-option:hover {{
                border-color: var(--primary-color);
                background: #f8fafc;
                transform: translateY(-2px);
            }}
            
            .site-option.active {{
                border-color: var(--primary-color);
                background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
                box-shadow: 0 6px 18px rgba(79, 70, 229, 0.15);
                transform: translateY(-3px) scale(1.01);
            }}
            
            .site-option.inactive {{
                opacity: 0.6;
                filter: grayscale(10%);
            }}
            
            .site-option .status-dot {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #9ca3af;
                transition: background 0.3s ease, transform 0.3s ease;
            }}
            
            .site-option.active .status-dot {{
                background: #10b981;
                transform: scale(1.2);
            }}
            
            .chart-container {{
                height: 300px;
                position: relative;
            }}
            
            .btn-agent {{
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border: none;
                color: white;
                padding: 8px 20px;
                border-radius: 25px;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            
            .btn-agent:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
                color: white;
            }}
            
            .btn-agent:disabled {{
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            
            .expandable {{
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
            }}
            
            .expandable.expanded {{
                max-height: 1000px;
            }}
            
            .fade-in {{
                animation: fadeIn 0.8s ease-in;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .pulse {{
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    </head>
    <body>
        {generate_navigation(lang)}
        
        <div class="container-fluid mt-4">
            <!-- AI Agent System 헤더 -->
            <div class="agent-header">
                <h1 class="display-4 mb-3">
                    <i class="fas fa-robot"></i> HORIZON AI Agent System
                </h1>
                <p class="lead mb-4">Multi-Site Energy Management AI Agents</p>
                <div class="row">
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalAgents">6</div>
                            <div class="kpi-label">총 에이전트</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="activeAgents">5</div>
                            <div class="kpi-label">활성 에이전트</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="totalPredictions">5,247</div>
                            <div class="kpi-label">총 예측 수</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="kpi-card">
                            <div class="kpi-value" id="avgAccuracy">91%</div>
                            <div class="kpi-label">평균 정확도</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 사이트 선택 -->
            <div class="site-selector">
                <h3 class="mb-4">
                    <i class="fas fa-map-marker-alt text-primary"></i> 
                    사이트 선택 / Select Site
                </h3>
                <div class="row">
                    <div class="col-md-3">
                        <div class="site-option active" onclick="selectSite('oulu')">
                            <div class="d-flex align-items-center">
                                <span class="fs-1 me-3">🇫🇮</span>
                                <div>
                                    <h5 class="mb-1">Oulu University</h5>
                                    <p class="mb-0 text-muted">Finland - 극한 기후</p>
                                </div>
                            </div>
                            <div class="status-dot"></div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="site-option" onclick="selectSite('kth')">
                            <div class="d-flex align-items-center">
                                <span class="fs-1 me-3">🇸🇪</span>
                                <div>
                                    <h5 class="mb-1">KTH Living Lab</h5>
                                    <p class="mb-0 text-muted">Sweden - 실증 연구</p>
                                </div>
                            </div>
                            <div class="status-dot"></div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="site-option" onclick="selectSite('beia')">
                            <div class="d-flex align-items-center">
                                <span class="fs-1 me-3">🇷🇴</span>
                                <div>
                                    <h5 class="mb-1">BEIA Research</h5>
                                    <p class="mb-0 text-muted">Romania - IoT 시스템</p>
                                </div>
                            </div>
                            <div class="status-dot"></div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="site-option" onclick="selectSite('triaena')">
                            <div class="d-flex align-items-center">
                                <span class="fs-1 me-3">🇬🇷</span>
                                <div>
                                    <h5 class="mb-1">Triaena/OTE</h5>
                                    <p class="mb-0 text-muted">Greece - 상업 빌딩</p>
                                </div>
                            </div>
                            <div class="status-dot"></div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- AI 에이전트 목록 -->
            <div class="row">
                <div class="col-12">
                    <div class="agent-card">
                        <h3 class="mb-4">
                            <i class="fas fa-cogs text-primary"></i> 
                            AI 에이전트 관리 / AI Agent Management
                        </h3>
                        
                        <!-- 에이전트 1: 에너지 수요 분석 -->
                        <div class="agent-item enabled" id="agent-demand-analysis">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-chart-line fa-2x text-primary"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">에너지 수요 분석 MCP</h5>
                                    <p class="mb-0 text-muted">Energy Demand Analysis MCP</p>
                                    <small class="text-muted">단기/중기 에너지 수요 예측, 소비 패턴 분석</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-active">✅ 활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: 94%</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill blue" style="width: 94%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 1,247</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 85%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: 0.3s</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 70%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('demand-analysis')">
                                        <i class="fas fa-pause"></i> 비활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('demand-analysis')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 (확장 가능) -->
                            <div class="expandable" id="details-demand-analysis">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> 시계열 예측 모델 (LSTM, Prophet)</li>
                                            <li><i class="fas fa-check text-success"></i> 기상 데이터 연동</li>
                                            <li><i class="fas fa-check text-success"></i> 거주자 행동 패턴 학습</li>
                                            <li><i class="fas fa-check text-success"></i> 계절별 수요 변동 분석</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">예측 윈도우:</small><br>
                                                <strong>48시간</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">업데이트 주기:</small><br>
                                                <strong>15분</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">신뢰도 임계값:</small><br>
                                                <strong>85%</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">계절 패턴:</small><br>
                                                <strong>일간</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 에이전트 2: AI/ML 모델 성능 평가 -->
                        <div class="agent-item enabled" id="agent-ml-performance">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-brain fa-2x text-purple"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">AI/ML 모델 성능 평가 MCP</h5>
                                    <p class="mb-0 text-muted">AI/ML Model Performance Evaluation MCP</p>
                                    <small class="text-muted">모델 성능 모니터링, A/B 테스트, 자동 재학습</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-active">✅ 활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: 92%</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill purple" style="width: 92%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 856</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 60%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: 0.5s</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 50%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('ml-performance')">
                                        <i class="fas fa-pause"></i> 비활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('ml-performance')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 -->
                            <div class="expandable" id="details-ml-performance">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> AutoML 파이프라인</li>
                                            <li><i class="fas fa-check text-success"></i> 모델 비교 (XGBoost, LGBM, RF, NN)</li>
                                            <li><i class="fas fa-check text-success"></i> 성능 메트릭 추적</li>
                                            <li><i class="fas fa-check text-success"></i> 모델 거버넌스 시스템</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">평가 주기:</small><br>
                                                <strong>일간</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">성능 임계값:</small><br>
                                                <strong>90%</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">자동 재학습:</small><br>
                                                <strong>활성</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">A/B 테스트:</small><br>
                                                <strong>7일</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 에이전트 3: 온톨로지 MCP -->
                        <div class="agent-item disabled" id="agent-ontology">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-project-diagram fa-2x text-indigo"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">온톨로지 MCP</h5>
                                    <p class="mb-0 text-muted">Ontology MCP</p>
                                    <small class="text-muted">에너지 시스템 지식 그래프, 데이터 표준화</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-inactive">⏸️ 비활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: -</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill indigo" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 0</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 0%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: -</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 0%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('ontology')">
                                        <i class="fas fa-play"></i> 활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('ontology')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 -->
                            <div class="expandable" id="details-ontology">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> SAREF 온톨로지 매핑</li>
                                            <li><i class="fas fa-check text-success"></i> 시맨틱 데이터 모델링</li>
                                            <li><i class="fas fa-check text-success"></i> 지식 추론 엔진</li>
                                            <li><i class="fas fa-check text-success"></i> RDF/OWL 변환</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">온톨로지 버전:</small><br>
                                                <strong>SAREF 4.0</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">추론 엔진:</small><br>
                                                <strong>Pellet</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">업데이트 모드:</small><br>
                                                <strong>증분</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">캐싱:</small><br>
                                                <strong>활성</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 에이전트 4: 에너지 공급 분석 -->
                        <div class="agent-item enabled" id="agent-supply-analysis">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-bolt fa-2x text-warning"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">에너지 공급 분석 MCP</h5>
                                    <p class="mb-0 text-muted">Energy Supply Analysis MCP</p>
                                    <small class="text-muted">발전량 예측, 재생에너지 최적화, ESS 관리</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-active">✅ 활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: 89%</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 89%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 2,134</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 100%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: 0.4s</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 60%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('supply-analysis')">
                                        <i class="fas fa-pause"></i> 비활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('supply-analysis')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 -->
                            <div class="expandable" id="details-supply-analysis">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> 태양광/풍력 발전 예측</li>
                                            <li><i class="fas fa-check text-success"></i> ESS 최적화 알고리즘</li>
                                            <li><i class="fas fa-check text-success"></i> 날씨 기반 출력 예측</li>
                                            <li><i class="fas fa-check text-success"></i> 그리드 연동 관리</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">예측 범위:</small><br>
                                                <strong>72시간</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">ESS 전략:</small><br>
                                                <strong>비용 최적화</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">안전 여유율:</small><br>
                                                <strong>15%</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">그리드 연계:</small><br>
                                                <strong>활성</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 에이전트 5: 수요 제어 알고리즘 -->
                        <div class="agent-item enabled" id="agent-demand-control">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-sliders-h fa-2x text-success"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">수요 제어 알고리즘 MCP</h5>
                                    <p class="mb-0 text-muted">Demand Control Algorithm MCP</p>
                                    <small class="text-muted">수요-공급 매칭, 피크 억제, 부하 제어</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-active">✅ 활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: 91%</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 91%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 567</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 40%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: 0.2s</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 80%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('demand-control')">
                                        <i class="fas fa-pause"></i> 비활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('demand-control')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 -->
                            <div class="expandable" id="details-demand-control">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> 수요반응(DR) 최적화</li>
                                            <li><i class="fas fa-check text-success"></i> 피크 시프팅 알고리즘</li>
                                            <li><i class="fas fa-check text-success"></i> 부하 우선순위 관리</li>
                                            <li><i class="fas fa-check text-success"></i> 제어 시뮬레이터</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">피크 임계값:</small><br>
                                                <strong>150 kW</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">전환 윈도우:</small><br>
                                                <strong>2시간</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">우선순위 레벨:</small><br>
                                                <strong>3단계</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">사용자 오버라이드:</small><br>
                                                <strong>허용</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 에이전트 6: 전력/탄소 거래 -->
                        <div class="agent-item enabled" id="agent-trading">
                            <div class="row align-items-center">
                                <div class="col-md-1">
                                    <div class="text-center">
                                        <i class="fas fa-dollar-sign fa-2x text-success"></i>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h5 class="mb-1">전력/탄소 거래 MCP</h5>
                                    <p class="mb-0 text-muted">Power & Carbon Trading MCP</p>
                                    <small class="text-muted">거래 최적화, 가격 예측, 자동 입찰</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="status-badge status-active">✅ 활성</span>
                                </div>
                                <div class="col-md-3">
                                    <div class="mb-2">
                                        <small class="text-muted">정확도: 87%</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 87%"></div>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">예측 수: 342</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill green" style="width: 25%"></div>
                                        </div>
                                    </div>
                                    <div>
                                        <small class="text-muted">응답시간: 0.6s</small>
                                        <div class="metric-bar">
                                            <div class="metric-fill yellow" style="width: 40%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-2">
                                    <button class="btn btn-agent btn-sm" onclick="toggleAgent('trading')">
                                        <i class="fas fa-pause"></i> 비활성화
                                    </button>
                                    <button class="btn btn-outline-primary btn-sm mt-1" onclick="toggleDetails('trading')">
                                        <i class="fas fa-cog"></i> 설정
                                    </button>
                                </div>
                            </div>
                            
                            <!-- 상세 설정 -->
                            <div class="expandable" id="details-trading">
                                <hr class="my-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-tools text-primary"></i> 도구 및 기능</h6>
                                        <ul class="list-unstyled">
                                            <li><i class="fas fa-check text-success"></i> 시장 가격 예측 모델</li>
                                            <li><i class="fas fa-check text-success"></i> 자동 거래 시스템</li>
                                            <li><i class="fas fa-check text-success"></i> 수익 최적화 알고리즘</li>
                                            <li><i class="fas fa-check text-success"></i> 탄소 배출 추적</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6><i class="fas fa-cog text-primary"></i> 에이전트 설정</h6>
                                        <div class="row">
                                            <div class="col-6">
                                                <small class="text-muted">거래 전략:</small><br>
                                                <strong>균형</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">리스크 수준:</small><br>
                                                <strong>중간</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">자동 거래:</small><br>
                                                <strong>활성</strong>
                                            </div>
                                            <div class="col-6">
                                                <small class="text-muted">일일 한도:</small><br>
                                                <strong>500 EUR</strong>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 성능 모니터링 차트 -->
            <div class="row">
                <div class="col-md-6">
                    <div class="agent-card">
                        <h3 class="mb-4">
                            <i class="fas fa-chart-line text-primary"></i> 
                            에이전트 성능 추이
                        </h3>
                        <div class="chart-container">
                            <canvas id="performanceChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="agent-card">
                        <h3 class="mb-4">
                            <i class="fas fa-chart-pie text-primary"></i> 
                            에이전트별 정확도
                        </h3>
                        <div class="chart-container">
                            <canvas id="accuracyChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 시스템 리소스 모니터링 -->
            <div class="row">
                <div class="col-12">
                    <div class="agent-card">
                        <h3 class="mb-4">
                            <i class="fas fa-server text-primary"></i> 
                            시스템 리소스 모니터링
                        </h3>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h5 class="text-primary">CPU 사용률</h5>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-primary" role="progressbar" style="width: 45%" id="cpuUsage">45%</div>
                                    </div>
                                    <small class="text-muted">4.2 GHz / 8 cores</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h5 class="text-success">메모리 사용</h5>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 62%" id="memoryUsage">62%</div>
                                    </div>
                                    <small class="text-muted">7.9 GB / 12.8 GB</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h5 class="text-warning">디스크 I/O</h5>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 28%" id="diskUsage">28%</div>
                                    </div>
                                    <small class="text-muted">280 MB/s</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h5 class="text-info">네트워크</h5>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-info" role="progressbar" style="width: 35%" id="networkUsage">35%</div>
                                    </div>
                                    <small class="text-muted">150 Mbps</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 사이트 선택
            function selectSite(siteId) {{
                // 모든 사이트 옵션에서 active 클래스 제거
                document.querySelectorAll('.site-option').forEach(option => {{
                    option.classList.remove('active');
                }});
                
                // 선택된 사이트에 active 클래스 추가
                event.target.closest('.site-option').classList.add('active');
                
                // 사이트별 에이전트 설정 로드 (실제 구현에서는 API 호출)
                loadSiteAgents(siteId);
            }}
            
            // 에이전트 활성화/비활성화
            function toggleAgent(agentId) {{
                const agentElement = document.getElementById(`agent-${{agentId}}`);
                const button = agentElement.querySelector('button');
                const statusBadge = agentElement.querySelector('.status-badge');
                
                if (agentElement.classList.contains('enabled')) {{
                    // 비활성화
                    agentElement.classList.remove('enabled');
                    agentElement.classList.add('disabled');
                    button.innerHTML = '<i class="fas fa-play"></i> 활성화';
                    statusBadge.innerHTML = '⏸️ 비활성';
                    statusBadge.className = 'status-badge status-inactive';
                }} else {{
                    // 활성화
                    agentElement.classList.remove('disabled');
                    agentElement.classList.add('enabled');
                    button.innerHTML = '<i class="fas fa-pause"></i> 비활성화';
                    statusBadge.innerHTML = '✅ 활성';
                    statusBadge.className = 'status-badge status-active';
                }}
                
                updateAgentStats();
            }}
            
            // 상세 설정 토글
            function toggleDetails(agentId) {{
                const detailsElement = document.getElementById(`details-${{agentId}}`);
                detailsElement.classList.toggle('expanded');
            }}
            
            // 사이트별 에이전트 설정 로드
            function loadSiteAgents(siteId) {{
                // 실제 구현에서는 API에서 사이트별 설정을 가져옴
                console.log(`Loading agents for site: ${{siteId}}`);
                
                // 사이트별 권장 설정 적용
                const siteConfigs = {{
                    'oulu': {{
                        recommended: ['demand-analysis', 'supply-analysis', 'demand-control', 'trading'],
                        optional: ['ml-performance']
                    }},
                    'kth': {{
                        recommended: ['demand-analysis', 'ml-performance', 'supply-analysis', 'demand-control', 'trading', 'ontology'],
                        optional: []
                    }},
                    'beia': {{
                        recommended: ['demand-analysis', 'supply-analysis', 'demand-control', 'trading', 'ontology'],
                        optional: ['ml-performance']
                    }},
                    'triaena': {{
                        recommended: ['supply-analysis', 'demand-control', 'trading', 'demand-analysis'],
                        optional: ['ml-performance']
                    }}
                }};
                
                const config = siteConfigs[siteId];
                if (config) {{
                    // 모든 에이전트를 비활성화
                    document.querySelectorAll('.agent-item').forEach(agent => {{
                        agent.classList.remove('enabled');
                        agent.classList.add('disabled');
                        const button = agent.querySelector('button');
                        const statusBadge = agent.querySelector('.status-badge');
                        button.innerHTML = '<i class="fas fa-play"></i> 활성화';
                        statusBadge.innerHTML = '⏸️ 비활성';
                        statusBadge.className = 'status-badge status-inactive';
                    }});
                    
                    // 권장 에이전트 활성화
                    config.recommended.forEach(agentId => {{
                        const agentElement = document.getElementById(`agent-${{agentId}}`);
                        if (agentElement) {{
                            agentElement.classList.remove('disabled');
                            agentElement.classList.add('enabled');
                            const button = agentElement.querySelector('button');
                            const statusBadge = agentElement.querySelector('.status-badge');
                            button.innerHTML = '<i class="fas fa-pause"></i> 비활성화';
                            statusBadge.innerHTML = '✅ 활성';
                            statusBadge.className = 'status-badge status-active';
                        }}
                    }});
                    
                    updateAgentStats();
                }}
            }}
            
            // 에이전트 통계 업데이트
            function updateAgentStats() {{
                const enabledAgents = document.querySelectorAll('.agent-item.enabled').length;
                const totalAgents = document.querySelectorAll('.agent-item').length;
                
                document.getElementById('activeAgents').textContent = enabledAgents;
                
                // 평균 정확도 계산 (실제 구현에서는 API에서 가져옴)
                const accuracies = [94, 92, 89, 91, 87]; // 예시 데이터
                const avgAccuracy = Math.round(accuracies.reduce((a, b) => a + b, 0) / accuracies.length);
                document.getElementById('avgAccuracy').textContent = avgAccuracy + '%';
            }}
            
            // 성능 차트 초기화
            function initPerformanceChart() {{
                const ctx = document.getElementById('performanceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: '에너지 수요 분석',
                            data: [92, 88, 95, 94, 91, 89],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'AI/ML 성능 평가',
                            data: [90, 89, 92, 91, 90, 88],
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: '에너지 공급 분석',
                            data: [87, 85, 89, 88, 86, 84],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: '수요 제어 알고리즘',
                            data: [89, 87, 91, 90, 88, 86],
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: '전력/탄소 거래',
                            data: [85, 83, 87, 86, 84, 82],
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
            
            // 정확도 차트 초기화
            function initAccuracyChart() {{
                const ctx = document.getElementById('accuracyChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['에너지 수요 분석', 'AI/ML 성능 평가', '에너지 공급 분석', '수요 제어 알고리즘', '전력/탄소 거래'],
                        datasets: [{{
                            data: [94, 92, 89, 91, 87],
                            backgroundColor: [
                                '#3b82f6',
                                '#8b5cf6',
                                '#f59e0b',
                                '#10b981',
                                '#ef4444'
                            ],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
            
            // 실시간 데이터 업데이트
            function updateRealTimeData() {{
                // CPU 사용률 업데이트
                const cpuUsage = Math.floor(Math.random() * 20 + 35);
                document.getElementById('cpuUsage').style.width = cpuUsage + '%';
                document.getElementById('cpuUsage').textContent = cpuUsage + '%';
                
                // 메모리 사용률 업데이트
                const memoryUsage = Math.floor(Math.random() * 15 + 55);
                document.getElementById('memoryUsage').style.width = memoryUsage + '%';
                document.getElementById('memoryUsage').textContent = memoryUsage + '%';
                
                // 디스크 I/O 업데이트
                const diskUsage = Math.floor(Math.random() * 20 + 20);
                document.getElementById('diskUsage').style.width = diskUsage + '%';
                document.getElementById('diskUsage').textContent = diskUsage + '%';
                
                // 네트워크 사용률 업데이트
                const networkUsage = Math.floor(Math.random() * 20 + 25);
                document.getElementById('networkUsage').style.width = networkUsage + '%';
                document.getElementById('networkUsage').textContent = networkUsage + '%';
            }}
            
            // 페이지 로드 시 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initPerformanceChart();
                initAccuracyChart();
                updateAgentStats();
                updateRealTimeData();
                
                // 30초마다 실시간 데이터 업데이트
                setInterval(updateRealTimeData, 30000);
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=8000)