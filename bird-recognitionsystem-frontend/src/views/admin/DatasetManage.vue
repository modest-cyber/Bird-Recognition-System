<template>
  <Layout>
    <div class="dataset-manage">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2>数据集管理与模型训练</h2>
        <el-button type="primary" @click="$router.push('/admin')">
          <el-icon><Back /></el-icon>
          返回仪表盘
        </el-button>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stat-cards">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="36" color="#409eff"><Picture /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.total_images || 0 }}</p>
                <p class="stat-label">图片总数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="36" color="#67c23a"><Document /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.labeled_images || 0 }}</p>
                <p class="stat-label">已标注图片</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="36" color="#e6a23c"><List /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.total_classes || 0 }}</p>
                <p class="stat-label">类别数量</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="36" :color="trainingStatusColor"><Cpu /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ trainingStatusText }}</p>
                <p class="stat-label">训练状态</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 功能标签页 -->
      <el-tabs v-model="activeTab" type="card" class="main-tabs">
        <!-- 数据集管理 -->
        <el-tab-pane label="数据集管理" name="dataset">
          <div class="tab-content">
            <!-- 上传区域 -->
            <el-row :gutter="20" class="upload-section">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>上传图片</span>
                  </template>
                  <el-upload
                    ref="imageUploadRef"
                    class="upload-area"
                    drag
                    multiple
                    :auto-upload="false"
                    accept=".jpg,.jpeg,.png,.webp,.bmp"
                    :on-change="handleImageChange"
                    :file-list="imageFileList"
                  >
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">
                      拖拽图片到此处，或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 jpg/jpeg/png/webp/bmp 格式
                      </div>
                    </template>
                  </el-upload>
                  <el-button 
                    type="primary" 
                    :loading="uploadingImages"
                    :disabled="imageFileList.length === 0"
                    @click="submitImageUpload"
                  >
                    上传图片 ({{ imageFileList.length }})
                  </el-button>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>上传标注文件</span>
                  </template>
                  <el-upload
                    ref="labelUploadRef"
                    class="upload-area"
                    drag
                    multiple
                    :auto-upload="false"
                    accept=".txt"
                    :on-change="handleLabelChange"
                    :file-list="labelFileList"
                  >
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">
                      拖拽标注文件到此处，或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        YOLO格式 .txt 文件，每行: 类别ID x y w h
                      </div>
                    </template>
                  </el-upload>
                  <el-button 
                    type="primary"
                    :loading="uploadingLabels"
                    :disabled="labelFileList.length === 0"
                    @click="submitLabelUpload"
                  >
                    上传标注 ({{ labelFileList.length }})
                  </el-button>
                </el-card>
              </el-col>
            </el-row>

            <!-- 文件列表 -->
            <el-card class="file-list-card">
              <template #header>
                <div class="card-header">
                  <span>数据集文件列表</span>
                  <div>
                    <el-button type="primary" size="small" @click="fetchFiles">
                      <el-icon><Refresh /></el-icon>
                      刷新
                    </el-button>
                    <el-popconfirm 
                      title="确定要清空所有数据集文件吗？"
                      @confirm="handleClearDataset"
                    >
                      <template #reference>
                        <el-button type="danger" size="small">
                          <el-icon><Delete /></el-icon>
                          清空数据集
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </div>
              </template>
              <el-table :data="fileList" style="width: 100%" v-loading="loadingFiles">
                <el-table-column prop="filename" label="文件名" min-width="200" />
                <el-table-column prop="size" label="大小" width="120">
                  <template #default="{ row }">
                    {{ formatSize(row.size) }}
                  </template>
                </el-table-column>
                <el-table-column prop="has_label" label="标注状态" width="120">
                  <template #default="{ row }">
                    <el-tag :type="row.has_label ? 'success' : 'warning'" size="small">
                      {{ row.has_label ? '已标注' : '未标注' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-popconfirm 
                      title="确定删除此文件？"
                      @confirm="handleDeleteFile(row.filename)"
                    >
                      <template #reference>
                        <el-button type="danger" size="small" link>删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
              <el-pagination
                class="pagination"
                v-model:current-page="filePage"
                v-model:page-size="filePageSize"
                :total="fileTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                @change="fetchFiles"
              />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 类别管理 -->
        <el-tab-pane label="类别管理" name="classes">
          <div class="tab-content">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>类别映射 (classes.txt)</span>
                  <el-button type="primary" size="small" @click="saveClasses" :loading="savingClasses">
                    保存类别
                  </el-button>
                </div>
              </template>
              <div class="classes-editor">
                <p class="tip">每行一个类别名称，行号即为类别ID（从0开始）</p>
                <el-input
                  v-model="classesText"
                  type="textarea"
                  :rows="15"
                  placeholder="输入类别名称，每行一个，例如：&#10;麻雀&#10;燕子&#10;喜鹊"
                />
                <div class="class-distribution" v-if="stats.class_distribution">
                  <h4>类别分布统计</h4>
                  <div class="distribution-list">
                    <div 
                      v-for="(count, name) in stats.class_distribution" 
                      :key="name"
                      class="distribution-item"
                    >
                      <span class="class-name">{{ name }}</span>
                      <el-progress 
                        :percentage="getClassPercentage(count)" 
                        :stroke-width="12"
                        :format="() => count + '个'"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 模型训练 -->
        <el-tab-pane label="模型训练" name="training">
          <div class="tab-content">
            <el-row :gutter="20">
              <!-- 训练配置 -->
              <el-col :span="12">
                <el-card>
                  <template #header>训练参数配置</template>
                  <el-form :model="trainingConfig" label-width="100px">
                    <el-form-item label="基础模型">
                      <el-select v-model="trainingConfig.model_name" style="width: 100%">
                        <el-option label="YOLOv8n (最小)" value="yolov8n" />
                        <el-option label="YOLOv8s (小型)" value="yolov8s" />
                        <el-option label="YOLOv8m (中型)" value="yolov8m" />
                        <el-option label="YOLOv8l (大型)" value="yolov8l" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="训练轮数">
                      <el-input-number 
                        v-model="trainingConfig.epochs" 
                        :min="1" 
                        :max="500"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="批次大小">
                      <el-input-number 
                        v-model="trainingConfig.batch_size" 
                        :min="1" 
                        :max="64"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="学习率">
                      <el-input-number 
                        v-model="trainingConfig.learning_rate" 
                        :min="0.0001" 
                        :max="1"
                        :step="0.001"
                        :precision="4"
                        style="width: 100%"
                      />
                    </el-form-item>
                    <el-form-item label="验证集比例">
                      <el-slider 
                        v-model="trainingConfig.val_split" 
                        :min="0.1" 
                        :max="0.5"
                        :step="0.05"
                        :format-tooltip="(val) => (val * 100).toFixed(0) + '%'"
                      />
                    </el-form-item>
                    <el-form-item label="图像尺寸">
                      <el-select v-model="trainingConfig.img_size" style="width: 100%">
                        <el-option label="320" :value="320" />
                        <el-option label="416" :value="416" />
                        <el-option label="512" :value="512" />
                        <el-option label="640 (推荐)" :value="640" />
                        <el-option label="800" :value="800" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="预训练">
                      <el-switch v-model="trainingConfig.pretrained" />
                    </el-form-item>
                    <el-form-item>
                      <el-button 
                        type="primary" 
                        size="large"
                        :loading="startingTraining"
                        :disabled="isTraining"
                        @click="handleStartTraining"
                        style="width: 100%"
                      >
                        <el-icon><VideoPlay /></el-icon>
                        开始训练
                      </el-button>
                      <el-button 
                        v-if="isTraining"
                        type="danger" 
                        size="large"
                        @click="handleStopTraining"
                        style="width: 100%; margin-top: 10px; margin-left: 0"
                      >
                        <el-icon><VideoPause /></el-icon>
                        停止训练
                      </el-button>
                    </el-form-item>
                  </el-form>
                </el-card>
              </el-col>

              <!-- 训练进度 -->
              <el-col :span="12">
                <el-card>
                  <template #header>训练进度</template>
                  <div class="training-progress">
                    <div class="progress-info">
                      <el-tag :type="getStatusType(trainingProgress.status)" size="large">
                        {{ getStatusText(trainingProgress.status) }}
                      </el-tag>
                      <span class="epoch-info" v-if="trainingProgress.total_epochs">
                        Epoch: {{ trainingProgress.current_epoch }} / {{ trainingProgress.total_epochs }}
                      </span>
                    </div>
                    <el-progress 
                      :percentage="trainingProgress.progress_percent || 0"
                      :stroke-width="20"
                      :status="trainingProgress.status === 'completed' ? 'success' : ''"
                    />
                    <div class="metrics" v-if="trainingProgress.train_loss">
                      <div class="metric-item">
                        <span class="label">训练损失:</span>
                        <span class="value">{{ trainingProgress.train_loss?.toFixed(4) }}</span>
                      </div>
                      <div class="metric-item" v-if="trainingProgress.val_loss">
                        <span class="label">验证损失:</span>
                        <span class="value">{{ trainingProgress.val_loss?.toFixed(4) }}</span>
                      </div>
                    </div>
                    <p class="message">{{ trainingProgress.message }}</p>
                  </div>
                </el-card>

                <!-- 训练日志 -->
                <el-card class="log-card">
                  <template #header>
                    <div class="card-header">
                      <span>训练日志</span>
                      <el-button size="small" @click="fetchLogs">
                        <el-icon><Refresh /></el-icon>
                        刷新
                      </el-button>
                    </div>
                  </template>
                  <div class="log-container" ref="logContainer">
                    <div 
                      v-for="(log, index) in trainingLogs" 
                      :key="index"
                      :class="['log-item', `log-${log.level.toLowerCase()}`]"
                    >
                      <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
                      <span class="log-level">[{{ log.level }}]</span>
                      <span class="log-msg">{{ log.message }}</span>
                    </div>
                    <el-empty v-if="trainingLogs.length === 0" description="暂无日志" />
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- 模型管理 -->
        <el-tab-pane label="模型管理" name="models">
          <div class="tab-content">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>已训练模型列表</span>
                  <el-button type="primary" size="small" @click="fetchModels">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <el-table :data="modelList" style="width: 100%" v-loading="loadingModels">
                <el-table-column prop="name" label="模型名称" min-width="200" />
                <el-table-column prop="size" label="大小" width="120">
                  <template #default="{ row }">
                    {{ formatSize(row.size) }}
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column prop="is_active" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                      {{ row.is_active ? '使用中' : '备用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="{ row }">
                    <el-button 
                      v-if="!row.is_active"
                      type="primary" 
                      size="small" 
                      link
                      @click="handleActivateModel(row)"
                    >
                      激活
                    </el-button>
                    <el-popconfirm 
                      v-if="!row.is_active"
                      title="确定删除此模型？"
                      @confirm="handleDeleteModel(row)"
                    >
                      <template #reference>
                        <el-button type="danger" size="small" link>删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="modelList.length === 0" description="暂无训练模型" />
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Layout from '@/components/Layout.vue'
import {
  getDatasetStats,
  getDatasetFiles,
  uploadImages,
  uploadLabels,
  deleteDatasetFile,
  clearDataset,
  getClasses,
  updateClasses,
  startTraining,
  stopTraining,
  getTrainingProgress,
  getTrainingLogs,
  getModels,
  activateModel,
  deleteModel
} from '@/api/dataset'

// 当前标签页
const activeTab = ref('dataset')

// 数据集统计
const stats = ref({})

// 上传相关
const imageUploadRef = ref(null)
const labelUploadRef = ref(null)
const imageFileList = ref([])
const labelFileList = ref([])
const uploadingImages = ref(false)
const uploadingLabels = ref(false)

// 文件列表
const fileList = ref([])
const filePage = ref(1)
const filePageSize = ref(20)
const fileTotal = ref(0)
const loadingFiles = ref(false)

// 类别管理
const classesText = ref('')
const savingClasses = ref(false)

// 训练配置
const trainingConfig = ref({
  model_name: 'yolov8n',
  epochs: 100,
  batch_size: 16,
  learning_rate: 0.01,
  val_split: 0.2,
  img_size: 640,
  pretrained: true
})

// 训练进度
const trainingProgress = ref({
  status: 'idle',
  current_epoch: 0,
  total_epochs: 0,
  progress_percent: 0,
  train_loss: null,
  val_loss: null,
  message: ''
})
const trainingLogs = ref([])
const startingTraining = ref(false)
const logContainer = ref(null)
let progressTimer = null

// 模型管理
const modelList = ref([])
const loadingModels = ref(false)

// 计算属性
const isTraining = computed(() => 
  ['training', 'preparing'].includes(trainingProgress.value.status)
)

const trainingStatusText = computed(() => {
  const statusMap = {
    idle: '空闲',
    preparing: '准备中',
    training: '训练中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[trainingProgress.value.status] || '未知'
})

const trainingStatusColor = computed(() => {
  const colorMap = {
    idle: '#909399',
    preparing: '#e6a23c',
    training: '#409eff',
    completed: '#67c23a',
    failed: '#f56c6c',
    cancelled: '#909399'
  }
  return colorMap[trainingProgress.value.status] || '#909399'
})

// 获取统计信息
const fetchStats = async () => {
  try {
    stats.value = await getDatasetStats()
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 获取文件列表
const fetchFiles = async () => {
  loadingFiles.value = true
  try {
    const res = await getDatasetFiles({ page: filePage.value, size: filePageSize.value })
    fileList.value = res.images || []
    fileTotal.value = res.total || 0
  } catch (error) {
    console.error('获取文件列表失败:', error)
  } finally {
    loadingFiles.value = false
  }
}

// 处理图片文件选择
const handleImageChange = (file, fileList) => {
  imageFileList.value = fileList
}

// 处理标注文件选择
const handleLabelChange = (file, fileList) => {
  labelFileList.value = fileList
}

// 提交图片上传
const submitImageUpload = async () => {
  if (imageFileList.value.length === 0) return
  
  uploadingImages.value = true
  try {
    const formData = new FormData()
    imageFileList.value.forEach(file => {
      formData.append('files', file.raw)
    })
    
    const res = await uploadImages(formData)
    ElMessage.success(res.message || '上传成功')
    imageFileList.value = []
    fetchStats()
    fetchFiles()
  } catch (error) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  } finally {
    uploadingImages.value = false
  }
}

// 提交标注上传
const submitLabelUpload = async () => {
  if (labelFileList.value.length === 0) return
  
  uploadingLabels.value = true
  try {
    const formData = new FormData()
    labelFileList.value.forEach(file => {
      formData.append('files', file.raw)
    })
    
    const res = await uploadLabels(formData)
    ElMessage.success(res.message || '上传成功')
    labelFileList.value = []
    fetchStats()
    fetchFiles()
  } catch (error) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  } finally {
    uploadingLabels.value = false
  }
}

// 删除文件
const handleDeleteFile = async (filename) => {
  try {
    await deleteDatasetFile(filename)
    ElMessage.success('删除成功')
    fetchStats()
    fetchFiles()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 清空数据集
const handleClearDataset = async () => {
  try {
    await clearDataset()
    ElMessage.success('数据集已清空')
    fetchStats()
    fetchFiles()
  } catch (error) {
    ElMessage.error('清空失败')
  }
}

// 获取类别
const fetchClasses = async () => {
  try {
    const res = await getClasses()
    classesText.value = (res.classes || []).join('\n')
  } catch (error) {
    console.error('获取类别失败:', error)
  }
}

// 保存类别
const saveClasses = async () => {
  savingClasses.value = true
  try {
    const classes = classesText.value.split('\n').map(s => s.trim()).filter(s => s)
    await updateClasses(classes)
    ElMessage.success('类别保存成功')
    fetchStats()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    savingClasses.value = false
  }
}

// 获取类别百分比
const getClassPercentage = (count) => {
  const total = Object.values(stats.value.class_distribution || {}).reduce((a, b) => a + b, 0)
  return total > 0 ? Math.round((count / total) * 100) : 0
}

// 开始训练
const handleStartTraining = async () => {
  if (stats.value.labeled_images < 10) {
    ElMessage.warning(`已标注图片数量不足，当前 ${stats.value.labeled_images} 张，至少需要 10 张`)
    return
  }
  
  if (stats.value.total_classes === 0) {
    ElMessage.warning('请先配置类别映射')
    return
  }
  
  startingTraining.value = true
  try {
    await startTraining(trainingConfig.value)
    ElMessage.success('训练已启动')
    startProgressPolling()
  } catch (error) {
    ElMessage.error(error.message || '启动训练失败')
  } finally {
    startingTraining.value = false
  }
}

// 停止训练
const handleStopTraining = async () => {
  try {
    await stopTraining()
    ElMessage.success('正在停止训练...')
  } catch (error) {
    ElMessage.error('停止训练失败')
  }
}

// 获取训练进度
const fetchProgress = async () => {
  try {
    trainingProgress.value = await getTrainingProgress()
  } catch (error) {
    console.error('获取训练进度失败:', error)
  }
}

// 获取训练日志
const fetchLogs = async () => {
  try {
    const res = await getTrainingLogs(100)
    trainingLogs.value = res.logs || []
    // 滚动到底部
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })
  } catch (error) {
    console.error('获取训练日志失败:', error)
  }
}

// 开始轮询训练进度
const startProgressPolling = () => {
  stopProgressPolling()
  progressTimer = setInterval(async () => {
    await fetchProgress()
    await fetchLogs()
    
    // 训练结束后停止轮询
    if (!isTraining.value && trainingProgress.value.status !== 'idle') {
      stopProgressPolling()
      fetchModels()
    }
  }, 2000)
}

// 停止轮询
const stopProgressPolling = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

// 获取模型列表
const fetchModels = async () => {
  loadingModels.value = true
  try {
    const res = await getModels()
    modelList.value = res.models || []
  } catch (error) {
    console.error('获取模型列表失败:', error)
  } finally {
    loadingModels.value = false
  }
}

// 激活模型
const handleActivateModel = async (model) => {
  try {
    await activateModel(model.path)
    ElMessage.success('模型已激活')
    fetchModels()
  } catch (error) {
    ElMessage.error('激活失败')
  }
}

// 删除模型
const handleDeleteModel = async (model) => {
  try {
    await deleteModel(model.path)
    ElMessage.success('模型已删除')
    fetchModels()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 工具函数
const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return bytes.toFixed(1) + ' ' + units[i]
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const formatLogTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

const getStatusType = (status) => {
  const typeMap = {
    idle: 'info',
    preparing: 'warning',
    training: '',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    idle: '空闲',
    preparing: '准备中',
    training: '训练中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return textMap[status] || '未知'
}

// 生命周期
onMounted(() => {
  fetchStats()
  fetchFiles()
  fetchClasses()
  fetchProgress()
  fetchLogs()
  fetchModels()
  
  // 如果正在训练，开始轮询
  if (isTraining.value) {
    startProgressPolling()
  }
})

onUnmounted(() => {
  stopProgressPolling()
})
</script>

<style scoped>
.dataset-manage {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.stat-label {
  color: #999;
  margin: 5px 0 0;
  font-size: 14px;
}

.main-tabs {
  background: #fff;
  border-radius: 4px;
}

.tab-content {
  padding: 20px;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  margin-bottom: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-list-card {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.classes-editor {
  .tip {
    color: #909399;
    margin-bottom: 10px;
    font-size: 14px;
  }
}

.class-distribution {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.class-distribution h4 {
  margin: 0 0 15px;
  color: #333;
}

.distribution-list {
  max-height: 300px;
  overflow-y: auto;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.distribution-item .class-name {
  width: 80px;
  flex-shrink: 0;
  color: #333;
}

.distribution-item .el-progress {
  flex: 1;
}

.training-progress {
  .progress-info {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
  }
  
  .epoch-info {
    color: #666;
    font-size: 14px;
  }
  
  .metrics {
    display: flex;
    gap: 30px;
    margin-top: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }
  
  .metric-item {
    .label {
      color: #909399;
      margin-right: 8px;
    }
    .value {
      color: #333;
      font-weight: bold;
    }
  }
  
  .message {
    margin-top: 10px;
    color: #666;
    font-size: 14px;
  }
}

.log-card {
  margin-top: 20px;
}

.log-container {
  height: 250px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background: #1e1e1e;
  border-radius: 4px;
  padding: 10px;
}

.log-item {
  padding: 2px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-time {
  color: #6a9955;
  margin-right: 8px;
}

.log-level {
  margin-right: 8px;
}

.log-info .log-level {
  color: #4fc1ff;
}

.log-warning .log-level {
  color: #dcdcaa;
}

.log-error .log-level {
  color: #f44747;
}

.log-msg {
  color: #d4d4d4;
}

.log-info .log-msg {
  color: #d4d4d4;
}

.log-warning .log-msg {
  color: #dcdcaa;
}

.log-error .log-msg {
  color: #f44747;
}
</style>
