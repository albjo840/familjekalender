import { useState, useEffect } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { sv } from 'date-fns/locale'
import axios from 'axios'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import './App.css'
import EventModal from './components/EventModal'
import AIChatBanner from './components/AIChatBanner'

const locales = {
  'sv': sv,
}

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
})

// 24-timmars format för svensk tid
const formats = {
  timeGutterFormat: 'HH:mm',
  eventTimeRangeFormat: ({ start, end }, culture, localizer) =>
    localizer.format(start, 'HH:mm', culture) + ' - ' + localizer.format(end, 'HH:mm', culture),
  agendaTimeRangeFormat: ({ start, end }, culture, localizer) =>
    localizer.format(start, 'HH:mm', culture) + ' - ' + localizer.format(end, 'HH:mm', culture),
  selectRangeFormat: ({ start, end }, culture, localizer) =>
    localizer.format(start, 'HH:mm', culture) + ' - ' + localizer.format(end, 'HH:mm', culture),
}

const API_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [events, setEvents] = useState([])
  const [users, setUsers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768)

  // Detektera mobilskärm
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Hämta användare
  useEffect(() => {
    fetchUsers()
  }, [])

  // Hämta events
  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/users`)
      setUsers(response.data)
    } catch (error) {
      console.error('Fel vid hämtning av användare:', error)
    }
  }

  const fetchEvents = async () => {
    try {
      const response = await axios.get(`${API_URL}/events`)
      const formattedEvents = response.data.map(event => ({
        id: event.id,
        title: event.title,
        start: new Date(event.start_time),
        end: new Date(event.end_time),
        resource: event,
      }))
      setEvents(formattedEvents)
    } catch (error) {
      console.error('Fel vid hämtning av händelser:', error)
    }
  }

  const handleSelectSlot = (slotInfo) => {
    setSelectedSlot(slotInfo)
    setSelectedEvent(null)
    setShowModal(true)
  }

  const handleSelectEvent = (event) => {
    setSelectedEvent(event)
    setSelectedSlot(null)
    setShowModal(true)
  }

  const handleSaveEvent = async (eventData) => {
    try {
      if (selectedEvent) {
        // Uppdatera befintlig händelse
        await axios.put(`${API_URL}/events/${selectedEvent.id}`, eventData)
      } else {
        // Skapa ny händelse
        await axios.post(`${API_URL}/events`, eventData)
      }
      fetchEvents()
      setShowModal(false)
      setSelectedEvent(null)
      setSelectedSlot(null)
    } catch (error) {
      console.error('Fel vid sparande av händelse:', error)
    }
  }

  const handleDeleteEvent = async (eventId) => {
    try {
      await axios.delete(`${API_URL}/events/${eventId}`)
      fetchEvents()
      setShowModal(false)
      setSelectedEvent(null)
    } catch (error) {
      console.error('Fel vid borttagning av händelse:', error)
    }
  }

  const eventStyleGetter = (event) => {
    const user = users.find(u => u.id === event.resource.user_id)
    const style = {
      backgroundColor: user ? user.color : '#3174ad',
      borderRadius: '4px',
      opacity: 0.9,
      color: 'white',
      border: 'none',
      display: 'block'
    }
    return {
      style: style
    }
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Familjekalender</h1>
        <div className="user-legend">
          {users.map(user => (
            <div key={user.id} className="user-badge">
              <span
                className="user-color"
                style={{ backgroundColor: user.color }}
              ></span>
              <span className="user-name">{user.name}</span>
            </div>
          ))}
        </div>
      </header>

      <div className="calendar-container">
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          selectable
          onSelectSlot={handleSelectSlot}
          onSelectEvent={handleSelectEvent}
          eventPropGetter={eventStyleGetter}
          views={['month', 'week', 'day']}
          defaultView={isMobile ? 'week' : 'month'}
          culture="sv"
          formats={formats}
          messages={{
            next: "Nästa",
            previous: "Föregående",
            today: "Idag",
            month: "Månad",
            week: "Vecka",
            day: "Dag",
          }}
        />
      </div>

      {showModal && (
        <EventModal
          users={users}
          event={selectedEvent}
          slot={selectedSlot}
          onSave={handleSaveEvent}
          onDelete={handleDeleteEvent}
          onClose={() => {
            setShowModal(false)
            setSelectedEvent(null)
            setSelectedSlot(null)
          }}
        />
      )}

      {/* AI Chat Banner - sticky footer */}
      <AIChatBanner onEventCreated={fetchEvents} />
    </div>
  )
}

export default App
