import { createRouter, createWebHistory } from 'vue-router'
import { getToken, isAdmin } from '@/utils/auth'
import { ElMessage } from 'element-plus'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', requiresAuth: false }
  },
  {
    path: '/recognize',
    name: 'Recognize',
    component: () => import('@/views/Recognize.vue'),
    meta: { title: '鸟类识别', requiresAuth: true }
  },
  {
    path: '/result',
    name: 'Result',
    component: () => import('@/views/Result.vue'),
    meta: { title: '识别结果', requiresAuth: true }
  },
  {
    path: '/birds',
    name: 'BirdList',
    component: () => import('@/views/BirdList.vue'),
    meta: { title: '鸟类百科', requiresAuth: false }
  },
  {
    path: '/birds/:id',
    name: 'BirdDetail',
    component: () => import('@/views/BirdDetail.vue'),
    meta: { title: '鸟类详情', requiresAuth: false }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { title: '识别历史', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManage',
    component: () => import('@/views/admin/UserManage.vue'),
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/birds',
    name: 'BirdManage',
    component: () => import('@/views/admin/BirdManage.vue'),
    meta: { title: '鸟类管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/dataset',
    name: 'DatasetManage',
    component: () => import('@/views/admin/DatasetManage.vue'),
    meta: { title: '数据集与训练', requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 鸟类识别系统` : '鸟类识别系统'
  
  const token = getToken()
  
  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!token) {
      ElMessage.warning('请先登录')
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    
    // 需要管理员权限
    if (to.meta.requiresAdmin && !isAdmin()) {
      ElMessage.error('没有权限访问')
      next('/home')
      return
    }
  }
  
  // 已登录用户访问登录/注册页面，跳转到首页
  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/home')
    return
  }
  
  next()
})

export default router
