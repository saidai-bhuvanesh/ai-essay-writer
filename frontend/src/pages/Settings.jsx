import React, { useState } from 'react'
import { Settings, User, Shield, Bell, Mic, Database, Palette, Save } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // Voice Settings
    wakeWord: 'jarvis',
    sttEngine: 'whisper',
    ttsEngine: 'pyttsx3',
    voiceRate: 150,
    voiceVolume: 90,
    
    // Security
    faceRecognition: true,
    auditLogging: true,
    killSwitch: true,
    
    // AI Settings
    llmModel: 'llama3',
    llmTemperature: 0.7,
    
    // General
    autoStart: false,
    notifications: true,
    theme: 'dark',
  })

  const handleSave = () => {
    // Save to backend
    console.log('Settings saved:', settings)
    alert('Settings saved successfully!')
  }

  const SettingSection = ({ icon: Icon, title, children }) => (
    <div className="glass rounded-xl p-6 mb-6">
      <div className="flex items-center gap-3 mb-6">
        <Icon size={20} className="text-primary-400" />
        <h2 className="text-xl font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  )

  const Toggle = ({ label, description, checked, onChange }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-800 last:border-0">
      <div>
        <p className="font-medium">{label}</p>
        {description && <p className="text-sm text-gray-400">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`w-12 h-6 rounded-full transition-colors ${
          checked ? 'bg-primary-600' : 'bg-gray-600'
        }`}
      >
        <div className={`w-5 h-5 rounded-full bg-white shadow transform transition-transform ${
          checked ? 'translate-x-6' : 'translate-x-0.5'
        }`} />
      </button>
    </div>
  )

  const Slider = ({ label, value, onChange, min, max, step = 1 }) => (
    <div className="py-3 border-b border-gray-800">
      <div className="flex items-center justify-between mb-2">
        <p className="font-medium">{label}</p>
        <span className="text-primary-400">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-dark-100 rounded-lg appearance-none cursor-pointer accent-primary-500"
      />
    </div>
  )

  const Select = ({ label, value, onChange, options }) => (
    <div className="py-3 border-b border-gray-800">
      <div className="flex items-center justify-between mb-2">
        <p className="font-medium">{label}</p>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="bg-dark-100 border border-gray-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-primary-500"
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>
    </div>
  )

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
          <p className="text-gray-400 mt-1">Configure your JARVIS assistant</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
        >
          <Save size={20} />
          Save Changes
        </button>
      </div>

      {/* Voice Settings */}
      <SettingSection icon={Mic} title="Voice Settings">
        <div className="space-y-0">
          <div className="py-3 border-b border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <p className="font-medium">Wake Word</p>
              <input
                type="text"
                value={settings.wakeWord}
                onChange={(e) => setSettings({ ...settings, wakeWord: e.target.value })}
                className="bg-dark-100 border border-gray-700 rounded-lg px-3 py-1.5 w-40 focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>
          <Select
            label="Speech-to-Text Engine"
            value={settings.sttEngine}
            onChange={(v) => setSettings({ ...settings, sttEngine: v })}
            options={[
              { value: 'whisper', label: 'Whisper' },
              { value: 'faster-whisper', label: 'Faster Whisper' },
            ]}
          />
          <Select
            label="Text-to-Speech Engine"
            value={settings.ttsEngine}
            onChange={(v) => setSettings({ ...settings, ttsEngine: v })}
            options={[
              { value: 'pyttsx3', label: 'pyttsx3' },
              { value: 'gtts', label: 'Google TTS' },
            ]}
          />
          <Slider
            label="Speech Rate"
            value={settings.voiceRate}
            onChange={(v) => setSettings({ ...settings, voiceRate: v })}
            min={50}
            max={300}
          />
          <Slider
            label="Voice Volume"
            value={settings.voiceVolume}
            onChange={(v) => setSettings({ ...settings, voiceVolume: v })}
            min={0}
            max={100}
          />
        </div>
      </SettingSection>

      {/* AI Settings */}
      <SettingSection icon={Database} title="AI Settings">
        <div className="space-y-0">
          <Select
            label="LLM Model"
            value={settings.llmModel}
            onChange={(v) => setSettings({ ...settings, llmModel: v })}
            options={[
              { value: 'llama3', label: 'Llama 3' },
              { value: 'mistral', label: 'Mistral' },
              { value: 'codellama', label: 'Code Llama' },
            ]}
          />
          <Slider
            label="Temperature"
            value={settings.llmTemperature}
            onChange={(v) => setSettings({ ...settings, llmTemperature: v })}
            min={0}
            max={1}
            step={0.1}
          />
        </div>
      </SettingSection>

      {/* Security Settings */}
      <SettingSection icon={Shield} title="Security">
        <div className="space-y-0">
          <Toggle
            label="Face Recognition"
            description="Use face recognition for authentication"
            checked={settings.faceRecognition}
            onChange={(v) => setSettings({ ...settings, faceRecognition: v })}
          />
          <Toggle
            label="Audit Logging"
            description="Log all actions for security review"
            checked={settings.auditLogging}
            onChange={(v) => setSettings({ ...settings, auditLogging: v })}
          />
          <Toggle
            label="Kill Switch"
            description="Enable emergency shutdown functionality"
            checked={settings.killSwitch}
            onChange={(v) => setSettings({ ...settings, killSwitch: v })}
          />
        </div>
      </SettingSection>

      {/* General Settings */}
      <SettingSection icon={Bell} title="General">
        <div className="space-y-0">
          <Toggle
            label="Auto Start"
            description="Start JARVIS when system boots"
            checked={settings.autoStart}
            onChange={(v) => setSettings({ ...settings, autoStart: v })}
          />
          <Toggle
            label="Notifications"
            description="Show system notifications"
            checked={settings.notifications}
            onChange={(v) => setSettings({ ...settings, notifications: v })}
          />
          <Select
            label="Theme"
            value={settings.theme}
            onChange={(v) => setSettings({ ...settings, theme: v })}
            options={[
              { value: 'dark', label: 'Dark' },
              { value: 'light', label: 'Light' },
              { value: 'system', label: 'System' },
            ]}
          />
        </div>
      </SettingSection>

      {/* About */}
      <SettingSection icon={User} title="About">
        <div className="space-y-2 text-gray-400">
          <p><span className="text-white">Version:</span> v1.0</p>
          <p><span className="text-white">Owner:</span> Bhuvi</p>
          <p><span className="text-white">Framework:</span> STUDX JARVIS</p>
          <p className="text-sm mt-4">A local AI-powered personal assistant with voice interaction, memory, automation, and more.</p>
        </div>
      </SettingSection>
    </div>
  )
}