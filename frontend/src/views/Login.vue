<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">Novel2ScriptAl</h1>
      <p class="login-sub">登录以继续使用小说转剧本工具</p>

      <div class="tabs">
        <button :class="['tab', { active: mode === 'login' }]" @click="switchMode('login')">登录</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="switchMode('register')">注册</button>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <input v-model="username" class="field" type="text" placeholder="用户名" autocomplete="username" minlength="3" maxlength="32" required />
        <input v-model="password" class="field" type="password" placeholder="密码" autocomplete="current-password" minlength="6" required />
        <p v-if="store.error" class="msg-error">{{ store.error }}</p>
        <button class="btn-submit" type="submit" :disabled="store.loading">
          {{ store.loading ? '请稍候…' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const store = useAuthStore()
const mode = ref('login')
const username = ref('')
const password = ref('')

function switchMode(m) { mode.value = m; store.error = null }

async function handleSubmit() {
  try {
    if (mode.value === 'login') await store.login(username.value, password.value)
    else await store.register(username.value, password.value)
    router.push('/')
  } catch {}
}
</script>

<style scoped>
.login-page { display:flex; justify-content:center; align-items:center; min-height:60vh; }
.login-card { width:100%; max-width:400px; background:#fff; border-radius:12px; padding:2.5rem 2rem; box-shadow:0 4px 16px rgba(0,0,0,.1); text-align:center; }
.login-title { font-size:1.6rem; color:#0f172a; margin-bottom:.25rem; }
.login-sub { color:#64748b; font-size:.9rem; margin-bottom:1.5rem; }
.tabs { display:flex; border-radius:6px; overflow:hidden; border:1px solid #cbd5e1; margin-bottom:1.25rem; }
.tab { flex:1; padding:.5rem 0; border:none; background:#f8fafc; color:#64748b; font-size:.9rem; font-weight:500; cursor:pointer; }
.tab.active { background:#6366f1; color:#fff; }
.login-form { display:flex; flex-direction:column; gap:.75rem; }
.field { width:100%; padding:.65rem .75rem; border:1px solid #cbd5e1; border-radius:6px; font-size:.95rem; font-family:inherit; }
.field:focus { outline:none; border-color:#6366f1; box-shadow:0 0 0 3px rgba(99,102,241,.15); }
.btn-submit { margin-top:.25rem; padding:.6rem 0; font-size:1rem; font-weight:600; color:#fff; background:#6366f1; border:none; border-radius:6px; cursor:pointer; }
.btn-submit:hover:not(:disabled) { background:#4f46e5; }
.btn-submit:disabled { opacity:.6; cursor:not-allowed; }
.msg-error { color:#dc2626; font-size:.85rem; text-align:center; }
</style>
