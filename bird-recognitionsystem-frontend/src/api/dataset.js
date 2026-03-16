/**
 * 数据集管理相关 API
 */
import request from '@/utils/request'

// ==================== 数据集统计 ====================

/**
 * 获取数据集统计信息
 */
export function getDatasetStats() {
  return request({
    url: '/api/admin/dataset/stats',
    method: 'get'
  })
}

// ==================== 数据集文件管理 ====================

/**
 * 获取数据集文件列表
 */
export function getDatasetFiles(params = {}) {
  return request({
    url: '/api/admin/dataset/files',
    method: 'get',
    params
  })
}

/**
 * 上传图片
 */
export function uploadImages(formData) {
  return request({
    url: '/api/admin/dataset/upload/images',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上传标注文件
 */
export function uploadLabels(formData) {
  return request({
    url: '/api/admin/dataset/upload/labels',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除数据集文件
 */
export function deleteDatasetFile(filename, fileType = 'image') {
  return request({
    url: `/api/admin/dataset/files/${encodeURIComponent(filename)}`,
    method: 'delete',
    params: { file_type: fileType }
  })
}

/**
 * 清空数据集
 */
export function clearDataset() {
  return request({
    url: '/api/admin/dataset/clear',
    method: 'delete'
  })
}

// ==================== 类别管理 ====================

/**
 * 获取类别列表
 */
export function getClasses() {
  return request({
    url: '/api/admin/dataset/classes',
    method: 'get'
  })
}

/**
 * 更新类别列表
 */
export function updateClasses(classes) {
  return request({
    url: '/api/admin/dataset/classes',
    method: 'put',
    data: { classes }
  })
}

// ==================== 模型训练 ====================

/**
 * 启动训练
 */
export function startTraining(config) {
  return request({
    url: '/api/admin/dataset/training/start',
    method: 'post',
    data: config
  })
}

/**
 * 停止训练
 */
export function stopTraining() {
  return request({
    url: '/api/admin/dataset/training/stop',
    method: 'post'
  })
}

/**
 * 获取训练进度
 */
export function getTrainingProgress() {
  return request({
    url: '/api/admin/dataset/training/progress',
    method: 'get'
  })
}

/**
 * 获取训练日志
 */
export function getTrainingLogs(limit = 100) {
  return request({
    url: '/api/admin/dataset/training/logs',
    method: 'get',
    params: { limit }
  })
}

// ==================== 模型管理 ====================

/**
 * 获取模型列表
 */
export function getModels() {
  return request({
    url: '/api/admin/dataset/models',
    method: 'get'
  })
}

/**
 * 激活模型
 */
export function activateModel(modelPath) {
  const formData = new FormData()
  formData.append('model_path', modelPath)
  return request({
    url: '/api/admin/dataset/models/activate',
    method: 'post',
    data: formData
  })
}

/**
 * 删除模型
 */
export function deleteModel(modelPath) {
  return request({
    url: '/api/admin/dataset/models',
    method: 'delete',
    params: { model_path: modelPath }
  })
}
