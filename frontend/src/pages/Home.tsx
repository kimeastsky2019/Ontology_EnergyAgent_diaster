import { Container, Typography, Box, Grid, Card, CardContent } from '@mui/material'

function Home() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        AI 재난 대응형 에너지 공유 플랫폼
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  에너지 자산
                </Typography>
                <Typography variant="h4" color="primary">
                  -
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  활성 재난
                </Typography>
                <Typography variant="h4" color="error">
                  -
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  에너지 밸런스
                </Typography>
                <Typography variant="h4" color="success.main">
                  -
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
}

export default Home




