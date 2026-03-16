<template>
  <Layout>
    <div class="user-manage">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>用户管理</span>
            <el-input 
              v-model="searchName" 
              placeholder="搜索用户名"
              prefix-icon="Search"
              clearable
              style="width: 250px"
              @keyup.enter="handleSearch"
            />
          </div>
        </template>
        
        <el-table v-loading="loading" :data="users" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : ''">
                {{ row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="180" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                :disabled="row.role === 'admin'"
                @change="handleStatusChange(row)"
              />
            </template>
          </el-table-column>
        </el-table>
        
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
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { getUserList, updateUserStatus } from '@/api/admin'
import { ElMessage } from 'element-plus'

const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const searchName = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getUserList({
      page: currentPage.value,
      size: pageSize.value,
      username: searchName.value || undefined
    })
    users.value = data.list || []
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

const handleStatusChange = async (row) => {
  try {
    await updateUserStatus(row.id, row.is_active)
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (error) {
    row.is_active = !row.is_active
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.user-manage {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
