/**
 * Pinia状态管理 - 族谱状态
 *
 * @author 古月
 * @version 1.0.0
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cacheStorage } from '@/utils/storage'
import { FamilyTreeVisibility, FamilyTreeStatus, TreeLayoutType } from '@/enums'
import type { Family, FamilyMembership } from '@/types/family'

/**
 * 族谱状态管理
 */
export const useFamilyStore = defineStore('family', () => {
  // 状态
  const currentFamily = ref<Family | null>(null)
  const familyList = ref<Family[]>([])
  const recentFamilies = ref<Family[]>([])
  const familyMembers = ref<FamilyMembership[]>([])
  const familyTree = ref<any[]>([])
  const selectedMember = ref<FamilyMembership | null>(null)
  const treeLayout = ref<TreeLayoutType>(TreeLayoutType.HORIZONTAL)
  const isLoading = ref(false)
  const searchKeyword = ref('')

  // 计算属性
  const hasCurrentFamily = computed(() => !!currentFamily.value)
  const currentFamilyId = computed(() => currentFamily.value?.id)
  const currentFamilyName = computed(() => currentFamily.value?.name || '')
  const isCurrentFamilyOwner = computed(() => {
    // 这里需要结合用户状态来判断
    return currentFamily.value?.creatorId === 1 // 需要从用户store获取实际用户ID
  })
  const activeMembersCount = computed(
    () =>
      familyMembers.value.filter((member: FamilyMembership) => member.status === 'active').length
  )
  const publicFamilies = computed(() =>
    familyList.value.filter((family: Family) => family.visibility === 'public')
  )
  const privateFamilies = computed(() =>
    familyList.value.filter((family: Family) => family.visibility === 'private')
  )

  // 动作
  /**
   * 设置当前族谱
   */
  function setCurrentFamily(family: Family | null) {
    currentFamily.value = family
    if (family) {
      addToRecentFamilies(family)
    }
  }

  /**
   * 设置族谱列表
   */
  function setFamilyList(families: Family[]) {
    familyList.value = families
  }

  /**
   * 添加族谱到列表
   */
  function addFamily(family: Family) {
    familyList.value.unshift(family)
  }

  /**
   * 更新族谱信息
   */
  function updateFamily(familyId: string, updates: Partial<Family>) {
    // 更新列表中的族谱
    const index = familyList.value.findIndex(f => f.id === familyId)
    if (index !== -1) {
      familyList.value[index] = { ...familyList.value[index], ...updates }
    }

    // 更新当前族谱
    if (currentFamily.value?.id === familyId) {
      currentFamily.value = { ...currentFamily.value, ...updates }
    }

    // 更新最近访问的族谱
    const recentIndex = recentFamilies.value.findIndex(f => f.id === familyId)
    if (recentIndex !== -1) {
      recentFamilies.value[recentIndex] = { ...recentFamilies.value[recentIndex], ...updates }
    }
  }

  /**
   * 删除族谱
   */
  function removeFamily(familyId: string) {
    familyList.value = familyList.value.filter((f: Family) => f.id !== familyId)
    recentFamilies.value = recentFamilies.value.filter((f: Family) => f.id !== familyId)

    if (currentFamily.value?.id === familyId) {
      currentFamily.value = null
    }
  }

  /**
   * 设置族谱成员
   */
  function setFamilyMembers(members: FamilyMembership[]) {
    familyMembers.value = members
  }

  /**
   * 添加族谱成员
   */
  function addFamilyMember(member: FamilyMembership) {
    familyMembers.value.push(member)
  }

  /**
   * 更新族谱成员
   */
  function updateFamilyMember(memberId: string, updates: Partial<FamilyMembership>) {
    const index = familyMembers.value.findIndex((m: FamilyMembership) => m.id === memberId)
    if (index !== -1) {
      familyMembers.value[index] = { ...familyMembers.value[index], ...updates }
    }

    if (selectedMember.value?.id === memberId) {
      selectedMember.value = { ...selectedMember.value, ...updates }
    }
  }

  /**
   * 删除族谱成员
   */
  function removeFamilyMember(memberId: string) {
    familyMembers.value = familyMembers.value.filter((m: FamilyMembership) => m.id !== memberId)

    if (selectedMember.value?.id === memberId) {
      selectedMember.value = null
    }
  }

  /**
   * 设置族谱树数据
   */
  function setFamilyTree(tree: any[]) {
    familyTree.value = tree
  }

  /**
   * 设置选中的成员
   */
  function setSelectedMember(member: FamilyMembership | null) {
    selectedMember.value = member
  }

  /**
   * 设置树形布局
   */
  function setTreeLayout(layout: TreeLayoutType) {
    treeLayout.value = layout
    // 保存到本地存储
    // appStorage.setTreeLayout(layout); // 需要从app store导入
  }

  /**
   * 添加到最近访问的族谱
   */
  function addToRecentFamilies(family: Family) {
    // 移除已存在的
    recentFamilies.value = recentFamilies.value.filter((f: Family) => f.id !== family.id)
    // 添加到开头
    recentFamilies.value.unshift(family)
    // 只保留最近10个
    if (recentFamilies.value.length > 10) {
      recentFamilies.value = recentFamilies.value.slice(0, 10)
    }
    // 保存到本地存储
    cacheStorage.setRecentFamilies(recentFamilies.value)
  }

  /**
   * 设置最近访问的族谱
   */
  function setRecentFamilies(families: Family[]) {
    recentFamilies.value = families
  }

  /**
   * 设置搜索关键词
   */
  function setSearchKeyword(keyword: string) {
    searchKeyword.value = keyword
  }

  /**
   * 设置加载状态
   */
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  /**
   * 根据ID查找族谱
   */
  function findFamilyById(familyId: string): Family | undefined {
    return familyList.value.find((f: Family) => f.id === familyId)
  }

  /**
   * 根据ID查找成员
   */
  function findMemberById(memberId: string): FamilyMembership | undefined {
    return familyMembers.value.find((m: FamilyMembership) => m.id === memberId)
  }

  /**
   * 获取成员的关系
   */
  function getMemberRelationships(memberId: string) {
    // FamilyMembership 类型中没有 relationships 属性，这里需要重新设计
    // 暂时返回空数组，后续需要从关系表中查询
    return []
  }

  /**
   * 从本地存储恢复数据
   */
  function restoreData() {
    const storedRecentFamilies = cacheStorage.getRecentFamilies<Family[]>()
    if (storedRecentFamilies) {
      setRecentFamilies(storedRecentFamilies)
    }
  }

  /**
   * 清空所有数据
   */
  function clearAll() {
    currentFamily.value = null
    familyList.value = []
    recentFamilies.value = []
    familyMembers.value = []
    familyTree.value = []
    selectedMember.value = null
    searchKeyword.value = ''
    isLoading.value = false
  }

  return {
    // 状态
    currentFamily,
    familyList,
    recentFamilies,
    familyMembers,
    familyTree,
    selectedMember,
    treeLayout,
    isLoading,
    searchKeyword,

    // 计算属性
    hasCurrentFamily,
    currentFamilyId,
    currentFamilyName,
    isCurrentFamilyOwner,
    activeMembersCount,
    publicFamilies,
    privateFamilies,

    // 动作
    setCurrentFamily,
    setFamilyList,
    addFamily,
    updateFamily,
    removeFamily,
    setFamilyMembers,
    addFamilyMember,
    updateFamilyMember,
    removeFamilyMember,
    setFamilyTree,
    setSelectedMember,
    setTreeLayout,
    addToRecentFamilies,
    setRecentFamilies,
    setSearchKeyword,
    setLoading,
    findFamilyById,
    findMemberById,
    getMemberRelationships,
    restoreData,
    clearAll
  }
})
