import React, { useState, useEffect } from 'react'
import { Plus, FolderKanban, CheckSquare, Clock, Trash2, Edit2 } from 'lucide-react'
import { useJarvis } from '../context/JarvisContext'

export default function Projects() {
  const { projects, fetchProjects, createProject, tasks, fetchTasks, createTask, completeTask } = useJarvis()
  const [showNewProject, setShowNewProject] = useState(false)
  const [showNewTask, setShowNewTask] = useState(false)
  const [newProject, setNewProject] = useState({ name: '', description: '' })
  const [newTask, setNewTask] = useState({ task: '', priority: 5 })
  const [selectedProject, setSelectedProject] = useState(null)

  useEffect(() => {
    fetchProjects()
    fetchTasks()
  }, [fetchProjects, fetchTasks])

  const handleCreateProject = async (e) => {
    e.preventDefault()
    if (!newProject.name.trim()) return
    await createProject(newProject)
    setNewProject({ name: '', description: '' })
    setShowNewProject(false)
  }

  const handleCreateTask = async (e) => {
    e.preventDefault()
    if (!newTask.task.trim()) return
    await createTask({ ...newTask, project_id: selectedProject?.id })
    setNewTask({ task: '', priority: 5 })
    setShowNewTask(false)
  }

  const projectTasks = selectedProject 
    ? tasks.filter(t => t.project_id === selectedProject.id)
    : tasks.filter(t => !t.project_id)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Projects</h1>
          <p className="text-gray-400 mt-1">Manage your projects and tasks</p>
        </div>
        <button
          onClick={() => setShowNewProject(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
        >
          <Plus size={20} />
          New Project
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Projects List */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FolderKanban size={20} className="text-primary-400" />
            All Projects
          </h2>
          <div className="space-y-3">
            <button
              onClick={() => setSelectedProject(null)}
              className={`w-full text-left p-3 rounded-lg transition-colors ${
                !selectedProject ? 'bg-primary-600/20 text-primary-400' : 'bg-dark-100 hover:bg-dark-200'
              }`}
            >
              <p className="font-medium">All Tasks</p>
              <p className="text-xs text-gray-400">{tasks.length} tasks</p>
            </button>
            {projects.map((project) => (
              <button
                key={project.id}
                onClick={() => setSelectedProject(project)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedProject?.id === project.id ? 'bg-primary-600/20 text-primary-400' : 'bg-dark-100 hover:bg-dark-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <p className="font-medium">{project.name}</p>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    project.status === 'active' ? 'bg-green-600/20 text-green-400' : 'bg-gray-600/20 text-gray-400'
                  }`}>
                    {project.status}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">{project.progress || 0}% complete</p>
              </button>
            ))}
          </div>
        </div>

        {/* Tasks */}
        <div className="lg:col-span-2 glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <CheckSquare size={20} className="text-primary-400" />
              {selectedProject ? selectedProject.name : 'All Tasks'}
            </h2>
            <button
              onClick={() => setShowNewTask(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-dark-100 hover:bg-dark-200 rounded-lg transition-colors text-sm"
            >
              <Plus size={16} />
              Add Task
            </button>
          </div>

          <div className="space-y-3">
            {projectTasks.map((task) => (
              <div key={task.id} className="flex items-center gap-4 p-4 bg-dark-100 rounded-lg group">
                <button
                  onClick={() => completeTask(task.id)}
                  className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                    task.completed 
                      ? 'bg-green-500 border-green-500' 
                      : 'border-gray-500 hover:border-primary-500'
                  }`}
                >
                  {task.completed && <CheckSquare size={14} className="text-white" />}
                </button>
                <div className="flex-1">
                  <p className={task.completed ? 'line-through text-gray-500' : ''}>{task.task}</p>
                  {task.description && (
                    <p className="text-sm text-gray-400 mt-1">{task.description}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  task.priority >= 7 ? 'bg-red-600/20 text-red-400' :
                  task.priority >= 4 ? 'bg-yellow-600/20 text-yellow-400' :
                  'bg-gray-600/20 text-gray-400'
                }`}>
                  P{task.priority}
                </span>
              </div>
            ))}
            {projectTasks.length === 0 && (
              <div className="text-center py-12 text-gray-400">
                <CheckSquare size={48} className="mx-auto mb-4 opacity-50" />
                <p>No tasks yet</p>
                <button
                  onClick={() => setShowNewTask(true)}
                  className="mt-4 text-primary-400 hover:underline"
                >
                  Add your first task
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* New Project Modal */}
      {showNewProject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">New Project</h3>
            <form onSubmit={handleCreateProject}>
              <input
                type="text"
                placeholder="Project name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:border-primary-500"
              />
              <textarea
                placeholder="Description (optional)"
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:border-primary-500 resize-none"
                rows={3}
              />
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowNewProject(false)}
                  className="flex-1 px-4 py-2 bg-dark-100 rounded-lg hover:bg-dark-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Task Modal */}
      {showNewTask && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="glass rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">New Task</h3>
            <form onSubmit={handleCreateTask}>
              <input
                type="text"
                placeholder="What needs to be done?"
                value={newTask.task}
                onChange={(e) => setNewTask({ ...newTask, task: e.target.value })}
                className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:border-primary-500"
              />
              <div className="mb-4">
                <label className="text-sm text-gray-400 mb-2 block">Priority</label>
                <select
                  value={newTask.priority}
                  onChange={(e) => setNewTask({ ...newTask, priority: parseInt(e.target.value) })}
                  className="w-full bg-dark-100 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                >
                  <option value={1}>Low</option>
                  <option value={4}>Medium</option>
                  <option value={7}>High</option>
                  <option value={10}>Critical</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowNewTask(false)}
                  className="flex-1 px-4 py-2 bg-dark-100 rounded-lg hover:bg-dark-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Add Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}