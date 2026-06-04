<template>
  <section class="home">
    <!-- Input area -->
    <div class="card">
      <label class="label" for="novel-input">小说内容</label>
      <textarea
        id="novel-input"
        v-model="store.content"
        class="text-input"
        rows="12"
        placeholder="在此粘贴小说文本……"
      ></textarea>

      <button
        class="btn-convert"
        :disabled="store.loading"
        @click="store.convert()"
      >
        {{ store.loading ? '转换中…' : '转换' }}
      </button>

      <p v-if="store.error" class="msg-error">{{ store.error }}</p>
    </div>

    <!-- Result area -->
    <div v-if="store.result" class="card result-card">
      <h2 class="label">转换结果</h2>
      <pre class="result-pre">{{ JSON.stringify(store.result, null, 2) }}</pre>
    </div>
  </section>
</template>

<script setup>
import { useNovelStore } from '../stores/novel'

const store = useNovelStore()
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #334155;
}

.text-input {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
}

.text-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.btn-convert {
  margin-top: 0.75rem;
  padding: 0.6rem 2rem;
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

.msg-error {
  margin-top: 0.5rem;
  color: #dc2626;
  font-size: 0.9rem;
}

.result-card {
  border-left: 4px solid #6366f1;
}

.result-pre {
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
