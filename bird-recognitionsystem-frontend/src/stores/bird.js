import { defineStore } from 'pinia'
import { getBirdList, getBirdDetail } from '@/api/bird'

export const useBirdStore = defineStore('bird', {
  state: () => ({
    birdList: [],
    total: 0,
    currentBird: null,
    loading: false
  }),
  
  actions: {
    // 获取鸟类列表
    async fetchBirdList(params) {
      this.loading = true
      try {
        const data = await getBirdList(params)
        this.birdList = data.list
        this.total = data.total
        return data
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 获取鸟类详情
    async fetchBirdDetail(id) {
      this.loading = true
      try {
        const data = await getBirdDetail(id)
        this.currentBird = data
        return data
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 清除当前鸟类信息
    clearCurrentBird() {
      this.currentBird = null
    }
  }
})
