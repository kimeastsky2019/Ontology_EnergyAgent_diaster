import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Alert,
  Button,
  Paper,
  Chip
} from '@mui/material'
import { api } from '../services/api'

interface DisasterAnalysis {
  disaster_analysis?: {
    disaster_type: string
    severity: string
    magnitude: number
    location?: any
    affected_radius_km: number
    priority: number
  }
  energy_analysis?: {
    balance: number
    status: string
    redistribution_needed: boolean
  }
  recommendations?: {
    priority: number
    redistribution_needed: boolean
    status: string
  }
}

interface MCPAgent {
  id: string
  name?: string
  type?: string
  description?: string
  registered_at?: string
}

const Disaster: React.FC = () => {
  const [disasterData, setDisasterData] = useState<any>({})
  const [analysis, setAnalysis] = useState<DisasterAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mcpAgents, setMcpAgents] = useState<MCPAgent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [loadingAgents, setLoadingAgents] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // 샘플 재난 데이터
      const sampleDisasterData = {
        type: 'earthquake',
        magnitude: 6.5,
        location: {
          lat: 35.6762,
          lon: 139.6503,
          name: 'Tokyo'
        }
      }

      const sampleEnergyData = {
        assets: [],
        total_production: 1000,
        total_demand: 800
      }

      const response = await api.post('/api/v1/orchestrator/analyze', {
        disaster_data: sampleDisasterData,
        energy_data: sampleEnergyData
      })

      setAnalysis(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '분석 실패')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  // MCP 에이전트 목록 가져오기
  useEffect(() => {
    const fetchAgents = async () => {
      setLoadingAgents(true)
      try {
        // 인증 없이 접근 가능한 public 엔드포인트 사용
        const response = await api.get('/api/v1/mcp/agents/public')
        const agentsList = Object.entries(response.data.agents || {}).map(([id, info]: [string, any]) => ({
          id,
          ...info
        }))
        setMcpAgents(agentsList)
        if (agentsList.length > 0 && !selectedAgent) {
          setSelectedAgent(agentsList[0].id)
        }
      } catch (err: any) {
        console.error('Failed to fetch MCP agents:', err)
        // 에러 발생 시에도 빈 목록으로 처리
        setMcpAgents([])
      } finally {
        setLoadingAgents(false)
      }
    }
    fetchAgents()
  }, [selectedAgent])

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'error'
      case 'severe': return 'error'
      case 'moderate': return 'warning'
      case 'minor': return 'info'
      default: return 'default'
    }
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          재난 상황 분석
        </Typography>
        <Typography variant="body1" color="text.secondary">
          재난 상황을 분석하고 에너지 재분배를 제안합니다.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* MCP 에이전트 선택 섹션 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                MCP 에이전트 선택
              </Typography>
              {loadingAgents ? (
                <Typography variant="body2" color="text.secondary">
                  에이전트 목록을 불러오는 중...
                </Typography>
              ) : mcpAgents.length > 0 ? (
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {mcpAgents.map((agent) => (
                    <Grid item xs={12} sm={6} md={4} key={agent.id}>
                      <Paper
                        sx={{
                          p: 2,
                          cursor: 'pointer',
                          border: selectedAgent === agent.id ? 2 : 1,
                          borderColor: selectedAgent === agent.id ? 'primary.main' : 'divider',
                          bgcolor: selectedAgent === agent.id ? 'action.selected' : 'background.paper',
                          '&:hover': {
                            bgcolor: 'action.hover'
                          }
                        }}
                        onClick={() => setSelectedAgent(agent.id)}
                      >
                        <Typography variant="subtitle1" fontWeight="bold">
                          {agent.name || agent.id}
                        </Typography>
                        {agent.type && (
                          <Chip
                            label={agent.type}
                            size="small"
                            sx={{ mt: 1, mr: 1 }}
                          />
                        )}
                        {agent.description && (
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            {agent.description}
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  등록된 MCP 에이전트가 없습니다.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ mb: 2 }}>
                <Button
                  variant="contained"
                  onClick={handleAnalyze}
                  disabled={loading || !selectedAgent}
                  sx={{ mr: 2 }}
                >
                  {loading ? '분석 중...' : '상황 분석 실행'}
                </Button>
                {selectedAgent && (
                  <Chip
                    label={`선택된 에이전트: ${mcpAgents.find(a => a.id === selectedAgent)?.name || selectedAgent}`}
                    color="primary"
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {analysis && (
                <Box>
                  {analysis.disaster_analysis && (
                    <Paper sx={{ p: 2, mb: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        재난 분석 결과
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            재난 유형
                          </Typography>
                          <Typography variant="body1" gutterBottom>
                            {analysis.disaster_analysis.disaster_type}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            심각도
                          </Typography>
                          <Chip
                            label={analysis.disaster_analysis.severity}
                            color={getSeverityColor(analysis.disaster_analysis.severity) as any}
                            sx={{ mb: 1 }}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            규모
                          </Typography>
                          <Typography variant="body1">
                            {analysis.disaster_analysis.magnitude}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            영향 반경
                          </Typography>
                          <Typography variant="body1">
                            {analysis.disaster_analysis.affected_radius_km} km
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary">
                            우선순위
                          </Typography>
                          <Typography variant="h5" color="error">
                            {analysis.disaster_analysis.priority} / 10
                          </Typography>
                        </Grid>
                      </Grid>
                    </Paper>
                  )}

                  {analysis.energy_analysis && (
                    <Paper sx={{ p: 2, mb: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        에너지 분석 결과
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            에너지 밸런스
                          </Typography>
                          <Typography variant="h6" color={analysis.energy_analysis.balance >= 0 ? 'success.main' : 'error.main'}>
                            {analysis.energy_analysis.balance.toFixed(2)} kW
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            상태
                          </Typography>
                          <Chip
                            label={analysis.energy_analysis.status}
                            color={analysis.energy_analysis.status === 'surplus' ? 'success' : 'warning'}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary">
                            재분배 필요
                          </Typography>
                          <Chip
                            label={analysis.energy_analysis.redistribution_needed ? '예' : '아니오'}
                            color={analysis.energy_analysis.redistribution_needed ? 'error' : 'success'}
                          />
                        </Grid>
                      </Grid>
                    </Paper>
                  )}

                  {analysis.recommendations && (
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        권장 사항
                      </Typography>
                      <Typography variant="body1">
                        우선순위: {analysis.recommendations.priority}
                      </Typography>
                      <Typography variant="body1">
                        재분배 필요: {analysis.recommendations.redistribution_needed ? '예' : '아니오'}
                      </Typography>
                      <Typography variant="body1">
                        상태: {analysis.recommendations.status}
                      </Typography>
                    </Paper>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}

export default Disaster

