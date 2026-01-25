<template>
  <div ref="containerRef" class="enhanced-family-graph">
    <!-- 工具栏 -->
    <div v-if="showToolbar" class="graph-toolbar">
      <div class="toolbar-section">
        <!-- 布局选择 -->
        <el-select v-model="currentLayout" size="small" @change="handleLayoutChange">
          <el-option label="层次布局" :value="FamilyLayoutType.HIERARCHICAL" />
          <el-option label="紧凑布局" :value="FamilyLayoutType.COMPACT" />
          <el-option label="环形布局" :value="FamilyLayoutType.CIRCULAR" />
          <el-option label="正交布局" :value="FamilyLayoutType.ORTHOGONAL" />
          <el-option label="有机布局" :value="FamilyLayoutType.ORGANIC" />
        </el-select>
        
        <!-- 显示选项 -->
        <el-switch
v-model="showRelationships" active-text="关系" 
                   inactive-text="关系" size="small" @change="handleToggleRelationships" />
        <el-switch
v-model="showPhotos" active-text="照片" 
                   inactive-text="照片" size="small" @change="handleTogglePhotos" />
        <el-switch
v-model="showDates" active-text="日期" 
                   inactive-text="日期" size="small" @change="handleToggleDates" />
        <el-switch
v-model="showGeneration" active-text="世代" 
                   inactive-text="世代" size="small" @change="handleToggleGeneration" />
      </div>
      
      <div class="toolbar-section">
        <!-- 缩放控制 -->
        <el-button-group>
          <el-button size="small" :icon="ZoomOutIcon" @click="zoomOut" />
          <el-button size="small" @click="resetZoom">{{ Math.round(internalZoom * 100) }}%</el-button>
          <el-button size="small" :icon="ZoomInIcon" @click="zoomIn" />
        </el-button-group>
        
        <!-- 视图控制 -->
        <el-button size="small" :icon="FullScreenIcon" @click="fitToScreen">适应屏幕</el-button>
        <el-button size="small" :icon="AimIcon" @click="centerGraph">居中</el-button>
        
        <!-- 导出 -->
        <el-dropdown @command="handleExport">
          <el-button size="small" :icon="DownloadIcon">
            导出<el-icon class="el-icon--right"><ArrowDownIcon /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="png">PNG 图片</el-dropdown-item>
              <el-dropdown-item command="svg">SVG 矢量图</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 图形容器 -->
    <div ref="graphContainerRef" class="graph-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner"></div>
          <p>正在加载族谱...</p>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && members.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <h3>暂无家族成员</h3>
        <p>点击"添加成员"开始构建您的家族族谱</p>
        <el-button type="primary" size="small" @click="$emit('addMember')">
          <el-icon><PlusIcon /></el-icon>
          添加成员
        </el-button>
      </div>
      
      <!-- 右键菜单 -->
      <div 
        v-show="contextMenu.visible" 
        class="context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        @click.stop
      >
        <div class="context-menu-item" @click="handleContextMenuAction('edit')">
          <el-icon><EditIcon /></el-icon>
          编辑成员
        </div>
        <div class="context-menu-item" @click="handleContextMenuAction('view')">
          <el-icon><ViewIcon /></el-icon>
          查看详情
        </div>
        <div class="context-menu-item" @click="handleContextMenuAction('select')">
          <el-icon><CheckIcon /></el-icon>
          选择成员
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item danger" @click="handleContextMenuAction('delete')">
          <el-icon><DeleteIcon /></el-icon>
          删除成员
        </div>
      </div>
      
      <!-- 快捷键帮助 -->
      <div v-show="showKeyboardHelp" class="keyboard-help">
        <div class="help-title">快捷键</div>
        <div class="help-item"><kbd>Ctrl + 滚轮</kbd> 缩放</div>
        <div class="help-item"><kbd>Ctrl + +</kbd> 放大</div>
        <div class="help-item"><kbd>Ctrl + -</kbd> 缩小</div>
        <div class="help-item"><kbd>Ctrl + 0</kbd> 重置缩放</div>
        <div class="help-item"><kbd>方向键</kbd> 平移</div>
        <div class="help-item"><kbd>?</kbd> 显示/隐藏帮助</div>
      </div>
      
      <!-- 帮助按钮 -->
      <button class="help-toggle" title="快捷键帮助" @click="toggleKeyboardHelp">?</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { 
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  FullScreen as FullScreenIcon,
  Aim as AimIcon,
  Download as DownloadIcon,
  ArrowDown as ArrowDownIcon,
  Plus as PlusIcon,
  Edit as EditIcon,
  View as ViewIcon,
  Check as CheckIcon,
  Delete as DeleteIcon
} from '@element-plus/icons-vue'

import { 
  FamilyGraphEngine, 
  createFamilyGraph,
  FamilyLayoutType,
  type FamilyMember,
  type FamilyGraphConfig
} from './FamilyGraphEngine'

// Props
interface Props {
  members: FamilyMember[]
  width?: number
  height?: number
  layout?: FamilyLayoutType
  showToolbar?: boolean
  showRelationships?: boolean
  showPhotos?: boolean
  showDates?: boolean
  showGeneration?: boolean
  enableAnimation?: boolean
  enableVirtualization?: boolean
  minZoom?: number
  maxZoom?: number
  zoomLevel?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 800,
  height: 600,
  layout: FamilyLayoutType.HIERARCHICAL,
  showToolbar: true,
  showRelationships: true,
  showPhotos: false,
  showDates: true,
  showGeneration: true,
  enableAnimation: true,
  enableVirtualization: true,
  minZoom: 0.1,
  maxZoom: 3,
  zoomLevel: 1
})

// Emits
const emit = defineEmits<{
  nodeClick: [member: FamilyMember]
  nodeDoubleClick: [member: FamilyMember]
  nodeEdit: [member: FamilyMember]
  nodeSelect: [members: FamilyMember[]]
  addMember: []
  export: [format: string]
  'update:zoomLevel': [level: number]
  'update-options': [options: { relationships?: boolean, photos?: boolean, dates?: boolean, generation?: boolean }]
}>()

// 响应式数据
const containerRef = ref<HTMLElement>()
const graphContainerRef = ref<HTMLElement>()
const loading = ref(false)
const showKeyboardHelp = ref(false)

// 图形引擎
let graphEngine: FamilyGraphEngine | null = null

// 当前状态
const currentLayout = ref<FamilyLayoutType>(props.layout)
// 初始化时使用 props 传入的值（这些值已经从 store 中读取了持久化配置）
const showRelationships = ref(props.showRelationships)
const showPhotos = ref(props.showPhotos)
const showDates = ref(props.showDates)
const showGeneration = ref(props.showGeneration)

// 监听 props 变化，确保外部 store 更新时同步更新内部状态
watch(() => props.showRelationships, (val) => { showRelationships.value = val })
watch(() => props.showPhotos, (val) => { showPhotos.value = val })
watch(() => props.showDates, (val) => { showDates.value = val })
watch(() => props.showGeneration, (val) => { showGeneration.value = val })

// 右键菜单
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  targetNodeId: null as string | null
})

const internalZoom = ref(1)

// 方法
const initializeGraph = async () => {
  if (!graphContainerRef.value) return
  
  loading.value = true
  
  try {
    const config: FamilyGraphConfig = {
      container: graphContainerRef.value,
      width: props.width,
      height: props.height,
      layout: currentLayout.value,
      showRelationships: showRelationships.value,
      showPhotos: showPhotos.value,
      showDates: showDates.value,
      showGeneration: showGeneration.value,
      enableAnimation: props.enableAnimation,
      enableVirtualization: props.enableVirtualization,
      minZoom: props.minZoom,
      maxZoom: props.maxZoom
    }
    
    graphEngine = createFamilyGraph(config)
    
    // 设置事件监听
    setupEventListeners()
    
    // 初始化引擎
    await graphEngine.initialize()
    
    // 应用初始缩放
    if (props.zoomLevel && props.zoomLevel !== 1) {
      graphEngine.setViewport({ zoom: props.zoomLevel })
      internalZoom.value = props.zoomLevel
    }
    
    // 加载数据
    if (props.members.length > 0) {
      graphEngine.loadData(props.members)
      // 自动适应屏幕
      graphEngine.fitToScreen()
    }
    
  } catch (error) {
    console.error('Failed to initialize graph:', error)
  } finally {
    loading.value = false
  }
}

const setupEventListeners = () => {
  if (!graphEngine) return

  // 视口变化
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('viewportChanged', (event: any) => {
    internalZoom.value = event.viewport.zoom
    emit('update:zoomLevel', event.viewport.zoom)
  })
  
  // 节点点击
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('nodeClick', (event: any) => {
    emit('nodeClick', event.node)
  })
  
  // 节点双击
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('nodeDoubleClick', (event: any) => {
    emit('nodeDoubleClick', event.node)
  })
  
  // 节点编辑
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('nodeEdit', (event: any) => {
    emit('nodeEdit', event.node)
  })
  
  // 选择变化
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('selectionChanged', (event: any) => {
    emit('nodeSelect', event.selectedMembers)
  })
  
  // 右键菜单
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('nodeContextMenu', (event: any) => {
    showContextMenu(event.nodeId, event.position)
  })
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  graphEngine.on('canvasContextMenu', (event: any) => {
    showContextMenu(null, event.position)
  })
}

const showContextMenu = (nodeId: string | null, position: { x: number, y: number }) => {
  contextMenu.value = {
    visible: true,
    x: position.x,
    y: position.y,
    targetNodeId: nodeId
  }
  
  // 点击其他地方关闭菜单
  nextTick(() => {
    document.addEventListener('click', hideContextMenu, { once: true })
  })
}

const hideContextMenu = () => {
  contextMenu.value.visible = false
}

const handleContextMenuAction = (action: string) => {
  const { targetNodeId } = contextMenu.value
  
  switch (action) {
    case 'edit':
      if (targetNodeId) {
        const member = props.members.find(m => m.id === targetNodeId)
        if (member) emit('nodeEdit', member)
      }
      break
    case 'view':
      if (targetNodeId) {
        const member = props.members.find(m => m.id === targetNodeId)
        if (member) emit('nodeClick', member)
      }
      break
    case 'select':
      if (targetNodeId && graphEngine) {
        graphEngine.selectMember(targetNodeId, true)
      }
      break
    case 'delete':
      // TODO: 实现删除功能
      console.log('Delete member:', targetNodeId)
      break
  }
  
  hideContextMenu()
}

// 布局控制
const handleLayoutChange = (layout: FamilyLayoutType) => {
  currentLayout.value = layout
  if (graphEngine) {
    graphEngine.setLayout(layout)
  }
}

// 显示控制
// 修改：这些处理函数现在应该触发 update 事件，通知父组件更新 store，而不是只更新本地状态
// 因为 EnhancedFamilyGraph 的 props 是单向数据流，状态源头在 FamilyTreePage 的 store 中
const handleToggleRelationships = (show: string | number | boolean) => {
  const val = Boolean(show)
  showRelationships.value = val
  // 触发父组件更新 store
  // 注意：这里没有定义 update:showRelationships 事件，但我们可以通过修改 props 默认行为或添加 emit
  // 鉴于 FamilyTreePage 直接绑定了 props，我们需要通知 store 更新
  // 这里暂时通过 updateGraphConfig 本地生效，但为了持久化，必须回传
  
  // 实际上，EnhancedFamilyGraph 的这些开关应该通过 v-model 绑定或者 emit 事件
  // 但目前代码结构中，FamilyTreePage 是通过 :show-relationships="familyStore.relationshipsVisible" 传进来的
  // 而 EnhancedFamilyGraph 内部又有开关控件，这导致了双向绑定断裂
  
  // 修正方案：
  // 1. EnhancedFamilyGraph 内部开关变化 -> 触发 updateGraphConfig (视觉更新) 
  // 2. 同时需要通知外部 Store 保存到 localStorage
  // 由于没有定义 emit，我们这里先确保本地视觉更新，同时尝试通过 emit 自定义事件通知父组件
  emit('update-options', { relationships: val })
  updateGraphConfig()
}

const handleTogglePhotos = (show: string | number | boolean) => {
  const val = Boolean(show)
  showPhotos.value = val
  emit('update-options', { photos: val })
  updateGraphConfig()
}

const handleToggleDates = (show: string | number | boolean) => {
  const val = Boolean(show)
  showDates.value = val
  emit('update-options', { dates: val })
  updateGraphConfig()
}

const handleToggleGeneration = (show: string | number | boolean) => {
  const val = Boolean(show)
  showGeneration.value = val
  emit('update-options', { generation: val })
  updateGraphConfig()
}

const updateGraphConfig = () => {
  // 重新初始化图形以应用新的配置
  if (graphEngine) {
    graphEngine.updateConfig({
      showRelationships: showRelationships.value,
      showPhotos: showPhotos.value,
      showDates: showDates.value,
      showGeneration: showGeneration.value
    })
    
    // 如果没有数据，则加载数据
    if (graphEngine.getMembers().value.length === 0 && props.members.length > 0) {
      graphEngine.loadData(props.members)
    }
  }
}

// 缩放控制
const zoomIn = () => {
  if (graphEngine) {
    const currentZoom = graphEngine.getViewport().value.zoom
    const newZoom = Math.min(props.maxZoom, currentZoom + 0.1)
    graphEngine.setViewport({ zoom: newZoom })
  }
}

const zoomOut = () => {
  if (graphEngine) {
    const currentZoom = graphEngine.getViewport().value.zoom
    const newZoom = Math.max(props.minZoom, currentZoom - 0.1)
    graphEngine.setViewport({ zoom: newZoom })
  }
}

const resetZoom = () => {
  if (graphEngine) {
    graphEngine.setViewport({ zoom: 1 })
  }
}

// 视图控制
const fitToScreen = () => {
  if (graphEngine) {
    graphEngine.fitToScreen()
  }
}

const centerGraph = () => {
  if (graphEngine) {
    graphEngine.centerGraph()
  }
}

// 导出
const handleExport = (format: string) => {
  if (graphEngine) {
    try {
      const dataURL = graphEngine.exportAsImage(format as 'png' | 'svg')
      const link = document.createElement('a')
      link.href = dataURL
      link.download = `family-tree.${format}`
      link.click()
      emit('export', format)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }
}

// 帮助
const toggleKeyboardHelp = () => {
  showKeyboardHelp.value = !showKeyboardHelp.value
}

// 监听数据变化
watch(() => props.members, (newMembers) => {
  if (graphEngine) {
    if (newMembers.length > 0) {
      graphEngine.loadData(newMembers)
    }
  }
}, { deep: true })

// 监听显示选项变化
watch(() => [props.showRelationships, props.showPhotos, props.showDates, props.showGeneration], () => {
  showRelationships.value = props.showRelationships
  showPhotos.value = props.showPhotos
  showDates.value = props.showDates
  showGeneration.value = props.showGeneration
  updateGraphConfig()
})

// 监听数据变化，重新加载并适应屏幕
watch(() => props.members, (newMembers) => {
  if (graphEngine && newMembers.length > 0) {
    graphEngine.loadData(newMembers)
    graphEngine.fitToScreen()
  }
}, { deep: true })

// 监听尺寸变化
watch(() => [props.width, props.height], () => {
  if (graphEngine && graphContainerRef.value) {
    // 重新调整尺寸
    initializeGraph()
  }
})

// 监听缩放变化
watch(() => props.zoomLevel, (newZoom) => {
  if (graphEngine && newZoom && Math.abs(newZoom - internalZoom.value) > 0.001) {
    graphEngine.setViewport({ zoom: newZoom })
  }
})

// 生命周期
onMounted(async () => {
  await nextTick()
  await initializeGraph()
})

onUnmounted(() => {
  if (graphEngine) {
    graphEngine.destroy()
    graphEngine = null
  }
})

// 暴露方法给父组件
defineExpose({
  fitToScreen,
  centerGraph,
  zoomIn,
  zoomOut,
  resetZoom,
  exportAsImage: (format: string) => handleExport(format)
})
</script>

<style scoped>
.enhanced-family-graph {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
}

/* 工具栏 */
.graph-toolbar {
  height: 56px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  gap: 16px;
  z-index: 10;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 图形容器 */
.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%);
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #6b7280;
  z-index: 10;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
}

.empty-state p {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 20px;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 4px 0;
  min-width: 160px;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.context-menu-item:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.context-menu-item.danger {
  color: #ef4444;
}

.context-menu-item.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.context-menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 4px 0;
}

/* 快捷键帮助 */
.keyboard-help {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  z-index: 30;
  min-width: 200px;
  backdrop-filter: blur(8px);
}

.help-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #fbbf24;
}

.help-item {
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-item kbd {
  background: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 11px;
}

/* 帮助按钮 */
.help-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  z-index: 25;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}

.help-toggle:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

/* Element Plus 样式覆盖 */
:deep(.el-select) {
  width: 120px;
}

:deep(.el-switch) {
  --el-switch-on-color: #3b82f6;
  --el-switch-off-color: #d1d5db;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .graph-toolbar {
    height: auto;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 8px;
  }
  
  .toolbar-section {
    justify-content: space-between;
    flex-wrap: wrap;
  }
  
  .context-menu {
    min-width: 140px;
  }
  
  .keyboard-help {
    top: 10px;
    right: 10px;
    min-width: 160px;
    font-size: 11px;
  }
}
</style>