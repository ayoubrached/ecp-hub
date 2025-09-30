import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material'

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#1A2027',
      paper: '#2D3748',
    },
    text: {
      primary: '#F7FAFC',
      secondary: '#A0AEC0',
    },
    primary: {
      main: '#3182CE',
    },
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 700 },
    body2: { color: '#A0AEC0' },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#2D3748',
          border: '1px solid rgba(255,255,255,0.06)',
          boxShadow: '0 4px 14px rgba(0,0,0,0.4)'
        }
      }
    }
  }
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
)
