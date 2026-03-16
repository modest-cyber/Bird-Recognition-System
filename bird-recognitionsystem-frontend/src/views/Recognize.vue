<template>
  <Layout>
    <div class="recognize">
      <el-card class="upload-card">
        <h2>鸟类识别</h2>
        <p class="tip">上传鸟类图片，AI 将自动识别鸟类种类</p>
        
        <el-upload
          class="upload-area"
          drag
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          accept=".jpg,.jpeg,.png,.webp"
        >
          <div v-if="previewUrl" class="preview-container">
            <el-image :src="previewUrl" fit="contain" />
          </div>
          <div v-else class="upload-placeholder">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>将图片拖到此处，或<em>点击上传</em></p>
              <p class="upload-hint">支持 jpg/png/webp 格式，大小不超过 10MB</p>
            </div>
          </div>
        </el-upload>
        
        <div class="action-bar">
          <el-button v-if="selectedFile" @click="clearFile">清除图片</el-button>
          <el-button 
            type="primary" 
            size="large"
            :loading="loading"
            :disabled="!selectedFile"
            @click="handleRecognize"
          >
            <el-icon><Search /></el-icon>
            开始识别
          </el-button>
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { recognize } from '@/api/record'
import { ElMessage } from 'element-plus'

const router = useRouter()

const selectedFile = ref(null)
const previewUrl = ref('')
const loading = ref(false)

const handleFileChange = (file) => {
  const rawFile = file.raw
  
  // 校验文件格式
  const validTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!validTypes.includes(rawFile.type)) {
    ElMessage.error('只支持 jpg/png/webp 格式的图片')
    return
  }
  
  // 校验文件大小（10MB）
  if (rawFile.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 10MB')
    return
  }
  
  selectedFile.value = rawFile
  previewUrl.value = URL.createObjectURL(rawFile)
}

const clearFile = () => {
  selectedFile.value = null
  previewUrl.value = ''
}

const handleRecognize = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  loading.value = true
  try {
    const result = await recognize(selectedFile.value)
    // 跳转到结果页，携带识别结果
    router.push({
      path: '/result',
      query: { id: result.record_id }
    })
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recognize {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  text-align: center;
}

.upload-card h2 {
  margin-bottom: 10px;
  color: #333;
}

.tip {
  color: #666;
  margin-bottom: 30px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container {
  width: 100%;
  height: 280px;
}

.preview-container .el-image {
  width: 100%;
  height: 100%;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 60px;
  color: #c0c4cc;
  margin-bottom: 20px;
}

.upload-text p {
  color: #666;
  margin: 0;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin-top: 10px !important;
}

.action-bar {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style>
