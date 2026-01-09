import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  // 主应用布局（顶部导航栏）
  {
    path: '/',
    component: () => import('@/views/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Software/List.vue')
      },
      {
        path: 'software',
        name: 'SoftwareList',
        component: () => import('@/views/Software/List.vue')
      },
      {
        path: 'software/:id',
        name: 'SoftwareDetail',
        component: () => import('@/views/Software/Detail.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue')
      },
      {
        path: 'requests',
        name: 'Requests',
        component: () => import('@/views/Requests.vue')
      },
      {
        path: 'my-downloads',
        name: 'MyDownloads',
        component: () => import('@/views/MyDownloads.vue')
      }
    ]
  },
  // 管理后台布局（左侧边栏）
  {
    path: '/admin',
    component: () => import('@/views/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/Admin/Dashboard.vue')
      },
      {
        path: 'requests',
        name: 'AdminRequests',
        component: () => import('@/views/Admin/Requests.vue')
      },
      {
        path: 'vulnerabilities',
        name: 'AdminVulnerabilities',
        component: () => import('@/views/Admin/Vulnerabilities.vue')
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/Admin/Categories.vue')
      },
      {
        path: 'config',
        name: 'AdminConfig',
        component: () => import('@/views/Admin/Config.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/Admin/Users.vue'),
        meta: { requiresSuperAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else if (to.meta.requiresAdmin && !userStore.isOps()) {
    next('/')
  } else if (to.meta.requiresSuperAdmin && !userStore.isAdmin()) {
    next('/admin')
  } else if (to.path === '/login' && userStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
