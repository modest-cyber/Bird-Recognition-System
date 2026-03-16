<template>
  <Layout>
    <div class="result">
      <el-row :gutter="20">
        <!-- 左侧：识别结果图 -->
        <el-col :span="14">
          <el-card>
            <h3>识别结果</h3>
            <div class="result-image">
              <el-image 
                v-if="resultData?.annotated_image_url"
                :src="getImageUrl(resultData.annotated_image_url)" 
                fit="contain"
                :preview-src-list="[getImageUrl(resultData.annotated_image_url)]"
              />
              <el-empty v-else description="暂无图片" />
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧：识别结果列表 -->
        <el-col :span="10">
          <el-card>
            <h3>识别到的鸟类</h3>
            <div v-if="resultData?.results?.length" class="result-list">
              <div 
                v-for="(item, index) in resultData.results" 
                :key="index"
                class="result-item"
                @click="goDetail(item.bird_id)"
              >
                <div class="result-info">
                  <span class="bird-name">{{ item.bird_name }}</span>
                  <span class="confidence">{{ (item.confidence * 100).toFixed(1) }}%</span>
                </div>
                <el-progress 
                  :percentage="item.confidence * 100" 
                  :color="getProgressColor(item.confidence)"
                  :show-text="false"
                />
              </div>
            </div>
            <el-empty v-else description="未识别到鸟类" />
          </el-card>
          
          <!-- 操作按钮 -->
          <div class="actions">
            <el-button type="primary" @click="$router.push('/recognize')">
              <el-icon><RefreshRight /></el-icon>
              重新识别
            </el-button>
            <el-button @click="$router.push('/history')">
              查看历史
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { getRecords } from '@/api/record'

const route = useRoute()
const router = useRouter()

const resultData = ref(null)
const loading = ref(false)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const getProgressColor = (confidence) => {
  if (confidence >= 0.8) return '#67c23a'
  if (confidence >= 0.5) return '#e6a23c'
  return '#f56c6c'
}

const goDetail = (birdId) => {
  if (birdId) {
    router.push(`/birds/${birdId}`)
  }
}

onMounted(async () => {
  const recordId = route.query.id
  if (recordId) {
    loading.value = true
    try {
      const data = await getRecords({ page: 1, size: 100 })
      const record = data.list?.find(r => r.id === parseInt(recordId))
      if (record) {
        resultData.value = {
          annotated_image_url: record.annotated_image_url || record.image_url,
          results: record.result_json
        }
      }
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.result {
  max-width: 1200px;
  margin: 0 auto;
}

h3 {
  margin: 0 0 20px;
  color: #333;
}

.result-image {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}

.result-image .el-image {
  max-width: 100%;
  max-height: 100%;
}

.result-list {
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.result-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.result-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.bird-name {
  font-weight: bold;
  color: #333;
}

.confidence {
  color: #409eff;
  font-weight: bold;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
