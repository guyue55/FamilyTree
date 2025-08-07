<template>
  <div class="user-profile-page">
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的个人信息</p>
    </div>

    <div class="profile-content">
      <el-card>
        <el-form :model="profileForm" label-width="120px">
          <el-form-item label="头像">
            <el-avatar :size="80" :src="profileForm.avatar" />
            <el-button style="margin-left: 20px">更换头像</el-button>
          </el-form-item>

          <el-form-item label="用户名">
            <el-input v-model="profileForm.username" disabled />
          </el-form-item>

          <el-form-item label="昵称">
            <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
          </el-form-item>

          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="手机号">
            <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
          </el-form-item>

          <el-form-item label="个人简介">
            <el-input
              v-model="profileForm.bio"
              type="textarea"
              :rows="4"
              placeholder="请输入个人简介"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="updateProfile">保存</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const profileForm = ref({
  username: 'user123',
  nickname: '',
  email: '',
  phone: '',
  bio: '',
  avatar: ''
})

function updateProfile() {
  // TODO: 实现个人资料更新逻辑
  ElMessage.success('个人资料更新成功')
}

function resetForm() {
  // TODO: 重置表单逻辑
  ElMessage.info('表单已重置')
}
</script>

<style scoped>
.user-profile-page {
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

.profile-content {
  max-width: 600px;
}
</style>
