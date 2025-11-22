<template>
  <div class="family-tree-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <button 
          class="back-btn" 
          @click="goBack"
          title="返回"
        >
          ←
        </button>
        <h1 class="page-title">
          <span class="title-icon">🌳</span>
          {{ familyStore.currentFamily?.name || '族谱' }}
        </h1>
      </div>
      
      <div class="header-right">
        <button class="header-btn" @click="openSettings">
          <span>⚙️</span>
          设置
        </button>
        <button class="header-btn" @click="shareFamily">
          <span>📤</span>
          分享
        </button>
        <button class="header-btn primary" @click="showAddMemberDialog = true">
          <span>➕</span>
          添加成员
        </button>
      </div>
    </header>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-section">
        <div class="toolbar-group">
          <span class="toolbar-label">世代</span>
          <el-select 
            v-model="selectedGeneration" 
            placeholder="选择世代"
            size="small"
            style="width: 120px"
            @change="handleGenerationChange"
          >
            <el-option label="全部世代" value="all" />
            <el-option 
              v-for="gen in availableGenerations" 
              :key="gen" 
              :label="`第${gen}代`"
              :value="gen"
            />
          </el-select>
        </div>
        
        <div class="toolbar-group">
          <span class="toolbar-label">搜索</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索家族成员..."
            size="small"
            style="width: 240px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <el-button 
          type="primary"
          size="small"
          :class="{ 'relationship-toggle': true, active: familyStore.relationshipsVisible }"
          @click="familyStore.toggleRelationships()"
        >
          <el-icon><Connection /></el-icon>
          {{ familyStore.relationshipsVisible ? '隐藏关系' : '显示关系' }}
        </el-button>
        
        <el-button 
          size="small"
          @click="openRelationshipQuery"
        >
          <el-icon><Search /></el-icon>
          称呼查询
        </el-button>
      </div>
      
      <div class="toolbar-section">
        <el-button-group>
          <el-button size="small" @click="familyStore.zoomOut()">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
          <el-button size="small" @click="familyStore.resetZoom()">
            {{ Math.round(familyStore.zoomLevel * 100) }}%
          </el-button>
          <el-button size="small" @click="familyStore.zoomIn()">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
        </el-button-group>
        
        <div class="toolbar-group">
          <span class="toolbar-label">导出</span>
          <el-select 
            placeholder="选择格式"
            size="small"
            style="width: 120px"
            @change="handleExport"
          >
            <el-option label="PNG图片" value="png" />
            <el-option label="PDF文档" value="pdf" />
            <el-option label="Excel表格" value="excel" />
          </el-select>
        </div>
        
        <el-button-group>
          <el-button size="small" @click="fitToScreen" title="适应屏幕">
            <el-icon><FullScreen /></el-icon>
          </el-button>
          <el-button size="small" @click="centerGraph" title="居中显示">
            <el-icon><Aim /></el-icon>
          </el-button>
          <el-button size="small" @click="toggleFullscreen" title="全屏">
            <el-icon><ScaleToOriginal /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 侧边栏 -->
      <aside 
        class="sidebar" 
        :class="{ collapsed: familyStore.sidebarCollapsed }"
      >
        <button 
          class="sidebar-toggle" 
          @click="familyStore.toggleSidebar()"
          :title="familyStore.sidebarCollapsed ? '展开' : '收起'"
        >
          {{ familyStore.sidebarCollapsed ? '▶' : '◀' }}
        </button>
        
        <div class="sidebar-header" v-if="!familyStore.sidebarCollapsed">
          <!-- 族谱信息卡片 -->
          <div class="family-info-card">
            <h2 class="family-name">
              <div class="family-icon">{{ familyIcon }}</div>
              {{ familyStore.currentFamily?.name || '张氏家族' }}
            </h2>
            <p class="family-desc">
              {{ familyStore.currentFamily?.description || '源远流长的家族，历经数百年传承。' }}
            </p>
            <div class="family-stats">
              <div class="stat-item">
                <span class="stat-value">{{ familyStore.familyStats.totalMembers }}</span>
                <span class="stat-label">总人数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ familyStore.familyStats.generations }}</span>
                <span class="stat-label">世代数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ familyStore.familyStats.branches }}</span>
                <span class="stat-label">分支数</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="sidebar-content" v-if="!familyStore.sidebarCollapsed">
          <!-- 筛选器 -->
          <div class="filters-section">
            <h3 class="section-title">
              <el-icon><Filter /></el-icon>
              筛选器
            </h3>
            
            <div class="filter-group">
              <div class="filter-label">性别</div>
              <el-radio-group 
                v-model="familyStore.filters.gender" 
                size="small"
                @change="(value) => familyStore.setFilter('gender', value)"
              >
                <el-radio-button 
                  v-for="option in genderOptions" 
                  :key="option.value"
                  :label="option.value"
                >
                  {{ option.label }}
                </el-radio-button>
              </el-radio-group>
            </div>
            
            <div class="filter-group">
              <div class="filter-label">在世状态</div>
              <el-radio-group 
                v-model="familyStore.filters.status" 
                size="small"
                @change="(value) => familyStore.setFilter('status', value)"
              >
                <el-radio-button 
                  v-for="option in statusOptions" 
                  :key="option.value"
                  :label="option.value"
                >
                  {{ option.label }}
                </el-radio-button>
              </el-radio-group>
            </div>
            
            <div class="filter-group">
              <div class="filter-label">显示选项</div>
              <div class="display-options">
                <el-checkbox 
                  v-model="familyStore.showPhotos"
                  @change="familyStore.togglePhotos()"
                >
                  照片
                </el-checkbox>
                <el-checkbox 
                  v-model="familyStore.showDates"
                  @change="familyStore.toggleDates()"
                >
                  日期
                </el-checkbox>
                <el-checkbox 
                  v-model="familyStore.showGeneration"
                  @change="familyStore.toggleGenerationDisplay()"
                >
                  世代
                </el-checkbox>
              </div>
            </div>
          </div>
          
          <!-- 成员列表 -->
          <div class="members-section">
            <div class="members-header">
              <h3 class="section-title">
                <el-icon><User /></el-icon>
                家族成员
              </h3>
              <el-button 
                type="primary"
                size="small"
                @click="showAddMemberDialog = true"
              >
                <el-icon><Plus /></el-icon>
                添加成员
              </el-button>
            </div>
            
            <div class="members-list">
              <el-card 
                v-for="member in familyStore.filteredMembers" 
                :key="member.id"
                class="member-card" 
                :class="{ selected: familyStore.selectedMember?.id === member.id }"
                shadow="hover"
                @click="selectMember(member)"
              >
                <div class="member-content">
                  <el-avatar 
                    :size="40"
                    :src="member.photo"
                    class="member-avatar"
                  >
                    {{ member.name.charAt(0) }}
                  </el-avatar>
                  <div class="member-info">
                    <div class="member-name">{{ member.name }}</div>
                    <div class="member-details">
                      <el-tag 
                        :type="member.gender === 'male' ? 'primary' : 'danger'"
                        size="small"
                      >
                        {{ member.gender === 'male' ? '男' : '女' }}
                      </el-tag>
                      <span v-if="member.birthDate" class="member-birth">{{ member.birthDate }}</span>
                    </div>
                  </div>
                  <div class="member-actions">
                    <el-button 
                      type="text"
                      size="small"
                      @click.stop="editMember(member)"
                      title="编辑"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button 
                      type="text"
                      size="small"
                      @click.stop="deleteMember(member.id)"
                      title="删除"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </aside>

      <!-- 图形区域 -->
      <div class="graph-area">
        <div class="graph-container" ref="graphContainer">
          <FamilyGraphComponent 
            ref="graphRef"
            :members="familyStore.filteredMembers"
            :zoom-level="familyStore.zoomLevel"
            :show-relationships="familyStore.relationshipsVisible"
            :show-photos="familyStore.showPhotos"
            :show-dates="familyStore.showDates"
            :show-generation="familyStore.showGeneration"
            @member-click="selectMember"
            @member-edit="editMember"
          />
        </div>
      </div>
    </main>

    <!-- 添加成员对话框 -->
    <el-dialog 
      v-model="showAddMemberDialog" 
      title="添加家族成员" 
      width="600px"
      :before-close="handleCloseAddDialog"
    >
      <el-form 
        ref="addMemberFormRef" 
        :model="newMember" 
        :rules="memberRules" 
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="newMember.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="newMember.gender">
                <el-radio value="male">男</el-radio>
                <el-radio value="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="newMember.birthDate"
                type="date"
                placeholder="选择出生日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="逝世日期">
              <el-date-picker
                v-model="newMember.deathDate"
                type="date"
                placeholder="选择逝世日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="世代" prop="generation">
              <el-input-number 
                v-model="newMember.generation" 
                :min="1" 
                :max="20" 
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父亲">
              <el-select v-model="newMember.parentId" placeholder="选择父亲" style="width: 100%" clearable>
                <el-option label="无" value="" />
                <el-option 
                  v-for="member in maleMembers" 
                  :key="member.id"
                  :label="member.name" 
                  :value="member.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="配偶">
          <el-select v-model="newMember.spouseId" placeholder="选择配偶" style="width: 100%" clearable>
            <el-option label="无" value="" />
            <el-option 
              v-for="member in availableSpouses" 
              :key="member.id"
              :label="member.name" 
              :value="member.id" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="handleCloseAddDialog">取消</el-button>
        <el-button type="primary" @click="handleAddMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFamilyStore } from '@/stores/family'
import type { FamilyMember } from '@/types/family'
import FamilyGraphComponent from '@/components/family/FamilyGraphComponent.vue'
import {
  ArrowLeft,
  Setting,
  Share,
  Plus,
  Search,
  Connection,
  Minus,
  FullScreen,
  Aim,
  Filter,
  User,
  Operation as TreeIcon,
  ZoomOut,
  ZoomIn,
  ScaleToOriginal,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const familyStore = useFamilyStore()

// 响应式数据
const showAddMemberDialog = ref(false)
const addMemberFormRef = ref<FormInstance>()
const graphContainer = ref<HTMLElement>()
const graphRef = ref()
const searchQuery = ref('')
const selectedGeneration = ref<number | 'all'>('all')

// 新成员表单数据
const newMember = ref({
  familyId: 1,
  name: '',
  gender: 'male' as 'male' | 'female',
  birthDate: '' as string,
  deathDate: '' as string,
  generation: 1,
  parentId: '' as string,
  spouseId: '' as string,
  children: [] as string[]
})

// 表单验证规则
const memberRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  generation: [
    { required: true, message: '请输入世代', trigger: 'blur' }
  ]
}

// 筛选选项
const genderOptions = [
  { label: '全部', value: 'all' as const },
  { label: '男性', value: 'male' as const },
  { label: '女性', value: 'female' as const }
]

const statusOptions = [
  { label: '全部', value: 'all' as const },
  { label: '在世', value: 'alive' as const },
  { label: '已故', value: 'deceased' as const }
]

// 计算属性
const familyIcon = computed(() => {
  const name = familyStore.currentFamily?.name || '张氏家族'
  return name.charAt(0)
})

const availableGenerations = computed(() => {
  const generations = new Set(familyStore.familyMembers.map(m => m.generation))
  return Array.from(generations).sort((a, b) => a - b)
})

const maleMembers = computed(() => {
  return familyStore.familyMembers.filter(m => m.gender === 'male')
})

const availableSpouses = computed(() => {
  return familyStore.familyMembers.filter(m => 
    m.gender !== newMember.value.gender && !m.spouseId
  )
})

// 方法
const goBack = () => {
  router.back()
}

const selectMember = (member: FamilyMember) => {
  familyStore.setSelectedMember(member)
}

const editMember = (member: FamilyMember) => {
  // TODO: 实现编辑成员功能
  console.log('编辑成员:', member)
}

const getInitial = (name: string) => {
  return name.charAt(0)
}

const formatDateRange = (birthDate?: string | null, deathDate?: string | null) => {
  const birth = birthDate ? new Date(birthDate).getFullYear() : '?'
  const death = deathDate ? new Date(deathDate).getFullYear() : ''
  return death ? `${birth}-${death}` : `${birth}-`
}

const handleSearch = (query: string) => {
  familyStore.searchMembers(query)
}

const handleGenerationChange = (generation: number | 'all') => {
  familyStore.setFilter('generation', generation === 'all' ? undefined : generation)
}

const handleExport = async (format: string) => {
  if (format !== 'png') return
  const el = graphContainer.value
  if (!el) return
  const { default: html2canvas } = await import('html2canvas')
  const canvas = await html2canvas(el as HTMLElement, { useCORS: true, scale: 2 })
  const link = document.createElement('a')
  link.href = canvas.toDataURL('image/png')
  link.download = 'family-tree.png'
  link.click()
}

const fitToScreen = () => {
  graphRef.value?.fitToScreen?.()
}

const centerGraph = () => {
  graphRef.value?.centerGraph?.()
}

const toggleFullscreen = () => {
  const el = graphContainer.value
  if (!el) return
  const d: any = document
  if (!d.fullscreenElement) {
    el.requestFullscreen?.()
  } else {
    d.exitFullscreen?.()
  }
}

const openSettings = () => {
  // TODO: 实现设置功能
  console.log('打开设置')
}

const shareFamily = () => {
  // TODO: 实现分享功能
  console.log('分享家族')
}

const openRelationshipQuery = () => {
  // TODO: 实现称呼查询功能
  console.log('称呼查询')
}

const handleAddMember = async () => {
  if (!addMemberFormRef.value) return
  
  try {
    await addMemberFormRef.value.validate()
    
    // 处理数据格式转换
    const memberData = {
      ...newMember.value,
      birthDate: newMember.value.birthDate || null,
      deathDate: newMember.value.deathDate || null,
      parentId: newMember.value.parentId || null,
      spouseId: newMember.value.spouseId || null
    }
    
    familyStore.addMember(memberData)
    showAddMemberDialog.value = false
    resetForm()
  } catch (error) {
    console.error('添加成员失败:', error)
  }
}

const handleCloseAddDialog = () => {
  showAddMemberDialog.value = false
  resetForm()
}

const resetForm = () => {
  newMember.value = {
    familyId: 1,
    name: '',
    gender: 'male',
    birthDate: '',
    deathDate: '',
    generation: 1,
    parentId: '',
    spouseId: '',
    children: []
  }
  addMemberFormRef.value?.resetFields()
}

// 生命周期
onMounted(async () => {
  // 初始化族谱数据
  const familyId = Number(route.params.id)
  
  // 设置当前家族信息
  familyStore.setCurrentFamily({
    id: familyId,
    name: '张氏家族',
    description: '源远流长的张氏家族，始祖张德明于明朝洪武年间自山西洪洞迁至此地，历经数百年传承，现已繁衍至第五代。',
    memberCount: 0,
    generationCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  })
  const loaded = await familyStore.loadMembers(familyId)
  if (!loaded || loaded.length === 0) {
    
    // 加载示例数据
  const sampleMembers: FamilyMember[] = [
    // 第一代 - 始祖
    {
      id: '1',
      familyId: familyId,
      name: '张德高',
      gender: 'male',
      birthDate: '1350-01-01',
      deathDate: '1420-12-31',
      generation: 1,
      parentId: null,
      spouseId: '2',
      children: ['3', '4', '5']
    },
    {
      id: '2',
      familyId: familyId,
      name: '李氏',
      gender: 'female',
      birthDate: '1355-01-01',
      deathDate: '1425-12-31',
      generation: 1,
      parentId: null,
      spouseId: '1',
      children: ['3', '4', '5']
    },
    
    // 第二代 - 子女
    {
      id: '3',
      familyId: familyId,
      name: '张文华',
      gender: 'male',
      birthDate: '1375-01-01',
      deathDate: '1448-12-31',
      generation: 2,
      parentId: '1',
      spouseId: '6',
      children: ['8', '9']
    },
    {
      id: '4',
      familyId: familyId,
      name: '张文武',
      gender: 'male',
      birthDate: '1378-01-01',
      deathDate: '1451-12-31',
      generation: 2,
      parentId: '1',
      spouseId: '7',
      children: ['10', '11', '12']
    },
    {
      id: '5',
      familyId: familyId,
      name: '张文秀',
      gender: 'female',
      birthDate: '1380-01-01',
      deathDate: '1455-12-31',
      generation: 2,
      parentId: '1',
      spouseId: null,
      children: []
    },
    
    // 第二代配偶
    {
      id: '6',
      familyId: familyId,
      name: '王氏',
      gender: 'female',
      birthDate: '1378-01-01',
      deathDate: '1450-12-31',
      generation: 2,
      parentId: null,
      spouseId: '3',
      children: ['8', '9']
    },
    {
      id: '7',
      familyId: familyId,
      name: '陈氏',
      gender: 'female',
      birthDate: '1380-01-01',
      deathDate: '1453-12-31',
      generation: 2,
      parentId: null,
      spouseId: '4',
      children: ['10', '11', '12']
    },
    
    // 第三代 - 孙辈
    {
      id: '8',
      familyId: familyId,
      name: '张志远',
      gender: 'male',
      birthDate: '1400-01-01',
      deathDate: '1475-12-31',
      generation: 3,
      parentId: '3',
      spouseId: '13',
      children: ['15', '16']
    },
    {
      id: '9',
      familyId: familyId,
      name: '张志明',
      gender: 'male',
      birthDate: '1403-01-01',
      deathDate: '1478-12-31',
      generation: 3,
      parentId: '3',
      spouseId: '14',
      children: ['17']
    },
    {
      id: '10',
      familyId: familyId,
      name: '张志强',
      gender: 'male',
      birthDate: '1405-01-01',
      deathDate: '1480-12-31',
      generation: 3,
      parentId: '4',
      spouseId: null,
      children: []
    },
    {
      id: '11',
      familyId: familyId,
      name: '张志华',
      gender: 'male',
      birthDate: '1408-01-01',
      deathDate: null,
      generation: 3,
      parentId: '4',
      spouseId: null,
      children: ['18', '19']
    },
    {
      id: '12',
      familyId: familyId,
      name: '张志兰',
      gender: 'female',
      birthDate: '1410-01-01',
      deathDate: '1485-12-31',
      generation: 3,
      parentId: '4',
      spouseId: null,
      children: []
    },
    
    // 第三代配偶
    {
      id: '13',
      familyId: familyId,
      name: '刘氏',
      gender: 'female',
      birthDate: '1402-01-01',
      deathDate: '1477-12-31',
      generation: 3,
      parentId: null,
      spouseId: '8',
      children: ['15', '16']
    },
    {
      id: '14',
      familyId: familyId,
      name: '赵氏',
      gender: 'female',
      birthDate: '1405-01-01',
      deathDate: '1480-12-31',
      generation: 3,
      parentId: null,
      spouseId: '9',
      children: ['17']
    },
    
    // 第四代 - 曾孙辈
    {
      id: '15',
      familyId: familyId,
      name: '张国栋',
      gender: 'male',
      birthDate: '1425-01-01',
      deathDate: '1500-12-31',
      generation: 4,
      parentId: '8',
      spouseId: '20',
      children: ['22', '23']
    },
    {
      id: '16',
      familyId: familyId,
      name: '张国梁',
      gender: 'male',
      birthDate: '1428-01-01',
      deathDate: '1503-12-31',
      generation: 4,
      parentId: '8',
      spouseId: '21',
      children: ['24']
    },
    {
      id: '17',
      familyId: familyId,
      name: '张国华',
      gender: 'male',
      birthDate: '1430-01-01',
      deathDate: null,
      generation: 4,
      parentId: '9',
      spouseId: null,
      children: []
    },
    {
      id: '18',
      familyId: familyId,
      name: '张国强',
      gender: 'male',
      birthDate: '1432-01-01',
      deathDate: null,
      generation: 4,
      parentId: '11',
      spouseId: null,
      children: ['25', '26']
    },
    {
      id: '19',
      familyId: familyId,
      name: '张国秀',
      gender: 'female',
      birthDate: '1435-01-01',
      deathDate: null,
      generation: 4,
      parentId: '11',
      spouseId: null,
      children: []
    },
    
    // 第四代配偶
    {
      id: '20',
      familyId: familyId,
      name: '孙氏',
      gender: 'female',
      birthDate: '1427-01-01',
      deathDate: '1502-12-31',
      generation: 4,
      parentId: null,
      spouseId: '15',
      children: ['22', '23']
    },
    {
      id: '21',
      familyId: familyId,
      name: '周氏',
      gender: 'female',
      birthDate: '1430-01-01',
      deathDate: '1505-12-31',
      generation: 4,
      parentId: null,
      spouseId: '16',
      children: ['24']
    },
    
    // 第五代 - 玄孙辈
    {
      id: '22',
      familyId: familyId,
      name: '张家兴',
      gender: 'male',
      birthDate: '1450-01-01',
      deathDate: null,
      generation: 5,
      parentId: '15',
      spouseId: null,
      children: []
    },
    {
      id: '23',
      familyId: familyId,
      name: '张家旺',
      gender: 'male',
      birthDate: '1453-01-01',
      deathDate: null,
      generation: 5,
      parentId: '15',
      spouseId: null,
      children: []
    },
    {
      id: '24',
      familyId: familyId,
      name: '张家富',
      gender: 'male',
      birthDate: '1455-01-01',
      deathDate: null,
      generation: 5,
      parentId: '16',
      spouseId: null,
      children: []
    },
    {
      id: '25',
      familyId: familyId,
      name: '张家贵',
      gender: 'male',
      birthDate: '1457-01-01',
      deathDate: null,
      generation: 5,
      parentId: '18',
      spouseId: null,
      children: []
    },
    {
      id: '26',
      familyId: familyId,
      name: '张家慧',
      gender: 'female',
      birthDate: '1460-01-01',
      deathDate: null,
      generation: 5,
      parentId: '18',
      spouseId: null,
      children: []
    }
  ]
  
  familyStore.setFamilyMembers(sampleMembers)
  }
})
</script>

<style scoped>
/* 页面布局 */
.family-tree-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--background-light);
}

/* 页面头部 */
.page-header {
  height: 64px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.back-btn {
  width: 40px;
  height: 40px;
}

.page-title {
  font-size: var(--font-2xl);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--text-primary);
  margin: 0;
}

.title-icon {
  font-size: var(--font-xl);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

/* 工具栏 */
.toolbar {
  height: 64px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-xl);
  gap: var(--spacing-lg);
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.toolbar-label {
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Element Plus 组件样式覆盖 */
.toolbar .el-select {
  width: 120px;
}

.toolbar .el-select .el-input__wrapper {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface);
  transition: all var(--duration-normal) ease;
}

.toolbar .el-select .el-input__wrapper:hover {
  border-color: var(--primary-light);
}

.toolbar .el-select .el-input__wrapper.is-focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

.toolbar .el-input {
  width: 240px;
}

.toolbar .el-input__wrapper {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface);
  transition: all var(--duration-normal) ease;
}

.toolbar .el-input__wrapper:hover {
  border-color: var(--primary-light);
}

.toolbar .el-input__wrapper.is-focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

.toolbar .el-button {
  background: var(--background-light);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  transition: all var(--duration-normal) ease;
  font-size: var(--font-sm);
  font-weight: 500;
}

.toolbar .el-button:hover {
  background: var(--primary-bg);
  border-color: var(--primary-light);
  color: var(--primary-color);
}

.toolbar .el-button.is-type-primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.toolbar .el-button.is-type-primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

.toolbar .el-button-group {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.toolbar .el-button-group .el-button {
  border: none;
  border-radius: 0;
  border-right: 1px solid var(--border);
  margin: 0;
}

.toolbar .el-button-group .el-button:last-child {
  border-right: none;
}

/* 关系显示控制按钮 */
.relationship-toggle {
  background: var(--primary-color) !important;
  color: white !important;
  border: 1px solid var(--primary-color) !important;
}

.relationship-toggle:hover {
  background: var(--primary-dark) !important;
  border-color: var(--primary-dark) !important;
  color: white !important;
}

.relationship-toggle.active {
  background: var(--primary-dark) !important;
  border-color: var(--primary-dark) !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    height: auto;
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }
  
  .toolbar-section {
    justify-content: space-between;
    flex-wrap: wrap;
  }
  
  .toolbar .el-input {
    width: 180px;
  }
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* 侧边栏 */
.sidebar {
  width: 360px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width var(--duration-normal) ease;
}

.sidebar.collapsed {
  width: 0;
  overflow: hidden;
}

.sidebar-toggle {
  position: absolute;
  top: var(--spacing-lg);
  right: -12px;
  width: 24px;
  height: 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-xs);
  color: var(--text-secondary);
  z-index: 10;
  transition: all var(--duration-normal) ease;
}

.sidebar-toggle:hover {
  background: var(--primary-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* 添加成员按钮 */
.add-member-btn {
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}

.add-member-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

/* 操作按钮 */
.member-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.member-item:hover .member-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f3f4f6;
  transform: scale(1.1);
}

.edit-btn:hover {
  background: #dbeafe;
}

.delete-btn:hover {
  background: #fee2e2;
}

.sidebar-header {
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--border);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

/* 家族信息卡片 */
.family-info-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.family-name {
  font-size: var(--font-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.family-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-color);
  color: white;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-xl);
  font-weight: 600;
}

.family-desc {
  color: var(--text-secondary);
  font-size: var(--font-sm);
  line-height: 1.6;
  margin-bottom: var(--spacing-lg);
}

.family-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.stat-item {
  text-align: center;
  padding: var(--spacing-md);
  background: var(--background-light);
  border-radius: var(--radius-lg);
}

.stat-value {
  display: block;
  font-size: var(--font-xl);
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: var(--font-xs);
  color: var(--text-muted);
  margin-top: var(--spacing-xs);
}

/* 筛选器部分 */
.filters-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.section-icon {
  font-size: var(--font-base);
}

.filter-group {
  margin-bottom: var(--spacing-lg);
}

.filter-label {
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: var(--spacing-sm);
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.filter-tag {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--background-light);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-normal) ease;
}

.filter-tag:hover {
  background: var(--primary-bg);
  border-color: var(--primary-light);
  color: var(--primary-color);
}

.filter-tag.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* Element Plus 组件样式覆盖 */
.el-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.el-radio-button__inner {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--background-light);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  transition: all var(--duration-normal) ease;
}

.el-radio-button__inner:hover {
  background: var(--primary-bg);
  border-color: var(--primary-light);
  color: var(--primary-color);
}

.el-radio-button.is-active .el-radio-button__inner {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.el-checkbox {
  margin-right: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.el-checkbox__label {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--background-light);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  font-size: var(--font-xs);
  color: var(--text-secondary);
  transition: all var(--duration-normal) ease;
}

.el-checkbox.is-checked .el-checkbox__label {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* 成员列表 */
.members-section {
  flex: 1;
}

.members-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}

.add-member-btn {
  background: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-normal) ease;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-sm);
  font-weight: 500;
}

.add-member-btn:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  max-height: 400px;
  overflow-y: auto;
}

.member-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-normal) ease;
}

.member-item:hover {
  background: var(--primary-bg);
  border-color: var(--primary-light);
}

.member-item.selected {
  background: var(--primary-bg);
  border-color: var(--primary-color);
}

.member-avatar {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  color: white;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-sm);
  font-weight: 600;
}

/* Element Plus 成员卡片样式 */
.member-card {
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.member-card.selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

.member-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-details {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.member-birth {
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

.member-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.member-card:hover .member-actions {
  opacity: 1;
}

/* Element Plus 组件样式覆盖 */
.el-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.el-radio-button__inner {
  padding: 6px 12px;
  font-size: 12px;
}

.el-checkbox {
  margin-right: 0;
  margin-bottom: 8px;
}

.el-card__body {
  padding: 0;
}

.display-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 筛选器部分样式更新 */
.filter-label {
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--el-text-color-regular);
  margin-bottom: var(--spacing-sm);
}

.section-title {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* 图形区域 */
.graph-area {
  flex: 1;
  background: var(--surface);
  position: relative;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
  overflow: auto;
  position: relative;
}

.graph-content {
  position: relative;
  transform-origin: center center;
  transition: transform 0.3s ease;
  background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%);
  border-radius: 12px;
  margin: 24px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 40px;
  min-width: 800px;
  min-height: 600px;
}

/* 世代容器 */
.generation {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80px;
}

.generation::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 1px;
  background: #e5e7eb;
}

.generation-label {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  padding: 8px 24px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  border: 2px solid white;
}

.node-group {
  display: flex;
  gap: 48px;
  align-items: flex-end;
  position: relative;
  flex-wrap: wrap;
  justify-content: center;
  min-height: 280px;
}

/* 夫妻组布局 */
.couple-group {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  position: relative;
  margin: 0 24px;
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.04), rgba(59, 130, 246, 0.04));
  border: 1px solid rgba(236, 72, 153, 0.15);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.08);
  align-self: flex-end;
}

.couple-group::after {
  content: '♥';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgba(236, 72, 153, 0.6);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 3px 5px;
  border-radius: 50%;
  z-index: 10;
  box-shadow: 0 2px 6px rgba(236, 72, 153, 0.15);
  border: 1px solid rgba(236, 72, 153, 0.3);
}
</style>
