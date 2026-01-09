<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px; align-items: center">
      <a-col :span="userStore.isOps() ? 10 : 12">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索软件名称"
          enter-button
          @search="loadSoftware"
        />
      </a-col>
      <a-col :span="userStore.isOps() ? 6 : 6">
        <a-select
          v-model:value="selectedCategory"
          placeholder="选择分类"
          style="width: 100%"
          allowClear
          @change="loadSoftware"
        >
          <a-select-option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </a-select-option>
        </a-select>
      </a-col>
      <a-col :span="2" v-if="userStore.isOps()">
        <a-button type="primary" @click="showUploadModal = true">
          <template #icon><UploadOutlined /></template>
          上传软件
        </a-button>
      </a-col>
      <a-col :span="userStore.isOps() ? 6 : 6" style="text-align: right; display: flex; justify-content: flex-end; align-items: center">
        <a-radio-group v-model:value="viewMode" button-style="solid">
          <a-radio-button value="grid">
            <AppstoreOutlined />
          </a-radio-button>
          <a-radio-button value="list">
            <UnorderedListOutlined />
          </a-radio-button>
        </a-radio-group>
      </a-col>
    </a-row>

    <!-- 网格视图 -->
    <div v-if="viewMode === 'grid'">
      <a-row :gutter="[16, 16]">
        <a-col
          v-for="software in softwareList"
          :key="software.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="4"
          :xl="4"
        >
          <a-card
            hoverable
            @click="viewDetail(software.id)"
            style="cursor: pointer; position: relative;"
          >
            <!-- Logo - 左上角 -->
            <div class="software-logo">
              <img
                v-if="software.logo"
                :src="software.logo"
                :alt="software.name"
                style="width: 64px; height: 64px; object-fit: contain;"
              />
              <AppstoreOutlined
                v-else
                style="font-size: 56px; color: #1890ff; background: white; border-radius: 8px; padding: 4px;"
              />
            </div>

            <template #cover>
              <div style="height: 100px;"></div>
            </template>
            <a-card-meta :title="software.name" class="software-title" />
            <p class="software-description">{{ software.description || '暂无描述' }}</p>
            <a-space direction="vertical" style="width: 100%">
              <div>
                <a-tag color="blue">{{ software.category || '未分类' }}</a-tag>
                <a-tag>最新: {{ software.latest_version || '-' }}</a-tag>
              </div>
              <a-statistic
                :value="software.total_downloads"
                :value-style="{ fontSize: '14px' }"
              >
                <template #prefix>
                  <DownloadOutlined />
                </template>
                <template #suffix>
                  次下载
                </template>
              </a-statistic>
              <!-- 下载按钮 -->
              <a-button 
                type="primary" 
                ghost 
                @click.stop="viewDetail(software.id)"
                style="margin-top: 12px; width: 100%;"
              >
                <template #icon><InfoCircleOutlined /></template>
                软件详情
              </a-button>
            </a-space>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 列表视图 -->
    <div v-else>
      <a-table
        :columns="listColumns"
        :data-source="softwareList"
        :pagination="false"
        :row-key="record => record.id"
        @row="record => ({ onClick: () => viewDetail(record.id) })"
        :custom-row="record => ({ onClick: () => viewDetail(record.id) })"
        :scroll="{ x: 800 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-typography-text strong>{{ record.name }}</a-typography-text>
          </template>
          <template v-else-if="column.key === 'category'">
            <a-tag color="blue">{{ record.category || '未分类' }}</a-tag>
          </template>
          <template v-else-if="column.key === 'latestVersion'">
            最新: {{ record.latest_version || '-' }}
          </template>
          <template v-else-if="column.key === 'totalDownloads'">
            <a-statistic
              :value="record.total_downloads"
              :value-style="{ fontSize: '14px' }"
            >
              <template #prefix>
                <DownloadOutlined />
              </template>
              <template #suffix>
                次下载
              </template>
            </a-statistic>
          </template>
          <template v-else-if="column.key === 'description'">
            <a-typography-paragraph
              v-if="record.description"
              :ellipsis="{ rows: 2 }"
              style="margin-bottom: 0;"
            >
              {{ record.description }}
            </a-typography-paragraph>
            <a-typography-paragraph v-else type="secondary" style="margin-bottom: 0;">
              暂无描述
            </a-typography-paragraph>
          </template>
          <template v-else-if="column.key === 'officialUrl'">
            <a v-if="record.official_url" :href="record.official_url" target="_blank" rel="noopener noreferrer">
              {{ record.official_url }}
            </a>
            <span v-else>-</span>
          </template>
        </template>
      </a-table>
    </div>

    <a-pagination
      v-model:current="pagination.current"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      @change="loadSoftware"
      style="margin-top: 24px; text-align: right"
    />

    <!-- 上传软件弹窗（仅运维） -->
    <a-modal
      v-model:open="showUploadModal"
      title="上传软件"
      @ok="handleUpload"
      :confirm-loading="uploadLoading"
      width="600px"
    >
      <a-form :model="uploadForm" layout="vertical">
        <a-form-item label="软件名称" required>
          <a-input v-model:value="uploadForm.name" placeholder="请输入软件名称" />
        </a-form-item>
        <a-form-item label="分类">
          <a-select v-model:value="uploadForm.category" placeholder="请选择分类">
            <a-select-option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="uploadForm.description" :rows="3" />
        </a-form-item>
        <a-form-item label="Logo">
          <a-upload
            :before-upload="beforeLogoUpload"
            :file-list="logoFileList"
            @remove="handleLogoRemove"
            list-type="picture"
            :max-count="1"
          >
            <a-button v-if="logoFileList.length === 0">
              <UploadOutlined /> 选择Logo图片
            </a-button>
          </a-upload>
          <div style="margin-top: 4px; color: #999; font-size: 12px;">支持 png, jpg, jpeg, gif, svg, webp, ico 格式，最大5MB</div>
        </a-form-item>
        <a-form-item label="官网链接">
          <a-input v-model:value="uploadForm.official_url" placeholder="https://" />
        </a-form-item>
      </a-form>
      <a-alert message="创建后可以进入详情页上传文件" type="info" show-icon />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  AppstoreOutlined,
  DownloadOutlined,
  UploadOutlined,
  UnorderedListOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { softwareApi } from '@/api/software'
import { categoryApi } from '@/api/category'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const searchText = ref('')
const selectedCategory = ref()
const categories = ref([])
const softwareList = ref([])
const pagination = ref({
  current: 1,
  pageSize: 12,
  total: 0
})

// 添加视图模式
const viewMode = ref('grid') // 'grid' 或 'list'

const showUploadModal = ref(false)
const uploadLoading = ref(false)
const logoFileList = ref([])
const uploadForm = ref({
  name: '',
  category: undefined,
  description: '',
  official_url: ''
})

// 列表视图的列配置
const listColumns = [
  {
    title: '软件名称',
    key: 'name',
    width: 200
  },
  {
    title: '分类',
    key: 'category',
    width: 100
  },
  {
    title: '最新版本',
    key: 'latestVersion',
    width: 120
  },
  {
    title: '描述',
    key: 'description',
    width: 200
  },
  {
    title: '下载次数',
    key: 'totalDownloads',
    width: 120
  },
  {
    title: '官网链接',
    key: 'officialUrl',
    width: 150
  }
]

const loadSoftware = async () => {
  try {
    const params = {
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    if (searchText.value) params.search = searchText.value
    if (selectedCategory.value) params.category = selectedCategory.value

    const data = await softwareApi.list(params)
    softwareList.value = data.items || data  // 兼容新旧格式
    pagination.value.total = data.total || 0  // 设置总数
  } catch (error) {
    console.error('加载软件列表失败:', error)
  }
}

const viewDetail = (id) => {
  router.push(`/software/${id}`)
}

const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getAllNames()
  } catch (error) {
    console.error('加载软件类型失败:', error)
  }
}

const beforeLogoUpload = (file) => {
  // 检查文件类型
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp', 'image/x-icon']
  const isAllowedType = allowedTypes.includes(file.type) || file.name.match(/\.(png|jpe?g|gif|svg|webp|ico)$/i)

  if (!isAllowedType) {
    message.error('只支持上传图片文件（png, jpg, jpeg, gif, svg, webp, ico）')
    return false
  }

  // 检查文件大小（5MB）
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('Logo文件大小不能超过5MB')
    return false
  }

  logoFileList.value = [file]
  return false
}

const handleLogoRemove = () => {
  logoFileList.value = []
}

const handleUpload = async () => {
  if (!uploadForm.value.name) {
    message.error('请输入软件名称')
    return
  }

  uploadLoading.value = true
  try {
    // 清理空字符串的URL字段
    const cleanedData = {
      ...uploadForm.value,
      official_url: uploadForm.value.official_url?.trim() || null
    }

    const software = await softwareApi.create(cleanedData)

    // 如果有logo文件，上传logo
    if (logoFileList.length > 0) {
      console.log('Uploading logo for new software:', logoFileList[0])
      await softwareApi.uploadLogo(software.id, logoFileList[0])
      console.log('Logo upload completed')
      message.success('软件创建成功，Logo已上传')
    } else {
      message.success('软件创建成功，请进入详情页上传文件')
    }

    showUploadModal.value = false
    uploadForm.value = {
      name: '',
      category: undefined,
      description: '',
      official_url: ''
    }
    logoFileList.value = []
    loadSoftware()
  } catch (error) {
    // 提供更友好的错误提示
    if (error.response?.data?.detail) {
      const errorDetail = error.response.data.detail;
      if (Array.isArray(errorDetail)) {
        const firstError = errorDetail[0];
        if (firstError.msg && firstError.msg.includes('URL')) {
          message.error('请输入有效的URL地址');
        } else {
          message.error(firstError.msg || '创建失败');
        }
      } else {
        message.error(errorDetail || '创建失败');
      }
    } else {
      message.error('创建失败，请检查输入信息');
    }
  } finally {
    uploadLoading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadSoftware()
})
</script>

<style scoped>
/* 搜索栏和工具栏 */
:deep(.ant-input-search) {
  border-radius: var(--radius-md);
}

:deep(.ant-input-search-button) {
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

:deep(.ant-select-selector) {
  border-radius: var(--radius-md);
}

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

/* 视图切换按钮 */
:deep(.ant-radio-group-solid .ant-radio-button-wrapper) {
  border-radius: var(--radius-md);
  border: none;
  font-weight: var(--font-medium);
}

:deep(.ant-radio-group-solid .ant-radio-button-wrapper-checked) {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

/* 卡片网格视图 */
:deep(.ant-card) {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-primary);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

:deep(.ant-card:hover) {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

:deep(.ant-card-cover) {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg-secondary) 100%);
}

:deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.software-logo {
  position: absolute;
  top: var(--space-sm);
  left: var(--space-sm);
  z-index: 10;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-sm);
  box-shadow: var(--shadow-md);
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
}

:deep(.ant-card:hover) .software-logo {
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
}

.software-title :deep(.ant-card-meta-title) {
  font-size: 1.125rem;
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.software-description {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  margin: var(--space-md) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 42px;
  line-height: 1.5;
}

/* 标签样式 */
:deep(.ant-tag) {
  border-radius: var(--radius-sm);
  font-weight: var(--font-medium);
  border: none;
  font-size: 0.75rem;
  padding: 2px 8px;
}

/* 按钮样式 */
:deep(.ant-btn-ghost) {
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  transition: all var(--transition-normal);
}

:deep(.ant-btn-ghost:hover) {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}

/* 统计数字 */
:deep(.ant-statistic) {
  margin: var(--space-sm) 0;
}

:deep(.ant-statistic-content-value) {
  font-size: 1rem;
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

/* 表格视图 */
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

:deep(.ant-table-tbody > tr) {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: var(--color-bg-tertiary);
}

:deep(.ant-table-tbody > tr > td) {
  border-bottom: 1px solid var(--color-border-secondary);
}

/* 分页 */
:deep(.ant-pagination) {
  margin-top: var(--space-xl);
}

:deep(.ant-pagination-item) {
  border-radius: var(--radius-md);
  border-color: var(--color-border-primary);
}

:deep(.ant-pagination-item-active) {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

:deep(.ant-pagination-item-active a) {
  color: white;
}

:deep(.ant-pagination-prev),
:deep(.ant-pagination-next) {
  border-radius: var(--radius-md);
}

/* 模态框 */
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

/* 上传组件 */
:deep(.ant-upload-list-picture-card-container) {
  border-radius: var(--radius-md);
}

:deep(.ant-upload.ant-upload-select-picture-card) {
  border-radius: var(--radius-md);
  border-style: dashed;
}

/* 响应式 */
@media (max-width: 768px) {
  .software-logo {
    width: 60px;
    height: 60px;
  }

  .software-logo img {
    width: 48px;
    height: 48px;
  }
}
</style>