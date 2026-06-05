import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useHistoryStore = defineStore('history', () => {
  const records = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchList(limit = 20, offset = 0) {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/history', { params: { limit, offset } })
      records.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail ?? '加载失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id) {
    const res = await api.get(`/history/${id}`)
    return res.data
  }

  return { records, loading, error, fetchList, fetchDetail }
})
