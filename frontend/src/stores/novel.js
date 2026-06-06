import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useNovelStore = defineStore('novel', () => {
  const content = ref('')
  const style = ref('faithful_realism')
  const addMood = ref(false)
  const yamlResult = ref('')
  const lastRecordId = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function convert() {
    if (!content.value.trim()) {
      error.value = '请输入小说内容'
      return
    }

    loading.value = true
    error.value = null
    yamlResult.value = ''

    try {
      const res = await api.post('/convert', {
        novel_text: content.value,
        style: style.value,
        add_mood: addMood.value,
      })
      yamlResult.value = res.data.yaml
      lastRecordId.value = res.data.record_id
    } catch (e) {
      error.value = e.response?.data?.detail ?? e.message ?? '请求失败，请检查后端是否已启动'
    } finally {
      loading.value = false
    }
  }

  return { content, style, addMood, yamlResult, lastRecordId, loading, error, convert }
})
