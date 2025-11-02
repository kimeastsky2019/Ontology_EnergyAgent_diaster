#!/usr/bin/env python3
"""
새로운 웹 인터페이스 - 게이지 차트와 도넛 차트를 사용한 현황/예측 대시보드
"""

import uvicorn
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
from datetime import datetime, timedelta
import random
import math

# FastAPI 앱 생성
web_app = FastAPI(title="Energy Analysis Web Interface", version="2.0")

# MCP 도구 등록 함수 (기존과 동일)
def register_tools():
    """MCP 도구들을 등록"""
    pass

@web_app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, lang: str = Query("ko", description="Language code")):
    """홈페이지"""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌞 Energy Analysis Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-gauge@0.3.0/dist/chartjs-gauge.min.js"></script>
        <style>
            body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .main-card {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            .metric-card {{ background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; border-radius: 15px; transition: transform 0.3s; }}
            .metric-card:hover {{ transform: translateY(-5px); }}
            .metric-card.success {{ background: linear-gradient(135deg, #00b894, #00a085); }}
            .metric-card.warning {{ background: linear-gradient(135deg, #fdcb6e, #e17055); }}
            .metric-card.info {{ background: linear-gradient(135deg, #74b9ff, #0984e3); }}
            .chart-container {{ position: relative; height: 300px; margin: 20px 0; }}
            .gauge-container {{ position: relative; height: 200px; margin: 20px 0; }}
            .status-indicator {{ 
                width: 12px; height: 12px; border-radius: 50%; 
                display: inline-block; margin-right: 8px; 
                animation: pulse 2s infinite;
            }}
            .status-past {{ background-color: #ff6b6b; }}
            .status-current {{ background-color: #00b894; }}
            .status-future {{ background-color: #e17055; }}
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
            .prediction-card {{ background: linear-gradient(135deg, #a29bfe, #6c5ce7); color: white; border-radius: 15px; }}
        </style>
    </head>
    <body>
        <div class="container-fluid py-4">
            <div class="row justify-content-center">
                <div class="col-12 col-xl-10">
                    <div class="main-card p-4">
                        <!-- 헤더 -->
                        <div class="text-center mb-4">
                            <h1 class="display-4 fw-bold text-primary">
                                <i class="fas fa-sun"></i> Energy Analysis Platform
                            </h1>
                            <p class="lead text-muted">Real-time Weather & Energy Monitoring Dashboard</p>
                        </div>

                        <!-- 네비게이션 -->
                        <nav class="navbar navbar-expand-lg navbar-light bg-light rounded mb-4">
                            <div class="container-fluid">
                                <a class="navbar-brand fw-bold" href="/">
                                    <i class="fas fa-home"></i> Home
                                </a>
                                <div class="navbar-nav ms-auto">
                                    <a class="nav-link" href="/data-collection?lang={lang}">
                                        <i class="fas fa-chart-line"></i> Data Collection
                                    </a>
                                    <a class="nav-link" href="/data-analysis?lang={lang}">
                                        <i class="fas fa-chart-bar"></i> Analysis
                                    </a>
                                </div>
                            </div>
                        </nav>

                        <!-- 메인 대시보드 -->
                        <div class="row">
                            <!-- 왼쪽: 실시간 메트릭 -->
                            <div class="col-md-6">
                                <h3 class="mb-3"><i class="fas fa-tachometer-alt"></i> Real-time Metrics</h3>
                                
                                <!-- 메트릭 카드들 -->
                                <div class="row mb-4">
                                    <div class="col-6 mb-3">
                                        <div class="metric-card p-3 text-center">
                                            <i class="fas fa-thermometer-half fa-2x mb-2"></i>
                                            <h4 id="currentTemp">24.5°C</h4>
                                            <small>Temperature</small>
                                        </div>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <div class="metric-card success p-3 text-center">
                                            <i class="fas fa-tint fa-2x mb-2"></i>
                                            <h4 id="currentHumidity">65%</h4>
                                            <small>Humidity</small>
                                        </div>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <div class="metric-card warning p-3 text-center">
                                            <i class="fas fa-wind fa-2x mb-2"></i>
                                            <h4 id="currentWind">2.3 m/s</h4>
                                            <small>Wind Speed</small>
                                        </div>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <div class="metric-card info p-3 text-center">
                                            <i class="fas fa-sun fa-2x mb-2"></i>
                                            <h4 id="currentSolar">850 W/m²</h4>
                                            <small>Solar Radiation</small>
                                        </div>
                                    </div>
                                </div>

                                <!-- 상태 표시기 -->
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5><i class="fas fa-info-circle"></i> Data Status</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span><span class="status-indicator status-past"></span>Past Data</span>
                                            <span class="badge bg-secondary">60%</span>
                                        </div>
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span><span class="status-indicator status-current"></span>Current Data</span>
                                            <span class="badge bg-success">20%</span>
                                        </div>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <span><span class="status-indicator status-future"></span>Prediction</span>
                                            <span class="badge bg-warning">20%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 오른쪽: 게이지 차트들 -->
                            <div class="col-md-6">
                                <h3 class="mb-3"><i class="fas fa-chart-pie"></i> Current Status & Prediction</h3>
                                
                                <!-- 온도 게이지 -->
                                <div class="row mb-3">
                                    <div class="col-6">
                                        <div class="gauge-container">
                                            <canvas id="tempGauge"></canvas>
                                        </div>
                                        <h6 class="text-center">Temperature</h6>
                                    </div>
                                    <div class="col-6">
                                        <div class="gauge-container">
                                            <canvas id="humidityGauge"></canvas>
                                        </div>
                                        <h6 class="text-center">Humidity</h6>
                                    </div>
                                </div>

                                <!-- 풍속과 태양복사량 도넛 차트 -->
                                <div class="row">
                                    <div class="col-6">
                                        <div class="chart-container">
                                            <canvas id="windDonut"></canvas>
                                        </div>
                                        <h6 class="text-center">Wind Speed</h6>
                                    </div>
                                    <div class="col-6">
                                        <div class="chart-container">
                                            <canvas id="solarDonut"></canvas>
                                        </div>
                                        <h6 class="text-center">Solar Radiation</h6>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 예측 섹션 -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="prediction-card p-4">
                                    <h4><i class="fas fa-crystal-ball"></i> Weather Prediction</h4>
                                    <div class="row">
                                        <div class="col-md-3 text-center">
                                            <h5>+1 Hour</h5>
                                            <div class="d-flex justify-content-center align-items-center">
                                                <i class="fas fa-thermometer-half fa-2x me-2"></i>
                                                <div>
                                                    <div id="predTemp1">25.2°C</div>
                                                    <small>Temperature</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3 text-center">
                                            <h5>+2 Hours</h5>
                                            <div class="d-flex justify-content-center align-items-center">
                                                <i class="fas fa-tint fa-2x me-2"></i>
                                                <div>
                                                    <div id="predHumidity2">68%</div>
                                                    <small>Humidity</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3 text-center">
                                            <h5>+3 Hours</h5>
                                            <div class="d-flex justify-content-center align-items-center">
                                                <i class="fas fa-wind fa-2x me-2"></i>
                                                <div>
                                                    <div id="predWind3">2.8 m/s</div>
                                                    <small>Wind Speed</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3 text-center">
                                            <h5>+4 Hours</h5>
                                            <div class="d-flex justify-content-center align-items-center">
                                                <i class="fas fa-sun fa-2x me-2"></i>
                                                <div>
                                                    <div id="predSolar4">920 W/m²</div>
                                                    <small>Solar Radiation</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 에너지 상관관계 -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-link"></i> Energy Correlations</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row text-center">
                                            <div class="col-4">
                                                <div class="p-3">
                                                    <h3 class="text-danger" id="tempCorrelation">0.78</h3>
                                                    <p class="mb-0">Temperature vs Consumption</p>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="p-3">
                                                    <h3 class="text-success" id="solarCorrelation">0.92</h3>
                                                    <p class="mb-0">Solar vs Generation</p>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="p-3">
                                                    <h3 class="text-warning" id="humidityCorrelation">-0.45</h3>
                                                    <p class="mb-0">Humidity vs Efficiency</p>
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
        <script>
            // 전역 변수
            let tempGauge, humidityGauge, windDonut, solarDonut;
            let currentData = {{
                temperature: 24.5,
                humidity: 65,
                windSpeed: 2.3,
                solarRadiation: 850
            }};

            // 데이터 생성 함수
            function generateData() {{
                const now = new Date();
                const hour = now.getHours();
                
                // 시간대별 기본값
                let baseTemp = 20 + Math.sin((hour - 6) * Math.PI / 12) * 8;
                let baseHumidity = 70 - Math.sin((hour - 6) * Math.PI / 12) * 20;
                let baseWind = 2 + Math.random() * 3;
                let baseSolar = Math.max(0, Math.sin((hour - 6) * Math.PI / 12) * 1000);
                
                // 랜덤 변동 추가
                currentData = {{
                    temperature: baseTemp + (Math.random() - 0.5) * 4,
                    humidity: Math.max(30, Math.min(90, baseHumidity + (Math.random() - 0.5) * 10)),
                    windSpeed: Math.max(0, baseWind + (Math.random() - 0.5) * 2),
                    solarRadiation: Math.max(0, baseSolar + (Math.random() - 0.5) * 200)
                }};
                
                return currentData;
            }}

            // 게이지 차트 생성
            function createGaugeChart(canvasId, value, max, color, label) {{
                const ctx = document.getElementById(canvasId).getContext('2d');
                return new Chart(ctx, {{
                    type: 'gauge',
                    data: {{
                        datasets: [{{
                            value: value,
                            minValue: 0,
                            maxValue: max,
                            backgroundColor: [color],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '75%',
                        circumference: 180,
                        rotation: 270,
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                enabled: false
                            }}
                        }},
                        elements: {{
                            arc: {{
                                borderWidth: 0
                            }}
                        }}
                    }}
                }});
            }}

            // 도넛 차트 생성
            function createDonutChart(canvasId, current, predicted, color, label) {{
                const ctx = document.getElementById(canvasId).getContext('2d');
                return new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Current', 'Predicted'],
                        datasets: [{{
                            data: [current, predicted],
                            backgroundColor: [color, color + '80'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.label + ': ' + context.parsed.toFixed(1);
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            // 차트 초기화
            function initializeCharts() {{
                const data = generateData();
                
                // 게이지 차트 생성
                tempGauge = createGaugeChart('tempGauge', data.temperature, 40, '#ff6b6b', 'Temperature');
                humidityGauge = createGaugeChart('humidityGauge', data.humidity, 100, '#00b894', 'Humidity');
                
                // 도넛 차트 생성
                windDonut = createDonutChart('windDonut', data.windSpeed, data.windSpeed * 1.2, '#fdcb6e', 'Wind Speed');
                solarDonut = createDonutChart('solarDonut', data.solarRadiation, data.solarRadiation * 1.1, '#74b9ff', 'Solar Radiation');
                
                // 메트릭 업데이트
                updateMetrics(data);
                
                // 예측 데이터 업데이트
                updatePredictions(data);
            }}

            // 메트릭 업데이트
            function updateMetrics(data) {{
                document.getElementById('currentTemp').textContent = data.temperature.toFixed(1) + '°C';
                document.getElementById('currentHumidity').textContent = data.humidity.toFixed(0) + '%';
                document.getElementById('currentWind').textContent = data.windSpeed.toFixed(1) + ' m/s';
                document.getElementById('currentSolar').textContent = data.solarRadiation.toFixed(0) + ' W/m²';
            }}

            // 예측 데이터 업데이트
            function updatePredictions(data) {{
                document.getElementById('predTemp1').textContent = (data.temperature + 0.7).toFixed(1) + '°C';
                document.getElementById('predHumidity2').textContent = (data.humidity + 3).toFixed(0) + '%';
                document.getElementById('predWind3').textContent = (data.windSpeed + 0.5).toFixed(1) + ' m/s';
                document.getElementById('predSolar4').textContent = (data.solarRadiation + 70).toFixed(0) + ' W/m²';
            }}

            // 상관관계 업데이트
            function updateCorrelations() {{
                document.getElementById('tempCorrelation').textContent = (0.75 + Math.random() * 0.1).toFixed(2);
                document.getElementById('solarCorrelation').textContent = (0.90 + Math.random() * 0.05).toFixed(2);
                document.getElementById('humidityCorrelation').textContent = (-0.40 - Math.random() * 0.1).toFixed(2);
            }}

            // 데이터 업데이트
            function updateData() {{
                const newData = generateData();
                
                // 게이지 차트 업데이트
                tempGauge.data.datasets[0].value = newData.temperature;
                humidityGauge.data.datasets[0].value = newData.humidity;
                
                // 도넛 차트 업데이트
                windDonut.data.datasets[0].data = [newData.windSpeed, newData.windSpeed * 1.2];
                solarDonut.data.datasets[0].data = [newData.solarRadiation, newData.solarRadiation * 1.1];
                
                // 차트 다시 그리기
                tempGauge.update('none');
                humidityGauge.update('none');
                windDonut.update('none');
                solarDonut.update('none');
                
                // 메트릭 및 예측 업데이트
                updateMetrics(newData);
                updatePredictions(newData);
                updateCorrelations();
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initializeCharts();
                setInterval(updateData, 5000); // 5초마다 업데이트
            }});
        </script>
    </body>
    </html>
    """

@web_app.get("/data-collection", response_class=HTMLResponse)
async def data_collection_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Data Collection 페이지 - 홈페이지와 동일한 내용"""
    return await home_page(request, lang)

@web_app.get("/data-analysis", response_class=HTMLResponse)
async def data_analysis_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Data Analysis 페이지 - 홈페이지와 동일한 내용"""
    return await home_page(request, lang)

if __name__ == "__main__":
    # MCP 도구 등록
    register_tools()
    
    # 웹 서버 실행
    uvicorn.run(web_app, host="0.0.0.0", port=8000)

