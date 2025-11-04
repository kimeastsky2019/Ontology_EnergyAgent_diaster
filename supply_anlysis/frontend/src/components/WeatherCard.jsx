import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Grid,
  Divider,
  Chip
} from '@mui/material';
import { 
  WbSunny,
  Cloud,
  Thunderstorm,
  AcUnit,
  Opacity,
  Air,
  Visibility,
  WbTwilight,
  NightsStay
} from '@mui/icons-material';
import api from '../services/api';

const WeatherCard = () => {
  const [weatherData, setWeatherData] = useState({
    current: {
      temp: 17,
      condition: 'sunny',
      humidity: 65,
      windSpeed: 3.5,
      visibility: 10,
      sunrise: '06:30',
      sunset: '18:45'
    },
    forecast: [
      { day: '월', temp: 18, condition: 'sunny' },
      { day: '화', temp: 16, condition: 'cloudy' },
      { day: '수', temp: 15, condition: 'rainy' },
      { day: '목', temp: 17, condition: 'sunny' },
      { day: '금', temp: 19, condition: 'sunny' },
      { day: '토', temp: 20, condition: 'sunny' },
      { day: '일', temp: 18, condition: 'cloudy' }
    ]
  });

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const response = await api.get('/weather/current');
        setWeatherData(response.data);
      } catch (error) {
        console.error('Failed to fetch weather data:', error);
      }
    };

    fetchWeatherData();
    const interval = setInterval(fetchWeatherData, 300000); // 5분마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const getWeatherIcon = (condition) => {
    const iconStyle = { fontSize: 40, color: '#FFA500' };
    switch (condition.toLowerCase()) {
      case 'sunny': return <WbSunny sx={iconStyle} />;
      case 'cloudy': return <Cloud sx={iconStyle} />;
      case 'rainy': return <Thunderstorm sx={iconStyle} />;
      case 'snowy': return <AcUnit sx={iconStyle} />;
      default: return <WbSunny sx={iconStyle} />;
    }
  };

  const getWeatherText = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny': return '맑음';
      case 'cloudy': return '흐림';
      case 'rainy': return '비';
      case 'snowy': return '눈';
      default: return '맑음';
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="primary" fontWeight="bold">
            날씨 정보
          </Typography>
          <Chip 
            label={new Date().toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
            size="small"
            sx={{ bgcolor: 'rgba(255, 107, 53, 0.1)', color: 'primary.main', fontWeight: 'bold' }}
          />
        </Box>

        {/* 현재 날씨 */}
        <Box sx={{ 
          textAlign: 'center', 
          p: 3,
          bgcolor: 'rgba(255, 165, 0, 0.05)',
          borderRadius: 2,
          mb: 2
        }}>
          {getWeatherIcon(weatherData.current.condition)}
          <Typography variant="h2" color="primary" fontWeight="bold" sx={{ my: 1 }}>
            {weatherData.current.temp}°C
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {getWeatherText(weatherData.current.condition)}
          </Typography>
        </Box>

        {/* 일출/일몰 */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center',
              p: 1.5,
              bgcolor: 'rgba(255, 107, 53, 0.05)',
              borderRadius: 2
            }}>
              <WbTwilight sx={{ color: '#FFA500', mb: 0.5 }} />
              <Typography variant="caption" color="text.secondary">
                일출
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {weatherData.current.sunrise}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center',
              p: 1.5,
              bgcolor: 'rgba(255, 107, 53, 0.05)',
              borderRadius: 2
            }}>
              <NightsStay sx={{ color: '#FF6B35', mb: 0.5 }} />
              <Typography variant="caption" color="text.secondary">
                일몰
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {weatherData.current.sunset}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* 상세 정보 */}
        <Grid container spacing={1.5}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Opacity sx={{ color: '#FFA500', fontSize: 24 }} />
              <Typography variant="caption" display="block" color="text.secondary">
                습도
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {weatherData.current.humidity}%
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Air sx={{ color: '#FFA500', fontSize: 24 }} />
              <Typography variant="caption" display="block" color="text.secondary">
                풍속
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {weatherData.current.windSpeed}m/s
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Visibility sx={{ color: '#FFA500', fontSize: 24 }} />
              <Typography variant="caption" display="block" color="text.secondary">
                가시거리
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {weatherData.current.visibility}km
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* 7일 예보 */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          주간 예보
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 0.5 }}>
          {weatherData.forecast.map((day, index) => (
            <Box 
              key={index}
              sx={{ 
                textAlign: 'center',
                p: 1,
                bgcolor: index === 0 ? 'rgba(255, 107, 53, 0.1)' : 'rgba(0, 0, 0, 0.02)',
                borderRadius: 2,
                flex: 1
              }}
            >
              <Typography variant="caption" fontWeight="bold" display="block">
                {day.day}
              </Typography>
              {getWeatherIcon(day.condition)}
              <Typography variant="caption" fontWeight="bold" color="primary" display="block">
                {day.temp}°
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default WeatherCard;
