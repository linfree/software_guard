<template>
  <div>
    <a-typography-title>系统配置</a-typography-title>
    
    <a-card title="存储配置">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { configApi } from '@/api/config'

const storageConfig = ref({
  storage_path: ''
})

const aiConfig = ref({
  ai_model_name: '',
  ai_base_url: '',
  ai_api_key: '',
  ai_auto_review_enabled: false
})

const loadConfigs = async () => {
  try {
    const configs = await configApi.list()
    
    // 加载存储配置
    const storagePathConfig = configs.find(c => c.key === 'storage_path')
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
  } catch (error) {
    message.error('加载配置失败')
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

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
:deep(.ant-card) {
  margin-bottom: 16px;
}
</style>