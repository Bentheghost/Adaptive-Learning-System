import React from 'react'
import { NavLink } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  LayoutDashboard, 
  BookOpen, 
  Brain, 
  TrendingUp, 
  Sparkles 
} from 'lucide-react'

const Sidebar = () => {
  const navItems = [
    { 
      path: '/', 
      icon: LayoutDashboard, 
      label: 'Dashboard',
      gradient: 'from-blue-500 to-cyan-500'
    },
    { 
      path: '/learn', 
      icon: BookOpen, 
      label: 'Learn',
      gradient: 'from-purple-500 to-pink-500'
    },
    { 
      path: '/quiz', 
      icon: Brain, 
      label: 'Quiz',
      gradient: 'from-green-500 to-emerald-500'
    },
    { 
      path: '/progress', 
      icon: TrendingUp, 
      label: 'Progress',
      gradient: 'from-orange-500 to-red-500'
    },
  ]

  return (
    <motion.aside
      className="h-screen w-64 bg-white border-r border-slate-100 flex flex-col shadow-lg"
    >
      {/* Logo - Compact */}
      <div className="p-4 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center shadow-md flex-shrink-0">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-base gradient-text">
              AdaptiveLearn
            </h2>
            <p className="text-xs text-slate-500">AI System</p>
          </div>
        </div>
      </div>

      {/* Navigation - Better spacing */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 group text-sm font-medium ${
                isActive
                  ? 'bg-gradient-to-r from-primary-500 to-accent-500 text-white shadow-md'
                  : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            {({ isActive }) => (
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-3 w-full"
              >
                <div className={`p-1.5 rounded-lg ${isActive ? 'bg-white/20' : `bg-gradient-to-br ${item.gradient}`}`}>
                  <item.icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-white'}`} />
                </div>
                <span>{item.label}</span>
              </motion.div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* AI Agent Status - Compact */}
      <div className="p-3 border-t border-slate-100 bg-slate-50">
        <div className="bg-gradient-to-r from-primary-500/10 to-accent-500/10 rounded-lg p-3 border border-primary-200/20">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs font-semibold text-slate-700">
              Agents Active
            </span>
          </div>
          <p className="text-xs text-slate-500">
            5 AI monitoring
          </p>
        </div>
      </div>
    </motion.aside>
  )
}

export default Sidebar