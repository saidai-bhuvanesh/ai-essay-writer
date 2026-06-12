import React, { useEffect } from 'react'
import { Activity, FolderKanban, CheckSquare, Database, Cpu, HardDrive, Wifi } from 'lucide-react'
import { useJarvis } from '../context/JarvisContext'

export default function Dashboard() {
  const { stats, fetchStats, projects, fetchProjects, tasks, fetchTasks } = useJarvis()

  useEffect(() => {
    fetchStats()
    fetchProjects()
    fetchTasks()
  }, [fetchStats, fetchProjects, fetchTasks])

  const statCards = [
    { label: 'Active Projects', value: stats?.projects?.active || 0, icon: FolderKanban, color: 'text-blue-400' },
    { label: 'Pending Tasks', value: stats?.tasks?.pending || 0, icon: CheckSquare, color: 'text-yellow-400' },
    { label: 'Completed Tasks', value: stats?.tasks?.completed || 0, icon: CheckSquare, color: 'text-green-400' },
    { label: 'Memories', value: stats?.memory?.total_memories || 0, icon: Database, color: 'text-purple-400' },
  ]

  const systemCards = [
    { label: 'CPU', value: `${stats?.system?.cpu_percent || 0}%`, icon: Cpu, color: 'text-cyan-400' },
    { label: 'Memory', value: `${stats?.system?.memory_percent || 0}%`, icon: HardDrive, color: 'text-orange-400' },
    { label: 'Disk', value: `${stats?.system?.disk_percent || 0}%`, icon: HardDrive, color: 'text-red-400' },
    { label: 'Status', value: 'Online', icon: Wifi, color: 'text-green-400' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome back, Bhuvi. Here's your assistant overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">{label}</p>
                <p className="text-3xl font-bold mt-2">{value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-dark-100 ${color}`}>
                <Icon size={24} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="text-primary-400" size={20} />
            <h2 className="text-xl font-semibold">System Status</h2>
          </div>
          <div className="space-y-4">
            {systemCards.map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="flex items-center justify-between p-3 bg-dark-100 rounded-lg">
                <div className="flex items-center gap-3">
                  <Icon className={color} size={20} />
                  <span>{label}</span>
                </div>
                <span className={`font-semibold ${color}`}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Projects */}
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FolderKanban className="text-primary-400" size={20} />
              <h2 className="text-xl font-semibold">Active Projects</h2>
            </div>
          </div>
          <div className="space-y-3">
            {projects.slice(0, 5).map((project) => (
              <div key={project.id} className="p-4 bg-dark-100 rounded-lg">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{project.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    project.status === 'active' ? 'bg-green-600/20 text-green-400' : 'bg-gray-600/20 text-gray-400'
                  }`}>
                    {project.status}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="h-2 bg-dark-300 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary-500 rounded-full transition-all"
                      style={{ width: `${project.progress || 0}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{project.progress || 0}% complete</p>
                </div>
              </div>
            ))}
            {projects.length === 0 && (
              <p className="text-gray-400 text-center py-8">No projects yet. Create one to get started!</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="glass rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <CheckSquare className="text-primary-400" size={20} />
            <h2 className="text-xl font-semibold">Recent Tasks</h2>
          </div>
        </div>
        <div className="space-y-3">
          {tasks.slice(0, 5).map((task) => (
            <div key={task.id} className="flex items-center gap-4 p-4 bg-dark-100 rounded-lg">
              <div className={`w-5 h-5 rounded border-2 ${
                task.completed ? 'bg-green-500 border-green-500' : 'border-gray-500'
              }`}>
                {task.completed && <CheckSquare size={14} className="text-white" />}
              </div>
              <div className="flex-1">
                <p className={task.completed ? 'line-through text-gray-500' : ''}>{task.task}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs ${
                task.priority >= 7 ? 'bg-red-600/20 text-red-400' :
                task.priority >= 4 ? 'bg-yellow-600/20 text-yellow-400' :
                'bg-gray-600/20 text-gray-400'
              }`}>
                Priority {task.priority}
              </span>
            </div>
          ))}
          {tasks.length === 0 && (
            <p className="text-gray-400 text-center py-8">No tasks yet. Add one to stay organized!</p>
          )}
        </div>
      </div>
    </div>
  )
}