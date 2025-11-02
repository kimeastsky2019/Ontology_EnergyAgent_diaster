import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Thermometer, 
  Droplets, 
  Wind, 
  Sun, 
  Eye,
  Gauge,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: ${props => props.gradient};
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const StatIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
`;

const StatTrend = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: ${props => props.trend === 'up' ? '#4ade80' : '#ef4444'};
`;

const StatValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  line-height: 1;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
`;

const StatDescription = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const StatProgress = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 1rem;
  overflow: hidden;
`;

const ProgressBar = styled(motion.div)`
  height: 100%;
  background: ${props => props.color};
  border-radius: 2px;
`;

const ChartsSection = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const ChartTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ChartArea = styled.div`
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.1rem;
`;

const PredictionsCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const PredictionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const PredictionItem = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const PredictionTime = styled.div`
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
`;

const PredictionValue = styled.div`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
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

const SimpleWeatherDashboard = () => {
  const [weatherData, setWeatherData] = useState({
    temperature: 24.5,
    humidity: 65,
    windSpeed: 2.3,
    irradiance: 850,
    pressure: 1013.2,
    visibility: 12.5
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const generateWeatherData = () => {
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
      visibility: 12.5 + (Math.random() - 0.5) * 5
    };
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setWeatherData(generateWeatherData());
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  // 자동 업데이트
  useEffect(() => {
    const interval = setInterval(() => {
      setWeatherData(generateWeatherData());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const stats = [
    {
      icon: Thermometer,
      label: 'Temperature',
      value: `${weatherData.temperature.toFixed(1)}°C`,
      description: 'Current temperature',
      trend: 'up',
      trendValue: '+0.3°C',
      progress: (weatherData.temperature / 40) * 100,
      gradient: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
      bgColor: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
      color: '#ff6b6b'
    },
    {
      icon: Droplets,
      label: 'Humidity',
      value: `${weatherData.humidity.toFixed(0)}%`,
      description: 'Relative humidity',
      trend: 'down',
      trendValue: '-2%',
      progress: weatherData.humidity,
      gradient: 'linear-gradient(135deg, #00b894, #00a085)',
      bgColor: 'linear-gradient(135deg, #00b894, #00a085)',
      color: '#00b894'
    },
    {
      icon: Wind,
      label: 'Wind Speed',
      value: `${weatherData.windSpeed.toFixed(1)} m/s`,
      description: 'Wind velocity',
      trend: 'up',
      trendValue: '+0.2 m/s',
      progress: (weatherData.windSpeed / 10) * 100,
      gradient: 'linear-gradient(135deg, #fdcb6e, #e17055)',
      bgColor: 'linear-gradient(135deg, #fdcb6e, #e17055)',
      color: '#fdcb6e'
    },
    {
      icon: Sun,
      label: 'Solar Radiation',
      value: `${weatherData.irradiance.toFixed(0)} W/m²`,
      description: 'Solar irradiance',
      trend: 'up',
      trendValue: '+45 W/m²',
      progress: (weatherData.irradiance / 1200) * 100,
      gradient: 'linear-gradient(135deg, #74b9ff, #0984e3)',
      bgColor: 'linear-gradient(135deg, #74b9ff, #0984e3)',
      color: '#74b9ff'
    },
    {
      icon: Eye,
      label: 'Visibility',
      value: `${weatherData.visibility.toFixed(1)} km`,
      description: 'Atmospheric visibility',
      trend: 'up',
      trendValue: '+0.8 km',
      progress: (weatherData.visibility / 20) * 100,
      gradient: 'linear-gradient(135deg, #a29bfe, #6c5ce7)',
      bgColor: 'linear-gradient(135deg, #a29bfe, #6c5ce7)',
      color: '#a29bfe'
    },
    {
      icon: Gauge,
      label: 'Pressure',
      value: `${weatherData.pressure.toFixed(1)} hPa`,
      description: 'Atmospheric pressure',
      trend: 'down',
      trendValue: '-1.2 hPa',
      progress: ((weatherData.pressure - 980) / (1040 - 980)) * 100,
      gradient: 'linear-gradient(135deg, #fd79a8, #e84393)',
      bgColor: 'linear-gradient(135deg, #fd79a8, #e84393)',
      color: '#fd79a8'
    }
  ];

  const predictions = [
    { time: '+1 Hour', temp: (weatherData.temperature + 0.7).toFixed(1) + '°C', humidity: (weatherData.humidity + 3).toFixed(0) + '%' },
    { time: '+2 Hours', temp: (weatherData.temperature + 1.2).toFixed(1) + '°C', humidity: (weatherData.humidity + 5).toFixed(0) + '%' },
    { time: '+3 Hours', temp: (weatherData.temperature + 0.8).toFixed(1) + '°C', humidity: (weatherData.humidity + 2).toFixed(0) + '%' },
    { time: '+4 Hours', temp: (weatherData.temperature + 1.5).toFixed(1) + '°C', humidity: (weatherData.humidity + 4).toFixed(0) + '%' }
  ];

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

      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            gradient={stat.gradient}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <StatHeader>
              <StatIcon bgColor={stat.bgColor}>
                <stat.icon size={24} />
              </StatIcon>
              <StatTrend trend={stat.trend}>
                {stat.trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {stat.trendValue}
              </StatTrend>
            </StatHeader>
            
            <StatValue>{stat.value}</StatValue>
            <StatLabel>{stat.label}</StatLabel>
            <StatDescription>
              <Eye size={12} />
              {stat.description}
            </StatDescription>
            
            <StatProgress>
              <ProgressBar
                color={stat.color}
                initial={{ width: 0 }}
                animate={{ width: `${stat.progress}%` }}
                transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
              />
            </StatProgress>
          </StatCard>
        ))}
      </StatsGrid>

      <ChartsSection>
        <ChartCard
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <ChartTitle>
            📊 Weather Analytics
          </ChartTitle>
          <ChartArea>
            Interactive charts will be displayed here
          </ChartArea>
        </ChartCard>

        <PredictionsCard
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <ChartTitle>
            🔮 Weather Forecast
          </ChartTitle>
          <PredictionsList>
            {predictions.map((prediction, index) => (
              <PredictionItem
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
              >
                <PredictionTime>{prediction.time}</PredictionTime>
                <PredictionValue>
                  {prediction.temp} | {prediction.humidity}
                </PredictionValue>
              </PredictionItem>
            ))}
          </PredictionsList>
        </PredictionsCard>
      </ChartsSection>

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

export default SimpleWeatherDashboard;







