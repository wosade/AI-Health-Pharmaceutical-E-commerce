<template>
  <div class="chat-container">
    <div class="chat-header">
      <RobotOutlined style="font-size: 20px; color: #1890ff" />
      <span>AI 智能助手</span>
      <a-tag color="blue">在线</a-tag>
    </div>

    <div class="chat-messages" ref="msgBox">
      <div v-if="messages.length === 0" class="welcome">
        <div class="welcome-icon">
          <RobotOutlined style="font-size: 48px; color: #bfbfbf" />
        </div>
        <p>你好！我是药智通 AI 助手</p>
        <p class="welcome-hint">可以帮你查询商品、订单、用户信息，试试问我吧</p>
      </div>

      <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
        <a-avatar
          :size="36"
          :style="{
            backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
            flexShrink: 0,
          }"
        >
          <template #icon>
            <UserOutlined v-if="msg.role === 'user'" />
            <RobotOutlined v-else />
          </template>
        </a-avatar>
        <div class="msg-content">{{ msg.content }}</div>
      </div>

      <div v-if="streaming" class="message assistant">
        <a-avatar :size="36" style="background-color: #52c41a; flex-shrink: 0">
          <template #icon><RobotOutlined /></template>
        </a-avatar>
        <div class="msg-content">
          {{ streamText }}<span class="cursor">|</span>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <a-textarea
        v-model:value="input"
        :auto-size="{ minRows: 1, maxRows: 4 }"
        placeholder="输入问题，按 Enter 发送..."
        :disabled="streaming"
        @press-enter="send"
      />
      <a-button
        type="primary"
        :loading="streaming"
        :disabled="!input.trim()"
        @click="send"
        style="height: 40px"
      >
        <template #icon><SendOutlined /></template>
        发送
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { RobotOutlined, UserOutlined, SendOutlined } from '@ant-design/icons-vue'
import { adminChat } from '../api/agent.js'

const messages = ref([])
const input = ref('')
const streaming = ref(false)
const streamText = ref('')
const msgBox = ref(null)

async function send() {
  const q = input.value.trim()
  if (!q || streaming.value) return

  messages.value.push({ role: 'user', content: q })
  input.value = ''
  streaming.value = true
  streamText.value = ''

  await nextTick()
  scrollBottom()

  try {
    const res = await adminChat(q)
    if (res.answer) {
      messages.value.push({ role: 'assistant', content: res.answer })
    } else {
      messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用' })
    }
  } catch {
    messages.value.push({ role: 'assistant', content: '连接失败，请检查服务是否正常运行' })
  }

  streaming.value = false
  streamText.value = ''
}

function scrollBottom() {
  if (msgBox.value) {
    msgBox.value.scrollTop = msgBox.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px 0 rgba(0,0,0,0.03), 0 1px 6px -1px rgba(0,0,0,0.02), 0 2px 4px 0 rgba(0,0,0,0.02);
  overflow: hidden;
  height: calc(100vh - 152px);
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(0,0,0,0.85);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #fafafa;
}

.welcome {
  text-align: center;
  padding: 80px 20px;
  color: rgba(0,0,0,0.45);
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome p {
  font-size: 16px;
  margin-bottom: 4px;
}

.welcome-hint {
  font-size: 13px;
  margin-top: 8px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.msg-content {
  max-width: 70%;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .msg-content {
  background: #e6f7ff;
  color: rgba(0,0,0,0.85);
  border-radius: 8px 4px 8px 8px;
}

.message.assistant .msg-content {
  background: #fff;
  color: rgba(0,0,0,0.85);
  border: 1px solid #f0f0f0;
  border-radius: 4px 8px 8px 8px;
}

.cursor {
  animation: blink 1s infinite;
  color: #1890ff;
}

@keyframes blink {
  50% { opacity: 0; }
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  align-items: flex-end;
}
</style>