import request from '@/utils/request'

// 获取鸟类列表
export function getBirdList(params) {
  return request.get('/api/birds', { params })
}

// 获取鸟类详情
export function getBirdDetail(id) {
  return request.get(`/api/birds/${id}`)
}

// 新增鸟类（管理员）
export function addBird(data) {
  return request.post('/api/birds', data)
}

// 修改鸟类（管理员）
export function updateBird(id, data) {
  return request.put(`/api/birds/${id}`, data)
}

// 删除鸟类（管理员）
export function deleteBird(id) {
  return request.delete(`/api/birds/${id}`)
}
