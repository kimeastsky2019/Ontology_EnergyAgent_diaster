import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Thermometer, 
  Droplets, 
  Wind, 
  Eye,
  Navigation,
  Layers,
  RefreshCw
} from 'lucide-react';

const MapContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  height: 500px;
  position: relative;
  overflow: hidden;
`;

const MapHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const MapTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const MapControls = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ControlButton = styled.button`
  padding: 0.5rem;
  border: none;
  border-radius: 8px;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'rgba(255, 255, 255, 0.6)'};
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const MapArea = styled.div`
  position: relative;
  width: 100%;
  height: 350px;
  background: linear-gradient(135deg, #1e3a8a, #1e40af);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const WeatherStation = styled(motion.div)`
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: ${props => props.bgColor};
  border: 3px solid white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10;

  &:hover {
    transform: scale(1.1);
    z-index: 20;
  }
`;

const StationIcon = styled.div`
  color: white;
  font-size: 1.2rem;
`;

const StationTooltip = styled(motion.div)`
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 30;
  pointer-events: none;

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: rgba(0, 0, 0, 0.9);
  }
`;

const MapOverlay = styled.div`
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 5;
`;

const MapLegend = styled.div`
  background: rgba(0, 0, 0, 0.7);
  padding: 1rem;
  border-radius: 8px;
  color: white;
  font-size: 0.8rem;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;

  &:last-child {
    margin-bottom: 0;
  }
`;

const LegendColor = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.color};
`;

const MapInfo = styled.div`
  background: rgba(0, 0, 0, 0.7);
  padding: 1rem;
  border-radius: 8px;
  color: white;
  font-size: 0.8rem;
  text-align: right;
`;

const WeatherMap = ({ data }) => {
  const [mapType, setMapType] = useState('temperature');
  const [selectedStation, setSelectedStation] = useState(null);
  const [stations, setStations] = useState([]);

  useEffect(() => {
    generateWeatherStations();
  }, [mapType]);

  const generateWeatherStations = () => {
    const newStations = [
      {
        id: 1,
        name: 'Seoul Central',
        x: 20,
        y: 30,
        temperature: 24.5,
        humidity: 65,
        windSpeed: 2.3,
        pressure: 1013.2,
        visibility: 12.5,
        icon: 'thermometer',
        bgColor: getStationColor(24.5, mapType)
      },
      {
        id: 2,
        name: 'Busan Port',
        x: 70,
        y: 80,
        temperature: 26.2,
        humidity: 72,
        windSpeed: 3.1,
        pressure: 1011.8,
        visibility: 15.2,
        icon: 'droplets',
        bgColor: getStationColor(26.2, mapType)
      },
      {
        id: 3,
        name: 'Jeju Island',
        x: 15,
        y: 85,
        temperature: 28.1,
        humidity: 68,
        windSpeed: 4.2,
        pressure: 1009.5,
        visibility: 18.7,
        icon: 'wind',
        bgColor: getStationColor(28.1, mapType)
      },
      {
        id: 4,
        name: 'Gangwon Mountains',
        x: 60,
        y: 20,
        temperature: 18.3,
        humidity: 78,
        windSpeed: 1.8,
        pressure: 1015.6,
        visibility: 8.9,
        icon: 'eye',
        bgColor: getStationColor(18.3, mapType)
      },
      {
        id: 5,
        name: 'Gwangju Plains',
        x: 40,
        y: 60,
        temperature: 25.7,
        humidity: 61,
        windSpeed: 2.7,
        pressure: 1012.3,
        visibility: 14.1,
        icon: 'thermometer',
        bgColor: getStationColor(25.7, mapType)
      }
    ];

    setStations(newStations);
  };

  const getStationColor = (value, type) => {
    switch (type) {
      case 'temperature':
        if (value < 15) return 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        if (value < 25) return 'linear-gradient(135deg, #10b981, #059669)';
        if (value < 30) return 'linear-gradient(135deg, #f59e0b, #d97706)';
        return 'linear-gradient(135deg, #ef4444, #dc2626)';
      case 'humidity':
        if (value < 40) return 'linear-gradient(135deg, #f59e0b, #d97706)';
        if (value < 60) return 'linear-gradient(135deg, #10b981, #059669)';
        if (value < 80) return 'linear-gradient(135deg, #3b82f6, #1d4ed8)';
        return 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
      case 'wind':
        if (value < 2) return 'linear-gradient(135deg, #10b981, #059669)';
        if (value < 4) return 'linear-gradient(135deg, #f59e0b, #d97706)';
        if (value < 6) return 'linear-gradient(135deg, #ef4444, #dc2626)';
        return 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
      default:
        return 'linear-gradient(135deg, #6b7280, #4b5563)';
    }
  };

  const getStationIcon = (icon) => {
    switch (icon) {
      case 'thermometer':
        return <Thermometer size={20} />;
      case 'droplets':
        return <Droplets size={20} />;
      case 'wind':
        return <Wind size={20} />;
      case 'eye':
        return <Eye size={20} />;
      default:
        return <MapPin size={20} />;
    }
  };

  const getMapTypeLabel = () => {
    switch (mapType) {
      case 'temperature':
        return 'Temperature Map';
      case 'humidity':
        return 'Humidity Map';
      case 'wind':
        return 'Wind Speed Map';
      default:
        return 'Weather Map';
    }
  };

  return (
    <MapContainer>
      <MapHeader>
        <MapTitle>
          <Navigation size={24} />
          {getMapTypeLabel()}
        </MapTitle>
        <MapControls>
          <ControlButton 
            active={mapType === 'temperature'} 
            onClick={() => setMapType('temperature')}
            title="Temperature"
          >
            <Thermometer size={16} />
          </ControlButton>
          <ControlButton 
            active={mapType === 'humidity'} 
            onClick={() => setMapType('humidity')}
            title="Humidity"
          >
            <Droplets size={16} />
          </ControlButton>
          <ControlButton 
            active={mapType === 'wind'} 
            onClick={() => setMapType('wind')}
            title="Wind Speed"
          >
            <Wind size={16} />
          </ControlButton>
          <ControlButton 
            onClick={() => generateWeatherStations()}
            title="Refresh"
          >
            <RefreshCw size={16} />
          </ControlButton>
        </MapControls>
      </MapHeader>

      <MapArea>
        <MapOverlay>
          <MapLegend>
            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
              {mapType === 'temperature' && 'Temperature (°C)'}
              {mapType === 'humidity' && 'Humidity (%)'}
              {mapType === 'wind' && 'Wind Speed (m/s)'}
            </div>
            {mapType === 'temperature' && (
              <>
                <LegendItem>
                  <LegendColor color="#3b82f6" />
                  <span>&lt; 15°C</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#10b981" />
                  <span>15-25°C</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#f59e0b" />
                  <span>25-30°C</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#ef4444" />
                  <span>&gt; 30°C</span>
                </LegendItem>
              </>
            )}
            {mapType === 'humidity' && (
              <>
                <LegendItem>
                  <LegendColor color="#f59e0b" />
                  <span>&lt; 40%</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#10b981" />
                  <span>40-60%</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#3b82f6" />
                  <span>60-80%</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#8b5cf6" />
                  <span>&gt; 80%</span>
                </LegendItem>
              </>
            )}
            {mapType === 'wind' && (
              <>
                <LegendItem>
                  <LegendColor color="#10b981" />
                  <span>&lt; 2 m/s</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#f59e0b" />
                  <span>2-4 m/s</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#ef4444" />
                  <span>4-6 m/s</span>
                </LegendItem>
                <LegendItem>
                  <LegendColor color="#8b5cf6" />
                  <span>&gt; 6 m/s</span>
                </LegendItem>
              </>
            )}
          </MapLegend>

          <MapInfo>
            <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Map Info</div>
            <div>Stations: {stations.length}</div>
            <div>Last Update: {new Date().toLocaleTimeString()}</div>
            <div>Data Source: KMA</div>
          </MapInfo>
        </MapOverlay>

        {stations.map((station) => (
          <WeatherStation
            key={station.id}
            bgColor={station.bgColor}
            style={{ left: `${station.x}%`, top: `${station.y}%` }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: station.id * 0.1 }}
            whileHover={{ scale: 1.2 }}
            onClick={() => setSelectedStation(selectedStation?.id === station.id ? null : station)}
          >
            <StationIcon>
              {getStationIcon(station.icon)}
            </StationIcon>
            
            {selectedStation?.id === station.id && (
              <StationTooltip
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
              >
                <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
                  {station.name}
                </div>
                <div>Temperature: {station.temperature}°C</div>
                <div>Humidity: {station.humidity}%</div>
                <div>Wind: {station.windSpeed} m/s</div>
                <div>Pressure: {station.pressure} hPa</div>
                <div>Visibility: {station.visibility} km</div>
              </StationTooltip>
            )}
          </WeatherStation>
        ))}
      </MapArea>
    </MapContainer>
  );
};

export default WeatherMap;







