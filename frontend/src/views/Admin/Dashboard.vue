<template>
  <div>
    <a-typography-title>管理仪表板</a-typography-title>
    <a-row :gutter="16" style="margin-top: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic title="总用户数" :value="stats.totalUsers">
            <template #prefix><UserOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总软件数" :value="stats.totalSoftware">
            <template #prefix><AppstoreOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总下载次数" :value="stats.totalDownloads">
            <template #prefix><DownloadOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="待审核申请"
            :value="stats.pendingRequests"
            :value-style="{ color: stats.pendingRequests > 0 ? '#cf1322' : '' }"
          >
            <template #prefix><FileTextOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <a-divider />

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="热门软件 TOP 10">
          <a-list :data-source="topSoftware" size="small">
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    {{ index + 1 }}. {{ item.name }}
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-statistic :value="item.count" />
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="最近下载">
          <a-list :data-source="recentDownloads" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>{{ item.software_name }}</template>
                  <template #description>{{ item.username }} - {{ item.version }}</template>
                </a-list-item-meta>
                <template #actions>
                  <span>{{ formatDate(item.download_time) }}</span>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  UserOutlined,
  AppstoreOutlined,
  DownloadOutlined,
  FileTextOutlined
} from '@ant-design/icons-vue'
import { statsApi } from '@/api/stats'
import { downloadApi } from '@/api/download'
import dayjs from 'dayjs'

const stats = ref({
  totalUsers: 0,
  totalSoftware: 0,
  totalDownloads: 0,
  pendingRequests: 0
})

const topSoftware = ref([])
const recentDownloads = ref([])

const formatDate = (date) => {
  return dayjs(date).format('MM-DD HH:mm')
}

const loadStats = async () => {
  try {
    // 获取仪表板统计数据
    const dashboardStats = await statsApi.getDashboard()
    stats.value.totalUsers = dashboardStats.user_count || 0
    stats.value.totalSoftware = dashboardStats.software_count || 0
    stats.value.totalDownloads = dashboardStats.total_downloads || 0
    stats.value.pendingRequests = dashboardStats.pending_requests || 0

    // 获取下载统计中的热门软件
    const downloadStats = await downloadApi.getStats()
    topSoftware.value = downloadStats?.top_software || []
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 确保出错时数据仍然是有效的数组
    topSoftware.value = []
  }
}

const loadRecentDownloads = async () => {
  try {
    const data = await downloadApi.getLogs({ limit: 10 })
    // 确保 data 是数组
    if (Array.isArray(data)) {
      recentDownloads.value = data
    } else if (data && Array.isArray(data.items)) {
      recentDownloads.value = data.items
    } else {
      recentDownloads.value = []
    }
  } catch (error) {
    console.error('加载最近下载失败:', error)
    recentDownloads.value = []
  }
}

onMounted(() => {
  loadStats()
  loadRecentDownloads()
})
</script>

<style scoped>
/* 标题样式 */
:deep(.ant-typography h1) {
  font-size: 1.75rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-lg);
}

/* 统计卡片 */
:deep(.ant-card) {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  height: 100%;
}

:deep(.ant-card:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

:deep(.ant-card-head) {
  border-bottom: 1px solid var(--color-border-primary);
  background: var(--color-bg-secondary);
}

:deep(.ant-card-head-title) {
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

/* 统计数字样式 */
:deep(.ant-statistic) {
  padding: var(--space-sm) 0;
}

:deep(.ant-statistic-title) {
  font-size: 0.875rem;
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

:deep(.ant-statistic-content) {
  font-size: 1.75rem;
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

:deep(.ant-statistic-content-prefix),
:deep(.ant-statistic-content-suffix) {
  font-size: 1rem;
  color: var(--color-text-tertiary);
}

/* 列表样式 */
:deep(.ant-list-item) {
  border-bottom: 1px solid var(--color-border-secondary);
  padding: var(--space-md) 0;
  transition: background-color var(--transition-fast);
}

:deep(.ant-list-item:hover) {
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

:deep(.ant-list-item-meta-title) {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

:deep(.ant-list-item-meta-description) {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

/* 分割线 */
:deep(.ant-divider) {
  border-color: var(--color-border-primary);
  margin: var(--space-xl) 0;
}

/* 网格布局 */
:deep(.ant-col) {
  margin-bottom: var(--space-md);
}

/* 响应式 */
@media (max-width: 768px) {
  :deep(.ant-col) {
    width: 100%;
    margin-bottom: var(--space-md);
  }

  :deep(.ant-statistic-content) {
    font-size: 1.5rem;
  }
}
</style>