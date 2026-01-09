import api from './index'

export const statsApi = {
  // 获取首页统计数据
  getDashboard() {
    return api.get('/stats/dashboard')
  }
}
