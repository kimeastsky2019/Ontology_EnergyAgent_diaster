import React from 'react'
import { Card, CardContent, Typography, Box, Grid } from '@mui/material'
import {
  WbSunny,
  WbCloudy,
  Cloud,
  Grain,
  WaterDrop,
  Air,
  Visibility,
  Compress
} from '@mui/icons-material'
import type { WeatherData, WeatherForecast } from '../../types/weather'

interface WeatherCardProps {
  weather?: WeatherData
  forecast?: WeatherForecast[]
}

const WeatherCard: React.FC<WeatherCardProps> = ({ weather, forecast }) => {
  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return <WbSunny sx={{ fontSize: 30 }} />
      case 'cloudy':
      case 'clouds':
        return <WbCloudy sx={{ fontSize: 30 }} />
      case 'rainy':
      case 'rain':
        return <Grain sx={{ fontSize: 30 }} />
      default:
        return <Cloud sx={{ fontSize: 30 }} />
    }
  }

  if (!weather) {
    return (
      <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            날씨 정보를 불러오는 중...
          </Typography>
        </CardContent>
      </Card>
    )
  }

  const formatTime = (timestamp: string | number) => {
    if (typeof timestamp === 'number') {
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    }
    return timestamp
  }

  return (
    <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
      <CardContent>
        {/* 날짜 및 위치 */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {new Date().toLocaleDateString('ko-KR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {weather.location}
        </Typography>

        {/* 현재 날씨 */}
        <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
          <Cloud sx={{ fontSize: 60, color: '#78909c', mr: 2 }} />
          <Typography variant="h2" sx={{ fontWeight: 'bold' }}>
            {weather.temperature}°C
          </Typography>
        </Box>

        {/* 상세 정보 */}
        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <WbSunny sx={{ fontSize: 20 }} />
              <Typography variant="body2">일출: {formatTime(weather.sunrise)}</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <WbSunny sx={{ fontSize: 20, color: '#ff9800' }} />
              <Typography variant="body2">일몰: {formatTime(weather.sunset)}</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <WaterDrop sx={{ fontSize: 20, color: '#2196f3' }} />
              <Typography variant="body2">습도: {weather.humidity}%</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Air sx={{ fontSize: 20 }} />
              <Typography variant="body2">풍속: {weather.windSpeed} m/s</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Visibility sx={{ fontSize: 20 }} />
              <Typography variant="body2">가시거리: {weather.visibility} km</Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Compress sx={{ fontSize: 20 }} />
              <Typography variant="body2">기압: {weather.pressure} hPa</Typography>
            </Box>
          </Grid>
        </Grid>

        {/* 일주일 예보 */}
        {forecast && forecast.length > 0 && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              gap: 1,
              mt: 2,
              pt: 2,
              borderTop: '1px solid #e0e0e0'
            }}
          >
            {forecast.slice(0, 7).map((day, index) => (
              <Box
                key={index}
                sx={{
                  textAlign: 'center',
                  flex: 1
                }}
              >
                <Typography variant="caption" display="block">
                  {new Date(day.date).toLocaleDateString('ko-KR', {
                    month: 'numeric',
                    day: 'numeric'
                  })}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 0.5 }}>
                  {getWeatherIcon(day.condition)}
                </Box>
                <Typography variant="caption" display="block">
                  {day.tempMax}° ~ {day.tempMin}°
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default WeatherCard


