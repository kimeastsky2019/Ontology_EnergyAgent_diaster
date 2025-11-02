import React from 'react'
import { Card, CardContent, Typography, Box, Chip } from '@mui/material'
import { SolarPower, ElectricCar, Home } from '@mui/icons-material'
import type { FacilityInfo } from '../../types/energy'

interface FacilityCardProps {
  facility: FacilityInfo
}

const FacilityCard: React.FC<FacilityCardProps> = ({ facility }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'success'
      case 'offline': return 'error'
      case 'maintenance': return 'warning'
      default: return 'default'
    }
  }

  return (
    <Card
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        border: '2px solid #81c784'
      }}
    >
      <CardContent>
        {/* 상단: 건물 일러스트 */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2
          }}
        >
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Home sx={{ fontSize: 60, color: '#757575' }} />
            <ElectricCar sx={{ fontSize: 40, color: '#66bb6a' }} />
          </Box>
          <Chip
            label={facility.status.toUpperCase()}
            color={getStatusColor(facility.status) as any}
            size="small"
          />
        </Box>

        {/* 시설 정보 */}
        <Typography variant="h6" gutterBottom>
          {facility.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {facility.id}
        </Typography>

        {/* 현재 전력 */}
        <Box
          sx={{
            mt: 3,
            p: 2,
            backgroundColor: '#f5f5f5',
            borderRadius: 1
          }}
        >
          <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
            {facility.current_power}
            <Typography component="span" variant="h6" sx={{ ml: 1 }}>
              W
            </Typography>
          </Typography>
        </Box>

        {/* 하단: 태양광 패널 아이콘 */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mt: 3
          }}
        >
          <SolarPower sx={{ fontSize: 40, color: '#2196f3' }} />
          <SolarPower sx={{ fontSize: 40, color: '#2196f3' }} />
        </Box>
      </CardContent>
    </Card>
  )
}

export default FacilityCard

