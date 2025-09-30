import { NavLink } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Box } from '@mui/material'
import { useTheme } from '@mui/material/styles'

function Header() {
  const theme = useTheme()
  const linkStyle = ({ isActive }) => ({
    color: isActive ? theme.palette.primary.main : theme.palette.text.secondary,
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: 600,
    padding: '6px 12px',
    borderRadius: 8
  })

  return (
    <AppBar position="sticky" elevation={0} sx={{ backgroundColor: 'background.paper', borderBottom: '1px solid rgba(255,255,255,0.06)', mb: 3 }}>
      <Toolbar sx={{ gap: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mr: 'auto' }}>Valet Event Hub</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <NavLink to="/events" style={linkStyle}>Events</NavLink>
          <NavLink to="/locations" style={linkStyle}>Locations</NavLink>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Header


