import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import { courseAPI, learningAPI, quizAPI } from '../../services/api'
import { 
  BookOpen, 
  Lock, 
  CheckCircle, 
  PlayCircle, 
  Brain,
  ChevronDown,
  ChevronRight,
  Award,
  ArrowLeft,
  Sparkles,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'
import LessonViewer from './LessonViewer'
import Quiz from '../Quiz/Quiz'

// 🎯 NEW: Dynamic Button State and Curriculum Label Calculator Loop
const getCurriculumButtonConfig = (current_phase, has_learned, quiz_attempts) => {
  switch (current_phase) {
    case 1:
      return { lessonLabel: "Read Lesson 1", quizLabel: "Take Quiz 1", showQuizButton: false };
    case 2:
      return { lessonLabel: "Review Lesson 1", quizLabel: "Take Quiz 1", showQuizButton: true };
    case 3:
      return { lessonLabel: "Read Lesson 2", quizLabel: "Take Quiz 2", showQuizButton: false };
    case 4:
      return { lessonLabel: "Review Lesson 2", quizLabel: "Take Quiz 2", showQuizButton: true };
    case 5:
      return { lessonLabel: "Read Lesson 3", quizLabel: "Take Quiz 3", showQuizButton: false };
    case 6:
      return { lessonLabel: "Review Lesson 3", quizLabel: "Take Quiz 3", showQuizButton: true };
    default:
      // Fallback alignment for legacy records or completed structures
      return { 
        lessonLabel: has_learned ? 'Review Lesson 3' : 'Start Learning', 
        quizLabel: quiz_attempts > 0 ? 'Retake Quiz 3' : 'Take Quiz 3', 
        showQuizButton: has_learned 
      };
  }
};

const CourseView = () => {
  const { courseId } = useParams()
  const navigate = useNavigate()
  
  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedTopics, setExpandedTopics] = useState({})
  const [currentView, setCurrentView] = useState('overview') // 'overview', 'lesson', 'quiz'
  const [currentSubtopic, setCurrentSubtopic] = useState(null)
  const [lesson, setLesson] = useState(null)
  const [loadingLesson, setLoadingLesson] = useState(false)
  const [isReviewMode, setIsReviewMode] = useState(false)

  useEffect(() => {
    loadCourse()
  }, [courseId])

  const loadCourse = async () => {
    try {
      setLoading(true)
      const response = await courseAPI.getById(courseId)
      setCourse(response.data)
      
      const expanded = {}
      response.data.topics.forEach(topic => {
        expanded[topic.id] = true  // Expand all
      })
      setExpandedTopics(expanded)
      
    } catch (error) {
      toast.error('Failed to load course')
    } finally {
      setLoading(false)
    }
  }

  const toggleTopic = (topicId) => {
    setExpandedTopics(prev => ({
      ...prev,
      [topicId]: !prev[topicId]
    }))
  }

  const handleStartLesson = async (subtopic) => {
    if (!subtopic.is_unlocked) {
      toast.error('🔒 Complete previous subtopics to unlock this one')
      return
    }

    setCurrentSubtopic(subtopic)
    setCurrentView('lesson')
    loadingLesson || setLoadingLesson(true)
    setIsReviewMode(false)

    try {
      const response = await courseAPI.generateLesson(subtopic.id, false, 0)
      setLesson(response.data)
      toast.success('✨ Lesson generated!')
    } catch (error) {
      toast.error('Failed to generate lesson')
      setCurrentView('overview')
    } finally {
      setLoadingLesson(false)
    }
  }

  const handleStartQuiz = (subtopic) => {
    if (!subtopic.is_unlocked) {
      toast.error('🔒 This subtopic is locked')
      return
    }
    setCurrentSubtopic(subtopic)
    setCurrentView('quiz')
  }

  const handleQuizComplete = async (results) => {
    await loadCourse()
    
    if (results.passed) {
      toast.success('🎉 Phase complete! Moving to next curriculum stage.')
    } else {
      toast.error('Score fell below 70%. Review the lesson note tier and try again.')
    }
    setCurrentView('results') 
  }

  const handleReview = async (subtopic, previousScore) => {
    setCurrentSubtopic(subtopic)
    setCurrentView('lesson')
    setLoadingLesson(true)
    setIsReviewMode(true)

    try {
      const response = await courseAPI.generateLesson(subtopic.id, true, previousScore)
      setLesson(response.data)
      toast.success('📝 Review lesson generated based on your quiz performance!')
    } catch (error) {
      toast.error('Failed to generate review')
      setCurrentView('overview')
    } finally {
      setLoadingLesson(false)
    }
  }

  const handleBackToOverview = () => {
    setCurrentView('overview')
    setLesson(null)
    setCurrentSubtopic(null)
    loadCourse()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Loading course...</p>
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Course not found</h2>
        <button onClick={() => navigate('/dashboard')} className="btn-primary mt-4">
          Back to Dashboard
        </button>
      </div>
    )
  }

  // LESSON VIEW
  if (currentView === 'lesson') {
    return (
      <div className="space-y-6">
        <button
          onClick={handleBackToOverview}
          className="flex items-center gap-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Course
        </button>

        {loadingLesson ? (
          <div className="flex items-center justify-center min-h-[40vh]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
              <p className="text-slate-600 font-medium">
                Generating {isReviewMode ? 'adaptive review' : 'personalized lesson'}...
              </p>
            </div>
          </div>
        ) : lesson ? (
          <LessonViewer 
            lesson={lesson} 
            subtopic={currentSubtopic}
            isReview={isReviewMode}
            onStartQuiz={() => handleStartQuiz(currentSubtopic)}
          />
        ) : null}
      </div>
    )
  }

  // QUIZ VIEW
  if (currentView === 'quiz') {
    return (
      <div className="space-y-6">
        <button
          onClick={handleBackToOverview}
          className="flex items-center gap-2 text-slate-600 hover:text-primary-600 transition-colors font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Course
        </button>

        <Quiz 
          subtopic={currentSubtopic}
          onComplete={handleQuizComplete}
          onReview={handleReview}
        />
      </div>
    )
  }

  // OVERVIEW (Default View)
  return (
    <div className="space-y-6">
      {/* Course Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-gradient-to-br from-primary-500 to-accent-600 text-white"
      >
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-white/80 hover:text-white transition-colors mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Dashboard
        </button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center">
                <BookOpen className="w-7 h-7" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">{course.name}</h1>
                <p className="text-primary-100">{course.description}</p>
              </div>
            </div>
          </div>

          <span className={`px-4 py-2 rounded-xl text-sm font-semibold ${
            course.difficulty === 'beginner' ? 'bg-green-500' :
            course.difficulty === 'intermediate' ? 'bg-yellow-500' :
            'bg-red-500'
          }`}>
            {course.difficulty}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold">Course Progress</span>
            <span className="text-sm font-semibold">
              {course.topics.reduce((sum, t) => sum + t.subtopics.filter(s => s.is_completed).length, 0)}/
              {course.topics.reduce((sum, t) => sum + t.subtopics.length, 0)} subtopics
            </span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ 
                width: `${(course.topics.reduce((sum, t) => sum + t.subtopics.filter(s => s.is_completed).length, 0) / 
                         course.topics.reduce((sum, t) => sum + t.subtopics.length, 0) * 100)}%` 
              }}
              className="h-full bg-white rounded-full"
            />
          </div>
        </div>
      </motion.div>

      {/* Topics and Subtopics */}
      <div className="space-y-4">
        {course.topics.map((topic, topicIndex) => (
          <motion.div
            key={topic.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: topicIndex * 0.1 }}
            className="card"
          >
            {/* Topic Header */}
            <div
              onClick={() => toggleTopic(topic.id)}
              className="flex items-center justify-between cursor-pointer group"
            >
              <div className="flex items-center gap-3">
                {expandedTopics[topic.id] ? (
                  <ChevronDown className="w-5 h-5 text-primary-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-slate-400" />
                )}
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">{topicIndex + 1}</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-800 group-hover:text-primary-600 transition-colors">
                    {topic.name}
                  </h3>
                  <p className="text-sm text-slate-600">{topic.description}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-sm font-semibold text-slate-700">
                    {topic.subtopics.filter(s => s.is_completed).length}/{topic.subtopics.length}
                  </div>
                  <div className="text-xs text-slate-500">completed</div>
                </div>
                {topic.subtopics.filter(s => s.is_completed).length === topic.subtopics.length && (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                )}
              </div>
            </div>

            {/* Subtopics */}
            <AnimatePresence>
              {expandedTopics[topic.id] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 space-y-2 ml-8"
                >
                  {topic.subtopics.map((subtopic, subIndex) => {
                    // Compute active dynamic labels based on the subtopic phase
                    const { lessonLabel, quizLabel, showQuizButton } = getCurriculumButtonConfig(
                      subtopic.current_phase || 1,
                      subtopic.has_learned,
                      subtopic.quiz_attempts
                    );

                    return (
                      <div
                        key={subtopic.id}
                        className={`p-4 rounded-xl border-2 transition-all ${
                          subtopic.is_completed
                            ? 'border-green-200 bg-green-50'
                            : subtopic.is_unlocked
                            ? 'border-primary-200 bg-primary-50 hover:border-primary-400'
                            : 'border-slate-200 bg-slate-50 opacity-60'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3 flex-1">
                            {subtopic.is_completed ? (
                              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                            ) : subtopic.is_unlocked ? (
                              <PlayCircle className="w-5 h-5 text-primary-600 flex-shrink-0" />
                            ) : (
                              <Lock className="w-5 h-5 text-slate-400 flex-shrink-0" />
                            )}

                            <div className="flex-1">
                              <h4 className="font-semibold text-slate-800">
                                {topicIndex + 1}.{subIndex + 1} {subtopic.name}
                              </h4>
                              <p className="text-sm text-slate-600">{subtopic.description}</p>
                              
                              {subtopic.best_score > 0 && (
                                <div className="flex items-center gap-2 mt-1">
                                  <Award className="w-4 h-4 text-yellow-600" />
                                  <span className="text-xs text-slate-600">
                                    Best Score: <span className="font-semibold">{subtopic.best_score}%</span>
                                  </span>
                                  {subtopic.quiz_attempts > 0 && (
                                    <span className="text-xs text-slate-500">
                                      • {subtopic.quiz_attempts} attempt{subtopic.quiz_attempts > 1 ? 's' : ''}
                                    </span>
                                  )}
                                </div>
                              )}

                              {/* 🧠 BKT Mastery Probability Gauge */}
                              {subtopic.knowledge_level !== undefined && subtopic.knowledge_level !== null && subtopic.knowledge_level > 0 && (
                                <div className="mt-3 pt-2 border-t border-slate-100 max-w-xs">
                                  <div className="flex items-center justify-between text-xs font-semibold text-purple-700 mb-1">
                                    <span className="flex items-center gap-1">
                                      <Brain className="w-3.5 h-3.5 text-purple-600" /> 
                                      AI Mastery Estimate
                                    </span>
                                    <span>{Math.round(subtopic.knowledge_level * 100)}%</span>
                                  </div>
                                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                                    <motion.div 
                                      initial={{ width: 0 }}
                                      animate={{ width: `${subtopic.knowledge_level * 100}%` }}
                                      transition={{ duration: 0.8, ease: "easeOut" }}
                                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full"
                                    />
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex items-center gap-2 ml-4">
                            {subtopic.is_unlocked && (
                              <>
                                {/* Dynamic Lesson Button */}
                                <motion.button
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                  onClick={() => handleStartLesson(subtopic)}
                                  className="btn-secondary flex items-center gap-2 text-sm"
                                >
                                  <BookOpen className="w-4 h-4" />
                                  {lessonLabel}
                                </motion.button>

                                {/* Dynamic Quiz Button */}
                                {showQuizButton && (
                                  <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => handleStartQuiz(subtopic)}
                                    className="btn-primary flex items-center gap-2 text-sm"
                                  >
                                    <Brain className="w-4 h-4" />
                                    {quizLabel}
                                  </motion.button>
                                )}

                                {/* Adaptive Review Button (if failed quiz) */}
                                {subtopic.quiz_attempts > 0 && !subtopic.is_completed && subtopic.best_score > 0 && (
                                  <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => handleReview(subtopic, subtopic.best_score)}
                                    className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2"
                                  >
                                    <Sparkles className="w-4 h-4" />
                                    Adaptive Review
                                  </motion.button>
                                )}
                              </>
                            )}

                            {!subtopic.is_unlocked && (
                              <span className="text-xs text-slate-500 italic">
                                Complete previous subtopics
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      {/* No Content Message */}
      {course.topics.length === 0 && (
        <div className="card text-center py-12">
          <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-2">No topics yet</h3>
          <p className="text-slate-600">Topics will be added soon!</p>
        </div>
      )}
    </div>
  )
}

export default CourseView