import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Sun, Moon, Cloud, CloudRain, Wind, Thermometer } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Title = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const Logo = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Subtitle = styled.p`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin: 0;
`;

const StatusBar = styled.div`
  display: flex;
  align-items: center;
  gap: 2rem;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-size: 0.9rem;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.status === 'online' ? '#4ade80' : '#ef4444'};
  animation: ${props => props.status === 'online' ? 'pulse 2s infinite' : 'none'};
`;

const TimeDisplay = styled.div`
  color: white;
  font-weight: 500;
  font-size: 1.1rem;
`;

const WeatherIcon = styled(motion.div)`
  font-size: 1.5rem;
  color: white;
`;

const Header = () => {
  const { t, i18n } = useTranslation();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [weatherIcon, setWeatherIcon] = useState('sun');

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const hour = currentTime.getHours();
    if (hour >= 6 && hour < 12) {
      setWeatherIcon('sun');
    } else if (hour >= 12 && hour < 18) {
      setWeatherIcon('cloud');
    } else if (hour >= 18 && hour < 22) {
      setWeatherIcon('cloud-rain');
    } else {
      setWeatherIcon('moon');
    }
  }, [currentTime]);

  const getWeatherIcon = () => {
    switch (weatherIcon) {
      case 'sun':
        return <Sun />;
      case 'cloud':
        return <Cloud />;
      case 'cloud-rain':
        return <CloudRain />;
      case 'moon':
        return <Moon />;
      default:
        return <Sun />;
    }
  };

  return (
    <HeaderContainer>
      <Title>
        <Logo>
          {getWeatherIcon()}
          {t('title')}
        </Logo>
        <Subtitle>{t('subtitle')}</Subtitle>
      </Title>
      
      <StatusBar>
        <StatusItem>
          <StatusIndicator status="online" />
          <span>{t('liveData', 'Live Data')}</span>
        </StatusItem>
        
        <StatusItem>
          <Thermometer size={16} />
          <span>24.5°C</span>
        </StatusItem>
        
        <StatusItem>
          <Wind size={16} />
          <span>2.3 m/s</span>
        </StatusItem>
        
        <TimeDisplay>
          {currentTime.toLocaleTimeString(i18n.language, {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })}
        </TimeDisplay>
      </StatusBar>
    </HeaderContainer>
  );
};

export default Header;

