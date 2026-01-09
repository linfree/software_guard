<template>
  <div>
    <a-typography-title>漏洞管理</a-typography-title>
    <a-button type="primary" @click="showAddModal = true" style="margin-bottom: 16px">
      <template #icon><PlusOutlined /></template>
      添加漏洞
    </a-button>

    <a-table
      :columns="columns"
      :data-source="vulnerabilities"
      :loading="loading"
      :pagination="pagination"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'softwareName'">
          {{ record.software_name }}
        </template>
        <template v-else-if="column.key === 'severity'">
          <a-tag :color="getSeverityColor(record.severity)">
            {{ record.severity.toUpperCase() }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'cveId'">
          <a v-if="record.cve_id" :href="`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${record.cve_id}`" target="_blank">
            {{ record.cve_id }}
          </a>
          <span v-else>-</span>
        </template>
        <template v-else-if="column.key === 'createdAt'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button type="link" size="small" @click="openEditModal(record)">
              <EditOutlined /> 编辑
            </a-button>
            <a-button type="link" size="small" danger @click="handleDelete(record)">
              <DeleteOutlined /> 删除
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 添加漏洞弹窗 -->
    <a-modal
      v-model:open="showAddModal"
      title="添加漏洞记录"
      @ok="handleAdd"
      :confirm-loading="addLoading"
      width="600px"
    >
      <a-form :model="vulnForm" layout="vertical">
        <a-form-item label="软件" required>
          <a-select
            v-model:value="vulnForm.software_id"
            placeholder="选择软件"
            show-search
            :filter-option="filterSoftware"
          >
            <a-select-option v-for="sw in softwareList" :key="sw.id" :value="sw.id">
              {{ sw.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="严重程度" required>
          <a-select v-model:value="vulnForm.severity" placeholder="选择严重程度">
            <a-select-option value="critical">严重</a-select-option>
            <a-select-option value="high">高危</a-select-option>
            <a-select-option value="medium">中危</a-select-option>
            <a-select-option value="low">低危</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="CVE 编号">
          <a-input v-model:value="vulnForm.cve_id" placeholder="如: CVE-2023-1234" />
        </a-form-item>
        <a-form-item label="标题">
          <a-input v-model:value="vulnForm.title" placeholder="漏洞标题" />
        </a-form-item>
        <a-form-item label="影响版本">
          <a-input v-model:value="vulnForm.affected_versions" placeholder="如: 1.0.0-1.5.0" />
        </a-form-item>
        <a-form-item label="修复版本">
          <a-input v-model:value="vulnForm.fixed_version" placeholder="如: 1.5.1" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="vulnForm.description" :rows="3" />
        </a-form-item>
        <a-form-item label="参考链接">
          <a-input v-model:value="vulnForm.reference_url" placeholder="https://" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑漏洞弹窗 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑漏洞记录"
      @ok="handleEdit"
      :confirm-loading="editLoading"
      width="600px"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="软件" required>
          <a-select
            v-model:value="editForm.software_id"
            placeholder="选择软件"
            show-search
            :filter-option="filterSoftware"
          >
            <a-select-option v-for="sw in softwareList" :key="sw.id" :value="sw.id">
              {{ sw.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="严重程度" required>
          <a-select v-model:value="editForm.severity" placeholder="选择严重程度">
            <a-select-option value="critical">严重</a-select-option>
            <a-select-option value="high">高危</a-select-option>
            <a-select-option value="medium">中危</a-select-option>
            <a-select-option value="low">低危</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="CVE 编号">
          <a-input v-model:value="editForm.cve_id" placeholder="如: CVE-2023-1234" />
        </a-form-item>
        <a-form-item label="标题">
          <a-input v-model:value="editForm.title" placeholder="漏洞标题" />
        </a-form-item>
        <a-form-item label="影响版本">
          <a-input v-model:value="editForm.affected_versions" placeholder="如: 1.0.0-1.5.0" />
        </a-form-item>
        <a-form-item label="修复版本">
          <a-input v-model:value="editForm.fixed_version" placeholder="如: 1.5.1" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="editForm.description" :rows="3" />
        </a-form-item>
        <a-form-item label="参考链接">
          <a-input v-model:value="editForm.reference_url" placeholder="https://" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { vulnerabilityApi } from '@/api/vulnerability'
import { softwareApi } from '@/api/software'
import dayjs from 'dayjs'

const loading = ref(false)
const vulnerabilities = ref([])
const softwareList = ref([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const showAddModal = ref(false)
const addLoading = ref(false)
const vulnForm = ref({
  software_id: undefined,
  severity: undefined,
  cve_id: '',
  title: '',
  affected_versions: '',
  fixed_version: '',
  description: '',
  reference_url: ''
})

const showEditModal = ref(false)
const editLoading = ref(false)
const editForm = ref({
  id: null,
  software_id: undefined,
  severity: undefined,
  cve_id: '',
  title: '',
  affected_versions: '',
  fixed_version: '',
  description: '',
  reference_url: ''
})

const columns = [
  { title: '软件', key: 'softwareName', dataIndex: 'software_name' },
  { title: 'CVE', key: 'cveId' },
  { title: '标题', key: 'title', dataIndex: 'title' },
  { title: '严重程度', key: 'severity' },
  { title: '影响版本', key: 'affectedVersions', dataIndex: 'affected_versions' },
  { title: '修复版本', key: 'fixedVersion', dataIndex: 'fixed_version' },
  { title: '创建时间', key: 'createdAt' },
  { title: '操作', key: 'actions' }
]

const getSeverityColor = (severity) => {
  const colors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'blue'
  }
  return colors[severity] || 'default'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const filterSoftware = (input, option) => {
  return option.children[0].children.toLowerCase().includes(input.toLowerCase())
}

const loadVulnerabilities = async () => {
  loading.value = true
  try {
    const data = await vulnerabilityApi.list({
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    vulnerabilities.value = data?.items || data || []
    pagination.value.total = data?.total || 0
  } catch (error) {
    console.error('加载漏洞列表失败:', error)
    vulnerabilities.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const loadSoftware = async () => {
  try {
    const data = await softwareApi.list({ limit: 100 })
    softwareList.value = data?.items || data || []
  } catch (error) {
    console.error('加载软件列表失败:', error)
    softwareList.value = []
  }
}

const handleAdd = async () => {
  if (!vulnForm.value.software_id || !vulnForm.value.severity) {
    message.error('请填写必填项')
    return
  }

  addLoading.value = true
  try {
    await vulnerabilityApi.create(vulnForm.value)
    message.success('添加成功')
    showAddModal.value = false
    vulnForm.value = {
      software_id: undefined,
      severity: undefined,
      cve_id: '',
      title: '',
      affected_versions: '',
      fixed_version: '',
      description: '',
      reference_url: ''
    }
    loadVulnerabilities()
  } catch (error) {
    message.error('添加失败')
  } finally {
    addLoading.value = false
  }
}

const openEditModal = (record) => {
  editForm.value = {
    id: record.id,
    software_id: record.software_id,
    severity: record.severity,
    cve_id: record.cve_id || '',
    title: record.title || '',
    affected_versions: record.affected_versions || '',
    fixed_version: record.fixed_version || '',
    description: record.description || '',
    reference_url: record.reference_url || ''
  }
  showEditModal.value = true
}

const handleEdit = async () => {
  if (!editForm.value.software_id || !editForm.value.severity) {
    message.error('请填写必填项')
    return
  }

  editLoading.value = true
  try {
    await vulnerabilityApi.update(editForm.value.id, editForm.value)
    message.success('更新成功')
    showEditModal.value = false
    loadVulnerabilities()
  } catch (error) {
    message.error('更新失败')
  } finally {
    editLoading.value = false
  }
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除漏洞"${record.title || record.cve_id}"吗？`,
    onOk: async () => {
      try {
        await vulnerabilityApi.delete(record.id)
        message.success('删除成功')
        loadVulnerabilities()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  loadVulnerabilities()
  loadSoftware()
})
</script>