<template>
  <div class="profile-container">
    <!-- 用户信息卡片 -->
    <a-card class="user-card">
      <div class="user-header">
        <div class="user-avatar">
          <UserOutlined />
        </div>
        <div class="user-details">
          <h2 class="user-name">{{ userStore.userInfo?.username }}</h2>
          <a-space>
            <a-tag v-if="userStore.isAdmin()" color="red">管理员</a-tag>
            <a-tag v-else-if="userStore.isOps()" color="blue">运维</a-tag>
            <a-tag v-else color="default">普通用户</a-tag>
          </a-space>
        </div>
      </div>
    </a-card>

    <!-- 功能菜单 -->
    <a-row :gutter="16" class="menu-grid">
      <a-col :xs="24" :sm="12" :md="8">
        <a-card class="menu-card" hoverable @click="$router.push('/requests')">
          <div class="menu-item">
            <div class="menu-icon">
              <FileTextOutlined />
            </div>
            <div class="menu-content">
              <h3>我的申请</h3>
              <p>查看软件申请记录和审核状态</p>
            </div>
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :sm="12" :md="8">
        <a-card class="menu-card" hoverable @click="$router.push('/my-downloads')">
          <div class="menu-item">
            <div class="menu-icon">
              <DownloadOutlined />
            </div>
            <div class="menu-content">
              <h3>下载记录</h3>
              <p>查看历史下载记录</p>
            </div>
          </div>
        </a-card>
      </a-col>

      <a-col :xs="24" :sm="12" :md="8" v-if="userStore.isOps()">
        <a-card class="menu-card" hoverable @click="$router.push('/admin')">
          <div class="menu-item">
            <div class="menu-icon admin">
              <SettingOutlined />
            </div>
            <div class="menu-content">
              <h3>管理后台</h3>
              <p>进入运维管理面板</p>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 统计信息 -->
    <a-card class="stats-card" title="我的统计">
      <a-row :gutter="16">
        <a-col :span="8">
          <a-statistic title="申请总数" :value="stats.totalRequests">
            <template #prefix><FileTextOutlined /></template>
          </a-statistic>
        </a-col>
        <a-col :span="8">
          <a-statistic title="下载总数" :value="stats.totalDownloads">
            <template #prefix><DownloadOutlined /></template>
          </a-statistic>
        </a-col>
        <a-col :span="8">
          <a-statistic title="待审核" :value="stats.pendingRequests">
            <template #prefix><ClockCircleOutlined /></template>
          </a-statistic>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { requestApi } from '@/api/request'
import { downloadApi } from '@/api/download'
import {
  UserOutlined,
  FileTextOutlined,
  DownloadOutlined,
  SettingOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue'

const userStore = useUserStore()

const stats = ref({
  totalRequests: 0,
  totalDownloads: 0,
  pendingRequests: 0
})

// 加载用户统计数据
const loadStats = async () => {
  try {
    // 并行获取申请和下载数据
    const [requestsData, downloadsData] = await Promise.all([
      requestApi.list({ limit: 100 }).catch(() => ({ items: [], total: 0 })),
      downloadApi.getLogs({ limit: 1 }).catch(() => ({ total: 0 }))
    ])

    // 计算统计数据
    const requests = requestsData?.items || requestsData || []
    const totalReq = requestsData?.total !== undefined ? requestsData.total : requests.length
    const pendingReq = requests.filter(r => r.status === 'pending').length
    const totalDown = downloadsData?.total || 0

    stats.value = {
      totalRequests: totalReq,
      totalDownloads: totalDown,
      pendingRequests: pendingReq
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 保持默认值
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 用户信息卡片 */
.user-card {
  margin-bottom: var(--space-lg);
  border-radius: var(--radius-lg);
}

.user-header {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  box-shadow: var(--shadow-md);
}

.user-details {
  flex: 1;
}

.user-name {
  margin: 0 0 var(--space-sm) 0;
  font-size: 1.5rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

/* 功能菜单 */
.menu-grid {
  margin-bottom: var(--space-lg);
}

.menu-card {
  border-radius: var(--radius-lg);
  height: 100%;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.menu-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.menu-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--color-primary-light);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.menu-icon.admin {
  background: #FFF7E6;
  color: #FA8C16;
}

.menu-content h3 {
  margin: 0 0 var(--space-xs) 0;
  font-size: 1.125rem;
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.menu-content p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* 统计卡片 */
.stats-card {
  border-radius: var(--radius-lg);
}

:deep(.ant-statistic) {
  padding: var(--space-md) 0;
}

:deep(.ant-statistic-title) {
  font-size: 0.875rem;
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

:deep(.ant-statistic-content) {
  font-size: 2rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

:deep(.ant-statistic-content-prefix) {
  font-size: 1rem;
  color: var(--color-text-tertiary);
  margin-right: var(--space-xs);
}

/* 响应式 */
@media (max-width: 768px) {
  .user-header {
    flex-direction: column;
    text-align: center;
  }

  .menu-grid .ant-col {
    margin-bottom: var(--space-md);
  }

  :deep(.ant-statistic-content) {
    font-size: 1.5rem;
  }
}
</style>
