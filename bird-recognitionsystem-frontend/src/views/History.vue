<template>
  <Layout>
    <div class="history">
      <el-card>
        <template #header>
          <span>检测历史</span>
        </template>

        <el-table v-loading="loading" :data="records" style="width: 100%">
          <el-table-column label="图片" width="120">
            <template #default="{ row }">
              <el-image
                :src="getImageUrl(row.image_url)"
                fit="cover"
                style="width: 80px; height: 60px; border-radius: 4px;"
                :preview-src-list="[getImageUrl(row.image_url)]"
              />
            </template>
          </el-table-column>
          <el-table-column label="检测结果" min-width="220">
            <template #default="{ row }">
              <div v-if="row.result_json?.length">
                <el-tag v-for="(item, index) in row.result_json.slice(0, 3)" :key="index" style="margin: 2px">
                  区域 {{ index + 1 }} ({{ (item.confidence * 100).toFixed(0) }}%)
                </el-tag>
                <span v-if="row.result_json.length > 3">...</span>
              </div>
              <span v-else class="no-result">未检测到鸟区域</span>
            </template>
          </el-table-column>
          <el-table-column label="检测时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">查看详情</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loading && !records.length" description="暂无检测记录" />

        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { deleteRecord, getRecords } from '@/api/record'

const router = useRouter()

const records = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getRecords({ page: currentPage.value, size: pageSize.value })
    records.value = data.list || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  router.push({ path: '/result', query: { id: row.id } })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteRecord(row.id)
    ElMessage.success('删除成功')
    fetchData()
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.history {
  max-width: 1200px;
  margin: 0 auto;
}

.no-result {
  color: #999;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
