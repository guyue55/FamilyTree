import { RenderType } from './FamilyGraphEngine'
import type { 
  FamilyMember, 
  Size, 
  Viewport, 
  LayoutResult, 
  FamilyGraphConfig,
  NodeEvent,
  EdgeEvent
} from './FamilyGraphEngine'

// 渲染器接口
export interface GraphRenderer {
  initialize(width: number, height: number): Promise<void>
  updateLayout(layoutResult: LayoutResult): void
  updateViewport(viewport: Viewport): void
  updateSelection(selectedIds: Set<string>): void
  updateRelationshipSelection(selectedIds: Set<string>): void
  render(scene: GraphScene): void
  exportAsImage(format: 'png' | 'jpeg' | 'svg'): string
  getCanvas(): HTMLElement
  destroy(): void
  on(event: string, listener: Function): void
}

// 渲染场景
export interface GraphScene {
  members: FamilyMember[]
  selectedMembers: Set<string>
  selectedRelationships: Set<string>
  layoutResult: LayoutResult
  viewport: Viewport
  config: FamilyGraphConfig
}

// SVG渲染器实现
export class SVGRenderer implements GraphRenderer {
  private container: HTMLElement
  private svgElement!: SVGSVGElement
  private defsElement!: SVGDefsElement
  private viewportGroup!: SVGGElement
  private contentGroup!: SVGGElement
  private relationshipGroup!: SVGGElement
  private nodeGroup!: SVGGElement
  
  private width = 0
  private height = 0
  private currentLayout: LayoutResult | null = null
  private eventListeners = new Map<string, Function[]>()
  
  constructor(container: HTMLElement) {
    this.container = container
  }
  
  async initialize(width: number, height: number): Promise<void> {
    this.width = width
    this.height = height
    
    // 创建SVG元素
    this.svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    this.svgElement.setAttribute('width', width.toString())
    this.svgElement.setAttribute('height', height.toString())
    this.svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`)
    this.svgElement.style.width = '100%'
    this.svgElement.style.height = '100%'
    // cursor handled by container/interaction manager
    
    // 创建定义元素
    this.defsElement = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    this.svgElement.appendChild(this.defsElement)
    
    // 创建滤镜和渐变
    this.createFiltersAndGradients()
    
    // 创建视口组（用于缩放和平移）
    this.viewportGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    this.viewportGroup.setAttribute('class', 'viewport')
    this.svgElement.appendChild(this.viewportGroup)
    
    // 创建内容组
    this.contentGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    this.contentGroup.setAttribute('class', 'content')
    this.viewportGroup.appendChild(this.contentGroup)
    
    // 创建关系组
    this.relationshipGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    this.relationshipGroup.setAttribute('class', 'relationships')
    this.contentGroup.appendChild(this.relationshipGroup)
    
    // 创建节点组
    this.nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    this.nodeGroup.setAttribute('class', 'nodes')
    this.contentGroup.appendChild(this.nodeGroup)
    
    // 添加到容器
    this.container.appendChild(this.svgElement)
  }
  
  private createFiltersAndGradients(): void {
    // 阴影滤镜
    const shadowFilter = document.createElementNS('http://www.w3.org/2000/svg', 'filter')
    shadowFilter.setAttribute('id', 'node-shadow')
    shadowFilter.setAttribute('x', '-50%')
    shadowFilter.setAttribute('y', '-50%')
    shadowFilter.setAttribute('width', '200%')
    shadowFilter.setAttribute('height', '200%')
    
    const blur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur')
    blur.setAttribute('in', 'SourceAlpha')
    blur.setAttribute('stdDeviation', '3')
    
    const offset = document.createElementNS('http://www.w3.org/2000/svg', 'feOffset')
    offset.setAttribute('dx', '0')
    offset.setAttribute('dy', '2')
    offset.setAttribute('result', 'offsetblur')
    
    const merge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge')
    const mergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode')
    const mergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode')
    mergeNode2.setAttribute('in', 'SourceGraphic')
    
    merge.appendChild(mergeNode1)
    merge.appendChild(mergeNode2)
    shadowFilter.appendChild(blur)
    shadowFilter.appendChild(offset)
    shadowFilter.appendChild(merge)
    
    this.defsElement.appendChild(shadowFilter)
    
    // 男性渐变
    const maleGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient')
    maleGradient.setAttribute('id', 'male-gradient')
    maleGradient.setAttribute('x1', '0%')
    maleGradient.setAttribute('y1', '0%')
    maleGradient.setAttribute('x2', '100%')
    maleGradient.setAttribute('y2', '100%')
    
    const maleStop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop')
    maleStop1.setAttribute('offset', '0%')
    maleStop1.setAttribute('stop-color', '#ffffff')
    
    const maleStop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop')
    maleStop2.setAttribute('offset', '100%')
    maleStop2.setAttribute('stop-color', '#dbeafe')
    
    maleGradient.appendChild(maleStop1)
    maleGradient.appendChild(maleStop2)
    this.defsElement.appendChild(maleGradient)
    
    // 女性渐变
    const femaleGradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient')
    femaleGradient.setAttribute('id', 'female-gradient')
    femaleGradient.setAttribute('x1', '0%')
    femaleGradient.setAttribute('y1', '0%')
    femaleGradient.setAttribute('x2', '100%')
    femaleGradient.setAttribute('y2', '100%')
    
    const femaleStop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop')
    femaleStop1.setAttribute('offset', '0%')
    femaleStop1.setAttribute('stop-color', '#ffffff')
    
    const femaleStop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop')
    femaleStop2.setAttribute('offset', '100%')
    femaleStop2.setAttribute('stop-color', '#fdf2f8')
    
    femaleGradient.appendChild(femaleStop1)
    femaleGradient.appendChild(femaleStop2)
    this.defsElement.appendChild(femaleGradient)
  }
  
  updateLayout(layoutResult: LayoutResult): void {
    this.currentLayout = layoutResult
  }
  
  updateSelection(selectedIds: Set<string>): void {
    if (!this.nodeGroup) return

    const nodes = this.nodeGroup.querySelectorAll('.family-node')
    nodes.forEach(node => {
      const id = node.getAttribute('data-member-id')
      const rect = node.querySelector('rect')
      if (!id || !rect) return

      if (selectedIds.has(id)) {
        rect.setAttribute('stroke', '#f59e0b')
        rect.setAttribute('stroke-width', '3')
      } else {
        const isMale = node.classList.contains('male')
        rect.setAttribute('stroke', isMale ? '#3b82f6' : '#ec4899')
        rect.setAttribute('stroke-width', '2')
      }
    })
  }

  updateRelationshipSelection(selectedIds: Set<string>): void {
    if (!this.relationshipGroup) return

    const lines = this.relationshipGroup.querySelectorAll('.relationship-line')
    lines.forEach(line => {
      const id = line.getAttribute('data-id')
      if (!id) return

      if (selectedIds.has(id)) {
        line.setAttribute('stroke', '#f59e0b')
        line.setAttribute('stroke-width', '3')
        line.setAttribute('opacity', '1')
      } else {
        // 恢复默认样式
        const isSpouse = line.classList.contains('spouse')
        
        line.setAttribute('stroke', isSpouse ? '#f43f5e' : '#3b82f6')
        line.setAttribute('stroke-width', '2')
        line.setAttribute('opacity', isSpouse ? '0.8' : '0.6')
      }
    })
  }

  updateViewport(viewport: Viewport): void {
    // 更新视口变换
    const transform = `translate(${viewport.x}, ${viewport.y}) scale(${viewport.zoom})`
    this.viewportGroup.setAttribute('transform', transform)
  }
  
  render(scene: GraphScene): void {
    if (!this.currentLayout) return
    
    // 清空现有内容
    this.clearGroups()
    
    // 渲染关系连线
    if (scene.config.showRelationships) {
      this.renderRelationships(scene)
    }
    
    // 渲染节点
    this.renderNodes(scene)
  }
  
  private clearGroups(): void {
    this.relationshipGroup.innerHTML = ''
    this.nodeGroup.innerHTML = ''
  }
  
  private renderRelationships(_scene: GraphScene): void {
    const { relationships } = this.currentLayout!
    
    relationships.forEach(relationship => {
      const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      pathElement.setAttribute('d', relationship.path || '')
      pathElement.setAttribute('class', `relationship-line ${relationship.type}`)
      pathElement.setAttribute('data-id', relationship.id) // 添加ID用于选择
      pathElement.setAttribute('stroke', relationship.style?.stroke || '#3b82f6')
      pathElement.setAttribute('stroke-width', (relationship.style?.strokeWidth || 2).toString())
      pathElement.setAttribute('fill', 'none')
      pathElement.setAttribute('opacity', (relationship.style?.opacity || 0.6).toString())
      
      if (relationship.style?.strokeDasharray) {
        pathElement.setAttribute('stroke-dasharray', relationship.style.strokeDasharray)
      }
      
      // 添加点击事件
      pathElement.addEventListener('click', (_e) => {
        this.emit('edgeClick', {
          type: 'edgeClick',
          target: pathElement,
          edge: relationship
        } as EdgeEvent)
      })
      
      this.relationshipGroup.appendChild(pathElement)
    })
  }
  
  private renderNodes(scene: GraphScene): void {
    const { members, selectedMembers, config } = scene
    const { positions } = this.currentLayout!
    
    members.forEach(member => {
      const position = positions.get(member.id)
      if (!position || !position.visible) return
      
      const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
      nodeGroup.setAttribute('class', `family-node ${member.gender}`)
      nodeGroup.setAttribute('data-member-id', member.id)
      nodeGroup.setAttribute('transform', `translate(${position.x}, ${position.y})`)
      
      // 节点背景
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('width', position.size.width.toString())
      rect.setAttribute('height', position.size.height.toString())
      rect.setAttribute('rx', '12')
      rect.setAttribute('ry', '12')
      rect.setAttribute('fill', `url(#${member.gender}-gradient)`)
      rect.setAttribute('stroke', member.gender === 'male' ? '#3b82f6' : '#ec4899')
      rect.setAttribute('stroke-width', '2')
      rect.setAttribute('filter', 'url(#node-shadow)')
      
      // 选中状态
      if (selectedMembers.has(member.id)) {
        rect.setAttribute('stroke', '#f59e0b')
        rect.setAttribute('stroke-width', '3')
      }
      
      nodeGroup.appendChild(rect)
      
      // 头像区域
      if (config.showPhotos) {
        this.renderAvatar(nodeGroup, member, position.size)
      }
      
      // 姓名文本
      const nameText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      nameText.setAttribute('x', (position.size.width / 2).toString())
      // 调整垂直位置，避免与头像过于贴合
      nameText.setAttribute('y', '75')
      nameText.setAttribute('text-anchor', 'middle')
      nameText.setAttribute('font-size', '14')
      nameText.setAttribute('font-weight', '600')
      nameText.setAttribute('fill', '#1f2937')
      nameText.textContent = member.name
      
      nodeGroup.appendChild(nameText)
      
      // 日期信息
      if (config.showDates && (member.birthDate || member.deathDate)) {
        const dateText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        dateText.setAttribute('x', (position.size.width / 2).toString())
        // 调整日期位置，增加间距
        dateText.setAttribute('y', '95')
        dateText.setAttribute('text-anchor', 'middle')
        dateText.setAttribute('font-size', '12')
        dateText.setAttribute('fill', '#6b7280')
        dateText.textContent = this.formatDateRange(member.birthDate, member.deathDate)
        
        nodeGroup.appendChild(dateText)
      }
      
      // 世代标签
      if (config.showGeneration) {
        const genCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
        genCircle.setAttribute('cx', (position.size.width - 10).toString())
        genCircle.setAttribute('cy', '10')
        genCircle.setAttribute('r', '8')
        genCircle.setAttribute('fill', '#3b82f6')
        genCircle.setAttribute('stroke', 'white')
        genCircle.setAttribute('stroke-width', '2')
        
        const genText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        genText.setAttribute('x', (position.size.width - 10).toString())
        genText.setAttribute('y', '14')
        genText.setAttribute('text-anchor', 'middle')
        genText.setAttribute('font-size', '8')
        genText.setAttribute('font-weight', '600')
        genText.setAttribute('fill', 'white')
        genText.textContent = member.generation.toString()
        
        nodeGroup.appendChild(genCircle)
        nodeGroup.appendChild(genText)
      }
      
      // 事件监听
      nodeGroup.addEventListener('click', (e) => {
        e.stopPropagation()
        this.emit('nodeClick', {
          type: 'nodeClick',
          target: nodeGroup,
          node: member,
          position: { x: position.x, y: position.y },
          data: { multiSelect: e.ctrlKey || e.metaKey }
        } as NodeEvent)
      })
      
      nodeGroup.addEventListener('dblclick', (e) => {
        e.stopPropagation()
        this.emit('nodeDoubleClick', {
          type: 'nodeDoubleClick',
          target: nodeGroup,
          node: member,
          position: { x: position.x, y: position.y }
        } as NodeEvent)
      })
      
      this.nodeGroup.appendChild(nodeGroup)
    })
  }
  
  private renderAvatar(parent: SVGGElement, member: FamilyMember, nodeSize: Size): void {
    const avatarSize = 32
    const avatarX = (nodeSize.width - avatarSize) / 2
    const avatarY = 20
    
    const avatarGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g')
    
    // 头像背景圆
    const avatarBg = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    avatarBg.setAttribute('cx', (avatarX + avatarSize / 2).toString())
    avatarBg.setAttribute('cy', (avatarY + avatarSize / 2).toString())
    avatarBg.setAttribute('r', (avatarSize / 2).toString())
    avatarBg.setAttribute('fill', '#f3f4f6')
    avatarBg.setAttribute('stroke', 'white')
    avatarBg.setAttribute('stroke-width', '2')
    
    avatarGroup.appendChild(avatarBg)
    
    // 头像文字（如果没有图片）
    const avatarText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    avatarText.setAttribute('x', (avatarX + avatarSize / 2).toString())
    avatarText.setAttribute('y', (avatarY + avatarSize / 2 + 5).toString())
    avatarText.setAttribute('text-anchor', 'middle')
    avatarText.setAttribute('font-size', '16')
    avatarText.setAttribute('font-weight', '600')
    avatarText.setAttribute('fill', '#6b7280')
    avatarText.textContent = member.name.charAt(0)
    
    avatarGroup.appendChild(avatarText)
    
    parent.appendChild(avatarGroup)
  }
  
  private formatDateRange(birthDate?: string | null, deathDate?: string | null): string {
    const birth = birthDate ? new Date(birthDate).getFullYear() : '?'
    const death = deathDate ? new Date(deathDate).getFullYear() : ''
    return death ? `${birth}-${death}` : `${birth}-`
  }
  
  exportAsImage(format: 'png' | 'jpeg' | 'svg' = 'png'): string {
    if (format === 'svg') {
      const serializer = new XMLSerializer()
      return serializer.serializeToString(this.svgElement)
    }
    
    // 对于PNG/JPEG，需要转换为canvas
    const canvas = document.createElement('canvas')
    canvas.width = this.width
    canvas.height = this.height
    const ctx = canvas.getContext('2d')!
    
    const img = new Image()
    const svgString = new XMLSerializer().serializeToString(this.svgElement)
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    
    return new Promise((resolve) => {
      img.onload = () => {
        ctx.drawImage(img, 0, 0)
        URL.revokeObjectURL(url)
        resolve(canvas.toDataURL(`image/${format}`))
      }
      img.src = url
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    }) as any
  }
  
  getCanvas(): HTMLElement {
     
    return this.svgElement as unknown as HTMLElement
  }
  
  destroy(): void {
    if (this.svgElement && this.svgElement.parentNode) {
      this.svgElement.parentNode.removeChild(this.svgElement)
    }
    this.eventListeners.clear()
  }
  
  on(event: string, listener: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(listener)
  }
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(listener => listener(data))
    }
  }
}

// 渲染器工厂
export function createGraphRenderer(container: HTMLElement, type: RenderType): GraphRenderer {
  switch (type) {
    case RenderType.SVG:
      return new SVGRenderer(container)
    case RenderType.CANVAS:
      // TODO: 实现Canvas渲染器
      throw new Error('Canvas renderer not implemented yet')
    case RenderType.WEBGL:
      // TODO: 实现WebGL渲染器
      throw new Error('WebGL renderer not implemented yet')
    default:
      return new SVGRenderer(container)
  }
}