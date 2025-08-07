<template>
  <div class="user-settings-page">
    <div class="page-header">
      <h1>账户设置</h1>
      <p>管理您的账户偏好设置</p>
    </div>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <h3>通知设置</h3>
        </template>
        <el-form label-width="150px">
          <el-form-item label="邮件通知">
            <el-switch v-model="settings.emailNotification" />
          </el-form-item>
          <el-form-item label="短信通知">
            <el-switch v-model="settings.smsNotification" />
          </el-form-item>
          <el-form-item label="系统通知">
            <el-switch v-model="settings.systemNotification" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <h3>隐私设置</h3>
        </template>
        <el-form label-width="150px">
          <el-form-item label="个人资料可见性">
            <el-select v-model="settings.profileVisibility">
              <el-option label="公开" value="public" />
              <el-option label="仅好友" value="friends" />
              <el-option label="私密" value="private" />
            </el-select>
          </el-form-item>
          <el-form-item label="允许搜索">
            <el-switch v-model="settings.allowSearch" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <h3>语言和地区</h3>
        </template>
        <el-form label-width="150px">
          <el-form-item label="语言">
            <el-select v-model="settings.language">
              <el-option label="中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
          <el-form-item label="时区">
            <el-select v-model="settings.timezone">
              <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
              <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>

      <div class="settings-actions">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetSettings">重置</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const settings = ref({
  emailNotification: true,
  smsNotification: false,
  systemNotification: true,
  profileVisibility: 'public',
  allowSearch: true,
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

function saveSettings() {
  // TODO: 实现设置保存逻辑
  ElMessage.success('设置保存成功')
}

function resetSettings() {
  // TODO: 重置设置逻辑
  ElMessage.info('设置已重置')
}
</script>

<style scoped>
.user-settings-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin-bottom: 10px;
  color: #303133;
}

.page-header p {
  color: #606266;
}

.settings-content {
  max-width: 600px;
}

.settings-card {
  margin-bottom: 20px;
}

.settings-card h3 {
  margin: 0;
  color: #409eff;
}

.settings-actions {
  margin-top: 30px;
}
</style>
