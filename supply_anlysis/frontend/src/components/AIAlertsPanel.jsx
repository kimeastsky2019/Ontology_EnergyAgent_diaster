import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress
} from '@mui/material';
import { 
  Psychology as AIIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckIcon,
  Build as BuildIcon,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';
import api from '../services/api';

const AIAlertsPanel = () => {
  const [alerts, setAlerts] = useState([]);
  const [diagnostics, setDiagnostics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiStatus, setAiStatus] = useState({
    anomalyDetection: 'active',
    faultDiagnostics: 'active',
    forecasting: 'active'
  });

  useEffect(() => {
    const fetchAIData = async () => {
      try {
        setLoading(true);
        
        // 이상징후 데이터
        const alertsResponse = await api.get('/ai/anomalies');
        setAlerts(alertsResponse.data);
        
        // 고장 진단 데이터
        const diagnosticsResponse = await api.get('/ai/diagnostics');
        setDiagnostics(diagnosticsResponse.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch AI data:', error);
        // 샘플 데이터
        setAlerts([
          {
            id: 1,
            type: 'warning',
            title: '비정상적인 전력 변동 감지',
            description: '14:30-15:00 사이 예상보다 30% 낮은 전력 생산',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            severity: 'medium'
          },
          {
            id: 2,
            type: 'info',
            title: '생산량 예측',
            description: '오늘 총 생산량 예상: 85.3 kWh (평균 대비 +5%)',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            severity: 'low'
          }
        ]);
        
        setDiagnostics([
          {
            id: 1,
            component: '태양광 패널 #3',
            status: 'warning',
            issue: '효율 저하',
            recommendation: '청소 필요 또는 음영 확인',
            confidence: 85
          },
          {
            id: 2,
            component: '인버터 #1',
            status: 'normal',
            issue: '정상 작동',
            recommendation: '다음 점검: 2주 후',
            confidence: 95
          }
        ]);
        
        setLoading(false);
      }
    };

    fetchAIData();
    const interval = setInterval(fetchAIData, 30000); // 30초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'error': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'normal': return <CheckIcon color="success" />;
      default: return <CheckIcon />;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress sx={{ 
            bgcolor: 'rgba(255, 107, 53, 0.1)',
            '& .MuiLinearProgress-bar': {
              bgcolor: '#FF6B35'
            }
          }} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AIIcon sx={{ color: '#FF6B35', fontSize: 28 }} />
            <Typography variant="h6" color="primary" fontWeight="bold">
              AI 모니터링 & 진단
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip 
              icon={<CheckIcon />}
              label="이상감지" 
              size="small"
              color={aiStatus.anomalyDetection === 'active' ? 'success' : 'default'}
            />
            <Chip 
              icon={<BuildIcon />}
              label="고장진단" 
              size="small"
              color={aiStatus.faultDiagnostics === 'active' ? 'success' : 'default'}
            />
            <Chip 
              icon={<TrendingUp />}
              label="예측" 
              size="small"
              color={aiStatus.forecasting === 'active' ? 'success' : 'default'}
            />
          </Box>
        </Box>

        {/* 이상징후 알림 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ color: '#FF6B35' }}>
            🔍 이상징후 감지
          </Typography>
          
          {alerts.length === 0 ? (
            <Alert 
              severity="success" 
              icon={<CheckIcon />}
              sx={{ 
                borderRadius: 2,
                '& .MuiAlert-icon': { color: '#66BB6A' }
              }}
            >
              모든 시스템이 정상적으로 작동 중입니다
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {alerts.map((alert) => (
                <Alert 
                  key={alert.id}
                  severity={getSeverityColor(alert.severity)}
                  sx={{ borderRadius: 2 }}
                  action={
                    <Chip 
                      label={new Date(alert.timestamp).toLocaleTimeString('ko-KR', { 
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                      size="small"
                      sx={{ bgcolor: 'rgba(255, 255, 255, 0.3)' }}
                    />
                  }
                >
                  <Typography variant="body2" fontWeight="bold">
                    {alert.title}
                  </Typography>
                  <Typography variant="caption">
                    {alert.description}
                  </Typography>
                </Alert>
              ))}
            </Box>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* 고장 진단 */}
        <Box>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ color: '#FF6B35' }}>
            🔧 설비 진단
          </Typography>
          
          <List sx={{ bgcolor: 'rgba(255, 107, 53, 0.02)', borderRadius: 2 }}>
            {diagnostics.map((diagnostic, index) => (
              <React.Fragment key={diagnostic.id}>
                <ListItem>
                  <ListItemIcon>
                    {getStatusIcon(diagnostic.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="bold">
                          {diagnostic.component}
                        </Typography>
                        <Chip 
                          label={diagnostic.issue}
                          size="small"
                          color={diagnostic.status === 'normal' ? 'success' : 'warning'}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {diagnostic.recommendation}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            신뢰도:
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={diagnostic.confidence}
                            sx={{ 
                              flex: 1,
                              height: 6,
                              borderRadius: 3,
                              bgcolor: 'rgba(255, 107, 53, 0.1)',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: diagnostic.confidence > 80 ? '#66BB6A' : '#FFA500',
                                borderRadius: 3
                              }
                            }}
                          />
                          <Typography variant="caption" fontWeight="bold" color="primary">
                            {diagnostic.confidence}%
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
                {index < diagnostics.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))}
          </List>
        </Box>

        {/* AI 분석 통계 */}
        <Box sx={{ 
          mt: 3,
          p: 2,
          bgcolor: 'linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(255, 165, 0, 0.05) 100%)',
          borderRadius: 2,
          border: '1px solid rgba(255, 107, 53, 0.2)'
        }}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            AI 분석 현황
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 1 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="primary" fontWeight="bold">
                {alerts.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                감지된 이상징후
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="primary" fontWeight="bold">
                {diagnostics.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                진단된 설비
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="success.main" fontWeight="bold">
                98.5%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                시스템 가동률
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AIAlertsPanel;
