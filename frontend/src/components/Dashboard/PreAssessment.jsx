import React, { useState } from 'react'
import { CheckCircle, Brain, Target, Shield } from 'lucide-react'
import api from '../../services/api'
import toast from 'react-hot-toast'
import { useAuth } from '../../hooks/useAuth'

const PreAssessment = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState('intro')
  const [answers, setAnswers] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { checkAuth } = useAuth() // Assuming we might want to refresh user state

  const questions = [
    {
      id: 'q1',
      text: 'How comfortable are you with basic programming concepts like variables and loops?',
      options: [
        { value: 10, label: 'I have never programmed before' },
        { value: 30, label: 'I know what they are, but struggle to write them' },
        { value: 60, label: 'I can write simple programs using them' },
        { value: 100, label: 'I use them fluently in my projects' }
      ]
    },
    {
      id: 'q2',
      text: 'Have you worked with data structures like arrays or dictionaries?',
      options: [
        { value: 10, label: 'No, what are those?' },
        { value: 40, label: 'I have used arrays but not dictionaries' },
        { value: 70, label: 'I use both regularly' },
        { value: 100, label: 'I can implement custom data structures' }
      ]
    },
    {
      id: 'q3',
      text: 'How do you rate your problem-solving skills in coding?',
      options: [
        { value: 10, label: 'I need step-by-step guidance' },
        { value: 40, label: 'I can solve simple problems with help' },
        { value: 70, label: 'I can solve most problems independently' },
        { value: 100, label: 'I enjoy optimizing and refactoring complex logic' }
      ]
    }
  ]

  const handleSelect = (questionId, value) => {
    setAnswers({ ...answers, [questionId]: value })
  }

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      toast.error('Please answer all questions')
      return
    }

    setIsSubmitting(true)
    try {
      // Calculate average score from self-assessment
      const totalScore = Object.values(answers).reduce((sum, val) => sum + val, 0)
      const avgScore = totalScore / questions.length

      await api.post('/api/preassessment/submit', { score: avgScore })
      toast.success('Pre-assessment completed! Your learning path has been calibrated.')
      
      // Update user state if checkAuth exists on context, else reload window
      if (typeof checkAuth === 'function') {
         await checkAuth()
      } else {
         window.location.reload()
      }

      if (onComplete) onComplete()
    } catch (error) {
      console.error(error)
      toast.error('Failed to submit assessment')
      setIsSubmitting(false)
    }
  }

  if (currentStep === 'intro') {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="bg-white p-8 rounded-2xl shadow-lg border border-primary-100">
          <div className="w-20 h-20 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="w-10 h-10" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to AdaptiveLearn!</h2>
          <p className="text-gray-600 mb-8 text-lg">
            Before you start, let's take a quick 3-question diagnostic to initialize your personal Knowledge Tracing profile. This helps the AI tailor the difficulty exactly to your level.
          </p>
          <button
            onClick={() => setCurrentStep('quiz')}
            className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-8 rounded-full transition-colors flex items-center mx-auto"
          >
            Start Diagnostic <Target className="ml-2 w-5 h-5" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="bg-white p-8 rounded-2xl shadow-lg border border-primary-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Diagnostic Assessment</h2>
        <div className="space-y-8">
          {questions.map((q, i) => (
            <div key={q.id} className="bg-slate-50 p-6 rounded-xl border border-slate-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {i + 1}. {q.text}
              </h3>
              <div className="space-y-3">
                {q.options.map(opt => (
                  <label
                    key={opt.value}
                    className={`flex items-center p-4 rounded-lg cursor-pointer border transition-all ${
                      answers[q.id] === opt.value
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-slate-200 hover:border-primary-300 hover:bg-white'
                    }`}
                  >
                    <input
                      type="radio"
                      name={q.id}
                      value={opt.value}
                      checked={answers[q.id] === opt.value}
                      onChange={() => handleSelect(q.id, opt.value)}
                      className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-3 font-medium">{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || Object.keys(answers).length < questions.length}
            className="bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-8 rounded-xl transition-colors flex items-center disabled:opacity-50"
          >
            {isSubmitting ? (
              <span className="animate-pulse">Calibrating BKT Engine...</span>
            ) : (
              <>Complete Setup <CheckCircle className="ml-2 w-5 h-5" /></>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PreAssessment
