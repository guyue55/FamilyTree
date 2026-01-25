import { createFamilyGraph, FamilyLayoutType } from './FamilyGraphEngine'
import type { NodeEvent, FamilyMember } from './FamilyGraphEngine'

// 示例数据
const sampleMembers = [
  // 第一代
  {
    id: '1',
    familyId: 1,
    name: '张德高',
    gender: 'male' as const,
    birthDate: '1350-01-01',
    deathDate: '1420-12-31',
    generation: 1,
    parentId: null,
    spouseId: '2'
  },
  {
    id: '2',
    familyId: 1,
    name: '李氏',
    gender: 'female' as const,
    birthDate: '1355-01-01',
    deathDate: '1425-12-31',
    generation: 1,
    parentId: null,
    spouseId: '1'
  },
  
  // 第二代
  {
    id: '3',
    familyId: 1,
    name: '张文华',
    gender: 'male' as const,
    birthDate: '1375-01-01',
    deathDate: '1448-12-31',
    generation: 2,
    parentId: '1',
    spouseId: '6'
  },
  {
    id: '6',
    familyId: 1,
    name: '王氏',
    gender: 'female' as const,
    birthDate: '1378-01-01',
    deathDate: '1450-12-31',
    generation: 2,
    parentId: null,
    spouseId: '3'
  },
  {
    id: '4',
    familyId: 1,
    name: '张文武',
    gender: 'male' as const,
    birthDate: '1378-01-01',
    deathDate: '1451-12-31',
    generation: 2,
    parentId: '1',
    spouseId: '7'
  },
  {
    id: '7',
    familyId: 1,
    name: '陈氏',
    gender: 'female' as const,
    birthDate: '1380-01-01',
    deathDate: '1453-12-31',
    generation: 2,
    parentId: null,
    spouseId: '4'
  },
  
  // 第三代
  {
    id: '8',
    familyId: 1,
    name: '张志远',
    gender: 'male' as const,
    birthDate: '1400-01-01',
    deathDate: '1475-12-31',
    generation: 3,
    parentId: '3',
    spouseId: '13'
  },
  {
    id: '13',
    familyId: 1,
    name: '刘氏',
    gender: 'female' as const,
    birthDate: '1402-01-01',
    deathDate: '1477-12-31',
    generation: 3,
    parentId: null,
    spouseId: '8'
  },
  {
    id: '9',
    familyId: 1,
    name: '张志明',
    gender: 'male' as const,
    birthDate: '1403-01-01',
    deathDate: '1478-12-31',
    generation: 3,
    parentId: '3',
    spouseId: '14'
  },
  {
    id: '14',
    familyId: 1,
    name: '赵氏',
    gender: 'female' as const,
    birthDate: '1405-01-01',
    deathDate: '1480-12-31',
    generation: 3,
    parentId: null,
    spouseId: '9'
  }
]

// 演示不同布局
async function demonstrateLayouts() {
  const container = document.getElementById('graph-container')
  if (!container) {
    console.error('Container not found')
    return
  }
  
  const layouts = [
    FamilyLayoutType.HIERARCHICAL,
    FamilyLayoutType.COMPACT,
    FamilyLayoutType.CIRCULAR,
    FamilyLayoutType.ORTHOGONAL,
    FamilyLayoutType.ORGANIC
  ]
  
  let currentLayoutIndex = 0
  
  async function showNextLayout() {
    const layoutType = layouts[currentLayoutIndex]
    
    // 清空容器
  if (container) {
    container.innerHTML = ''
  }

  // 创建新的图形引擎
  const graphEngine = createFamilyGraph({
    container: container!,
    width: 1200,
      height: 800,
      layout: layoutType,
      showRelationships: true,
      showPhotos: false,
      showDates: true,
      showGeneration: true,
      enableAnimation: true,
      enableVirtualization: true
    })
    
    try {
      await graphEngine.initialize()
      graphEngine.loadData(sampleMembers)
      graphEngine.fitToScreen()
      
      // 设置事件监听
      graphEngine.on('nodeClick', (event: NodeEvent) => {
        console.log('Node clicked:', event.node.name)
      })
      
      graphEngine.on('nodeDoubleClick', (event: NodeEvent) => {
        console.log('Node double clicked:', event.node.name)
      })
      
      // 显示当前布局类型
      console.log(`Current layout: ${layoutType}`)
      
      // 添加控制按钮
      addControlButtons(graphEngine, currentLayoutIndex)
      
    } catch (error) {
      console.error('Failed to initialize graph:', error)
    }
    
    currentLayoutIndex = (currentLayoutIndex + 1) % layouts.length
  }
  
  // 初始显示
  await showNextLayout()
  
  // 每5秒切换布局
  setInterval(showNextLayout, 5000)
}

function addControlButtons(graphEngine: ReturnType<typeof createFamilyGraph>, layoutIndex: number) {
  const existingControls = document.getElementById('graph-controls')
  if (existingControls) {
    existingControls.remove()
  }

  const controlsContainer = document.createElement('div')
  controlsContainer.id = 'graph-controls'
  controlsContainer.style.cssText = `
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    gap: 10px;
    z-index: 1000;
  `
  
  // 缩放控制
  const zoomInBtn = document.createElement('button')
  zoomInBtn.textContent = '放大'
  zoomInBtn.onclick = () => graphEngine.setViewport({ zoom: Math.min(3, graphEngine.getViewport().value.zoom + 0.1) })
  
  const zoomOutBtn = document.createElement('button')
  zoomOutBtn.textContent = '缩小'
  zoomOutBtn.onclick = () => graphEngine.setViewport({ zoom: Math.max(0.1, graphEngine.getViewport().value.zoom - 0.1) })
  
  const resetBtn = document.createElement('button')
  resetBtn.textContent = '重置'
  resetBtn.onclick = () => graphEngine.centerGraph()
  
  const fitBtn = document.createElement('button')
  fitBtn.textContent = '适应'
  fitBtn.onclick = () => graphEngine.fitToScreen()
  
  const exportBtn = document.createElement('button')
  exportBtn.textContent = '导出PNG'
  exportBtn.onclick = async () => {
    try {
      const dataURL = await graphEngine.exportAsImage('png')
      const link = document.createElement('a')
      link.href = dataURL
      link.download = `family-tree-${layoutIndex}.png`
      link.click()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }
  
  controlsContainer.appendChild(zoomInBtn)
  controlsContainer.appendChild(zoomOutBtn)
  controlsContainer.appendChild(resetBtn)
  controlsContainer.appendChild(fitBtn)
  controlsContainer.appendChild(exportBtn)
  
  document.body.appendChild(controlsContainer)
}

// 性能测试
async function performanceTest() {
  console.log('Starting performance test...')
  
  // 生成大量测试数据
  const largeDataset: FamilyMember[] = []
  let idCounter = 1
  
  // 创建5代，每代20人的大型族谱
  for (let gen = 1; gen <= 5; gen++) {
    for (let i = 0; i < 20; i++) {
      const memberId = (idCounter++).toString()
      const parentId = gen > 1 ? Math.floor((idCounter - 21) / 2).toString() : null
      const spouseId = i % 2 === 0 ? (idCounter).toString() : (idCounter - 1).toString()
      
      largeDataset.push({
        id: memberId,
        familyId: 1,
        name: `成员${memberId}`,
        gender: (Math.random() > 0.5 ? 'male' : 'female') as 'male' | 'female',
        birthDate: `${1300 + gen * 30}-01-01`,
        deathDate: Math.random() > 0.3 ? `${1380 + gen * 30}-12-31` : null,
        generation: gen,
        parentId,
        spouseId: i % 2 === 0 ? null : spouseId
      })
    }
  }
  
  const container = document.getElementById('performance-container')
  if (!container) return
  
  const startTime = performance.now()
  
  const graphEngine = createFamilyGraph({
    container,
    width: 1200,
    height: 800,
    layout: FamilyLayoutType.COMPACT,
    enableVirtualization: true,
    enableAnimation: false // 性能测试时关闭动画
  })
  
  await graphEngine.initialize()
  graphEngine.loadData(largeDataset)
  
  const endTime = performance.now()
  console.log(`Performance test completed: ${endTime - startTime}ms for ${largeDataset.length} nodes`)
  
  // 清理
  setTimeout(() => {
    graphEngine.destroy()
  }, 5000)
}

// 导出到全局作用域供演示使用
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(window as any).familyGraphDemo = {
  demonstrateLayouts,
  performanceTest,
  sampleMembers
}

console.log('Family Graph Demo loaded. Use familyGraphDemo.demonstrateLayouts() to start.')
console.log('Use familyGraphDemo.performanceTest() to run performance tests.')