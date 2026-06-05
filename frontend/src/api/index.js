import axios from 'axios'

// Always use /api prefix.
// Dev:  Vite proxies /api → backend :8000
// Prod: FastAPI serves frontend + /api/* routes on the same origin
const api = axios.create({
  baseURL: '/api',
  timeout: 120000,  // 2 min — LLM calls can take time
})

// ---- request interceptor: attach JWT ----
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ---- response interceptor: 401 → logout ----
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export default api
