import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FamilyMember, Family } from '@/types/family'

export interface FilterOptions {
  gender: 'all' | 'male' | 'female'
  status: 'all' | 'alive' | 'deceased'
  generation: number | undefined
  searchQuery: string
}

export const useFamilyStore = defineStore('family', () => {
  // 状态
  const currentFamily = ref<Family | null>(null)
  const familyMembers = ref<FamilyMember[]>([])
  const selectedMember = ref<FamilyMember | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 界面状态
  const sidebarCollapsed = ref(false)
  const relationshipsVisible = ref(false)
  const zoomLevel = ref(1)
  const showPhotos = ref(true)
  const showDates = ref(true)
  const showGeneration = ref(true)
  
  // 筛选器状态
  const filters = ref<FilterOptions>({
    gender: 'all',
    status: 'all',
    generation: undefined,
    searchQuery: ''
  })

  // 计算属性
  const members = computed(() => familyMembers.value)
  
  const filteredMembers = computed(() => {
    let result = familyMembers.value
    
    // 性别筛选
    if (filters.value.gender !== 'all') {
      result = result.filter(member => member.gender === filters.value.gender)
    }
    
    // 状态筛选
    if (filters.value.status !== 'all') {
      if (filters.value.status === 'alive') {
        result = result.filter(member => !member.deathDate)
      } else {
        result = result.filter(member => member.deathDate)
      }
    }
    
    // 世代筛选
    if (filters.value.generation !== undefined) {
      result = result.filter(member => member.generation === filters.value.generation)
    }
    
    // 搜索筛选
    if (filters.value.searchQuery) {
      const query = filters.value.searchQuery.toLowerCase()
      result = result.filter(member => 
        member.name.toLowerCase().includes(query)
      )
    }
    
    return result
  })
  
  const membersByGeneration = computed(() => {
    const generations: Record<number, FamilyMember[]> = {}
    filteredMembers.value.forEach(member => {
      if (!generations[member.generation]) {
        generations[member.generation] = []
      }
      generations[member.generation].push(member)
    })
    return generations
  })
  
  const familyStats = computed(() => {
    const totalMembers = familyMembers.value.length
    const generations = new Set(familyMembers.value.map(m => m.generation)).size
    const branches = familyMembers.value.filter(m => m.children && m.children.length > 0).length
    
    return {
      totalMembers,
      generations,
      branches
    }
  })

  // 方法
  const setCurrentFamily = (family: Family) => {
    currentFamily.value = family
  }

  const setFamilyMembers = (members: FamilyMember[]) => {
    familyMembers.value = members
  }

  const setSelectedMember = (member: FamilyMember | null) => {
    selectedMember.value = member
  }

  const updateMember = (member: FamilyMember) => {
    const index = familyMembers.value.findIndex(m => m.id === member.id)
    if (index !== -1) {
      familyMembers.value[index] = member
    }
  }

  const deleteMember = (memberId: string) => {
    familyMembers.value = familyMembers.value.filter(m => m.id !== memberId)
  }

  const addMember = (member: Omit<FamilyMember, 'id'>) => {
    const newMember: FamilyMember = {
      ...member,
      id: Date.now().toString()
    }
    familyMembers.value.push(newMember)
    return newMember
  }

  const loadMembers = async () => {
    // TODO: 实现从API加载成员数据
    return []
  }
  
  // 界面控制方法
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  const toggleRelationships = () => {
    relationshipsVisible.value = !relationshipsVisible.value
  }
  
  const setZoomLevel = (level: number) => {
    zoomLevel.value = Math.max(0.1, Math.min(3, level))
  }
  
  const zoomIn = () => {
    setZoomLevel(zoomLevel.value + 0.1)
  }
  
  const zoomOut = () => {
    setZoomLevel(zoomLevel.value - 0.1)
  }
  
  const resetZoom = () => {
    setZoomLevel(1)
  }
  
  const togglePhotos = () => {
    showPhotos.value = !showPhotos.value
  }
  
  const toggleDates = () => {
    showDates.value = !showDates.value
  }
  
  const toggleGenerationDisplay = () => {
    showGeneration.value = !showGeneration.value
  }
  
  // 筛选器方法
  const setFilter = <K extends keyof FilterOptions>(key: K, value: FilterOptions[K]) => {
    filters.value[key] = value
  }
  
  const resetFilters = () => {
    filters.value = {
      gender: 'all',
      status: 'all',
      generation: undefined,
      searchQuery: ''
    }
  }
  
  const searchMembers = (query: string) => {
    filters.value.searchQuery = query
  }

  return {
    // 状态
    currentFamily,
    familyMembers,
    selectedMember,
    loading,
    error,
    sidebarCollapsed,
    relationshipsVisible,
    zoomLevel,
    showPhotos,
    showDates,
    showGeneration,
    filters,
    // 计算属性
    members,
    filteredMembers,
    membersByGeneration,
    familyStats,
    // 方法
    setCurrentFamily,
    setFamilyMembers,
    setSelectedMember,
    updateMember,
    deleteMember,
    addMember,
    loadMembers,
    toggleSidebar,
    toggleRelationships,
    setZoomLevel,
    zoomIn,
    zoomOut,
    resetZoom,
    togglePhotos,
    toggleDates,
    toggleGenerationDisplay,
    setFilter,
    resetFilters,
    searchMembers
  }
})