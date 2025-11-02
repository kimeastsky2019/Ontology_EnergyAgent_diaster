import { Container, Typography, Box } from '@mui/material'

function Assets() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        에너지 자산 관리
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography>에너지 자산 목록이 여기에 표시됩니다.</Typography>
      </Box>
    </Container>
  )
}

export default Assets




