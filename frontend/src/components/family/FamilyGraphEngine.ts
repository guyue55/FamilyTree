import { ref, computed, type Ref, type ComputedRef } from 'vue'
import type { FamilyMember, Family, GenerationGroup, MemberGroup } from '@/types/family'
export type { FamilyMember, Family, GenerationGroup, MemberGroup }

import { createGraphRenderer, type GraphRenderer } from './GraphRenderer'
import { LayoutManager } from './LayoutManager'
import { InteractionManager } from './InteractionManager'
import { AnimationManager, VirtualizationManager } from './AnimationManager'

// 核心类型定义
export interface Position {
  x: number
  y: number
}

export interface Size {
  width: number
  height: number
}

export interface Bounds {
  left: number
  top: number
  right: number
  bottom: number
}

export interface Viewport {
  x: number
  y: number
  width: number
  height: number
  zoom: number
}

export interface NodePosition extends Position {
  size: Size
  visible: boolean
}

export interface RelationshipLine {
  id: string
  type: 'parent' | 'spouse' | 'sibling'
  from: string
  to: string
  path?: string
  style?: RelationshipStyle
}

export interface RelationshipStyle {
  stroke: string
  strokeWidth: number
  strokeDasharray?: string
  opacity?: number
}

// 布局类型枚举
export enum FamilyLayoutType {
  HIERARCHICAL = 'hierarchical',    // 层次布局
  COMPACT = 'compact',              // 紧凑布局
  CIRCULAR = 'circular',            // 环形布局
  ORTHOGONAL = 'orthogonal',        // 正交布局
  ORGANIC = 'organic'               // 有机布局
}

// 渲染类型枚举
export enum RenderType {
  SVG = 'svg',
  CANVAS = 'canvas',
  WEBGL = 'webgl'
}

// 交互模式枚举
export enum InteractionMode {
  PAN = 'pan',
  ZOOM = 'zoom',
  SELECT = 'select',
  EDIT = 'edit',
  DRAG = 'drag'
}

// 配置接口
export interface FamilyGraphConfig {
  container: HTMLElement
  width?: number
  height?: number
  layout?: FamilyLayoutType
  renderType?: RenderType
  showRelationships?: boolean
  showPhotos?: boolean
  showDates?: boolean
  showGeneration?: boolean
  enableAnimation?: boolean
  enableVirtualization?: boolean
  minZoom?: number
  maxZoom?: number
}

// 布局结果接口
export interface LayoutResult {
  positions: Map<string, NodePosition>
  bounds: Bounds
  relationships: RelationshipLine[]
}

// 事件接口
export interface GraphEvent {
  type: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  target: any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any
}

export interface NodeEvent extends GraphEvent {
  node: FamilyMember
  position: Position
}

export interface EdgeEvent extends GraphEvent {
  edge: RelationshipLine
}

// 核心引擎类
export class FamilyGraphEngine {
  private container: HTMLElement
  private config: Required<FamilyGraphConfig>
  private members: Ref<FamilyMember[]>
  private selectedMembers: Ref<Set<string>>
  private selectedRelationships: Ref<Set<string>>
  private viewport: Ref<Viewport>
  
  // 核心模块
  private renderer!: GraphRenderer
  private layoutManager!: LayoutManager
  private interactionManager!: InteractionManager
  private animationManager!: AnimationManager
  private virtualizationManager!: VirtualizationManager
  
  // 状态
  private isInitialized = false
  private isDestroyed = false
  private eventListeners = new Map<string, Function[]>()
  
  constructor(config: FamilyGraphConfig) {
    this.container = config.container
    this.config = this.mergeConfig(config)
    
    // 响应式状态
    this.members = ref<FamilyMember[]>([])
    this.selectedMembers = ref<Set<string>>(new Set())
    this.selectedRelationships = ref<Set<string>>(new Set())
    this.viewport = ref<Viewport>({
      x: 0,
      y: 0,
      width: this.config.width,
      height: this.config.height,
      zoom: 1
    })
    
    // 初始化核心模块
    this.initializeModules()
  }
  
  private mergeConfig(config: FamilyGraphConfig): Required<FamilyGraphConfig> {
    return {
      container: config.container,
      width: config.width || 800,
      height: config.height || 600,
      layout: config.layout || FamilyLayoutType.HIERARCHICAL,
      renderType: config.renderType || RenderType.SVG,
      showRelationships: config.showRelationships ?? true,
      showPhotos: config.showPhotos ?? false,
      showDates: config.showDates ?? true,
      showGeneration: config.showGeneration ?? true,
      enableAnimation: config.enableAnimation ?? true,
      enableVirtualization: config.enableVirtualization ?? true,
      minZoom: config.minZoom || 0.1,
      maxZoom: config.maxZoom || 3
    }
  }
  
  private initializeModules() {
    const self = this
    this.renderer = createGraphRenderer(this.container, this.config.renderType)
    this.layoutManager = new LayoutManager(this.config.layout)
    this.interactionManager = new InteractionManager({
      get current() { return self.viewport.value },
      set current(v) { self.viewport.value = v }
    })
    this.animationManager = new AnimationManager(this.config.enableAnimation)
    this.virtualizationManager = new VirtualizationManager(this.config.enableVirtualization)
  }
  
  // 公共API
  public async initialize(): Promise<void> {
    if (this.isInitialized) return
    
    try {
      // 初始化渲染器
      await this.renderer.initialize(this.config.width, this.config.height)
      
      // 设置事件监听
      this.setupEventListeners()
      
      // 初始化交互管理器
      this.interactionManager.initialize(this.renderer.getCanvas())
      
      this.isInitialized = true
      this.emit('initialized')
    } catch (error) {
      console.error('Failed to initialize FamilyGraphEngine:', error)
      throw error
    }
  }
  
  public loadData(members: FamilyMember[]): void {
    this.members.value = members
    
    // 执行布局计算
    const layoutResult = this.layoutManager.calculateLayout(members)
    
    // 更新渲染器
    this.renderer.updateLayout(layoutResult)
    
    // 触发重新渲染
    this.scheduleRender()
    
    this.emit('dataLoaded', { members, layoutResult })
  }
  
  public setLayout(layoutType: FamilyLayoutType): void {
    if (this.config.layout === layoutType) return
    
    this.config.layout = layoutType
    this.layoutManager.setLayoutType(layoutType)
    
    // 重新计算布局
    if (this.members.value.length > 0) {
      this.loadData(this.members.value)
    }
    
    this.emit('layoutChanged', { layoutType })
  }
  
  public setViewport(viewport: Partial<Viewport>): void {
    const newViewport = { ...this.viewport.value, ...viewport }
    this.viewport.value = newViewport
    
    // 更新渲染器视口
    this.renderer.updateViewport(newViewport)
    
    // 虚拟化裁剪
    if (this.config.enableVirtualization) {
      this.virtualizationManager.cullNodes(this.members.value, newViewport)
    }
    
    this.emit('viewportChanged', { viewport: newViewport })
  }
  
  public selectMember(memberId: string, multiSelect = false): void {
    if (!multiSelect) {
      this.selectedMembers.value.clear()
    }
    
    if (this.selectedMembers.value.has(memberId)) {
      this.selectedMembers.value.delete(memberId)
    } else {
      this.selectedMembers.value.add(memberId)
    }
    
    this.emit('selectionChanged', { 
      selectedMembers: Array.from(this.selectedMembers.value),
      member: this.members.value.find(m => m.id === memberId)
    })
    
    // 优化：仅更新选中状态，不触发全量重绘
    this.renderer.updateSelection(this.selectedMembers.value)
  }

  public selectRelationship(relationshipId: string, multiSelect = false): void {
    if (!multiSelect) {
      this.selectedRelationships.value.clear()
    }
    
    if (this.selectedRelationships.value.has(relationshipId)) {
      this.selectedRelationships.value.delete(relationshipId)
    } else {
      this.selectedRelationships.value.add(relationshipId)
    }
    
    // 触发局部更新
    this.renderer.updateRelationshipSelection(this.selectedRelationships.value)
  }
  
  public fitToScreen(): void {
    if (this.members.value.length === 0) return
    
    const bounds = this.layoutManager.getCurrentBounds()
    const viewportWidth = this.config.width
    const viewportHeight = this.config.height
    
    // 计算合适的缩放比例
    const scaleX = viewportWidth / (bounds.right - bounds.left)
    const scaleY = viewportHeight / (bounds.bottom - bounds.top)
    const zoom = Math.min(scaleX, scaleY, this.config.maxZoom)
    
    // 计算居中位置
    const centerX = (bounds.left + bounds.right) / 2
    const centerY = (bounds.top + bounds.bottom) / 2
    
    this.setViewport({
      zoom: Math.max(zoom, this.config.minZoom),
      x: viewportWidth / 2 - centerX * zoom,
      y: viewportHeight / 2 - centerY * zoom
    })
  }
  
  public centerGraph(): void {
    this.setViewport({
      zoom: 1,
      x: 0,
      y: 0
    })
  }
  
  public exportAsImage(format: 'png' | 'jpeg' | 'svg' = 'png'): string {
    return this.renderer.exportAsImage(format)
  }
  
  public updateConfig(newConfig: Partial<FamilyGraphConfig>): void {
    this.config = {
      ...this.config,
      ...newConfig
    }
    this.scheduleRender()
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
  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(listener => listener(data))
    }
  }
  
  private setupEventListeners(): void {
    // 渲染器事件
    this.renderer.on('nodeClick', (event: NodeEvent) => {
      this.selectMember(event.node.id, event.data?.multiSelect)
      this.emit('nodeClick', event)
    })
    
    this.renderer.on('nodeDoubleClick', (event: NodeEvent) => {
      this.emit('nodeDoubleClick', event)
    })
    
    this.renderer.on('edgeClick', (event: EdgeEvent) => {
      this.selectRelationship(event.edge.id, event.data?.multiSelect)
      this.emit('edgeClick', event)
    })
    
    // 交互管理器事件
    this.interactionManager.on('viewportChange', (viewport: Viewport) => {
      this.setViewport(viewport)
    })
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    this.interactionManager.on('nodeDrag', (data: any) => {
      this.emit('nodeDrag', data)
    })
  }
  
  private scheduleRender(): void {
    if (this.config.enableVirtualization) {
      this.virtualizationManager.scheduleRender(() => {
        this.render()
      })
    } else {
      requestAnimationFrame(() => this.render())
    }
  }
  
  private render(): void {
    if (this.isDestroyed) return
    
    const viewport = this.viewport.value
    const members = this.members.value
    const selectedMembers = this.selectedMembers.value
    const selectedRelationships = this.selectedRelationships.value
    
    // 获取当前布局结果
    const layoutResult = this.layoutManager.getCurrentLayout()
    if (!layoutResult) return
    
    // 渲染场景
    this.renderer.render({
      members,
      selectedMembers,
      selectedRelationships,
      layoutResult,
      viewport,
      config: this.config
    })
  }
  
  // 清理资源
  public destroy(): void {
    if (this.isDestroyed) return
    
    this.isDestroyed = true
    
    // 清理模块
    this.renderer?.destroy()
    this.interactionManager?.destroy()
    this.animationManager?.destroy()
    this.virtualizationManager?.destroy()
    
    // 清理事件监听器
    this.eventListeners.clear()
    
    this.emit('destroyed')
  }
  
  // Getters
  public getMembers(): ComputedRef<FamilyMember[]> {
    return computed(() => this.members.value)
  }
  
  public getSelectedMembers(): ComputedRef<FamilyMember[]> {
    return computed(() => {
      return this.members.value.filter(m => this.selectedMembers.value.has(m.id))
    })
  }
  
  public getViewport(): ComputedRef<Viewport> {
    return computed(() => this.viewport.value)
  }
  
  public getCurrentLayout(): ComputedRef<LayoutResult | null> {
    return computed(() => this.layoutManager.getCurrentLayout())
  }
}

// 导出默认实例工厂
export function createFamilyGraph(config: FamilyGraphConfig): FamilyGraphEngine {
  return new FamilyGraphEngine(config)
}