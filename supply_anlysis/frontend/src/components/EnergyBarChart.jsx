import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  IconButton,
  TextField
} from '@mui/material';
import { 
  BarChart as BarChartIcon,
  NavigateBefore,
  NavigateNext
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import api from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const EnergyBarChart = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  useEffect(() => {
    const fetchEnergyData = async () => {
      try {
        const response = await api.get(`/energy/daily?date=${selectedDate}`);
        
        const data = response.data;
        
        setChartData({
          labels: data.labels,
          datasets: [
            {
              label: '누적 에너지 생산 (kWh)',
              data: data.values,
              backgroundColor: (context) => {
                const value = context.parsed.y;
                const max = Math.max(...data.values);
                const ratio = value / max;
                return `rgba(255, ${Math.floor(107 + (165 - 107) * ratio)}, ${Math.floor(53 + (0 - 53) * ratio)}, 0.8)`;
              },
              borderColor: '#FF6B35',
              borderWidth: 2,
              borderRadius: 8,
              hoverBackgroundColor: 'rgba(255, 107, 53, 1)',
            }
          ]
        });
      } catch (error) {
        console.error('Failed to fetch energy data:', error);
        // 샘플 데이터
        generateSampleData();
      }
    };

    const generateSampleData = () => {
      const labels = [];
      const values = [];
      
      for (let hour = 0; hour < 24; hour++) {
        labels.push(`${hour.toString().padStart(2, '0')}:00`);
        
        // 시간대별 에너지 생산 패턴
        let energy = 0;
        if (hour >= 6 && hour <= 18) {
          // 낮 시간대는 높은 생산량
          energy = 5 + Math.sin((hour - 6) / 12 * Math.PI) * 20 + Math.random() * 5;
        } else {
          // 밤 시간대는 낮은 생산량
          energy = Math.random() * 2;
        }
        
        values.push(energy);
      }
      
      setChartData({
        labels,
        datasets: [
          {
            label: '누적 에너지 생산 (kWh)',
            data: values,
            backgroundColor: (context) => {
              const value = context.parsed.y;
              const max = Math.max(...values);
              const ratio = value / max;
              return `rgba(255, ${Math.floor(107 + (165 - 107) * ratio)}, ${Math.floor(53 + (0 - 53) * ratio)}, 0.8)`;
            },
            borderColor: '#FF6B35',
            borderWidth: 2,
            borderRadius: 8,
            hoverBackgroundColor: 'rgba(255, 107, 53, 1)',
          }
        ]
      });
    };

    fetchEnergyData();
  }, [selectedDate]);

  const handlePreviousDay = () => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() - 1);
    setSelectedDate(date.toISOString().split('T')[0]);
  };

  const handleNextDay = () => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + 1);
    if (date <= new Date()) {
      setSelectedDate(date.toISOString().split('T')[0]);
    }
  };

  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
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
            return `에너지: ${context.parsed.y.toFixed(2)} kWh`;
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
            return value + ' kWh';
          }
        }
      }
    }
  };

  const totalEnergy = chartData.datasets[0]?.data ? 
    chartData.datasets[0].data.reduce((a, b) => a + b, 0).toFixed(2) : 0;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BarChartIcon sx={{ color: '#FF6B35', fontSize: 28 }} />
            <Typography variant="h6" color="primary" fontWeight="bold">
              일일 에너지 생산
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton 
              onClick={handlePreviousDay}
              sx={{ 
                color: '#FF6B35',
                '&:hover': { bgcolor: 'rgba(255, 107, 53, 0.1)' }
              }}
            >
              <NavigateBefore />
            </IconButton>
            
            <TextField
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              size="small"
              InputProps={{
                sx: {
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255, 107, 53, 0.3)',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#FF6B35',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#FF6B35',
                  }
                }
              }}
              inputProps={{
                max: new Date().toISOString().split('T')[0]
              }}
            />
            
            <IconButton 
              onClick={handleNextDay}
              disabled={selectedDate === new Date().toISOString().split('T')[0]}
              sx={{ 
                color: '#FF6B35',
                '&:hover': { bgcolor: 'rgba(255, 107, 53, 0.1)' }
              }}
            >
              <NavigateNext />
            </IconButton>
          </Box>
        </Box>

        <Box sx={{ height: 300 }}>
          <Bar data={chartData} options={options} />
        </Box>

        {/* 일일 총 생산량 */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center',
          alignItems: 'center',
          mt: 3,
          p: 2,
          bgcolor: 'linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 165, 0, 0.1) 100%)',
          borderRadius: 2,
          border: '2px solid rgba(255, 107, 53, 0.3)'
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              총 생산량
            </Typography>
            <Typography variant="h4" color="primary" fontWeight="bold">
              {totalEnergy} kWh
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date(selectedDate).toLocaleDateString('ko-KR', { 
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
              })}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default EnergyBarChart;
