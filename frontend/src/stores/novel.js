import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useNovelStore = defineStore('novel', () => {
  const content = ref('')
  const result = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function convert() {
    if (!content.value.trim()) {
      error.value = '请输入小说内容'
      return
    }

    loading.value = true
    error.value = null
    result.value = null

    try {
      const res = await api.post('/convert', { text: content.value })
      result.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail ?? e.message ?? '请求失败，请检查后端是否已启动'
    } finally {
      loading.value = false
    }
  }

  return { content, result, loading, error, convert }
})
