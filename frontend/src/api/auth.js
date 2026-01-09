import api from './index'

export const authApi = {
  // 登录
  login(data) {
    return api.post('/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  // 注册
  register(data) {
    return api.post('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/auth/me')
  }
}
