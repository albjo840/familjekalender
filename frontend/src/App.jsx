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
const CACHE_VERSION = 'v2' // Öka detta när cache-format ändras

function App() {
  const [events, setEvents] = useState([])
  const [users, setUsers] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768)
  const [isLoadingEvents, setIsLoadingEvents] = useState(true)
  const [isLoadingUsers, setIsLoadingUsers] = useState(true)

  // Detektera mobilskärm
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Ladda cachad data först, sedan hämta färsk data
  useEffect(() => {
    // Kontrollera cache-version och rensa om den är gammal
    const cachedVersion = localStorage.getItem('familjekalender_cache_version')
    if (cachedVersion !== CACHE_VERSION) {
      console.log('Cache version mismatch, clearing cache...')
      localStorage.removeItem('familjekalender_events')
      localStorage.removeItem('familjekalender_users')
      localStorage.setItem('familjekalender_cache_version', CACHE_VERSION)
    } else {
      // Ladda cached events omedelbart
      const cachedEvents = localStorage.getItem('familjekalender_events')
      if (cachedEvents) {
        try {
          const parsed = JSON.parse(cachedEvents)
          // Formatera events för kalendern
          const formatted = parsed.map(event => ({
            id: event.id,
            title: event.title,
            start: new Date(event.start),
            end: new Date(event.end),
            resource: event.resource
          }))
          setEvents(formatted)
          console.log(`Loaded ${formatted.length} cached events`)
        } catch (e) {
          console.error('Fel vid laddning av cachade events:', e)
          localStorage.removeItem('familjekalender_events')
        }
      }

      // Ladda cached users omedelbart
      const cachedUsers = localStorage.getItem('familjekalender_users')
      if (cachedUsers) {
        try {
          const parsed = JSON.parse(cachedUsers)
          setUsers(parsed)
          console.log(`Loaded ${parsed.length} cached users`)
        } catch (e) {
          console.error('Fel vid laddning av cachade användare:', e)
          localStorage.removeItem('familjekalender_users')
        }
      }
    }

    // Hämta färsk data parallellt
    fetchUsersAndEvents()
  }, [])

  // Hämta användare och events parallellt
  const fetchUsersAndEvents = async () => {
    try {
      const [usersResponse, eventsResponse] = await Promise.all([
        axios.get(`${API_URL}/users`),
        axios.get(`${API_URL}/events`)
      ])

      // Uppdatera users
      setUsers(usersResponse.data)
      localStorage.setItem('familjekalender_users', JSON.stringify(usersResponse.data))
      setIsLoadingUsers(false)

      // Uppdatera events
      const formattedEvents = eventsResponse.data.map(event => ({
        id: event.id,
        title: event.title,
        start: new Date(event.start_time),
        end: new Date(event.end_time),
        resource: event,
      }))
      setEvents(formattedEvents)

      // Cacha events (spara med ISO strings för att kunna serialisera)
      const eventsToCache = eventsResponse.data.map(event => ({
        id: event.id,
        title: event.title,
        start: event.start_time,
        end: event.end_time,
        resource: event,
      }))
      localStorage.setItem('familjekalender_events', JSON.stringify(eventsToCache))
      setIsLoadingEvents(false)
    } catch (error) {
      console.error('Fel vid hämtning av data:', error)
      setIsLoadingUsers(false)
      setIsLoadingEvents(false)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/users`)
      setUsers(response.data)
      localStorage.setItem('familjekalender_users', JSON.stringify(response.data))
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

      // Cacha events
      const eventsToCache = response.data.map(event => ({
        id: event.id,
        title: event.title,
        start: event.start_time,
        end: event.end_time,
        resource: event,
      }))
      localStorage.setItem('familjekalender_events', JSON.stringify(eventsToCache))
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
          {users && users.length > 0 ? (
            users.map(user => (
              <div key={user.id} className="user-badge">
                <span
                  className="user-color"
                  style={{ backgroundColor: user.color }}
                ></span>
                <span className="user-name">{user.name}</span>
              </div>
            ))
          ) : (
            <div style={{ fontSize: '12px', color: '#666' }}>Laddar användare...</div>
          )}
        </div>
      </header>

      <div className="calendar-container">
        {(isLoadingEvents || isLoadingUsers) && events.length === 0 && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Laddar kalender...</p>
          </div>
        )}

        {(isLoadingEvents || isLoadingUsers) && events.length > 0 && (
          <div className="loading-badge">
            <div className="loading-spinner-small"></div>
            <span>Uppdaterar...</span>
          </div>
        )}

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
