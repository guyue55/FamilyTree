<template>
  <div class="search-page">
    <div class="search-header">
      <h1>搜索</h1>
      <el-input
        v-model="searchKeyword"
        placeholder="请输入搜索关键词"
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <div v-if="searchResults.length > 0" class="search-results">
      <h2>搜索结果</h2>
      <div class="results-list">
        <div v-for="result in searchResults" :key="result.id" class="result-item">
          <h3>{{ result.name }}</h3>
          <p>{{ result.description }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="hasSearched" class="no-results">
      <p>未找到相关结果</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const searchKeyword = ref('')
const searchResults = ref<any[]>([])
const hasSearched = ref(false)

function handleSearch() {
  if (!searchKeyword.value.trim()) return

  hasSearched.value = true
  // TODO: 实现搜索逻辑
  searchResults.value = []
}
</script>

<style scoped>
.search-page {
  padding: 20px;
}

.search-header {
  margin-bottom: 30px;
}

.search-header h1 {
  margin-bottom: 20px;
  color: #303133;
}

.search-input {
  max-width: 600px;
}

.search-results h2 {
  margin-bottom: 20px;
  color: #303133;
}

.results-list {
  display: grid;
  gap: 20px;
}

.result-item {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-item h3 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.result-item p {
  margin: 0;
  color: #606266;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>
