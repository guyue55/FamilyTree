<template>
  <el-dialog
    v-model="visible"
    title="分享家族"
    width="500px"
    :before-close="handleClose"
  >
    <div class="share-content">
      <div class="share-section">
        <h3>分享链接</h3>
        <div class="link-box">
          <el-input v-model="shareUrl" readonly>
            <template #append>
              <el-button @click="copyLink">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        <p class="share-hint">将此链接发送给家人，邀请他们查看族谱。</p>
      </div>

      <div class="share-section">
        <h3>导出图片</h3>
        <p class="share-hint">将族谱导出为图片，保存或打印。</p>
        <div class="export-buttons">
          <el-button @click="$emit('export', 'png')">
            导出 PNG
          </el-button>
          <el-button @click="$emit('export', 'pdf')">
            导出 PDF
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'export': [format: string]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const shareUrl = ref(window.location.href)

const handleClose = () => {
  visible.value = false
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('链接已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const handleExport = (format: string) => {
  emit('export', format)
}
</script>

<style scoped>
.share-section {
  margin-bottom: 24px;
}

.share-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1f2937;
}

.share-hint {
  font-size: 14px;
  color: #6b7280;
  margin-top: 8px;
}

.export-buttons {
  display: flex;
  gap: 12px;
}
</style>
