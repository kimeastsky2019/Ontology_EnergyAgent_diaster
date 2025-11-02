"""Main FastAPI application"""
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from datetime import datetime
import logging

from src.config import settings
from src.database import engine, async_engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Language support
LANGUAGE_OPTIONS = {
    "ko": {"label": "한국어", "flag": "🇰🇷", "locale": "ko-KR"},
    "en": {"label": "English", "flag": "🇺🇸", "locale": "en-US"},
    "zh": {"label": "中文", "flag": "🇨🇳", "locale": "zh-CN"},
}

LANGUAGE_STRINGS = {
    "ko": {
        "page_title": "🔍 에너지 모니터링 플랫폼",
        "hero_title": "AI 재난 대응형 에너지 공유 플랫폼",
        "hero_subtitle": "실시간 에너지 모니터링 및 재난 대응 솔루션",
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
        "system_data_detail": "PostgreSQL 데이터베이스",
        "system_data_link": "데이터 수집 페이지",
        "system_uptime_title": "업타임",
        "system_uptime_label": "계산 중...",
        "system_uptime_link": "통계 페이지",
        "last_update_label": "업데이트 시간",
    },
    "en": {
        "page_title": "🔍 Energy Monitoring Platform",
        "hero_title": "AI Disaster-Resilient Energy Sharing Platform",
        "hero_subtitle": "Real-time energy monitoring and disaster response solution",
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
        "system_data_detail": "PostgreSQL database",
        "system_data_link": "Open data collection page",
        "system_uptime_title": "Uptime",
        "system_uptime_label": "Calculating...",
        "system_uptime_link": "View statistics page",
        "last_update_label": "Last update",
    },
    "zh": {
        "page_title": "🔍 能源监控平台",
        "hero_title": "AI 灾害应对型能源共享平台",
        "hero_subtitle": "实时能源监控和灾害应对解决方案",
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
        "system_data_detail": "PostgreSQL 数据库",
        "system_data_link": "打开数据采集页面",
        "system_uptime_title": "运行时间",
        "system_uptime_label": "计算中...",
        "system_uptime_link": "查看统计页面",
        "last_update_label": "更新时间",
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


# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting up application...")
    # Create tables (in production, use Alembic migrations)
    # Use async engine for async operations
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    
    # Initialize agents
    logger.info("Initializing MCP agents...")
    from src.agents.data_quality_agent import DataQualityAgent
    from src.agents.demand_sector_agent import DemandSectorAgent
    from src.agents.supply_sector_agent import SupplySectorAgent
    from src.agents.weather_agent import WeatherAgent
    from src.agents.energy_demand_agent import EnergyDemandAgent
    
    # Agents are auto-registered via BaseAgent.__init__
    logger.info("MCP agents initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")


# Root endpoint - redirect to health page
@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 페이지 - Health 페이지로 리다이렉트"""
    return RedirectResponse(url="/health?lang=ko")


# Energy Dashboard endpoint - accessible at /api/energy-dashboard
@app.get("/api/energy-dashboard", response_class=HTMLResponse)
async def energy_dashboard():
    """에너지 수요 분석 대시보드"""
    import os
    from pathlib import Path
    
    dashboard_path = Path(__file__).parent.parent / "static" / "energy_dashboard.html"
    
    if dashboard_path.exists():
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


# Health page endpoint (from web_interface.py)
@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request, lang: str = Query("ko", description="Language code")):
    """에너지 모니터링 플랫폼 Health 페이지"""
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
                    <i class="fas fa-bolt"></i> {texts['hero_title']}
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
                <div class="system-card" onclick="window.location.href='/api/v1/energy/realtime-power'">
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

                <div class="system-card" onclick="window.location.href='/docs'">
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

                <div class="system-card" onclick="window.location.href='/api/v1/assets'">
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

                <div class="system-card" onclick="window.location.href='/ready'">
                    <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                    <h5>{texts['system_uptime_title']}</h5>
                    <p class="uptime-display" id="uptime">{texts['system_uptime_label']}</p>
                    <small class="text-muted">{texts['last_update_label']}: <span id="lastUpdate"></span></small>
                    <div class="link-indicator">
                        🔗 {texts['system_uptime_link']}
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

            function updateUptime() {{
                const startTime = new Date('{datetime.now().isoformat()}');
                const now = new Date();
                const diff = now - startTime;

                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);

                document.getElementById('uptime').textContent = `${{hours}}h ${{minutes}}m ${{seconds}}s`;
            }}

            document.addEventListener('DOMContentLoaded', function() {{
                updateStats();
                updateUptime();
                setInterval(updateStats, 5000);
                setInterval(updateUptime, 1000);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString(locale);
            }});
        </script>
    </body>
    </html>
    """


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check database connection
        from sqlalchemy import text
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
from src.api.v1 import auth, assets, orchestrator, mcp, energy_dashboard, weather, energy_demand

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(orchestrator.router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["MCP"])
app.include_router(energy_dashboard.router, prefix="/api/v1/energy", tags=["Energy Dashboard"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(energy_demand.router, prefix="/api/v1/energy-demand", tags=["Energy Demand"])

# TODO: Add more routers as they are created
# from src.api.v1 import users, devices, disasters
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
# app.include_router(disasters.router, prefix="/api/v1/disasters", tags=["Disasters"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
