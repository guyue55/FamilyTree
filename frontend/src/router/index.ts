import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/families'
  },
  {
    path: '/families',
    name: 'FamilyList',
    component: () => import('@/pages/family/FamilyListPage.vue'),
    meta: { title: '家族列表' }
  },
  {
    path: '/family/:id/tree',
    name: 'FamilyTree',
    component: () => import('@/pages/family/FamilyTreePage.vue'),
    meta: {
      title: '族谱图'
    }
  },
  {
    path: '/members/:id',
    name: 'MemberDetail',
    component: () => import('@/pages/members/MemberDetailPage.vue'),
    meta: { title: '成员详情' }
  },
  {
    path: '/members/:id/edit',
    name: 'MemberEdit',
    component: () => import('@/pages/members/MemberEditPage.vue'),
    meta: { title: '编辑成员' }
  },
  {
    path: '/family/:id/relations',
    name: 'Relations',
    component: () => import('@/pages/relations/RelationsPage.vue'),
    meta: { title: '关系管理' }
  },
  {
    path: '/family/:id/media',
    name: 'MediaGallery',
    component: () => import('@/pages/media/MediaGalleryPage.vue'),
    meta: { title: '媒体图库' }
  },
  {
    path: '/search',
    name: 'SearchQuery',
    component: () => import('@/pages/search/SearchQueryPage.vue'),
    meta: { title: '搜索与称呼查询' }
  },
  {
    path: '/tools/import-export',
    name: 'ImportExport',
    component: () => import('@/pages/tools/ImportExportPage.vue'),
    meta: { title: '导入与导出' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/settings/SettingsPage.vue'),
    meta: { title: '设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router