<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>Software Guard</h1>
        <p>公司内网软件下载站</p>
      </div>
      <a-form
        :model="loginForm"
        @finish="handleLogin"
        layout="vertical"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input
            v-model:value="loginForm.username"
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>
        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password
            v-model:value="loginForm.password"
            placeholder="请输入密码"
            size="large"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginForm = ref({
  username: '',
  password: ''
})

const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.login(loginForm.value)
    message.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  padding: var(--space-md);
}

.login-box {
  width: 100%;
  max-width: 420px;
  padding: var(--space-2xl);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.login-header h1 {
  font-size: 2rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
  letter-spacing: -0.02em;
}

.login-header p {
  color: var(--color-text-secondary);
  font-size: 0.9375rem;
  margin-bottom: 0;
}

/* 表单样式优化 */
.login-box :deep(.ant-form-item) {
  margin-bottom: var(--space-lg);
}

.login-box :deep(.ant-form-item-label > label) {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.login-box :deep(.ant-input),
.login-box :deep(.ant-input-password) {
  border-radius: var(--radius-md);
  border-color: var(--color-border-primary);
  padding: var(--space-sm) var(--space-md);
  transition: all var(--transition-normal);
}

.login-box :deep(.ant-input:focus),
.login-box :deep(.ant-input-password:focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.login-box :deep(.ant-input-affix-wrapper) {
  border-radius: var(--radius-md);
  border-color: var(--color-border-primary);
}

.login-box :deep(.ant-input-affix-wrapper-focused) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* 登录按钮 */
.login-box :deep(.ant-btn-primary) {
  height: 44px;
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  font-size: 1rem;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.login-box :deep(.ant-btn-primary:hover:not(:disabled)) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.login-box :deep(.ant-btn-primary:active:not(:disabled)) {
  transform: translateY(0);
}

/* 图标样式 */
.login-box :deep(.anticon) {
  color: var(--color-text-tertiary);
}
</style>
