import React, { useState, useEffect } from 'react'
import { progressAPI, courseAPI } from '../../services/api'
import Loading from '../Common/Loading'
import Card from '../Common/Card'
import toast from 'react-hot-toast'
import SkillTree from './SkillTree'

const Progress = () => {
  const [progressData, setProgressData] = useState(null)
  const [courseDetails, setCourseDetails] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProgress()
  }, [])

  const fetchProgress = async () => {
    try {
      setLoading(true)
      const [summaryRes, coursesRes] = await Promise.all([
        progressAPI.getProgressSummary(),
        courseAPI.getAll()
      ])
      setProgressData(summaryRes.data)
      
      if (coursesRes.data && coursesRes.data.length > 0) {
        // Fetch the first course's detailed skill tree data
        const courseId = coursesRes.data[0].id
        const detailRes = await courseAPI.getById(courseId)
        setCourseDetails(detailRes.data)
      }
    } catch (error) {
      console.error('Failed to load progress:', error)
      toast.error('Failed to load progress data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading />

  if (!progressData) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Progress Data</h3>
        <p className="text-gray-500">Start learning to see your progress</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">📊 Your Progress</h1>
        <p className="text-gray-600">Track your learning journey</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="p-6 text-center">
            <div className="text-5xl font-bold mb-2">{progressData.completion_percentage}%</div>
            <div className="text-blue-100">Overall Completion</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="p-6 text-center">
            <div className="text-5xl font-bold mb-2">{progressData.completed_subtopics}</div>
            <div className="text-green-100">Lessons Completed</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="p-6 text-center">
            <div className="text-5xl font-bold mb-2">{progressData.average_score}%</div>
            <div className="text-purple-100">Average Score</div>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="p-6 text-center">
            <div className="text-5xl font-bold mb-2">{Math.round(progressData.average_knowledge * 100)}%</div>
            <div className="text-orange-100">Knowledge Level</div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Skill Tree Area */}
        <div className="lg:col-span-2">
          {courseDetails ? (
            <SkillTree course={courseDetails} />
          ) : (
            <Card>
              <div className="p-12 text-center text-gray-500">
                Loading your learning path...
              </div>
            </Card>
          )}
        </div>

        {/* Progress Details Side Panel */}
        <div className="lg:col-span-1">
          <Card>
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Learning Statistics</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Total Lessons Available</span>
                  <span className="text-2xl font-bold text-gray-800">{progressData.total_subtopics}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Unlocked Lessons</span>
                  <span className="text-2xl font-bold text-blue-600">{progressData.unlocked_subtopics}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Completed Lessons</span>
                  <span className="text-2xl font-bold text-green-600">{progressData.completed_subtopics}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Progress