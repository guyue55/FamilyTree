/**
 * Pinia状态管理 - 用户状态
 *
 * @author 古月
 * @version 1.0.0
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userStorage } from '@/utils/storage'
import { UserStatus, UserRole } from '@/enums'
import type { User } from '@/types/user'

/**
 * 用户状态管理
 */
export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => false) // TODO: 需要在User类型中添加role属性
  const isModerator = computed(() => false) // TODO: 需要在User类型中添加role属性
  const isActive = computed(() => user.value?.status === 'active')
  const userName = computed(() => user.value?.nickname || user.value?.username || '')
  const userAvatar = computed(() => user.value?.avatar || '')

  // 动作
  /**
   * 设置用户信息
   */
  function setUser(userData: User) {
    user.value = userData
  }

  /**
   * 设置token
   */
  function setToken(tokenValue: string) {
    token.value = tokenValue
    userStorage.setToken(tokenValue)
  }

  /**
   * 设置刷新token
   */
  function setRefreshToken(refreshTokenValue: string) {
    refreshToken.value = refreshTokenValue
    userStorage.setRefreshToken(refreshTokenValue)
  }

  /**
   * 设置用户数据（包含token）
   */
  function setUserData(userData: User, tokenValue: string, refreshTokenValue?: string) {
    setUser(userData)
    setToken(tokenValue)
    if (refreshTokenValue) {
      setRefreshToken(refreshTokenValue)
    }
    userStorage.setUserInfo(userData)
  }

  /**
   * 更新用户信息
   */
  function updateUser(userData: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      userStorage.setUserInfo(user.value)
    }
  }

  /**
   * 清除用户数据
   */
  function clearUser() {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    userStorage.clearUserData()
  }

  /**
   * 从本地存储恢复用户数据
   */
  function restoreUser() {
    const storedToken = userStorage.getToken()
    const storedRefreshToken = userStorage.getRefreshToken()
    const storedUser = userStorage.getUserInfo<User>()

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = storedUser
      if (storedRefreshToken) {
        refreshToken.value = storedRefreshToken
      }
    }
  }

  /**
   * 检查用户权限
   */
  function hasPermission(permission: string): boolean {
    // TODO: 需要在User类型中添加permissions属性
    return false
  }

  /**
   * 检查用户角色
   */
  function hasRole(role: UserRole): boolean {
    // TODO: 需要在User类型中添加role属性
    return false
  }

  /**
   * 检查是否有任一角色
   */
  function hasAnyRole(roles: UserRole[]): boolean {
    // TODO: 需要在User类型中添加role属性
    return false
  }

  /**
   * 设置加载状态
   */
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    isLoading,

    // 计算属性
    isAuthenticated,
    isAdmin,
    isModerator,
    isActive,
    userName,
    userAvatar,

    // 动作
    setUser,
    setToken,
    setRefreshToken,
    setUserData,
    updateUser,
    clearUser,
    restoreUser,
    hasPermission,
    hasRole,
    hasAnyRole,
    setLoading
  }
})
