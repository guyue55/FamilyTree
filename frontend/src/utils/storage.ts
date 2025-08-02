/**
 * 本地存储工具函数
 * 提供统一的本地存储管理
 *
 * @author 古月
 * @version 1.0.0
 */

import { SYSTEM_CONSTANTS } from '@/constants/system'

/**
 * 存储类型枚举
 */
export enum StorageType {
  LOCAL = 'localStorage',
  SESSION = 'sessionStorage'
}

/**
 * 存储键名常量
 */
export const STORAGE_KEYS = {
  TOKEN: 'familytree_token',
  REFRESH_TOKEN: 'familytree_refresh_token',
  USER_INFO: 'familytree_user_info',
  LANGUAGE: 'familytree_language',
  THEME: 'familytree_theme',
  SIDEBAR_COLLAPSED: 'familytree_sidebar_collapsed',
  RECENT_FAMILIES: 'familytree_recent_families',
  SEARCH_HISTORY: 'familytree_search_history',
  UPLOAD_PROGRESS: 'familytree_upload_progress',
  TREE_LAYOUT: 'familytree_tree_layout',
  DISPLAY_OPTIONS: 'familytree_display_options'
} as const

/**
 * 存储项接口
 */
interface StorageItem<T = any> {
  value: T
  timestamp: number
  expiry?: number
}

/**
 * 存储管理类
 */
class StorageManager {
  private storage: Storage

  constructor(type: StorageType = StorageType.LOCAL) {
    this.storage = window[type]
  }

  /**
   * 设置存储项
   * @param key 键名
   * @param value 值
   * @param expiry 过期时间（毫秒），可选
   */
  set<T>(key: string, value: T, expiry?: number): void {
    try {
      const item: StorageItem<T> = {
        value,
        timestamp: Date.now(),
        expiry: expiry ? Date.now() + expiry : undefined
      }
      this.storage.setItem(key, JSON.stringify(item))
    } catch (error) {
      console.error('存储设置失败:', error)
    }
  }

  /**
   * 获取存储项
   * @param key 键名
   * @param defaultValue 默认值
   */
  get<T>(key: string, defaultValue?: T): T | undefined {
    try {
      const itemStr = this.storage.getItem(key)
      if (!itemStr) return defaultValue

      const item: StorageItem<T> = JSON.parse(itemStr)

      // 检查是否过期
      if (item.expiry && Date.now() > item.expiry) {
        this.remove(key)
        return defaultValue
      }

      return item.value
    } catch (error) {
      console.error('存储获取失败:', error)
      return defaultValue
    }
  }

  /**
   * 移除存储项
   * @param key 键名
   */
  remove(key: string): void {
    try {
      this.storage.removeItem(key)
    } catch (error) {
      console.error('存储移除失败:', error)
    }
  }

  /**
   * 清空所有存储项
   */
  clear(): void {
    try {
      this.storage.clear()
    } catch (error) {
      console.error('存储清空失败:', error)
    }
  }

  /**
   * 检查键是否存在
   * @param key 键名
   */
  has(key: string): boolean {
    return this.storage.getItem(key) !== null
  }

  /**
   * 获取所有键名
   */
  keys(): string[] {
    const keys: string[] = []
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i)
      if (key) keys.push(key)
    }
    return keys
  }

  /**
   * 获取存储大小（字节）
   */
  size(): number {
    let total = 0
    for (let i = 0; i < this.storage.length; i++) {
      const key = this.storage.key(i)
      if (key) {
        const value = this.storage.getItem(key)
        if (value) {
          total += key.length + value.length
        }
      }
    }
    return total
  }

  /**
   * 清理过期项
   */
  cleanup(): void {
    const keys = this.keys()
    keys.forEach(key => {
      try {
        const itemStr = this.storage.getItem(key)
        if (itemStr) {
          const item: StorageItem = JSON.parse(itemStr)
          if (item.expiry && Date.now() > item.expiry) {
            this.remove(key)
          }
        }
      } catch (error) {
        // 如果解析失败，可能是旧格式数据，保留不删除
        console.warn('清理存储项时解析失败:', key, error)
      }
    })
  }
}

/**
 * 本地存储实例
 */
export const localStorage = new StorageManager(StorageType.LOCAL)

/**
 * 会话存储实例
 */
export const sessionStorage = new StorageManager(StorageType.SESSION)

/**
 * 用户相关存储操作
 */
export const userStorage = {
  /**
   * 设置用户token
   */
  setToken(token: string): void {
    localStorage.set(STORAGE_KEYS.TOKEN, token, SYSTEM_CONSTANTS.TOKEN_CACHE_TIME)
  },

  /**
   * 获取用户token
   */
  getToken(): string | undefined {
    return localStorage.get<string>(STORAGE_KEYS.TOKEN)
  },

  /**
   * 移除用户token
   */
  removeToken(): void {
    localStorage.remove(STORAGE_KEYS.TOKEN)
    localStorage.remove(STORAGE_KEYS.REFRESH_TOKEN)
  },

  /**
   * 设置刷新token
   */
  setRefreshToken(token: string): void {
    localStorage.set(STORAGE_KEYS.REFRESH_TOKEN, token, SYSTEM_CONSTANTS.TOKEN_CACHE_TIME)
  },

  /**
   * 获取刷新token
   */
  getRefreshToken(): string | undefined {
    return localStorage.get<string>(STORAGE_KEYS.REFRESH_TOKEN)
  },

  /**
   * 设置用户信息
   */
  setUserInfo(userInfo: any): void {
    localStorage.set(STORAGE_KEYS.USER_INFO, userInfo)
  },

  /**
   * 获取用户信息
   */
  getUserInfo<T = any>(): T | undefined {
    return localStorage.get<T>(STORAGE_KEYS.USER_INFO)
  },

  /**
   * 移除用户信息
   */
  removeUserInfo(): void {
    localStorage.remove(STORAGE_KEYS.USER_INFO)
  },

  /**
   * 清空所有用户数据
   */
  clearUserData(): void {
    this.removeToken()
    this.removeUserInfo()
  }
}

/**
 * 应用设置存储操作
 */
export const appStorage = {
  /**
   * 设置语言
   */
  setLanguage(language: string): void {
    localStorage.set(STORAGE_KEYS.LANGUAGE, language)
  },

  /**
   * 获取语言
   */
  getLanguage(): string | undefined {
    return localStorage.get<string>(STORAGE_KEYS.LANGUAGE)
  },

  /**
   * 设置主题
   */
  setTheme(theme: string): void {
    localStorage.set(STORAGE_KEYS.THEME, theme)
  },

  /**
   * 获取主题
   */
  getTheme(): string | undefined {
    return localStorage.get<string>(STORAGE_KEYS.THEME)
  },

  /**
   * 设置侧边栏折叠状态
   */
  setSidebarCollapsed(collapsed: boolean): void {
    localStorage.set(STORAGE_KEYS.SIDEBAR_COLLAPSED, collapsed)
  },

  /**
   * 获取侧边栏折叠状态
   */
  getSidebarCollapsed(): boolean {
    return localStorage.get<boolean>(STORAGE_KEYS.SIDEBAR_COLLAPSED, false) ?? false
  },

  /**
   * 设置树形布局
   */
  setTreeLayout(layout: string): void {
    localStorage.set(STORAGE_KEYS.TREE_LAYOUT, layout)
  },

  /**
   * 获取树形布局
   */
  getTreeLayout(): string | undefined {
    return localStorage.get<string>(STORAGE_KEYS.TREE_LAYOUT)
  },

  /**
   * 设置显示选项
   */
  setDisplayOptions(options: any): void {
    localStorage.set(STORAGE_KEYS.DISPLAY_OPTIONS, options)
  },

  /**
   * 获取显示选项
   */
  getDisplayOptions<T = any>(): T | undefined {
    return localStorage.get<T>(STORAGE_KEYS.DISPLAY_OPTIONS)
  }
}

/**
 * 数据缓存存储操作
 */
export const cacheStorage = {
  /**
   * 设置最近访问的族谱
   */
  setRecentFamilies(families: any[]): void {
    localStorage.set(STORAGE_KEYS.RECENT_FAMILIES, families, SYSTEM_CONSTANTS.DATA_CACHE_TIME)
  },

  /**
   * 获取最近访问的族谱
   */
  getRecentFamilies<T = any[]>(): T | undefined {
    return localStorage.get<T>(STORAGE_KEYS.RECENT_FAMILIES)
  },

  /**
   * 添加到最近访问
   */
  addRecentFamily(family: any): void {
    const recent = this.getRecentFamilies() || []
    const filtered = recent.filter((item: any) => item.id !== family.id)
    filtered.unshift(family)
    // 只保留最近10个
    this.setRecentFamilies(filtered.slice(0, 10))
  },

  /**
   * 设置搜索历史
   */
  setSearchHistory(history: string[]): void {
    localStorage.set(STORAGE_KEYS.SEARCH_HISTORY, history)
  },

  /**
   * 获取搜索历史
   */
  getSearchHistory(): string[] {
    return localStorage.get<string[]>(STORAGE_KEYS.SEARCH_HISTORY, []) ?? []
  },

  /**
   * 添加搜索历史
   */
  addSearchHistory(keyword: string): void {
    if (!keyword.trim()) return

    const history = this.getSearchHistory()
    const filtered = history.filter(item => item !== keyword)
    filtered.unshift(keyword)
    // 只保留最近20个
    this.setSearchHistory(filtered.slice(0, 20))
  },

  /**
   * 清空搜索历史
   */
  clearSearchHistory(): void {
    localStorage.remove(STORAGE_KEYS.SEARCH_HISTORY)
  }
}

/**
 * 定期清理过期数据
 */
export function startStorageCleanup(): void {
  // 立即清理一次
  localStorage.cleanup()
  sessionStorage.cleanup()

  // 每小时清理一次
  setInterval(
    () => {
      localStorage.cleanup()
      sessionStorage.cleanup()
    },
    60 * 60 * 1000
  )
}

// 页面加载时启动清理
if (typeof window !== 'undefined') {
  startStorageCleanup()
}
