import request from '@/utils/request'

// 上传图片识别
export function recognize(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/recognize', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 识别可能需要更长时间
  })
}

// 获取历史记录
export function getRecords(params) {
  return request.get('/api/records', { params })
}

// 删除历史记录
export function deleteRecord(id) {
  return request.delete(`/api/records/${id}`)
}
