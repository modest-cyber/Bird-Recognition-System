<template>
  <Layout>
    <div class="dashboard">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stat-cards">
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="40" color="#409eff"><User /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.total_users || 0 }}</p>
                <p class="stat-label">总用户数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="40" color="#67c23a"><Document /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.total_records || 0 }}</p>
                <p class="stat-label">总识别次数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <div class="stat-item">
              <el-icon :size="40" color="#e6a23c"><Clock /></el-icon>
              <div class="stat-info">
                <p class="stat-value">{{ stats.today_records || 0 }}</p>
                <p class="stat-label">今日识别</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 快捷入口 -->
      <el-row :gutter="20" class="quick-actions">
        <el-col :span="12">
          <el-card>
            <template #header>快捷操作</template>
            <div class="action-buttons">
              <el-button type="primary" @click="$router.push('/admin/users')">
                <el-icon><User /></el-icon>
                用户管理
              </el-button>
              <el-button type="success" @click="$router.push('/admin/birds')">
                <el-icon><Collection /></el-icon>
                鸟类管理
              </el-button>
              <el-button type="warning" @click="$router.push('/admin/dataset')">
                <el-icon><Cpu /></el-icon>
                数据集与训练
              </el-button>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>鸟类识别排行</template>
            <div v-if="stats.bird_rank?.length" class="rank-list">
              <div 
                v-for="(item, index) in stats.bird_rank.slice(0, 5)" 
                :key="index"
                class="rank-item"
              >
                <span class="rank-index">{{ index + 1 }}</span>
                <span class="rank-name">{{ item.bird_name }}</span>
                <span class="rank-count">{{ item.count }}次</span>
              </div>
            </div>
            <el-empty v-else description="暂无数据" :image-size="60" />
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 图表区域 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card>
            <template #header>识别趋势（近7天）</template>
            <div ref="chartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Layout from '@/components/Layout.vue'
import { getStats } from '@/api/admin'
import * as echarts from 'echarts'

const stats = ref({})
const chartRef = ref(null)
let chart = null

const fetchStats = async () => {
  try {
    stats.value = await getStats()
    renderChart()
  } catch (error) {
    console.error(error)
  }
}

const renderChart = () => {
  if (!chartRef.value || !stats.value.daily_trend) return
  
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  const data = stats.value.daily_trend || []
  
  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '识别次数',
      type: 'line',
      smooth: true,
      data: data.map(item => item.count),
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      },
      lineStyle: {
        color: '#409eff'
      },
      itemStyle: {
        color: '#409eff'
      }
    }]
  })
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.stat-label {
  color: #999;
  margin: 5px 0 0;
}

.quick-actions {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.rank-list {
  max-height: 200px;
  overflow-y: auto;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-index {
  width: 24px;
  height: 24px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 10px;
}

.rank-name {
  flex: 1;
  color: #333;
}

.rank-count {
  color: #999;
}

.chart-container {
  height: 300px;
}
</style>
