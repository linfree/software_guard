<template>
  <div>
    <a-typography-title>申请审核</a-typography-title>

    <!-- 过滤器 -->
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="8">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索软件名称"
          enter-button
          @search="loadRequests"
        />
      </a-col>
      <a-col :span="6">
        <a-select
          v-model:value="statusFilter"
          placeholder="筛选状态"
          style="width: 100%"
          allowClear
          @change="loadRequests"
        >
          <a-select-option value="pending">待审核</a-select-option>
          <a-select-option value="approved">已批准</a-select-option>
          <a-select-option value="rejected">已拒绝</a-select-option>
          <a-select-option value="processing">处理中</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="6">
        <a-select
          v-model:value="categoryFilter"
          placeholder="筛选分类"
          style="width: 100%"
          allowClear
          @change="loadRequests"
        >
          <a-select-option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </a-select-option>
        </a-select>
      </a-col>
    </a-row>

    <a-table
      :columns="columns"
      :data-source="filteredRequests"
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
        <template v-else-if="column.key === 'reviewComment'">
          <div v-if="record.review_comment">
            <a-tooltip v-if="isLongComment(record.review_comment)" :title="record.review_comment" placement="topLeft">
              <span class="comment-truncated">{{ getTruncatedComment(record.review_comment) }}</span>
            </a-tooltip>
            <span v-else class="comment-short">{{ record.review_comment }}</span>
          </div>
          <div v-else>-</div>
        </template>
        <template v-else-if="column.key === 'createdAt'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button
              v-if="record.status === 'pending'"
              type="primary"
              size="small"
              @click="reviewRequest(record, 'approved')"
            >
              批准
            </a-button>
            <a-button
              v-if="record.status === 'pending'"
              danger
              size="small"
              @click="reviewRequest(record, 'rejected')"
            >
              拒绝
            </a-button>
            <a-button size="small" @click="viewDetail(record)">
              查看详情
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 审核弹窗 -->
    <a-modal
      v-model:open="reviewModal"
      :title="reviewAction === 'approved' ? '批准申请' : '拒绝申请'"
      @ok="submitReview"
      :confirm-loading="reviewLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="审核意见">
          <a-textarea v-model:value="reviewComment" :rows="3" placeholder="请输入审核意见" />
        </a-form-item>
      </a-form>
      <template v-if="currentRequest">
        <a-descriptions :column="1" size="small">
          <a-descriptions-item label="软件名称">
            {{ currentRequest.software_name }}
          </a-descriptions-item>
          <a-descriptions-item label="版本">
            {{ currentRequest.version }}
          </a-descriptions-item>
          <a-descriptions-item label="下载链接">
            <a :href="currentRequest.download_url" target="_blank">
              {{ currentRequest.download_url }}
            </a>
          </a-descriptions-item>
          <a-descriptions-item label="描述">
            {{ currentRequest.description || '-' }}
          </a-descriptions-item>
          <a-descriptions-item v-if="currentRequest.review_comment && currentRequest.review_comment.includes('AI自动审核建议拒绝')" label="AI审核建议">
            <a-alert
              message="AI审核建议拒绝"
              :description="currentRequest.review_comment.split('\n')[0].replace('AI自动审核建议拒绝: ', '')"
              type="warning"
              show-icon
            />
          </a-descriptions-item>
        </a-descriptions>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { requestApi } from '@/api/request'
import { categoryApi } from '@/api/category'
import dayjs from 'dayjs'

const loading = ref(false)
const requests = ref([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

// 过滤器
const searchText = ref('')
const statusFilter = ref()
const categoryFilter = ref()
const categories = ref([])

const reviewModal = ref(false)
const reviewLoading = ref(false)
const reviewAction = ref('')
const reviewComment = ref('')
const currentRequest = ref(null)

const columns = [
  { title: '软件名称', key: 'softwareName', dataIndex: 'software_name' },
  { title: '版本', key: 'version', dataIndex: 'version' },
  { title: '申请人', key: 'applicantName', dataIndex: 'applicant_name' },
  { title: '分类', key: 'category', dataIndex: 'category' },
  { title: '状态', key: 'status' },
  { title: '审核意见', key: 'reviewComment', dataIndex: 'review_comment' },
  { title: '申请时间', key: 'createdAt' },
  { title: '操作', key: 'actions' }
]

// 前端过滤逻辑
const filteredRequests = computed(() => {
  let result = requests.value

  // 按软件名称搜索
  if (searchText.value) {
    result = result.filter(req =>
      req.software_name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  // 按状态过滤
  if (statusFilter.value) {
    result = result.filter(req => req.status === statusFilter.value)
  }

  // 按分类过滤
  if (categoryFilter.value) {
    result = result.filter(req => req.category === categoryFilter.value)
  }

  return result
})

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

// 判断评论是否过长（超过 30 个字符）
const isLongComment = (comment) => {
  return comment && comment.length > 30
}

// 获取截取后的评论（显示前 30 个字符 + 省略号）
const getTruncatedComment = (comment) => {
  if (!comment) return ''
  if (comment.includes('AI自动审核建议拒绝')) {
    // AI 审核建议特殊处理
    const lines = comment.split('\n')
    if (lines[0].length > 30) {
      return lines[0].substring(0, 30) + '...'
    }
    return lines[0] + '...'
  }
  return comment.length > 30 ? comment.substring(0, 30) + '...' : comment
}

const loadRequests = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    // 如果有状态过滤，传递给后端
    if (statusFilter.value) {
      params.status = statusFilter.value
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

const reviewRequest = (record, action) => {
  currentRequest.value = record
  reviewAction.value = action
  // 如果有AI审核建议，将其作为初始评论
  if (record.review_comment && record.review_comment.includes('AI自动审核建议拒绝')) {
    reviewComment.value = record.review_comment.split('\n')[0].replace('AI自动审核建议拒绝: ', '') + '\n'
  } else {
    reviewComment.value = ''
  }
  reviewModal.value = true
}

const submitReview = async () => {
  reviewLoading.value = true
  try {
    await requestApi.review(currentRequest.value.id, {
      status: reviewAction.value,
      comment: reviewComment.value
    })
    message.success(reviewAction.value === 'approved' ? '已批准' : '已拒绝')
    reviewModal.value = false
    loadRequests()
  } catch (error) {
    message.error('操作失败')
  } finally {
    reviewLoading.value = false
  }
}

const viewDetail = (record) => {
  // 显示详情
  currentRequest.value = record
  reviewComment.value = record.review_comment || ''
  reviewModal.value = true
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
})
</script>

<style scoped>
/* 搜索和过滤样式 */
:deep(.ant-input-search) {
  border-radius: var(--radius-md);
}

:deep(.ant-input-search-button) {
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

:deep(.ant-select-selector) {
  border-radius: var(--radius-md);
}

/* 标签样式 */
:deep(.ant-tag) {
  border-radius: var(--radius-sm);
  font-weight: var(--font-medium);
  border: none;
}

/* 按钮样式 */
:deep(.ant-btn-primary) {
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

:deep(.ant-btn-primary:hover) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 表格样式 */
:deep(.ant-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

:deep(.ant-table-thead > tr > th) {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
  border-bottom: 2px solid var(--color-border-primary);
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: var(--color-bg-tertiary);
}

/* 模态框样式 */
:deep(.ant-modal-content) {
  border-radius: var(--radius-lg);
}

:deep(.ant-modal-header) {
  border-bottom: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

:deep(.ant-modal-title) {
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

:deep(.ant-modal-footer) {
  border-top: 1px solid var(--color-border-primary);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

/* Alert 样式优化 */
:deep(.ant-alert) {
  border-radius: var(--radius-md);
}

/* 审核意见样式 */
.comment-truncated {
  color: var(--color-text-secondary);
  cursor: help;
  display: inline-block;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.comment-short {
  color: var(--color-text-secondary);
  display: inline-block;
  max-width: 300px;
}
</style>
