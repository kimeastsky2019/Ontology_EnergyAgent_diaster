import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  ToggleButtonGroup,
  ToggleButton
} from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon 
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import api from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const RealtimePowerChart = () => {
  const [timeRange, setTimeRange] = useState('hour');
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  useEffect(() => {
    const fetchPowerData = async () => {
      try {
        const response = await api.get(`/energy/realtime?range=${timeRange}`);
        
        const data = response.data;
        
        setChartData({
          labels: data.labels,
          datasets: [
            {
              label: '전력 생산 (kW)',
              data: data.values,
              fill: true,
              backgroundColor: (context) => {
                const ctx = context.chart.ctx;
                const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                gradient.addColorStop(0, 'rgba(255, 107, 53, 0.3)');
                gradient.addColorStop(1, 'rgba(255, 165, 0, 0.05)');
                return gradient;
              },
              borderColor: '#FF6B35',
              borderWidth: 3,
              pointBackgroundColor: '#FFA500',
              pointBorderColor: '#fff',
              pointBorderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6,
              tension: 0.4
            }
          ]
        });
      } catch (error) {
        console.error('Failed to fetch power data:', error);
        // 샘플 데이터
        generateSampleData();
      }
    };

    const generateSampleData = () => {
      const now = new Date();
      const labels = [];
      const values = [];
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now - i * 60 * 60 * 1000);
        labels.push(time.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }));
        // 시간대별로 다른 패턴 (낮에 높고 밤에 낮음)
        const hour = time.getHours();
        let baseValue = 0;
        if (hour >= 6 && hour <= 18) {
          baseValue = 30 + Math.sin((hour - 6) / 12 * Math.PI) * 60;
        } else {
          baseValue = Math.random() * 10;
        }
        values.push(baseValue + Math.random() * 10);
      }
      
      setChartData({
        labels,
        datasets: [
          {
            label: '전력 생산 (kW)',
            data: values,
            fill: true,
            backgroundColor: (context) => {
              const ctx = context.chart.ctx;
              const gradient = ctx.createLinearGradient(0, 0, 0, 300);
              gradient.addColorStop(0, 'rgba(255, 107, 53, 0.3)');
              gradient.addColorStop(1, 'rgba(255, 165, 0, 0.05)');
              return gradient;
            },
            borderColor: '#FF6B35',
            borderWidth: 3,
            pointBackgroundColor: '#FFA500',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.4
          }
        ]
      });
    };

    fetchPowerData();
    const interval = setInterval(fetchPowerData, 10000); // 10초마다 업데이트

    return () => clearInterval(interval);
  }, [timeRange]);

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#2D2D2D',
          font: {
            size: 14,
            weight: 'bold'
          },
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 107, 53, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        padding: 12,
        borderColor: '#FFA500',
        borderWidth: 2,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `전력: ${context.parsed.y.toFixed(2)} kW`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#666',
          font: {
            size: 11
          }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 107, 53, 0.1)',
          borderDash: [5, 5]
        },
        ticks: {
          color: '#666',
          font: {
            size: 12
          },
          callback: function(value) {
            return value + ' kW';
          }
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUpIcon sx={{ color: '#FF6B35', fontSize: 28 }} />
            <Typography variant="h6" color="primary" fontWeight="bold">
              실시간 전력 생산
            </Typography>
          </Box>
          
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                color: '#666',
                borderColor: 'rgba(255, 107, 53, 0.3)',
                '&.Mui-selected': {
                  bgcolor: '#FF6B35',
                  color: 'white',
                  '&:hover': {
                    bgcolor: '#E54E1E'
                  }
                }
              }
            }}
          >
            <ToggleButton value="hour">시간</ToggleButton>
            <ToggleButton value="day">일</ToggleButton>
            <ToggleButton value="month">월</ToggleButton>
            <ToggleButton value="year">년</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Box sx={{ height: 350 }}>
          <Line data={chartData} options={options} />
        </Box>

        {/* 통계 정보 */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-around',
          mt: 3,
          p: 2,
          bgcolor: 'rgba(255, 107, 53, 0.05)',
          borderRadius: 2
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              평균
            </Typography>
            <Typography variant="h6" color="primary" fontWeight="bold">
              {chartData.datasets[0]?.data ? 
                (chartData.datasets[0].data.reduce((a, b) => a + b, 0) / chartData.datasets[0].data.length).toFixed(2) 
                : 0} kW
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              최대
            </Typography>
            <Typography variant="h6" color="primary" fontWeight="bold">
              {chartData.datasets[0]?.data ? 
                Math.max(...chartData.datasets[0].data).toFixed(2) 
                : 0} kW
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              최소
            </Typography>
            <Typography variant="h6" color="primary" fontWeight="bold">
              {chartData.datasets[0]?.data ? 
                Math.min(...chartData.datasets[0].data).toFixed(2) 
                : 0} kW
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RealtimePowerChart;
