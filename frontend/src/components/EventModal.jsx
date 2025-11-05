import { useState, useEffect } from 'react'
import './EventModal.css'

function EventModal({ users, event, slot, onSave, onDelete, onClose }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    user_id: users[0]?.id || 1,
    all_day: false,
    reminder_enabled: false,
    reminder_minutes: 30,
  })

  useEffect(() => {
    if (event) {
      // Redigera befintlig händelse
      setFormData({
        title: event.resource.title,
        description: event.resource.description || '',
        start_time: formatDateTimeLocal(event.start),
        end_time: formatDateTimeLocal(event.end),
        user_id: event.resource.user_id,
        all_day: event.resource.all_day,
        reminder_enabled: event.resource.reminder_enabled,
        reminder_minutes: event.resource.reminder_minutes,
      })
    } else if (slot) {
      // Ny händelse från valt tidsintervall
      setFormData(prev => ({
        ...prev,
        start_time: formatDateTimeLocal(slot.start),
        end_time: formatDateTimeLocal(slot.end),
      }))
    }
  }, [event, slot])

  const formatDateTimeLocal = (date) => {
    const d = new Date(date)
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
    return d.toISOString().slice(0, 16)
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    const eventData = {
      ...formData,
      start_time: new Date(formData.start_time).toISOString(),
      end_time: new Date(formData.end_time).toISOString(),
    }

    onSave(eventData)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const getUserColor = (userId) => {
    const user = users.find(u => u.id === parseInt(userId))
    return user ? user.color : '#3174ad'
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{event ? 'Redigera händelse' : 'Ny händelse'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Titel *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="Händelsens titel"
            />
          </div>

          <div className="form-group">
            <label htmlFor="user_id">Person</label>
            <select
              id="user_id"
              name="user_id"
              value={formData.user_id}
              onChange={handleChange}
              style={{ borderLeft: `4px solid ${getUserColor(formData.user_id)}` }}
            >
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start_time">Starttid *</label>
              <input
                type="datetime-local"
                id="start_time"
                name="start_time"
                value={formData.start_time}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="end_time">Sluttid *</label>
              <input
                type="datetime-local"
                id="end_time"
                name="end_time"
                value={formData.end_time}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="all_day"
                checked={formData.all_day}
                onChange={handleChange}
              />
              <span>Heldag</span>
            </label>
          </div>

          <div className="form-group">
            <label htmlFor="description">Beskrivning</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              placeholder="Lägg till en beskrivning..."
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="reminder_enabled"
                checked={formData.reminder_enabled}
                onChange={handleChange}
              />
              <span>Påminnelse</span>
            </label>
          </div>

          {formData.reminder_enabled && (
            <div className="form-group">
              <label htmlFor="reminder_minutes">Påminn innan (minuter)</label>
              <select
                id="reminder_minutes"
                name="reminder_minutes"
                value={formData.reminder_minutes}
                onChange={handleChange}
              >
                <option value="5">5 minuter</option>
                <option value="15">15 minuter</option>
                <option value="30">30 minuter</option>
                <option value="60">1 timme</option>
                <option value="1440">1 dag</option>
              </select>
            </div>
          )}

          <div className="modal-actions">
            {event && (
              <button
                type="button"
                className="delete-button"
                onClick={() => onDelete(event.id)}
              >
                Ta bort
              </button>
            )}
            <div className="action-buttons">
              <button type="button" className="cancel-button" onClick={onClose}>
                Avbryt
              </button>
              <button type="submit" className="save-button">
                Spara
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EventModal
