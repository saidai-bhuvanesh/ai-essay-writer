import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Home, MessageSquare, FolderKanban, Database, Settings, LogOut, Mic, MicOff } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Projects from './pages/Projects'
import Memory from './pages/Memory'
import SettingsPage from './pages/Settings'
import { JarvisProvider, useJarvis } from './context/JarvisContext'
import VoiceIndicator from './components/VoiceIndicator'

function Sidebar() {
  const { isListening, toggleListening } = useJarvis()
  
  const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/chat', icon: MessageSquare, label: 'Chat' },
    { to: '/projects', icon: FolderKanban, label: 'Projects' },
    { to: '/memory', icon: Database, label: 'Memory' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <aside className="w-64 bg-dark-200 h-screen fixed left-0 top-0 flex flex-col border-r border-gray-800">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold gradient-text">STUDX JARVIS</h1>
        <p className="text-sm text-gray-400 mt-1">v1.0 Local AI Assistant</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive 
                  ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30' 
                  : 'text-gray-400 hover:text-white hover:bg-dark-100'
              }`
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <button
          onClick={toggleListening}
          className={`w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg transition-all ${
            isListening 
              ? 'bg-red-600/20 text-red-400 border border-red-500/30 pulse-glow' 
              : 'bg-dark-100 text-gray-400 hover:text-white hover:bg-gray-800'
          }`}
        >
          {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          <span>{isListening ? 'Stop Listening' : 'Voice Control'}</span>
        </button>
      </div>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
            <span className="font-semibold">B</span>
          </div>
          <div className="flex-1">
            <p className="font-medium">Bhuvi</p>
            <p className="text-xs text-gray-400">Owner</p>
          </div>
          <button className="text-gray-400 hover:text-red-400 transition-colors">
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  )
}

function MainContent() {
  return (
    <main className="ml-64 min-h-screen p-8">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/memory" element={<Memory />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </main>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <JarvisProvider>
        <div className="flex min-h-screen">
          <Sidebar />
          <MainContent />
          <VoiceIndicator />
        </div>
      </JarvisProvider>
    </BrowserRouter>
  )
}