<template>
  <el-header class="navbar">
    <div class="navbar-left">
      <router-link to="/home" class="logo">
        <el-icon><Sunrise /></el-icon>
        <span>鸟类识别系统</span>
      </router-link>
    </div>
    
    <el-menu
      mode="horizontal"
      :default-active="activeMenu"
      :ellipsis="false"
      router
      class="navbar-menu"
    >
      <el-menu-item index="/home">首页</el-menu-item>
      <el-menu-item index="/recognize" v-if="userStore.isLoggedIn">识别</el-menu-item>
      <el-menu-item index="/birds">鸟类百科</el-menu-item>
      <el-menu-item index="/history" v-if="userStore.isLoggedIn">历史记录</el-menu-item>
      <el-menu-item index="/admin" v-if="userStore.isAdmin">管理后台</el-menu-item>
    </el-menu>
    
    <div class="navbar-right">
      <template v-if="userStore.isLoggedIn">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" icon="User" />
            <span class="username">{{ userStore.userInfo.username }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button type="primary" @click="$router.push('/login')">登录</el-button>
        <el-button @click="$router.push('/register')">注册</el-button>
      </template>
    </div>
  </el-header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    // 可以跳转到个人中心页面
    ElMessage.info('个人中心功能开发中')
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 60px;
}

.navbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  text-decoration: none;
  gap: 8px;
}

.navbar-menu {
  border-bottom: none;
  flex: 1;
  justify-content: center;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #333;
}
</style>
