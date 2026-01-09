<template>
  <div>
    <a-typography-title>下载记录</a-typography-title>
    <a-table
      :columns="columns"
      :data-source="downloads"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'downloadTime'">
          {{ formatDate(record.download_time) }}
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import api from '@/api/index'
import dayjs from 'dayjs'

const loading = ref(false)
const downloads = ref([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const columns = [
  { title: '软件名称', key: 'softwareName', dataIndex: 'software_name' },
  { title: '版本', key: 'version', dataIndex: 'version' },
  { title: '下载时间', key: 'downloadTime' }
]

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const loadDownloads = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    const data = await api.get('/downloads/logs', { params })
    downloads.value = data?.items || data || []
    pagination.value.total = data?.total || 0
  } catch (error) {
    console.error('加载下载记录失败:', error)
    downloads.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.value.current = pag.current
  loadDownloads()
}

onMounted(() => {
  loadDownloads()
})
</script>
