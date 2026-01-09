<template>
  <div v-if="loading">
    <a-spin />
  </div>
  <div v-else-if="software">
    <a-page-header
      :title="software.name"
      @back="$router.back()"
    >
      <template #extra>
        <a-space>
          <a-button v-if="userStore.isOps()" @click="openEditModal">
            <template #icon><EditOutlined /></template>
            编辑软件
          </a-button>
          <a-button v-if="userStore.isOps()" danger @click="handleDelete">
            <template #icon><DeleteOutlined /></template>
            删除
          </a-button>
          <a-button v-if="userStore.isOps()" @click="showVersionModal = true">
            <template #icon><UploadOutlined /></template>
            上传新版本
          </a-button>
          <a-button type="primary" @click="downloadLatest">
            <template #icon><DownloadOutlined /></template>
            下载最新版
          </a-button>
        </a-space>
      </template>
      <template #footer>
        <a-tabs>
          <a-tab-pane key="versions" tab="版本列表">
            <a-table
              :columns="versionColumns"
              :data-source="software.versions"
              :pagination="false"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'version'">
                  <a-tag color="blue">{{ record.version }}</a-tag>
                </template>
                <template v-else-if="column.key === 'fileSize'">
                  {{ formatFileSize(record.file_size) }}
                </template>
                <template v-else-if="column.key === 'fileHash'">
                  <a-typography-text copyable :content="record.file_hash">
                    {{ record.file_hash?.slice(0, 16) }}...
                  </a-typography-text>
                </template>
                <template v-else-if="column.key === 'uploadTime'">
                  {{ formatDate(record.upload_time) }}
                </template>
                <template v-else-if="column.key === 'originalDownloadUrl'">
                  <a-tooltip v-if="record.original_download_url" :title="record.original_download_url">
                    <a :href="record.original_download_url" target="_blank" rel="noopener noreferrer">
                      <LinkOutlined />
                    </a>
                  </a-tooltip>
                  <span v-else>-</span>
                </template>
                <template v-else-if="column.key === 'actions'">
                  <a-space>
                    <a-button
                      type="link"
                      size="small"
                      @click="downloadVersion(record)"
                    >
                      <DownloadOutlined /> 下载
                    </a-button>
                    <a-button
                      type="link"
                      size="small"
                      @click="checkVulnerability(record)"
                    >
                      <SafetyOutlined /> 检查漏洞
                    </a-button>
                    <a-button
                      v-if="userStore.isOps()"
                      type="link"
                      size="small"
                      danger
                      @click="handleDeleteVersion(record)"
                    >
                      <DeleteOutlined /> 删除
                    </a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-tab-pane>
          <a-tab-pane key="downloads" tab="下载记录" v-if="userStore.isOps()">
            <a-table
              :columns="downloadColumns"
              :data-source="downloadLogs"
              :loading="loadingDownloads"
              :pagination="{ pageSize: 20 }"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'downloadTime'">
                  {{ formatDate(record.download_time) }}
                </template>
              </template>
            </a-table>
          </a-tab-pane>
        </a-tabs>
      </template>
    </a-page-header>

    <a-descriptions style="margin-top: 24px" :column="2">
      <a-descriptions-item label="描述">
        {{ software.description || '暂无描述' }}
      </a-descriptions-item>
      <a-descriptions-item label="分类">
        <a-tag>{{ software.category || '未分类' }}</a-tag>
      </a-descriptions-item>
      <a-descriptions-item label="官网">
        <a v-if="software.official_url" :href="software.official_url" target="_blank">
          {{ software.official_url }}
        </a>
        <span v-else>-</span>
      </a-descriptions-item>
      <a-descriptions-item label="版本数">
        {{ software.versions.length }}
      </a-descriptions-item>
    </a-descriptions>

    <!-- 上传版本弹窗 -->
    <a-modal
      v-model:open="showVersionModal"
      title="上传新版本"
      @ok="handleUploadVersion"
      :confirm-loading="uploadLoading"
    >
      <a-form :model="versionForm" layout="vertical">
        <a-form-item label="版本号" required>
          <a-input v-model:value="versionForm.version" placeholder="如: 1.0.0" />
        </a-form-item>
        <a-form-item label="文件" required>
          <a-upload
            :before-upload="beforeUpload"
            :file-list="fileList"
            @remove="() => fileList = []"
          >
            <a-button>
              <UploadOutlined /> 选择文件
            </a-button>
          </a-upload>
        </a-form-item>
        <a-form-item label="更新说明">
          <a-textarea v-model:value="versionForm.release_notes" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 漏洞检查弹窗 -->
    <a-modal
      v-model:open="showVulnModal"
      title="漏洞检查结果"
      :footer="null"
    >
      <a-spin :spinning="checkingVuln">
        <div v-if="vulnerabilities.length === 0">
          <a-result status="success" title="未发现已知漏洞" />
        </div>
        <div v-else>
          <a-alert
            v-for="vuln in vulnerabilities"
            :key="vuln.id"
            :type="vuln.severity === 'critical' || vuln.severity === 'high' ? 'error' : 'warning'"
            style="margin-bottom: 12px"
          >
            <template #message>
              {{ vuln.title || vuln.cve_id }}
              <a-tag :color="getSeverityColor(vuln.severity)">
                {{ vuln.severity }}
              </a-tag>
            </template>
            <p>{{ vuln.description }}</p>
            <p v-if="vuln.fixed_version">
              修复版本: {{ vuln.fixed_version }}
            </p>
          </a-alert>
        </div>
      </a-spin>
    </a-modal>

    <!-- 编辑软件弹窗 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑软件"
      @ok="handleEdit"
      :confirm-loading="editLoading"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="软件名称" required>
          <a-input v-model:value="editForm.name" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="editForm.description" :rows="3" />
        </a-form-item>
        <a-form-item label="分类">
          <a-select v-model:value="editForm.category">
            <a-select-option v-for="cat in categories" :key="cat" :value="cat">
              {{ cat }}
            </a-select-option>
          </a-select>
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
          <div v-if="editForm.logo && logoFileList.length === 0" style="margin-top: 8px;">
            <img :src="editForm.logo" alt="当前Logo" style="max-width: 80px; max-height: 80px; object-fit: contain; border: 1px solid #d9d9d9; border-radius: 4px;" />
            <div style="margin-top: 4px; color: #999; font-size: 12px;">当前Logo</div>
          </div>
        </a-form-item>
        <a-form-item label="官网">
          <a-input v-model:value="editForm.official_url" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  DownloadOutlined,
  UploadOutlined,
  SafetyOutlined,
  EditOutlined,
  DeleteOutlined,
  LinkOutlined
} from '@ant-design/icons-vue'
import { softwareApi } from '@/api/software'
import { vulnerabilityApi } from '@/api/vulnerability'
import { categoryApi } from '@/api/category'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const software = ref(null)
const showVersionModal = ref(false)
const uploadLoading = ref(false)
const versionForm = ref({
  version: '',
  release_notes: ''
})
const fileList = ref([])
const logoFileList = ref([])

const showVulnModal = ref(false)
const checkingVuln = ref(false)
const vulnerabilities = ref([])

const showEditModal = ref(false)
const editLoading = ref(false)
const editForm = ref({
  name: '',
  description: '',
  category: '',
  logo: '',
  official_url: ''
})

const categories = ref([])

const downloadLogs = ref([])
const loadingDownloads = ref(false)

const versionColumns = [
  { title: '版本', key: 'version', dataIndex: 'version' },
  { title: '文件名', key: 'fileName', dataIndex: 'file_name' },
  { title: '文件大小', key: 'fileSize' },
  { title: 'SHA256', key: 'fileHash', dataIndex: 'file_hash' },
  { title: '下载次数', key: 'downloadCount', dataIndex: 'download_count' },
  { title: '原始下载地址', key: 'originalDownloadUrl', dataIndex: 'original_download_url' },
  { title: '上传时间', key: 'uploadTime' },
  { title: '操作', key: 'actions' }
]

const downloadColumns = [
  { title: '用户名', key: 'username', dataIndex: 'username' },
  { title: '版本', key: 'version', dataIndex: 'version' },
  { title: '下载时间', key: 'downloadTime', dataIndex: 'download_time' },
  { title: 'IP地址', key: 'ip_address', dataIndex: 'ip_address' }
]

const latestVersion = computed(() => {
  return software.value?.versions?.[0]
})

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadDetail = async () => {
  loading.value = true
  try {
    software.value = await softwareApi.getDetail(route.params.id)
  } catch (error) {
    message.error('加载软件详情失败')
  } finally {
    loading.value = false
  }
}

const downloadLatest = () => {
  if (latestVersion.value) {
    downloadVersion(latestVersion.value)
  }
}

const downloadVersion = async (version) => {
  try {
    message.loading({ content: '准备下载...', key: 'download' })

    // 使用 fetch 下载文件，手动携带认证信息
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/downloads/${version.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error('下载失败')
    }

    // 创建 blob URL
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = version.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    message.success({ content: '下载开始', key: 'download' })
  } catch (error) {
    message.error({ content: '下载失败', key: 'download' })
  }
}

const beforeUpload = (file) => {
  fileList.value = [file]
  return false
}

const beforeLogoUpload = (file) => {
  console.log('beforeLogoUpload called with file:', file)

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
  console.log('logoFileList after setting:', logoFileList.value)
  return false
}

const handleLogoRemove = () => {
  console.log('handleLogoRemove called, clearing logoFileList')
  logoFileList.value = []
}

const openEditModal = () => {
  console.log('Opening edit modal, clearing logoFileList')
  logoFileList.value = []
  showEditModal.value = true
}

const handleUploadVersion = async () => {
  if (!versionForm.value.version || fileList.value.length === 0) {
    message.error('请填写版本号并选择文件')
    return
  }

  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('version', versionForm.value.version)
    formData.append('file', fileList.value[0])
    formData.append('release_notes', versionForm.value.release_notes || '')

    await softwareApi.uploadVersion(route.params.id, formData)
    message.success('上传成功')
    showVersionModal.value = false
    versionForm.value = { version: '', release_notes: '' }
    fileList.value = []
    loadDetail()
  } catch (error) {
    message.error('上传失败')
  } finally {
    uploadLoading.value = false
  }
}

const checkVulnerability = async (version) => {
  showVulnModal.value = true
  checkingVuln.value = true
  try {
    vulnerabilities.value = await vulnerabilityApi.check(route.params.id, version.version)
  } catch (error) {
    console.error('检查漏洞失败:', error)
  } finally {
    checkingVuln.value = false
  }
}

const getSeverityColor = (severity) => {
  const colors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'blue'
  }
  return colors[severity] || 'default'
}

const loadDownloadLogs = async () => {
  if (!userStore.isOps()) return
  loadingDownloads.value = true
  try {
    // 获取当前软件所有版本的下载记录
    const versionIds = software.value?.versions?.map(v => v.id) || []
    const allLogs = []
    for (const vid of versionIds) {
      const logs = await softwareApi.getDownloadLogs(vid)
      // 确保 logs 是数组后再展开
      if (Array.isArray(logs)) {
        allLogs.push(...logs)
      } else if (logs && Array.isArray(logs.items)) {
        // 如果返回的是分页数据格式 { items: [...], total: ... }
        allLogs.push(...(logs.items || []))
      }
    }
    downloadLogs.value = allLogs
  } catch (error) {
    console.error('加载下载记录失败:', error)
    // 发生错误时设置为空数组
    downloadLogs.value = []
  } finally {
    loadingDownloads.value = false
  }
}

const handleEdit = async () => {
  console.log('handleEdit called, logoFileList:', logoFileList.value)
  console.log('logoFileList.length:', logoFileList.value.length)

  if (!editForm.value.name) {
    message.error('请输入软件名称')
    return
  }
  editLoading.value = true

  try {
    // 如果有新的logo文件，先上传logo
    if (logoFileList.value.length > 0) {
      console.log('Uploading logo:', logoFileList.value[0])
      const result = await softwareApi.uploadLogo(route.params.id, logoFileList.value[0])
      console.log('Logo upload result:', result)
    } else {
      console.log('No logo to upload')
    }

    // 清理空字符串的URL字段
    const cleanedData = {
      name: editForm.value.name,
      description: editForm.value.description,
      category: editForm.value.category,
      official_url: editForm.value.official_url?.trim() || null
    }

    await softwareApi.update(route.params.id, cleanedData)
    message.success('更新成功')
    showEditModal.value = false
    logoFileList.value = []
    loadDetail()
  } catch (error) {
    // 提供更友好的错误提示
    if (error.response?.data?.detail) {
      const errorDetail = error.response.data.detail;
      if (Array.isArray(errorDetail)) {
        const firstError = errorDetail[0];
        if (firstError.msg && firstError.msg.includes('URL')) {
          message.error('请输入有效的URL地址');
        } else {
          message.error(firstError.msg || '更新失败');
        }
      } else {
        message.error(errorDetail || '更新失败');
      }
    } else {
      message.error('更新失败，请检查输入信息');
    }
  } finally {
    editLoading.value = false
  }
}

const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除软件"${software.value?.name}"吗？此操作不可恢复。`,
    onOk: () => {
      softwareApi.delete(route.params.id)
        .then(() => {
          message.success('删除成功')
          router.push('/software')
        })
        .catch(() => {
          message.error('删除失败')
        })
    }
  })
}

const handleDeleteVersion = (version) => {
  Modal.confirm({
    title: '确认删除版本',
    content: `确定要删除版本"${version.version}"吗？此操作不可恢复，文件将被永久删除。`,
    okText: '确认删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await softwareApi.deleteVersion(route.params.id, version.id)
        message.success('版本删除成功')
        loadDetail() // 重新加载详情页以更新版本列表
      } catch (error) {
        message.error('删除失败: ' + (error.response?.data?.detail || '未知错误'))
      }
    }
  })
}

watch(software, () => {
  if (software.value) {
    // 初始化编辑表单
    editForm.value = {
      name: software.value.name,
      description: software.value.description || '',
      category: software.value.category || '',
      logo: software.value.logo || '',
      official_url: software.value.official_url || ''
    }
    // 加载下载记录
    loadDownloadLogs()
  }
})

const loadCategories = async () => {
  try {
    categories.value = await categoryApi.getAllNames()
  } catch (error) {
    console.error('加载软件类型失败:', error)
  }
}

onMounted(() => {
  loadCategories()
  loadDetail()
})
</script>