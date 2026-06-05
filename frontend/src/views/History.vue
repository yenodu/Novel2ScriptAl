<template>
  <section class="history-page">
    <div class="page-header">
      <h2>转换历史</h2>
      <router-link to="/" class="back-link">← 返回转换</router-link>
    </div>

    <p v-if="store.error" class="msg-error">{{ store.error }}</p>
    <p v-if="store.loading" class="msg-loading">加载中…</p>

    <p v-if="!store.loading && !store.records.length" class="msg-empty">
      暂无历史记录，去首页转换一段小说吧。
    </p>

    <table v-if="store.records.length" class="history-table">
      <thead>
        <tr>
          <th>小说预览</th>
          <th class="col-style">风格</th>
          <th class="col-time">时间</th>
          <th class="col-action">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in store.records" :key="r.id">
          <td class="col-preview">{{ r.novel_preview }}{{ r.novel_preview.length >= 100 ? '…' : '' }}</td>
          <td class="col-style">{{ styleLabel(r.style) }}</td>
          <td class="col-time">{{ formatTime(r.created_at) }}</td>
          <td class="col-action">
            <router-link :to="`/history/${r.id}`" class="btn-view">查看</router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="store.records.length" class="pagination">
      <button :disabled="offset === 0" @click="prevPage">上一页</button>
      <span class="page-info">{{ offset + 1 }}–{{ offset + store.records.length }}</span>
      <button :disabled="store.records.length < limit" @click="nextPage">下一页</button>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useHistoryStore } from '../stores/history'

const store = useHistoryStore()
const limit = 20
const offset = ref(0)

onMounted(() => load())

async function load() { await store.fetchList(limit, offset.value) }
function prevPage() { offset.value = Math.max(0, offset.value - limit); load() }
function nextPage() { offset.value += limit; load() }

function styleLabel(s) {
  return { film: '电影', stage: '舞台剧', short: '短视频' }[s] ?? s
}
function formatTime(iso) {
  return iso ? iso.replace('T', ' ').slice(0, 19) : ''
}
</script>

<style scoped>
.history-page { max-width: 900px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }
.page-header h2 { font-size: 1.25rem; color: #0f172a; }
.back-link { font-size: .9rem; color: #6366f1; text-decoration: none; }
.back-link:hover { text-decoration: underline; }

.msg-error { color: #dc2626; font-size: .9rem; margin-bottom: 1rem; }
.msg-loading { color: #64748b; text-align: center; padding: 3rem 0; }
.msg-empty { color: #94a3b8; text-align: center; padding: 3rem 0; font-size: .95rem; }

.history-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.history-table th { background: #f8fafc; color: #475569; font-weight: 600; font-size: .8rem; text-transform: uppercase; letter-spacing: .5px; padding: .75rem 1rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
.history-table td { padding: .75rem 1rem; font-size: .9rem; color: #334155; border-bottom: 1px solid #f1f5f9; }
.history-table tbody tr:hover { background: #f8fafc; }

.col-preview { max-width: 360px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.col-style { width: 80px; }
.col-time { width: 150px; white-space: nowrap; }
.col-action { width: 80px; text-align: center; }

.btn-view { padding: .3rem .8rem; font-size: .8rem; color: #6366f1; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 4px; cursor: pointer; text-decoration: none; }
.btn-view:hover { background: #e0e7ff; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.25rem; }
.pagination button { padding: .4rem 1rem; font-size: .85rem; border: 1px solid #cbd5e1; border-radius: 4px; background: #fff; cursor: pointer; }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }
.pagination button:not(:disabled):hover { border-color: #6366f1; color: #6366f1; }
.page-info { font-size: .85rem; color: #64748b; }
</style>
