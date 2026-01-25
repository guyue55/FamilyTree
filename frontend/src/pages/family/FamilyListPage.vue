<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">家族列表</h1>
      <el-button type="primary" size="small" @click="createFamily">新建家族</el-button>
    </header>
    <el-card class="page-card">
      <el-input v-model="query" placeholder="搜索家族名称" clearable size="small" class="mb-3" />
      <el-row :gutter="16">
        <el-col v-for="family in filtered" :key="family.id" :span="6">
          <el-card shadow="hover" class="family-card" @click="goFamily(family.id)">
            <div class="family-card__title">{{ family.name }}</div>
            <div class="family-card__meta">成员：{{ family.memberCount }} · 世代：{{ family.generationCount }}</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
  </template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

interface FamilyLite {
  id: number
  name: string
  memberCount: number
  generationCount: number
}

const router = useRouter()
const query = ref('')
const loading = ref(false)
const error = ref('')
const families = ref<FamilyLite[]>([])

const fetchFamilies = async () => {
  loading.value = true
  error.value = ''
  try {
    const { listPublicFamilies } = await import('@/api/family')
    const { items } = await listPublicFamilies({ page: 1, page_size: 20, search: query.value })
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    families.value = items.map((f: any) => ({
      id: Number(f.id),
      name: String(f.name),
      memberCount: Number(f.member_count || 0),
      generationCount: Number(f.generation_count || 1)
    }))
  } catch {
    error.value = '加载家族列表失败'
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return families.value
  return families.value.filter(f => f.name.toLowerCase().includes(q))
})

const goFamily = (id: number) => {
  router.push({ name: 'FamilyTree', params: { id } })
}

const createFamily = () => {
  // TODO: 打开创建弹窗
}

fetchFamilies()
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.page-card { }
.mb-3 { margin-bottom: 12px; }
.family-card { cursor: pointer; }
.family-card__title { font-weight: 600; margin-bottom: 6px; }
.family-card__meta { color: var(--el-text-color-secondary); font-size: 12px; }
</style>


