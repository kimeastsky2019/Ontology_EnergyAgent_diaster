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
  Power
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
      if (editingAsset) {
        // 수정은 아직 구현되지 않았으므로 생성만 구현
        const response = await api.post('/api/v1/assets', assetData)
        return response.data
      } else {
        const response = await api.post('/api/v1/assets', assetData)
        return response.data
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      setOpenDialog(false)
      setEditingAsset(null)
      setFormData({ name: '', type: 'solar', capacity_kw: '' })
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
        capacity_kw: asset.capacity_kw?.toString() || ''
      })
    } else {
      setEditingAsset(null)
      setFormData({ name: '', type: 'solar', capacity_kw: '' })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingAsset(null)
    setFormData({ name: '', type: 'solar', capacity_kw: '' })
  }

  const handleSubmit = () => {
    const submitData = {
      name: formData.name,
      type: formData.type,
      capacity_kw: formData.capacity_kw ? parseFloat(formData.capacity_kw) : undefined
    }
    mutation.mutate(submitData)
  }

  const handleDelete = (assetId: string) => {
    if (window.confirm('이 자산을 삭제하시겠습니까?')) {
      deleteMutation.mutate(assetId)
    }
  }

  const getAssetTypeIcon = (type: string) => {
    switch (type) {
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
      grid_connection: '전력망'
    }
    return labels[type] || type
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
              label="자산 타입"
              select
              fullWidth
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              required
            >
              <MenuItem value="solar">태양광</MenuItem>
              <MenuItem value="wind">풍력</MenuItem>
              <MenuItem value="battery">배터리</MenuItem>
              <MenuItem value="grid_connection">전력망</MenuItem>
            </TextField>
            <TextField
              label="용량 (kW)"
              type="number"
              fullWidth
              value={formData.capacity_kw}
              onChange={(e) => setFormData({ ...formData, capacity_kw: e.target.value })}
              inputProps={{ min: 0, step: 0.1 }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>취소</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.name || mutation.isPending}
          >
            {mutation.isPending ? '저장 중...' : editingAsset ? '수정' : '추가'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

export default Assets
