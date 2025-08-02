/** * 族谱图形展示组件 * 基于G6图形库和Element Plus实现族谱的树形可视化 * * @author 古月 * @version
1.0.0 */

<template>
  <div class="family-tree-graph">
    <!-- 工具栏 -->
    <div class="graph-toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="layoutType"
          placeholder="选择布局"
          size="default"
          style="width: 140px"
          @change="handleLayoutChange"
        >
          <el-option
            v-for="layout in layoutOptions"
            :key="layout.value"
            :label="layout.label"
            :value="layout.value"
          />
        </el-select>

        <el-select
          v-model="generationRange"
          placeholder="世代范围"
          size="default"
          style="width: 120px"
          @change="handleGenerationChange"
        >
          <el-option label="全部世代" value="all" />
          <el-option label="1-3世代" value="1-3" />
          <el-option label="1-5世代" value="1-5" />
          <el-option label="1-7世代" value="1-7" />
        </el-select>

        <el-input
          v-model="searchKeyword"
          placeholder="搜索成员"
          size="default"
          style="width: 200px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="toolbar-right">
        <el-button-group>
          <el-button size="default" :icon="ZoomIn" @click="zoomIn">放大</el-button>
          <el-button size="default" :icon="ZoomOut" @click="zoomOut">缩小</el-button>
          <el-button size="default" :icon="Refresh" @click="resetZoom">重置</el-button>
        </el-button-group>

        <el-dropdown @command="handleExport">
          <el-button type="primary" size="default">
            导出图片
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="png">PNG格式</el-dropdown-item>
              <el-dropdown-item command="jpeg">JPEG格式</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 图形容器 -->
    <div
      ref="containerRef"
      v-loading="loading"
      class="graph-container"
      element-loading-text="加载中..."
      element-loading-spinner="el-icon-loading"
    />

    <!-- 成员详情弹窗 -->
    <el-dialog
      v-model="memberDialogVisible"
      :title="selectedMember?.name || '成员详情'"
      width="600px"
      :before-close="handleDialogClose"
    >
      <MemberDetailCard v-if="selectedMember" :member="selectedMember" :readonly="true" />

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="memberDialogVisible = false">关闭</el-button>
          <el-button v-if="canEditMember" type="primary" @click="handleEditMember">编辑</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 关系路径显示 -->
    <el-drawer v-model="pathDrawerVisible" title="关系路径" direction="rtl" size="400px">
      <div v-if="relationshipPath.length > 0" class="relationship-path">
        <div v-for="(step, index) in relationshipPath" :key="index" class="path-step">
          <div class="step-member">
            <el-avatar :src="step.member.avatar" :size="40" class="member-avatar">
              {{ step.member.name.charAt(0) }}
            </el-avatar>
            <span class="member-name">{{ step.member.name }}</span>
          </div>

          <div v-if="index < relationshipPath.length - 1" class="step-relation">
            <el-icon><ArrowDown /></el-icon>
            <span>{{ step.relationship }}</span>
          </div>
        </div>
      </div>

      <el-empty v-else description="请选择两个成员查看关系路径" :image-size="100" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, withDefaults, defineProps, defineEmits } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElMessage,
  ElMessageBox,
  ElSelect,
  ElOption,
  ElInput,
  ElButton,
  ElButtonGroup,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElDialog,
  ElDrawer,
  ElAvatar,
  ElEmpty,
  ElIcon
} from 'element-plus'
import { Search, ZoomIn, ZoomOut, Refresh, ArrowDown } from '@element-plus/icons-vue'

import { useFamilyTreeGraph } from '@/composables/useFamilyTreeGraph'
import { useFamilyStore } from '@/stores/family'
import { useUserStore } from '@/stores/user'
import { familyTreeApi } from '@/api/family'
import { LayoutType } from '@/enums/familyTree'
import { UserRole } from '@/enums/user'
import type { GraphData, GraphNode } from '@/types/graph'
import type { FamilyMember } from '@/types/family'
import { Gender } from '@/types/family'

/**
 * 组件属性
 */
interface Props {
  familyId: string
  height?: number
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 600,
  readonly: false
})

/**
 * 组件事件
 */
interface Emits {
  (e: 'memberSelect', member: FamilyMember): void
  (e: 'memberEdit', member: FamilyMember): void
  (e: 'relationshipCalculate', member1: FamilyMember, member2: FamilyMember): void
}

const emit = defineEmits<Emits>()

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const familyStore = useFamilyStore()
const userStore = useUserStore()

// 使用图形组合式函数
const {
  loading,
  selectedNode,
  layoutType,
  containerRef,
  loadData,
  zoomIn,
  zoomOut,
  resetZoom,
  exportImage,
  highlightPath,
  setNodeDoubleClickHandler
} = useFamilyTreeGraph({
  height: props.height,
  fitView: true,
  animate: true
})

// 响应式状态
const generationRange = ref('all')
const searchKeyword = ref('')
const memberDialogVisible = ref(false)
const pathDrawerVisible = ref(false)
const selectedMember = ref<FamilyMember | null>(null)
const relationshipPath = ref<
  Array<{
    member: FamilyMember
    relationship: string
  }>
>([])

// 布局选项
const layoutOptions = [
  { label: '树形布局', value: LayoutType.TREE },
  { label: '力导向布局', value: LayoutType.FORCE },
  { label: '环形布局', value: LayoutType.CIRCULAR },
  { label: '径向布局', value: LayoutType.RADIAL }
]

// 计算属性
const canEditMember = computed(() => {
  if (props.readonly) return false

  // 暂时允许所有已认证用户编辑，后续可以根据实际需求调整权限逻辑
  return userStore.isAuthenticated
})

/**
 * 处理布局变化
 */
const handleLayoutChange = (newLayout: LayoutType) => {
  layoutType.value = newLayout
  loadGraphData()
}

/**
 * 处理世代范围变化
 */
const handleGenerationChange = (range: string) => {
  generationRange.value = range
  loadGraphData()
}

/**
 * 处理搜索
 */
const handleSearch = (keyword: string) => {
  if (!keyword.trim()) {
    // 清除高亮
    highlightPath([])
    return
  }

  // TODO: 实现搜索功能，需要从正确的数据源搜索FamilyMember
  ElMessage.warning('搜索功能暂未实现')
}

/**
 * 处理导出
 */
const handleExport = (format: 'png' | 'jpeg') => {
  const filename = `family-tree-${props.familyId}-${Date.now()}`
  exportImage(format, filename)
}

/**
 * 处理成员详情弹窗关闭
 */
const handleDialogClose = (done: () => void) => {
  selectedMember.value = null
  done()
}

/**
 * 处理编辑成员
 */
const handleEditMember = () => {
  if (selectedMember.value) {
    emit('memberEdit', selectedMember.value)
    memberDialogVisible.value = false
  }
}

/**
 * 处理节点双击
 */
const handleNodeDoubleClick = async (node: GraphNode) => {
  try {
    // 从节点数据中构造FamilyMember对象
     if (node.data) {
       // 转换Gender枚举值
       let genderValue: Gender
       switch (node.data.gender) {
         case 1: // MALE from user enum
           genderValue = Gender.MALE
           break
         case 2: // FEMALE from user enum
           genderValue = Gender.FEMALE
           break
         default: // UNKNOWN
           genderValue = Gender.UNKNOWN
           break
       }
       
       const member: FamilyMember = {
         id: node.data.memberId,
         family_id: parseInt(props.familyId),
         name: node.data.name,
         gender: genderValue,
         birth_date: node.data.birthDate,
         death_date: node.data.deathDate,
         is_alive: node.data.isAlive,
         generation: node.data.generation,
         avatar: node.data.avatarUrl,
         occupation: node.data.occupation,
         birth_place: node.data.birthPlace,
         father_id: node.data.fatherId ? Number(node.data.fatherId) : undefined,
         mother_id: node.data.motherId ? Number(node.data.motherId) : undefined,
         spouse_ids: node.data.spouseIds?.map(id => Number(id)),
         children_ids: node.data.childrenIds?.map(id => Number(id)),
         createdAt: new Date().toISOString(),
         updatedAt: new Date().toISOString()
       }
      
      selectedMember.value = member
      memberDialogVisible.value = true
      emit('memberSelect', member)
    }
  } catch (error) {
    console.error('获取成员信息失败:', error)
    ElMessage.error('获取成员信息失败')
  }
}

/**
 * 加载图形数据
 */
const loadGraphData = async () => {
  try {
    loading.value = true

    // 获取族谱图形数据
    const response = await familyTreeApi.getFamilyTree(props.familyId, {
      max_generations: generationRange.value === 'all' ? undefined : parseInt(generationRange.value),
      include_spouses: true
    })

    if (response.data) {
       // 转换数据格式为图形数据
       const graphData: GraphData = {
         nodes: response.data.map((member: any) => ({
           id: member.id.toString(),
           label: member.name,
           type: 'member',
           data: member
         })),
         edges: [] // 需要根据关系数据构建边
       }
      
      await loadData(graphData)
    }
  } catch (error) {
    console.error('加载图形数据失败:', error)
    ElMessage.error('加载图形数据失败')
  } finally {
    loading.value = false
  }
}

/**
 * 计算两个成员的关系
 */
const calculateRelationship = async (member1Id: string, member2Id: string) => {
  try {
    const result = await familyTreeApi.calculateRelationship(
      props.familyId,
      member1Id,
      member2Id
    )

    if (result.data) {
      relationshipPath.value = result.data.path.map((member: FamilyMember, index: number) => ({
        member,
        relationship: index < result.data.path.length - 1 ? result.data.relationship : ''
      }))

      pathDrawerVisible.value = true
    }
  } catch (error) {
    console.error('计算关系失败:', error)
    ElMessage.error('计算关系失败')
  }
}

// 监听选中节点变化
watch(selectedNode, node => {
  if (node) {
    emit('memberSelect', node as any)
  }
})

// 监听族谱ID变化
watch(
  () => props.familyId,
  () => {
    loadGraphData()
  }
)

// 组件挂载时初始化
onMounted(() => {
  // 设置节点双击处理器
  setNodeDoubleClickHandler(handleNodeDoubleClick)

  // 加载图形数据
  loadGraphData()
})
</script>

<style scoped lang="scss">
.family-tree-graph {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  border-radius: 8px 8px 0 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.graph-container {
  flex: 1;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
  position: relative;
  overflow: hidden;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.relationship-path {
  padding: 20px 0;
}

.path-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.step-member {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  width: 100%;
}

.member-avatar {
  flex-shrink: 0;
}

.member-name {
  font-weight: 500;
  color: #303133;
}

.step-relation {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 8px 0;
  color: #909399;
  font-size: 14px;
}

// 响应式设计
@media (max-width: 768px) {
  .graph-toolbar {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }

  .toolbar-left {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .toolbar-left {
    flex-direction: column;
    align-items: stretch;

    .el-select,
    .el-input {
      width: 100% !important;
    }
  }

  .toolbar-right {
    flex-direction: column;
    align-items: stretch;

    .el-button-group {
      width: 100%;

      .el-button {
        flex: 1;
      }
    }
  }
}
</style>
