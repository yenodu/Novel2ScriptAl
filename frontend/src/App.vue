<template>
  <div id="app-container">
    <header class="app-header">
      <h1>Novel2ScriptAl</h1>
      <p class="subtitle">小说转剧本工具</p>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// App-level setup — keep minimal; page logic lives in views.
</script>

<style>
/* Global reset & base styles */
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
  text-align: center;
  margin-bottom: 2rem;
}

.app-header h1 {
  font-size: 2rem;
  color: #0f172a;
}

.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
}
</style>
