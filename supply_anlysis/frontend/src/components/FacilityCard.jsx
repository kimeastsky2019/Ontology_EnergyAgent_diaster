import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip,
  Divider,
  LinearProgress
} from '@mui/material';
import { 
  Business as BusinessIcon,
  DirectionsCar as CarIcon,
  SolarPower as SolarIcon,
  PowerOutlined,
  CheckCircle,
  Warning
} from '@mui/icons-material';
import api from '../services/api';

const FacilityCard = () => {
  const [facilityData, setFacilityData] = useState({
    name: '光点试验电站01',
    id: 'U0089',
    currentPower: 0,
    status: 'online',
    capacity: 100000, // 100kW
    efficiency: 85
  });

  useEffect(() => {
    const fetchFacilityData = async () => {
      try {
        const response = await api.get('/facilities/current');
        setFacilityData(response.data);
      } catch (error) {
        console.error('Failed to fetch facility data:', error);
      }
    };

    fetchFacilityData();
    const interval = setInterval(fetchFacilityData, 5000); // 5초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const isOnline = facilityData.status === 'online';

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="primary" fontWeight="bold">
            시설 정보
          </Typography>
          <Chip 
            icon={isOnline ? <CheckCircle /> : <Warning />}
            label={isOnline ? 'Online' : 'Offline'}
            color={isOnline ? 'success' : 'error'}
            size="small"
          />
        </Box>

        {/* 건물 및 차량 일러스트 */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          gap: 2,
          p: 3,
          bgcolor: 'rgba(255, 107, 53, 0.05)',
          borderRadius: 2,
          mb: 2
        }}>
          <BusinessIcon sx={{ fontSize: 60, color: '#FF6B35' }} />
          <CarIcon sx={{ fontSize: 60, color: '#FFA500' }} />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            시설명
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="primary">
            {facilityData.name}
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            시설 ID
          </Typography>
          <Typography variant="body1" fontWeight="bold">
            {facilityData.id}
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* 현재 전력 */}
        <Box sx={{ 
          textAlign: 'center', 
          p: 2, 
          bgcolor: 'rgba(255, 165, 0, 0.1)',
          borderRadius: 2,
          mb: 2
        }}>
          <PowerOutlined sx={{ fontSize: 40, color: '#FFA500', mb: 1 }} />
          <Typography variant="h3" color="primary" fontWeight="bold">
            {facilityData.currentPower.toFixed(1)}W
          </Typography>
          <Typography variant="body2" color="text.secondary">
            현재 전력
          </Typography>
        </Box>

        {/* 효율성 */}
        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              시스템 효율
            </Typography>
            <Typography variant="body2" fontWeight="bold" color="primary">
              {facilityData.efficiency}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={facilityData.efficiency} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              bgcolor: 'rgba(255, 107, 53, 0.1)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #FF6B35 0%, #FFA500 100%)',
                borderRadius: 4
              }
            }}
          />
        </Box>

        {/* 태양광 패널 정보 */}
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1,
          mt: 2,
          p: 1.5,
          bgcolor: 'rgba(255, 107, 53, 0.05)',
          borderRadius: 2
        }}>
          <SolarIcon sx={{ color: '#FFA500' }} />
          <Box>
            <Typography variant="body2" fontWeight="bold">
              태양광 패널
            </Typography>
            <Typography variant="caption" color="text.secondary">
              정격 용량: {(facilityData.capacity / 1000).toFixed(0)}kW
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default FacilityCard;
