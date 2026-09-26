import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../../hooks/useAuth'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import { 
  Menu, 
  X,
  LogOut, 
  User, 
  Bell, 
  LayoutDashboard, 
  BookOpen, 
  TrendingUp,
  Activity,
  Flame,
  Star
} from 'lucide-react'

const Navbar = ({ onMenuClick }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/learn', label: 'Learn', icon: BookOpen },
    { path: '/progress', label: 'Progress', icon: TrendingUp },
    { path: '/agents', label: 'Agents', icon: Activity }
  ]

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
    if (onMenuClick) onMenuClick()
  }

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="glass-effect sticky top-0 z-40 border-b border-white/20"
    >
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Left section */}
          <div className="flex items-center gap-4">
            <button
              onClick={toggleMobileMenu}
              className="p-2 rounded-xl hover:bg-primary-50 transition-colors lg:hidden"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6 text-slate-700" />
              ) : (
                <Menu className="w-6 h-6 text-slate-700" />
              )}
            </button>
            
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">AL</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-bold gradient-text">
                  Adaptive Learning
                </h1>
                <p className="text-xs text-slate-500">AI-Powered Education</p>
              </div>
            </div>
          </div>

          {/* Center: Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive =
                location.pathname === link.path ||
                (link.path === '/learn' && location.pathname.startsWith('/learn')) ||
                (link.path === '/dashboard' && (location.pathname === '/' || location.pathname === '/dashboard'))

              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className="relative group"
                >
                  <motion.div
                    whileHover={{ y: -2 }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'text-primary-600 font-semibold'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <link.icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </motion.div>

                  {isActive && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-accent-500 rounded-t"
                      transition={{ duration: 0.3 }}
                    />
                  )}
                </Link>
              )
            })}
          </div>

          {/* Right section */}
          <div className="flex items-center gap-3">

            {/* Notifications */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative p-2 rounded-xl hover:bg-primary-50 transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5 text-slate-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-accent-500 rounded-full"></span>
            </motion.button>

            {/* Gamification Badges */}
            {user && user.role !== 'admin' && (
              <div className="hidden md:flex items-center gap-4 px-4 py-1 bg-slate-50 rounded-full border border-slate-200">
                <div className="flex items-center gap-1 text-orange-600 font-semibold" title="Day Streak">
                  <Flame className="w-4 h-4 fill-orange-500" />
                  <span>{user.current_streak || 0}</span>
                </div>
                <div className="flex items-center gap-1 text-yellow-600 font-semibold" title="Experience Points">
                  <Star className="w-4 h-4 fill-yellow-500" />
                  <span>{user.xp || 0} XP</span>
                </div>
              </div>
            )}

            {/* User Menu */}
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-semibold text-slate-700">
                  {user?.username}
                </p>
                <p className="text-xs text-slate-500 capitalize">{user?.role || 'Student'}</p>
              </div>

              <div className="relative group">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-100 to-accent-100 flex items-center justify-center font-semibold text-primary-700"
                  aria-label="User menu"
                >
                  {user?.username?.charAt(0).toUpperCase()}
                </motion.button>

                {/* Dropdown */}
                <div className="absolute right-0 mt-2 w-48 glass-effect rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="p-2">
                    {user && ['admin', 'lecturer', 'teacher'].includes(user.role) && (
                      <Link 
                        to="/admin/dashboard" 
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-primary-50 transition-colors text-left text-slate-700 text-sm"
                      >
                        <LayoutDashboard className="w-4 h-4 text-red-600" />
                        <span>Lecturer Portal</span>
                      </Link>
                    )}
                    <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-primary-50 transition-colors text-left text-slate-700">
                      <User className="w-4 h-4" />
                      <span className="text-sm">Profile</span>
                    </button>

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-red-50 text-red-600 transition-colors text-left text-sm"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

      {/* Mobile Navigation Dropdown Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-white/95 backdrop-blur-md border-b border-slate-200 px-4 pt-3 pb-6 space-y-2 shadow-2xl"
          >
            {navLinks.map((link) => {
              const isActive =
                location.pathname === link.path ||
                (link.path === '/learn' && location.pathname.startsWith('/learn')) ||
                (link.path === '/dashboard' && (location.pathname === '/' || location.pathname === '/dashboard'))

              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-500 to-accent-500 text-white shadow-md'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <link.icon className="w-5 h-5" />
                  <span className="text-base">{link.label}</span>
                </Link>
              )
            })}

            {user && user.role !== 'admin' && (
              <div className="flex items-center justify-around px-4 py-3 bg-slate-50 rounded-xl border border-slate-200 mt-3">
                <div className="flex items-center gap-1.5 text-orange-600 font-semibold text-sm">
                  <Flame className="w-4 h-4 fill-orange-500" />
                  <span>{user.current_streak || 0} Day Streak</span>
                </div>
                <div className="flex items-center gap-1.5 text-yellow-600 font-semibold text-sm">
                  <Star className="w-4 h-4 fill-yellow-500" />
                  <span>{user.xp || 0} XP</span>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}

export default Navbar