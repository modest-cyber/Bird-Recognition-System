import { defineStore } from 'pinia'
import { login as loginApi, getProfile } from '@/api/auth'
import { getToken, setToken, setUser, getUser, clearAuth } from '@/utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    userInfo: getUser() || {
      id: null,
      username: '',
      role: '',
      email: ''
    }
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },
  
  actions: {
    // 登录
    async login(loginForm) {
      try {
        const data = await loginApi(loginForm)
        this.token = data.token
        this.userInfo = data.userInfo
        setToken(data.token)
        setUser(data.userInfo)
        return data
      } catch (error) {
        throw error
      }
    },
    
    // 获取用户信息
    async fetchUserInfo() {
      try {
        const data = await getProfile()
        this.userInfo = data
        setUser(data)
        return data
      } catch (error) {
        throw error
      }
    },
    
    // 退出登录
    logout() {
      this.token = ''
      this.userInfo = {
        id: null,
        username: '',
        role: '',
        email: ''
      }
      clearAuth()
    }
  }
})
