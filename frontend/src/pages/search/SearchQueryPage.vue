<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">搜索与称呼查询</h1>
    </header>
    <el-card>
      <el-input v-model="query" placeholder="输入姓名或关键字" clearable class="mb-3" />
      <el-row :gutter="12">
        <el-col :span="12">
          <el-card shadow="never" class="p-2">
            <div class="section-title">搜索结果</div>
            <el-empty v-if="!results.length" description="暂无结果" />
            <el-list v-else>
              <el-list-item v-for="r in results" :key="r.id">{{ r.name }} · 第{{ r.generation }}代</el-list-item>
            </el-list>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="p-2">
            <div class="section-title">称呼查询</div>
            <div class="row">
              <el-input v-model="from" placeholder="我（姓名）" class="mr-2" />
              <el-input v-model="to" placeholder="对方（姓名）" class="mr-2" />
              <el-button type="primary" @click="calc">计算</el-button>
            </div>
            <div class="mt-2">称呼：<b>{{ title || '-' }}</b></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const query = ref('')
const results = ref<any[]>([])
const from = ref('我')
const to = ref('他')
const title = ref('')

const calc = () => {
  // TODO: 调用称呼计算逻辑
  title.value = '堂兄'
}
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.mb-3 { margin-bottom: 12px; }
.p-2 { padding: 8px; }
.row { display: flex; align-items: center; }
.mr-2 { margin-right: 8px; }
.mt-2 { margin-top: 8px; }
.section-title { font-weight: 600; margin-bottom: 8px; }
</style>


