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
        <button class="btn-copy" @click="copyYaml">复制</button>
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
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.panel-output {
  border-left: 4px solid #6366f1;
}

/* ---------- header ---------- */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.panel-title {
  font-size: 1rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.style-selector {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.style-label {
  font-size: 0.85rem;
  color: #64748b;
}

.select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  background: #fff;
}

.select:focus {
  outline: none;
  border-color: #6366f1;
}

.mood-toggle {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
}
.mood-toggle input { cursor: pointer; }

/* ---------- textarea ---------- */
.text-input,
.yaml-editor {
  flex: 1;
  width: 100%;
  padding: 0.75rem;
  font-size: 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  resize: none;
  line-height: 1.7;
  min-height: 420px;
}

.text-input {
  font-family: inherit;
}

.text-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.yaml-editor {
  font-family: 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  color: #e2e8f0;
  background: #0f172a;
  border-color: #334155;
  tab-size: 2;
}

.yaml-editor:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.yaml-editor::placeholder {
  color: #64748b;
  font-family: inherit;
}

/* ---------- button ---------- */
.btn-convert {
  margin-top: 0.75rem;
  padding: 0.6rem 0;
  width: 100%;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: #6366f1;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-convert:hover:not(:disabled) {
  background: #4f46e5;
}

.btn-convert:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-copy {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  color: #6366f1;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-copy:hover {
  background: #e0e7ff;
}

/* ---------- messages ---------- */
.msg-error {
  margin-top: 0.5rem;
  color: #dc2626;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.placeholder-hint {
  margin-top: 0.5rem;
  color: #94a3b8;
  font-size: 0.8rem;
  text-align: center;
  flex-shrink: 0;
}
</style>
