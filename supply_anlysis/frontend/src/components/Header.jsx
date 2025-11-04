import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { BoltOutlined, AnalyticsOutlined } from '@mui/icons-material';

const Header = () => {
  return (
    <Box sx={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      mb: 3,
      p: 3,
      background: 'linear-gradient(135deg, #FF6B35 0%, #FFA500 100%)',
      borderRadius: 3,
      boxShadow: 3,
      color: 'white'
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <BoltOutlined sx={{ fontSize: 48 }} />
        <Box>
          <Typography variant="h4" fontWeight="bold">
            에너지 모니터링 대시보드
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            실시간 전력 생산 및 AI 기반 이상징후 감지
          </Typography>
        </Box>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Chip 
          icon={<AnalyticsOutlined />}
          label="AI Agent 작동 중" 
          color="success"
          sx={{ 
            bgcolor: 'rgba(255, 255, 255, 0.3)',
            color: 'white',
            fontWeight: 'bold'
          }}
        />
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          {new Date().toLocaleString('ko-KR', { 
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long',
            hour: '2-digit',
            minute: '2-digit'
          })}
        </Typography>
      </Box>
    </Box>
  );
};

export default Header;
