import request from '@/utils/request'

// 获取统计数据
export function getStats() {
  return request.get('/api/admin/stats')
}

// 获取用户列表
export function getUserList(params) {
  return request.get('/api/admin/users', { params })
}

// 启用/禁用用户
export function updateUserStatus(id, isActive) {
  return request.patch(`/api/admin/users/${id}/status`, { is_active: isActive })
}

// 获取全量识别记录
export function getAllRecords(params) {
  return request.get('/api/admin/records', { params })
}
