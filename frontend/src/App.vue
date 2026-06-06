<template>
  <div id="app-container">
    <header class="app-header">
      <div class="header-left"><h1>Novel2ScriptAl</h1><p class="subtitle">小说转剧本工具</p></div>
      <div class="header-right">
        <select v-model="themeStore.current" @change="themeStore.setTheme($event.target.value)" class="theme-select">
          <option v-for="(t,k) in themeStore.themes" :key="k" :value="k">{{ t.name }}</option>
        </select>
        <template v-if="auth.isLoggedIn">
          <router-link to="/folders" class="nav-link">文件夹</router-link>
          <router-link to="/history" class="nav-link">历史记录</router-link>
          <span class="user-tag">{{ auth.user?.username ?? '...' }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </template>
      </div>
    </header>
    <main>
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
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
body{font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg-body);background-image:radial-gradient(ellipse at 20% 0%, var(--accent-light) 0%, transparent 50%),radial-gradient(ellipse at 80% 100%, var(--bg-card-alt) 0%, transparent 50%);color:var(--text-primary);min-height:100vh}
#app-container{max-width:1200px;margin:0 auto;padding:2rem 1.5rem}
.app-header{padding:1.5rem 2rem;margin-bottom:2rem;background:linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-alt) 100%);border-radius:16px;border:1px solid var(--border-light);box-shadow:0 4px 24px var(--shadow);display:flex;justify-content:space-between;align-items:center}
.header-left h1{font-size:1.8rem;font-weight:800;background:linear-gradient(135deg, var(--accent), var(--accent-text));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{color:var(--text-secondary);margin-top:.15rem;font-size:.85rem;letter-spacing:.05em;text-transform:uppercase}
.header-right{display:flex;align-items:center;gap:.75rem}
.theme-select{padding:.4rem .6rem;border:1px solid var(--border);border-radius:8px;font-size:.8rem;background:var(--bg-input);color:var(--text-primary);cursor:pointer;outline:none}
.theme-select:focus{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb, var(--accent) 25%, transparent)}
.nav-link{font-size:.85rem;color:var(--accent);text-decoration:none;font-weight:500;padding:.35rem .75rem;border-radius:6px;transition:all .15s}
.nav-link:hover{background:var(--accent-light);text-decoration:none}
.user-tag{font-size:.85rem;color:var(--tag-text);background:var(--tag-bg);padding:.3rem .75rem;border-radius:999px;border:1px solid var(--border-light)}
.btn-logout{padding:.35rem .85rem;font-size:.8rem;color:var(--text-muted);background:transparent;border:1px solid var(--border);border-radius:8px;cursor:pointer;transition:all .15s}
.btn-logout:hover{color:var(--danger);border-color:var(--danger);background:color-mix(in srgb, var(--danger) 10%, transparent)}

/* ---- page transitions ---- */
.page-enter-active,.page-leave-active{transition:opacity .2s ease,transform .2s ease}
.page-enter-from{opacity:0;transform:translateY(8px)}
.page-leave-to{opacity:0;transform:translateY(-4px)}

/* ---- shared animations ---- */
@keyframes fadeInUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scaleIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes slideDown{from{opacity:0;max-height:0}to{opacity:1;max-height:600px}}
@keyframes ripple{0%{transform:scale(0);opacity:.4}100%{transform:scale(2.5);opacity:0}}

/* ---- button press ---- */
button:active:not(:disabled){transform:scale(.97);transition:transform .1s}
.ripple{position:relative;overflow:hidden}
.ripple::after{content:'';position:absolute;inset:0;background:radial-gradient(circle,var(--accent) 10%,transparent 10%);opacity:0;transition:opacity .4s}
.ripple:active::after{opacity:.2;transition:0s}

/* ---- modal animation ---- */
.modal-enter-active{animation:fadeIn .2s ease}
.modal-enter-active .modal-card,.modal-enter-active .mood-modal,.modal-enter-active .save-modal,.modal-enter-active .mini-modal{animation:fadeInUp .25s ease}

/* ---- toast ---- */
.toast-enter-active{animation:fadeInUp .3s ease}
.toast-leave-active{animation:fadeIn .2s ease reverse}

/* ---- list stagger ---- */
.list-enter-active{transition:all .3s ease}
.list-enter-from{opacity:0;transform:translateX(-12px)}
.list-leave-active{transition:all .2s ease;position:absolute}
.list-leave-to{opacity:0;transform:translateX(12px)}
.list-move{transition:transform .3s ease}

/* ---- folder expand ---- */
.folder-enter-active{animation:slideDown .3s ease}
.folder-leave-active{animation:slideDown .2s ease reverse}
</style>
