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
  Chip,
  CircularProgress,
  LinearProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { api } from '../services/api'

interface EnergyDemandAnalysis {
  agent?: string
  quality_report?: {
    total_records: number
    quality_score: number
    missing_values: Record<string, any>
    duplicates: number
  }
  anomalies?: Array<{
    timestamp: string
    kWh: number
    kW?: number
    anomaly_score: number
  }>
  training_metrics?: {
    MAE: number
    RMSE: number
    R2: number
    MAPE: number
  }
  predictions?: Array<{
    timestamp: string
    predicted_kWh: number
    confidence_lower: number
    confidence_upper: number
  }>
  statistics?: {
    total_energy_consumed: number
    average_consumption: number
    peak_demand: number
    min_demand: number
    std_deviation: number
    total_records: number
    anomalies_detected: number
    data_quality_score: number
    peak_hour?: number
    off_peak_hour?: number
  }
  timestamp?: string
}

const EnergyDemand: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<EnergyDemandAnalysis | null>(null)
  const [dataFile, setDataFile] = useState<File | null>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setDataFile(event.target.files[0])
    }
  }

  const handleAnalyze = async () => {
    if (!dataFile) {
      setError('파일을 선택해주세요')
      return
    }

    setLoading(true)
    setError(null)
    setAnalysis(null)

    try {
      // Read file and convert to JSON
      const fileContent = await dataFile.text()
      const lines = fileContent.split('\n')
      const headers = lines[0].split(',').map(h => h.trim())
      
      const data = []
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
          const values = lines[i].split(',')
          const row: Record<string, any> = {}
          headers.forEach((header, index) => {
            row[header] = values[index]?.trim()
          })
          data.push(row)
        }
      }

      // Send to API
      const response = await api.post('/api/v1/energy-demand/analyze/public', {
        data: data,
        hours_ahead: 168  // 7 days
      })

      setAnalysis(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '분석 실패')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'success'
    if (score >= 70) return 'warning'
    return 'error'
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          에너지 수요 관리 AI 분석
        </Typography>
        <Typography variant="body1" color="text.secondary">
          에너지 데이터를 분석하여 수요 예측, 이상 탐지, 품질 검증을 수행합니다.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 파일 업로드 및 분석 섹션 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                데이터 업로드 및 분석
              </Typography>
              
              <Box sx={{ mt: 2, mb: 2 }}>
                <input
                  accept=".csv"
                  style={{ display: 'none' }}
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                />
                <label htmlFor="file-upload">
                  <Button variant="outlined" component="span" sx={{ mr: 2 }}>
                    파일 선택
                  </Button>
                </label>
                {dataFile && (
                  <Chip
                    label={dataFile.name}
                    onDelete={() => setDataFile(null)}
                    color="primary"
                    sx={{ mr: 2 }}
                  />
                )}
                <Button
                  variant="contained"
                  onClick={handleAnalyze}
                  disabled={loading || !dataFile}
                  sx={{ mt: 1 }}
                >
                  {loading ? '분석 중...' : '분석 시작'}
                </Button>
              </Box>

              {loading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                    데이터 전처리, 이상 탐지, 예측 모델 학습 중...
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 분석 결과 */}
        {analysis && (
          <>
            {/* 데이터 품질 리포트 */}
            {analysis.quality_report && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      데이터 품질 리포트
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            총 레코드 수
                          </Typography>
                          <Typography variant="h5">
                            {analysis.quality_report.total_records.toLocaleString()}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            데이터 품질 점수
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={analysis.quality_report.quality_score}
                              sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                              color={getQualityColor(analysis.quality_report.quality_score) as any}
                            />
                            <Typography variant="h6">
                              {analysis.quality_report.quality_score.toFixed(1)}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            중복 레코드
                          </Typography>
                          <Typography variant="body1">
                            {analysis.quality_report.duplicates}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* 통계 정보 */}
            {analysis.statistics && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      주요 통계
                    </Typography>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          총 소비량
                        </Typography>
                        <Typography variant="h6">
                          {analysis.statistics.total_energy_consumed.toLocaleString()} kWh
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          평균 소비량
                        </Typography>
                        <Typography variant="h6">
                          {analysis.statistics.average_consumption.toFixed(2)} kWh
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          최대 수요
                        </Typography>
                        <Typography variant="h6">
                          {analysis.statistics.peak_demand.toFixed(2)} kW
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          이상 탐지
                        </Typography>
                        <Typography variant="h6" color="error">
                          {analysis.statistics.anomalies_detected}
                        </Typography>
                      </Grid>
                      {analysis.statistics.peak_hour !== undefined && (
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            피크 시간
                          </Typography>
                          <Typography variant="body1">
                            {analysis.statistics.peak_hour}시
                          </Typography>
                        </Grid>
                      )}
                      {analysis.statistics.off_peak_hour !== undefined && (
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            비피크 시간
                          </Typography>
                          <Typography variant="body1">
                            {analysis.statistics.off_peak_hour}시
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* 모델 성능 메트릭 */}
            {analysis.training_metrics && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      모델 성능 메트릭
                    </Typography>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          MAE
                        </Typography>
                        <Typography variant="body1">
                          {analysis.training_metrics.MAE}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          RMSE
                        </Typography>
                        <Typography variant="body1">
                          {analysis.training_metrics.RMSE}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          R² Score
                        </Typography>
                        <Typography variant="body1">
                          {analysis.training_metrics.R2.toFixed(4)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          MAPE
                        </Typography>
                        <Typography variant="body1">
                          {analysis.training_metrics.MAPE.toFixed(2)}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* 이상 탐지 결과 */}
            {analysis.anomalies && analysis.anomalies.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      이상 탐지 결과
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      탐지된 이상: {analysis.anomalies.length}건
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>시간</TableCell>
                            <TableCell align="right">kWh</TableCell>
                            <TableCell align="right">이상 점수</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analysis.anomalies.slice(0, 10).map((anomaly, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                {anomaly.timestamp ? new Date(anomaly.timestamp).toLocaleString('ko-KR') : '-'}
                              </TableCell>
                              <TableCell align="right">
                                {anomaly.kWh?.toFixed(2) || '-'}
                              </TableCell>
                              <TableCell align="right">
                                {anomaly.anomaly_score?.toFixed(3) || '-'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* 예측 결과 차트 */}
            {analysis.predictions && analysis.predictions.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      7일 수요 예측
                    </Typography>
                    <Box sx={{ mt: 2, height: 400 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={analysis.predictions}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR')}
                          />
                          <YAxis />
                          <Tooltip
                            labelFormatter={(value) => new Date(value).toLocaleString('ko-KR')}
                          />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="predicted_kWh"
                            stroke="#8884d8"
                            name="예측값"
                            strokeWidth={2}
                          />
                          <Line
                            type="monotone"
                            dataKey="confidence_lower"
                            stroke="#82ca9d"
                            name="하한선"
                            strokeDasharray="5 5"
                          />
                          <Line
                            type="monotone"
                            dataKey="confidence_upper"
                            stroke="#ffc658"
                            name="상한선"
                            strokeDasharray="5 5"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </>
        )}
      </Grid>
    </Container>
  )
}

export default EnergyDemand


