import React from 'react'

const Question = ({ question, questionNumber, selectedAnswer, onAnswer }) => {
  if (!question) {
    return (
      <div className="text-center py-8 bg-yellow-50 rounded-lg border-2 border-yellow-200">
        <p className="text-yellow-800 font-medium">Question data is missing</p>
      </div>
    )
  }

  // 🔥 HANDLE MULTIPLE OPTION FORMATS
  let options = []
  
  try {
    // Case 1: Already an array
    if (Array.isArray(question.options)) {
      options = question.options
    }
    // Case 2: JSON string array
    else if (typeof question.options === 'string') {
      const parsed = JSON.parse(question.options)
      if (Array.isArray(parsed)) {
        options = parsed
      } else if (typeof parsed === 'object') {
        // Convert object to array
        options = Object.values(parsed)
      }
    }
    // Case 3: Object like {"A": "...", "B": "...", "C": "...", "D": "..."}
    else if (typeof question.options === 'object' && question.options !== null) {
      options = Object.values(question.options)
    }
  } catch (e) {
    console.error('Failed to parse options:', e)
    options = []
  }

  // Filter out empty options
  options = options.filter(opt => opt && opt.trim() !== '')

  if (options.length === 0) {
    return (
      <div className="text-center py-8 bg-red-50 rounded-lg border-2 border-red-200">
        <p className="text-red-600 font-medium">⚠️ No valid options available for this question</p>
        <p className="text-sm text-red-500 mt-2">Please contact support or skip this question</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-start gap-3 mb-4">
          <span className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
            {questionNumber}
          </span>
          <h3 className="text-xl font-semibold text-gray-800 flex-1">
            {question.question}
          </h3>
        </div>
        
        {question.difficulty && (
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
            question.difficulty === 'beginner' || question.difficulty === 'easy' 
              ? 'bg-green-100 text-green-800' :
            question.difficulty === 'intermediate' || question.difficulty === 'medium' 
              ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {question.difficulty}
          </span>
        )}
      </div>

      <div className="space-y-3">
        {options.map((option, index) => (
          <button
            key={index}
            onClick={() => onAnswer(option)}
            className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
              selectedAnswer === option
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                selectedAnswer === option
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300'
              }`}>
                {selectedAnswer === option && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <span className="font-medium text-gray-700">{option}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default Question