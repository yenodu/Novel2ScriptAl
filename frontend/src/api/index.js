import axios from 'axios'

// Dev:  Vite proxies /api → backend :8000
// Prod: same origin, call /convert directly (no /api prefix)
const baseURL = import.meta.env.PROD ? '' : '/api'

const api = axios.create({
  baseURL,
  timeout: 120000,  // 2 min — LLM calls can take time
})

export default api
