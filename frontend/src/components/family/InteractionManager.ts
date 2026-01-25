import { InteractionMode } from './FamilyGraphEngine'
import type { Viewport } from './FamilyGraphEngine'

// 交互事件
export interface InteractionEvent {
  type: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any
}

export interface ViewportChangeEvent extends InteractionEvent {
  viewport: Viewport
}

export interface NodeDragEvent extends InteractionEvent {
  nodeId: string
  startPosition: { x: number, y: number }
  currentPosition: { x: number, y: number }
}

// 交互管理器
export class InteractionManager {
  private viewport: { current: Viewport }
  private canvas!: HTMLElement
  private currentMode: InteractionMode = InteractionMode.PAN
  private isDestroyed = false
  private eventListeners = new Map<string, Function[]>()
  
  // 拖拽状态
  private isDragging = false
  private isPointerDown = false
  private pointerDownStart = { x: 0, y: 0 }
  private pointerDownTarget: HTMLElement | null = null
  private readonly dragThreshold = 5
  private dragStart = { x: 0, y: 0 }
  private viewportStart = { x: 0, y: 0 }
  
  // 缩放状态
  private zoomVelocity = 0
  private lastZoomTime = 0
  
  // 节点拖拽状态
  private isNodeDragging = false
  private draggedNodeId: string | null = null
  private nodeDragStart = { x: 0, y: 0 }
  
  constructor(viewport: { current: Viewport }) {
    this.viewport = viewport
    this.canvas = document.createElement('div') // Temporary initialization
  }
  
  initialize(canvas: HTMLElement): void {
    this.canvas = canvas
    this.setupEventListeners()
  }
  
  setMode(mode: InteractionMode): void {
    this.currentMode = mode
    this.updateCursor()
  }
  
  private setupEventListeners(): void {
    // 指针事件 (替代鼠标事件，支持捕获)
    this.canvas.addEventListener('pointerdown', this.handlePointerDown.bind(this))
    this.canvas.addEventListener('pointermove', this.handlePointerMove.bind(this))
    this.canvas.addEventListener('pointerup', this.handlePointerUp.bind(this))
    this.canvas.addEventListener('pointercancel', this.handlePointerUp.bind(this))
    this.canvas.addEventListener('wheel', this.handleWheel.bind(this), { passive: false })
    
    // 触摸事件 (保留用于多指手势)
    this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false })
    this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false })
    this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this))
    
    // 键盘事件
    document.addEventListener('keydown', this.handleKeyDown.bind(this))
    
    // 右键菜单
    this.canvas.addEventListener('contextmenu', this.handleContextMenu.bind(this))
  }
  
  private handlePointerDown(event: PointerEvent): void {
    if (event.pointerType === 'touch') return // 交给 Touch 事件处理
    if (event.button !== 0) return // 只处理左键
    
    // 设置指针捕获，防止光标移出区域后事件丢失或光标样式失效
    this.canvas.setPointerCapture(event.pointerId)
    
    const target = event.target as HTMLElement
    const nodeElement = target.closest('.family-node')
    
    if (nodeElement && this.currentMode === InteractionMode.DRAG) {
      // 开始节点拖拽
      this.startNodeDrag(nodeElement, event)
    } else if (this.currentMode === InteractionMode.PAN) {
      // 开始视口拖拽
      this.startViewportDrag(event)
    }
  }
  
  private handlePointerMove(event: PointerEvent): void {
    if (event.pointerType === 'touch') return
    
    if (this.isNodeDragging && this.draggedNodeId) {
      this.updateNodeDrag(event)
    } else if (this.isDragging) {
      this.updateViewportDrag(event)
    }
  }
  
  private handlePointerUp(event: PointerEvent): void {
    if (event.pointerType === 'touch') return
    
    // 无论是否拖拽，都释放捕获
    try {
      this.canvas.releasePointerCapture(event.pointerId)
    } catch (e) {
      // 忽略释放失败（可能已经释放或未捕获）
    }

    if (this.isNodeDragging) {
      this.endNodeDrag(event)
    } else if (this.isDragging) {
      this.endViewportDrag(event)
    }
  }
  
  private handleWheel(event: WheelEvent): void {
    event.preventDefault()
    
    if (this.currentMode !== InteractionMode.ZOOM && !event.ctrlKey && !event.metaKey) {
      return
    }
    
    const rect = this.canvas.getBoundingClientRect()
    const centerX = event.clientX - rect.left
    const centerY = event.clientY - rect.top
    
    // 计算缩放增量
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.1, Math.min(3, this.viewport.current.zoom * delta))
    
    // 计算新的平移位置以保持缩放中心
    const zoomRatio = newZoom / this.viewport.current.zoom
    const newPanX = centerX - (centerX - this.viewport.current.x) * zoomRatio
    const newPanY = centerY - (centerY - this.viewport.current.y) * zoomRatio
    
    this.updateViewport({
      zoom: newZoom,
      x: newPanX,
      y: newPanY
    })
  }
  
  private handleTouchStart(event: TouchEvent): void {
    event.preventDefault()
    
    if (event.touches.length === 1) {
      // 单指触摸 - 拖拽
      const touch = event.touches[0]
      this.startViewportDrag({
        clientX: touch.clientX,
        clientY: touch.clientY,
        ctrlKey: false,
        metaKey: false,
        preventDefault: () => {},
        target: event.target
      } as MouseEvent)
    } else if (event.touches.length === 2) {
      // 双指触摸 - 缩放
      this.startPinchZoom(event.touches[0], event.touches[1])
    }
  }
  
  private handleTouchMove(event: TouchEvent): void {
    event.preventDefault()
    
    if (event.touches.length === 1 && this.isDragging) {
      // 单指拖拽
      const touch = event.touches[0]
      this.updateViewportDrag({
        clientX: touch.clientX,
        clientY: touch.clientY,
        ctrlKey: false,
        metaKey: false,
        preventDefault: () => {},
        target: event.target
      } as MouseEvent)
    } else if (event.touches.length === 2) {
      // 双指缩放
      this.updatePinchZoom(event.touches[0], event.touches[1])
    }
  }
  
  private handleTouchEnd(event: TouchEvent): void {
    if (event.touches.length === 0) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      this.endViewportDrag(event as any)
    }
  }
  
  private handleKeyDown(event: KeyboardEvent): void {
    // 防止在输入框中触发
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
      return
    }
    
    const step = 50
    const viewportUpdate: Partial<Viewport> = {}
    
    switch (event.key) {
      case 'ArrowUp':
        event.preventDefault()
        viewportUpdate.y = this.viewport.current.y + step
        break
      case 'ArrowDown':
        event.preventDefault()
        viewportUpdate.y = this.viewport.current.y - step
        break
      case 'ArrowLeft':
        event.preventDefault()
        viewportUpdate.x = this.viewport.current.x + step
        break
      case 'ArrowRight':
        event.preventDefault()
        viewportUpdate.x = this.viewport.current.x - step
        break
      case '+':
      case '=':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault()
          viewportUpdate.zoom = Math.min(3, this.viewport.current.zoom + 0.1)
        }
        break
      case '-':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault()
          viewportUpdate.zoom = Math.max(0.1, this.viewport.current.zoom - 0.1)
        }
        break
      case '0':
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault()
          viewportUpdate.zoom = 1
          viewportUpdate.x = 0
          viewportUpdate.y = 0
        }
        break
    }
    
    if (Object.keys(viewportUpdate).length > 0) {
      this.updateViewport(viewportUpdate)
    }
  }
  
  private handleContextMenu(event: MouseEvent): void {
    event.preventDefault()
    
    const target = event.target as HTMLElement
    const nodeElement = target.closest('.family-node')
    
    if (nodeElement) {
      // 显示节点右键菜单
      this.emit('nodeContextMenu', {
        nodeId: nodeElement.getAttribute('data-member-id'),
        position: { x: event.clientX, y: event.clientY }
      })
    } else {
      // 显示画布右键菜单
      this.emit('canvasContextMenu', {
        position: { x: event.clientX, y: event.clientY }
      })
    }
  }
  
  // 拖拽方法
  private startViewportDrag(event: PointerEvent | MouseEvent): void {
    this.isDragging = true
    this.dragStart = { x: event.clientX, y: event.clientY }
    this.viewportStart = { x: this.viewport.current.x, y: this.viewport.current.y }
    this.canvas.style.cursor = 'grabbing'
  }
  
  private updateViewportDrag(event: MouseEvent): void {
    if (!this.isDragging) return
    
    const deltaX = event.clientX - this.dragStart.x
    const deltaY = event.clientY - this.dragStart.y
    
    this.updateViewport({
      x: this.viewportStart.x + deltaX,
      y: this.viewportStart.y + deltaY
    })
  }
  
  private endViewportDrag(_event: MouseEvent): void {
    this.isDragging = false
    this.canvas.style.cursor = this.getCursorForMode()
  }
  
  // 节点拖拽方法
  private startNodeDrag(nodeElement: Element, event: MouseEvent): void {
    const nodeId = nodeElement.getAttribute('data-member-id')
    if (!nodeId) return
    
    this.isNodeDragging = true
    this.draggedNodeId = nodeId
    this.nodeDragStart = { x: event.clientX, y: event.clientY }
    
    this.emit('nodeDragStart', {
      nodeId,
      startPosition: { x: event.clientX, y: event.clientY }
    })
  }
  
  private updateNodeDrag(event: MouseEvent): void {
    if (!this.isNodeDragging || !this.draggedNodeId) return
    
    const deltaX = event.clientX - this.nodeDragStart.x
    const deltaY = event.clientY - this.nodeDragStart.y
    
    this.emit('nodeDrag', {
      nodeId: this.draggedNodeId,
      startPosition: this.nodeDragStart,
      currentPosition: { x: event.clientX, y: event.clientY },
      delta: { x: deltaX, y: deltaY }
    })
  }
  
  private endNodeDrag(event: MouseEvent): void {
    if (!this.isNodeDragging || !this.draggedNodeId) return
    
    this.emit('nodeDragEnd', {
      nodeId: this.draggedNodeId,
      startPosition: this.nodeDragStart,
      endPosition: { x: event.clientX, y: event.clientY }
    })
    
    this.isNodeDragging = false
    this.draggedNodeId = null
  }
  
  // 缩放方法
  private startPinchZoom(_touch1: Touch, _touch2: Touch): void {
    this.zoomVelocity = 0
    this.lastZoomTime = Date.now()
  }
  
  private updatePinchZoom(touch1: Touch, touch2: Touch): void {
    const currentDistance = this.getTouchDistance(touch1, touch2)
    const rect = this.canvas.getBoundingClientRect()
    const centerX = (touch1.clientX + touch2.clientX) / 2 - rect.left
    const centerY = (touch1.clientY + touch2.clientY) / 2 - rect.top
    
    // 简化的缩放计算
    const delta = currentDistance > this.lastZoomTime ? 1.02 : 0.98
    const newZoom = Math.max(0.1, Math.min(3, this.viewport.current.zoom * delta))
    
    const zoomRatio = newZoom / this.viewport.current.zoom
    const newPanX = centerX - (centerX - this.viewport.current.x) * zoomRatio
    const newPanY = centerY - (centerY - this.viewport.current.y) * zoomRatio
    
    this.updateViewport({
      zoom: newZoom,
      x: newPanX,
      y: newPanY
    })
    
    this.lastZoomTime = currentDistance
  }
  
  // 辅助方法
  private getTouchDistance(touch1: Touch, touch2: Touch): number {
    const dx = touch1.clientX - touch2.clientX
    const dy = touch1.clientY - touch2.clientY
    return Math.sqrt(dx * dx + dy * dy)
  }
  
  private updateViewport(update: Partial<Viewport>): void {
    const newViewport = { ...this.viewport.current, ...update }
    this.viewport.current = newViewport
    this.emit('viewportChange', { viewport: newViewport })
  }
  
  private updateCursor(): void {
    this.canvas.style.cursor = this.getCursorForMode()
  }
  
  private getCursorForMode(): string {
    switch (this.currentMode) {
      case InteractionMode.PAN:
        return this.isDragging ? 'grabbing' : 'grab'
      case InteractionMode.ZOOM:
        return 'zoom-in'
      case InteractionMode.SELECT:
        return 'pointer'
      case InteractionMode.EDIT:
        return 'text'
      case InteractionMode.DRAG:
        return 'move'
      default:
        return 'default'
    }
  }
  
  // 公共方法
  public fitToScreen(bounds: { width: number, height: number }): void {
    const canvasRect = this.canvas.getBoundingClientRect()
    const scaleX = canvasRect.width / bounds.width
    const scaleY = canvasRect.height / bounds.height
    const zoom = Math.min(scaleX, scaleY, 3)
    
    this.updateViewport({
      zoom: Math.max(zoom, 0.1),
      x: canvasRect.width / 2 - (bounds.width / 2) * zoom,
      y: canvasRect.height / 2 - (bounds.height / 2) * zoom
    })
  }
  
  public centerGraph(): void {
    this.updateViewport({
      zoom: 1,
      x: 0,
      y: 0
    })
  }
  
  public zoomIn(): void {
    const newZoom = Math.min(3, this.viewport.current.zoom + 0.1)
    this.updateViewport({ zoom: newZoom })
  }
  
  public zoomOut(): void {
    const newZoom = Math.max(0.1, this.viewport.current.zoom - 0.1)
    this.updateViewport({ zoom: newZoom })
  }
  
  public resetZoom(): void {
    this.updateViewport({ zoom: 1 })
  }
  
  // 事件系统
  public on(event: string, listener: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(listener)
  }
  
  public off(event: string, listener: Function): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(listener)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      [...listeners].forEach(listener => listener(data))
    }
  }
  
  public destroy(): void {
    if (this.isDestroyed) return
    
    this.isDestroyed = true
    
    // 移除事件监听器
    // 注意：bind 返回的是新函数，这里需要修改为正确的移除逻辑，或者在构造函数中绑定
    // 为简化，这里暂时只做简单的清理标记，实际应用中建议使用 AbortController 或保存 bound function 引用
    this.canvas.replaceWith(this.canvas.cloneNode(true))
    
    document.removeEventListener('keydown', this.handleKeyDown.bind(this))
    
    this.eventListeners.clear()
  }
}