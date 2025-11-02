#!/usr/bin/env python3
"""
Weather Data Analysis 전용 페이지
"""

import uvicorn
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse

# FastAPI 앱 생성
app = FastAPI(title="Weather Analysis", version="1.0")

@app.get("/weather-analysis", response_class=HTMLResponse)
async def weather_analysis_page(request: Request, lang: str = Query("ko", description="Language code")):
    """Weather Data Analysis 전용 페이지"""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌤️ Weather Data Analysis</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .main-card {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            .weather-stat {{ text-align: center; padding: 15px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; border-radius: 10px; margin: 5px; }}
            .weather-stat.success {{ background: linear-gradient(135deg, #00b894, #00a085); }}
            .weather-stat.warning {{ background: linear-gradient(135deg, #fdcb6e, #e17055); }}
            .weather-stat.info {{ background: linear-gradient(135deg, #74b9ff, #0984e3); }}
            .stat-value {{ font-size: 1.5rem; font-weight: bold; }}
            .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}
            .prediction-card {{ background: linear-gradient(135deg, #a29bfe, #6c5ce7); color: white; border-radius: 15px; padding: 20px; }}
            .correlation-item {{ text-align: center; padding: 10px; }}
            .correlation-value {{ font-size: 1.8rem; font-weight: bold; }}
            .correlation-label {{ font-size: 0.8rem; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container-fluid py-4">
            <div class="row justify-content-center">
                <div class="col-12 col-xl-10">
                    <div class="main-card p-4">
                        <!-- 헤더 -->
                        <div class="text-center mb-4">
                            <h1 class="display-5 fw-bold text-primary">
                                <i class="fas fa-cloud-sun"></i> Weather Data Analysis
                            </h1>
                            <p class="lead text-muted">Real-time Weather Monitoring & Prediction</p>
                        </div>

                        <!-- 날씨 통계 요약 -->
                        <div class="row mb-4">
                            <div class="col-6 col-md-3">
                                <div class="weather-stat">
                                    <div class="stat-value" id="avgTemperature">24.5°C</div>
                                    <div class="stat-label">평균 온도</div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="weather-stat success">
                                    <div class="stat-value" id="avgHumidity">65%</div>
                                    <div class="stat-label">평균 습도</div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="weather-stat warning">
                                    <div class="stat-value" id="maxWindSpeed">2.3 m/s</div>
                                    <div class="stat-label">최대 풍속</div>
                                </div>
                            </div>
                            <div class="col-6 col-md-3">
                                <div class="weather-stat info">
                                    <div class="stat-value" id="solarIrradiance">850 W/m²</div>
                                    <div class="stat-label">태양 복사량</div>
                                </div>
                            </div>
                        </div>

                        <!-- 현황/예측 차트 -->
                        <div class="row mb-4">
                            <div class="col-6">
                                <div class="text-center">
                                    <canvas id="weatherTempGauge" height="120"></canvas>
                                    <h6 class="mt-2">Temperature</h6>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <canvas id="weatherHumidityGauge" height="120"></canvas>
                                    <h6 class="mt-2">Humidity</h6>
                                </div>
                            </div>
                        </div>

                        <div class="row mb-4">
                            <div class="col-6">
                                <div class="text-center">
                                    <canvas id="weatherWindDonut" height="120"></canvas>
                                    <h6 class="mt-2">Wind Speed</h6>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <canvas id="weatherSolarDonut" height="120"></canvas>
                                    <h6 class="mt-2">Solar Radiation</h6>
                                </div>
                            </div>
                        </div>

                        <!-- 예측 섹션 -->
                        <div class="prediction-card mb-4">
                            <h4 class="text-center mb-3"><i class="fas fa-crystal-ball"></i> Weather Prediction</h4>
                            <div class="row text-center">
                                <div class="col-3">
                                    <h6>+1 Hour</h6>
                                    <div class="fw-bold" id="predTemp1">25.2°C</div>
                                    <small>Temperature</small>
                                </div>
                                <div class="col-3">
                                    <h6>+2 Hours</h6>
                                    <div class="fw-bold" id="predHumidity2">68%</div>
                                    <small>Humidity</small>
                                </div>
                                <div class="col-3">
                                    <h6>+3 Hours</h6>
                                    <div class="fw-bold" id="predWind3">2.8 m/s</div>
                                    <small>Wind Speed</small>
                                </div>
                                <div class="col-3">
                                    <h6>+4 Hours</h6>
                                    <div class="fw-bold" id="predSolar4">920 W/m²</div>
                                    <small>Solar Radiation</small>
                                </div>
                            </div>
                        </div>

                        <!-- 에너지 상관관계 -->
                        <div class="row">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h5><i class="fas fa-link"></i> 에너지 상관관계</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row text-center">
                                            <div class="col-4">
                                                <div class="correlation-item">
                                                    <div class="correlation-value text-danger" id="tempCorrelation">0.78</div>
                                                    <div class="correlation-label">온도 vs 소비</div>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="correlation-item">
                                                    <div class="correlation-value text-success" id="solarCorrelation">0.92</div>
                                                    <div class="correlation-label">태양광 vs 발전</div>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="correlation-item">
                                                    <div class="correlation-value text-warning" id="humidityCorrelation">-0.45</div>
                                                    <div class="correlation-label">습도 vs 효율</div>
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
            let weatherCharts = {{}};
            let currentData = {{
                temperature: 24.5,
                humidity: 65,
                windSpeed: 2.3,
                irradiance: 850
            }};

            // 데이터 생성 함수
            function generateWeatherData() {{
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
                    irradiance: Math.max(0, baseSolar + (Math.random() - 0.5) * 200)
                }};
                
                return currentData;
            }}

            // 게이지 차트 생성 함수
            function createWeatherGaugeChart(canvasId, value, max, color, label) {{
                const ctx = document.getElementById(canvasId).getContext('2d');
                const chart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        datasets: [{{
                            data: [value, max - value],
                            backgroundColor: [color, '#f0f0f0'],
                            borderWidth: 0,
                            cutout: '75%'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
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
                
                weatherCharts[canvasId] = chart;
                return chart;
            }}

            // 도넛 차트 생성 함수
            function createWeatherDonutChart(canvasId, current, predicted, color, label) {{
                const ctx = document.getElementById(canvasId).getContext('2d');
                const chart = new Chart(ctx, {{
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
                
                weatherCharts[canvasId] = chart;
                return chart;
            }}

            // 차트 초기화
            function initializeWeatherCharts() {{
                const data = generateWeatherData();
                
                // 게이지 차트 생성
                createWeatherGaugeChart('weatherTempGauge', data.temperature, 40, '#ff6b6b', 'Temperature');
                createWeatherGaugeChart('weatherHumidityGauge', data.humidity, 100, '#00b894', 'Humidity');
                
                // 도넛 차트 생성
                createWeatherDonutChart('weatherWindDonut', data.windSpeed, data.windSpeed * 1.2, '#fdcb6e', 'Wind Speed');
                createWeatherDonutChart('weatherSolarDonut', data.irradiance, data.irradiance * 1.1, '#74b9ff', 'Solar Radiation');
                
                // 메트릭 업데이트
                updateWeatherMetrics(data);
                
                // 예측 데이터 업데이트
                updateWeatherPredictions(data);
                
                // 상관관계 업데이트
                updateCorrelations();
            }}

            // 메트릭 업데이트
            function updateWeatherMetrics(data) {{
                document.getElementById('avgTemperature').textContent = data.temperature.toFixed(1) + '°C';
                document.getElementById('avgHumidity').textContent = data.humidity.toFixed(0) + '%';
                document.getElementById('maxWindSpeed').textContent = data.windSpeed.toFixed(1) + ' m/s';
                document.getElementById('solarIrradiance').textContent = data.irradiance.toFixed(0) + ' W/m²';
            }}

            // 예측 데이터 업데이트
            function updateWeatherPredictions(data) {{
                document.getElementById('predTemp1').textContent = (data.temperature + 0.7).toFixed(1) + '°C';
                document.getElementById('predHumidity2').textContent = (data.humidity + 3).toFixed(0) + '%';
                document.getElementById('predWind3').textContent = (data.windSpeed + 0.5).toFixed(1) + ' m/s';
                document.getElementById('predSolar4').textContent = (data.irradiance + 70).toFixed(0) + ' W/m²';
            }}

            // 상관관계 업데이트
            function updateCorrelations() {{
                document.getElementById('tempCorrelation').textContent = (0.75 + Math.random() * 0.1).toFixed(2);
                document.getElementById('solarCorrelation').textContent = (0.90 + Math.random() * 0.05).toFixed(2);
                document.getElementById('humidityCorrelation').textContent = (-0.40 - Math.random() * 0.1).toFixed(2);
            }}

            // 데이터 업데이트
            function updateWeatherData() {{
                const newData = generateWeatherData();
                
                // 게이지 차트 업데이트
                if (weatherCharts['weatherTempGauge']) {{
                    weatherCharts['weatherTempGauge'].data.datasets[0].data = [newData.temperature, 40 - newData.temperature];
                    weatherCharts['weatherTempGauge'].update('none');
                }}
                
                if (weatherCharts['weatherHumidityGauge']) {{
                    weatherCharts['weatherHumidityGauge'].data.datasets[0].data = [newData.humidity, 100 - newData.humidity];
                    weatherCharts['weatherHumidityGauge'].update('none');
                }}
                
                // 도넛 차트 업데이트
                if (weatherCharts['weatherWindDonut']) {{
                    weatherCharts['weatherWindDonut'].data.datasets[0].data = [newData.windSpeed, newData.windSpeed * 1.2];
                    weatherCharts['weatherWindDonut'].update('none');
                }}
                
                if (weatherCharts['weatherSolarDonut']) {{
                    weatherCharts['weatherSolarDonut'].data.datasets[0].data = [newData.irradiance, newData.irradiance * 1.1];
                    weatherCharts['weatherSolarDonut'].update('none');
                }}
                
                // 메트릭 및 예측 업데이트
                updateWeatherMetrics(newData);
                updateWeatherPredictions(newData);
                updateCorrelations();
            }}

            // 초기화
            document.addEventListener('DOMContentLoaded', function() {{
                initializeWeatherCharts();
                setInterval(updateWeatherData, 5000); // 5초마다 업데이트
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

