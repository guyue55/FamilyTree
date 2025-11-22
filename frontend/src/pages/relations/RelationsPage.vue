<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">关系管理</h1>
    </header>
    <el-card>
      <el-table :data="rows" size="small" style="width: 100%">
        <el-table-column prop="child" label="子女" width="160" />
        <el-table-column prop="parent" label="父母" width="160" />
        <el-table-column prop="spouse" label="配偶" width="160" />
        <el-table-column label="操作" width="160">
          <template #default>
            <el-button link type="primary" size="small">编辑</el-button>
            <el-button link type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const rows = ref([
  { child: '张三', parent: '张大', spouse: '李四' },
  { child: '王五', parent: '王大', spouse: '赵六' }
])
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
</style>


