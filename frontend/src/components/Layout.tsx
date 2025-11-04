import { Outlet, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
} from '@mui/material'
import { RootState } from '../store/store'
import { logout } from '../store/slices/authSlice'

function Layout() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { user } = useSelector((state: RootState) => state.auth)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Energy Orchestrator
          </Typography>
          <Button color="inherit" onClick={() => navigate('/')}>
            홈
          </Button>
          <Button color="inherit" onClick={() => navigate('/assets')}>
            자산
          </Button>
          <Button color="inherit" onClick={() => navigate('/disaster')}>
            재난 분석
          </Button>
          {user ? (
            <Button color="inherit" onClick={() => navigate('/my-page')}>
              마이페이지
            </Button>
          ) : (
            <Button color="inherit" onClick={() => navigate('/login')}>
              로그인
            </Button>
          )}
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ flex: 1, mt: 4, mb: 4 }}>
        <Outlet />
      </Container>
    </Box>
  )
}

export default Layout




