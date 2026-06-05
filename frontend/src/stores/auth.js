import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(t) {
    token.value = t
    if (t) {
      localStorage.setItem('token', t)
    } else {
      localStorage.removeItem('token')
    }
  }

  async function register(username, password) {
    loading.value = true
    error.value = null
    try {
      await api.post('/register', { username, password })
      return await login(username, password)
    } catch (e) {
      error.value = e.response?.data?.detail ?? '注册失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      const res = await api.post('/login', { username, password })
      setToken(res.data.access_token)
      user.value = { username: res.data.username }
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail ?? '登录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await api.get('/me')
      user.value = { username: res.data.username }
    } catch {
      setToken('')
      user.value = null
    }
  }

  function logout() {
    setToken('')
    user.value = null
    error.value = null
  }

  return { token, user, loading, error, isLoggedIn, register, login, fetchMe, logout }
})
