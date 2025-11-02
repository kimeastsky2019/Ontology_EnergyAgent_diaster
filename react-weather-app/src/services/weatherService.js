import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Mock weather data generator
const generateMockWeatherData = () => {
  const now = new Date();
  const hour = now.getHours();
  
  // 시간대별 기본값 계산
  const baseTemp = 20 + Math.sin((hour - 6) * Math.PI / 12) * 8;
  const baseHumidity = 70 - Math.sin((hour - 6) * Math.PI / 12) * 20;
  const baseWind = 2 + Math.random() * 3;
  const baseSolar = Math.max(0, Math.sin((hour - 6) * Math.PI / 12) * 1000);
  
  // 랜덤 변동 추가
  return {
    temperature: baseTemp + (Math.random() - 0.5) * 4,
    humidity: Math.max(30, Math.min(90, baseHumidity + (Math.random() - 0.5) * 10)),
    windSpeed: Math.max(0, baseWind + (Math.random() - 0.5) * 2),
    irradiance: Math.max(0, baseSolar + (Math.random() - 0.5) * 200),
    pressure: 1013.2 + (Math.random() - 0.5) * 20,
    visibility: 12.5 + (Math.random() - 0.5) * 5,
    uvIndex: Math.max(0, Math.min(11, 5 + Math.sin((hour - 6) * Math.PI / 12) * 3 + (Math.random() - 0.5) * 2)),
    timestamp: now.toISOString(),
    location: {
      name: 'Seoul',
      latitude: 37.5665,
      longitude: 126.9780,
      country: 'South Korea'
    },
    conditions: {
      main: hour >= 6 && hour < 18 ? 'Clear' : 'Partly Cloudy',
      description: hour >= 6 && hour < 18 ? 'Clear sky' : 'Partly cloudy',
      icon: hour >= 6 && hour < 18 ? '01d' : '02n'
    }
  };
};

// API 클라이언트 설정
const weatherAPI = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
weatherAPI.interceptors.request.use(
  (config) => {
    console.log(`Making request to: ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
weatherAPI.interceptors.response.use(
  (response) => {
    console.log(`Response from: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

// 날씨 데이터 가져오기
export const fetchWeatherData = async () => {
  try {
    // 실제 API 호출 시도
    const response = await weatherAPI.get('/api/weather/current');
    return response.data;
  } catch (error) {
    console.warn('API call failed, using mock data:', error.message);
    // API 실패 시 모의 데이터 반환
    return generateMockWeatherData();
  }
};

// 예보 데이터 가져오기
export const fetchForecastData = async (days = 5) => {
  try {
    const response = await weatherAPI.get(`/api/weather/forecast?days=${days}`);
    return response.data;
  } catch (error) {
    console.warn('Forecast API call failed, using mock data:', error.message);
    // 모의 예보 데이터 생성
    return generateMockForecastData(days);
  }
};

// 모의 예보 데이터 생성
const generateMockForecastData = (days) => {
  const forecasts = [];
  const now = new Date();
  
  for (let i = 0; i < days; i++) {
    const date = new Date(now.getTime() + i * 24 * 60 * 60 * 1000);
    const dayOfYear = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
    
    // 계절별 패턴 적용
    const seasonalTemp = 15 + Math.sin((dayOfYear - 80) * 2 * Math.PI / 365) * 15;
    const seasonalHumidity = 60 + Math.sin((dayOfYear - 80) * 2 * Math.PI / 365) * 20;
    
    forecasts.push({
      date: date.toISOString().split('T')[0],
      temperature: {
        min: seasonalTemp - 5 + (Math.random() - 0.5) * 4,
        max: seasonalTemp + 5 + (Math.random() - 0.5) * 4,
        avg: seasonalTemp + (Math.random() - 0.5) * 2
      },
      humidity: Math.max(30, Math.min(90, seasonalHumidity + (Math.random() - 0.5) * 10)),
      windSpeed: 2 + Math.random() * 4,
      pressure: 1013 + (Math.random() - 0.5) * 20,
      conditions: {
        main: ['Clear', 'Clouds', 'Rain', 'Snow'][Math.floor(Math.random() * 4)],
        description: ['Clear sky', 'Few clouds', 'Scattered clouds', 'Light rain'][Math.floor(Math.random() * 4)],
        icon: ['01d', '02d', '03d', '10d'][Math.floor(Math.random() * 4)]
      },
      precipitation: {
        probability: Math.random() * 100,
        amount: Math.random() * 10
      }
    });
  }
  
  return { forecasts };
};

// 에너지 상관관계 데이터 가져오기
export const fetchEnergyCorrelations = async () => {
  try {
    const response = await weatherAPI.get('/api/energy/correlations');
    return response.data;
  } catch (error) {
    console.warn('Energy correlations API call failed, using mock data:', error.message);
    return {
      correlations: [
        {
          type: 'temperature_energy',
          value: 0.78,
          description: 'Temperature vs Energy Consumption',
          trend: 'positive'
        },
        {
          type: 'solar_generation',
          value: 0.92,
          description: 'Solar Radiation vs Generation',
          trend: 'positive'
        },
        {
          type: 'humidity_efficiency',
          value: -0.45,
          description: 'Humidity vs Efficiency',
          trend: 'negative'
        },
        {
          type: 'wind_turbine',
          value: 0.65,
          description: 'Wind Speed vs Turbine Output',
          trend: 'positive'
        }
      ]
    };
  }
};

// 실시간 데이터 스트림 (WebSocket 대신 폴링)
export const subscribeToWeatherUpdates = (callback, interval = 5000) => {
  const fetchData = async () => {
    try {
      const data = await fetchWeatherData();
      callback(data);
    } catch (error) {
      console.error('Error fetching weather updates:', error);
    }
  };

  // 즉시 한 번 실행
  fetchData();
  
  // 주기적으로 실행
  const intervalId = setInterval(fetchData, interval);
  
  // 구독 해제 함수 반환
  return () => clearInterval(intervalId);
};

// 에러 처리 유틸리티
export const handleWeatherError = (error) => {
  if (error.response) {
    // 서버 응답이 있는 경우
    const status = error.response.status;
    const message = error.response.data?.message || 'Unknown server error';
    
    switch (status) {
      case 400:
        return '잘못된 요청입니다. 입력값을 확인해주세요.';
      case 401:
        return '인증이 필요합니다. API 키를 확인해주세요.';
      case 403:
        return '접근이 거부되었습니다.';
      case 404:
        return '요청한 데이터를 찾을 수 없습니다.';
      case 429:
        return '요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.';
      case 500:
        return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      default:
        return `서버 오류 (${status}): ${message}`;
    }
  } else if (error.request) {
    // 네트워크 오류
    return '네트워크 연결을 확인해주세요.';
  } else {
    // 기타 오류
    return `오류가 발생했습니다: ${error.message}`;
  }
};

export default {
  fetchWeatherData,
  fetchForecastData,
  fetchEnergyCorrelations,
  subscribeToWeatherUpdates,
  handleWeatherError
};







