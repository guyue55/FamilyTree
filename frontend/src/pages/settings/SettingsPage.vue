<template>
  <div class="page page-wrap">
    <header class="page-header">
      <h1 class="page-title">设置</h1>
    </header>
    <el-card>
      <div class="section-title">显示</div>
      <el-form label-width="120px" style="max-width: 640px">
        <el-form-item label="显示照片"><el-switch v-model="showPhotos" /></el-form-item>
        <el-form-item label="显示日期"><el-switch v-model="showDates" /></el-form-item>
        <el-form-item label="显示世代"><el-switch v-model="showGeneration" /></el-form-item>
        <el-form-item label="连线风格">
          <el-select v-model="lineStyle" style="width: 240px">
            <el-option label="品字形" value="bus" />
            <el-option label="直连" value="direct" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const showPhotos = ref(true)
const showDates = ref(true)
const showGeneration = ref(true)
const lineStyle = ref('bus')
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.section-title { font-weight: 600; margin-bottom: 8px; }
</style>


