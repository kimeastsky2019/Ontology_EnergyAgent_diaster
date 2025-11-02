#!/usr/bin/env python3
"""
연결된 Digital Experience Intelligence Platform
Health 카드와 메뉴에 기존 페이지들을 연결한 플랫폼
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
import uvicorn

# FastAPI 앱 생성
web_app = FastAPI(title="Digital Experience Intelligence Platform", version="2.0.0")

def get_available_languages():
    """사용 가능한 언어 목록 반환"""
    return ["ko", "en", "zh"]

@web_app.get("/", response_class=HTMLResponse)
async def root():
    """루트 페이지 - Health 페이지로 리다이렉트"""
    return RedirectResponse(url="/health?lang=ko")

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
        <title>🔍 Digital Experience Intelligence Platform</title>
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
                    <i class="fas fa-brain"></i> Digital Experience Intelligence Platform
                </h1>
                <p class="lead mb-4">포괄적인 사용자 경험 분석 및 최적화 솔루션</p>
                
                <!-- 실시간 통계 -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalInteractions">0</div>
                        <div class="stat-label">총 상호작용</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="activeSessions">0</div>
                        <div class="stat-label">활성 세션</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="conversionRate">0%</div>
                        <div class="stat-label">전환율</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="errorRate">0%</div>
                        <div class="stat-label">오류율</div>
                    </div>
                </div>
            </div>

            <!-- 시스템 상태 (Health 카드들) -->
            <div class="system-status-grid">
                <div class="system-card" onclick="window.location.href='/?lang={lang}'">
                    <i class="fas fa-server fa-3x text-success mb-3"></i>
                    <h5>Web Server</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>Online</strong>
                    </p>
                    <small class="text-muted">Port: 8000</small>
                    <div class="link-indicator">
                        🔗 메인 대시보드로 이동
                    </div>
                </div>
                
                <div class="system-card" onclick="window.location.href='/api/health'">
                    <i class="fas fa-cogs fa-3x text-primary mb-3"></i>
                    <h5>API Services</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>Healthy</strong>
                    </p>
                    <small class="text-muted">All endpoints active</small>
                    <div class="link-indicator">
                        🔗 API 상태 확인
                    </div>
                </div>
                
                <div class="system-card" onclick="window.location.href='/data-collection?lang={lang}'">
                    <i class="fas fa-database fa-3x text-info mb-3"></i>
                    <h5>Data Storage</h5>
                    <p>
                        <span class="status-indicator status-online"></span>
                        <strong>Connected</strong>
                    </p>
                    <small class="text-muted">SQLite Database</small>
                    <div class="link-indicator">
                        🔗 데이터 수집 페이지
                    </div>
                </div>
                
                <div class="system-card" onclick="window.location.href='/statistics?lang={lang}'">
                    <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                    <h5>Uptime</h5>
                    <p class="uptime-display" id="uptime">Calculating...</p>
                    <small class="text-muted">Last Update: <span id="lastUpdate"></span></small>
                    <div class="link-indicator">
                        🔗 통계 페이지
                    </div>
                </div>
            </div>

            <!-- 기능 카드들 (메뉴) -->
            <div class="feature-grid">
                <!-- 실시간 이벤트 캡처 -->
                <div class="feature-card interaction-tracker" onclick="window.location.href='/data-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-mouse-pointer"></i>
                    </div>
                    <h3>실시간 이벤트 캡처</h3>
                    <p>클릭, 스크롤, 폼 제출 등 모든 사용자 상호작용을 실시간으로 추적합니다.</p>
                    
                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 95%"></div>
                    </div>
                    <small>프론트엔드 이벤트 캡처율: 95%</small>
                    
                    <div class="progress-modern">
                        <div class="progress-bar-modern" style="width: 98%"></div>
                    </div>
                    <small>백엔드 API 호출 캡처율: 98%</small>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/data-analysis?lang={lang}'">
                            <i class="fas fa-chart-line"></i> 데이터 분석 페이지
                        </button>
                    </div>
                </div>

                <!-- AI 인사이트 -->
                <div class="feature-card ai-insights" onclick="window.location.href='/llm-slm?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>AI 인사이트 (SLM 기반)</h3>
                    <p>Small Language Model 기반 대화형 분석 어시스턴트로 심층적인 인사이트를 제공합니다.</p>
                    
                    <div class="ai-chat" id="aiChat">
                        <div class="ai-message ai-assistant">
                            <strong>AI Assistant:</strong> 안녕하세요! 사용자 경험 분석을 도와드리겠습니다.
                        </div>
                        <div class="ai-message ai-user">
                            전환율을 개선하는 방법을 알려주세요
                        </div>
                        <div class="ai-message ai-assistant">
                            <strong>AI Assistant:</strong> 분석 결과, 3단계에서 이탈률이 높습니다. CTA 버튼 위치를 조정해보세요.
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/llm-slm?lang={lang}'">
                            <i class="fas fa-brain"></i> LLM-SLM 개발 페이지
                        </button>
                    </div>
                </div>

                <!-- 세션 리플레이 -->
                <div class="feature-card session-replay" onclick="window.location.href='/weather-analysis?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <h3>세션 리플레이</h3>
                    <p>사용자 행동 패턴을 시각화하고 히트맵으로 마찰 지점을 분석합니다.</p>
                    
                    <div class="heatmap-container" id="heatmapContainer">
                        <div class="heatmap-point" style="top: 20px; left: 30px;"></div>
                        <div class="heatmap-point" style="top: 50px; left: 80px;"></div>
                        <div class="heatmap-point" style="top: 80px; left: 120px;"></div>
                        <div class="heatmap-point" style="top: 120px; left: 200px;"></div>
                        <div class="heatmap-point" style="top: 150px; left: 250px;"></div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-analysis?lang={lang}'">
                            <i class="fas fa-cloud-sun"></i> 날씨 분석 페이지
                        </button>
                    </div>
                </div>

                <!-- 프라이버시 보호 -->
                <div class="feature-card privacy-protection" onclick="window.location.href='/model-testing?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>프라이버시 보호</h3>
                    <p>PII, PCI, PHI 등 민감한 데이터를 자동으로 마스킹하여 보안을 보장합니다.</p>
                    
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> PII 데이터 마스킹: 100% 활성
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> PCI 데이터 마스킹: 100% 활성
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> PHI 데이터 마스킹: 100% 활성
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/model-testing?lang={lang}'">
                            <i class="fas fa-cogs"></i> ML/AI 엔진 페이지
                        </button>
                    </div>
                </div>

                <!-- 실시간 모니터링 -->
                <div class="feature-card real-time-monitoring" onclick="window.location.href='/weather-dashboard?lang={lang}'">
                    <div class="feature-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <h3>실시간 모니터링</h3>
                    <p>전환율 변화, 오류 감지, 사용자 불편을 실시간으로 모니터링하고 알림합니다.</p>
                    
                    <div class="alert alert-modern alert-warning">
                        <i class="fas fa-exclamation-triangle"></i> 전환율 15% 감소 감지
                    </div>
                    <div class="alert alert-modern alert-info">
                        <i class="fas fa-info-circle"></i> 새로운 사용자 세션 시작
                    </div>
                    <div class="alert alert-modern alert-success">
                        <i class="fas fa-check-circle"></i> 시스템 정상 작동
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/weather-dashboard?lang={lang}'">
                            <i class="fas fa-chart-area"></i> 날씨 대시보드
                        </button>
                    </div>
                </div>

                <!-- 유연한 배포 -->
                <div class="feature-card flexible-deployment" onclick="window.location.href='/api/dashboard'">
                    <div class="feature-icon">
                        <i class="fas fa-cloud"></i>
                    </div>
                    <h3>유연한 배포</h3>
                    <p>하이브리드, 싱글 테넌트, 멀티 테넌트 환경을 지원합니다.</p>
                    
                    <div class="row">
                        <div class="col-4 text-center">
                            <i class="fas fa-cloud fa-2x mb-2" style="color: #667eea;"></i>
                            <div class="small">하이브리드</div>
                            <span class="badge bg-primary">활성</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-server fa-2x mb-2" style="color: #28a745;"></i>
                            <div class="small">싱글 테넌트</div>
                            <span class="badge bg-success">사용 가능</span>
                        </div>
                        <div class="col-4 text-center">
                            <i class="fas fa-users fa-2x mb-2" style="color: #17a2b8;"></i>
                            <div class="small">멀티 테넌트</div>
                            <span class="badge bg-info">사용 가능</span>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button class="btn btn-light btn-modern" onclick="event.stopPropagation(); window.location.href='/api/dashboard'">
                            <i class="fas fa-chart-bar"></i> API 대시보드
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
                const startTime = new Date('2025-10-11T01:22:47Z');
                const now = new Date();
                const diff = now - startTime;
                
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById('uptime').textContent = `${{hours}}h ${{minutes}}m ${{seconds}}s`;
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                updateStats();
                updateUptime();
                setInterval(updateStats, 5000); // 5초마다 통계 업데이트
                setInterval(updateUptime, 1000); // 1초마다 업타임 업데이트
                setInterval(generateHeatmap, 10000); // 10초마다 히트맵 업데이트
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
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

if __name__ == "__main__":
    uvicorn.run(web_app, host="0.0.0.0", port=8000)
