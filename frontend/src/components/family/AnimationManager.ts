// 动画管理器
export class AnimationManager {
  private isEnabled: boolean
  private animations: Map<string, Animation> = new Map()
  private frameId: number | null = null
  
  constructor(isEnabled: boolean) {
    this.isEnabled = isEnabled
  }
  
  // 节点动画
  public animateNodePosition(
    element: HTMLElement, 
    from: { x: number, y: number }, 
    to: { x: number, y: number },
    duration: number = 300,
    easing: string = 'cubic-bezier(0.4, 0, 0.2, 1)'
  ): Promise<void> {
    if (!this.isEnabled) {
      element.style.transform = `translate(${to.x}px, ${to.y}px)`
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { transform: `translate(${from.x}px, ${from.y}px)` },
        { transform: `translate(${to.x}px, ${to.y}px)` }
      ], {
        duration,
        easing,
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set(element.id || 'node', animation)
    })
  }
  
  // 缩放动画
  public animateZoom(
    element: HTMLElement,
    from: number,
    to: number,
    duration: number = 200
  ): Promise<void> {
    if (!this.isEnabled) {
      element.style.scale = to.toString()
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { scale: from },
        { scale: to }
      ], {
        duration,
        easing: 'ease-out',
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set('zoom', animation)
    })
  }
  
  // 淡入动画
  public fadeIn(element: HTMLElement, duration: number = 300): Promise<void> {
    if (!this.isEnabled) {
      element.style.opacity = '1'
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { opacity: '0' },
        { opacity: '1' }
      ], {
        duration,
        easing: 'ease-out',
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set(element.id || 'fadein', animation)
    })
  }
  
  // 淡出动画
  public fadeOut(element: HTMLElement, duration: number = 300): Promise<void> {
    if (!this.isEnabled) {
      element.style.opacity = '0'
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { opacity: '1' },
        { opacity: '0' }
      ], {
        duration,
        easing: 'ease-in',
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set(element.id || 'fadeout', animation)
    })
  }
  
  // 弹跳动画
  public bounce(element: HTMLElement): Promise<void> {
    if (!this.isEnabled) {
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { transform: 'scale(1)' },
        { transform: 'scale(1.2)' },
        { transform: 'scale(0.9)' },
        { transform: 'scale(1.1)' },
        { transform: 'scale(1)' }
      ], {
        duration: 600,
        easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set(element.id || 'bounce', animation)
    })
  }
  
  // 脉冲动画
  public pulse(element: HTMLElement, duration: number = 1000): Promise<void> {
    if (!this.isEnabled) {
      return Promise.resolve()
    }
    
    return new Promise(resolve => {
      const animation = element.animate([
        { transform: 'scale(1)', opacity: '1' },
        { transform: 'scale(1.05)', opacity: '0.8' },
        { transform: 'scale(1)', opacity: '1' }
      ], {
        duration,
        iterations: 1,
        easing: 'ease-in-out',
        fill: 'forwards'
      })
      
      animation.onfinish = () => resolve()
      this.animations.set(element.id || 'pulse', animation)
    })
  }
  
  // 停止所有动画
  public stopAll(): void {
    this.animations.forEach(animation => {
      animation.cancel()
    })
    this.animations.clear()
    
    if (this.frameId) {
      cancelAnimationFrame(this.frameId)
      this.frameId = null
    }
  }
  
  public destroy(): void {
    this.stopAll()
  }
}

// 虚拟化管理器
export class VirtualizationManager {
  private isEnabled: boolean
  private visibleNodes: Set<string> = new Set()
  private renderCallback: (() => void) | null = null
  private frameId: number | null = null
  private viewport: { x: number, y: number, width: number, height: number, zoom: number } = {
    x: 0, y: 0, width: 800, height: 600, zoom: 1
  }
  
  constructor(isEnabled: boolean) {
    this.isEnabled = isEnabled
  }
  
  // 裁剪节点
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public cullNodes(members: any[], viewport: any): void {
    if (!this.isEnabled) {
      // 如果未启用虚拟化，所有节点都可见
      members.forEach(member => this.visibleNodes.add(member.id))
      return
    }
    
    this.viewport = viewport
    const newVisibleNodes = new Set<string>()
    
    // 计算视口边界
    const bounds = this.getViewportBounds(viewport)
    
    // 检查每个节点是否在视口内
    members.forEach(member => {
      if (this.isNodeInViewport(member, bounds)) {
        newVisibleNodes.add(member.id)
      }
    })
    
    // 检查可见性是否发生变化
    const hasChanges = 
      newVisibleNodes.size !== this.visibleNodes.size ||
      ![...newVisibleNodes].every(id => this.visibleNodes.has(id))
    
    if (hasChanges) {
      this.visibleNodes = newVisibleNodes
      this.scheduleRender()
    }
  }
  
  // 检查节点是否在视口内
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private isNodeInViewport(member: any, bounds: any): boolean {
    // 简化的边界检查
    // 实际实现中需要根据节点的实际位置和大小来判断
    const margin = 100 // 添加边距以确保平滑过渡
    
    return (
      member.x >= bounds.left - margin &&
      member.x <= bounds.right + margin &&
      member.y >= bounds.top - margin &&
      member.y <= bounds.bottom + margin
    )
  }
  
  // 获取视口边界
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private getViewportBounds(viewport: any): any {
    const { x, y, width, height, zoom } = viewport
    
    return {
      left: -x / zoom,
      top: -y / zoom,
      right: (-x + width) / zoom,
      bottom: (-y + height) / zoom
    }
  }
  
  // 调度渲染
  public scheduleRender(callback?: () => void): void {
    if (callback) {
      this.renderCallback = callback
    }
    
    if (this.frameId) {
      return
    }
    
    this.frameId = requestAnimationFrame(() => {
      if (this.renderCallback) {
        this.renderCallback()
      }
      this.frameId = null
    })
  }
  
  // 获取可见节点
  public getVisibleNodes(): Set<string> {
    return this.visibleNodes
  }
  
  // 检查节点是否可见
  public isNodeVisible(nodeId: string): boolean {
    return this.visibleNodes.has(nodeId)
  }
  
  // 强制重新计算可见性
  public invalidate(): void {
    this.visibleNodes.clear()
    this.scheduleRender()
  }
  
  public destroy(): void {
    if (this.frameId) {
      cancelAnimationFrame(this.frameId)
      this.frameId = null
    }
    this.visibleNodes.clear()
    this.renderCallback = null
  }
}