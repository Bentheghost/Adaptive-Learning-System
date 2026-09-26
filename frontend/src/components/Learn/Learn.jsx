import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { courseAPI } from '../../services/api'
import Card from '../Common/Card'
import Loading from '../Common/Loading'
import toast from 'react-hot-toast'

const Learn = () => {
  const navigate = useNavigate()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCourses()
  }, [])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      const response = await courseAPI.getAll()
      setCourses(response.data)
    } catch (error) {
      console.error('Failed to load courses:', error)
      toast.error('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">📚 Learn</h1>
        <p className="text-gray-600">Choose a course to start your learning journey</p>
      </div>

      {courses.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📖</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Courses Available</h3>
          <p className="text-gray-500">Courses will appear here once they are added.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <Card 
              key={course.id}
              className="hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
              onClick={() => navigate(`/course/${course.id}`)}
            >
              <div className="p-6">
                {/* Difficulty Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    course.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                    course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {course.difficulty}
                  </span>
                  <div className="text-2xl">
                    {course.difficulty === 'beginner' ? '🌱' :
                     course.difficulty === 'intermediate' ? '🔥' : '⚡'}
                  </div>
                </div>

                {/* Course Info */}
                <h3 className="text-2xl font-bold text-gray-800 mb-3">{course.name}</h3>
                <p className="text-gray-600 mb-4 line-clamp-2">{course.description}</p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-blue-600 font-semibold">Topics</div>
                    <div className="text-2xl font-bold text-gray-800">{course.total_topics}</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-purple-600 font-semibold">Lessons</div>
                    <div className="text-2xl font-bold text-gray-800">{course.total_subtopics}</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-semibold text-gray-800">
                      {course.completion_percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${course.completion_percentage}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {course.completed_subtopics} / {course.total_subtopics} lessons completed
                  </div>
                </div>

                {/* Start Button */}
                <button className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold py-3 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 shadow-md hover:shadow-lg">
                  {course.completion_percentage > 0 ? 'Continue Learning →' : 'Start Course →'}
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default Learn