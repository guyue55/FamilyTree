<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">导入与导出</h1>
    </header>
    <el-card>
      <div class="section">
        <div class="section-title">导入</div>
        <el-upload action="#" :auto-upload="false">
          <el-button type="primary" size="small">选择文件</el-button>
        </el-upload>
      </div>
      <div class="section">
        <div class="section-title">导出</div>
        <el-button size="small">导出 JSON</el-button>
        <el-button size="small">导出 GEDCOM</el-button>
        <el-button size="small">导出 PNG</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.section { margin-bottom: 16px; }
.section-title { font-weight: 600; margin-bottom: 8px; }
</style>


