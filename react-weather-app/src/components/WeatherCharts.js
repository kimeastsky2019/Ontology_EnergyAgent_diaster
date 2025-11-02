import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { TrendingUp, BarChart3, PieChart } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

const ChartsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const ChartHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const ChartTitle = styled.h3`
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const ChartTabs = styled.div`
  display: flex;
  gap: 0.5rem;
`;

const Tab = styled.button`
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

const ChartArea = styled.div`
  height: 400px;
  position: relative;
`;

const WeatherCharts = ({ data }) => {
  const [activeTab, setActiveTab] = React.useState('temperature');

  const generateTimeLabels = () => {
    const labels = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      labels.push(time.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }));
    }
    return labels;
  };

  const generateTemperatureData = () => {
    const baseTemp = data?.temperature || 24.5;
    return Array.from({ length: 24 }, (_, i) => {
      const hour = (new Date().getHours() - 23 + i + 24) % 24;
      const variation = Math.sin((hour - 6) * Math.PI / 12) * 8;
      return baseTemp + variation + (Math.random() - 0.5) * 2;
    });
  };

  const generateHumidityData = () => {
    const baseHumidity = data?.humidity || 65;
    return Array.from({ length: 24 }, (_, i) => {
      const hour = (new Date().getHours() - 23 + i + 24) % 24;
      const variation = -Math.sin((hour - 6) * Math.PI / 12) * 20;
      return Math.max(30, Math.min(90, baseHumidity + variation + (Math.random() - 0.5) * 5));
    });
  };

  const generateWindData = () => {
    const baseWind = data?.windSpeed || 2.3;
    return Array.from({ length: 24 }, () => 
      Math.max(0, baseWind + (Math.random() - 0.5) * 3)
    );
  };

  const temperatureData = {
    labels: generateTimeLabels(),
    datasets: [
      {
        label: 'Temperature (°C)',
        data: generateTemperatureData(),
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#ff6b6b',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
      }
    ]
  };

  const humidityData = {
    labels: generateTimeLabels(),
    datasets: [
      {
        label: 'Humidity (%)',
        data: generateHumidityData(),
        borderColor: '#00b894',
        backgroundColor: 'rgba(0, 184, 148, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#00b894',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
      }
    ]
  };

  const windData = {
    labels: generateTimeLabels(),
    datasets: [
      {
        label: 'Wind Speed (m/s)',
        data: generateWindData(),
        backgroundColor: [
          'rgba(253, 203, 110, 0.8)',
          'rgba(116, 185, 255, 0.8)',
          'rgba(162, 155, 254, 0.8)',
          'rgba(253, 121, 168, 0.8)',
        ],
        borderColor: [
          '#fdcb6e',
          '#74b9ff',
          '#a29bfe',
          '#fd79a8',
        ],
        borderWidth: 2,
      }
    ]
  };

  const weatherDistributionData = {
    labels: ['Sunny', 'Cloudy', 'Rainy', 'Windy'],
    datasets: [
      {
        data: [45, 25, 15, 15],
        backgroundColor: [
          'rgba(255, 107, 107, 0.8)',
          'rgba(116, 185, 255, 0.8)',
          'rgba(0, 184, 148, 0.8)',
          'rgba(253, 203, 110, 0.8)',
        ],
        borderColor: [
          '#ff6b6b',
          '#74b9ff',
          '#00b894',
          '#fdcb6e',
        ],
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
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
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)',
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          padding: 20,
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
    }
  };

  const renderChart = () => {
    switch (activeTab) {
      case 'temperature':
        return <Line data={temperatureData} options={chartOptions} />;
      case 'humidity':
        return <Line data={humidityData} options={chartOptions} />;
      case 'wind':
        return <Bar data={windData} options={chartOptions} />;
      case 'distribution':
        return <Doughnut data={weatherDistributionData} options={doughnutOptions} />;
      default:
        return <Line data={temperatureData} options={chartOptions} />;
    }
  };

  const getChartIcon = () => {
    switch (activeTab) {
      case 'temperature':
        return <TrendingUp size={24} />;
      case 'humidity':
        return <TrendingUp size={24} />;
      case 'wind':
        return <BarChart3 size={24} />;
      case 'distribution':
        return <PieChart size={24} />;
      default:
        return <TrendingUp size={24} />;
    }
  };

  return (
    <ChartsContainer>
      <ChartHeader>
        <ChartTitle>
          {getChartIcon()}
          Weather Analytics
        </ChartTitle>
        <ChartTabs>
          <Tab 
            active={activeTab === 'temperature'} 
            onClick={() => setActiveTab('temperature')}
          >
            Temperature
          </Tab>
          <Tab 
            active={activeTab === 'humidity'} 
            onClick={() => setActiveTab('humidity')}
          >
            Humidity
          </Tab>
          <Tab 
            active={activeTab === 'wind'} 
            onClick={() => setActiveTab('wind')}
          >
            Wind
          </Tab>
          <Tab 
            active={activeTab === 'distribution'} 
            onClick={() => setActiveTab('distribution')}
          >
            Distribution
          </Tab>
        </ChartTabs>
      </ChartHeader>
      
      <ChartArea>
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderChart()}
        </motion.div>
      </ChartArea>
    </ChartsContainer>
  );
};

export default WeatherCharts;







