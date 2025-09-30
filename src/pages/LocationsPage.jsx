import { Box, Button, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Stack, Typography } from '@mui/material'
import { locations } from '../mock-data'

function LocationsPage() {
  return (
    <Box sx={{ p: 3, maxWidth: 1000, mx: 'auto' }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 800 }}>Locations</Typography>
        <Button variant="contained" color="primary">Add New Location</Button>
      </Stack>

      <TableContainer component={Paper}>
        <Table size="small" aria-label="locations table">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Location Name</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Address</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {locations.map((loc) => (
              <TableRow key={loc.id} hover>
                <TableCell>{loc.name}</TableCell>
                <TableCell>{loc.address}</TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <Button size="small" variant="outlined">Edit</Button>
                    <Button size="small" variant="outlined" color="error">Delete</Button>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default LocationsPage


