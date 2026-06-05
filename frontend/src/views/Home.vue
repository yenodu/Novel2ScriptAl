<template>
  <section class="home">
    <!-- Left: Input -->
    <div class="panel panel-input">
      <div class="panel-header">
        <h2 class="panel-title">小说内容</h2>
        <div class="style-selector">
          <label class="style-label">风格：</label>
          <select v-model="category" class="select" @change="onCategoryChange">
            <option v-for="(label, key) in categories" :key="key" :value="key">{{ label }}</option>
          </select>
          <select v-model="store.style" class="select">
            <option v-for="s in currentSubStyles" :key="s.key" :value="s.key">{{ s.label }}</option>
          </select>
          <label class="mood-toggle">
            <input type="checkbox" v-model="store.addMood" />
            <span>情感标签</span>
          </label>
        </div>
      </div>

      <textarea
        id="novel-input"
        v-model="store.content"
        class="text-input"
        placeholder="在此粘贴小说文本……"
      ></textarea>

      <button
        class="btn-convert"
        :disabled="store.loading"
        @click="store.convert()"
      >
        {{ store.loading ? '转换中…' : '→ 转换' }}
      </button>

      <p v-if="store.error" class="msg-error">{{ store.error }}</p>
    </div>

    <!-- Right: YAML Output (always visible) -->
    <div class="panel panel-output">
      <div class="panel-header">
        <h2 class="panel-title">剧本 YAML（可编辑）</h2>
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
      <textarea
        v-model="store.yamlResult"
        class="yaml-editor"
        placeholder="转换后的 YAML 剧本将显示在这里……"
        spellcheck="false"
      ></textarea>
      <p v-if="!store.yamlResult && !store.loading" class="placeholder-hint">
        左侧粘贴小说内容，点击「→ 转换」生成 YAML 剧本
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useNovelStore } from '../stores/novel'
import { exportYaml, exportTxt, exportFdx } from '../utils/export'

const store = useNovelStore()

// ---- style data ----
const categories = {
  realism: '写实生活化',
  commercial: '商业化强戏剧',
  arthouse: '文艺诗意化',
  fantasy: '奇幻架空类',
  suspense: '悬疑惊悚',
  comedy: '喜剧夸张',
}

const subStyles = {
  realism: [
    { key: 'faithful_realism', label: '原著忠实写实' },
    { key: 'slice_of_life', label: '市井烟火写实' },
    { key: 'documentary', label: '纪实改编' },
  ],
  commercial: [
    { key: 'fast_paced', label: '强爽点浓缩改编' },
    { key: 'family_friendly', label: '合家欢通俗改编' },
    { key: 'crime_thriller', label: '悬疑刑侦商业化' },
  ],
  arthouse: [
    { key: 'poetic_minimalist', label: '意象留白改编' },
    { key: 'lyrical_prose', label: '抒情散文诗改编' },
    { key: 'absurdist_arthouse', label: '荒诞文艺改编' },
  ],
  fantasy: [
    { key: 'epic_fantasy', label: '史诗宏大改编' },
    { key: 'light_fantasy', label: '轻量化魔改改编' },
    { key: 'soft_scifi', label: '软科幻落地改编' },
  ],
  suspense: [
    { key: 'honkaku_mystery', label: '本格推理改编' },
    { key: 'horror_atmosphere', label: '惊悚氛围改编' },
    { key: 'social_suspense', label: '社会派悬疑改编' },
  ],
  comedy: [
    { key: 'slapstick_absurd', label: '无厘头魔改' },
    { key: 'light_comedy', label: '轻喜剧落地改编' },
    { key: 'satirical_dark', label: '讽刺黑色喜剧' },
  ],
}

// Find current category from store.style
function findCategory(styleKey) {
  for (const [cat, list] of Object.entries(subStyles)) {
    if (list.some(s => s.key === styleKey)) return cat
  }
  return 'realism'
}

const category = ref(findCategory(store.style))
const currentSubStyles = computed(() => subStyles[category.value] || subStyles.realism)

function onCategoryChange() {
  store.style = currentSubStyles.value[0].key
}

// Keep category in sync if store.style changes externally
watch(() => store.style, (val) => {
  category.value = findCategory(val)
})

// ---- export ----
const showExport = ref(false)
function doExport(format) {
  showExport.value = false
  if (!store.yamlResult) return
  if (format === 'yaml') exportYaml(store.yamlResult)
  else if (format === 'txt') exportTxt(store.yamlResult)
  else if (format === 'fdx') exportFdx(store.yamlResult)
}

// ---- copy ----
async function copyYaml() {
  if (!store.yamlResult) return
  try { await navigator.clipboard.writeText(store.yamlResult) } catch {}
}
</script>

<style scoped>
/* ---------- two-column layout ---------- */
.home {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.panel {
  flex: 1; min-width: 0;
  background: var(--bg-card); border-radius: 10px; padding: 1.5rem;
  box-shadow: 0 1px 3px var(--shadow); display: flex; flex-direction: column;
}
.panel-output { border-left: 4px solid var(--accent); }

/* ---------- header ---------- */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.panel-title { font-size: 1rem; font-weight: 600; color: var(--text-primary); margin: 0; }

.style-selector {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.style-label { font-size: .85rem; color: var(--text-secondary); }
.select { padding: .25rem .5rem; border: 1px solid var(--border); border-radius: 4px; font-size: .85rem; cursor: pointer; background: var(--bg-card); color: var(--text-primary); }
.select:focus { outline: none; border-color: var(--accent); }
.mood-toggle { display: flex; align-items: center; gap: .3rem; font-size: .85rem; color: var(--text-secondary); cursor: pointer; white-space: nowrap; }
.mood-toggle input { cursor: pointer; }

/* ---------- textarea ---------- */
.text-input,.yaml-editor { flex:1; width:100%; padding:.75rem; font-size:.9rem; border-radius:6px; resize:none; line-height:1.7; min-height:420px; }
.text-input { font-family:inherit; background:var(--bg-input); color:var(--text-primary); border:1px solid var(--border); }
.text-input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px color-mix(in srgb,var(--accent)20%,transparent); }
.yaml-editor { font-family:'Cascadia Code','Fira Code','Consolas',monospace; color:var(--code-text); background:var(--bg-code); border:1px solid var(--code-border); tab-size:2; }
.yaml-editor:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px color-mix(in srgb,var(--accent)30%,transparent); }
.yaml-editor::placeholder { color:var(--text-muted); font-family:inherit; }

/* ---------- button ---------- */
.btn-convert {
  margin-top: 0.75rem;
  padding: 0.6rem 0;
  width: 100%;
  font-size: 1rem;
  font-weight: 600;
  color: var(--btn-primary-text);
  background: var(--accent);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-convert:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-convert:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.header-actions { display: flex; gap: .5rem; align-items: center; }
.export-dropdown { position: relative; }
.btn-export { padding: .25rem .75rem; font-size: .8rem; color: #475569; background: #fff; border: 1px solid #cbd5e1; border-radius: 4px; cursor: pointer; }
.btn-export:hover { border-color: #6366f1; color: #6366f1; }
.export-menu { position: absolute; top: 100%; right: 0; margin-top: 4px; background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,.1); z-index: 50; min-width: 180px; overflow: hidden; }
.export-menu button { display: block; width: 100%; padding: .5rem .75rem; border: none; background: transparent; font-size: .8rem; color: #334155; cursor: pointer; text-align: left; }
.export-menu button:hover { background: #f1f5f9; color: #6366f1; }

.btn-copy {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  color: var(--accent);
  background: var(--accent-light);
  border: 1px solid var(--accent-light);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-copy:hover {
  background: var(--accent-hover);
}

/* ---------- messages ---------- */
.msg-error {
  margin-top: 0.5rem;
  color: var(--danger);
  font-size: 0.85rem;
  flex-shrink: 0;
}

.placeholder-hint {
  margin-top: 0.5rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  text-align: center;
  flex-shrink: 0;
}
</style>
