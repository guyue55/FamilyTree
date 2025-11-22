<template>
  <div class="family-graph-component">
    <div 
      ref="graphContainer"
      class="graph-container"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
      @wheel="handleWheel"
    >
      <!-- 族谱内容区域 -->
      <div 
        class="graph-content"
        :style="{
          transform: `scale(${zoomLevel}) translate(${panX}px, ${panY}px)`
        }"
        @wheel="handleWheel"
      >
        <!-- 世代布局 -->
        <div 
          v-for="generation in generationGroups" 
          :key="generation.level"
          class="generation"
        >
          <!-- 世代标签 -->
          <div class="generation-label">
            第{{ generation.level }}代
          </div>
          
          <!-- 成员节点组 -->
          <div class="node-group">
            <!-- 遍历该世代的所有成员组 -->
            <template v-for="group in generation.groups" :key="group.id">
              <!-- 夫妻组 -->
              <div v-if="group.type === 'couple'" class="couple-group">
                <div
                  v-for="member in group.members"
                  :key="member.id"
                  class="family-node"
                  :data-member-id="member.id"
                  :class="[
                    member.gender,
                    { 
                      selected: (selectedMember && selectedMember.id === member.id),
                      deceased: member.deathDate 
                    }
                  ]"
                  @click="handleMemberClick(member)"
                  @dblclick="handleMemberEdit(member)"
                >
                  <!-- 头像 -->
                  <div class="node-avatar">
                  <img 
                    v-if="member.photo && props.showPhotos" 
                    :src="member.photo" 
                    :alt="member.name"
                    class="avatar-image"
                  >
                    <div v-else class="avatar-placeholder">
                      {{ getInitial(member.name) }}
                    </div>
                  </div>
                  
                  <!-- 姓名 -->
                  <div class="node-name">{{ member.name }}</div>
                  
                  <!-- 日期信息 -->
                  <div v-if="props.showDates" class="node-dates">
                    {{ formatDateRange(member.birthDate, member.deathDate) }}
                  </div>
                  
                  <!-- 世代信息 -->
                  <div v-if="props.showGeneration" class="node-generation">
                    第{{ member.generation }}代
                  </div>
                </div>
              </div>
              
              <!-- 单身成员 -->
              <div v-else class="family-node"
                :data-member-id="group.member.id"
                :class="[
                  group.member.gender,
                  { 
                    selected: (selectedMember && selectedMember.id === group.member.id),
                    deceased: group.member.deathDate 
                  }
                ]"
                @click="handleMemberClick(group.member)"
                @dblclick="handleMemberEdit(group.member)"
              >
                <!-- 头像 -->
                <div class="node-avatar">
                  <img 
                    v-if="group.member.photo && props.showPhotos" 
                    :src="group.member.photo" 
                    :alt="group.member.name"
                    class="avatar-image"
                  >
                  <div v-else class="avatar-placeholder">
                    {{ getInitial(group.member.name) }}
                  </div>
                </div>
                
                <!-- 姓名 -->
                <div class="node-name">{{ group.member.name }}</div>
                
                <!-- 日期信息 -->
                <div v-if="props.showDates" class="node-dates">
                  {{ formatDateRange(group.member.birthDate, group.member.deathDate) }}
                </div>
                
                <!-- 世代信息 -->
                <div v-if="props.showGeneration" class="node-generation">
                  第{{ group.member.generation }}代
                </div>
              </div>
            </template>
          </div>
        </div>
        
        <!-- 关系连线 -->
        <svg 
          class="relationship-lines"
          :class="{ show: props.showRelationships, hide: !props.showRelationships }"
          ref="linesSvg"
        >
          <!-- 父子关系连线分段渲染：先竖后横，横向在最上层形成跨越效果 -->
          <g v-for="line in parentChildLines" :key="line.id + '-v'">
            <path v-if="line.v1" :d="line.v1" class="parent-child-line pc-vert-line" />
            <path v-if="line.v2" :d="line.v2" class="parent-child-line pc-vert-line" />
          </g>
          <g v-for="line in parentChildLines" :key="line.id + '-h'">
            <path v-if="line.h" :d="line.h" class="parent-child-line pc-horz-line" />
            <path v-if="line.hc" :d="line.hc" class="parent-child-line pc-horz-line" />
          </g>
        </svg>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p>正在加载族谱...</p>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && members.length === 0" class="empty-state">
        <div class="empty-icon">👥</div>
        <h3>暂无家族成员</h3>
        <p>点击"添加成员"开始构建您的家族族谱</p>
      </div>
      
      <!-- 快捷键帮助提示 -->
      <div class="keyboard-help" v-show="showKeyboardHelp">
        <div class="help-title">快捷键</div>
        <div class="help-item"><kbd>Ctrl + 滚轮</kbd> 缩放</div>
        <div class="help-item"><kbd>Ctrl + +</kbd> 放大</div>
        <div class="help-item"><kbd>Ctrl + -</kbd> 缩小</div>
        <div class="help-item"><kbd>Ctrl + 0</kbd> 重置缩放</div>
        <div class="help-item"><kbd>Ctrl+C</kbd> 居中</div>
        <div class="help-item"><kbd>Ctrl+F</kbd> 适应屏幕</div>
        <div class="help-item"><kbd>滚轮</kbd> 上下滚动</div>
        <div class="help-item"><kbd>方向键</kbd> 平移</div>
        <div class="help-item"><kbd>?</kbd> 显示/隐藏帮助</div>
      </div>
      
      <!-- 帮助按钮 -->
      <button class="help-toggle" @click="toggleKeyboardHelp" title="快捷键帮助">?</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { FamilyMember } from '@/types/family'

// Props
interface Props {
  members: FamilyMember[]
  zoomLevel?: number
  showRelationships?: boolean
  showPhotos?: boolean
  showDates?: boolean
  showGeneration?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  zoomLevel: 1,
  showRelationships: true,
  showPhotos: false,
  showDates: true,
  showGeneration: true
})

// Emits
const emit = defineEmits<{
  memberClick: [member: FamilyMember]
  memberEdit: [member: FamilyMember]
}>()

// 响应式数据
const graphContainer = ref<HTMLElement>()
const linesSvg = ref<SVGSVGElement>()
const loading = ref(false)
const selectedMember = ref<FamilyMember | null>(null)
const showKeyboardHelp = ref(false)

// 缩放和平移
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)

// 拖拽状态
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const panStart = ref({ x: 0, y: 0 })

// 鼠标事件处理
const handleMouseDown = (event: MouseEvent) => {
  if (event.button === 0) { // 左键
    isDragging.value = true
    dragStart.value = { x: event.clientX, y: event.clientY }
    panStart.value = { x: panX.value, y: panY.value }
    event.preventDefault()
  }
}

const handleMouseMove = (event: MouseEvent) => {
  if (isDragging.value) {
    const deltaX = event.clientX - dragStart.value.x
    const deltaY = event.clientY - dragStart.value.y
    panX.value = panStart.value.x + deltaX
    panY.value = panStart.value.y + deltaY
  }
}

const handleMouseUp = () => {
  isDragging.value = false
}

// 触发布局重算的计数器
const layoutTick = ref(0)

// 统一的位置计算函数（优先从DOM测量，退化到估算）
const calculateMemberPositions = () => {
  const memberPositions = new Map<string, { x: number; y: number; width: number; height: number }>()
  
  // 优先根据真实DOM节点测量（以 .graph-content / SVG 同一坐标系为基准）
  if (graphContainer.value) {
    const baseEl = linesSvg.value?.parentElement || graphContainer.value.querySelector('.graph-content') || graphContainer.value
    const containerRect = (baseEl as HTMLElement).getBoundingClientRect()
    const nodeEls = baseEl.querySelectorAll<HTMLElement>('.family-node[data-member-id]')
    nodeEls.forEach((el) => {
      const id = el.dataset.memberId
      if (!id) return
      const rect = el.getBoundingClientRect()
      memberPositions.set(id, {
        x: rect.left - containerRect.left,
        y: rect.top - containerRect.top,
        width: rect.width,
        height: rect.height
      })
    })
  }
  
  // 如果DOM还未渲染到位，退化到基于分组的估算，避免空白
  if (memberPositions.size === 0) {
    generationGroups.value.forEach((generation, genIndex) => {
      const generationY = genIndex * 200 + 100
      let groupX = 100
      generation.groups.forEach(group => {
        if (group.type === 'couple' && group.members) {
          group.members.forEach((member, memberIndex) => {
            memberPositions.set(member.id, {
              x: groupX + memberIndex * 180,
              y: generationY,
              width: 160,
              height: 120
            })
          })
          groupX += 360
        } else if (group.type === 'single' && group.member) {
          memberPositions.set(group.member.id, {
            x: groupX,
            y: generationY,
            width: 160,
            height: 120
          })
          groupX += 180
        }
      })
    })
  }
  
  return memberPositions
}

// 计算属性
const generationGroups = computed(() => {
  if (!props.members || props.members.length === 0) return []

  const membersByGeneration = new Map<number, FamilyMember[]>()
  props.members.forEach(member => {
    const gen = member.generation || 1
    if (!membersByGeneration.has(gen)) membersByGeneration.set(gen, [])
    membersByGeneration.get(gen)!.push(member)
  })

  const levels = Array.from(membersByGeneration.keys()).sort((a, b) => a - b)
  const generations: Array<{
    level: number
    groups: Array<{ id: string; type: 'couple' | 'single'; members?: FamilyMember[]; member?: FamilyMember }>
  }> = []

  levels.forEach(level => {
    const members = membersByGeneration.get(level) || []
    const processed = new Set<string>()
    const prevGroups = generations.length > 0 ? generations[generations.length - 1].groups : []

    const findPrevIndex = (parentId?: string | null): number => {
      if (!parentId) return Number.POSITIVE_INFINITY
      for (let i = 0; i < prevGroups.length; i++) {
        const g = prevGroups[i]
        if (g.type === 'couple' && g.members && g.members.find(m => m.id === parentId)) return i
        if (g.type === 'single' && g.member && g.member.id === parentId) return i
      }
      return Number.POSITIVE_INFINITY
    }

    const clusters = new Map<number, Array<{ id: string; type: 'couple' | 'single'; members?: FamilyMember[]; member?: FamilyMember }>>()

    members.forEach(member => {
      if (processed.has(member.id)) return
      if (member.spouseId) {
        const spouse = members.find(m => m.id === member.spouseId)
        if (spouse && !processed.has(spouse.id)) {
          const idx = Math.min(findPrevIndex(member.parentId || null), findPrevIndex(spouse.parentId || null))
          const arr = clusters.get(idx) || []
          arr.push({ id: `couple-${member.id}-${spouse.id}`, type: 'couple', members: [member, spouse] })
          clusters.set(idx, arr)
          processed.add(member.id)
          processed.add(spouse.id)
        }
      }
    })

    members.forEach(member => {
      if (!processed.has(member.id)) {
        const idx = findPrevIndex(member.parentId || null)
        const arr = clusters.get(idx) || []
        arr.push({ id: `single-${member.id}`, type: 'single', member })
        clusters.set(idx, arr)
        processed.add(member.id)
      }
    })

    const orderedKeys = Array.from(clusters.keys()).sort((a, b) => a - b)
    const groups: Array<{ id: string; type: 'couple' | 'single'; members?: FamilyMember[]; member?: FamilyMember }> = []
    orderedKeys.forEach(k => {
      const arr = clusters.get(k) || []
      arr.forEach(g => groups.push(g))
    })

    generations.push({ level, groups })
  })

  return generations
})

// 常量定义
const nodeSpacingX = 200
const nodeSpacingY = 150
const containerWidth = ref(800)

const positionedMembers = computed(() => {
  if (!props.members.length) return []
  
  // 按世代分组
  const membersByGeneration = new Map<number, FamilyMember[]>()
  props.members.forEach(member => {
    const generation = member.generation || 1
    if (!membersByGeneration.has(generation)) {
      membersByGeneration.set(generation, [])
    }
    membersByGeneration.get(generation)!.push(member)
  })
  
  // 计算位置
  const positioned: Array<FamilyMember & { x: number; y: number }> = []
  
  membersByGeneration.forEach((members, generation) => {
    const generationY = (generation - 1) * nodeSpacingY + 50
    const totalWidth = members.length * nodeSpacingX
    const startX = (containerWidth.value - totalWidth) / 2
    
    members.forEach((member, index) => {
      positioned.push({
        ...member,
        x: startX + index * nodeSpacingX,
        y: generationY
      })
    })
  })
  
  return positioned
})

// 计算父子关系连线（品字形：父节点垂直向下到中线，再水平到子节点垂直下）
const parentChildLines = computed(() => {
  if (!props.showRelationships || !props.members.length) return []

  const lines: Array<{ id: string; v1?: string; h?: string; v2?: string; hc?: string }> = []
  const memberPositions = calculateMemberPositions()
  const byId = new Map<string, FamilyMember>()
  props.members.forEach(m => byId.set(m.id, m))

  const coupleCenterByMember = new Map<string, { cx: number; cy: number }>()
  const parentGroupIndexByMember = new Map<string, number>()
  generationGroups.value.forEach(gen => {
    gen.groups.forEach((g, idx) => {
      if (g.type === 'couple' && g.members && g.members.length === 2) {
        const p1 = memberPositions.get(g.members[0].id)
        const p2 = memberPositions.get(g.members[1].id)
        if (p1 && p2) {
          const cx = (p1.x + p1.width / 2 + p2.x + p2.width / 2) / 2
          const cy = Math.max(p1.y + p1.height, p2.y + p2.height)
          coupleCenterByMember.set(g.members[0].id, { cx, cy })
          coupleCenterByMember.set(g.members[1].id, { cx, cy })
        }
        parentGroupIndexByMember.set(g.members[0].id, idx)
        parentGroupIndexByMember.set(g.members[1].id, idx)
      }
      if (g.type === 'single' && g.member) {
        parentGroupIndexByMember.set(g.member.id, idx)
      }
    })
  })

  const childrenByParent = new Map<string, FamilyMember[]>()
  props.members.forEach(child => {
    if (!child.parentId) return
    const parent = byId.get(child.parentId)
    if (!parent) return
    if ((parent.generation || 1) !== (child.generation || 1) - 1) return
    const arr = childrenByParent.get(child.parentId) || []
    arr.push(child)
    childrenByParent.set(child.parentId, arr)
  })

  childrenByParent.forEach((children, parentId) => {
    const parentPos = memberPositions.get(parentId)
    if (!parentPos) return
    const coupleCenter = coupleCenterByMember.get(parentId)
    const startX = coupleCenter ? coupleCenter.cx : parentPos.x + parentPos.width / 2
    const startY = coupleCenter ? coupleCenter.cy : parentPos.y + parentPos.height

    const childCenters = children
      .map(c => ({ c, pos: memberPositions.get(c.id) }))
      .filter(({ pos }) => !!pos) as Array<{ c: FamilyMember; pos: { x: number; y: number; width: number; height: number } }>
    if (!childCenters.length) return

    const endYs = childCenters.map(({ pos }) => pos.y)
    const avgEndY = endYs.reduce((a, b) => a + b, 0) / endYs.length
    const verticalStep = Math.min(80, Math.max(32, (avgEndY - startY) * 0.5))
    const groupIdx = parentGroupIndexByMember.get(parentId) ?? 0
    const yOffset = (groupIdx % 3 - 1) * 8
    const midY = startY + Math.max(32, verticalStep) + yOffset

    const minX = Math.min(...childCenters.map(({ pos }) => pos.x + pos.width / 2))
    const maxX = Math.max(...childCenters.map(({ pos }) => pos.x + pos.width / 2))

    const v1 = `M ${startX} ${startY} L ${startX} ${midY}`
    const h = `M ${minX} ${midY} L ${maxX} ${midY}`
    let hc: string | undefined
    if (startX < minX) {
      hc = `M ${startX} ${midY} L ${minX} ${midY}`
    } else if (startX > maxX) {
      hc = `M ${maxX} ${midY} L ${startX} ${midY}`
    }
    lines.push({ id: `parentbus-${parentId}`, v1 })
    lines.push({ id: `bus-${parentId}`, h, hc })

    childCenters.forEach(({ c, pos }) => {
      const cx = pos.x + pos.width / 2
      const v2 = `M ${cx} ${midY} L ${cx} ${pos.y}`
      lines.push({ id: `stub-${parentId}-${c.id}`, v2 })
    })
  })

  return lines
})

 

// 方法
const getInitial = (name: string) => {
  return name.charAt(0)
}

const formatDateRange = (birthDate?: string | null, deathDate?: string | null) => {
  const birth = birthDate ? new Date(birthDate).getFullYear() : '?'
  const death = deathDate ? new Date(deathDate).getFullYear() : ''
  return death ? `${birth}-${death}` : `${birth}-`
}

const handleMemberClick = (member: FamilyMember) => {
  selectedMember.value = member
  emit('memberClick', member)
}

const handleMemberEdit = (member: FamilyMember) => {
  emit('memberEdit', member)
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()
  
  // 检查是否按住Ctrl键，如果是则进行缩放
  if (event.ctrlKey || event.metaKey) {
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.3, Math.min(2, zoomLevel.value * delta))
    
    // 计算缩放中心点
    if (graphContainer.value) {
      const rect = graphContainer.value.getBoundingClientRect()
      const centerX = event.clientX - rect.left - rect.width / 2
      const centerY = event.clientY - rect.top - rect.height / 2
      
      // 调整平移以保持缩放中心
      const scaleFactor = newZoom / zoomLevel.value
      panX.value = panX.value * scaleFactor - centerX * (scaleFactor - 1)
      panY.value = panY.value * scaleFactor - centerY * (scaleFactor - 1)
    }
    
    zoomLevel.value = newZoom
  } else {
    // 普通滚轮滚动
    const scrollSpeed = 30
    panY.value += event.deltaY > 0 ? -scrollSpeed : scrollSpeed
  }
}

const centerGraph = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

const fitToScreen = () => {
  zoomLevel.value = 0.8
  panX.value = 0
  panY.value = 0
}

const toggleKeyboardHelp = () => {
  showKeyboardHelp.value = !showKeyboardHelp.value
}

// 键盘事件处理
const handleKeyDown = (event: KeyboardEvent) => {
  // 防止在输入框中触发快捷键
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return
  }
  
  switch (event.key) {
    case '+':
    case '=':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        zoomLevel.value = Math.min(3, zoomLevel.value + 0.1)
      }
      break
    case '-':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        zoomLevel.value = Math.max(0.1, zoomLevel.value - 0.1)
      }
      break
    case '0':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        zoomLevel.value = 1
      }
      break
    case 'c':
    case 'C':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        centerGraph()
      }
      break
    case 'f':
    case 'F':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        fitToScreen()
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      panY.value += 50
      break
    case 'ArrowDown':
      event.preventDefault()
      panY.value -= 50
      break
    case 'ArrowLeft':
      event.preventDefault()
      panX.value += 50
      break
    case 'ArrowRight':
      event.preventDefault()
      panX.value -= 50
      break
    case '?':
      event.preventDefault()
      toggleKeyboardHelp()
      break
  }
}

// 生命周期
onMounted(() => {
  // 添加全局鼠标事件监听器
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  // 添加键盘事件监听器
  document.addEventListener('keydown', handleKeyDown)
  // 监听容器尺寸与滚动，触发布局重算
  const resizeObserver = new ResizeObserver(() => {
    layoutTick.value++
  })
  if (graphContainer.value) {
    resizeObserver.observe(graphContainer.value)
  }
  const mutationObserver = new MutationObserver(() => {
    layoutTick.value++
  })
  if (graphContainer.value) {
    mutationObserver.observe(graphContainer.value, { childList: true, subtree: true, attributes: true })
    graphContainer.value.addEventListener('scroll', () => { layoutTick.value++ })
  }
  const onWindowResize = () => { layoutTick.value++ }
  window.addEventListener('resize', onWindowResize)
  ;(window as any)._fg_onResize = onWindowResize
  // 初次渲染后
  nextTick(() => { layoutTick.value++ })
})

onUnmounted(() => {
  // 移除全局鼠标事件监听器
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  // 移除键盘事件监听器
  document.removeEventListener('keydown', handleKeyDown)
  const fn = (window as any)._fg_onResize
  if (fn) {
    window.removeEventListener('resize', fn)
    ;(window as any)._fg_onResize = null
  }
})

// 当数据或布局tick变化时，强制依赖重新计算
watch([() => props.members, layoutTick, zoomLevel, panX, panY], async () => {
  await nextTick()
  // 访问一次以建立依赖关系
  void calculateMemberPositions()
}, { deep: true })

// 暴露方法
defineExpose({
  centerGraph,
  fitToScreen
})
</script>

<style scoped>
.family-graph-component {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  overflow: hidden;
  padding: 40px;
  cursor: grab;
  user-select: none;
}

.graph-container:active {
  cursor: grabbing;
}

.graph-content {
  min-width: 100%;
  min-height: 100%;
  position: relative;
  transform-origin: center center;
}

/* 世代容器 */
.generation {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 var(--spacing-xl);
  position: relative;
  min-height: 120px;
  margin-bottom: 60px;
}

.generation-label {
  position: sticky;
  top: var(--spacing-md);
  background: linear-gradient(135deg, #1e40af, #3730a3);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  box-shadow: 0 6px 20px rgba(30, 64, 175, 0.4);
  z-index: 100;
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(12px);
  letter-spacing: 0.8px;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  min-width: 80px;
}

/* 节点组 */
.node-group {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: max-content;
  gap: var(--spacing-lg);
  justify-content: center;
  align-items: start;
  margin: var(--spacing-md) 0;
  position: relative;
  padding: var(--spacing-xs);
}

/* 夫妻组 */
.couple-group {
  display: grid;
  grid-template-columns: repeat(2, max-content);
  justify-content: center;
  align-items: center;
  gap: 12px;
  position: relative;
  margin: 0 var(--spacing-lg);
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.04), rgba(59, 130, 246, 0.04));
  border: 1px solid rgba(236, 72, 153, 0.15);
  border-radius: var(--radius-xl);
  padding: 8px;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.08);
  align-self: auto;
}

.couple-group::after {
  content: '♥';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgba(236, 72, 153, 0.6);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 3px 5px;
  border-radius: 50%;
  z-index: 10;
  box-shadow: 0 2px 6px rgba(236, 72, 153, 0.15);
  border: 1px solid rgba(236, 72, 153, 0.3);
}

/* 族谱节点 */
.family-node {
  background: white;
  border: 3px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  text-align: center;
  cursor: pointer;
  transition: all var(--duration-normal) ease;
  position: relative;
  min-width: 160px;
  color: var(--text-primary);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  align-self: auto;
  overflow: hidden;
}

.family-node:hover {
  /* 保持位置不变，避免与连线脱离，仅增强阴影与边框 */
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.family-node.male {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #ffffff, #eff6ff);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15);
}

.family-node.male:hover {
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.25);
  border-color: #2563eb;
}

.family-node.female {
  border-color: #ec4899;
  background: linear-gradient(135deg, #ffffff, #fdf2f8);
  box-shadow: 0 6px 20px rgba(236, 72, 153, 0.15);
}

.family-node.female:hover {
  box-shadow: 0 12px 32px rgba(236, 72, 153, 0.25);
  border-color: #db2777;
}

.family-node.selected {
  background: var(--primary-bg);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-lg);
}

/* 节点头像 */
.node-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.8);
  margin-bottom: var(--spacing-xs);
  transition: all var(--transition-fast) ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: var(--surface);
  margin: 16px auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  color: #64748b;
  overflow: hidden;
}

.node-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.family-node:hover .node-avatar {
  transform: scale(1.08);
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

/* 节点信息 */
.node-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 auto var(--spacing-xs);
  text-align: center;
  line-height: 1.4;
  width: 100%;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-xs);
}

.node-dates {
  font-size: 10px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.2;
  margin-bottom: var(--spacing-xs);
  opacity: 0.8;
}

.node-generation {
  position: absolute;
  top: -6px;
  right: -6px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  font-size: 9px;
  font-weight: 600;
  padding: 2px 5px;
  border-radius: var(--radius-full);
  min-width: 18px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 5;
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
  z-index: 10;
}

.loading-spinner {
  text-align: center;
}

.spinner {
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
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
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
}

/* 状态指示器 */
.status-indicator {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
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
  z-index: 20;
  min-width: 200px;
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
  z-index: 15;
  transition: all 0.2s ease;
}

.help-toggle:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

/* 关系连接线 */
.connection-line {
  position: absolute;
  background: var(--border);
  transition: opacity var(--transition-normal) ease;
  z-index: 1;
}

.connection-line.parent-child {
  background: linear-gradient(90deg, var(--primary), var(--primary-light));
  height: 2px;
}

.connection-line.spouse {
  background: linear-gradient(90deg, var(--accent), var(--accent-light));
  height: 2px;
}

.connection-line.sibling {
  background: linear-gradient(90deg, var(--text-secondary), var(--text-muted));
  height: 1px;
}

/* 关系线显示状态 */
.family-tree.show-relationships .connection-line {
  opacity: 1;
}

.family-tree:not(.show-relationships) .connection-line {
  opacity: 0;
}

/* SVG 关系连线样式 */
.relationship-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  transition: opacity var(--transition-normal) ease;
}

.relationship-lines.show {
  opacity: 1;
}

.relationship-lines.hide {
  opacity: 0;
}


/* 交错更友好的线条样式：圆角+halo */
.line-halo {
  stroke: #ffffff;
  stroke-width: 6;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.9;
}

.parent-child-halo { stroke: rgba(255,255,255,0.95); }
.spouse-halo { stroke: rgba(255,255,255,0.9); }

.parent-child-line {
  stroke: #3b82f6;
  stroke-width: 3;
  fill: none;
  stroke-dasharray: none;
  transition: all var(--transition-normal) ease;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* 让横向段在视觉上“跨过”竖线：略增线宽与微升不透明度 */
.pc-horz-line { stroke-width: 3.25; opacity: 1; }
.pc-vert-line { stroke-width: 3; opacity: 0.98; }

.spouse-line {
  stroke: #ec4899;
  stroke-width: 2.5;
  fill: none;
  stroke-dasharray: 8,4;
  transition: all var(--transition-normal) ease;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.parent-child-line:hover { stroke-width: 4; }

.spouse-line:hover { stroke-width: 3.2; }

/* 响应式设计 */
@media (max-width: 768px) {
  .family-node {
    min-width: 120px;
    padding: var(--spacing-sm);
  }
  
  .node-avatar {
    width: 36px;
    height: 36px;
  }
  
  .node-name {
    font-size: 12px;
    max-width: 70px;
  }
  
  .node-dates {
    font-size: 9px;
  }
  
  .node-generation {
    font-size: 8px;
    padding: 1px 4px;
    min-width: 16px;
  }
  
  .generation-label {
    font-size: 11px;
    padding: var(--spacing-xs) var(--spacing-sm);
  }
  
  .node-group {
    gap: var(--spacing-md);
  }
  
  .couple-group {
    gap: var(--spacing-sm);
    padding: var(--spacing-xs);
  }
}

@media (max-width: 480px) {
  .family-node {
    min-width: 100px;
    padding: var(--spacing-xs);
  }
  
  .node-avatar {
    width: 32px;
    height: 32px;
  }
  
  .node-name {
    font-size: 11px;
    max-width: 60px;
  }
  
  .node-dates {
    font-size: 8px;
  }
  
  .generation-container {
    margin: 0 var(--spacing-md);
  }
}
</style>
