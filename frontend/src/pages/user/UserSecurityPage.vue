<template>
  <div class="user-security-page">
    <div class="page-header">
      <h1>安全设置</h1>
      <p>管理您的账户安全设置</p>
    </div>

    <div class="security-content">
      <el-card class="security-card">
        <template #header>
          <h3>密码设置</h3>
        </template>
        <el-form :model="passwordForm" label-width="120px">
          <el-form-item label="当前密码">
            <el-input
              v-model="passwordForm.currentPassword"
              type="password"
              placeholder="请输入当前密码"
            />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              placeholder="请输入新密码"
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="updatePassword">更新密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="security-card">
        <template #header>
          <h3>两步验证</h3>
        </template>
        <p>启用两步验证可以提高账户安全性</p>
        <el-switch v-model="twoFactorEnabled" @change="toggleTwoFactor" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const twoFactorEnabled = ref(false)

function updatePassword() {
  // TODO: 实现密码更新逻辑
  ElMessage.success('密码更新成功')
}

function toggleTwoFactor(value: string | number | boolean) {
  // TODO: 实现两步验证切换逻辑
  ElMessage.success(value ? '两步验证已启用' : '两步验证已关闭')
}
</script>

<style scoped>
.user-security-page {
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

.security-content {
  max-width: 600px;
}

.security-card {
  margin-bottom: 20px;
}

.security-card h3 {
  margin: 0;
  color: #409eff;
}
</style>
