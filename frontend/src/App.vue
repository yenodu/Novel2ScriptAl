<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-left">
        <h1>Novel2ScriptAl</h1>
        <p class="subtitle">小说转剧本工具</p>
      </div>
      <div v-if="auth.isLoggedIn" class="header-right">
        <router-link to="/history" class="nav-link">历史记录</router-link>
        <span class="user-tag">{{ auth.user?.username ?? '...' }}</span>
        <button class="btn-logout" @click="handleLogout">退出</button>
      </div>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()

// Restore user from token on page load / refresh
auth.fetchMe()

function handleLogout() {
  auth.logout()
  window.location.href = '/login'
}
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f4f5f7;
  color: #1e293b;
  min-height: 100vh;
}

#app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-left h1 {
  font-size: 2rem;
  color: #0f172a;
}

.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.nav-link { font-size: .9rem; color: #6366f1; text-decoration: none; font-weight: 500; }
.nav-link:hover { text-decoration: underline; }
.user-tag {
  font-size: 0.9rem;
  color: #475569;
  background: #e2e8f0;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
}

.btn-logout {
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
  color: #64748b;
  background: transparent;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-logout:hover {
  color: #dc2626;
  border-color: #dc2626;
}
</style>
