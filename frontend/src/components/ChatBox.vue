<template>
  <div class="chat-box">
    <div class="messages" ref="msgBox">
      <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="msg assistant">
        <div class="avatar">AI</div>
        <div class="bubble"><span class="cursor">|</span></div>
      </div>
    </div>
    <div class="input-area">
      <input v-model="input" @keydown.enter="send" placeholder="输入您的问题..." :disabled="loading" />
      <button @click="send" :disabled="loading || !input.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { chatClient } from '../api.js'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const msgBox = ref(null)

function scrollBottom() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

function send() {
  const q = input.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', content: q })
  input.value = ''
  loading.value = true
  scrollBottom()

  let aiMsg = { role: 'assistant', content: '' }
  messages.value.push(aiMsg)

  chatClient(
    q,
    (chunk) => {
      aiMsg.content += chunk
      scrollBottom()
    },
    (data) => {
      loading.value = false
      scrollBottom()
    },
    (err) => {
      aiMsg.content = `错误: ${err}`
      loading.value = false
      scrollBottom()
    }
  )
}
</script>

<style scoped>
.chat-box {
  display: flex; flex-direction: column; height: 100vh;
  max-width: 800px; margin: 0 auto; background: #f5f5f5;
}
.messages {
  flex: 1; overflow-y: auto; padding: 20px;
}
.msg { display: flex; gap: 10px; margin-bottom: 16px; }
.msg.user { flex-direction: row-reverse; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%; display: flex;
  align-items: center; justify-content: center; font-size: 14px;
  color: white; flex-shrink: 0;
}
.msg.user .avatar { background: #1890ff; }
.msg.assistant .avatar { background: #52c41a; }
.bubble {
  max-width: 70%; padding: 10px 14px; border-radius: 12px; line-height: 1.6;
  white-space: pre-wrap; word-break: break-word;
}
.msg.user .bubble { background: #1890ff; color: white; }
.msg.assistant .bubble { background: white; color: #333; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.cursor { animation: blink 1s infinite; }
@keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }
.input-area {
  display: flex; padding: 16px; background: white; border-top: 1px solid #e8e8e8;
}
.input-area input {
  flex: 1; padding: 10px 14px; border: 1px solid #d9d9d9; border-radius: 8px;
  font-size: 15px; outline: none;
}
.input-area input:focus { border-color: #1890ff; }
.input-area button {
  margin-left: 10px; padding: 10px 24px; background: #1890ff; color: white;
  border: none; border-radius: 8px; font-size: 15px; cursor: pointer;
}
.input-area button:disabled { background: #ccc; cursor: not-allowed; }
</style>