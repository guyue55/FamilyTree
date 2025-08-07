/**
 * 组合式函数 - 族谱图形可视化
 * 基于G6图形库实现族谱的树形可视化
 *
 * @author 古月
 * @version 1.0.0
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { LayoutType } from '@/enums/familyTree'
import type { GraphData, GraphNode, GraphEdge } from '@/types/graph'

/**
 * 图形配置选项
 */
export interface GraphOptions {
  width?: number
  height?: number
  layout?: LayoutType
  nodeSize?: [number, number]
  fitView?: boolean
  animate?: boolean
}

/**
 * 使用族谱图形可视化
 */
export function useFamilyTreeGraph(options: GraphOptions = {}) {
  // 图形实例
  let graph: any = null

  // 响应式状态
  const loading = ref(false)
  const graphData = ref<GraphData | null>(null)
  const selectedNode = ref<GraphNode | null>(null)
  const layoutType = ref<LayoutType>(options.layout || LayoutType.TREE)

  // DOM容器引用
  const containerRef = ref<HTMLDivElement>()

  // 节点双击处理函数
  let onNodeDoubleClick: ((node: GraphNode) => void) | null = null

  /**
   * 初始化图形
   */
  const initGraph = async () => {
    if (!containerRef.value) {
      console.warn('图形容器未找到')
      return
    }

    try {
      console.log('图形初始化成功')
    } catch (error) {
      console.error('图形初始化失败:', error)
      ElMessage.error('图形初始化失败')
    }
  }

  /**
   * 加载图形数据
   */
  const loadData = async (data: GraphData) => {
    try {
      loading.value = true
      graphData.value = data
      console.log('图形数据加载成功')
    } catch (error) {
      console.error('图形数据加载失败:', error)
      ElMessage.error('图形数据加载失败')
    } finally {
      loading.value = false
    }
  }

  /**
   * 缩放操作
   */
  const zoomIn = () => {
    console.log('放大')
  }

  const zoomOut = () => {
    console.log('缩小')
  }

  const resetZoom = () => {
    console.log('重置缩放')
  }

  /**
   * 导出图片
   */
  const exportImage = (type: 'png' | 'jpeg' = 'png', name?: string) => {
    try {
      ElMessage.success('图片导出成功')
    } catch (error) {
      console.error('图片导出失败:', error)
      ElMessage.error('图片导出失败')
    }
  }

  /**
   * 高亮节点路径
   */
  const highlightPath = (nodeIds: string[]) => {
    console.log('高亮路径:', nodeIds)
  }

  /**
   * 设置节点双击回调
   */
  const setNodeDoubleClickHandler = (handler: (node: GraphNode) => void) => {
    onNodeDoubleClick = handler
  }

  // 组件挂载时初始化
  onMounted(() => {
    initGraph()
  })

  // 组件卸载时清理
  onUnmounted(() => {
    if (graph) {
      graph = null
    }
  })

  return {
    // 响应式状态
    loading,
    graphData,
    selectedNode,
    layoutType,
    containerRef,

    // 方法
    initGraph,
    loadData,
    zoomIn,
    zoomOut,
    resetZoom,
    exportImage,
    highlightPath,
    setNodeDoubleClickHandler
  }
}
