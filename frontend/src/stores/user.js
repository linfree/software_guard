import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const login = async (loginForm) => {
    const formData = new URLSearchParams()
    formData.append('username', loginForm.username)
    formData.append('password', loginForm.password)

    const response = await authApi.login(formData)
    setToken(response.access_token)
    setUserInfo(response.user)
    return response
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  const fetchUserInfo = async () => {
    const info = await authApi.getCurrentUser()
    setUserInfo(info)
    return info
  }

  const isAdmin = () => {
    return userInfo.value?.role === 'admin'
  }

  const isOps = () => {
    return userInfo.value?.role === 'admin' || userInfo.value?.role === 'ops'
  }

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    login,
    logout,
    fetchUserInfo,
    isAdmin,
    isOps
  }
})
