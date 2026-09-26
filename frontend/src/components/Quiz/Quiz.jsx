import React, { useState, useEffect, useRef } from 'react'
import { quizAPI, telemetryAPI } from '../../services/api'
import Question from './Question'
import Results from './Results'
import Loading from '../Common/Loading'
import toast from 'react-hot-toast'
import { Brain, CheckCircle, AlertCircle } from 'lucide-react'

const Quiz = ({ subtopic, onComplete, onReview }) => {
  const [quiz, setQuiz] = useState(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [results, setResults] = useState(null)
  const [answerTimes, setAnswerTimes] = useState({})
  const fetchedSubtopicId = useRef(null)
  const questionStartTimeRef = useRef(Date.now())

  useEffect(() => {
    questionStartTimeRef.current = Date.now()
  }, [currentQuestionIndex])

  useEffect(() => {
    if (!subtopic) {
      toast.error('No subtopic selected')
      return
    }
    // Prevent double-fetching in React StrictMode
    if (fetchedSubtopicId.current === subtopic.id) {
      return
    }
    fetchedSubtopicId.current = subtopic.id
    generateQuiz()
  }, [subtopic])

  const generateQuiz = async () => {
    try {
      setLoading(true)
      const response = await quizAPI.generateQuiz(subtopic.id)
      setQuiz(response.data)
      toast.success('Quiz loaded!')
    } catch (error) {
      console.error('Failed to generate quiz:', error)
      toast.error('Failed to load quiz')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = (questionIndex, answer) => {
    if (!answers[questionIndex]) {
      const timeTakenMs = Date.now() - questionStartTimeRef.current
      setAnswerTimes(prev => ({
        ...prev,
        [questionIndex]: timeTakenMs
      }))
    }
    
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }))
  }

  const handleNext = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleSubmit = async () => {
    // Check if all questions are answered
    const unanswered = quiz.questions.filter((_, idx) => !answers[idx])
    if (unanswered.length > 0) {
      toast.error(`Please answer all questions (${unanswered.length} remaining)`)
      return
    }

    try {
      setSubmitting(true)
      
      // 1. Format answers cleanly for the backend payload
      const formattedAnswers = quiz.questions.map((q, idx) => ({
        question: q.question,
        user_answer: answers[idx],
        correct_answer: q.correct_answer,
        difficulty: q.difficulty || 'intermediate'
      }))

      // 2. Fire the network request and capture 'response' in the main scope
      const response = await quizAPI.submitQuiz({
        subtopic_id: subtopic.id,
        session_id: quiz.session_id,
        answers: formattedAnswers
      });

      telemetryAPI.sendEvent({
        event_type: 'quiz_completed',
        context: subtopic?.name || 'unknown',
        data: {
          session_id: quiz.session_id,
          answer_times: answerTimes
        }
      }).catch(err => console.error("Telemetry error", err))

      // 3. Combine the response data with the local answers array
      const resultsWithAnswers = {
        ...response.data,
        answers: Object.values(answers)
      }

      setResults(resultsWithAnswers)
      
      // 4. Trigger the correct destructured prop callback handler
      if (typeof onComplete === 'function') {
        onComplete(resultsWithAnswers)
      } else {
        console.warn("Quiz submitted successfully, but onComplete callback handler prop was missing.")
      }
      
    } catch (error) {
      console.error('Failed to submit quiz:', error)
      toast.error(error.response?.data?.error || 'Failed to submit quiz')
    } finally {
      setSubmitting(false)
    }
  }
  const handleRetry = () => {
    setResults(null)
    setAnswers({})
    setAnswerTimes({})
    setCurrentQuestionIndex(0)
    // Clear the ref so we can fetch again
    fetchedSubtopicId.current = null
    // The useEffect will catch the change since subtopic hasn't changed, wait no it won't.
    // Actually, we just need to manually call generateQuiz() and update the ref to prevent useEffect from doing it later.
    fetchedSubtopicId.current = subtopic.id
    generateQuiz()
  }

  const handleReviewLesson = () => {
    if (onReview && results) {
      onReview(subtopic, results.score)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Generating quiz...</p>
        </div>
      </div>
    )
  }

  if (results) {
    return <Results 
      results={results} 
      quiz={quiz} 
      onRetry={handleRetry}
      onReview={handleReviewLesson}
    />
  }

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="card text-center py-12">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-4">No Questions Available</h2>
        <p className="text-slate-600 mb-6">Unable to generate quiz for this topic.</p>
      </div>
    )
  }

  const currentQuestion = quiz.questions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100
  const answeredCount = Object.keys(answers).length

  return (
    <div className="space-y-6">
      {/* Quiz Header */}
      <div className="card bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{quiz.subtopic_name}</h1>
                <p className="text-purple-100 text-sm">
                  {quiz.topic_name} • {quiz.course_name}
                </p>
              </div>
            </div>
          </div>
          <div className="text-right bg-white/10 rounded-xl px-4 py-2">
            <div className="text-sm opacity-90">Question</div>
            <div className="text-3xl font-bold">
              {currentQuestionIndex + 1}<span className="text-lg">/{quiz.questions.length}</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-white h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-sm">
            <span>Progress: {Math.round(progress)}%</span>
            <span>Answered: {answeredCount}/{quiz.questions.length}</span>
          </div>
        </div>

        {/* Passing Score Badge */}
        <div className="mt-4 inline-flex items-center gap-2 bg-white/20 rounded-lg px-4 py-2">
          <CheckCircle className="w-5 h-5" />
          <span className="font-semibold">Passing Score: {quiz.passing_score}%</span>
        </div>
      </div>

      {/* Question Card */}
      <div className="card bg-white shadow-xl">
        <Question
          question={currentQuestion}
          questionNumber={currentQuestionIndex + 1}
          selectedAnswer={answers[currentQuestionIndex]}
          onAnswer={(answer) => handleAnswer(currentQuestionIndex, answer)}
        />
      </div>

      {/* Navigation */}
      <div className="card bg-slate-50">
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="px-6 py-3 bg-slate-300 text-slate-700 rounded-lg hover:bg-slate-400 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-all"
          >
            ← Previous
          </button>

          <div className="text-center">
            {answeredCount < quiz.questions.length ? (
              <div className="flex items-center gap-2 text-orange-600 font-medium">
                <AlertCircle className="w-5 h-5" />
                <span>{quiz.questions.length - answeredCount} question(s) remaining</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-green-600 font-medium">
                <CheckCircle className="w-5 h-5" />
                <span>All questions answered!</span>
              </div>
            )}
          </div>

          {currentQuestionIndex === quiz.questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={submitting || answeredCount < quiz.questions.length}
              className="px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg transition-all flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Submit Quiz
                </>
              )}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 font-semibold transition-all"
            >
              Next →
            </button>
          )}
        </div>
      </div>

      {/* Question Navigator */}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-600 mb-3">Question Navigator</h3>
        <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
          {quiz.questions.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentQuestionIndex(idx)}
              className={`w-10 h-10 rounded-lg font-semibold transition-all ${
                idx === currentQuestionIndex
                  ? 'bg-primary-500 text-white shadow-lg scale-110'
                  : answers[idx]
                  ? 'bg-green-100 text-green-700 border-2 border-green-300'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Quiz