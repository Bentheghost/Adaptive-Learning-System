import React, { useState, useEffect } from 'react'
import { agentAPI } from '../../services/api'
import Loading from '../Common/Loading'
import Card from '../Common/Card'
import toast from 'react-hot-toast'

const AgentStatus = () => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
    // Refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const response = await agentAPI.getAnalytics()
      setAnalytics(response.data)
    } catch (error) {
      console.error('Failed to load analytics:', error)
      toast.error('Failed to load agent analytics')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !analytics) return <Loading />

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Analytics Available</h3>
        <p className="text-gray-500 mb-4">Start learning to see agent activity</p>
        <button 
          onClick={fetchAnalytics}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>
    )
  }

  const { overview, agents, difficulty_performance, recent_activity } = analytics

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">🤖 AI Agent Monitoring</h1>
        <p className="text-gray-600">Real-time analytics of all AI agents</p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="p-6">
            <div className="text-3xl mb-2">📚</div>
            <div className="text-4xl font-bold mb-1">{overview.total_lessons_generated}</div>
            <div className="text-blue-100">Lessons Generated</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="p-6">
            <div className="text-3xl mb-2">📝</div>
            <div className="text-4xl font-bold mb-1">{overview.total_quizzes_generated}</div>
            <div className="text-purple-100">Quizzes Created</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="p-6">
            <div className="text-3xl mb-2">✅</div>
            <div className="text-4xl font-bold mb-1">{overview.overall_quiz_accuracy}%</div>
            <div className="text-green-100">Quiz Accuracy</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="p-6">
            <div className="text-3xl mb-2">🎯</div>
            <div className="text-4xl font-bold mb-1">{overview.completion_rate}%</div>
            <div className="text-orange-100">Completion Rate</div>
          </div>
        </Card>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {Object.entries(agents).map(([agentName, agentData]) => (
          <Card key={agentName}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800">{agentName}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  agentData.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {agentData.status}
                </span>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Tasks Completed:</span>
                  <span className="font-semibold">{agentData.tasks_completed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Success Rate:</span>
                  <span className="font-semibold text-green-600">{agentData.success_rate}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Response Time:</span>
                  <span className="font-semibold">{agentData.avg_response_time}s</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Difficulty Performance */}
      <Card className="mb-8">
        <div className="p-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">Performance by Difficulty</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(difficulty_performance).map(([difficulty, stats]) => (
              <div key={difficulty} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-lg font-semibold capitalize">{difficulty}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                    difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {Math.round(stats.accuracy)}%
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Questions:</span>
                    <span className="font-medium">{stats.total}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Correct:</span>
                    <span className="font-medium text-green-600">{stats.correct}</span>
                  </div>
                </div>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${stats.accuracy}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Recent Activity */}
      {recent_activity && recent_activity.length > 0 && (
        <Card>
          <div className="p-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Recent Activity</h3>
            <div className="space-y-3">
              {recent_activity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">{activity.user}</div>
                    <div className="text-sm text-gray-600">
                      {activity.course} → {activity.topic} → {activity.subtopic}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      activity.type === 'lesson' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                    }`}>
                      {activity.type}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Refresh Button */}
      <div className="mt-6 text-center">
        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : '🔄 Refresh Data'}
        </button>
      </div>
    </div>
  )
}

export default AgentStatus