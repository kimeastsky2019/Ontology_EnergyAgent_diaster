import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const AI_API_BASE_URL = process.env.REACT_APP_AI_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const aiApi = axios.create({
  baseURL: AI_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // 필요시 인증 토큰 추가
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // 서버가 응답을 반환했지만 상태 코드가 2xx 범위를 벗어남
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // 요청이 이루어졌지만 응답을 받지 못함
      console.error('No response received:', error.request);
    } else {
      // 요청 설정 중에 오류가 발생
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// AI API interceptors
aiApi.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

aiApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('AI API Error:', error);
    return Promise.reject(error);
  }
);

// API 엔드포인트
export const energyAPI = {
  // 실시간 데이터
  getRealtime: (range = 'hour') => api.get(`/api/energy/realtime?range=${range}`),
  
  // 과거 데이터
  getHistory: (startDate, endDate) => 
    api.get(`/api/energy/history?start=${startDate}&end=${endDate}`),
  
  // 일일 데이터
  getDaily: (date) => api.get(`/api/energy/daily?date=${date}`),
  
  // 예측 데이터
  getForecast: (days = 7) => api.get(`/api/energy/forecast?days=${days}`),
};

export const facilityAPI = {
  // 모든 시설 목록
  getAll: () => api.get('/api/facilities'),
  
  // 현재 시설 정보
  getCurrent: () => api.get('/api/facilities/current'),
  
  // 특정 시설 정보
  getById: (id) => api.get(`/api/facilities/${id}`),
};

export const weatherAPI = {
  // 현재 날씨
  getCurrent: () => api.get('/api/weather/current'),
  
  // 예보
  getForecast: (days = 7) => api.get(`/api/weather/forecast?days=${days}`),
};

export const aiAgentAPI = {
  // 이상징후 목록
  getAnomalies: () => aiApi.get('/api/ai/anomalies'),
  
  // 고장 진단
  getDiagnostics: () => aiApi.get('/api/ai/diagnostics'),
  
  // 즉시 분석 실행
  runAnalysis: () => aiApi.post('/api/ai/analyze'),
  
  // AI 상태
  getStatus: () => aiApi.get('/api/ai/status'),
};

export default api;
