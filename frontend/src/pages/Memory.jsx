import React, { useState, useEffect } from 'react'
import { Search, Database, Brain, Plus, Trash2, Star, Filter } from 'lucide-react'
import { useJarvis } from '../context/JarvisContext'

export default function Memory() {
  const { memories, fetchMemories, addMemory } = useJarvis()
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [showNew, setShowNew] = useState(false)
  const [newMemory, setNewMemory] = useState({ content: '', category: 'general', importance: 5 })

  useEffect(() => {
    fetchMemories()
  }, [fetchMemories])

  const categories = ['all', 'general', 'preference', 'project', 'learning', 'personal']

  const filteredMemories = memories.filter(m => {
    const matchesSearch = m.content.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = category === 'all' || m.category === category
    return matchesSearch && matchesCategory
  })

  const handleAddMemory = async (e) => {
    e.preventDefault()
    if (!newMemory.content.trim()) return
    await addMemory(newMemory.content, newMemory.category, newMemory.importance)
    setNewMemory({ content: '', category: 'general', importance: 5 })
    setShowNew(false)
  }

  const getImportanceColor = (importance) => {
    if (importance >= 8) return 'text-red-400 bg-red-600/20'
    if (importance >= 5) return 'text-yellow-400 bg-yellow-600/20'
    return 'text-gray-400 bg-gray-600/20'
  }

  const getCategoryColor = (cat) => {
    const colors = {
      general: 'bg-blue-600/20 text-blue-400',
      preference: 'bg-purple-600/20 text-purple-400',
      project: 'bg-green-600/20 text-green-400',
      learning: 'bg-orange-600/20 text-orange-400',
      personal: 'bg-pink-600/20 text-pink-400',
    }
    return colors[cat] || 'bg-gray-600/20 text-gray-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Memory</h1>
          <p className="text-gray-400 mt-1">JARVIS's long-term memory and knowledge</p>
        </div>
        <button
          onClick={() => setShowNew(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
        >
          <Plus size={20} />
          Add Memory
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {categories.slice(1).map((cat) => (
          <div key={cat} className="glass rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 text-sm capitalize">{cat}</span>
              <span className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(cat)}`}>
                {memories.filter(m => m.category === cat).length}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Search & Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search memories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-dark-100 border border-gray-700 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-primary-500"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-dark-100 border border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:border-primary-500"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Memory List */}
      <div className="space-y-4">
        {filteredMemories.length === 0 ? (
          <div className="glass rounded-xl p-12 text-center">
            <Brain size={48} className="mx-auto mb-4 text-gray-600" />
            <p className="text-gray-400">No memories found</p>
            <button
              onClick={() => setShowNew(true)}
              className="mt-4 text-primary-400 hover:underline"
            >
              Add your first memory
            </button>
          </div>
        ) : (
          filteredMemories.map((memory) => (
            <div key={memory.id} className="glass rounded-xl p-6 hover:border-primary-500/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs capitalize ${getCategoryColor(memory.category)}`}>
                      {memory.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 ${getImportanceColor(memory.importance)}`}>
                      <Star size={10} />
                      {memory.importance}
                    </span>
                    <span className="text-xs text-gray-500">
                      Accessed {memory.access_count || 0} times
                    </span>
                  </div>
                  <p className="text-white">{memory.content}</p>
                </div>
                <button className="text-gray-400 hover:text-red-400 transition-colors">
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* New Memory Modal */}
      {showNew && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold mb-4">Add New Memory</h3>
            <form onSubmit={handleAddMemory}>
              <textarea
                placeholder="What would you like JARVIS to remember?"
                value={newMemory.content}
                onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
                className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:border-primary-500 resize-none"
                rows={4}
              />
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Category</label>
                  <select
                    value={newMemory.category}
                    onChange={(e) => setNewMemory({ ...newMemory, category: e.target.value })}
                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                  >
                    {categories.slice(1).map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Importance (1-10)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={newMemory.importance}
                    onChange={(e) => setNewMemory({ ...newMemory, importance: parseInt(e.target.value) })}
                    className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowNew(false)}
                  className="flex-1 px-4 py-2 bg-dark-100 rounded-lg hover:bg-dark-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Save Memory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}