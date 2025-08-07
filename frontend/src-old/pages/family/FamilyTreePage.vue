<template>
  <div class="family-tree-page">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-left">
        <el-button 
          type="text" 
          :icon="ArrowLeft" 
          @click="goBack"
          class="back-btn"
        >
          返回
        </el-button>
        <div class="nav-title">
          <h1>{{ familyStore.currentFamilyName || '张氏家族' }}</h1>
          <span class="nav-subtitle">族谱图</span>
        </div>
      </div>
      
      <div class="nav-center">
        <el-input
          v-model="searchQuery"
          placeholder="搜索成员姓名..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
      </div>
      
      <div class="nav-right">
        <el-button-group class="view-controls">
          <el-button 
            :type="showRelationships ? 'primary' : ''"
            :icon="Connection"
            @click="toggleRelationships"
          >
            {{ showRelationships ? '隐藏关系' : '显示关系' }}
          </el-button>
          <el-button 
            :icon="ZoomIn"
            @click="zoomIn"
          />
          <el-button 
            :icon="ZoomOut"
            @click="zoomOut"
          />
          <el-button 
            :icon="Refresh"
            @click="resetZoom"
          />
          <el-button 
            :icon="FullScreen"
            @click="toggleFullscreen"
          />
        </el-button-group>
        
        <el-dropdown @command="handleCommand" class="more-actions">
          <el-button type="primary">
            更多操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="share" :icon="Share">分享族谱</el-dropdown-item>
              <el-dropdown-item command="export" :icon="Download">导出图片</el-dropdown-item>
              <el-dropdown-item command="print" :icon="Printer">打印</el-dropdown-item>
              <el-dropdown-item command="settings" :icon="Setting">设置</el-dropdown-item>
              <el-dropdown-item command="invite" :icon="UserPlus">邀请成员</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 左侧边栏 -->
      <aside 
        :class="['sidebar', { collapsed: !sidebarOpen }]"
        id="sidebar"
      >
        <div class="sidebar-header">
          <h3 v-show="sidebarOpen">成员列表</h3>
          <el-button 
            text 
            @click="toggleSidebar"
            class="sidebar-toggle"
            :title="sidebarOpen ? '收起' : '展开'"
          >
            <el-icon>
              <component :is="sidebarOpen ? 'ArrowLeft' : 'ArrowRight'" />
            </el-icon>
          </el-button>
        </div>
        
        <div v-show="sidebarOpen" class="sidebar-content">
          <!-- 筛选器 -->
          <div class="filter-section">
            <h4>筛选</h4>
            <div class="filter-group">
              <label>世代:</label>
              <div class="filter-tags">
                <span 
                  v-for="gen in generations"
                  :key="gen"
                  :class="['filter-tag', { active: selectedGeneration === gen }]"
                  @click="filterByGeneration(gen)"
                >
                  {{ gen === 0 ? '全部' : `第${gen}代` }}
                </span>
              </div>
            </div>
            
            <div class="filter-group">
              <label>性别:</label>
              <div class="filter-tags">
                <span 
                  :class="['filter-tag', { active: selectedGender === 'all' }]"
                  @click="filterByGender('all')"
                >
                  全部
                </span>
                <span 
                  :class="['filter-tag', { active: selectedGender === 'male' }]"
                  @click="filterByGender('male')"
                >
                  男性
                </span>
                <span 
                  :class="['filter-tag', { active: selectedGender === 'female' }]"
                  @click="filterByGender('female')"
                >
                  女性
                </span>
              </div>
            </div>
          </div>
          
          <!-- 成员列表 -->
          <div class="members-list">
            <div class="list-header">
              <h4>成员 ({{ filteredMembers.length }})</h4>
              <el-button 
                type="primary" 
                size="small"
                :icon="Plus"
                @click="showAddMemberDialog"
              >
                添加
              </el-button>
            </div>
            
            <div class="member-items">
              <div 
                v-for="member in filteredMembers"
                :key="member.id"
                :class="['member-item', { selected: selectedMember?.id === member.id }]"
                @click="selectMember(member)"
              >
                <div class="member-avatar">
                  {{ member.name.charAt(0) }}
                </div>
                <div class="member-info">
                  <div class="member-name">{{ member.name }}</div>
                  <div class="member-details">
                    <span>{{ formatDateRange(member.birthDate, member.deathDate) }}</span>
                    <span class="member-generation">第{{ member.generation }}代</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 图形区域 -->
      <section class="graph-area">
        <div 
          ref="graphContainer"
          class="graph-container"
          id="graphContainer"
        >
          <div 
            ref="familyTree"
            :class="['family-tree', { 'show-relationships': showRelationships }]"
            :style="{ transform: `scale(${currentZoom})` }"
            id="familyTree"
          >
            <!-- 世代渲染 -->
            <div 
              v-for="generation in visibleGenerations"
              :key="generation.number"
              class="generation"
              :data-generation="generation.number"
            >
              <div class="generation-label">
                {{ generation.label }}
              </div>
              <div class="node-group">
                <!-- 渲染该世代的成员 -->
                <template v-for="group in generation.groups" :key="group.id">
                  <!-- 夫妻组 -->
                  <div v-if="group.type === 'couple'" class="couple-group">
                    <div 
                      v-for="member in group.members"
                      :key="member.id"
                      :class="[
                        'family-node', 
                        member.gender,
                        'animate-fade-in-up',
                        { selected: selectedMember?.id === member.id }
                      ]"
                      :style="{ animationDelay: `${member.animationDelay}s` }"
                      :data-member-id="member.id"
                      :data-parent="member.parentId"
                      :data-spouse="member.spouseId"
                      @click="showMemberDetail(member)"
                    >
                      <div class="node-avatar">{{ member.name.charAt(0) }}</div>
                      <div class="node-name">{{ member.name }}</div>
                      <div class="node-dates">{{ formatDateRange(member.birthDate, member.deathDate) }}</div>
                      <div class="node-generation">第{{ member.generation }}代</div>
                    </div>
                  </div>
                  
                  <!-- 单身成员 -->
                  <div 
                    v-else
                    :class="[
                      'family-node', 
                      group.member.gender,
                      'animate-fade-in-up',
                      { selected: selectedMember?.id === group.member.id }
                    ]"
                    :style="{ animationDelay: `${group.member.animationDelay}s` }"
                    :data-member-id="group.member.id"
                    :data-parent="group.member.parentId"
                    @click="showMemberDetail(group.member)"
                  >
                    <div class="node-avatar">{{ group.member.name.charAt(0) }}</div>
                    <div class="node-name">{{ group.member.name }}</div>
                    <div class="node-dates">{{ formatDateRange(group.member.birthDate, group.member.deathDate) }}</div>
                    <div class="node-generation">第{{ group.member.generation }}代</div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-item">
        <span>当前显示:</span>
        <span class="status-value">{{ statusDisplay }}</span>
      </div>
      <div class="status-item">
        <span>总成员数:</span>
        <span class="status-value">{{ totalMembers }}人</span>
      </div>
      <div class="status-item">
        <span>缩放比例:</span>
        <span class="status-value">{{ Math.round(currentZoom * 100) }}%</span>
      </div>
      <div class="status-item">
        <span>关系显示:</span>
        <span class="status-value">{{ showRelationships ? '显示' : '隐藏' }}</span>
      </div>
    </div>

    <!-- 成员详情对话框 -->
    <el-dialog 
      v-model="memberDetailVisible"
      :title="selectedMember?.name || '成员详情'"
      width="500px"
      class="member-detail-dialog"
    >
      <div v-if="selectedMember" class="member-detail-content">
        <div class="member-header">
          <div class="member-avatar-large">
            {{ selectedMember.name.charAt(0) }}
          </div>
          <div class="member-basic-info">
            <h3>{{ selectedMember.name }}</h3>
            <p class="member-dates">{{ formatDateRange(selectedMember.birthDate, selectedMember.deathDate) }}</p>
            <el-tag :type="selectedMember.gender === 'male' ? 'primary' : 'danger'">
              {{ selectedMember.gender === 'male' ? '男' : '女' }}
            </el-tag>
            <el-tag type="info">第{{ selectedMember.generation }}代</el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <div class="member-relationships">
          <h4>家庭关系</h4>
          <div class="relationship-item" v-if="selectedMember.spouse">
            <label>配偶:</label>
            <span>{{ selectedMember.spouse.name }}</span>
          </div>
          <div class="relationship-item" v-if="selectedMember.parents?.length">
            <label>父母:</label>
            <span>{{ selectedMember.parents.map(p => p.name).join(', ') }}</span>
          </div>
          <div class="relationship-item" v-if="selectedMember.children?.length">
            <label>子女:</label>
            <span>{{ selectedMember.children.map(c => c.name).join(', ') }}</span>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="memberDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="editMember">编辑信息</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加成员对话框 -->
    <el-dialog 
      v-model="addMemberDialogVisible"
      title="添加成员"
      width="600px"
    >
      <el-form 
        ref="addMemberFormRef"
        :model="newMemberForm"
        :rules="addMemberRules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="newMemberForm.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="newMemberForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="出生日期">
          <el-date-picker 
            v-model="newMemberForm.birthDate"
            type="date"
            placeholder="选择出生日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="逝世日期">
          <el-date-picker 
            v-model="newMemberForm.deathDate"
            type="date"
            placeholder="选择逝世日期（可选）"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="关系类型" prop="relationshipType">
          <el-select v-model="newMemberForm.relationshipType" placeholder="选择关系类型">
            <el-option label="父亲" value="father" />
            <el-option label="母亲" value="mother" />
            <el-option label="儿子" value="son" />
            <el-option label="女儿" value="daughter" />
            <el-option label="配偶" value="spouse" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关联成员" v-if="newMemberForm.relationshipType">
          <el-select 
            v-model="newMemberForm.relatedMemberId"
            placeholder="选择关联的成员"
            filterable
          >
            <el-option 
              v-for="member in availableRelatedMembers"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addMemberDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddMember">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { 
  ArrowDown, 
  ArrowLeft, 
  ArrowRight,
  Search, 
  Connection, 
  ZoomIn, 
  ZoomOut, 
  Refresh, 
  FullScreen,
  Share,
  Download,
  Printer,
  Setting,
  UserPlus,
  Plus
} from '@element-plus/icons-vue'
import { useFamilyStore } from '@/stores/family'

// 接口定义
interface FamilyMember {
  id: number
  name: string
  gender: 'male' | 'female'
  birthDate?: string
  deathDate?: string
  generation: number
  parentId?: number
  spouseId?: number
  animationDelay?: number
  spouse?: FamilyMember
  parents?: FamilyMember[]
  children?: FamilyMember[]
}

interface GenerationGroup {
  id: string
  type: 'couple' | 'single'
  members?: FamilyMember[]
  member?: FamilyMember
}

interface Generation {
  number: number
  label: string
  groups: GenerationGroup[]
}

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const familyStore = useFamilyStore()

// 响应式数据
const graphContainer = ref<HTMLElement>()
const familyTree = ref<HTMLElement>()
const addMemberFormRef = ref<FormInstance>()

// 基础状态
const searchQuery = ref('')
const selectedMember = ref<FamilyMember | null>(null)
const sidebarOpen = ref(true)
const showRelationships = ref(false)
const currentZoom = ref(1)
const memberDetailVisible = ref(false)
const addMemberDialogVisible = ref(false)

// 筛选状态
const selectedGeneration = ref(0)
const selectedGender = ref<'all' | 'male' | 'female'>('all')

// 表单数据
const newMemberForm = reactive({
  name: '',
  gender: 'male' as 'male' | 'female',
  birthDate: '',
  deathDate: '',
  relationshipType: '',
  relatedMemberId: null as number | null
})

// 表单验证规则
const addMemberRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  relationshipType: [
    { required: true, message: '请选择关系类型', trigger: 'change' }
  ]
}

// 示例数据
const familyMembers = ref<FamilyMember[]>([
  {
    id: 1,
    name: '张德明',
    gender: 'male',
    birthDate: '1368-01-01',
    deathDate: '1435-12-31',
    generation: 1,
    spouseId: 2,
    animationDelay: 0.1
  },
  {
    id: 2,
    name: '李氏',
    gender: 'female',
    birthDate: '1372-01-01',
    deathDate: '1438-12-31',
    generation: 1,
    spouseId: 1,
    animationDelay: 0.2
  },
  {
    id: 3,
    name: '张文华',
    gender: 'male',
    birthDate: '1395-01-01',
    deathDate: '1468-12-31',
    generation: 2,
    parentId: 1,
    spouseId: 5,
    animationDelay: 0.3
  },
  {
    id: 4,
    name: '张文武',
    gender: 'male',
    birthDate: '1398-01-01',
    deathDate: '1471-12-31',
    generation: 2,
    parentId: 1,
    animationDelay: 0.4
  },
  {
    id: 5,
    name: '王氏',
    gender: 'female',
    birthDate: '1400-01-01',
    deathDate: '1475-12-31',
    generation: 2,
    spouseId: 3,
    animationDelay: 0.5
  },
  {
    id: 6,
    name: '张志远',
    gender: 'male',
    birthDate: '1420-01-01',
    deathDate: '1489-12-31',
    generation: 3,
    parentId: 3,
    spouseId: 8,
    animationDelay: 0.6
  },
  {
    id: 7,
    name: '张志高',
    gender: 'male',
    birthDate: '1422-01-01',
    deathDate: '1491-12-31',
    generation: 3,
    parentId: 3,
    animationDelay: 0.7
  },
  {
    id: 8,
    name: '赵氏',
    gender: 'female',
    birthDate: '1425-01-01',
    deathDate: '1494-12-31',
    generation: 3,
    spouseId: 6,
    animationDelay: 0.8
  },
  {
    id: 9,
    name: '张明德',
    gender: 'male',
    birthDate: '1445-01-01',
    deathDate: '1520-12-31',
    generation: 4,
    parentId: 6,
    spouseId: 11,
    animationDelay: 0.9
  },
  {
    id: 10,
    name: '张明智',
    gender: 'male',
    birthDate: '1448-01-01',
    deathDate: '1523-12-31',
    generation: 4,
    parentId: 6,
    animationDelay: 1.0
  },
  {
    id: 11,
    name: '刘氏',
    gender: 'female',
    birthDate: '1450-01-01',
    deathDate: '1525-12-31',
    generation: 4,
    spouseId: 9,
    animationDelay: 1.1
  },
  {
    id: 12,
    name: '张明礼',
    gender: 'male',
    birthDate: '1452-01-01',
    deathDate: '1527-12-31',
    generation: 4,
    parentId: 7,
    animationDelay: 1.2
  },
  {
    id: 13,
    name: '张建国',
    gender: 'male',
    birthDate: '1970-01-01',
    generation: 5,
    parentId: 9,
    spouseId: 14,
    animationDelay: 1.3
  },
  {
    id: 14,
    name: '李美华',
    gender: 'female',
    birthDate: '1975-01-01',
    generation: 5,
    spouseId: 13,
    animationDelay: 1.4
  },
  {
    id: 15,
    name: '张建华',
    gender: 'male',
    birthDate: '1972-01-01',
    generation: 5,
    parentId: 10,
    animationDelay: 1.5
  }
])

// 计算属性
const generations = computed(() => {
  const gens = new Set(familyMembers.value.map(m => m.generation))
  return [0, ...Array.from(gens).sort()]
})

const filteredMembers = computed(() => {
  let members = familyMembers.value

  // 按世代筛选
  if (selectedGeneration.value > 0) {
    members = members.filter(m => m.generation === selectedGeneration.value)
  }

  // 按性别筛选
  if (selectedGender.value !== 'all') {
    members = members.filter(m => m.gender === selectedGender.value)
  }

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    members = members.filter(m => m.name.toLowerCase().includes(query))
  }

  return members
})

const visibleGenerations = computed(() => {
  const generationMap = new Map<number, FamilyMember[]>()
  
  // 按世代分组
  filteredMembers.value.forEach(member => {
    if (!generationMap.has(member.generation)) {
      generationMap.set(member.generation, [])
    }
    generationMap.get(member.generation)!.push(member)
  })

  // 构建世代数据
  const generations: Generation[] = []
  
  for (const [genNumber, members] of generationMap.entries()) {
    const groups: GenerationGroup[] = []
    const processedIds = new Set<number>()
    
    members.forEach(member => {
      if (processedIds.has(member.id)) return
      
      // 检查是否有配偶
      const spouse = member.spouseId ? members.find(m => m.id === member.spouseId) : null
      
      if (spouse && !processedIds.has(spouse.id)) {
        // 夫妻组
        groups.push({
          id: `couple-${member.id}-${spouse.id}`,
          type: 'couple',
          members: [member, spouse]
        })
        processedIds.add(member.id)
        processedIds.add(spouse.id)
      } else if (!processedIds.has(member.id)) {
        // 单身成员
        groups.push({
          id: `single-${member.id}`,
          type: 'single',
          member
        })
        processedIds.add(member.id)
      }
    })
    
    generations.push({
      number: genNumber,
      label: getGenerationLabel(genNumber),
      groups
    })
  }
  
  return generations.sort((a, b) => a.number - b.number)
})

const totalMembers = computed(() => familyMembers.value.length)

const statusDisplay = computed(() => {
  if (selectedGeneration.value > 0) {
    return `第${selectedGeneration.value}代`
  }
  return '全部世代'
})

const availableRelatedMembers = computed(() => {
  return familyMembers.value.filter(m => m.id !== selectedMember.value?.id)
})

// 工具函数
function getGenerationLabel(generation: number): string {
  const labels = {
    1: '第一代 · 始祖',
    2: '第二代 · 承继',
    3: '第三代 · 发展',
    4: '第四代 · 繁荣',
    5: '第五代 · 传承'
  }
  return labels[generation as keyof typeof labels] || `第${generation}代`
}

function formatDateRange(birthDate?: string, deathDate?: string): string {
  if (!birthDate && !deathDate) return '未知'
  
  const birth = birthDate ? birthDate.split('-')[0] : '?'
  const death = deathDate ? deathDate.split('-')[0] : ''
  
  return death ? `${birth}-${death}` : `${birth}-`
}

// 事件处理函数
function goBack() {
  router.back()
}

function handleSearch() {
  // 搜索逻辑已在计算属性中实现
}

function toggleRelationships() {
  showRelationships.value = !showRelationships.value
  ElMessage.info(showRelationships.value ? '已显示关系线' : '已隐藏关系线')
}

function zoomIn() {
  currentZoom.value = Math.min(currentZoom.value + 0.1, 3)
}

function zoomOut() {
  currentZoom.value = Math.max(currentZoom.value - 0.1, 0.3)
}

function resetZoom() {
  currentZoom.value = 1
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

function handleCommand(command: string) {
  switch (command) {
    case 'share':
      shareFamily()
      break
    case 'export':
      exportFamily()
      break
    case 'print':
      window.print()
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'invite':
      ElMessage.info('邀请功能开发中...')
      break
  }
}

function shareFamily() {
  if (navigator.share) {
    navigator.share({
      title: '张氏家族族谱',
      text: '查看我们的家族族谱',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      ElMessage.success('链接已复制到剪贴板')
    })
  }
}

function exportFamily() {
  ElMessage.info('导出功能开发中...')
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function filterByGeneration(generation: number) {
  selectedGeneration.value = generation
}

function filterByGender(gender: 'all' | 'male' | 'female') {
  selectedGender.value = gender
}

function selectMember(member: FamilyMember) {
  selectedMember.value = member
  
  // 高亮对应的族谱节点
  const node = document.querySelector(`[data-member-id="${member.id}"]`)
  if (node) {
    node.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

function showMemberDetail(member: FamilyMember) {
  // 构建关系信息
  const memberWithRelations = {
    ...member,
    spouse: member.spouseId ? familyMembers.value.find(m => m.id === member.spouseId) : undefined,
    parents: familyMembers.value.filter(m => m.id === member.parentId),
    children: familyMembers.value.filter(m => m.parentId === member.id)
  }
  
  selectedMember.value = memberWithRelations
  memberDetailVisible.value = true
}

function showAddMemberDialog() {
  // 重置表单
  Object.assign(newMemberForm, {
    name: '',
    gender: 'male',
    birthDate: '',
    deathDate: '',
    relationshipType: '',
    relatedMemberId: null
  })
  
  addMemberDialogVisible.value = true
}

function confirmAddMember() {
  addMemberFormRef.value?.validate((valid) => {
    if (valid) {
      // 生成新ID
      const newId = Math.max(...familyMembers.value.map(m => m.id)) + 1
      
      // 计算世代
      let generation = 1
      if (newMemberForm.relatedMemberId) {
        const relatedMember = familyMembers.value.find(m => m.id === newMemberForm.relatedMemberId)
        if (relatedMember) {
          if (['son', 'daughter'].includes(newMemberForm.relationshipType)) {
            generation = relatedMember.generation + 1
          } else if (['father', 'mother'].includes(newMemberForm.relationshipType)) {
            generation = relatedMember.generation - 1
          } else {
            generation = relatedMember.generation
          }
        }
      }
      
      // 创建新成员
      const newMember: FamilyMember = {
        id: newId,
        name: newMemberForm.name,
        gender: newMemberForm.gender,
        birthDate: newMemberForm.birthDate || undefined,
        deathDate: newMemberForm.deathDate || undefined,
        generation,
        animationDelay: familyMembers.value.length * 0.1
      }
      
      // 设置关系
      if (newMemberForm.relatedMemberId) {
        if (['son', 'daughter'].includes(newMemberForm.relationshipType)) {
          newMember.parentId = newMemberForm.relatedMemberId
        } else if (newMemberForm.relationshipType === 'spouse') {
          newMember.spouseId = newMemberForm.relatedMemberId
          // 更新配偶的关系
          const spouse = familyMembers.value.find(m => m.id === newMemberForm.relatedMemberId)
          if (spouse) {
            spouse.spouseId = newId
          }
        }
      }
      
      familyMembers.value.push(newMember)
      addMemberDialogVisible.value = false
      ElMessage.success('成员添加成功')
    }
  })
}

function editMember() {
  ElMessage.info('编辑成员功能开发中...')
}

// 生命周期
onMounted(() => {
  const familyId = route.params.id
  console.log('加载族谱:', familyId)
  
  // 添加键盘快捷键
  document.addEventListener('keydown', handleKeydown)
})

function handleKeydown(e: KeyboardEvent) {
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case '=':
      case '+':
        e.preventDefault()
        zoomIn()
        break
      case '-':
        e.preventDefault()
        zoomOut()
        break
      case '0':
        e.preventDefault()
        resetZoom()
        break
      case 'f':
        e.preventDefault()
        toggleFullscreen()
        break
      case 'r':
        e.preventDefault()
        toggleRelationships()
        break
    }
  }
  
  if (e.key === 'Escape') {
    memberDetailVisible.value = false
    addMemberDialogVisible.value = false
  }
}
</script>

<style scoped>
/* 全局样式 */
.family-tree-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 顶部导航栏 */
.top-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
}

.nav-title h1 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.nav-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.nav-center {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 250px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__inner) {
  color: white;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

.search-input :deep(.el-input__wrapper:focus) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-controls .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
}

.view-controls .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.more-actions .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar.collapsed {
  width: 60px;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.sidebar-toggle {
  padding: 4px;
  min-height: auto;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 筛选器 */
.filter-section {
  margin-bottom: 24px;
}

.filter-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
}

.filter-group {
  margin-bottom: 16px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  display: block;
  margin-bottom: 8px;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-tag {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tag:hover {
  background: #e5e7eb;
}

.filter-tag.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* 成员列表 */
.members-list {
  flex: 1;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.list-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.member-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.member-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
  font-size: 14px;
}

.member-details {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-generation {
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
}

/* 图形区域 */
.graph-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  position: relative;
}

.graph-container {
  flex: 1;
  overflow: auto;
  position: relative;
  background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%),
              linear-gradient(-45deg, #f8f9fa 25%, transparent 25%),
              linear-gradient(45deg, transparent 75%, #f8f9fa 75%),
              linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

.family-tree {
  padding: 40px;
  min-width: 100%;
  min-height: 100%;
  transform-origin: top left;
  transition: transform 0.3s ease;
}

/* 世代样式 */
.generation {
  margin-bottom: 60px;
  animation: fadeInUp 0.6s ease-out;
}

.generation-label {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  margin-bottom: 30px;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.node-group {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  flex-wrap: wrap;
  justify-content: center;
  min-height: 280px;
}

/* 夫妻组样式 */
.couple-group {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 8px;
  position: relative;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  align-self: flex-end;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.couple-group:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.couple-group::after {
  content: '💕';
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff6b6b;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

/* 家庭成员节点样式 */
.family-node {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  width: 160px;
  align-self: flex-end;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: fadeInScale 0.6s ease-out;
}

.family-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.family-node.male {
  border-color: #3b82f6;
}

.family-node.female {
  border-color: #ec4899;
}

.family-node.selected {
  border-color: #10b981;
  background: #f0fdf4;
}

.node-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.family-node.male .node-avatar {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.family-node.female .node-avatar {
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
}

.node-name {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.node-dates {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.node-generation {
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
}

/* 状态栏 */
.status-bar {
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  padding: 8px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-value {
  font-weight: 500;
  color: #374151;
}

/* 成员详情对话框 */
.member-detail-dialog :deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

.member-detail-content {
  padding: 24px;
}

.member-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.member-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: 600;
  flex-shrink: 0;
}

.member-basic-info h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #374151;
}

.member-dates {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.member-relationships h4 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
}

.relationship-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.relationship-item:last-child {
  border-bottom: none;
}

.relationship-item label {
  color: #6b7280;
  font-weight: 500;
  width: 60px;
  margin-right: 12px;
}

.relationship-item span {
  color: #374151;
  font-weight: 500;
}

/* 添加成员对话框 */
.add-member-form {
  padding: 24px;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 280px;
  }
  
  .search-input {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    z-index: 100;
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .nav-center {
    display: none;
  }
  
  .family-tree {
    padding: 20px;
  }
  
  .node-group {
    gap: 16px;
  }
  
  .family-node {
    width: 140px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>