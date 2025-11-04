import React from 'react';
import { ThemeProvider, CssBaseline, Container, Grid, Box } from '@mui/material';
import theme from './theme/theme';
import FacilityCard from './components/FacilityCard';
import WeatherCard from './components/WeatherCard';
import RealtimePowerChart from './components/RealtimePowerChart';
import EnergyBarChart from './components/EnergyBarChart';
import AIAlertsPanel from './components/AIAlertsPanel';
import Header from './components/Header';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #FFF8F3 0%, #FFE8D9 100%)',
        py: 3
      }}>
        <Container maxWidth="xl">
          <Header />
          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {/* 왼쪽 패널 */}
            <Grid item xs={12} md={4} lg={3}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FacilityCard />
                </Grid>
                <Grid item xs={12}>
                  <WeatherCard />
                </Grid>
              </Grid>
            </Grid>

            {/* 오른쪽 패널 */}
            <Grid item xs={12} md={8} lg={9}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <RealtimePowerChart />
                </Grid>
                <Grid item xs={12}>
                  <EnergyBarChart />
                </Grid>
                <Grid item xs={12}>
                  <AIAlertsPanel />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
