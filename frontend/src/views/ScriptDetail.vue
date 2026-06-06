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
            <button class="btn-copy" @click="copyYaml">复制</button>
          </div>
          <div class="yaml-wrapper">
            <textarea
              ref="yamlRef"
              v-model="editedYaml"
              class="yaml-editor"
              spellcheck="false"
              @mouseup="onTextSelect"
              @keyup="hideFloat"
            ></textarea>
            <!-- floating mood button -->
            <button
              v-if="floatVisible"
              class="float-btn"
              :style="floatStyle"
              @click="openMoodModal"
            >🎭 重新定义情感</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mood Modal -->
    <div v-if="showMoodModal" class="modal-overlay" @click.self="showMoodModal=false">
      <div class="mood-modal">
        <h3>🎭 设置情感标签</h3>
        <p class="mood-context">场景 {{ moodSceneId }}：{{ moodContext }}</p>
        <label class="mood-label">Mood（情绪）</label>
        <input v-model="moodValue" class="mood-input" placeholder="如：紧张、悲伤、温馨…" @keyup.enter="applyMood" />
        <label class="mood-label">Suggested Lighting（灯光，可选）</label>
        <input v-model="moodLighting" class="mood-input" placeholder="如：暖黄顶光" />
        <label class="mood-label">Suggested Sound（音效，可选）</label>
        <input v-model="moodSound" class="mood-input" placeholder="如：雨声白噪" />
        <div class="mood-actions">
          <button class="btn-cancel" @click="showMoodModal=false">取消</button>
          <button class="btn-apply" @click="applyMood">应用</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="toast">{{ toast }}</div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
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

// ---- mood editing ----
const yamlRef = ref(null)
const floatVisible = ref(false)
const floatStyle = ref({})
const showMoodModal = ref(false)
const moodSceneId = ref(0)
const moodContext = ref('')
const moodValue = ref('')
const moodLighting = ref('')
const moodSound = ref('')
const toast = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const data = await historyStore.fetchDetail(route.params.id)
    record.value = data
    editedYaml.value = data.script_yaml
  } catch (e) {
    error.value = e.response?.data?.detail ?? '加载失败'
  } finally { loading.value = false }
})

// ---- selection → floating button ----
function onTextSelect() {
  const ta = yamlRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  if (start === end) { floatVisible.value = false; return }

  // Find which scene the cursor is in
  const text = editedYaml.value
  const before = text.slice(0, start)
  const sceneMatch = before.match(/scene_id:\s*(\d+)/g)
  if (!sceneMatch) { floatVisible.value = false; return }
  const sceneId = parseInt(sceneMatch[sceneMatch.length - 1].match(/\d+/)[0])
  moodSceneId.value = sceneId

  // Find scene heading/action context
  const sceneStart = before.lastIndexOf(`scene_id: ${sceneId}`)
  const sceneText = text.slice(sceneStart, sceneStart + 200).split('\n').slice(0, 4).join(' ').replace(/\s+/g, ' ').slice(0, 80)
  moodContext.value = sceneText

  // Position floating button near selection
  const rect = ta.getBoundingClientRect()
  floatStyle.value = {
    top: (start > 0 ? _caretY(ta, start) : rect.height / 2) + 'px',
    left: (rect.width - 160) + 'px',
  }
  floatVisible.value = true
}

function _caretY(ta, pos) {
  // Approximate caret Y position using line count
  const text = ta.value.slice(0, pos)
  const lines = text.split('\n')
  const lh = 1.7 * 0.85 * 16 // line-height * font-size * base
  return Math.min(lines.length * lh, ta.clientHeight - 40)
}

function hideFloat() { floatVisible.value = false }

function openMoodModal() {
  floatVisible.value = false
  moodValue.value = ''
  moodLighting.value = ''
  moodSound.value = ''
  showMoodModal.value = true
  nextTick(() => document.querySelector('.mood-input')?.focus())
}

// ---- apply mood to YAML text ----
async function applyMood() {
  if (!moodValue.value.trim()) return
  showMoodModal.value = false
  const sid = moodSceneId.value

  // Find scene block and insert/update mood fields
  let yaml = editedYaml.value
  const lines = yaml.split('\n')
  let inScene = false
  let sceneIndex = -1
  let hasMood = false, hasLighting = false, hasSound = false
  let moodIdx = -1, lightingIdx = -1, soundIdx = -1
  let insertAfter = -1

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    if (line.trimStart().startsWith(`- scene_id: ${sid}`)) {
      inScene = true
      sceneIndex = i
      continue
    }
    if (inScene) {
      // Stop at next scene or end of scenes
      if (line.trimStart().startsWith('- scene_id:')) break
      if (line.trimStart() === 'dialogues:') { insertAfter = i - 1; break }
      if (line.match(/^\s{4}mood:/)) { hasMood = true; moodIdx = i }
      if (line.match(/^\s{4}suggested_lighting:/)) { hasLighting = true; lightingIdx = i }
      if (line.match(/^\s{4}suggested_sound:/)) { hasSound = true; soundIdx = i }
      insertAfter = i
    }
  }

  if (!inScene) { _toast('未找到对应场景'); return }

  const indent = '    ' // 4 spaces
  const newMoodLine = `${indent}mood: ${moodValue.value}`

  if (hasMood) {
    lines[moodIdx] = newMoodLine
  } else {
    lines.splice(insertAfter + 1, 0, newMoodLine)
    insertAfter++
  }

  if (moodLighting.value.trim()) {
    const newLightLine = `${indent}suggested_lighting: ${moodLighting.value}`
    if (hasLighting) { lines[lightingIdx] = newLightLine }
    else { lines.splice(insertAfter + 1, 0, newLightLine); insertAfter++ }
  }
  if (moodSound.value.trim()) {
    const newSoundLine = `${indent}suggested_sound: ${moodSound.value}`
    if (hasSound) { lines[soundIdx] = newSoundLine }
    else { lines.splice(insertAfter + 1, 0, newSoundLine); insertAfter++ }
  }

  editedYaml.value = lines.join('\n')

  // Persist to backend
  try {
    await api.patch(`/record/${route.params.id}/mood`, {
      scene_id: sid,
      mood: moodValue.value,
      suggested_lighting: moodLighting.value.trim() || null,
      suggested_sound: moodSound.value.trim() || null,
    })
  } catch { /* non-blocking */ }

  _toast(`✅ 场景 ${sid} 情感已更新为「${moodValue.value}」`)
}

function _toast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 2500)
}

// ----
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
.novel-text { white-space: pre-wrap; font-size: .9rem; line-height: 1.7; color: #475569; max-height: 400px; overflow-y: auto; padding-right: .5rem; }
.novel-text::-webkit-scrollbar { width: 6px; }
.novel-text::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

.yaml-wrapper { position: relative; }
.yaml-editor { width: 100%; min-height: 400px; padding: .75rem; font-family: 'Cascadia Code','Fira Code','Consolas',monospace; font-size: .85rem; line-height: 1.7; color: #e2e8f0; background: #0f172a; border: 1px solid #334155; border-radius: 6px; resize: vertical; }
.yaml-editor:focus { outline: none; border-color: #6366f1; }

.btn-copy { padding: .25rem .75rem; font-size: .8rem; color: #6366f1; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 4px; cursor: pointer; }
.btn-copy:hover { background: #e0e7ff; }

/* floating button */
.float-btn {
  position: absolute;
  padding: .4rem .8rem;
  font-size: .8rem;
  color: #fff;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,.25);
  z-index: 10;
  animation: fadeUp .2s;
}
@keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

/* mood modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; justify-content: center; align-items: center; z-index: 100; }
.mood-modal { background: #fff; border-radius: 12px; padding: 1.75rem; width: 90%; max-width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,.2); }
.mood-modal h3 { font-size: 1.1rem; margin-bottom: .5rem; color: #0f172a; }
.mood-context { font-size: .8rem; color: #64748b; margin-bottom: 1rem; padding: .4rem .6rem; background: #f8fafc; border-radius: 4px; }
.mood-label { display: block; font-size: .8rem; color: #475569; margin: .5rem 0 .2rem; }
.mood-input { width: 100%; padding: .45rem .6rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: .9rem; }
.mood-input:focus { outline: none; border-color: #6366f1; }
.mood-actions { display: flex; gap: .5rem; justify-content: flex-end; margin-top: 1rem; }
.btn-cancel { padding: .4rem 1rem; font-size: .85rem; color: #64748b; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; }
.btn-apply { padding: .4rem 1rem; font-size: .85rem; color: #fff; background: #6366f1; border: none; border-radius: 6px; cursor: pointer; }
.btn-apply:hover { background: #4f46e5; }

/* toast */
.toast { position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%); padding: .6rem 1.5rem; background: #1e293b; color: #fff; border-radius: 8px; font-size: .9rem; z-index: 200; animation: fadeUp .3s; }
</style>
