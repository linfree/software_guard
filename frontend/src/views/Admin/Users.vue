<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="18">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索用户名"
          enter-button
          @search="loadUsers"
        />
      </a-col>
      <a-col :span="6">
        <a-button type="primary" @click="showCreateModal = true">
          <template #icon><PlusOutlined /></template>
          创建用户
        </a-button>
      </a-col>
    </a-row>

    <a-table
      :columns="columns"
      :data-source="users"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="getRoleColor(record.role)">
            {{ getRoleText(record.role) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'isActive'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '正常' : '禁用' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'createdAt'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'actions'">
          <a-space>
            <a-button
              size="small"
              @click="editUser(record)"
              :disabled="record.id === currentUserId"
            >
              编辑
            </a-button>
            <a-popconfirm
              title="确定删除该用户吗？"
              @confirm="deleteUser(record)"
              :disabled="record.id === currentUserId"
            >
              <a-button
                size="small"
                danger
                :disabled="record.id === currentUserId"
              >
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 创建用户弹窗 -->
    <a-modal
      v-model:open="showCreateModal"
      title="创建用户"
      @ok="handleCreate"
      :confirm-loading="createLoading"
    >
      <a-form :model="createForm" layout="vertical">
        <a-form-item label="用户名" required>
          <a-input v-model:value="createForm.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="createForm.password" placeholder="请输入密码（至少6位）" />
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input v-model:value="createForm.email" placeholder="请输入邮箱" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑用户弹窗 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑用户"
      @ok="handleUpdate"
      :confirm-loading="updateLoading"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="用户名">
          <a-input v-model:value="editForm.username" disabled />
        </a-form-item>
        <a-form-item label="角色" required>
          <a-select v-model:value="editForm.role">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="ops">运维人员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态" required>
          <a-select v-model:value="editForm.is_active">
            <a-select-option :value="true">正常</a-select-option>
            <a-select-option :value="false">禁用</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { userApi } from '@/api/user'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userInfo?.id)

const loading = ref(false)
const users = ref([])
const searchText = ref('')
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const showCreateModal = ref(false)
const createLoading = ref(false)
const createForm = ref({
  username: '',
  password: '',
  email: ''
})

const showEditModal = ref(false)
const updateLoading = ref(false)
const editForm = ref({
  id: null,
  username: '',
  role: 'user',
  is_active: true
})

const columns = [
  { title: 'ID', key: 'id', dataIndex: 'id', width: 80 },
  { title: '用户名', key: 'username', dataIndex: 'username' },
  { title: '邮箱', key: 'email', dataIndex: 'email' },
  { title: '角色', key: 'role' },
  { title: '状态', key: 'isActive' },
  { title: '创建时间', key: 'createdAt' },
  { title: '操作', key: 'actions', width: 150 }
]

const getRoleColor = (role) => {
  const colors = {
    admin: 'red',
    ops: 'blue',
    user: 'green'
  }
  return colors[role] || 'default'
}

const getRoleText = (role) => {
  const texts = {
    admin: '管理员',
    ops: '运维',
    user: '普通用户'
  }
  return texts[role] || role
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }
    const data = await userApi.list(params)
    users.value = data?.items || data || []
    pagination.value.total = data?.total || 0
  } catch (error) {
    console.error('加载用户列表失败:', error)
    users.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.value.current = pag.current
  loadUsers()
}

const handleCreate = async () => {
  if (!createForm.value.username || !createForm.value.password) {
    message.error('请填写用户名和密码')
    return
  }

  if (createForm.value.password.length < 6) {
    message.error('密码至少6位')
    return
  }

  createLoading.value = true
  try {
    await userApi.create(createForm.value)
    message.success('创建成功')
    showCreateModal.value = false
    createForm.value = {
      username: '',
      password: '',
      email: ''
    }
    loadUsers()
  } catch (error) {
    message.error('创建失败')
  } finally {
    createLoading.value = false
  }
}

const editUser = (user) => {
  editForm.value = {
    id: user.id,
    username: user.username,
    role: user.role,
    is_active: user.is_active
  }
  showEditModal.value = true
}

const handleUpdate = async () => {
  updateLoading.value = true
  try {
    await userApi.update(editForm.value.id, {
      role: editForm.value.role,
      is_active: editForm.value.is_active
    })
    message.success('更新成功')
    showEditModal.value = false
    loadUsers()
  } catch (error) {
    message.error('更新失败')
  } finally {
    updateLoading.value = false
  }
}

const deleteUser = async (user) => {
  try {
    await userApi.delete(user.id)
    message.success('删除成功')
    loadUsers()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>
