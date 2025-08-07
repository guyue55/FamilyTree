/**
 * 图形数据类型定义
 * 定义G6图形库相关的数据结构
 *
 * @author 古月
 * @version 1.0.0
 */

import type { ID } from './index'
import { Gender } from '@/enums/user'
import { LayoutType, NodeShape, EdgeStyle } from '@/enums/familyTree'

/**
 * 图形节点数据接口
 */
export interface GraphNode {
  /** 节点ID */
  id: string
  /** 节点标签 */
  label: string
  /** 节点类型 */
  type: string
  /** X坐标 */
  x?: number
  /** Y坐标 */
  y?: number
  /** 节点样式 */
  style?: {
    /** 填充颜色 */
    fill?: string
    /** 边框颜色 */
    stroke?: string
    /** 边框宽度 */
    lineWidth?: number
    /** 透明度 */
    opacity?: number
    /** 阴影 */
    shadowColor?: string
    /** 阴影模糊度 */
    shadowBlur?: number
    /** 阴影偏移X */
    shadowOffsetX?: number
    /** 阴影偏移Y */
    shadowOffsetY?: number
  }
  /** 节点大小 */
  size?: number | [number, number]
  /** 节点形状 */
  shape?: string
  /** 节点图标 */
  icon?: {
    /** 图标类型 */
    type: 'text' | 'image' | 'font'
    /** 图标内容 */
    value: string
    /** 图标大小 */
    size?: number
    /** 图标颜色 */
    color?: string
  }
  /** 节点图片 */
  img?: string
  /** 节点状态 */
  state?: {
    /** 是否选中 */
    selected?: boolean
    /** 是否高亮 */
    highlight?: boolean
    /** 是否激活 */
    active?: boolean
    /** 是否禁用 */
    disabled?: boolean
  }
  /** 扩展数据 */
  data?: {
    /** 成员ID */
    memberId: ID
    /** 成员姓名 */
    name: string
    /** 性别 */
    gender: Gender
    /** 出生日期 */
    birthDate?: string
    /** 逝世日期 */
    deathDate?: string
    /** 是否在世 */
    isAlive: boolean
    /** 世代 */
    generation: number
    /** 头像URL */
    avatarUrl?: string
    /** 职业 */
    occupation?: string
    /** 出生地 */
    birthPlace?: string
    /** 现居地 */
    currentAddress?: string
    /** 配偶ID列表 */
    spouseIds?: ID[]
    /** 父亲ID */
    fatherId?: ID
    /** 母亲ID */
    motherId?: ID
    /** 子女ID列表 */
    childrenIds?: ID[]
  }
}

/**
 * 图形边数据接口
 */
export interface GraphEdge {
  /** 边ID */
  id: string
  /** 源节点ID */
  source: string
  /** 目标节点ID */
  target: string
  /** 边类型 */
  type: string
  /** 边标签 */
  label?: string
  /** 边样式 */
  style?: {
    /** 边颜色 */
    stroke?: string
    /** 边宽度 */
    lineWidth?: number
    /** 线型 */
    lineDash?: number[]
    /** 透明度 */
    opacity?: number
    /** 端点样式 */
    endArrow?:
      | boolean
      | {
          /** 箭头路径 */
          path: string
          /** 箭头大小 */
          d: number
        }
    /** 起点样式 */
    startArrow?:
      | boolean
      | {
          /** 箭头路径 */
          path: string
          /** 箭头大小 */
          d: number
        }
  }
  /** 边形状 */
  shape?: string
  /** 控制点 */
  controlPoints?: Array<{ x: number; y: number }>
  /** 边状态 */
  state?: {
    /** 是否选中 */
    selected?: boolean
    /** 是否高亮 */
    highlight?: boolean
    /** 是否激活 */
    active?: boolean
    /** 是否禁用 */
    disabled?: boolean
  }
  /** 扩展数据 */
  data?: {
    /** 关系类型 */
    relationshipType: string
    /** 关系描述 */
    relationshipDesc: string
    /** 关系强度 */
    strength?: number
    /** 是否为主要关系 */
    isPrimary?: boolean
  }
}

/**
 * 图形数据接口
 */
export interface GraphData {
  /** 节点列表 */
  nodes: GraphNode[]
  /** 边列表 */
  edges: GraphEdge[]
  /** 组合列表 */
  combos?: Array<{
    /** 组合ID */
    id: string
    /** 组合标签 */
    label: string
    /** 组合类型 */
    type?: string
    /** 组合样式 */
    style?: Record<string, any>
  }>
}

/**
 * 图形配置接口
 */
export interface GraphConfig {
  /** 容器ID */
  container: string | HTMLElement
  /** 画布宽度 */
  width: number
  /** 画布高度 */
  height: number
  /** 布局类型 */
  layout: LayoutType
  /** 布局配置 */
  layoutConfig?: {
    /** 节点间距 */
    nodeSpacing?: number
    /** 层级间距 */
    levelSpacing?: number
    /** 根节点位置 */
    rootPosition?: 'top' | 'bottom' | 'left' | 'right' | 'center'
    /** 是否启用动画 */
    animate?: boolean
    /** 动画持续时间 */
    animationDuration?: number
  }
  /** 默认节点配置 */
  defaultNode?: {
    /** 节点类型 */
    type?: string
    /** 节点大小 */
    size?: number | [number, number]
    /** 节点样式 */
    style?: Record<string, any>
    /** 节点标签配置 */
    labelCfg?: {
      /** 标签位置 */
      position?: 'center' | 'top' | 'bottom' | 'left' | 'right'
      /** 标签样式 */
      style?: Record<string, any>
    }
  }
  /** 默认边配置 */
  defaultEdge?: {
    /** 边类型 */
    type?: string
    /** 边样式 */
    style?: Record<string, any>
    /** 边标签配置 */
    labelCfg?: {
      /** 标签位置 */
      position?: 'start' | 'middle' | 'end'
      /** 标签样式 */
      style?: Record<string, any>
    }
  }
  /** 交互模式 */
  modes?: {
    /** 默认模式 */
    default?: string[]
    /** 编辑模式 */
    edit?: string[]
  }
  /** 是否启用缩放 */
  enableZoom?: boolean
  /** 是否启用拖拽 */
  enableDrag?: boolean
  /** 是否自适应画布 */
  fitView?: boolean
  /** 自适应边距 */
  fitViewPadding?: number | [number, number, number, number]
  /** 最小缩放比例 */
  minZoom?: number
  /** 最大缩放比例 */
  maxZoom?: number
}

/**
 * 图形事件接口
 */
export interface GraphEvent {
  /** 事件类型 */
  type: string
  /** 事件目标 */
  target: any
  /** 事件数据 */
  item?: GraphNode | GraphEdge
  /** 画布坐标 */
  canvasX?: number
  /** 画布坐标 */
  canvasY?: number
  /** 客户端坐标 */
  clientX?: number
  /** 客户端坐标 */
  clientY?: number
  /** 原始事件 */
  originalEvent?: Event
}

/**
 * 图形操作选项接口
 */
export interface GraphOptions {
  /** 是否启用动画 */
  animate?: boolean
  /** 动画持续时间 */
  duration?: number
  /** 动画缓动函数 */
  easing?: string
  /** 是否延迟执行 */
  delay?: number
  /** 回调函数 */
  callback?: () => void
}

/**
 * 图形导出选项接口
 */
export interface GraphExportOptions {
  /** 导出格式 */
  type: 'image/png' | 'image/jpeg' | 'image/webp'
  /** 图片质量 */
  quality?: number
  /** 图片宽度 */
  width?: number
  /** 图片高度 */
  height?: number
  /** 背景颜色 */
  backgroundColor?: string
  /** 文件名 */
  name?: string
}

/**
 * 图形搜索结果接口
 */
export interface GraphSearchResult {
  /** 匹配的节点 */
  nodes: GraphNode[]
  /** 匹配的边 */
  edges: GraphEdge[]
  /** 搜索关键词 */
  keyword: string
  /** 匹配数量 */
  total: number
}

/**
 * 图形路径接口
 */
export interface GraphPath {
  /** 路径节点 */
  nodes: GraphNode[]
  /** 路径边 */
  edges: GraphEdge[]
  /** 路径长度 */
  length: number
  /** 路径权重 */
  weight?: number
}

/**
 * 图形统计信息接口
 */
export interface GraphStats {
  /** 节点总数 */
  nodeCount: number
  /** 边总数 */
  edgeCount: number
  /** 最大世代数 */
  maxGeneration: number
  /** 最小世代数 */
  minGeneration: number
  /** 男性成员数 */
  maleCount: number
  /** 女性成员数 */
  femaleCount: number
  /** 在世成员数 */
  aliveCount: number
  /** 已故成员数 */
  deceasedCount: number
  /** 平均年龄 */
  averageAge?: number
}

/**
 * 图形布局算法接口
 */
export interface GraphLayoutAlgorithm {
  /** 算法名称 */
  name: string
  /** 算法类型 */
  type: LayoutType
  /** 算法配置 */
  config: Record<string, any>
  /** 执行算法 */
  execute: (data: GraphData) => GraphData
}

/**
 * 图形主题接口
 */
export interface GraphTheme {
  /** 主题名称 */
  name: string
  /** 主题描述 */
  description?: string
  /** 节点主题 */
  node: {
    /** 默认样式 */
    default: Record<string, any>
    /** 选中样式 */
    selected?: Record<string, any>
    /** 高亮样式 */
    highlight?: Record<string, any>
    /** 禁用样式 */
    disabled?: Record<string, any>
  }
  /** 边主题 */
  edge: {
    /** 默认样式 */
    default: Record<string, any>
    /** 选中样式 */
    selected?: Record<string, any>
    /** 高亮样式 */
    highlight?: Record<string, any>
    /** 禁用样式 */
    disabled?: Record<string, any>
  }
  /** 画布主题 */
  canvas?: {
    /** 背景颜色 */
    backgroundColor?: string
    /** 网格配置 */
    grid?: {
      /** 是否显示网格 */
      visible: boolean
      /** 网格颜色 */
      color: string
      /** 网格大小 */
      size: number
    }
  }
}

/**
 * 关系信息接口
 */
export interface RelationshipInfo {
  /** 关系类型 */
  type: string
  /** 关系描述 */
  description: string
  /** 关系方向 */
  direction: 'up' | 'down' | 'same' | 'spouse'
  /** 世代差 */
  generationDiff: number
  /** 是否为直系关系 */
  isDirect: boolean
  /** 是否为血缘关系 */
  isBloodRelated: boolean
}
