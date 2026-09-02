<template>
  <div class="app">
    <header class="header">
      <h1>药智通 AI 助手</h1>
      <span class="badge">客户端</span>
    </header>
    <ChatBox />
  </div>
</template>

<script setup>
import ChatBox from './components/ChatBox.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app { height: 100vh; display: flex; flex-direction: column; }
.header {
  display: flex; align-items: center; gap: 10px; padding: 12px 20px;
  background: white; border-bottom: 1px solid #e8e8e8;
}
.header h1 { font-size: 18px; color: #333; }
.badge {
  font-size: 12px; padding: 2px 8px; border-radius: 4px;
  background: #e6f7ff; color: #1890ff;
}
</style>