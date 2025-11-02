import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import WeatherStats from './WeatherStats';
import WeatherCharts from './WeatherCharts';
import WeatherPredictions from './WeatherPredictions';
import EnergyCorrelations from './EnergyCorrelations';
import WeatherMap from './WeatherMap';
import LoadingSpinner from './LoadingSpinner';
import ErrorBoundary from './ErrorBoundary';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
`;

const DashboardHeader = styled(motion.div)`
  text-align: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 3rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const FullWidthGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const RefreshButton = styled(motion.button)`
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(74, 222, 128, 0.3);
  z-index: 1000;

  &:hover {
    transform: scale(1.1);
  }
`;

const WeatherDashboard = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 모의 날씨 데이터 생성 함수
  const generateMockWeatherData = () => {
    const now = new Date();
    const hour = now.getHours();
    
    const baseTemp = 20 + Math.sin((hour - 6) * Math.PI / 12) * 8;
    const baseHumidity = 70 - Math.sin((hour - 6) * Math.PI / 12) * 20;
    const baseWind = 2 + Math.random() * 3;
    const baseSolar = Math.max(0, Math.sin((hour - 6) * Math.PI / 12) * 1000);
    
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

  // 데이터 로드 함수
  const loadWeatherData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // API 호출 시도
      const response = await fetch('http://localhost:3000/api/weather/current');
      if (response.ok) {
        const data = await response.json();
        setWeatherData(data);
      } else {
        throw new Error('API call failed');
      }
    } catch (err) {
      console.warn('API call failed, using mock data:', err.message);
      // API 실패 시 모의 데이터 사용
      setWeatherData(generateMockWeatherData());
    } finally {
      setIsLoading(false);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    loadWeatherData();
  }, []);

  // 자동 새로고침
  useEffect(() => {
    const interval = setInterval(() => {
      loadWeatherData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshKey(prev => prev + 1);
    await loadWeatherData();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  if (isLoading && !weatherData) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <ErrorBoundary>
        <div style={{ textAlign: 'center', color: 'white', padding: '2rem' }}>
          <h2>데이터를 불러오는 중 오류가 발생했습니다.</h2>
          <p>잠시 후 다시 시도해주세요.</p>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <DashboardContainer>
      <DashboardHeader
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Title>🌤️ Weather Analysis Dashboard</Title>
        <Subtitle>Real-time Weather Monitoring & Advanced Analytics</Subtitle>
      </DashboardHeader>

      <AnimatePresence mode="wait">
        <motion.div
          key={refreshKey}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <GridContainer>
            <WeatherStats data={weatherData} />
          </GridContainer>

          <FullWidthGrid>
            <WeatherCharts data={weatherData} />
            <WeatherPredictions data={weatherData} />
          </FullWidthGrid>

          <GridContainer>
            <EnergyCorrelations data={weatherData} />
            <WeatherMap data={weatherData} />
          </GridContainer>
        </motion.div>
      </AnimatePresence>

      <RefreshButton
        onClick={handleRefresh}
        disabled={isRefreshing}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{ rotate: isRefreshing ? 360 : 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          animate={{ rotate: isRefreshing ? 360 : 0 }}
          transition={{ duration: 1, repeat: isRefreshing ? Infinity : 0 }}
        >
          🔄
        </motion.div>
      </RefreshButton>
    </DashboardContainer>
  );
};

export default WeatherDashboard;
