<template>
  <Layout>
    <section class="admin-dashboard">
      <div class="hero">
        <div>
          <p class="eyebrow">Admin Console</p>
          <h1>后台管理</h1>
          <p class="subtitle">只保留高频后台操作，通过页签切换进入用户管理和数据集训练。</p>
        </div>
        <div class="hero-meta">
          <span class="meta-chip">{{ stats.total_users || 0 }} 位用户</span>
          <span class="meta-chip">{{ stats.total_records || 0 }} 条识别记录</span>
          <span class="meta-chip">今日 {{ stats.today_records || 0 }} 次识别</span>
        </div>
      </div>

      <el-card class="panel-card" shadow="never">
        <el-tabs v-model="activeTab" class="admin-tabs" stretch>
          <el-tab-pane label="用户管理" name="users">
            <div class="tab-panel">
              <p class="tab-text">查看用户列表、搜索用户，并启用或禁用普通账号。</p>
              <div class="tab-actions">
                <el-button type="primary" size="large" @click="$router.push('/admin/users')">进入用户管理</el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="数据集与训练" name="dataset">
            <div class="tab-panel">
              <p class="tab-text">管理数据集文件、类别映射和训练任务。</p>
              <div class="tab-actions">
                <el-button type="primary" size="large" @click="$router.push('/admin/dataset')">进入数据集与训练</el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </section>
  </Layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { getStats } from '@/api/admin'

const activeTab = ref('users')
const stats = ref({})

const fetchStats = async () => {
  try {
    stats.value = await getStats()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.admin-dashboard {
  max-width: 1180px;
  margin: 0 auto;
}

.hero {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
  padding: 32px;
  margin-bottom: 24px;
  border-radius: 28px;
  color: #fff;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.24), transparent 32%),
    linear-gradient(135deg, #123b31 0%, #1f6b54 50%, #7dc58d 100%);
  box-shadow: 0 22px 60px rgba(18, 59, 49, 0.2);
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  opacity: 0.72;
}

.hero h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.05;
}

.subtitle {
  max-width: 520px;
  margin: 14px 0 0;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.86);
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: flex-end;
  gap: 12px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 16px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(8px);
}

.panel-card {
  border: none;
  border-radius: 24px;
}

.tab-panel {
  min-height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 18px;
  padding: 18px 6px 6px;
}

.tab-text {
  margin: 0;
  max-width: 560px;
  font-size: 15px;
  line-height: 1.8;
  color: #4f5d56;
}

.tab-actions {
  display: flex;
  gap: 12px;
}

:deep(.el-tabs__item) {
  height: 50px;
  font-weight: 600;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .hero h1 {
    font-size: 32px;
  }

  .hero-meta {
    justify-content: flex-start;
  }
}
</style>
