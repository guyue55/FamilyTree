/**
 * Pinia状态管理 - 应用状态
 *
 * @author 古月
 * @version 1.0.0
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { appStorage } from '@/utils/storage'
import { Theme, Language, LoadingState } from '@/enums'

/**
 * 应用状态管理
 */
export const useAppStore = defineStore('app', () => {
  // 状态
  const theme = ref<Theme>(Theme.LIGHT)
  const language = ref<Language>(Language.ZH_CN)
  const sidebarCollapsed = ref(false)
  const loadingState = ref<LoadingState>(LoadingState.IDLE)
  const loadingText = ref('')
  const pageTitle = ref('族谱系统')
  const breadcrumbs = ref<Array<{ name: string; path?: string }>>([])

  // 计算属性
  const isDarkTheme = computed(() => theme.value === Theme.DARK)
  const isLoading = computed(() => loadingState.value === LoadingState.LOADING)
  const isEnglish = computed(() => language.value === Language.EN_US)
  const isChinese = computed(() => language.value === Language.ZH_CN)

  // 动作
  /**
   * 设置主题
   */
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    appStorage.setTheme(newTheme)

    // 更新HTML类名
    const html = document.documentElement
    html.classList.remove('light', 'dark')
    html.classList.add(newTheme)
  }

  /**
   * 切换主题
   */
  function toggleTheme() {
    const newTheme = theme.value === Theme.LIGHT ? Theme.DARK : Theme.LIGHT
    setTheme(newTheme)
  }

  /**
   * 设置语言
   */
  function setLanguage(newLanguage: Language) {
    language.value = newLanguage
    appStorage.setLanguage(newLanguage)

    // 更新HTML lang属性
    document.documentElement.lang = newLanguage === Language.ZH_CN ? 'zh-CN' : 'en-US'
  }

  /**
   * 设置侧边栏折叠状态
   */
  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
    appStorage.setSidebarCollapsed(collapsed)
  }

  /**
   * 切换侧边栏折叠状态
   */
  function toggleSidebar() {
    setSidebarCollapsed(!sidebarCollapsed.value)
  }

  /**
   * 设置加载状态
   */
  function setLoadingState(state: LoadingState, text?: string) {
    loadingState.value = state
    if (text !== undefined) {
      loadingText.value = text
    }
  }

  /**
   * 开始加载
   */
  function startLoading(text: string = '加载中...') {
    setLoadingState(LoadingState.LOADING, text)
  }

  /**
   * 结束加载
   */
  function stopLoading() {
    setLoadingState(LoadingState.IDLE, '')
  }

  /**
   * 设置页面标题
   */
  function setPageTitle(title: string) {
    pageTitle.value = title
    document.title = `${title} - 族谱系统`
  }

  /**
   * 设置面包屑导航
   */
  function setBreadcrumbs(crumbs: Array<{ name: string; path?: string }>) {
    breadcrumbs.value = crumbs
  }

  /**
   * 添加面包屑项
   */
  function addBreadcrumb(crumb: { name: string; path?: string }) {
    breadcrumbs.value.push(crumb)
  }

  /**
   * 清空面包屑导航
   */
  function clearBreadcrumbs() {
    breadcrumbs.value = []
  }

  /**
   * 从本地存储恢复应用设置
   */
  function restoreSettings() {
    // 恢复主题
    const storedTheme = appStorage.getTheme() as Theme
    if (storedTheme && Object.values(Theme).includes(storedTheme)) {
      setTheme(storedTheme)
    }

    // 恢复语言
    const storedLanguage = appStorage.getLanguage() as Language
    if (storedLanguage && Object.values(Language).includes(storedLanguage)) {
      setLanguage(storedLanguage)
    }

    // 恢复侧边栏状态
    const storedSidebarCollapsed = appStorage.getSidebarCollapsed()
    setSidebarCollapsed(storedSidebarCollapsed)
  }

  /**
   * 重置应用设置
   */
  function resetSettings() {
    setTheme(Theme.LIGHT)
    setLanguage(Language.ZH_CN)
    setSidebarCollapsed(false)
    setLoadingState(LoadingState.IDLE, '')
    setPageTitle('族谱系统')
    clearBreadcrumbs()
  }

  return {
    // 状态
    theme,
    language,
    sidebarCollapsed,
    loadingState,
    loadingText,
    pageTitle,
    breadcrumbs,

    // 计算属性
    isDarkTheme,
    isLoading,
    isEnglish,
    isChinese,

    // 动作
    setTheme,
    toggleTheme,
    setLanguage,
    setSidebarCollapsed,
    toggleSidebar,
    setLoadingState,
    startLoading,
    stopLoading,
    setPageTitle,
    setBreadcrumbs,
    addBreadcrumb,
    clearBreadcrumbs,
    restoreSettings,
    resetSettings
  }
})
