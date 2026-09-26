import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { agentAPI } from '../../services/api'
import { 
  Activity, 
  Cpu, 
  TrendingUp, 
  CheckCircle, 
  XCircle,
  Zap,
  Brain,
  BookOpen,
  Target,
  Users,
  Award,
  Clock,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'

const AgentMonitoring = () => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const response = await agentAPI.getAnalytics()
      setAnalytics(response.data)
    } catch (error) {
      toast.error('Failed to load agent analytics')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadAnalytics()
    setRefreshing(false)
    toast.success('Analytics refreshed!')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-4"
          />
          <p className="text-slate-600 font-medium">Loading agent analytics...</p>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <Activity className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-800 mb-2">No analytics available</h2>
      </div>
    )
  }

  const getAgentIcon = (name) => {
    switch(name) {
      case 'TeachingAgent': return BookOpen
      case 'AssessmentAgent': return Brain
      case 'RecommendationAgent': return Target
      case 'KnowledgeAgent': return TrendingUp
      default: return Cpu
    }
  }

  const getAgentColor = (name) => {
    switch(name) {
      case 'TeachingAgent': return 'from-blue-500 to-cyan-500'
      case 'AssessmentAgent': return 'from-green-500 to-emerald-500'
      case 'RecommendationAgent': return 'from-purple-500 to-pink-500'
      case 'KnowledgeAgent': return 'from-orange-500 to-red-500'
      default: return 'from-slate-500 to-slate-600'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="card bg-gradient-to-br from-primary-500 to-accent-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <Activity className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-2">AI Agent Monitoring</h1>
              <p className="text-primary-100">Real-time performance analytics for autonomous agents</p>
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={refreshing}
            className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl font-semibold flex items-center gap-2 disabled:opacity-50"
          >
            <motion.div
              animate={refreshing ? { rotate: 360 } : {}}
              transition={{ duration: 1, repeat: refreshing ? Infinity : 0, ease: "linear" }}
            >
              <Zap className="w-5 h-5" />
            </motion.div>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </motion.button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
              <BookOpen className="w-7 h-7 text-white" />
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-800">{analytics.overview.total_lessons_generated}</div>
              <div className="text-sm text-slate-600">Lessons Generated</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-800">{analytics.overview.total_quizzes_generated}</div>
              <div className="text-sm text-slate-600">Quizzes Created</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Award className="w-7 h-7 text-white" />
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-800">{analytics.overview.overall_quiz_accuracy}%</div>
              <div className="text-sm text-slate-600">Quiz Accuracy</div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center">
              <Users className="w-7 h-7 text-white" />
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-800">{analytics.overview.total_users}</div>
              <div className="text-sm text-slate-600">Active Users</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Agent Performance */}
      <div className="card">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Cpu className="w-7 h-7 text-primary-600" />
          Agent Performance
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {analytics.agents.map((agent, index) => {
            const AgentIcon = getAgentIcon(agent.name)
            const colorClass = getAgentColor(agent.name)

            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border-2 border-slate-200 rounded-xl p-6 hover:border-primary-300 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 bg-gradient-to-br ${colorClass} rounded-xl flex items-center justify-center`}>
                      <AgentIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-800">{agent.name}</h3>
                      <p className="text-sm text-slate-600">{agent.description}</p>
                    </div>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    agent.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {agent.status}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Total Tasks</span>
                    <span className="font-bold text-slate-800">{agent.total_tasks}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Errors</span>
                    <span className="font-bold text-red-600">{agent.errors}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Success Rate</span>
                    <div className="flex items-center gap-2">
                      <span className={`font-bold ${
                        agent.success_rate >= 95 ? 'text-green-600' :
                        agent.success_rate >= 80 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {agent.success_rate}%
                      </span>
                      {agent.success_rate >= 95 && <CheckCircle className="w-5 h-5 text-green-600" />}
                      {agent.success_rate < 95 && <XCircle className="w-5 h-5 text-red-600" />}
                    </div>
                  </div>

                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden mt-2">
                    <div 
                      className={`h-full bg-gradient-to-r ${colorClass} rounded-full transition-all duration-500`}
                      style={{ width: `${agent.success_rate}%` }}
                    ></div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Difficulty Performance */}
      <div className="card">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <BarChart3 className="w-7 h-7 text-primary-600" />
          Performance by Difficulty
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(analytics.difficulty_performance).map(([difficulty, stats], index) => (
            <motion.div
              key={difficulty}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-6 rounded-xl border-2 ${
                difficulty === 'beginner' ? 'border-green-200 bg-green-50' :
                difficulty === 'intermediate' ? 'border-yellow-200 bg-yellow-50' :
                'border-red-200 bg-red-50'
              }`}
            >
              <h3 className="font-bold text-lg capitalize mb-4">{difficulty}</h3>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Questions</span>
                  <span className="font-bold">{stats.total}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Correct</span>
                  <span className="font-bold text-green-600">{stats.correct}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Accuracy</span>
                  <span className="font-bold text-primary-600">{stats.accuracy.toFixed(1)}%</span>
                </div>

                <div className="w-full bg-white rounded-full h-3 overflow-hidden mt-3">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${
                      difficulty === 'beginner' ? 'bg-green-500' :
                      difficulty === 'intermediate' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${stats.accuracy}%` }}
                  ></div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Clock className="w-7 h-7 text-primary-600" />
          Recent Activity
        </h2>

        <div className="space-y-3">
          {analytics.recent_activity.map((activity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  activity.type === 'lesson' ? 'bg-blue-100' : 'bg-purple-100'
                }`}>
                  {activity.type === 'lesson' ? 
                    <BookOpen className="w-5 h-5 text-blue-600" /> : 
                    <Zap className="w-5 h-5 text-purple-600" />
                  }
                </div>
                <div>
                  <div className="font-semibold text-slate-800">
                    {activity.user} - {activity.type === 'lesson' ? 'Learned' : 'Reviewed'}
                  </div>
                  <div className="text-sm text-slate-600">
                    {activity.course} → {activity.topic} → {activity.subtopic}
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-500">
                {new Date(activity.timestamp).toLocaleString()}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* System Health */}
      <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200">
        <div className="flex items-center gap-4">
          <CheckCircle className="w-12 h-12 text-green-600" />
          <div>
            <h3 className="text-xl font-bold text-green-900 mb-1">System Healthy</h3>
            <p className="text-green-700">
              All {analytics.agents.length} AI agents are operational and performing optimally.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentMonitoring