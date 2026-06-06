import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useFolderStore = defineStore('folder', () => {
  const folders = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchFolders() {
    loading.value = true; error.value = null
    try { const r = await api.get('/folders'); folders.value = r.data }
    catch (e) { error.value = e.response?.data?.detail ?? '加载失败' }
    finally { loading.value = false }
  }

  async function createFolder(name) {
    const r = await api.post('/folders', { name })
    folders.value.push(r.data)
    return r.data
  }

  async function renameFolder(id, name) {
    await api.put(`/folders/${id}`, { name })
    const f = folders.value.find(x => x.id === id)
    if (f) f.name = name
  }

  async function moveRecord(recordId, folderId) {
    await api.put(`/records/${recordId}/folder`, { folder_id: folderId })
  }

  return { folders, loading, error, fetchFolders, createFolder, renameFolder, moveRecord }
})
