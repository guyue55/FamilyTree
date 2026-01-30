import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { FamilyMember, Family } from '@/types/family'

export interface FilterOptions {
  gender: 'all' | 'male' | 'female'
  status: 'all' | 'alive' | 'deceased'
  generation: number | undefined
  searchQuery: string
}

// 本地存储键名
const STORAGE_KEY = 'family-tree-preferences'

// 默认配置
const DEFAULT_PREFERENCES = {
  relationshipsVisible: false,
  showPhotos: true,
  showDates: true,
  showGeneration: true
}

export const useFamilyStore = defineStore('family', () => {
  // 加载本地配置
  const loadPreferences = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) } : DEFAULT_PREFERENCES
    } catch {
      return DEFAULT_PREFERENCES
    }
  }

  const prefs = loadPreferences()

  // 状态
  const currentFamily = ref<Family | null>(null)
  const familyMembers = ref<FamilyMember[]>([])
  const selectedMember = ref<FamilyMember | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 界面状态
  const sidebarCollapsed = ref(false)
  const relationshipsVisible = ref(prefs.relationshipsVisible)
  const zoomLevel = ref(1)
  const showPhotos = ref(prefs.showPhotos)
  const showDates = ref(prefs.showDates)
  const showGeneration = ref(prefs.showGeneration)
  
  // 监听并保存配置
  watch(
    [relationshipsVisible, showPhotos, showDates, showGeneration],
    () => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          relationshipsVisible: relationshipsVisible.value,
          showPhotos: showPhotos.value,
          showDates: showDates.value,
          showGeneration: showGeneration.value
        }))
      } catch (e) {
        console.warn('Failed to save preferences:', e)
      }
    }
  )
  
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

  const updateMember = async (member: FamilyMember) => {
    try {
      loading.value = true
      const { updateMember: apiUpdateMember } = await import('@/api/members')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await apiUpdateMember(member.id, member as any)
      if (res) {
        const familyId = currentFamily.value?.id
        if (familyId) {
          await loadMembers(familyId)
        }
      }
      return res
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Update failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteMember = async (memberId: string) => {
    try {
      loading.value = true
      const { deleteMember: apiDeleteMember } = await import('@/api/members')
      await apiDeleteMember(memberId)
      
      familyMembers.value = familyMembers.value.filter(m => m.id !== memberId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Delete failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const addMember = async (member: Omit<FamilyMember, 'id'>) => {
    try {
      loading.value = true
      const { createMember: apiCreateMember } = await import('@/api/members')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await apiCreateMember(member as any)
      
      if (res) {
        const familyId = currentFamily.value?.id
        if (familyId) {
          const refreshed = await loadMembers(familyId)
          return refreshed.find(m => m.id === String(res.id)) || null
        }
        return null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Create failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadMembers = async (familyId?: number) => {
    try {
      if (!familyId && currentFamily.value) familyId = currentFamily.value.id
      if (!familyId) return []
      const { getFamilyMembersFlat } = await import('@/api/members')
      const data = await getFamilyMembersFlat(familyId)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const mapped = (data || []).map((m: any) => ({
        id: String(m.id),
        familyId: Number(m.familyId),
        name: String(m.name),
        gender: m.gender === 'female' ? 'female' : 'male',
        birthDate: m.birthDate || null,
        deathDate: m.deathDate || null,
        generation: Number(m.generation) || 1,
        parentId: m.parentId ? String(m.parentId) : null,
        spouseId: m.spouseId ? String(m.spouseId) : null,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        children: Array.isArray(m.children) ? m.children.map((c: any) => String(c)) : []
      })) as FamilyMember[]
      familyMembers.value = mapped
      return mapped
    } catch {
      return []
    }
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
