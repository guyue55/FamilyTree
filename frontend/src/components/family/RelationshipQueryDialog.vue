<template>
  <el-dialog
    v-model="visible"
    title="称呼查询"
    width="600px"
    :before-close="handleClose"
  >
    <div class="query-content">
      <div class="member-selectors">
        <div class="selector-group">
          <label>成员 A (称呼者)</label>
          <el-select
            v-model="personAId"
            filterable
            placeholder="选择成员"
            style="width: 100%"
          >
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </div>
        
        <div class="exchange-btn">
          <el-button circle @click="exchangeMembers">
            <el-icon><Switch /></el-icon>
          </el-button>
        </div>

        <div class="selector-group">
          <label>成员 B (被称呼者)</label>
          <el-select
            v-model="personBId"
            filterable
            placeholder="选择成员"
            style="width: 100%"
          >
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </div>
      </div>

      <div class="result-area" v-if="result">
        <div class="result-card">
          <div class="result-title">
            {{ getMemberName(personAId) }} 称呼 {{ getMemberName(personBId) }} 为：
          </div>
          <div class="result-value">{{ result.title }}</div>
          <div class="result-path" v-if="result.path">
            关系路径：{{ result.path }}
          </div>
        </div>
        
        <div class="result-card reverse">
          <div class="result-title">
            {{ getMemberName(personBId) }} 称呼 {{ getMemberName(personAId) }} 为：
          </div>
          <div class="result-value">{{ result.reverseTitle }}</div>
        </div>
      </div>
      
      <div class="empty-state" v-else-if="personAId && personBId">
        <el-empty description="无法计算关系或无直接血缘关系" />
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="calculate" :disabled="!canCalculate">计算</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Switch } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FamilyMember } from '@/types/family'
import { kinshipApi } from '@/api/kinship'

const props = defineProps<{
  modelValue: boolean
  members: FamilyMember[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const personAId = ref('')
const personBId = ref('')
const result = ref<{ title: string; reverseTitle: string; path: string } | null>(null)
const loading = ref(false)

const canCalculate = computed(() => personAId.value && personBId.value && personAId.value !== personBId.value)

const handleClose = () => {
  visible.value = false
  // Reset on close? Maybe better to keep state
}

const getMemberName = (id: string) => {
  return props.members.find(m => m.id === id)?.name || '未知'
}

const exchangeMembers = () => {
  const temp = personAId.value
  personAId.value = personBId.value
  personBId.value = temp
  if (result.value) {
    calculate()
  }
}

const calculate = async () => {
  if (!canCalculate.value) return
  
  const memberA = props.members.find(m => m.id === personAId.value)
  if (!memberA) return

  loading.value = true
  result.value = null
  
  try {
    const response = await kinshipApi.calculate({
      family_tree_id: memberA.familyId,
      from_member_id: personAId.value,
      to_member_id: personBId.value
    })
    
    const data = response.data
    
    // Format path description
    let pathDesc = data.relationship_path
    if (data.path_details && data.path_details.length > 0) {
       // Convert path details to readable string if needed, 
       // but relationship_path from backend might be technical like "parent,parent"
       // Let's rely on the backend response or format it better if we had a mapping.
       // For now, let's display the raw path or a simple count.
       pathDesc = `${data.relationship_path} (${data.generation_diff > 0 ? '长辈' : (data.generation_diff < 0 ? '晚辈' : '同辈')})`
    }

    result.value = {
      title: data.title,
      reverseTitle: data.reverse_title,
      path: pathDesc
    }
  } catch (error) {
    console.error('Kinship calculation failed:', error)
    // If 404, it means no relationship found
    // @ts-ignore
    if (error.response && error.response.status === 404) {
      ElMessage.warning('无法计算这两个成员之间的关系（无路径连接）')
    } else {
      ElMessage.error('计算关系失败')
    }
  } finally {
    loading.value = false
  }
}

watch([personAId, personBId], () => {
  result.value = null
})
</script>

<style scoped>
.member-selectors {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 32px;
}

.selector-group {
  flex: 1;
}

.selector-group label {
  display: block;
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.exchange-btn {
  padding-bottom: 4px;
}

.result-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  background: #f3f4f6;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.result-card.reverse {
  border-left-color: #10b981;
}

.result-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.result-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.result-path {
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
  font-family: monospace;
}
</style>
