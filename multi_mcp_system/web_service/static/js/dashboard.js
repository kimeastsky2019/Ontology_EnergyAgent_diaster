/**
 * Multi-MCP Time Series Analysis Dashboard JavaScript
 */

// 전역 변수
let socket;
let dataChart;
let currentData = null;
let forecastingModels = [];
let anomalyModels = [];

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeChart();
    loadInitialData();
    updateModelCounts();
});

// Socket.IO 초기화
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('model_trained', function(data) {
        console.log('Model trained:', data);
        addRealtimeUpdate(`모델 훈련 완료: ${data.model_name} (${data.type})`);
        updateModelCounts();
        updateModelResults(data);
    });
    
    socket.on('prediction_completed', function(data) {
        console.log('Prediction completed:', data);
        addRealtimeUpdate(`예측 완료: ${data.model_name}`);
        updatePredictionResults(data);
    });
    
    socket.on('anomaly_detection_completed', function(data) {
        console.log('Anomaly detection completed:', data);
        addRealtimeUpdate(`이상치 탐지 완료: ${data.model_name}`);
        updateAnomalyResults(data);
    });
    
    socket.on('coordinated_analysis_completed', function(data) {
        console.log('Coordinated analysis completed:', data);
        addRealtimeUpdate(`통합 분석 완료: ${data.analysis_type}`);
        updateAnalysisHistory(data);
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
    const ctx = document.getElementById('dataChart').getContext('2d');
    dataChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '시계열 데이터',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// 초기 데이터 로드
async function loadInitialData() {
    try {
        const response = await fetch('/api/data/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                n_samples: 1000,
                n_features: 1,
                trend: true,
                seasonality: true,
                noise_level: 0.1
            })
        });
        
        const result = await response.json();
        currentData = result.data;
        updateChart(result.data);
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// 샘플 데이터 생성
async function generateSampleData() {
    showLoading('샘플 데이터 생성 중...');
    
    try {
        const sampleCount = parseInt(document.getElementById('sampleCount').value);
        const featureCount = parseInt(document.getElementById('featureCount').value);
        
        const response = await fetch('/api/data/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                n_samples: sampleCount,
                n_features: featureCount,
                trend: true,
                seasonality: true,
                noise_level: 0.1
            })
        });
        
        const result = await response.json();
        currentData = result.data;
        updateChart(result.data);
        addRealtimeUpdate(`샘플 데이터 생성 완료: ${result.shape[0]}개 샘플, ${result.shape[1]}개 특성`);
        
    } catch (error) {
        console.error('Error generating sample data:', error);
        alert('데이터 생성 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// 예측 모델 훈련
async function trainForecastingModel() {
    if (!currentData) {
        alert('먼저 데이터를 생성해주세요.');
        return;
    }
    
    const modelType = document.getElementById('forecastingModelType').value;
    const modelName = document.getElementById('forecastingModelName').value;
    
    if (!modelName) {
        alert('모델 이름을 입력해주세요.');
        return;
    }
    
    showLoading(`${modelType} 모델 훈련 중...`);
    
    try {
        const response = await fetch('/api/models/forecasting/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_type: modelType,
                data: JSON.stringify(currentData),
                model_name: modelName,
                sequence_length: 30,
                prediction_length: 1,
                epochs: 100
            })
        });
        
        const result = await response.json();
        console.log('Forecasting model training result:', result);
        
    } catch (error) {
        console.error('Error training forecasting model:', error);
        alert('모델 훈련 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// 이상치 탐지 모델 훈련
async function trainAnomalyModel() {
    if (!currentData) {
        alert('먼저 데이터를 생성해주세요.');
        return;
    }
    
    const modelType = document.getElementById('anomalyModelType').value;
    const modelName = document.getElementById('anomalyModelName').value;
    
    if (!modelName) {
        alert('모델 이름을 입력해주세요.');
        return;
    }
    
    showLoading(`${modelType} 모델 훈련 중...`);
    
    try {
        const response = await fetch('/api/models/anomaly/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_type: modelType,
                data: JSON.stringify(currentData),
                model_name: modelName,
                model_params: {}
            })
        });
        
        const result = await response.json();
        console.log('Anomaly model training result:', result);
        
    } catch (error) {
        console.error('Error training anomaly model:', error);
        alert('모델 훈련 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// 통합 분석 실행
async function runCoordinatedAnalysis() {
    if (!currentData) {
        alert('먼저 데이터를 생성해주세요.');
        return;
    }
    
    const analysisType = document.getElementById('analysisType').value;
    
    showLoading('통합 분석 실행 중...');
    
    try {
        const response = await fetch('/api/analysis/coordinated', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: JSON.stringify(currentData),
                analysis_type: analysisType,
                forecasting_model: 'lstm',
                anomaly_model: 'prophet'
            })
        });
        
        const result = await response.json();
        console.log('Coordinated analysis result:', result);
        
    } catch (error) {
        console.error('Error running coordinated analysis:', error);
        alert('통합 분석 중 오류가 발생했습니다.');
    } finally {
        hideLoading();
    }
}

// 차트 업데이트
function updateChart(data) {
    if (!data || data.length === 0) return;
    
    const labels = Array.from({length: data.length}, (_, i) => i);
    const values = data.map(d => Array.isArray(d) ? d[0] : d);
    
    dataChart.data.labels = labels;
    dataChart.data.datasets[0].data = values;
    dataChart.update();
}

// 모델 수 업데이트
async function updateModelCounts() {
    try {
        const [forecastingResponse, anomalyResponse, analysisResponse] = await Promise.all([
            fetch('/api/models/forecasting'),
            fetch('/api/models/anomaly'),
            fetch('/api/analysis/history')
        ]);
        
        const forecastingData = await forecastingResponse.json();
        const anomalyData = await anomalyResponse.json();
        const analysisData = await analysisResponse.json();
        
        document.getElementById('forecastingModelCount').textContent = forecastingData.models.length;
        document.getElementById('anomalyModelCount').textContent = anomalyData.models.length;
        document.getElementById('analysisCount').textContent = analysisData.total;
        
    } catch (error) {
        console.error('Error updating model counts:', error);
    }
}

// 모델 결과 업데이트
function updateModelResults(data) {
    const resultsDiv = document.getElementById('forecastingResults');
    
    if (data.type === 'forecasting') {
        const result = data.result;
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card card';
        modelCard.innerHTML = `
            <div class="card-body">
                <h6 class="card-title">${result.model_name}</h6>
                <p class="card-text">
                    <small class="text-muted">타입: ${result.model_type}</small><br>
                    <small class="text-success">RMSE: ${result.metrics.rmse.toFixed(4)}</small><br>
                    <small class="text-info">R²: ${result.metrics.r2.toFixed(4)}</small>
                </p>
            </div>
        `;
        resultsDiv.appendChild(modelCard);
    }
}

// 예측 결과 업데이트
function updatePredictionResults(data) {
    console.log('Updating prediction results:', data);
    // 예측 결과를 차트에 추가하는 로직
}

// 이상치 결과 업데이트
function updateAnomalyResults(data) {
    const resultsDiv = document.getElementById('anomalyResults');
    
    const result = data.result;
    const modelCard = document.createElement('div');
    modelCard.className = 'anomaly-card card';
    modelCard.innerHTML = `
        <div class="card-body">
            <h6 class="card-title">${result.model_name}</h6>
            <p class="card-text">
                <small class="text-muted">탐지된 이상치: ${result.anomaly_detection.anomaly_count}개</small><br>
                <small class="text-warning">이상치 비율: ${(result.anomaly_detection.anomaly_rate * 100).toFixed(2)}%</small>
            </p>
        </div>
    `;
    resultsDiv.appendChild(modelCard);
}

// 분석 히스토리 업데이트
function updateAnalysisHistory(data) {
    const historyDiv = document.getElementById('analysisHistory');
    
    const historyItem = document.createElement('div');
    historyItem.className = 'real-time-update';
    historyItem.innerHTML = `
        <div class="d-flex justify-content-between">
            <div>
                <strong>${data.analysis_type}</strong>
                <br>
                <small class="text-muted">${new Date(data.timestamp).toLocaleString()}</small>
            </div>
            <div class="text-end">
                <span class="badge bg-success">완료</span>
            </div>
        </div>
    `;
    
    historyDiv.insertBefore(historyItem, historyDiv.firstChild);
    
    // 최대 10개 항목만 유지
    const items = historyDiv.querySelectorAll('.real-time-update');
    if (items.length > 10) {
        items[items.length - 1].remove();
    }
}

// 실시간 업데이트 추가
function addRealtimeUpdate(message) {
    const updatesDiv = document.getElementById('realtimeUpdates');
    
    const updateItem = document.createElement('div');
    updateItem.className = 'real-time-update';
    updateItem.innerHTML = `
        <div class="d-flex justify-content-between">
            <div>
                <i class="fas fa-circle text-success me-2" style="font-size: 8px;"></i>
                ${message}
            </div>
            <div>
                <small class="text-muted">${new Date().toLocaleTimeString()}</small>
            </div>
        </div>
    `;
    
    updatesDiv.insertBefore(updateItem, updatesDiv.firstChild);
    
    // 최대 20개 항목만 유지
    const items = updatesDiv.querySelectorAll('.real-time-update');
    if (items.length > 20) {
        items[items.length - 1].remove();
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

// 주기적으로 모델 수 업데이트
setInterval(updateModelCounts, 5000);

// 주기적으로 분석 히스토리 업데이트
setInterval(async function() {
    try {
        const response = await fetch('/api/analysis/history?limit=5');
        const data = await response.json();
        
        const historyDiv = document.getElementById('analysisHistory');
        if (data.history.length === 0) {
            historyDiv.innerHTML = '<p class="text-muted">분석 기록이 없습니다.</p>';
        }
    } catch (error) {
        console.error('Error updating analysis history:', error);
    }
}, 10000);


