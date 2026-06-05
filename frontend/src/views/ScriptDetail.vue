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
        <button class="btn-character" @click="openCheck" :disabled="checking">
          {{ checking ? '校验中…' : '🔍 角色一致性校验' }}
        </button>
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
            <button class="btn-copy" @click="copyYaml">复制</button>
          </div>
          <textarea v-model="editedYaml" class="yaml-editor" spellcheck="false"></textarea>
        </div>
      </div>
    </div>

    <!-- Character Check Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>角色一致性校验报告</h3>
          <button class="btn-close" @click="showModal = false">✕</button>
        </div>

        <!-- Extracted Features -->
        <h4 class="section-title">提取的角色特征</h4>
        <table class="feature-table" v-if="Object.keys(features).length">
          <thead>
            <tr><th>角色</th><th>性格</th><th>口头禅</th><th>外貌</th></tr>
          </thead>
          <tbody>
            <tr v-for="(f, name) in features" :key="name">
              <td><strong>{{ name }}</strong></td>
              <td><input v-model="f.personality" class="feat-input" /></td>
              <td><input v-model="f.catchphrase" class="feat-input" /></td>
              <td><input v-model="f.appearance" class="feat-input" /></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="msg-hint">暂无特征数据</p>
        <button class="btn-recheck" @click="runCheck(true)" :disabled="checking">
          {{ checking ? '校验中…' : '基于编辑后特征重新校验' }}
        </button>

        <!-- Deviations -->
        <h4 class="section-title">偏差报告</h4>
        <div v-if="deviations.length" class="deviation-list">
          <div v-for="(d, i) in deviations" :key="i" class="deviation-item">
            <span class="dev-char">{{ d.character }}</span>
            <span class="dev-line">"{{ d.line }}"</span>
            <span class="dev-issue">{{ d.issue }}</span>
          </div>
        </div>
        <p v-else class="msg-hint msg-ok">✅ 所有角色对话与特征一致</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useHistoryStore } from '../stores/history'

const route = useRoute()
const router = useRouter()
const historyStore = useHistoryStore()

const record = ref(null)
const editedYaml = ref('')
const loading = ref(false)
const error = ref(null)
const reconverting = ref(false)
const checking = ref(false)

// Character check state
const showModal = ref(false)
const features = ref({})
const deviations = ref([])

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
function formatTime(iso) { return iso ? iso.replace('T', ' ').slice(0, 19) : '' }
async function copyYaml() { try { await navigator.clipboard.writeText(editedYaml.value) } catch {} }

async function reconvert() {
  if (!record.value) return
  reconverting.value = true; error.value = null
  try {
    const res = await api.post('/convert', { novel_text: record.value.novel_text, style: record.value.style })
    router.push(`/history/${res.data.record_id}`)
  } catch (e) { error.value = e.response?.data?.detail ?? '重新转换失败' }
  finally { reconverting.value = false }
}

async function openCheck() { await runCheck(false) }

async function runCheck(useOverride) {
  checking.value = true; error.value = null; showModal.value = true
  try {
    const body = { record_id: Number(route.params.id) }
    if (useOverride) body.features_override = features.value
    const res = await api.post('/character_check', body)
    features.value = res.data.extracted_features || {}
    deviations.value = res.data.deviations || []
  } catch (e) { error.value = e.response?.data?.detail ?? '校验失败' }
  finally { checking.value = false }
}
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.page-header h2 { font-size: 1.25rem; color: var(--text-primary); }
.back-link { font-size: .9rem; color: var(--accent); text-decoration: none; }
.back-link:hover { text-decoration: underline; }

.msg-error { color: var(--danger); font-size: .9rem; margin-bottom: 1rem; }
.msg-loading { color: var(--text-secondary); text-align: center; padding: 3rem 0; }

.meta-bar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.meta-tag { font-size: .8rem; color: var(--text-secondary); background: var(--tag-bg); padding: .2rem .6rem; border-radius: 4px; }
.btn-reconvert { margin-left: auto; padding: .3rem 1rem; font-size: .85rem; font-weight: 500; color: var(--btn-primary-text); background: var(--accent); border: none; border-radius: 4px; cursor: pointer; }
.btn-reconvert:hover:not(:disabled) { background: var(--accent-hover); }
.btn-reconvert:disabled,.btn-character:disabled,.btn-recheck:disabled { opacity: .6; cursor: not-allowed; }
.btn-character { padding: .3rem 1rem; font-size: .85rem; font-weight: 500; color: var(--accent); background: var(--accent-light); border: 1px solid var(--accent-light); border-radius: 4px; cursor: pointer; }
.btn-character:hover:not(:disabled) { background: var(--accent-hover); }

.columns { display: flex; gap: 1.5rem; align-items: flex-start; }
.panel { flex: 1; min-width: 0; background: var(--bg-card); border-radius: 10px; padding: 1.25rem; box-shadow: 0 1px 3px var(--shadow); }
.panel-yaml { border-left: 4px solid var(--accent); }
.panel-title { font-size: .95rem; font-weight: 600; color: var(--text-primary); margin-bottom: .5rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
.novel-text { white-space: pre-wrap; font-size: .9rem; line-height: 1.7; color: var(--text-secondary); }
.yaml-editor { width: 100%; min-height: 400px; padding: .75rem; font-family: 'Cascadia Code','Fira Code','Consolas',monospace; font-size: .85rem; line-height: 1.7; color: var(--code-text); background: var(--bg-code); border: 1px solid var(--code-border); border-radius: 6px; resize: vertical; }
.yaml-editor:focus { outline: none; border-color: var(--accent); }
.btn-copy { padding: .25rem .75rem; font-size: .8rem; color: var(--accent); background: var(--accent-light); border: 1px solid var(--accent-light); border-radius: 4px; cursor: pointer; }
.btn-copy:hover { background: var(--accent-hover); }

/* modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-card { background: var(--bg-card); border-radius: 12px; width: 90%; max-width: 800px; max-height: 85vh; overflow-y: auto; padding: 2rem; box-shadow: 0 8px 32px var(--shadow); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.modal-header h3 { font-size: 1.15rem; color: var(--text-primary); }
.btn-close { padding: .25rem .6rem; font-size: 1rem; border: none; background: transparent; cursor: pointer; color: var(--text-secondary); }
.btn-close:hover { color: var(--danger); }

.section-title { font-size: .95rem; font-weight: 600; color: var(--text-primary); margin: 1rem 0 .5rem; border-bottom: 1px solid var(--border-light); padding-bottom: .25rem; }

.feature-table { width: 100%; border-collapse: collapse; margin-bottom: .5rem; }
.feature-table th { background: var(--bg-card-alt); font-size: .8rem; color: var(--text-secondary); padding: .5rem; text-align: left; border-bottom: 1px solid var(--border-light); }
.feature-table td { padding: .4rem .5rem; border-bottom: 1px solid var(--border-light); }
.feat-input { width: 100%; padding: .3rem .4rem; border: 1px solid var(--border); border-radius: 4px; font-size: .8rem; font-family: inherit; }
.feat-input:focus { outline: none; border-color: var(--accent); }

.btn-recheck { padding: .4rem 1rem; font-size: .85rem; font-weight: 500; color: var(--btn-primary-text); background: var(--accent); border: none; border-radius: 4px; cursor: pointer; margin-top: .5rem; }
.btn-recheck:hover:not(:disabled) { background: var(--accent-hover); }

.deviation-list { display: flex; flex-direction: column; gap: .5rem; }
.deviation-item { display: flex; gap: .75rem; padding: .5rem .75rem; background: #3A2020; border-radius: 6px; font-size: .85rem; align-items: flex-start; }
.dev-char { font-weight: 600; color: #FCA5A5; white-space: nowrap; }
.dev-line { color: #FCA5A5; font-style: italic; }
.dev-issue { color: #FCA5A5; margin-left: auto; text-align: right; max-width: 300px; }
.msg-hint { font-size: .85rem; color: var(--text-muted); }
.msg-ok { color: var(--success); }
</style>
