import React, { createContext, useState, useEffect, useContext } from 'react'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

// 1. Keep the raw Context internal to this file (Remove "export")
const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await authAPI.getCurrentUser()
      setUser(response.data)
      if (response.data?.user_id) {
        localStorage.setItem('user_id', response.data.user_id)
      }
    } catch (error) {
      setUser(null)
      localStorage.removeItem('user_id')
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      setUser(response.data)
      if (response.data?.user_id) {
        localStorage.setItem('user_id', response.data.user_id)
      }
      toast.success('Welcome back!')
      return response.data
    } catch (error) {
      throw error
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      if (response.data.requires_verification) {
        toast.success('Registration successful. Please verify your email.')
        return response.data
      }
      setUser(response.data)
      if (response.data?.user_id) {
        localStorage.setItem('user_id', response.data.user_id)
      }
      toast.success('Account created successfully!')
      return response.data
    } catch (error) {
      throw error
    }
  }

  const verifyOTP = async (data) => {
    try {
      const response = await authAPI.verifyOTP(data)
      setUser(response.data)
      if (response.data?.user_id) {
        localStorage.setItem('user_id', response.data.user_id)
      }
      toast.success('Email verified successfully!')
      return response.data
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
      setUser(null)
      localStorage.removeItem('user_id')
      toast.success('Logged out successfully')
    } catch (error) {
      console.error('Logout error:', error)
      localStorage.removeItem('user_id')
    }
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, verifyOTP, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

// 2. Export a clean custom hook for consumers instead of exporting the raw context
export const useAuthContext = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context;
}