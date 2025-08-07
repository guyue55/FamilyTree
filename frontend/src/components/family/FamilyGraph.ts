import { Graph } from '@antv/g6'
import type { FamilyMember } from '@/types/family'

export interface FamilyGraphOptions {
  container: string | HTMLElement
  width?: number
  height?: number
  fitView?: boolean
  modes?: any
}

export class FamilyGraph {
  private graph: Graph | null = null
  private data: {
    nodes: any[]
    edges: any[]
  } = {
    nodes: [],
    edges: []
  }

  constructor(private options: FamilyGraphOptions) {}

  public init(): Graph {
    // 创建图实例
    this.graph = new Graph({
      container: this.options.container,
      width: this.options.width || 800,
      height: this.options.height || 600,
      fitView: this.options.fitView !== false,
      modes: this.options.modes || {
        default: ['drag-canvas', 'zoom-canvas', 'drag-node']
      },
      layout: {
        type: 'dagre',
        rankdir: 'TB',
        align: 'UL',
        nodesep: 100,
        ranksep: 150
      },
      defaultNode: {
        type: 'rect',
        size: [120, 80],
        style: {
          fill: '#fff',
          stroke: '#e5e7eb',
          radius: 8
        },
        labelCfg: {
          style: {
            fill: '#333',
            fontSize: 14
          }
        }
      },
      defaultEdge: {
        type: 'line',
        style: {
          stroke: '#aaa',
          lineWidth: 2
        }
      }
    })

    return this.graph
  }



  public loadData(members: FamilyMember[]) {
    if (!this.graph) {
      console.error('Graph not initialized')
      return
    }

    // 转换成G6需要的数据格式
    const nodes = members.map(member => ({
      id: member.id,
      label: member.name,
      style: {
        fill: member.gender === 'male' ? '#e3f2fd' : '#fce4ec'
      }
    }))

    // 创建边
    const edges: any[] = []

    // 添加父子关系边
    members.forEach(member => {
      if (member.parentId) {
        edges.push({
          source: member.parentId,
          target: member.id
        })
      }
    })

    this.data = { nodes, edges }
    this.graph.data(this.data)
    this.graph.render()
    this.graph.fitView()
  }

  public updateLayout() {
    if (!this.graph) return
    this.graph.updateLayout()
    this.graph.fitView()
  }

  public resize(width: number, height: number) {
    if (!this.graph) return
    this.graph.changeSize(width, height)
    this.graph.fitView()
  }

  public destroy() {
    if (this.graph) {
      this.graph.destroy()
      this.graph = null
    }
  }
}

export default FamilyGraph