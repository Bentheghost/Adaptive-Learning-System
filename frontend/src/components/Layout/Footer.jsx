import React from 'react'
import { motion } from 'framer-motion'
import { 
  Github, 
  Linkedin, 
  Mail, 
  Heart, 
  Sparkles,
  BookOpen,
  Brain,
  Code,
  Twitter
} from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    product: [
      { name: 'Features', href: '#features' },
      { name: 'AI Agents', href: '#agents' },
      { name: 'Pricing', href: '#pricing' },
      { name: 'Roadmap', href: '#roadmap' }
    ],
    resources: [
      { name: 'Documentation', href: '#docs' },
      { name: 'API Reference', href: '#api' },
      { name: 'Tutorials', href: '#tutorials' },
      { name: 'Blog', href: '#blog' }
    ],
    company: [
      { name: 'About Us', href: '#about' },
      { name: 'Careers', href: '#careers' },
      { name: 'Contact', href: '#contact' },
      { name: 'Privacy Policy', href: '#privacy' },
      { name: 'Lecturer Portal', href: '/admin/login' }
    ]
  }

  const socialLinks = [
    { icon: Github, href: 'https://github.com', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com', label: 'LinkedIn' },
    { icon: Twitter, href: 'https://twitter.com', label: 'Twitter' },
    { icon: Mail, href: 'mailto:contact@adaptivelearn.com', label: 'Email' }
  ]

  const features = [
    { icon: Brain, text: 'AI-Powered Learning' },
    { icon: BookOpen, text: 'Adaptive Content' },
    { icon: Code, text: 'Interactive Coding' },
    { icon: Sparkles, text: 'Multi-Agent System' }
  ]

  return (
    <footer className="bg-slate-900 text-white border-t border-slate-800 mt-auto">
      {/* Main Footer Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Section */}
        <div className="py-6 grid grid-cols-2 md:grid-cols-5 gap-6">
          {/* Brand - Left Column */}
          <div className="col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="space-y-2"
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-lg font-bold">AdaptiveLearn</h3>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                Revolutionizing education with AI-powered adaptive learning.
              </p>
            </motion.div>
          </div>

          {/* Links Columns - 3 columns */}
          {Object.entries(footerLinks).map(([category, links], categoryIndex) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: categoryIndex * 0.05 }}
            >
              <h4 className="text-sm font-bold mb-2 capitalize text-slate-100">
                {category}
              </h4>
              <ul className="space-y-1.5">
                {links.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link.href}
                      className="text-xs text-slate-400 hover:text-primary-400 transition-colors inline-flex items-center gap-1 group"
                    >
                      <span className="group-hover:translate-x-0.5 transition-transform">
                        {link.name}
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-slate-800"></div>

        {/* Bottom Section */}
        <div className="py-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div>
            © {currentYear} AdaptiveLearn • Made with <Heart className="w-3 h-3 text-red-500 fill-red-500 inline mx-0.5 animate-pulse" /> by Your Team
          </div>
          <div className="flex items-center gap-4">
            <a href="#privacy" className="hover:text-primary-400 transition-colors">Privacy</a>
            <a href="#terms" className="hover:text-primary-400 transition-colors">Terms</a>
            <div className="flex items-center gap-1.5">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-6 h-6 bg-slate-800 hover:bg-primary-500 rounded-md flex items-center justify-center transition-colors group"
                  aria-label={social.label}
                >
                  <social.icon className="w-3 h-3 text-slate-300 group-hover:text-white transition-colors" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer