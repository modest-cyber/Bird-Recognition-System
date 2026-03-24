<template>
  <Layout>
    <div class="result">
      <el-row :gutter="20">
        <el-col :span="15">
          <el-card>
            <div class="card-header">
              <div>
                <h3>鸟区域检测结果</h3>
                <p class="card-subtitle">前端根据接口返回的 bbox 在原图上直接绘制检测框。</p>
              </div>
              <el-tag type="success">共 {{ resultData?.bird_count || 0 }} 个区域</el-tag>
            </div>

            <div class="result-image">
              <div v-if="resultData?.original_image_url" ref="imageStage" class="image-stage">
                <img
                  ref="imageRef"
                  class="target-image"
                  :src="getImageUrl(resultData.original_image_url)"
                  alt="bird-detection"
                  @load="handleImageLoad"
                />
                <button
                  v-for="(item, index) in resultData.results"
                  :key="`${index}-${item.bbox.join('-')}`"
                  type="button"
                  class="bbox"
                  :class="{ active: activeIndex === index }"
                  :style="getBoxStyle(item.bbox, index)"
                  @click="activeIndex = index"
                >
                  <span class="bbox-label">区域 {{ index + 1 }} {{ formatConfidence(item.confidence) }}</span>
                </button>
              </div>
              <el-empty v-else description="暂无图片" />
            </div>

            <div v-if="resultData?.annotated_image_url" class="annotated-preview">
              <span>后端标注图：</span>
              <el-link :href="getImageUrl(resultData.annotated_image_url)" target="_blank" type="primary">打开查看</el-link>
            </div>
          </el-card>
        </el-col>

        <el-col :span="9">
          <el-card>
            <h3>区域列表</h3>
            <div v-if="resultData?.results?.length" class="result-list">
              <div
                v-for="(item, index) in resultData.results"
                :key="index"
                class="result-item"
                :class="{ active: activeIndex === index }"
                @mouseenter="activeIndex = index"
                @click="activeIndex = index"
              >
                <div class="result-info">
                  <span class="bird-name">区域 {{ index + 1 }}</span>
                  <span class="confidence">{{ formatConfidence(item.confidence) }}</span>
                </div>
                <div class="bbox-text">bbox: [{{ item.bbox.join(', ') }}]</div>
                <div class="bbox-text">中心点: [{{ item.center.join(', ') }}]</div>
                <el-progress :percentage="Number((item.confidence * 100).toFixed(1))" :show-text="false" :color="getProgressColor(item.confidence)" />
              </div>
            </div>
            <el-empty v-else description="未检测到鸟区域" />
          </el-card>

          <el-card v-if="activeDetection" class="detail-card">
            <h3>当前区域</h3>
            <div class="detail-row"><span>区域编号</span><strong>#{{ activeIndex + 1 }}</strong></div>
            <div class="detail-row"><span>置信度</span><strong>{{ formatConfidence(activeDetection.confidence) }}</strong></div>
            <div class="detail-row"><span>中心点</span><strong>[{{ activeDetection.center.join(', ') }}]</strong></div>
            <div class="detail-row"><span>面积</span><strong>{{ activeDetection.area }}</strong></div>
          </el-card>

          <div class="actions">
            <el-button type="primary" @click="$router.push('/recognize')">
              <el-icon><RefreshRight /></el-icon>
              重新检测
            </el-button>
            <el-button @click="$router.push('/history')">查看历史</el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { getRecords } from '@/api/record'

const route = useRoute()

const resultData = ref(null)
const loading = ref(false)
const activeIndex = ref(0)
const imageRef = ref(null)
const imageSize = ref({ width: 1, height: 1 })

const activeDetection = computed(() => resultData.value?.results?.[activeIndex.value] || null)

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

const formatConfidence = (confidence) => `${(confidence * 100).toFixed(1)}%`

const getBoxStyle = (bbox, index) => {
  const [x1, y1, x2, y2] = bbox
  const width = imageSize.value.width || 1
  const height = imageSize.value.height || 1
  return {
    left: `${(x1 / width) * 100}%`,
    top: `${(y1 / height) * 100}%`,
    width: `${((x2 - x1) / width) * 100}%`,
    height: `${((y2 - y1) / height) * 100}%`,
    borderColor: activeIndex.value === index ? '#ff5a36' : '#36cfc9'
  }
}

const handleImageLoad = (event) => {
  imageSize.value = {
    width: event.target.naturalWidth || 1,
    height: event.target.naturalHeight || 1
  }
}

const normalizeResultData = (data) => {
  if (!data) return null
  const results = (data.results || data.result_json || []).map((item) => ({
    bird_id: item.bird_id ?? null,
    bird_name: item.bird_name || 'bird',
    confidence: Number(item.confidence || 0),
    bbox: item.bbox || [0, 0, 0, 0],
    center: item.center || [
      Number((((item.bbox?.[0] || 0) + (item.bbox?.[2] || 0)) / 2).toFixed(2)),
      Number((((item.bbox?.[1] || 0) + (item.bbox?.[3] || 0)) / 2).toFixed(2))
    ],
    area: item.area ?? Math.max(0, (item.bbox?.[2] || 0) - (item.bbox?.[0] || 0)) * Math.max(0, (item.bbox?.[3] || 0) - (item.bbox?.[1] || 0))
  }))

  return {
    record_id: data.record_id || data.id,
    original_image_url: data.original_image_url || data.image_url,
    annotated_image_url: data.annotated_image_url || data.image_url,
    bird_count: data.bird_count ?? results.length,
    results
  }
}

const loadFromSession = () => {
  const cached = sessionStorage.getItem('latestRecognizeResult')
  if (!cached) return null

  try {
    const parsed = JSON.parse(cached)
    if (!route.query.id || Number(parsed.record_id) === Number(route.query.id)) {
      return normalizeResultData(parsed)
    }
  } catch (error) {
    console.error(error)
  }

  return null
}

onMounted(async () => {
  const cached = loadFromSession()
  if (cached) {
    resultData.value = cached
    await nextTick()
    return
  }

  const recordId = Number(route.query.id)
  if (!recordId) return

  loading.value = true
  try {
    const data = await getRecords({ page: 1, size: 100 })
    const record = data.list?.find((item) => item.id === recordId)
    if (record) {
      resultData.value = normalizeResultData(record)
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.result {
  max-width: 1280px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.card-header h3,
.detail-card h3,
.el-card h3 {
  margin: 0;
  color: #333;
}

.card-subtitle {
  margin: 6px 0 0;
  color: #666;
  font-size: 13px;
}

.result-image {
  min-height: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  border-radius: 12px;
  padding: 20px;
}

.image-stage {
  position: relative;
  display: inline-block;
  max-width: 100%;
  max-height: 420px;
}

.target-image {
  display: block;
  max-width: 100%;
  max-height: 420px;
  border-radius: 10px;
}

.bbox {
  position: absolute;
  background: rgba(54, 207, 201, 0.08);
  border: 2px solid #36cfc9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bbox.active {
  background: rgba(255, 90, 54, 0.1);
  border-color: #ff5a36;
  box-shadow: 0 0 0 2px rgba(255, 90, 54, 0.12);
}

.bbox-label {
  position: absolute;
  top: -30px;
  left: 0;
  white-space: nowrap;
  background: rgba(17, 24, 39, 0.86);
  color: #fff;
  font-size: 12px;
  line-height: 1;
  padding: 7px 10px;
  border-radius: 999px;
}

.annotated-preview {
  margin-top: 14px;
  font-size: 13px;
  color: #666;
}

.result-list {
  max-height: 440px;
  overflow-y: auto;
}

.result-item {
  padding: 14px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-item:hover,
.result-item.active {
  border-color: #409eff;
  background: #f7fbff;
}

.result-info,
.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.result-info {
  margin-bottom: 8px;
}

.bird-name,
.confidence {
  font-weight: 700;
}

.confidence {
  color: #409eff;
}

.bbox-text {
  color: #666;
  font-size: 12px;
  margin-bottom: 8px;
}

.detail-card {
  margin-top: 16px;
}

.detail-card h3 {
  margin-bottom: 14px;
}

.detail-row {
  margin-bottom: 12px;
  color: #666;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
