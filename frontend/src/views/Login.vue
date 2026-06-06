<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">Novel2ScriptAl</h1>
      <p class="login-sub">登录以继续使用小说转剧本工具</p>

      <div class="tabs">
        <button
          :class="['tab', { active: mode === 'login' }]"
          @click="switchMode('login')"
        >登录</button>
        <button
          :class="['tab', { active: mode === 'register' }]"
          @click="switchMode('register')"
        >注册</button>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <input
          v-model="username"
          class="field"
          type="text"
          placeholder="用户名"
          autocomplete="username"
          minlength="3"
          maxlength="32"
          required
        />
        <input
          v-model="password"
          class="field"
          type="password"
          placeholder="密码"
          autocomplete="current-password"
          minlength="6"
          required
        />

        <p v-if="store.error" class="msg-error">{{ store.error }}</p>

        <button class="btn-submit ripple" type="submit" :disabled="store.loading">
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

function switchMode(m) {
  mode.value = m
  store.error = null
}

async function handleSubmit() {
  try {
    if (mode.value === 'login') {
      await store.login(username.value, password.value)
    } else {
      await store.register(username.value, password.value)
    }
    router.push('/')
  } catch {
    // error already set in store
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 65vh; padding: 2rem 0; }
.login-card { width: 100%; max-width: 420px; background: var(--bg-card); border-radius: 20px; padding: 3rem 2.5rem; box-shadow: 0 8px 40px var(--shadow); text-align: center; border: 1px solid var(--border-light); position: relative; overflow: hidden; }
.login-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, var(--accent), var(--accent-hover), var(--accent-light)); }
.login-title { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, var(--accent), var(--accent-text)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: .3rem; }
.login-sub { color: var(--text-secondary); font-size: .9rem; margin-bottom: 2rem; }

.tabs { display: flex; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); margin-bottom: 1.5rem; background: var(--bg-card-alt); }
.tab { flex: 1; padding: .6rem 0; border: none; background: transparent; color: var(--text-secondary); font-size: .9rem; font-weight: 500; cursor: pointer; transition: all .2s; }
.tab.active { background: linear-gradient(135deg, var(--accent), var(--accent-hover)); color: var(--btn-primary-text); box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 40%, transparent); }

.login-form { display: flex; flex-direction: column; gap: .85rem; }
.field { width: 100%; padding: .75rem .9rem; border: 1.5px solid var(--border); border-radius: 10px; font-size: .95rem; font-family: inherit; background: var(--bg-input); color: var(--text-primary); transition: all .15s; }
.field:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 15%, transparent); }
.field::placeholder { color: var(--text-muted); }

.btn-submit { margin-top: .5rem; padding: .7rem 0; font-size: 1rem; font-weight: 700; color: var(--btn-primary-text); background: linear-gradient(135deg, var(--accent), var(--accent-hover)); border: none; border-radius: 10px; cursor: pointer; transition: all .2s; letter-spacing: .02em; }
.btn-submit:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 16px color-mix(in srgb, var(--accent) 40%, transparent); }
.btn-submit:disabled { opacity: .6; cursor: not-allowed; transform: none; }
.msg-error { color: var(--danger); font-size: .85rem; text-align: center; margin-top: .25rem; }
</style>
