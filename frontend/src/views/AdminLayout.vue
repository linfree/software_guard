<template>
  <a-layout class="admin-layout">
    <!-- 顶部导航 -->
    <a-layout-header class="admin-header">
      <div class="header-left">
        <div class="logo" @click="$router.push('/')">
          <AppstoreOutlined />
          <span>Software Guard</span>
          <a-tag color="blue" size="small" style="margin-left: 8px">管理后台</a-tag>
        </div>
      </div>
      <div class="header-right">
        <a-button type="text" @click="$router.push('/')">
          <template #icon><HomeOutlined /></template>
          返回前台
        </a-button>
        <a-divider type="vertical" />
        <a-dropdown>
          <div class="user-info">
            <UserOutlined />
            <span>{{ userStore.userInfo?.username }}</span>
          </div>
          <template #overlay>
            <a-menu @click="handleUserMenuClick">
              <a-menu-item key="profile">
                <UserOutlined />
                个人中心
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">
                <LogoutOutlined />
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <a-layout>
      <!-- 侧边栏 -->
      <a-layout-sider
        :width="240"
        class="admin-sider"
        :style="{ overflow: 'auto', height: 'calc(100vh - 64px)', position: 'sticky', top: '64px' }"
      >
        <a-menu
          v-model:selectedKeys="selectedKeys"
          v-model:openKeys="openKeys"
          mode="inline"
          :style="{ height: '100%', borderRight: 0 }"
          @select="handleMenuSelect"
        >
          <a-menu-item key="dashboard">
            <DashboardOutlined />
            <span>仪表板</span>
          </a-menu-item>

          <a-menu-item key="requests">
            <FileTextOutlined />
            <span>申请审核</span>
          </a-menu-item>

          <a-menu-item key="vulnerabilities">
            <SafetyOutlined />
            <span>漏洞管理</span>
          </a-menu-item>

          <a-menu-item key="categories">
            <TagsOutlined />
            <span>软件类型</span>
          </a-menu-item>

          <a-menu-item key="config">
            <SettingOutlined />
            <span>配置管理</span>
          </a-menu-item>

          <a-menu-item key="users" v-if="userStore.isAdmin()">
            <TeamOutlined />
            <span>用户管理</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>

      <!-- 内容区 -->
      <a-layout-content class="admin-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  AppstoreOutlined,
  HomeOutlined,
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SafetyOutlined,
  SettingOutlined,
  TeamOutlined,
  TagsOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const selectedKeys = ref(['dashboard'])
const openKeys = ref([])

// 监听路由变化更新选中状态
watch(() => route.path, (newPath) => {
  if (newPath === '/admin' || newPath === '/admin/') {
    selectedKeys.value = ['dashboard']
  } else if (newPath.includes('requests')) {
    selectedKeys.value = ['requests']
  } else if (newPath.includes('vulnerabilities')) {
    selectedKeys.value = ['vulnerabilities']
  } else if (newPath.includes('categories')) {
    selectedKeys.value = ['categories']
  } else if (newPath.includes('config')) {
    selectedKeys.value = ['config']
  } else if (newPath.includes('users')) {
    selectedKeys.value = ['users']
  } else {
    selectedKeys.value = ['dashboard']
  }
}, { immediate: true })

const handleMenuSelect = ({ key }) => {
  switch (key) {
    case 'dashboard':
      router.push('/admin')
      break
    case 'requests':
      router.push('/admin/requests')
      break
    case 'vulnerabilities':
      router.push('/admin/vulnerabilities')
      break
    case 'categories':
      router.push('/admin/categories')
      break
    case 'config':
      router.push('/admin/config')
      break
    case 'users':
      router.push('/admin/users')
      break
  }
}

const handleUserMenuClick = ({ key }) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
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
.admin-layout {
  min-height: 100vh;
}

/* 顶部导航 */
.admin-header {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
  padding: 0 var(--space-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-left .logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  font-size: 1.125rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  transition: opacity var(--transition-fast);
}

.header-left .logo:hover {
  opacity: 0.8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
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

/* 侧边栏 */
.admin-sider {
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-primary);
}

:deep(.ant-menu) {
  border-right: none;
}

:deep(.ant-menu-item) {
  margin: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

:deep(.ant-menu-item-selected) {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

:deep(.ant-menu-item:hover) {
  background-color: var(--color-bg-tertiary);
}

/* 内容区 */
.admin-content {
  background: var(--color-bg-primary);
}

.content-wrapper {
  padding: var(--space-xl);
  min-height: calc(100vh - 64px);
}
</style>
