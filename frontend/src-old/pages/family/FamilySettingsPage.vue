<template>
  <div class="family-settings-page">
    <div class="page-header">
      <h1>族谱设置</h1>
      <p>管理族谱的各项设置</p>
    </div>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <h3>基本设置</h3>
        </template>
        <el-form :model="familySettings" label-width="120px">
          <el-form-item label="族谱名称">
            <el-input v-model="familySettings.name" />
          </el-form-item>
          <el-form-item label="族谱描述">
            <el-input v-model="familySettings.description" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="可见性">
            <el-select v-model="familySettings.visibility">
              <el-option label="公开" value="public" />
              <el-option label="家族内部" value="family" />
              <el-option label="私密" value="private" />
            </el-select>
          </el-form-item>
          <el-form-item label="允许加入">
            <el-switch v-model="familySettings.allowJoin" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <h3>权限设置</h3>
        </template>
        <el-form label-width="120px">
          <el-form-item label="成员邀请">
            <el-switch v-model="familySettings.permissions.memberInvite" />
          </el-form-item>
          <el-form-item label="内容编辑">
            <el-switch v-model="familySettings.permissions.contentEdit" />
          </el-form-item>
          <el-form-item label="媒体上传">
            <el-switch v-model="familySettings.permissions.mediaUpload" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <h3>显示设置</h3>
        </template>
        <el-form label-width="120px">
          <el-form-item label="树形布局">
            <el-select v-model="familySettings.treeLayout">
              <el-option label="水平布局" value="horizontal" />
              <el-option label="垂直布局" value="vertical" />
              <el-option label="径向布局" value="radial" />
            </el-select>
          </el-form-item>
          <el-form-item label="显示照片">
            <el-switch v-model="familySettings.display.showPhotos" />
          </el-form-item>
          <el-form-item label="显示生日">
            <el-switch v-model="familySettings.display.showBirthDates" />
          </el-form-item>
        </el-form>
      </el-card>

      <div class="settings-actions">
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
        <el-button @click="resetSettings">重置</el-button>
        <el-button type="danger" @click="deleteFamily">删除族谱</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const familySettings = ref({
  name: '示例族谱',
  description: '这是一个示例族谱',
  visibility: 'public',
  allowJoin: true,
  permissions: {
    memberInvite: true,
    contentEdit: false,
    mediaUpload: true
  },
  treeLayout: 'horizontal',
  display: {
    showPhotos: true,
    showBirthDates: true
  }
})

function saveSettings() {
  // TODO: 实现设置保存逻辑
  ElMessage.success('设置保存成功')
}

function resetSettings() {
  // TODO: 重置设置逻辑
  ElMessage.info('设置已重置')
}

async function deleteFamily() {
  try {
    await ElMessageBox.confirm('确定要删除这个族谱吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // TODO: 实现删除族谱逻辑
    ElMessage.success('族谱删除成功')
  } catch {
    ElMessage.info('已取消删除')
  }
}
</script>

<style scoped>
.family-settings-page {
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

.settings-actions .el-button {
  margin-right: 10px;
}
</style>
