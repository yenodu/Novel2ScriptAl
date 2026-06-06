<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-left"><h1>Novel2ScriptAl</h1><p class="subtitle">小说转剧本工具</p></div>
      <div class="header-right">
        <select v-model="themeStore.current" @change="themeStore.setTheme($event.target.value)" class="theme-select">
          <option v-for="(t,k) in themeStore.themes" :key="k" :value="k">{{ t.name }}</option>
        </select>
        <template v-if="auth.isLoggedIn">
          <router-link to="/history" class="nav-link">历史记录</router-link>
          <span class="user-tag">{{ auth.user?.username ?? '...' }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </template>
      </div>
    </header>
    <main><router-view /></main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
const auth = useAuthStore(); const themeStore = useThemeStore()
auth.fetchMe()
function handleLogout() { auth.logout(); window.location.href = '/login' }
</script>

<style>
:root { --bg-body:#1E1A2F;--bg-card:#2A2440;--bg-card-alt:#352E50;--bg-input:#1A1628;--bg-code:#0F0B1E;--code-text:#e2e8f0;--code-border:#334155;--bg-modal:#2A2440;--text-primary:#E8E0F0;--text-secondary:#A89BB5;--text-muted:#7A6D8A;--border:#3D3560;--border-light:#4A4168;--accent:#9b59b6;--accent-hover:#8E44AD;--accent-light:#3D2560;--accent-text:#D4A0F0;--btn-primary-text:#fff;--danger:#E74C3C;--success:#27AE60;--shadow:rgba(0,0,0,.35);--table-stripe:#302544;--tag-bg:#3D3560;--tag-text:#C8B8E0; }
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg-body);color:var(--text-primary);min-height:100vh}
#app-container{max-width:1200px;margin:0 auto;padding:2rem 1.5rem}
.app-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:2rem}
.header-left h1{font-size:2rem;color:var(--text-primary)}
.subtitle{color:var(--text-secondary);margin-top:.25rem}
.header-right{display:flex;align-items:center;gap:.75rem;margin-top:.5rem}
.theme-select{padding:.25rem .5rem;border:1px solid var(--border);border-radius:4px;font-size:.8rem;background:var(--bg-card);color:var(--text-primary);cursor:pointer}
.theme-select:focus{outline:none;border-color:var(--accent)}
.nav-link{font-size:.9rem;color:var(--accent);text-decoration:none;font-weight:500}
.nav-link:hover{text-decoration:underline}
.user-tag{font-size:.9rem;color:var(--tag-text);background:var(--tag-bg);padding:.25rem .75rem;border-radius:999px}
.btn-logout{padding:.3rem .8rem;font-size:.8rem;color:var(--text-muted);background:transparent;border:1px solid var(--border);border-radius:4px;cursor:pointer}
.btn-logout:hover{color:var(--danger);border-color:var(--danger)}
</style>
