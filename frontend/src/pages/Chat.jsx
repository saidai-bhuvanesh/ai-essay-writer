import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Mic, MicOff, Volume2 } from 'lucide-react'
import { useJarvis } from '../context/JarvisContext'

export default function Chat() {
  const { conversation, sendMessage, isListening, toggleListening } = useJarvis()
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isProcessing) return

    const message = input.trim()
    setInput('')
    setIsProcessing(true)

    try {
      await sendMessage(message)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">Chat</h1>
        <p className="text-gray-400 mt-1">Talk to JARVIS using voice or text</p>
      </div>

      {/* Voice Toggle */}
      <div className="flex justify-end mb-4">
        <button
          onClick={toggleListening}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            isListening 
              ? 'bg-red-600/20 text-red-400 border border-red-500/30' 
              : 'bg-dark-100 text-gray-400 hover:text-white'
          }`}
        >
          {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          {isListening ? 'Voice On' : 'Voice Off'}
        </button>
      </div>

      {/* Chat Container */}
      <div className="flex-1 glass rounded-xl p-6 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {conversation.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <Bot size={48} className="mb-4 text-primary-400" />
              <p className="text-lg">Hello! I'm JARVIS</p>
              <p className="text-sm mt-2">How can I help you today?</p>
            </div>
          )}

          {conversation.map((msg, idx) => (
            <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user' ? 'bg-primary-600' : 'bg-dark-100'
              }`}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} className="text-primary-400" />}
              </div>
              <div className={`max-w-[70%] rounded-xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-primary-600 text-white rounded-tr-none' 
                  : 'bg-dark-100 rounded-tl-none'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-dark-100 flex items-center justify-center">
                <Bot size={20} className="text-primary-400" />
              </div>
              <div className="bg-dark-100 rounded-xl rounded-tl-none p-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 bg-dark-100 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={!input.trim() || isProcessing}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-xl transition-colors flex items-center gap-2"
          >
            <Send size={20} />
            Send
          </button>
        </form>
      </div>
    </div>
  )
}