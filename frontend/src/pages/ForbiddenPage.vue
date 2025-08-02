<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-code">403</div>
      <div class="error-title">访问被拒绝</div>
      <div class="error-description">抱歉，您没有权限访问此页面。</div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/dashboard')
}

function goBack() {
  router.go(-1)
}
</script>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.error-content {
  text-align: center;
  padding: 2rem;
}

.error-code {
  font-size: 6rem;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 1rem;
}

.error-description {
  font-size: 1rem;
  color: #606266;
  margin-bottom: 2rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style>
