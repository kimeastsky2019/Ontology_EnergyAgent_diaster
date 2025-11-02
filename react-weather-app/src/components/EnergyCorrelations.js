import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Zap, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  BarChart3,
  PieChart,
  Target
} from 'lucide-react';
import { Line, Bar } from 'react-chartjs-2';

const CorrelationsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const CorrelationsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const CorrelationsTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ViewToggle = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const ToggleButton = styled.button`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.2)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'rgba(255, 255, 255, 0.6)'};
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
`;

const CorrelationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const CorrelationCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;

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

const CorrelationIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin: 0 auto 1rem;
`;

const CorrelationValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
`;

const CorrelationLabel = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
`;

const CorrelationDescription = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
`;

const ChartContainer = styled.div`
  height: 300px;
  margin-top: 2rem;
`;

const EnergyCorrelations = ({ data }) => {
  const [viewMode, setViewMode] = useState('overview');

  const correlations = [
    {
      icon: Thermometer,
      label: 'Temperature vs Energy Consumption',
      value: '0.78',
      description: 'Strong positive correlation',
      gradient: 'linear-gradient(135deg, #ef4444, #dc2626)',
      bgColor: 'linear-gradient(135deg, #ef4444, #dc2626)',
      trend: 'up'
    },
    {
      icon: Sun,
      label: 'Solar Radiation vs Generation',
      value: '0.92',
      description: 'Very strong positive correlation',
      gradient: 'linear-gradient(135deg, #f59e0b, #d97706)',
      bgColor: 'linear-gradient(135deg, #f59e0b, #d97706)',
      trend: 'up'
    },
    {
      icon: Droplets,
      label: 'Humidity vs Efficiency',
      value: '-0.45',
      description: 'Moderate negative correlation',
      gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)',
      bgColor: 'linear-gradient(135deg, #3b82f6, #2563eb)',
      trend: 'down'
    },
    {
      icon: Wind,
      label: 'Wind Speed vs Turbine Output',
      value: '0.65',
      description: 'Strong positive correlation',
      gradient: 'linear-gradient(135deg, #10b981, #059669)',
      bgColor: 'linear-gradient(135deg, #10b981, #059669)',
      trend: 'up'
    }
  ];

  const generateCorrelationData = () => {
    const labels = [];
    const tempData = [];
    const energyData = [];
    const solarData = [];
    const generationData = [];

    for (let i = 0; i < 24; i++) {
      const hour = new Date().getHours() - 23 + i;
      labels.push(`${hour}:00`);
      
      // 온도 데이터 (시간대별 패턴)
      const temp = 20 + Math.sin((hour - 6) * Math.PI / 12) * 8 + (Math.random() - 0.5) * 2;
      tempData.push(temp);
      
      // 에너지 소비 데이터 (온도와 상관관계)
      const energy = 100 + temp * 2.5 + (Math.random() - 0.5) * 20;
      energyData.push(energy);
      
      // 태양복사량 데이터
      const solar = Math.max(0, Math.sin((hour - 6) * Math.PI / 12) * 1000 + (Math.random() - 0.5) * 200);
      solarData.push(solar);
      
      // 태양광 발전 데이터 (태양복사량과 상관관계)
      const generation = solar * 0.8 + (Math.random() - 0.5) * 100;
      generationData.push(generation);
    }

    return {
      labels,
      tempData,
      energyData,
      solarData,
      generationData
    };
  };

  const correlationData = generateCorrelationData();

  const temperatureEnergyData = {
    labels: correlationData.labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: correlationData.tempData,
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y',
        borderWidth: 2,
        fill: false,
      },
      {
        label: 'Energy Consumption (kWh)',
        data: correlationData.energyData,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        yAxisID: 'y1',
        borderWidth: 2,
        fill: false,
      }
    ]
  };

  const solarGenerationData = {
    labels: correlationData.labels,
    datasets: [
      {
        label: 'Solar Radiation (W/m²)',
        data: correlationData.solarData,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        yAxisID: 'y',
        borderWidth: 2,
        fill: false,
      },
      {
        label: 'Solar Generation (kW)',
        data: correlationData.generationData,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        yAxisID: 'y1',
        borderWidth: 2,
        fill: false,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
          maxTicksLimit: 8,
        }
      },
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
        }
      }
    }
  };

  return (
    <CorrelationsContainer>
      <CorrelationsHeader>
        <CorrelationsTitle>
          <Zap size={24} />
          Energy Correlations
        </CorrelationsTitle>
        <ViewToggle>
          <ToggleButton 
            active={viewMode === 'overview'} 
            onClick={() => setViewMode('overview')}
          >
            <PieChart size={16} />
            Overview
          </ToggleButton>
          <ToggleButton 
            active={viewMode === 'analysis'} 
            onClick={() => setViewMode('analysis')}
          >
            <BarChart3 size={16} />
            Analysis
          </ToggleButton>
        </ViewToggle>
      </CorrelationsHeader>

      {viewMode === 'overview' ? (
        <CorrelationsGrid>
          {correlations.map((correlation, index) => (
            <CorrelationCard
              key={index}
              gradient={correlation.gradient}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <CorrelationIcon bgColor={correlation.bgColor}>
                <correlation.icon size={24} />
              </CorrelationIcon>
              <CorrelationValue>{correlation.value}</CorrelationValue>
              <CorrelationLabel>{correlation.label}</CorrelationLabel>
              <CorrelationDescription>
                {correlation.trend === 'up' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {correlation.description}
              </CorrelationDescription>
            </CorrelationCard>
          ))}
        </CorrelationsGrid>
      ) : (
        <div>
          <ChartContainer>
            <Line data={temperatureEnergyData} options={chartOptions} />
          </ChartContainer>
          <ChartContainer>
            <Line data={solarGenerationData} options={chartOptions} />
          </ChartContainer>
        </div>
      )}
    </CorrelationsContainer>
  );
};

export default EnergyCorrelations;







