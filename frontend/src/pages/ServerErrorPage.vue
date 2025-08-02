<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-code">500</div>
      <div class="error-title">服务器错误</div>
      <div class="error-description">
        抱歉，服务器出现了一些问题，请稍后再试。
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="refresh">刷新页面</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function goHome() {
  router.push('/dashboard');
}

function refresh() {
  window.location.reload();
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
  color: #e6a23c;
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