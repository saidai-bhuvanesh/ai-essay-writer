import React, { createContext, useContext, useState, useCallback } from 'react'
import axios from 'axios'

const JarvisContext = createContext(null)

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export function JarvisProvider({ children }) {
  const [isListening, setIsListening] = useState(false)
  const [conversation, setConversation] = useState([])
  const [user, setUser] = useState(null)
  const [stats, setStats] = useState(null)
  const [projects, setProjects] = useState([])
  const [tasks, setTasks] = useState([])
  const [memories, setMemories] = useState([])

  const toggleListening = useCallback(() => {
    setIsListening(prev => !prev)
  }, [])

  const sendMessage = useCallback(async (message) => {
    try {
      const response = await api.post('/chat', { message })
      setConversation(prev => [...prev, 
        { role: 'user', content: message },
        { role: 'assistant', content: response.data.response }
      ])
      return response.data.response
    } catch (error) {
      console.error('Chat error:', error)
      return "I'm having trouble connecting right now. Please try again."
    }
  }, [])

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get('/dashboard/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Stats error:', error)
    }
  }, [])

  const fetchProjects = useCallback(async () => {
    try {
      const response = await api.get('/projects')
      setProjects(response.data)
    } catch (error) {
      console.error('Projects error:', error)
    }
  }, [])

  const fetchTasks = useCallback(async () => {
    try {
      const response = await api.get('/tasks')
      setTasks(response.data)
    } catch (error) {
      console.error('Tasks error:', error)
    }
  }, [])

  const fetchMemories = useCallback(async () => {
    try {
      const response = await api.get('/memory')
      setMemories(response.data)
    } catch (error) {
      console.error('Memories error:', error)
    }
  }, [])

  const createProject = useCallback(async (project) => {
    try {
      const response = await api.post('/projects', project)
      await fetchProjects()
      return response.data
    } catch (error) {
      console.error('Create project error:', error)
      throw error
    }
  }, [fetchProjects])

  const createTask = useCallback(async (task) => {
    try {
      const response = await api.post('/tasks', task)
      await fetchTasks()
      return response.data
    } catch (error) {
      console.error('Create task error:', error)
      throw error
    }
  }, [fetchTasks])

  const completeTask = useCallback(async (taskId) => {
    try {
      await api.post(`/tasks/${taskId}/complete`)
      await fetchTasks()
    } catch (error) {
      console.error('Complete task error:', error)
    }
  }, [fetchTasks])

  const addMemory = useCallback(async (content, category = 'general', importance = 5) => {
    try {
      await api.post('/memory', { content, category, importance })
      await fetchMemories()
    } catch (error) {
      console.error('Add memory error:', error)
    }
  }, [fetchMemories])

  const value = {
    isListening,
    toggleListening,
    conversation,
    setConversation,
    user,
    setUser,
    stats,
    fetchStats,
    projects,
    fetchProjects,
    createProject,
    tasks,
    fetchTasks,
    createTask,
    completeTask,
    memories,
    fetchMemories,
    addMemory,
    sendMessage,
  }

  return (
    <JarvisContext.Provider value={value}>
      {children}
    </JarvisContext.Provider>
  )
}

export function useJarvis() {
  const context = useContext(JarvisContext)
  if (!context) {
    throw new Error('useJarvis must be used within JarvisProvider')
  }
  return context
}