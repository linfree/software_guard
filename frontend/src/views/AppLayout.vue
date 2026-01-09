<template>
  <a-layout class="app-layout">
    <!-- 顶部导航栏 -->
    <a-layout-header class="app-header">
      <div class="header-container">
        <!-- Logo 和主导航 -->
        <div class="header-left">
          <RouterLink to="/" class="logo">
            <AppstoreOutlined class="logo-icon" />
            <span class="logo-text">Software Guard</span>
          </RouterLink>

          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="horizontal"
            :style="{ background: 'transparent', flex: 1 }"
            @select="handleMenuSelect"
          >
            <a-menu-item key="software">
              <AppstoreOutlined />
              软件库
            </a-menu-item>
          </a-menu>
        </div>

        <!-- 右侧用户区 -->
        <div class="header-right">
          <template v-if="userStore.token">
            <a-dropdown>
              <div class="user-info">
                <UserOutlined class="user-icon" />
                <span class="user-name">{{ userStore.userInfo?.username }}</span>
                <a-tag v-if="userStore.isAdmin()" color="red" size="small">管理员</a-tag>
                <a-tag v-else-if="userStore.isOps()" color="blue" size="small">运维</a-tag>
              </div>
              <template #overlay>
                <a-menu @click="handleUserMenuClick">
                  <a-menu-item key="profile">
                    <UserOutlined />
                    个人中心
                  </a-menu-item>
                  <a-menu-item key="downloads">
                    <DownloadOutlined />
                    下载记录
                  </a-menu-item>
                  <a-menu-item key="requests">
                    <FileTextOutlined />
                    我的申请
                  </a-menu-item>
                  <a-menu-divider v-if="userStore.isOps()" />
                  <a-menu-item key="admin" v-if="userStore.isOps()">
                    <SettingOutlined />
                    管理后台
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
          <template v-else>
            <a-button type="primary" @click="$router.push('/login')">
              登录
            </a-button>
          </template>
        </div>
      </div>
    </a-layout-header>

    <!-- 主内容区 -->
    <a-layout-content class="app-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </a-layout-content>

    <!-- 底部 -->
    <a-layout-footer class="app-footer">
      <div class="footer-content">
        <span>Software Guard © 2024</span>
        <span class="footer-divider">|</span>
        <span>公司内部软件下载站</span>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  AppstoreOutlined,
  DownloadOutlined,
  FileTextOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const selectedKeys = ref([])

// 监听路由变化更新选中状态
watch(() => route.path, (newPath) => {
  if (newPath === '/' || newPath.startsWith('/software')) {
    selectedKeys.value = ['software']
  } else {
    selectedKeys.value = []
  }
}, { immediate: true })

const handleMenuSelect = ({ key }) => {
  if (key === 'software') {
    router.push('/software')
  }
}

const handleUserMenuClick = ({ key }) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'downloads':
      router.push('/my-downloads')
      break
    case 'requests':
      router.push('/requests')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      userStore.logout()
      message.success('已退出登录')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.app-header {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
  padding: 0;
  line-height: normal;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.logo-text {
  font-size: 1.25rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.user-info:hover {
  background-color: var(--color-bg-tertiary);
}

.user-icon {
  font-size: 1rem;
  color: var(--color-text-secondary);
}

.user-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

/* 菜单样式 */
:deep(.ant-menu) {
  border-bottom: none;
}

:deep(.ant-menu-item) {
  border-radius: var(--radius-md);
  margin: 0 var(--space-xs);
  transition: all var(--transition-fast);
}

:deep(.ant-menu-item-selected) {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

:deep(.ant-menu-item:hover) {
  background-color: var(--color-bg-tertiary);
}

:deep(.ant-menu-horizontal),
:deep(.ant-menu-item) {
  line-height: 64px;
}

/* 主内容区 */
.app-content {
  flex: 1;
  background-color: var(--color-bg-primary);
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
  min-height: calc(100vh - 64px - 70px);
}

/* 底部 */
.app-footer {
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-primary);
  text-align: center;
  padding: var(--space-lg) 0;
}

.footer-content {
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

.footer-divider {
  margin: 0 var(--space-md);
}

/* 下拉菜单样式 */
:deep(.ant-dropdown-menu) {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border-primary);
}

:deep(.ant-dropdown-menu-item) {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  margin: var(--space-xs) var(--space-sm);
}

:deep(.ant-dropdown-menu-item:hover) {
  background-color: var(--color-bg-tertiary);
}

:deep(.ant-dropdown-menu-item-divider) {
  margin: var(--space-xs) 0;
}
</style>
