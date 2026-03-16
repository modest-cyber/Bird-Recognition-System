<template>
  <Layout>
    <div class="bird-detail" v-loading="loading">
      <el-card v-if="bird">
        <el-row :gutter="30">
          <!-- 左侧图片 -->
          <el-col :span="10">
            <div class="bird-image">
              <el-image 
                :src="getImageUrl(bird.image_url)" 
                fit="cover"
                :preview-src-list="[getImageUrl(bird.image_url)]"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon :size="80"><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </el-col>
          
          <!-- 右侧信息 -->
          <el-col :span="14">
            <h1 class="bird-name">{{ bird.name }}</h1>
            <p class="bird-latin">{{ bird.latin_name || '暂无学名' }}</p>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="科目">
                {{ bird.family || '未分类' }}
              </el-descriptions-item>
              <el-descriptions-item label="分布地区">
                <el-tag 
                  v-for="region in (bird.regions || [])" 
                  :key="region"
                  type="info"
                  style="margin-right: 5px"
                >
                  {{ region }}
                </el-tag>
                <span v-if="!bird.regions?.length">暂无数据</span>
              </el-descriptions-item>
            </el-descriptions>
            
            <div class="bird-description">
              <h3>特征描述</h3>
              <p>{{ bird.description || '暂无描述' }}</p>
            </div>
            
            <el-button @click="$router.push('/birds')">
              <el-icon><Back /></el-icon>
              返回列表
            </el-button>
          </el-col>
        </el-row>
      </el-card>
      
      <el-empty v-else-if="!loading" description="鸟类信息不存在" />
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { getBirdDetail } from '@/api/bird'

const route = useRoute()
const bird = ref(null)
const loading = ref(false)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    loading.value = true
    try {
      bird.value = await getBirdDetail(id)
    } catch (error) {
      console.error(error)
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.bird-detail {
  max-width: 1000px;
  margin: 0 auto;
}

.bird-image {
  height: 350px;
  border-radius: 8px;
  overflow: hidden;
}

.bird-image .el-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #ccc;
}

.bird-name {
  font-size: 28px;
  margin: 0 0 5px;
  color: #333;
}

.bird-latin {
  color: #999;
  font-style: italic;
  margin-bottom: 20px;
}

.bird-description {
  margin: 20px 0;
}

.bird-description h3 {
  margin-bottom: 10px;
  color: #333;
}

.bird-description p {
  color: #666;
  line-height: 1.8;
}
</style>
