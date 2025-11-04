import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Pagination,
  Stack
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  SolarPower,
  WindPower,
  BatteryChargingFull,
  Power,
  Analytics,
  OpenInNew
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'

interface EnergyAsset {
  id: string
  name: string
  type: string
  capacity_kw?: number
  status?: string
  organization_id?: string
  metadata?: any
  created_at?: string
}

interface AssetListResponse {
  items: EnergyAsset[]
  total: number
  skip: number
  limit: number
}

function Assets() {
  const [page, setPage] = useState(1)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingAsset, setEditingAsset] = useState<EnergyAsset | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    type: 'solar',
    sector: 'supply', // 'demand' 또는 'supply'
    capacity_kw: ''
  })

  const queryClient = useQueryClient()
  const limit = 10

  // 자산 목록 조회
  const { data, isLoading, error } = useQuery<AssetListResponse>({
    queryKey: ['assets', page],
    queryFn: async () => {
      try {
        const skip = (page - 1) * limit
        const response = await api.get('/api/v1/assets', {
          params: { skip, limit }
        })
        return response.data
      } catch (err: any) {
        console.error('Assets fetch error:', err)
        // 에러 발생 시 빈 목록 반환
        return { items: [], total: 0, skip: 0, limit: limit }
      }
    },
    retry: 1,
    refetchOnWindowFocus: false
  })

  // 자산 생성/수정 mutation
  const mutation = useMutation({
    mutationFn: async (assetData: any) => {
      console.log('🚀 자산 추가 요청 시작:', assetData)
      const response = await api.post('/api/v1/assets', assetData)
      console.log('✅ 자산 추가 성공:', response.data)
      return response.data
    },
    onSuccess: (data) => {
      console.log('✅ 자산 추가 완료, 목록 새로고침:', data)
      
      // 수요 부문 자산 추가 시 성공 메시지
      if (data.type === 'demand_sector') {
        console.log('✅ 수요 부문 자산 추가됨, 카드 표시 예정:', data)
      }
      
      // 쿼리 무효화 및 다이얼로그 닫기
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      
      // 약간의 지연 후 다이얼로그 닫기 (카드가 나타나는 것을 확인할 수 있도록)
      setTimeout(() => {
        setOpenDialog(false)
        setEditingAsset(null)
        setFormData({ name: '', type: 'solar', sector: 'supply', capacity_kw: '' })
        
        if (data.type === 'demand_sector') {
          alert('수요 부문 자산이 추가되었습니다.\n에너지 수요 분석 대시보드 카드가 자동으로 표시됩니다.')
        } else if (data.type === 'solar' || data.type === 'wind' || data.type === 'battery' || data.type === 'grid_connection') {
          alert('공급 부문 자산이 추가되었습니다.\n에너지 공급 분석 대시보드 카드가 자동으로 표시됩니다.')
        }
      }, 300)
    },
    onError: (error: any) => {
      console.error('❌ 자산 추가/수정 오류:', error)
      console.error('에러 상세:', error.response?.data)
      console.error('에러 상태:', error.response?.status)
      console.error('에러 메시지:', error.message)
      console.error('전체 에러 객체:', error)
      
      const errorMessage = 
        error.response?.data?.detail || 
        error.response?.data?.message || 
        error.message || 
        '자산 추가에 실패했습니다.'
      
      alert(`자산 추가 실패:\n${errorMessage}\n\n상세 내용은 콘솔을 확인하세요.`)
    }
  })

  // 자산 삭제 mutation
  const deleteMutation = useMutation({
    mutationFn: async (assetId: string) => {
      await api.delete(`/api/v1/assets/${assetId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
    }
  })

  const handleOpenDialog = (asset?: EnergyAsset) => {
    if (asset) {
      setEditingAsset(asset)
      setFormData({
        name: asset.name,
        type: asset.type,
        sector: asset.type === 'demand_sector' ? 'demand' : 'supply',
        capacity_kw: asset.capacity_kw?.toString() || ''
      })
    } else {
      setEditingAsset(null)
      setFormData({ name: '', type: 'solar', sector: 'supply', capacity_kw: '' })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingAsset(null)
    setFormData({ name: '', type: 'solar', sector: 'supply', capacity_kw: '' })
  }

  const handleSubmit = () => {
    console.log('📝 handleSubmit 호출됨', formData)
    
    // 유효성 검사
    if (!formData.name?.trim()) {
      alert('자산 이름을 입력해주세요.')
      return
    }
    
    if (formData.sector === 'supply' && (!formData.type || formData.type === 'demand_sector')) {
      alert('공급 부문의 자산 타입을 선택해주세요.')
      return
    }
    
    // 부문에 따라 타입 결정
    const assetType = formData.sector === 'demand' ? 'demand_sector' : formData.type
    
    const submitData = {
      name: formData.name.trim(),
      type: assetType,
      sector: formData.sector,
      capacity_kw: formData.capacity_kw ? parseFloat(formData.capacity_kw) : undefined
    }
    
    console.log('📤 제출할 데이터:', submitData)
    
    // mutation 실행
    mutation.mutate(submitData, {
      onSuccess: (data) => {
        console.log('✅ Mutation 성공:', data)
      },
      onError: (error) => {
        console.error('❌ Mutation 실패:', error)
      }
    })
  }

  const handleDelete = (assetId: string) => {
    if (window.confirm('이 자산을 삭제하시겠습니까?')) {
      deleteMutation.mutate(assetId)
    }
  }


  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'online':
        return 'success'
      case 'offline':
        return 'error'
      case 'maintenance':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      solar: '태양광',
      wind: '풍력',
      battery: '배터리',
      grid_connection: '전력망',
      demand_sector: '수요 부문'
    }
    return labels[type] || type
  }
  
  const getAssetTypeIcon = (type: string) => {
    switch (type) {
      case 'demand_sector':
        return <Analytics sx={{ fontSize: 24, color: '#667eea' }} />
      case 'solar':
        return <SolarPower sx={{ fontSize: 24, color: '#ff9800' }} />
      case 'wind':
        return <WindPower sx={{ fontSize: 24, color: '#2196f3' }} />
      case 'battery':
        return <BatteryChargingFull sx={{ fontSize: 24, color: '#4caf50' }} />
      case 'grid_connection':
        return <Power sx={{ fontSize: 24, color: '#9c27b0' }} />
      default:
        return <Power sx={{ fontSize: 24 }} />
    }
  }

  const totalPages = data ? Math.ceil(data.total / limit) : 1

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          에너지 자산 관리
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          자산 추가
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          자산 목록을 불러오는 중 오류가 발생했습니다.
        </Alert>
      )}

      {/* 자산 통계 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                총 자산
              </Typography>
              <Typography variant="h4">
                {isLoading ? <CircularProgress size={24} /> : data?.total || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                운영 중
              </Typography>
              <Typography variant="h4" color="success.main">
                {isLoading ? (
                  <CircularProgress size={24} />
                ) : (
                  data?.items.filter((a) => a.status === 'online').length || 0
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                총 용량
              </Typography>
              <Typography variant="h4">
                {isLoading ? (
                  <CircularProgress size={24} />
                ) : (
                  `${data?.items.reduce((sum, a) => sum + (a.capacity_kw || 0), 0).toFixed(1) || 0} kW`
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                평균 용량
              </Typography>
              <Typography variant="h4">
                {isLoading ? (
                  <CircularProgress size={24} />
                ) : (
                  `${data?.items.length > 0 ? (data.items.reduce((sum, a) => sum + (a.capacity_kw || 0), 0) / data.items.length).toFixed(1) : 0} kW`
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 수요 부문 자산별 에너지 수요 분석 대시보드 카드 - 수요 부문 자산이 있을 때만 표시 */}
      {(() => {
        const demandAssets = data?.items.filter(asset => asset.type === 'demand_sector') || []
        console.log('📊 수요 부문 자산 확인:', {
          totalItems: data?.items.length || 0,
          demandAssetsCount: demandAssets.length,
          demandAssets: demandAssets,
          allAssets: data?.items || []
        })
        
        if (demandAssets.length > 0) {
          return (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12}>
                <Typography variant="h6" component="h2" gutterBottom sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
                  📊 에너지 수요 분석 대시보드
                </Typography>
              </Grid>
              {demandAssets.map((asset) => (
                <Grid item xs={12} md={6} key={asset.id}>
                  <Card
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      cursor: 'pointer',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      height: '100%',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 6
                      }
                    }}
                    onClick={() => {
                      const dashboardUrl = 'https://damcp.gngmeta.com/api/energy-dashboard'
                      console.log('📊 대시보드 열기:', dashboardUrl, '자산:', asset.name)
                      window.open(dashboardUrl, '_blank')
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                          <Analytics sx={{ fontSize: 48, color: 'white' }} />
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="h5" component="div" gutterBottom sx={{ fontWeight: 'bold' }}>
                              {asset.name}
                            </Typography>
                            <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                              에너지 수요 분석 대시보드
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.8, display: 'block' }}>
                              AI 기반 예측 · 이상 탐지 · 데이터 품질 검증
                            </Typography>
                          </Box>
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1, ml: 2 }}>
                          <OpenInNew sx={{ fontSize: 28 }} />
                          <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                            열기
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )
        }
        return null
      })()}

      {/* 공급 부문 자산별 에너지 공급 분석 대시보드 카드 - 공급 부문 자산이 있을 때만 표시 */}
      {(() => {
        try {
          // 공급 부문 자산 필터링 (수요 부문이 아닌 모든 자산)
          const allItems = data?.items || []
          const supplyAssets = allItems.filter(asset => {
            const isSupplyType = asset.type === 'solar' || 
                                 asset.type === 'wind' || 
                                 asset.type === 'battery' || 
                                 asset.type === 'grid_connection'
            const isNotDemand = asset.type !== 'demand_sector'
            return isNotDemand && isSupplyType
          })
          
          console.log('⚡ 공급 부문 자산 확인:', {
            totalItems: allItems.length,
            supplyAssetsCount: supplyAssets.length,
            supplyAssets: supplyAssets,
            allAssets: allItems,
            allAssetTypes: allItems.map(a => a.type),
            filteredByType: allItems.filter(a => a.type === 'solar' || a.type === 'wind' || a.type === 'battery' || a.type === 'grid_connection')
          })
          
          // 공급 부문 자산이 있으면 카드 표시
          if (supplyAssets.length > 0) {
            console.log('✅ 공급 부문 카드 렌더링:', supplyAssets.length, '개')
            return (
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ mb: 2, fontWeight: 'bold', color: 'warning.main' }}>
                    ⚡ 에너지 공급 분석 대시보드
                  </Typography>
                </Grid>
                {supplyAssets.map((asset) => {
                  try {
                    const icon = getAssetTypeIcon(asset.type)
                    const typeLabel = getTypeLabel(asset.type)
                    
                    return (
                      <Grid item xs={12} md={6} key={asset.id}>
                        <Card
                          sx={{
                            background: 'linear-gradient(135deg, #FF6B35 0%, #FFA500 100%)',
                            color: 'white',
                            cursor: 'pointer',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            height: '100%',
                            '&:hover': {
                              transform: 'translateY(-4px)',
                              boxShadow: 6
                            }
                          }}
                          onClick={() => {
                            const dashboardUrl = 'https://damcp.gngmeta.com/supply_analysis'
                            console.log('⚡ 공급 분석 대시보드 열기:', dashboardUrl, '자산:', asset.name, '타입:', asset.type)
                            window.open(dashboardUrl, '_blank')
                          }}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                                {icon}
                                <Box sx={{ flex: 1 }}>
                                  <Typography variant="h5" component="div" gutterBottom sx={{ fontWeight: 'bold' }}>
                                    {asset.name}
                                  </Typography>
                                  <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                                    에너지 공급 분석 대시보드
                                  </Typography>
                                  <Typography variant="caption" sx={{ opacity: 0.8, display: 'block' }}>
                                    {typeLabel} · 실시간 모니터링 · AI 이상 탐지
                                  </Typography>
                                </Box>
                              </Box>
                              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1, ml: 2 }}>
                                <OpenInNew sx={{ fontSize: 28 }} />
                                <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                                  열기
                                </Typography>
                              </Box>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    )
                  } catch (error) {
                    console.error('❌ 공급 부문 카드 렌더링 오류:', error, asset)
                    return null
                  }
                })}
              </Grid>
            )
          } else {
            // 디버깅: 공급 부문 자산이 없을 때 로그
            if (allItems.length > 0) {
              const nonDemandAssets = allItems.filter(a => a.type !== 'demand_sector')
              console.log('⚠️ 공급 부문 카드가 표시되지 않음:', {
                totalAssets: allItems.length,
                nonDemandAssets: nonDemandAssets,
                nonDemandAssetTypes: nonDemandAssets.map(a => a.type),
                filteredSupplyAssets: supplyAssets,
                allItems: allItems
              })
            }
          }
        } catch (error) {
          console.error('❌ 공급 부문 카드 섹션 오류:', error)
        }
        
        return null
      })()}

      {/* 자산 목록 테이블 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>타입</TableCell>
              <TableCell>이름</TableCell>
              <TableCell align="right">용량 (kW)</TableCell>
              <TableCell>상태</TableCell>
              <TableCell>생성일</TableCell>
              <TableCell align="center">작업</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : data && data.items.length > 0 ? (
              data.items.map((asset) => (
                <TableRow key={asset.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getAssetTypeIcon(asset.type)}
                      <Typography variant="body2">{getTypeLabel(asset.type)}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body1" fontWeight="medium">
                      {asset.name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {asset.capacity_kw ? `${asset.capacity_kw.toFixed(2)} kW` : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={asset.status || 'unknown'}
                      color={getStatusColor(asset.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {asset.created_at
                      ? new Date(asset.created_at).toLocaleDateString('ko-KR')
                      : '-'}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(asset)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(asset.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary">
                    등록된 자산이 없습니다.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 페이지네이션 */}
      {data && data.total > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(e, value) => setPage(value)}
            color="primary"
          />
        </Box>
      )}

      {/* 자산 추가/수정 다이얼로그 */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingAsset ? '자산 수정' : '자산 추가'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="자산 이름"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              label="부문 선택"
              select
              fullWidth
              value={formData.sector}
              onChange={(e) => {
                const sector = e.target.value
                const newFormData: any = { 
                  ...formData, 
                  sector
                }
                // 수요 부문 선택 시 타입은 demand_sector로, 공급 부문 선택 시 기본값으로
                if (sector === 'demand') {
                  newFormData.type = 'demand_sector'
                } else {
                  newFormData.type = 'solar' // 공급 부문 기본값
                }
                setFormData(newFormData)
              }}
              required
            >
              <MenuItem value="demand">수요 부문</MenuItem>
              <MenuItem value="supply">공급 부문</MenuItem>
            </TextField>
            {formData.sector === 'supply' && (
              <TextField
                label="자산 타입"
                select
                fullWidth
                value={formData.type || 'solar'}
                onChange={(e) => {
                  setFormData({ ...formData, type: e.target.value })
                }}
                required
              >
                <MenuItem value="solar">태양광</MenuItem>
                <MenuItem value="wind">풍력</MenuItem>
                <MenuItem value="battery">배터리</MenuItem>
                <MenuItem value="grid_connection">전력망</MenuItem>
              </TextField>
            )}
            {formData.sector === 'supply' && (
              <TextField
                label="용량 (kW)"
                type="number"
                fullWidth
                value={formData.capacity_kw}
                onChange={(e) => setFormData({ ...formData, capacity_kw: e.target.value })}
                inputProps={{ min: 0, step: 0.1 }}
              />
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              console.log('추가 버튼 클릭됨', formData)
              handleSubmit()
            }}
            variant="contained"
            disabled={
              !formData.name?.trim() || 
              mutation.isPending ||
              (formData.sector === 'supply' && (!formData.type || formData.type === 'demand_sector'))
            }
            type="button"
          >
            {mutation.isPending ? '저장 중...' : editingAsset ? '수정' : '추가'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Assets
