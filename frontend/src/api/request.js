import api from './index'

export const requestApi = {
  // 创建申请
  create(data) {
    return api.post('/requests', data)
  },

  // 获取申请列表
  list(params) {
    return api.get('/requests', { params })
  },

  // 审核申请
  review(id, data) {
    return api.post(`/requests/${id}/review`, data)
  }
}
