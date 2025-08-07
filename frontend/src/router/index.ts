import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/family/1/tree'
  },
  {
    path: '/family/:id/tree',
    name: 'FamilyTree',
    component: () => import('@/pages/family/FamilyTreePage.vue'),
    meta: {
      title: '族谱图'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router