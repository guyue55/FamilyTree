# 族谱页面完整UI设计方案

## 1. 设计概述

### 1.1 页面定位
族谱页面是系统的核心功能页面，承载家族关系的可视化展示、成员管理、关系查询等核心功能。

### 1.2 设计目标
- **直观性**: 清晰展示家族关系树形结构
- **易用性**: 提供便捷的成员管理和关系建立功能  
- **信息性**: 支持多层次信息展示和查询
- **交互性**: 提供流畅的缩放、拖拽、搜索等交互体验
- **响应性**: 适配不同设备和屏幕尺寸

### 1.3 技术要求确认
- **前端框架**: Vue.js 3.4+
- **UI组件库**: Element Plus 2.4+
- **图形库**: G6 (AntV) 4.8+
- **状态管理**: Pinia 2.1+
- **构建工具**: Vite 5.0+
- **类型安全**: TypeScript

## 2. 页面架构设计

### 2.1 整体布局结构
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              顶部导航栏 (64px)                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              族谱工具栏 (60px)                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  侧边栏  │                                                                       │
│ (320px) │                        族谱图形展示区域                                  │
│         │                                                                       │
│ 族谱信息 │                                                                       │
│ 成员列表 │                                                                       │
│ 筛选器   │                                                                       │
│ 统计信息 │                                                                       │
│         │                                                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              底部状态栏 (40px)                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件层次结构
```
FamilyTreePage.vue (主页面)
├── FamilyTreeHeader.vue (页面头部)
├── FamilyTreeToolbar.vue (工具栏)
├── FamilyTreeSidebar.vue (侧边栏)
│   ├── FamilyInfoCard.vue (族谱信息卡片)
│   ├── MemberFilters.vue (成员筛选器)
│   ├── MemberList.vue (成员列表)
│   └── FamilyStats.vue (统计信息)
├── FamilyTreeGraph.vue (图形展示区域)
│   ├── GraphCanvas.vue (图形画布)
│   ├── GraphNode.vue (节点组件)
│   └── GraphEdge.vue (连线组件)
├── FamilyTreeStatusBar.vue (状态栏)
└── 弹窗组件
    ├── MemberDetailDialog.vue (成员详情弹窗)
    ├── AddMemberDialog.vue (添加成员弹窗)
    ├── EditMemberDialog.vue (编辑成员弹窗)
    └── RelationshipDrawer.vue (关系查询抽屉)
```

## 3. 详细组件设计

### 3.1 FamilyTreePage.vue (主页面)

#### 3.1.1 模板结构
```vue
<template>
  <div class="family-tree-page">
    <!-- 页面头部 -->
    <FamilyTreeHeader 
      :family="currentFamily"
      @back="handleBack"
      @share="handleShare"
      @settings="handleSettings"
    />
    
    <!-- 工具栏 -->
    <FamilyTreeToolbar
      v-model:layout="layoutType"
      v-model:generation-range="generationRange"
      v-model:search-keyword="searchKeyword"
      v-model:view-options="viewOptions"
      @zoom-in="handleZoomIn"
      @zoom-out="handleZoomOut"
      @reset-zoom="handleResetZoom"
      @toggle-fullscreen="handleToggleFullscreen"
      @export="handleExport"
      @calculate-relationship="handleCalculateRelationship"
    />
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <FamilyTreeSidebar
        v-model:visible="sidebarVisible"
        :family="currentFamily"
        :members="filteredMembers"
        :filters="memberFilters"
        @member-select="handleMemberSelect"
        @member-add="handleMemberAdd"
        @filter-change="handleFilterChange"
      />
      
      <!-- 图形展示区域 -->
      <div class="graph-area">
        <FamilyTreeGraph
          ref="graphRef"
          :family-id="familyId"
          :layout="layoutType"
          :generation-range="generationRange"
          :search-keyword="searchKeyword"
          :view-options="viewOptions"
          :selected-members="selectedMembers"
          @member-click="handleMemberClick"
          @member-double-click="handleMemberDoubleClick"
          @member-context-menu="handleMemberContextMenu"
          @relationship-create="handleRelationshipCreate"
        />
      </div>
    </div>
    
    <!-- 状态栏 -->
    <FamilyTreeStatusBar
      :total-members="totalMembers"
      :selected-count="selectedMembers.length"
      :zoom-level="zoomLevel"
      :layout-type="layoutType"
      :last-update="lastUpdateTime"
    />
    
    <!-- 弹窗组件 -->
    <MemberDetailDialog
      v-model:visible="memberDetailVisible"
      :member="selectedMember"
      @edit="handleMemberEdit"
      @delete="handleMemberDelete"
    />
    
    <AddMemberDialog
      v-model:visible="addMemberVisible"
      :parent-member="parentMember"
      @confirm="handleMemberAddConfirm"
    />
    
    <EditMemberDialog
      v-model:visible="editMemberVisible"
      :member="editingMember"
      @confirm="handleMemberEditConfirm"
    />
    
    <RelationshipDrawer
      v-model:visible="relationshipVisible"
      :base-member="baseMember"
      :target-member="targetMember"
      :relationship-result="relationshipResult"
    />
  </div>
</template>
```

#### 3.1.2 脚本逻辑
```typescript
<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'

// 组件导入
import FamilyTreeHeader from '@/components/family/FamilyTreeHeader.vue'
import FamilyTreeToolbar from '@/components/family/FamilyTreeToolbar.vue'
import FamilyTreeSidebar from '@/components/family/FamilyTreeSidebar.vue'
import FamilyTreeGraph from '@/components/family/FamilyTreeGraph.vue'
import FamilyTreeStatusBar from '@/components/family/FamilyTreeStatusBar.vue'
import MemberDetailDialog from '@/components/family/MemberDetailDialog.vue'
import AddMemberDialog from '@/components/family/AddMemberDialog.vue'
import EditMemberDialog from '@/components/family/EditMemberDialog.vue'
import RelationshipDrawer from '@/components/family/RelationshipDrawer.vue'

// 类型导入
import type { FamilyMember, Family } from '@/types/family'
import type { LayoutType, ViewOptions, MemberFilters } from '@/types/familyTree'

// Store导入
import { useFamilyStore } from '@/stores/family'
import { useUserStore } from '@/stores/user'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const familyStore = useFamilyStore()
const userStore = useUserStore()

// 响应式数据
const familyId = computed(() => route.params.id as string)
const graphRef = ref()
const sidebarVisible = ref(true)

// 族谱数据
const { currentFamily, members, loading } = storeToRefs(familyStore)

// 视图状态
const layoutType = ref<LayoutType>('tree-vertical')
const generationRange = ref('all')
const searchKeyword = ref('')
const viewOptions = ref<ViewOptions>({
  showPhotos: true,
  showDates: true,
  showGeneration: true,
  showRelationshipLines: true
})

// 筛选器
const memberFilters = ref<MemberFilters>({
  gender: [],
  generationRange: [1, 10],
  ageFilter: 'all',
  statusFilter: 'all'
})

// 选中状态
const selectedMembers = ref<FamilyMember[]>([])
const selectedMember = ref<FamilyMember | null>(null)

// 弹窗状态
const memberDetailVisible = ref(false)
const addMemberVisible = ref(false)
const editMemberVisible = ref(false)
const relationshipVisible = ref(false)

// 编辑状态
const editingMember = ref<FamilyMember | null>(null)
const parentMember = ref<FamilyMember | null>(null)

// 关系查询
const baseMember = ref<FamilyMember | null>(null)
const targetMember = ref<FamilyMember | null>(null)
const relationshipResult = ref<any>(null)

// 计算属性
const filteredMembers = computed(() => {
  return familyStore.getFilteredMembers(memberFilters.value)
})

const totalMembers = computed(() => members.value.length)

const zoomLevel = computed(() => {
  return graphRef.value?.getZoomLevel() || 1
})

const lastUpdateTime = computed(() => {
  return currentFamily.value?.updatedAt || new Date()
})

// 事件处理器
const handleBack = () => {
  router.push('/family')
}

const handleShare = () => {
  // 实现分享功能
  ElMessage.success('分享链接已复制到剪贴板')
}

const handleSettings = () => {
  // 打开族谱设置
  router.push(`/family/${familyId.value}/settings`)
}

const handleZoomIn = () => {
  graphRef.value?.zoomIn()
}

const handleZoomOut = () => {
  graphRef.value?.zoomOut()
}

const handleResetZoom = () => {
  graphRef.value?.resetZoom()
}

const handleToggleFullscreen = () => {
  graphRef.value?.toggleFullscreen()
}

const handleExport = (format: string) => {
  graphRef.value?.exportImage(format)
}

const handleCalculateRelationship = () => {
  if (selectedMembers.value.length === 2) {
    baseMember.value = selectedMembers.value[0]
    targetMember.value = selectedMembers.value[1]
    relationshipVisible.value = true
  } else {
    ElMessage.warning('请选择两个成员进行关系查询')
  }
}

const handleMemberSelect = (member: FamilyMember) => {
  selectedMember.value = member
  if (!selectedMembers.value.find(m => m.id === member.id)) {
    selectedMembers.value.push(member)
  }
}

const handleMemberAdd = (parent?: FamilyMember) => {
  parentMember.value = parent || null
  addMemberVisible.value = true
}

const handleFilterChange = (filters: MemberFilters) => {
  memberFilters.value = { ...filters }
}

const handleMemberClick = (member: FamilyMember) => {
  handleMemberSelect(member)
}

const handleMemberDoubleClick = (member: FamilyMember) => {
  selectedMember.value = member
  memberDetailVisible.value = true
}

const handleMemberContextMenu = (member: FamilyMember, event: MouseEvent) => {
  // 显示右键菜单
  event.preventDefault()
  // TODO: 实现右键菜单
}

const handleRelationshipCreate = (from: FamilyMember, to: FamilyMember, type: string) => {
  // 创建关系
  familyStore.createRelationship(from.id, to.id, type)
}

const handleMemberEdit = (member: FamilyMember) => {
  editingMember.value = member
  editMemberVisible.value = true
  memberDetailVisible.value = false
}

const handleMemberDelete = async (member: FamilyMember) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除成员 ${member.name} 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await familyStore.deleteMember(member.id)
    ElMessage.success('删除成功')
    memberDetailVisible.value = false
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleMemberAddConfirm = async (memberData: Partial<FamilyMember>) => {
  try {
    await familyStore.addMember({
      ...memberData,
      family_id: parseInt(familyId.value)
    } as FamilyMember)
    ElMessage.success('添加成员成功')
    addMemberVisible.value = false
  } catch (error) {
    ElMessage.error('添加成员失败')
  }
}

const handleMemberEditConfirm = async (memberData: FamilyMember) => {
  try {
    await familyStore.updateMember(memberData)
    ElMessage.success('更新成员信息成功')
    editMemberVisible.value = false
  } catch (error) {
    ElMessage.error('更新成员信息失败')
  }
}

// 生命周期
onMounted(async () => {
  try {
    await familyStore.loadFamily(familyId.value)
    await familyStore.loadMembers(familyId.value)
  } catch (error) {
    ElMessage.error('加载族谱数据失败')
    router.push('/family')
  }
})

onUnmounted(() => {
  familyStore.clearCurrentFamily()
})

// 监听器
watch(familyId, async (newId) => {
  if (newId) {
    await familyStore.loadFamily(newId)
    await familyStore.loadMembers(newId)
  }
})
</script>
```

#### 3.1.3 样式设计
```scss
<style scoped lang="scss">
.family-tree-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.graph-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 8px;
  margin: 0 16px 16px 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

// 响应式设计
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }
  
  .graph-area {
    margin: 0 16px 16px 16px;
  }
}

@media (max-width: 768px) {
  .family-tree-page {
    height: 100vh;
  }
  
  .graph-area {
    margin: 0 8px 8px 8px;
    border-radius: 4px;
  }
}
</style>
```

### 3.2 FamilyTreeToolbar.vue (工具栏组件)

#### 3.2.1 模板结构
```vue
<template>
  <div class="family-tree-toolbar">
    <div class="toolbar-left">
      <!-- 布局选择器 -->
      <el-select
        :model-value="layout"
        placeholder="布局方式"
        size="default"
        style="width: 140px"
        @update:model-value="$emit('update:layout', $event)"
      >
        <el-option
          v-for="option in layoutOptions"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </el-select>

      <!-- 世代筛选器 -->
      <el-select
        :model-value="generationRange"
        placeholder="世代范围"
        size="default"
        style="width: 120px"
        @update:model-value="$emit('update:generationRange', $event)"
      >
        <el-option label="全部世代" value="all" />
        <el-option label="1-3世代" value="1-3" />
        <el-option label="1-5世代" value="1-5" />
        <el-option label="1-7世代" value="1-7" />
      </el-select>

      <!-- 搜索框 -->
      <el-input
        :model-value="searchKeyword"
        placeholder="搜索成员姓名"
        size="default"
        style="width: 200px"
        clearable
        @update:model-value="$emit('update:searchKeyword', $event)"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 称呼查询按钮 -->
      <el-button
        type="primary"
        size="default"
        :icon="Connection"
        @click="$emit('calculateRelationship')"
      >
        称呼查询
      </el-button>
    </div>

    <div class="toolbar-right">
      <!-- 缩放控制 -->
      <el-button-group>
        <el-button
          size="default"
          :icon="ZoomIn"
          @click="$emit('zoomIn')"
        >
          放大
        </el-button>
        <el-button
          size="default"
          :icon="ZoomOut"
          @click="$emit('zoomOut')"
        >
          缩小
        </el-button>
        <el-button
          size="default"
          :icon="Refresh"
          @click="$emit('resetZoom')"
        >
          重置
        </el-button>
        <el-button
          size="default"
          :icon="FullScreen"
          @click="$emit('toggleFullscreen')"
        >
          全屏
        </el-button>
      </el-button-group>

      <!-- 视图选项 -->
      <el-dropdown @command="handleViewOption">
        <el-button size="default">
          视图选项
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              :command="{ key: 'showPhotos', value: !viewOptions.showPhotos }"
            >
              <el-checkbox :model-value="viewOptions.showPhotos" />
              显示照片
            </el-dropdown-item>
            <el-dropdown-item
              :command="{ key: 'showDates', value: !viewOptions.showDates }"
            >
              <el-checkbox :model-value="viewOptions.showDates" />
              显示生卒年
            </el-dropdown-item>
            <el-dropdown-item
              :command="{ key: 'showGeneration', value: !viewOptions.showGeneration }"
            >
              <el-checkbox :model-value="viewOptions.showGeneration" />
              显示世代
            </el-dropdown-item>
            <el-dropdown-item
              :command="{ key: 'showRelationshipLines', value: !viewOptions.showRelationshipLines }"
            >
              <el-checkbox :model-value="viewOptions.showRelationshipLines" />
              显示关系线
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- 导出功能 -->
      <el-dropdown @command="handleExport">
        <el-button type="primary" size="default">
          导出
          <el-icon class="el-icon--right"><Download /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="png">导出PNG图片</el-dropdown-item>
            <el-dropdown-item command="pdf">导出PDF文档</el-dropdown-item>
            <el-dropdown-item command="excel">导出Excel表格</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>
```

#### 3.2.2 脚本逻辑
```typescript
<script setup lang="ts">
import { computed } from 'vue'
import {
  Search,
  Connection,
  ZoomIn,
  ZoomOut,
  Refresh,
  FullScreen,
  ArrowDown,
  Download
} from '@element-plus/icons-vue'

import type { LayoutType, ViewOptions } from '@/types/familyTree'

// Props
interface Props {
  layout: LayoutType
  generationRange: string
  searchKeyword: string
  viewOptions: ViewOptions
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'update:layout', value: LayoutType): void
  (e: 'update:generationRange', value: string): void
  (e: 'update:searchKeyword', value: string): void
  (e: 'update:viewOptions', value: ViewOptions): void
  (e: 'zoomIn'): void
  (e: 'zoomOut'): void
  (e: 'resetZoom'): void
  (e: 'toggleFullscreen'): void
  (e: 'export', format: string): void
  (e: 'calculateRelationship'): void
}

const emit = defineEmits<Emits>()

// 布局选项
const layoutOptions = [
  { label: '垂直树形', value: 'tree-vertical' },
  { label: '水平树形', value: 'tree-horizontal' },
  { label: '径向布局', value: 'radial' },
  { label: '力导向图', value: 'force' }
]

// 事件处理器
const handleViewOption = (command: { key: keyof ViewOptions; value: boolean }) => {
  const newOptions = { ...props.viewOptions }
  newOptions[command.key] = command.value
  emit('update:viewOptions', newOptions)
}

const handleExport = (format: string) => {
  emit('export', format)
}
</script>
```

#### 3.2.3 样式设计
```scss
<style scoped lang="scss">
.family-tree-toolbar {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

// 响应式设计
@media (max-width: 1200px) {
  .toolbar-left {
    gap: 12px;
  }
  
  .toolbar-left .el-input {
    width: 160px !important;
  }
}

@media (max-width: 768px) {
  .family-tree-toolbar {
    flex-direction: column;
    height: auto;
    padding: 12px 16px;
    gap: 12px;
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .toolbar-left .el-select,
  .toolbar-left .el-input {
    width: 120px !important;
  }
}
</style>
```

### 3.3 FamilyTreeSidebar.vue (侧边栏组件)

#### 3.3.1 模板结构
```vue
<template>
  <div class="family-tree-sidebar" :class="{ collapsed: !visible }">
    <!-- 折叠按钮 -->
    <div class="sidebar-toggle" @click="toggleSidebar">
      <el-icon>
        <ArrowLeft v-if="visible" />
        <ArrowRight v-else />
      </el-icon>
    </div>

    <!-- 侧边栏内容 -->
    <div v-show="visible" class="sidebar-content">
      <!-- 族谱信息卡片 -->
      <FamilyInfoCard :family="family" />

      <!-- 快速筛选器 -->
      <MemberFilters
        :filters="filters"
        @update:filters="$emit('filterChange', $event)"
      />

      <!-- 成员列表 -->
      <MemberList
        :members="members"
        :selected-members="selectedMembers"
        @member-select="$emit('memberSelect', $event)"
        @member-add="$emit('memberAdd', $event)"
      />

      <!-- 统计信息 -->
      <FamilyStats :family="family" :members="members" />
    </div>
  </div>
</template>
```

#### 3.3.2 脚本逻辑
```typescript
<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

import FamilyInfoCard from './FamilyInfoCard.vue'
import MemberFilters from './MemberFilters.vue'
import MemberList from './MemberList.vue'
import FamilyStats from './FamilyStats.vue'

import type { Family, FamilyMember } from '@/types/family'
import type { MemberFilters as MemberFiltersType } from '@/types/familyTree'

// Props
interface Props {
  visible: boolean
  family: Family | null
  members: FamilyMember[]
  filters: MemberFiltersType
  selectedMembers?: FamilyMember[]
}

const props = withDefaults(defineProps<Props>(), {
  selectedMembers: () => []
})

// Emits
interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'memberSelect', member: FamilyMember): void
  (e: 'memberAdd', parent?: FamilyMember): void
  (e: 'filterChange', filters: MemberFiltersType): void
}

const emit = defineEmits<Emits>()

// 方法
const toggleSidebar = () => {
  emit('update:visible', !props.visible)
}
</script>
```

#### 3.3.3 样式设计
```scss
<style scoped lang="scss">
.family-tree-sidebar {
  width: 320px;
  background: #fafafa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  transition: width 0.3s ease;
  position: relative;
  
  &.collapsed {
    width: 60px;
  }
}

.sidebar-toggle {
  position: absolute;
  top: 50%;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transform: translateY(-50%);
  transition: all 0.3s ease;
  
  &:hover {
    background: #f5f7fa;
    border-color: #c0c4cc;
  }
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// 响应式设计
@media (max-width: 1200px) {
  .family-tree-sidebar {
    width: 280px;
    
    &.collapsed {
      width: 50px;
    }
  }
}

@media (max-width: 768px) {
  .family-tree-sidebar {
    position: fixed;
    left: 0;
    top: 124px; // 头部 + 工具栏高度
    height: calc(100vh - 164px); // 减去头部、工具栏、状态栏高度
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .sidebar-toggle {
    right: -30px;
    width: 30px;
    height: 40px;
    border-radius: 0 8px 8px 0;
  }
}
</style>
```

### 3.4 GraphNode.vue (节点组件)

#### 3.4.1 模板结构
```vue
<template>
  <div
    class="graph-node"
    :class="[
      `node-${member.gender}`,
      { 
        selected: isSelected,
        highlighted: isHighlighted,
        'has-children': hasChildren,
        'is-married': isMarried
      }
    ]"
    @click="handleClick"
    @dblclick="handleDoubleClick"
    @contextmenu="handleContextMenu"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 节点主体 -->
    <div class="node-body">
      <!-- 头像区域 -->
      <div class="node-avatar">
        <img
          v-if="member.avatar && showPhotos"
          :src="member.avatar"
          :alt="member.name"
          @error="handleImageError"
        />
        <div v-else class="avatar-placeholder">
          {{ member.name.charAt(0) }}
        </div>
        
        <!-- 状态指示器 -->
        <div class="status-indicators">
          <div v-if="!member.is_alive" class="indicator deceased" title="已故" />
          <div v-if="hasChildren" class="indicator has-children" title="有子女" />
          <div v-if="isMarried" class="indicator married" title="已婚" />
        </div>
      </div>
      
      <!-- 信息区域 -->
      <div class="node-info">
        <div class="node-name" :title="member.name">{{ member.name }}</div>
        <div v-if="showDates" class="node-dates">
          {{ formatDates(member.birth_date, member.death_date) }}
        </div>
        <div v-if="showGeneration" class="node-generation">
          第{{ member.generation }}世
        </div>
        <div v-if="member.occupation" class="node-occupation">
          {{ member.occupation }}
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div v-show="isHovered && !readonly" class="node-actions">
      <el-button
        type="primary"
        size="small"
        circle
        :icon="View"
        title="查看详情"
        @click.stop="handleViewDetails"
      />
      <el-button
        type="success"
        size="small"
        circle
        :icon="Edit"
        title="编辑信息"
        @click.stop="handleEdit"
      />
      <el-button
        type="info"
        size="small"
        circle
        :icon="Connection"
        title="添加关系"
        @click.stop="handleAddRelation"
      />
    </div>
    
    <!-- 连接点 -->
    <div class="connection-points">
      <div class="connection-point top" data-direction="top" />
      <div class="connection-point right" data-direction="right" />
      <div class="connection-point bottom" data-direction="bottom" />
      <div class="connection-point left" data-direction="left" />
    </div>
  </div>
</template>
```

#### 3.4.2 脚本逻辑
```typescript
<script setup lang="ts">
import { ref, computed } from 'vue'
import { View, Edit, Connection } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import type { FamilyMember } from '@/types/family'

// Props
interface Props {
  member: FamilyMember
  isSelected?: boolean
  isHighlighted?: boolean
  showPhotos?: boolean
  showDates?: boolean
  showGeneration?: boolean
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isHighlighted: false,
  showPhotos: true,
  showDates: true,
  showGeneration: true,
  readonly: false
})

// Emits
interface Emits {
  (e: 'click', member: FamilyMember, event: MouseEvent): void
  (e: 'double-click', member: FamilyMember, event: MouseEvent): void
  (e: 'context-menu', member: FamilyMember, event: MouseEvent): void
  (e: 'view-details', member: FamilyMember): void
  (e: 'edit', member: FamilyMember): void
  (e: 'add-relation', member: FamilyMember): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const isHovered = ref(false)

// 计算属性
const hasChildren = computed(() => {
  return props.member.children_ids && props.member.children_ids.length > 0
})

const isMarried = computed(() => {
  return props.member.spouse_ids && props.member.spouse_ids.length > 0
})

// 方法
const formatDates = (birthDate?: string, deathDate?: string) => {
  const birth = birthDate ? formatDate(birthDate, 'YYYY') : '?'
  const death = deathDate ? formatDate(deathDate, 'YYYY') : (props.member.is_alive ? '' : '?')
  
  if (death) {
    return `${birth}-${death}`
  } else {
    return birth
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

const handleClick = (event: MouseEvent) => {
  emit('click', props.member, event)
}

const handleDoubleClick = (event: MouseEvent) => {
  emit('double-click', props.member, event)
}

const handleContextMenu = (event: MouseEvent) => {
  emit('context-menu', props.member, event)
}

const handleMouseEnter = () => {
  isHovered.value = true
}

const handleMouseLeave = () => {
  isHovered.value = false
}

const handleViewDetails = () => {
  emit('view-details', props.member)
}

const handleEdit = () => {
  emit('edit', props.member)
}

const handleAddRelation = () => {
  emit('add-relation', props.member)
}
</script>
```

#### 3.4.3 样式设计
```scss
<style scoped lang="scss">
.graph-node {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  
  &:hover {
    transform: scale(1.05);
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.15));
  }
  
  &.selected {
    transform: scale(1.1);
    filter: drop-shadow(0 6px 12px rgba(200, 16, 46, 0.3));
  }
  
  &.highlighted {
    animation: pulse 2s infinite;
  }
}

.node-body {
  width: 120px;
  padding: 12px;
  border-radius: 8px;
  background: white;
  border: 3px solid #1890ff;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

// 性别样式
.node-male .node-body {
  border-color: #1890ff;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
}

.node-female .node-body {
  border-color: #eb2f96;
  background: linear-gradient(135deg, #fff0f6 0%, #ffadd6 100%);
}

// 头像区域
.node-avatar {
  position: relative;
  width: 50px;
  height: 50px;
  margin: 0 auto 8px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: #1890ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.node-female .avatar-placeholder {
  background: #eb2f96;
}

// 状态指示器
.status-indicators {
  position: absolute;
  top: -2px;
  right: -2px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  
  &.deceased {
    background: #8c8c8c;
  }
  
  &.has-children {
    background: #52c41a;
  }
  
  &.married {
    background: #eb2f96;
  }
}

// 信息区域
.node-info {
  .node-name {
    font-size: 14px;
    font-weight: 500;
    color: #262626;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .node-dates {
    font-size: 11px;
    color: #8c8c8c;
    margin-bottom: 4px;
  }
  
  .node-generation {
    font-size: 10px;
    color: #595959;
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 2px;
  }
  
  .node-occupation {
    font-size: 10px;
    color: #722ed1;
    background: #f9f0ff;
    padding: 1px 4px;
    border-radius: 8px;
    display: inline-block;
  }
}

// 操作按钮
.node-actions {
  position: absolute;
  top: -20px;
  right: -20px;
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.9);
  padding: 4px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  
  .el-button {
    width: 24px;
    height: 24px;
    padding: 0;
    
    .el-icon {
      font-size: 12px;
    }
  }
}

// 连接点
.connection-points {
  .connection-point {
    position: absolute;
    width: 8px;
    height: 8px;
    background: #1890ff;
    border: 2px solid white;
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.3s ease;
    
    &.top {
      top: -4px;
      left: 50%;
      transform: translateX(-50%);
    }
    
    &.right {
      right: -4px;
      top: 50%;
      transform: translateY(-50%);
    }
    
    &.bottom {
      bottom: -4px;
      left: 50%;
      transform: translateX(-50%);
    }
    
    &.left {
      left: -4px;
      top: 50%;
      transform: translateY(-50%);
    }
  }
}

.graph-node:hover .connection-point {
  opacity: 1;
}

// 动画
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(200, 16, 46, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(200, 16, 46, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(200, 16, 46, 0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .node-body {
    width: 100px;
    padding: 8px;
  }
  
  .node-avatar {
    width: 40px;
    height: 40px;
  }
  
  .avatar-placeholder {
    font-size: 16px;
  }
  
  .node-info .node-name {
    font-size: 12px;
  }
  
  .node-actions {
    top: -15px;
    right: -15px;
    
    .el-button {
      width: 20px;
      height: 20px;
      
      .el-icon {
        font-size: 10px;
      }
    }
  }
}
</style>
```

## 4. 交互设计规范

### 4.1 节点交互
- **单击**: 选中节点，显示基本信息
- **双击**: 打开成员详情弹窗
- **右键**: 显示上下文菜单
- **悬浮**: 节点放大，显示操作按钮
- **拖拽**: 调整节点位置（自由布局模式）

### 4.2 画布交互
- **鼠标滚轮**: 缩放画布
- **拖拽空白区域**: 平移画布
- **Ctrl+拖拽**: 框选多个节点
- **双指手势**: 移动端缩放支持

### 4.3 键盘快捷键
- **Ctrl+A**: 全选节点
- **Delete**: 删除选中节点
- **Ctrl+Z**: 撤销操作
- **Ctrl+Y**: 重做操作
- **F11**: 全屏模式
- **Esc**: 取消选择

## 5. 响应式设计

### 5.1 桌面端 (>1200px)
- 完整三栏布局
- 侧边栏宽度320px
- 工具栏完整显示所有功能

### 5.2 平板端 (768px-1200px)
- 侧边栏可收缩至60px
- 工具栏部分功能合并
- 触摸优化交互

### 5.3 移动端 (<768px)
- 侧边栏改为抽屉式
- 工具栏简化布局
- 节点大小适配触摸

## 6. 性能优化

### 6.1 渲染优化
- 虚拟滚动处理大量成员列表
- 图形渲染优化和懒加载
- 节点复用和缓存机制

### 6.2 交互优化
- 防抖处理搜索和筛选
- 节流处理缩放和拖拽
- 异步加载成员详情

### 6.3 内存优化
- 及时清理事件监听器
- 图片懒加载和压缩
- 数据分页和按需加载

## 7. 无障碍设计

### 7.1 键盘导航
- Tab键遍历所有可交互元素
- 方向键导航节点
- Enter键激活选中元素

### 7.2 屏幕阅读器
- 语义化HTML结构
- ARIA标签和属性
- 图片alt文本描述

### 7.3 视觉辅助
- 高对比度模式支持
- 字体大小调节
- 色盲友好的配色方案

## 8. 开发实现指南

### 8.1 技术栈确认
- **Vue 3.4+**: 组合式API + TypeScript
- **Element Plus 2.4+**: UI组件库
- **G6 4.8+**: 图形可视化
- **Pinia 2.1+**: 状态管理
- **Vite 5.0+**: 构建工具

### 8.2 关键依赖
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.4.0",
    "@element-plus/icons-vue": "^2.1.0",
    "@antv/g6": "^4.8.0",
    "dayjs": "^1.11.0",
    "lodash-es": "^4.17.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "typescript": "^5.0.0",
    "sass": "^1.69.0"
  }
}
```

### 8.3 目录结构
```
src/
├── components/
│   └── family/
│       ├── FamilyTreeHeader.vue
│       ├── FamilyTreeToolbar.vue
│       ├── FamilyTreeSidebar.vue
│       ├── FamilyTreeGraph.vue
│       ├── FamilyTreeStatusBar.vue
│       ├── FamilyInfoCard.vue
│       ├── MemberFilters.vue
│       ├── MemberList.vue
│       ├── FamilyStats.vue
│       ├── GraphNode.vue
│       ├── GraphEdge.vue
│       ├── MemberDetailDialog.vue
│       ├── AddMemberDialog.vue
│       ├── EditMemberDialog.vue
│       └── RelationshipDrawer.vue
├── pages/
│   └── family/
│       └── FamilyTreePage.vue
├── composables/
│   ├── useFamilyTreeGraph.ts
│   ├── useFamilyTree.ts
│   └── useGraphInteraction.ts
├── stores/
│   ├── family.ts
│   └── user.ts
├── types/
│   ├── family.ts
│   └── familyTree.ts
└── utils/
    ├── graph.ts
    ├── date.ts
    └── export.ts
```

### 8.4 开发优先级
1. **第一阶段**: 基础页面结构和布局
2. **第二阶段**: 图形展示和基础交互
3. **第三阶段**: 成员管理和详情功能
4. **第四阶段**: 高级功能和优化
5. **第五阶段**: 响应式和无障碍优化

这个完整的UI设计方案提供了族谱页面的详细实现指南，包含了所有必要的组件设计、交互规范、样式定义和开发指导。您可以按照这个方案逐步实现族谱页面的各个功能模块。