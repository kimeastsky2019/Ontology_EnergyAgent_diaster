import { useSelector } from 'react-redux'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Avatar,
  Divider,
  Chip,
} from '@mui/material'
import { Person, Email, Badge, CheckCircle } from '@mui/icons-material'
import { RootState } from '../store/store'

function MyPage() {
  const { user } = useSelector((state: RootState) => state.auth)

  if (!user) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" color="error">
              로그인이 필요합니다.
            </Typography>
          </CardContent>
        </Card>
      </Container>
    )
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        마이페이지
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* 프로필 카드 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                <Avatar
                  sx={{
                    width: 100,
                    height: 100,
                    bgcolor: 'primary.main',
                    fontSize: 40,
                  }}
                >
                  {user.email?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5" gutterBottom>
                    {user.email || '사용자'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {user.full_name || '이름 없음'}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      icon={<Badge />}
                      label={user.role || 'user'}
                      color="primary"
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      icon={<CheckCircle />}
                      label="활성 계정"
                      color="success"
                      size="small"
                    />
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 상세 정보 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                계정 정보
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Email color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        이메일
                      </Typography>
                      <Typography variant="body1">{user.email || '-'}</Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Person color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        사용자 ID
                      </Typography>
                      <Typography variant="body1">{user.id || '-'}</Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Badge color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        역할
                      </Typography>
                      <Typography variant="body1">{user.role || 'user'}</Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <CheckCircle color="action" />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        계정 상태
                      </Typography>
                      <Typography variant="body1">
                        {user.is_active ? '활성' : '비활성'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}

export default MyPage
