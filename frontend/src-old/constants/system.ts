/**
 * 系统常量配置
 * 包含系统级别的配置常量
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * 系统基础常量
 */
export const SYSTEM_CONSTANTS = {
  // 应用信息
  APP_NAME: '族谱系统',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: '传统纸质族谱的现代化电子版本',

  // 分页配置
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],

  // 文件上传限制
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_AVATAR_SIZE: 5 * 1024 * 1024, // 5MB
  MAX_COVER_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ],

  // 缓存时间
  TOKEN_CACHE_TIME: 7 * 24 * 60 * 60 * 1000, // 7天
  DATA_CACHE_TIME: 30 * 60 * 1000, // 30分钟
  SEARCH_CACHE_TIME: 5 * 60 * 1000, // 5分钟

  // 界面配置
  SIDEBAR_WIDTH: 240,
  SIDEBAR_COLLAPSED_WIDTH: 64,
  HEADER_HEIGHT: 60,
  FOOTER_HEIGHT: 40,

  // 请求配置
  REQUEST_TIMEOUT: 30000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000,

  // 密码规则
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 32,

  // 族谱配置
  MAX_TREE_DEPTH: 20,
  MAX_MEMBERS_PER_FAMILY: 10000,
  DEFAULT_TREE_LAYOUT: 'horizontal',

  // 搜索配置
  SEARCH_MIN_LENGTH: 2,
  SEARCH_MAX_RESULTS: 100,
  SEARCH_DEBOUNCE_TIME: 300
} as const

/**
 * 性别类型常量
 */
export const GENDER_TYPES = {
  UNKNOWN: 0,
  MALE: 1,
  FEMALE: 2
} as const

/**
 * 性别显示文本
 */
export const GENDER_LABELS = {
  [GENDER_TYPES.UNKNOWN]: '未知',
  [GENDER_TYPES.MALE]: '男',
  [GENDER_TYPES.FEMALE]: '女'
} as const

/**
 * 用户角色常量
 */
export const USER_ROLES = {
  CREATOR: 1,
  ADMIN: 2,
  EDITOR: 3,
  VIEWER: 4
} as const

/**
 * 用户角色显示文本
 */
export const USER_ROLE_LABELS = {
  [USER_ROLES.CREATOR]: '创建者',
  [USER_ROLES.ADMIN]: '管理员',
  [USER_ROLES.EDITOR]: '编辑者',
  [USER_ROLES.VIEWER]: '查看者'
} as const

/**
 * 族谱可见性常量
 */
export const VISIBILITY_TYPES = {
  PUBLIC: 1,
  FAMILY: 2,
  PRIVATE: 3
} as const

/**
 * 族谱可见性显示文本
 */
export const VISIBILITY_LABELS = {
  [VISIBILITY_TYPES.PUBLIC]: '公开',
  [VISIBILITY_TYPES.FAMILY]: '家族内',
  [VISIBILITY_TYPES.PRIVATE]: '私有'
} as const

/**
 * 用户状态常量
 */
export const USER_STATUS = {
  INACTIVE: 0,
  ACTIVE: 1,
  SUSPENDED: 2,
  DELETED: 3
} as const

/**
 * 用户状态显示文本
 */
export const USER_STATUS_LABELS = {
  [USER_STATUS.INACTIVE]: '未激活',
  [USER_STATUS.ACTIVE]: '正常',
  [USER_STATUS.SUSPENDED]: '已暂停',
  [USER_STATUS.DELETED]: '已删除'
} as const

/**
 * 族谱状态常量
 */
export const FAMILY_STATUS = {
  DRAFT: 0,
  ACTIVE: 1,
  ARCHIVED: 2,
  DELETED: 3
} as const

/**
 * 族谱状态显示文本
 */
export const FAMILY_STATUS_LABELS = {
  [FAMILY_STATUS.DRAFT]: '草稿',
  [FAMILY_STATUS.ACTIVE]: '正常',
  [FAMILY_STATUS.ARCHIVED]: '已归档',
  [FAMILY_STATUS.DELETED]: '已删除'
} as const

/**
 * 主题类型常量
 */
export const THEME_TYPES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
} as const

/**
 * 语言类型常量
 */
export const LANGUAGE_TYPES = {
  ZH_CN: 'zh-CN',
  EN_US: 'en-US',
  ZH_TW: 'zh-TW'
} as const

/**
 * 语言显示文本
 */
export const LANGUAGE_LABELS = {
  [LANGUAGE_TYPES.ZH_CN]: '简体中文',
  [LANGUAGE_TYPES.EN_US]: 'English',
  [LANGUAGE_TYPES.ZH_TW]: '繁體中文'
} as const
