import React, { useState } from 'react'
import { Grid, Box, Paper } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import FacilityCard from './FacilityCard'
import WeatherCard from './WeatherCard'
import PowerChart from './PowerChart'
import EnergyBarChart from './EnergyBarChart'
import { energyApi } from '../../services/energyApi'
import { weatherApi } from '../../services/weatherApi'

const DashboardLayout: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(new Date())

  // 실시간 전력 데이터
  const { data: realtimePower, isLoading: loadingPower, error: errorPower } = useQuery({
    queryKey: ['realtimePower'],
    queryFn: async () => {
      try {
        return await energyApi.getRealtimePower('U0089')
      } catch (err: any) {
        console.error('Failed to fetch realtime power:', err)
        throw err
      }
    },
    refetchInterval: 5000, // 5초마다 갱신
    retry: 2,
    onError: (err) => {
      console.error('Realtime power query error:', err)
    }
  })

  // 일일 에너지 데이터
  const { data: dailyEnergy, isLoading: loadingEnergy, error: errorEnergy } = useQuery({
    queryKey: ['dailyEnergy', selectedDate],
    queryFn: async () => {
      try {
        return await energyApi.getDailyEnergy('U0089', selectedDate)
      } catch (err: any) {
        console.error('Failed to fetch daily energy:', err)
        throw err
      }
    },
    refetchInterval: 60000, // 1분마다 갱신
    retry: 2,
    onError: (err) => {
      console.error('Daily energy query error:', err)
    }
  })

  // 날씨 데이터
  const { data: weather, isLoading: loadingWeather, error: errorWeather } = useQuery({
    queryKey: ['weather'],
    queryFn: async () => {
      try {
        return await weatherApi.getCurrentWeather('Shanghai')
      } catch (err: any) {
        console.error('Failed to fetch weather:', err)
        throw err
      }
    },
    refetchInterval: 300000, // 5분마다 갱신
    retry: 2,
    onError: (err) => {
      console.error('Weather query error:', err)
    }
  })

  // 날씨 예보
  const { data: forecast, isLoading: loadingForecast, error: errorForecast } = useQuery({
    queryKey: ['forecast'],
    queryFn: async () => {
      try {
        return await weatherApi.getForecast('Shanghai', 7)
      } catch (err: any) {
        console.error('Failed to fetch forecast:', err)
        throw err
      }
    },
    refetchInterval: 3600000, // 1시간마다 갱신
    retry: 2,
    onError: (err) => {
      console.error('Forecast query error:', err)
    }
  })

  // 시설 정보 (실시간 전력에서 가져오기)
  const facilityInfo = realtimePower
    ? {
        id: realtimePower.facility_id,
        name: '光点试验电站01',
        location: 'Asia/Shanghai',
        capacity_kw: 100,
        current_power: realtimePower.current_power,
        status: 'online' as const
      }
    : {
        id: 'U0089',
        name: '光点试验电站01',
        location: 'Asia/Shanghai',
        capacity_kw: 100,
        current_power: 0,
        status: 'online' as const
      }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#e8f5e9',
        padding: 3
      }}
    >
      <Grid container spacing={3}>
        {/* 좌측 패널 */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={3}>
            {/* 시설 정보 */}
            <Grid item xs={12}>
              <FacilityCard facility={facilityInfo} />
            </Grid>

            {/* 날씨 정보 */}
            <Grid item xs={12}>
              <WeatherCard weather={weather} forecast={forecast} />
            </Grid>
          </Grid>
        </Grid>

        {/* 우측 패널 */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {/* 실시간 전력 그래프 */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, height: '400px' }}>
                <PowerChart data={realtimePower?.history || []} />
              </Paper>
            </Grid>

            {/* 누적 에너지 차트 */}
            <Grid item xs={12}>
              <Paper sx={{ p: 2, height: '400px' }}>
                <EnergyBarChart
                  data={dailyEnergy || []}
                  selectedDate={selectedDate}
                  onDateChange={setSelectedDate}
                />
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  )
}

export default DashboardLayout

