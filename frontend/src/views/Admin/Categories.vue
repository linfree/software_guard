<template>
  <div>
    <a-page-header
      title="软件类型管理"
      sub-title="管理软件分类，支持增删改查操作"
    />

    <a-card style="margin-top: 16px">
      <!-- 工具栏 -->
      <a-row :gutter="16" style="margin-bottom: 16px">
        <a-col :span="18">
          <a-space>
            <a-button type="primary" @click="showCreateModal">
              <template #icon><PlusOutlined /></template>
              新增类型
            </a-button>
          </a-space>
        </a-col>
      </a-row>

      <!-- 数据表格 -->
      <a-table
        :columns="columns"
        :data-source="categories"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-typography-text strong>{{ record.name }}</a-typography-text>
          </template>
          <template v-else-if="column.key === 'description'">
            <a-typography-paragraph
              v-if="record.description"
              :ellipsis="{ rows: 2 }"
              style="margin-bottom: 0"
            >
              {{ record.description }}
            </a-typography-paragraph>
            <a-typography-text v-else type="secondary">-</a-typography-text>
          </template>
          <template v-else-if="column.key === 'sort_order'">
            <a-tag color="blue">{{ record.sort_order }}</a-tag>
          </template>
          <template v-else-if="column.key === 'software_count'">
            <a-statistic
              :value="record.software_count"
              :value-style="{ fontSize: '16px' }"
            >
              <template #suffix>
                个软件
              </template>
            </a-statistic>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="handleEdit(record)"
              >
                <template #icon><EditOutlined /></template>
                编辑
              </a-button>
              <a-popconfirm
                title="确定删除该软件类型吗？"
                :description="record.software_count > 0 ? `该类型下还有 ${record.software_count} 个软件，无法删除` : '删除后无法恢复'"
                @confirm="handleDelete(record)"
                :disabled="record.software_count > 0"
              >
                <a-button
                  type="link"
                  size="small"
                  danger
                  :disabled="record.software_count > 0"
                >
                  <template #icon><DeleteOutlined /></template>
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 新增/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="editingCategory ? '编辑软件类型' : '新增软件类型'"
      @ok="handleSubmit"
      :confirm-loading="submitLoading"
      width="600px"
    >
      <a-form
        :model="formData"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="类型名称" required>
          <a-input
            v-model:value="formData.name"
            placeholder="请输入类型名称"
            :maxlength="50"
          />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入类型描述"
            :rows="3"
            :maxlength="200"
          />
        </a-form-item>
        <a-form-item label="排序">
          <a-input-number
            v-model:value="formData.sort_order"
            :min="0"
            :max="9999"
            style="width: 100%"
          />
          <div style="color: #999; font-size: 12px; margin-top: 4px">
            数值越小排序越靠前
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { categoryApi } from '@/api/category'

const loading = ref(false)
const categories = ref([])
const modalVisible = ref(false)
const submitLoading = ref(false)
const editingCategory = ref(null)

const formData = ref({
  name: '',
  description: '',
  sort_order: 0
})

const columns = [
  {
    title: '类型名称',
    key: 'name',
    width: 150
  },
  {
    title: '描述',
    key: 'description',
    width: 250
  },
  {
    title: '排序',
    key: 'sort_order',
    width: 100
  },
  {
    title: '软件数量',
    key: 'software_count',
    width: 120
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    customRender: ({ record }) => {
      return new Date(record.created_at).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    fixed: 'right'
  }
]

const loadCategories = async () => {
  loading.value = true
  try {
    const data = await categoryApi.list()
    categories.value = data || []
  } catch (error) {
    message.error('加载软件类型失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const showCreateModal = () => {
  editingCategory.value = null
  formData.value = {
    name: '',
    description: '',
    sort_order: 0
  }
  modalVisible.value = true
}

const handleEdit = (record) => {
  editingCategory.value = record
  formData.value = {
    name: record.name,
    description: record.description || '',
    sort_order: record.sort_order
  }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.name.trim()) {
    message.error('请输入类型名称')
    return
  }

  submitLoading.value = true
  try {
    if (editingCategory.value) {
      await categoryApi.update(editingCategory.value.id, formData.value)
      message.success('更新成功')
    } else {
      await categoryApi.create(formData.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadCategories()
  } catch (error) {
    message.error('操作失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (record) => {
  try {
    await categoryApi.delete(record.id)
    message.success('删除成功')
    loadCategories()
  } catch (error) {
    message.error('删除失败: ' + (error.response?.data?.detail || error.message))
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
:deep(.ant-page-header) {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: 16px 24px;
}

:deep(.ant-card) {
  border-radius: var(--radius-lg);
}

:deep(.ant-table) {
  border-radius: var(--radius-md);
}

:deep(.ant-table-thead > tr > th) {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
}

:deep(.ant-btn-primary) {
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
}

:deep(.ant-modal-content) {
  border-radius: var(--radius-lg);
}
</style>
