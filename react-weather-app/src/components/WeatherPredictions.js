import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Clock, 
  Thermometer, 
  Droplets, 
  Wind, 
  Sun, 
  Cloud,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from 'lucide-react';

const PredictionsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  height: fit-content;
`;

const PredictionsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const PredictionsTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const TimeRangeSelector = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const TimeButton = styled.button`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'rgba(255, 255, 255, 0.6)'};
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.8rem;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const PredictionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const PredictionCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: ${props => props.gradient};
  }
`;

const PredictionHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const PredictionTime = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
`;

const PredictionIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const PredictionValues = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
`;

const PredictionValue = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
`;

const ValueNumber = styled.span`
  color: white;
  font-weight: 600;
`;

const TrendIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: ${props => props.trend === 'up' ? '#4ade80' : '#ef4444'};
`;

const AlertCard = styled(motion.div)`
  background: linear-gradient(135deg, #fef3c7, #f59e0b);
  border-radius: 12px;
  padding: 1rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #92400e;
`;

const WeatherPredictions = ({ data }) => {
  const [timeRange, setTimeRange] = useState('24h');
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    generatePredictions();
  }, [data, timeRange]);

  const generatePredictions = () => {
    const baseTemp = data?.temperature || 24.5;
    const baseHumidity = data?.humidity || 65;
    const baseWind = data?.windSpeed || 2.3;
    const baseSolar = data?.irradiance || 850;

    const hours = timeRange === '24h' ? 24 : timeRange === '48h' ? 48 : 72;
    const newPredictions = [];

    for (let i = 1; i <= Math.min(hours, 12); i++) {
      const hour = new Date().getHours() + i;
      const timeOfDay = hour % 24;
      
      // 시간대별 패턴 적용
      const tempVariation = Math.sin((timeOfDay - 6) * Math.PI / 12) * 8;
      const humidityVariation = -Math.sin((timeOfDay - 6) * Math.PI / 12) * 20;
      const solarVariation = Math.max(0, Math.sin((timeOfDay - 6) * Math.PI / 12) * 1000);
      
      const prediction = {
        time: `${i}h`,
        timeOfDay,
        temperature: baseTemp + tempVariation + (Math.random() - 0.5) * 2,
        humidity: Math.max(30, Math.min(90, baseHumidity + humidityVariation + (Math.random() - 0.5) * 5)),
        windSpeed: Math.max(0, baseWind + (Math.random() - 0.5) * 3),
        solarRadiation: Math.max(0, solarVariation + (Math.random() - 0.5) * 200),
        precipitation: Math.random() * 30,
        icon: getWeatherIcon(timeOfDay, Math.random() * 30),
        gradient: getGradient(timeOfDay)
      };
      
      newPredictions.push(prediction);
    }
    
    setPredictions(newPredictions);
  };

  const getWeatherIcon = (timeOfDay, precipitation) => {
    if (precipitation > 20) return 'rain';
    if (timeOfDay >= 6 && timeOfDay < 18) return 'sun';
    if (timeOfDay >= 18 && timeOfDay < 22) return 'cloud';
    return 'moon';
  };

  const getGradient = (timeOfDay) => {
    if (timeOfDay >= 6 && timeOfDay < 12) return 'linear-gradient(135deg, #fbbf24, #f59e0b)';
    if (timeOfDay >= 12 && timeOfDay < 18) return 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
    if (timeOfDay >= 18 && timeOfDay < 22) return 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
    return 'linear-gradient(135deg, #1f2937, #111827)';
  };

  const getIconComponent = (icon) => {
    switch (icon) {
      case 'sun':
        return <Sun size={20} />;
      case 'cloud':
        return <Cloud size={20} />;
      case 'rain':
        return <Droplets size={20} />;
      case 'moon':
        return <Cloud size={20} />;
      default:
        return <Sun size={20} />;
    }
  };

  const getIconBgColor = (icon) => {
    switch (icon) {
      case 'sun':
        return 'linear-gradient(135deg, #fbbf24, #f59e0b)';
      case 'cloud':
        return 'linear-gradient(135deg, #6b7280, #4b5563)';
      case 'rain':
        return 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
      case 'moon':
        return 'linear-gradient(135deg, #1f2937, #111827)';
      default:
        return 'linear-gradient(135deg, #fbbf24, #f59e0b)';
    }
  };

  const hasAlerts = predictions.some(p => p.precipitation > 25 || p.windSpeed > 5);

  return (
    <PredictionsContainer>
      <PredictionsHeader>
        <PredictionsTitle>
          <Clock size={24} />
          Weather Forecast
        </PredictionsTitle>
        <TimeRangeSelector>
          <TimeButton 
            active={timeRange === '24h'} 
            onClick={() => setTimeRange('24h')}
          >
            24h
          </TimeButton>
          <TimeButton 
            active={timeRange === '48h'} 
            onClick={() => setTimeRange('48h')}
          >
            48h
          </TimeButton>
          <TimeButton 
            active={timeRange === '72h'} 
            onClick={() => setTimeRange('72h')}
          >
            72h
          </TimeButton>
        </TimeRangeSelector>
      </PredictionsHeader>

      <PredictionsList>
        <AnimatePresence>
          {predictions.map((prediction, index) => (
            <PredictionCard
              key={`${timeRange}-${index}`}
              gradient={prediction.gradient}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <PredictionHeader>
                <PredictionTime>
                  <Clock size={16} />
                  +{prediction.time}
                </PredictionTime>
                <PredictionIcon bgColor={getIconBgColor(prediction.icon)}>
                  {getIconComponent(prediction.icon)}
                </PredictionIcon>
              </PredictionHeader>

              <PredictionValues>
                <PredictionValue>
                  <Thermometer size={16} />
                  <span>Temperature:</span>
                  <ValueNumber>{prediction.temperature.toFixed(1)}°C</ValueNumber>
                  <TrendIndicator trend={prediction.temperature > (data?.temperature || 24.5) ? 'up' : 'down'}>
                    {prediction.temperature > (data?.temperature || 24.5) ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  </TrendIndicator>
                </PredictionValue>

                <PredictionValue>
                  <Droplets size={16} />
                  <span>Humidity:</span>
                  <ValueNumber>{prediction.humidity.toFixed(0)}%</ValueNumber>
                  <TrendIndicator trend={prediction.humidity > (data?.humidity || 65) ? 'up' : 'down'}>
                    {prediction.humidity > (data?.humidity || 65) ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  </TrendIndicator>
                </PredictionValue>

                <PredictionValue>
                  <Wind size={16} />
                  <span>Wind:</span>
                  <ValueNumber>{prediction.windSpeed.toFixed(1)} m/s</ValueNumber>
                  <TrendIndicator trend={prediction.windSpeed > (data?.windSpeed || 2.3) ? 'up' : 'down'}>
                    {prediction.windSpeed > (data?.windSpeed || 2.3) ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  </TrendIndicator>
                </PredictionValue>

                <PredictionValue>
                  <Sun size={16} />
                  <span>Solar:</span>
                  <ValueNumber>{prediction.solarRadiation.toFixed(0)} W/m²</ValueNumber>
                  <TrendIndicator trend={prediction.solarRadiation > (data?.irradiance || 850) ? 'up' : 'down'}>
                    {prediction.solarRadiation > (data?.irradiance || 850) ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  </TrendIndicator>
                </PredictionValue>
              </PredictionValues>
            </PredictionCard>
          ))}
        </AnimatePresence>
      </PredictionsList>

      {hasAlerts && (
        <AlertCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <AlertTriangle size={20} />
          <div>
            <strong>Weather Alert:</strong> High precipitation or wind speed expected in the next 24 hours.
          </div>
        </AlertCard>
      )}
    </PredictionsContainer>
  );
};

export default WeatherPredictions;







