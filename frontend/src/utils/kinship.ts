import relationship from 'relationship.js'
import { FamilyMember } from '@/types/family'

// relationship.js 类型定义
interface RelationshipOptions {
  text: string
  sex: 0 | 1 // 0: female, 1: male
  reverse?: boolean
  type?: 'default' | 'chain' | 'pair'
}

export class KinshipCalculator {
  private membersMap: Map<string, FamilyMember>
  private graph: Map<string, Array<{target: string, type: 'parent' | 'child' | 'spouse'}>>

  constructor(members: FamilyMember[]) {
    this.membersMap = new Map(members.map(m => [String(m.id), m]))
    this.graph = this.buildGraph(members)
  }

  private buildGraph(members: FamilyMember[]) {
    const graph = new Map<string, Array<{target: string, type: 'parent' | 'child' | 'spouse'}>>()
    
    const addEdge = (from: string, to: string, type: 'parent' | 'child' | 'spouse') => {
      const fromStr = String(from)
      const toStr = String(to)
      if (!graph.has(fromStr)) graph.set(fromStr, [])
      graph.get(fromStr)!.push({ target: toStr, type })
    }

    members.forEach(m => {
      // Parent relationship
      if (m.parentId) {
        // m is child of parentId
        // edge: m -> parent -> parentId
        addEdge(m.id, m.parentId, 'parent')
        // edge: parentId -> child -> m
        addEdge(m.parentId, m.id, 'child')
      }
      // Spouse relationship
      if (m.spouseId) {
        addEdge(m.id, m.spouseId, 'spouse')
        addEdge(m.spouseId, m.id, 'spouse')
      }
    })
    return graph
  }

  public calculateAll(centerId: string): Record<string, string> {
    const results: Record<string, string> = {}
    const centerIdStr = String(centerId)
    
    // BFS to find all reachable nodes
    const paths = this.findAllPaths(centerIdStr)
    
    paths.forEach((path, targetId) => {
      if (targetId === centerIdStr) {
        results[targetId] = '本人'
        return
      }
      
      const relText = this.convertPathToText(centerIdStr, path)
      if (relText) {
        const centerMember = this.membersMap.get(centerIdStr)
        const options: RelationshipOptions = {
          text: relText,
          sex: centerMember?.gender === 'male' ? 1 : 0,
        }
        
        try {
          const names = relationship(options)
          if (names && names.length > 0) {
            results[targetId] = names[0]
          }
        } catch (e) {
          console.error('Kinship calculation error:', e)
        }
      }
    })
    
    return results
  }

  private findAllPaths(startId: string): Map<string, Array<{target: string, type: string}>> {
    const paths = new Map<string, Array<{target: string, type: string}>>()
    const queue: Array<{id: string, path: Array<{target: string, type: string}>}> = []
    const visited = new Set<string>()

    queue.push({ id: startId, path: [] })
    visited.add(startId)
    paths.set(startId, [])

    while (queue.length > 0) {
      const { id, path } = queue.shift()!
      
      // 限制搜索深度，防止性能问题
      if (path.length > 10) continue

      const neighbors = this.graph.get(id) || []
      for (const edge of neighbors) {
        if (!visited.has(edge.target)) {
          visited.add(edge.target)
          const newPath = [...path, edge]
          paths.set(edge.target, newPath)
          queue.push({ id: edge.target, path: newPath })
        }
      }
    }
    
    return paths
  }

  private convertPathToText(startId: string, path: Array<{target: string, type: string}>): string {
    const parts: string[] = []
    
    // 我们需要追踪路径上的"当前人"和"上一个人"，以便检测同胞关系
    let currentId = startId
    let prevId: string | null = null
    let prevType: string | null = null

    for (let i = 0; i < path.length; i++) {
      const step = path[i]
      const targetMember = this.membersMap.get(step.target)
      const currentMember = this.membersMap.get(currentId) // 这是 step 的出发点（即父亲/母亲）
      
      if (!targetMember || !currentMember) return ''
      
      const isMale = targetMember.gender === 'male'
      
      // 检测同胞关系模式：parent -> child
      // 上一步是 parent (说明 currentMember 是 prevMember 的父母)
      // 这一步是 child (说明 targetMember 也是 currentMember 的孩子)
      // 那么 prevMember 和 targetMember 是兄弟姐妹
      // 注意：这里我们需要知道 prevMember 是谁。
      // 在 i=0 时，prevMember 是 startId (如果是 parent->child，说明 target 是 start 的兄弟)
      // 等等，i=0 时，currentId=startId。step.type='parent'。currentId 变成 targetId。
      // i=1 时，currentId=Parent。step.type='child'。targetId=Sibling。
      // 此时 prevType='parent', step.type='child'。
      // 确实是 父亲的儿子 -> 兄弟。
      
      let term = ''
      
      switch (step.type) {
        case 'parent':
          term = isMale ? '父亲' : '母亲'
          break
        case 'spouse':
          term = isMale ? '丈夫' : '妻子'
          break
        case 'child':
          // 默认是 儿子/女儿
          term = isMale ? '儿子' : '女儿'
          
          // 尝试优化为 哥哥/弟弟/姐姐/妹妹
          if (prevType === 'parent' && prevId) {
             const prevMember = this.membersMap.get(prevId)
             if (prevMember) {
               // 比较 prevMember 和 targetMember 的年龄
               const isOlder = this.compareAge(targetMember, prevMember) > 0
               if (isMale) {
                 term = isOlder ? '哥哥' : '弟弟'
               } else {
                 term = isOlder ? '姐姐' : '妹妹'
               }
               // 此时，我们需要修改 parts 的最后一个元素
               // 因为 "父亲" + "哥哥" = "父亲的哥哥" (伯父)，这是不对的。
               // 应该是 "父亲的儿子" -> "哥哥"。
               // relationship.js 能够理解 "父亲的儿子" = "兄弟"。
               // 但如果直接给 "哥哥"，它能理解吗？
               // relationship.js 支持 "哥哥" 作为输入。
               // 但如果路径是 "父亲的哥哥"，那就是 "伯父"。
               // 我们的路径是 "我 -> 父亲 -> 哥哥"。
               // 如果 parts 是 ["父亲", "哥哥"]，relationship.js 会解析为 "父亲的哥哥" = 伯父。
               // 这就错了！因为这里的"哥哥"是相对于"我"的，而不是相对于"父亲"的。
               // 实际上，"父亲的儿子" 这个表达本身就模糊（可能是"我"，可能是"兄弟"）。
               
               // 关键点：relationship.js 是基于"链式呼叫"的。
               // "父亲的儿子" -> 这种链式无法表达"比我大的那个儿子"。
               // 除非 relationship.js 支持 "父亲的长子" 这种输入，但它不支持。
               
               // 换个思路：
               // 我们的 convertPathToText 生成的是 "父亲的父亲的..." 这种文本。
               // 如果我们要表达 "表嫂"，路径可能是 "母亲的哥哥的妻子"。
               // relationship.js 解析 "母亲的哥哥" -> "舅舅"。 "舅舅的妻子" -> "舅妈"。
               // 如果路径是 "母亲的哥哥的女儿" (表妹) "的丈夫" (表妹夫/表妹婿)。
               
               // 这里的核心难点是：如何区分 "舅舅" (母亲的哥哥) 和 "舅舅" (母亲的弟弟)？
               // 如果不区分，relationship.js 可能会统称为 "舅舅" 或 "舅父"。
               // 对于 "表嫂" (表哥的妻子)，我们需要先准确定位 "表哥"。
               // "表哥" = "母亲的兄弟的儿子" (且比我大)。
               
               // 方案：
               // 我们不能简单地替换 term。我们需要生成包含长幼信息的描述。
               // 但 relationship.js 的输入通过文本描述很难传达"比我大"这个信息，除非用特定的称谓。
               // 例如：用 "哥哥" 代替 "父亲的儿子"。
               // 但如前所述，直接拼 "父亲的哥哥" 会变成伯父。
               
               // 唯一的方法是：当检测到同胞关系时，不要 push "父亲" 和 "儿子"，
               // 而是直接合并这两步，生成一个 "哥哥" 放入 parts？
               // 不行，parts.join('的') 会变成 "哥哥"。
               // 如果前面还有路径呢？ "爷爷 -> 父亲 -> 哥哥"
               // "爷爷的哥哥" -> 伯公。这是对的。
               // 所以，如果能检测到 `parent -> child` 结构，并且确认是同胞，
               // 我们可以把这两个 step 合并为一个 "哥哥/弟弟/..." 的 step。
               
               // 让我们尝试实现这个合并逻辑。
             }
          }
          break
      }
      
      // 合并逻辑：如果当前是 child，且上一步是 parent，说明是同胞
      if (step.type === 'child' && prevType === 'parent' && parts.length > 0) {
        // 弹出上一步的 "父亲/母亲"
        parts.pop()
        // 此时 term 已经是 "儿子/女儿"，我们需要把它升级为 "哥哥/弟弟..."
        // 但注意，这里的比较对象是 prevMember (即"我"或路径上的上一个人)
        if (prevId) {
             const prevMember = this.membersMap.get(prevId)
             if (prevMember && targetMember.id !== prevMember.id) { // 排除自己
               const isOlder = this.compareAge(targetMember, prevMember) > 0
               if (isMale) {
                 term = isOlder ? '哥哥' : '弟弟'
               } else {
                 term = isOlder ? '姐姐' : '妹妹'
               }
               // push 新的 term
               parts.push(term)
             } else {
               // 如果是自己（父亲的儿子是我），这在路径中不应该出现（除非环路），或者直接忽略
               // 我们的路径算法应该不会包含"回头路"到自己，除非成环。
               // 如果真的回到了自己，就忽略这一对 parent-child
             }
        }
      } else {
        parts.push(term)
      }

      prevId = currentId
      prevType = step.type
      currentId = step.target
    }
    
    return parts.join('的')
  }

  private compareAge(m1: FamilyMember, m2: FamilyMember): number {
    // 返回 1 if m1 > m2 (m1 is older), -1 if m1 < m2, 0 if unknown
    // 注意：birthDate 越小，年龄越大
    if (!m1.birthDate || !m2.birthDate) return 0
    const d1 = new Date(m1.birthDate).getTime()
    const d2 = new Date(m2.birthDate).getTime()
    return d1 < d2 ? 1 : -1
  }

  public getBirthOrder(memberId: string): string {
    const member = this.membersMap.get(String(memberId))
    if (!member || !member.parentId) return ''
    
    // Find all siblings (children of the same parent)
    const parentId = String(member.parentId)
    const siblings: FamilyMember[] = []
    
    // Iterate over all members to find those with the same parentId
    this.membersMap.forEach(m => {
      if (String(m.parentId) === parentId) {
        siblings.push(m)
      }
    })
    
    if (siblings.length <= 1) return '独生子女'
    
    // Sort by birth date
    siblings.sort((a, b) => {
      if (!a.birthDate) return 1
      if (!b.birthDate) return -1
      return new Date(a.birthDate).getTime() - new Date(b.birthDate).getTime()
    })
    
    // Filter by gender to determine "Eldest Son", "Second Daughter", etc.
    const sameGenderSiblings = siblings.filter(s => s.gender === member.gender)
    const index = sameGenderSiblings.findIndex(s => String(s.id) === String(member.id))
    
    if (index === -1) return ''
    
    const isMale = member.gender === 'male'
    const orderNames = ['长', '次', '三', '四', '五', '六', '七', '八', '九', '十']
    const suffix = isMale ? '子' : '女'
    
    if (index < orderNames.length) {
      return orderNames[index] + suffix
    }
    
    return `第${index + 1}${suffix}`
  }
}
