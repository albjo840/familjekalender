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
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

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
    await submitMessage()
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

  // Starta ljudinspelning
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Prova olika format beroende på vad som stöds
      let mimeType = 'audio/webm'
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4'
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          mimeType = 'audio/ogg'
        }
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      console.log('Recording with mimeType:', mimeType)

      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        console.log('Audio blob created:', audioBlob.size, 'bytes', audioBlob.type)
        await transcribeAudio(audioBlob, mimeType)

        // Stäng av mikrofonen
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Fel vid åtkomst till mikrofon:', error)
      alert('Kunde inte komma åt mikrofonen. Kontrollera att du har gett tillåtelse.')
    }
  }

  // Stoppa ljudinspelning
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  // Transkribera ljud med Groq Whisper
  const transcribeAudio = async (audioBlob, mimeType) => {
    setIsTranscribing(true)

    try {
      const formData = new FormData()

      // Bestäm filnamn baserat på MIME type
      let filename = 'recording.webm'
      if (mimeType.includes('mp4')) {
        filename = 'recording.mp4'
      } else if (mimeType.includes('ogg')) {
        filename = 'recording.ogg'
      }

      formData.append('audio', audioBlob, filename)
      console.log('Sending audio for transcription:', filename, audioBlob.size, 'bytes')

      const response = await axios.post(`${API_URL}/ai/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 30000 // 30 sekunder timeout
      })

      console.log('Transcription response:', response.data)

      if (response.data.success && response.data.text) {
        const transcribedText = response.data.text.trim()
        console.log('Transcribed text:', transcribedText)
        setMessage(transcribedText)

        // Auto-submit om det finns text
        if (transcribedText) {
          await submitMessage(transcribedText)
        }
      } else {
        console.error('Transkribering misslyckades:', response.data)
        alert(`Kunde inte transkribera ljudet. Fel: ${response.data.error || 'Okänt fel'}`)
      }
    } catch (error) {
      console.error('Fel vid transkribering:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Okänt fel'
      alert(`Ett fel uppstod vid transkribering: ${errorMsg}`)
    } finally {
      setIsTranscribing(false)
    }
  }

  // Extrahera submit-logik till egen funktion
  const submitMessage = async (textToSend) => {
    const userMessage = textToSend || message.trim()

    if (!userMessage || isLoading) return

    setMessage('')
    setIsLoading(true)

    const newHistory = [...conversationHistory, { role: 'user', content: userMessage }]
    setConversationHistory(newHistory)

    try {
      const response = await axios.post(`${API_URL}/ai/chat`, {
        message: userMessage,
        session_id: sessionId,
        conversation_history: conversationHistory
      })

      if (response.data.success) {
        setConversationHistory(response.data.conversation_history)
        if (onEventCreated) {
          onEventCreated()
        }
      } else {
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
            {/* Mikrofon-knapp */}
            <button
              type="button"
              className={`voice-button ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading || isTranscribing}
              title={isRecording ? 'Stoppa inspelning' : 'Håll in för att prata'}
            >
              {isTranscribing ? '⏳' : isRecording ? '🔴' : '🎤'}
            </button>

            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isRecording ? 'Spelar in...' : isTranscribing ? 'Transkriberar...' : 'Skriv eller prata...'}
              disabled={isLoading || isRecording || isTranscribing}
            />

            <button
              type="submit"
              disabled={!message.trim() || isLoading || isRecording || isTranscribing}
              title="Skicka meddelande"
            >
              {isLoading ? '⏳' : '📤'}
            </button>
          </form>

          {/* Info about deduplication and voice */}
          <div className="ai-chat-footer">
            <small>
              ✅ Dubblettskydd aktivt | 🎤 Röststyrning med Groq Whisper
            </small>
          </div>
        </div>
      )}
    </div>
  )
}

export default AIChatBanner
