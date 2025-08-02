/**
 * API配置文件
 * 包含API相关的配置常量
 *
 * @author 古月
 * @version 1.0.0
 */

/**
 * API配置常量
 */
export const API_CONFIG = {
  // 基础URL
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  
  // 请求超时时间（毫秒）
  TIMEOUT: 30000,
  
  // 重试次数
  RETRY_TIMES: 3,
  
  // 重试延迟（毫秒）
  RETRY_DELAY: 1000,
  
  // 文件上传相关
  UPLOAD_URL: '/upload',
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  
  // 分页配置
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  
  // 缓存配置
  CACHE_TIME: 5 * 60 * 1000, // 5分钟
  
  // 请求头配置
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
} as const

/**
 * API端点配置
 */
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    VERIFY_EMAIL: '/auth/verify-email'
  },
  
  // 用户相关
  USER: {
    PROFILE: '/user/profile',
    UPDATE_PROFILE: '/user/profile',
    CHANGE_PASSWORD: '/user/change-password',
    UPLOAD_AVATAR: '/user/avatar',
    SETTINGS: '/user/settings'
  },
  
  // 族谱相关
  FAMILY: {
    LIST: '/families',
    CREATE: '/families',
    DETAIL: '/families/:id',
    UPDATE: '/families/:id',
    DELETE: '/families/:id',
    MEMBERS: '/families/:id/members',
    TREE: '/families/:id/tree',
    SEARCH: '/families/search',
    STATISTICS: '/families/:id/statistics'
  },
  
  // 成员相关
  MEMBER: {
    LIST: '/members',
    CREATE: '/members',
    DETAIL: '/members/:id',
    UPDATE: '/members/:id',
    DELETE: '/members/:id',
    RELATIONSHIPS: '/members/:id/relationships',
    SEARCH: '/members/search'
  },
  
  // 文件上传
  UPLOAD: {
    IMAGE: '/upload/image',
    DOCUMENT: '/upload/document',
    AVATAR: '/upload/avatar'
  }
} as const

/**
 * 环境配置
 */
export const ENV_CONFIG = {
  // 是否为开发环境
  IS_DEV: import.meta.env.DEV,
  
  // 是否为生产环境
  IS_PROD: import.meta.env.PROD,
  
  // API基础URL
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  
  // 应用标题
  APP_TITLE: import.meta.env.VITE_APP_TITLE || '族谱系统',
  
  // 应用版本
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0'
} as const