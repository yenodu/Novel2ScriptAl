<template>
  <section class="detail-page">
    <div class="page-header">
      <router-link :to="backLink" class="back-link">← {{ backLabel }}</router-link>
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
        <button class="btn-save" @click="saveRecord" :disabled="saving">{{ saving ? '保存中…' : '💾 保存' }}</button>
        <button class="btn-reconvert" @click="reconvert" :disabled="reconverting">
          {{ reconverting ? '转换中…' : '重新转换' }}
        </button>
      </div>

      <div class="columns">
        <div class="panel">
          <h3 class="panel-title">原始小说</h3>
          <textarea v-model="editedNovel" class="novel-textarea"></textarea>
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

    <!-- Character Check Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-card">
        <div class="modal-header"><h3>角色一致性校验报告</h3><button class="btn-close" @click="showModal = false">✕</button></div>
        <h4 class="section-title">提取的角色特征</h4>
        <table class="feature-table" v-if="Object.keys(features).length"><thead><tr><th>角色</th><th>性格</th><th>口头禅</th><th>外貌</th></tr></thead><tbody><tr v-for="(f, name) in features" :key="name"><td><strong>{{ name }}</strong></td><td><input v-model="f.personality" class="feat-input" /></td><td><input v-model="f.catchphrase" class="feat-input" /></td><td><input v-model="f.appearance" class="feat-input" /></td></tr></tbody></table>
        <p v-else class="msg-hint">暂无特征数据</p>
        <button class="btn-recheck" @click="runCheck(true)" :disabled="checking">{{ checking ? '校验中…' : '基于编辑后特征重新校验' }}</button>
        <h4 class="section-title">偏差报告</h4>
        <div v-if="deviations.length" class="deviation-list"><div v-for="(d, i) in deviations" :key="i" class="deviation-item"><span class="dev-char">{{ d.character }}</span><span class="dev-line">"{{ d.line }}"</span><span class="dev-issue">{{ d.issue }}</span></div></div>
        <p v-else class="msg-hint msg-ok">✅ 所有角色对话与特征一致</p>
      </div>
    </div>

    <!-- Mood Modal -->
    <div v-if="showMoodModal" class="modal-overlay" @click.self="showMoodModal=false">
      <div class="mood-modal"><h3>🎭 设置情感标签</h3><p class="mood-context">场景 {{ moodSceneId }}：{{ moodContext }}</p>
        <label class="mood-label">Mood（情绪）</label><input v-model="moodValue" class="mood-input" placeholder="如：紧张、悲伤…" @keyup.enter="applyMood" />
        <label class="mood-label">灯光（可选）</label><input v-model="moodLighting" class="mood-input" placeholder="如：暖黄顶光" />
        <label class="mood-label">音效（可选）</label><input v-model="moodSound" class="mood-input" placeholder="如：雨声白噪" />
        <div class="mood-actions"><button class="btn-cancel" @click="showMoodModal=false">取消</button><button class="btn-apply" @click="applyMood">应用</button></div>
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
import { exportYaml, exportTxt, exportFdx } from '../utils/export'

const route = useRoute()
const router = useRouter()
const historyStore = useHistoryStore()

const record = ref(null)
const editedYaml = ref('')
const editedNovel = ref('')
const loading = ref(false)
const saving = ref(false)

const from = route.query.from
const backLink = from === 'folders' ? '/folders' : '/history'
const backLabel = from === 'folders' ? '返回文件夹' : '返回历史'
const error = ref(null)
const reconverting = ref(false)
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
    editedNovel.value = data.novel_text
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

async function saveRecord() {
  if (!record.value) return; saving.value = true; error.value = null
  try { await api.patch(`/records/${route.params.id}`, { novel_text: editedNovel.value, script_yaml: editedYaml.value }); _toast('✅ 已保存') }
  catch (e) { error.value = e.response?.data?.detail ?? '保存失败' } finally { saving.value = false }
}

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
.panel-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem}
.novel-textarea{width:100%;min-height:400px;padding:.75rem;font-family:inherit;font-size:.9rem;line-height:1.7;color:var(--text-primary);background:var(--bg-input);border:1px solid var(--border);border-radius:6px;resize:vertical;overflow-y:auto}
.novel-textarea:focus{outline:none;border-color:var(--accent)}
.novel-textarea::-webkit-scrollbar{width:6px}.novel-textarea::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px}
.btn-save{padding:.3rem 1rem;font-size:.85rem;font-weight:500;color:var(--btn-primary-text);background:var(--success);border:none;border-radius:4px;cursor:pointer}
.btn-save:disabled{opacity:.6;cursor:not-allowed}
.header-actions{display:flex;gap:.5rem;align-items:center}.export-dropdown{position:relative}
.btn-export{padding:.25rem .75rem;font-size:.8rem;color:var(--text-secondary);background:var(--bg-card);border:1px solid var(--border);border-radius:4px;cursor:pointer}
.btn-export:hover{border-color:var(--accent);color:var(--accent)}
.export-menu{position:absolute;top:100%;right:0;margin-top:4px;background:var(--bg-card);border:1px solid var(--border-light);border-radius:6px;box-shadow:0 4px 12px var(--shadow);z-index:50;min-width:180px;overflow:hidden}
.export-menu button{display:block;width:100%;padding:.5rem .75rem;border:none;background:transparent;font-size:.8rem;color:var(--text-primary);cursor:pointer;text-align:left}
.export-menu button:hover{background:var(--bg-card-alt);color:var(--accent)}
.btn-copy{padding:.25rem .75rem;font-size:.8rem;color:var(--accent);background:var(--accent-light);border:1px solid var(--accent-light);border-radius:4px;cursor:pointer}
.btn-copy:hover{background:var(--accent-hover)}
.yaml-wrapper{position:relative}
.yaml-editor{width:100%;min-height:400px;padding:.75rem;font-family:'Cascadia Code','Fira Code','Consolas',monospace;font-size:.85rem;line-height:1.7;color:var(--code-text);background:var(--bg-code);border:1px solid var(--code-border);border-radius:6px;resize:vertical}
.yaml-editor:focus{outline:none;border-color:var(--accent)}
.float-btn{position:absolute;padding:.4rem .8rem;font-size:.8rem;color:#fff;background:var(--accent);border:none;border-radius:6px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.25);z-index:10;animation:fadeUp .2s}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;justify-content:center;align-items:center;z-index:100}
.modal-card{background:var(--bg-card);border-radius:12px;width:90%;max-width:800px;max-height:85vh;overflow-y:auto;padding:2rem;box-shadow:0 8px 32px var(--shadow)}
.modal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem}
.modal-header h3{font-size:1.15rem;color:var(--text-primary)}.btn-close{padding:.25rem .6rem;font-size:1rem;border:none;background:transparent;cursor:pointer;color:var(--text-secondary)}.btn-close:hover{color:var(--danger)}
.section-title{font-size:.95rem;font-weight:600;color:var(--text-primary);margin:1rem 0 .5rem;border-bottom:1px solid var(--border-light);padding-bottom:.25rem}
.feature-table{width:100%;border-collapse:collapse;margin-bottom:.5rem}
.feature-table th{background:var(--bg-card-alt);font-size:.8rem;color:var(--text-secondary);padding:.5rem;text-align:left;border-bottom:1px solid var(--border-light)}
.feature-table td{padding:.4rem .5rem;border-bottom:1px solid var(--border-light)}
.feat-input{width:100%;padding:.3rem .4rem;border:1px solid var(--border);border-radius:4px;font-size:.8rem;font-family:inherit;background:var(--bg-input);color:var(--text-primary)}
.feat-input:focus{outline:none;border-color:var(--accent)}
.btn-recheck{padding:.4rem 1rem;font-size:.85rem;font-weight:500;color:var(--btn-primary-text);background:var(--accent);border:none;border-radius:4px;cursor:pointer;margin-top:.5rem}
.deviation-list{display:flex;flex-direction:column;gap:.5rem}
.deviation-item{display:flex;gap:.75rem;padding:.5rem .75rem;background:#3A2020;border-radius:6px;font-size:.85rem;align-items:flex-start}
.dev-char{font-weight:600;color:#FCA5A5;white-space:nowrap}.dev-line{color:#FCA5A5;font-style:italic}.dev-issue{color:#FCA5A5;margin-left:auto;text-align:right;max-width:300px}
.msg-hint{font-size:.85rem;color:var(--text-muted)}.msg-ok{color:var(--success)}
.mood-modal{background:var(--bg-card);border-radius:12px;padding:1.75rem;width:90%;max-width:420px;box-shadow:0 8px 32px var(--shadow)}
.mood-modal h3{font-size:1.1rem;margin-bottom:.5rem;color:var(--text-primary)}
.mood-context{font-size:.8rem;color:var(--text-muted);margin-bottom:1rem;padding:.4rem .6rem;background:var(--bg-card-alt);border-radius:4px}
.mood-label{display:block;font-size:.8rem;color:var(--text-secondary);margin:.5rem 0 .2rem}
.mood-input{width:100%;padding:.45rem .6rem;border:1px solid var(--border);border-radius:6px;font-size:.9rem;background:var(--bg-input);color:var(--text-primary)}
.mood-input:focus{outline:none;border-color:var(--accent)}
.mood-actions{display:flex;gap:.5rem;justify-content:flex-end;margin-top:1rem}
.btn-cancel{padding:.4rem 1rem;font-size:.85rem;color:var(--text-secondary);background:var(--bg-card-alt);border:1px solid var(--border-light);border-radius:6px;cursor:pointer}
.btn-apply{padding:.4rem 1rem;font-size:.85rem;color:var(--btn-primary-text);background:var(--accent);border:none;border-radius:6px;cursor:pointer}
.toast{position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);padding:.6rem 1.5rem;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border);border-radius:8px;font-size:.9rem;z-index:200;animation:fadeUp .3s}
</style>
