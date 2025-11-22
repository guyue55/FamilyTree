<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">媒体图库</h1>
      <el-upload action="#" :auto-upload="false">
        <el-button size="small" type="primary">上传</el-button>
      </el-upload>
    </header>
    <el-card>
      <el-row :gutter="12">
        <el-col v-for="i in 8" :key="i" :span="6">
          <el-card shadow="hover" class="media-card">
            <div class="media-thumb" />
            <div class="media-meta">张三 · 2020-01-01</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.media-card { cursor: pointer; }
.media-thumb { height: 120px; background: #f3f4f6; border-radius: 8px; }
.media-meta { margin-top: 8px; color: var(--el-text-color-secondary); font-size: 12px; }
</style>


