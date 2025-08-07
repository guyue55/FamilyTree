<template>
  <div class="help-page">
    <div class="help-header">
      <h1>帮助中心</h1>
      <p>欢迎使用族谱系统，这里为您提供详细的使用指南和常见问题解答。</p>
    </div>

    <div class="help-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="help-card">
            <template #header>
              <h3>快速开始</h3>
            </template>
            <ul>
              <li>创建您的第一个族谱</li>
              <li>添加家族成员</li>
              <li>建立成员关系</li>
              <li>查看族谱树</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="help-card">
            <template #header>
              <h3>功能介绍</h3>
            </template>
            <ul>
              <li>族谱管理</li>
              <li>成员管理</li>
              <li>关系管理</li>
              <li>媒体管理</li>
            </ul>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="help-card">
            <template #header>
              <h3>常见问题</h3>
            </template>
            <ul>
              <li>如何邀请家族成员？</li>
              <li>如何设置族谱权限？</li>
              <li>如何导出族谱数据？</li>
              <li>如何联系客服？</li>
            </ul>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
// 帮助页面逻辑
</script>

<style scoped>
.help-page {
  padding: 20px;
}

.help-header {
  margin-bottom: 30px;
  text-align: center;
}

.help-header h1 {
  margin-bottom: 10px;
  color: #303133;
}

.help-header p {
  color: #606266;
  font-size: 1.1rem;
}

.help-content {
  max-width: 1200px;
  margin: 0 auto;
}

.help-card {
  height: 100%;
}

.help-card h3 {
  margin: 0;
  color: #409eff;
}

.help-card ul {
  margin: 0;
  padding-left: 20px;
}

.help-card li {
  margin-bottom: 8px;
  color: #606266;
}
</style>
