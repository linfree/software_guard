import api from './index'

export const configApi = {
  // 获取配置列表
  list() {
    return api.get('/configs')
  },

  // 获取单个配置
  get(key) {
    return api.get(`/configs/${key}`)
  },

  // 创建配置
  create(data) {
    return api.post('/configs', data)
  },

  // 更新配置
  update(key, data) {
    return api.put(`/configs/${key}`, data)
  },

  // 删除配置
  delete(key) {
    return api.delete(`/configs/${key}`)
  }
}