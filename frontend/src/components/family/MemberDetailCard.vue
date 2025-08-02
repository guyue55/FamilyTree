/** * 成员详情卡片组件 * 用于展示族谱成员的详细信息 * * @author 古月 * @version 1.0.0 */

<template>
  <div class="member-detail-card">
    <!-- 基本信息 -->
    <div class="member-header">
      <div class="member-avatar-section">
        <el-avatar :src="member.avatar" :size="80" class="member-avatar">
          {{ member.name.charAt(0) }}
        </el-avatar>

        <el-button
          v-if="!readonly && canEdit"
          type="primary"
          size="small"
          circle
          class="avatar-edit-btn"
          @click="handleAvatarEdit"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
      </div>

      <div class="member-basic-info">
        <h3 class="member-name">{{ member.name }}</h3>
        <div class="member-meta">
          <el-tag :type="getGenderTagType(member.gender)" size="small">
            {{ getGenderText(member.gender) }}
          </el-tag>

          <el-tag v-if="member.generation" type="info" size="small">
            第{{ member.generation }}世
          </el-tag>

          <el-tag
            v-if="member.is_alive !== undefined"
            :type="member.is_alive ? 'success' : 'danger'"
            size="small"
          >
            {{ member.is_alive ? '在世' : '已故' }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 详细信息 -->
    <el-divider />

    <div class="member-details">
      <el-descriptions :column="2" size="default" border>
        <!-- 基本信息 -->
        <el-descriptions-item label="姓名">
          <template v-if="!readonly && editMode">
            <el-input v-model="editForm.name" size="small" placeholder="请输入姓名" />
          </template>
          <template v-else>
            {{ member.name }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="性别">
          <template v-if="!readonly && editMode">
            <el-select v-model="editForm.gender" size="small" placeholder="请选择性别">
              <el-option
                v-for="option in genderOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </template>
          <template v-else>
            {{ getGenderText(member.gender) }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="出生日期">
          <template v-if="!readonly && editMode">
            <el-date-picker
              v-model="editForm.birth_date"
              type="date"
              size="small"
              placeholder="请选择出生日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </template>
          <template v-else>
            {{ member.birth_date ? formatDate(member.birth_date) : '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item v-if="!member.is_alive" label="逝世日期">
          <template v-if="!readonly && editMode">
            <el-date-picker
              v-model="editForm.death_date"
              type="date"
              size="small"
              placeholder="请选择逝世日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </template>
          <template v-else>
            {{ member.death_date ? formatDate(member.death_date) : '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="出生地">
          <template v-if="!readonly && editMode">
            <el-input v-model="editForm.birth_place" size="small" placeholder="请输入出生地" />
          </template>
          <template v-else>
            {{ member.birth_place || '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="现居地">
          <template v-if="!readonly && editMode">
            <el-input v-model="addressString" size="small" placeholder="请输入现居地" />
          </template>
          <template v-else>
            {{ formatAddress(member.contact?.address) || '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="职业">
          <template v-if="!readonly && editMode">
            <el-input v-model="editForm.occupation" size="small" placeholder="请输入职业" />
          </template>
          <template v-else>
            {{ member.occupation || '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="教育程度">
          <template v-if="!readonly && editMode">
            <el-select
              v-model="editForm.education"
              size="small"
              placeholder="请选择教育程度"
              clearable
            >
              <el-option
                v-for="option in educationOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </template>
          <template v-else>
            {{ member.education || '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="联系电话">
          <template v-if="!readonly && editMode">
            <el-input v-model="editForm.contact!.phone" size="small" placeholder="请输入联系电话" />
          </template>
          <template v-else>
            {{ member.contact?.phone || '-' }}
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="电子邮箱">
          <template v-if="!readonly && editMode">
            <el-input v-model="editForm.contact!.email" size="small" placeholder="请输入电子邮箱" />
          </template>
          <template v-else>
            {{ member.contact?.email || '-' }}
          </template>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 个人简介 -->
      <div v-if="member.bio || (!readonly && editMode)" class="member-bio">
        <h4>个人简介</h4>
        <template v-if="!readonly && editMode">
          <el-input
            v-model="editForm.bio"
            type="textarea"
            :rows="4"
            placeholder="请输入个人简介"
            maxlength="500"
            show-word-limit
          />
        </template>
        <template v-else>
          <p class="bio-content">{{ member.bio || '暂无简介' }}</p>
        </template>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="!readonly && canEdit" class="member-actions">
      <template v-if="editMode">
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
      </template>
      <template v-else>
        <el-button type="primary" @click="startEdit">编辑信息</el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, withDefaults, defineProps, defineEmits } from 'vue'
import {
  ElAvatar,
  ElButton,
  ElTag,
  ElDivider,
  ElDescriptions,
  ElDescriptionsItem,
  ElInput,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElMessage,
  ElIcon
} from 'element-plus'
import { Edit } from '@element-plus/icons-vue'

import { useFamilyStore } from '@/stores/family'
import { useUserStore } from '@/stores/user'
import { familyMemberApi } from '@/api/family'
import { UserRole } from '@/enums'
import { formatDate } from '@/utils/date'
import type { FamilyMember } from '@/types/family'
import { Gender } from '@/types/family'
import type { Address } from '@/types'

/**
 * 组件属性
 */
interface Props {
  member: FamilyMember
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false
})

/**
 * 组件事件
 */
interface Emits {
  (e: 'update', member: FamilyMember): void
  (e: 'avatarEdit', member: FamilyMember): void
}

const emit = defineEmits<Emits>()

// 状态管理
const familyStore = useFamilyStore()
const userStore = useUserStore()

// 响应式状态
const editMode = ref(false)
const saving = ref(false)

// 编辑表单
const editForm = reactive<Partial<FamilyMember>>({})

// 性别选项
const genderOptions = [
  { label: '男', value: Gender.MALE },
  { label: '女', value: Gender.FEMALE },
  { label: '未知', value: Gender.UNKNOWN }
]

// 教育程度选项
const educationOptions = [
  { label: '小学', value: '小学' },
  { label: '初中', value: '初中' },
  { label: '高中', value: '高中' },
  { label: '中专', value: '中专' },
  { label: '大专', value: '大专' },
  { label: '本科', value: '本科' },
  { label: '硕士', value: '硕士' },
  { label: '博士', value: '博士' },
  { label: '其他', value: '其他' }
]

// 计算属性
const canEdit = computed(() => {
  // 暂时允许所有已认证用户编辑，后续可以根据实际需求调整权限逻辑
  return userStore.isAuthenticated
})

// 地址字符串计算属性
const addressString = computed({
  get: () => {
    const address = editForm.contact?.address
    if (!address) return ''
    return formatAddress(address)
  },
  set: (value: string) => {
    if (!editForm.contact) {
      editForm.contact = {}
    }
    // 简单处理：将字符串存储为detail字段
    editForm.contact.address = { detail: value }
  }
})

/**
 * 格式化地址对象为字符串
 */
const formatAddress = (address?: Address): string => {
  if (!address) return ''
  
  const parts = [
    address.province,
    address.city,
    address.district,
    address.street,
    address.detail
  ].filter(Boolean)
  
  return parts.join(' ')
}

/**
 * 获取性别标签类型
 */
const getGenderTagType = (gender: Gender): 'primary' | 'success' | 'info' | 'warning' | 'danger' => {
  switch (gender) {
    case Gender.MALE:
      return 'primary'
    case Gender.FEMALE:
      return 'danger'
    default:
      return 'info'
  }
}

/**
 * 获取性别文本
 */
const getGenderText = (gender: Gender) => {
  switch (gender) {
    case Gender.MALE:
      return '男'
    case Gender.FEMALE:
      return '女'
    default:
      return '未知'
  }
}

/**
 * 开始编辑
 */
const startEdit = () => {
  // 复制成员数据到编辑表单
  Object.assign(editForm, { 
    ...props.member,
    contact: props.member.contact ? { ...props.member.contact } : {} // 确保contact对象被正确复制，如果不存在则创建空对象
  })
  editMode.value = true
}

/**
 * 取消编辑
 */
const cancelEdit = () => {
  editMode.value = false
  // 清空编辑表单
  Object.keys(editForm).forEach(key => {
    delete editForm[key as keyof typeof editForm]
  })
}

/**
 * 保存编辑
 */
const saveEdit = async () => {
  try {
    saving.value = true

    // 验证必填字段
    if (!editForm.name?.trim()) {
      ElMessage.error('姓名不能为空')
      return
    }

    // 更新成员信息
    const updatedMember = await familyMemberApi.updateMember(
      String(props.member.family_id),
      String(props.member.id),
      editForm as Partial<FamilyMember>
    )

    if (updatedMember) {
      ElMessage.success('更新成功')
      // 更新本地状态
      familyStore.updateFamilyMember(String(props.member.id), updatedMember.data)
      emit('update', updatedMember.data)
      editMode.value = false
    }
  } catch (error) {
    console.error('更新成员信息失败:', error)
    ElMessage.error('更新失败，请重试')
  } finally {
    saving.value = false
  }
}

/**
 * 处理头像编辑
 */
const handleAvatarEdit = () => {
  emit('avatarEdit', props.member)
}

// 监听成员变化，重置编辑状态
watch(
  () => props.member,
  () => {
    if (editMode.value) {
      cancelEdit()
    }
  }
)
</script>

<style scoped lang="scss">
.member-detail-card {
  padding: 20px;
}

.member-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 20px;
}

.member-avatar-section {
  position: relative;
  flex-shrink: 0;
}

.member-avatar {
  border: 3px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-edit-btn {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.member-basic-info {
  flex: 1;
}

.member-name {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.member-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.member-details {
  margin-bottom: 20px;
}

.member-bio {
  margin-top: 20px;

  h4 {
    margin: 0 0 12px 0;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
  }
}

.bio-content {
  margin: 0;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.member-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

// 响应式设计
@media (max-width: 768px) {
  .member-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .member-basic-info {
    width: 100%;
  }

  .member-meta {
    justify-content: center;
  }

  :deep(.el-descriptions) {
    .el-descriptions__body {
      .el-descriptions__table {
        .el-descriptions__cell {
          padding: 8px 12px;
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .member-detail-card {
    padding: 16px;
  }

  .member-name {
    font-size: 20px;
  }

  .member-actions {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }

  :deep(.el-descriptions) {
    .el-descriptions__body {
      .el-descriptions__table {
        .el-descriptions__row {
          display: block;

          .el-descriptions__cell {
            display: block;
            width: 100% !important;
            border-right: none !important;

            &.el-descriptions__label {
              background: #fafafa;
              font-weight: 500;
            }
          }
        }
      }
    }
  }
}
</style>
