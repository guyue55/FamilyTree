<template>
  <div class="page page-wrap">
    <header class="page-header">
      <el-button size="small" @click="$router.back()">返回</el-button>
      <h1 class="page-title">成员详情</h1>
      <el-button type="primary" size="small" @click="edit">编辑</el-button>
    </header>
    <el-card>
      <div class="info-row"><span class="label">姓名</span><span>{{ member.name }}</span></div>
      <div class="info-row"><span class="label">性别</span><span>{{ member.gender === 'male' ? '男' : '女' }}</span></div>
      <div class="info-row"><span class="label">世代</span><span>{{ member.generation }}</span></div>
      <div class="info-row"><span class="label">生日</span><span>{{ member.birthDate || '-' }}</span></div>
      <div class="info-row"><span class="label">逝世</span><span>{{ member.deathDate || '-' }}</span></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const member = ref({
  id: String(route.params.id || '1'),
  name: '张三',
  gender: 'male',
  generation: 2,
  birthDate: '1990-01-01',
  deathDate: ''
})

const edit = () => {
  router.push({ name: 'MemberEdit', params: { id: member.value.id } })
}
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; margin-left: auto; margin-right: auto; }
.info-row { display: flex; gap: 12px; padding: 8px 0; }
.label { width: 80px; color: var(--el-text-color-secondary); }
</style>


