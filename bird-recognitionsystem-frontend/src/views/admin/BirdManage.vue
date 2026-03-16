<template>
  <Layout>
    <div class="bird-manage">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>鸟类管理</span>
            <el-button type="primary" @click="openDialog()">
              <el-icon><Plus /></el-icon>
              添加鸟类
            </el-button>
          </div>
        </template>
        
        <el-table v-loading="loading" :data="birds" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="图片" width="100">
            <template #default="{ row }">
              <el-image 
                :src="getImageUrl(row.image_url)" 
                fit="cover"
                style="width: 60px; height: 45px; border-radius: 4px;"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="latin_name" label="学名" />
          <el-table-column prop="family" label="科目" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
      
      <!-- 编辑弹窗 -->
      <el-dialog 
        v-model="dialogVisible" 
        :title="editingBird ? '编辑鸟类' : '添加鸟类'"
        width="500px"
      >
        <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
          <el-form-item label="名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入中文名" />
          </el-form-item>
          <el-form-item label="学名" prop="latin_name">
            <el-input v-model="form.latin_name" placeholder="请输入学名" />
          </el-form-item>
          <el-form-item label="科目" prop="family">
            <el-input v-model="form.family" placeholder="请输入科目" />
          </el-form-item>
          <el-form-item label="图片URL" prop="image_url">
            <el-input v-model="form.image_url" placeholder="请输入图片路径" />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="4"
              placeholder="请输入特征描述" 
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </div>
  </Layout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { getBirdList, addBird, updateBird, deleteBird } from '@/api/bird'
import { ElMessage, ElMessageBox } from 'element-plus'

const birds = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const editingBird = ref(null)
const saving = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '',
  latin_name: '',
  family: '',
  image_url: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const getImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `http://localhost:8000${url}`
}

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getBirdList({
      page: currentPage.value,
      size: pageSize.value
    })
    birds.value = data.list || []
    total.value = data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openDialog = (bird = null) => {
  editingBird.value = bird
  if (bird) {
    Object.assign(form, {
      name: bird.name,
      latin_name: bird.latin_name || '',
      family: bird.family || '',
      image_url: bird.image_url || '',
      description: bird.description || ''
    })
  } else {
    Object.assign(form, {
      name: '',
      latin_name: '',
      family: '',
      image_url: '',
      description: ''
    })
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    if (editingBird.value) {
      await updateBird(editingBird.value.id, form)
      ElMessage.success('修改成功')
    } else {
      await addBird(form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    saving.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteBird(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      // 错误已在拦截器中处理
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bird-manage {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-error {
  width: 60px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #ccc;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
