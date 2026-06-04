import axios from 'axios'

const api = axios.create({
  baseURL: '/api',   // proxied by Vite → http://127.0.0.1:8000
  timeout: 30000,
})

export default api
