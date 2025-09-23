<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f8fafc;
}

#app {
  height: 100vh;
  overflow: hidden;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .character-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .header-actions {
    order: -1;
    justify-content: center;
  }
  
  .character-grid {
    grid-template-columns: 1fr;
  }
  
  .message-content {
    max-width: 85% !important;
  }
  
  .input-area {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .character-selector {
    margin: 1rem;
    padding: 1rem;
  }
  
  .input-box {
    gap: 0.25rem;
  }
  
  .voice-btn, .send-btn {
    width: 45px;
    height: 45px;
  }
}
</style>
