<template>
  <section class="detail-page">
    <div class="page-header">
      <router-link to="/history" class="back-link">← 返回历史</router-link>
      <h2>剧本详情</h2>
      <span></span>
    </div>

    <p v-if="error" class="msg-error">{{ error }}</p>
    <p v-if="loading" class="msg-loading">加载中…</p>

    <div v-if="record" class="detail-body">
      <div class="meta-bar">
        <span class="meta-tag">风格：{{ styleLabel(record.style) }}</span>
        <span class="meta-tag">时间：{{ formatTime(record.created_at) }}</span>
        <button class="btn-reconvert" @click="reconvert" :disabled="reconverting">
          {{ reconverting ? '转换中…' : '重新转换' }}
        </button>
      </div>

      <div class="columns">
        <div class="panel">
          <h3 class="panel-title">原始小说</h3>
          <div class="novel-text">{{ record.novel_text }}</div>
        </div>
        <div class="panel panel-yaml">
          <div class="panel-header">
            <h3 class="panel-title">剧本 YAML</h3>
            <div class="header-actions">
              <div class="export-dropdown">
                <button class="btn-export" @click="showExport = !showExport">导出 ▾</button>
                <div v-if="showExport" class="export-menu">
                  <button @click="doExport('yaml')">导出 YAML (.yaml)</button>
                  <button @click="doExport('txt')">导出 TXT (.txt)</button>
                  <button @click="doExport('fdx')">导出 Final Draft (.fdx)</button>
                </div>
              </div>
              <button class="btn-copy" @click="copyYaml">复制</button>
            </div>
          </div>
          <textarea v-model="editedYaml" class="yaml-editor" spellcheck="false"></textarea>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useHistoryStore } from '../stores/history'
import { exportYaml, exportTxt, exportFdx } from '../utils/export'

const route = useRoute()
const router = useRouter()
const historyStore = useHistoryStore()

const record = ref(null)
const editedYaml = ref('')
const loading = ref(false)
const error = ref(null)
const reconverting = ref(false)
<<<<<<< Updated upstream
=======
const checking = ref(false)
const showExport = ref(false)

function doExport(format) {
  showExport.value = false
  if (format === 'yaml') exportYaml(editedYaml.value)
  else if (format === 'txt') exportTxt(editedYaml.value)
  else if (format === 'fdx') exportFdx(editedYaml.value)
}

// Character check state
const showModal = ref(false)
const features = ref({})
const deviations = ref([])
>>>>>>> Stashed changes

onMounted(async () => {
  loading.value = true
  try {
    const data = await historyStore.fetchDetail(route.params.id)
    record.value = data
    editedYaml.value = data.script_yaml
  } catch (e) {
    error.value = e.response?.data?.detail ?? '加载失败'
  } finally {
    loading.value = false
  }
})

function styleLabel(s) {
  return { film: '电影剧本', stage: '舞台剧', short: '短视频' }[s] ?? s
}
function formatTime(iso) {
  return iso ? iso.replace('T', ' ').slice(0, 19) : ''
}
async function copyYaml() {
  try { await navigator.clipboard.writeText(editedYaml.value) } catch {}
}
async function reconvert() {
  if (!record.value) return
  reconverting.value = true
  error.value = null
  try {
    const res = await api.post('/convert', {
      novel_text: record.value.novel_text,
      style: record.value.style,
    })
    router.push(`/history/${res.data.record_id}`)
  } catch (e) {
    error.value = e.response?.data?.detail ?? '重新转换失败'
  } finally {
    reconverting.value = false
  }
}
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.page-header h2 { font-size: 1.25rem; color: #0f172a; }
.back-link { font-size: .9rem; color: #6366f1; text-decoration: none; }
.back-link:hover { text-decoration: underline; }

.msg-error { color: #dc2626; font-size: .9rem; margin-bottom: 1rem; }
.msg-loading { color: #64748b; text-align: center; padding: 3rem 0; }

.meta-bar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.meta-tag { font-size: .8rem; color: #475569; background: #e2e8f0; padding: .2rem .6rem; border-radius: 4px; }
.btn-reconvert { margin-left: auto; padding: .3rem 1rem; font-size: .85rem; font-weight: 500; color: #fff; background: #6366f1; border: none; border-radius: 4px; cursor: pointer; }
.btn-reconvert:hover:not(:disabled) { background: #4f46e5; }
.btn-reconvert:disabled { opacity: .6; cursor: not-allowed; }

.columns { display: flex; gap: 1.5rem; align-items: flex-start; }
.panel { flex: 1; min-width: 0; background: #fff; border-radius: 10px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.panel-yaml { border-left: 4px solid #6366f1; }
.panel-title { font-size: .95rem; font-weight: 600; color: #334155; margin-bottom: .5rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }

.novel-text { white-space: pre-wrap; font-size: .9rem; line-height: 1.7; color: #475569; }

.yaml-editor { width: 100%; min-height: 400px; padding: .75rem; font-family: 'Cascadia Code','Fira Code','Consolas',monospace; font-size: .85rem; line-height: 1.7; color: #e2e8f0; background: #0f172a; border: 1px solid #334155; border-radius: 6px; resize: vertical; }
.yaml-editor:focus { outline: none; border-color: #6366f1; }
<<<<<<< Updated upstream
=======
.header-actions { display: flex; gap: .5rem; align-items: center; }
.export-dropdown { position: relative; }
.btn-export { padding: .25rem .75rem; font-size: .8rem; color: #475569; background: #fff; border: 1px solid #cbd5e1; border-radius: 4px; cursor: pointer; }
.btn-export:hover { border-color: #6366f1; color: #6366f1; }
.export-menu { position: absolute; top: 100%; right: 0; margin-top: 4px; background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,.1); z-index: 50; min-width: 180px; overflow: hidden; }
.export-menu button { display: block; width: 100%; padding: .5rem .75rem; border: none; background: transparent; font-size: .8rem; color: #334155; cursor: pointer; text-align: left; }
.export-menu button:hover { background: #f1f5f9; color: #6366f1; }
>>>>>>> Stashed changes

.btn-copy { padding: .25rem .75rem; font-size: .8rem; color: #6366f1; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 4px; cursor: pointer; }
.btn-copy:hover { background: #e0e7ff; }
</style>
