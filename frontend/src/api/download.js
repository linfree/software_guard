import api from './index'

export const downloadApi = {
  // 获取下载日志
  getLogs(params) {
    return api.get('/downloads/logs', { params })
  },

  // 获取下载统计
  getStats() {
    return api.get('/downloads/stats')
  }
}