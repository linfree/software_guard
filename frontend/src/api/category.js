/**
 * 软件类型相关 API
 */
import api from './index'

export const categoryApi = {
  /**
   * 获取软件类型列表
   */
  list: (params = {}) => {
    return api.get('/categories', { params })
  },

  /**
   * 获取所有软件类型名称（用于下拉列表）
   */
  getAllNames: () => {
    return api.get('/categories/all')
  },

  /**
   * 获取软件类型详情
   */
  get: (id) => {
    return api.get(`/categories/${id}`)
  },

  /**
   * 创建软件类型
   */
  create: (data) => {
    return api.post('/categories', data)
  },

  /**
   * 更新软件类型
   */
  update: (id, data) => {
    return api.put(`/categories/${id}`, data)
  },

  /**
   * 删除软件类型
   */
  delete: (id) => {
    return api.delete(`/categories/${id}`)
  }
}
