"""
에너지 분석 웹 인터페이스 - 다국어 지원
FastAPI 기반 웹 대시보드
"""

import os
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime
import json

# 기존 server_cloud.py의 기능을 가져오기
from server_cloud import register_tools

# 다국어 번역 시스템 import
from translations import get_translation, get_available_languages, get_language_name

# 웹 인터페이스용 FastAPI 앱 생성
web_app = FastAPI(
    title="Energy Analysis Web Interface",
    description="에너지 분석 시스템 웹 대시보드",
    version="2.0.0"
)

# 정적 파일과 템플릿 설정 (디렉토리가 없으면 생성)
import os
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")

web_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# server_cloud.py의 API 엔드포인트들을 web_app에 직접 추가
@web_app.get("/api/")
async def api_root():
    """API 루트 엔드포인트"""
    return {
        "message": "Energy Analysis API v2.0.0",
        "status": "active",
        "domain": "damcp.gngmeta.com",
        "features": [
            "energy_prediction",
            "anomaly_detection", 
            "climate_analysis",
            "real_time_monitoring",
            "ensemble_modeling"
        ]
    }

@web_app.get("/api/health")
async def api_health_check():
    """헬스 체크 엔드포인트"""
    try:
        register_tools()
        return {
            "status": "healthy",
            "service": "energy-analysis-api",
            "version": "2.0.0",
            "domain": "damcp.gngmeta.com"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@web_app.get("/api/dashboard")
async def get_dashboard_data():
    """대시보드 데이터 조회"""
    try:
        register_tools()
        return {
            "prediction_accuracy": 95.2,
            "anomaly_count": 3,
            "climate_correlation": 0.78,
            "active_models": 5,
            "energy_consumption": [100, 120, 110, 130, 125, 140],
            "predictions": [135, 142, 138, 145, 150],
            "anomalies": [
                {"timestamp": "2024-01-15T10:30:00Z", "severity": "medium"},
                {"timestamp": "2024-01-15T14:45:00Z", "severity": "low"},
                {"timestamp": "2024-01-15T18:20:00Z", "severity": "high"}
            ],
            "climate_data": {
                "temperature": 22.5,
                "humidity": 65,
                "precipitation": 0.2
            }
        }
    except Exception as e:
        return {"error": str(e)}

@web_app.get("/api/models")
async def get_models():
    """사용 가능한 모델 목록"""
    try:
        register_tools()
        return {
            "models": [
                {
                    "name": "Energy Prediction LSTM",
                    "type": "forecasting",
                    "accuracy": 95.2,
                    "status": "active"
                },
                {
                    "name": "Anomaly Detection Forest",
                    "type": "anomaly_detection",
                    "accuracy": 92.1,
                    "status": "active"
                },
                {
                    "name": "Climate Prediction DeepMind",
                    "type": "climate",
                    "accuracy": 89.5,
                    "status": "active"
                }
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@web_app.get("/api/statistics")
async def get_statistics():
    """시스템 통계"""
    try:
        register_tools()
        return {
            "total_predictions": 15420,
            "accuracy_rate": 95.2,
            "anomalies_detected": 23,
            "models_active": 5,
            "uptime_hours": 168
        }
    except Exception as e:
        return {"error": str(e)}

# 언어 관련 API 엔드포인트
@web_app.get("/api/languages")
async def get_languages():
    """사용 가능한 언어 목록 반환"""
    languages = []
    for lang_code in get_available_languages():
        languages.append({
            "code": lang_code,
            "name": get_language_name(lang_code)
        })
    return {"languages": languages}

@web_app.get("/api/translations/{language}")
async def get_translations(language: str):
    """특정 언어의 모든 번역 반환"""
    if language not in get_available_languages():
        language = "ko"  # 기본값
    
    from translations import TRANSLATIONS
    return {"translations": TRANSLATIONS[language]}

@web_app.get("/api/mcp-models")
async def get_mcp_models():
    """등록된 MCP 모델들의 목록을 반환"""
    try:
        # MCP 모델 카테고리별로 정리
        mcp_models = {
            "time_series": {
                "name": "시계열 분석 모델",
                "description": "ARIMA, Prophet, LSTM 등 시계열 예측 모델",
                "tools": [
                    {"name": "arima_forecast", "description": "ARIMA 모델을 사용한 에너지 소비량 예측"},
                    {"name": "prophet_forecast", "description": "Prophet 모델을 사용한 시계열 예측"},
                    {"name": "lstm_forecast", "description": "LSTM 신경망을 사용한 예측"},
                    {"name": "seasonal_decompose", "description": "계절성 분해 분석"},
                    {"name": "stationarity_test", "description": "정상성 검정"}
                ],
                "status": "active",
                "accuracy": 94.2,
                "category": "forecasting"
            },
            "energy_analysis": {
                "name": "에너지 분석 모델",
                "description": "에너지 효율성, 절약 잠재력 분석 모델",
                "tools": [
                    {"name": "energy_efficiency_analysis", "description": "에너지 효율성 분석"},
                    {"name": "consumption_pattern_analysis", "description": "소비 패턴 분석"},
                    {"name": "peak_demand_analysis", "description": "최대 수요 분석"},
                    {"name": "energy_savings_potential", "description": "에너지 절약 잠재력 분석"}
                ],
                "status": "active",
                "accuracy": 91.8,
                "category": "analysis"
            },
            "climate_prediction": {
                "name": "기후 예측 모델",
                "description": "DeepMind 기반 강수 예측 및 기후 분석 모델",
                "tools": [
                    {"name": "precipitation_forecast", "description": "강수량 예측 (DeepMind 모델)"},
                    {"name": "weather_correlation", "description": "날씨와 에너지 소비 상관관계 분석"},
                    {"name": "synthetic_radar_data", "description": "합성 레이더 데이터 생성"},
                    {"name": "climate_impact_analysis", "description": "기후 영향 분석"}
                ],
                "status": "active",
                "accuracy": 89.5,
                "category": "climate"
            },
            "anomaly_detection": {
                "name": "이상 탐지 모델",
                "description": "Isolation Forest, HMM 등 이상 탐지 모델",
                "tools": [
                    {"name": "isolation_forest_detection", "description": "Isolation Forest 이상 탐지"},
                    {"name": "hmm_anomaly_detection", "description": "HMM 기반 이상 탐지"},
                    {"name": "statistical_anomaly_detection", "description": "통계적 이상 탐지"},
                    {"name": "prophet_anomaly_detection", "description": "Prophet 기반 이상 탐지"}
                ],
                "status": "active",
                "accuracy": 92.7,
                "category": "anomaly"
            },
            "tfhub_models": {
                "name": "TensorFlow Hub 모델",
                "description": "TensorFlow Hub의 사전 훈련된 모델들",
                "tools": [
                    {"name": "load_tfhub_model", "description": "TF-Hub 모델 로드 (256x256, 512x512, 1536x1280)"},
                    {"name": "precipitation_nowcasting", "description": "실시간 강수 예측"},
                    {"name": "model_inference", "description": "모델 추론 실행"},
                    {"name": "model_evaluation", "description": "모델 성능 평가"}
                ],
                "status": "active",
                "accuracy": 87.3,
                "category": "deep_learning"
            },
            "data_analysis": {
                "name": "데이터 분석 모델",
                "description": "EDA, 통계 분석, 시각화 모델",
                "tools": [
                    {"name": "descriptive_statistics", "description": "기술 통계 분석"},
                    {"name": "correlation_analysis", "description": "상관관계 분석"},
                    {"name": "trend_analysis", "description": "트렌드 분석"},
                    {"name": "data_quality_check", "description": "데이터 품질 검사"}
                ],
                "status": "active",
                "accuracy": 95.1,
                "category": "statistics"
            }
        }
        
        return {
            "success": True,
            "models": mcp_models,
            "total_models": len(mcp_models),
            "active_models": len([m for m in mcp_models.values() if m["status"] == "active"])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@web_app.post("/api/select-mcp-model")
async def select_mcp_model(request: Request):
    """MCP 모델을 선택하고 활성화"""
    try:
        data = await request.json()
        model_name = data.get("model_name")
        model_type = data.get("model_type")
        
        if not model_name or not model_type:
            return {"success": False, "error": "Model name and type are required"}
        
        # 모델 선택 로직 (실제 구현에서는 모델 상태를 업데이트)
        selected_model = {
            "name": model_name,
            "type": model_type,
            "selected_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return {
            "success": True,
            "message": f"MCP 모델 '{model_name}' ({model_type})이 성공적으로 선택되었습니다.",
            "selected_model": selected_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@web_app.post("/api/deploy-mcp-model")
async def deploy_mcp_model(request: Request):
    """선택된 MCP 모델을 배포"""
    try:
        data = await request.json()
        model_name = data.get("model_name")
        model_type = data.get("model_type")
        
        if not model_name or not model_type:
            return {"success": False, "error": "Model name and type are required"}
        
        # 모델 배포 로직 (실제 구현에서는 모델을 프로덕션 환경에 배포)
        deployment_info = {
            "model_name": model_name,
            "model_type": model_type,
            "deployed_at": datetime.now().isoformat(),
            "status": "deployed",
            "endpoint": f"/api/mcp/{model_type}/{model_name}",
            "version": "1.0.0"
        }
        
        return {
            "success": True,
            "message": f"MCP 모델 '{model_name}' ({model_type})이 성공적으로 배포되었습니다.",
            "deployment": deployment_info
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

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
        <title>🔋 Energy Management System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <style>
            .energy-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .energy-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
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
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-bolt"></i> <span data-translate="dashboard_title">Energy Management System</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a class="nav-link me-2" href="/health?lang={lang}">
                        <i class="fas fa-heartbeat"></i> <span data-translate="nav_health">Health</span>
                    </a>
                    <a class="nav-link me-2" href="/model-testing?lang={lang}">
                        <i class="fas fa-brain"></i> <span data-translate="nav_ml_ai">ML/AI Engine</span>
                    </a>
                    <a class="nav-link me-2" href="/data-analysis?lang={lang}">
                        <i class="fas fa-chart-bar"></i> <span data-translate="nav_demand">Demand</span>
                    </a>
                    <a class="nav-link me-2" href="/data-collection?lang={lang}">
                        <i class="fas fa-satellite-dish"></i> <span data-translate="nav_supply">Supply</span>
                    </a>
                    <a class="nav-link me-2" href="/statistics?lang={lang}">
                        <i class="fas fa-chart-line"></i> <span data-translate="nav_control">Control</span>
                    </a>
                    <a class="nav-link me-2" href="/llm-slm?lang={lang}">
                        <i class="fas fa-robot"></i> LLM SLM
                    </a>
                    <a class="nav-link me-2" href="/api/docs" target="_blank">
                        <i class="fas fa-book"></i> <span data-translate="nav_api_docs">API Docs</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown me-2">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
                <span class="navbar-text">
                    <span class="status-indicator status-online"></span>
                    System Online
                </span>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <!-- LLM SLM Development 메인 카드 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card energy-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <div class="card-body text-center py-5">
                            <div class="row align-items-center">
                                <div class="col-md-2">
                                    <i class="fas fa-robot" style="font-size: 4rem; color: #fff;"></i>
                                </div>
                                <div class="col-md-8">
                                    <h2 class="card-title mb-2">
                                        <i class="fas fa-brain"></i> LLM SLM Development
                                    </h2>
                                    <p class="card-text mb-3" style="font-size: 1.1rem;">
                                        에너지 특화 언어 모델 개발
                                    </p>
                                    <p class="card-text">
                                        <small>Advanced AI language model specialized for energy management and analysis</small>
                                    </p>
                                </div>
                                <div class="col-md-2">
                                    <a href="/llm-slm?lang={lang}" class="btn btn-light btn-lg">
                                        <i class="fas fa-arrow-right"></i> LLM SLM
                                    </a>
                                </div>
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
                            <h6 class="card-title">System Health</h6>
                            <p class="card-text small text-muted mb-3">
                                Real-time system status monitoring
                            </p>
                            <a href="/health?lang={lang}" class="btn btn-success btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> Health
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
                            <h6 class="card-title">ML/AI Engine</h6>
                            <p class="card-text small text-muted mb-3">
                                ML/AI model management and testing
                            </p>
                            <a href="/model-testing?lang={lang}" class="btn btn-primary btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> ML/AI Engine
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
                            <h6 class="card-title">Energy Demand Monitoring</h6>
                            <p class="card-text small text-muted mb-3">
                                Energy demand analysis and quality management
                            </p>
                            <a href="/data-analysis?lang={lang}" class="btn btn-info btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> Demand
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Energy Supply Monitoring 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-satellite-dish text-warning" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">Energy Supply Monitoring</h6>
                            <p class="card-text small text-muted mb-3">
                                Energy supply monitoring and management
                            </p>
                            <a href="/data-collection?lang={lang}" class="btn btn-warning btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> Supply
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Demand Control 카드 -->
                <div class="col-md-2 mb-4">
                    <div class="card energy-card h-100">
                        <div class="card-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-chart-line text-danger" style="font-size: 2.5rem;"></i>
                            </div>
                            <h6 class="card-title">Demand Control</h6>
                            <p class="card-text small text-muted mb-3">
                                Demand control and system management
                            </p>
                            <a href="/statistics?lang={lang}" class="btn btn-danger btn-sm w-100">
                                <i class="fas fa-arrow-right"></i> Control
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 차트 -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> Real-time Energy Analysis</h5>
                        </div>
                        <div class="card-body">
                            <div style="position: relative; height: 400px; width: 100%;">
                                <canvas id="energyChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 현실적인 24시간 에너지 소비 데이터 생성
            function generateRealisticEnergyData() {{
                const hours = [];
                const consumption = [];
                const predictions = [];
                
                // 24시간 데이터 생성 (새벽 최소, 오후 최대)
                for (let i = 0; i < 24; i++) {{
                    hours.push(i.toString().padStart(2, '0') + ':00');
                    
                    // 현실적인 에너지 소비 패턴
                    let baseConsumption;
                    if (i >= 3 && i <= 5) {{
                        baseConsumption = 45 + Math.random() * 10; // 새벽 최소
                    }} else if (i >= 6 && i <= 8) {{
                        baseConsumption = 60 + Math.random() * 15; // 아침 증가
                    }} else if (i >= 9 && i <= 11) {{
                        baseConsumption = 80 + Math.random() * 20; // 오전 증가
                    }} else if (i >= 12 && i <= 14) {{
                        baseConsumption = 95 + Math.random() * 25; // 오후 최대
                    }} else if (i >= 15 && i <= 17) {{
                        baseConsumption = 85 + Math.random() * 20; // 오후 감소
                    }} else if (i >= 18 && i <= 20) {{
                        baseConsumption = 70 + Math.random() * 15; // 저녁 감소
                    }} else if (i >= 21 && i <= 23) {{
                        baseConsumption = 55 + Math.random() * 10; // 밤 감소
                    }} else {{
                        baseConsumption = 50 + Math.random() * 10; // 심야
                    }}
                    
                    consumption.push(Math.round(baseConsumption));
                    
                    // 예측 데이터 (현재 시간 이후만)
                    if (i > new Date().getHours()) {{
                        const prediction = baseConsumption + (Math.random() - 0.5) * 15;
                        predictions.push(Math.round(prediction));
                    }} else {{
                        predictions.push(null);
                    }}
                }}
                
                return {{ hours, consumption, predictions }};
            }}

            // 차트 초기화
            const ctx = document.getElementById('energyChart').getContext('2d');
            const energyData = generateRealisticEnergyData();
            
            const energyChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: energyData.hours,
                    datasets: [{{
                        label: '실제 에너지 소비 (kWh)',
                        data: energyData.consumption,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        tension: 0.4,
                        fill: true
                    }}, {{
                        label: '예측 에너지 소비 (kWh)',
                        data: energyData.predictions,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 3,
                        borderDash: [8, 4],
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        tension: 0.4,
                        fill: false
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        intersect: false,
                        mode: 'index'
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '24시간 실시간 에너지 분석',
                            font: {{
                                size: 16,
                                weight: 'bold'
                            }}
                        }},
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                usePointStyle: true,
                                padding: 20
                            }}
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            borderWidth: 1,
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y + ' kWh';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '시간 (24시간)',
                                font: {{
                                    weight: 'bold'
                                }}
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }},
                        y: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '에너지 소비량 (kWh)',
                                font: {{
                                    weight: 'bold'
                                }}
                            }},
                            beginAtZero: true,
                            max: 120,
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }},
                            ticks: {{
                                callback: function(value) {{
                                    return value + ' kWh';
                                }}
                            }}
                        }}
                    }},
                    animation: {{
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    }}
                }}
            }});

            // 실시간 데이터 업데이트
            async function updateData() {{
                try {{
                    const response = await fetch('/api/dashboard');
                    const data = await response.json();
                    
                    // 카드 데이터 업데이트
                    document.getElementById('accuracy').textContent = (data.prediction_accuracy || 95.2) + '%';
                    document.getElementById('anomalies').textContent = data.anomaly_count || 3;
                    document.getElementById('models').textContent = data.active_models || 5;
                    
                    // 기후 데이터 업데이트
                    if (data.climate_data && data.climate_data.length > 0) {{
                        const climate = data.climate_data[0];
                        document.getElementById('temperature').textContent = climate.temperature + '°C';
                        document.getElementById('humidity').textContent = climate.humidity + '%';
                        document.getElementById('precipitation').textContent = climate.precipitation + 'mm';
                    }}
                    
                    // 차트 데이터 실시간 업데이트 (현재 시간 데이터만)
                    const currentHour = new Date().getHours();
                    if (energyChart && energyData) {{
                        // 현재 시간의 에너지 소비량을 약간 변동시켜 실시간 효과 생성
                        const currentConsumption = energyData.consumption[currentHour];
                        const variation = (Math.random() - 0.5) * 5; // ±2.5kWh 변동
                        energyData.consumption[currentHour] = Math.max(0, currentConsumption + variation);
                        
                        // 예측 데이터도 업데이트
                        for (let i = currentHour + 1; i < 24; i++) {{
                            if (energyData.predictions[i] !== null) {{
                                const basePrediction = energyData.consumption[i] || 70;
                                const predictionVariation = (Math.random() - 0.5) * 10;
                                energyData.predictions[i] = Math.max(0, basePrediction + predictionVariation);
                            }}
                        }}
                        
                        // 차트 업데이트
                        energyChart.data.datasets[0].data = energyData.consumption;
                        energyChart.data.datasets[1].data = energyData.predictions;
                        energyChart.update('none'); // 애니메이션 없이 즉시 업데이트
                    }}
                    
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                }} catch (error) {{
                    console.error('Error updating data:', error);
                    // 오류 발생 시에도 기본 데이터로 차트 업데이트
                    if (energyChart && energyData) {{
                        energyChart.data.datasets[0].data = energyData.consumption;
                        energyChart.data.datasets[1].data = energyData.predictions;
                        energyChart.update('none');
                    }}
                }}
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                updateData();
                setInterval(updateData, 30000); // 30초마다 업데이트
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Demand Control 페이지 - Smart Grid Service Overview 기반"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎛️ Demand Control - Smart Grid Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
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
            .toggle-switch {{
                position: relative;
                display: inline-block;
                width: 50px;
                height: 24px;
            }}
            .toggle-switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}
            .slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 24px;
            }}
            .slider:before {{
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }}
            input:checked + .slider {{
                background-color: #2196F3;
            }}
            input:checked + .slider:before {{
                transform: translateX(26px);
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-sliders-h"></i> <span data-translate="demand_control_title">Demand Control</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> <span data-translate="nav_home">Dashboard</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <!-- Smart ESS 중앙 제어 -->
            <div class="row">
                <div class="col-12">
                    <div class="control-card smart-ess-card">
                        <h4><i class="fas fa-microchip"></i> <span data-translate="smart_ess_title">Smart ESS (Energy Storage System)</span></h4>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="control-value" id="essCapacity">85%</div>
                                <div class="control-label" data-translate="smart_ess_capacity">Battery Capacity</div>
                            </div>
                            <div class="col-md-3">
                                <div class="control-value" id="essPower">2.3 kW</div>
                                <div class="control-label" data-translate="smart_ess_power">Current Power</div>
                            </div>
                            <div class="col-md-3">
                                <div class="control-value" id="essEfficiency">94.2%</div>
                                <div class="control-label" data-translate="smart_ess_efficiency">System Efficiency</div>
                            </div>
                            <div class="col-md-3">
                                <div class="control-value" id="essStatus" data-translate="online">Online</div>
                                <div class="control-label" data-translate="smart_ess_status">System Status</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Peak/Night-time Power Supply & Environmental Sensors -->
            <div class="row">
                <!-- Peak/Night-time Power Supply -->
                <div class="col-lg-6">
                    <div class="control-card">
                        <h5><i class="fas fa-solar-panel"></i> Peak/Night-time Power Supply</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="device-item">
                                    <span><i class="fas fa-sun text-warning"></i> Solar Generation</span>
                                    <span class="text-success" id="solarGen">3.2 kW</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-wind text-info"></i> Small-scale Wind Energy</span>
                                    <span class="text-info" id="windGen">1.8 kW</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-battery-half text-primary"></i> Fuel Cells & Others</span>
                                    <span class="text-primary" id="fuelCell">0.5 kW</span>
                                </div>
                                <div class="alert alert-info mt-3" role="alert">
                                    <i class="fas fa-wifi"></i> <strong>WiFi Network:</strong> Connected to Supply-side Monitoring
                                </div>
                            </div>
                            <div class="col-md-6">
                                <canvas id="supplyChart" class="chart-container"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Wireless Integrated Environmental Sensors -->
                <div class="col-lg-6">
                    <div class="control-card sensor-card">
                        <h5><i class="fas fa-thermometer-half"></i> Wireless Integrated Environmental Sensors</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="device-item">
                                    <span><i class="fas fa-thermometer-half"></i> Temperature</span>
                                    <span id="temperature">24.5°C</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-tint"></i> Humidity</span>
                                    <span id="humidity">65%</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-weight"></i> Pressure</span>
                                    <span id="pressure">1013 hPa</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-lightbulb"></i> Illumination</span>
                                    <span id="illumination">450 lux</span>
                                </div>
                                <div class="device-item">
                                    <span><i class="fas fa-users"></i> Occupancy</span>
                                    <span id="occupancy">12 people</span>
                                </div>
                                <div class="alert alert-info mt-3" role="alert">
                                    <i class="fas fa-wifi"></i> <strong>WiFi Network:</strong> Connected to Smart ESS
                                </div>
                            </div>
                            <div class="col-md-6">
                                <canvas id="sensorChart" class="chart-container"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Controllable Units & Service Orchestration -->
            <div class="row">
                <!-- Controllable Units - Small Business Schools -->
                <div class="col-lg-6">
                    <div class="control-card">
                        <h5><i class="fas fa-building"></i> Controllable Units - Small Business Schools</h5>
                        <div class="row">
                            <div class="col-md-4">
                                <h6 class="text-success">Controllable</h6>
                                <div class="form-check form-switch mb-2">
                                    <input class="form-check-input" type="checkbox" id="temperatureControl" checked>
                                    <label class="form-check-label" for="temperatureControl">
                                        <i class="fas fa-thermometer-half"></i> Temperature
                                    </label>
                                </div>
                                <div class="form-check form-switch mb-2">
                                    <input class="form-check-input" type="checkbox" id="copyMachineControl" checked>
                                    <label class="form-check-label" for="copyMachineControl">
                                        <i class="fas fa-copy"></i> Copy Machine
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <h6 class="text-warning">Selectable Control</h6>
                                <div class="form-check form-switch mb-2">
                                    <input class="form-check-input" type="checkbox" id="lightControl">
                                    <label class="form-check-label" for="lightControl">
                                        <i class="fas fa-lightbulb"></i> Light
                                    </label>
                                </div>
                                <div class="form-check form-switch mb-2">
                                    <input class="form-check-input" type="checkbox" id="fanControl">
                                    <label class="form-check-label" for="fanControl">
                                        <i class="fas fa-fan"></i> Fan
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <h6 class="text-danger">Not Controllable</h6>
                                <div class="mb-2">
                                    <i class="fas fa-microphone text-muted"></i> <span class="text-muted">Microwave</span>
                                </div>
                                <div class="mb-2">
                                    <i class="fas fa-tv text-muted"></i> <span class="text-muted">TV</span>
                                </div>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3" role="alert">
                            <i class="fas fa-wifi"></i> <strong>WiFi Network:</strong> Connected to Demand Device → Smart Controller
                        </div>
                    </div>
                </div>

                <!-- Service Orchestration Layer Platform -->
                <div class="col-lg-6">
                    <div class="control-card">
                        <h5><i class="fas fa-cogs"></i> Service Orchestration Layer Platform</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Local Aggregators</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>System Schedule</strong>
                                            <br><small class="text-muted">Local Aggregator</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>System Operator</strong>
                                            <br><small class="text-muted">Local Aggregator</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Central Aggregator</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>System Operator</strong>
                                            <br><small class="text-muted">Central Aggregator</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                </ul>
                                <h6 class="mt-3">Applications</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>Demand Forecasting</strong>
                                            <br><small class="text-muted">ML-based prediction</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>Dynamic ESS</strong>
                                            <br><small class="text-muted">Optimization response</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>User Interface</strong>
                                            <br><small class="text-muted">Feedback system</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3" role="alert">
                            <i class="fas fa-wifi"></i> <strong>Connected to Smart ESS:</strong> Processing data from all sources
                        </div>
                    </div>
                </div>
            </div>

            <!-- MCP Aggregation Price Service & Output Stations -->
            <div class="row">
                <!-- MCP Aggregation Price Service -->
                <div class="col-lg-6">
                    <div class="control-card">
                        <h5><i class="fas fa-dollar-sign"></i> MCP Aggregation Price Service</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Current Prices</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Current Price
                                        <span class="badge bg-primary" id="currentPrice">$0.12/kWh</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Peak Price
                                        <span class="badge bg-danger" id="peakPrice">$0.18/kWh</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Off-Peak Price
                                        <span class="badge bg-success" id="offPeakPrice">$0.08/kWh</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Market Functions</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>Bids/Offers Collection</strong>
                                            <br><small class="text-muted">Active Bids</small>
                                        </div>
                                        <span class="badge bg-info" id="activeBids">15</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>Price Calculation Engine</strong>
                                            <br><small class="text-muted">Real-time pricing</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong>Market Settlement</strong>
                                            <br><small class="text-muted">Transaction processing</small>
                                        </div>
                                        <span class="status-badge status-active">Active</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3" role="alert">
                            <i class="fas fa-wifi"></i> <strong>Connected to Smart ESS:</strong> Real-time price calculation and market settlement
                        </div>
                    </div>
                </div>

                <!-- Output Stations - Demand Device Control -->
                <div class="col-lg-6">
                    <div class="control-card">
                        <h5><i class="fas fa-plug"></i> Output Stations - Demand Device Control</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Control Statistics</h6>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Controlled Devices
                                        <span class="badge bg-primary" id="controlledDevices">8</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Energy Saved
                                        <span class="badge bg-success" id="energySaved">2.3 kWh</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Response Time
                                        <span class="badge bg-info" id="responseTime">45ms</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        System Uptime
                                        <span class="badge bg-success" id="systemUptime">99.8%</span>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Control Actions</h6>
                                <canvas id="controlChart" class="chart-container"></canvas>
                                <div class="mt-2">
                                    <small class="text-muted">
                                        <i class="fas fa-chart-bar"></i> 
                                        Control efficiency over the last 5 days
                                    </small>
                                </div>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3" role="alert">
                            <i class="fas fa-wifi"></i> <strong>Connected to Smart ESS:</strong> Real-time device control and monitoring
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Overview Flow -->
            <div class="row">
                <div class="col-12">
                    <div class="control-card">
                        <h5><i class="fas fa-project-diagram"></i> Smart Grid Service Overview Flow</h5>
                        <div class="row">
                            <div class="col-md-3 text-center">
                                <div class="p-3 border rounded">
                                    <i class="fas fa-solar-panel fa-2x text-warning mb-2"></i>
                                    <h6>Power Supply</h6>
                                    <small class="text-muted">Solar, Wind, Fuel Cells</small>
                                </div>
                            </div>
                            <div class="col-md-1 text-center d-flex align-items-center">
                                <i class="fas fa-arrow-right fa-2x text-primary"></i>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="p-3 border rounded bg-primary text-white">
                                    <i class="fas fa-microchip fa-2x mb-2"></i>
                                    <h6>Smart ESS</h6>
                                    <small>Central Processing</small>
                                </div>
                            </div>
                            <div class="col-md-1 text-center d-flex align-items-center">
                                <i class="fas fa-arrow-right fa-2x text-primary"></i>
                            </div>
                            <div class="col-md-3 text-center">
                                <div class="p-3 border rounded">
                                    <i class="fas fa-cogs fa-2x text-success mb-2"></i>
                                    <h6>Applications</h6>
                                    <small class="text-muted">Forecasting, Control, UI</small>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12 text-center">
                                <div class="alert alert-info" role="alert">
                                    <i class="fas fa-info-circle"></i> 
                                    <strong>Data Flow:</strong> All components communicate via WiFi Network, with Smart ESS as the central hub processing data from supply-side monitoring, environmental sensors, and demand devices to orchestrate intelligent energy management.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 공급 차트 생성
            function createSupplyChart() {{
                const ctx = document.getElementById('supplyChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Solar', 'Wind', 'Fuel Cells'],
                        datasets: [{{
                            data: [3.2, 1.8, 0.5],
                            backgroundColor: ['#ffc107', '#17a2b8', '#007bff'],
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
                            }}
                        }}
                    }}
                }});
            }}

            // 센서 차트 생성
            function createSensorChart() {{
                const ctx = document.getElementById('sensorChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                        datasets: [{{
                            label: 'Temperature (°C)',
                            data: [22, 20, 24, 28, 26, 23],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            pointRadius: 3
                        }}, {{
                            label: 'Humidity (%)',
                            data: [70, 75, 60, 55, 65, 70],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4,
                            pointRadius: 3
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}

            // 제어 차트 생성
            function createControlChart() {{
                const ctx = document.getElementById('controlChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                        datasets: [{{
                            label: 'Control Efficiency',
                            data: [85, 92, 78, 96, 88],
                            backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}
                    }}
                }});
            }}

            // 실시간 데이터 업데이트
            function updateRealtimeData() {{
                // ESS 데이터 업데이트
                document.getElementById('essCapacity').textContent = (85 + Math.random() * 10).toFixed(1) + '%';
                document.getElementById('essPower').textContent = (2.3 + Math.random() * 0.5).toFixed(1) + ' kW';
                document.getElementById('essEfficiency').textContent = (94.2 + Math.random() * 2).toFixed(1) + '%';

                // 공급 데이터 업데이트
                document.getElementById('solarGen').textContent = (3.2 + Math.random() * 0.5).toFixed(1) + ' kW';
                document.getElementById('windGen').textContent = (1.8 + Math.random() * 0.3).toFixed(1) + ' kW';
                document.getElementById('fuelCell').textContent = (0.5 + Math.random() * 0.2).toFixed(1) + ' kW';

                // 센서 데이터 업데이트
                document.getElementById('temperature').textContent = (24.5 + Math.random() * 2).toFixed(1) + '°C';
                document.getElementById('humidity').textContent = (65 + Math.random() * 10).toFixed(0) + '%';
                document.getElementById('pressure').textContent = (1013 + Math.random() * 5).toFixed(0) + ' hPa';
                document.getElementById('illumination').textContent = (450 + Math.random() * 100).toFixed(0) + ' lux';
                document.getElementById('occupancy').textContent = (12 + Math.random() * 5).toFixed(0) + ' people';

                // 가격 데이터 업데이트
                document.getElementById('currentPrice').textContent = '$' + (0.12 + Math.random() * 0.02).toFixed(2) + '/kWh';
                document.getElementById('peakPrice').textContent = '$' + (0.18 + Math.random() * 0.03).toFixed(2) + '/kWh';
                document.getElementById('offPeakPrice').textContent = '$' + (0.08 + Math.random() * 0.01).toFixed(2) + '/kWh';
                document.getElementById('activeBids').textContent = (15 + Math.random() * 5).toFixed(0);

                // 제어 통계 업데이트
                document.getElementById('controlledDevices').textContent = (8 + Math.random() * 2).toFixed(0);
                document.getElementById('energySaved').textContent = (2.3 + Math.random() * 0.5).toFixed(1) + ' kWh';
                document.getElementById('responseTime').textContent = (45 + Math.random() * 10).toFixed(0) + 'ms';
                document.getElementById('systemUptime').textContent = (99.8 + Math.random() * 0.2).toFixed(1) + '%';
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                createSupplyChart();
                createSensorChart();
                createControlChart();
                updateRealtimeData();
                setInterval(updateRealtimeData, 10000); // 10초마다 업데이트
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request, lang: str = Query("ko", description="Language code")):
    """시스템 Health Check 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💚 System Health Check</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .health-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .health-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
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
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-heartbeat"></i> <span data-translate="card_health">System Health Check</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> <span data-translate="nav_home">Dashboard</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- 시스템 상태 카드 -->
                <div class="col-md-4 mb-4">
                    <div class="card health-card">
                        <div class="card-body text-center">
                            <i class="fas fa-server fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Web Server</h5>
                            <p class="card-text">
                                <span class="status-indicator status-online"></span>
                                <strong>Online</strong>
                            </p>
                            <p class="card-text">
                                <small class="text-muted">Port: 8000</small>
                            </p>
                        </div>
                    </div>
                </div>

                <!-- API 상태 카드 -->
                <div class="col-md-4 mb-4">
                    <div class="card health-card">
                        <div class="card-body text-center">
                            <i class="fas fa-plug fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">API Services</h5>
                            <p class="card-text">
                                <span class="status-indicator status-online"></span>
                                <strong>Healthy</strong>
                            </p>
                            <p class="card-text">
                                <small class="text-muted">All endpoints active</small>
                            </p>
                        </div>
                    </div>
                </div>

                <!-- 데이터베이스 상태 카드 -->
                <div class="col-md-4 mb-4">
                    <div class="card health-card">
                        <div class="card-body text-center">
                            <i class="fas fa-database fa-3x text-info mb-3"></i>
                            <h5 class="card-title">Data Storage</h5>
                            <p class="card-text">
                                <span class="status-indicator status-online"></span>
                                <strong>Connected</strong>
                            </p>
                            <p class="card-text">
                                <small class="text-muted">SQLite Database</small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- 서비스 상세 정보 -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-info-circle"></i> Service Details</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>System Information</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Service Name:</strong> Energy Analysis Web Interface</li>
                                        <li><strong>Version:</strong> 2.0.0</li>
                                        <li><strong>Status:</strong> <span class="badge bg-success">Running</span></li>
                                        <li><strong>Uptime:</strong> <span id="uptime">Calculating...</span></li>
                                        <li><strong>Last Update:</strong> <span id="lastUpdate"></span></li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>API Endpoints</h6>
                                    <ul class="list-unstyled">
                                        <li><span class="status-indicator status-online"></span> /api/health</li>
                                        <li><span class="status-indicator status-online"></span> /api/dashboard</li>
                                        <li><span class="status-indicator status-online"></span> /api/models</li>
                                        <li><span class="status-indicator status-online"></span> /api/statistics</li>
                                        <li><span class="status-indicator status-online"></span> /api/languages</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 업타임 계산
            function updateUptime() {{
                const startTime = new Date('2025-10-11T01:22:47Z'); // 서비스 시작 시간
                const now = new Date();
                const diff = now - startTime;
                
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById('uptime').textContent = `${{hours}}h ${{minutes}}m ${{seconds}}s`;
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                updateUptime();
                setInterval(updateUptime, 1000);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/model-testing", response_class=HTMLResponse)
async def model_testing_page(request: Request, lang: str = Query("ko", description="Language code")):
    """ML/AI Engine 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🧠 ML/AI Engine</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .model-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .model-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            }}
            .performance-controls {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .model-selection {{
                margin-bottom: 20px;
            }}
            .form-check {{
                padding: 10px;
                border: 2px solid transparent;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            .form-check:hover {{
                background: #f8f9fa;
                border-color: #e9ecef;
            }}
            .form-check-input:checked + .form-check-label {{
                color: #007bff;
            }}
            .form-check:has(.form-check-input:checked) {{
                background: #e3f2fd;
                border-color: #2196f3;
            }}
            .model-actions .btn {{
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }}
            .model-actions .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            .selected-model-info {{
                animation: fadeIn 0.5s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .metric-card h6 {{
                color: #333;
                margin-bottom: 15px;
                font-weight: bold;
            }}
            .mcp-model-card {{
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
                cursor: pointer;
                background: #fff;
            }}
            .mcp-model-card:hover {{
                border-color: #007bff;
                box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
                transform: translateY(-2px);
            }}
            .mcp-model-card.selected {{
                border-color: #28a745;
                background: #f8fff9;
                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
            }}
            .mcp-model-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .mcp-model-name {{
                font-weight: bold;
                font-size: 1.1rem;
                color: #333;
                margin: 0;
            }}
            .mcp-model-accuracy {{
                background: #28a745;
                color: white;
                padding: 4px 8px;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .mcp-model-description {{
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 10px;
            }}
            .mcp-model-tools {{
                margin-top: 10px;
            }}
            .mcp-tool-item {{
                background: #f8f9fa;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 5px;
                font-size: 0.8rem;
                color: #495057;
                display: inline-block;
            }}
            .mcp-model-status {{
                display: flex;
                align-items: center;
                margin-top: 10px;
            }}
            .status-indicator {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 5px;
            }}
            .status-active {{
                background: #28a745;
            }}
            .status-inactive {{
                background: #dc3545;
            }}
            .selected-mcp-model {{
                min-height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .mcp-model-selection {{
                background: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .mcp-model-selection h6 {{
                color: #1976d2;
                margin-bottom: 10px;
            }}
            .mcp-model-details {{
                font-size: 0.9rem;
                color: #666;
            }}
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-brain"></i> <span data-translate="nav_ml_ai">ML/AI Engine</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> <span data-translate="nav_home">Dashboard</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- ML 모델 카드들 -->
                <div class="col-md-4 mb-4">
                    <div class="card model-card">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Energy Prediction</h5>
                            <p class="card-text">LSTM 기반 에너지 소비 예측 모델</p>
                            <div class="mb-3">
                                <span class="badge bg-success">Active</span>
                                <span class="badge bg-info">Accuracy: 95.2%</span>
                            </div>
                            <button class="btn btn-primary btn-sm">Test Model</button>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card model-card">
                        <div class="card-body text-center">
                            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Anomaly Detection</h5>
                            <p class="card-text">Isolation Forest 기반 이상 탐지</p>
                            <div class="mb-3">
                                <span class="badge bg-success">Active</span>
                                <span class="badge bg-info">F1-Score: 92.1%</span>
                            </div>
                            <button class="btn btn-warning btn-sm">Test Model</button>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card model-card">
                        <div class="card-body text-center">
                            <i class="fas fa-cloud-sun fa-3x text-info mb-3"></i>
                            <h5 class="card-title">Climate Prediction</h5>
                            <p class="card-text">DeepMind 기반 기후 예측 모델</p>
                            <div class="mb-3">
                                <span class="badge bg-success">Active</span>
                                <span class="badge bg-info">MAE: 0.8°C</span>
                            </div>
                            <button class="btn btn-info btn-sm">Test Model</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MCP 모델 선택 섹션 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-robot"></i> MCP Model Selection</h5>
                            <p class="card-text">등록된 MCP (Model Context Protocol) 모델들을 선택하고 배포할 수 있습니다.</p>
                            
                            <!-- MCP 모델 카테고리 탭 -->
                            <ul class="nav nav-tabs" id="mcpModelTabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" id="forecasting-tab" data-bs-toggle="tab" data-bs-target="#forecasting" type="button" role="tab">
                                        <i class="fas fa-chart-line"></i> Forecasting
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="analysis-tab" data-bs-toggle="tab" data-bs-target="#analysis" type="button" role="tab">
                                        <i class="fas fa-analytics"></i> Analysis
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="anomaly-tab" data-bs-toggle="tab" data-bs-target="#anomaly" type="button" role="tab">
                                        <i class="fas fa-exclamation-triangle"></i> Anomaly
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="climate-tab" data-bs-toggle="tab" data-bs-target="#climate" type="button" role="tab">
                                        <i class="fas fa-cloud-sun"></i> Climate
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="deeplearning-tab" data-bs-toggle="tab" data-bs-target="#deeplearning" type="button" role="tab">
                                        <i class="fas fa-brain"></i> Deep Learning
                                    </button>
                                </li>
                            </ul>
                            
                            <!-- MCP 모델 탭 콘텐츠 -->
                            <div class="tab-content" id="mcpModelTabsContent">
                                <!-- Forecasting Models -->
                                <div class="tab-pane fade show active" id="forecasting" role="tabpanel">
                                    <div class="row mt-3" id="forecastingModels">
                                        <!-- MCP 모델들이 여기에 동적으로 로드됩니다 -->
                                    </div>
                                </div>
                                
                                <!-- Analysis Models -->
                                <div class="tab-pane fade" id="analysis" role="tabpanel">
                                    <div class="row mt-3" id="analysisModels">
                                        <!-- MCP 모델들이 여기에 동적으로 로드됩니다 -->
                                    </div>
                                </div>
                                
                                <!-- Anomaly Models -->
                                <div class="tab-pane fade" id="anomaly" role="tabpanel">
                                    <div class="row mt-3" id="anomalyModels">
                                        <!-- MCP 모델들이 여기에 동적으로 로드됩니다 -->
                                    </div>
                                </div>
                                
                                <!-- Climate Models -->
                                <div class="tab-pane fade" id="climate" role="tabpanel">
                                    <div class="row mt-3" id="climateModels">
                                        <!-- MCP 모델들이 여기에 동적으로 로드됩니다 -->
                                    </div>
                                </div>
                                
                                <!-- Deep Learning Models -->
                                <div class="tab-pane fade" id="deeplearning" role="tabpanel">
                                    <div class="row mt-3" id="deeplearningModels">
                                        <!-- MCP 모델들이 여기에 동적으로 로드됩니다 -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 지표 그래프 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-chart-line"></i> Model Performance Metrics</h5>
                            <div class="row">
                                <div class="col-lg-8">
                                    <canvas id="performanceChart" height="400"></canvas>
                                </div>
                                <div class="col-lg-4">
                                    <div class="performance-controls">
                                        <h6><strong>Selected MCP Model</strong></h6>
                                        <div class="selected-mcp-model" id="selectedMCPModel">
                                            <div class="alert alert-info">
                                                <i class="fas fa-info-circle"></i> MCP 모델을 선택해주세요
                                            </div>
                                        </div>
                                        
                                        <div class="model-actions mt-4">
                                            <button class="btn btn-primary w-100 mb-2" onclick="selectMCPModel()" id="selectMCPBtn" disabled>
                                                <i class="fas fa-check"></i> Select MCP Model
                                            </button>
                                            <button class="btn btn-success w-100 mb-2" onclick="deployMCPModel()" id="deployMCPBtn" disabled>
                                                <i class="fas fa-rocket"></i> Deploy MCP Model
                                            </button>
                                            <button class="btn btn-info w-100" onclick="testMCPModel()" id="testMCPBtn" disabled>
                                                <i class="fas fa-flask"></i> Test MCP Model
                                            </button>
                                        </div>
                                        
                                        <div class="selected-model-info mt-3" id="selectedModelInfo" style="display: none;">
                                            <div class="alert alert-success">
                                                <h6><i class="fas fa-check-circle"></i> Selected Model</h6>
                                                <div id="selectedModelName"></div>
                                                <div id="selectedModelMetrics"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 상세 분석 -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-analytics"></i> Detailed Performance Analysis</h5>
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="metric-card">
                                        <h6>Accuracy Trends</h6>
                                        <canvas id="accuracyChart" height="200"></canvas>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="metric-card">
                                        <h6>Training Loss</h6>
                                        <canvas id="lossChart" height="200"></canvas>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="metric-card">
                                        <h6>Inference Time</h6>
                                        <canvas id="inferenceChart" height="200"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-cogs"></i> Model Management</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Active Models</h6>
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Energy Prediction LSTM
                                            <span class="badge bg-primary rounded-pill">v2.1.0</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Anomaly Detection Forest
                                            <span class="badge bg-primary rounded-pill">v1.8.2</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Climate Prediction DeepMind
                                            <span class="badge bg-primary rounded-pill">v3.0.1</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>Model Performance</h6>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 95%">Energy Prediction: 95%</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 92%">Anomaly Detection: 92%</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-info" role="progressbar" style="width: 88%">Climate Prediction: 88%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 모델 성능 지표 그래프 생성
            function createPerformanceChart() {{
                const ctx = document.getElementById('performanceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
                        datasets: [{{
                            label: 'Energy Prediction Accuracy',
                            data: [92.1, 93.5, 94.2, 95.1, 95.8, 96.2, 95.9, 95.2],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}, {{
                            label: 'Anomaly Detection F1-Score',
                            data: [88.5, 89.2, 90.1, 91.3, 92.0, 92.5, 92.1, 92.1],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}, {{
                            label: 'Climate Prediction MAE',
                            data: [1.2, 1.1, 1.0, 0.9, 0.8, 0.8, 0.8, 0.8],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y1'
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
                                    text: 'Accuracy / F1-Score (%)'
                                }},
                                min: 85,
                                max: 100
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'MAE (°C)'
                                }},
                                min: 0.5,
                                max: 1.5,
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                            title: {{
                                display: true,
                                text: 'Model Performance Over Time'
                            }}
                        }}
                    }}
                }});
            }}

            // 정확도 트렌드 차트
            function createAccuracyChart() {{
                const ctx = document.getElementById('accuracyChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Epoch 1', 'Epoch 5', 'Epoch 10', 'Epoch 15', 'Epoch 20', 'Epoch 25', 'Epoch 30'],
                        datasets: [{{
                            label: 'Training Accuracy',
                            data: [75.2, 82.1, 87.5, 91.2, 93.8, 95.1, 95.2],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Validation Accuracy',
                            data: [73.8, 80.5, 85.9, 89.7, 92.3, 94.1, 94.8],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
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
                        }}
                    }}
                }});
            }}

            // 훈련 손실 차트
            function createLossChart() {{
                const ctx = document.getElementById('lossChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Epoch 1', 'Epoch 5', 'Epoch 10', 'Epoch 15', 'Epoch 20', 'Epoch 25', 'Epoch 30'],
                        datasets: [{{
                            label: 'Training Loss',
                            data: [2.5, 1.8, 1.2, 0.8, 0.5, 0.3, 0.2],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Validation Loss',
                            data: [2.6, 1.9, 1.3, 0.9, 0.6, 0.4, 0.3],
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
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
            }}

            // 추론 시간 차트
            function createInferenceChart() {{
                const ctx = document.getElementById('inferenceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Energy Prediction', 'Anomaly Detection', 'Climate Prediction'],
                        datasets: [{{
                            label: 'Inference Time (ms)',
                            data: [45, 23, 67],
                            backgroundColor: ['#007bff', '#28a745', '#dc3545']
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
            }}

            // 모델 선택 함수
            function selectModel() {{
                const selectedModel = document.querySelector('input[name="modelType"]:checked');
                const modelInfo = document.getElementById('selectedModelInfo');
                const modelName = document.getElementById('selectedModelName');
                const modelMetrics = document.getElementById('selectedModelMetrics');
                
                if (selectedModel) {{
                    const modelData = {{
                        energy: {{
                            name: 'Energy Prediction LSTM v2.1.0',
                            metrics: 'Accuracy: 95.2% | F1-Score: 94.8% | Inference: 45ms'
                        }},
                        anomaly: {{
                            name: 'Anomaly Detection Forest v1.8.2',
                            metrics: 'F1-Score: 92.1% | Precision: 91.5% | Recall: 92.7%'
                        }},
                        climate: {{
                            name: 'Climate Prediction DeepMind v3.0.1',
                            metrics: 'MAE: 0.8°C | RMSE: 1.2°C | R²: 0.94'
                        }}
                    }};
                    
                    const data = modelData[selectedModel.value];
                    modelName.textContent = data.name;
                    modelMetrics.textContent = data.metrics;
                    modelInfo.style.display = 'block';
                    
                    showNotification(`${{data.name}} selected successfully!`, 'success');
                }}
            }}

            // 모델 배포 함수
            function deployModel() {{
                const selectedModel = document.querySelector('input[name="modelType"]:checked');
                if (selectedModel) {{
                    const modelNames = {{
                        energy: 'Energy Prediction LSTM',
                        anomaly: 'Anomaly Detection Forest',
                        climate: 'Climate Prediction DeepMind'
                    }};
                    
                    showNotification(`${{modelNames[selectedModel.value]}} deployed successfully!`, 'success');
                }} else {{
                    showNotification('Please select a model first!', 'warning');
                }}
            }}

            // 모델 비교 함수
            function compareModels() {{
                showNotification('Opening model comparison dashboard...', 'info');
            }}

            // MCP 모델 로드 함수
            async function loadMCPModels() {{
                try {{
                    const response = await fetch('/api/mcp-models');
                    const data = await response.json();
                    
                    if (data.success) {{
                        displayMCPModels(data.models);
                    }} else {{
                        console.error('Failed to load MCP models:', data.error);
                    }}
                }} catch (error) {{
                    console.error('Error loading MCP models:', error);
                }}
            }}

            // MCP 모델 표시 함수
            function displayMCPModels(models) {{
                const categories = {{
                    'forecasting': 'forecastingModels',
                    'analysis': 'analysisModels',
                    'anomaly': 'anomalyModels',
                    'climate': 'climateModels',
                    'deep_learning': 'deeplearningModels'
                }};

                Object.keys(models).forEach(modelKey => {{
                    const model = models[modelKey];
                    const category = model.category;
                    const containerId = categories[category];
                    
                    if (containerId) {{
                        const container = document.getElementById(containerId);
                        if (container) {{
                            const modelCard = createMCPModelCard(modelKey, model);
                            container.appendChild(modelCard);
                        }}
                    }}
                }});
            }}

            // MCP 모델 카드 생성 함수
            function createMCPModelCard(modelKey, model) {{
                const col = document.createElement('div');
                col.className = 'col-md-6 col-lg-4';
                
                const toolsHtml = model.tools.map(tool => 
                    `<span class="mcp-tool-item">${{tool.name}}</span>`
                ).join('');
                
                col.innerHTML = `
                    <div class="mcp-model-card" onclick="selectMCPModelCard('${{modelKey}}', this)" data-model-key="${{modelKey}}">
                        <div class="mcp-model-header">
                            <h6 class="mcp-model-name">${{model.name}}</h6>
                            <span class="mcp-model-accuracy">${{model.accuracy}}%</span>
                        </div>
                        <div class="mcp-model-description">${{model.description}}</div>
                        <div class="mcp-model-tools">
                            ${{toolsHtml}}
                        </div>
                        <div class="mcp-model-status">
                            <span class="status-indicator status-${{model.status}}"></span>
                            <small>${{model.status === 'active' ? 'Active' : 'Inactive'}}</small>
                        </div>
                    </div>
                `;
                
                return col;
            }}

            // MCP 모델 카드 선택 함수
            function selectMCPModelCard(modelKey, element) {{
                // 모든 카드에서 선택 상태 제거
                document.querySelectorAll('.mcp-model-card').forEach(card => {{
                    card.classList.remove('selected');
                }});
                
                // 선택된 카드에 선택 상태 추가
                element.classList.add('selected');
                
                // 선택된 모델 정보 업데이트
                window.selectedMCPModel = modelKey;
                
                // 버튼 활성화
                document.getElementById('selectMCPBtn').disabled = false;
                document.getElementById('deployMCPBtn').disabled = false;
                document.getElementById('testMCPBtn').disabled = false;
                
                // 선택된 모델 정보 표시
                updateSelectedMCPModel(modelKey);
            }}

            // 선택된 MCP 모델 정보 업데이트
            function updateSelectedMCPModel(modelKey) {{
                const container = document.getElementById('selectedMCPModel');
                container.innerHTML = `
                    <div class="mcp-model-selection">
                        <h6><i class="fas fa-robot"></i> Selected MCP Model</h6>
                        <div class="mcp-model-details">
                            <strong>${{modelKey}}</strong><br>
                            <small>Model Context Protocol Model</small>
                        </div>
                    </div>
                `;
            }}

            // MCP 모델 선택 함수
            async function selectMCPModel() {{
                if (!window.selectedMCPModel) {{
                    showNotification('Please select a MCP model first!', 'warning');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/select-mcp-model', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            model_name: window.selectedMCPModel,
                            model_type: 'mcp'
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        showNotification(data.message, 'success');
                        document.getElementById('selectedModelInfo').style.display = 'block';
                        document.getElementById('selectedModelName').textContent = data.selected_model.name;
                        document.getElementById('selectedModelMetrics').textContent = `Type: ${{data.selected_model.type}} | Status: ${{data.selected_model.status}}`;
                    }} else {{
                        showNotification(data.error, 'error');
                    }}
                }} catch (error) {{
                    showNotification('Error selecting MCP model: ' + error.message, 'error');
                }}
            }}

            // MCP 모델 배포 함수
            async function deployMCPModel() {{
                if (!window.selectedMCPModel) {{
                    showNotification('Please select a MCP model first!', 'warning');
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/deploy-mcp-model', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            model_name: window.selectedMCPModel,
                            model_type: 'mcp'
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        showNotification(data.message, 'success');
                        console.log('Deployment info:', data.deployment);
                    }} else {{
                        showNotification(data.error, 'error');
                    }}
                }} catch (error) {{
                    showNotification('Error deploying MCP model: ' + error.message, 'error');
                }}
            }}

            // MCP 모델 테스트 함수
            function testMCPModel() {{
                if (!window.selectedMCPModel) {{
                    showNotification('Please select a MCP model first!', 'warning');
                    return;
                }}
                
                showNotification(`Testing MCP model: ${{window.selectedMCPModel}}`, 'info');
                // 실제 구현에서는 모델 테스트 로직을 실행
            }}

            // 알림 표시 함수
            function showNotification(message, type) {{
                const notification = document.createElement('div');
                notification.className = `alert alert-${{type}} alert-dismissible fade show position-fixed`;
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
                }}, 3000);
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                createPerformanceChart();
                createAccuracyChart();
                createLossChart();
                createInferenceChart();
                loadMCPModels();
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/data-analysis", response_class=HTMLResponse)
async def data_analysis_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Energy Demand Monitoring 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Energy Demand Monitoring</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .analysis-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .analysis-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            }}
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-chart-bar"></i> <span data-translate="card_demand">Energy Demand Monitoring</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> <span data-translate="nav_home">Dashboard</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- 데이터 품질 카드들 -->
                <div class="col-md-3 mb-4">
                    <div class="card analysis-card">
                        <div class="card-body text-center">
                            <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Data Completeness</h5>
                            <h2 class="text-success">98.5%</h2>
                            <p class="card-text">완전성</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card analysis-card">
                        <div class="card-body text-center">
                            <i class="fas fa-bullseye fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Data Accuracy</h5>
                            <h2 class="text-primary">96.2%</h2>
                            <p class="card-text">정확성</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card analysis-card">
                        <div class="card-body text-center">
                            <i class="fas fa-sync-alt fa-3x text-info mb-3"></i>
                            <h5 class="card-title">Data Consistency</h5>
                            <h2 class="text-info">94.8%</h2>
                            <p class="card-text">일관성</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3 mb-4">
                    <div class="card analysis-card">
                        <div class="card-body text-center">
                            <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Data Freshness</h5>
                            <h2 class="text-warning">99.1%</h2>
                            <p class="card-text">신선도</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> Energy Demand Analysis</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Current Demand Metrics</h6>
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Peak Demand
                                            <span class="badge bg-danger rounded-pill">125.3 kW</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Average Demand
                                            <span class="badge bg-primary rounded-pill">87.2 kW</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Base Load
                                            <span class="badge bg-success rounded-pill">45.8 kW</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>Demand Patterns</h6>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-danger" role="progressbar" style="width: 85%">Peak Hours: 85%</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-primary" role="progressbar" style="width: 70%">Normal Hours: 70%</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 40%">Off-Peak: 40%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 전력량계 모니터링 섹션 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-tachometer-alt"></i> Power Meter Monitoring</h5>
                            <p class="card-text">전력량계 설치 후 실시간 전력 사용량 모니터링 및 분석</p>
                            
                            <!-- 전력량계 상태 카드 -->
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="card bg-primary text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-bolt fa-2x mb-2"></i>
                                            <h6>Current Power</h6>
                                            <h4 id="currentPower">0.0 kW</h4>
                                            <small>실시간 전력</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-success text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-chart-line fa-2x mb-2"></i>
                                            <h6>Today's Usage</h6>
                                            <h4 id="todayUsage">0.0 kWh</h4>
                                            <small>오늘 사용량</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-warning text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-chart-bar fa-2x mb-2"></i>
                                            <h6>Peak Demand</h6>
                                            <h4 id="peakDemand">0.0 kW</h4>
                                            <small>최대 수요</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-info text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-percentage fa-2x mb-2"></i>
                                            <h6>Efficiency</h6>
                                            <h4 id="efficiency">0.0%</h4>
                                            <small>효율성</small>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 전력량계 모니터링 차트 -->
                            <div class="row">
                                <div class="col-lg-8">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-chart-line"></i> Real-time Power Consumption</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="powerMeterChart" height="300"></canvas>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-chart-pie"></i> Power Distribution</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="powerDistributionChart" height="300"></canvas>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 시간대별 전력 사용량 분석 -->
                            <div class="row mt-4">
                                <div class="col-lg-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-clock"></i> Hourly Power Usage Pattern</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="hourlyUsageChart" height="250"></canvas>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-calendar-day"></i> Daily Power Trend</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="dailyTrendChart" height="250"></canvas>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 전력량계 설정 및 제어 -->
                            <div class="row mt-4">
                                <div class="col-12">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-cogs"></i> Power Meter Settings & Control</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="row">
                                                <div class="col-md-4">
                                                    <div class="form-group">
                                                        <label for="meterInterval">Data Collection Interval</label>
                                                        <select class="form-control" id="meterInterval">
                                                            <option value="1">1 minute</option>
                                                            <option value="5" selected>5 minutes</option>
                                                            <option value="15">15 minutes</option>
                                                            <option value="30">30 minutes</option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div class="col-md-4">
                                                    <div class="form-group">
                                                        <label for="alertThreshold">Alert Threshold (kW)</label>
                                                        <input type="number" class="form-control" id="alertThreshold" value="100" step="0.1">
                                                    </div>
                                                </div>
                                                <div class="col-md-4">
                                                    <div class="form-group">
                                                        <label for="meterStatus">Meter Status</label>
                                                        <div class="btn-group w-100" role="group">
                                                            <button type="button" class="btn btn-success" id="startMeter">Start</button>
                                                            <button type="button" class="btn btn-warning" id="pauseMeter">Pause</button>
                                                            <button type="button" class="btn btn-danger" id="stopMeter">Stop</button>
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
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 전력량계 모니터링 변수
            let powerMeterChart = null;
            let powerDistributionChart = null;
            let hourlyUsageChart = null;
            let dailyTrendChart = null;
            let powerData = [];
            let isMeterRunning = false;

            // 전력량계 실시간 데이터 생성
            function generatePowerData() {{
                const now = new Date();
                const hour = now.getHours();
                
                // 시간대별 기본 패턴 (kW)
                let basePower = 50;
                if (hour >= 6 && hour <= 9) {{
                    basePower = 80 + Math.random() * 20; // 아침 피크
                }} else if (hour >= 18 && hour <= 22) {{
                    basePower = 90 + Math.random() * 30; // 저녁 피크
                }} else if (hour >= 22 || hour <= 6) {{
                    basePower = 30 + Math.random() * 15; // 야간
                }} else {{
                    basePower = 60 + Math.random() * 25; // 일반 시간
                }}
                
                return {{
                    timestamp: now.toISOString(),
                    power: Math.round(basePower * 100) / 100,
                    voltage: 220 + Math.random() * 10,
                    current: basePower / 220 + Math.random() * 0.5,
                    frequency: 60 + Math.random() * 0.2
                }};
            }}

            // 전력량계 차트 생성
            function createPowerMeterChart() {{
                const ctx = document.getElementById('powerMeterChart').getContext('2d');
                powerMeterChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: [],
                        datasets: [{{
                            label: 'Power (kW)',
                            data: [],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4,
                            fill: true
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
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Time'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true
                            }},
                            title: {{
                                display: true,
                                text: 'Real-time Power Consumption'
                            }}
                        }}
                    }}
                }});
            }}

            // 전력 분포 차트 생성
            function createPowerDistributionChart() {{
                const ctx = document.getElementById('powerDistributionChart').getContext('2d');
                powerDistributionChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Lighting', 'HVAC', 'Equipment', 'Other'],
                        datasets: [{{
                            data: [25, 35, 30, 10],
                            backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }},
                            title: {{
                                display: true,
                                text: 'Power Distribution'
                            }}
                        }}
                    }}
                }});
            }}

            // 시간대별 사용량 차트 생성
            function createHourlyUsageChart() {{
                const ctx = document.getElementById('hourlyUsageChart').getContext('2d');
                const hours = Array.from({{length: 24}}, (_, i) => i + ':00');
                const usage = hours.map(hour => {{
                    const h = parseInt(hour);
                    if (h >= 6 && h <= 9) return 80 + Math.random() * 20;
                    if (h >= 18 && h <= 22) return 90 + Math.random() * 30;
                    if (h >= 22 || h <= 6) return 30 + Math.random() * 15;
                    return 60 + Math.random() * 25;
                }});

                hourlyUsageChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: hours,
                        datasets: [{{
                            label: 'Power Usage (kW)',
                            data: usage,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
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
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Hour'
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 일별 트렌드 차트 생성
            function createDailyTrendChart() {{
                const ctx = document.getElementById('dailyTrendChart').getContext('2d');
                const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                const trend = days.map(() => 60 + Math.random() * 40);

                dailyTrendChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: days,
                        datasets: [{{
                            label: 'Daily Average (kW)',
                            data: trend,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
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
            }}

            // 전력량계 데이터 업데이트
            function updatePowerMeterData() {{
                if (!isMeterRunning) return;

                const newData = generatePowerData();
                powerData.push(newData);

                // 최근 30개 데이터만 유지
                if (powerData.length > 30) {{
                    powerData.shift();
                }}

                // 실시간 차트 업데이트
                if (powerMeterChart) {{
                    const labels = powerData.map(d => new Date(d.timestamp).toLocaleTimeString());
                    const data = powerData.map(d => d.power);
                    
                    powerMeterChart.data.labels = labels;
                    powerMeterChart.data.datasets[0].data = data;
                    powerMeterChart.update('none');
                }}

                // 상태 카드 업데이트
                document.getElementById('currentPower').textContent = newData.power.toFixed(1) + ' kW';
                
                // 오늘 사용량 계산 (간단한 시뮬레이션)
                const todayUsage = powerData.reduce((sum, d) => sum + d.power, 0) * 0.083; // 5분 간격
                document.getElementById('todayUsage').textContent = todayUsage.toFixed(1) + ' kWh';
                
                // 최대 수요 업데이트
                const maxPower = Math.max(...powerData.map(d => d.power));
                document.getElementById('peakDemand').textContent = maxPower.toFixed(1) + ' kW';
                
                // 효율성 계산 (간단한 시뮬레이션)
                const efficiency = Math.min(95, 70 + Math.random() * 25);
                document.getElementById('efficiency').textContent = efficiency.toFixed(1) + '%';
            }}

            // 전력량계 제어 함수들
            function startMeter() {{
                isMeterRunning = true;
                document.getElementById('startMeter').classList.add('active');
                document.getElementById('pauseMeter').classList.remove('active');
                document.getElementById('stopMeter').classList.remove('active');
                console.log('Power meter started');
            }}

            function pauseMeter() {{
                isMeterRunning = false;
                document.getElementById('startMeter').classList.remove('active');
                document.getElementById('pauseMeter').classList.add('active');
                document.getElementById('stopMeter').classList.remove('active');
                console.log('Power meter paused');
            }}

            function stopMeter() {{
                isMeterRunning = false;
                powerData = [];
                document.getElementById('startMeter').classList.remove('active');
                document.getElementById('pauseMeter').classList.remove('active');
                document.getElementById('stopMeter').classList.add('active');
                
                // 차트 초기화
                if (powerMeterChart) {{
                    powerMeterChart.data.labels = [];
                    powerMeterChart.data.datasets[0].data = [];
                    powerMeterChart.update();
                }}
                
                // 상태 카드 초기화
                document.getElementById('currentPower').textContent = '0.0 kW';
                document.getElementById('todayUsage').textContent = '0.0 kWh';
                document.getElementById('peakDemand').textContent = '0.0 kW';
                document.getElementById('efficiency').textContent = '0.0%';
                
                console.log('Power meter stopped');
            }}

            // 이벤트 리스너 등록
            document.getElementById('startMeter').addEventListener('click', startMeter);
            document.getElementById('pauseMeter').addEventListener('click', pauseMeter);
            document.getElementById('stopMeter').addEventListener('click', stopMeter);

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                
                // 전력량계 차트 생성
                createPowerMeterChart();
                createPowerDistributionChart();
                createHourlyUsageChart();
                createDailyTrendChart();
                
                // 전력량계 데이터 업데이트 (5초마다)
                setInterval(updatePowerMeterData, 5000);
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/data-collection", response_class=HTMLResponse)
async def data_collection_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Energy Supply Monitoring 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌞 Energy Supply Monitoring</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .supply-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .supply-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            }}
            
            /* 날씨 분석 스타일 */
            .weather-stat {{
                text-align: center;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-bottom: 10px;
            }}
            .stat-value {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 0.8rem;
                color: #6c757d;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .correlation-item {{
                text-align: center;
                padding: 8px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin-bottom: 5px;
            }}
            .correlation-value {{
                font-size: 1.1rem;
                font-weight: bold;
                color: #e74c3c;
                margin-bottom: 3px;
            }}
            .correlation-label {{
                font-size: 0.7rem;
                color: #6c757d;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-satellite-dish"></i> <span data-translate="card_supply">Energy Supply Monitoring</span>
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> <span data-translate="nav_home">Dashboard</span>
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <div class="row">
                <!-- 태양광 모니터링 카드들 -->
                <div class="col-md-4 mb-4">
                    <div class="card supply-card">
                        <div class="card-body text-center">
                            <i class="fas fa-sun fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Solar Generation</h5>
                            <h2 class="text-warning">3.25 kW</h2>
                            <p class="card-text">현재 발전량</p>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-warning" role="progressbar" style="width: 72%">72%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card supply-card">
                        <div class="card-body text-center">
                            <i class="fas fa-battery-half fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Energy Storage</h5>
                            <h2 class="text-success">85%</h2>
                            <p class="card-text">배터리 충전률</p>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" role="progressbar" style="width: 85%">85%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card supply-card">
                        <div class="card-body text-center">
                            <i class="fas fa-cloud-sun fa-3x text-info mb-3"></i>
                            <h5 class="card-title">Weather Data</h5>
                            <h2 class="text-info">24.5°C</h2>
                            <p class="card-text">현재 온도</p>
                            <small class="text-muted">습도: 65%</small>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-solar-panel"></i> Solar Energy Management System</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>PV Module Status</h6>
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Module 1
                                            <span class="badge bg-success rounded-pill">Active</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Module 2
                                            <span class="badge bg-success rounded-pill">Active</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Module 3
                                            <span class="badge bg-warning rounded-pill">Maintenance</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>Power Generation</h6>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 72%">Current: 3.25 kW</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-info" role="progressbar" style="width: 100%">Rated: 4.50 kW</div>
                                    </div>
                                    <div class="progress mb-2">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 85%">Today: 28.5 kWh</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- SPO 스타일 데이터 분석 차트 섹션 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> Power Data Analysis Platform</h5>
                            <p class="mb-0">Real-time energy data monitoring and analysis system</p>
                        </div>
                        <div class="card-body">
                            <!-- 실시간 상태 카드 -->
                            <div class="row mb-4">
                                <div class="col-md-3">
                                    <div class="card bg-warning text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-sun fa-2x mb-2"></i>
                                            <h6>Solar Power</h6>
                                            <h4 id="currentSolarPower">0.00 kW</h4>
                                            <small>Current Generation</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-success text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-battery-full fa-2x mb-2"></i>
                                            <h6>Battery SOC</h6>
                                            <h4 id="currentBatterySOC">0.0%</h4>
                                            <small>State of Charge</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-info text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-thermometer-half fa-2x mb-2"></i>
                                            <h6>Temperature</h6>
                                            <h4 id="currentTemperature">0.0°C</h4>
                                            <small>Ambient Temp</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="card bg-primary text-white">
                                        <div class="card-body text-center">
                                            <i class="fas fa-tint fa-2x mb-2"></i>
                                            <h6>Humidity</h6>
                                            <h4 id="currentHumidity">0.0%</h4>
                                            <small>Relative Humidity</small>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 메인 차트 영역 -->
                            <div class="row">
                                <div class="col-lg-8">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-chart-line"></i> Real-time Power Data Analysis</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="spoPowerDataChart" height="300"></canvas>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-chart-bar"></i> 24-Hour Energy Trend</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="spoEnergyTrendChart" height="300"></canvas>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 하단 분석 차트 -->
                            <div class="row mt-4">
                                <div class="col-lg-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-chart-line"></i> System Efficiency Analysis</h6>
                                        </div>
                                        <div class="card-body">
                                            <canvas id="spoEfficiencyChart" height="250"></canvas>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-cloud-sun"></i> Weather Data Analysis</h6>
                                        </div>
                                        <div class="card-body">
                                            <!-- 날씨 통계 요약 -->
                                            <div class="row mb-3">
                                                <div class="col-6">
                                                    <div class="weather-stat">
                                                        <div class="stat-value" id="avgTemperature">24.5°C</div>
                                                        <div class="stat-label">평균 온도</div>
                                                    </div>
                                                </div>
                                                <div class="col-6">
                                                    <div class="weather-stat">
                                                        <div class="stat-value" id="avgHumidity">65%</div>
                                                        <div class="stat-label">평균 습도</div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <div class="col-6">
                                                    <div class="weather-stat">
                                                        <div class="stat-value" id="maxWindSpeed">2.3 m/s</div>
                                                        <div class="stat-label">최대 풍속</div>
                                                    </div>
                                                </div>
                                                <div class="col-6">
                                                    <div class="weather-stat">
                                                        <div class="stat-value" id="solarIrradiance">850 W/m²</div>
                                                        <div class="stat-label">태양 복사량</div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <!-- 현황/예측 시계열 차트 -->
                                            <canvas id="spoWeatherChart" height="250"></canvas>
                                            
                                            <!-- 에너지 상관관계 분석 -->
                                            <div class="mt-3">
                                                <h6 class="text-muted mb-2">에너지 상관관계</h6>
                                                <div class="row">
                                                    <div class="col-4">
                                                        <div class="correlation-item">
                                                            <div class="correlation-value" id="tempCorrelation">0.78</div>
                                                            <div class="correlation-label">온도 vs 소비</div>
                                                        </div>
                                                    </div>
                                                    <div class="col-4">
                                                        <div class="correlation-item">
                                                            <div class="correlation-value" id="solarCorrelation">0.92</div>
                                                            <div class="correlation-label">태양광 vs 발전</div>
                                                        </div>
                                                    </div>
                                                    <div class="col-4">
                                                        <div class="correlation-item">
                                                            <div class="correlation-value" id="humidityCorrelation">-0.45</div>
                                                            <div class="correlation-label">습도 vs 효율</div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 데이터 테이블 -->
                            <div class="row mt-4">
                                <div class="col-12">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6><i class="fas fa-table"></i> Real-time Data Table</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="table-responsive">
                                                <table class="table table-striped table-hover">
                                                    <thead class="table-dark">
                                                        <tr>
                                                            <th>Timestamp</th>
                                                            <th>Solar Power (kW)</th>
                                                            <th>Battery SOC (%)</th>
                                                            <th>Temperature (°C)</th>
                                                            <th>Humidity (%)</th>
                                                            <th>Wind Speed (m/s)</th>
                                                            <th>Irradiance (W/m²)</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody id="dataTableBody">
                                                        <tr>
                                                            <td colspan="7" class="text-center">Loading data...</td>
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
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/llm-slm", response_class=HTMLResponse)
async def llm_slm_page(request: Request, lang: str = Query("ko", description="Language code")):
    """LLM 기반 에너지 SLM 개발 페이지"""
    # 언어 설정
    if lang not in get_available_languages():
        lang = "ko"
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 LLM-based Energy SLM Development</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js?v=2.0"></script>
        <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/loader.js"></script>
        <style>
            .llm-card {{
                transition: transform 0.2s;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .llm-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            }}
            .prompt-card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .code-editor {{
                height: 300px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .model-status {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .status-training {{ background-color: #ffc107; color: #000; }}
            .status-ready {{ background-color: #28a745; color: white; }}
            .status-error {{ background-color: #dc3545; color: white; }}
            .status-idle {{ background-color: #6c757d; color: white; }}
            .progress-custom {{
                height: 8px;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.2);
            }}
            .progress-bar-custom {{
                background: linear-gradient(90deg, #28a745, #20c997);
                border-radius: 4px;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin-bottom: 15px;
            }}
            .metric-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .metric-label {{
                font-size: 0.9rem;
                opacity: 0.8;
            }}
            .phone-mockup {{
                display: inline-block;
                width: 200px;
                height: 400px;
                background: #333;
                border-radius: 25px;
                padding: 10px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                position: relative;
            }}
            .phone-screen {{
                width: 100%;
                height: 100%;
                background: #fff;
                border-radius: 20px;
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }}
            .phone-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .phone-content {{
                flex: 1;
                padding: 15px;
                font-size: 0.7rem;
                overflow-y: auto;
            }}
            .phone-footer {{
                padding: 10px;
                text-align: center;
                background: #f8f9fa;
            }}
            .progress-chart {{
                display: flex;
                align-items: end;
                height: 80px;
                gap: 5px;
                margin: 10px 0;
            }}
            .chart-bar {{
                flex: 1;
                border-radius: 3px 3px 0 0;
                min-height: 20px;
            }}
            .notification-list {{
                margin-bottom: 15px;
            }}
            .notification-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 5px;
            }}
            .notification-item i {{
                margin-right: 8px;
                width: 16px;
            }}
            .status-indicators {{
                margin-top: 10px;
            }}
            .status-item {{
                display: flex;
                align-items: center;
                margin-bottom: 5px;
                font-size: 0.6rem;
            }}
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .status-online {{ background-color: #28a745; }}
            .status-warning {{ background-color: #ffc107; }}
            .status-offline {{ background-color: #dc3545; }}
            .simulator-container {{
                margin-bottom: 20px;
            }}
            .interactive-phone {{
                display: inline-block;
                width: 100%;
                max-width: 300px;
                background: #333;
                border-radius: 25px;
                padding: 10px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                position: relative;
            }}
            .interactive-chart {{
                margin: 15px 0;
            }}
            .chart-container {{
                display: flex;
                align-items: end;
                height: 120px;
                gap: 8px;
                margin: 10px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            .chart-bar.interactive {{
                flex: 1;
                position: relative;
                cursor: pointer;
                transition: all 0.3s ease;
                border-radius: 4px 4px 0 0;
            }}
            .chart-bar.interactive:hover {{
                transform: scale(1.05);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            .bar-fill {{
                width: 100%;
                border-radius: 4px 4px 0 0;
                transition: height 0.5s ease;
                position: relative;
            }}
            .bar-label {{
                position: absolute;
                bottom: -20px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 0.7rem;
                font-weight: bold;
                color: #333;
            }}
            .bar-value {{
                position: absolute;
                top: -25px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 0.8rem;
                font-weight: bold;
                color: #333;
                background: rgba(255, 255, 255, 0.9);
                padding: 2px 6px;
                border-radius: 10px;
            }}
            .carbon-credits {{
                margin-top: 10px;
                text-align: center;
                color: #28a745;
                font-weight: bold;
            }}
            .notification-system {{
                margin-bottom: 15px;
            }}
            .notification-item.interactive {{
                cursor: pointer;
                transition: all 0.3s ease;
                border-radius: 8px;
                position: relative;
            }}
            .notification-item.interactive:hover {{
                background: #e3f2fd;
                transform: translateX(5px);
            }}
            .notification-count {{
                position: absolute;
                right: 10px;
                background: #dc3545;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.7rem;
                font-weight: bold;
            }}
            .power-status {{
                margin-top: 15px;
            }}
            .status-grid {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .status-card.interactive {{
                display: flex;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }}
            .status-card.interactive:hover {{
                background: #e3f2fd;
                border-color: #2196f3;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .status-card.interactive.active {{
                background: #e8f5e8;
                border-color: #28a745;
            }}
            .status-indicator {{
                margin-right: 10px;
            }}
            .status-info {{
                flex: 1;
            }}
            .status-label {{
                font-weight: bold;
                font-size: 0.8rem;
                color: #333;
            }}
            .status-value {{
                font-size: 0.9rem;
                color: #666;
            }}
            .status-control {{
                margin-left: 10px;
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }}
            .status-control.active {{
                color: #28a745;
            }}
            .control-panel {{
                margin-top: 15px;
                display: flex;
                gap: 10px;
                justify-content: center;
            }}
            .control-panel .btn {{
                flex: 1;
                max-width: 120px;
            }}
            .performance-controls {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .model-selection {{
                margin-bottom: 20px;
            }}
            .form-check {{
                padding: 10px;
                border: 2px solid transparent;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            .form-check:hover {{
                background: #f8f9fa;
                border-color: #e9ecef;
            }}
            .form-check-input:checked + .form-check-label {{
                color: #007bff;
            }}
            .form-check:has(.form-check-input:checked) {{
                background: #e3f2fd;
                border-color: #2196f3;
            }}
            .model-actions .btn {{
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }}
            .model-actions .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }}
            .selected-model-info {{
                animation: fadeIn 0.5s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .metric-card h6 {{
                color: #333;
                margin-bottom: 15px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <nav class="navbar navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand mb-0 h1">
                    <i class="fas fa-robot"></i> LLM-based Energy SLM Development
                </span>
                <div class="navbar-nav ms-auto d-flex flex-row">
                    <a href="/?lang={lang}" class="btn btn-outline-light btn-sm me-2">
                        <i class="fas fa-home"></i> Dashboard
                    </a>
                    <!-- 언어 선택 드롭다운 -->
                    <div class="dropdown">
                        <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe"></i> <span id="currentLanguage">{get_language_name(lang)}</span>
                        </button>
                        <ul class="dropdown-menu" aria-labelledby="languageDropdown">
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('ko')">🇰🇷 한국어</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">🇺🇸 English</a></li>
                            <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">🇨🇳 中文</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </nav>

        <div class="container-fluid mt-4">
            <!-- 모델 상태 대시보드 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="llm-card">
                        <div class="card-body">
                            <h4 class="card-title">
                                <i class="fas fa-brain"></i> Energy SLM Model Status
                                <span class="model-status status-ready" id="modelStatus">Ready</span>
                            </h4>
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="metric-card">
                                        <div class="metric-value" id="modelAccuracy">94.2%</div>
                                        <div class="metric-label">Accuracy</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card">
                                        <div class="metric-value" id="trainingProgress">100%</div>
                                        <div class="metric-label">Training Progress</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card">
                                        <div class="metric-value" id="inferenceTime">45ms</div>
                                        <div class="metric-label">Inference Time</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="metric-card">
                                        <div class="metric-value" id="modelSize">2.3B</div>
                                        <div class="metric-label">Parameters</div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <div class="progress progress-custom">
                                        <div class="progress-bar progress-bar-custom" role="progressbar" style="width: 100%" id="trainingProgressBar"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 프롬프트 엔지니어링 & 파인 튜닝 -->
            <div class="row">
                <!-- 프롬프트 엔지니어링 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-edit"></i> Prompt Engineering</h5>
                        <div class="mb-3">
                            <label class="form-label"><strong>System Prompt</strong></label>
                            <div id="systemPromptEditor" class="code-editor" style="height: 200px;"></div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>User Prompt Template</strong></label>
                            <div id="userPromptEditor" class="code-editor" style="height: 200px;"></div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label"><strong>Few-shot Examples</strong></label>
                            <div id="fewShotEditor" class="code-editor" style="height: 200px;"></div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <button class="btn btn-primary w-100" onclick="testPrompt()">
                                    <i class="fas fa-play"></i> Test Prompt
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-success w-100" onclick="savePrompt()">
                                    <i class="fas fa-save"></i> Save Prompt
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 파인 튜닝 관리 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-cogs"></i> Fine-tuning Management</h5>
                        <div class="mb-3">
                            <label class="form-label"><strong>Training Configuration</strong></label>
                            <div id="trainingConfigEditor" class="code-editor" style="height: 200px;"></div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label"><strong>Learning Rate</strong></label>
                                <input type="number" class="form-control" id="learningRate" value="0.0001" step="0.0001">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label"><strong>Batch Size</strong></label>
                                <input type="number" class="form-control" id="batchSize" value="8">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label"><strong>Epochs</strong></label>
                                <input type="number" class="form-control" id="epochs" value="10">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label"><strong>Warmup Steps</strong></label>
                                <input type="number" class="form-control" id="warmupSteps" value="100">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <button class="btn btn-warning w-100" onclick="startTraining()">
                                    <i class="fas fa-play-circle"></i> Start Training
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-danger w-100" onclick="stopTraining()">
                                    <i class="fas fa-stop-circle"></i> Stop Training
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 인터랙티브 시뮬레이터 섹션 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="prompt-card">
                        <h5><i class="fas fa-mobile-alt"></i> Interactive Simulator</h5>
                        <div class="row">
                            <!-- Progress Monitoring Simulator -->
                            <div class="col-md-6">
                                <div class="simulator-container">
                                    <h6><strong>Progress Monitoring and Progress Automation</strong></h6>
                                    <div class="interactive-phone">
                                        <div class="phone-header">
                                            <h6>RE700 Progress Monitoring and Progress Automation</h6>
                                        </div>
                                        <div class="phone-content">
                                            <p>We have adopted new initiatives to improve energy efficiency and reduce carbon footprint.</p>
                                            
                                            <!-- 인터랙티브 진행률 차트 -->
                                            <div class="interactive-chart">
                                                <h6>Energy Efficiency Progress</h6>
                                                <div class="chart-container">
                                                    <div class="chart-bar interactive" data-category="Solar" data-value="75" onclick="updateProgress('solar')">
                                                        <div class="bar-fill" style="height: 75%; background: linear-gradient(45deg, #28a745, #20c997);"></div>
                                                        <div class="bar-label">Solar</div>
                                                        <div class="bar-value">75%</div>
                                                    </div>
                                                    <div class="chart-bar interactive" data-category="Wind" data-value="85" onclick="updateProgress('wind')">
                                                        <div class="bar-fill" style="height: 85%; background: linear-gradient(45deg, #007bff, #0056b3);"></div>
                                                        <div class="bar-label">Wind</div>
                                                        <div class="bar-value">85%</div>
                                                    </div>
                                                    <div class="chart-bar interactive" data-category="Storage" data-value="60" onclick="updateProgress('storage')">
                                                        <div class="bar-fill" style="height: 60%; background: linear-gradient(45deg, #ffc107, #e0a800);"></div>
                                                        <div class="bar-label">Storage</div>
                                                        <div class="bar-value">60%</div>
                                                    </div>
                                                    <div class="chart-bar interactive" data-category="Grid" data-value="90" onclick="updateProgress('grid')">
                                                        <div class="bar-fill" style="height: 90%; background: linear-gradient(45deg, #dc3545, #c82333);"></div>
                                                        <div class="bar-label">Grid</div>
                                                        <div class="bar-value">90%</div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <!-- 인터랙티브 버튼 -->
                                            <div class="phone-footer">
                                                <button class="btn btn-success btn-sm" onclick="tradeCarbonCredits()">
                                                    <i class="fas fa-leaf"></i> Trade Carbon Credits
                                                </button>
                                                <div class="carbon-credits" id="carbonCredits">
                                                    <small>Credits: <span id="creditsValue">1,250</span></small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Power Generation Status Simulator -->
                            <div class="col-md-6">
                                <div class="simulator-container">
                                    <h6><strong>Power Generation Status</strong></h6>
                                    <div class="interactive-phone">
                                        <div class="phone-header">
                                            <h6>Power Generation after scheduled maintenance</h6>
                                        </div>
                                        <div class="phone-content">
                                            <!-- 인터랙티브 알림 시스템 -->
                                            <div class="notification-system">
                                                <h6>System Notifications</h6>
                                                <div class="notification-list">
                                                    <div class="notification-item interactive" onclick="handleNotification('news')">
                                                        <i class="fas fa-bell text-primary"></i>
                                                        <span>New/News</span>
                                                        <span class="notification-count" id="newsCount">3</span>
                                                    </div>
                                                    <div class="notification-item interactive" onclick="handleNotification('maintenance')">
                                                        <i class="fas fa-tools text-warning"></i>
                                                        <span>Maintenance Required</span>
                                                        <span class="notification-count" id="maintenanceCount">1</span>
                                                    </div>
                                                    <div class="notification-item interactive" onclick="handleNotification('completed')">
                                                        <i class="fas fa-check-circle text-success"></i>
                                                        <span>Maintenance Completed</span>
                                                        <span class="notification-count" id="completedCount">5</span>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <!-- 인터랙티브 발전 상태 -->
                                            <div class="power-status">
                                                <h6>Power Generation Status</h6>
                                                <div class="status-grid">
                                                    <div class="status-card interactive" onclick="togglePowerSource('solar')">
                                                        <div class="status-indicator">
                                                            <span class="status-dot status-online" id="solarStatus"></span>
                                                        </div>
                                                        <div class="status-info">
                                                            <div class="status-label">Solar</div>
                                                            <div class="status-value" id="solarValue">3.2 kW</div>
                                                        </div>
                                                        <div class="status-control">
                                                            <i class="fas fa-power-off" id="solarIcon"></i>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class="status-card interactive" onclick="togglePowerSource('wind')">
                                                        <div class="status-indicator">
                                                            <span class="status-dot status-warning" id="windStatus"></span>
                                                        </div>
                                                        <div class="status-info">
                                                            <div class="status-label">Wind</div>
                                                            <div class="status-value" id="windValue">1.8 kW</div>
                                                        </div>
                                                        <div class="status-control">
                                                            <i class="fas fa-power-off" id="windIcon"></i>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class="status-card interactive" onclick="togglePowerSource('battery')">
                                                        <div class="status-indicator">
                                                            <span class="status-dot status-offline" id="batteryStatus"></span>
                                                        </div>
                                                        <div class="status-info">
                                                            <div class="status-label">Battery</div>
                                                            <div class="status-value" id="batteryValue">85%</div>
                                                        </div>
                                                        <div class="status-control">
                                                            <i class="fas fa-battery-half" id="batteryIcon"></i>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <!-- 실시간 제어 패널 -->
                                            <div class="control-panel">
                                                <button class="btn btn-primary btn-sm" onclick="refreshStatus()">
                                                    <i class="fas fa-sync-alt"></i> Refresh
                                                </button>
                                                <button class="btn btn-warning btn-sm" onclick="emergencyStop()">
                                                    <i class="fas fa-stop"></i> Emergency Stop
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

            <!-- 데이터셋 관리 & 모델 평가 -->
            <div class="row">
                <!-- 데이터셋 관리 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-database"></i> Dataset Management</h5>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Training Dataset</span>
                                <span class="badge bg-primary" id="trainDatasetSize">12,450 samples</span>
                            </div>
                            <div class="progress mb-2">
                                <div class="progress-bar" role="progressbar" style="width: 85%">85% Quality</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Validation Dataset</span>
                                <span class="badge bg-info" id="valDatasetSize">2,100 samples</span>
                            </div>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-info" role="progressbar" style="width: 92%">92% Quality</div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Test Dataset</span>
                                <span class="badge bg-success" id="testDatasetSize">1,800 samples</span>
                            </div>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" role="progressbar" style="width: 95%">95% Quality</div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <button class="btn btn-outline-primary w-100" onclick="uploadDataset()">
                                    <i class="fas fa-upload"></i> Upload
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-outline-info w-100" onclick="preprocessDataset()">
                                    <i class="fas fa-tools"></i> Preprocess
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-outline-success w-100" onclick="validateDataset()">
                                    <i class="fas fa-check"></i> Validate
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 모델 평가 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-chart-line"></i> Model Evaluation</h5>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="text-center">
                                    <h6>BLEU Score</h6>
                                    <div class="metric-value text-primary" id="bleuScore">0.87</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="text-center">
                                    <h6>ROUGE-L</h6>
                                    <div class="metric-value text-success" id="rougeScore">0.82</div>
                                </div>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="text-center">
                                    <h6>Perplexity</h6>
                                    <div class="metric-value text-warning" id="perplexity">12.3</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="text-center">
                                    <h6>F1 Score</h6>
                                    <div class="metric-value text-info" id="f1Score">0.91</div>
                                </div>
                            </div>
                        </div>
                        <canvas id="evaluationChart" height="200"></canvas>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <button class="btn btn-primary w-100" onclick="runEvaluation()">
                                    <i class="fas fa-play"></i> Run Evaluation
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-success w-100" onclick="exportResults()">
                                    <i class="fas fa-download"></i> Export Results
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 실시간 테스트 & 배포 -->
            <div class="row">
                <!-- 실시간 테스트 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-flask"></i> Real-time Testing</h5>
                        <div class="mb-3">
                            <label class="form-label">Test Input</label>
                            <textarea class="form-control" id="testInput" rows="3" placeholder="Enter your energy-related query here...">What is the optimal energy consumption pattern for a residential building during peak hours?</textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Model Response</label>
                            <div class="border rounded p-3" id="modelResponse" style="min-height: 150px; background-color: #f8f9fa;">
                                <em class="text-muted">Click "Test Model" to see the response...</em>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <button class="btn btn-primary w-100" onclick="testModel()">
                                    <i class="fas fa-play"></i> Test Model
                                </button>
                            </div>
                            <div class="col-md-6">
                                <button class="btn btn-info w-100" onclick="clearTest()">
                                    <i class="fas fa-trash"></i> Clear
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 모델 배포 -->
                <div class="col-lg-6 mb-4">
                    <div class="prompt-card">
                        <h5><i class="fas fa-rocket"></i> Model Deployment</h5>
                        <div class="mb-3">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Production Model</span>
                                <span class="model-status status-ready">v2.1.0</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Staging Model</span>
                                <span class="model-status status-training">v2.2.0-beta</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span>Development Model</span>
                                <span class="model-status status-idle">v2.3.0-dev</span>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Deployment Configuration</label>
                            <div id="deploymentConfigEditor" class="code-editor"></div>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <button class="btn btn-success w-100" onclick="deployModel()">
                                    <i class="fas fa-rocket"></i> Deploy
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-warning w-100" onclick="rollbackModel()">
                                    <i class="fas fa-undo"></i> Rollback
                                </button>
                            </div>
                            <div class="col-md-4">
                                <button class="btn btn-info w-100" onclick="monitorModel()">
                                    <i class="fas fa-eye"></i> Monitor
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 비교 -->
            <div class="row">
                <div class="col-12">
                    <div class="prompt-card">
                        <h5><i class="fas fa-balance-scale"></i> Model Performance Comparison</h5>
                        <canvas id="comparisonChart" height="300"></canvas>
                        <div class="row mt-3">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Base Model</h6>
                                    <div class="metric-value text-muted">78.5%</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Fine-tuned v1</h6>
                                    <div class="metric-value text-primary">89.2%</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Fine-tuned v2</h6>
                                    <div class="metric-value text-success">94.2%</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Current Model</h6>
                                    <div class="metric-value text-warning">96.1%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 지표 그래프 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="prompt-card">
                        <h5><i class="fas fa-chart-line"></i> Model Performance Metrics</h5>
                        <div class="row">
                            <div class="col-lg-8">
                                <canvas id="performanceChart" height="400"></canvas>
                            </div>
                            <div class="col-lg-4">
                                <div class="performance-controls">
                                    <h6><strong>Model Selection</strong></h6>
                                    <div class="model-selection">
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="radio" name="modelType" id="energyPrediction" value="energy" checked>
                                            <label class="form-check-label" for="energyPrediction">
                                                <strong>Energy Prediction</strong>
                                                <small class="d-block text-muted">LSTM 기반 에너지 소비 예측</small>
                                            </label>
                                        </div>
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="radio" name="modelType" id="anomalyDetection" value="anomaly">
                                            <label class="form-check-label" for="anomalyDetection">
                                                <strong>Anomaly Detection</strong>
                                                <small class="d-block text-muted">Isolation Forest 기반 이상 탐지</small>
                                            </label>
                                        </div>
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="radio" name="modelType" id="climatePrediction" value="climate">
                                            <label class="form-check-label" for="climatePrediction">
                                                <strong>Climate Prediction</strong>
                                                <small class="d-block text-muted">DeepMind 기반 기후 예측</small>
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="model-actions mt-4">
                                        <button class="btn btn-primary w-100 mb-2" onclick="selectModel()">
                                            <i class="fas fa-check"></i> Select Model
                                        </button>
                                        <button class="btn btn-success w-100 mb-2" onclick="deployModel()">
                                            <i class="fas fa-rocket"></i> Deploy Selected
                                        </button>
                                        <button class="btn btn-info w-100" onclick="compareModels()">
                                            <i class="fas fa-balance-scale"></i> Compare All
                                        </button>
                                    </div>
                                    
                                    <div class="selected-model-info mt-3" id="selectedModelInfo" style="display: none;">
                                        <div class="alert alert-success">
                                            <h6><i class="fas fa-check-circle"></i> Selected Model</h6>
                                            <div id="selectedModelName"></div>
                                            <div id="selectedModelMetrics"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 모델 성능 상세 분석 -->
            <div class="row">
                <div class="col-12">
                    <div class="prompt-card">
                        <h5><i class="fas fa-analytics"></i> Detailed Performance Analysis</h5>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6>Accuracy Trends</h6>
                                    <canvas id="accuracyChart" height="200"></canvas>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6>Training Loss</h6>
                                    <canvas id="lossChart" height="200"></canvas>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="metric-card">
                                    <h6>Inference Time</h6>
                                    <canvas id="inferenceChart" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // 현재 언어 설정
            let currentLanguage = '{lang}';
            let translations = {{}};
            let editors = {{}};

            // Monaco Editor 초기화
            require.config({{ paths: {{ 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' }} }});
            require(['vs/editor/editor.main'], function() {{
                // System Prompt Editor
                editors.systemPrompt = monaco.editor.create(document.getElementById('systemPromptEditor'), {{
                    value: `You are an expert energy management AI assistant specialized in analyzing energy consumption patterns, optimizing energy usage, and providing intelligent recommendations for energy efficiency. You have deep knowledge of:

- Energy consumption patterns in residential, commercial, and industrial buildings
- Renewable energy systems (solar, wind, geothermal)
- Energy storage systems and smart grid technologies
- Energy efficiency optimization strategies
- Real-time energy monitoring and control systems

Always provide accurate, data-driven insights and practical recommendations for energy management.`,
                    language: 'markdown',
                    theme: 'vs-dark',
                    minimap: {{ enabled: false }},
                    scrollBeyondLastLine: false,
                    automaticLayout: true
                }});

                // User Prompt Editor
                editors.userPrompt = monaco.editor.create(document.getElementById('userPromptEditor'), {{
                    value: `Context: Energy consumption data for {{building_type}} in {{location}}
Time period: {{start_date}} to {{end_date}}
Energy sources: {{energy_sources}}
Current consumption: {{current_consumption}} kWh
Peak demand: {{peak_demand}} kW

Question: {{user_question}}

Please analyze the energy consumption patterns and provide specific recommendations for optimization.`,
                    language: 'markdown',
                    theme: 'vs-dark',
                    minimap: {{ enabled: false }},
                    scrollBeyondLastLine: false,
                    automaticLayout: true
                }});

                // Few-shot Examples Editor
                editors.fewShot = monaco.editor.create(document.getElementById('fewShotEditor'), {{
                    value: `Example 1:
Input: "How can I reduce energy consumption during peak hours?"
Output: "To reduce energy consumption during peak hours, consider: 1) Shifting non-essential loads to off-peak hours, 2) Implementing demand response strategies, 3) Using energy storage systems to discharge during peak periods, 4) Optimizing HVAC settings and scheduling."

Example 2:
Input: "What's the optimal solar panel configuration for a 2000 sq ft home?"
Output: "For a 2000 sq ft home, optimal solar configuration typically includes: 1) 6-8 kW system capacity, 2) South-facing panels at 30-35° tilt, 3) 20-25 panels (300W each), 4) 10-15 kWh battery storage for backup, 5) Net metering for grid integration."`,
                    language: 'markdown',
                    theme: 'vs-dark',
                    minimap: {{ enabled: false }},
                    scrollBeyondLastLine: false,
                    automaticLayout: true
                }});

                // Training Config Editor
                editors.trainingConfig = monaco.editor.create(document.getElementById('trainingConfigEditor'), {{
                    value: `{{
  "model_name": "energy-slm-v2",
  "base_model": "microsoft/DialoGPT-medium",
  "max_length": 512,
  "learning_rate": 0.0001,
  "batch_size": 8,
  "epochs": 10,
  "warmup_steps": 100,
  "weight_decay": 0.01,
  "gradient_accumulation_steps": 4,
  "fp16": true,
  "dataloader_num_workers": 4,
  "save_steps": 500,
  "eval_steps": 500,
  "logging_steps": 100
}}`,
                    language: 'json',
                    theme: 'vs-dark',
                    minimap: {{ enabled: false }},
                    scrollBeyondLastLine: false,
                    automaticLayout: true
                }});

                // Deployment Config Editor
                editors.deploymentConfig = monaco.editor.create(document.getElementById('deploymentConfigEditor'), {{
                    value: `{{
  "model_path": "/models/energy-slm-v2.1.0",
  "deployment_type": "api",
  "endpoint": "/api/v1/energy-slm",
  "max_concurrent_requests": 100,
  "timeout": 30,
  "gpu_memory_fraction": 0.8,
  "batch_size": 16,
  "enable_caching": true,
  "cache_size": 1000,
  "monitoring": {{
    "enable_metrics": true,
    "log_level": "INFO",
    "health_check_interval": 60
  }}
}}`,
                    language: 'json',
                    theme: 'vs-dark',
                    minimap: {{ enabled: false }},
                    scrollBeyondLastLine: false
                }});
            }});

            // 번역 로드
            async function loadTranslations(lang) {{
                try {{
                    const response = await fetch(`/api/translations/${{lang}}`);
                    const data = await response.json();
                    translations = data.translations;
                    applyTranslations();
                }} catch (error) {{
                    console.error('Error loading translations:', error);
                }}
            }}

            // 번역 적용
            function applyTranslations() {{
                const elements = document.querySelectorAll('[data-translate]');
                elements.forEach(element => {{
                    const key = element.getAttribute('data-translate');
                    if (translations[key]) {{
                        element.textContent = translations[key];
                    }}
                }});
            }}

            // 언어 변경
            function changeLanguage(lang) {{
                currentLanguage = lang;
                loadTranslations(lang);
                
                // URL 업데이트
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.pushState({{}}, '', url);
                
                // 현재 언어 표시 업데이트
                const languageNames = {{
                    'ko': '한국어',
                    'en': 'English',
                    'zh': '中文'
                }};
                document.getElementById('currentLanguage').textContent = languageNames[lang];
            }}

            // 프롬프트 테스트
            function testPrompt() {{
                const systemPrompt = editors.systemPrompt.getValue();
                const userPrompt = editors.userPrompt.getValue();
                const fewShot = editors.fewShot.getValue();
                
                console.log('Testing prompt configuration...');
                alert('Prompt configuration saved and ready for testing!');
            }}

            // 프롬프트 저장
            function savePrompt() {{
                const systemPrompt = editors.systemPrompt.getValue();
                const userPrompt = editors.userPrompt.getValue();
                const fewShot = editors.fewShot.getValue();
                
                console.log('Saving prompt configuration...');
                alert('Prompt configuration saved successfully!');
            }}

            // 훈련 시작
            function startTraining() {{
                const config = editors.trainingConfig.getValue();
                const learningRate = document.getElementById('learningRate').value;
                const batchSize = document.getElementById('batchSize').value;
                const epochs = document.getElementById('epochs').value;
                const warmupSteps = document.getElementById('warmupSteps').value;
                
                document.getElementById('modelStatus').textContent = 'Training';
                document.getElementById('modelStatus').className = 'model-status status-training';
                
                // 훈련 진행률 시뮬레이션
                let progress = 0;
                const interval = setInterval(() => {{
                    progress += Math.random() * 10;
                    if (progress >= 100) {{
                        progress = 100;
                        clearInterval(interval);
                        document.getElementById('modelStatus').textContent = 'Ready';
                        document.getElementById('modelStatus').className = 'model-status status-ready';
                    }}
                    document.getElementById('trainingProgress').textContent = Math.round(progress) + '%';
                    document.getElementById('trainingProgressBar').style.width = progress + '%';
                }}, 1000);
                
                console.log('Starting training with configuration:', config);
                alert('Training started! Monitor progress in the dashboard.');
            }}

            // 훈련 중지
            function stopTraining() {{
                document.getElementById('modelStatus').textContent = 'Idle';
                document.getElementById('modelStatus').className = 'model-status status-idle';
                console.log('Training stopped');
                alert('Training stopped successfully!');
            }}

            // 데이터셋 업로드
            function uploadDataset() {{
                console.log('Uploading dataset...');
                alert('Dataset upload functionality would be implemented here!');
            }}

            // 데이터셋 전처리
            function preprocessDataset() {{
                console.log('Preprocessing dataset...');
                alert('Dataset preprocessing started!');
            }}

            // 데이터셋 검증
            function validateDataset() {{
                console.log('Validating dataset...');
                alert('Dataset validation completed!');
            }}

            // 평가 실행
            function runEvaluation() {{
                console.log('Running model evaluation...');
                alert('Model evaluation started!');
            }}

            // 결과 내보내기
            function exportResults() {{
                console.log('Exporting evaluation results...');
                alert('Results exported successfully!');
            }}

            // 모델 테스트
            function testModel() {{
                const testInput = document.getElementById('testInput').value;
                const responseDiv = document.getElementById('modelResponse');
                
                responseDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div> Generating response...';
                
                // 시뮬레이션된 응답
                setTimeout(() => {{
                    responseDiv.innerHTML = `
                        <strong>Energy SLM Response:</strong><br><br>
                        Based on the energy consumption pattern analysis, here are my recommendations for optimizing energy usage during peak hours:<br><br>
                        
                        <strong>1. Load Shifting Strategies:</strong><br>
                        • Move non-essential appliances (dishwasher, washing machine) to off-peak hours (10 PM - 6 AM)<br>
                        • Schedule HVAC pre-cooling/heating before peak periods<br><br>
                        
                        <strong>2. Demand Response Implementation:</strong><br>
                        • Install smart thermostats with peak hour programming<br>
                        • Use energy storage systems to discharge during peak periods<br>
                        • Implement automated load shedding for non-critical systems<br><br>
                        
                        <strong>3. Energy Efficiency Measures:</strong><br>
                        • Upgrade to ENERGY STAR certified appliances<br>
                        • Improve building insulation and sealing<br>
                        • Install LED lighting with occupancy sensors<br><br>
                        
                        <strong>Expected Savings:</strong> 15-25% reduction in peak hour consumption, resulting in $150-300 monthly savings.
                    `;
                }}, 2000);
            }}

            // 테스트 클리어
            function clearTest() {{
                document.getElementById('testInput').value = '';
                document.getElementById('modelResponse').innerHTML = '<em class="text-muted">Click "Test Model" to see the response...</em>';
            }}

            // 모델 배포
            function deployModel() {{
                console.log('Deploying model...');
                alert('Model deployment started!');
            }}

            // 모델 롤백
            function rollbackModel() {{
                console.log('Rolling back model...');
                alert('Model rollback completed!');
            }}

            // 모델 모니터링
            function monitorModel() {{
                console.log('Opening model monitoring dashboard...');
                alert('Model monitoring dashboard opened!');
            }}

            // 평가 차트 생성
            function createEvaluationChart() {{
                const ctx = document.getElementById('evaluationChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Epoch 1', 'Epoch 2', 'Epoch 3', 'Epoch 4', 'Epoch 5', 'Epoch 6', 'Epoch 7', 'Epoch 8', 'Epoch 9', 'Epoch 10'],
                        datasets: [{{
                            label: 'Training Loss',
                            data: [2.5, 2.1, 1.8, 1.6, 1.4, 1.2, 1.0, 0.9, 0.8, 0.7],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Validation Loss',
                            data: [2.6, 2.2, 1.9, 1.7, 1.5, 1.3, 1.1, 1.0, 0.9, 0.8],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'BLEU Score',
                            data: [0.65, 0.72, 0.78, 0.82, 0.85, 0.87, 0.89, 0.90, 0.91, 0.92],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
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
                                    text: 'Loss'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'BLEU Score'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 비교 차트 생성
            function createComparisonChart() {{
                const ctx = document.getElementById('comparisonChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Accuracy', 'BLEU Score', 'ROUGE-L', 'F1 Score', 'Perplexity'],
                        datasets: [{{
                            label: 'Base Model',
                            data: [78.5, 0.65, 0.72, 0.75, 25.3],
                            backgroundColor: '#6c757d'
                        }}, {{
                            label: 'Fine-tuned v1',
                            data: [89.2, 0.78, 0.82, 0.85, 18.7],
                            backgroundColor: '#007bff'
                        }}, {{
                            label: 'Fine-tuned v2',
                            data: [94.2, 0.87, 0.89, 0.91, 12.3],
                            backgroundColor: '#28a745'
                        }}, {{
                            label: 'Current Model',
                            data: [96.1, 0.92, 0.94, 0.95, 8.9],
                            backgroundColor: '#ffc107'
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
                        }}
                    }}
                }});
            }}

            // 모델 성능 지표 그래프 생성
            function createPerformanceChart() {{
                const ctx = document.getElementById('performanceChart').getContext('2d');
                window.performanceChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
                        datasets: [{{
                            label: 'Energy Prediction Accuracy',
                            data: [92.1, 93.5, 94.2, 95.1, 95.8, 96.2, 95.9, 95.2],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}, {{
                            label: 'Anomaly Detection F1-Score',
                            data: [88.5, 89.2, 90.1, 91.3, 92.0, 92.5, 92.1, 92.1],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}, {{
                            label: 'Climate Prediction MAE',
                            data: [1.2, 1.1, 1.0, 0.9, 0.8, 0.8, 0.8, 0.8],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y1'
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
                                    text: 'Accuracy / F1-Score (%)'
                                }},
                                min: 85,
                                max: 100
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'MAE (°C)'
                                }},
                                min: 0.5,
                                max: 1.5,
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                            title: {{
                                display: true,
                                text: 'Model Performance Over Time'
                            }}
                        }}
                    }}
                }});
            }}

            // 정확도 트렌드 차트
            function createAccuracyChart() {{
                const ctx = document.getElementById('accuracyChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Epoch 1', 'Epoch 5', 'Epoch 10', 'Epoch 15', 'Epoch 20', 'Epoch 25', 'Epoch 30'],
                        datasets: [{{
                            label: 'Training Accuracy',
                            data: [75.2, 82.1, 87.5, 91.2, 93.8, 95.1, 95.2],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Validation Accuracy',
                            data: [73.8, 80.5, 85.9, 89.7, 92.3, 94.1, 94.8],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
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
                        }}
                    }}
                }});
            }}

            // 훈련 손실 차트
            function createLossChart() {{
                const ctx = document.getElementById('lossChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['Epoch 1', 'Epoch 5', 'Epoch 10', 'Epoch 15', 'Epoch 20', 'Epoch 25', 'Epoch 30'],
                        datasets: [{{
                            label: 'Training Loss',
                            data: [2.5, 1.8, 1.2, 0.8, 0.5, 0.3, 0.2],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Validation Loss',
                            data: [2.6, 1.9, 1.3, 0.9, 0.6, 0.4, 0.3],
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
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
            }}

            // 추론 시간 차트
            function createInferenceChart() {{
                const ctx = document.getElementById('inferenceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Energy Prediction', 'Anomaly Detection', 'Climate Prediction'],
                        datasets: [{{
                            label: 'Inference Time (ms)',
                            data: [45, 23, 67],
                            backgroundColor: ['#007bff', '#28a745', '#dc3545']
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
            }}

            // 모델 선택 함수
            function selectModel() {{
                const selectedModel = document.querySelector('input[name="modelType"]:checked');
                const modelInfo = document.getElementById('selectedModelInfo');
                const modelName = document.getElementById('selectedModelName');
                const modelMetrics = document.getElementById('selectedModelMetrics');
                
                if (selectedModel) {{
                    const modelData = {{
                        energy: {{
                            name: 'Energy Prediction LSTM v2.1.0',
                            metrics: 'Accuracy: 95.2% | F1-Score: 94.8% | Inference: 45ms'
                        }},
                        anomaly: {{
                            name: 'Anomaly Detection Forest v1.8.2',
                            metrics: 'F1-Score: 92.1% | Precision: 91.5% | Recall: 92.7%'
                        }},
                        climate: {{
                            name: 'Climate Prediction DeepMind v3.0.1',
                            metrics: 'MAE: 0.8°C | RMSE: 1.2°C | R²: 0.94'
                        }}
                    }};
                    
                    const data = modelData[selectedModel.value];
                    modelName.textContent = data.name;
                    modelMetrics.textContent = data.metrics;
                    modelInfo.style.display = 'block';
                    
                    showNotification(`${{data.name}} selected successfully!`, 'success');
                }}
            }}

            // 모델 배포 함수
            function deployModel() {{
                const selectedModel = document.querySelector('input[name="modelType"]:checked');
                if (selectedModel) {{
                    const modelNames = {{
                        energy: 'Energy Prediction LSTM',
                        anomaly: 'Anomaly Detection Forest',
                        climate: 'Climate Prediction DeepMind'
                    }};
                    
                    showNotification(`${{modelNames[selectedModel.value]}} deployed successfully!`, 'success');
                }} else {{
                    showNotification('Please select a model first!', 'warning');
                }}
            }}

            // 모델 비교 함수
            function compareModels() {{
                showNotification('Opening model comparison dashboard...', 'info');
                // 실제 구현에서는 모델 비교 페이지로 이동하거나 모달을 열 수 있습니다
            }}

            // 실시간 데이터 업데이트
            function updateRealtimeData() {{
                // 모델 정확도 업데이트
                document.getElementById('modelAccuracy').textContent = (94.2 + Math.random() * 2).toFixed(1) + '%';
                
                // 추론 시간 업데이트
                document.getElementById('inferenceTime').textContent = (45 + Math.random() * 10).toFixed(0) + 'ms';
                
                // 평가 지표 업데이트
                document.getElementById('bleuScore').textContent = (0.87 + Math.random() * 0.05).toFixed(2);
                document.getElementById('rougeScore').textContent = (0.82 + Math.random() * 0.05).toFixed(2);
                document.getElementById('perplexity').textContent = (12.3 + Math.random() * 2).toFixed(1);
                document.getElementById('f1Score').textContent = (0.91 + Math.random() * 0.03).toFixed(2);
            }}

            // 인터랙티브 시뮬레이터 함수들
            function updateProgress(category) {{
                const bar = document.querySelector(`[data-category="${{category}}"]`);
                const barFill = bar.querySelector('.bar-fill');
                const barValue = bar.querySelector('.bar-value');
                const currentValue = parseInt(bar.dataset.value);
                
                // 랜덤하게 진행률 업데이트
                const newValue = Math.min(100, currentValue + Math.floor(Math.random() * 10) + 5);
                bar.dataset.value = newValue;
                
                // 애니메이션으로 높이 업데이트
                barFill.style.height = newValue + '%';
                barValue.textContent = newValue + '%';
                
                // 성공 메시지 표시
                showNotification(`${{category}} efficiency improved to ${{newValue}}%!`, 'success');
            }}
            
            function tradeCarbonCredits() {{
                const creditsElement = document.getElementById('creditsValue');
                const currentCredits = parseInt(creditsElement.textContent.replace(',', ''));
                const newCredits = currentCredits + Math.floor(Math.random() * 100) + 50;
                
                creditsElement.textContent = newCredits.toLocaleString();
                
                // 버튼 애니메이션
                const button = event.target.closest('button');
                button.style.transform = 'scale(0.95)';
                setTimeout(() => {{
                    button.style.transform = 'scale(1)';
                }}, 150);
                
                showNotification(`Carbon credits increased to ${{newCredits.toLocaleString()}}!`, 'success');
            }}
            
            function handleNotification(type) {{
                const countElement = document.getElementById(type + 'Count');
                const currentCount = parseInt(countElement.textContent);
                
                if (currentCount > 0) {{
                    countElement.textContent = currentCount - 1;
                    showNotification(`${{type}} notification cleared!`, 'info');
                }} else {{
                    showNotification('No more notifications of this type', 'warning');
                }}
            }}
            
            function togglePowerSource(source) {{
                const card = event.target.closest('.status-card');
                const statusDot = document.getElementById(source + 'Status');
                const icon = document.getElementById(source + 'Icon');
                const valueElement = document.getElementById(source + 'Value');
                
                // 토글 상태
                const isActive = card.classList.contains('active');
                
                if (isActive) {{
                    // 끄기
                    card.classList.remove('active');
                    statusDot.className = 'status-dot status-offline';
                    icon.className = 'fas fa-power-off';
                    valueElement.textContent = '0 kW';
                    showNotification(`${{source}} power source turned off`, 'warning');
                }} else {{
                    // 켜기
                    card.classList.add('active');
                    statusDot.className = 'status-dot status-online';
                    icon.className = 'fas fa-power-off active';
                    
                    // 랜덤 값 생성
                    const values = {{
                        solar: (Math.random() * 2 + 2).toFixed(1) + ' kW',
                        wind: (Math.random() * 1.5 + 1).toFixed(1) + ' kW',
                        battery: Math.floor(Math.random() * 20 + 80) + '%'
                    }};
                    valueElement.textContent = values[source];
                    showNotification(`${{source}} power source turned on`, 'success');
                }}
            }}
            
            function refreshStatus() {{
                // 모든 상태 새로고침
                const sources = ['solar', 'wind', 'battery'];
                sources.forEach(source => {{
                    const valueElement = document.getElementById(source + 'Value');
                    const values = {{
                        solar: (Math.random() * 2 + 2).toFixed(1) + ' kW',
                        wind: (Math.random() * 1.5 + 1).toFixed(1) + ' kW',
                        battery: Math.floor(Math.random() * 20 + 80) + '%'
                    }};
                    valueElement.textContent = values[source];
                }});
                
                // 알림 카운트 업데이트
                document.getElementById('newsCount').textContent = Math.floor(Math.random() * 5);
                document.getElementById('maintenanceCount').textContent = Math.floor(Math.random() * 3);
                document.getElementById('completedCount').textContent = Math.floor(Math.random() * 8) + 2;
                
                showNotification('Status refreshed successfully!', 'info');
            }}
            
            function emergencyStop() {{
                // 모든 전원 끄기
                const cards = document.querySelectorAll('.status-card');
                cards.forEach(card => {{
                    card.classList.remove('active');
                    const source = card.onclick.toString().match(/togglePowerSource\\('(\\w+)'\\)/)[1];
                    const statusDot = document.getElementById(source + 'Status');
                    const icon = document.getElementById(source + 'Icon');
                    const valueElement = document.getElementById(source + 'Value');
                    
                    statusDot.className = 'status-dot status-offline';
                    icon.className = 'fas fa-power-off';
                    valueElement.textContent = '0 kW';
                }});
                
                showNotification('EMERGENCY STOP ACTIVATED! All power sources turned off.', 'danger');
            }}
            
            function showNotification(message, type) {{
                // 알림 생성
                const notification = document.createElement('div');
                notification.className = `alert alert-${{type}} alert-dismissible fade show position-fixed`;
                notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
                notification.innerHTML = `
                    ${{message}}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.body.appendChild(notification);
                
                // 3초 후 자동 제거
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        notification.remove();
                    }}
                }}, 3000);
            }}
            
            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                createEvaluationChart();
                createComparisonChart();
                createPerformanceChart();
                createAccuracyChart();
                createLossChart();
                createInferenceChart();
                updateRealtimeData();
                setInterval(updateRealtimeData, 5000); // 5초마다 업데이트
                
                // 시뮬레이터 초기화
                initializeSimulator();
            }});
            
            function initializeSimulator() {{
                // 초기 상태 설정
                console.log('Interactive Simulator initialized');
                
                // 실시간 데이터 업데이트 (시뮬레이터용)
                setInterval(() => {{
                    // 진행률 차트 자동 업데이트
                    const bars = document.querySelectorAll('.chart-bar.interactive');
                    bars.forEach(bar => {{
                        const currentValue = parseInt(bar.dataset.value);
                        const variation = Math.floor(Math.random() * 6) - 3; // -3 to +3
                        const newValue = Math.max(0, Math.min(100, currentValue + variation));
                        
                        if (newValue !== currentValue) {{
                            bar.dataset.value = newValue;
                            const barFill = bar.querySelector('.bar-fill');
                            const barValue = bar.querySelector('.bar-value');
                            barFill.style.height = newValue + '%';
                            barValue.textContent = newValue + '%';
                        }}
                    }});
                }}, 10000); // 10초마다 업데이트
            }}

            // SPO 스타일 데이터 분석 차트 변수
            let powerDataChart = null;
            let energyTrendChart = null;
            let efficiencyChart = null;
            let weatherChart = null;
            let weatherForecastChart = null;
            let realtimeData = [];

            // 샘플 데이터 생성 함수
            function generateSampleData() {{
                const data = [];
                const now = new Date();
                
                // 24시간 샘플 데이터 생성
                for (let i = 23; i >= 0; i--) {{
                    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
                    const hour = time.getHours();
                    
                    // 태양광 발전 패턴 (6시-18시)
                    let solarPower = 0;
                    if (hour >= 6 && hour <= 18) {{
                        const sunAngle = Math.sin((hour - 6) * Math.PI / 12);
                        solarPower = sunAngle * (3.5 + Math.random() * 1.0);
                    }}
                    
                    // 배터리 SOC 패턴 (밤에 방전, 낮에 충전)
                    let batterySOC = 85;
                    if (hour >= 6 && hour <= 14) {{
                        batterySOC = 85 + (hour - 6) * 1.5 + Math.random() * 2;
                    }} else if (hour >= 15 && hour <= 23) {{
                        batterySOC = 95 - (hour - 15) * 1.2 + Math.random() * 2;
                    }} else {{
                        batterySOC = 80 - (hour + 1) * 0.5 + Math.random() * 2;
                    }}
                    
                    // 온도 패턴 (낮에 높고 밤에 낮음)
                    let temperature = 18 + Math.sin((hour - 6) * Math.PI / 12) * 8 + Math.random() * 3;
                    if (hour < 6 || hour > 18) {{
                        temperature = 18 + Math.random() * 4;
                    }}
                    
                    // 습도 패턴 (온도와 반비례)
                    let humidity = 70 - (temperature - 20) * 2 + Math.random() * 10;
                    humidity = Math.max(40, Math.min(90, humidity));
                    
                    data.push({{
                        timestamp: time.toISOString(),
                        hour: hour,
                        solarPower: Math.round(solarPower * 100) / 100,
                        batterySOC: Math.round(batterySOC * 10) / 10,
                        temperature: Math.round(temperature * 10) / 10,
                        humidity: Math.round(humidity * 10) / 10,
                        windSpeed: Math.round((3 + Math.random() * 7) * 10) / 10,
                        irradiance: hour >= 6 && hour <= 18 ? Math.round((800 + Math.random() * 400)) : 0
                    }});
                }}
                
                return data;
            }}

            // SPO 스타일 실시간 데이터 생성
            function generateSPOData() {{
                const now = new Date();
                const hour = now.getHours();
                
                // 시간대별 태양광 발전 패턴
                let solarPower = 0;
                if (hour >= 6 && hour <= 18) {{
                    const sunAngle = Math.sin((hour - 6) * Math.PI / 12);
                    solarPower = sunAngle * (3.5 + Math.random() * 1.0);
                }}
                
                return {{
                    timestamp: now.toISOString(),
                    solarPower: Math.round(solarPower * 100) / 100,
                    batterySOC: 80 + Math.random() * 15,
                    temperature: 20 + Math.random() * 10,
                    humidity: 60 + Math.random() * 20,
                    windSpeed: Math.random() * 10,
                    irradiance: hour >= 6 && hour <= 18 ? 800 + Math.random() * 400 : 0
                }};
            }}

            // SPO 스타일 전력 데이터 차트 생성
            function createSPOPowerDataChart() {{
                try {{
                    const canvas = document.getElementById('spoPowerDataChart');
                    if (!canvas) {{
                        console.error('spoPowerDataChart canvas를 찾을 수 없습니다.');
                        return;
                    }}
                    
                    const ctx = canvas.getContext('2d');
                    const sampleData = generateSampleData();
                    
                    console.log('전력 데이터 차트 생성 중...', sampleData.length + '개 데이터');
                    
                    powerDataChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: sampleData.map(d => d.hour + ':00'),
                        datasets: [{{
                            label: 'Solar Power (kW)',
                            data: sampleData.map(d => d.solarPower),
                            borderColor: '#ff6b35',
                            backgroundColor: 'rgba(255, 107, 53, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y'
                        }}, {{
                            label: 'Battery SOC (%)',
                            data: sampleData.map(d => d.batterySOC),
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            fill: false,
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
                                    text: 'Power (kW)'
                                }},
                                min: 0,
                                max: 5
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: 'SOC (%)'
                                }},
                                min: 0,
                                max: 100,
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                            title: {{
                                display: true,
                                text: 'Real-time Power Data Analysis'
                            }},
                            tooltip: {{
                                mode: 'index',
                                intersect: false
                            }}
                        }}
                    }}
                }});
                
                console.log('전력 데이터 차트 생성 완료!');
                }} catch (error) {{
                    console.error('전력 데이터 차트 생성 오류:', error);
                }}
            }}

            // SPO 스타일 에너지 트렌드 차트 생성
            function createSPOEnergyTrendChart() {{
                const ctx = document.getElementById('spoEnergyTrendChart').getContext('2d');
                const sampleData = generateSampleData();

                energyTrendChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: sampleData.map(d => d.hour + ':00'),
                        datasets: [{{
                            label: 'Solar Generation (kW)',
                            data: sampleData.map(d => d.solarPower),
                            backgroundColor: 'rgba(255, 107, 53, 0.8)',
                            borderColor: '#ff6b35',
                            borderWidth: 1
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
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Time (Hour)'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true
                            }},
                            title: {{
                                display: true,
                                text: '24-Hour Energy Generation Trend'
                            }}
                        }}
                    }}
                }});
            }}

            // SPO 스타일 효율성 차트 생성
            function createSPOEfficiencyChart() {{
                const ctx = document.getElementById('spoEfficiencyChart').getContext('2d');
                const sampleData = generateSampleData();
                
                // 시간대별 효율성 계산 (태양광 발전량 기반)
                const efficiencyData = sampleData.map(d => {{
                    if (d.solarPower > 0) {{
                        return Math.round((75 + (d.solarPower / 4.5) * 20 + Math.random() * 5) * 10) / 10;
                    }}
                    return Math.round((70 + Math.random() * 10) * 10) / 10;
                }});
                
                const pvEfficiencyData = sampleData.map(d => {{
                    if (d.solarPower > 0) {{
                        return Math.round((85 + (d.solarPower / 4.5) * 10 + Math.random() * 3) * 10) / 10;
                    }}
                    return Math.round((80 + Math.random() * 5) * 10) / 10;
                }});

                efficiencyChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: sampleData.map(d => d.hour + ':00'),
                        datasets: [{{
                            label: 'System Efficiency (%)',
                            data: efficiencyData,
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            fill: true
                        }}, {{
                            label: 'PV Efficiency (%)',
                            data: pvEfficiencyData,
                            borderColor: '#ff6b35',
                            backgroundColor: 'rgba(255, 107, 53, 0.1)',
                            tension: 0.4,
                            fill: false
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
                                    text: 'Efficiency (%)'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true
                            }},
                            title: {{
                                display: true,
                                text: 'System Efficiency Analysis'
                            }}
                        }}
                    }}
                }});
            }}

            // SPO 스타일 날씨 차트 생성 (현황/예측 포함)
            function createSPOWeatherChart() {{
                const ctx = document.getElementById('spoWeatherChart').getContext('2d');
                const sampleData = generateSampleData();

                // 현재 시간 기준으로 과거/현재/미래 데이터 분리
                const currentHour = new Date().getHours();
                const pastData = sampleData.slice(0, Math.floor(sampleData.length * 0.6)); // 60%는 과거 데이터
                const currentData = sampleData.slice(Math.floor(sampleData.length * 0.6), Math.floor(sampleData.length * 0.8)); // 20%는 현재 데이터
                const futureData = sampleData.slice(Math.floor(sampleData.length * 0.8)); // 20%는 미래 예측 데이터
                
                // 예측 데이터 생성 (현재 데이터 기반으로 트렌드 적용)
                const lastCurrentTemp = currentData[currentData.length - 1]?.temperature || 24;
                const lastCurrentHumidity = currentData[currentData.length - 1]?.humidity || 65;
                const lastCurrentWind = currentData[currentData.length - 1]?.windSpeed || 2.3;
                const lastCurrentIrradiance = currentData[currentData.length - 1]?.irradiance || 850;
                
                const forecastData = futureData.map((d, index) => ({{
                    ...d,
                    temperature: lastCurrentTemp + (Math.sin(index * 0.5) * 2) + (Math.random() - 0.5) * 1,
                    humidity: Math.max(30, Math.min(90, lastCurrentHumidity + (Math.random() - 0.5) * 10)),
                    windSpeed: Math.max(0, lastCurrentWind + (Math.random() - 0.5) * 1),
                    irradiance: Math.max(0, lastCurrentIrradiance + (Math.sin(index * 0.3) * 100) + (Math.random() - 0.5) * 50)
                }}));
                
                // 모든 데이터 합치기
                const allData = [...pastData, ...currentData, ...forecastData];
                const labels = allData.map((d, index) => {{
                    const hour = (currentHour - Math.floor(sampleData.length * 0.6) + index) % 24;
                    return hour + ':00';
                }});
                
                // 구분점 인덱스
                const currentStartIndex = pastData.length;
                const futureStartIndex = pastData.length + currentData.length;

                weatherChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: 'Temperature (°C)',
                            data: allData.map(d => d.temperature),
                            borderColor: '#ff6b35',
                            backgroundColor: 'rgba(255, 107, 53, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#ff6b35'; // 과거: 주황색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
                        }}, {{
                            label: 'Humidity (%)',
                            data: allData.map(d => d.humidity),
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y1',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#4ecdc4'; // 과거: 청록색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
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
                            x: {{
                                display: true,
                                title: {{
                                    display: true,
                                    text: '시간'
                                }},
                                grid: {{
                                    color: function(context) {{
                                        const index = context.index;
                                        if (index === currentStartIndex || index === futureStartIndex) {{
                                            return '#dc3545'; // 구분선
                                        }}
                                        return 'rgba(0, 0, 0, 0.1)';
                                    }}
                                }}
                            }},
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
                                    text: 'Humidity (%)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
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
                                text: '현황/예측 시계열 분석'
                            }}
                        }}
                    }}
                }});
                
                // 날씨 통계 업데이트
                updateWeatherStatistics(sampleData);
            }}
            
            // 날씨 통계 업데이트 함수
            function updateWeatherStatistics(data) {{
                if (!data || data.length === 0) return;
                
                // 평균 온도 계산
                const avgTemp = data.reduce((sum, d) => sum + d.temperature, 0) / data.length;
                document.getElementById('avgTemperature').textContent = avgTemp.toFixed(1) + '°C';
                
                // 평균 습도 계산
                const avgHumidity = data.reduce((sum, d) => sum + d.humidity, 0) / data.length;
                document.getElementById('avgHumidity').textContent = avgHumidity.toFixed(1) + '%';
                
                // 최대 풍속 계산
                const maxWindSpeed = Math.max(...data.map(d => d.windSpeed));
                document.getElementById('maxWindSpeed').textContent = maxWindSpeed.toFixed(1) + ' m/s';
                
                // 평균 태양 복사량 계산
                const avgIrradiance = data.reduce((sum, d) => sum + d.irradiance, 0) / data.length;
                document.getElementById('solarIrradiance').textContent = avgIrradiance.toFixed(0) + ' W/m²';
                
                // 에너지 상관관계 계산 (샘플 데이터 기반)
                const tempCorrelation = calculateCorrelation(
                    data.map(d => d.temperature),
                    data.map(d => d.solarPower)
                );
                const solarCorrelation = calculateCorrelation(
                    data.map(d => d.irradiance),
                    data.map(d => d.solarPower)
                );
                const humidityCorrelation = calculateCorrelation(
                    data.map(d => d.humidity),
                    data.map(d => d.batterySOC)
                );
                
                document.getElementById('tempCorrelation').textContent = tempCorrelation.toFixed(2);
                document.getElementById('solarCorrelation').textContent = solarCorrelation.toFixed(2);
                document.getElementById('humidityCorrelation').textContent = humidityCorrelation.toFixed(2);
            }}
            
            // 상관계수 계산 함수
            function calculateCorrelation(x, y) {{
                const n = x.length;
                const sumX = x.reduce((a, b) => a + b, 0);
                const sumY = y.reduce((a, b) => a + b, 0);
                const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
                const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
                const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
                
                const numerator = n * sumXY - sumX * sumY;
                const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
                
                return denominator === 0 ? 0 : numerator / denominator;
            }}
            
            // 현황/예측 시계열 차트 생성 함수
            function createWeatherForecastChart(data) {{
                const ctx = document.getElementById('weatherForecastChart').getContext('2d');
                
                // 현재 시간 기준으로 과거/현재/미래 데이터 분리
                const currentHour = new Date().getHours();
                const pastData = data.slice(0, Math.floor(data.length * 0.6)); // 60%는 과거 데이터
                const currentData = data.slice(Math.floor(data.length * 0.6), Math.floor(data.length * 0.8)); // 20%는 현재 데이터
                const futureData = data.slice(Math.floor(data.length * 0.8)); // 20%는 미래 예측 데이터
                
                // 예측 데이터 생성 (현재 데이터 기반으로 트렌드 적용)
                const lastCurrentTemp = currentData[currentData.length - 1]?.temperature || 24;
                const lastCurrentHumidity = currentData[currentData.length - 1]?.humidity || 65;
                const lastCurrentWind = currentData[currentData.length - 1]?.windSpeed || 2.3;
                const lastCurrentIrradiance = currentData[currentData.length - 1]?.irradiance || 850;
                
                const forecastData = futureData.map((d, index) => ({{
                    ...d,
                    temperature: lastCurrentTemp + (Math.sin(index * 0.5) * 2) + (Math.random() - 0.5) * 1,
                    humidity: Math.max(30, Math.min(90, lastCurrentHumidity + (Math.random() - 0.5) * 10)),
                    windSpeed: Math.max(0, lastCurrentWind + (Math.random() - 0.5) * 1),
                    irradiance: Math.max(0, lastCurrentIrradiance + (Math.sin(index * 0.3) * 100) + (Math.random() - 0.5) * 50)
                }}));
                
                // 모든 데이터 합치기
                const allData = [...pastData, ...currentData, ...forecastData];
                const labels = allData.map((d, index) => {{
                    const hour = (currentHour - Math.floor(data.length * 0.6) + index) % 24;
                    return hour + ':00';
                }});
                
                // 구분점 인덱스
                const currentStartIndex = pastData.length;
                const futureStartIndex = pastData.length + currentData.length;
                
                weatherForecastChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            label: '온도 (°C)',
                            data: allData.map(d => d.temperature),
                            borderColor: '#ff6b35',
                            backgroundColor: 'rgba(255, 107, 53, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#ff6b35'; // 과거: 주황색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
                        }}, {{
                            label: '습도 (%)',
                            data: allData.map(d => d.humidity),
                            borderColor: '#4ecdc4',
                            backgroundColor: 'rgba(78, 205, 196, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y1',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#4ecdc4'; // 과거: 청록색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
                        }}, {{
                            label: '풍속 (m/s)',
                            data: allData.map(d => d.windSpeed),
                            borderColor: '#9b59b6',
                            backgroundColor: 'rgba(155, 89, 182, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y2',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#9b59b6'; // 과거: 보라색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
                        }}, {{
                            label: '태양복사량 (W/m²)',
                            data: allData.map(d => d.irradiance),
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.4,
                            fill: false,
                            yAxisID: 'y3',
                            segment: {{
                                borderColor: function(ctx) {{
                                    const index = ctx.p1DataIndex;
                                    if (index < currentStartIndex) return '#f39c12'; // 과거: 주황색
                                    if (index < futureStartIndex) return '#28a745'; // 현재: 초록색
                                    return '#dc3545'; // 미래: 빨간색
                                }}
                            }}
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
                            x: {{
                                display: true,
                                title: {{
                                    display: true,
                                    text: '시간'
                                }},
                                grid: {{
                                    color: function(context) {{
                                        const index = context.index;
                                        if (index === currentStartIndex || index === futureStartIndex) {{
                                            return '#dc3545'; // 구분선
                                        }}
                                        return 'rgba(0, 0, 0, 0.1)';
                                    }}
                                }}
                            }},
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: '온도 (°C)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '습도 (%)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }},
                            y2: {{
                                type: 'linear',
                                display: false,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '풍속 (m/s)'
                                }}
                            }},
                            y3: {{
                                type: 'linear',
                                display: false,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '태양복사량 (W/m²)'
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
                                text: '현황/예측 시계열 분석'
                            }},
                            annotation: {{
                                annotations: {{
                                    currentLine: {{
                                        type: 'line',
                                        xMin: currentStartIndex,
                                        xMax: currentStartIndex,
                                        borderColor: '#28a745',
                                        borderWidth: 2,
                                        borderDash: [5, 5],
                                        label: {{
                                            content: '현재',
                                            enabled: true,
                                            position: 'start'
                                        }}
                                    }},
                                    futureLine: {{
                                        type: 'line',
                                        xMin: futureStartIndex,
                                        xMax: futureStartIndex,
                                        borderColor: '#dc3545',
                                        borderWidth: 2,
                                        borderDash: [5, 5],
                                        label: {{
                                            content: '예측 시작',
                                            enabled: true,
                                            position: 'start'
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // SPO 스타일 데이터 업데이트
            function updateSPOData() {{
                const newData = generateSPOData();
                realtimeData.push(newData);
                
                // 날씨 통계 실시간 업데이트
                updateWeatherStatistics(realtimeData);
                
                // 현황/예측 차트 업데이트
                if (typeof weatherForecastChart !== 'undefined' && weatherForecastChart) {{
                    createWeatherForecastChart(realtimeData);
                }}

                // 최근 50개 데이터만 유지
                if (realtimeData.length > 50) {{
                    realtimeData.shift();
                }}

                // 실시간 차트 업데이트
                if (powerDataChart) {{
                    const labels = realtimeData.map(d => new Date(d.timestamp).toLocaleTimeString());
                    const solarData = realtimeData.map(d => d.solarPower);
                    const socData = realtimeData.map(d => d.batterySOC);
                    
                    powerDataChart.data.labels = labels;
                    powerDataChart.data.datasets[0].data = solarData;
                    powerDataChart.data.datasets[1].data = socData;
                    powerDataChart.update('none');
                }}

                // 상태 카드 업데이트
                document.getElementById('currentSolarPower').textContent = newData.solarPower.toFixed(2) + ' kW';
                document.getElementById('currentBatterySOC').textContent = newData.batterySOC.toFixed(1) + '%';
                document.getElementById('currentTemperature').textContent = newData.temperature.toFixed(1) + '°C';
                document.getElementById('currentHumidity').textContent = newData.humidity.toFixed(1) + '%';

                // 데이터 테이블 업데이트
                updateDataTable();
            }}

            // 데이터 테이블 업데이트
            function updateDataTable() {{
                const tbody = document.getElementById('dataTableBody');
                if (!tbody) return;

                // 샘플 데이터 사용 (최근 10개)
                const sampleData = generateSampleData();
                const recentData = sampleData.slice(-10).reverse();
                
                tbody.innerHTML = recentData.map(data => {{
                    const timestamp = new Date(data.timestamp).toLocaleString();
                    return `
                        <tr>
                            <td>${{timestamp}}</td>
                            <td>${{data.solarPower.toFixed(2)}}</td>
                            <td>${{data.batterySOC.toFixed(1)}}</td>
                            <td>${{data.temperature.toFixed(1)}}</td>
                            <td>${{data.humidity.toFixed(1)}}</td>
                            <td>${{data.windSpeed.toFixed(1)}}</td>
                            <td>${{data.irradiance.toFixed(0)}}</td>
                        </tr>
                    `;
                }}).join('');
            }}

            // SPO 스타일 차트 초기화
            function initializeSPOCharts() {{
                try {{
                    console.log('SPO 차트 초기화 시작...');
                    
                    // 샘플 데이터로 상태 카드 초기화
                    const sampleData = generateSampleData();
                    const currentData = sampleData[sampleData.length - 1]; // 최신 데이터
                    
                    console.log('샘플 데이터 생성 완료:', currentData);
                    
                    // 상태 카드 업데이트
                    const solarPowerEl = document.getElementById('currentSolarPower');
                    const batterySOCEl = document.getElementById('currentBatterySOC');
                    const temperatureEl = document.getElementById('currentTemperature');
                    const humidityEl = document.getElementById('currentHumidity');
                    
                    if (solarPowerEl) solarPowerEl.textContent = currentData.solarPower.toFixed(2) + ' kW';
                    if (batterySOCEl) batterySOCEl.textContent = currentData.batterySOC.toFixed(1) + '%';
                    if (temperatureEl) temperatureEl.textContent = currentData.temperature.toFixed(1) + '°C';
                    if (humidityEl) humidityEl.textContent = currentData.humidity.toFixed(1) + '%';
                    
                    console.log('상태 카드 업데이트 완료');
                    
                    // 차트 생성
                    createSPOPowerDataChart();
                    createSPOEnergyTrendChart();
                    createSPOEfficiencyChart();
                    createSPOWeatherChart();
                    
                    console.log('차트 생성 완료');
                    
                    // 데이터 테이블 초기화
                    updateDataTable();
                    
                    console.log('데이터 테이블 초기화 완료');
                    
                    // 실시간 데이터 업데이트 (5초마다)
                    setInterval(updateSPOData, 5000);
                    
                    console.log('SPO 차트 초기화 완료!');
                }} catch (error) {{
                    console.error('SPO 차트 초기화 오류:', error);
                }}
            }}

            // 초기화에 SPO 차트 추가
            document.addEventListener('DOMContentLoaded', function() {{
                loadTranslations(currentLanguage);
                updateRealtimeData();
                setInterval(updateRealtimeData, 10000);
                initializeSPOCharts();
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    # MCP 도구 등록
    register_tools()
    
    # 웹 서버 실행
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
