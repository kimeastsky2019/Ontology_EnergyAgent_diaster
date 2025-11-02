import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Thermometer, 
  Droplets, 
  Wind, 
  Sun, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Gauge
} from 'lucide-react';

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  width: 100%;
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

const WeatherStats = ({ data }) => {
  const stats = [
    {
      icon: Thermometer,
      label: 'Temperature',
      value: `${data?.temperature?.toFixed(1) || '24.5'}°C`,
      description: 'Current temperature',
      trend: 'up',
      trendValue: '+0.3°C',
      progress: (data?.temperature || 24.5) / 40 * 100,
      gradient: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
      bgColor: 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
      color: '#ff6b6b'
    },
    {
      icon: Droplets,
      label: 'Humidity',
      value: `${data?.humidity?.toFixed(0) || '65'}%`,
      description: 'Relative humidity',
      trend: 'down',
      trendValue: '-2%',
      progress: data?.humidity || 65,
      gradient: 'linear-gradient(135deg, #00b894, #00a085)',
      bgColor: 'linear-gradient(135deg, #00b894, #00a085)',
      color: '#00b894'
    },
    {
      icon: Wind,
      label: 'Wind Speed',
      value: `${data?.windSpeed?.toFixed(1) || '2.3'} m/s`,
      description: 'Wind velocity',
      trend: 'up',
      trendValue: '+0.2 m/s',
      progress: ((data?.windSpeed || 2.3) / 10) * 100,
      gradient: 'linear-gradient(135deg, #fdcb6e, #e17055)',
      bgColor: 'linear-gradient(135deg, #fdcb6e, #e17055)',
      color: '#fdcb6e'
    },
    {
      icon: Sun,
      label: 'Solar Radiation',
      value: `${data?.irradiance?.toFixed(0) || '850'} W/m²`,
      description: 'Solar irradiance',
      trend: 'up',
      trendValue: '+45 W/m²',
      progress: ((data?.irradiance || 850) / 1200) * 100,
      gradient: 'linear-gradient(135deg, #74b9ff, #0984e3)',
      bgColor: 'linear-gradient(135deg, #74b9ff, #0984e3)',
      color: '#74b9ff'
    },
    {
      icon: Eye,
      label: 'Visibility',
      value: `${data?.visibility?.toFixed(1) || '12.5'} km`,
      description: 'Atmospheric visibility',
      trend: 'up',
      trendValue: '+0.8 km',
      progress: ((data?.visibility || 12.5) / 20) * 100,
      gradient: 'linear-gradient(135deg, #a29bfe, #6c5ce7)',
      bgColor: 'linear-gradient(135deg, #a29bfe, #6c5ce7)',
      color: '#a29bfe'
    },
    {
      icon: Gauge,
      label: 'Pressure',
      value: `${data?.pressure?.toFixed(1) || '1013.2'} hPa`,
      description: 'Atmospheric pressure',
      trend: 'down',
      trendValue: '-1.2 hPa',
      progress: ((data?.pressure || 1013.2) - 980) / (1040 - 980) * 100,
      gradient: 'linear-gradient(135deg, #fd79a8, #e84393)',
      bgColor: 'linear-gradient(135deg, #fd79a8, #e84393)',
      color: '#fd79a8'
    }
  ];

  return (
    <StatsContainer>
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
    </StatsContainer>
  );
};

export default WeatherStats;







