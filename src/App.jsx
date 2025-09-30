import './App.css'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Header from './components/Header.jsx'
import EventsPage from './pages/EventsPage.jsx'
import LocationsPage from './pages/LocationsPage.jsx'

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/events" replace />} />
        <Route path="/events" element={<EventsPage />} />
        <Route path="/locations" element={<LocationsPage />} />
      </Routes>
    </Router>
  )
}

export default App
