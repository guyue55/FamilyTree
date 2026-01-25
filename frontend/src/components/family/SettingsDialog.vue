<template>
  <el-dialog
    v-model="visible"
    title="族谱设置"
    width="500px"
    :before-close="handleClose"
  >
    <div class="settings-content">
      <div class="setting-item">
        <div class="setting-info">
          <h3>重置视图</h3>
          <p>恢复默认的缩放级别和位置。</p>
        </div>
        <el-button @click="$emit('reset-view')">重置</el-button>
      </div>

      <el-divider />

      <div class="setting-item">
        <div class="setting-info">
          <h3>清除缓存</h3>
          <p>清除此家族的本地显示配置（如显示/隐藏选项）。</p>
        </div>
        <el-button type="warning" @click="handleClearCache">清除</el-button>
      </div>

      <el-divider />

      <div class="setting-item">
        <div class="setting-info">
          <h3>关于</h3>
          <p>FamilyTree v1.0.0</p>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'reset-view': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const handleClose = () => {
  visible.value = false
}

const handleClearCache = () => {
  localStorage.removeItem('family-tree-preferences')
  ElMessage.success('缓存已清除，刷新页面后生效')
}
</script>

<style scoped>
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.setting-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1f2937;
}

.setting-info p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}
</style>
