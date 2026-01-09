import api from './index'

export const userApi = {
  // 获取用户列表
  list(params) {
    return api.get('/users', { params })
  },

  // 创建用户
  create(data) {
    return api.post('/users', data)
  },

  // 更新用户
  update(id, data) {
    return api.put(`/users/${id}`, data)
  },

  // 删除用户
  delete(id) {
    return api.delete(`/users/${id}`)
  }
}
