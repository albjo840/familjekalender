import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './AIChatBanner.css'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Generera en unik session ID för att förhindra multipla bokningar
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

function AIChatBanner({ onEventCreated }) {
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [conversationHistory, setConversationHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(generateSessionId())
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Auto-scroll till senaste meddelandet
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversationHistory])

  // Fokusera input när chatten öppnas
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!message.trim() || isLoading) return

    const userMessage = message.trim()
    setMessage('')
    setIsLoading(true)

    // Lägg till användarmeddelande direkt i UI
    const newHistory = [...conversationHistory, { role: 'user', content: userMessage }]
    setConversationHistory(newHistory)

    try {
      const response = await axios.post(`${API_URL}/ai/chat`, {
        message: userMessage,
        session_id: sessionId,
        conversation_history: conversationHistory
      })

      if (response.data.success) {
        // Uppdatera med AI:ns svar och komplett historik
        setConversationHistory(response.data.conversation_history)

        // Om en händelse skapades, uppdatera kalendern
        if (onEventCreated) {
          onEventCreated()
        }
      } else {
        // Fel från AI:n
        setConversationHistory([
          ...newHistory,
          {
            role: 'assistant',
            content: response.data.error || 'Ett fel uppstod. Försök igen.'
          }
        ])
      }
    } catch (error) {
      console.error('Fel vid AI-chat:', error)
      setConversationHistory([
        ...newHistory,
        {
          role: 'assistant',
          content: 'Kunde inte kommunicera med AI-assistenten. Kontrollera din anslutning.'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const clearChat = () => {
    setConversationHistory([])
  }

  return (
    <div className={`ai-chat-banner ${isOpen ? 'open' : 'closed'}`}>
      {/* Toggle button */}
      <button
        className="ai-chat-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title={isOpen ? 'Stäng AI-assistent' : 'Öppna AI-assistent'}
      >
        <span className="ai-icon">🤖</span>
        <span className="ai-label">AI-assistent</span>
        {!isOpen && conversationHistory.length > 0 && (
          <span className="chat-indicator">{conversationHistory.length}</span>
        )}
      </button>

      {/* Chat container */}
      {isOpen && (
        <div className="ai-chat-container">
          {/* Header */}
          <div className="ai-chat-header">
            <h3>🤖 Kalendern AI-assistent</h3>
            <p className="ai-chat-subtitle">Fråga mig om bokningar eller skapa nya händelser</p>
            {conversationHistory.length > 0 && (
              <button
                className="clear-chat-btn"
                onClick={clearChat}
                title="Rensa chatten"
              >
                🗑️ Rensa
              </button>
            )}
          </div>

          {/* Messages */}
          <div className="ai-chat-messages">
            {conversationHistory.length === 0 ? (
              <div className="ai-welcome-message">
                <p>👋 Hej! Jag är din AI-assistent för kalendern.</p>
                <p>Jag kan hjälpa dig med:</p>
                <ul>
                  <li>📅 Se vad som är bokat</li>
                  <li>➕ Skapa nya bokningar</li>
                  <li>👥 Kolla vem som är bokad när</li>
                </ul>
                <p className="ai-example">
                  <strong>Exempel:</strong><br/>
                  "Vad har jag bokat imorgon?"<br/>
                  "Boka lunch med Maria kl 12 på fredag"
                </p>
              </div>
            ) : (
              conversationHistory.map((msg, index) => (
                <div
                  key={index}
                  className={`ai-message ${msg.role === 'user' ? 'user' : 'assistant'}`}
                >
                  <div className="message-icon">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="ai-message assistant">
                <div className="message-icon">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input form */}
          <form className="ai-chat-input" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Skriv ditt meddelande..."
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              title="Skicka meddelande"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </form>

          {/* Info about deduplication */}
          <div className="ai-chat-footer">
            <small>✅ Dubblettskydd aktivt - endast en bokning skapas per förfrågan</small>
          </div>
        </div>
      )}
    </div>
  )
}

export default AIChatBanner
