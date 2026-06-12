import React from 'react'
import { useJarvis } from '../context/JarvisContext'
import { Mic, MicOff, Volume2 } from 'lucide-react'

export default function VoiceIndicator() {
  const { isListening } = useJarvis()

  if (!isListening) return null

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <div className="glass rounded-2xl p-6 flex items-center gap-4 pulse-glow">
        <div className="flex items-end gap-1 h-8">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-primary-400 rounded-full listening-bar"
              style={{ height: '100%' }}
            />
          ))}
        </div>
        <div className="flex items-center gap-3">
          <Mic className="text-primary-400" size={24} />
          <div>
            <p className="font-medium text-white">Listening...</p>
            <p className="text-xs text-gray-400">Say "Hey Jarvis" to activate</p>
          </div>
        </div>
      </div>
    </div>
  )
}