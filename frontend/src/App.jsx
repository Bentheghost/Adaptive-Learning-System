import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './hooks/useAuth'

// Layout Components
import Navbar from './components/Layout/Navbar'
import Footer from './components/Layout/Footer'

// Auth Components
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'

// Main Components
import Dashboard from './components/Dashboard/Dashboard'
import GlobalChatbot from './components/Common/GlobalChatbot'
import CourseView from './components/Learn/CourseView'
import Learn from './components/Learn/Learn'
import Progress from './components/Progress/Progress'
import AgentStatus from './components/Dashboard/AgentStatus'

// Admin Components
import AdminLogin from './components/Admin/AdminLogin'
import AdminDashboard from './components/Admin/AdminDashboard'

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

const AdminRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-600"></div>
      </div>
    )
  }
  
  return (user && ['admin', 'lecturer', 'teacher'].includes(user.role)) ? children : <Navigate to="/admin/login" />
}

const App = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false)

  return (
    <AuthProvider>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
          <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          
          <main className="flex-1 container mx-auto px-4 py-8">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              
              {/* Admin Routes */}
              <Route path="/admin/dashboard" element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              } />
              
              {/* Private Routes */}
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              
              <Route path="/learn" element={
                <PrivateRoute>
                  <Learn />
                </PrivateRoute>
              } />
              
              <Route path="/course/:courseId" element={
                <PrivateRoute>
                  <CourseView />
                </PrivateRoute>
              } />
              
              <Route path="/progress" element={
                <PrivateRoute>
                  <Progress />
                </PrivateRoute>
              } />

              <Route path="/agents" element={
                <PrivateRoute>
                  <AgentStatus />
                </PrivateRoute>
              } />
              
              {/* Default Routes */}
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
          </main>
          
          <Footer />
          <GlobalChatbot />
          
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#333',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App