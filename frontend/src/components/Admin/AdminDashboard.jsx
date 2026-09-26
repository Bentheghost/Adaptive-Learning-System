import React, { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import { Users, BookOpen, Target, TrendingUp, AlertCircle, Flag, BarChart2, CheckCircle, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const AdminDashboard = () => {
  const [students, setStudents] = useState([])
  const [flaggedQuestions, setFlaggedQuestions] = useState([])
  const [telemetry, setTelemetry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('students') // 'students', 'flagged', 'telemetry'

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [studentRes, flaggedRes, telemetryRes] = await Promise.all([
        adminAPI.getStudents(),
        adminAPI.getFlaggedQuestions(),
        adminAPI.getTelemetry()
      ])
      setStudents(studentRes.data)
      setFlaggedQuestions(flaggedRes.data)
      setTelemetry(telemetryRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleExportCSV = async () => {
    try {
      const response = await adminAPI.exportStudents()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'student_progress_report.csv')
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      toast.success('Export downloaded successfully')
    } catch (error) {
      console.error('Failed to export CSV:', error)
      toast.error('Failed to export CSV')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-red-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Lecturer Dashboard</h1>
          <p className="text-gray-500 mt-1">Monitor your students' learning progress</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={handleExportCSV}
            className="flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors shadow-sm font-medium"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
          <div className="bg-red-50 px-4 py-2 rounded-lg border border-red-100 flex items-center gap-4">
            <div className="flex items-center">
              <Users className="w-5 h-5 text-red-600 mr-2" />
              <span className="font-semibold text-red-700">{students.length} Total Students</span>
            </div>
            <div className="flex items-center pl-4 border-l border-red-200">
               <Flag className="w-5 h-5 text-orange-600 mr-2" />
               <span className="font-semibold text-orange-700">{flaggedQuestions.length} Flagged Issues</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('students')}
          className={`py-3 px-6 font-semibold transition-colors border-b-2 ${
            activeTab === 'students' 
              ? 'border-red-500 text-red-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Student Progress Overview
          </div>
        </button>
        <button
          onClick={() => setActiveTab('flagged')}
          className={`py-3 px-6 font-semibold transition-colors border-b-2 ${
            activeTab === 'flagged' 
              ? 'border-orange-500 text-orange-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <Flag className="w-4 h-4" />
            Flagged Questions
            {flaggedQuestions.length > 0 && (
              <span className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded-full">
                {flaggedQuestions.length}
              </span>
            )}
          </div>
        </button>
        <button
          onClick={() => setActiveTab('telemetry')}
          className={`py-3 px-6 font-semibold transition-colors border-b-2 ${
            activeTab === 'telemetry' 
              ? 'border-purple-500 text-purple-600' 
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4" />
            Telemetry Analytics
          </div>
        </button>
      </div>

      {activeTab === 'students' && (
        <>
          {/* Chart Section */}
          {students.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-blue-500" />
                Class Knowledge Distribution (BKT)
              </h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={students.map(s => ({ name: s.username, knowledge: Math.round(s.avg_knowledge * 100) }))}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} label={{ value: 'Avg Knowledge (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="knowledge" stroke="#3b82f6" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {students.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex flex-col items-center justify-center text-center">
          <AlertCircle className="w-16 h-16 text-gray-300 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900">No students found</h3>
          <p className="text-gray-500 mt-2">There are currently no students registered in the system.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <div key={student.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900">{student.username}</h3>
                  <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full">
                    Joined {student.joined}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center text-sm">
                    <BookOpen className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">Subtopics:</span>
                    <span className="ml-auto font-semibold">
                      {student.completed_subtopics} / {student.unlocked_subtopics} completed
                    </span>
                  </div>
                  
                  <div className="flex items-center text-sm">
                    <Target className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">Avg Score:</span>
                    <span className="ml-auto font-semibold">{student.avg_score}%</span>
                  </div>
                  
                  <div className="flex items-center text-sm">
                    <TrendingUp className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">Est. Knowledge:</span>
                    <span className="ml-auto font-semibold">
                      {Math.round(student.avg_knowledge * 100)}%
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-6 py-4">
                <div className="text-sm">
                  <span className="text-gray-500 block mb-1">Recent Activity:</span>
                  <span className="font-medium text-gray-900 truncate block">
                    {student.recent_activity}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      </>
      )}

      {activeTab === 'flagged' && (
        <div className="space-y-4">
          {flaggedQuestions.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex flex-col items-center justify-center text-center">
              <CheckCircle className="w-16 h-16 text-green-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900">No Flagged Questions</h3>
              <p className="text-gray-500 mt-2">All good! Students haven't reported any hallucinations or bad questions.</p>
            </div>
          ) : (
            flaggedQuestions.map((fq) => (
              <div key={fq.id} className="bg-white rounded-xl shadow-sm border-l-4 border-l-orange-500 border border-gray-200 p-6">
                <div className="flex justify-between items-start mb-4">
                   <h4 className="text-lg font-bold text-gray-800 flex-1">{fq.question}</h4>
                   <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">Reported by: {fq.username} • {fq.date}</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm bg-gray-50 p-4 rounded-lg">
                  <div>
                    <span className="font-semibold text-gray-700 block mb-1">Student's Answer:</span>
                    <span className="text-red-600 font-medium">{fq.user_answer}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700 block mb-1">System's Correct Answer:</span>
                    <span className="text-green-600 font-medium">{fq.correct_answer}</span>
                  </div>
                </div>

                {fq.misconception && (
                  <div className="mt-4 flex items-start gap-2 text-orange-700 bg-orange-50 p-3 rounded-lg border border-orange-100">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <div>
                       <span className="font-semibold block text-sm">System's Misconception Diagnosis:</span>
                       <span className="text-sm">{fq.misconception}</span>
                    </div>
                  </div>
                )}
                
                <div className="mt-4 flex justify-end gap-2">
                  <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 font-medium">Edit Question</button>
                  <button className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg text-sm hover:bg-orange-200 font-medium">Dismiss Flag</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'telemetry' && telemetry && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-2">Average Active Lesson View</h3>
              <p className="text-3xl font-extrabold text-blue-600">{telemetry.avg_lesson_time} <span className="text-xl text-gray-500 font-medium">seconds</span></p>
              <p className="text-sm text-gray-500 mt-2">Active time spent by students reading a single lesson.</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-2">Total Code Attempts</h3>
              <p className="text-3xl font-extrabold text-green-600">{telemetry.total_code_attempts}</p>
              <p className="text-sm text-gray-500 mt-2">Number of times code was executed in the playground.</p>
            </div>
          </div>

          {telemetry.error_distribution && telemetry.error_distribution.length > 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-500" />
                Code Error Distribution
              </h3>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={telemetry.error_distribution}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex flex-col items-center justify-center text-center">
              <CheckCircle className="w-16 h-16 text-green-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900">No Code Errors Logged</h3>
              <p className="text-gray-500 mt-2">There is not enough telemetry data yet to show error distributions.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AdminDashboard
