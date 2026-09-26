import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { BookOpen, Brain, Sparkles, CheckCircle, Lightbulb, Target } from 'lucide-react'
import { telemetryAPI } from '../../services/api'
import CodePlayground from './CodePlayground'

const LessonViewer = ({ lesson, subtopic, isReview, onStartQuiz }) => {
  const activeTimeRef = useRef(0)
  const lastActiveStartRef = useRef(Date.now())
  const maxScrollRef = useRef(0)
  const clickCountRef = useRef(0)

  useEffect(() => {
    lastActiveStartRef.current = Date.now()
    activeTimeRef.current = 0
    maxScrollRef.current = 0
    clickCountRef.current = 0

    const handleVisibilityChange = () => {
      if (document.hidden) {
        activeTimeRef.current += Date.now() - lastActiveStartRef.current
      } else {
        lastActiveStartRef.current = Date.now()
      }
    }

    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const scrollHeight = document.documentElement.scrollHeight
      const clientHeight = document.documentElement.clientHeight
      
      const scrollPercent = scrollHeight > clientHeight 
        ? Math.round((scrollTop / (scrollHeight - clientHeight)) * 100) 
        : 100
        
      if (scrollPercent > maxScrollRef.current) {
        maxScrollRef.current = scrollPercent
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    window.addEventListener("scroll", handleScroll)

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
      window.removeEventListener("scroll", handleScroll)

      if (!document.hidden) {
        activeTimeRef.current += Date.now() - lastActiveStartRef.current
      }

      const duration = Math.round(activeTimeRef.current / 1000)
      telemetryAPI.sendEvent({
        event_type: 'lesson_view',
        context: subtopic?.name || 'unknown',
        data: {
          duration_seconds: duration,
          click_count: clickCountRef.current,
          max_scroll_depth: maxScrollRef.current
        }
      }).catch(err => console.error("Telemetry error", err))
    }
  }, [subtopic])

  const handleContentClick = () => {
    clickCountRef.current += 1
  }

  const handleStartQuizClick = () => {
    // We optionally can also send an event here, or just let unmount handle the duration.
    // Let's let unmount handle it to avoid duplicate telemetry when component unmounts right after.
    if (onStartQuiz) onStartQuiz();
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Lesson Header */}
      <div className={`card ${isReview ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gradient-to-br from-primary-500 to-accent-600'} text-white relative overflow-hidden`}>
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center">
              {isReview ? <Sparkles className="w-7 h-7" /> : <BookOpen className="w-7 h-7" />}
            </div>
            <div>
              <div className="text-sm font-semibold opacity-90 mb-1">
                {isReview ? '📝 Adaptive Review Lesson' : '📚 Personalized Lesson'}
              </div>
              <h1 className="text-3xl font-bold">
                {subtopic.name}
              </h1>
            </div>
          </div>
          
          {isReview && (
            <div className="mt-4 flex items-start gap-3 bg-white/10 rounded-xl p-4">
              <Lightbulb className="w-6 h-6 flex-shrink-0 mt-1" />
              <div>
                <p className="text-white/95 font-medium">
                  This review is customized based on your quiz performance. Focus on the areas that need improvement!
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Lesson Content with Beautiful Styling */}
      <div className="card lesson-content" onClick={handleContentClick}>
        <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
      </div>

      {/* Code Playground for Practice */}
      <CodePlayground topicName={subtopic.name} />

      {/* Key Takeaways Section */}
      {!isReview && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200"
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-green-800 mb-2">Ready to Test Your Knowledge?</h3>
              <p className="text-green-700 mb-4">
                You've completed the lesson! Take the quiz to reinforce what you've learned and unlock the next subtopic.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Action Button */}
      {onStartQuiz && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex justify-center"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleStartQuizClick}
            className="btn-primary flex items-center gap-3 text-lg px-8 py-4 shadow-2xl"
          >
            <Brain className="w-6 h-6" />
            {isReview ? 'Retake Quiz' : 'Take Quiz Now'}
            <Target className="w-6 h-6" />
          </motion.button>
        </motion.div>
      )}

      {/* Learning Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card bg-blue-50 border-2 border-blue-200"
      >
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-bold text-blue-900 mb-2">💡 Study Tips</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Read through the content carefully</li>
              <li>• Try the code examples yourself</li>
              <li>• Take notes on key concepts</li>
              <li>• Practice makes perfect!</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default LessonViewer