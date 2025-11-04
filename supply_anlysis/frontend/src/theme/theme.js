import { createTheme } from '@mui/material/styles';

// 주황색 톤의 에너지 테마
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#FF6B35', // 메인 주황색
      light: '#FF8C61',
      dark: '#E54E1E',
      contrastText: '#fff',
    },
    secondary: {
      main: '#FFA500', // 보조 주황색
      light: '#FFB733',
      dark: '#CC8400',
      contrastText: '#fff',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    error: {
      main: '#D32F2F',
      light: '#EF5350',
      dark: '#C62828',
    },
    success: {
      main: '#66BB6A',
      light: '#81C784',
      dark: '#388E3C',
    },
    info: {
      main: '#29B6F6',
      light: '#4FC3F7',
      dark: '#0288D1',
    },
    background: {
      default: '#FFF8F3', // 연한 주황색 배경
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2D2D2D',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      color: '#FF6B35',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      color: '#FF6B35',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(255, 107, 53, 0.1)',
    '0px 4px 8px rgba(255, 107, 53, 0.1)',
    '0px 6px 12px rgba(255, 107, 53, 0.15)',
    '0px 8px 16px rgba(255, 107, 53, 0.15)',
    '0px 10px 20px rgba(255, 107, 53, 0.2)',
    '0px 12px 24px rgba(255, 107, 53, 0.2)',
    '0px 14px 28px rgba(255, 107, 53, 0.25)',
    '0px 16px 32px rgba(255, 107, 53, 0.25)',
    '0px 18px 36px rgba(255, 107, 53, 0.3)',
    '0px 20px 40px rgba(255, 107, 53, 0.3)',
    '0px 22px 44px rgba(255, 107, 53, 0.35)',
    '0px 24px 48px rgba(255, 107, 53, 0.35)',
    '0px 26px 52px rgba(255, 107, 53, 0.4)',
    '0px 28px 56px rgba(255, 107, 53, 0.4)',
    '0px 30px 60px rgba(255, 107, 53, 0.45)',
    '0px 32px 64px rgba(255, 107, 53, 0.45)',
    '0px 34px 68px rgba(255, 107, 53, 0.5)',
    '0px 36px 72px rgba(255, 107, 53, 0.5)',
    '0px 38px 76px rgba(255, 107, 53, 0.55)',
    '0px 40px 80px rgba(255, 107, 53, 0.55)',
    '0px 42px 84px rgba(255, 107, 53, 0.6)',
    '0px 44px 88px rgba(255, 107, 53, 0.6)',
    '0px 46px 92px rgba(255, 107, 53, 0.65)',
    '0px 48px 96px rgba(255, 107, 53, 0.65)',
  ],
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 12px rgba(255, 107, 53, 0.1)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0px 8px 24px rgba(255, 107, 53, 0.15)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          padding: '8px 20px',
        },
        contained: {
          boxShadow: '0px 4px 8px rgba(255, 107, 53, 0.2)',
          '&:hover': {
            boxShadow: '0px 6px 12px rgba(255, 107, 53, 0.3)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600,
        },
        colorPrimary: {
          background: 'linear-gradient(45deg, #FF6B35 30%, #FFA500 90%)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

export default theme;
