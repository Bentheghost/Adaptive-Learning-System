import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { courseAPI, progressAPI } from '../../services/api'
import { useAuth } from '../../hooks/useAuth'
import { 
  BookOpen, 
  TrendingUp, 
  Zap, 
  ArrowRight,
  Sparkles,
  Trophy,
  Lock,
  CheckCircle
} from 'lucide-react'
import toast from 'react-hot-toast'
import PreAssessment from './PreAssessment'

const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [courses, setCourses] = useState([])
  const [progressSummary, setProgressSummary] = useState(null)
  const [nextSubtopic, setNextSubtopic] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Extract a safe fallback user ID from your useAuth context hooks
      const userId = user?.id || user?.user_id || user?.uid;
      
      const [coursesRes, progressRes] = await Promise.all([
        courseAPI.getAll(),
        progressAPI.getProgressSummary(userId) // ✅ Passed userId here!
      ])

      setCourses(coursesRes.data)
      setProgressSummary(progressRes.data)

      try {
        const nextRes = await progressAPI.getNextSubtopic(userId) // ✅ Passed userId here too!
        setNextSubtopic(nextRes.data)
      } catch (err) {
        // No next subtopic available
      }

    } catch (error) {
      toast.error('Failed to load dashboard data summaries')
    } finally {
      setLoading(false)
    }
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (user && user.role !== 'admin' && user.has_completed_preassessment === false) {
    return <PreAssessment />
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Welcome Header */}
      <motion.div variants={item} className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 p-8 text-white">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>
        
        <div className="relative z-10">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
          >
            <Sparkles className="w-12 h-12 mb-4" />
          </motion.div>
          
          <h1 className="text-4xl font-bold mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-primary-100 text-lg mb-6">
            Your AI-powered learning journey continues
          </p>

          {nextSubtopic && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate(`/course/${nextSubtopic.course_id}`)}
              className="bg-white text-primary-600 px-6 py-3 rounded-xl font-semibold shadow-xl hover:shadow-2xl transition-all flex items-center gap-2"
            >
              <Zap className="w-5 h-5" />
              Continue: {nextSubtopic.subtopic_name}
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          )}
        </div>
      </motion.div>

      {/* Progress Stats */}
      {progressSummary && (
        <motion.div variants={item}>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                  <BookOpen className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-800">{progressSummary.unlocked_subtopics}</div>
                  <div className="text-sm text-slate-600">Unlocked</div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-800">{progressSummary.completed_subtopics}</div>
                  <div className="text-sm text-slate-600">Completed</div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <Trophy className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-800">{progressSummary.average_score}%</div>
                  <div className="text-sm text-slate-600">Avg Score</div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-3xl font-bold text-slate-800">{progressSummary.completion_percentage}%</div>
                  <div className="text-sm text-slate-600">Overall</div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Courses */}
      <motion.div variants={item}>
        <h2 className="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
          <BookOpen className="w-7 h-7 text-primary-600" />
          Your Courses
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -8 }}
              onClick={() => navigate(`/course/${course.id}`)}
              className="card cursor-pointer group relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-primary-100 to-accent-100 rounded-full -mr-16 -mt-16 opacity-50 group-hover:scale-150 transition-transform duration-500"></div>

              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                    <BookOpen className="w-6 h-6 text-white" />
                  </div>

                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    course.difficulty === 'beginner' ? 'bg-green-100 text-green-700' :
                    course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {course.difficulty}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-slate-800 mb-2 group-hover:text-primary-600 transition-colors">
                  {course.name}
                </h3>

                <p className="text-sm text-slate-600 mb-4">
                  {course.description}
                </p>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-600">Progress</span>
                    <span className="font-semibold text-primary-600">
                      {course.completed_subtopics}/{course.total_subtopics}
                    </span>
                  </div>

                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500"
                      style={{ width: `${course.completion_percentage}%` }}
                    ></div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>{course.total_topics} topics</span>
                    <span>{course.completion_percentage}% complete</span>
                  </div>
                </div>

                <motion.div
                  className="mt-4 flex items-center gap-2 text-primary-600 font-semibold text-sm"
                  whileHover={{ gap: 8 }}
                >
                  Start Learning
                  <ArrowRight className="w-4 h-4" />
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default Dashboard