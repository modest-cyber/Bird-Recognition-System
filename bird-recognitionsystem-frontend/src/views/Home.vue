<template>
  <Layout>
    <div class="home">
      <!-- 横幅区域 -->
      <section class="banner">
        <div class="banner-content">
          <h1>鸟类识别系统</h1>
          <p>基于 YOLOv8 深度学习的智能鸟类识别平台</p>
          <el-button type="primary" size="large" @click="goRecognize">
            <el-icon><Camera /></el-icon>
            立即识别
          </el-button>
        </div>
      </section>
      
      <!-- 功能介绍 -->
      <section class="features">
        <h2>功能特点</h2>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon :size="40" color="#409eff"><Camera /></el-icon>
              </template>
              <h3>智能识别</h3>
              <p>上传鸟类图片，AI 自动识别鸟类种类</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon :size="40" color="#67c23a"><Collection /></el-icon>
              </template>
              <h3>鸟类百科</h3>
              <p>丰富的鸟类知识库，了解各种鸟类信息</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon :size="40" color="#e6a23c"><Clock /></el-icon>
              </template>
              <h3>历史记录</h3>
              <p>保存识别历史，随时查看以往识别结果</p>
            </el-card>
          </el-col>
        </el-row>
      </section>
      
      <!-- 快捷入口 -->
      <section class="quick-entry">
        <h2>快捷入口</h2>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="entry-card" shadow="hover" @click="$router.push('/birds')">
              <el-icon :size="50"><Reading /></el-icon>
              <h3>鸟类百科</h3>
            </el-card>
          </el-col>
          <el-col :span="8" v-if="userStore.isLoggedIn">
            <el-card class="entry-card" shadow="hover" @click="$router.push('/history')">
              <el-icon :size="50"><Clock /></el-icon>
              <h3>识别历史</h3>
            </el-card>
          </el-col>
          <el-col :span="8" v-if="userStore.isAdmin">
            <el-card class="entry-card" shadow="hover" @click="$router.push('/admin')">
              <el-icon :size="50"><Setting /></el-icon>
              <h3>管理后台</h3>
            </el-card>
          </el-col>
        </el-row>
      </section>
    </div>
  </Layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Layout from '@/components/Layout.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const goRecognize = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push('/recognize')
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  padding: 60px 40px;
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}

.banner h1 {
  font-size: 36px;
  margin-bottom: 15px;
}

.banner p {
  font-size: 18px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.features {
  margin-bottom: 40px;
}

.features h2,
.quick-entry h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.features .el-card {
  text-align: center;
  padding: 20px 0;
}

.features h3 {
  margin: 15px 0 10px;
  color: #333;
}

.features p {
  color: #666;
  font-size: 14px;
}

.quick-entry {
  margin-bottom: 40px;
}

.entry-card {
  text-align: center;
  padding: 30px 0;
  cursor: pointer;
  transition: transform 0.3s;
}

.entry-card:hover {
  transform: translateY(-5px);
}

.entry-card .el-icon {
  color: #409eff;
  margin-bottom: 15px;
}

.entry-card h3 {
  color: #333;
  margin: 0;
}
</style>
