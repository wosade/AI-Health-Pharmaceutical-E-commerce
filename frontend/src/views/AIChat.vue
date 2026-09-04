<template>
  <div class="chat-page">
    <ChatBox />
  </div>
</template>

<script setup>
import ChatBox from '../components/ChatBox.vue'
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}
</style>