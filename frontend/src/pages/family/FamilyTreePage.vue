<template>
  <div class="family-tree-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <el-button 
          link
          class="back-btn" 
          title="返回"
          @click="goBack"
        >
          <el-icon :size="20"><Back /></el-icon>
        </el-button>
        <h1 class="page-title">
          <span class="title-icon">🌳</span>
          {{ familyStore.currentFamily?.name || '族谱' }}
        </h1>
      </div>
      
      <div class="header-right">
        <el-button @click="openSettings">
          <el-icon class="el-icon--left"><Setting /></el-icon>
          设置
        </el-button>
        <el-button @click="shareFamily">
          <el-icon class="el-icon--left"><Share /></el-icon>
          分享
        </el-button>
        <el-button type="primary" @click="showAddMemberDialog = true">
          <el-icon class="el-icon--left"><Plus /></el-icon>
          添加成员
        </el-button>
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
          <el-button size="small" title="适应屏幕" @click="fitToScreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
          <el-button size="small" title="居中显示" @click="centerGraph">
            <el-icon><Aim /></el-icon>
          </el-button>
          <el-button size="small" title="全屏" @click="toggleFullscreen">
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
          :title="familyStore.sidebarCollapsed ? '展开' : '收起'"
          @click="familyStore.toggleSidebar()"
        >
          {{ familyStore.sidebarCollapsed ? '▶' : '◀' }}
        </button>
        
        <div v-if="!familyStore.sidebarCollapsed" class="sidebar-header">
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
        
        <div v-if="!familyStore.sidebarCollapsed" class="sidebar-content">
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
                @change="(value) => familyStore.setFilter('gender', value as 'male' | 'female' | 'all')"
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
                @change="(value) => familyStore.setFilter('status', value as 'all' | 'alive' | 'deceased')"
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
                      title="编辑"
                      @click.stop="editMember(member)"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button 
                      type="text"
                      size="small"
                      title="删除"
                      @click.stop="deleteMember(member.id)"
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
<div ref="graphContainer" class="graph-container">
          <EnhancedFamilyGraph 
            ref="graphRef"
            :members="familyStore.filteredMembers"
            :show-relationships="familyStore.relationshipsVisible"
            :show-photos="familyStore.showPhotos"
            :show-dates="familyStore.showDates"
            :show-generation="familyStore.showGeneration"
            v-model:zoomLevel="familyStore.zoomLevel"
            @node-click="selectMember"
            @node-view="handleViewMember"
            @node-select="handleNodeSelect"
            @node-edit="editMember"
            @add-member="handleAddMember"
            @delete-member="deleteMember"
            @export="handleExport"
            @update-options="handleUpdateOptions"
            @view-kinship="handleViewKinship"
          />
        </div>
      </div>
    </main>

    <!-- 功能对话框 - 移至底部统一管理 -->


    <!-- 添加/编辑成员对话框 -->
    <el-dialog 
      v-model="showAddMemberDialog" 
      :title="isEditing ? '编辑成员' : '添加家族成员'" 
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

    <el-dialog 
      v-model="showMemberDetailDialog" 
      title="成员详情" 
      width="520px"
    >
      <div v-if="memberDetail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="姓名">{{ memberDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ memberDetail.gender === 'male' ? '男' : '女' }}</el-descriptions-item>
          <el-descriptions-item label="排行">{{ birthOrder }}</el-descriptions-item>
          <el-descriptions-item label="世代">{{ memberDetail.generation }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ memberDetail.birthDate || '-' }}</el-descriptions-item>
          <el-descriptions-item label="逝世日期">{{ memberDetail.deathDate || '-' }}</el-descriptions-item>
          <el-descriptions-item label="父亲">{{ fatherName }}</el-descriptions-item>
          <el-descriptions-item label="母亲">{{ motherName }}</el-descriptions-item>
          <el-descriptions-item label="配偶">{{ spouseName }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showMemberDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 功能对话框 -->
    <ShareDialog 
      v-model="showShareDialog" 
      @export="handleExport"
    />
    
    <SettingsDialog 
      v-model="showSettingsDialog"
      @reset-view="handleResetView" 
    />
    
    <RelationshipQueryDialog 
      v-model="showRelationshipQueryDialog"
      :members="familyStore.familyMembers"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFamilyStore } from '@/stores/family'
import type { FamilyMember } from '@/types/family'
import EnhancedFamilyGraph from '@/components/family/EnhancedFamilyGraph.vue'
import ShareDialog from '@/components/family/ShareDialog.vue'
import SettingsDialog from '@/components/family/SettingsDialog.vue'
import RelationshipQueryDialog from '@/components/family/RelationshipQueryDialog.vue'
import { kinshipApi } from '@/api/kinship'
import {
  Plus,
  Search,
  Connection,
  FullScreen,
  Aim,
  Filter,
  User,
  ZoomOut,
  ZoomIn,
  ScaleToOriginal,
  Edit,
  Delete,
  Setting,
  Share,
  Back,
  Switch
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ensureAuthToken } from '@/api/auth'
import { getFamilyDetail, getFamilyPermissions, joinFamily } from '@/api/family'

import { KinshipCalculator } from '@/utils/kinship'

const route = useRoute()
const router = useRouter()
const familyStore = useFamilyStore()

// 响应式数据
const showAddMemberDialog = ref(false)
const showShareDialog = ref(false)
const showSettingsDialog = ref(false)
const showRelationshipQueryDialog = ref(false)
const isEditing = ref(false)
const currentMemberId = ref<string>('')
const addMemberFormRef = ref<FormInstance>()
const graphContainer = ref<HTMLElement>()
const graphRef = ref()
const searchQuery = ref('')
const selectedGeneration = ref<number | 'all'>('all')

// 称呼查看模式
const kinshipMode = ref(false)
const centerMemberId = ref('')
const kinshipDirection = ref<'from' | 'to'>('from') // 'from': 我称呼TA, 'to': TA称呼我
const centerMemberName = computed(() => {
  const member = familyStore.familyMembers.find(m => m.id === centerMemberId.value)
  return member ? member.name : '未知'
})

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
  graphRef.value?.selectMemberExact?.(member.id)
}

const showMemberDetailDialog = ref(false)
const memberDetail = ref<FamilyMember | null>(null)

const handleViewMember = (member: FamilyMember) => {
  memberDetail.value = member
  showMemberDetailDialog.value = true
}

const getMemberNameById = (id: string | null | undefined) => {
  if (!id) return '-'
  const m = familyStore.familyMembers.find(x => x.id === id)
  return m ? m.name : '-'
}

const fatherName = computed(() => {
  const p = memberDetail.value?.parentId ? familyStore.familyMembers.find(x => x.id === memberDetail.value?.parentId) : null
  if (p && p.gender === 'male') return p.name
  const spouse = p?.spouseId ? familyStore.familyMembers.find(x => x.id === p.spouseId) : null
  return spouse && spouse.gender === 'male' ? spouse.name : '-'
})

const motherName = computed(() => {
  const p = memberDetail.value?.parentId ? familyStore.familyMembers.find(x => x.id === memberDetail.value?.parentId) : null
  if (p && p.gender === 'female') return p.name
  const spouse = p?.spouseId ? familyStore.familyMembers.find(x => x.id === p.spouseId) : null
  return spouse && spouse.gender === 'female' ? spouse.name : '-'
})

const spouseName = computed(() => getMemberNameById(memberDetail.value?.spouseId))

const birthOrder = computed(() => {
  if (!memberDetail.value) return '-'
  // 优先使用后端返回的 birth_order
  if (memberDetail.value.birth_order) return memberDetail.value.birth_order
  
  // 如果后端没有返回（兼容旧数据），则尝试前端计算
  const calculator = new KinshipCalculator(familyStore.familyMembers)
  return calculator.getBirthOrder(memberDetail.value.id)
})

const editMember = (member: FamilyMember) => {
  isEditing.value = true
  currentMemberId.value = member.id
  newMember.value = {
    familyId: member.familyId,
    name: member.name,
    gender: member.gender,
    birthDate: member.birthDate || '',
    deathDate: member.deathDate || '',
    generation: member.generation,
    parentId: member.parentId || '',
    spouseId: member.spouseId || '',
    children: [...(member.children || [])]
  }
  showAddMemberDialog.value = true
}

const deleteMember = (id: string) => {
  ElMessageBox.confirm(
    '确定要删除该成员吗？此操作不可恢复。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await familyStore.deleteMember(id)
        ElMessage.success('删除成功')
      } catch (error) {
        ElMessage.error('删除失败')
        console.error(error)
      }
    })
    .catch(() => {
      // cancel
    })
}

const handleSearch = (query: string) => {
  familyStore.searchMembers(query)
}

const handleGenerationChange = (generation: number | 'all') => {
  familyStore.setFilter('generation', generation === 'all' ? undefined : generation)
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
  if (!document.fullscreenElement) {
    el.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

const openSettings = () => {
  showSettingsDialog.value = true
}

const shareFamily = () => {
  showShareDialog.value = true
}

const openRelationshipQuery = () => {
  showRelationshipQueryDialog.value = true
}

const handleResetView = () => {
  familyStore.resetZoom()
  centerGraph()
  showSettingsDialog.value = false
}

const handleExport = async (format: string) => {
  if (format === 'excel') {
    // 导出 Excel (CSV)
    try {
      const members = familyStore.familyMembers
      const headers = ['ID', '姓名', '性别', '世代', '出生日期', '逝世日期', '父亲ID', '配偶ID']
      const rows = members.map(m => [
        m.id,
        m.name,
        m.gender === 'male' ? '男' : '女',
        m.generation,
        m.birthDate || '',
        m.deathDate || '',
        m.parentId || '',
        m.spouseId || ''
      ])
      
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')
      
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `family-tree-export.csv`
      link.click()
      URL.revokeObjectURL(link.href)
      ElMessage.success('导出成功')
    } catch (error) {
      console.error('Export excel failed:', error)
      ElMessage.error('导出失败')
    }
  } else if (graphRef.value) {
    // 导出图片
    try {
      // 如果 format 是 base64 数据 URL（从 EnhancedFamilyGraph 传来的），直接下载
      if (format.startsWith('data:')) {
        const link = document.createElement('a')
        link.href = format
        // 猜测文件类型
        let ext = 'png'
        if (format.startsWith('data:image/svg')) ext = 'svg'
        else if (format.startsWith('data:application/pdf')) ext = 'pdf'
        
        link.download = `family-tree.${ext}`
        link.click()
        ElMessage.success('导出成功')
        return
      }
      
      // 否则触发组件导出
      // 注意：这里需要处理 EnhancedFamilyGraph 导出后会再次触发 emit('export', dataURL)
      // 所以我们调用 graphRef.value.exportAsImage 时，不需要在这里处理结果，
      // 而是等待组件 emit 回来的数据（通过递归调用 handleExport）。
      await graphRef.value.exportAsImage(format)
    } catch (error) {
      console.error('Export image failed:', error)
      ElMessage.error('导出失败')
    }
  }
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
    
    if (isEditing.value && currentMemberId.value) {
      // 更新现有成员
      await familyStore.updateMember({
        ...memberData,
        id: currentMemberId.value
      } as FamilyMember)
      ElMessage.success('更新成员成功')
    } else {
      // 添加新成员
      await familyStore.addMember(memberData)
      ElMessage.success('添加成员成功')
    }
    
    showAddMemberDialog.value = false
    resetForm()
  } catch (error: any) {
    console.error(isEditing.value ? '更新成员失败:' : '添加成员失败:', error)
    // 尝试提取后端返回的具体错误信息
    const errorMsg = error.response?.data?.message || error.message || (isEditing.value ? '更新成员失败' : '添加成员失败')
    ElMessage.error(errorMsg)
  }
}

const handleCloseAddDialog = () => {
  showAddMemberDialog.value = false
  resetForm()
}

const resetForm = () => {
  isEditing.value = false
  currentMemberId.value = ''
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

const handleUpdateOptions = (options: { relationships?: boolean, photos?: boolean, dates?: boolean, generation?: boolean }) => {
  if (options.relationships !== undefined) familyStore.toggleRelationships() // 注意：store 的 toggle 只是取反，这里最好直接 set
  // 由于 store 目前只有 toggle 方法，且 toggle 是取反 current value，
  // 而 options.relationships 是最新值。
  // 如果 store.value !== options.value，则 toggle。
  if (options.relationships !== undefined && familyStore.relationshipsVisible !== options.relationships) familyStore.toggleRelationships()
  
  if (options.photos !== undefined && familyStore.showPhotos !== options.photos) familyStore.togglePhotos()
  if (options.dates !== undefined && familyStore.showDates !== options.dates) familyStore.toggleDates()
  if (options.generation !== undefined && familyStore.showGeneration !== options.generation) familyStore.toggleGenerationDisplay()
}

const handleNodeSelect = (selectedIds: string[]) => {
  if (!selectedIds || selectedIds.length === 0) {
    familyStore.setSelectedMember(null)
    return
  }
  const member = familyStore.familyMembers.find(m => m.id === selectedIds[0])
  if (member) {
    familyStore.setSelectedMember(member)
  }
}

// 称呼查看相关方法
const kinshipResults = ref<Record<string, any> | null>(null)

const handleViewKinship = async (member: FamilyMember) => {
  centerMemberId.value = member.id
  kinshipMode.value = true
  kinshipDirection.value = 'from'
  
  try {
    // 使用前端计算库 relationship.js
    const calculator = new KinshipCalculator(familyStore.familyMembers)
    // 计算以 member 为中心，对所有其他成员的称呼
    const results = calculator.calculateAll(member.id)
    
    kinshipResults.value = results
    updateKinshipDisplay()
    ElMessage.success(`已切换至以 ${member.name} 为中心的称呼视图`)
  } catch (error) {
    console.error('Failed to calculate kinship:', error)
    ElMessage.error('计算称呼失败')
    exitKinshipMode()
  }
}

const updateKinshipDisplay = () => {
  if (!kinshipResults.value || !graphRef.value) return
  
  const titles = kinshipResults.value as Record<string, string>
  graphRef.value.setMemberTitles(titles)
  graphRef.value.fitToScreen?.()
}

const toggleKinshipDirection = (direction: 'from' | 'to') => {
  if (kinshipDirection.value === direction) return
  kinshipDirection.value = direction
  updateKinshipDisplay()
}

const exitKinshipMode = () => {
  kinshipMode.value = false
  centerMemberId.value = ''
  kinshipResults.value = null
  if (graphRef.value) {
    graphRef.value.setMemberTitles({})
  }
}

// 生命周期
onMounted(async () => {
  // 初始化族谱数据
  const familyId = Number(route.params.id)
  await ensureAuthToken()
  
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
    ElMessage.info('暂无家族成员数据，请添加成员')
  }

  try {
    const detail = await getFamilyDetail(familyId)
    if (!detail) {
      ElMessage.warning('家族不存在或不可见，部分功能可能不可用')
    }
    const perms = await getFamilyPermissions(familyId)
    if (perms && !perms.is_member && perms.can_join) {
      await joinFamily(familyId)
      ElMessage.success('已加入家族，您可进行增删改查操作')
    } else if (perms && !perms.is_member && !perms.can_join) {
      ElMessage.warning('您不是该家族成员，且不允许加入，增删改查功能将不可用')
    }
  } catch (e) {
    // 忽略权限检查异常，避免阻断渲染
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
  margin-right: var(--spacing-sm);
  color: var(--text-primary);
}

.back-btn:hover {
  color: var(--primary-color);
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
