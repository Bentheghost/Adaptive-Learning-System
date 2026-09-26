import React, { useState } from 'react'
import { Trophy, XCircle, BarChart, Sparkles, RotateCcw, CheckCircle, AlertCircle, Flag, ArrowRight, AlertTriangle } from 'lucide-react'
import { quizAPI } from '../../services/api'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

const Results = ({ results, quiz, onRetry, onReview }) => {
  const [showDetails, setShowDetails] = useState(false)
  const passed = results.passed
  const percentage = Math.round(results.score)

  const handleFlagQuestion = async (questionText) => {
    try {
      await quizAPI.flagQuestion({ question: questionText })
      toast.success('Question flagged for review by your instructor')
    } catch (err) {
      toast.error('Failed to flag question')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6"
    >
      {/* Results Header */}
      <div className={`card text-center relative overflow-hidden ${
        passed 
          ? 'bg-gradient-to-br from-green-500 to-emerald-600' 
          : 'bg-gradient-to-br from-orange-500 to-red-600'
      } text-white`}>
        
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>
        
        <div className="relative z-10">
          {/* Icon */}
          <div className="text-8xl mb-4">
            {passed ? '🎉' : '📚'}
          </div>

          {/* Title */}
          <h2 className="text-4xl font-bold mb-2">
            {passed ? 'Congratulations!' : 'Keep Learning!'}
          </h2>
          <p className="text-lg opacity-90 mb-6">
            {passed 
              ? 'You have successfully passed this quiz!' 
              : 'You need more practice. Review the material and try again.'}
          </p>

          {/* Score Circle */}
          <div className="inline-block">
            <div className={`w-48 h-48 rounded-full border-8 flex items-center justify-center mx-auto ${
              passed ? 'border-white bg-white/20' : 'border-white bg-white/20'
            }`}>
              <div className="text-center">
                <div className="text-6xl font-bold">{percentage}%</div>
                <div className="text-sm opacity-90">Your Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-blue-50 border-2 border-blue-200">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-1">{results.total}</div>
            <div className="text-sm text-blue-800 font-medium">Total Questions</div>
          </div>
        </div>

        <div className="card bg-green-50 border-2 border-green-200">
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-1">{results.correct}</div>
            <div className="text-sm text-green-800 font-medium">Correct Answers</div>
          </div>
        </div>

        <div className="card bg-red-50 border-2 border-red-200">
          <div className="text-center">
            <div className="text-4xl font-bold text-red-600 mb-1">{results.total - results.correct}</div>
            <div className="text-sm text-red-800 font-medium">Incorrect Answers</div>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="card bg-slate-50">
        <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
          <BarChart className="w-5 h-5" />
          Quiz Statistics
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex justify-between items-center p-3 bg-white rounded-lg">
            <span className="text-slate-600">Passing Score:</span>
            <span className="font-bold text-slate-800">{results.passing_score}%</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white rounded-lg">
            <span className="text-slate-600">Your Best Score:</span>
            <span className="font-bold text-green-600">{results.best_score}%</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white rounded-lg col-span-2">
            <span className="text-slate-600">Total Attempts:</span>
            <span className="font-bold text-slate-800">{results.quiz_attempts}</span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="card">
        <div className="mb-3">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-medium text-slate-700">Accuracy</span>
            <span className="font-bold text-slate-800">{percentage}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-4 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-4 rounded-full ${
                passed ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-orange-500 to-red-500'
              }`}
            />
          </div>
        </div>
      </div>

      {/* Detailed Breakdown Toggle */}
      <div className="card">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg hover:from-blue-100 hover:to-purple-100 transition-all"
        >
          <span className="font-semibold text-slate-800 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {showDetails ? 'Hide' : 'View'} Detailed Answer Breakdown
          </span>
          <span className="text-2xl">{showDetails ? '▲' : '▼'}</span>
        </button>

        {showDetails && quiz && quiz.questions && (
          <div className="mt-4 space-y-4">
            {quiz.questions.map((question, index) => {
              // Find user's answer from session storage or results
              const userAnswer = results.answers?.[index] || null
              const isCorrect = userAnswer === question.correct_answer
              
              return (
                <div 
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    isCorrect 
                      ? 'bg-green-50 border-green-300' 
                      : 'bg-red-50 border-red-300'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      isCorrect ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      {isCorrect ? (
                        <CheckCircle className="w-5 h-5 text-white" />
                      ) : (
                        <XCircle className="w-5 h-5 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800 mb-2">
                        Question {index + 1}: {question.question}
                      </p>
                      
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium text-slate-600">Your Answer: </span>
                          <span className={`font-semibold ${
                            isCorrect ? 'text-green-700' : 'text-red-700'
                          }`}>
                            {userAnswer || 'Not answered'}
                          </span>
                        </div>
                        
                        {!isCorrect && (
                          <div>
                            <span className="text-sm font-medium text-slate-600">Correct Answer: </span>
                            <span className="font-semibold text-green-700">
                              {question.correct_answer}
                            </span>
                          </div>
                        )}
                        
                        {question.explanation && (
                          <div className="mt-2 p-3 bg-white rounded border border-slate-200">
                            <span className="text-sm font-medium text-slate-600">Explanation: </span>
                            <p className="text-sm text-slate-700 mt-1">{question.explanation}</p>
                          </div>
                        )}
                        
                        {!isCorrect && question.misconception && (
                          <div className="mt-2 p-3 bg-orange-50 rounded border border-orange-200 flex items-start gap-2">
                            <AlertTriangle className="w-5 h-5 text-orange-500 flex-shrink-0" />
                            <div>
                              <span className="text-sm font-medium text-orange-800">Identified Misconception: </span>
                              <p className="text-sm text-orange-700 mt-1">{question.misconception}</p>
                            </div>
                          </div>
                        )}
                        
                        <div className="mt-2 text-right">
                           <button 
                             onClick={() => handleFlagQuestion(question.question)}
                             className="text-xs flex items-center gap-1 text-slate-400 hover:text-red-500 transition-colors ml-auto"
                           >
                             <Flag className="w-3 h-3" /> Flag Issue
                           </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Message */}
      <div className={`card ${
        passed ? 'bg-green-50 border-2 border-green-200' : 'bg-orange-50 border-2 border-orange-200'
      }`}>
        <div className="flex items-start gap-3">
          {passed ? (
            <Trophy className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
          ) : (
            <XCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
          )}
          <p className={`font-medium ${passed ? 'text-green-800' : 'text-orange-800'}`}>
            {results.message}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4">
        {!passed && onReview && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onReview}
            className="flex-1 btn-primary bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Get Adaptive Review
          </motion.button>
        )}
        
        {!passed && onRetry && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onRetry}
            className="flex-1 btn-secondary flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Retry Quiz
          </motion.button>
        )}

        {passed && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onRetry}
            className="flex-1 btn-primary flex items-center justify-center gap-2"
          >
            <Trophy className="w-5 h-5" />
            Quiz Completed!
          </motion.button>
        )}
      </div>
    </motion.div>
  )
}

export default Results