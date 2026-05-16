<template>
  <div>
    <a-typography-title>系统配置</a-typography-title>

    <a-card title="站点配置">
      <a-form :model="siteConfig" layout="vertical">
        <a-form-item label="站点名称">
          <a-input v-model:value="siteConfig.site_name" placeholder="如: Software Guard" />
          <span style="color: #999; font-size: 12px;">显示在登录页、导航栏和浏览器标题栏</span>
        </a-form-item>
        <a-form-item label="站点描述">
          <a-input v-model:value="siteConfig.site_description" placeholder="如: 公司内网软件下载站" />
          <span style="color: #999; font-size: 12px;">显示在登录页副标题和页脚</span>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="updateSiteConfig">保存</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="存储配置" style="margin-top: 16px;">
      <a-form :model="storageConfig" layout="vertical">
        <a-form-item label="存储目录">
          <a-input v-model:value="storageConfig.storage_path" placeholder="请输入存储目录路径" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="updateStorageConfig">保存</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="AI大模型配置" style="margin-top: 16px;">
      <a-form :model="aiConfig" layout="vertical">
        <a-form-item label="模型名称">
          <a-input v-model:value="aiConfig.ai_model_name" placeholder="如: gpt-3.5-turbo" />
        </a-form-item>
        <a-form-item label="Base URL">
          <a-input v-model:value="aiConfig.ai_base_url" placeholder="如: https://api.openai.com/v1" />
        </a-form-item>
        <a-form-item label="API Key">
          <a-input-password v-model:value="aiConfig.ai_api_key" placeholder="请输入API Key" />
        </a-form-item>
        <a-form-item label="启用AI自动审核">
          <a-switch v-model:checked="aiConfig.ai_auto_review_enabled" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="updateAIConfig">保存</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="安全配置" style="margin-top: 16px;">
      <a-form :model="securityConfig" layout="vertical">
        <a-form-item label="开放注册">
          <a-switch v-model:checked="securityConfig.allow_registration" />
          <span style="margin-left: 8px; color: #999;">允许未登录用户自行注册账号</span>
        </a-form-item>
        <a-form-item label="登录速率限制 - 最大尝试次数">
          <a-input-number v-model:value="securityConfig.login_rate_limit_max" :min="1" :max="50" />
          <span style="margin-left: 8px; color: #999;">同一 IP 在限制窗口内允许的登录次数</span>
        </a-form-item>
        <a-form-item label="登录速率限制 - 时间窗口（秒）">
          <a-input-number v-model:value="securityConfig.login_rate_limit_window" :min="60" :max="3600" :step="60" />
          <span style="margin-left: 8px; color: #999;">速率限制的统计时间窗口</span>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="updateSecurityConfig">保存</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="上传配置" style="margin-top: 16px;">
      <a-form :model="uploadConfig" layout="vertical">
        <a-form-item label="最大上传大小 (GB)">
          <a-input-number v-model:value="uploadConfig.max_upload_size_gb" :min="1" :max="10" :step="1" :precision="1" />
          <span style="margin-left: 8px; color: #999;">允许上传的单个文件最大大小</span>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="updateUploadConfig">保存</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card title="LDAP/AD 认证配置" style="margin-top: 16px;">
      <a-form :model="ldapConfig" layout="vertical">
        <a-form-item label="启用 LDAP 认证">
          <a-switch v-model:checked="ldapConfig.ldap_enabled" />
          <span style="margin-left: 8px; color: #999;">启用后，用户可使用企业域账号登录</span>
        </a-form-item>
        <a-form-item label="服务器地址">
          <a-input v-model:value="ldapConfig.ldap_server_url" placeholder="如: ldap://dc1.company.com:389" />
        </a-form-item>
        <a-form-item label="绑定账号 DN">
          <a-input v-model:value="ldapConfig.ldap_bind_dn" placeholder="如: CN=svc_ldap,OU=Service,DC=company,DC=com" />
        </a-form-item>
        <a-form-item label="绑定账号密码">
          <a-input-password v-model:value="ldapConfig.ldap_bind_password" placeholder="用于搜索用户的绑定账号密码" />
        </a-form-item>
        <a-form-item label="用户搜索基础 DN">
          <a-input v-model:value="ldapConfig.ldap_base_dn" placeholder="如: OU=Users,DC=company,DC=com" />
        </a-form-item>
        <a-form-item label="用户搜索过滤器">
          <a-input v-model:value="ldapConfig.ldap_user_filter" placeholder="(sAMAccountName={username})" />
          <span style="margin-left: 8px; color: #999;">用 {username} 代表登录时输入的用户名</span>
        </a-form-item>
        <a-form-item label="新用户默认角色">
          <a-select v-model:value="ldapConfig.ldap_default_role" style="width: 200px;">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="ops">运维人员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
          <span style="margin-left: 8px; color: #999;">LDAP 新用户首次登录时分配的角色</span>
        </a-form-item>
        <a-form-item>
          <a-space>
            <a-button type="primary" @click="updateLdapConfig">保存</a-button>
            <a-button @click="testLdapConnection" :loading="ldapTesting">测试连接</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { configApi } from '@/api/config'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()

const siteConfig = ref({
  site_name: '',
  site_description: ''
})

const storageConfig = ref({
  storage_path: ''
})

const aiConfig = ref({
  ai_model_name: '',
  ai_base_url: '',
  ai_api_key: '',
  ai_auto_review_enabled: false
})

const securityConfig = ref({
  allow_registration: false,
  login_rate_limit_max: 5,
  login_rate_limit_window: 300
})

const uploadConfig = ref({
  max_upload_size_gb: 3
})

const ldapConfig = ref({
  ldap_enabled: false,
  ldap_server_url: '',
  ldap_bind_dn: '',
  ldap_bind_password: '',
  ldap_base_dn: '',
  ldap_user_filter: '(sAMAccountName={username})',
  ldap_default_role: 'user'
})

const ldapTesting = ref(false)

const loadConfigs = async () => {
  try {
    const configs = await configApi.list()
    
    // 加载存储配置
    const storagePathConfig = configs.find(c => c.key === 'storage_path')
    if (storagePathConfig) {
      storageConfig.value.storage_path = storagePathConfig.value
    }

    // 加载站点配置
    const siteName = configs.find(c => c.key === 'site_name')
    if (siteName) siteConfig.value.site_name = siteName.value

    const siteDesc = configs.find(c => c.key === 'site_description')
    if (siteDesc) siteConfig.value.site_description = siteDesc.value
    if (storagePathConfig) {
      storageConfig.value.storage_path = storagePathConfig.value
    }
    
    // 加载AI配置
    const aiModelName = configs.find(c => c.key === 'ai_model_name')
    if (aiModelName) aiConfig.value.ai_model_name = aiModelName.value
    
    const aiBaseUrl = configs.find(c => c.key === 'ai_base_url')
    if (aiBaseUrl) aiConfig.value.ai_base_url = aiBaseUrl.value
    
    const aiApiKey = configs.find(c => c.key === 'ai_api_key')
    if (aiApiKey) aiConfig.value.ai_api_key = aiApiKey.value
    
    const aiAutoReview = configs.find(c => c.key === 'ai_auto_review_enabled')
    if (aiAutoReview) aiConfig.value.ai_auto_review_enabled = aiAutoReview.value.toLowerCase() === 'true'

    // 加载安全配置
    const allowRegistration = configs.find(c => c.key === 'allow_registration')
    if (allowRegistration) securityConfig.value.allow_registration = allowRegistration.value.toLowerCase() === 'true'

    const rateLimitMax = configs.find(c => c.key === 'login_rate_limit_max')
    if (rateLimitMax) securityConfig.value.login_rate_limit_max = parseInt(rateLimitMax.value) || 5

    const rateLimitWindow = configs.find(c => c.key === 'login_rate_limit_window')
    if (rateLimitWindow) securityConfig.value.login_rate_limit_window = parseInt(rateLimitWindow.value) || 300

    const maxUploadSize = configs.find(c => c.key === 'max_upload_size')
    if (maxUploadSize) uploadConfig.value.max_upload_size_gb = parseInt(maxUploadSize.value) / (1024 * 1024 * 1024)

    // 加载 LDAP 配置
    const ldapEnabled = configs.find(c => c.key === 'ldap_enabled')
    if (ldapEnabled) ldapConfig.value.ldap_enabled = ldapEnabled.value.toLowerCase() === 'true'

    const ldapServerUrl = configs.find(c => c.key === 'ldap_server_url')
    if (ldapServerUrl) ldapConfig.value.ldap_server_url = ldapServerUrl.value

    const ldapBindDn = configs.find(c => c.key === 'ldap_bind_dn')
    if (ldapBindDn) ldapConfig.value.ldap_bind_dn = ldapBindDn.value

    const ldapBindPassword = configs.find(c => c.key === 'ldap_bind_password')
    if (ldapBindPassword) ldapConfig.value.ldap_bind_password = ldapBindPassword.value

    const ldapBaseDn = configs.find(c => c.key === 'ldap_base_dn')
    if (ldapBaseDn) ldapConfig.value.ldap_base_dn = ldapBaseDn.value

    const ldapUserFilter = configs.find(c => c.key === 'ldap_user_filter')
    if (ldapUserFilter) ldapConfig.value.ldap_user_filter = ldapUserFilter.value

    const ldapDefaultRole = configs.find(c => c.key === 'ldap_default_role')
    if (ldapDefaultRole) ldapConfig.value.ldap_default_role = ldapDefaultRole.value
  } catch (error) {
    message.error('加载配置失败')
  }
}

const updateSiteConfig = async () => {
  try {
    await _saveConfigItem('site_name', siteConfig.value.site_name, '站点名称')
    await _saveConfigItem('site_description', siteConfig.value.site_description, '站点描述')
    siteStore.setName(siteConfig.value.site_name)
    siteStore.setDescription(siteConfig.value.site_description)
    message.success('站点配置更新成功')
  } catch (error) {
    message.error('站点配置更新失败')
  }
}

const updateStorageConfig = async () => {
  try {
    // 检查存储路径配置是否存在
    try {
      await configApi.get('storage_path')
      // 如果存在，更新它
      await configApi.update('storage_path', {
        value: storageConfig.value.storage_path,
        description: '存储目录路径'
      })
    } catch (error) {
      // 如果不存在，创建它
      if (error.response?.status === 404) {
        await configApi.create({
          key: 'storage_path',
          value: storageConfig.value.storage_path,
          description: '存储目录路径'
        })
      }
    }
    message.success('存储配置更新成功')
  } catch (error) {
    message.error('存储配置更新失败')
  }
}

const updateAIConfig = async () => {
  try {
    // 更新AI模型名称配置
    try {
      await configApi.get('ai_model_name')
      await configApi.update('ai_model_name', {
        value: aiConfig.value.ai_model_name,
        description: 'AI大模型名称'
      })
    } catch (error) {
      if (error.response?.status === 404) {
        await configApi.create({
          key: 'ai_model_name',
          value: aiConfig.value.ai_model_name,
          description: 'AI大模型名称'
        })
      }
    }
    
    // 更新AI Base URL配置
    try {
      await configApi.get('ai_base_url')
      await configApi.update('ai_base_url', {
        value: aiConfig.value.ai_base_url,
        description: 'AI大模型Base URL'
      })
    } catch (error) {
      if (error.response?.status === 404) {
        await configApi.create({
          key: 'ai_base_url',
          value: aiConfig.value.ai_base_url,
          description: 'AI大模型Base URL'
        })
      }
    }
    
    // 更新AI API Key配置
    try {
      await configApi.get('ai_api_key')
      await configApi.update('ai_api_key', {
        value: aiConfig.value.ai_api_key,
        description: 'AI大模型API Key'
      })
    } catch (error) {
      if (error.response?.status === 404) {
        await configApi.create({
          key: 'ai_api_key',
          value: aiConfig.value.ai_api_key,
          description: 'AI大模型API Key'
        })
      }
    }
    
    // 更新AI自动审核启用状态配置
    try {
      await configApi.get('ai_auto_review_enabled')
      await configApi.update('ai_auto_review_enabled', {
        value: aiConfig.value.ai_auto_review_enabled.toString(),
        description: '是否启用AI自动审核'
      })
    } catch (error) {
      if (error.response?.status === 404) {
        await configApi.create({
          key: 'ai_auto_review_enabled',
          value: aiConfig.value.ai_auto_review_enabled.toString(),
          description: '是否启用AI自动审核'
        })
      }
    }
    
    message.success('AI配置更新成功')
  } catch (error) {
    message.error('AI配置更新失败')
  }
}

const updateSecurityConfig = async () => {
  try {
    const securityItems = [
      { key: 'allow_registration', value: securityConfig.value.allow_registration.toString(), desc: '是否允许开放注册' },
      { key: 'login_rate_limit_max', value: securityConfig.value.login_rate_limit_max.toString(), desc: '登录速率限制最大尝试次数' },
      { key: 'login_rate_limit_window', value: securityConfig.value.login_rate_limit_window.toString(), desc: '登录速率限制时间窗口（秒）' }
    ]
    for (const item of securityItems) {
      try {
        await configApi.get(item.key)
        await configApi.update(item.key, { value: item.value, description: item.desc })
      } catch (error) {
        if (error.response?.status === 404) {
          await configApi.create({ key: item.key, value: item.value, description: item.desc })
        }
      }
    }
    message.success('安全配置更新成功')
  } catch (error) {
    message.error('安全配置更新失败')
  }
}

const updateUploadConfig = async () => {
  try {
    const valueBytes = Math.round(uploadConfig.value.max_upload_size_gb * 1024 * 1024 * 1024)
    try {
      await configApi.get('max_upload_size')
      await configApi.update('max_upload_size', { value: valueBytes.toString(), description: '最大上传文件大小（字节）' })
    } catch (error) {
      if (error.response?.status === 404) {
        await configApi.create({ key: 'max_upload_size', value: valueBytes.toString(), description: '最大上传文件大小（字节）' })
      }
    }
    message.success('上传配置更新成功')
  } catch (error) {
    message.error('上传配置更新失败')
  }
}

const _saveConfigItem = async (key, value, description) => {
  try {
    await configApi.get(key)
    await configApi.update(key, { value, description })
  } catch (error) {
    if (error.response?.status === 404) {
      await configApi.create({ key, value, description })
    }
  }
}

const updateLdapConfig = async () => {
  try {
    const items = [
      { key: 'ldap_enabled', value: ldapConfig.value.ldap_enabled.toString(), desc: '是否启用 LDAP 认证' },
      { key: 'ldap_server_url', value: ldapConfig.value.ldap_server_url, desc: 'LDAP 服务器地址' },
      { key: 'ldap_bind_dn', value: ldapConfig.value.ldap_bind_dn, desc: 'LDAP 绑定账号 DN' },
      { key: 'ldap_bind_password', value: ldapConfig.value.ldap_bind_password, desc: 'LDAP 绑定账号密码' },
      { key: 'ldap_base_dn', value: ldapConfig.value.ldap_base_dn, desc: 'LDAP 用户搜索基础 DN' },
      { key: 'ldap_user_filter', value: ldapConfig.value.ldap_user_filter, desc: 'LDAP 用户搜索过滤器' },
      { key: 'ldap_default_role', value: ldapConfig.value.ldap_default_role, desc: 'LDAP 新用户默认角色' }
    ]
    for (const item of items) {
      await _saveConfigItem(item.key, item.value, item.desc)
    }
    message.success('LDAP 配置更新成功')
  } catch (error) {
    message.error('LDAP 配置更新失败')
  }
}

const testLdapConnection = async () => {
  ldapTesting.value = true
  try {
    await updateLdapConfig()
    const res = await fetch('/api/auth/ldap/test', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    const data = await res.json()
    if (res.ok && data.success) {
      message.success(`连接成功: ${data.message || 'LDAP 服务器可达'}`)
    } else {
      message.error(`连接失败: ${data.detail || '未知错误'}`)
    }
  } catch (error) {
    message.error('连接测试失败: ' + (error.message || '未知错误'))
  } finally {
    ldapTesting.value = false
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
:deep(.ant-card) {
  margin-bottom: 16px;
}
</style>