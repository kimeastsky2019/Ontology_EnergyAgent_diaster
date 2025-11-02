/**
 * Energy Analysis Integration Dashboard JavaScript
 */

// 전역 변수
let socket;
let energyChart;
let currentData = null;
let monitoringActive = false;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeChart();
    loadInitialData();
    setupEventListeners();
});

// Socket.IO 초기화
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to Energy Dashboard');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from Energy Dashboard');
        updateConnectionStatus(false);
    });
    
    socket.on('forecast_completed', function(data) {
        console.log('Forecast completed:', data);
        addRealtimeAlert(`예측 완료: ${data.model_type} 모델`, 'success');
        updateForecastResults(data.result);
    });
    
    socket.on('anomaly_detection_completed', function(data) {
        console.log('Anomaly detection completed:', data);
        addRealtimeAlert(`이상치 탐지 완료: ${data.detection_methods.join(', ')}`, 'warning');
        updateAnomalyResults(data.result);
    });
    
    socket.on('climate_analysis_completed', function(data) {
        console.log('Climate analysis completed:', data);
        addRealtimeAlert(`기후 분석 완료: ${data.analysis_type}`, 'info');
        updateClimateResults(data.result);
    });
    
    socket.on('ensemble_forecast_completed', function(data) {
        console.log('Ensemble forecast completed:', data);
        addRealtimeAlert(`앙상블 예측 완료: ${data.models.join(', ')}`, 'primary');
        updateEnsembleResults(data.result);
    });
    
    socket.on('monitoring_data', function(data) {
        console.log('Monitoring data received:', data);
        updateMonitoringData(data);
    });
    
    socket.on('monitoring_stopped', function(data) {
        console.log('Monitoring stopped:', data);
        updateMonitoringStatus('모니터링이 중지되었습니다.', 'danger');
    });
}

// 연결 상태 업데이트
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connectionStatus');
    const statusText = document.getElementById('connectionText');
    
    if (connected) {
        statusIndicator.className = 'status-indicator status-online';
        statusText.textContent = '연결됨';
    } else {
        statusIndicator.className = 'status-indicator status-offline';
        statusText.textContent = '연결 끊김';
    }
}

// 차트 초기화
function initializeChart() {
    const ctx = document.getElementById('energyChart').getContext('2d');
    energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '에너지 소비',
                data: [],
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.2)',
                tension: 0.1
            }, {
                label: '예측값',
                data: [],
                borderColor: 'rgb(255, 193, 7)',
                backgroundColor: 'rgba(255, 193, 7, 0.2)',
                tension: 0.1,
                borderDash: [5, 5]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '에너지 소비량 (kWh)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '시간'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 민감도 슬라이더
    const sensitivitySlider = document.getElementById('anomalySensitivity');
    const sensitivityValue = document.getElementById('sensitivityValue');
    
    sensitivitySlider.addEventListener('input', function() {
        sensitivityValue.textContent = this.value;
    });
}

// 초기 데이터 로드
async function loadInitialData() {
    try {
        const response = await fetch('/api/energy/sample-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                n_samples: 1000,
                include_weather: true
            })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            currentData = result.data;
            updateChart(result.data);
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// 샘플 데이터 생성
async function generateSampleData() {
    showLoading('샘플 데이터 생성 중...');
    
    try {
        const sampleCount = parseInt(document.getElementById('sampleCount').value);
        const includeWeather = document.getElementById('includeWeather').value === 'true';
        
        const response = await fetch('/api/energy/sample-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                n_samples: sampleCount,
                include_weather: includeWeather
            })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            currentData = result.data;
            updateChart(result.data);
            addRealtimeAlert(`샘플 데이터 생성 완료: ${result.shape[0]}개 샘플`, 'success');
        }
    } catch (error) {
        console.error('Error generating sample data:', error);
        addRealtimeAlert('데이터 생성 중 오류가 발생했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 향상된 예측 실행
async function runEnhancedForecast() {
    if (!currentData) {
        addRealtimeAlert('먼저 데이터를 생성해주세요.', 'warning');
        return;
    }
    
    showLoading('향상된 예측 실행 중...');
    
    try {
        const modelType = document.getElementById('forecastModelType').value;
        const predictionHours = parseInt(document.getElementById('predictionHours').value);
        const includeWeather = document.getElementById('includeWeatherForecast').checked;
        const includeAnomaly = document.getElementById('includeAnomalyForecast').checked;
        
        const response = await fetch('/api/energy/forecast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                use_sample_data: true,
                model_type: modelType,
                prediction_hours: predictionHours,
                include_weather: includeWeather,
                include_anomaly_detection: includeAnomaly,
                latitude: 37.5665,
                longitude: 126.9780
            })
        });
        
        const result = await response.json();
        console.log('Enhanced forecast result:', result);
        
    } catch (error) {
        console.error('Error running enhanced forecast:', error);
        addRealtimeAlert('예측 실행 중 오류가 발생했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 이상치 탐지 실행
async function runAnomalyDetection() {
    if (!currentData) {
        addRealtimeAlert('먼저 데이터를 생성해주세요.', 'warning');
        return;
    }
    
    showLoading('이상치 탐지 실행 중...');
    
    try {
        const methods = Array.from(document.getElementById('anomalyMethods').selectedOptions)
            .map(option => option.value);
        const sensitivity = parseFloat(document.getElementById('anomalySensitivity').value);
        
        const response = await fetch('/api/energy/anomaly', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                use_sample_data: true,
                detection_methods: methods,
                sensitivity: sensitivity,
                include_weather_correlation: true,
                latitude: 37.5665,
                longitude: 126.9780
            })
        });
        
        const result = await response.json();
        console.log('Anomaly detection result:', result);
        
    } catch (error) {
        console.error('Error running anomaly detection:', error);
        addRealtimeAlert('이상치 탐지 중 오류가 발생했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 기후 분석 실행
async function runClimateAnalysis() {
    if (!currentData) {
        addRealtimeAlert('먼저 데이터를 생성해주세요.', 'warning');
        return;
    }
    
    showLoading('기후 인식 분석 실행 중...');
    
    try {
        const analysisType = document.getElementById('climateAnalysisType').value;
        const predictionDays = parseInt(document.getElementById('predictionDays').value);
        
        const response = await fetch('/api/energy/climate-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                use_sample_data: true,
                analysis_type: analysisType,
                include_precipitation: true,
                include_temperature: true,
                latitude: 37.5665,
                longitude: 126.9780,
                prediction_days: predictionDays
            })
        });
        
        const result = await response.json();
        console.log('Climate analysis result:', result);
        
    } catch (error) {
        console.error('Error running climate analysis:', error);
        addRealtimeAlert('기후 분석 중 오류가 발생했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 앙상블 예측 실행
async function runEnsembleForecast() {
    if (!currentData) {
        addRealtimeAlert('먼저 데이터를 생성해주세요.', 'warning');
        return;
    }
    
    showLoading('앙상블 예측 실행 중...');
    
    try {
        const models = [];
        if (document.getElementById('ensembleLSTM').checked) models.push('lstm');
        if (document.getElementById('ensembleCNN').checked) models.push('cnn');
        if (document.getElementById('ensembleProphet').checked) models.push('prophet');
        if (document.getElementById('ensembleARIMA').checked) models.push('arima');
        
        if (models.length === 0) {
            addRealtimeAlert('최소 하나의 모델을 선택해주세요.', 'warning');
            return;
        }
        
        const response = await fetch('/api/energy/ensemble', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                use_sample_data: true,
                models: models,
                prediction_hours: 24,
                include_uncertainty: true,
                latitude: 37.5665,
                longitude: 126.9780
            })
        });
        
        const result = await response.json();
        console.log('Ensemble forecast result:', result);
        
    } catch (error) {
        console.error('Error running ensemble forecast:', error);
        addRealtimeAlert('앙상블 예측 중 오류가 발생했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 실시간 모니터링 시작
function startMonitoring() {
    if (monitoringActive) {
        addRealtimeAlert('모니터링이 이미 실행 중입니다.', 'warning');
        return;
    }
    
    monitoringActive = true;
    socket.emit('start_monitoring', {
        data_source: 'file',
        monitoring_interval: 300,
        alert_threshold: 2.0,
        latitude: 37.5665,
        longitude: 126.9780
    });
    
    updateMonitoringStatus('모니터링이 시작되었습니다.', 'success');
    addRealtimeAlert('실시간 모니터링이 시작되었습니다.', 'info');
}

// 실시간 모니터링 중지
function stopMonitoring() {
    if (!monitoringActive) {
        addRealtimeAlert('모니터링이 실행 중이 아닙니다.', 'warning');
        return;
    }
    
    monitoringActive = false;
    socket.emit('stop_monitoring');
    
    updateMonitoringStatus('모니터링이 중지되었습니다.', 'danger');
    addRealtimeAlert('실시간 모니터링이 중지되었습니다.', 'info');
}

// 차트 업데이트
function updateChart(data) {
    if (!data || data.length === 0) return;
    
    const labels = data.map((d, i) => i);
    const consumption = data.map(d => d.consumption);
    
    energyChart.data.labels = labels;
    energyChart.data.datasets[0].data = consumption;
    energyChart.update();
}

// 예측 결과 업데이트
function updateForecastResults(result) {
    const resultsDiv = document.getElementById('forecastResults');
    
    if (result.status === 'success') {
        const predictions = result.predictions;
        let html = '<h6>예측 결과</h6>';
        
        for (const [model, pred] of Object.entries(predictions)) {
            if (Array.isArray(pred)) {
                const avgPred = pred.reduce((a, b) => a + b, 0) / pred.length;
                html += `
                    <div class="mb-2">
                        <strong>${model.toUpperCase()}:</strong> 
                        <span class="energy-metric text-warning">${avgPred.toFixed(2)} kWh</span>
                    </div>
                `;
            }
        }
        
        if (result.basic_analysis) {
            html += `<div class="mt-2"><small class="text-muted">기본 분석 완료</small></div>`;
        }
        
        resultsDiv.innerHTML = html;
        
        // 차트에 예측값 추가
        if (predictions.ensemble) {
            energyChart.data.datasets[1].data = predictions.ensemble;
            energyChart.update();
        }
    } else {
        resultsDiv.innerHTML = `<p class="text-danger">오류: ${result.message}</p>`;
    }
}

// 이상치 결과 업데이트
function updateAnomalyResults(result) {
    const resultsDiv = document.getElementById('anomalyResults');
    
    if (result.status === 'success') {
        const detectionResults = result.detection_results;
        let html = '<h6>이상치 탐지 결과</h6>';
        
        for (const [method, anomalies] of Object.entries(detectionResults)) {
            const count = Array.isArray(anomalies) ? anomalies.length : 0;
            html += `
                <div class="mb-2">
                    <strong>${method}:</strong> 
                    <span class="energy-metric text-danger">${count}개</span>
                </div>
            `;
        }
        
        if (result.consensus_anomalies) {
            html += `
                <div class="mt-2">
                    <strong>합의 이상치:</strong> 
                    <span class="energy-metric text-danger">${result.consensus_anomalies.length}개</span>
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
        
        // 대시보드 카드 업데이트
        document.getElementById('anomalyCount').textContent = result.total_anomalies_detected || 0;
    } else {
        resultsDiv.innerHTML = `<p class="text-danger">오류: ${result.message}</p>`;
    }
}

// 기후 분석 결과 업데이트
function updateClimateResults(result) {
    const resultsDiv = document.getElementById('climateResults');
    
    if (result.status === 'success') {
        let html = '<h6>기후 분석 결과</h6>';
        
        if (result.weather_correlation) {
            const correlation = result.weather_correlation.correlation_coefficient || 0;
            html += `
                <div class="mb-2">
                    <strong>날씨-에너지 상관계수:</strong> 
                    <span class="energy-metric text-info">${correlation.toFixed(3)}</span>
                </div>
            `;
            
            // 대시보드 카드 업데이트
            document.getElementById('climateCorrelation').textContent = correlation.toFixed(2);
        }
        
        if (result.energy_analysis) {
            html += `<div class="mt-2"><small class="text-muted">에너지 패턴 분석 완료</small></div>`;
        }
        
        if (result.precipitation_analysis) {
            html += `<div class="mt-2"><small class="text-muted">강수 패턴 분석 완료</small></div>`;
        }
        
        resultsDiv.innerHTML = html;
    } else {
        resultsDiv.innerHTML = `<p class="text-danger">오류: ${result.message}</p>`;
    }
}

// 앙상블 결과 업데이트
function updateEnsembleResults(result) {
    if (result.status === 'success') {
        const ensemblePred = result.ensemble_prediction;
        const uncertainty = result.uncertainty;
        
        let html = '<h6>앙상블 예측 결과</h6>';
        
        if (ensemblePred && ensemblePred.length > 0) {
            const avgPred = ensemblePred.reduce((a, b) => a + b, 0) / ensemblePred.length;
            html += `
                <div class="mb-2">
                    <strong>앙상블 예측:</strong> 
                    <span class="energy-metric text-warning">${avgPred.toFixed(2)} kWh</span>
                </div>
            `;
            
            if (uncertainty) {
                const avgUncertainty = uncertainty.reduce((a, b) => a + b, 0) / uncertainty.length;
                html += `
                    <div class="mb-2">
                        <strong>불확실성:</strong> 
                        <span class="energy-metric text-secondary">±${avgUncertainty.toFixed(2)}</span>
                    </div>
                `;
            }
        }
        
        if (result.model_weights) {
            html += '<div class="mt-2"><small class="text-muted">모델 가중치: ';
            const weights = Object.entries(result.model_weights)
                .map(([model, weight]) => `${model}: ${weight.toFixed(2)}`)
                .join(', ');
            html += weights + '</small></div>';
        }
        
        document.getElementById('forecastResults').innerHTML = html;
        
        // 차트에 앙상블 예측 추가
        if (ensemblePred) {
            energyChart.data.datasets[1].data = ensemblePred;
            energyChart.update();
        }
    }
}

// 모니터링 데이터 업데이트
function updateMonitoringData(data) {
    if (data.status === 'success') {
        const monitoringData = data.monitoring_data;
        const alerts = data.alerts || [];
        
        // 대시보드 카드 업데이트
        if (monitoringData.current_consumption) {
            // 현재 소비량 표시 (실제로는 차트에 추가)
        }
        
        if (monitoringData.anomalies_detected) {
            document.getElementById('anomalyCount').textContent = monitoringData.anomalies_detected;
        }
        
        // 알림 표시
        alerts.forEach(alert => {
            addRealtimeAlert(alert.message, alert.severity === 'high' ? 'danger' : 'warning');
        });
    }
}

// 모니터링 상태 업데이트
function updateMonitoringStatus(message, type) {
    const statusDiv = document.getElementById('monitoringStatus');
    statusDiv.innerHTML = `<span class="text-${type}">${message}</span>`;
}

// 실시간 알림 추가
function addRealtimeAlert(message, type = 'info') {
    const alertsDiv = document.getElementById('realtimeAlerts');
    
    const alertClass = {
        'success': 'alert-success',
        'danger': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info',
        'primary': 'alert-primary'
    }[type] || 'alert-info';
    
    const alertItem = document.createElement('div');
    alertItem.className = `alert ${alertClass} alert-dismissible fade show`;
    alertItem.innerHTML = `
        <i class="fas fa-circle me-2" style="font-size: 8px;"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <small class="text-muted ms-2">${new Date().toLocaleTimeString()}</small>
    `;
    
    alertsDiv.insertBefore(alertItem, alertsDiv.firstChild);
    
    // 최대 10개 알림만 유지
    const alerts = alertsDiv.querySelectorAll('.alert');
    if (alerts.length > 10) {
        alerts[alerts.length - 1].remove();
    }
}

// 로딩 모달 표시
function showLoading(text) {
    document.getElementById('loadingText').textContent = text;
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

// 로딩 모달 숨기기
function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
    }
}


