<template>
  <Layout>
    <div class="bird-list">
      <el-card>
        <!-- 搜索筛选 -->
        <div class="filter-bar">
          <el-input 
            v-model="searchName" 
            placeholder="搜索鸟类名称"
            prefix-icon="Search"
            clearable
            style="width: 250px"
            @keyup.enter="handleSearch"
          />
          <el-select 
            v-model="searchFamily" 
            placeholder="按科目筛选"
            clearable
            style="width: 150px"
          >
            <el-option label="鹭科" value="鹭科" />
            <el-option label="雀科" value="雀科" />
            <el-option label="鸦科" value="鸦科" />
            <el-option label="鹰科" value="鹰科" />
            <el-option label="鸭科" value="鸭科" />
          </el-select>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>
        
        <!-- 鸟类列表 -->
        <div v-loading="loading" class="card-container">
          <el-row :gutter="20">
            <el-col 
              v-for="bird in birdList" 
              :key="bird.id" 
              :xs="12" :sm="8" :md="6"
            >
              <BirdCard 
                :bird="bird" 
                @click="$router.push(`/birds/${bird.id}`)"
              />
            </el-col>
          </el-row>
          
          <el-empty v-if="!loading && !birdList.length" description="暂无数据" />
        </div>
        
        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 36]"
            layout="total, sizes, prev, pager, next"
            @size-change="fetchData"
            @current-change="fetchData"
          />
        </div>
      </el-card>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import BirdCard from '@/components/BirdCard.vue'
import { getBirdList } from '@/api/bird'

const birdList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const loading = ref(false)
const searchName = ref('')
const searchFamily = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getBirdList({
      page: currentPage.value,
      size: pageSize.value,
      name: searchName.value || undefined,
      family: searchFamily.value || undefined
    })
    birdList.value = data.list || []
    total.value = data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bird-list {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.card-container {
  min-height: 300px;
}

.card-container .el-col {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
