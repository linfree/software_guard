<template>
  <div>
    <a-typography-title>我的申请</a-typography-title>
    <a-button type="primary" @click="showRequestModal = true" style="margin-bottom: 16px;">
      <template #icon><PlusOutlined /></template>
      申请软件
    </a-button>
    
    <a-table
      :columns="columns"
      :data-source="requests"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'createdAt'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'reviewComment'">
          <a-tooltip v-if="record.review_comment" :title="record.review_comment">
            {{ record.review_comment?.substring(0, 20) }}...
          </a-tooltip>
          <span v-else>-</span>
        </template>
      </template>
    </a-table>

    <!-- 申请软件弹窗 -->
    <a-modal
      v-model:open="showRequestModal"
      title="申请软件"
      @ok="handleRequest"
      :confirm-loading="requestLoading"
      width="600px"
    >
      <a-form :model="requestForm" layout="vertical">
        <a-form-item label="软件名称" required>
          <a-auto-complete
            v-model:value="requestForm.software_name"
            :options="softwareOptions"
            placeholder="输入或选择软件名称"
            @search="handleSoftwareSearch"
            @select="handleSoftwareSelect"
            style="width: 100%"
          >
            <template #option="{ name, category }">
              <div>
                <span>{{ name }}</span>
                <a-tag style="margin-left: 8px">{{ category }}</a-tag>
              </div>
            </template>
          </a-auto-complete>
          <div v-if="selectedSoftware" style="margin-top: 8px; color: #52c41a;">
            <CheckCircleOutlined /> 已选择现有软件：{{ selectedSoftware.name }}
          </div>
        </a-form-item>
        <a-form-item label="版本" required>
          <a-input v-model:value="requestForm.version" placeholder="请输入版本号" />
        </a-form-item>
        <a-form-item label="下载链接" required>
          <a-input v-model:value="requestForm.download_url" placeholder="请输入官方下载链接" />
        </a-form-item>
        <a-form-item label="分类">
          <a-select v-model:value="requestForm.category" placeholder="请选择分类">
            <a-select-option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="Logo URL" v-if="!selectedSoftware">
          <a-input v-model:value="requestForm.logo" placeholder="请输入 Logo 图片的 URL 地址（可选）" />
          <div style="margin-top: 4px; color: #999; font-size: 12px;">提示：申请通过后也可在软件详情页上传Logo文件</div>
        </a-form-item>
        <a-form-item label="官网链接">
          <a-input v-model:value="requestForm.official_url" placeholder="https://" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="requestForm.description" :rows="3" placeholder="请输入软件描述" />
        </a-form-item>
      </a-form>
      <a-alert v-if="selectedSoftware" message="将添加新版本到已有软件" type="info" show-icon />
      <a-alert v-else message="将创建新软件记录" type="info" show-icon />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, CheckCircleOutlined } from '@ant-design/icons-vue'
import { requestApi } from '@/api/request'
import { softwareApi } from '@/api/software'
import { categoryApi } from '@/api/category'
import dayjs from 'dayjs'

const loading = ref(false)
const requests = ref([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

// 申请软件相关变量
const showRequestModal = ref(false)
const requestLoading = ref(false)
const requestForm = ref({
  software_name: '',
  version: '',
  download_url: '',
  category: undefined,
  logo: '',
  official_url: '',
  description: ''
})

const categories = ref([])

const softwareOptions = ref([])
const selectedSoftware = ref(null)
const allSoftware = ref([])

// 自动刷新相关变量
const refreshInterval = ref(null)
const refreshIntervalTime = 10000 // 10秒刷新一次

const columns = [
  { title: '软件名称', key: 'softwareName', dataIndex: 'software_name' },
  { title: '版本', key: 'version', dataIndex: 'version' },
  { title: '分类', key: 'category', dataIndex: 'category' },
  { title: '状态', key: 'status' },
  { title: '审核意见', key: 'reviewComment' },
  { title: '申请时间', key: 'createdAt' }
]

const getStatusColor = (status) => {
  const colors = {
    pending: 'blue',
    approved: 'green',
    rejected: 'red',
    processing: 'orange'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝',
    processing: '处理中'
  }
  return texts[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadRequests = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    const data = await requestApi.list(params)
    requests.value = data?.items || data || []
    pagination.value.total = data?.total || 0
  } catch (error) {
    console.error('加载申请列表失败:', error)
    requests.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.value.current = pag.current
  loadRequests()
}

// 加载软件列表用于自动完成
const loadSoftwareList = async () => {
  try {
    const data = await softwareApi.list({ limit: 100 })
    allSoftware.value = data?.items || data || []
  } catch (error) {
    console.error('加载软件列表失败:', error)
    allSoftware.value = []
  }
}

const handleSoftwareSearch = (value) => {
  if (!value) {
    softwareOptions.value = []
    return
  }
  // 搜索匹配的软件
  const filtered = allSoftware.value
    .filter(sw => sw.name.toLowerCase().includes(value.toLowerCase()))
    .slice(0, 10)
    .map(sw => ({
      value: sw.name,
      name: sw.name,
      category: sw.category || '未分类'
    }))
  softwareOptions.value = filtered
}

const handleSoftwareSelect = (value) => {
  const software = allSoftware.value.find(sw => sw.name === value)
  if (software) {
    selectedSoftware.value = software
    requestForm.value.category = software.category
  }
}

const handleRequest = async () => {
  if (!requestForm.value.software_name || !requestForm.value.version || !requestForm.value.download_url) {
    message.error('请填写必填项')
    return
  }

  requestLoading.value = true
  try {
    // 清理空字符串的URL字段
    const cleanedData = {
      ...requestForm.value,
      logo: requestForm.value.logo?.trim() || null,
      official_url: requestForm.value.official_url?.trim() || null
    }

    await requestApi.create(cleanedData)
    message.success('申请已提交，请等待审核')
    showRequestModal.value = false
    // 重置表单
    requestForm.value = {
      software_name: '',
      version: '',
      download_url: '',
      category: undefined,
      logo: '',
      official_url: '',
      description: ''
    }
    selectedSoftware.value = null
    // 重新加载申请列表
    loadRequests()
  } catch (error) {
    // 提供更友好的错误提示
    if (error.response?.data?.detail) {
      const errorDetail = error.response.data.detail;
      if (Array.isArray(errorDetail)) {
        const firstError = errorDetail[0];
        if (firstError.msg && firstError.msg.includes('URL')) {
          message.error('请输入有效的URL地址');
        } else {
          message.error(firstError.msg || '申请失败');
        }
      } else {
        message.error(errorDetail || '申请失败');
      }
    } else {
      message.error('申请失败，请检查输入信息');
    }
  } finally {
    requestLoading.value = false
  }
}

// 开始自动刷新
const startAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  refreshInterval.value = setInterval(() => {
    loadRequests()
  }, refreshIntervalTime)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getAllNames()
  } catch (error) {
    console.error('加载软件类型失败:', error)
  }
}

onMounted(() => {
  loadCategories()
  loadRequests()
  loadSoftwareList()
  // 开始自动刷新
  startAutoRefresh()
})

// 组件卸载时停止自动刷新
onUnmounted(() => {
  stopAutoRefresh()
})
</script>