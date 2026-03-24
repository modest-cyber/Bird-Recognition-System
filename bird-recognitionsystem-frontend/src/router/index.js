import { createRouter, createWebHistory } from 'vue-router'
import { getToken, isAdmin } from '@/utils/auth'
import { ElMessage } from 'element-plus'

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
    meta: { title: '立即识别', requiresAuth: true }
  },
  {
    path: '/result',
    name: 'Result',
    component: () => import('@/views/Result.vue'),
    meta: { title: '识别结果', requiresAuth: true }
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

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 鸟类识别系统` : '鸟类识别系统'

  const token = getToken()

  if (to.meta.requiresAuth) {
    if (!token) {
      ElMessage.warning('请先登录')
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }

    if (to.meta.requiresAdmin && !isAdmin()) {
      ElMessage.error('没有权限访问')
      next('/home')
      return
    }
  }

  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/home')
    return
  }

  next()
})

export default router
