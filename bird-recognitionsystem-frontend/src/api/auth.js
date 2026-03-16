import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request.post('/api/auth/login', data)
}

// 用户注册
export function register(data) {
  return request.post('/api/auth/register', data)
}

// 获取个人信息
export function getProfile() {
  return request.get('/api/user/profile')
}

// 修改个人信息
export function updateProfile(data) {
  return request.put('/api/user/profile', data)
}

// 修改密码
export function updatePassword(data) {
  return request.put('/api/user/password', data)
}
