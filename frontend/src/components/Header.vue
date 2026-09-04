<template>
  <header class="top-bar">
    <div class="header-left">
      <h2 class="page-title">{{ $route.meta.title }}</h2>
    </div>
    <div class="header-right">
      <div class="status-indicator">
        <span class="status-dot" :class="backendStatus"></span>
        <span>{{ backendStatus === 'online' ? '服务正常' : '服务离线' }}</span>
      </div>
      <a-dropdown>
        <div class="admin-info">
          <a-avatar :size="32" style="background-color: #1890ff">
            <template #icon><UserOutlined /></template>
          </a-avatar>
          <span class="admin-name">{{ userName }}</span>
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="logout" @click="handleLogout">
              <LogoutOutlined />
              <span style="margin-left: 8px">退出登录</span>
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, LogoutOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import axios from 'axios'

const router = useRouter()
const backendStatus = ref('offline')
const userName = ref('管理员')

onMounted(async () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      userName.value = user.nickname || user.username || '管理员'
    }
    await axios.get('/health')
    backendStatus.value = 'online'
  } catch {
    backendStatus.value = 'offline'
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
  message.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.top-bar {
  height: var(--header-height);
  background: #fff;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d9d9d9;
}

.status-dot.online {
  background: #52c41a;
}

.status-dot.offline {
  background: #ff4d4f;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.3s;
}

.admin-info:hover {
  background: #f5f5f5;
}

.admin-name {
  font-size: 14px;
  color: var(--text);
}
</style>