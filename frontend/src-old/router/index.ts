/**
 * 路由配置
 *
 * @author 古月
 * @version 1.0.0
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { userStorage } from '@/utils/storage'
import { ElMessage } from 'element-plus'

/**
 * 路由元信息接口
 */
export interface RouteMeta {
  title?: string
  requiresAuth?: boolean
  requiresGuest?: boolean
  roles?: string[]
  permissions?: string[]
  icon?: string
  hidden?: boolean
  keepAlive?: boolean
  breadcrumb?: boolean
  affix?: boolean
  noCache?: boolean
  activeMenu?: string
}

/**
 * 基础路由配置
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: {
      title: '登录',
      requiresGuest: true,
      hidden: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/auth/RegisterPage.vue'),
    meta: {
      title: '注册',
      requiresGuest: true,
      hidden: true
    }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/pages/auth/ForgotPasswordPage.vue'),
    meta: {
      title: '忘记密码',
      requiresGuest: true,
      hidden: true
    }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/pages/auth/ResetPasswordPage.vue'),
    meta: {
      title: '重置密码',
      requiresGuest: true,
      hidden: true
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '控制台',
      requiresAuth: true,
      icon: 'dashboard'
    },
    children: [
      {
        path: '',
        name: 'DashboardHome',
        component: () => import('@/pages/DashboardPage.vue'),
        meta: {
          title: '首页',
          icon: 'home',
          affix: true
        }
      }
    ]
  },
  {
    path: '/family',
    name: 'Family',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '族谱管理',
      requiresAuth: true,
      icon: 'family'
    },
    children: [
      {
        path: '',
        name: 'FamilyList',
        component: () => import('@/pages/family/FamilyListPage.vue'),
        meta: {
          title: '族谱列表',
          icon: 'list'
        }
      },
      {
        path: 'create',
        name: 'FamilyCreate',
        component: () => import('@/pages/family/FamilyCreatePage.vue'),
        meta: {
          title: '创建族谱',
          icon: 'plus'
        }
      },
      {
        path: ':id',
        name: 'FamilyDetail',
        component: () => import('@/pages/family/FamilyDetailPage.vue'),
        meta: {
          title: '族谱详情',
          hidden: true,
          keepAlive: true
        }
      },
      {
        path: ':id/edit',
        name: 'FamilyEdit',
        component: () => import('@/pages/family/FamilyEditPage.vue'),
        meta: {
          title: '编辑族谱',
          hidden: true
        }
      },
      {
        path: ':id/tree',
        name: 'FamilyTree',
        component: () => import('@/pages/family/FamilyTreePage.vue'),
        meta: {
          title: '族谱树',
          hidden: true,
          keepAlive: true
        }
      },
      {
        path: ':id/members',
        name: 'FamilyMembers',
        component: () => import('@/pages/family/FamilyMembersPage.vue'),
        meta: {
          title: '成员管理',
          hidden: true
        }
      },
      {
        path: ':id/settings',
        name: 'FamilySettings',
        component: () => import('@/pages/family/FamilySettingsPage.vue'),
        meta: {
          title: '族谱设置',
          hidden: true
        }
      }
    ]
  },
  {
    path: '/user',
    name: 'User',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '个人中心',
      requiresAuth: true,
      icon: 'user'
    },
    children: [
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/pages/user/UserProfilePage.vue'),
        meta: {
          title: '个人资料',
          icon: 'profile'
        }
      },
      {
        path: 'settings',
        name: 'UserSettings',
        component: () => import('@/pages/user/UserSettingsPage.vue'),
        meta: {
          title: '账户设置',
          icon: 'settings'
        }
      },
      {
        path: 'security',
        name: 'UserSecurity',
        component: () => import('@/pages/user/UserSecurityPage.vue'),
        meta: {
          title: '安全设置',
          icon: 'security'
        }
      }
    ]
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '搜索',
      requiresAuth: true,
      icon: 'search'
    },
    children: [
      {
        path: '',
        name: 'SearchHome',
        component: () => import('@/pages/SearchPage.vue'),
        meta: {
          title: '搜索',
          icon: 'search'
        }
      }
    ]
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      title: '帮助中心',
      requiresAuth: true,
      icon: 'help'
    },
    children: [
      {
        path: '',
        name: 'HelpHome',
        component: () => import('@/pages/HelpPage.vue'),
        meta: {
          title: '帮助中心',
          icon: 'help'
        }
      }
    ]
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/pages/NotFoundPage.vue'),
    meta: {
      title: '页面不存在',
      hidden: true
    }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/pages/ForbiddenPage.vue'),
    meta: {
      title: '访问被拒绝',
      hidden: true
    }
  },
  {
    path: '/500',
    name: 'ServerError',
    component: () => import('@/pages/ServerErrorPage.vue'),
    meta: {
      title: '服务器错误',
      hidden: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

/**
 * 路由守卫
 */
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 族谱系统`
  } else {
    document.title = '族谱系统'
  }

  // 获取用户token
  const token = userStorage.getToken()
  const isAuthenticated = !!token

  // 检查是否需要认证
  if (to.meta?.requiresAuth && !isAuthenticated) {
    ElMessage.warning('请先登录')
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // 检查是否需要游客状态（已登录用户不能访问登录页等）
  if (to.meta?.requiresGuest && isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }

  // 角色权限检查（如果需要的话）
  const routeMeta = to.meta as RouteMeta
  if (routeMeta?.roles && routeMeta.roles.length > 0) {
    const userInfo = userStorage.getUserInfo()
    const userRole = userInfo?.role

    if (!userRole || !routeMeta.roles.includes(userRole)) {
      ElMessage.error('您没有权限访问此页面')
      next({ name: 'Forbidden' })
      return
    }
  }

  // 权限检查（如果需要的话）
  if (routeMeta?.permissions && routeMeta.permissions.length > 0) {
    const userInfo = userStorage.getUserInfo()
    const userPermissions = userInfo?.permissions || []

    const hasPermission = routeMeta.permissions.some((permission: string) =>
      userPermissions.includes(permission)
    )

    if (!hasPermission) {
      ElMessage.error('您没有权限访问此页面')
      next({ name: 'Forbidden' })
      return
    }
  }

  next()
})

/**
 * 路由错误处理
 */
router.onError(error => {
  console.error('路由错误:', error)
  ElMessage.error('页面加载失败，请刷新重试')
})

export default router
