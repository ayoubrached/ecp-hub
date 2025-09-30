import { useEffect, useMemo, useState } from 'react'
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, ButtonGroup, Button, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material'
import AccessTimeRoundedIcon from '@mui/icons-material/AccessTimeRounded'
import GroupRoundedIcon from '@mui/icons-material/GroupRounded'
import { locations } from '../mock-data'

function formatDateLabel(isoDate) {
  const d = new Date(`${isoDate}T00:00:00`)
  return d.toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })
}

function EventsPage() {
  const [selectedLocationId, setSelectedLocationId] = useState('all')
  const [view, setView] = useState('day')
  const [events, setEvents] = useState([])
  const [addOpen, setAddOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    locationId: '',
    eventName: '',
    date: '',
    startTime: '',
    endTime: '',
    notes: '',
  })

  const fetchEvents = () => {
    fetch(`${import.meta.env.VITE_API_URL}/events`)
      .then((r) => r.json())
      .then((res) => {
        if (res && res.items) setEvents(res.items)
      })
      .catch(() => {})
  }

  useEffect(() => {
    fetchEvents()
  }, [])

  const onChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  const onSubmit = async () => {
    if (!form.locationId || !form.eventName || !form.date || !form.startTime || !form.endTime) return
    setSubmitting(true)
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          locationId: Number(form.locationId),
          eventName: form.eventName,
          date: form.date,
          startTime: form.startTime,
          endTime: form.endTime,
          notes: form.notes,
        }),
      })
      setAddOpen(false)
      setForm({ locationId: '', eventName: '', date: '', startTime: '', endTime: '', notes: '' })
      fetchEvents()
    } catch (_) {
    } finally {
      setSubmitting(false)
    }
  }

  const filteredEvents = useMemo(() => {
    if (selectedLocationId === 'all') return events
    const idNum = Number(selectedLocationId)
    return events.filter(e => e.locationId === idNum)
  }, [selectedLocationId])

  const eventsGroupedByDate = useMemo(() => {
    const map = new Map()
    for (const ev of filteredEvents) {
      if (!map.has(ev.date)) map.set(ev.date, [])
      map.get(ev.date).push(ev)
    }
    return Array.from(map.entries()).sort((a, b) => a[0].localeCompare(b[0]))
  }, [filteredEvents])

  return (
    <Box sx={{ p: 3, maxWidth: 960, mx: 'auto' }}>
      <Stack spacing={3}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 260 }}>
            <InputLabel id="location-select-label" sx={{ color: 'text.primary', '&.Mui-focused': { color: 'primary.main' } }}>Location</InputLabel>
            <Select
              labelId="location-select-label"
              id="location-select"
              label="Location"
              value={selectedLocationId}
              onChange={(e) => setSelectedLocationId(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.16)' },
                '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.24)' },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: 'primary.main' }
              }}
            >
              <MenuItem value="all">All Locations</MenuItem>
              {locations.map(loc => (
                <MenuItem key={loc.id} value={loc.id}>{loc.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <ButtonGroup variant="outlined" aria-label="view range">
            <Button color="primary" variant={view === 'day' ? 'contained' : 'outlined'} onClick={() => setView('day')} sx={view === 'day' ? { boxShadow: 'none' } : { color: 'text.secondary', borderColor: 'rgba(255,255,255,0.16)' }}>Day</Button>
            <Button color="primary" variant={view === 'week' ? 'contained' : 'outlined'} onClick={() => setView('week')} sx={view === 'week' ? { boxShadow: 'none' } : { color: 'text.secondary', borderColor: 'rgba(255,255,255,0.16)' }}>Week</Button>
            <Button color="primary" variant={view === 'month' ? 'contained' : 'outlined'} onClick={() => setView('month')} sx={view === 'month' ? { boxShadow: 'none' } : { color: 'text.secondary', borderColor: 'rgba(255,255,255,0.16)' }}>Month</Button>
          </ButtonGroup>
          <Box sx={{ flex: 1 }} />
          <Button variant="contained" color="primary" onClick={() => setAddOpen(true)}>Add Event</Button>
        </Stack>

        {eventsGroupedByDate.length === 0 ? (
          <Typography color="text.secondary">No events.</Typography>
        ) : (
          eventsGroupedByDate.map(([date, items]) => (
            <Box key={date}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1, textTransform: 'uppercase', letterSpacing: 0.5 }}>{formatDateLabel(date)}</Typography>
              <Stack spacing={2}>
                {items.map(ev => (
                  <Card key={ev.id} variant="outlined">
                    <CardContent sx={{ p: 2.5 }}>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: 'text.primary', mb: 0.5 }}>{ev.name}</Typography>
                      <Stack direction="row" spacing={1.2} alignItems="center" sx={{ mb: 0.5 }}>
                        <AccessTimeRoundedIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                          {ev.startTime} – {ev.endTime}
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={1.2} alignItems="center">
                        <GroupRoundedIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">{ev.notes}</Typography>
                      </Stack>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          ))
        )}
      </Stack>

      <Dialog open={addOpen} onClose={() => setAddOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Add New Event</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Stack spacing={2}>
            <FormControl size="small" fullWidth>
              <InputLabel id="add-location-label">Location</InputLabel>
              <Select
                labelId="add-location-label"
                label="Location"
                value={form.locationId}
                onChange={onChange('locationId')}
              >
                {locations.map(loc => (
                  <MenuItem key={loc.id} value={loc.id}>{loc.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField label="Event Name" value={form.eventName} onChange={onChange('eventName')} fullWidth />
            <TextField label="Date" type="date" value={form.date} onChange={onChange('date')} InputLabelProps={{ shrink: true }} fullWidth />
            <Stack direction="row" spacing={2}>
              <TextField label="Start Time" type="time" value={form.startTime} onChange={onChange('startTime')} InputLabelProps={{ shrink: true }} fullWidth />
              <TextField label="End Time" type="time" value={form.endTime} onChange={onChange('endTime')} InputLabelProps={{ shrink: true }} fullWidth />
            </Stack>
            <TextField label="Notes" value={form.notes} onChange={onChange('notes')} fullWidth multiline minRows={3} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)} disabled={submitting}>Cancel</Button>
          <Button onClick={onSubmit} variant="contained" disabled={submitting || !form.locationId || !form.eventName || !form.date || !form.startTime || !form.endTime}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default EventsPage


