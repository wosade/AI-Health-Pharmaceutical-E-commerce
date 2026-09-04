<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-card">
        <div class="login-form-wrapper">
          <div class="login-logo">
            <img src="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg" alt="logo" />
          </div>
          <h1 class="login-title">药智通后台管理系统</h1>
          <p class="login-desc">更高效、更现代的医药管理解决方案</p>

          <a-form
            :model="formState"
            :rules="rules"
            ref="formRef"
            @finish="handleSubmit"
            style="margin-top: 24px"
          >
            <a-form-item name="username">
              <a-input
                v-model:value="formState.username"
                size="large"
                placeholder="请输入用户名"
              >
                <template #prefix>
                  <UserOutlined style="color: #1890ff" />
                </template>
              </a-input>
            </a-form-item>

            <a-form-item name="password">
              <a-input-password
                v-model:value="formState.password"
                size="large"
                placeholder="请输入密码"
              >
                <template #prefix>
                  <LockOutlined style="color: #1890ff" />
                </template>
              </a-input-password>
            </a-form-item>

            <a-form-item>
              <div class="login-extra">
                <a-checkbox v-model:checked="formState.autoLogin">自动登录</a-checkbox>
                <a class="forgot-link">忘记密码？</a>
              </div>
            </a-form-item>

            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                :loading="loading"
                block
                class="login-btn"
              >
                进入系统
              </a-button>
            </a-form-item>
          </a-form>
        </div>
      </div>
    </div>
    <div class="login-footer">
      <div class="footer-text">药智通 ©2024 医药智能管理系统</div>
      <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" class="beian-link">
        陕ICP备2023007009号-2
      </a>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import axios from 'axios'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const formState = reactive({
  username: 'admin',
  password: '',
  autoLogin: true,
})

const rules = {
  username: [{ required: true, message: '请输入用户名！', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码！', trigger: 'blur' }],
}

const handleSubmit = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/auth/login', {
      username: formState.username,
      password: formState.password,
    })
    if (res.data.code === 200) {
      localStorage.setItem('token', res.data.data.accessToken)
      localStorage.setItem('refreshToken', res.data.data.refreshToken)
      localStorage.setItem('user', JSON.stringify(res.data.data.user))
      message.success('登录成功！')
      router.push('/')
    } else {
      message.error(res.data.message || '登录失败')
    }
  } catch (err) {
    message.error(err.response?.data?.detail || '登录失败，请重试！')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: auto;
  background: #f0f2f5;
  background-image: url('https://mdn.alipayobjects.com/yuyan_qk0oxh/afts/img/V-_oS6r-i7wAAAAAAAAAAAAAFl94AQBr');
  background-size: 100% 100%;
  position: relative;
}

.login-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
  z-index: 1;
}

.login-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 12px;
  width: 400px;
  max-width: 90vw;
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.login-form-wrapper {
  padding: 24px;
}

.login-logo {
  text-align: center;
  margin-bottom: 16px;
}

.login-logo img {
  width: 48px;
  height: 48px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  text-align: center;
  margin: 0 0 8px;
}

.login-desc {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  text-align: center;
  margin: 0 0 32px;
}

.warning-banner {
  margin-top: -12px;
  margin-bottom: 24px;
  text-align: center;
  font-size: 12px;
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.06);
  padding: 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 77, 79, 0.1);
}

.login-extra {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.forgot-link {
  color: #1890ff;
  font-size: 14px;
}

.login-btn {
  height: 45px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 12px;
}

.login-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding-bottom: 24px;
}

.footer-text {
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
  margin-bottom: 8px;
}

.beian-link {
  display: block;
  width: fit-content;
  margin: 0 auto 16px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  line-height: 20px;
  text-decoration: none;
}

.beian-link:hover {
  color: #1890ff;
}
</style>