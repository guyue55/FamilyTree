import { FamilyLayoutType } from './FamilyGraphEngine'
import type { 
  FamilyMember, 
  Bounds, 
  NodePosition, 
  LayoutResult, 
  RelationshipLine
} from './FamilyGraphEngine'

// 布局管理器
export class LayoutManager {
  private currentLayoutType: FamilyLayoutType
  private currentLayout: LayoutResult | null = null
  private nodeSize = { width: 160, height: 120 }
  private horizontalSpacing = 200
  private verticalSpacing = 180
  
  constructor(layoutType: FamilyLayoutType) {
    this.currentLayoutType = layoutType
  }
  
  setLayoutType(layoutType: FamilyLayoutType): void {
    this.currentLayoutType = layoutType
  }
  
  calculateLayout(members: FamilyMember[]): LayoutResult {
    switch (this.currentLayoutType) {
      case FamilyLayoutType.HIERARCHICAL:
        return this.hierarchicalLayout(members)
      case FamilyLayoutType.COMPACT:
        return this.compactLayout(members)
      case FamilyLayoutType.CIRCULAR:
        return this.circularLayout(members)
      case FamilyLayoutType.ORTHOGONAL:
        return this.orthogonalLayout(members)
      case FamilyLayoutType.ORGANIC:
        return this.organicLayout(members)
      default:
        return this.hierarchicalLayout(members)
    }
  }
  
  getCurrentLayout(): LayoutResult | null {
    return this.currentLayout
  }
  
  getCurrentBounds(): Bounds {
    if (!this.currentLayout) {
      return { left: 0, top: 0, right: 800, bottom: 600 }
    }
    
    const { positions } = this.currentLayout
    let minX = Infinity, minY = Infinity
    let maxX = -Infinity, maxY = -Infinity
    
    positions.forEach(pos => {
      minX = Math.min(minX, pos.x)
      minY = Math.min(minY, pos.y)
      maxX = Math.max(maxX, pos.x + pos.size.width)
      maxY = Math.max(maxY, pos.y + pos.size.height)
    })
    
    return {
      left: minX,
      top: minY,
      right: maxX,
      bottom: maxY
    }
  }
  
  // 层次布局（树状结构优化版）
  private hierarchicalLayout(members: FamilyMember[]): LayoutResult {
    const positions = new Map<string, NodePosition>()
    const relationships: RelationshipLine[] = []
    
    // 配置参数
    const NODE_WIDTH = this.nodeSize.width
    const NODE_HEIGHT = this.nodeSize.height
    // 缩减兄弟节点间距，从 40 调整为 20
    const SIBLING_SPACING = 20 
    // 缩减家族树间距，从 80 调整为 40
    const TREE_SPACING = 40    
    const V_SPACING = this.verticalSpacing
    const COUPLE_GAP = 0       // 夫妻间距（贴合）

    // 1. 构建数据结构：FamilyUnit
    interface FamilyUnit {
      id: string
      members: FamilyMember[]
      children: FamilyUnit[]
      width: number
      x: number
      y: number
    }

    const memberMap = new Map<string, FamilyMember>()
    members.forEach(m => memberMap.set(m.id, m))
    
    const processedMembers = new Set<string>()
    const units: FamilyUnit[] = []
    const unitMap = new Map<string, FamilyUnit>()

    // 组装夫妻单元
    members.forEach(m => {
      if (processedMembers.has(m.id)) return
      
      const unitMembers = [m]
      processedMembers.add(m.id)
      
      if (m.spouseId && memberMap.has(m.spouseId) && !processedMembers.has(m.spouseId)) {
        const spouse = memberMap.get(m.spouseId)!
        unitMembers.push(spouse)
        processedMembers.add(spouse.id)
      }
      
      // 确保男性在前（可选，为了视觉一致性）
      unitMembers.sort((a, b) => (a.gender === 'male' ? -1 : 1))
      
      const unit: FamilyUnit = {
        id: unitMembers[0].id,
        members: unitMembers,
        children: [],
        width: 0,
        x: 0,
        y: 0
      }
      
      units.push(unit)
      unitMembers.forEach(um => unitMap.set(um.id, unit))
    })

    // 构建树状关系
    const rootUnits: FamilyUnit[] = []
    const childUnits = new Set<FamilyUnit>()
    
    units.forEach(unit => {
      // 查找父单元
      let parentUnit: FamilyUnit | undefined
      
      // 只要任意成员有父节点，且该父节点存在于当前数据中
      for (const m of unit.members) {
        if (m.parentId && unitMap.has(m.parentId)) {
          parentUnit = unitMap.get(m.parentId)
          break
        }
      }
      
      if (parentUnit) {
        parentUnit.children.push(unit)
        childUnits.add(unit)
      }
    })
    
    // 识别根节点
    units.forEach(u => {
      if (!childUnits.has(u)) {
        rootUnits.push(u)
      }
    })

    // 安全检查：如果存在循环依赖导致没有根节点，或者有部分节点未被访问
    // 将所有未被标记为"子节点"的单元视为根节点（已完成）
    // 如果 rootUnits 为空但 units 不为空，说明存在完全的循环依赖，任意选取一个作为根
    if (rootUnits.length === 0 && units.length > 0) {
      console.warn('Cycle detected in family tree, forcing a root.')
      rootUnits.push(units[0])
    }
    
    // 另外，为了防止孤立的循环子图被遗漏，我们需要确保所有单元最终都被布局
    // 但在当前的简单实现中，我们先假设图是合法的（无循环）。
    // 如果需要更强的鲁棒性，可以在布局后检查 visited 集合。

    // 2. 测量阶段（递归计算宽度）
    const measureUnit = (unit: FamilyUnit) => {
      const unitContentWidth = unit.members.length * NODE_WIDTH + (unit.members.length - 1) * COUPLE_GAP
      
      if (unit.children.length === 0) {
        unit.width = unitContentWidth
      } else {
        let childrenTotalWidth = 0
        unit.children.forEach((child, i) => {
          measureUnit(child)
          childrenTotalWidth += child.width
          if (i < unit.children.length - 1) childrenTotalWidth += SIBLING_SPACING
        })
        
        unit.width = Math.max(unitContentWidth, childrenTotalWidth)
      }
    }
    
    rootUnits.forEach(measureUnit)

    // 3. 布局阶段（递归放置）
    const layoutVisitedInRecursion = new Set<FamilyUnit>()
    const layoutUnit = (unit: FamilyUnit, x: number, y: number) => {
      if (layoutVisitedInRecursion.has(unit)) return
      layoutVisitedInRecursion.add(unit)

      unit.x = x
      unit.y = y
      
      const unitContentWidth = unit.members.length * NODE_WIDTH + (unit.members.length - 1) * COUPLE_GAP
      
      // 居中放置当前单元成员
      const startX = x + (unit.width - unitContentWidth) / 2
      
      unit.members.forEach((m, index) => {
        const mx = startX + index * (NODE_WIDTH + COUPLE_GAP)
        positions.set(m.id, {
          x: mx,
          y: y,
          size: { width: NODE_WIDTH, height: NODE_HEIGHT },
          visible: true
        })
      })
      
      // 放置子节点
      if (unit.children.length > 0) {
        const nextY = y + V_SPACING
        
        let childrenBlockWidth = 0
        unit.children.forEach((child, i) => {
          childrenBlockWidth += child.width
          if (i < unit.children.length - 1) childrenBlockWidth += SIBLING_SPACING
        })
        
        // 居中放置子节点块
        let currentChildX = x + (unit.width - childrenBlockWidth) / 2
        
        unit.children.forEach(child => {
          layoutUnit(child, currentChildX, nextY)
          currentChildX += child.width + SIBLING_SPACING
        })
      }
    }

    // 布局所有根树
    let currentRootX = 100
    
    const processLayout = (roots: FamilyUnit[]) => {
      roots.forEach(root => {
        if (layoutVisitedInRecursion.has(root)) return
        
        layoutUnit(root, currentRootX, 100)
        currentRootX += root.width + TREE_SPACING
      })
    }
    
    processLayout(rootUnits)
    
    // 检查是否有未访问的节点（处理循环依赖或断开的组件）
    const unvisited = units.filter(u => !layoutVisitedInRecursion.has(u))
    if (unvisited.length > 0) {
       console.warn('Found disconnected or cyclic components, laying them out separately.')
       processLayout(unvisited)
    }

    // 4. 计算连线
    this.calculateRelationshipLines(members, positions, relationships)
    
    this.currentLayout = { positions, relationships, bounds: this.calculateBounds(positions) }
    return this.currentLayout
  }
  
  // 紧凑布局
  private compactLayout(members: FamilyMember[]): LayoutResult {
    const positions = new Map<string, NodePosition>()
    const relationships: RelationshipLine[] = []
    
    const generations = this.groupByGeneration(members)
    const generationKeys = Array.from(generations.keys()).sort((a, b) => a - b)
    
    // 减少间距
    const compactHSpacing = this.horizontalSpacing * 0.7
    const compactVSpacing = this.verticalSpacing * 0.8
    
    generationKeys.forEach((gen, genIndex) => {
      const genMembers = generations.get(gen)!
      const y = genIndex * compactVSpacing + 80
      
      // 优化排列：优先夫妻并排，然后紧凑排列单身
      const couples = this.identifyCouples(genMembers)
      const singles = genMembers.filter(m => !couples.some(c => c.includes(m)))
      
      let xOffset = 50
      
      couples.forEach(couple => {
        couple.forEach((member, index) => {
          positions.set(member.id, {
            x: xOffset + index * (this.nodeSize.width * 0.9),
            y,
            size: { ...this.nodeSize },
            visible: true
          })
        })
        xOffset += this.nodeSize.width * 1.8 + compactHSpacing * 0.5
      })
      
      singles.forEach(member => {
        positions.set(member.id, {
          x: xOffset,
          y,
          size: { ...this.nodeSize },
          visible: true
        })
        xOffset += this.nodeSize.width + compactHSpacing * 0.7
      })
    })
    
    this.calculateRelationshipLines(members, positions, relationships)
    
    this.currentLayout = { positions, relationships, bounds: this.calculateBounds(positions) }
    return this.currentLayout
  }
  
  // 环形布局
  private circularLayout(members: FamilyMember[]): LayoutResult {
    const positions = new Map<string, NodePosition>()
    const relationships: RelationshipLine[] = []
    
    const generations = this.groupByGeneration(members)
    const generationKeys = Array.from(generations.keys()).sort((a, b) => a - b)
    
    const centerX = 400
    const centerY = 300
    
    generationKeys.forEach((gen, genIndex) => {
      const genMembers = generations.get(gen)!
      const radius = 80 + genIndex * 100
      const angleStep = (2 * Math.PI) / genMembers.length
      
      genMembers.forEach((member, memberIndex) => {
        const angle = memberIndex * angleStep - Math.PI / 2
        const x = centerX + radius * Math.cos(angle) - this.nodeSize.width / 2
        const y = centerY + radius * Math.sin(angle) - this.nodeSize.height / 2
        
        positions.set(member.id, {
          x,
          y,
          size: { ...this.nodeSize },
          visible: true
        })
      })
    })
    
    this.calculateRelationshipLines(members, positions, relationships)
    
    this.currentLayout = { positions, relationships, bounds: this.calculateBounds(positions) }
    return this.currentLayout
  }
  
  // 正交布局
  private orthogonalLayout(members: FamilyMember[]): LayoutResult {
    const positions = new Map<string, NodePosition>()
    const relationships: RelationshipLine[] = []
    
    const generations = this.groupByGeneration(members)
    const generationKeys = Array.from(generations.keys()).sort((a, b) => a - b)
    
    // 网格对齐
    const gridWidth = this.nodeSize.width + this.horizontalSpacing
    const gridHeight = this.nodeSize.height + this.verticalSpacing
    
    generationKeys.forEach((gen, genIndex) => {
      const genMembers = generations.get(gen)!
      const y = genIndex * gridHeight + 100
      
      genMembers.forEach((member, memberIndex) => {
        const x = memberIndex * gridWidth + 100
        
        positions.set(member.id, {
          x,
          y,
          size: { ...this.nodeSize },
          visible: true
        })
      })
    })
    
    this.calculateRelationshipLines(members, positions, relationships)
    
    this.currentLayout = { positions, relationships, bounds: this.calculateBounds(positions) }
    return this.currentLayout
  }
  
  // 有机布局（力导向）
  private organicLayout(members: FamilyMember[]): LayoutResult {
    const positions = new Map<string, NodePosition>()
    const relationships: RelationshipLine[] = []
    
    // 初始化随机位置
    members.forEach(member => {
      positions.set(member.id, {
        x: Math.random() * 600 + 100,
        y: Math.random() * 400 + 100,
        size: { ...this.nodeSize },
        visible: true
      })
    })
    
    // 简单的力导向算法
    const iterations = 20
    const k = Math.sqrt((800 * 600) / members.length) // 理想距离
    
    for (let iter = 0; iter < iterations; iter++) {
      const forces = new Map<string, { x: number, y: number }>()
      
      // 初始化力
      members.forEach(member => {
        forces.set(member.id, { x: 0, y: 0 })
      })
      
      // 排斥力（所有节点之间）
      members.forEach((member1, i) => {
        members.forEach((member2, j) => {
          if (i >= j) return
          
          const pos1 = positions.get(member1.id)!
          const pos2 = positions.get(member2.id)!
          const dx = pos1.x - pos2.x
          const dy = pos1.y - pos2.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          
          if (distance > 0 && distance < k * 2) {
            const force = (k * k) / (distance * distance)
            const fx = (dx / distance) * force
            const fy = (dy / distance) * force
            
            const force1 = forces.get(member1.id)!
            const force2 = forces.get(member2.id)!
            
            force1.x += fx
            force1.y += fy
            force2.x -= fx
            force2.y -= fy
          }
        })
      })
      
      // 吸引力（有关系的节点）
      members.forEach(member => {
        if (member.parentId) {
          const parentPos = positions.get(member.parentId)
          const childPos = positions.get(member.id)
          
          if (parentPos && childPos) {
            const dx = parentPos.x - childPos.x
            const dy = parentPos.y - childPos.y
            const distance = Math.sqrt(dx * dx + dy * dy)
            
            if (distance > 0) {
              const force = (distance * distance) / k
              const fx = (dx / distance) * force * 0.1
              const fy = (dy / distance) * force * 0.1
              
              const force1 = forces.get(member.id)!
              force1.x += fx
              force1.y += fy
            }
          }
        }
      })
      
      // 应用力
      members.forEach(member => {
        const pos = positions.get(member.id)!
        const force = forces.get(member.id)!
        
        pos.x += force.x * 0.1
        pos.y += force.y * 0.1
        
        // 边界约束
        pos.x = Math.max(50, Math.min(750, pos.x))
        pos.y = Math.max(50, Math.min(550, pos.y))
      })
    }
    
    this.calculateRelationshipLines(members, positions, relationships)
    
    this.currentLayout = { positions, relationships, bounds: this.calculateBounds(positions) }
    return this.currentLayout
  }
  
  // 辅助方法
  private groupByGeneration(members: FamilyMember[]): Map<number, FamilyMember[]> {
    const groups = new Map<number, FamilyMember[]>()
    
    members.forEach(member => {
      const gen = member.generation || 1
      if (!groups.has(gen)) {
        groups.set(gen, [])
      }
      groups.get(gen)!.push(member)
    })
    
    return groups
  }
  
  private identifyCouples(members: FamilyMember[]): FamilyMember[][] {
    const couples: FamilyMember[][] = []
    const processed = new Set<string>()
    
    members.forEach(member => {
      if (processed.has(member.id) || !member.spouseId) return
      
      const spouse = members.find(m => m.id === member.spouseId)
      if (spouse && !processed.has(spouse.id)) {
        couples.push([member, spouse])
        processed.add(member.id)
        processed.add(spouse.id)
      }
    })
    
    return couples
  }
  
  private calculateRelationshipLines(
    members: FamilyMember[], 
    positions: Map<string, NodePosition>, 
    relationships: RelationshipLine[]
  ): void {
    
    members.forEach(member => {
      // 父子关系
      if (member.parentId) {
        const parentPos = positions.get(member.parentId)
        const childPos = positions.get(member.id)
        
        // 增加对 spouseId 的检查，如果父亲有配偶，连线起点应该从夫妻中间发出
         let startX = 0
         let startY = 0
         
         if (parentPos) {
            // 默认起点：父节点底部中心
            startX = parentPos.x + parentPos.size.width / 2
            startY = parentPos.y + parentPos.size.height

            const parent = members.find(m => m.id === member.parentId)
            if (parent && parent.spouseId && positions.has(parent.spouseId)) {
              // 找到配偶的位置
              const spousePos = positions.get(parent.spouseId)!
              // 计算夫妻中间位置
              const parentCenterX = parentPos.x + parentPos.size.width / 2
              const spouseCenterX = spousePos.x + spousePos.size.width / 2
              
              // 只有当两者在同一水平线上且距离合理时才使用中间点
              if (Math.abs(parentPos.y - spousePos.y) < 10) {
                  startX = (parentCenterX + spouseCenterX) / 2
              }
            }
         }

        if (parentPos && childPos) {
          const path = this.calculateBezierPath(
            startX,
            startY,
            childPos.x + childPos.size.width / 2,
            childPos.y
          )
          
          if (path) {
            relationships.push({
              id: `parent-${member.parentId}-${member.id}`,
              type: 'parent',
              from: member.parentId,
              to: member.id,
              path,
              style: {
                stroke: '#3b82f6',
                strokeWidth: 2,
                opacity: 0.6
              }
            })
          }
        }
      }
      
      // 配偶关系
      if (member.spouseId) {
        // 避免重复添加配偶连线（只添加一次）
        if (member.id > member.spouseId) return

        const spousePos = positions.get(member.spouseId)
        const memberPos = positions.get(member.id)
        
        if (spousePos && memberPos) {
          
          relationships.push({
            id: `spouse-${member.id}-${member.spouseId}`,
            type: 'spouse',
            from: member.id,
            to: member.spouseId,
            path: `M ${memberPos.x + memberPos.size.width / 2} ${memberPos.y + memberPos.size.height / 2} L ${spousePos.x + spousePos.size.width / 2} ${spousePos.y + spousePos.size.height / 2}`,
            style: {
              stroke: '#f43f5e',
              strokeWidth: 2,
              opacity: 0.8
            }
          })
        }
      }
    })
  }
  
  private calculateBezierPath(x1: number, y1: number, x2: number, y2: number): string {
    const midY = (y1 + y2) / 2
    // 增加控制点的垂直距离，使曲线更平滑
    const controlY1 = y1 + (midY - y1) * 0.85
    const controlY2 = y2 - (y2 - midY) * 0.85
    
    return `M ${x1} ${y1} C ${x1} ${controlY1}, ${x2} ${controlY2}, ${x2} ${y2}`
  }
  
  private calculateBounds(positions: Map<string, NodePosition>): Bounds {
    let minX = Infinity, minY = Infinity
    let maxX = -Infinity, maxY = -Infinity
    
    positions.forEach(pos => {
      minX = Math.min(minX, pos.x)
      minY = Math.min(minY, pos.y)
      maxX = Math.max(maxX, pos.x + pos.size.width)
      maxY = Math.max(maxY, pos.y + pos.size.height)
    })
    
    return {
      left: minX === Infinity ? 0 : minX,
      top: minY === Infinity ? 0 : minY,
      right: maxX === -Infinity ? 800 : maxX,
      bottom: maxY === -Infinity ? 600 : maxY
    }
  }
}