import axios from 'axios';

const getBaseURL = () => {
  return import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach Authorization fallback token (user_id) if present
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('user_id');
  if (userId) {
    config.headers['Authorization'] = `Bearer ${userId}`;
  }
  return config;
});

// Course & Lesson APIs
export const courseAPI = {
  getAll: () => api.get('/api/courses'),
  getById: (id) => api.get(`/api/courses/${id}`),
  generateLesson: (subtopicId, isReview = false, previousScore = 0) => 
    api.post('/api/generate-lesson', { 
      subtopic_id: subtopicId, 
      is_review: isReview, 
      previous_score: previousScore 
    })
};

// Progress APIs
export const progressAPI = {
  getProgressSummary: () => api.get('/api/progress-summary'),
  getNextSubtopic: (userId) => api.get(`/api/recommendations/next-topic?user_id=${userId}`)
};

// Authentication APIs (Adding this fallback in case it was at the top of your file)
export const authAPI = {
  login: (credentials) => api.post('/api/login', credentials),
  register: (userData) => api.post('/api/register', userData),
  verifyOTP: (data) => api.post('/api/verify-otp', data),
  logout: () => api.post('/api/logout'),
  getCurrentUser: () => api.get('/api/current-user'),
};

// Quiz APIs 
export const quizAPI = {
  generateQuiz: (subtopicId) => api.post('/api/generate-quiz', { subtopic_id: subtopicId }),
  submitQuiz: (quizData) => api.post('/api/quiz/submit', quizData), // <-- Changed from submitAttempt to submitQuiz
  getHistory: (userId) => api.get(`/api/quiz/history?user_id=${userId}`),
  flagQuestion: (data) => api.post('/api/quiz/flag', data),
};
// Learning Session APIs - Added to fix the CourseView.jsx import crash!
export const learningAPI = {
  startSession: (data) => api.post('/api/learn/session/start', data),
  endSession: (sessionId, data) => api.post(`/api/learn/session/${sessionId}/end`, data),
  checkCode: (code) => api.post('/api/check-code', { code }),
  askHint: (data) => api.post('/api/hint', data)
};
// Agent Status APIs
export const agentAPI = {
  getStatus: () => api.get('/api/agent-status'),
  getLogs: () => api.get('/api/agents/logs'),
  getAnalytics: () => api.get('/api/agent-analytics'),
};

// Admin APIs
export const adminAPI = {
  getStudents: () => api.get('/api/admin/students'),
  getFlaggedQuestions: () => api.get('/api/admin/flagged-questions'),
  getTelemetry: () => api.get('/api/admin/telemetry'),
  exportStudents: () => api.get('/api/admin/export', { responseType: 'blob' }),
};

// Telemetry API
export const telemetryAPI = {
  sendEvent: (data) => api.post('/api/telemetry', data),
};

// Chat API
export const chatAPI = {
  getHistory: (userId) => api.get(`/api/chat/history?user_id=${userId}`),
  sendMessage: (message, userId) => api.post('/api/chat', { message, user_id: userId })
};

export default api;