/**
 * 常量定义文件
 *
 * 定义项目中使用的所有常量
 * 避免魔法数字和硬编码字符串
 *
 * @author 古月
 * @version 1.0.0
 */

// 导出系统常量
export * from './system'

// 导出关系常量
export * from './relationships'

// 路由常量
export const ROUTES = {
  HOME: '/',
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  VERIFY_EMAIL: '/auth/verify-email',
  DASHBOARD: '/dashboard',
  PROFILE: '/user/profile',
  SETTINGS: '/user/settings',
  FAMILY_LIST: '/family',
  FAMILY_DETAIL: '/family/:id',
  FAMILY_CREATE: '/family/create',
  FAMILY_EDIT: '/family/:id/edit',
  FAMILY_TREE: '/family/:id/tree',
  FAMILY_MEMBERS: '/family/:id/members',
  FAMILY_MEDIA: '/family/:id/media',
  MEMBER_DETAIL: '/member/:id',
  MEMBER_EDIT: '/member/:id/edit',
  MEDIA_GALLERY: '/media',
  MEDIA_UPLOAD: '/media/upload',
  ADMIN: '/admin',
  NOT_FOUND: '/404',
  FORBIDDEN: '/403',
  SERVER_ERROR: '/500'
} as const

// 存储键名常量
export const STORAGE_KEYS = {
  TOKEN: 'familytree_token',
  REFRESH_TOKEN: 'familytree_refresh_token',
  USER_INFO: 'familytree_user_info',
  LANGUAGE: 'familytree_language',
  THEME: 'familytree_theme',
  SIDEBAR_COLLAPSED: 'familytree_sidebar_collapsed',
  RECENT_FAMILIES: 'familytree_recent_families',
  SEARCH_HISTORY: 'familytree_search_history',
  UPLOAD_PROGRESS: 'familytree_upload_progress'
} as const

// 支持的图片格式
export const IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'] as const

// 支持的视频格式
export const VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'] as const

// 支持的音频格式
export const AUDIO_FORMATS = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'] as const

// 支持的文档格式
export const DOCUMENT_FORMATS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'] as const

// 邀请状态常量
export const INVITATION_STATUS = {
  PENDING: 'pending',
  ACCEPTED: 'accepted',
  REJECTED: 'rejected',
  EXPIRED: 'expired'
} as const

// 媒体处理状态常量
export const MEDIA_STATUS = {
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const

// 导出格式常量
export const EXPORT_FORMATS = {
  EXCEL: 'excel',
  CSV: 'csv',
  JSON: 'json',
  PDF: 'pdf',
  GEDCOM: 'gedcom'
} as const

// 正则表达式常量
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^1[3-9]\d{9}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
  CHINESE_NAME: /^[\u4e00-\u9fa5]{2,10}$/,
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/
} as const

// 错误代码常量
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  UNSUPPORTED_FILE_TYPE: 'UNSUPPORTED_FILE_TYPE',
  UPLOAD_FAILED: 'UPLOAD_FAILED'
} as const

// 默认配置常量
export const DEFAULT_CONFIG = {
  AVATAR: '/images/default-avatar.png',
  COVER: '/images/default-cover.jpg',
  FAMILY_AVATAR: '/images/default-family.png',
  LOADING_TEXT: '加载中...',
  EMPTY_TEXT: '暂无数据',
  ERROR_TEXT: '加载失败',
  RETRY_TEXT: '重试'
} as const

// 动画持续时间常量
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500
} as const

// 防抖延迟常量
export const DEBOUNCE_DELAY = {
  SEARCH: 300,
  RESIZE: 100,
  SCROLL: 50,
  INPUT: 500
} as const
